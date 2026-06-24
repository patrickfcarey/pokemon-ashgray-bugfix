# Wild-Encounter Table Integrity — Pokémon Ash Gray

**Scope of lead:** A wild slot with an invalid species (0 or >411) or an
invalid level (0 or >100) yields a Bad Egg or can crash the battle-intro on a
**fresh save** (box-fix-immune). Ash Gray ships custom anime-location wild
encounters, so this is a real data audit of `gWildMonHeaders` and every
sub-table it references.

ROM: `rom/ashgray.gba` (16 MiB, base `0x08000000`). Clean base:
`base/firered.gba`. Validator: pure-Python little-endian struct walk; no
assumed offsets — the table base was located by signature and confirmed.

---

## VERDICT

**Essentially clean for the stated failure mode. No Bad-Egg / invalid-species
risk anywhere in the wild tables.**

- Every one of the **2617** wild slots has a species in **1–411** (actual range
  in use: **10–246**). There is **no** species == 0 and **no** species > 411
  anywhere in the table. So no wild encounter can roll an invalid species ⇒
  **no Bad Egg, no species-driven battle-intro crash from this data.**
- Levels are in **1–100** on all but **one** slot (range in use 2–70).
- **One** genuine, Ash-Gray-authored data defect exists: a single water slot
  with `minLevel > maxLevel` (35 > 30). Its species is valid (Staryu, 120), so
  it cannot Bad-Egg or crash — the only effect is a malformed level field on one
  slot of one map. Raw-byte confirmed below. **Severity: cosmetic/low.**

Nothing here is box/var-corruption dependent (the already-mitigated D1 class);
the one finding is a static byte in ROM that is wrong on a fresh save.

---

## Confirmed table base (signature, not assumed)

The commonly-cited FRLG offset **0x083C9CB8** is correct **for the clean base**
(`base/firered.gba`: a valid 132-row header table starts exactly there). In
**Ash Gray that offset is all `0xFF` padding** — the header array was
**relocated**.

Signature scan (rows of `{u8 mapGroup, u8 mapNum, u16 pad==0, u32 land, u32
water, u32 rock, u32 fish}` where every non-zero pointer is 4-aligned and
in-ROM) finds exactly one long run in each ROM:

| ROM      | gWildMonHeaders base | file off  | header rows | terminator |
|----------|----------------------|-----------|-------------|------------|
| FireRed  | `0x083C9CB8`         | `0x3C9CB8`| 132         | row 132    |
| Ash Gray | **`0x088CD1F8`**     | `0x8CD1F8`| **170**     | row 170    |

Confirmation that `0x088CD1F8` is the true start, not a mid-table hit:
- The 8 rows *before* it decode as garbage (non-zero `pad`, junk/unaligned
  pointers); row 0 is the first clean header.
- Row 0 = `mg=2 mn=27 pad=0000 land=0x083C73D0 water=rock=fish=0` — sane.
- The run ends at row 170 = `mg=0xFF mn=0xFF pad=0000` (the engine terminator).
  Its pointer words are filler `0x77777777`, harmless because the engine stops
  on the `0xFFFF` mapGroup/mapNum before reading them.

So Ash Gray moved the **header array** to high ROM and kept most sub-tables in
place: of **280** non-null sub-table pointers, **222** still point into the
original FireRed data block (`0x083C73D0`–`0x083C9CB8`) and **58** point into
Ash Gray's expanded data region (`0x0871xxxx`–`0x0874xxxx`) — the custom
anime-location encounters.

---

## Counts and ranges (Ash Gray)

- **Header rows (non-terminator):** 170
- **Non-null sub-tables parsed:** 280
  (slot counts honored: land 12, water 5, rock-smash 5, fishing 10)
- **Total slots range-checked:** 2617
- **Distinct species in use:** 127; **min 10, max 246** → all within 1–411,
  **zero** out of range.
- **Level range in use:** **min 2, max 70** → within 1–100 (one slot violates
  `min<=max`, see finding).
- **encounterRate values seen:** 0–200 (0,1,2,…,60,64,200). The `0` values are
  intentional encounter-disables (see Finding B), not corruption.

(FireRed baseline for sanity: 132 headers, 227 sub-tables, 2176 slots, species
10–246, levels 2–67, **0** integrity issues — validator agrees with a known-good
table.)

---

## Finding A — single `minLevel > maxLevel` slot (CONFIRMED, low severity)

