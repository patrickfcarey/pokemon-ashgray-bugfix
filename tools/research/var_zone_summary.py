#!/usr/bin/env python3
"""Quantify how much of the hack's story-variable system overlaps PC storage.
Real story vars = those that appear as BOTH setvar(0x16) and compare(0x21) in the
script code bank (0x800000-0x8D0000), noise-filtered. Bucket each by where its
deep-alias address lands."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
LO, HI = 0x800000, 0x8D0000
SB1_SIZE = 0x3D88           # vanilla SaveBlock1 size
SB1_TO_STORAGE = 0x3DE8     # storage starts here (rel. to sb1)
STORAGE_SIZE = 0x83D0

def alias_off(vid):
    return 0x1000 + 2 * (vid - 0x4000)

def zone(vid):
    o = alias_off(vid)
    if vid < 0x4100:
        return 'vanilla temp/array (safe)'
    if o < SB1_SIZE:
        return 'SaveBlock1 interior (UNEXAMINED overflow zone; NOT the F2/F6 cause)'
    so = o - SB1_TO_STORAGE
    if so < 0:
        return 'gap (sb1 tail)'
    if so >= STORAGE_SIZE:
        return 'beyond storage'
    box = (so - 4) // 80 // 30 if so >= 4 else -1
    return f'PC STORAGE / Box {box+1}'

def collect(op):
    s = set()
    for i in range(LO, HI - 3):
        if ag[i] == op:
            vid = struct.unpack('<H', ag[i+1:i+3])[0]
            # 0x4100..0x7FFF = the hack's custom persistent story vars.
            # EXCLUDE 0x8000+ : those are FireRed's special/temp scratch vars (not stored
            # in the save-block array, engine-special-cased) + pointer-byte noise.
            if 0x4100 <= vid < 0x8000:
                s.add(vid)
    return s

real = sorted(collect(0x16) & collect(0x21))
from collections import Counter
buckets = Counter(zone(v) for v in real)
total = len(real)
storage = sum(n for z, n in buckets.items() if z.startswith('PC STORAGE'))
print(f'real custom story vars (set AND compared in script bank): {total}')
print(f'min id 0x{min(real):04X}  max id 0x{max(real):04X}')
print()
for z, n in sorted(buckets.items(), key=lambda kv: -kv[1]):
    print(f'  {n:4d}  ({100*n/total:4.1f}%)  {z}')
print()
print(f'PC-storage-overlapping total: {storage}/{total} = {100*storage/total:.1f}%')
