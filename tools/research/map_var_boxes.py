#!/usr/bin/env python3
"""Find which PC boxes the hack's overflowing story-vars actually land in.

Scan the ROM for every var-WRITE opcode (setvar/addvar/subvar/copyvar/setorcopyvar),
collect distinct destination var IDs, keep the ones that overflow into PC storage, and
map each to (box, slot, byte) so we can say which boxes are touched vs clean.

Confirmed live addresses (FireRed fixed layout, stable):
  gSaveBlock1Ptr   = 0x02025534
  gPokemonStorage  = 0x0202931C   (= sb1 + 0x3DE8)
  var id -> alias  = sb1 + 0x1000 + 2*(id-0x4000)
  storage offset   = alias - 0x3DE8
PokemonStorage layout: currentBox @0; boxes[14][30] @4 (80 bytes each, =0x50);
  boxNames @0x8344; boxWallpapers @0x83C2; total 0x83D0.
"""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()

SB1_TO_STORAGE = 0x3DE8          # storage starts here, relative to sb1
STORAGE_SIZE   = 0x83D0
BOXES_OFF      = 4               # boxes[] start
MON            = 80              # sizeof(BoxPokemon)
BOXNAMES_OFF   = 0x8344

def alias_off(vid):              # offset from sb1
    return 0x1000 + 2 * (vid - 0x4000)

def storage_off(vid):            # offset into PokemonStorage, or None if not in it
    o = alias_off(vid) - SB1_TO_STORAGE
    return o if 0 <= o < STORAGE_SIZE else None

def classify(vid):
    o = storage_off(vid)
    if o is None:
        return None
    if o < BOXES_OFF:
        return ('currentBox', None, None, o)
    if o >= BOXNAMES_OFF:
        return ('boxName/wallpaper(cosmetic)', None, None, o)
    slot = (o - BOXES_OFF) // MON
    box = slot // 30
    sib = slot % 30
    byte = (o - BOXES_OFF) % MON
    return ('box', box, sib, byte)

# opcodes that WRITE a var as their first u16 operand
WRITE_OPS = {0x16: 'setvar', 0x17: 'addvar', 0x18: 'subvar',
             0x19: 'copyvar', 0x1A: 'setorcopyvar'}

found = {}   # vid -> set of opcodes
for i in range(len(ag) - 5):
    op = ag[i]
    if op in WRITE_OPS:
        vid = struct.unpack('<H', ag[i+1:i+3])[0]
        # keep only plausible hack var IDs in the storage-overflow band
        if 0x56F4 <= vid <= 0x9000:
            found.setdefault(vid, set()).add(WRITE_OPS[op])

print(f'distinct storage-overlapping var IDs written: {len(found)}')
boxes_touched = set()
rows = []
for vid in sorted(found):
    c = classify(vid)
    if c is None:
        continue
    kind, box, sib, byte = c
    if kind == 'box':
        boxes_touched.add(box)
        rows.append((vid, f'Box {box+1} (0idx {box}) slot {sib} byte +0x{byte:02X}', ','.join(sorted(found[vid]))))
    else:
        rows.append((vid, kind, ','.join(sorted(found[vid]))))
for vid, where, ops in rows:
    print(f'  var 0x{vid:04X} -> {where:38s} [{ops}]')

print()
if boxes_touched:
    lo, hi = min(boxes_touched), max(boxes_touched)
    print(f'BOXES TOUCHED (1-indexed): {sorted(b+1 for b in boxes_touched)}')
    all_boxes = set(range(14))
    clean = sorted(b+1 for b in (all_boxes - boxes_touched))
    print(f'BOXES NOT TOUCHED by any var-write (1-indexed): {clean}')
