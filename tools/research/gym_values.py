#!/usr/bin/env python3
"""Value-routing for the other exposed gyms' gate vars (like marsh_values.py for 0x6072).
For each: every setvar/addvar (legit progression values + scene) and every compare (branch).
Goal: does a CORRUPT value (outside the legit set) route to a badge-block?"""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
cs = {0xBB+j: chr(65+j) for j in range(26)}; cs.update({0xD5+j: chr(97+j) for j in range(26)})
cs.update({0x00:' ',0xAD:'.',0xB4:"'",0xAC:'!',0xF0:':',0xFE:'/'}); [cs.update({0xA1+j:str(j)}) for j in range(10)]
def dec(o,n=48):
    s=''
    for b in ag[o:o+n]:
        if b==0xFF: break
        s+=cs.get(b,'')
    return s.strip()
def near_text(o,rng=64):
    best=''
    for k in range(o-rng,o+rng):
        p=struct.unpack('<I',ag[k:k+4])[0]
        if 0x8000000<=p<0x8000000+len(ag):
            t=dec(p-ROM)
            if sum(c.isalpha() for c in t)>sum(c.isalpha() for c in best): best=t
    return best[:44]
COND={0:'<',1:'==',2:'>',3:'<=',4:'>=',5:'!='}
GYMVAR={0x6082:'Boulder/Brock',0x6190:'Cascade/Daisy(gateA)',0x6113:'Cascade(gateB=L13)',
        0x6186:'Volcano/Blaine',0x6088:'Thunder/Surge(downstream)'}
for var,nm in GYMVAR.items():
    print(f"\n===== 0x{var:04X} {nm} =====")
    lo=bytes([var&0xFF,var>>8]); i=-1; sets=[]; comps=[]
    while True:
        i=ag.find(lo,i+1)
        if i<0: break
        if not(0x7F0000<=i<0x8D0000): continue
        op=ag[i-1]
        if op in (0x16,0x17):
            v=struct.unpack('<H',ag[i+2:i+4])[0]; sets.append((i-1,op,v))
        elif op==0x21:
            v=struct.unpack('<H',ag[i+2:i+4])[0]; nx=ag[i+4]
            cond=ag[i+5] if nx in (6,7) else None
            tgt=struct.unpack('<I',ag[i+6:i+10])[0]-ROM if nx in (6,7) else None
            comps.append((i-1,v,cond,tgt))
    vals=sorted(set(v for _,_,v in sets))
    print(f"  legit values set: {[hex(v) for v in vals]}")
    for o,op,v in sets:
        print(f"   {'setvar' if op==0x16 else 'addvar'} ={hex(v)} @{o:#x}  \"{near_text(o)}\"")
    for o,v,cond,tgt in comps:
        ts = f"{tgt:#x}" if tgt else "(no branch)"
        print(f"   compare {COND.get(cond,'?')}{hex(v)} @{o:#x} -> {ts}")
