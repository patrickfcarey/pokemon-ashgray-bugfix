# Ash Gray — pure-ROM control-flow softlock audit (lock/release imbalance, waitstate/waitmovement, ON_TRANSITION)

Scope: scripts that permanently freeze / input-lock the PLAYER on a FRESH, uncorrupted save,
independent of any var/box corruption (box-fix-IMMUNE). Reachability-aware static analysis
(not a raw opcode-byte scan), confirmed per-finding by decompilation and, for the confirmed
case, by in-engine reproduction on the libmgba rig.

ROM under test: `rom/ashgray.gba`  (md5 43216f9fa86e9bbecb118d6203ef83c2), base 0x08000000.

---

> ### ⛔ CORRECTION (independent in-engine re-test, 2026-06-16) — FINDING 1 RETRACTED, FALSE POSITIVE
> Finding 1 ("confirmed first-sleep freeze") **does NOT reproduce on the real play path** and is a
> false positive. Re-tested by driving the *genuine* dresser→bed sequence from the legit
> `checkpoint.ss` (NO flag-poking): real dresser sets `0x1166`, real bed interaction runs the dream
> (`0x1006` 0→1), and after **fully** advancing the dialogue (`mashA 1800`) the player **wakes,
> stands up out of bed, and walks freely** — LOC moved (3,5)→(4,5)→(4,4)→(3,4); screenshot
> `_emu/rt_mobility.png` shows Ash standing in pajamas, no textbox, normal field control.
> The apparent "freeze" was the dream's final `callstd 4` "…woke up from his restless sleep."
> message **waiting for a button press**: the original repro under-advanced it (`mashA 700`) and then
> tested mobility with **direction keys, which cannot dismiss a textbox**, so LOC looked stuck.
> The dream script is **byte-identical to the completable clean 4.5.3** (diffed) — consistent with
> "it works." **No freeze, no fix needed.** (See ISSUES.md session log for the full re-test.)

## BOTTOM LINE

- **~~1 CONFIRMED freeze~~ → RETRACTED (false positive, see correction above):** the first-sleep
  starter-dream on map 4.1 does **not** freeze; the player wakes and regains control normally once
  the final "woke up" textbox is dismissed. The static `lock`+`end`-without-`release` pattern did
  not produce a real freeze in-engine on the genuine path.
- **1 CANDIDATE, unconfirmed** (latent, high suspicion, not reproduced): map **5.4** Nugget-Bridge
  trigger `0x800680` — a malformed `goto_if cond=1 -> 0x8007D8` lands on `FF FF` (engine stops
  gracefully) *after* `lockall`, on the path taken once flag **0x575** is set. Freeze requires
  0x575 set (post-wild-battle) + re-stepping a bridge tile; I could not prove the reachable
  walk-back, so it is labelled candidate.
- **0 other freezes.** The other 16 candidate scripts surfaced by the scan are all the SAME
  benign vanilla-FRLG idiom: a value-dispatch ladder (multichoice / yesno / menu-special) whose
  every real choice releases, with a defensive bare `end` as the unreachable post-`0x7F` default.
  None is reachable on real data. Detail + list below.
- waitstate/waitmovement (pattern 2): no clear hang found. ON_TRANSITION/ON_LOAD (pattern 3):
  the only type-3 map-entry script that fits the net (4.1 type-3 @0x81A50D) just sets respawn
  vars and is harmless; the confirmed bug is a type-2 *bed sign*, not a map-entry script.

---

## METHOD

- Roots (reachability seeds), per the `tools/scan_dead_scripts.py` / `tools/decomp.py`
  convention: every map's person events (stride 24, script @+16), triggers (stride 16, @+12),
  signs (stride 12, @+8 when kind<5); every mapscript subtable script (header @ map_header+8;
  type 1/3 = direct script, type 2/4 = `{u16 var,u16 val,u32 script}` subtables); the 10
  gStdScripts @0x08160450. Bank table pointer @ file offset 0x5524C. 3249 roots gathered.
- Inter-procedural lock-state walk: each script is explored as a graph; state = (offset, locked,
  cleared, call-stack). `lock`/`lockall` set locked; `release`/`releaseall`, any `warp*`, and any
  battle (`trainerbattle`/`dowildbattle`) set cleared (the engine auto-releases the player on
  map/state change). A finding = a path that reaches a terminator (`end`/`return`/`returnram`/
  `endram`) while locked-and-not-cleared and NOT immediately followed by warp/battle.
