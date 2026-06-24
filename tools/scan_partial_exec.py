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
LEN = {0x00:1,0x01:1,0x02:1,0x03:1,0x04:5,0x05:5,0x06:6,0x07:6,0x08:2,0x09:2,0x0A:3,0x0B:3,0x0C:1,0x0D:1,
0x0E:2,0x0F:6,0x10:3,0x11:6,0x12:6,0x13:6,0x14:3,0x15:9,0x16:5,0x17:5,0x18:5,0x19:5,0x1A:5,0x1B:3,0x1C:3,
0x1D:6,0x1E:6,0x1F:6,0x20:9,0x21:5,0x22:5,0x23:5,0x24:5,0x25:3,0x26:5,0x27:1,0x28:3,0x29:3,0x2A:3,0x2B:3,
0x2C:5,0x2D:1,0x2E:1,0x2F:3,0x30:1,0x31:3,0x32:1,0x33:4,0x34:3,0x35:1,0x36:3,0x37:2,0x38:2,0x39:8,0x3A:8,
0x3B:8,0x3C:3,0x3D:8,0x3E:8,0x3F:8,0x40:8,0x41:8,0x42:5,0x43:1,0x44:5,0x45:5,0x46:5,0x47:5,0x48:3,0x49:5,
0x4A:5,0x4B:3,0x4C:3,0x4D:3,0x4E:3,0x4F:7,0x50:9,0x51:3,0x52:5,0x53:3,0x54:5,0x55:3,0x56:5,0x57:7,0x58:5,
0x59:5,0x5A:1,0x5B:4,0x5C:0,0x5D:1,0x5E:1,0x5F:1,0x60:3,0x61:3,0x62:3,0x63:7,0x64:3,0x65:4,0x66:1,0x67:5,
0x68:1,0x69:1,0x6A:1,0x6B:1,0x6C:1,0x6D:1,0x6E:3,0x6F:5,0x70:6,0x71:6,0x72:1,0x73:5,0x74:5,0x75:5,0x76:1,
0x77:2,0x78:5,0x79:12,0x7A:3,0x7B:5,0x7C:3,0x7D:4,0x7E:2,0x7F:4,0x80:4,0x81:4,0x82:4,0x83:4,0x84:4,0x85:6,
0x86:5,0x87:5,0x88:5,0x89:3,0x8A:4,0x8B:1,0x8C:1,0x8D:1,0x8E:1,0x8F:3,0x90:6,0x91:6,0x92:6,0x93:4,0x94:3,
0x95:4,0x96:3,0x97:2,0x98:3,0x99:3,0x9A:2,0x9B:5,0x9C:3,0x9D:4,0x9E:3,0x9F:3,0xA0:1,0xA1:5,0xA2:9,0xA3:1,
0xA4:3,0xA5:1,0xA6:2,0xA7:3,0xA8:5,0xA9:4,0xAA:8,0xAB:3,0xAC:5,0xAD:5,0xAE:1,0xAF:5,0xB0:5,0xB1:8,0xB2:1,
0xB3:3,0xB4:3,0xB5:3,0xB6:6,0xB7:1,0xB8:5,0xB9:5,0xBA:5,0xBB:6,0xBC:6,0xBD:5,0xBE:5,0xBF:6,0xC0:3,0xC1:3,
0xC2:3,0xC3:2,0xC4:8,0xC5:1,0xC6:4,0xC7:2,0xC8:5,0xC9:1,0xCA:1,0xCB:1,0xCC:6,0xCD:3,0xCE:3,0xCF:1,0xD0:3,
0xD1:8,0xD2:4,0xD3:5,0xD4:6}
TERM = {0x02,0x03,0x05,0x08,0x0C,0x0D,0x24,0xB9}
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
