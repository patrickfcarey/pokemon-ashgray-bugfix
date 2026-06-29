#!/usr/bin/env python3
"""Generate d7_real2.rig — in-situ D7 run via the (4,9) warp-trigger.
Escape Oak -> HP=1 -> arm trigger + refresh stale gMapHeader.events -> step DOWN ->
warp to 5.4 (6,8) -> Misty scene -> save d7_pc.ss + PRE dumps -> Joy (decline heal) ->
exit-line ambush -> motto -> type-9 battle -> Growl loss -> real cinematic -> POST dumps."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

DUMPS = ("peek8 0x02024029\ndump 0x02024284 0x258\n"
         "dump1 0x1000 0x200\ndump1 0xEE0 0x120\n"
         "dump1 0x3000 0x100\ndump1 0x2F00 0x100\n"
         "dump 0x0202931C 0x100\n")

s = "# D7 real-scene run v2 (script-warp)\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x020242DA 1\n"                       # Pikachu HP=1
s += "poke16 0x02026722 1\n"                       # var 0x40F7=1 (arm)
s += "poke32 0x02036E00 0x08C00280\n"              # refresh in-RAM events ptr
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 240\nloc\n"                           # warp lands 5.4 (6,8); Misty fires
s += apair(8)
s += "frames 60\nloc\nshot v1_postmisty.raw\nsave d7_pc.ss\n"
s += DUMPS
s += leg("UP", 4) + leg("RIGHT", 1) + leg("UP", 1)
s += "tap UP 4 20\ntap A 4 40\n" + apair(2)
s += "tap B 4 40\nframes 60\n" + apair(2)
s += "shot v2_postjoy.raw\nloc\n"
s += leg("DOWN", 4)
s += apair(10)
s += "shot v3_preintro.raw\n"
s += apair(14)
s += "shot v4_battle.raw\n"
for t in range(8):
    s += "tap B 4 30\n" + apair(1)
    s += "tap A 4 45\ntap RIGHT 4 30\ntap A 4 45\nframes 650\n"
s += "shot v5_postturns.raw\n"
s += apair(12)
s += "shot v6_end.raw\nloc\nframes 400\nshot v7_settle.raw\nloc\n"
s += DUMPS
s += "loc\n"
open('d7_real2.rig', 'w').write(s)
print('ON DISK:', 'v7_settle' in open('d7_real2.rig').read())
