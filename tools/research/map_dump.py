#!/usr/bin/env python3
"""Dump any map's persons + warps + dims. usage: map_dump.py bank num [leader_script_hex]"""
import struct, sys
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read(); ROM = 0x08000000; LIT = 0x5524C
def pf(o):
    v=struct.unpack('<I',ag[o:o+4])[0]
    return v-ROM if 0x08000000<=v<0x08000000+len(ag) else None
def plist(off,cap):
    r=[]
    for k in range(cap):
        p=pf(off+4*k)
        if p is None: break
        r.append(p)
    return r
def s16(o): return struct.unpack('<h',ag[o:o+2])[0]
bank,num = int(sys.argv[1]), int(sys.argv[2])
leader = int(sys.argv[3],16) if len(sys.argv)>3 else None
h = plist(plist(pf(LIT),64)[bank],150)[num]
print(f"map {bank}.{num} header @{h:#x}")
layout = pf(h+0)
if layout:
    w=struct.unpack('<I',ag[layout:layout+4])[0]; ht=struct.unpack('<I',ag[layout+4:layout+8])[0]
    print(f"  dims {w} x {ht}")
ev = pf(h+4); nP,nW = ag[ev], ag[ev+1]; pP,pW = pf(ev+4), pf(ev+8)
print(f"  {nP} persons, {nW} warps")
for i in range(nP):
    b=pP+i*24; lid=ag[b]; x=s16(b+4); y=s16(b+6); sp=pf(b+16)
    tag='  <-- LEADER' if sp==leader else ''
    sps = f"{sp:#x}" if sp else "0"
    print(f"    person{i}: id={lid} ({x},{y}) script={sps}{tag}")
for i in range(nW):
    b=pW+i*8; x=s16(b); y=s16(b+2); wid=ag[b+4]; dm=ag[b+5]; dg=ag[b+6]
    print(f"    warp{i}: ({x},{y}) -> {dg}.{dm} warp{wid}")