- **gStdScripts release-modeling (key to suppressing false positives):** the std scripts at
  0x08160450 were decompiled. `callstd 2` (0x1A73BB), `callstd 3` (0x1A73C7), `callstd 6`
  (0x1A73E6) each contain `release`/`releaseall`; `callstd 4` (0x1A73D2) and `callstd 5`
  (0x1A73DB) do NOT. Modeling `callstd 2/3/6` as releasing collapsed the raw 45 candidate
  scripts to 18. Every opcode byte relied on (lock 0x6A, lockall 0x69, release 0x6C, releaseall
  0x6B, applymovement 0x4F, waitmovement 0x51, waitstate 0x27, warp 0x39 / warpsilent 0x3A /
  warpdoor 0x3B / warphole 0x3C / warpteleport 0x3D / warpspinenter 0xD1, end 0x02, return 0x03)
  was checked against the authoritative table in `tools/decomp.py`.
- Engine facts relied on (given, not re-derived): an out-of-range/garbage opcode just STOPS the
  script gracefully (no freeze) — so a dangling pointer only freezes if a real blocking command
  (here `lock`/`lockall`) executed first on that path.
- Scanner: `/tmp/freeze_scan.py`. Per-candidate proof: `/tmp/decompA.py` (private copy of
  `tools/decomp.py`, writes `/tmp/decompA.md`; `audit/06-decompile.md` was NOT touched).
- In-engine confirmation rig scripts: `_emu/dream_repro4.rig` (+ dream_repro/2/3, dream_probe)
  driven from `_emu/checkpoint.ss` (post-intro bedroom save).

---

## FINDING 1 — CONFIRMED FREEZE: first-sleep starter-dream, map 4.1 (Ash's bedroom)

**Player-facing symptom:** After changing into pajamas, the player goes to bed for the first
time; the "dream about your first POKéMON" sequence plays (BULBASAUR/SQUIRTLE/CHARMANDER), then
the screen fades to black on "{PLAYER} woke up from his restless sleep." and **never returns** —
the player is permanently input-locked on a black screen. This is the very first scripted sleep,
on a clean save, so it is box-fix-immune and game-blocking for the path that hits it.

**Trigger:** map 4.1 bg/sign event **sign4**, kind=2 (`PLAYER_FACING_SOUTH`) at tile **(3,6)**
(the bed). Reproduced by standing on **(3,5)** above the bed, facing **down**, pressing **A**.
- Sign event record (map 4.1 bg events @0x0873061C): `x=3 y=6 elev=0 kind=2 script=0x0884C0B0`.

**Decompiled exit-path proof** (`/tmp/decompA.py 0x84C0B0`):

```
; sign4 @0x84C0B0
  0x84C0B0: lock                         <-- player locked here (byte 0x6A)
  0x84C0B1: checkflag 0x1166             <-- 0x1166 = "wearing pajamas"
  0x84C0B4: goto_if cond=1 -> 0x8085DB
  0x84C0BA: ..."can't go to bed until pajamas"; callstd 4; release; end   (0x1166 CLEAR path: OK, releases)

; 0x8085DB  (0x1166 SET)
  0x8085DB: checkflag 0x1006             <-- 0x1006 = "dream already seen"
  0x8085DE: goto_if cond=0 -> 0x800057   <-- DREAM (first time)
  0x8085E4: ..."no time to sleep now!"; callstd 6; end   (0x1006 SET path: OK, callstd 6 releases)

; 0x800057  THE DREAM
  0x800057: setflag 0x1006               <-- marks dream seen
  ... showmonpic / playmoncry x3 (BULBASAUR/SQUIRTLE/CHARMANDER), all via callstd 4 (NO release)
  0x8000AD: fadescreen (fade to black)
  0x8000AF: loadword "...woke up from his restless sleep."
  0x8000B5: callstd 4                     <-- std4 does NOT release
  0x8000B7: closemessage
  0x8000B8: end                           <-- TERMINATES with lock still held, screen black
```

Byte-level confirmation: `sign4@0x84C0B0 = 0x6A (lock)`; the dream body 0x800057..0x8000B8
contains **no** `releaseall` (0x6B), **no** `release` (0x6C), and **no** warp
(0x39–0x3D/0xD1); it ends at `0x8000B8 = 0x02 (end)`. So on the (0x1166 set, 0x1006 clear) path
— exactly the first sleep in pajamas — the script ends locked with no release and no warp.

**Flag lifecycle (proves the path is the normal first-sleep, fresh-save reachable):**
- 0x1166 ("pajamas") is set in normal play only by the dresser person1 @0x84AA7D
  (`...changed into his pajamas; callstd 6; setflag 0x1166; warpsilent (refresh same room);
  releaseall`). Checked only by sign4 @0x84C0B1.
