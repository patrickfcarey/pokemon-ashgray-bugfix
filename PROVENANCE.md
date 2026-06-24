# Ash Gray — ROM provenance & artifact record

Where every ROM came from, how to rebuild it, and the checksums to verify it.
ROMs themselves live **outside this git repo** (in the `gba/` library, per repo policy — see README);
this record + the fork patch are the source of truth. Verified 2026-06-15.

> ✅ **Git status (2026-06-24):** the working tree is committed — `patches/ashgray-fork.ips`, this
> `PROVENANCE.md`, the fix tooling, and the audit docs are all tracked. Git now reproduces the current
> `5cffa700` build: clean FireRed + the committed `ashgray-fork.ips` → MD5 `5cffa700…`, CRC `63478921`
> (verified). The rebuild recipes below are truthful against `HEAD`.

## The base

| | value |
|---|---|
| ROM | **Pokémon FireRed Version (USA)** — No-Intro v1.0 ("squirrels") |
| file | `ashgray-fork/base/firered.gba` |
| MD5 | `e26ee0d44e809351c8ce2d73c7400cdd` |
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
| kept ROM | `gba/Ashgray-fork.gba`  — rebuilt 2026-06-16 |
| **MD5** | **`5cffa700fee4378fd9c48e8ba849a2d0`** |
| SHA-256 | `a08055484c8366768d3e98e2dbed0998641abd2899ffbfc8d7f132925875f7a1` |
| CRC-32 | `63478921` |

**Source:** `ashgray-fork/patches/ashgray-fork.ips` (MD5 `d013c124c4ce2b2c7b73166e64c4cc91`) — tracked,
and **committed** as of 2026-06-24, so this `5cffa700` build is captured in git history.

**Rebuild recipe:**
```
python3 ashgray-fork/tools/patcher.py \
  ashgray-fork/base/firered.gba \
  ashgray-fork/patches/ashgray-fork.ips \
  ashgray-fork/rom/ashgray.gba
# -> MD5 5cffa700… , CRC 63478921
```

**Fork build history (hash moves as fixes land):** `04d28f01` (box-reserve era) → `6e5cf85e` (+ person33
braille-freeze fix) → `43216f9f` (+ person4/map-1.59 braille-freeze fix) → **`5cffa700`** (+ wild-level typo
fix: map (0,17) Surf Staryu min>max). Full fix list: `ISSUES.md`.

> **Built & kept (2026-06-16):** `gba/Ashgray-fork.gba` is the current fork (MD5 `5cffa700…`,
> CRC `63478921`), built from `firered.gba` + `ashgray-fork.ips`, sitting alongside the clean
> `gba/Pokemon Ash Gray (4.5.3).gba`.
>
> **Removed (2026-06-16):** the stale duplicate `gba/Pokemon Ash Gray (4.5.3, fork).gba` (an older fork
> build, MD5 `5ec9a7052a615465a928f99a24b2590b`, CRC `0cc1dfb9`) was **deleted** — superseded by
> `Ashgray-fork.gba` (`5cffa700`). Hash kept here for the record; it was a stale build no one needed.

## Integrity table (quick reference)

| artifact | MD5 | CRC-32 | RA? |
|---|---|---|---|
| FireRed (USA) v1.0 base | `e26ee0d4…cdd` | `dd88761c` | n/a |
| **Ash Gray 4.5.3 (original / RA)** | `92262059…fb14` | `10ef71a7` | ✅ recognized |
| **Ash Gray 4.5.3 fork (current)** | `5cffa700…2d0` | `63478921` | ❌ not recognized |

## Which to play

- **RetroAchievements (credited hardcore):** the original `9226…` ROM. See `HARDCORE-RA-GUIDE.md`.
- **Best bug-fixed run (no RA credit):** the fork `43216f9f…` ROM.
- Same `.sav` works in both (identical save format).
