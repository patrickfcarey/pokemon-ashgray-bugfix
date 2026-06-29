#!/usr/bin/env python3
"""Build tvtest/l12_test.gba — L12 Spearow-loss whiteout repro.

Two injections:
  lab 4.3 (4,9)  var 0x40F7==1 -> setvar 0x40F7,2; warp 3.19 (Route 1) @(8,20); waitstate; end
  route1 3.19 (8,21) var 0x40F6==1 -> setvar 0x40F6,2; setwildbattle SPEAROW lv5;
                                      dowildbattle; setvar 0x40F6,3; end
Lose the wild battle (1-HP Pikachu, Growl) -> REAL whiteout -> observe the respawn
placement (the intro's setrespawn 1 / 0x405A=4 state is live, as for a real player).
Free space: lab script @0xC00200, lab coords @0xC00240, lab events @0xC00280,
            r1 script @0xC00300, r1 coords @0xC00320, r1 events @0xC00340."""
import struct

ag = bytearray(open('../ashgray-fork/rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

banks = pf(0x5524C)

# --- lab 4.3 ---
b4 = pf(banks + 16)
hdr = pf(b4 + 12)
ev = pf(hdr + 4)
no, nw, nc, nb = ag[ev], ag[ev+1], ag[ev+2], ag[ev+3]
po, pw, pc, pb = (struct.unpack('<I', ag[ev+4+4*i:ev+8+4*i])[0] for i in range(4))
assert (no, nw, nc, nb) == (1, 1, 2, 10)
scr = bytes.fromhex('16f7400200') + bytes.fromhex('390313ff08001400') + b'\x27\x02'
ag[0xC00200:0xC00200+len(scr)] = scr
old = bytes(ag[pc-ROM:pc-ROM+nc*16])
new = struct.pack('<hhBBHHH', 4, 9, 3, 0, 0x40F7, 1, 0) + struct.pack('<I', ROM+0xC00200)
ag[0xC00240:0xC00240+len(old)+16] = old + new
ag[0xC00280:0xC00280+20] = bytes([no, nw, nc+1, nb]) + struct.pack('<IIII', po, pw, ROM+0xC00240, pb)
ag[hdr+4:hdr+8] = struct.pack('<I', ROM+0xC00280)

# --- route 1 (3.19) ---
b3 = pf(banks + 12)
rh = pf(b3 + 4*19)
rev = pf(rh + 4)
rno, rnw, rnc, rnb = ag[rev], ag[rev+1], ag[rev+2], ag[rev+3]
rpo, rpw, rpc, rpb = (struct.unpack('<I', ag[rev+4+4*i:rev+8+4*i])[0] for i in range(4))
assert (rnc, rnb) == (0, 0), (rno, rnw, rnc, rnb)
rscr = bytes.fromhex('16f6400200') + bytes.fromhex('b61500050000b7') + bytes.fromhex('16f6400300') + b'\x02'
ag[0xC00300:0xC00300+len(rscr)] = rscr
rnew = struct.pack('<hhBBHHH', 8, 21, 0, 0, 0x40F6, 1, 0) + struct.pack('<I', ROM+0xC00300)
ag[0xC00320:0xC00320+16] = rnew
ag[0xC00340:0xC00340+20] = bytes([rno, rnw, 1, rnb]) + struct.pack('<IIII', rpo, rpw, ROM+0xC00320, rpb)
ag[rh+4:rh+8] = struct.pack('<I', ROM+0xC00340)

open('tvtest/l12_test.gba', 'wb').write(ag)
print('l12_test.gba: lab(4,9)->warp Route1(8,20); Route1(8,21)->wild SPEAROW lv5')