- 0x1006 ("dream seen") is clear on a fresh save; the dream itself sets it at 0x800057.
- The room's trigger trig0 @0x8189BB would `releaseall` if 0x1006 is set and you STEP on (10,2)
  — but after the dream the player is locked at the bed and cannot walk there, so nothing
  releases. (This is almost certainly the intent the dream omits: it should release on its own.)

**In-engine reproduction (decisive):** rig `_emu/dream_repro4.rig` from `_emu/checkpoint.ss`
(map 4.1, player free at (6,6); both flags clear). Steps: `pokeflag 0x1166 1`,
`pokeflag 0x1006 0` (simulate pajamas-on, dream-unseen), walk to **(3,5)**, face down, tap A:
- `FLAG 0x1006` flips **0 -> 1** at the A-press → the dream script ran.
- After `mashA 700` (advancing the whole dream): screenshot `_emu/dr4_postdream.png` =
  **fully black screen**.
- MOBILITY TEST: `tap DOWN`, `tap RIGHT` — `LOC` stays **(3,5)** both times. The player cannot
  move; input is dead. Screenshot `_emu/dr4_mobility.png` shows the field frozen with a stuck
  textbox. → **permanent control-flow freeze, reproduced.**
  (Approaches from the other three sides — (4,6) face-west, (3,7) face-north, (2,6) — do NOT
  fire sign4: tile (3,6) is solid and kind=2 only triggers from the north tile (3,5) facing
  south. So the dream is reached by exactly one tile+facing, which is the normal "go to sleep".)

**Proposed fix:** make the dream branch release the player (and restore the screen) before it
ends. Minimal, in-place: replace the final `closemessage; end` at 0x8000B7/0x8000B8 so the script
first fades back in and `releaseall`s, e.g. `fadescreen(in); releaseall; end`. Since the byte
budget at the tail is tight (end is a single byte), the clean edit is to repoint/extend the
dream's tail to a short stub `... fadescreenspeed/normalmsg as needed; releaseall; end`, or — if
the design intends a next-morning scene — have the dream `goto`/`call` the wake-up sequence
(which sets 0x1006 at 0x807955+ and releases) instead of a bare `end`. The load-bearing
requirement either way: a `releaseall` (0x6B) must execute on this path before control returns to
the field, and the screen must be faded back in.

---

## FINDING 2 — CANDIDATE (unconfirmed): map 5.4 bridge trigger 0x800680, post-0x575 path

**Pattern:** lock/lockall reaching a stop with no release, via a malformed branch pointer.

Map 5.4 triggers trig0/1/2 at bridge tiles (6,8)/(7,7)/(8,8), gate var 0x0000==0 (always
active), all run `0x800680`:

```
; 0x800680
  0x800680: lockall                      <-- player locked (byte 0x69)
  0x800681: setflag 0x2C
  0x800684: setvar 0x5025, 1
  0x800689: checkflag 0x575
  0x80068C: goto_if cond=0 -> 0x80036F    <-- 0x575 CLEAR: Misty bike cutscene -> releaseall; end  (fresh save: OK)
  0x800692: goto_if cond=1 -> 0x8007D8    <-- 0x575 SET: target 0x8007D8 = bytes FF FF (engine stops)
  0x800698: end
```

The cond=1 branch operand 0x8007D8 points at `FF FF` (0x8007D8=FF, 0x8007D9=FF). Per the engine
bounds-check, an unknown opcode STOPS the script gracefully — but `lockall` already ran on this
path and **no release executes**, so the player is left frozen. (0x8007DA, two bytes later, is a
real `lockall; setflag 0x2C; setvar 0x5025,1; checkflag 0x575; ...` script — the `-> 0x8007D8`
looks like a 2-byte-off / dead "post-scene do-nothing" pointer; it is referenced twice: from
0x800694 here and from 0x800CB1.)

**Reachability:** flag 0x575 is set exactly once, at 0x804531, immediately after a wild battle
(`setwildbattle; dowildbattle; setflag 0x575; releaseall; end`) in this map's scene scripting.
On a fresh save 0x575 is clear, so the FIRST bridge cross takes the safe Misty-cutscene branch.
The freeze would require: 0x575 already set (i.e., after that wild battle) AND the player walking
back onto a bridge tile (trig0/1/2 are always-active and shadow the later trig3/4/5 on the same
tiles). I could not prove that walk-back is reachable (the scene may leave the player past the
trigger tiles / off the bridge), and I did NOT reproduce it in-engine, so this stays a candidate.

**Proposed fix (if confirmed):** repoint `goto_if cond=1 -> 0x8007D8` to a real
`releaseall; end` stub (or to 0x8007DA if that is the intended post-scene handler), so the
post-0x575 re-step releases instead of stranding the lockall.

