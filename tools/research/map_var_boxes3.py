#!/usr/bin/env python3
"""Rigorous: count setvar(0x16)/compare(0x21) ONLY where the opcode sits in Ash Gray's
script code bank (0x800000-0x8D0000) — where every decompile-confirmed story var lives.
Data/graphics noise (0x1cxxxx/0x1fxxxx/0x23xxxx) is excluded. Map the real storage-
overlapping vars to PC boxes."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
LO, HI = 0x800000, 0x8D0000          # script code bank
SB1_TO_STORAGE, STORAGE_SIZE = 0x3DE8, 0x83D0
BOXES_OFF, MON, BOXNAMES_OFF = 4, 80, 0x8344

def storage_off(vid):
    o = (0x1000 + 2*(vid-0x4000)) - SB1_TO_STORAGE
    return o if 0 <= o < STORAGE_SIZE else None

def box_of(vid):
    o = storage_off(vid)
    if o is None or o < BOXES_OFF or o >= BOXNAMES_OFF:
        return None
    slot = (o - BOXES_OFF)//MON
    return slot//30, slot%30

def collect(op):
    s = {}
    i = LO
    while i < HI - 3:
        if ag[i] == op:
            vid = struct.unpack('<H', ag[i+1:i+3])[0]
            if 0x4100 <= vid <= 0x7000:
                s[vid] = s.get(vid, 0)+1
        i += 1
    return s

setv = collect(0x16)
comp = collect(0x21)
real = sorted(v for v in setv if v in comp)
ov = [v for v in real if storage_off(v) is not None]
sb = [v for v in real if storage_off(v) is None]
print(f'real script-bank vars (set AND compared): {len(real)}, max 0x{max(real):04X}')
print(f'  SaveBlock1 band (id<0x56F4, F2/F6 class, not boxes): {len(sb)} '
      f'[{", ".join(f"0x{v:04X}" for v in sb)}]')
print(f'  storage-overlapping (boxes): {len(ov)}')
boxes = {}
for v in ov:
    b = box_of(v)
    if b:
        boxes.setdefault(b[0], []).append(v)
for v in ov:
    b = box_of(v)
    where = f'Box {b[0]+1} slot {b[1]}' if b else 'box-name/header'
    print(f'   0x{v:04X} -> {where:18s} [set x{setv[v]}, cmp x{comp[v]}]')
print()
touched = sorted(boxes)
print(f'BOXES touched (1-indexed): {[b+1 for b in touched]}')
print(f'BOXES clean (1-indexed): {[b+1 for b in range(14) if b not in boxes]}')
if real:
    mx = max(real)
    print(f'highest real var 0x{mx:04X} -> storage offset 0x{(0x1000+2*(mx-0x4000))-SB1_TO_STORAGE:04X} '
          f'(Box {box_of(mx)[0]+1 if box_of(mx) else "?"})')
