# Progression dead-end audit (2026-06-15)

Hunt for **permanent progression dead-ends** beyond the already-fixed L1/L2/L9 — i.e.
gates that can leave the player unable to advance with **no recovery path**, on the main
Kanto quest or the reachable Orange Islands (OI). Method per the brief: trace every
critical-path gate's required flag/var to a *reachable, non-missable* setter, and look for
branches that forget to advance (L2/L9 shape).

**Verdict: NO NEW permanent dead-end found.** The OI-entry chain and the OI gym/ferry chain
are sound (forced setters + recoverable declines). One ROM-wide orphan-gate scan surfaced
only two truly-never-set gates, both proven benign. Details below. Anything I could not
reach-verify in-engine is marked.

Tools written this session (all in /tmp, throwaway): `find_ops.py` (flag/var op finder),
`w2_findmap.py` (which bank.map's scripts reach an address, follows trainerbattle conts),
`w2_orphan2.py` (walk all reachable scripts; report gates whose flag/var has no setter in
walked code), `w2_check.py` (raw-scan whole ROM to confirm true-zero-setter), `w2_item.py`/
`w2_give.py` (item id + give/check sites), `w2_mapinfo.py` (warps/conns), `w2_tb.py`
(trainerbattle pointer decoder). **Decompiler offset note:** `tools/decomp.py <0xADDR>` takes
a **file offset** (= ROM addr − 0x08000000); `<bank,map>` mode takes real ids. Easy to get
wrong (I did at first).

---

## 1. Orange-Islands ENTRY from Kanto — VERIFIED SOUND (the one gate that would matter most)

The whole OI arc hangs off getting from Kanto to **Valencia Island**. Two candidate routes
exist in the ROM; traced both.

### Main route: Oak's errand → rigged raffle → BLIMP (the real path)
- **Forced trigger:** the post-party Prof-Oak cutscene (`@0x0881CB0`) hands the player the
  "fetch the GS BALL from PROF. IVY on VALENCIA ISLAND" errand and does
  **`setvar 0x6306, 2`** (`@0x0881CD9`), then warps. This is a mandatory story scene.
- **Raffle (`map 3.78`, the Route-1-river raffle hut, person1 `@0x08B55CB`):** branches on
  **`compare 0x6306, 2 ; goto_if cond=4`** (`@0x08B55CC`). I decoded the engine condition
  table at `0x083A7248` (3 bytes/row, indexed by LESS/EQUAL/GREATER): **cond 4 = `>=`**.
  So once the errand is given (`0x6306 ≥ 2`), the raffle is **rigged to always award the
  GRAND PRIZE blimp** (sets flag `0x1343`, guarded by a `checkflag 0x1343` so it can't
  re-award). Because the test is `>=`, every later story state (3/4/5) still wins it — **no
  skip-window.** Before the errand, the same NPC runs the *random* raffle (small prizes /
  "didn't win"), which is harmless and re-enterable.
- **Blimp boarding** (airship hangar, person at `@0x085F543` → yes-branch `@0x0872B7E` →
  completion `@0x08820BD`): the "Would you ride?" prompt; **yes** boards you (`setvar 0x7030`,
  warp to Valencia, `setflag 0x1344`); **no** is fully re-offerable ("when you're ready…").
- **0x6306 state machine:** set to 1 at several early sites (`0x0880B34`, `0x0882791`,
  `0x089DC7E`), to 2 at the forced Oak errand. It is a Box-3 D1 var (the `0x6300` master),
  so it is *D1-corruptible* — but that's the known D1 architecture (box-reserve-mitigated),
  **not a new gate bug**. The gate logic itself is correct and the setter is forced.

⇒ **OI entry cannot be permanently missed.** Even reaching the raffle "too early" is
recoverable (the rig switches on the moment the errand var hits 2).

### Vestigial alt route: the "TROPIC PASS" ship — HARMLESS (not a dead-end)
- Item **TROPIC PASS = 0x170** exists in the item table, and an NPC string says *"you need
  the TROPIC PASS to board the ship to sail the ORANGE ARCHIPELAGO."*
- **The TROPIC PASS is never given to the player:** ROM-wide there is **no** clean give —
  no `setorcopyvar 0x8000,0x0170` and no `additem 0x0170 qty=1` anywhere (`w2_give.py`).
  The only real `checkitem 0x170` is a tiny `checkitem; return` subroutine (`@0x0872 9BE2`)
  in the custom ferry region.
- **But the "need TROPIC PASS" NPC gates nothing.** That string lives in a stand-alone
  person script (`person0 @0x0809B1B`: *loadword → callstd 2 → **end***) that is **reused as
  a decorative dock NPC on ≥9 maps** (32.4, 33.4, 35.5, 36.2, …). It has no yesno, no warp,
  no flag — talking to it just prints the line. The actual OI travel is the blimp (above)
  plus the in-OI Lapras/ferries (below).
⇒ The unobtainable TROPIC PASS is dead content, **not** a blocked route. No dead-end.

---

## 2. OI gym / inter-island chain — VERIFIED RECOVERABLE

The Orange Crew arc the hack actually ships: Valencia → **Tangelo** (Tracey + Lapras) →
**Mikan / Cissy (Gym 1)** → **Navel / Danny (Gym 2)** → **Mandarin / Trovitopolis** →
**Trovita / Rudy (Gym 3)**. (Gym 4 Luana / Drake finale were never authored — known
content-end, not a dead-end.)

**Topology (warps + map-edge connections, `w2_mapinfo.py`):** the OI is mostly **one big
walk-connected overworld web**, not isolated ferry hops. e.g. Tangelo `3.13`↕`3.86`↕Mikan
`3.16`; the Mandarin cluster `3.122–3.118–3.112–3.124` all connect by map edges; Navel
overworld `3.17` connects to `3.62/3.100/3.45`. So most island-to-island movement is just
walking — nothing to gate-strand. Only two real *script* travel gates exist:

- **Tangelo Lapras arc — var `0x7036`** (Tangelo island `3.13` + park `33.2`). Self-contained
  state machine 0→2 (TR Lapras-rescue scene, `3.13 person5 @0x087D9F8`) →3 (Lapras given) →4
  (Tracey send-off "nearest GYM is MIKAN", `@0x0872FDC`). Gated only behind flag `0x1353`
  (Tracey intro, set by a Pokémon-Center NPC — non-missable). The decline at the Lapras-give
  is re-offerable (object persists). And Mikan is **walk-reachable from Tangelo anyway**
  (`3.13→3.86→3.16`), so the Lapras is not even a hard travel gate. *Note:* `0x7036` is a
  Box-6 D1 var — D1-corruptible (box-reserve-mitigated), not a new bug. (The ISSUES.md note
  that "OI gym progress uses 0x7036" is really this Lapras/Tangelo arc; I found **no**
  gym-leader badge epilogue that sets 0x7036 — the gym-completion flags are `0x1350-0x1355`,
  and the badges proper are handled inside the gym minigames.)

- **Trovita ferry — var `0x7064`** (Mandarin/Trovitopolis `3.118 person4 @0x08BB7E4`):
  `compare 0x7064, 3 ; if == → "All aboard!" warp to Trovita 3.15`, else **"The ferry isn't
  running quite yet. Come back in a little while."** (no warp). This is the one genuine
  L1-shaped gate in the OI — **but its setter chain is reachable AND recoverable:**
  `0x7064` advances via the **Bulbasaur-in-the-sewer** anime quest — 0→1 (talk Officer Jenny,
  `3.118 person1 @0x08BB382`) → sewer `warphole` → **pick up Bulbasaur** (`3.119 person1
  @0x08B9267`, `setvar 0x7064, 2`) → talk Jenny again (`@0x08BB3FC`, `setvar 0x7064, 3`). The
  pickup is a yes/no; declining leaves the Bulbasaur in place (re-grabbable), and the pickup
  `setvar`s 2 unconditionally regardless of the prior value, so the chain can't wedge at an
  intermediate state. Trovita `3.15` also has an **unconditional return ferry** ("set sail to
  MANDARIN", person1 `@0x08BBFCD`) and a direct walk-connection to `3.118` — you can never be
  stranded on Trovita. *Note:* `0x7064` is a Box-6 D1 var (D1-corruptible, box-reserve-
  mitigated) — same D1 class, not a new bug.

- **Shamouti / 2nd-movie hub (Maren, `@0x08E7F82`/`0x08E7FB4`):** "Where would you like to
  go" → Butwal/Cleopatra/Shamouti-Shrine/Lightning/Ice/Fire — all **unconditional
  `warpsilent`s**, no gating. Benign side-area. Not on the gym critical path.

⇒ No inter-island stranding; the single conditional ferry has a forced+recoverable setter.

---

## 3. ROM-wide orphan-gate scan — only 2 true-orphans, both BENIGN

`w2_orphan2.py` walked **5 438** reachable script blocks (all map persons/triggers/signs/
mapscripts, following call/goto/if **and** trainerbattle continuation pointers) and collected
every `checkflag`/`compare`-var gate vs every `setflag`/`setvar` setter. It flagged 30 gate
flags + 10 gate vars with "no setter in walked code." Cross-checking each against a **raw
whole-ROM setter scan** (`w2_check.py`) showed all but two are set somewhere (my walker simply
didn't reach the setter site — e.g. setters behind trainerbattle paths or std-script
dispatch). The two with **literally zero setters anywhere**:

- **Flag `0x150A`** — checked at `0x08CD089` (map `0.19`, the **TAD / Charizard-obedience**
  event). It's a `checkflag 0x150A ; call_if cond=1 → give ICE HEAL`. Since 0x150A is never
  set, the conditional **never fires → the optional ICE HEAL gift is just disabled**, and
  execution falls straight through to the next line. The event's real progression runs on
  `var 0x7070` (which *is* set, `@0x08CCD41`). ICE HEAL is a buyable consumable. **Not a
  block.**
- **"Var `0x0FA1`"** — `compare 0x0FA1, 0x1B ; call_if cond=1 → applymovement` in the
  WARTORTLE/Squirtle-Squad cutscene (`map 2.57 trig4 @0x085847C`). It sits among sibling
  `compare 0x4001(player-Y), …` movement-positioning conditionals; when it doesn't fire the
  WARTORTLE just uses default movement, and the trigger ends with an **unconditional**
  `setvar 0x6189, 2`. A cosmetic movement tweak, **not a progression gate.**

The remaining "orphans" (flags `0x126B-0x126D`, `0x1320-0x1323`, `0x129B`, `0x1366`, `0x1375`,
`0x139B`, `0x1098/0x1099`, `0x1012`, `0x1182/0x1185`, `0x1192`, `0x1000`, …; vars `0x6137`,
`0x6176`, `0x6184`, `0x6197`, `0x6301`, `0x6302`, `0x7055`, …) all have real setters in the
script bank — confirmed by raw scan. (Several flags' only setters are in the new-game-init /
`special` / relocated-table regions = engine/system flags, e.g. `0x834` = OAK's-LAB-box-full.)

---

## 4. L2-shape spot-checks (branches that forget to advance) — CLEAN

- **Togepi EGG handoff** (`map 2.38 person0 @0x0815B45`): decline → no flag, **re-offerable**;
  **full-party "make room"** branch → `release` with **no `removeobject` and no advancement
  flag**, so it's correctly re-offerable; accept-with-room → `giveegg ; setflag 0x1034 ;
  setvar 0x6159,3`. This is the *correct* version of the L2 pattern (the no-room branch does
  NOT consume the giver or skip a needed flag). Side-collectible anyway.
- The blimp-boarding "no" and the Lapras / Bulbasaur / Trovita-ferry declines are all
  re-offerable (above). No forgotten-advance found on these.

---

## Honest limits
- **Custom OI gym minigames** (Cissy wave-race, Danny ice-climb, Rudy targets) and their
  in-gym **badge-award** logic live behind `trainerbattle` continuations and custom specials
  that the static decompiler stops at; consistent with the prior audit, I did **not** re-derive
  their winnability (needs in-engine late-game state). I checked only that the *travel/access*
  gates around them are sound. The OI gym-completion flags `0x1350-0x1355` and `0x7036` are
  set on reachable scripts; none gate a ferry/warp in a way that can strand.
- The custom **ferry data-routine** (`@0x087534B8`, referenced from the relocated event-table
  at `0x087313C0`) is hand-coded ASM/data and remains unreversed; I confirmed the *script-side*
  ferry NPCs (Trovita, Mandarin, Maren) are sound, but a latent bug inside that ASM dispatcher
  is not statically excludable.
- The orphan-gate walker can't follow std-script-table dispatch or some dynamic warps, so
  "reachable" there is approximate; I mitigated this by raw-scanning the whole ROM for setters
  (which sees everything) before clearing each candidate.
- D1-class corruption (box deposits clobbering `0x6306`/`0x7036`/`0x7064` etc.) can break
  these chains, but that's the documented, box-reserve-mitigated D1 architecture — **not** a
  separate gate bug, per the brief. Noted where relevant; not counted as a finding.

**Bottom line:** no third L1/L2/L9-class permanent dead-end on the main quest or reachable
Orange Islands. The most load-bearing gate (OI entry) is rigged to be unmissable; the one
conditional in-OI ferry (Trovita) has a forced, recoverable setter; the only never-satisfiable
gates in reachable code are a disabled optional item-give and a cosmetic movement check.
