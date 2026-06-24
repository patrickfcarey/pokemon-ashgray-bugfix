# D1 gym badge-blocks — "won 6 badges, shows 5" (2026-06-13)

**Finding:** several gym leaders gate their badge path on a **Box 3 story var** (D1-overlapping).
Depositing a Pokémon in the matching Box 3 slot writes near-random data into that var, which the
gym reads as a large out-of-range value → routes to a dead-end/"done" branch → **the badge becomes
unobtainable.** This is the real, reproduced mechanism behind the community's "I won 6 badges, it
shows 5": not a display bug and not the badge-award code (both sound), but the gym **staging** —
same root cause as D1 / L14 / L15.

This was found the authoritative way (`_emu/trace_all_gyms.py` → `trace_gym_gates.py` →
per-gym decompile + value-routing `gym_values.py`/`marsh_values.py`), *after* an earlier region-scan
guess (Koga via 0x6155) was traced, disproven, and retracted. Koga, Erika (Rainbow) and Giovanni
(Earth) are **safe** — bare/clean badge paths, no storage var.

## The mechanism

A gym leader's interaction script begins by branching on a story var that tracks "how far into this
gym's anime sequence are you." That var physically lives in PC storage (D1). Because the comparison
is 16-bit against a tiny legit set (e.g. `<3`, `==5`), a corrupted slot (near-random box data) is
almost always outside the legit range → the "in-progress battle/give" branch is skipped → you land in
the "done"/filler/dead-end branch with **no battle, no give, and the badge flag never set.**

## Per-gym routing

| Gym (leader, map) | gate var | Box 3 slot | legit values | corrupt (out-of-range) routes to | "6-shows-5" risk |
|---|---|---|---|---|---|
| **Marsh** (Sabrina, 14.3) | `0x6072` | **slot 0** | 0,1,2,3 | `>3` → `release;end` → **NPC inert** | **HIGH — LIVE-REPRODUCED** |
| **Boulder** (Brock, 6.2) | `0x6082` | **slot 1** | 3,4,5,6 (battle@`==5`) | `≠5` → "Your POKéMON aren't powerful enough / come back when you're stronger" | **HIGH — LIVE-REPRODUCED** |
| **Cascade** (Daisy, 7.5) | `0x6190` | **slot 7** | 1,2,3 | `≥3` → "the Underwater Ballet was a success!" (no give) | **HIGH — LIVE-REPRODUCED** |
| Cascade gate B | `0x6113` (=L13 var) | **slot 4** | 1,2,3,4 | give needs `≥3`; `<3` also blocks the give | medium (also = the L13 pool bug) |
| **Volcano** (Blaine, 12.0) | `0x6186` | **slot 7** | 1,3,4,5 | `==2/4` → "FIRE BLAST" filler; else → "I guess you solved my riddle!" → advances the puzzle on nothing | **LIVE-REPRODUCED** (`volcano_proof.png`) — a riddle-state **desync**, not a clean block |
| Thunder (Surge, 9.6) | `0x6088` | slot 1 | 1,2 | gates a `setrespawn`, **not** the battle | **safe** (incidental) |
| Rainbow / Soul / Earth | — | — | — | no D1 gate on badge path | **safe** |

## Which Box 3 deposit bricks which gym

The PC fills Box 3 front-to-back, so this is roughly the order a player trips them:

- **slot 0** → **Marsh** (Sabrina goes silent)
- **slot 1** → **Boulder** (Brock: "come back when you're stronger")
- **slot 4** → **Cascade** gate B (`0x6113`) + the **L13** Cerulean-pool re-trigger
- **slot 7** → **Cascade** (`0x6190` → "ballet success") + **Volcano** riddle desync

## Live proofs (Marsh, Boulder, Cascade)

All three: warp into the gym (bedroom-stairs redirect via `mk_warp_test.py`, destination warp
repointed adjacent to the leader), stand on one tile, press A — **only the Box-3 var differs** between
the two frames.

