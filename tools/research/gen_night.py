#!/usr/bin/env python3
"""Generate f1_night.rig (v12): finish Caterpie, marathon the night scene, save forest2.ss."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n")*n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n")*n
def turn(): return "tap B 4 30\ntap B 4 30\ntap A 4 60\ntap RIGHT 4 30\ntap A 4 60\nframes 820\n"
def probe(): return "key DOWN\nframes 14\nkey -\nframes 22\nloc\nkey UP\nframes 14\nkey -\nframes 22\nloc\n"
s = "# F1 v12: finish Caterpie, marathon night scene, save forest2.ss at freedom.\nflash1m\n"
for i in range(3): s += turn()
s += "shot q1_postbattle.raw\nloc\n"
for b in range(3):
    s += apair(14) + f"shot q{b+2}_scene.raw\nloc\n" + probe()
s += apair(10) + "shot q5_late.raw\nloc\n" + probe()
s += "peek8 0x02024029\nsave forest2.ss\nlog saved\n"
open('f1_night.rig', 'w').write(s)
print('v12 ON DISK:', 'forest2.ss' in open('f1_night.rig').read(), len(s.splitlines()), 'lines')
