#!/usr/bin/env python3
"""Generate sbsize.rig — measure how much of sb1 the FR save-block shuffle copies.
Poke markers at old sb1 (0x02025534) + offsets, warp (lab trigger), read them back
via dump1 at the new sb1. Markers that survive = inside the copied struct."""
OFFS = [0x3D00, 0x3F00, 0x4500, 0x50F2, 0x5400]
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n

s = "# sb1 copy-length probe\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x02026722 1\npoke32 0x02036E00 0x08C00280\n"
for i, off in enumerate(OFFS):
    s += f"poke16 {0x02025534+off:#x} {0xAA01+i:#x}\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 240\nloc\n"
for off in OFFS:
    s += f"dump1 {off:#x} 2\n"
open('sbsize.rig', 'w').write(s)
print('ON DISK:', 'sbsize' in 'sbsize.rig' and '0x5400' in open('sbsize.rig').read())
