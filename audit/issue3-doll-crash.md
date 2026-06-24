# Issue #3 — "Doll competition / Team Rocket vs Lickitung — talk → crash"

**Map:** 3.72 (PRINCESS POKéMON FESTIVAL, the doll competition). 58 persons / 41 triggers.
Header file 0x76B2D4, events 0x7C0320.

**Verdict (short):**
- The **doll-competition / Lickitung scene scripts themselves contain NO crash.** Every
  candidate vector was checked against actual data and ruled out (details below). During
  the Lickitung scenes there is **nothing talkable** — every Team-Rocket / Lickitung object
  has a NULL or pure-`0xFF` (benign-stop) script, so "talking" is a no-op.
- I did find **one genuine latent crash-class bug on this map that the prior 0xFF-dangling
  analysis missed**, but it is in a **different sub-scene** (the pre-school "release your
  Pokémon" playground), not the Lickitung battle: **person33 executes `braillemessage` on a
  wild out-of-ROM pointer.** Honest severity caveat: that wild pointer lands in the GBA
  open-bus/OAM-mirror plane, so it most likely produces a **garbled/stuck textbox or visual
  corruption rather than a guaranteed hard reset** — I could not do an in-engine repro
  (warpto-3.72 doesn't render, per the rig limitation), so I am not claiming a clean crash.

So: **the specific report-#3 Lickitung "talk-crash" is NOT reproduced as a script fault.**
The closest real bug on the map is the Machamp/braille bug. Both findings are documented.

---

## What I examined and how it was ruled out

### 1. Trainerbattles (incl. the Lickitung battle) — CLEAN
gTrainers confirmed at vanilla base **ROM 0x0823EAC8** (40-byte entries). All 8
trainerbattle commands in the map parsed and every trainer struct + party validated:

| script offset | type | id | trainer | nMons | party ptr | party (species/level) |
|---|---|---|---|---|---|---|
| 0x81728C (person0) | 01 | 277 | HAROLD | 1 | 0x23B3D8 ✓ | 111 L40 |
| 0x81DC16 (person17) | 01 | 244 | **JESSIE** | 4 | 0x23B170 ✓ | 24 L38, 110 L38, 52 L20, 108 L35 |
| 0x823933 (person53) | 00 | 157 | **CARL** | 2 | 0x23A910 ✓ | 52 L30, 52 L32 |
| **0x84C2F0 (trig33, Lickitung→battle)** | 01 | 157 | **CARL** | 2 | 0x23A910 ✓ | 52 L30, 52 L32 (2× Meowth) |
| 0x857968 (person54) | 00 | 310 | KIRK | 3 | 0x23B6A8 ✓ | 104,37,42 L30 |
| 0x85788A (person55) | 00 | 473 | SIMON | 3 | 0x23CD10 ✓ | 20,33,75 L30 |
| 0x856F66 (person56) | 00 | 279 | JANE | 3 | 0x23B400 ✓ | 44,17,44 L30 |
| 0x857A63 (person57) | 00 | 270 | TIFFANY | 1 | 0x23B348 ✓ | 53 L35 |

All `partyFlags=0x00` (NoItem/DefaultMoves, 8-byte entries). No null/garbage party ptr,
no 0-mon party, no out-of-range species or level. **The Lickitung battle (CARL, 2× Meowth)
is valid.** Trainerbattle ruled out.

### 2. specials — CLEAN
gSpecials at **ROM 0x0815FD60**; table runs ~444 valid entries before the natural end at
index 0x1BC. Every special index used in the map — `0x06, 0x17, 0x85, 0x9F, 0xBA, 0xDC,
0x113, 0x114, 0x13D, 0x17C` (max 0x17C = 380) — is in range and resolves to a valid Thumb
code pointer. No OOB special dispatch. Ruled out.

### 3. applymovement object ids — CLEAN
Map 3.72 valid localIds are 0x01..0x3C. Every `applymovement / addobject / removeobject /
setobjectxyperm` operand in the SW Rocket/Lickitung cutscenes (trig14, trig27, trig33,
person43, person35, mapscr_t3) targets a valid localId (or player 0x00FF / camera 0x007F /
a var). No movement onto a non-existent object → no "F4-class" object softlock here. Ruled out.

### 4. applymovement movement-data pointers — CLEAN
Every movement-data pointer in those cutscenes resolves into ROM **and** has a proper
`0xFE` terminator within range. No wild movement pointer, no unterminated march → no
infinite `waitmovement`. Ruled out.

### 5. givemon / multichoice / pokemart / text & branch pointers — CLEAN
A map-wide walk of **all 108 reachable script blocks** found: no `givemon` with OOR
species/level; no `multichoice/grid`, `pokemart`, or `callstd` with an out-of-range index;
no `message`/`loadword` text pointer or `call`/`goto` target that falls outside ROM.

### 6. The Lickitung scenes have nothing talkable
- **Scene 1 (trig14 @0x84B076, "JESSIE: How dare you eat the present… LICKITUNG!"):** the
  Rocket trio + Lickitung are persons 37–41 — **all `script = 0x000000` (NULL)**.
- **Scene 2 (trig33 @0x84C2A6, "Stop thief!" → CARL battle):** persons 45–52 are NULL or
  empty-script extras. The one talkable object nearby, **person43 (@0x84C4C5, the wild
  MEOWTH)**, is a clean script (lock/faceplayer/playmoncry/yesno/give MEOWTH).

A null script is a no-op in the FireRed VM, so "I try to talk" during the Lickitung scene
does nothing — there is no script to fault. This is why the report's exact mechanism does
not reproduce as a script bug.

---

## The one real latent bug found: person33 `braillemessage` on a wild pointer

**Object:** person33 — localId **0x24**, **gfx 134**, at (93,12), flag 0x002C.
**Script:** 0x160DDF. Raw: `80 20 20 31  78 08 43 30 70  F0 …`

Decoded as FireRed script:
```
0x160DDF: 0x80 bufferitemname  buf=0x20 item=0x3120     ; benign buffer write
0x160DE3: 0x78 braillemessage  ptr=0x70304308           ; <<< WILD POINTER (outside ROM)
0x160DE8: 0xF0 (not in 213-entry cmd table) -> VM stops  ; benign stop, but TOO LATE
```

**Why the prior "all dangling NPCs are benign" ruling does not cover this one:**
person25 (@0x166CDC) and person29 (@0x167407) are **pure `0xFF`** — first byte not in the
command table → the bounds-checked VM (`RunScriptCommand` @0x08069804) stops *immediately*,
executing nothing. Those two are genuinely benign. **person33 is different:** it begins with
two **valid** opcodes (`bufferitemname`, `braillemessage`) that the VM **executes** before it
reaches the invalid `0xF0`. The opcode bounds-check only protects against the trailing byte;
it does not prevent `braillemessage` from running on garbage.

**Why the data is bad / what faults (verified by disassembly):**
- `braillemessage` handler @0x0806BC04: `bl ScriptReadWord(0x08069910)` pulls the 4-byte
  operand (0x70304308) and, since it is non-zero, passes it (r2) into the braille/text
  printer `0x08002C48`. That printer does `str r2,[sp]` and processes r2 as glyph data —
  **no null/range guard** on the pointer.
- 0x70304308 is **not in any ROM/RAM data region** (it falls in the 0x07xxxxxx OAM-mirror /
  open-bus plane). The printer therefore reads **garbage** as braille tile data.

**Severity — stated honestly:** on GBA, reads from 0x07xxxxxx return open-bus/OAM-mirror
values rather than triggering a bus abort, so this is **most likely garbled/corrupt braille
output or a stuck textbox, not a guaranteed clean reset.** A player could reasonably call
that "a crash/freeze," but I have **not** confirmed a hard crash (no in-engine repro — the
170×39 map won't render under a bare warpto, per the rig limitation noted in the brief). So I
am flagging this as a confirmed **bad-data deref / corruption bug**, with crash severity
**uncertain**.

**Reachability — confirmed:** person33 (localId 0x24) is spawned by person20's
"release some of your Pokémon for the children to play with" minigame (@0x81F7F4…),
specifically the branch gated on **owning species 67 = MACHAMP**:
```
0x81F8F5: setvar 0x8004 = 0x0043 (species 67, MACHAMP)
0x81F8FA: specialvar 0x800D = special 0x017C   ; "do you own this species?"
0x81F904: call_if cond=1 -> 0x81FA25           ; playmoncry; waitmoncry; addobject 0x24; return
```
So: **own a Machamp → choose "release Pokémon for the kids" → the Machamp field object
(person33) appears → talk to it → `braillemessage` fires on 0x70304308.**
(For reference, the other release slots — Bulbasaur/Charmander/Squirtle/Pikachu/Poliwrath/
Slowbro/Pidgeot/Kangaskhan/Psyduck → localIds 0x1E,0x22,0x23,0x1F,0x1C,0x1D,0x20,0x25,0x21 —
all point to **valid** cry/text scripts. Only the Machamp slot, person33, is corrupt.)

### Minimal proposed fix (person33)
The script body at 0x160DDF is corrupt (it is engine bytes, not an intended script — gfx 134
should behave like its siblings: `playmoncry; loadword <cry text>; callstd 2; end`). Two safe
options, both byte-only and in-place:

1. **Repoint person33's script** (person-event field at file `0x7BFA98 + 33*24 + 16`) to an
   existing valid Machamp/cry script, or to any harmless `release;end`/`end` stub already in
   the ROM. Cleanest, touches 4 bytes, no new data needed.
2. **Neuter the script in place**: overwrite the first byte at 0x160DDF (currently `0x80`)
   with `0x02` (`end`). The VM then stops immediately and `braillemessage` never runs. Touches
   1 byte. (Only do this if 0x160DDF is not also referenced as engine code elsewhere — it is
   reached as a *script pointer* from the person event, but confirm no code xref before
   overwriting; option 1 avoids that concern entirely by not modifying 0x160DDF.)

Recommend **option 1** (repoint) to avoid editing a region that may double as code.

---

## Bottom line for report #3
- **Not definitively reproduced as written.** The doll-competition / Lickitung scene scripts
  are clean across every checked vector (trainer data, specials, object ids, movement data,
  pointer derefs), and the Lickitung scene has no talkable script to fault. If the player's
  "crash" was during that battle/cutscene specifically, the cause is **not in the map's event
  scripts** — candidates would then be battle-engine/graphics (e.g. the known D3 "switch in
  first Jessie battle → invisible mons" class) rather than a scripted talk.
- **The one concrete, reachable bad-data bug on this map is person33** (Machamp release-object
  → `braillemessage` on wild ptr 0x70304308). It is a real defect the earlier 0xFF analysis
  under-counted, with a clean minimal fix — but its crash *severity* is unconfirmed and it is
  a **different sub-scene** from the Lickitung battle described in the report.

### Files / offsets
- ROM: `rom/ashgray.gba`; map 3.72 header file 0x76B2D4, events 0x7C0320, persons 0x7BFA98.
- gTrainers ROM 0x0823EAC8; gSpecials ROM 0x0815FD60; script-cmd table ROM 0x0815F9B4 (213 entries).
- person33 script file 0x160DDF (ROM 0x08160DDF); braillemessage handler ROM 0x0806BC04;
  ScriptReadWord ROM 0x08069910; braille text printer ROM 0x08002C48.
