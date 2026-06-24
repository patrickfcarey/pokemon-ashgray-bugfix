#!/usr/bin/env python3
"""L13 finalize — the gym walkway tip (8,9) on 7.5.

Root cause (refined by A/B): the tip cell was block 0x299 (rim piece, behavior 0xF4)
at ELEVATION 1 — the water level — at the end of the elevation-4 walkway. The rim
behavior permits stepping on despite the mismatch; every exit is then vetoed by the
elevation check from a normal tile = one-way trap.

fix_l13.py already swapped the block to 0x2A4 but preserved the old elev bits, which
seals the tile (no longer a trap, but the board tip went dead). Correct restoration:
clone the FULL cell from (8,10) — block 0x2A4, col 0, elev 4 — making the tip a normal
bidirectional walkway end.
"""
import struct

ag = bytearray(open('rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

banks = pf(0x5524C)
b7 = pf(banks + 28)
h = pf(b7 + 4*5)
lay = pf(h)
W = struct.unpack('<I', ag[lay:lay+4])[0]
bd = pf(lay + 12)
tip = bd + (9*W + 8) * 2
ref = bd + (10*W + 8) * 2
old = struct.unpack('<H', ag[tip:tip+2])[0]
new = struct.unpack('<H', ag[ref:ref+2])[0]
assert old == 0x12A4, f'expected post-v1 cell 0x12A4 at (8,9), got {old:#06x}'
assert new == 0x42A4, f'expected walkway cell 0x42A4 at (8,10), got {new:#06x}'
ag[tip:tip+2] = struct.pack('<H', new)
open('rom/ashgray.gba', 'wb').write(ag)
print(f'L13 finalized: tip (8,9) cell {old:#06x} -> {new:#06x} (full clone of (8,10): elev 4, bidirectional)')
