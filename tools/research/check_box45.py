#!/usr/bin/env python3
"""Is the Box 3 -> Box 6 jump real, or did the detector miss vars in Box 4/5?
Box ranges (var id): Box4 ~0x6506-0x69B6, Box5 ~0x69B6-0x6E66 (storage offset math below).
Check THREE sources: (1) map coord-event trigger tables (raw structs, missed by opcode scans),
(2) all var-touching opcodes (setvar/addvar/subvar/copyvar/setorcopyvar/compare/comparevv/specialvar),
(3) the gap var-id range directly."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read(); ROM=0x08000000; LIT=0x5524C
def u16(o): return ag[o]|ag[o+1]<<8
def pf(o):
    v=struct.unpack('<I',ag[o:o+4])[0]; return v-ROM if 0x08000000<=v<0x08000000+len(ag) else None
def plist(off,cap):
    r=[]
    for k in range(cap):
        p=pf(off+4*k)
        if p is None: break
        r.append(p)
    return r
def box_slot(v):
    o=(0x1000+2*(v-0x4000))-0x3DE8
    if o<4 or o>=0x8344: return None
    s=(o-4)//80; return s//30+1, s%30
# (1) coord-event trigger vars across all maps
print("=== (1) map coord-event trigger vars (the opcode-scan blind spot) ===")
banks=plist(pf(LIT),64); coordvars={}
for b,bt in enumerate(banks):
    for m,h in enumerate(plist(bt,150)):
        ev=pf(h+4)
        if ev is None or ev+20>len(ag): continue
        nC=ag[ev+2]; pC=pf(ev+12)
        if not pC or nC>40: continue
        for i in range(nC):
            base=pC+i*16
            if base+16>len(ag): continue
            var=u16(base+6); val=u16(base+8)
            if 0x4100<=var<0x8000:
                coordvars.setdefault(var,[]).append((b,m,val))
from collections import Counter
cbox=Counter()
for v in coordvars:
    bs=box_slot(v); cbox[bs[0] if bs else 'sb1-interior']+=1
print(f"  {len(coordvars)} distinct trigger vars; by box: {dict(sorted(cbox.items(),key=lambda x:str(x[0])))}")
b45=[v for v in coordvars if box_slot(v) and box_slot(v)[0] in (4,5)]
print(f"  trigger vars in Box 4/5: {[hex(v) for v in sorted(b45)]}")

# (2) ALL var-touching opcodes, bucket by box
print("\n=== (2) all var-touching opcodes, by box ===")
OPVAR={0x16:('setvar',1),0x17:('addvar',1),0x18:('subvar',1),0x19:('copyvar',2),0x1A:('setorcopyvar',2),
       0x21:('compare',1),0x22:('comparevv',2),0x26:('specialvar',1)}
touched=set(); i=0x7F0000
while i<0x8D0000-6:
    op=ag[i]
    if op in OPVAR:
        v=u16(i+1)
        if 0x4100<=v<0x8000: touched.add(v)
        if OPVAR[op][1]==2:
            v2=u16(i+3)
            if 0x4100<=v2<0x8000: touched.add(v2)
    i+=1
tbox=Counter()
for v in touched:
    bs=box_slot(v); tbox[bs[0] if bs else 'sb1-interior']+=1
print(f"  {len(touched)} distinct vars (noisy); by box: {dict(sorted(tbox.items(),key=lambda x:str(x[0])))}")

# (3) the gap range directly: any var 0x6500-0x6E66 referenced at all?
print("\n=== (3) Box 4/5 var-id range 0x6500-0x6E66 — any references? ===")
gap=sorted(v for v in (touched|set(coordvars)) if 0x6500<=v<0x6E66)
print(f"  vars in range referenced: {len(gap)} -> {[hex(v) for v in gap]}")
