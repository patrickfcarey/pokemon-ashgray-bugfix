# Ash Gray — ROM provenance & artifact record

Where every ROM came from, how to rebuild it, and the checksums to verify it.
ROMs themselves live **outside this git repo** (in the `gba/` library, per repo policy — see README);
this record + the fork patch are the source of truth. Verified 2026-06-15.

> ✅ **Git status (2026-07-02):** the working tree is committed — `patches/ashgray-fork.ips`, this
> `PROVENANCE.md`, the fix tooling, and the audit docs are all tracked. Git reproduces the current
> `f6b3162a` build: clean FireRed + the committed `ashgray-fork.ips` → MD5 `f6b3162a…`, CRC `e36b3c4d`
> (verified). The rebuild recipes below are truthful against `HEAD`. *(The previous public build was
> `5cffa700…` / CRC `63478921`, superseded by the F6b position-gate repair — see ISSUES.md.)*

## The base

| | value |
|---|---|
| ROM | **Pokémon FireRed Version (USA)** — original "squirrels" dump, **rev 0** (*not* the `(USA, Europe) (Rev 1)` revision) |
| file | `ashgray-fork/base/firered.gba` |
| MD5 | `e26ee0d44e809351c8ce2d73c7400cdd` |
| SHA-1 | `41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc` |
| SHA-256 | `3d0c79f1627022e18765766f6cb5ea067f6b5bf7dca115552189ad65a5c3a8ac` |
| CRC-32 | `dd88761c` |

Everything below is built on this exact base.

## 1. Original released Ash Gray 4.5.3 — the **RetroAchievements-matching** ROM

This is the ROM to load for **credited hardcore RA play** (RA game #5245). Keep it untouched.

| | value |
|---|---|
| kept ROM | `gba/Pokemon Ash Gray (4.5.3).gba` |
| **MD5** | **`92262059190c05a5615be6b98612fb14`**  ← the RA-supported checksum |
| SHA-256 | `4cbc7665358593fdf49ec8b8c1635a3a5d35f6cf09d846cc1fd858af4cdd8c17` |
| CRC-32 | `10ef71a7` |

**Source / how we got it:** `gba/_patches/AshGray_RA.zip` (the RA-distributed patch). Contents:
- `Pokemon - FireRed Version - AshGray (v4.5.3) (metapod23).bps` — metapod23's v4.5.3 BPS patch
- `readme.txt` — says "Use with: No Intro / Pokemon - FireRed Version (USA).gba / `e26ee0d4…` / `DD88761C`"

**Rebuild recipe (verified — BPS reports VERIFIED OK, output MD5 = `9226…fb14`):**
```
python3 ashgray-fork/tools/patcher.py \
  ashgray-fork/base/firered.gba \
  "gba/_patches/AshGray_RA.zip → Pokemon - FireRed Version - AshGray (v4.5.3) (metapod23).bps" \
  "gba/Pokemon Ash Gray (4.5.3).gba"
```

## 2. Our bug-fix fork — the **patched** ROM

This is the ROM to load for the **best fixed playthrough** (all our bug fixes incl. the D1 box-reserve).
Its hash differs from the original, so RA will **not** recognize it — fixed experience, no RA credit.
Shares 4.5.3's save format, so its `.sav` is interchangeable with the clean ROM.

| | value |
|---|---|
| working ROM | `ashgray-fork/rom/ashgray.gba` (git-ignored) |
| kept ROM | `gba/Pokemon Ash Gray (4.5.3, bugfix fork).gba`  — rebuilt 2026-07-02 |
| **MD5** | **`f6b3162afc333dcf543597066d8b3091`** |
| SHA-256 | `6fdfc3bbcad462a2384792a2aaebefe0dafb7398bfb6af4729a5a3b8357e77cd` |
| CRC-32 | `e36b3c4d` |

**Source:** `ashgray-fork/patches/ashgray-fork.ips` (MD5 `1640a0a9780eb487c45d80ab4c9a4d40`) — tracked
and committed, so this `f6b3162a` build is captured in git history (as was `5cffa700` before it).

**Rebuild recipe:**
```
python3 ashgray-fork/tools/patcher.py \
  ashgray-fork/base/firered.gba \
  ashgray-fork/patches/ashgray-fork.ips \
  ashgray-fork/rom/ashgray.gba
# -> MD5 f6b3162a… , CRC e36b3c4d
```

**Fork build history (hash moves as fixes land):** `04d28f01` (box-reserve era) → `6e5cf85e` (+ person33
braille-freeze fix) → `43216f9f` (+ person4/map-1.59 braille-freeze fix) → `5cffa700` (+ wild-level typo
fix: map (0,17) Surf Staryu min>max) → **`f6b3162a`** (+ F6b v2: the Pokémon-Park position-gate wrapper
repaired — v1 mis-assembled `getplayerxy`, so the y<3 gate never actually evaluated; see ISSUES.md F6).
Full fix list: `ISSUES.md`.

> **Built & kept (2026-07-02):** `gba/Pokemon Ash Gray (4.5.3, bugfix fork).gba` is the current fork (MD5 `f6b3162a…`,
> CRC `e36b3c4d`), built from `firered.gba` + `ashgray-fork.ips`, sitting alongside the clean
> `gba/Pokemon Ash Gray (4.5.3).gba`. (Previous kept build `5cffa700…`/CRC `63478921`, 2026-06-16, superseded.)
>
> **Removed (2026-06-16):** the stale duplicate `gba/Pokemon Ash Gray (4.5.3, fork).gba` (an older fork
> build, MD5 `5ec9a7052a615465a928f99a24b2590b`, CRC `0cc1dfb9`) was **deleted** — superseded by
> `Ashgray-fork.gba` (`5cffa700`). Hash kept here for the record; it was a stale build no one needed.

## Integrity table (quick reference)

| artifact | MD5 | CRC-32 | RA? |
|---|---|---|---|
| FireRed (USA) **rev 0** base ("squirrels", *not* Rev 1) | `e26ee0d4…cdd` | `dd88761c` | n/a |
| **Ash Gray 4.5.3 (original / RA)** | `92262059…fb14` | `10ef71a7` | ✅ recognized |
| **Ash Gray 4.5.3 fork (current)** | `f6b3162a…091` | `e36b3c4d` | ❌ not recognized |

## Which to play

- **RetroAchievements (credited hardcore):** the original `9226…` ROM. See `HARDCORE-RA-GUIDE.md`.
- **Best bug-fixed run (no RA credit):** the fork `f6b3162a…` ROM.
- Same `.sav` works in both (identical save format).
