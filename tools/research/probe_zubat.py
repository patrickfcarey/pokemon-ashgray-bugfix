#!/usr/bin/env python3
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/', 0xFB: '|'})
def dec(o, n=60):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF:
            break
        s += cs.get(b, f'[{b:02x}]')
    return s

# ZUBAT text = D4 CF BC BB CE
print('=== "ZUBAT" text ===')
pat = bytes([0xD4, 0xCF, 0xBC, 0xBB, 0xCE])
i = 0; hits = []
while True:
    i = ag.find(pat, i + 1)
    if i < 0: break
    hits.append(i)
print(f'  {len(hits)} hits')
for h in hits[:12]:
    print(f'   @{h:#x}: "{dec(h)}"')

# setwildbattle ZUBAT = B6 29 00
print('=== setwildbattle ZUBAT (B6 29 00) in script bank ===')
i = 0
while True:
    i = ag.find(b'\xb6\x29\x00', i + 1)
    if i < 0: break
    if 0x700000 < i < 0x8D0000:
        print(f'   @{i:#x}: lvl={ag[i+3]} ctx={ag[i-5:i+8].hex(" ")}')

# Mt Moon map name "MT" — gMapNames region; search "MT[2e]MOON" = C7 CE AD C7 C9 C9 C8
print('=== "MT.MOON" map name ===')
pat2 = bytes([0xC7, 0xCE, 0xAD, 0xC7, 0xC9, 0xC9, 0xC8])
i = 0
while True:
    i = ag.find(pat2, i + 1)
    if i < 0: break
    print(f'   @{i:#x}: "{dec(i)}"')
# also without the dot
pat3 = bytes([0xC7, 0xCE, 0x00, 0xC7, 0xC9, 0xC9, 0xC8])
i = 0
while True:
    i = ag.find(pat3, i + 1)
    if i < 0: break
    print(f'   @{i:#x} (no-dot): "{dec(i)}"')
