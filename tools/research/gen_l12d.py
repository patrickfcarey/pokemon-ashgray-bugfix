#!/usr/bin/env python3
"""Generate l12_diag.rig — stage-2 whiteout, then in-stuck-state diagnosis:
long apair ride-out, full var dumps, then live A/B pokes of the loop-suspect vars
(0x4056 morning-gate, 0x6198 chores-gate) with movement probes between.
Whiteout sb1 is deterministic: 0x0202555C."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

s = "# L12 stuck-state diagnosis\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x020242DA 1\n"
s += "poke8 0x0202661C 0x04\n"
s += "poke16 0x0202A626 2\npoke16 0x02028554 2\n"
s += "poke16 0x0202671C 1\npoke16 0x0202671E 1\npoke16 0x02026722 1\n"
s += "poke32 0x02036E00 0x08C00280\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 240\nloc\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 400\n"
s += apair(4)
for t in range(6):
    s += apair(1)
    s += "tap A 4 45\ntap RIGHT 4 30\ntap A 4 45\nframes 650\n"
# whiteout -> ride out generously
s += apair(30)
s += "frames 600\nloc\nshot z1_ride.raw\n"
s += "dump1 0x1000 0x200\ndump1 0x5320 0x20\ndump1 0x3020 4\n"
s += leg("DOWN", 1)                       # probe 1
s += "shot z2_probe1.raw\nloc\n"
# A/B poke 1: morning gate 0x4056=1 @ 0x0202555C+0x10AC
s += "poke16 0x02026608 1\n" + apair(3) + "frames 200\n"
s += leg("DOWN", 1)                       # probe 2
s += "shot z3_probe2.raw\nloc\n"
# A/B poke 2: chores gate 0x6198=3 @ 0x0202555C+0x5330
s += "poke16 0x0202A88C 3\n" + apair(3) + "frames 200\n"
s += leg("DOWN", 1)                       # probe 3
s += "shot z4_probe3.raw\nloc\n"
s += leg("LEFT", 1) + leg("UP", 1)
s += "shot z5_final.raw\nloc\n"
open('l12_diag.rig', 'w').write(s)
print('ON DISK:', 'z5_final' in open('l12_diag.rig').read())
