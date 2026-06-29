#!/usr/bin/env python3
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/', 0xFB: '|'})
def dec(o, n=80):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF:
            break
        s += cs.get(b, f'[{b:02x}]')
    return s
def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

# (A) #6 — Fuchsia "WINNING TRAINERS" board: search "WINNING" = D1 C3 C8 C8 C3 C8 C1
print("=== #6 'WINNING TRAINERS' text ===")
pat = bytes([0xD1,0xC3,0xC8,0xC8,0xC3,0xC8,0xC1])
i = 0
while True:
    i = ag.find(pat, i+1)
    if i < 0: break
    print(f'  @{i:#x}: "{dec(i)}"')

# (B) #4 — breeding center: which map owns the Cassidy&Butch fight (0x852C40)? + is there
# a separate Jessie&James crash point? find map owning scripts near 0x852C00-0x852D00.
print("\n=== #4 breeding-center map (owner of 0x852C40 B&C fight) ===")
banks = pf(0x5524C)
def plist(off, cap):
    r=[]
    for k in range(cap):
        p=pf(off+4*k)
        if p is None: break
        r.append(p)
    return r
for b,bt in enumerate(plist(banks,64)):
    if bt is None: continue
    for m,h in enumerate(plist(bt,230)):
        if h is None or h+0x20>len(ag): continue
        ev=pf(h+4)
        if ev is None: continue
        no=ag[ev]; po=pf(ev+4)
        if not(po and no): continue
        for k in range(no):
            sp=struct.unpack('<I',ag[po+24*k+16:po+24*k+20])[0]-ROM
            if 0x852C00<=sp<=0x852D00:
                print(f"  MAP {b}.{m} obj[{k}] -> {sp:#x}")

# (C) #7 — warden/medicine: search GOLD TEETH / medicine / warden. "WARDEN" = D1 BB CC BE BF C8
print("\n=== #7 warden / medicine event ===")
for label,pat2 in (("WARDEN", bytes([0xD1,0xBB,0xCC,0xBE,0xBF,0xC8])),
                   ("GOLD TEETH", bytes([0xC1,0xC9,0xC6,0xBE,0x00,0xCE,0xBF,0xBF,0xCE,0xC2]))):
    i=0; hh=[]
    while True:
        i=ag.find(pat2,i+1)
        if i<0: break
        hh.append(i)
    print(f'  "{label}": {len(hh)} hits' + (f' e.g. @{hh[0]:#x} "{dec(hh[0])}"' if hh else ''))
