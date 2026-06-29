#!/usr/bin/env python3
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000

# F5: the scripted chase-Spearow setwildbattle @0x822362 — is it a normal Spearow?
print('=== F5: scripted Spearow setup ===')
o = 0x822362
print(f'  @{o:#x}: {ag[o:o+7].hex(" ")}  (B6=setwildbattle species lvl item)')
sp = struct.unpack('<H', ag[o+1:o+3])[0]
print(f'  species={sp} (21=SPEAROW) level={ag[o+3]} item={struct.unpack("<H",ag[o+4:o+6])[0]}')
# outcome handler 0x886D53 checks special 0xB4 outcomes — does it handle CAUGHT (7)?
# already decompiled: outcome 7 -> 0x886E16 (flock-help). So catch is handled.

# D5: any scripted release/removemon of PIDGEOT(18=0x12)/PIDGEOTTO(17=0x11)?
print('\n=== D5: scripted Pidgeot/Pidgeotto release? ===')
# removemon doesn't exist as a clean opcode; releases use special 0x9F (release-to-wild
# storage UI) or setmondata. Search for PIDGEOT text and any 'release' special near it.
# PIDGEOT = P I D G E O T = 0xCA 0xC3 0xBE 0xC1 0xBF 0xC9 0xCE
pat = bytes([0xCA, 0xC3, 0xBE, 0xC1, 0xBF, 0xC9, 0xCE])
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/'})
def dec(o, n=60):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF:
            break
        s += cs.get(b, f'[{b:02x}]')
    return s
i = 0
hits = []
while True:
    i = ag.find(pat, i + 1)
    if i < 0:
        break
    hits.append(i)
print(f'  "PIDGEOT" (exact, not PIDGEOTTO): {len(hits)} hits')
for h in hits[:12]:
    nb = ag[h+7]
    is_otto = (nb == 0xCE and ag[h+8] == 0xC9)  # PIDGEOTTO has extra TO
    print(f'   @{h:#x}: "{dec(h)}"')
# special 0x9F = release-mon-from-storage (the "release to the wild" path)
print('\n  release special (0x9F = 9f 00 special) sites:')
i = 0
while True:
    i = ag.find(b'\x25\x9f\x00', i + 1)  # special 0x009F
    if i < 0:
        break
    if 0x7E0000 < i < 0xC11000:
        print(f'   @{i:#x}: special 0x9F  ctx={ag[i-6:i+6].hex(" ")}')
