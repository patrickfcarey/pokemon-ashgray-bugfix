# Pokémon Data-Table Integrity Audit — Ash Gray (FireRed romhack)

ROM audited: `rom/ashgray.gba` (16 MiB, md5 `43216f9fa86e9bbecb118d6203ef83c2`).
Clean base: `base/firered.gba` (md5 `e26ee0d44e809351c8ce2d73c7400cdd`).
Both ROMs identify as **FireRed v1.0 US** (header title `POKEMON FIRE`, game code `BPRE`,
maker `01`, version byte `0`) — so the v1.0 table offsets apply.
Species universe: FRLG has 412 entries; valid species for this check = **1–411** (0 = `???`).
Move universe: verified max move id = **354** (`PSYCHO BOOST`); move 355 decodes to garbage
in `gMoveNames` — so the hack did **not** expand the move table and valid move = **1–354**.

---

## VERDICT — ALL CLEAN

| Table | Base offset (confirmed) | Result | Custom vs FireRed |
|---|---|---|---|
| Evolution table (`gEvolutionTable`) | **0x08259754** | **CLEAN** — 0 out-of-range | 25 entries / 15 species |
| Level-up learnsets (`gLevelUpLearnsets`) | **0x0825D7B4** (ptr table) | **CLEAN** — 0 out-of-range | 364 / 412 species relocated/edited |
| TM/HM compat (`gTMHMLearnsets`) | **0x08252BC8** | **CLEAN** — 0 overflow | 55 species |
| TM/HM move list (`gTMHMMoves`) | **0x0845A5A4** | **CLEAN** — all 58 valid | identical to FR (primary table) |
| Egg moves (`gEggMoves`) | **0x0825EF0C** | **CLEAN** — 0 out-of-range | identical to FR (0 species differ) |

**No data-table fault produces a Bad Egg or crash on a fresh save.** Every evolution target
is 1–411, every learnset/TM/egg move id is 1–354, every level is 0–100, every learnset
pointer is in-ROM and 0xFFFF-terminated, and the TM/HM compat bitfields contain no bit ≥ 58.
The custom (diff-vs-FireRed) entries are all deliberate, in-range hack edits (gen-1-style
trade-evolution removal; gen-1 learnset/TM tweaks). Confirmed to the raw bytes.

Supporting anchor: `gBaseStats` base = **0x08254784** (proven below) — not my deliverable
table, but it nails the species indexing all three audited tables share. The commonly-cited
`gBaseStats ~0x082547F4` is **wrong by 0x54** (it lands on Charmander); corrected here.

---

## Signature / offset proofs

All offsets verified by content signature AND code xref before scanning — no assumed offset
was trusted.

### gBaseStats = 0x08254784 (species indexing anchor)
- Bulbasaur (`HP45 Atk49 Def49 Spe45 SpA65 SpD65`, bytes `2D 31 31 2D 41 41`) occurs exactly
  once in each ROM, at file `0x2547A0` = ROM `0x082547A0`. That is species **#1**, so
  base = 0x082547A0 − 28 = **0x08254784**.
- Confirmed: species#0 = all-zero; #2 Ivysaur `60/62/63/60/80/80`; #3 Venusaur
  `80/82/83/80/100/100`; #151 Mew all-100. 56 xrefs in code.
- AG vs FR: 9 species have edited base stats (17, 25, 26, 128, 143, 172, 252, 253, 254) —
  expected for a gen-1 hack, out of scope here.

