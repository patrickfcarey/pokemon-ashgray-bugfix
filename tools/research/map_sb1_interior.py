#!/usr/bin/env python3
"""Map EVERY hack var that writes into the SaveBlock1 interior (ids 0x4100-0x56F3) to its
sb1 offset and the nearest known field. Flag any that hit live/dangerous fields.
Landmarks (from the live dump, sb1 base):
  ~0x2E00-0x2F16  mailbox (0x24-byte MailStruct entries)   -> vars ~0x4F00-0x4F8B
  ~0x30EC-0x3140  ENIGMA BERRY (name + 2 ROM func pointers) -> vars ~0x5076-0x50A0  *** danger
  elsewhere       zero/unused tail
"""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
LO, HI = 0x800000, 0x8D0000

def off(vid):
    return 0x1000 + 2 * (vid - 0x4000)

def landmark(vid):
    o = off(vid)
    if 0x2E00 <= o < 0x2F16:
        return 'MAILBOX'
    if 0x30EC <= o < 0x3140:
        return '*** ENIGMA BERRY (func ptrs ~0x30F8) ***'
    return 'zero/unused tail'

# write opcodes (dest var = first u16) + compare
WRITE = {0x16: 'setvar', 0x17: 'addvar', 0x18: 'subvar', 0x19: 'copyvar', 0x1A: 'setorcopyvar'}
writes = {}   # vid -> count of plausible write sites
comps = set()
i = LO
while i < HI - 4:
    op = ag[i]
    vid = struct.unpack('<H', ag[i+1:i+3])[0]
    if 0x4100 <= vid <= 0x56F3:
        if op in WRITE:
            # plausibility: for setvar/addvar/subvar the value (bytes+3,+4) should be small
            if op in (0x16, 0x17, 0x18):
                val = struct.unpack('<H', ag[i+3:i+5])[0]
                if val <= 0x100:
                    writes[vid] = writes.get(vid, 0) + 1
            else:  # copyvar/setorcopyvar: dest is a var, src follows
                writes[vid] = writes.get(vid, 0) + 1
        elif op == 0x21:
            comps.add(vid)
    i += 1

print('Vars written into the SaveBlock1 interior (write-count, also-compared, offset, field):')
for vid in sorted(writes):
    o = off(vid)
    c = 'cmp' if vid in comps else '   '
    print(f'  0x{vid:04X}  x{writes[vid]:<2} {c}  sb1+0x{o:04X}  {landmark(vid)}')
hits_mail = [v for v in writes if landmark(v) == 'MAILBOX']
hits_berry = [v for v in writes if 'ENIGMA' in landmark(v)]
print(f'\nMAILBOX hits: {[hex(v) for v in hits_mail]}')
print(f'ENIGMA BERRY hits: {[hex(v) for v in hits_berry]}')
