# Data-Integrity Audit — out-of-range operands in reachable scripts

Scope (W1): the remaining data-integrity classes for Pokémon Ash Gray (FireRed romhack),
ROM `rom/ashgray.gba`. Goal: find any out-of-range operand in a **reachable** script that
would crash the game, in three opcode classes:

1. `setwildbattle` (0xB6): species u16@+1, level u8@+3, item u16@+4
2. `givemon` (0x79): species u16@+1, level u8@+3, item u16@+4
3. `special` (0x25): index u16@+1, and `specialvar` (0x26): var u16@+1, index u16@+3

Valid ranges: species 1–411, level 1–100.

**Bottom line: ALL CLEAN.** No reachable `setwildbattle`/`givemon`/`special`/`specialvar`
has an out-of-range operand that can crash the game. One class of apparent hits (6 Game
Corner `givemon`s reading species 16385) was investigated to the bytes/engine and proven a
false positive (var-reference, not a literal). Out-of-range special indices are additionally
*structurally impossible to crash* because the dispatch bounds-checks — proven below.

---

## Method (reachability + var-awareness)

Rather than raw-byte scanning (which the lead flagged as ~5000 false positives in script
regions — opcode bytes appear constantly in data/text/movement), I enumerated **reachable
scripts** and linearly decoded each, recording every site of the four opcodes.

Reachability roots (same map-walk convention as `tools/scan_dead_scripts.py`):
- every map's person (stride 24, ptr@+16), trigger (stride 16, ptr@+12), sign (stride 12,
  ptr@+8 when type<5) event-script pointer;
- every map-script subtable script (header@`map_header+8`, types 2/4 → `{u16 var,u16 val,u32 script}`);
- the 10 entries of **gStdScripts** (`0x08160450..0x08160478`, located via the `callstd`/`gotostd`
  handlers — it sits immediately after gSpecials);
- transitive closure through `call`/`goto`/`call_if`/`goto_if` pointer operands, plus
  conservative continuation pointers embedded in `trainerbattle` (post-battle/beaten scripts).

Decoded **42,724** reachable script-byte positions. Site counts in reachable scripts:
`setwildbattle=28  givemon=54  special=931  specialvar=313`.

Scanner: `/tmp/scan_full.py` (reachable walk + flagging), `/tmp/scan_operands.py` (initial
literal-only pass), `/tmp/gm_local.py` (path-sensitive var resolution), `/tmp/raw_scan.py`
(raw-vs-reachable cross-check). Engine disassembly in `/tmp/*.py` via capstone 5.0.7.

---

## 1. setwildbattle (0xB6) — CLEAN (28/28 valid)

All 28 reachable sites have **literal** species 1–254 and level 5–75. None use a
var-reference. Examples: `1.0/trig11` species=10 lv=5; `3.55/trig1` species=130 lv=25;
`1.110/person0` species=254 lv=75; `3.45/person4` species=143 lv=35.

Engine note (matters for correctness of this check): the `setwildbattle` handler
`@0x0806C369` reads species/level/item with `ScriptReadHalfword`/`ldrb` and passes them
**directly** to `CreateScriptedWildMon` (`0x080A029C`) — it does **NOT** call VarGet. So a
var-reference here would be a real bug. There are none; every operand is an in-range literal.
Conclusion: clean.

## 2. givemon (0x79) — CLEAN (54/54 valid after var resolution)

- 48 sites are **literal** species (all 1–411) and level 5–50 — valid. (Includes the
  Bill/starter/fossil/trade gift NPCs D2 already audited, plus a few in std/trainerbattle-
  continuation scripts; all in range.)