**Location:** header index 162 → **mapGroup 0, mapNum 17**, **water**
sub-table, **slot 2**.
Header @ `0x088CDEA0`; waterPtr `0x0872BA94`; slots @ `0x0872BA80`
(in Ash Gray's custom data region, i.e. an authored set, not vanilla FR).

**Raw bytes @ `0x0872BA88`:** `23 1e 78 00`
→ `minLevel = 0x23 = 35`, `maxLevel = 0x1E = 30`, `species = 0x0078 = 120
(Staryu)`.

Full water table for (0,17) and its two copy-paste neighbors:

```
(0,16) water: 116/116/120/120/117  levels (25,30)(25,30)(25,30)(25,30)(30,35)
(0,17) water: 116/116/120/120/117  levels (25,30)(25,30)(35,30)(25,30)(30,35)   <-- slot2 min>max
(0,18) water: 129/129/ 60/ 60/ 61  levels (25,30)(25,30)(25,30)(25,30)(30,35)
```

(0,16) and (0,17) are byte-identical except slot 2's min: `0x19`=25 in (0,16)
vs `0x23`=35 in (0,17). This is a one-byte transcription typo — the min byte
should be `0x19` (25), matching the sibling map and the slot's own max of 30.

**Engine impact (precisely characterized):**
- The species (120, Staryu) is valid, so this slot **cannot** create a Bad Egg
  and **cannot** crash the battle-intro. That is the load-bearing fact for this
  audit.
- The level: FRLG's `ChooseWildMonLevel` computes `range = (maxLevel -
  minLevel + 1)` and returns `minLevel + Random() % range` in **u8** math. With
  min=35, max=30, `range = (30 - 35 + 1) & 0xFF = 252`, so the slot can yield a
  level well outside the intended 30–35 band (min plus a 0–251 remainder,
  wrapping in u8). The exact `ChooseWildMonLevel` arithmetic was not
  re-disassembled here (the struct read uses register-offset addressing and did
  not match a literal `ldrb #0 / ldrb #1` probe); the formula above is the
  documented/decompiled FRLG behavior and is consistent across FRLG/Emerald.
  **Effect = an off-spec level on this one water slot only.** Cosmetic to the
  stated Bad-Egg/crash lead.

**Fix (if desired):** change the byte at file offset `0x72BA88` from `0x23` to
`0x19` (set minLevel 35→25 to match maxLevel 30 and sibling map (0,16)).

---

## Finding B — 19 sub-tables with `encounterRate == 0` (NOT a bug)

19 of the 280 sub-tables have `encounterRate == 0`. This is **intentional**, not
corruption:

- Every one corresponds to a map that had a **non-zero** rate in vanilla
  FireRed (e.g. hdr2 mg2/mn29 land FR=7→AG=0; hdr70 mg3/mn45 land FR=21→AG=0;
  …). Ash Gray zeroed the rate to **disable step-triggered wild encounters** on
  those routes while leaving the slot data intact.
- The slot data behind these rate-0 tables is fully valid. Example dump,
  hdr70 (mg3/mn45) land: species `21,77,22,77,74,52,21,54,78,53,78,53`, levels
  30–40 — all in range.
- `encounterRate == 0` means the per-step encounter roll never fires, so **no
  encounter is ever generated** ⇒ it cannot produce a Bad Egg or any crash.

The validator's initial "rate must be 1–255" was an over-strict heuristic from
the brief; rate 0 is a legitimate, common romhack technique. **Not flagged.**

The full list of rate-0 sub-tables (hdr index, mapGroup, mapNum, terrain):
2(2,29,land) 16(1,59,land) 19(1,62,land) 34(1,90,land) 44(1,103,land)
51(1,110,land) 56(2,13,land) 58(2,15,land) 68(2,25,land) 70(3,45,land)
74(3,49,land) 75(3,54,water) 84(3,63,land) 85(3,64,land) 87(3,19,land)
92(3,24,water) 107(3,39,land) 132(3,67,water) 132(3,67,fish).

---

## What was checked

For all 170 headers and 280 non-null sub-tables: header `pad == 0`; each
sub-table pointer in-ROM and 4-aligned; each sub-table's `slotsPtr` in-ROM;
every slot's `species ∈ 1..411`, `minLevel ∈ 1..100`, `maxLevel ∈ 1..100`,
`minLevel <= maxLevel`. Slot counts used: land 12 / water 5 / rock-smash 5 /
fishing 10. Result: **0** species-range violations, **0** bad pointers, **0**
header-pad violations, **1** `min>max` level violation (Finding A). All raw
bytes for the one finding were dumped and confirmed against the correct,
signature-verified table base.
