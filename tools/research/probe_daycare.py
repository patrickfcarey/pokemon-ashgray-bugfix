#!/usr/bin/env python3
"""Is Ash Gray's daycare/breeding center FUNCTIONAL (can you deposit a Pokémon)?
If not, the SaveBlock1-tail overflow is moot. Search for daycare text + the FireRed
daycare specials (StorePokemonInDaycare etc.)."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/', 0xFB: '|'})
def dec(o, n=70):
    s = ''
    for b in ag[o:o+n]:
        if b == 0xFF: break
        s += cs.get(b, f'[{b:02x}]')
    return s

# daycare text: "DAY CARE" = BE BB D3 00 BD BB CC BF
for label, pat in (('DAY CARE', bytes([0xBE,0xBB,0xD3,0x00,0xBD,0xBB,0xCC,0xBF])),
                   ('DAYCARE',  bytes([0xBE,0xBB,0xD3,0xBD,0xBB,0xCC,0xBF])),
                   ('raise',    bytes([0xCC,0xD5,0xDD,0xCD,0xBF]))):  # "raise" lowercase
    i = 0; hits = []
    while True:
        i = ag.find(pat, i+1)
        if i < 0: break
        hits.append(i)
    print(f'"{label}": {len(hits)} hits')
    for h in hits[:6]:
        print(f'   @{h:#x}: "{dec(h)}"')

# FireRed daycare specials (US): StorePokemonInEmptyDaycareSlot etc. live around special
# indices 0x18B-0x19x. Search special(0x25)/specialvar(0x26) opcodes with those indices
# in the script bank, and report which are USED.
print('\n--- daycare-ish specials used in scripts (special 0x25 NN NN) ---')
from collections import Counter
spec = Counter()
i = 0x150000
while i < 0x8D0000 - 3:
    if ag[i] == 0x25:  # special
        idx = struct.unpack('<H', ag[i+1:i+3])[0]
        if 0x150 <= idx <= 0x1B0:   # rough daycare/storage special band
            spec[idx] += 1
    i += 1
for idx, n in sorted(spec.items()):
    print(f'   special 0x{idx:03X}: used {n}x')