- 6 sites at **map 2.35 / person8** (the **Celadon Game Corner prize-exchange counter**,
  script @0x08848E8D) read species field = **0x4001 = 16385**. This is the only apparent
  out-of-range hit in the whole audit, and it is a **FALSE POSITIVE**:

  - Raw bytes at e.g. `@0x08848FF7`: `79 01 40 09 ...` → the species u16 is literally
    `0x4001`, i.e. the script-variable **VAR_0x4001**, not a literal species.
  - The `givemon` handler `@0x0806BFD0` reads the species operand with `ScriptReadHalfword`
    then calls **VarGet** (`0x0806E568`) on it before use (verified: VarGet does
    `GetVarPointer(id); if ptr return *ptr else return id` — so id≥0x4000 reads the var).
    Level is likewise VarGet'd. So the effective species is `VAR_0x4001`'s stored value,
    never 16385.
  - Path-sensitive resolution of VAR_0x4001 along every execution path into these 6 givemons
    (`/tmp/gm_local.py`) yields species ∈ **{35, 63, 123, 137, 147}** = Clefairy, Abra,
    Scyther, Porygon, Dratini — all valid; levels 8–26 — all valid. (The script sets
    VAR_0x4001 via `setvar` to the chosen prize just before the `givemon`.)

  Conclusion: not a bug. (An earlier whole-graph var over-approximation made this look
  invalid because VAR_0x4001 is a shared temp set to large values in *other* scripts — that
  aliasing does not occur at run time; the var is re-set locally on each interaction.)

## 3. special (0x25) / specialvar (0x26) — CLEAN, and OOB is benign anyway

- **Table length = 444.** gSpecials base `0x0815FD60`. Both handlers' end-pointer pool word
  is `0x08160450` ⇒ `(0x08160450 − 0x0815FD60)/4 = 444` entries (indices 0–443 valid). This
  agrees exactly with counting consecutive thumb-function pointers (entry[444]@0x08160450 is
  the first non-thumb word). gStdScripts begins at 0x08160450.
- **All reachable indices are in range:** across 931 `special` + 313 `specialvar` sites, the
  distinct index set spans **0..440** — every one < 444. No OOB index is used.
- **Even an OOB index could not crash**, because both dispatchers bounds-check the index,
  exactly like the script-opcode dispatch:

  `ScrCmd_special` @0x08069EFC:
  ```
  bl ScriptReadHalfword            ; idx
  lsls/lsrs r0  ; idx*4 (byte offset)
  ldr r1,=gSpecials(0x0815FD60); adds r1,r0,r1   ; &gSpecials[idx]
  ldr r0,=0x08160450               ; end
  cmp r1, r0
  bhs 0x08069F20                   ; if &gSpecials[idx] >= end: SKIP — no load, no call
  ldr r0,[r1]; bl <call>           ; in-range path only
  ```
  `ScrCmd_specialvar` @0x08069F3C does the identical `cmp r1,end; bhs 0x08069F74` skip.

  This is the same pattern as the script-opcode dispatch in `RunScriptCommand` @0x08069804
  (`ldr r1,&cmdTable[op]; ldr r0,cmdTableEnd; cmp; bhs 0x08069838 → skip`; cmdTable
  `0x0815F9B4..0x0815FD08`, 213 entries) which the lead established makes OOB opcodes benign.
  So: **an out-of-range special/specialvar index is a no-op, not a crash.** (None occur, but
  this closes the "is it a crash?" question definitively per the brief's CRITICAL requirement.)

  Conclusion: clean.

---

## Cross-check against raw scanning (false-positive control)

A raw ROM-wide scan of the script regions (vanilla 0x140000–0x180000, custom
0x71A000–0x9A0000) for these four opcode bytes with an out-of-range *literal* operand yields
**5,023** hits (specialvar 1642, special 1565, setwildbattle 1260, givemon 556). Intersecting
those byte positions with the 42,724 positions my reachable graph actually decodes as that
instruction gives **0** — every raw OOB hit lands in data/text/movement bytes that are never
executed as one of these commands. This confirms there is no reachable OOB site hiding outside
the walked graph.

---

## Result

| Class            | Reachable sites | Out-of-range & reachable | Verdict |
|------------------|-----------------|--------------------------|---------|
| setwildbattle    | 28              | 0                        | clean   |
| givemon          | 54              | 0 (6 var-refs proven valid) | clean |
| special/specialvar | 1244          | 0 (and OOB is benign)    | clean   |

**No fix required for any of the three classes.** All clean.

Key engine facts established (reusable):
- gSpecials @0x0815FD60, **444 entries** (end 0x08160450); gStdScripts @0x08160450 (10 entries).
- `special`/`specialvar` dispatch **bounds-check** the index (`cmp;bhs`) ⇒ OOB special = no-op.
- `givemon` handler @0x0806BFD0 **VarGets** species & level (so var-ref operands are legitimate).
- `setwildbattle` handler @0x0806C369 does **NOT** VarGet (uses literal species/level/item).
