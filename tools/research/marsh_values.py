#!/usr/bin/env python3
"""Static value routing for the Marsh (Sabrina/Saffron) gym. Enumerate the full lifecycle of
its gate vars 0x6072 & 0x6074: every setvar/addvar (what values, in what scene) and every
compare (what the dispatcher branches on). Goal: find the 'done/badge-earned' value, and what
a CORRUPT value (not a legit progression value) routes to — block vs looks-done-no-badge."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
cs = {0xBB+j: chr(65+j) for j in range(26)}; cs.update({0xD5+j: chr(97+j) for j in range(26)})
cs.update({0x00:' ',0xAD:'.',0xB4:"'",0xAC:'!',0xF0:':',0xFE:'/'}); [cs.update({0xA1+j:str(j)}) for j in range(10)]
def dec(o,n=52):
    s=''
    for b in ag[o:o+n]:
        if b==0xFF: break
        s+=cs.get(b,'')
    return s.strip()
def near_text(o,rng=70):
    best=''
    for k in range(o-rng,o+rng):
        p=struct.unpack('<I',ag[k:k+4])[0]
        if 0x8000000<=p<0x8000000+len(ag):
            t=dec(p-ROM)
            if sum(c.isalpha() for c in t)>sum(c.isalpha() for c in best): best=t
    return best[:48]
COND={0:'<',1:'==',2:'>',3:'<=',4:'>=',5:'!='}
for var in (0x6072,0x6074):
    print(f"\n========== var 0x{var:04X} lifecycle ==========")
    lo=bytes([var&0xFF,var>>8])
    i=-1
    while True:
        i=ag.find(lo,i+1)
        if i<0: break
        if not(0x7F0000<=i<0x8D0000): continue
        op=ag[i-1]
        if op==0x16:   # setvar
            val=struct.unpack('<H',ag[i+2:i+4])[0]
            print(f"  setvar  =0x{val:X}  @{i-1:#x}   \"{near_text(i)}\"")
        elif op==0x17: # addvar
            val=struct.unpack('<H',ag[i+2:i+4])[0]
            print(f"  addvar  +0x{val:X}  @{i-1:#x}   \"{near_text(i)}\"")
        elif op==0x21: # compare
            val=struct.unpack('<H',ag[i+2:i+4])[0]
            nx=ag[i+4]; cond=ag[i+5] if nx in (6,7) else None
            tgt=struct.unpack('<I',ag[i+6:i+10])[0]-ROM if nx in (6,7) else None
            br=f"{'goto_if' if nx==6 else 'call_if' if nx==7 else '?'} {COND.get(cond,'?')} ->{tgt:#x}" if tgt else ''
            print(f"  compare {COND.get(cond,'?')}0x{val:X}  @{i-1:#x}   {br}")
