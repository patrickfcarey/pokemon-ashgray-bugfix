#!/usr/bin/env python3
"""Global warp-event audit: for every warp on every map, validate
   (a) dest bank/map exists, (b) dest header + layout are sane (dims < 1000),
   (c) dest warpId is within the dest map's warp table.
Catches F6-class dead-map warps and L5-class wrong-destination wiring ROM-wide."""
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000

def pf(o):
    if o is None or o+4 > len(ag): return None
    v = ag[o] | ag[o+1] << 8 | ag[o+2] << 16 | ag[o+3] << 24
    return v - ROM if 0x08000000 <= v < 0x08000000 + len(ag) else None

def u16(o): return ag[o] | ag[o+1] << 8
def u32(o): return int.from_bytes(ag[o:o+4], 'little')

def plist(off, cap):
    r = []
    for i in range(cap):
        p = pf(off + 4*i)
        if p is None: break
        r.append(p)
    return r

banks = plist(pf(0x5524C), 64)
maps = {b: plist(bt, 200) for b, bt in enumerate(banks)}

def mapinfo(b, m):
    """returns (ok, nwarps, reason)"""
    if b >= len(banks) or m >= len(maps[b]): return (False, 0, 'NO SUCH MAP')
    h = maps[b][m]
    if h is None or h + 0x1C > len(ag): return (False, 0, 'BAD HEADER')
    lay = pf(h)
    if lay is None: return (False, 0, 'BAD LAYOUT PTR')
    W, H = u32(lay), u32(lay+4)
    if not (0 < W < 1000 and 0 < H < 1000): return (False, 0, f'INSANE LAYOUT {W}x{H}')
    ev = pf(h+4)
    if ev is None: return (False, 0, 'BAD EVENTS PTR')
    nW = ag[ev+1]
    return (True, nW, '')

bad = 0
total = 0
for b in maps:
    for m, h in enumerate(maps[b]):
        if h is None or h + 0x1C > len(ag): continue
        ev = pf(h+4)
        if ev is None: continue
        nW = ag[ev+1]; pW = pf(ev+8)
        if not pW or nW == 0: continue
        for w in range(min(nW, 40)):
            o = pW + w*8
            if o+8 > len(ag):
                print(f'TRUNCATED WARP TABLE: map {b}.{m} warp#{w} @0x{o:06X}')
                bad += 1
                break
            dg, dn, dw = ag[o+7], ag[o+6], ag[o+5]
            total += 1
            if dg == 0x7F:   # special: dynamic warp (used by some systems)
                continue
            ok, dnW, reason = mapinfo(dg, dn)
            if not ok:
                bad += 1
                print(f'BAD DEST: map {b}.{m} warp#{w} @({u16(o)},{u16(o+2)}) -> {dg}.{dn} [{reason}]')
            elif dw != 0xFF and dw >= dnW:
                bad += 1
                print(f'BAD WARPID: map {b}.{m} warp#{w} @({u16(o)},{u16(o+2)}) -> {dg}.{dn} warpId {dw} (dest has {dnW})')
print(f'\naudited {total} warps; {bad} problems')
