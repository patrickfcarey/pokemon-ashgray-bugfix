#!/usr/bin/env python3
"""#6a deeper: can a gym SKIP its epilogue (and thus the badge setflag)?
(1) audit leader-beaten flags 0x4B0-0x4B7 — any setter OUTSIDE the epilogue = a skip vector.
(2) find the trainerbattle for each gym (win-pointer landing near each epilogue).
(3) find every pointer that ENTERS each epilogue region (who can jump in / skip in)."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
def u32(o): return struct.unpack('<I', ag[o:o+4])[0]

# epilogue entries we decompiled (block start = the 'special 0x173' / nop just before)
EPI = {'Boulder':0x824234,'Cascade':0x828ADF,'Thunder':0x831771,
       'Rainbow':0x806B24,'Soul':0x83FE0A,'Marsh':0x83527C,
       'Volcano':0x8569D3,'Earth':0x85B0BB}
LEADER = {0x4B0:'Boulder',0x4B1:'Cascade',0x4B2:'Thunder',0x4B3:'?3',
          0x4B4:'Soul',0x4B5:'Rainbow/Marsh',0x4B6:'?6',0x4B7:'?7'}

print("===== (1) leader-beaten flags 0x4B0-0x4B7 set/clear/check =====")
for op, opn in ((0x29,'setflag'),(0x2A,'clearflag'),(0x2B,'checkflag')):
    for fid, nm in LEADER.items():
        pat = bytes([op, fid & 0xFF, (fid>>8)&0xFF])
        sites=[]; i=-1
        while True:
            i = ag.find(pat, i+1)
            if i<0: break
            if 0x7F0000<=i<0x8D0000: sites.append(i)
        if sites:
            print(f"  {opn:9s} 0x{fid:03x} {nm:14s}: {[hex(s) for s in sites]}")

print("\n===== (2) trainerbattles whose win-script points into an epilogue region =====")
# scan all trainerbattle (5C) opcodes; type at +1, win-ptr commonly at +6 (type 0/1) or +10
i=-1
while True:
    i = ag.find(b'\x5c', i+1)
    if i<0 or i>=0x8D0000: break
    if i < 0x7F0000: continue
    typ = ag[i+1]
    if typ>9: continue
    for poff in (6,10,14):
        if i+poff+4>len(ag): continue
        p = u32(i+poff)
        if not (0x08000000<=p<0x09000000): continue
        t = p-ROM
        for nm,e in EPI.items():
            if e-0x60 <= t <= e+0x10:
                print(f"  tb @{i:#x} type={typ} win-ptr(+{poff})={t:#x} -> near {nm} epilogue {e:#x}")

print("\n===== (3) pointers that land in each epilogue region (entry/skip points) =====")
for nm,e in EPI.items():
    refs=[]
    for t in range(e-0x80, e+0x4):
        ptr = struct.pack('<I', t+ROM)
        j=-1
        while True:
            j = ag.find(ptr, j+1)
            if j<0: break
            if 0x7F0000<=j<0x8D0000: refs.append((j,t))
    # show distinct targets referenced
    tgts = sorted(set(t for _,t in refs))
    print(f"  {nm:8s} epilogue {e:#x}: {len(refs)} ptr(s) into region, targets={[hex(t) for t in tgts]}")
