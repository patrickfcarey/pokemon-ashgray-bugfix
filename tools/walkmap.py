#!/usr/bin/env python3
"""Render a map's collision grid (ASCII) from its layout blockdata.
usage: walkmap.py <bank> <map> [x0 y0 x1 y1]   (. = walkable, # = blocked, W = warp)"""
import sys
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000

def pf(o):
    v = ag[o] | ag[o+1] << 8 | ag[o+2] << 16 | ag[o+3] << 24
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

def u16(o): return ag[o] | ag[o+1] << 8
def s16(o):
    v = u16(o); return v - 0x10000 if v & 0x8000 else v

def plist(off, cap):
    r = []
    for i in range(cap):
        p = pf(off + 4*i)
        if p is None: break
        r.append(p)
    return r

b, m = int(sys.argv[1]), int(sys.argv[2])
banks = plist(pf(0x5524C), 64)
h = plist(banks[b], 200)[m]
lay = pf(h)
W = int.from_bytes(ag[lay:lay+4], 'little'); H = int.from_bytes(ag[lay+4:lay+8], 'little')
bd = pf(lay+12)
ev = pf(h+4); nW = ag[ev+1]; pW = pf(ev+8)
warps = {}
for w in range(nW):
    o = pW + w*8
    warps[(s16(o), s16(o+2))] = w
x0, y0, x1, y1 = 0, 0, W-1, H-1
if len(sys.argv) > 6:
    x0, y0, x1, y1 = map(int, sys.argv[3:7])
print(f'map {b}.{m}: {W}x{H}  (window {x0},{y0})-({x1},{y1})')
hdr = '    ' + ''.join(str(x % 10) for x in range(x0, x1+1))
print(hdr)
for y in range(y0, min(y1+1, H)):
    row = []
    for x in range(x0, min(x1+1, W)):
        blk = u16(bd + (y*W + x)*2)
        col = (blk >> 10) & 3
        ch = '.' if col == 0 else '#'
        if (x, y) in warps: ch = 'W'
        row.append(ch)
    print(f'{y:3} ' + ''.join(row))
