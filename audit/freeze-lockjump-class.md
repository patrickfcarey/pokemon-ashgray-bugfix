# Lock-then-stop "freeze" class — VERDICT: BENIGN (not a freeze)

**Bottom line:** A script that runs `lock`/`lockall` and then reaches a graceful script-VM
STOP (a `goto`/`call`/`goto_if`/`call_if` whose target decodes to an out-of-range opcode, or a
linear fall-through into one) with **no** `release`/`releaseall`/warp/battle does **NOT** freeze
the player. **Proven in-engine** on the exact map-5.4 candidate: after the lock + OOB-stop fires,
the player recovers full overworld control and walks freely. The whole class is empty of real
freezes. This is the same auto-release behavior as the first-sleep dream's `lock → end` (which
was already disproven as a freeze).

Addresses use the project convention (drop the leading `08`): `0x800680` = ROM `0x08800680` =
file offset `0x800680`. ROM md5 `43216f9fa86e9bbecb118d6203ef83c2`.

---

## TASK 1 — In-engine: does `lockall` + graceful VM-stop freeze? **NO.**

### Rig setup
- ROM: `_emu/tvtest/pc_test.gba` (bedroom-stairs warp redirected to map 5.4; native clean load
  of the Viridian City Pokémon Center interior — renders faithfully, NOT a `warpto` artifact).
- Preload state: `_emu/pc_clean.ss` spawns the player on map 5.4 at **(6,8) = trig0 tile**,
  live `sb1 = 0x0202555C`. Baseline: `var 0x5025 = 0`, `flag 0x575 = 0`.
- Driver: `_emu/rig.sh tvtest/pc_test.gba <script> pc_clean.ss`.

### The candidate script (byte-confirmed)
trig0 (6,8) / trig1 (7,7) / trig2 (8,8) → script `0x800680`, gate `var 0x5025 == 0`:

```
0x800680: lockall
0x800681: setflag  0x002C
0x800684: setvar   0x5025, 1          ; <-- closes the gate the instant the trigger fires
0x800689: checkflag 0x0575
0x80068C: goto_if cond=0 -> 0x80036F   ; 575 CLEAR: Misty "you wrecked my bike" scene, ends releaseall
0x800692: goto_if cond=1 -> 0x8007D8   ; 575 SET:   jump to 0x8007D8
0x800698: end
0x8007D8: 0xFF                          ; out-of-range opcode -> script VM STOPS (no release)
```

### Result A — baseline (`flag 0x575 = 0`, the Misty branch 0x80036F)
Stepped onto (6,8) → trigger fired (`var 0x5025` went 0→1). The Misty cutscene played
(Misty appears, "Now I've got you!" / "MISTY: I knew I'd find you here! … It was destroyed by
lightning when you stole it!"). After fully advancing dialogue (`mashA 600` + `mashA 400`), the
final `releaseall` ran and the player **walked freely**: (6,8)→(5,8)→(3,8)→(3,7)→(4,7), no
textbox on screen (`_emu/lockjump_baseline_misty_recovered.png`). NORMAL, recoverable cutscene.
(This is the classic trap: with too-few A-taps the open textbox makes LOC look stuck — it is not.)

### Result B — freeze branch (`flag 0x575 = 1`, the OOB stop 0x8007D8) — THE TEST
Poked `flag 0x575 = 1`, kept `var 0x5025 = 0`, stepped onto (6,8). Trigger fired
(`var 0x5025` → 1, confirming `0x800680` ran and took `goto_if cond=1 -> 0x8007D8`). The 575-SET
path has **no dialogue at all** — it just `lockall`s and jumps to the `0xFF` stop.

3-step protocol applied:
1. `mashA 400` (advance any/all dialogue).
2. Screenshot — **NO textbox on screen** (`_emu/lockjump_575set_afterfire.png`); player standing
   plainly on the field, no Misty (the 575-SET branch skips the whole scene).
3. Mobility test — player **moves freely**:
   - taps: (6,8)→(5,8)→(6,8)→(6,7)→(6,8) ✓
   - decisive walk-away (held-direction): (6,8)→(6,4)→(0,4)→(0,2) — crossed the whole map
     (`_emu/lockjump_575set_walkaway.png`).

**"No textbox open AND can move" = NOT a freeze.** `lockall` + graceful VM-stop auto-releases.

### Mechanism (why it auto-releases)
`RunScriptCommand`/script-context runner @`0x08069804` reads the opcode, advances the script PC,
computes `entry = gScriptCmdTable + op*4`, and bounds-checks `entry` against the table-end pointer
(`cmp r1, r0` @`0x08069866`; loaded from ctx `[r4,#0x60]`). `gScriptCmdTable` @`0x0815F9B4` has
~213/214 entries (ends `0x0815FD0C`). Opcode `0xFF` (255) lands far past the end → the bounds
check fails → the runner returns **without executing** and the script context stops cleanly (no
garbage execution, no infinite loop). The player-lock is held by the *running script task*, not by
a persistent saveblock flag; when the script context stops, the field-lock state is torn down and
normal input resumes. Hence "lock then stop" behaves exactly like "lock then end."

---

## TASK 2 — Map 5.4 reachability (Viridian City Pokémon Center, bank 5 / map 4)

Map 5.4 is the **Viridian City Pokémon Center interior** (15×10), warps out to map 3.1 (Viridian
City). It is NOT a route/bridge map — the "bridge trigger tile" framing in the lead was incorrect;
the trigger tiles (6,8)/(7,7)/(8,8) are the PC's three entrance/exit floor tiles (they coincide
with warp0/warp1/warp2 back to the city).

