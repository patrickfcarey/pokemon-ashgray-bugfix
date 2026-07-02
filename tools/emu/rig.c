/* Command-driven headless GBA test rig (libmgba).
   Compile once; drive input / screenshots / RAM peek-poke / savestates from a script.

   usage: rig <rom> <script|-> [savestate-to-preload]
   If a 3rd arg is given and the file exists, it is loaded as a savestate after reset
   (so a script can resume from a checkpoint instead of re-running the intro).

   Script commands (one per line, '#' = comment):
     key  <NAMES..|- >     set the held key set (replaces). names: A B SELECT START
                           RIGHT LEFT UP DOWN R L ; '-' or NONE = release all
     frames <n>            advance n frames with the current held keys
     tap <NAME> <h> <r>    press NAME for h frames, then release for r frames
     shot <file.raw>       dump the 240x160 framebuffer (mColor) to file
     peek8|peek16|peek32 <addr>            busRead, print "PEEK <addr> = <val>"
     poke8|poke16|poke32 <addr> <val>      busWrite
     deref <ptraddr> <off> <8|16|32>       base=read32(ptraddr); print read<sz>(base+off)
     loc                   FireRed: print map group/num + x/y from *gSaveBlock1Ptr
     save <file.ss>        write a savestate
     load <file.ss>        load a savestate
     call <addr> [r0..r3]  invoke a Thumb fn in isolation; run until it returns (lr=sentinel).
                           saves/restores CPU regs+cpsr+prefetch. logs ret r0/r1 + step count.
                           set up RAM with poke/dump first, read results after. (e.g. test CopyMonToPC)
     log <text...>         echo a line to stderr (progress marker)

   --- memory tracer (instruction-level; wraps the ARM load/store fn pointers) ---
     watch  <addr> [len]                   trace WRITES into [addr,+len): logs PC, lr(=caller),
                                           value, r0-r3. dedup by PC (= the set of writers).
     rwatch <addr> [len]                   same for READS (only real data loads, not fetches).
     watchif  <addr> <len> <op> <val>      conditional WRITE watch; op = eq ne gt lt ge le
     rwatchif <addr> <len> <op> <val>      conditional READ watch (no dedup; logs each hit, cap 400)
     watchvar <id>                         watch writes to FRLG var <id> (off the live sb1)
     watchderef <ptraddr> <off> [len]      watch [ *ptraddr + off , +len )
     unwatch                               clear all watches
   --- FRLG var/flag helpers (addresses computed off the live gSaveBlock1Ptr) ---
     var <id>            / pokevar <id> <val>      read / write var (sb1+0x1000+2*(id-0x4000))
     flag <id>           / pokeflag <id> <0|1>     read / set-clear flag bit (sb1+0xEE0+id/8)
   (TODO if ever needed: execution breakpoints — mgba fetches bypass the load path, so they'd
    need the mDebugger module rather than the fn-pointer wrap used here.)
*/
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/core/serialize.h>
#include <mgba/gba/core.h>
#include <mgba/internal/gba/gba.h>
#include <mgba/internal/gba/savedata.h>
#include <mgba/internal/arm/arm.h>
#include <mgba/internal/arm/isa-inlines.h>
#include <mgba-util/vfs.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct VFile* VFileOpen(const char* path, int flags);
static void noLog(struct mLogger* l, int c, enum mLogLevel lv, const char* f, va_list a) {
	(void) l; (void) c; (void) lv; (void) f; (void) a;
}
static struct mLogger SL = { .log = noLog };

/* FireRed (U) v1.0 */
#define GSAVEBLOCK1PTR 0x03005008u

static struct mCore* core;
static mColor* buf;
static unsigned VW, VH;
static uint32_t held = 0;

/* ---- instruction-level memory tracer: wrap the ARM load/store fn pointers ----
   watch/rwatch a byte range; on a matching access log the PC, link reg (= caller),
   the access, and r0-r3 (likely args/values). Optional condition (op,val) fires only
   when the accessed value matches -> catches "when does X become >N". Plain watches
   dedup by PC (find the set of accessing functions); conditional ones log every hit.
   LIMIT: only CPU data accesses go through these fn pointers — DMA transfers (and PPU
   fetches) bypass them entirely, so a DMA write into a watched range is invisible.
   Also note the plain-watch PC dedup set is shared across ALL active watches. */
