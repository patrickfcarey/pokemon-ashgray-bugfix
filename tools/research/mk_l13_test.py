#!/usr/bin/env python3
"""Build tvtest/l13_test.gba — same lab coord-trigger injection as d7_test.gba at (4,9)
(var 0x40F7==1), but the script WARPS to the Cerulean gym pool hall 7.5 instead of running
a bare trainerbattle. The whole D7 scene then runs stock on its real map:
    setvar 0x40F7, 2
    warp 7.5 (8,16)
    waitstate
    end
Free space (test ROM only): script @0xC00200, coords @0xC00240, events @0xC00280."""
import struct

ag = bytearray(open('../ashgray-fork/rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

banks = pf(0x5524C)
bank4 = pf(banks + 16)
hdr = pf(bank4 + 12)
ev = pf(hdr + 4)
no, nw, nc, nb = ag[ev], ag[ev+1], ag[ev+2], ag[ev+3]
po, pw, pc, pb = (struct.unpack('<I', ag[ev+4+4*i:ev+8+4*i])[0] for i in range(4))
assert (no, nw, nc, nb) == (1, 1, 2, 10), (no, nw, nc, nb)

SCRIPT, COORDS, EVENTS = 0xC00200, 0xC00240, 0xC00280
scr = bytes.fromhex('16f7400200') + bytes.fromhex('390705ff08001000') + b'\x27\x02'
ag[SCRIPT:SCRIPT+len(scr)] = scr

old = bytes(ag[pc-ROM:pc-ROM+nc*16])
new = struct.pack('<hhBBHHH', 4, 9, 3, 0, 0x40F7, 1, 0) + struct.pack('<I', ROM+SCRIPT)
ag[COORDS:COORDS+len(old)+16] = old + new

ag[EVENTS:EVENTS+20] = bytes([no, nw, nc+1, nb]) + struct.pack('<IIII', po, pw, ROM+COORDS, pb)
ag[hdr+4:hdr+8] = struct.pack('<I', ROM+EVENTS)

open('tvtest/l13_test.gba', 'wb').write(ag)
print('l13_test.gba: lab trigger (4,9) var 0x40F7==1 -> warp 5.4')
