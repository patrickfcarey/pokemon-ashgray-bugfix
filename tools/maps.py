#!/usr/bin/env python3
"""Walk FireRed/Ash Gray map+event tables (table addr is a literal @0x5524C),
extract script pointers, flag maps whose scripts point into Ash Gray's >0x700000 area."""
ag = open('rom/ashgray.gba', 'rb').read()
fr = open('base/firered.gba', 'rb').read()
ROM = 0x08000000
NEW = 0x700000
LIT = 0x5524C   # code literal holding the map-bank-table address

def u32(d, o): return d[o] | d[o+1]<<8 | d[o+2]<<16 | d[o+3]<<24
def ptr(d, o):
    v = u32(d, o)
    return (v - ROM) if 0x08000000 <= v < 0x08000000 + len(d) else None
def ptr_list(d, off, cap):
    out=[]
    for i in range(cap):
        p=ptr(d, off+4*i)
        if p is None: break
        out.append(p)
    return out

bt_fr = ptr(fr, LIT); bt_ag = ptr(ag, LIT)
print(f"bank table: FireRed @0x{bt_fr:06X}  AshGray @0x{bt_ag:06X}  ({'RELOCATED' if bt_fr!=bt_ag else 'same'})")
banks = ptr_list(ag, bt_ag, 64)
print("banks:", len(banks))

maps=[]
for bi,boff in enumerate(banks):
    hdrs=ptr_list(ag, boff, 150)
    for mi,hoff in enumerate(hdrs):
        if hoff in banks: break          # ran into next bank list
        maps.append((bi,mi,hoff))

def scripts_of(d, hoff):
    res=[]
    ev=ptr(d,hoff+4); ms=ptr(d,hoff+8)
    if ms: res.append(('mapscript',ms))
    if ev is None or ev+20>len(d): return res
    nP,nW,nT,nS=d[ev],d[ev+1],d[ev+2],d[ev+3]
    pP,pT,pS=ptr(d,ev+4),ptr(d,ev+12),ptr(d,ev+16)
    if pP:
        for i in range(min(nP,80)):
            sp=ptr(d,pP+i*24+16)
            if sp: res.append((f'person{i}',sp))
    if pT:
        for i in range(min(nT,80)):
            sp=ptr(d,pT+i*16+12)
            if sp: res.append((f'trig{i}',sp))
    if pS:
        for i in range(min(nS,80)):
            o=pS+i*12
            if o+12<=len(d) and d[o+5]<5:
                sp=ptr(d,o+8)
                if sp: res.append((f'sign{i}',sp))
    return res

rewritten=[]; tot=0; new=0
for (bi,mi,hoff) in maps:
    s=scripts_of(ag,hoff); tot+=len(s)
    nw=[(l,o) for l,o in s if o>=NEW]; new+=len(nw)
    if nw: rewritten.append((bi,mi,hoff,s,nw))

print(f"maps: {len(maps)}  script refs: {tot}  new(>0x700000): {new}  rewritten maps: {len(rewritten)}")

# Known FireRed bank.map names for the early game (for readability)
NAMES={(3,0):'Pallet Town',(3,1):'Viridian City',(3,2):'Pewter City',(3,3):'Cerulean City',
 (3,4):'Lavender Town',(3,5):'Vermilion City',(3,6):'Celadon City',(3,7):'Fuchsia City',
 (3,8):'Cinnabar Island',(3,9):'Indigo Plateau',(3,10):'Saffron City',
 (4,0):'Route 1',(4,1):'Route 2',(4,2):'Route 3',(4,3):'Route 4',(4,4):'Route 5',
 (2,0):'Player house 1F',(2,1):'Player house 2F',(2,2):'Rival house',(2,3):'Oak Lab'}

out=['# Ash Gray — maps with rewritten event scripts\n',
     f'- bank table relocated to 0x{bt_ag:06X} (FireRed: 0x{bt_fr:06X})',
     f'- maps walked: {len(maps)} · script refs: {tot} · rewritten maps: **{len(rewritten)}**\n',
     '| bank.map | name | #refs | rewritten script offsets |',
     '|----------|------|-------|--------------------------|']
for (bi,mi,hoff,s,nw) in rewritten:
    nm=NAMES.get((bi,mi),'')
    refs=', '.join(f'{l}@0x{o:06X}' for l,o in nw[:6])
    if len(nw)>6: refs+=f' …(+{len(nw)-6})'
    out.append(f'| {bi}.{mi} | {nm} | {len(s)} | {refs} |')
# scratch path by default (AUDIT_OUT=audit/02-maps.md to update the tracked doc)
import os as _os
_outf = _os.environ.get('AUDIT_OUT', '/tmp/02-maps.md')
open(_outf,'w').write('\n'.join(out)+'\n')
print(f'-> {_outf}')
for (bi,mi,hoff,s,nw) in rewritten[:14]:
    print(f"  {bi}.{mi} {NAMES.get((bi,mi),''):16} refs={len(s):2}  e.g. {nw[0][0]}@0x{nw[0][1]:06X}")
