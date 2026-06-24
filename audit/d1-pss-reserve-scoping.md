# D1 reserve fix — PC storage system (PSS) scoping (2026-06-13)

Goal: permanently block deposits/viewing into the hazard boxes (Box 2 tail, Box 3, Box 6) so the
var↔storage overlap can never corrupt — the source-level cure for the whole D1 storage-overlap class.

## Feasibility: CONFIRMED

The PSS is standard FRLG and fully disassemblable (capstone). Mapped this session:

- **`gPokemonStoragePtr`** @ EWRAM `0x03005010` → storage buffer = `sb1 + 0x3DE8` (verified live).
  Struct is vanilla: `currentBox`(u8)@+0, `boxes[14][30]` (BoxPokemon, 80 B) @+4, names @+0x8344.
- **PSS UI module:** `0x0808c000–0x08093000` (task-driven state machine).
  - work-struct pointer **`sStorage`** @ EWRAM `0x020397b0`; state byte @ `sStorage[0]`;
    **displayed/scroll-target box** @ `sStorage + 0x2CA` (u8).
- **`GetCurrentBoxIndex()`** @ `0x0808b9f4` — returns `gPokemonStorage.currentBox` (32 callers).
- **`SetCurrentBox(boxId)`** @ `0x0808ba00` — bounds-checks `≤13`, writes `currentBox`. **Only 3 callers**
  (`0x0808c7e4` sets box 0 = init; `0x0808d686` & `0x0808ea76` sync `sStorage+0x2CA → currentBox`).
- **`SetUpScrollToBox(boxId)`** @ `0x08091514` — sets scroll params toward a target box; calls the
  **direction helper** @ `0x080916f4` which does `box+1 mod 14` step-counting from `GetCurrentBoxIndex`.
- **Box-slot accessors** (`0x0808ba18` family): the `&boxes[boxId][slot]` math (`×5,×16,−,×32,+4` then
  `slot×80`) is **inlined per-accessor** — there is no single `GetBoxedMonPtr` choke point.

## EMPIRICAL CONFIRMATION (2026-06-13, live UI + memory watch) ✅

Reached the box-storage UI in-engine and traced the box-cycle by hand. The PokéCenter PC menu is
custom — boot text "…booted up the PC." → "Which PC should be accessed?" → multichoice
**`OAK'S LAB` / `MY PC` / `PROF. OAK'S PC` / `LOG OFF`**. **`OAK'S LAB` = the Pokémon box storage**
(replaces stock "SOMEONE'S PC"); it opens the standard FRLG `WITHDRAW/DEPOSIT/MOVE/MOVE ITEMS/SEE YA!`
submenu and the vanilla box-grid view.

- **Box-cycle UI control:** press **UP** to move the cursor onto the box-title bar (the d-pad LEFT/RIGHT
  inside the grid just wrap within the row), then **LEFT/RIGHT** cycles boxes. (`L`/`R` shoulders are the
  **HELP** system here, not box-cycle.)
- **Live pointers (in-box-view):** `sStorage = *(0x020397b0) = 0x02003208`;
  **displayed/scroll box = `[sStorage + 0x2CA]` = `0x020034d2`** (u16; idle value is junk, set to the box
  index on first navigation). `gPokemonStorage = sb1+0x3DE8 = 0x02029344`, `currentBox = [0x02029344]`.
- **`GetCurrentBoxIndex` @0x0808b9f4** = `ldr =0x03005010; ldr; ldrb` → returns **`currentBox`** (NOT
  sStorage+0x2CA — corrects earlier note). Both nav handlers read committed `currentBox`, step, write the
  UI scroll-target, and the scroll later commits it back.
- **RIGHT (forward) handler @0x0808d462** (watch fired pc=0x0808d474 strh, val 0→1): `box=GetCurrentBoxIndex();
  box+1; strh box,[sStorage+0x2CA]; if box>13 → strh 0`. Continues at 0x0808d47e.
- **LEFT (backward) handler @0x0808d49a** (watch fired pc=0x0808d4ac strh 0xffff, then pc=0x0808d4b4 strh 0xd):
  `box=GetCurrentBoxIndex(); box-1; strh; if box<0 → strh 13`. Continues at 0x0808d4b6. LEFT from BOX1→BOX14 ✓.
