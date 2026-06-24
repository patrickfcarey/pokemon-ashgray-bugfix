#!/usr/bin/env python3
"""Phase 2: for each problem destination/source, compare warp counts + layout vs vanilla
(same header address, vanilla-region only) and check incoming-warp reachability."""
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
fr = open('base/firered.gba', 'rb').read()

def pf(d, o):
    if o is None or o+4 > len(d): return None
    v = d[o] | d[o+1] << 8 | d[o+2] << 16 | d[o+3] << 24
    return v - ROM if 0x08000000 <= v < 0x08000000 + len(d) else None

def plist(d, off, cap):
    r = []
    for i in range(cap):
        p = pf(d, off + 4*i)
        if p is None: break
        r.append(p)
    return r

banks = plist(ag, pf(ag, 0x5524C), 64)
amaps = {b: plist(ag, bt, 200) for b, bt in enumerate(banks)}

def info(d, h):
    ev = pf(d, h+4)
    if ev is None: return None
    return (ag if d is ag else fr)[ev+1], pf(d, ev+8)

# interesting maps from the audit
TARGETS = [(3,25),(3,26),(3,49),(2,13),(3,30),(1,49),(1,50),(1,59),(3,10),(3,116),(10,10),
           (3,8),(16,0),(21,0),(25,1),(3,37),(3,64),(35,1),(37,0),(37,1),(34,2),(1,85),(10,7),(10,8)]
print(f'{"map":8} {"hdr":>8} {"ash nW":>6} {"van nW":>6}  layoutOK?  note')
for g, n in TARGETS:
    if n >= len(amaps[g]): print(f'{g}.{n}: missing'); continue
    h = amaps[g][n]
    vreg = 0x340000 <= h < 0x360000
    anW = info(ag, h)
    a = anW[0] if anW else '?'
    v = '-'
    if vreg:
        vev = pf(fr, h+4)
        v = fr[vev+1] if vev is not None else '?'
    lay = pf(ag, h)
    W = int.from_bytes(ag[lay:lay+4], 'little') if lay else 0
    H = int.from_bytes(ag[lay+4:lay+8], 'little') if lay else 0
    ok = 'ok' if 0 < W < 1000 and 0 < H < 1000 else f'BAD {W}x{H}'
    print(f'{g}.{n:<6} 0x{h:06X} {a:>6} {v:>6}  {ok:10} {"vanilla-region" if vreg else "CUSTOM"}')
# incoming warps to the bad-source maps (reachability proxy)
print('\nincoming warps into bad-source maps:')
SRC = [(1,30),(1,32),(1,33),(1,35),(1,55),(1,56),(1,61),(1,85),(2,20),(2,21),(2,22),(2,23),
       (2,34),(2,40),(2,55),(3,18),(3,115),(10,7),(10,8),(10,11),(12,7),(16,1),(20,0),(21,1),
       (23,0),(25,2),(27,0),(33,4),(34,1),(35,2),(37,0),(37,1),(42,0)]
incount = {s: 0 for s in SRC}
for b in amaps:
    for m, h in enumerate(amaps[b]):
        if h is None or h+0x1C > len(ag): continue
        ev = pf(ag, h+4)
        if ev is None: continue
        nW = ag[ev+1]; pW = pf(ag, ev+8)
        if not pW: continue
        for w in range(min(nW, 40)):
            o = pW + w*8
            if o+8 > len(ag): break
            key = (ag[o+7], ag[o+6])
            if key in incount: incount[key] += 1
print('  ', {f'{a}.{b}': c for (a, b), c in incount.items() if c > 0})
print('  zero-incoming:', [f'{a}.{b}' for (a, b), c in incount.items() if c == 0])
