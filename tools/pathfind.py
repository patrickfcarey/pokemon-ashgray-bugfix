#!/usr/bin/env python3
"""BFS a walkable route on a map's collision grid.
usage: pathfind.py <bank> <map> <sx> <sy> <tx> <ty>  -> prints hold-style move legs"""
import sys
from collections import deque
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000

def pf(o):
    v = ag[o] | ag[o+1] << 8 | ag[o+2] << 16 | ag[o+3] << 24
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

def u16(o): return ag[o] | ag[o+1] << 8

def plist(off, cap):
    r = []
    for i in range(cap):
        p = pf(off + 4*i)
        if p is None: break
        r.append(p)
    return r

b, m, sx, sy, tx, ty = map(int, sys.argv[1:7])
banks = plist(pf(0x5524C), 64)
h = plist(banks[b], 200)[m]
lay = pf(h)
W = int.from_bytes(ag[lay:lay+4], 'little'); H = int.from_bytes(ag[lay+4:lay+8], 'little')
bd = pf(lay+12)

def walk(x, y):
    if not (0 <= x < W and 0 <= y < H): return False
    return ((u16(bd + (y*W+x)*2) >> 10) & 3) == 0

prev = {(sx, sy): None}
q = deque([(sx, sy)])
while q:
    x, y = q.popleft()
    if (x, y) == (tx, ty): break
    for dx, dy, d in ((1,0,'RIGHT'),(-1,0,'LEFT'),(0,1,'DOWN'),(0,-1,'UP')):
        nx, ny = x+dx, y+dy
        if (nx, ny) not in prev and (walk(nx, ny) or (nx, ny) == (tx, ty)):
            prev[(nx, ny)] = (x, y, d)
            q.append((nx, ny))
if (tx, ty) not in prev:
    print('NO PATH'); sys.exit(1)
# reconstruct + compress into legs
path = []
cur = (tx, ty)
while prev[cur]:
    x, y, d = prev[cur]
    path.append(d)
    cur = (x, y)
path.reverse()
legs = []
for d in path:
    if legs and legs[-1][0] == d: legs[-1][1] += 1
    else: legs.append([d, 1])
print(f'route {sx},{sy} -> {tx},{ty}: {len(path)} steps, {len(legs)} legs')
for d, n in legs:
    print(f'  {d} x{n}')
