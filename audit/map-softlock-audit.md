# Ash Gray — map-data softlock audit (enter-but-can't-leave traps)

Goal: find NEW player-facing softlocks of the M1/L13 class — tiles/regions a player can
ENTER but cannot LEAVE (no walkable exit, no warp, no script escape). Built on the existing
collision/layout parsers (`tools/walkmap.py`, `tools/pathfind.py`, `tools/oi_map_graph.py`).

**Bottom line:** after scanning all 540 reachable maps with a movement model validated
against the two known traps, **0 new softlocks were confirmed.** Pattern A (M1-class "ledge
prison") = **0** ROM-wide. Every Pattern-B / "reachable-can't-exit" candidate resolved to a
false positive (NPC-occupied tile, unreachable filler, map-connection edge, stair tile, or —
the only non-trivial class — normal **water-shore / pier-edge** tiles that the model
over-flags). The two already-known fixes (M1 3.66, L13 7.5) are still intact.

---

## Map-data format (reverse-engineered + validated)

Per-tile **cell** is a `u16` in the map blockdata (layout header +0x0C):
- bits 0–9  = metatile/block index (`& 0x3FF`)
- bits 10–11 = collision (`(c>>10)&3`; 0 = passable)
- bits 12–15 = elevation / z (`(c>>12)&0xF`)

**Metatile behavior** (encodes ledges, water, stairs, water-edges): the tileset header is
`+0x00 isCompressed, +0x01 isSecondary, +0x04 tiles, +0x08 palettes, +0x0C metatiles,
+0x10 callback, +0x14 metatileAttributes`. Attributes are **u32 per metatile**, behavior =
**low byte** (`u32(attr + blk*4) & 0xFF`). Primary tileset holds blocks `0x000–0x27F`
(640 = `0x280`); the secondary tileset holds `0x280+` (indexed at `blk-0x280`).

This was nailed down by validation, not assumption:
- Reading attributes as **u16** gave garbage (staggered `0x00` interleave = reading half-
  entries). Reading as **u32 low-byte** reproduced the canonical FRLG ledge cluster
  (`0x38/0x39/0x3A/0x3B` at the standard `0x083–0x0C9` primary block range) **and** the exact
  values from the L13 fix notes: 7.5 secondary block `0x299` → behavior **0xF4** (the "rim"),
  block `0x2A4` → **0x70** (the "walkway"). Both match → format confirmed.

**Behavior constants used** (FRLG):
- Ledges (one-way): `0x38`=JUMP_EAST, `0x39`=JUMP_WEST, `0x3A`=JUMP_NORTH, `0x3B`=JUMP_SOUTH.
- Water (impassable on foot, needs Surf): `0x10–0x1F` (gym pool / sea are `0x15`).
- Stairs / free elevation crossing: `0x21`, `0xFE` (census: high "bridges-different-elevation" rate).
- Water-edge / shore / "rim": `0xF0–0xFC` (the shoreline boundary between land and water).

## Movement model

A move from `(x,y)` onto neighbor `(nx,ny)` is allowed iff the target is foot-walkable
(collision 0 **and** behavior not water) and:
- **ledge**: if the target carries a ledge behavior, it may be entered only moving in its
  arrow direction, and it carries you to the tile one beyond (the M1 "jump landing");
- **elevation**: crossing requires equal elevation, OR either tile's z is `0`/`15`
  (transition), OR a stair behavior is on either side.

Reachability is BFS from real entrances only: foot-walkable **warp** tiles + **connected
map borders** (NPC/sign tiles are *not* treated as escapes — talking to a trainer doesn't
un-stick a movement softlock).

### Validation (the model catches the known traps)
- **L13** (7.5): reverting tile `(8,9)` to its buggy state (block `0x299`/`0xF4`, elev 1) makes
  the detector flag `(8,9)` as a **dead-end** (every non-water neighbor is the elev-4 walkway,
  and leaving the rim back onto the board is elevation-vetoed) — exactly the documented trap.
- **M1** (3.66): the fixed pocket `(25,16)` is solid (`col=1`); fix confirmed intact. (M1's
  buggy cell value isn't recoverable from the patched ROM, so M1 was validated by mechanism +
  confirming the fix held, not by byte-revert.)

---

## Candidate scan results (540 maps)

**Pattern A — M1-class "ledge jump into a solid-walled pocket": 0 candidates ROM-wide.**
With the corrected `u32` behavior table there are no ledge tiles whose jump-landing is a
solid-enclosed dead cell anywhere in the game. (Note: the earlier `u16` mis-read invented
hundreds of phantom ledges and ~146 phantom pockets — all artifacts, now gone.)

**Strongest net — "reachable but cannot return to any warp/connected border" (NPC tiles
excluded):** only 3 maps, all the same water-edge class:

| map | tiles | behavior | verdict |
|-----|-------|----------|---------|
| 3.5  | 13 (`25–37,31` area) | `0xFA/0xFC` pier edge | **rejected** (shore class — see below) |
| 3.15 | 3 (`29–31,38`)        | `0xFA/0xFB/0xFC` pier tip | **rejected** (shore class) |
| 7.5  | 8 (`4–7,6`,`9–12,6`)  | `0xF3` pool top-rim | **rejected** (rim ring live-verified safe in L13 work) |

A looser net (small dead-regions, before the strict return-to-exit filter) additionally
surfaced these, all **rejected**:

| map.tile | why rejected |
|----------|--------------|
| 1.5 (9,8), 1.5 (28,8), 3.94 (27,8), 3.67 (32,16) | tile is an **NPC/sign position** (`script_xy`), not a tile the player occupies; sealed by solids |
| 3.100 (39,4) | isolated tile on a **connected border** (`conns=right`); crossing from the neighbor map returns via the same connection — not a trap |
| 3.125 (20,44) | behavior `0x21` = **stairs**; unreachable from real seeds anyway |
| 3.127 (18,5) | **unreachable** from this map's warps/connections (no inbound on-foot path) |

### Why the water-shore / "rim" class is a false positive (not a trap)

The decisive evidence: behavior **`0xF4`** is the behavior that *did* trap at L13 — but it is
simply the **normal water-shoreline tile**. There are **126 foot-walkable `0xF4` tiles**
across the game (every pond/lake/sea edge: 1.110, 3.1, 3.3, 3.7, 3.44, 3.67, 3.75, 3.89, 5.8,
7.5 …), and **none of them is board-adjacent**. They are the land/deck-side shore tiles you
stand on to look at (or Surf onto) water; you walk on and off them freely from the adjacent
land. L13 was a trap not because `0xF4` is dangerous but because of a **specific geometry**:
a `0xF4` shore tile sat mid-board (the elev-4 walkway had a 1-tile gap at (8,9)), so you
walked the board straight onto an elev-1 shore tile and the elevation rule then vetoed every
exit. The fix re-stamped that one cell to match the board (elev 4 / `0x70`).

The remaining 3.5 / 3.15 / 7.5 candidates are ordinary shore/pier-edge rows of this same
class. The model flags them only because of an over-strict assumption (treating shore/rim
behaviors as one-way "enter-but-not-leave"); the 126-tile census shows the assumption is
wrong in general. For 7.5 specifically, the **L13 fix authors already live-probed the pool's
rim ring and declared it safe** except the single (8,9) tip — that ring *includes* the
`0xF3` top row flagged here.

### In-engine verification status (honest)

I attempted live repro of the pier/rim candidates (3.15, 7.5) with the libmgba rig. The
`warpto` recipe + the save/reset/Continue dance **works on plain maps** (verified: warped to
Route 1 4.0 and walked the player), but **fails on exactly these maps** because they run an
**on-entry cutscene that `lockall`s the player** (3.15 opens with the rescued-NPC scene
"HEEEELP! … I'm very grateful to you …"; 7.5 is the gym with its water/setup script). The
field never hands back control, so the player can't be walked onto the candidate tile. This
is the same warpto limitation noted in the rig docs (script-heavy maps), so these tiles are
**static-only** — they could not be walked in/out in-engine. I weight the prior **live**
verification of the 7.5 rim ring, plus the 126-tile `0xF4`-is-just-shoreline census, as
sufficient to classify them false positives, but I did not personally walk into them.

---

## Verdict

- **Confirmed new softlocks: 0.**
- **Pattern A (ledge prison): 0** ROM-wide (clean, high-confidence static result).
- **Pattern B / can't-exit:** all candidates are NPC tiles, unreachable filler, connection
  edges, stairs, or normal water-shore/pier-edge tiles. The water-shore class is shown to be
  benign by a ROM-wide census (126 such tiles, all ordinary shorelines) and, for 7.5, by the
  prior live-verified L13 finding.
- **No proposed map-data fix** — there is nothing confirmed to fix. The two known traps
  (M1 3.66, L13 7.5) remain correctly fixed.

## Tooling
Detector + validation scripts live in `/tmp` (`final_detect.py` = the validated model;
`val_final.py`/`trace*.py` = L13/M1 validation; `find_0xF4.py` = the shoreline census;
`global_trap.py` = the strongest can't-exit net). They read `rom/ashgray.gba` directly and
do not modify it. (Left in /tmp, not added to tools/, to avoid colliding with other workers.)
