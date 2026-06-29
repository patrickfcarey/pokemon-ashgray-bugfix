#!/usr/bin/env python3
"""Generate d7_real3.rig — from d7_pc.ss (5.4 @(6,8), HP=1, both triggers armed).
Joy: decline heal with deterministic timing. Then DOWN to (7,7): MISTY fires first
(0x5025==0 outranks the ambush on the same tile); ride it out; step off + back on ->
TR AMBUSH -> motto -> type-9 battle -> Growl loss -> real cinematic -> POST dumps."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

DUMPS = ("peek8 0x02024029\ndump 0x02024284 0x258\n"
         "dump1 0x1000 0x200\ndump1 0xEE0 0x120\n"
         "dump1 0x3000 0x100\ndump1 0x2F00 0x100\n"
         "dump 0x0202931C 0x100\n")

s = "# D7 real-scene v3 (Joy-decline, Misty pass, ambush)\nframes 180\nloc\n"
s += "dump 0x02024284 0x60\n"
s += leg("UP", 4) + leg("RIGHT", 1)
s += "tap UP 4 20\ntap A 4 40\n"
s += apair(1)
s += "frames 260\n"
s += "tap DOWN 4 24\ntap A 4 30\n"
s += apair(1) + "frames 60\n"
s += "shot j1_postjoy.raw\nloc\ndump1 0x3000 0x70\n"
s += "poke16 0x020242DA 1\n"
s += leg("DOWN", 3)
s += apair(8)
s += "shot j2_postmisty.raw\nloc\ndump1 0x3000 0x70\n"
s += leg("UP", 1) + leg("DOWN", 1)
s += apair(10)
s += "shot j3_motto.raw\n"
s += apair(14)
s += "shot j4_battle.raw\n"
for t in range(8):
    s += "tap B 4 30\n" + apair(1)
    s += "tap A 4 45\ntap RIGHT 4 30\ntap A 4 45\nframes 650\n"
s += "shot j5_postturns.raw\n"
s += apair(12)
s += "shot j6_end.raw\nloc\nframes 400\nshot j7_settle.raw\nloc\n"
s += DUMPS
s += "loc\n"
open('d7_real3.rig', 'w').write(s)
print('ON DISK:', 'j7_settle' in open('d7_real3.rig').read())
