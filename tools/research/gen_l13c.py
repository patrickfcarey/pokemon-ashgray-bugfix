#!/usr/bin/env python3
"""Generate l13_rim.rig — rim-trap probes from the deck (land (4,18)):
A) UP onto south rim (4,17): enter? then DOWN/LEFT/RIGHT/UP probes.
B) (if mobile) LEFT to (1,18), UP the west deck to (1,8), RIGHT onto west rim (2,8),
   then retreat probes. locs after every leg tell the story."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

s = "# L13 rim probes\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x02026722 1\npoke32 0x02036E00 0x08C00280\n"
s += "poke16 0x0202A75A 1\n"             # 0x6113=1: pre-show, exit triggers dead
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 240\nloc\nshot m0_deck.raw\n"
s += leg("UP", 1)                         # probe A: onto (4,17)?
s += leg("DOWN", 1)                       # retreat?
s += leg("UP", 1) + leg("LEFT", 1) + leg("RIGHT", 1) + leg("UP", 1)
s += "shot m1_southrim.raw\nloc\n"
s += leg("DOWN", 2)                       # back to deck if possible
s += leg("LEFT", 3)                       # -> (1,18)
s += leg("UP", 10)                        # west deck col -> (1,8)
s += leg("RIGHT", 1)                      # probe B: onto (2,8)?
s += leg("LEFT", 1)                       # retreat?
s += leg("RIGHT", 1) + leg("UP", 1) + leg("DOWN", 1)
s += "shot m2_westrim.raw\nloc\n"
open('l13_rim.rig', 'w').write(s)
print('ON DISK:', 'm2_westrim' in open('l13_rim.rig').read())