- **Marsh** `_emu/marsh_proof.png` (`marsh_repro2.rig`): at (23,3) facing Sabrina. `0x6072=0x40` →
  no textbox, **inert**; `=0` → **"Hehehehe!"** match offer.
- **Boulder** `_emu/boulder_proof.png` (`boulder_repro.rig`/`boulder_active.rig`): at (6,6) below
  Brock. `0x6082=0x40` (+flag 0x1010 set) → **"Your POKéMON aren't powerful enough… come back when
  you're stronger"**; `=0` → **"Who goes there?"** (Brock engages).
- **Cascade** `_emu/cascade_proof.png` (`cascade_blocked.rig`/`cascade_active.rig`): at (8,4) below
  Daisy. `0x6190=0x40` → **"The Underwater Ballet was a success!"** (no give); `0x6113=3,0x6190=0` →
  **"That was quite a battle! We're giving this BADGE to you"** (badge handed over). The starkest of
  the three — the badge itself is given or withheld on the value of a single box slot.

### Real-flow proof (Marsh, the actual player action) — `_emu/marsh_real_proof.png`

The three repros above poke the gate var directly. This one mirrors what a player actually does — a
**Box deposit** — and shows it corrupts the gym (`marsh_real.rig`):
1. Confirmed the aliasing **live**: `gPokemonStoragePtr` (0x03005010) `= 0x02029344 = sb1 + 0x3DE8`,
   so the storage buffer sits right after SaveBlock1 and **Box 3 slot 0 byte 56 (0x0202A640) IS var
   `0x6072` (sb1+0x50E4)** — the same RAM.
2. Extracted the player's **real PIKACHU** (80-byte BoxPokemon from `gPlayerParty[0]` in `pikachu.ss`)
   and **deposited it into Box 3 slot 0** by writing those 80 bytes to the storage buffer (0x0202A608) —
   i.e. wrote to the *box*, not the var.
3. The gym var `0x6072` went **0 → 0x2923** on its own — that's PIKACHU's own encrypted-data byte 56–57,
   not a value we chose. → Sabrina **inert** (no response).
4. Cleared the slot (withdrew) → var back to 0 → **"Hehehehe!"** she works again.

So: *deposit a Pokémon in Box 3 → the Saffron gym variable takes on that Pokémon's data → Sabrina won't
give the Marsh badge.* The only step done by RAM write rather than the in-game PC menu is the deposit
copy itself; the bytes, the destination slot, and the corruption are all the real thing.

### Sabrina is multi-stage — you fight her *before* the badge exists (`sabrina_midarc_proof.png`)

