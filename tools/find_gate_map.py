#!/usr/bin/env python3
"""Find which map runs the Indigo-gate script (any event type). Diagnostics included."""
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
def u16(o): return ag[o] | ag[o+1] << 8
def s16(o):
    v = u16(o); return v - 0x10000 if v & 0x8000 else v
def pf(o):
    if o is None or o+4 > len(ag): return None
    v = ag[o] | ag[o+1]<<8 | ag[o+2]<<16 | ag[o+3]<<24
    return v - ROM if 0x08000000 <= v < 0x08000000+len(ag) else None
LIT = 0x5524C
banktbl = pf(LIT)
print(f"map-bank table: *0x{LIT:05X} -> 0x{banktbl:06X}" if banktbl else "bank table deref FAILED")
def plist(off, cap):
    r = []
    for i in range(cap):
        p = pf(off + 4*i)
        if p is None: break
        r.append(p)
    return r
banks = plist(banktbl, 64)
print(f"banks found: {len(banks)}")
TARGETS = {0x869E5A, 0x869E75, 0x82789A}   # gate dispatch, 2nd trigger, "hasn't begun" msgbox
scanned = 0
for b, bt in enumerate(banks):
    maps = plist(bt, 200)
    for m, h in enumerate(maps):
        if h is None or h+28 > len(ag): continue
        scanned += 1
        ev = pf(h + 4)
        if not ev or ev+20 > len(ag): continue
        nObj, nWarp, nTrig, nBg = ag[ev], ag[ev+1], ag[ev+2], ag[ev+3]
        pP, pT, pS = pf(ev+4), pf(ev+12), pf(ev+16)
        # person events (24 bytes, script @+16)
        if pP:
            for i in range(min(nObj,80)):
                sp = pf(pP+i*24+16)
                if sp in TARGETS:
                    x,y = s16(pP+i*24+4), s16(pP+i*24+6)
                    print(f"  PERSON map {b}.{m} obj#{i} x={x} y={y} script=0x{sp:06X}")
        # triggers (16 bytes, script @+12)
        if pT:
            for i in range(min(nTrig,80)):
                sp = pf(pT+i*16+12)
                if sp in TARGETS:
                    print(f"  TRIGGER map {b}.{m} #{i} x={s16(pT+i*16)} y={s16(pT+i*16+2)} script=0x{sp:06X}")
        # signs (12 bytes, script @+8)
        if pS:
            for i in range(min(nBg,80)):
                sp = pf(pS+i*12+8)
                if sp in TARGETS:
                    print(f"  SIGN map {b}.{m} #{i} x={s16(pS+i*12)} y={s16(pS+i*12+2)} script=0x{sp:06X}")
        # mapscripts (header+8)
        ms = pf(h+8)
        if ms:
            j = ms
            for _ in range(20):
                if j+5 > len(ag) or ag[j]==0: break
                p = pf(j+1)
                if p in TARGETS:
                    print(f"  MAPSCRIPT map {b}.{m} type={ag[j]} ptr=0x{p:06X}")
                j += 5
print(f"scanned {scanned} maps. done")
