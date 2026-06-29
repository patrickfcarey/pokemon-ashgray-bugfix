#!/usr/bin/env python3
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
pat = bytes([0xCD, 0xBB, 0xC0, 0xBB, 0xCC, 0xC3])  # SAFARI (S A F A R I)
hits = []
i = 0
while True:
    i = ag.find(pat, i + 1)
    if i < 0:
        break
    hits.append(i)
print(f'"SAFARI" occurrences: {len(hits)}; first few: {[hex(h) for h in hits[:8]]}')
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xAE: '-', 0xB4: ',', 0xAC: '!', 0xF0: ':'})
def dec(o, n=44):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF:
            break
        s += cs.get(b, f'[{b:02x}]')
    return s
for h in hits[:6]:
    print(f'  @{h:#x}: "{dec(h)}"')
# Safari step special: FR uses var 0x4020-ish + special. Find "step" counter special.
# The Safari gate: search the SAFARI ZONE GATE text and a "500 steps"/ball count.