enum { WT_WRITE = 0, WT_READ = 1 };
struct Watch { uint32_t lo, hi; int type, op; uint32_t val; };
static struct ARMCore* wcpu = NULL;
static void (*orig_s8)(struct ARMCore*, uint32_t, int8_t, int*);
static void (*orig_s16)(struct ARMCore*, uint32_t, int16_t, int*);
static void (*orig_s32)(struct ARMCore*, uint32_t, int32_t, int*);
static uint32_t (*orig_l8)(struct ARMCore*, uint32_t, int*);
static uint32_t (*orig_l16)(struct ARMCore*, uint32_t, int*);
static uint32_t (*orig_l32)(struct ARMCore*, uint32_t, int*);
static struct Watch watches[16];
static int n_watch = 0, store_wrapped = 0, load_wrapped = 0, log_cap = 0;
static uint32_t seen_pc[2048]; static int n_seen = 0;
static int cond_ok(int op, uint32_t v, uint32_t r) {
	switch (op) {
	case 1: return v == r;  case 2: return v != r;
	case 3: return (int32_t) v >  (int32_t) r;  case 4: return (int32_t) v <  (int32_t) r;
	case 5: return (int32_t) v >= (int32_t) r;  case 6: return (int32_t) v <= (int32_t) r;
	default: return 1;
	}
}
static void wcheck(struct ARMCore* c, uint32_t a, int sz, uint32_t v, int type) {
	for (int i = 0; i < n_watch; i++) {
		struct Watch* w = &watches[i];
		if (w->type != type || !(a < w->hi && a + sz > w->lo) || !cond_ok(w->op, v, w->val)) continue;
		uint32_t pc = c->gprs[15];
		if (w->op == 0) {                      /* plain: one line per unique writer PC */
			for (int k = 0; k < n_seen; k++) if (seen_pc[k] == pc) return;
			if (n_seen < 2048) seen_pc[n_seen++] = pc;
		}
		if (log_cap >= 400) { if (log_cap++ == 400) fprintf(stderr, "WATCH (log cap 400 reached)\n"); return; }
		log_cap++;
		fprintf(stderr, "WATCH %c pc=0x%08x lr=0x%08x [0x%08x]=0x%x sz%d  r0=%x r1=%x r2=%x r3=%x\n",
			type == WT_READ ? 'r' : 'w', pc, c->gprs[14], a, v, sz,
			c->gprs[0], c->gprs[1], c->gprs[2], c->gprs[3]);
		return;
	}
}
static void w_s8(struct ARMCore* c, uint32_t a, int8_t v, int* cc)   { wcheck(c, a, 1, (uint8_t) v,  WT_WRITE); orig_s8(c, a, v, cc); }
static void w_s16(struct ARMCore* c, uint32_t a, int16_t v, int* cc) { wcheck(c, a, 2, (uint16_t) v, WT_WRITE); orig_s16(c, a, v, cc); }
static void w_s32(struct ARMCore* c, uint32_t a, int32_t v, int* cc) { wcheck(c, a, 4, (uint32_t) v, WT_WRITE); orig_s32(c, a, v, cc); }
static uint32_t w_l8(struct ARMCore* c, uint32_t a, int* cc)  { uint32_t v = orig_l8(c, a, cc);  wcheck(c, a, 1, v, WT_READ); return v; }
static uint32_t w_l16(struct ARMCore* c, uint32_t a, int* cc) { uint32_t v = orig_l16(c, a, cc); wcheck(c, a, 2, v, WT_READ); return v; }
static uint32_t w_l32(struct ARMCore* c, uint32_t a, int* cc) { uint32_t v = orig_l32(c, a, cc); wcheck(c, a, 4, v, WT_READ); return v; }
static struct ARMCore* wc(void) { if (!wcpu) wcpu = ((struct GBA*) core->board)->cpu; return wcpu; }
static void wrap_store(void) {
	if (store_wrapped) return; store_wrapped = 1; struct ARMCore* c = wc();
	orig_s8 = c->memory.store8; c->memory.store8 = w_s8;
	orig_s16 = c->memory.store16; c->memory.store16 = w_s16;
	orig_s32 = c->memory.store32; c->memory.store32 = w_s32;
}
static void wrap_load(void) {  /* heavier (fires on data loads); only when a read-watch is set */
	if (load_wrapped) return; load_wrapped = 1; struct ARMCore* c = wc();
	orig_l8 = c->memory.load8; c->memory.load8 = w_l8;
	orig_l16 = c->memory.load16; c->memory.load16 = w_l16;
	orig_l32 = c->memory.load32; c->memory.load32 = w_l32;
}
static void watch_add(uint32_t lo, uint32_t hi, int type, int op, uint32_t val) {
	if (type == WT_READ) wrap_load(); else wrap_store();
	if (n_watch < 16) { watches[n_watch++] = (struct Watch){ lo, hi, type, op, val }; }
	n_seen = 0; log_cap = 0;
	fprintf(stderr, "WATCH +%c [0x%08x,0x%08x) op=%d val=0x%x\n", type == WT_READ ? 'r' : 'w', lo, hi, op, val);
}
static int parse_op(const char* s) {
	if (!strcmp(s, "eq")) return 1; if (!strcmp(s, "ne")) return 2;
	if (!strcmp(s, "gt")) return 3; if (!strcmp(s, "lt")) return 4;
	if (!strcmp(s, "ge")) return 5; if (!strcmp(s, "le")) return 6; return 0;
}
/* FRLG var/flag address math off the live gSaveBlock1Ptr */
static uint32_t varaddr(uint32_t id) { return core->busRead32(core, GSAVEBLOCK1PTR) + 0x1000 + 2 * (id - 0x4000); }
static uint32_t flagbyte(uint32_t id) { return core->busRead32(core, GSAVEBLOCK1PTR) + 0xEE0 + (id >> 3); }

