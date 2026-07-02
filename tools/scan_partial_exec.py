#!/usr/bin/env python3
"""Find person33-class freeze/crash NPCs: event scripts that EXECUTE a valid pointer-dereferencing
command on a WILD (out-of-ROM) operand before the bounds-checked VM stops. (person33's braillemessage
on an open-bus pointer is the prototype: it infinite-loops the braille renderer -> hard freeze.)

Unlike scan_dead_scripts.py (which flags scripts that *start* on garbage), this decodes the leading
commands and only flags ones whose POINTER operand is outside [0x08000000, 0x08000000+romlen)."""
import sys
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000; ROMEND = ROM + len(ag)
def u16(o): return ag[o] | ag[o+1] << 8
def u32(o): return ag[o] | ag[o+1]<<8 | ag[o+2]<<16 | ag[o+3]<<24
def pf(o):
    if o is None or o+4 > len(ag): return None
    v = u32(o); return v-ROM if ROM <= v < ROMEND else None
def plist(off, cap):
    r=[]
    for i in range(cap):
        p=pf(off+4*i)
        if p is None: break
        r.append(p)
    return r
from oplen import LEN, TERM   # canonical engine-derived lengths (see tools/oplen.py)
# commands that unambiguously take a ROM POINTER operand, with the operand's byte offset and a danger tag
DEREF = {0x67:('message',1,'text-render-loop'), 0x78:('braillemessage',1,'braille-render-loop'),
         0x4F:('applymovement',3,'garbage-movement'), 0x50:('applymovement_at',3,'garbage-movement'),
         0x23:('callnative',1,'CODE-EXEC'), 0x24:('gotonative',1,'CODE-EXEC'),
         0x9B:('messageautoscroll',1,'text-render-loop'), 0xBD:('vmessage',1,'text-render-loop'),
         0xC8:('loadhelp',1,'text-render-loop'), 0x85:('bufferstring',2,'string-copy')}

def analyze(sp):
    """decode leading commands; return list of (cmd_name, danger, wild_ptr) for deref cmds w/ out-of-ROM ptr."""
    o = sp; hits = []
    for _ in range(40):
        if o < 0 or o >= len(ag): break
        op = ag[o]
        if op not in LEN: break          # hit invalid opcode (dangling into garbage) -> stop
        if op in DEREF:
            nm, poff, danger = DEREF[op]
            val = u32(o+poff)
            if not (ROM <= val < ROMEND):   # operand is NOT a valid ROM pointer -> WILD
                hits.append((o, nm, danger, val))
        if op == 0x5C or op in TERM: break
        o += LEN[op]
    return hits

banks = plist(pf(0x5524C), 64)
total = 0
for b, bt in enumerate(banks):
    for m, h in enumerate(plist(bt, 160)):
        ev = pf(h+4)
        if not ev or ev+20 > len(ag): continue
        nP, nT, nS = ag[ev], ag[ev+2], ag[ev+3]
        pP, pT, pS = pf(ev+4), pf(ev+12), pf(ev+16)
        def emit(kind, i, sp):
            global total
            for (at, nm, danger, val) in analyze(sp):
                print('  MAP %-5s %s%-2d script=0x%08X  ->  %s @0x%08X operand=0x%08X  [%s]'
                      % (f'{b}.{m}', kind, i, ROM+sp, nm, ROM+at, val, danger))
                total += 1
        if pP:
            for i in range(min(nP, 90)):
                sp = pf(pP+i*24+16)
                if sp is not None: emit('person', i, sp)
        if pT:
            for i in range(min(nT, 90)):
                sp = pf(pT+i*16+12)
                if sp is not None: emit('trig', i, sp)
        if pS:
            for i in range(min(nS, 90)):
                oo = pS+i*12
                if oo+12 <= len(ag) and ag[oo+5] < 5:
                    sp = pf(oo+8)
                    if sp is not None: emit('sign', i, sp)
print(f'\nTOTAL wild-deref event scripts (person33-class freeze/crash candidates): {total}')
