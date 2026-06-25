# Pokémon Ash Gray — bug-fix fork (release notes)

A community bug-fix fork of **Pokémon Ash Gray** (beta 4.5.3) by **metapod23**. All credit for the hack itself goes to metapod23 — this is an unofficial patch that fixes crashes, softlocks, and save-corruption traps in the released 4.5.3 build. It changes no story, maps, or balance beyond the fixes listed below.

This is a diagnosis-and-repair effort: every fix was reproduced and A/B-verified in a headless emulator (libmgba) against an unmodified 4.5.3 ROM. Where something could **not** be fixed safely, it's disclosed under "Known caveats" rather than papered over.

## How to apply

The fork ships as an **IPS patch** you apply to a clean FireRed ROM. It does **not** include any copyrighted ROM.

1. Obtain a clean **Pokémon FireRed Version (USA) v1.0** ROM ("No-Intro" / "squirrels").
   - MD5 `e26ee0d44e809351c8ce2d73c7400cdd`
   - CRC-32 `dd88761c`
2. Apply `patches/ashgray-fork.ips` to it with any IPS patcher (Lunar IPS, Flips, etc.).
   - Patch MD5 `d013c124c4ce2b2c7b73166e64c4cc91`
3. Verify the output matches the fork build:
   - MD5 `5cffa700fee4378fd9c48e8ba849a2d0`
   - CRC-32 `63478921`
   - SHA-256 `a08055484c8366768d3e98e2dbed0998641abd2899ffbfc8d7f132925875f7a1`

If your output hash matches, you have the exact fork. If it doesn't, your base ROM isn't the right FireRed.

**Saves:** the fork uses the same save format as clean 4.5.3, so a `.sav` is interchangeable between them. (Read the box-storage caveat below before migrating a long save.)

**RetroAchievements:** the fork's hash differs from the original, so RA will **not** recognize it. For credited RA play, use the unmodified 4.5.3 ROM (MD5 `92262059190c05a5615be6b98612fb14`, RA game #5245) — see `HARDCORE-RA-GUIDE.md`. Play the fork for the best bug-fixed run; play the original for RA credit.

## What's fixed

**Crashes & freezes**
- Breeding-center crash when talking to Jessie & James / Butch & Cassidy with a full party (a malformed condition that bypassed the party-full guard). This was a main-quest blocker.
- Grampa Canyon "pickaxe from the rival" softlock (a scripted NPC march that collided with terrain and never released).
- Underwater-cave black-screen freeze after Dragonite's tournament message (an unfilled text buffer + overlapping map-script tables).
- Tangelo Island "back of the building" crash on arrival in the Orange Islands (a warp to a deleted map).
- "Talk to an NPC → freeze" at the doll-competition scene and one sibling map (a corrupt script pointer that ran the braille text renderer on garbage and looped forever).

**Progression softlocks**
- Indigo Plateau guard refusing entry with all 8 badges + the exam passed (the real eligibility check was unreachable; now it runs).
- Prof. Oak stalling the league send-off if your party was full on league day.
- Declining Dragonite's invitation to Mewtwo's island making the game unwinnable (decline now re-offers instead of dead-ending).
- A Pallet Town ledge-jump that hopped you into a sealed one-tile pocket two screens into the game.
- The Cerulean Gym pool-walkway tip that trapped you with no way back.
- A batch of dangling warps across the game that could spawn you at garbage coordinates (21 reachable cases corrected).

**Quality / data**
- Running shoes restored on 44 maps where the editor had zeroed the run flag (Pallet Town included).
- Bike usage restored on 16 maps that had lost biking permission.
- The Teachy TV (flagged "broken — don't use" by the author) now safely declines instead of dropping you into a black void.
- A wild-encounter level typo (surfing Staryu spawning at a wrapped level).
- Several text fixes ("INIDGO PLATEAU" → "INDIGO", "recieved" → "received" ×2, "sacrfices" → "sacrifices", a duplicated word).

**Save-corruption mitigation (the "Bad Eggs") — partial**
- Ash Gray's story progress physically overlaps your PC storage, which is the real, non-cheat cause of the infamous Bad Eggs and a lot of "backtracking corrupted my save" reports. The fork can't fully fix that without a save-format rewrite, but it **reserves the three hazardous boxes (Box 2, Box 3, Box 6) in the storage UI** so you can no longer deposit a Pokémon into a slot the game will overwrite. See the caveat below for what this does and doesn't cover.

## Known caveats (read before playing)

These are the honest limits of the fork. Some are bugs we could not safely fix; others are by design in the original hack.

- **The early-forest scripted battle does *not* appear to freeze (earlier report retracted).** An earlier note flagged the Pidgeotto/Caterpie scripted battles as freezing during the battle-end fade. On a careful in-engine re-test (~19 runs plus a 10-timing RNG sweep, driven to both a whiteout and a clean return to the field) it **could not be reproduced** — every run completed normally. The original "freeze" was almost certainly a testing artifact (a battle menu waiting for input that looked stuck), not a real hang. Details in `audit/f1-battle-freeze-retest.md`. As far as we can tell the fork has **no remaining game-blocking bug** — though we can't prove a universal negative across every RNG path, so in the unlikely event you hit a hard hang in that opening battle, a reset and retry will clear it.
- **The Bad-Egg box reserve protects new placements only.** It stops you from *depositing* into a hazard box and stops fresh Bad Eggs from box use going forward. It does **not** heal a save that already has a Pokémon sitting in Box 2, 3, or 6 — move those out **before** patching if you can. It also reduces usable boxes from 14 to 11. The safe rule still applies as a habit: keep anything you care about out of Box 3 and Box 6, and don't completely fill Box 2.
- **The hack is unfinished.** Content ends partway through the Orange Islands (around the third Orange-League gym); Gym 4 and the Drake/Pummelo finale were never built. That's the original hack's frontier, not a bug.
- **A couple of minor issues are documented, not fixed:** the first Jessie & James battle can make switched-in Pokémon briefly invisible (engine-level); the Sunny-Town medicine errand lets you "deliver" without the medicine and pocket a free bicycle (harmless); the girl-disguise battle sprite is mis-colored (needs art).
- **Some things look like bugs but are intentional** (anime-accurate): HMs are replaced by key items (Cut/Surf "not working" is expected), Brock's first battle is a scripted loss even if you win, Pikachu refuses to battle Misty, and Charmander/Charizard disobeys after evolving.

## For tinkerers

The full per-issue analysis, reproduction steps, and fix tooling are in this repo: see `ISSUES.md` (the tracker), `audit/` (deep dives, including the Bad-Egg variable→box map), `tools/fix_*.py` (each fix as a byte-guarded script), and `PROVENANCE.md` (exact build recipe and checksums). The fork is fully reproducible from clean FireRed + the committed patch.