Decompiling her battle's win-continuation (0x8055c7): winning the first Sabrina fight does **not** give
the badge — she says *"You are no match for my psychic power. Be my friend…"*, sets `0x6073=1`, and
`warpteleport`s you away (the doll plot). The badge comes after the later Haunter/laugh stages. So the
Saffron gym is a genuine multi-stage arc, and the whole arc lives in **three Box-3-slot-0 vars**
(`0x6072`/`0x6073`/`0x6074`, bytes 56/58/60). **Reproduced the mid-arc dead-end:** set her to stage 2
(as if you'd fought her and were progressing) → she engages ("Hehehehe!"); deposit a Pokémon in Box 3
slot 0 → all three arc vars go to garbage (0x2923 / 0xdb9e / 0x2947) → she's inert, the arc dead-ends,
no badge. This is the literal *"I was partway through the gym, stored a Pokémon, and it broke"* report.

## No "give-without-credit" split (all 8 badges checked, 2026-06-13)

Confirmed (`_emu/check_badge_split.py` + control-flow decompile of every `setflag 0x82x` site) that
**no gym can show its badge-award dialogue while failing to set the flag.** The announce and the
`setflag` are always coupled, in one of two shapes:

- **Battle gyms (Boulder, Thunder, Soul, Marsh, + Erika's thundershock path):** the epilogue sets the
  badge flag *first* (`special 0x173 → setflag 0x4Bx → setflag 0x82x`), and the "Now you have the X
  BADGE" effect text comes *after*. The announce literally cannot run before the flag.
- **Give gyms (Cascade, Erika/Gloom path, Earth/Team-Rocket-drop, Volcano/riddle):** the "here's your
  badge / you received the X BADGE" message is immediately followed by the `setflag` with no
  conditional branch between them, e.g. Erika: `"…received the RAINBOW BADGE from ERIKA!" →
  closemessage → setflag 0x823`.

All 12 setter sites (Boulder ×1, Cascade ×1, Thunder ×1, Rainbow ×3, Soul ×1, Marsh ×1, Volcano ×2,
Earth ×2) check out. The one site the coarse linear scan flagged (Rainbow 0x83cc9c) was a false
positive — the branch sits upstream of the announce, not between it and the flag.

**So "6 shows 5" is always a clean block** (the leader routes to a wrong/inert branch *before* any
badge dialogue), never a leader saying "you got it" while the flag silently fails. And the badge flags
themselves (sb1+0xFE4) are non-storage, so a deposit can neither fake a give nor un-set an earned badge.

## Potential fix

**Real fix = D1 var relocation** (move the 0x6xxx story vars out of the storage-overlapping region +
save-format migration). This is the only thing that fixes *all* of D1 (badge blocks, Bad Eggs, L14/L15
nav softlocks) at once. It's the big "from-scratch" rework the project owner already flagged.

**Targeted per-gym band-aid (corruption-proof for the badge only):** re-guard each exposed gym on its
**badge flag** (which lives at sb1+0xFE4, *not* in storage) instead of — or before — the story var.
Pattern: `checkflag <badge>; if set → "done" dialogue; else → battle/give`. Because the badge flag
can't be storage-corrupted, the player can always be routed back to the battle if they don't yet have
the badge, so the badge can never be permanently blocked.
- **Marsh prototype — BUILT & VERIFIED** (`tools/fix_marsh_reguard.py`, `_emu/marsh_reguard_proof.png`).
  Redirect the dispatcher entry `@0x806505 → goto 0xC00150` (free space); the re-guarded dispatcher is
  `checkflag 0x825; goto_if SET → 0x80D67C (done)` then the **original** staging
  (`compare 0x6072,3; <→0x805406; ==→0x80D67C`) with the `>3` fall-through redirected to `0x805406`
  (engage) instead of the dead-end. Three cases tested on a patched ROM, depositing the real PIKACHU
  to corrupt the var:
  - **normal play** (0x6072=0, no badge) → "Hehehehe!" match offer — **byte-identical, no regression**.
  - **corrupt var** (0x6072=0x2923, no badge) → "Hehehehe!" — **engages instead of inert** (badge still earnable).
  - **badge already earned** (flag 0x825 set + corrupt var) → "What? Another battle?" rematch — **short-circuits to done** (corruption-proof).
- *Caveat:* per-gym free-space surgery; the same shape applies to Boulder/Cascade/Volcano (each needs its
  own dispatcher patch). It only patches the **badge** symptom — not the other D1 damage (Bad Eggs,
  navigation softlocks, the loops). It's a band-aid; the cure is the var relocation.

## Honest scope

- Marsh is **reproduced in-engine**; Boulder/Cascade are traced (decompiled dispatchers + value
  routing) but not yet live-reproduced; Volcano is exposed but its effect is value-dependent
  (skip-ahead/softlock more than clean block); Thunder is effectively safe.
- "Corrupt value" = near-random box data at the var's 2-byte offset; the block branch fires for almost
  all values (only the tiny legit set avoids it), so a deposit in the matching slot blocks the badge
  nearly every time — this is not a rare edge case.
