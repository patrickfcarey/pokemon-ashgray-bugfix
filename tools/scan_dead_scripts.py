#!/usr/bin/env python3
"""Scan every map's person/trigger/sign event scripts for DANGLING/INVALID pointers —
scripts that begin in 0xFF free space or hit an invalid opcode in the first few steps.
These crash the game when the event is interacted with (the "talk -> crash" class)."""
import sys
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
def u16(o): return ag[o] | ag[o+1] << 8
def u32(o): return ag[o] | ag[o+1]<<8 | ag[o+2]<<16 | ag[o+3]<<24
def pf(o):
    if o is None or o+4 > len(ag): return None
    v = u32(o); return v-ROM if ROM <= v < ROM+len(ag) else None
def plist(off, cap):
    r=[]
    for i in range(cap):
        p=pf(off+4*i)
        if p is None: break
        r.append(p)
    return r
from oplen import LEN, TERM   # canonical engine-derived lengths (see tools/oplen.py)

def diag(sp):
    """return None if script looks valid, else a reason string."""
    if sp is None: return None  # null pointer = no-script (engine handles)
    if all(ag[sp+k] == 0xFF for k in range(4)): return 'starts in 0xFF free space'
    o = sp; steps = 0
    while steps < 40:
        if o >= len(ag): return 'runs off ROM end'
        op = ag[o]
        if op == 0x5C: return None         # trainerbattle (variable len) — assume ok
        if op not in LEN: return 'invalid opcode 0x%02X at +%d' % (op, o-sp)
        if op in TERM: return None
        o += LEN[op]; steps += 1
    return None  # long but parseable

banks = plist(pf(0x5524C), 64)
found = 0
for b, bt in enumerate(banks):
    for m, h in enumerate(plist(bt, 160)):
        ev = pf(h+4)
        if not ev or ev+20 > len(ag): continue
        nP, nT, nS = ag[ev], ag[ev+2], ag[ev+3]
        pP, pT, pS = pf(ev+4), pf(ev+12), pf(ev+16)
        if pP:
            for i in range(min(nP, 90)):
                sp = pf(pP+i*24+16); d = diag(sp)
                if d: print(f'  MAP {b}.{m} person{i:<2} script=0x{ROM+sp:08X}  -> {d}'); found+=1
        if pT:
            for i in range(min(nT, 90)):
                sp = pf(pT+i*16+12); d = diag(sp)
                if d: print(f'  MAP {b}.{m} trig{i:<3} script=0x{ROM+sp:08X}  -> {d}'); found+=1
        if pS:
            for i in range(min(nS, 90)):
                oo = pS+i*12
                if oo+12 <= len(ag) and ag[oo+5] < 5:
                    sp = pf(oo+8); d = diag(sp)
                    if d: print(f'  MAP {b}.{m} sign{i:<3} script=0x{ROM+sp:08X}  -> {d}'); found+=1
print(f'\nTOTAL dangling/invalid event scripts: {found}')
