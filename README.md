# Pokémon Ash Gray — bug-fix fork

An unofficial **bug-fix patch** for **Pokémon Ash Gray** (beta 4.5.3) by **metapod23** — the FireRed romhack that retells Season 1 of the anime. It fixes crashes, softlocks, and the infamous "Bad Egg" save corruption in the released build, **without changing any story, maps, or balance** beyond the fixes.

> ⚠️ **This is a fan project. No ROM is included here** — only IPS and BPS patches you apply to a clean FireRed you legally own. See [`NOTICE`](NOTICE). All credit for Ash Gray itself goes to metapod23.

Every fix was reproduced and A/B-verified in a headless emulator against an unmodified 4.5.3 ROM. Where something couldn't be fixed safely, it's disclosed in [`RELEASE.md`](RELEASE.md) rather than papered over.

## What it fixes (highlights)

- **The "Bad Eggs" — root-caused and mitigated.** Ash Gray's story progress physically overlaps your PC storage, which is the real, non-cheat cause of Bad Eggs (and a lot of "backtracking corrupted my save" reports). The patch **reserves the three hazardous boxes (Box 2, 3, 6)** in the storage UI so you can no longer deposit a Pokémon into a slot the game will overwrite. (Diagnosis + the full variable→box map are in [`audit/`](audit/).)
- **Crashes fixed:** breeding-center (Jessie & James / Butch & Cassidy with a full party), Grampa Canyon "pickaxe from the rival" softlock, the underwater-cave black screen after Dragonite's message, the Tangelo Island arrival crash, and a "talk to an NPC → freeze" at the doll-competition scene.
- **Softlocks fixed:** the Indigo Plateau guard refusing entry with all 8 badges, Prof. Oak stalling the league send-off, declining Dragonite's invite making the game unwinnable, the Cerulean Gym pool-walkway trap, a Pallet Town ledge that sealed you in a one-tile pocket, and a batch of dangling warps.
- **Quality:** running shoes restored on 44 maps, bike usage on 16 maps, the "broken — don't use" Teachy TV made safe, a wild-encounter level typo, and several text fixes.

Full per-issue list with verification notes: **[`RELEASE.md`](RELEASE.md)** · live tracker: **[`ISSUES.md`](ISSUES.md)**.

## How to apply

You apply the patch to a clean **Pokémon FireRed (USA)** ROM — specifically the **original release**: the No-Intro **"squirrels"** dump, a.k.a. **rev 0** (this is what "v1.0" means here). It is **not** the `(USA, Europe) (Rev 1)` revision — that's a different ROM with different hashes, and the patch will **not** produce a correct result on it. Two equivalent patch formats are provided (`.ips` and `.bps`); use whichever your patcher prefers — both produce the identical fork. Verify your base against all three checksums:

| | MD5 | SHA-1 | CRC-32 |
|---|---|---|---|
| **Base** — FireRed (USA), rev 0 | `e26ee0d44e809351c8ce2d73c7400cdd` | `41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc` | `dd88761c` |
| **Patch (IPS)** — `patches/ashgray-fork.ips` | `1640a0a9780eb487c45d80ab4c9a4d40` | `459532fda7453369e8106b1c94582998609b6476` | — |
| **Patch (BPS)** — `patches/ashgray-fork.bps` | `aed795498023b7ca85ecb4bed9603ca8` | — | — |
| **Result** — this fork | `f6b3162afc333dcf543597066d8b3091` | `d67f8678674f0a1739bcde1601687ed5ec35e940` | `e36b3c4d` |

1. Get a clean **rev 0** FireRed (USA) ROM (matching all three base checksums above — it's 16,777,216 bytes).
2. Apply either [`patches/ashgray-fork.ips`](patches/ashgray-fork.ips) (IPS) or [`patches/ashgray-fork.bps`](patches/ashgray-fork.bps) (BPS) with any patcher (Lunar IPS, Flips, beat, etc.).
3. Verify the output is MD5 `f6b3162a…` / SHA-256 `6fdfc3bbcad462a2384792a2aaebefe0dafb7398bfb6af4729a5a3b8357e77cd`. If it matches, you have the exact fork.

**Saves** use the same format as clean 4.5.3, so a `.sav` is interchangeable. (Read the box-storage caveat in `RELEASE.md` before migrating a long save — the reserve protects *new* placements, not a Pokémon already sitting in a hazard box.)

## RetroAchievements

The fork's hash differs from the original, so RA will **not** recognize it. For credited RA play, use the unmodified 4.5.3 ROM (MD5 `92262059190c05a5615be6b98612fb14`, RA game #5245). Play the fork for the best bug-fixed run; play the original for RA credit. See [`HARDCORE-RA-GUIDE.md`](HARDCORE-RA-GUIDE.md).

## Known limits (read before playing)

- The hack is **unfinished** — content ends partway through the Orange Islands (~the third Orange-League gym). That's metapod23's frontier, not a bug.
- Some things look like bugs but are **intentional** (anime-accurate): HMs replaced by key items, Brock's scripted first-battle loss, Pikachu refusing Misty, Charizard disobedience.
- A few minor issues are documented, not fixed — see `RELEASE.md`.

## For tinkerers

- [`patches/`](patches/) — the distributable IPS and BPS patches (both produce the identical fork). [`PROVENANCE.md`](PROVENANCE.md) — exact build recipe + checksums (rebuildable from clean FireRed).
- [`tools/`](tools/) — each fix as a byte-guarded Python script, a script decompiler, a patch applier (`patcher.py`, IPS + BPS) and BPS generator (`make_bps.py`), and analysis tools.
- [`tools/research/`](tools/research/) — the investigation & reproduction toolchain (the scripts that *found* and reproduced each bug: repro builders, state probes, the Thumb disassembler, the variable↔box mapping).
- [`tools/emu/`](tools/emu/) — the headless libmgba verification harness used to reproduce and prove every fix.
- [`audit/`](audit/) — deep dives (the Bad-Egg architecture, per-domain sweeps, the freeze-class analysis).

## Credits & license

- **Pokémon Ash Gray** © **metapod23**. Pokémon / FireRed © Nintendo · Game Freak · The Pokémon Company.
- This fork's tooling and documentation are MIT-licensed ([`LICENSE`](LICENSE)); the patch is offered as a fan bug-fix under the terms in [`NOTICE`](NOTICE).
