#!/usr/bin/env python3
"""Label the high-value gate vars by the dialogue near their gate sites, to name the
story events that Box 3/6 corruption can misroute. Confirms known D1 cases + surfaces new."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
cs = {0xBB+j: chr(65+j) for j in range(26)}; cs.update({0xD5+j: chr(97+j) for j in range(26)})
cs.update({0x00:' ',0xAD:'.',0xB4:"'",0xAC:'!',0xF0:':',0xFE:'/',0xFA:' ',0xFB:' '})
for j in range(10): cs[0xA1+j] = str(j)
def dec(o, n=44):
    s=''
    for b in ag[o:o+n]:
        if b==0xFF: break
        s += cs.get(b,'')
    return s.strip()
def label(v, sites):
    # scan a window around each gate site for a text pointer; return the wordiest decode
    best=''
    for st in sites[:6]:
        for k in range(st-40, st+80):
            p = struct.unpack('<I', ag[k:k+4])[0]
            if 0x08000000 <= p < 0x08000000+len(ag):
                t = dec(p-ROM)
                if sum(c.isalpha() for c in t) > sum(c.isalpha() for c in best):
                    best=t
    return best[:40]
# recollect gate sites for the vars of interest
def gate_sites(v):
    out=[]; i=0x800000
    while i<0x8D0000-10:
        if ag[i]==0x21 and struct.unpack('<H',ag[i+1:i+3])[0]==v and ag[i+5] in (0x06,0x07):
            p=struct.unpack('<I',ag[i+7:i+11])[0]
            if 0x08000000<=p<0x08000000+len(ag): out.append(i)
        i+=1
    return out
KNOWN = {0x6079:'L14 Spearow chase',0x6105:'L15 Seymour/Zubat',0x6113:'L13 Cerulean gym',
         0x6155:'#6a Koga/Soul',0x6086:'Charmander',0x7014:'L1 Indigo gate',0x6158:'F4 pickaxe'}
TOP = [0x6300,0x6173,0x7005,0x6192,0x6301,0x6306,0x6194,0x6143,0x6167,0x6186,0x7003,0x6303,
       0x6117,0x6097,0x6137,0x7051,0x7040,0x7012,0x6060,0x6069,0x6082,0x6100,0x6000]
print("=== KNOWN D1 cases (confirm mapping) ===")
for v,nm in KNOWN.items():
    print(f"  0x{v:04X} {nm:20s}: \"{label(v, gate_sites(v))}\"")
print("\n=== TOP-referenced / lowest-slot gates (the 'other broken things') ===")
for v in TOP:
    s=gate_sites(v)
    print(f"  0x{v:04X} ({len(s):2d} sites): \"{label(v, s)}\"")