### gEvolutionTable = 0x08259754 (5 entries × 8 bytes/species; entry = u16 method, u16 param, u16 target, u16 pad)
- Bulbasaur signature `method=4(LEVEL) param=16 target=2(Ivysaur)` (bytes `04 00 10 00 02 00`)
  occurs once, at ROM `0x0825977C` = base + 1×40 (species #1 entry 0). ⇒ base = **0x08259754**.
- 5 code xrefs (0x8042F6C, 0x8042FBC, 0x8043138, 0x804599C, 0x80CE8C4). No relocated 2nd copy.

### gLevelUpLearnsets = 0x0825D7B4 (412 × u32 pointers)
- Pointer[1] (Bulbasaur) = 0x08257494; decoding the stream there (9-bit move / 7-bit level,
  0xFFFF terminator) yields `L1 Tackle(33), L4 Growl(45), L7 Leech Seed(73)…` — a valid
  learnset. ⇒ table base = **0x0825D7B4**. 6 code xrefs. Word after entry 412 = 0 (clean end).
- Move names decode correctly from `gMoveNames` (0x08247094): 1=POUND, 33=TACKLE, 45=GROWL,
  354=PSYCHO BOOST — validates the move-id ↔ move mapping.

### gTMHMMoves = 0x0845A5A4 (58 × u16 move ids: TM01–TM50, HM01–HM08)
- Full 58-id canonical FRLG sequence (TM01 FOCUS PUNCH 264 … HM08 DIVE 291) matches at
  ROM `0x0845A5A4`. (An earlier signature hit at 0x0825E014 was a **coincidental** byte match
  inside learnset data — rejected.)

### gTMHMLearnsets = 0x08252BC8 (412 × u64 compat bitfields)
- Found by brute-force xref+structural search: the only ROM address that (a) is referenced by
  a 4-byte pointer literal in code, (b) has species#0 mask = 0, (c) has **no** species with any
  bit ≥ 58 set, and (d) ≥ 200 species learn a TM. Referenced at 0x08043C68 / 0x08043C80
  (adjacent loads in the TM-teach routine). Sanity-decoded: Bulbasaur→TM06 Toxic/TM22 Solar
  Beam/HM01 Cut; Charizard→TM35 Flamethrower/TM38 Fire Blast/HM02 Fly; Pikachu→TM24/TM25
  Thunder; Mewtwo→nearly all TMs. (The commonly-cited 0x0825D124 is **wrong** — it has no
  xref and collides with learnset-pointer data, producing 202 false "overflow" species.)

### gEggMoves = 0x0825EF0C (u16 stream; species header = species + 20000; 0xFFFF terminator)
- Bulbasaur header `20001` (0x4E21) followed by move `113` (Light Screen) at ROM `0x0825EF0C`,
  preceded by a `0` pad word. Stream parses to a clean 0xFFFF terminator. 2 code xrefs
  (0x08045C50 / 0x08045CC8).

---

## 1. Evolution table — CLEAN (0/2060 entries out of range)

Scanned all 412 species × 5 entries = 2060 entries.
- **Range check: 0 flags.** Every non-empty entry has target ∈ 1–411, method ∈ 1–15,
  padding = 0. Empty slots (method=param=target=0) skipped.
- **25 custom entries across 15 species** (differ from FireRed): 44, 61, 64, 67, 72, 75, 79,
  93, 95, 117, 123, 133, 137, 236, 373.

Raw-byte confirmation of every custom entry (AG → FR):
- These are **trade-evolution removals** typical of gen-1 hacks — TRADE/TRADE_ITEM methods
  swapped to FRIEND/ITEM/LEVEL so the line can evolve without trading. All targets in range.
- Examples: #64 Kadabra `TRADE→FRIEND ↦#65`; #75 Graveler `TRADE→FRIEND ↦#76`;
  #93 Haunter `TRADE→FRIEND ↦#94`; #95 Onix `TRADE_ITEM→ITEM(Metal Coat) ↦#208`;
  #123 Scyther `TRADE_ITEM→ITEM ↦#212`; #133 Eevee item-evos reordered (↦#134/#135/#196/#197);
  #236 Tyrogue branch (atk/def compare) reordered (↦#106/#107/#237); #373 Salamence-region
  branch (↦#374/#375).
- One inert artifact (harmless): **#72 Tentacool** entry0 = method `NONE(0)`, param 0,
  target #252. Method 0 means the entry never triggers regardless of target, so #252 is dead
  data; the real Tentacool→Tentacruel evo is in entry1 (`LEVEL 30 ↦ #73`). No effect.

Every AG target species in the custom set: 45, 62, 65, 68, 76, 80, 94, 106, 107, 134, 135,
182, 186, 196, 197, 199, 208, 212, 230, 233, 237, 252, 374, 375 — **all 1–411**.

## 2. Level-up learnsets — CLEAN (0 problems / 4046 entries)

- All **412 pointers in-ROM** (0 OOB); data span 0x08257494–0x08259736 (sits exactly in the
  gap between gBaseStats and gEvolutionTable, as in vanilla — no pointer escapes to foreign data).
- Decoded **4046 move-entries**; **every learnset cleanly 0xFFFF-terminated** within bounds
  (none unterminated, none read OOB).
- **0 range problems**: every move id ∈ 1–354 (max seen = 354), every level ∈ 0–100.
- **364 / 412 species** have a pointer differing from FireRed. This is expected: Ash Gray
  edits several early gen-1 learnsets (Bulbasaur line, etc.), and because the learnset blobs
  are variable-length and packed contiguously, editing an early one shifts the offsets of all
  later species — the pointer table was rewritten to match. Spot-checks of edited species
  (Charizard #6, Pikachu #25, Snorlax #143) decode to plausible, well-formed movesets.

## 3a. TM/HM move list (gTMHMMoves) — CLEAN

All 58 entries ∈ 1–354 (min 15 Cut, max 352 Water Pulse). The primary table at 0x0845A5A4 is
**identical to FireRed**. A secondary 58-entry copy exists at 0x0845A80C (FRLG's per-item TM
move field region); in AG two entries there differ (TM05 46→242, TM09 331→244) — **both still
in range 1–354**, so no integrity risk regardless of which structure consumes it.

## 3b. TM/HM compatibility (gTMHMLearnsets) — CLEAN

- 412 species × u64. species#0 mask = 0 (`???` learns nothing).
- **0 species with any bit ≥ 58 set** — i.e. no compat field indexes past the 58-entry
  gTMHMMoves array (this is the relevant "out-of-range" condition for this table, since the
  bits index gTMHMMoves rather than carrying move ids directly; and gTMHMMoves is already
  proven all-valid). 373 species learn ≥ 1 TM/HM.
- **55 species differ from FireRed** (Ash Gray adjusted some gen-1 TM compat). All within the
  58-bit field. Every move any of these bits can reference is a valid gTMHMMoves entry ⇒ valid.

## 3c. Egg moves (gEggMoves) — CLEAN

- Stream parses to a clean 0xFFFF terminator (1139 u16 words, end 0x0825F7F2).
- **165 species**, **973 move entries**. **0 bad species headers** (all 1–411),
  **0 bad move ids** (all 1–354; actual range 2–350).
- **Identical to FireRed** — Ash Gray did not modify the egg-move table (0 species differ).

---

## Method notes / scanners
- Read-only Python (`/tmp/evo_dump.py`, `/tmp/learn_audit.py`, `/tmp/learn_verify2.py`,
  `/tmp/tmhm_verify.py`, `/tmp/egg_audit.py`, `/tmp/find_compat_xref.py`, `/tmp/final_xref.py`).
- For every table: (1) locate base by content signature, (2) confirm by code xref, (3)
  range-check the **whole** table (not just diffs), (4) diff AG-vs-FR to isolate custom data,
  (5) dump raw bytes of every flagged/custom entry to confirm it is a real literal value, not a
  misread pointer/var.
- No over-claims: zero entries were flagged as bugs. The only items worth a footnote are the
  inert `NONE`-method evo slot on #72 (harmless dead data) and the in-range secondary
  gTMHMMoves edits — neither is an integrity fault.
