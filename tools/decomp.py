#!/usr/bin/env python3
"""FireRed event-script decompiler (curated opcode set; stops at unknown opcodes
rather than desyncing). Usage: decomp.py [bank,map | 0xOFFSET] ..."""
import sys
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
def u16(o): return ag[o] | ag[o+1] << 8
def u32(o): return ag[o] | ag[o+1]<<8 | ag[o+2]<<16 | ag[o+3]<<24
def pf(o):
    v = u32(o); return v-ROM if 0x08000000 <= v < 0x08000000+len(ag) else None
CH = {0x00:' '}
for i,c in enumerate('0123456789'): CH[0xA1+i]=c
for i in range(26): CH[0xBB+i]=chr(65+i)
for i in range(26): CH[0xD5+i]=chr(97+i)
CH.update({0xAB:'!',0xAC:'?',0xAD:'.',0xAE:'-',0xB0:'…',0xB8:',',0xBA:'/',0xB5:'♂',0xB6:'♀',
 0xF0:':',0xB1:'“',0xB2:'”',0xB4:'’',0xB3:'‘'})
def dtext(o):
    if o is None or o >= len(ag): return '<bad ptr>'
    s=[]; i=o; lim=o+300
    while 0 <= i < len(ag) and i < lim:
        b=ag[i]
        if b==0xFF: break
        if b==0xFE: s.append('\\n')
        elif b==0xFB: s.append('\\p')
        elif b==0xFA: s.append('\\l')
        elif b in (0xFD,0xFC): s.append('{%02X%02X}'%(b, ag[i+1] if i+1<len(ag) else 0)); i+=2; continue
        elif b in CH: s.append(CH[b])
        else: s.append('[%02X]'%b)
        i+=1
    return ''.join(s)

T={0x00:('nop',1),0x01:('nop1',1),0x02:('end',1),0x03:('return',1),0x04:('call',5),0x05:('goto',5),
0x06:('if_goto',6),0x07:('if_call',6),0x08:('gotostd',2),0x09:('callstd',2),0x0A:('gotostd_if',3),
0x0B:('callstd_if',3),0x0D:('killscript',1),0x0F:('loadpointer',6),0x16:('setvar',5),0x17:('addvar',5),
0x18:('subvar',5),0x19:('copyvar',5),0x1A:('setorcopyvar',5),0x21:('compare',5),0x25:('special',3),
0x26:('special2',5),0x27:('waitstate',1),0x28:('pause',3),0x29:('setflag',3),0x2A:('clearflag',3),
0x2B:('checkflag',3),0x2F:('sound',3),0x31:('fanfare',3),0x32:('waitfanfare',1),0x33:('playsong',4),
0x36:('fadesong',3),0x4F:('applymovement',7),0x51:('waitmovement',3),0x53:('hidesprite',3),
0x54:('showsprite',3),0x5A:('faceplayer',1),0x6A:('lock',1),0x6B:('lockall',1),0x6C:('release',1),
0x6D:('releaseall',1)}
TERM={0x02,0x03,0x05,0x0D}
SUB={0x04,0x05,0x06,0x07}

def decompile(start, out, visited, depth=0):
    if start in visited or depth > 40: return
    visited.add(start)
    out.append(f'\n; ---- @0x{start:06X} ----')
    o = start
    while 0 <= o < len(ag):
        op = ag[o]
        if op not in T:
            out.append(f'  0x{o:06X}: ??? 0x{op:02X}  (opcode not in v1 table — stop)'); break
        name, ln = T[op]
        note = ''
        if op == 0x0F: note = '  text="%s"' % dtext(pf(o+2))
        elif op in (0x29,0x2A,0x2B): note = '  flag=0x%04X' % u16(o+1)
        elif op == 0x25: note = '  special=0x%04X' % u16(o+1)
        elif op in (0x16,0x17,0x19,0x1A,0x21): note = '  var=0x%04X val=0x%04X' % (u16(o+1), u16(o+3))
        elif op == 0x09: note = '  std=%d' % ag[o+1]
        sub = pf(o + (2 if op in (0x06,0x07) else 1)) if op in SUB else None
        if sub is not None: note += '  ->0x%06X' % sub
        out.append(f'  0x{o:06X}: {name}{note}')
        if sub is not None: decompile(sub, out, visited, depth+1)
        if op in TERM: break
        o += ln

LIT = 0x5524C
def plist(off, cap):
    r=[]
    for i in range(cap):
        p=pf(off+4*i)
        if p is None: break
        r.append(p)
    return r
def header(bank, mp): return plist(plist(pf(LIT),64)[bank],150)[mp]
def scripts(hoff):
    res=[]; ev=pf(hoff+4); ms=pf(hoff+8)
    if ev:
        nP,nT,nS=ag[ev],ag[ev+2],ag[ev+3]; pP,pT,pS=pf(ev+4),pf(ev+12),pf(ev+16)
        if pP:
            for i in range(min(nP,80)):
                sp=pf(pP+i*24+16); res.append(('person%d'%i,sp)) if sp else None
        if pT:
            for i in range(min(nT,80)):
                sp=pf(pT+i*16+12); res.append(('trig%d'%i,sp)) if sp else None
        if pS:
            for i in range(min(nS,80)):
                oo=pS+i*12
                if oo+12<=len(ag) and ag[oo+5]<5:
                    sp=pf(oo+8); res.append(('sign%d'%i,sp)) if sp else None
    if ms:
        i=ms
        while i+5<=len(ag) and ag[i]!=0:
            p=pf(i+1); res.append(('mapscr_t%d'%ag[i],p)) if p else None; i+=5
    return res

args = sys.argv[1:] or ['3,0']
out=['# Ash Gray — decompiled scripts (v1 decompiler)\n']
for a in args:
    if ',' in a:
        b,m=map(int,a.split(',')); h=header(b,m)
        scrs=scripts(h)
        out.append(f'\n## map {b}.{m} (header 0x{h:06X}) — {len(scrs)} script refs')
        vis=set()
        for lbl,off in scrs:
            out.append(f'\n### {lbl} @0x{off:06X}')
            decompile(off,out,vis)
    else:
        off=int(a,16); decompile(off,out,set())
open('audit/06-decompile.md','w').write('\n'.join(out)+'\n')
print('-> audit/06-decompile.md\n'); print('\n'.join(out[:70]))
