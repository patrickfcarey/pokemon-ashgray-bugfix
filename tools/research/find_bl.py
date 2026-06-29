#!/usr/bin/env python3
"""Find every direct Thumb BL to a target function, alignment-independent (encode-and-match)."""
import sys
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
def bl_to(T):
    Tf = T - 0x08000000          # caller addresses below are file offsets
    out = []
    for A in range(0, 0x200000, 2):
        off = Tf - (A + 4)
        if off < -(1 << 22) or off >= (1 << 22): continue
        o = off & 0x7FFFFF
        h1 = 0xF000 | ((o >> 12) & 0x7FF)
        h2 = 0xF800 | ((o >> 1) & 0x7FF)
        if ag[A] == (h1 & 0xFF) and ag[A+1] == (h1 >> 8) and ag[A+2] == (h2 & 0xFF) and ag[A+3] == (h2 >> 8):
            out.append(A)
    return out
if len(sys.argv) > 1:
    targets = [('target', int(sys.argv[1], 16))]
else:
    targets = [('SetUpScrollToBox', 0x8091514), ('boxstep_helper', 0x80916f4)]
for name, T in targets:
    c = bl_to(T)
    print(f'{name} @{T:#x}: {len(c)} BL callers')
    for a in c[:40]:
        print(f'   from 0x{a+0x08000000:08x}')
