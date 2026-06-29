#!/usr/bin/env python3
"""Generate l12_bride.rig — stage-2 loss, but ride the post-whiteout home scene with
B-pairs ONLY (B advances text but never re-engages mom). If the player then walks free,
the 'permanent lock' was my A-spam re-talking her — not a game bug. Then proceed to
the (2,7) trigger -> 3.67 -> flock-wall check (the remaining genuine L12 question)."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

s = "# L12 B-ride: is the lock my own A-spam?\nframes 30\n"
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
# whiteout: B-ONLY ride-out
s += bpair(12)
s += "frames 600\nloc\nshot r1_home.raw\n"
s += leg("DOWN", 1)
s += "shot r2_step.raw\nloc\n"
s += leg("LEFT", 6) + leg("DOWN", 1)      # -> (2,7) -> warp 3.67
s += "frames 240\nloc\nshot r3_back.raw\n"
s += leg("DOWN", 4)
s += bpair(4)
s += "shot r4_line.raw\nloc\n"
s += leg("DOWN", 2)
s += "shot r5_funnel.raw\nloc\n"
s += leg("DOWN", 2)
s += "shot r6_wall.raw\nloc\n"
s += leg("LEFT", 1) + leg("RIGHT", 2)
s += "shot r7_final.raw\nloc\n"
s += "dump1 0x10E8 2\ndump1 0x50F2 2\n"
open('l12_bride.rig', 'w').write(s)
print('ON DISK:', 'r7_final' in open('l12_bride.rig').read())
