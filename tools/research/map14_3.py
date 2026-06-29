#!/usr/bin/env python3
"""Dump Saffron Gym (map 14.3) layout: person positions (find Sabrina person5), warps (entry),
and map dimensions — to plan the live repro navigation."""
import struct
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
h = plist(plist(pf(LIT),64)[14],150)[3]
print(f"map 14.3 header @{h:#x}")
layout = pf(h+0)
if layout:
    w=struct.unpack('<I',ag[layout:layout+4])[0]; ht=struct.unpack('<I',ag[layout+4:layout+8])[0]
    print(f"  dimensions: {w} x {ht}")
ev = pf(h+4)
nP,nW = ag[ev], ag[ev+1]
pP,pW = pf(ev+4), pf(ev+8)
print(f"  {nP} persons, {nW} warps")
print("  PERSONS (id, x, y, script):")
for i in range(nP):
    b=pP+i*24
    lid=ag[b]; x=s16(b+4); y=s16(b+6); sp=pf(b+16)
    tag='  <-- SABRINA (gates Marsh)' if sp==0x806505 else ''
    print(f"    person{i}: id={lid} ({x},{y}) script={sp:#x}{tag}")
print("  WARPS (x, y -> dest):")
for i in range(nW):
    b=pW+i*8
    x=s16(b); y=s16(b+2); wid=ag[b+4]; dm=ag[b+5]; dg=ag[b+6]
    print(f"    warp{i}: ({x},{y}) -> bank {dg}.{dm} warp{wid}")