### Trigger gating (corrects the lead's "gate var 0x0000==0 always-active")
| trig | tile  | gate var/val      | script    |
|------|-------|-------------------|-----------|
| 0/1/2| (6,8)/(7,7)/(8,8) | **var 0x5025 == 0** | 0x800680 (lock→Misty / 575-stop) |
| 3/4/5| (8,8)/(7,7)/(6,8) | var 0x5030 == 1   | 0x800C9D (Team Rocket robbery)   |

trig0/1/2 are **not** always-active — they fire only while `var 0x5025 == 0`, and the script's
**first** real op (after `lockall`) is `setvar 0x5025, 1`, so they self-disable after the very
first contact. The map's level-scripts (ON_LOAD type 3 @0x822277 = heal-point `setrespawn`;
type 5 @0x804D6D = `special 0x182`; type 2 var-table fires only on `var 0x6082==3`, a Boulder/Box3
var) do **not** drive this scene — the trigger events do.

### How flag 0x575 gets set — the load-bearing fact
- **Only ONE opcode in the entire ROM sets flag 0x575 via `setflag`: file 0x804531** — and it is
  **UNREACHABLE**. It lives inside MAIDEN'S ROCK sign data (the bytes
  `b6 5c 00 20 00 00 b7 29 75 05 6b 02` @0x80452A coincidentally decode as
  `setwildbattle 0x5C,0x20; dowildbattle; setflag 0x575; releaseall; end`). **Zero** pointers
  reference 0x80452A/0x804530/0x804531 (verified by xref + unaligned scan), and the byte before
  (0x804529 = `02`/end) blocks fall-through. The reachability closure (42,495 reachable script
  offsets from all event/mapscript/std roots) confirms 0x80452A and 0x804531 are **not** reachable.
  ⇒ The lead's premise that "the wild battle @0x804531 sets flag 0x575 while the player can walk
  back onto a bridge trigger" is based on a **mis-identified, unreachable byte fragment** (it is
  Maiden's Peak sign text, a different/post-game area), NOT a real wild battle on this map.
- **HOWEVER**, flag 0x575 is a **trainer-defeated flag**: `FLAG_TRAINER_FLAG_START (0x500) + 0x75`.
  The engine sets it when the player defeats **trainer 0x75 = MAP 3.21 person2** (a reachable
  route trainer; map 3.21 is an 84×22 multi-trainer route). So flag 0x575 **can** be set in normal
  play — as a side effect of beating that route trainer, not by any story `setflag`.

