#!/usr/bin/env python3
"""Build tvtest/l12b_test.gba — full L12 loop: real Spearow scene on 3.67, lose,
whiteout home, warp back, re-enter the scene with post-loss state (0x5010=1).

Injections:
  lab 4.3 (4,9)   var 0x40F7==1 -> warp 3.67 @(15,45)
  house 4.0 (8,6) var 0x40F5==1 -> warp 3.67 @(15,45)   (post-respawn return ride)
Free space: lab script @0xC00200, lab coords @0xC00240, lab events @0xC00280,
            house script @0xC00390, house coords @0xC00360, house events @0xC00370."""
import struct

ag = bytearray(open('../ashgray-fork/rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

banks = pf(0x5524C)
WARP367 = bytes.fromhex('390343ff0f002d00')   # warp 3,0x43,wid FF,x=15,y=45

# --- lab 4.3 trigger -> warp ---
b4 = pf(banks + 16)
hdr = pf(b4 + 12)
ev = pf(hdr + 4)
no, nw, nc, nb = ag[ev], ag[ev+1], ag[ev+2], ag[ev+3]
po, pw, pc, pb = (struct.unpack('<I', ag[ev+4+4*i:ev+8+4*i])[0] for i in range(4))
assert (no, nw, nc, nb) == (1, 1, 2, 10)
scr = bytes.fromhex('16f7400200') + WARP367 + b'\x27\x02'
ag[0xC00200:0xC00200+len(scr)] = scr
old = bytes(ag[pc-ROM:pc-ROM+nc*16])
new = struct.pack('<hhBBHHH', 4, 9, 3, 0, 0x40F7, 1, 0) + struct.pack('<I', ROM+0xC00200)
ag[0xC00240:0xC00240+len(old)+16] = old + new
ag[0xC00280:0xC00280+20] = bytes([no, nw, nc+1, nb]) + struct.pack('<IIII', po, pw, ROM+0xC00240, pb)
ag[hdr+4:hdr+8] = struct.pack('<I', ROM+0xC00280)

# --- house 4.0 trigger -> warp back ---
hh = pf(b4 + 0)
hev = pf(hh + 4)
hno, hnw, hnc, hnb = ag[hev], ag[hev+1], ag[hev+2], ag[hev+3]
hpo, hpw, hpc, hpb = (struct.unpack('<I', ag[hev+4+4*i:hev+8+4*i])[0] for i in range(4))
assert (hnc, hnb) == (0, 0), (hno, hnw, hnc, hnb)
hscr = bytes.fromhex('16f5400200') + WARP367 + b'\x27\x02'
ag[0xC00390:0xC00390+len(hscr)] = hscr
hnew = struct.pack('<hhBBHHH', 8, 6, 0, 0, 0x40F5, 1, 0) + struct.pack('<I', ROM+0xC00390)
ag[0xC00360:0xC00360+16] = hnew
ag[0xC00370:0xC00370+20] = bytes([hno, hnw, 1, hnb]) + struct.pack('<IIII', hpo, hpw, ROM+0xC00360, hpb)
ag[hh+4:hh+8] = struct.pack('<I', ROM+0xC00370)

open('tvtest/l12b_test.gba', 'wb').write(ag)
print('l12b_test.gba: lab(4,9)+house(8,6) -> warp 3.67 (15,45)')
