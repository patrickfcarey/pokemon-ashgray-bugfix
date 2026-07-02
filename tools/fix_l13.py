#!/usr/bin/env python3
"""L13 — "Stuck on Cerulean city gym pool" (French patcher's list). REPRODUCED live.

The gym hall (map 7.5) has a center walkway / diving board over the pool (blocks with
behavior 0x70, bidirectional). Its tip at (8,9) is stamped with block 0x299 — a SOUTH-RIM
edge piece whose behavior (0xF4, directional) lets you step ON from the walkway but
refuses every exit, including the way back. One step onto the board tip = permanent
softlock (one-room interior, nothing to interact with).

The rim ring elsewhere is safe (deck-side entry is rejected — verified by live probes),
and the only other map sharing this tileset (3.89) has no walkway adjacency. So the fix
is one cell: re-stamp (8,9) from 0x299 to 0x2A4 — the walkway block used at (8,10),
proven bidirectional in-engine. Cosmetic-only change to the board tip; no new routes
(above it is plain 0x15 water, which blocks on its own).
"""
import struct

ag = bytearray(open('rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

banks = pf(0x5524C)
b7 = pf(banks + 28)
h = pf(b7 + 4*5)                    # map 7.5
lay = pf(h)
W = struct.unpack('<I', ag[lay:lay+4])[0]
bd = pf(lay + 12)
cell = bd + (9*W + 8) * 2           # (8,9)
old = struct.unpack('<H', ag[cell:cell+2])[0]
ref  = struct.unpack('<H', ag[bd + (10*W + 8)*2 : bd + (10*W + 8)*2 + 2])[0]
if old & 0x3FF == 0x2A4:
    print('L13 already applied (tip block already 0x2A4) — no change')
    raise SystemExit(0)
assert old & 0x3FF == 0x299, f'expected block 0x299 at (8,9), got {old & 0x3FF:#x}'
assert (old >> 10) & 3 == 0, 'expected col=0 at (8,9)'
assert ref & 0x3FF == 0x2A4, f'expected walkway block 0x2A4 at (8,10), got {ref & 0x3FF:#x}'
new = (old & 0xFC00) | 0x2A4
ag[cell:cell+2] = struct.pack('<H', new)
open('rom/ashgray.gba', 'wb').write(ag)
print(f'L13 fixed: gym walkway tip (8,9) block 0x{old & 0x3FF:03X} -> 0x2A4 (bidirectional); pool no longer traps')
