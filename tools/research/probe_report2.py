#!/usr/bin/env python3
"""Second trace pass for the 8-item PokeCommunity report.
#3 doll competition / Lickitung crash; #4 both Rocket duos at breeding center;
#5 Safari Zone Team Rocket; #7 warden / medicine / Dragonair ordering."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/', 0xFB: '|', 0xFA: '\\n'})

def dec(o, n=90):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF:
            break
        s += cs.get(b, f'[{b:02x}]')
    return s

def enc(t):
    inv = {v: k for k, v in cs.items()}
    return bytes(inv[c] for c in t)

def findall(pat, lo=0, hi=None):
    hi = hi or len(ag)
    out = []
    i = lo - 1
    while True:
        i = ag.find(pat, i + 1)
        if i < 0 or i >= hi:
            break
        out.append(i)
    return out

# names that anchor each event
for label in ("JESSIE", "JAMES", "CASSIDY", "BUTCH", "LICKITUNG", "DRAGONAIR",
              "DRATINI", "WARDEN", "MEDICINE", "DOLL"):
    hits = findall(enc(label))
    txt = [h for h in hits]
    print(f'{label:10s}: {len(hits):3d} hits' +
          (f'  e.g. @{hits[0]:#x} "{dec(hits[0],40)}"' if hits else ''))

# #3 Lickitung species 108 = 0x6c — scripted battles (setwildbattle b6 6c 00, trainer too)
print("\n#3 setwildbattle LICKITUNG (b6 6c 00):")
for h in findall(b'\xb6\x6c\x00'):
    if 0x700000 < h < 0x8d0000:
        print(f"  @{h:#x} lvl={ag[h+3]} ctx={ag[h-3:h+10].hex(' ')}")

# #4 trainerbattle (5c) instances in the breeding-center script region 0x852000-0x853000
print("\n#4 trainerbattle (0x5c) in 0x852000-0x853000:")
for h in findall(b'\x5c', 0x852000, 0x853000):
    typ = ag[h+1]
    tid = struct.unpack('<H', ag[h+2:h+4])[0]
    if typ <= 9 and tid < 0x400:
        print(f"  @{h:#x} type={typ} trainer={tid}")