- **Commit @0x0808d67c** (watch fired pc=0x0808ba0e strb, lr=0x0808d68b): `SetCurrentBox([sStorage+0x2CA])`
  → `currentBox = uiBox` (clamped ≤13). Confirmed: cycling BOX1→BOX2→BOX3 advanced currentBox 0→1→2.

Both inline step sites have **identical structure** (only +1/wrap-0 vs −1/wrap-13). 16 contiguous patchable
bytes each: RIGHT `0x0808d46e–0x0808d47d`, LEFT `0x0808d4a6–0x0808d4b5`.

## THE FIX — built & proven (`_emu/fix_boxreserve.py`, 2026-06-13)

Hazard boxes = **indices {1, 2, 5}** (Box 2 / Box 3 / Box 6; full-box reserve, not slot-level — wastes
Box 2's 27 safe slots but far simpler). Two free-space leaf helpers skip them (usable boxes 14→11):
- **`NextSafeFwd`** @`0x08197600`: `do { box=(box+1)%14 } while box∈{1,2,5}` (only touches r0).
- **`PrevSafeBwd`** @`0x08197616`: `do { box=(box-1)%14 } while box∈{1,2,5}`.
- Free space MUST be BL-reachable: `0x0C00150` is >4MB from PSS code (out of Thumb-BL ±4MB range, and
  ARM7TDMI has no BLX-reg). Used `0x08197600` (43KB FF run, ~1MB away, in range). All BLs verified.

**Six hook sites** (each replaces the inline `box±1`+wrap with a BL to a helper):
| # | site | what | helper | status |
|---|------|------|--------|--------|
| 1 | `0x0808d46e` | MOVE/box-view RIGHT nav | NextSafeFwd | ✅ UI-proven (BOX1→4→5→7) |
| 2 | `0x0808d4a6` | MOVE/box-view LEFT nav | PrevSafeBwd | ✅ UI-proven (BOX7→5→4→1→14) |
| 3 | `0x08040c1a` | auto-deposit scan A (give-mon `CopyMonToPC`) | NextSafeFwd | ✅ runtime-proven (BOX1 full → mon→BOX4, BOX2/3 untouched) |
| 4 | `0x080cc85e` | auto-deposit scan B (storage) | NextSafeFwd | ✅ byte-identical hook to A + runs clean |
| 5 | `0x0808cc1e` | "Deposit in which BOX?" fwd (ChooseBoxMenu) | NextSafeFwd | ✅ UI-proven |
| 6 | `0x0808cc4e` | "Deposit in which BOX?" bwd (ChooseBoxMenu) | PrevSafeBwd | ✅ UI-proven (0→3→4→3→0) |

**Real-testing caught two things assumption would have missed:**
- DEPOSIT mode does NOT reuse the main 0x0808d462/0x49a handlers. STORE → **"Deposit in which BOX?"**
  selector is a **separate `ChooseBoxMenu`** (box index @`*(0x020397ac)+0x244`, fwd @0x0808cc10 / bwd
  @0x0808cc44). Without hooks 5/6 a player could deposit straight into Box 2/3 (verified: it went BOX1→BOX2→BOX3).
- The ChooseBoxMenu **backward handler embeds its literal-pool word `0x020397ac` at `0x0808cc5c`** (read by
  its own `ldr r0,[pc,#0x14]` @0x0808cc46, skipped at runtime by the original's branches). The hook MUST
  preserve those 4 bytes and branch over them — NOP-filling them corrupts the struct pointer and silently
  no-ops LEFT. (Forward handler's literal is @0x0808cc40, before its hook, so it was unaffected.)

## Post-ship verification pass (2026-06-14) — placement-prevention scope SEALED

- **Boot (real distribution path):** `patcher.py firered.gba ashgray-fork.ips` → boots from scratch,
  shows Ash Gray's custom intro + Oak speech, runs clean. crc `f4ee7240` (== fork ROM). ✅
- **All-boxes-full edge:** filled all 11 usable boxes, left reserved boxes open, called scan A → returns
  `r0=2` ("full") and **Box 2/3/6 stay empty** — refuses reserved boxes even when desperate, hands off to
  the game's storage-full path. No crash/timeout. ✅
- **Every box-SELECTION path audited:** nav step (hooked), ChooseBoxMenu step (hooked), auto-deposit
  advance (hooked), and the scroll/commit path `0x0808ea44`/`0x0808d686` (reads the *already-safe*
  `sStorage+0x2CA`, no independent ±1). `SetCurrentBox` init sets box 0. No unhooked selection path. ✅
- New rig capabilities used: `call <addr> [r0..r3]` (invoke any Thumb fn in isolation) and `fill`.

## The marker-READ side — investigated to closure: BENIGN (2026-06-14)

**CORRECTION of an earlier over-claim in this doc.** A prior draft said a var-garbage reserved-box slot
"reads back as species 0x19c (Bad Egg)" and that "all-box scans still see Bad Eggs." **That was wrong —
it read the wrong field.** `GetBoxMonData(MON_DATA_SPECIES=0xB)` does return junk (`0x19c`) for a
garbage slot, but the game never uses that to decide occupancy. The real occupancy test is the
**has-species SANITY bit** (`field 5`, BoxPokemon offset 0x13 bit 1), and that reads **0 = empty** for
var-garbage — verified for realistic AND worst-case writes (`gen_field5_test.py`). So the var-garbage in
an empty reserved box is **invisible** to the game: it is *not* a displayable Bad Egg, and all-box scans
that gate on the sanity bit treat those slots as empty.

**The one all-box scan, identified and tested.** `0x08111574` (nested box×slot via `0x0808ba18`) turned
out to be the **FireRed Quest Log** ("Previously on your quest.." recap) — `0x0811xxxx` is the Quest Log
module; the scan is its state-clear: *for each box/slot, if field-5 ≠ 0 → `ZeroBoxMon` (0x0803d97c)*.
Because var-garbage reads field 5 = 0, the Quest Log **skips the reserved boxes entirely** — does not
erase them, does not touch the overlapping vars, does not pull anything into the party (party is restored
from the Quest Log's own snapshot buffer, never from a box scan). **Benign.** (special 0x187, a red
herring, is a trivial getter — unrelated.)

**Narrow edge (pre-existing, not introduced here):** *if* a story var ever wrote slot offset 0x12–0x13
with bit `0x0200` set, that slot would read "occupied" and the Quest Log clear would zero it, wiping that
one var (`gen_hasspecies_test.py` demonstrated `0x0003 → 0x0000`). A specific coincidence; couldn't be
triggered with realistic garbage; identical with or without this patch; same GATE-class as existing D1.

**Why the box-reserve fix is correctly shaped:** a *real* Bad Egg requires a *real* Pokémon in a hazard
box (sanity bit = 1) whose data a var-write then corrupts (checksum fails → Bad Egg). This fix prevents
exactly that — no real Pokémon ever lands there. The leftover var-garbage in the now-permanently-empty
hazard boxes reads as empty and is inert to the Quest Log and every other sanity-gated all-box scan. So
there is **no live read-side residual** to close; var-relocation would still be the only way to stop the
underlying writes, but they land in dead, empty-reading space.

## Migration caveat
A save made pre-patch with a mon already in Box 2/3/6 (or `currentBox` parked on a hazard box) is not
retroactively fixed — the fix prevents NEW placements. Fresh playthroughs are fully covered.

## Trace harness (done)

`rig.c` write/read watchpoints (`watch`/`watchderef`/`rwatch`) pin the exact box functions by navigating
the live UI: `watchderef 0x020397b0 0x2ca 1` then press RIGHT/LEFT and read `WATCH … pc=… lr=…`. Reusable
states: `pc_atpc.ss` (facing PC), `pc_oakmenu.ss` (PC menu), `pc_submenu.ss` (storage menu),
`pc_boxgrid.ss` (box grid BOX1), `pc_title.ss` (cursor on box title, ready to cycle).

## Honest scope

This is a real multi-step ARM/Thumb project (PSS is large + task-driven), not a one-shot patch:
(1) build the PC-UI trace harness, (2) pin the cycle + auto-deposit selectors by tracing,
(3) write the skip-hazard Thumb hooks, (4) test in-engine. Feasible and now well-understood — but
several focused passes. Tooling: `find_bl.py` (alignment-correct Thumb-BL caller finder),
`disasm_pss.py` (Thumb disasm + literal resolve).
