#!/usr/bin/env python3
"""Build tvtest/l12c_test.gba — L12 stage-2-whiteout repro.

Like l12b (lab(4,9) + house(8,6) warp triggers -> 3.67 (15,45)) PLUS a battle trigger
ON 3.67 at (15,46), var 0x40F4==1 -> wild SPEAROW lv5 (the losable battle a real player
finds via stage-2 wilds). Plan: poke POST-WIN state (0x6079=2, 0x5010=2, flagbyte
+0x10E8=0x04 = flock visible/Spearow hidden), lose at 1 HP -> whiteout resets vars but
NOT the flags -> walk back -> flock walls the funnel at y=51."""
import struct

ag = bytearray(open('../ashgray-fork/rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

banks = pf(0x5524C)
WARP367 = bytes.fromhex('390343ff0f002d00')

# --- lab 4.3 ---
b4 = pf(banks + 16)
hdr = pf(b4 + 12)
ev = pf(hdr + 4)
no, nw, nc, nb = ag[ev], ag[ev+1], ag[ev+2], ag[ev+3]
po, pw, pc, pb = (struct.unpack('<I', ag[ev+4+4*i:ev+8+4*i])[0] for i in range(4))
scr = bytes.fromhex('16f7400200') + WARP367 + b'\x27\x02'
ag[0xC00200:0xC00200+len(scr)] = scr
old = bytes(ag[pc-ROM:pc-ROM+nc*16])
new = struct.pack('<hhBBHHH', 4, 9, 3, 0, 0x40F7, 1, 0) + struct.pack('<I', ROM+0xC00200)
ag[0xC00240:0xC00240+len(old)+16] = old + new
ag[0xC00280:0xC00280+20] = bytes([no, nw, nc+1, nb]) + struct.pack('<IIII', po, pw, ROM+0xC00240, pb)
ag[hdr+4:hdr+8] = struct.pack('<I', ROM+0xC00280)

# --- house 4.0 ---
hh = pf(b4 + 0)
hev = pf(hh + 4)
hno, hnw, hnc, hnb = ag[hev], ag[hev+1], ag[hev+2], ag[hev+3]
hpo, hpw, hpc, hpb = (struct.unpack('<I', ag[hev+4+4*i:hev+8+4*i])[0] for i in range(4))
hscr = bytes.fromhex('16f5400200') + WARP367 + b'\x27\x02'
ag[0xC00390:0xC00390+len(hscr)] = hscr
hnew = struct.pack('<hhBBHHH', 8, 6, 0, 0, 0x40F5, 1, 0) + struct.pack('<I', ROM+0xC00390)
ag[0xC00360:0xC00360+16] = hnew
ag[0xC00370:0xC00370+20] = bytes([hno, hnw, 1, hnb]) + struct.pack('<IIII', hpo, hpw, ROM+0xC00360, hpb)
ag[hh+4:hh+8] = struct.pack('<I', ROM+0xC00370)

# --- 3.67: add battle trigger at (15,46), var 0x40F4==1 ---
ch = 0x7313BC
cev = pf(ch + 4)
cno, cnw, cnc, cnb = ag[cev], ag[cev+1], ag[cev+2], ag[cev+3]
cpo, cpw, cpc, cpb = (struct.unpack('<I', ag[cev+4+4*i:cev+8+4*i])[0] for i in range(4))
assert cnc == 20, cnc
bscr = bytes.fromhex('16f4400200') + bytes.fromhex('b61500050000b7') + bytes.fromhex('16f4400300') + b'\x02'
ag[0xC003A0:0xC003A0+len(bscr)] = bscr
cold = bytes(ag[cpc-ROM:cpc-ROM+cnc*16])
cnew = struct.pack('<hhBBHHH', 15, 46, 0, 0, 0x40F4, 1, 0) + struct.pack('<I', ROM+0xC003A0)
ag[0xC003C0:0xC003C0+len(cold)+16] = cold + cnew
ag[0xC00520:0xC00520+20] = bytes([cno, cnw, cnc+1, cnb]) + struct.pack('<IIII', cpo, cpw, ROM+0xC003C0, cpb)
ag[ch+4:ch+8] = struct.pack('<I', ROM+0xC00520)

open('tvtest/l12c_test.gba', 'wb').write(ag)
print('l12c_test.gba: lab+house->3.67(15,45); 3.67(15,46) 0x40F4==1 -> wild SPEAROW')
