#!/usr/bin/env python3
"""Build tvtest/d4_test.gba — lab (4,9) trigger: additem TEACHY_TV(0x16E); end.
Then the rig menu-drives BAG -> KEY ITEMS -> USE to capture what happens (A/B)."""
import struct

ag = bytearray(open('../ashgray-fork/rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

banks = pf(0x5524C)
b4 = pf(banks + 16)
hdr = pf(b4 + 12)
ev = pf(hdr + 4)
no, nw, nc, nb = ag[ev], ag[ev+1], ag[ev+2], ag[ev+3]
po, pw, pc, pb = (struct.unpack('<I', ag[ev+4+4*i:ev+8+4*i])[0] for i in range(4))
scr = bytes.fromhex('16f7400200') + bytes.fromhex('446e0101 00'.replace(' ','')) + b'\x02'
ag[0xC00200:0xC00200+len(scr)] = scr
old = bytes(ag[pc-ROM:pc-ROM+nc*16])
new = struct.pack('<hhBBHHH', 4, 9, 3, 0, 0x40F7, 1, 0) + struct.pack('<I', ROM+0xC00200)
ag[0xC00240:0xC00240+len(old)+16] = old + new
ag[0xC00280:0xC00280+20] = bytes([no, nw, nc+1, nb]) + struct.pack('<IIII', po, pw, ROM+0xC00240, pb)
ag[hdr+4:hdr+8] = struct.pack('<I', ROM+0xC00280)
open('tvtest/d4_test.gba', 'wb').write(ag)
print('d4_test.gba: lab(4,9) -> additem TEACHY TV')
