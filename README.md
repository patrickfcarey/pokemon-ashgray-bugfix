# Ash Gray — bug-fix fork

A personal bug-fixing **fork of Pokémon Ash Gray** (FireRed hack by **metapod23**).
All credit for Ash Gray goes to metapod23; this repo only adds targeted fixes on top.

**This repo does not contain any ROM.** It ships the *patch* and the tooling/analysis.
To build the forked ROM, apply `patches/ashgray-fork.ips` to a clean
**Pokémon FireRed (USA) v1.0** ("squirrels", CRC32 `dd88761c`).

## Layout
- `base/firered.gba`   — clean FireRed v1.0 (git-ignored; supply your own)
- `rom/ashgray.gba`    — working ROM you edit (git-ignored)
- `tools/` — analysis & build scripts:
  - `diff.py`      — change footprint vs FireRed
  - `maps.py`      — walk map/event tables, list script offsets
  - `text.py`      — decode the anime dialogue (for proofreading)
  - `makepatch.py` — regenerate `patches/ashgray-fork.ips` from `rom/ashgray.gba`
  - `patcher.py`   — apply IPS/BPS/UPS (to verify the patch round-trips)
- `audit/` — analysis output (footprint, maps, dialogue dump)
- `patches/` — the distributable fork patch

## Workflow
1. Edit bytes/scripts/text in `rom/ashgray.gba` (via the tools).
2. `python3 tools/makepatch.py` → updates `patches/ashgray-fork.ips`.
3. Verify it round-trips against clean FireRed before sharing.

## Findings so far
- Ash Gray relocated the **map bank table** to `0x73E2F4` (expanded space) to add maps.
- ~1.5 MB of new scripts+dialogue live at `0x71A000–0x9A0000`; ~4,880 strings decoded.
- See `audit/` for details.

> Note on sharing: respect metapod23's wishes — credit the original, don't claim
> ownership, and check the project's terms before redistributing a forked build.
