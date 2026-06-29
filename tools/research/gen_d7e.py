#!/usr/bin/env python3
"""Generate d7_real.rig — FULL in-situ D7 scene on tvtest/d7_real.gba + pikachu.ss.

Escape Oak -> disarm lab-exit triggers (var 0x7000=2) -> poke Pikachu HP=1 -> walk out
the lab door (redirected to Viridian PC 5.4 warp0) -> Misty entry scene -> PRE dumps ->
talk to Joy, DECLINE heal (0x5030 armed anyway) -> walk into the exit trigger line ->
TR ambush -> motto -> type-9 battle -> Growl-only loss -> REAL thundershock cinematic
-> POST dumps. Party stays at fixed 0x02024284; saveblock dumps via dump1 (sb1 moves)."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

DUMPS = ("peek8 0x02024029\ndump 0x02024284 0x258\n"
         "dump1 0x1000 0x200\ndump1 0xEE0 0x120\n"
         "dump1 0x3000 0x100\ndump1 0x2F00 0x100\n"
         "deref 0x03005010 0 32\n")

s = "# D7 real-scene run\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x0202C534 2\n"          # var 0x7000=2 (disarm lab-exit intercept)
s += "poke16 0x020242DA 1\n"          # Pikachu HP=1
s += leg("DOWN", 2) + leg("RIGHT", 8) + leg("UP", 4) + leg("LEFT", 1)
s += "frames 150\nloc\n"              # door warp -> 5.4 (6,8); Misty scene auto-fires
s += apair(8)
s += "frames 60\nloc\nshot v1_postmisty.raw\nsave d7_pc.ss\n"
s += DUMPS
s += leg("UP", 4) + leg("RIGHT", 1) + leg("UP", 1)
s += "tap UP 4 20\ntap A 4 40\n" + apair(2)
s += "tap B 4 40\nframes 60\n" + apair(2)
s += "shot v2_postjoy.raw\nloc\n"
s += leg("DOWN", 4)                   # crosses (7,7) -> AMBUSH
s += apair(10)                        # intro + motto + steal text
s += "shot v3_preintro.raw\n"
s += apair(14)                        # battle intro + Joy lecture
s += "shot v4_battle.raw\n"
for t in range(8):
    s += "tap B 4 30\n" + apair(1)
    s += "tap A 4 45\ntap RIGHT 4 30\ntap A 4 45\nframes 650\n"
s += "shot v5_postturns.raw\n"
s += apair(12)                        # faint + loss + cinematic + blastoff
s += "shot v6_end.raw\nloc\nframes 400\nshot v7_settle.raw\nloc\n"
s += DUMPS
s += "loc\n"
open('d7_real.rig', 'w').write(s)
print('ON DISK:', 'v7_settle' in open('d7_real.rig').read())