### Is the freeze branch reachable on a fresh save? Reachable, but BENIGN.
The 575-SET branch (`goto_if cond=1 -> 0x8007D8`) fires iff, at the moment of the player's **first**
step onto trig0/1/2 (when `var 0x5025` is still 0), flag 0x575 is already set — i.e. the player
defeated route-trainer 0x75 (map 3.21 person2) **before** ever stepping on the Viridian PC entrance
tiles. That ordering is possible on a clean save (no var/flag corruption needed — pure trainer-flag
collision: the trigger author meant 0x575 as a story marker, but nothing story-side sets it; only
the unrelated route trainer does). So the branch IS reachable.

**But TASK 1 proves that branch does not freeze** — it `lockall`s, hits the `0xFF` stop, and the
engine auto-releases the player. So even in the worst-case ordering it is a no-op (the player walks
onto the tile, briefly locks, and immediately regains control with the Misty scene simply skipped).
No softlock, no corruption, box-fix-immune or not — there is nothing to brick.

The reachable `var 0x5025` setters are 0x8003B0 (Misty-branch end) and 0x800684 (the trigger
itself); 0x800588 and 0x8007DE are in unreachable map-script fragments.

---

## TASK 3 — Reachability-aware class sweep (`tools`-style closure)

Computed the full reachability closure over every map's person(+16)/trigger(+12)/sign(+8,kind<5)
script, mapscript subtables (types 2 & 4), and gStdScripts (×10), following call/goto/goto_if/
call_if + trainerbattle continuations. For each reachable instruction tracked whether a
`lock`/`lockall` was active with no intervening `release`/`releaseall`/warp/battle, then flagged
any control-transfer to an out-of-ROM / OOB-opcode target **and** any locked linear fall-through
into an invalid opcode.

**Result: exactly ONE reachable lock-then-stop instance in the entire script graph.**

| # | jump @ | kind | target | reason | lock @ | map/event | verdict (per TASK-1 engine finding) |
|---|--------|------|--------|--------|--------|-----------|------|
| 1 | 0x800692 | goto_if cond=1 | 0x8007D8 | OOB opcode 0xFF | 0x800680 (lockall) | map 5.4 trig0/1/2 | **BENIGN — not a freeze** (in-engine reproduced; auto-releases) |

No other instances exist (broader fall-through detection included). The class is a single member,
and that member is benign.

### Distinction from the already-fixed freeze fixes
The two freeze fixes already shipped (`tools/fix_person33_freeze.py` map 3.72 person33,
`tools/fix_person4_159_freeze.py` map 1.59 person4) are a **different** class: `braillemessage`
on a wild/out-of-ROM pointer → the braille glyph renderer infinite-loops (a real hard freeze, no
auto-release). Those are NOT lock-then-stop; they are wild-deref render loops (see
`tools/scan_partial_exec.py`). The lock-then-stop class investigated here is empty of real freezes.

---

## Tools (this audit; kept in /tmp, not added to the repo)
- `/tmp/reach.py` — reachability closure + lock-state tracker + lock-then-stop sweep (the class scan).
- `/tmp/dump_events.py`, `/tmp/dump_warps.py` — map 5.4 event/warp tables.
- `/tmp/find_refs.py` (flag/var opcode refs), `/tmp/find_ptr.py` / `/tmp/ptr_in_range.py` /
  `/tmp/find_trainer.py` — pointer & trainer-flag xrefs proving 0x804531 unreachable and 0x575 =
  trainer-0x75 flag.
- `/tmp/disasm_rsc.py` — RunScriptCommand bounds-check + gScriptCmdTable size (213/214 entries).
- Rig scripts: `/tmp/baseline_full.rig`, `/tmp/freeze_test.rig`, `/tmp/freeze_walkaway.rig`.
- Proof images (copied to `_emu/`): `lockjump_baseline_misty_recovered.png` (575-clear Misty scene
  recovered → free walk), `lockjump_575set_afterfire.png` (575-set OOB-stop, no textbox),
  `lockjump_575set_walkaway.png` (575-set, player crossed the whole map = full control).
