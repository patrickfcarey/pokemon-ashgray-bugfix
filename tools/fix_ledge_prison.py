#!/usr/bin/env python3
"""M1 — Pallet (3.66) ledge prison.

The lab's south door tile (24,15) carries an east-jump ledge behavior: pressing UP from
(24,16) bounces the player east into (25,16), a 1-tile pocket with no exit in any
direction (verified by live probing) — a permanent softlock two screens from the start
of the game. The door warp on that tile is also unreachable (dead).

Fix: replace the (24,15) block with the neighboring solid wall block (23,15) — the
UP-press now just bumps, the trap is unreachable, no new routes are created. One u16.
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = ag[o] | ag[o+1] << 8 | ag[o+2] << 16 | ag[o+3] << 24
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

h = 0x7306FC                      # map 3.66 header
lay = pf(h)
W = int.from_bytes(ag[lay:lay+4], 'little')
bd = pf(lay+12)
src = bd + (16*W + 26) * 2        # solid block at (26,16)
dst = bd + (16*W + 25) * 2        # the 1-tile prison pocket (25,16)
old = ag[dst] | ag[dst+1] << 8
new = ag[src] | ag[src+1] << 8
assert ((old >> 10) & 3) == 0, f'expected walkable pocket at (25,16), got col={(old>>10)&3}'
assert ((new >> 10) & 3) != 0, f'expected solid block at (26,16)'
ag[dst] = ag[src]; ag[dst+1] = ag[src+1]
open('rom/ashgray.gba', 'wb').write(ag)
print(f'M1 fixed: prison tile (25,16) block 0x{old:04X} -> 0x{new:04X} (solid); jump landing blocked')
