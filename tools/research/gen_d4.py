#!/usr/bin/env python3
"""Generate d4_use.rig — get Teachy TV via the (4,9) trigger, then menu-drive:
START -> BAG -> KEY ITEMS pocket -> USE Teachy TV. Shots at every stage."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n

s = "# D4 Teachy TV USE probe\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x02026722 1\npoke32 0x02036E00 0x08C00280\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 120\n"                      # additem ran silently
s += "tap START 4 40\nframes 40\nshot t0_menu.raw\n"
s += "tap DOWN 4 24\ntap DOWN 4 24\ntap A 4 40\nframes 60\nshot t1_bag.raw\n"
s += "tap RIGHT 4 30\nframes 40\nshot t2_keyitems.raw\n"
s += "tap DOWN 4 24\nframes 30\n"
s += "tap A 4 40\nframes 40\nshot t3_context.raw\n"
s += "tap A 4 40\nframes 240\nshot t4_used.raw\nloc\n"
s += "frames 600\nshot t5_after.raw\nloc\n"
s += "mash B 600\nframes 120\nshot t6_escape.raw\nloc\n"
open('d4_use.rig', 'w').write(s)
print('ON DISK:', 't6_escape' in open('d4_use.rig').read())