static uint32_t keybit(const char* n) {
	if (!strcmp(n, "A")) return 0x001;
	if (!strcmp(n, "B")) return 0x002;
	if (!strcmp(n, "SELECT")) return 0x004;
	if (!strcmp(n, "START")) return 0x008;
	if (!strcmp(n, "RIGHT")) return 0x010;
	if (!strcmp(n, "LEFT")) return 0x020;
	if (!strcmp(n, "UP")) return 0x040;
	if (!strcmp(n, "DOWN")) return 0x080;
	if (!strcmp(n, "R")) return 0x100;
	if (!strcmp(n, "L")) return 0x200;
	return 0;
}

static void advance(int n, uint32_t keys) {
	for (int i = 0; i < n; i++) { core->setKeys(core, keys); core->runFrame(core); }
}

static void dump(const char* path) {
	FILE* o = fopen(path, "wb");
	if (!o) { fprintf(stderr, "shot: cannot open %s\n", path); return; }
	fwrite(buf, sizeof(mColor), (size_t) VW * VH, o);
	fclose(o);
	fprintf(stderr, "SHOT %s (%ux%u)\n", path, VW, VH);
}

static uint32_t rd(uint32_t a, int sz) {
	if (sz == 8) return core->busRead8(core, a);
	if (sz == 16) return core->busRead16(core, a);
	return core->busRead32(core, a);
}
static void wr(uint32_t a, int sz, uint32_t v) {
	if (sz == 8) core->busWrite8(core, a, (uint8_t) v);
	else if (sz == 16) core->busWrite16(core, a, (uint16_t) v);
	else core->busWrite32(core, a, v);
}

static int dosave(const char* path) {
	/* O_RDWR (not O_WRONLY): mgba maps the file MAP_WRITE via mmap(PROT_WRITE,
	   MAP_SHARED), which the kernel rejects on a write-only fd -> map returns NULL
	   and the state is never written (file ends up zero-filled by the truncate). */
	struct VFile* vf = VFileOpen(path, O_RDWR | O_CREAT | O_TRUNC);
	if (!vf) { fprintf(stderr, "save: open fail %s\n", path); return 0; }
	/* flags=0 => core state only (EWRAM/IWRAM/VRAM/regs). That is all we need to
	   resume within the same session; the optional savedata extdata block is what
	   returned false before (no flash/SRAM type configured yet). */
	int ok = mCoreSaveStateNamed(core, vf, 0);
	vf->close(vf);
	fprintf(stderr, "SAVE %s -> %s\n", path, ok ? "ok" : "FAIL");
	return ok;
}
static int doload(const char* path) {
	struct VFile* vf = VFileOpen(path, O_RDONLY);
	if (!vf) { fprintf(stderr, "load: open fail %s\n", path); return 0; }
	int ok = mCoreLoadStateNamed(core, vf, 0);
	vf->close(vf);
	fprintf(stderr, "LOAD %s -> %s\n", path, ok ? "ok" : "FAIL");
	return ok;
}

/* ---- CPU introspection (for localizing freezes) ----
   ARMRun() steps one instruction AND processes the event scheduler when cycles
   cross nextEvent, so stepping it here is faithful to hardware timing. */
static void print_regs(struct ARMCore* c) {
	uint32_t pc = c->gprs[15];
	fprintf(stderr, "REGS pc=0x%08x lr=0x%08x sp=0x%08x cpsr=0x%08x t=%d mode=%d\n",
		pc, c->gprs[14], c->gprs[13], (uint32_t) c->cpsr.packed, c->cpsr.t, c->executionMode);
	for (int i = 0; i < 16; i += 4)
		fprintf(stderr, "  r%-2d=%08x r%-2d=%08x r%-2d=%08x r%-2d=%08x\n",
			i, c->gprs[i], i + 1, c->gprs[i + 1], i + 2, c->gprs[i + 2], i + 3, c->gprs[i + 3]);
	/* show the few code halfwords around PC (thumb pipeline: executing insn ~ pc-4) */
	fprintf(stderr, "  code@pc-4..+2:");
	for (int o = -4; o <= 2; o += 2) fprintf(stderr, " %04x", core->busRead16(core, (pc + o) & ~1u));
	fprintf(stderr, "\n");
}

