#!/usr/bin/env python3
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/'})
def dec(o, n=72):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF:
            break
        s += cs.get(b, f'[{b:02x}]')
    return s
pat = bytes([0xC7, 0xBF, 0xCE, 0xBB, 0xCA, 0xC9, 0xBE])  # METAPOD
i = 0
hits = []
while True:
    i = ag.find(pat, i + 1)
    if i < 0:
        break
    hits.append(i)
print(f'METAPOD text hits: {len(hits)}')
for h in hits[:8]:
    print(f'  @{h:#x}: "{dec(h)}"')
print("givemon METAPOD (79 0b 00) in script bank:")
i = 0
while True:
    i = ag.find(b'\x79\x0b\x00', i + 1)
    if i < 0:
        break
    if 0x700000 < i < 0x8D0000:
        print(f"  @{i:#x} lvl={ag[i+3]} ctx={ag[i-4:i+10].hex(' ')}")
# Caterpie(0x0A) setwildbattle, and any special evolving party. Also search the
# 'createmon/setmondata' patterns near METAPOD text.
print("setwildbattle METAPOD (b6 0b 00):")
i = 0
while True:
    i = ag.find(b'\xb6\x0b\x00', i + 1)
    if i < 0:
        break
    if 0x700000 < i < 0x8D0000:
        print(f"  @{i:#x} lvl={ag[i+3]}")
