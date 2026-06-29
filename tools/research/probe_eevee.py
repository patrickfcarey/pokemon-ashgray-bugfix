#!/usr/bin/env python3
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
# givemon EEVEE: opcode 0x79 <species u16=0x85> <level> <item u16> ...
# also setwildbattle/special gifts. Search givemon (0x79) with species 133 (0x0085).
print('--- givemon EEVEE (79 85 00):')
i = 0
while True:
    i = ag.find(b'\x79\x85\x00', i + 1)
    if i < 0:
        break
    if 0x7E0000 < i < 0xC11000:
        lvl = ag[i + 3]
        print(f'  @{i:#x}: givemon EEVEE lvl={lvl} ctx={ag[i-4:i+14].hex(" ")}')
# "EEVEE" text = E E V E E = 0xBF 0xBF 0xD0 0xBF 0xBF
print('--- "EEVEE" text:')
pat = bytes([0xBF, 0xBF, 0xD0, 0xBF, 0xBF])
i = 0
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':'})
def dec(o, n=50):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF:
            break
        s += cs.get(b, f'[{b:02x}]')
    return s
hits = []
while True:
    i = ag.find(pat, i + 1)
    if i < 0:
        break
    hits.append(i)
print(f'  {len(hits)} hits; samples:')
for h in hits[:10]:
    print(f'  @{h:#x}: "{dec(h)}"')
