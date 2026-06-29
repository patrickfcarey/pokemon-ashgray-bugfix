#!/usr/bin/env python3
"""Are the high (0x74xx+) 'story vars' real, or pointer-byte noise?
A real `setvar VID, VAL` is `16 [vid:2] [val:2]` with VAL small (story stages 0-~50).
A false positive is `16 50 85 08 ...` = the low bytes of a pointer 0x08855016, so the
byte at +3 is 0x08 (pointer high byte) → 'val' looks huge. Check each high var's sites."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
LO, HI = 0x800000, 0x8D0000

def collect(op):
    s = set()
    for i in range(LO, HI - 3):
        if ag[i] == op:
            vid = struct.unpack('<H', ag[i+1:i+3])[0]
            if 0x4100 <= vid <= 0x9000:
                s.add(vid)
    return s

real = sorted(collect(0x16) & collect(0x21))
# storage-overlap threshold and high band
hi_vars = [v for v in real if v >= 0x7400]   # beyond the confirmed 0x60xx/0x70xx clusters
print(f'vars >= 0x7400 that passed set∩compare: {[hex(v) for v in hi_vars]}')
print()
for v in hi_vars:
    pat = bytes([0x16, v & 0xFF, v >> 8])
    real_site = False
    samples = []
    i = LO
    while i < HI - 5:
        if ag[i:i+3] == pat:
            val = struct.unpack('<H', ag[i+3:i+5])[0]
            nxt = ag[i+5]
            looks_ptr = (ag[i+3] == 0x08) or (ag[i+4] == 0x08) or val > 0x200
            samples.append((i, val, ag[i-1], nxt, looks_ptr))
            if not looks_ptr:
                real_site = True
        i += 1
    tag = 'REAL (has plausible setvar)' if real_site else 'NOISE (all sites pointer-like)'
    print(f'  0x{v:04X}: {tag}')
    for off, val, prev, nxt, lp in samples[:3]:
        print(f'      @{off:#x} val=0x{val:04X} prev=0x{prev:02x} next=0x{nxt:02x} {"<ptr-noise>" if lp else "<plausible>"}')
