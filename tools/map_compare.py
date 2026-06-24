#!/usr/bin/env python3
"""Compare map headers/layouts: is 28.0 a bedroom-layout clone of 4.1?
Also dump 28.0's full event lists and find who references the dream-TV text."""
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
def u16(o): return ag[o] | ag[o+1] << 8
def s16(o):
    v = u16(o); return v - 0x10000 if v & 0x8000 else v
def pf(o):
    if o is None or o+4 > len(ag): return None
    v = ag[o] | ag[o+1]<<8 | ag[o+2]<<16 | ag[o+3]<<24
    return v - ROM if 0x08000000 <= v < 0x08000000+len(ag) else None
LIT = 0x5524C
def plist(off, cap):
    r = []
    for i in range(cap):
        p = pf(off + 4*i)
        if p is None: break
        r.append(p)
    return r
banks = plist(pf(LIT), 64)
def header(b, m): return plist(banks[b], 200)[m]
for tag, b, m in (("bedroom", 4, 1), ("gate?", 28, 0)):
    h = header(b, m)
    lay = pf(h)                     # header+0 = map layout ptr
    ev = pf(h+4)
    print(f"{tag} {b}.{m}: header=0x{h:06X} layout=0x{lay:06X}" if lay else f"{tag}: bad layout")
    if lay:
        w, hh = pf(lay) is not None and u16(lay) or 0, u16(lay+4)
        # layout: +0 width(4) +4 height(4) +8 border +12 blockdata +16 tileset1 +20 tileset2
        import struct
        W = int.from_bytes(ag[lay:lay+4], 'little'); H = int.from_bytes(ag[lay+4:lay+8], 'little')
        bd = pf(lay+12); t1 = pf(lay+16); t2 = pf(lay+20)
        print(f"   size={W}x{H} blocks=0x{bd:06X} tilesets=0x{t1:06X},0x{t2:06X}")
    if ev:
        nO, nW, nT, nB = ag[ev], ag[ev+1], ag[ev+2], ag[ev+3]
        print(f"   events: obj={nO} warp={nW} trig={nT} bg={nB}")
        pP, pB = pf(ev+4), pf(ev+16)
        if pP:
            for i in range(min(nO, 10)):
                o = pP + i*24
                spr = ag[o+1]; x, y = s16(o+4), s16(o+6)
                sp = pf(o+16); fl = u16(o+20)
                print(f"     obj#{i}: sprite={spr} pos=({x},{y}) script={'0x%06X'%sp if sp else None} flag=0x{fl:04X}")
        if pB:
            for i in range(min(nB, 10)):
                o = pB + i*12
                x, y = s16(o), s16(o+2)
                kind = ag[o+5]; sp = pf(o+8)
                print(f"     bg#{i}: pos=({x},{y}) kind={kind} script={'0x%06X'%sp if sp else None}")
print("done")
