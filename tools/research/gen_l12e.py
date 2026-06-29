#!/usr/bin/env python3
"""Generate l12_final.rig — stage-2 loss with the house trigger SAFELY at (2,7):
1) confirm the home scene completes (no hang = previous hang was my (8,6) trigger);
2) walk to (2,7) -> warp back to 3.67;
3) walk down the funnel: check the un-reset flock (flags 0x1041/0x1042) walls y=51."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

s = "# L12 final: stage-2 loss, clean return, flock-wall check\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x020242DA 1\n"
s += "poke8 0x0202661C 0x04\n"            # post-win flags: flock visible, Spearow hidden
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
s += apair(14)                             # whiteout + mom-heal + home scene, generous
s += "frames 600\nloc\nshot q1_home.raw\n"
s += leg("DOWN", 1)                        # (8,5)->(8,6): free now (no trigger there)
s += leg("LEFT", 6) + leg("DOWN", 1)       # -> (2,7) trigger -> warp 3.67
s += "frames 240\nloc\nshot q2_back.raw\n"
s += leg("DOWN", 4)                        # toward funnel (15,49)
s += apair(6)                              # any scene
s += "shot q3_line.raw\nloc\n"
s += leg("DOWN", 2)                        # try to pass y=50/51 (flock wall?)
s += "shot q4_wall.raw\nloc\n"
s += leg("DOWN", 2)
s += "shot q5_wall2.raw\nloc\n"
s += "tap DOWN 4 20\ntap A 4 40\n" + apair(2)
s += "shot q6_talk.raw\nloc\n"
s += leg("LEFT", 1) + leg("RIGHT", 2) + leg("DOWN", 1)
s += "shot q7_final.raw\nloc\n"
s += "dump1 0x10E8 2\ndump1 0x50F2 2\n"
open('l12_final.rig', 'w').write(s)
print('ON DISK:', 'q7_final' in open('l12_final.rig').read())
