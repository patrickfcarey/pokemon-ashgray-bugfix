# D1 — reproduced & root-caused catalog (authoritative, 2026-06-13)

One artifact listing every D1 finding we have reproduced and/or root-caused, with its variable,
its PC-box location, what corruption does, how it was reproduced, and the proof. Supersedes the
finding-by-finding notes scattered across `ISSUES.md`; the deep dives live in
`d1-var-classification.md` and `d1-gym-badge-blocks.md`.

## The one root cause

FireRed's `VarSet`/`VarGet` index a fixed 256-entry array at `sb1+0x1000` (var IDs 0x4000–0x40FF)
with **no bounds check**. Ash Gray's story vars run to 0x70xx, so:

```
addr(var N) = sb1 + 0x1000 + 2*(N − 0x4000)
```

Vars ≥ 0x56F4 overflow **past** SaveBlock1 (vanilla size 0x3D88) into the **PC storage buffer**,
which sits immediately after it. **Verified live this session:** `gPokemonStoragePtr` (0x03005010)
`= 0x02029344 = sb1 + 0x3DE8`. So a story var and a boxed-Pokémon byte are the *same RAM*, and the
corruption runs both directions:

- **GATE (storage → logic):** depositing a Pokémon overwrites a var the game *reads* → wrong branch
  (loops, gym blocks). The Pokémon's encrypted bytes are ~random, so the wrong branch fires almost
  every time.
- **MARKER (logic → storage):** the game *writes* a story var → overwrites a boxed Pokémon's bytes →
  checksum fails → **Bad Egg**.

Boxes 1, 4, 5, 7–14 are clean; the story vars cluster in **Box 3** (bulk), **Box 6** (0x70xx), and the
**Box 2 tail** (slots 27–29).

## Reproduced (in-engine) and root-caused

| # | Finding | Var(s) | PC location | What corruption does | Proof |
|---|---|---|---|---|---|
| 1 | **Bad Eggs (core)** | 0x6079 | Box 3 slot 0 +70 | a story-var *write* lands in a boxed Pokémon's data → Bad Egg (MARKER dir.) | `badegg_demo.rig` — poked 0xCAFE "as var 0x6079", `fe ca` appeared in the box mon |
| 2 | **L14 — Spearow loop** | 0x6079 | Box 3 slot 0 +70 | a box write resets the chase-complete var → opening Spearow scene re-arms | `d1repro_proof.png` |
| 3 | **L13 — Cerulean pool trap** | 0x6113 | Box 3 slot 4 +58 | gym-pool state var; symptom reproduced + fixed, var later tied to D1 | `l13_proof.png` |
| 4 | **Marsh badge block** | 0x6072/0x6073/0x6074 | Box 3 slot 0 +56/+58/+60 | Sabrina goes inert → Marsh badge unreachable | `marsh_proof.png`, `marsh_real_proof.png` (real PIKACHU deposited), `sabrina_midarc_proof.png` (mid-arc dead-end) |
| 5 | **Boulder badge block** | 0x6082 | Box 3 slot 1 +8 | Brock: "come back when you're stronger" → no battle, no badge | `boulder_proof.png` |
| 6 | **Cascade badge block** | 0x6190 | Box 3 slot 7 +68 | Daisy: "the Underwater Ballet was a success!" → badge withheld | `cascade_proof.png` |
| 7 | **Volcano (desync)** | 0x6186 | Box 3 slot 7 +48 | Blaine: "I guess you solved my riddle!" → advances the puzzle on nothing (a riddle-state **desync**, not a clean block) | `volcano_proof.png` |

## Root-caused / same class (not separately screenshot-reproduced)

| Finding | Var(s) | PC location | Status |
|---|---|---|---|
| **L15 — Zubat/Seymour loop** | 0x6105 | Box 3 slot 4 +30 | scene-retrigger; root-caused to a Box-3 var, same shape as L14 |
| **The full class** | 134 gate-vars | Box 2 tail / Box 3 / Box 6 | every story branch that reads a Box-3/6 var is misroutable; see `d1-var-classification.md` |
| Soul / Rainbow / Earth / Thunder badges | — | — | **SAFE** — badge path has no D1 gate (verified) |

## Deposit-order map (why "extended play / backtracking breaks saves")

The PC fills front-to-back; this is roughly the order a player trips them:

- **Box 1 + Box 2 slots 0–26:** safe (~57 Pokémon stored before anything breaks).
- **Box 2 slot 27:** first corruption (var 0x6000, "can't warp where you haven't been").
- **Box 3 slot 0:** Spearow loop (L14) **and** the whole Sabrina/Marsh arc (0x6072/73/74).
- **Box 3 slot 1:** Boulder (Brock).
- **Box 3 slot 4:** Mt. Moon/Seymour (L15) **and** Cerulean/Cascade gate B (0x6113).
- **Box 3 slot 7:** Cascade gate A (0x6190) **and** Volcano (0x6186).
- **Box 6 slots 10–13:** the 0x70xx late-game vars (incl. the Indigo gate, L1).

**Box 4/5 are genuinely clean — the Box 3→6 jump is real, not a detector blind spot** (`check_box45.py`,
2026-06-13). Verified 4 ways: coord-event trigger tables (the opcode-scan blind spot) cluster in Box
2/3/6 with none in 4/5; the noisy all-opcode sweep flags 4/5 candidates but also flags provably-clean
Box 7/8/9 (= noise); the low-noise set∩compare set (136 real vars) has zero in Box 4/5 or the id-gap;
and every 4/5 byte-match sits in ARM code / graphics / text data, never the script bank. Cause: the
author numbered story vars `0x6000–0x6306` then jumped to a fresh `0x7000` block — IDs `0x6307–0x6FFF`
(which would map to Box 4/5) were simply never allocated. **Reserve scope = Box 2 (tail), Box 3, Box 6
only; Box 1, 4, 5, 7–14 fully usable.**

## What we proved does NOT happen

- **No "win the badge battle, then get denied."** All 8 badges' announce-text and `setflag` are coupled
  (no skippable branch between them). The block always lands *before* the award. (`check_badge_split.py`)
- **Badges can't be un-set or faked.** The badge flags live at sb1+0xFE4 (inside SaveBlock1, *not*
  storage), so a deposit can neither forge a give nor erase an earned badge.

## Bottom line

The spine of the community's reports — Bad Eggs, the forced-scene loops, the "backtracking breaks my
save," and "I did the gym but got no badge" — is one architectural bug, reproduced in-engine across
**seven** findings and root-caused across the rest. The *whole* bug is **not byte-fixable**; the real fix
is relocating the var space (+ save-format migration). Player-side mitigation: avoid Box 2 (tail), Box 3,
and Box 6.

**Per-gym band-aid (prototyped):** the *badge-block* symptom specifically *can* be byte-patched, by
re-guarding each exposed gym on its (non-storage) badge flag. **Built & verified for Marsh**
(`tools/fix_marsh_reguard.py`, `_emu/marsh_reguard_proof.png`): on a patched ROM, the same Box-3 deposit
that bricks Sabrina now leaves her engageable (badge still earnable), normal play is unchanged, and
badge-holders short-circuit to "done." It's a band-aid (one gym, badge-only) — not the cure — but it
proves the badge blocks are individually fixable if a from-scratch relocation isn't on the table. See
`d1-gym-badge-blocks.md`.
