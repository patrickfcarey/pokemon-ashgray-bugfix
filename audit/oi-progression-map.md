# Orange Islands — progression map & boundary (2026-06-14)

Goal: separate *fixable* OI script/progression blockers from the genuine (unfixable) content-end.
Tools: `tools/oi_map_graph.py` (name/dims/warps/conns per map), `tools/oi_reach.py` (warp+conn BFS
reachability). Map-name table @0x083f1d88.

## Structure

- **OI overworld islands** live in **bank 3** (nid 144–149): `3.13` (TANGELO), `3.14`, `3.15`, `3.16`,
  `3.18`. Each island's town/buildings live in a dedicated bank:
  `33→3.13` (Tangelo), `34→3.14`, `35→3.15`, `36→3.16`, `37→3.18`.
- The islands are **isolated walk-clusters** — the warp+connection BFS from the start reaches 314 maps
  but NOT 3.14/3.15/3.18 (and most of banks 31/32/34/35/37/40/41/42). They're reached only by **script
  warps** = the **custom ferry**.
- **Ferry**: a hand-coded, data-table-driven system (destination table @`0x087534B8`, entries
  `[index byte][warp cmd]`) routing to `3.5 / 3.14 / 3.30 / 3.48 / 3.55 / 3.61 / 3.69` etc. Decompiles as
  data, not standard script → custom routine; its exact destination-gating is unreversed.
- **Corpse back-rooms** (deleted, FF'd layouts): `33.3, 34.2, 35.2, 37.0, 37.1`. All warps into them were
  already **sealed (F6/L5)** — unreachable, can't crash. They mark where maps were cut.

## Content density (audit/02-maps.md script refs)

| island | overworld refs | buildings | verdict |
|--------|----------------|-----------|---------|
| Tangelo 3.13 | 11 | bank 33: 33.2=8 | **rich** (Tracey, Cissy gym) |
| 3.14 | 0 | bank 34: 3 lone NPCs | thin/stub |
| 3.15 | 5 | bank 35: 35.0=5, 35.1=7, 35.6=6 | **populated** (Pinkan + event) |
| 3.16 | 3 | bank 36: 36.0=9 | **populated** |
| **3.18** | **0** | **bank 37: 0 scripts (corpses only)** | **EMPTY STUB → content-end** |

Events confirmed present (dialogue): **Nastina/Tentacool–Tentacruel**, **Princess-dollset competition**
(Misty/Jessie), **Maiden's Peak** — these are the playable OI set-pieces (and where **F7**'s crash lives).

## Content reach vs the anime saga (ROM-wide name search, authoritative)

The Orange League = 4 Orange Crew gyms → Champion Drake at Pummelo Stadium. ROM presence:

| saga beat | island | leader / badge | in ROM? |
|-----------|--------|----------------|---------|
| arrival | Valencia | Prof. Ivy / GS Ball (Brock stays) | ✅ (IVY 16, GS BALL 8) |
| meet Tracey | Tangelo | — (Pokémon Park) | ✅ (TRACEY 31) |
| Gym 1 | Mikan | **Cissy** / Coral-Eye | ✅ (CISSY 22, CORAL 2, MIKAN 9) |
| Gym 2 | Navel | **Danny** / Sea Ruby | ✅ (DANNY 25, SEA RUBY 5, NAVEL 11) |
| Gym 3 | Trovita | **Rudy** / Spike Shell | ✅ (RUDY 20, SPIKE 12, TROVITA 15) |
| Gym 4 | **Kumquat** | **Luana** / Jade Star | ❌ **ABSENT** (KUMQUAT 0, LUANA 0, JADE 0) |
| **FINAL BOSS** | **Pummelo** | **Drake** / Orange League | ❌ **ABSENT** (PUMMELO 0; "DRAKE" only the Indigo E4 ref) |

Filler islands present: Pinkan(3), Mandarin(15, Lorelei), Moro(7), + Nastina/Tentacool & Maiden's Peak
sea episodes (anime-Kanto, used as travel filler). Lapras travel present (LAPRAS 24).

## Boundary verdict (CORRECTED)

- The game implements the OI **through Gym 3 (Rudy / Trovita / Spike Shell)**, plus filler islands.
- **Content-END is between Gym 3 and Gym 4**: the 4th gym (Luana/Kumquat) and the entire finale
  (Drake/Pummelo Stadium) were **never built**. So the saga's *final boss* does not exist in 4.5.3.
- The empty stub `3.18`/bank 37 is an **unbuilt next island** (the dev's frontier — likely the
  intended Kumquat/Pummelo), NOT a designed ending. Earlier "ends right after Tangelo" was an
  under-estimate (the gym islands 3.14/3.15/3.16 = Mikan/Navel/Trovita DO have built gym content).
- So: the *unfixable* ceiling is the missing Gym 4 + Drake finale. The only *fixable* progression
  blockers possible are bugs WITHIN the 3 built gyms / the ferry that reaches them (e.g. F7).

## Gym verification (static, 2026-06-14)

Decompiled the three gyms past their `trainerbattle` (the tool stops there). Each has real
completion logic and sets progression state:

| gym | trainer | post-battle script | sets |
|-----|---------|--------------------|------|
| 1 | 0x21 | @0x8A1654 | setflag 0x1350/0x1351, clearflag 0x1352, **setvar 0x7036=1** |
| 2 | 0x22 | @0x8A1764 | setflag 0x1352, setflag 0x0249, **setvar 0x7036=3** |
| 3 | 0x23 | @0x8A283F | setflag 0x1355 |

- **No crash / corpse-warp / obviously-broken gate found** in the gym or event scripts. The three gyms
  are structurally built and *do* complete + advance state (good sign for "beatable").
- **★ The OI gym progression var `0x7036` lives in Box 6 (slot 11) — a D1 hazard var.** So the Orange
  Crew gym sequence is **corruptible by D1** (depositing a Pokémon in Box 6 clobbers the gym-progress var
  → a GATE-class break of the OI badge chain, same mechanism as L14/L15). **The box-reserve fix (which
  reserves Box 6) directly protects OI gym progression** — a concrete tie between the two investigations.
  (F6's `0x7035` is the neighboring Box-6 slot; the OI arc leans on this region.)

## Limits / still-open (honest)
- **Custom gym MECHANICS** (Cissy accuracy/wave-race, Danny ice-race, Rudy targets) can't be statically
  proven winnable — needs in-engine play with valid late-game state (feasibility wall: hours to reach, or
  a huge flag-poke setup).
- **Full ferry gate-chain** (which `checkflag`/`compare` actually gates each island on the prior gym's
  flag/var) not exhaustively traced — the gates live on the custom ferry routine / island-access scripts.
- **F7** — the named "lady event" crash; its offsets are dialogue strings not scripts, so it needs the
  real event person-script + a repro (which wants the story state). Unpinned.