int main(int argc, char** argv) {
	setbuf(stderr, NULL);
	mLogSetDefaultLogger(&SL);
	if (argc < 3) { fprintf(stderr, "usage: rig rom script|- [preload.ss]\n"); return 1; }

	struct VFile* vf = VFileOpen(argv[1], O_RDONLY);
	if (!vf) { fprintf(stderr, "rom open fail\n"); return 2; }
	core = GBACoreCreate();
	core->init(core);
	mCoreInitConfig(core, NULL);
	core->loadROM(core, vf);
	core->baseVideoSize(core, &VW, &VH);
	buf = malloc((size_t) VW * VH * sizeof(mColor));
	core->setVideoBuffer(core, buf, VW);
	core->reset(core);

	if (argc > 3) doload(argv[3]);

	FILE* sc = !strcmp(argv[2], "-") ? stdin : fopen(argv[2], "r");
	if (!sc) { fprintf(stderr, "script open fail: %s\n", argv[2]); return 3; }

	char line[1024];
	while (fgets(line, sizeof line, sc)) {
		char* p = line;
		while (*p == ' ' || *p == '\t') p++;
		if (*p == '#' || *p == '\n' || *p == '\0' || *p == '\r') continue;
		char cmd[32];
		int adv = 0;
		if (sscanf(p, "%31s%n", cmd, &adv) != 1) continue;
		char* rest = p + adv;

		if (!strcmp(cmd, "key")) {
			uint32_t k = 0; char nm[32]; int a;
			char* q = rest;
			while (sscanf(q, "%31s%n", nm, &a) == 1) {
				if (!strcmp(nm, "-") || !strcmp(nm, "NONE")) { k = 0; }
				else k |= keybit(nm);
				q += a;
			}
			held = k;
			fprintf(stderr, "KEY 0x%03x\n", held);
		} else if (!strcmp(cmd, "call")) {
			/* call <addr> [r0 r1 r2 r3] : invoke a Thumb fn in isolation and run until it
			   returns. Saves/restores CPU regs+cpsr+prefetch; lr=sentinel, stop when PC hits it.
			   Set up memory with poke/dump first, then read results after. */
			uint32_t addr, a[4] = { 0, 0, 0, 0 };
			int na = sscanf(rest, "%i %i %i %i %i", &addr, &a[0], &a[1], &a[2], &a[3]);
			if (na >= 1) {
				struct ARMCore* c = wc();
				uint32_t sg[16]; for (int i = 0; i < 16; i++) sg[i] = c->gprs[i];
				union PSR scpsr = c->cpsr; enum ExecutionMode smode = c->executionMode;
				uint32_t spf0 = c->prefetch[0], spf1 = c->prefetch[1];
				const uint32_t SENT = 0x08000000u;
				for (int i = 0; i < 4; i++) c->gprs[i] = a[i];
				c->gprs[14] = SENT | 1; c->gprs[15] = addr & ~1u;
				c->cpsr.t = 1; c->executionMode = MODE_THUMB; c->memory.activeMask |= 2;
				ThumbWritePC(c);
				long steps = 0; const long MAX = 8000000;
				while (steps < MAX) {
					uint32_t pc = c->gprs[15];
					if (pc >= SENT && pc <= SENT + 8) break;
					ARMRun(c); steps++;
				}
				fprintf(stderr, "CALL 0x%08x(%x,%x,%x,%x) -> r0=0x%x r1=0x%x steps=%ld pc=0x%08x%s\n",
					addr, a[0], a[1], a[2], a[3], c->gprs[0], c->gprs[1], steps, c->gprs[15],
					steps >= MAX ? " [TIMEOUT]" : "");
				for (int i = 0; i < 16; i++) c->gprs[i] = sg[i];
				c->cpsr = scpsr; c->executionMode = smode;
				c->prefetch[0] = spf0; c->prefetch[1] = spf1;
				c->memory.activeMask = smode == MODE_THUMB ? (c->memory.activeMask | 2) : (c->memory.activeMask & ~2);
			}
		} else if (!strcmp(cmd, "frames")) {
			int n = atoi(rest);
			advance(n, held);
		} else if (!strcmp(cmd, "mash")) {
			/* blow through intro/dialogue: A 10f, START 10f, release 10f, repeat */
			int n = atoi(rest);
			for (int f = 0; f < n; f++) {
				int ph = (f / 10) % 3;
				core->setKeys(core, ph == 0 ? 0x1 : (ph == 1 ? 0x8 : 0));
				core->runFrame(core);
			}
			held = 0;
			fprintf(stderr, "MASH %d frames\n", n);
		} else if (!strcmp(cmd, "mashA")) {
			/* A-only masher: A 6f, release 6f, repeat. Advances all dialogue/naming
			   but NEVER opens the START menu, so it lands on a clean field. */
			int n = atoi(rest);
			for (int f = 0; f < n; f++) {
				core->setKeys(core, (f / 6) % 2 == 0 ? 0x1 : 0);
				core->runFrame(core);
			}
			held = 0;
			fprintf(stderr, "MASHA %d frames\n", n);
		} else if (!strcmp(cmd, "tap")) {
			char nm[32]; int h = 1, r = 1;
			sscanf(rest, "%31s %d %d", nm, &h, &r);
			advance(h, keybit(nm));
			advance(r, 0);
			held = 0;
			fprintf(stderr, "TAP %s h=%d r=%d\n", nm, h, r);
		} else if (!strcmp(cmd, "shot")) {
			char f[600]; if (sscanf(rest, "%599s", f) == 1) dump(f);
		} else if (!strcmp(cmd, "peek8") || !strcmp(cmd, "peek16") || !strcmp(cmd, "peek32")) {
			uint32_t a = (uint32_t) strtoul(rest, NULL, 0);
			int sz = cmd[4] == '8' ? 8 : (cmd[4] == '1' ? 16 : 32);
			uint32_t v = rd(a, sz);   /* single read: a read-side-effecting I/O reg must not be hit twice */
			fprintf(stderr, "PEEK 0x%08x = 0x%x (%u)\n", a, v, v);
		} else if (!strcmp(cmd, "poke8") || !strcmp(cmd, "poke16") || !strcmp(cmd, "poke32")) {
			uint32_t a, v;
			if (sscanf(rest, "%i %i", &a, &v) == 2) {
				int sz = cmd[4] == '8' ? 8 : (cmd[4] == '1' ? 16 : 32);
				wr(a, sz, v);
				fprintf(stderr, "POKE 0x%08x <= 0x%x\n", a, v);
			}
		} else if (!strcmp(cmd, "fill")) {
			/* fill <addr> <byte> <len> : write <byte> for <len> bytes (block memset) */
			uint32_t a, b, len;
			if (sscanf(rest, "%i %i %i", &a, &b, &len) == 3) {
				for (uint32_t i = 0; i < len; i++) wr(a + i, 8, b & 0xff);
				fprintf(stderr, "FILL 0x%08x <= 0x%02x x %u\n", a, b & 0xff, len);
			}
		} else if (!strcmp(cmd, "memcpy")) {
			/* memcpy <dst> <src> <len> : byte block-copy (e.g. clone a party Pokemon) */
			uint32_t d, s, len;
			if (sscanf(rest, "%i %i %i", &d, &s, &len) == 3) {
				for (uint32_t i = 0; i < len; i++) wr(d + i, 8, rd(s + i, 8));
				fprintf(stderr, "MEMCPY 0x%08x <- 0x%08x x %u\n", d, s, len);
			}
		} else if (!strcmp(cmd, "search")) {
			/* search <start> <end> <value> [8|16|32] : scan for a value, print matches.
			   Finds any global by its known value (gBattleTypeFlags, menu cursors, ...). */
			uint32_t start, end, val; int sz = 32;
			if (sscanf(rest, "%i %i %i %d", &start, &end, &val, &sz) >= 3) {
				int hits = 0, step = sz / 8;
				for (uint32_t a = start; a + step <= end && hits < 200; a += step) {
					if (rd(a, sz) == val) { fprintf(stderr, "  @0x%08x\n", a); hits++; }
				}
				fprintf(stderr, "SEARCH %d hit(s) for 0x%x [%d] in [0x%08x,0x%08x)\n", hits, val, sz, start, end);
			}
		} else if (!strcmp(cmd, "state")) {
			/* state : one-line interpretation of gMain.callback2 (Ash Gray values) +
			   party count + loc — saves a screenshot round-trip when probing flow. */
			uint32_t cb2 = core->busRead32(core, 0x030030f4u);
			const char* s = cb2 == 0x080565b5u ? "FIELD-IDLE" : cb2 == 0x08011101u ? "BATTLE" :
			                cb2 == 0x0811eba1u ? "PARTY-MENU" : cb2 == 0x0812eb11u ? "MAIN-MENU" : "?";
			uint32_t sb1 = core->busRead32(core, GSAVEBLOCK1PTR);
			fprintf(stderr, "STATE cb2=0x%08x (%s) party=%u loc=%u.%u(%u,%u)\n", cb2, s,
				core->busRead8(core, 0x02024029u), core->busRead8(core, sb1 + 4),
				core->busRead8(core, sb1 + 5), core->busRead16(core, sb1 + 0), core->busRead16(core, sb1 + 2));
		} else if (!strcmp(cmd, "deref")) {
			uint32_t pa, off; int sz = 32;
			if (sscanf(rest, "%i %i %d", &pa, &off, &sz) >= 2) {
				uint32_t base = core->busRead32(core, pa);
				fprintf(stderr, "DEREF *0x%08x=0x%08x +0x%x [%d] = 0x%x\n",
					pa, base, off, sz, rd(base + off, sz));
			}
		} else if (!strcmp(cmd, "watch") || !strcmp(cmd, "rwatch")) {
			/* watch|rwatch <addr> [len] : trace writes|reads into [addr,addr+len) */
			uint32_t a, len = 1;
			if (sscanf(rest, "%i %i", &a, &len) >= 1)
				watch_add(a, a + len, cmd[0] == 'r' ? WT_READ : WT_WRITE, 0, 0);
		} else if (!strcmp(cmd, "watchif") || !strcmp(cmd, "rwatchif")) {
			/* watchif <addr> <len> <eq|ne|gt|lt|ge|le> <val> : fire only when value matches */
			uint32_t a, len; char ops[8]; uint32_t val;
			if (sscanf(rest, "%i %i %7s %i", &a, &len, ops, &val) == 4)
				watch_add(a, a + len, cmd[0] == 'r' ? WT_READ : WT_WRITE, parse_op(ops), val);
		} else if (!strcmp(cmd, "watchvar")) {
			/* watchvar <id> : trace writes to FRLG var <id> (sb1+0x1000+2*(id-0x4000)) */
			uint32_t id;
			if (sscanf(rest, "%i", &id) == 1) { uint32_t a = varaddr(id); fprintf(stderr, "watchvar 0x%x @0x%08x\n", id, a); watch_add(a, a + 2, WT_WRITE, 0, 0); }
		} else if (!strcmp(cmd, "watchderef")) {
			/* watchderef <ptraddr> <off> [len] : base=*ptraddr; watch [base+off, +len) */
			uint32_t pa, off, len = 1;
			if (sscanf(rest, "%i %i %i", &pa, &off, &len) >= 2) {
				uint32_t base = core->busRead32(core, pa);
				fprintf(stderr, "WATCHDEREF *0x%08x=0x%08x +0x%x\n", pa, base, off);
				watch_add(base + off, base + off + len, WT_WRITE, 0, 0);
			}
		} else if (!strcmp(cmd, "var")) {
			/* var <id> : print FRLG var value */
			uint32_t id;
			if (sscanf(rest, "%i", &id) == 1) { uint32_t a = varaddr(id); fprintf(stderr, "VAR 0x%x @0x%08x = 0x%x\n", id, a, core->busRead16(core, a)); }
		} else if (!strcmp(cmd, "pokevar")) {
			/* pokevar <id> <val> */
			uint32_t id, v;
			if (sscanf(rest, "%i %i", &id, &v) == 2) { uint32_t a = varaddr(id); core->busWrite16(core, a, (uint16_t) v); fprintf(stderr, "POKEVAR 0x%x @0x%08x <= 0x%x\n", id, a, v); }
		} else if (!strcmp(cmd, "flag")) {
			/* flag <id> : print FRLG flag bit */
			uint32_t id;
			if (sscanf(rest, "%i", &id) == 1) { uint32_t a = flagbyte(id); int bit = (core->busRead8(core, a) >> (id & 7)) & 1; fprintf(stderr, "FLAG 0x%x @0x%08x bit%d = %d\n", id, a, id & 7, bit); }
		} else if (!strcmp(cmd, "pokeflag")) {
			/* pokeflag <id> <0|1> */
			uint32_t id, set;
			if (sscanf(rest, "%i %i", &id, &set) == 2) { uint32_t a = flagbyte(id); uint8_t b = core->busRead8(core, a); b = set ? (b | (1 << (id & 7))) : (b & ~(1 << (id & 7))); core->busWrite8(core, a, b); fprintf(stderr, "POKEFLAG 0x%x @0x%08x bit%d <= %d\n", id, a, id & 7, set ? 1 : 0); }
		} else if (!strcmp(cmd, "unwatch")) {
			n_watch = 0; n_seen = 0; log_cap = 0; fprintf(stderr, "WATCH cleared\n");
		} else if (!strcmp(cmd, "regs")) {
			print_regs(wc());
		} else if (!strcmp(cmd, "trace")) {
			/* trace <n> : step n instructions, histogram the PC, print hottest.
			   A frozen game shows few distinct PCs in a tiny range = the spin loop. */
			long n = atol(rest); if (n <= 0) n = 200000;
			struct ARMCore* c = wc();
			enum { HN = 16384 };
			static uint32_t hpc[HN]; static uint32_t hct[HN];
			for (int i = 0; i < HN; i++) { hpc[i] = 0; hct[i] = 0; }
			uint32_t minpc = 0xffffffffu, maxpc = 0; int distinct = 0;
			for (long s = 0; s < n; s++) {
				uint32_t pc = c->gprs[15];
				if (pc < minpc) minpc = pc; if (pc > maxpc) maxpc = pc;
				uint32_t h = (pc * 2654435761u) >> 18;
				for (int probe = 0; probe < HN; probe++) {
					uint32_t idx = (h + probe) & (HN - 1);
					if (hct[idx] == 0) { hpc[idx] = pc; hct[idx] = 1; distinct++; break; }
					if (hpc[idx] == pc) { hct[idx]++; break; }
				}
				ARMRun(c);
			}
			fprintf(stderr, "TRACE n=%ld distinctPC=%d range[0x%08x,0x%08x] span=%u\n",
				n, distinct, minpc, maxpc, maxpc - minpc);
			for (int top = 0; top < 24; top++) {
				int best = -1; uint32_t bc = 0;
				for (int i = 0; i < HN; i++) if (hct[i] > bc) { bc = hct[i]; best = i; }
				if (best < 0 || bc == 0) break;
				fprintf(stderr, "  #%2d pc=0x%08x  %u  (%.1f%%)\n", top, hpc[best], bc, 100.0 * bc / n);
				hct[best] = 0;
			}
			print_regs(c);
		} else if (!strcmp(cmd, "stepto")) {
			/* stepto <addr> [maxsteps] : faithfully run until PC enters [addr,addr+6]. */
			uint32_t target; long mx = 5000000;
			if (sscanf(rest, "%i %li", &target, &mx) >= 1) {
				struct ARMCore* c = wc(); long s = 0; int hit = 0;
				for (; s < mx; s++) {
					uint32_t pc = c->gprs[15] & ~1u;
					if (pc >= (target & ~1u) && pc <= (target & ~1u) + 6) { hit = 1; break; }
					ARMRun(c);
				}
				fprintf(stderr, "STEPTO 0x%08x %s after %ld steps\n", target, hit ? "HIT" : "MISS(timeout)", s);
				print_regs(c);
			}
		} else if (!strcmp(cmd, "warpto")) {
			/* Poke the save-block warp destination so a subsequent in-game save + reset +
			   Continue spawns on this map. args: mapGroup mapNum x y */
			int g, n, x, y, lid = -1;
			int cnt = sscanf(rest, "%i %i %i %i %i", &g, &n, &x, &y, &lid);
			if (cnt >= 4) {
				uint32_t base = core->busRead32(core, GSAVEBLOCK1PTR);
				core->busWrite16(core, base + 0, (uint16_t) x);   /* pos.x */
				core->busWrite16(core, base + 2, (uint16_t) y);   /* pos.y */
				/* write the WarpData {mapGroup,mapNum,warpId,_,x,y} to EVERY spawn
				   source: location(0x04), continueGameWarp(0x0C), dynamicWarp(0x14),
				   lastHealLocation(0x1C), escapeWarp(0x24). FR's Continue can redirect
				   to lastHealLocation via SaveBlock2.specialSaveWarpFlags — clear it. */
				uint32_t slots[5] = { base + 0x04, base + 0x0C, base + 0x14,
				                      base + 0x1C, base + 0x24 };
				for (int s = 0; s < 5; s++) {
					uint32_t w = slots[s];
					core->busWrite8(core, w + 0, (uint8_t) g);
					core->busWrite8(core, w + 1, (uint8_t) n);
					core->busWrite8(core, w + 2, 0xFF);
					core->busWrite16(core, w + 4, (uint16_t) x);
					core->busWrite16(core, w + 6, (uint16_t) y);
				}
				uint32_t sb2 = core->busRead32(core, 0x0300500Cu);
				uint8_t ssw = core->busRead8(core, sb2 + 0x09);
				core->busWrite8(core, sb2 + 0x09, 0);  /* specialSaveWarpFlags = 0 */
				/* Continue draws TILES from SaveBlock1.mapLayoutId (+0x32), not from the
				   location's header — must match the target map or you get the old map's
				   tiles with the new map's events. */
				if (lid >= 0) core->busWrite16(core, base + 0x32, (uint16_t) lid);
				/* zero mapView (+0x34, 0x100 u16) — else Continue pastes the saved
				   around-the-save-point blocks over the new map (SavedMapViewIsEmpty
				   gates the paste). */
				for (int i = 0; i < 0x200; i++) core->busWrite8(core, base + 0x34 + i, 0);
				fprintf(stderr, "WARPTO map=%d.%d pos=(%d,%d) layout=%d sb1=0x%08x sb2=0x%08x sswf(was 0x%02x)=0\n",
					g, n, x, y, lid, base, sb2, ssw);
			}
		} else if (!strcmp(cmd, "dumpsb")) {
			/* hex-dump n bytes from *gSaveBlock1Ptr to spot WarpData fields */
			int n = atoi(rest); if (n <= 0 || n > 256) n = 64;
			uint32_t base = core->busRead32(core, GSAVEBLOCK1PTR);
			fprintf(stderr, "DUMPSB sb1=0x%08x:", base);
			for (int i = 0; i < n; i++) {
				if (i % 16 == 0) fprintf(stderr, "\n  +0x%02X:", i);
				fprintf(stderr, " %02x", core->busRead8(core, base + i));
			}
			fprintf(stderr, "\n");
		} else if (!strcmp(cmd, "dump")) {
			/* hex-dump n bytes from an absolute address: dump <addr> <len> */
			uint32_t pa; int n;
			if (sscanf(rest, "%i %i", &pa, &n) == 2) {
				if (n > 4096) n = 4096;
				fprintf(stderr, "DUMP 0x%08x:", pa);
				for (int i = 0; i < n; i++) {
					if (i % 16 == 0) fprintf(stderr, "\n  +0x%03X:", i);
					fprintf(stderr, " %02x", core->busRead8(core, pa + i));
				}
				fprintf(stderr, "\n");
			}
		} else if (!strcmp(cmd, "dump1")) {
			/* hex-dump n bytes from *gSaveBlock1Ptr + off (sb1 moves across
			   warps/battles — this follows it): dump1 <off> <len> */
			uint32_t off; int n;
			if (sscanf(rest, "%i %i", &off, &n) == 2) {
				if (n > 4096) n = 4096;
				uint32_t base = core->busRead32(core, GSAVEBLOCK1PTR);
				fprintf(stderr, "DUMP1 sb1=0x%08x +0x%x:", base, off);
				for (int i = 0; i < n; i++) {
					if (i % 16 == 0) fprintf(stderr, "\n  +0x%03X:", i);
					fprintf(stderr, " %02x", core->busRead8(core, base + off + i));
				}
				fprintf(stderr, "\n");
			}
		} else if (!strcmp(cmd, "loc")) {
			uint32_t base = core->busRead32(core, GSAVEBLOCK1PTR);
			uint16_t x = core->busRead16(core, base + 0);
			uint16_t y = core->busRead16(core, base + 2);
			uint8_t mg = core->busRead8(core, base + 4);
			uint8_t mn = core->busRead8(core, base + 5);
			fprintf(stderr, "LOC sb1=0x%08x map=%u.%u pos=(%u,%u)\n", base, mg, mn, x, y);
		} else if (!strcmp(cmd, "flash1m")) {
			/* Force the cartridge save type to Flash 128K (2 banks) — FireRed's type.
			   Without this, autodetect can pick 64K and the in-game save hangs at
			   "SAVING..." (bank-1 writes never verify). Issue before the first save. */
			struct GBA* gba = (struct GBA*) core->board;
			GBASavedataForceType(&gba->memory.savedata, GBA_SAVEDATA_FLASH1M);
			fprintf(stderr, "FLASH1M forced\n");
		} else if (!strcmp(cmd, "savfile")) {
			/* Attach a 128KB (Flash1M) save file so in-game saves complete instead of
			   hanging at "SAVING...", and persist across reset. Issue before any save. */
			char f[600];
			if (sscanf(rest, "%599s", f) == 1) {
				FILE* sf = fopen(f, "rb");
				long sz = 0;
				if (sf) { fseek(sf, 0, SEEK_END); sz = ftell(sf); fclose(sf); }
				if (sz < 0x20000) {
					FILE* w = fopen(f, sz > 0 ? "r+b" : "wb");
					if (w) { fseek(w, 0, SEEK_END);
						for (long i = sz; i < 0x20000; i++) fputc(0xFF, w);
						fclose(w); }
				}
				struct VFile* sv = VFileOpen(f, O_RDWR);
				if (sv && core->loadSave(core, sv)) fprintf(stderr, "SAVFILE %s (flash 128K)\n", f);
				else fprintf(stderr, "SAVFILE fail %s\n", f);
			}
		} else if (!strcmp(cmd, "savedbg")) {
			struct GBASavedata* sd = &((struct GBA*) core->board)->memory.savedata;
			size_t sz = GBASavedataSize(sd);
			fprintf(stderr, "SAVEDBG type=%d size=%zu mapMode=%d dirty=%d data=%p vf=%p first32:",
				sd->type, sz, sd->mapMode, sd->dirty, (void*) sd->data, (void*) sd->vf);
			for (int i = 0; i < 32 && sd->data; i++) fprintf(stderr, " %02x", sd->data[i]);
			fprintf(stderr, "\n");
		} else if (!strcmp(cmd, "savesync")) {
			/* flush the in-memory savedata buffer out to the backing vfile so it
			   survives a reset (the in-game save leaves it dirty/unflushed). */
			struct GBASavedata* sd = &((struct GBA*) core->board)->memory.savedata;
			GBASavedataClean(sd, 0xFFFFFFFFu);
			size_t sz = GBASavedataSize(sd);
			if (sd->vf && sd->data && sz) sd->vf->sync(sd->vf, sd->data, sz);
			fprintf(stderr, "SAVESYNC type=%d size=%zu dirty=%d\n", sd->type, sz, sd->dirty);
		} else if (!strcmp(cmd, "reset")) {
			/* soft-reset the GBA (console reset button). Flush savedata to the vfile
			   FIRST so an in-game save survives the reset -> CONTINUE appears. */
			struct GBASavedata* sd = &((struct GBA*) core->board)->memory.savedata;
			GBASavedataClean(sd, 0xFFFFFFFFu);
			size_t sz = GBASavedataSize(sd);
			if (sd->vf && sd->data && sz) sd->vf->sync(sd->vf, sd->data, sz);
			core->reset(core);
			core->setVideoBuffer(core, buf, VW);  /* renderer re-inits on reset */
			held = 0;
			fprintf(stderr, "RESET (savedata flushed %zu B)\n", sz);
		} else if (!strcmp(cmd, "save")) {
			char f[600]; if (sscanf(rest, "%599s", f) == 1) dosave(f);
		} else if (!strcmp(cmd, "load")) {
			char f[600]; if (sscanf(rest, "%599s", f) == 1) doload(f);
		} else if (!strcmp(cmd, "log")) {
			fprintf(stderr, "LOG %s", rest);
		} else {
			fprintf(stderr, "?? unknown cmd: %s\n", cmd);
		}
	}
	if (sc != stdin) fclose(sc);
	printf("%u %u\n", VW, VH);
	return 0;
}
