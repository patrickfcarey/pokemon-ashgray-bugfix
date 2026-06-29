#!/usr/bin/env python3
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/'})
def dec(o, n=70):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF:
            break
        s += cs.get(b, f'[{b:02x}]')
    return s
# TENTACRUEL = species 73 = 0x49. setwildbattle (b6 49 00) / dowildbattle context.
print("setwildbattle TENTACRUEL (b6 49 00):")
i = 0
while True:
    i = ag.find(b'\xb6\x49\x00', i + 1)
    if i < 0:
        break
    if 0x700000 < i < 0x8D0000:
        # check the battle type after dowildbattle: is it escapable? wild battles allow RUN.
        print(f"  @{i:#x}: lvl={ag[i+3]} item={struct.unpack('<H',ag[i+4:i+6])[0]} next={ag[i+6]:#02x} ctx={ag[i-3:i+12].hex(' ')}")
# TENTACRUEL text
pat = bytes([0xCE,0xBF,0xC8,0xCE,0xBB,0xBD,0xCC,0xCF,0xBF,0xC6])  # TENTACRUEL
i = 0
hits = []
while True:
    i = ag.find(pat, i + 1)
    if i < 0:
        break
    hits.append(i)
print(f'\nTENTACRUEL text hits: {len(hits)}')
for h in hits[:6]:
    print(f'  @{h:#x}: "{dec(h)}"')
# also TENTACOOL (species 72 = 0x48) scripted battles
print("\nsetwildbattle TENTACOOL (b6 48 00):")
i = 0
while True:
    i = ag.find(b'\xb6\x48\x00', i + 1)
    if i < 0:
        break
    if 0x700000 < i < 0x8D0000:
        print(f"  @{i:#x}: lvl={ag[i+3]}")
