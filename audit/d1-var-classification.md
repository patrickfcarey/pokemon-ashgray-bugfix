# D1 var classification — gate vs marker, by box (2026-06-13)

**Question:** of the ~190 story vars that overlap PC storage (D1), which can *misroute the
game* when a box slot is corrupted (GATE = read in a branch) versus which merely get
*clobbered* (MARKER = written by a script, so the script stomps a Pokémon parked there)?

**Method (`_emu/var_classify.py`):** scan the script bank (0x800000–0x8D0000).
- **GATE** = a `compare`(0x21) immediately followed by `goto_if`/`call_if`(0x06/07) with a
  valid ROM pointer — a real read-and-branch. Very low noise (the structure is specific).
- **MARKER** = `setvar`(0x16, value <0x80) but never read in any branch.
- **STATE** = both (most are): misroutes *and* clobbers.
Each var's PC location = `sb1 + 0x1000 + 2*(id−0x4000)` → offset into the storage buffer.

## Headline

| | count |
|---|---|
| storage-overlapping story vars | **192** |
| **GATE-capable** (read → can misroute the game) | **134** |
| MARKER-only (write → clobbers your Pokémon) | 58 |

**The hack's whole mid/late story is built on Box 3 and Box 6 vars.** Corrupting those
boxes doesn't just make Bad Eggs — it can silently rewrite which story branch the game
takes. L13/L14/L15 and the Koga/#6a finding are four confirmed instances of a class with
**~134 members**.

## By box

| Box | gate-capable (misroute) | marker-only (clobber) | notes |
|---|---|---|---|
| **Box 2** | 3 | 5 | only the **tail**, slots 27–29 (first corruption point) |
| **Box 3** | **89** | 35 | the minefield — slots 0,1,4,5,6,7,8,10,17 |
| **Box 6** | **42** | 18 | late game — slots 10,11,12,13 (0x70xx vars) |
| Box 1, 4, 5, 7–14 | 0 | 0 | **clean** |

## Deposit-exposure timeline (why "extended play / backtracking breaks saves")

The PC fills the current box front-to-back and auto-advances 1→2→3…:
- **Box 1 (30 slots): 100% safe.**
- **Box 2 slots 0–26: safe.** First corruption is **Box 2 slot 27** → var `0x6000`
  ("You can't warp to a place you haven't been") — i.e., ~**57 Pokémon can be stored
  before anything breaks**, which is why casual players never see it and heavy players do.
- **Box 3: pervasive.** The first Pokémon in Box 3 (slot 0) corrupts the slot-0 cluster
  `0x6060–0x6079`, which includes the opening Spearow chase (`0x6079`, = L14).
- **Box 6: the late-game store**, where 0x70xx vars live.

## The confirmed cases (this classification unifies them)

| var | box/slot | event | issue |
|---|---|---|---|
| 0x6079 | B3 s0 | opening Spearow chase | **L14** |
| 0x6086 | B3 s1 | the abandoned CHARMANDER | (lead) |
| 0x6105 | B3 s4 | Seymour / Mt. Moon "weird couple" | **L15** |
| 0x6113 | B3 s4 | Cerulean gym (DAISY) | **L13** |
| 0x6158 | B3 s6 | Grampa Canyon pickaxe | F4 area |
| 0x7014 | B6 s10 | Indigo Plateau gate | **L1** |

## "Other broken things" this surfaced — high-exposure gates not yet tracked

Labelled by the dialogue near a gate site (a *sample* — high-reference vars span many
scenes, so treat as a hint, not a precise assignment):

| var | box/slot | sites | sampled event |
|---|---|---|---|
| **0x6300** | B3 s17 | **92** | league/battle scheduling ("no matches scheduled") — a **master** var |
| **0x6173** | B3 s7 | **83** | stadium/ranch announcer (LARAMIE) — a **master** var |
| 0x7005 | B6 s10 | 28 | late-game crisis ("our POKéMON are fighting…") |
| 0x6192 | B3 s7 | 20 | a BROCK event |
| 0x6301 | B3 s17 | 19 | a surf/current event |
| 0x7012 | B6 s10 | 12 | **Celadon gym — ERIKA** (another badge gym, like Koga) |
| 0x6167 / 0x6069 | B3 s6/s0 | 14/7 | **P1 Grand Prix** championship |
| 0x6194 | B3 s7 | 15 | the SHELLDER / well puzzle |
| 0x6143 | B3 s5 | 15 | Snorlax / Poké Flute |
| 0x6137 | B3 s5 | 10 | the KAS/YAS gym feud |
| 0x6117 / 0x6306 / 0x6303 | B3 s4/s17 | 12/15/13 | the video-phone / call-mom system |
| 0x6082 | B3 s1 | 3 | the Pokémon race/bike event |
| 0x6100 | B3 s4 | 6 | a town restaurant event |

**Two master vars (`0x6173`, `0x6300`, ~90 references each, both in Box 3)** are the most
destructive single-slot corruptions — they gate story logic game-wide.

## Honesty / scope

- **The GATE/MARKER classification, box/slot mapping, and counts (134/58) are solid** — they
  depend only on opcode + address arithmetic, not on knowing which event a var drives.
- **The event LABELS are unreliable** and should be treated as guesses, not facts. The
  single-nearest-text method mislabels even known-good vars (it tags `0x6113`/Cerulean as
  "Valencia Island"). **Concrete burn (2026-06-13):** `0x6155` was labeled and reported as
  "Koga / Soul badge" → it is actually the **P1 Grand Prix** var (confirmed by decompiling its
  dispatcher: BLACK BELT / P1 CHAMPIONSHIP / ANTHONY). The "Celadon/Erika 0x7012", "P1 Grand
  Prix 0x6167", etc. rows below are **unverified hints** — any one could be similarly wrong.
- "GATE" = **structurally misroutable** (read in a branch). Only **L13/L14/L15** are
  *confirmed* instances (live A/B-verified separately). The rest are exposures of the same
  mechanism, **not** individually reproduced, and **not** mapped to specific events with
  confidence.
- All of this is one root cause = **D1**. Fix = relocate the var space (save-format rework);
  the only player-side mitigation is avoiding Box 2 (tail) / Box 3 / Box 6.
