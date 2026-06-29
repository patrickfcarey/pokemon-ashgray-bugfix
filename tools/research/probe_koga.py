#!/usr/bin/env python3
"""What selects Koga FIRST-battle (0x83fd16, gives badge) vs REMATCH (0x86eeb1, no badge)?
Climb the pointer chain from the first-battle callers to the gym-leader object script,
and find the branch variable. If it's a 0x6xxx (D1-overlapping) var, that's a real
#6a<-D1 vector: storage corruption flips Koga to rematch -> 'won, no Soul badge'."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
def u32(o): return struct.unpack('<I', ag[o:o+4])[0]
def refs(lo, hi):
    out = []
    for t in range(lo, hi):
        ptr = struct.pack('<I', t+ROM); j = -1
        while True:
            j = ag.find(ptr, j+1)
            if j < 0: break
            if 0x7F0000 <= j < 0x8D0000: out.append((j, t))
    return out

# climb: callers of the first-battle entry, then callers of THOSE blocks
print("first-battle entry 0x83fd16 referenced by:")
for j, t in refs(0x83fd16, 0x83fd17):
    print(f"  @{j:#x} -> {t:#x}")
print("\nblocks 0x83ff00-0x83ffc2 referenced by (climb toward object script):")
for j, t in refs(0x83ff00, 0x83ffc2):
    print(f"  @{j:#x} -> {t:#x}  ctx={ag[j-3:j+5].hex(' ')}")
print("\nblocks 0x840400-0x84044a referenced by:")
for j, t in refs(0x840400, 0x84044a):
    print(f"  @{j:#x} -> {t:#x}  ctx={ag[j-3:j+5].hex(' ')}")

# is the Koga gym gated on a 0x6xxx var? scan the Koga script region for 'compare var 0x6xxx'
# compare opcode 0x21: 21 [var:2] [val:2]; copyvar/setvar 0x16. find 0x6xxx var touches near Koga.
print("\n0x6xxx var touches in 0x83fc00-0x840500 (Koga script region):")
i = 0x83fc00
while i < 0x840500:
    op = ag[i]
    if op in (0x16, 0x21, 0x1A, 0x1B):   # setvar/compare/copyvar family
        var = ag[i+1] | ag[i+2] << 8
        if 0x6000 <= var < 0x7100:
            ov = u32(i+1) & 0xFFFF
            print(f"  @{i:#x} op={op:#02x} var={var:#x} (D1: sb1+{0x1000+2*(var-0x4000):#x})")
    i += 1