---

## CLEARED — the 16 benign "dispatch-default `end`" candidates (NOT freezes)

After std-release modeling, the scan flagged 18 unique scripts. Two are the findings above. The
remaining 16 are all the identical, benign vanilla-FRLG idiom: `lock`/`lockall`, then a
value-dispatch ladder (`multichoice` / `yesnobox` via callstd 5 / a menu `special`) where EVERY
real return value (including the `0x7F` = B-button case) is handled and ends with
`release`/`releaseall` (or `callstd 2/3/6`), and the flagged terminator is a **defensive bare
`end` fall-through past the last `compare … 0x7F; goto_if`** that is only reached if the
multichoice/special returns an out-of-range value it cannot return. Unreachable on real data →
not a freeze (this exact code ships and runs safely in stock FireRed).

| script start | map / event | what it is | flagged bare `end`(s) | verdict |
|---|---|---|---|---|
| 0x1A72D6 | gStdScript1 (std 1) | give-item ordinal/buffer helper (var-dispatch) | 0x1A722F | FP — index always valid from caller; releases via caller |
| 0x802F94 | 1.5 person1 | Magikarp salesman (givemon dispatch) | 0x8332A4 | FP — give-status default |
| 0x80979C | 6.5 person2 | profile NPC (multichoice) | 0x824F44 | FP — post-0x7F default |
| 0x8097CA | 0.28 mapscr_t4_sub | PokéCenter nurse (special 0x187/0x1B1/0x183) | 0x8256BB,0x82572F | FP — caller releases; defaults unreachable |
| 0x81832F | 5.4 person0 | PokéCenter nurse (same as above) | 0x822F27,0x822F9B | FP — same |
| 0x827EAF | 7.0 person0 | badge-describer (special 0x158/0x159 → 0..8,0x7F) | 0x827F3B,0x828035 | FP — post-dispatch defaults |
| 0x8289C0 | 2.0 mapscr_t2_sub | bike shop (multichoice) | 0x8289F7 | FP — post-0x7F default |
| 0x828AA4 | 5.2 sign1 | status blackboard (multichoicegrid) | 0x82B349 | FP — post-0x7F default |
| 0x837A35 | 8.4 person0 | Name Rater (yesno/special dispatch) | 0x837A55,0x837A79,0x837AD8 | FP — all real paths release |
| 0x838E96 | 10.2 person2 | dept-store clerk (multichoice) | 0x838EE3 | FP — post-0x7F default |
| 0x839AB5 | 10.6 sign0 | dept elevator (floor-select special) | 0x839B18,0x839BAD | FP — post-dispatch defaults |
| 0x847CFC | 2.35 person0 | Game Corner prize counter (multichoice) | 0x848148 | FP — post-0x7F default |
| 0x847EA4 | 2.35 person1 | Game Corner coin counter (multichoice) | 0x847EFC,0x847F20 | FP — post-0x7F default |
| 0x848E8D | 2.35 person8 | Game Corner prize counter (multichoice) | 0x848F21,0x848FE7,0x849096 | FP — post-dispatch defaults |
| 0x8493F4 | 2.35 person9 | Game Corner TM counter (multichoice) | 0x849488 | FP — post-0x7F default |
| 0x84C0B0 | 4.1 sign4 | (FINDING 1 — the bed; the OTHER branch 0x84C0BA releases) | — | the bug is the dream branch only |
| 0x8558B3 | 12.1 person2 | fossil doctor (givemon dispatch) | 0x855966,0x855B33,0x855B79,… | FP — give-status defaults |

(Already-known/cleared classes per the brief were excluded from re-reporting: F8 braillemessage
talk-freeze 3.72/1.59 fixed; the ~258 0x08000000 empty-script sentinels benign; trainer data;
setwildbattle/givemon/special operands; mapscript ON_WARP overlaps F2 fixed, 2.36/3.93 benign.)

---

## Tooling (left in /tmp and _emu; ROM not modified)
- `/tmp/freeze_scan.py` — the reachability-aware lock/release scanner (3249 roots → 18 unique
  candidate scripts after std-release modeling).
- `/tmp/decompA.py` — private copy of `tools/decomp.py` writing `/tmp/decompA.md`.
- `_emu/dream_repro4.rig` (decisive), `_emu/dream_repro{,2,3}.rig`, `_emu/dream_probe.rig`,
  driven from `_emu/checkpoint.ss`; proof screenshots `_emu/dr4_postdream.png` (black screen) and
  `_emu/dr4_mobility.png` (frozen field).
