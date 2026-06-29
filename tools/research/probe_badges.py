#!/usr/bin/env python3
"""#6a hard audit: every setflag/clearflag/checkflag of badge flags 0x820-0x827.
Failure modes that produce "6 won shows 5":
  (a) a badge flag with ZERO setters  -> unobtainable legitimately
  (b) two gyms set the SAME flag       -> 6 wins = 5 distinct flags
  (c) a badge flag gets CLEARED somewhere after being earned
setflag=0x29, clearflag=0x2A, checkflag=0x2B; operand = 2-byte flag LE."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/', 0xFB: '|'})
def dec(o, n=40):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF: break
        s += cs.get(b, f'[{b:02x}]')
    return s
BADGE = {0x820:'Boulder',0x821:'Cascade',0x822:'Thunder',0x823:'Rainbow',
         0x824:'Soul',0x825:'Marsh',0x826:'Volcano',0x827:'Earth'}
OPS = {0x29:'setflag', 0x2A:'clearflag', 0x2B:'checkflag'}

# collect by (op, flag)
from collections import defaultdict
hits = defaultdict(list)
for op, opname in OPS.items():
    for fid in BADGE:
        pat = bytes([op, fid & 0xFF, (fid >> 8) & 0xFF])
        i = -1
        while True:
            i = ag.find(pat, i + 1)
            if i < 0: break
            if 0x7F0000 <= i < 0x8D0000:        # script bank
                hits[(opname, fid)].append(i)

for opname in ('setflag','clearflag','checkflag'):
    print(f"\n===== {opname} badge flags =====")
    for fid, name in BADGE.items():
        sites = hits[(opname, fid)]
        flag = ''
        if opname == 'setflag' and len(sites) == 0: flag = '   <<< NO SETTER (unobtainable!)'
        if opname == 'clearflag' and len(sites) > 0: flag = '   <<< CLEARED somewhere!'
        print(f"  0x{fid:03x} {name:8s}: {len(sites):2d} site(s) {[hex(s) for s in sites[:8]]}{flag}")

# show context for every SETTER so we can eyeball which gym (collision detection)
print("\n===== setter context (which script awards each badge) =====")
for fid, name in BADGE.items():
    for s in hits[('setflag', fid)]:
        # peek nearby text pointer to identify the scene
        print(f"  0x{fid:03x} {name:8s} setter @{s:#x}  ctx={ag[s-6:s+6].hex(' ')}")
