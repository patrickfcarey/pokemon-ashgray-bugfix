#!/usr/bin/env python3
"""Lower-noise: a var is 'real' only if it appears as BOTH a setvar-destination (0x16)
AND a compare-operand (0x21) somewhere in the ROM. Random data almost never produces
the same high ID in both roles. Report the real storage-overlapping vars + box span."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()

SB1_TO_STORAGE = 0x3DE8
STORAGE_SIZE   = 0x83D0
BOXES_OFF      = 4
MON            = 80
BOXNAMES_OFF   = 0x8344

def storage_off(vid):
    o = (0x1000 + 2 * (vid - 0x4000)) - SB1_TO_STORAGE
    return o if 0 <= o < STORAGE_SIZE else None

def classify(vid):
    o = storage_off(vid)
    if o is None:
        return None
    if o < BOXES_OFF:
        return ('currentBox-header', None, None)
    if o >= BOXNAMES_OFF:
        return ('boxName/wallpaper', None, None)
    slot = (o - BOXES_OFF) // MON
    return ('box', slot // 30, slot % 30)

def collect(op):
    s = {}
    i = 0
    while i < len(ag) - 5:
        j = ag.find(bytes([op]), i)
        if j < 0:
            break
        vid = struct.unpack('<H', ag[j+1:j+3])[0]
        if 0x4000 <= vid <= 0x9000:
            s[vid] = s.get(vid, 0) + 1
        i = j + 1
    return s

setvars = collect(0x16)     # setvar dest
compares = collect(0x21)    # compare operand
real = {v for v in setvars if v in compares}              # appears as both
real_hi = {v for v in real if v >= 0x4100}                # exclude vanilla temp band
overlap = sorted(v for v in real_hi if storage_off(v) is not None)
sb1band = sorted(v for v in real_hi if storage_off(v) is None and v >= 0x4100)

print(f'real vars (set AND compared): {len(real_hi)} ; max id = 0x{max(real_hi):04X}')
print(f'  -> in SaveBlock1 band (id<0x56F4, NOT storage): {len(sb1band)} '
      f'[{", ".join(f"0x{v:04X}" for v in sb1band[:12])}{" ..." if len(sb1band)>12 else ""}]')
print(f'  -> storage-overlapping (id>=0x56F4): {len(overlap)}')
boxes = set()
for v in overlap:
    k = classify(v)
    if k[0] == 'box':
        boxes.add(k[1])
        print(f'   var 0x{v:04X} -> Box {k[1]+1} (0idx {k[1]}) slot {k[2]}  '
              f'[set x{setvars[v]}, compared x{compares[v]}]')
    else:
        print(f'   var 0x{v:04X} -> {k[0]}')
print()
if boxes:
    print(f'BOXES physically touched by real overflow vars (1-indexed): {sorted(b+1 for b in boxes)}')
    print(f'Highest real var id 0x{max(real_hi):04X} maps to storage offset '
          f'0x{(0x1000+2*(max(real_hi)-0x4000))-SB1_TO_STORAGE:04X}')
    print(f'Boxes NOT in reach of any real var-write (1-indexed): '
          f'{sorted(b+1 for b in (set(range(14))-boxes))}')
else:
    print('No real storage-overlapping vars found.')
