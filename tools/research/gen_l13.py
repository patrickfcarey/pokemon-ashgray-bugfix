#!/usr/bin/env python3
"""Generate l13_gym.rig — Cerulean gym door-block round-trip at stage 0x6113==3:
expect: door blocks ("get the CASCADE BADGE from DAISY") -> Daisy gives badge ->
door lets you out to 3.3. If any leg strands, that's L13."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

s = "# L13 gym door-block round trip\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x02026722 1\n"            # lab warp trigger
s += "poke32 0x02036E00 0x08C00280\n"   # stale header refresh
s += "poke16 0x0202A75A 3\n"            # var 0x6113=3 (post-show stage), relocates
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 240\nloc\nshot k0_arrive.raw\n"
s += leg("DOWN", 1)                      # (8,17) -> exit-block trigger
s += bpair(3) + "frames 120\nloc\nshot k1_blocked.raw\n"
s += leg("UP", 12) + leg("LEFT", 1)      # to (7,4), facing Daisy at (7,3)
s += "tap UP 4 20\ntap A 4 40\n"
s += apair(8)                            # Daisy dialog + badge
s += "frames 120\nloc\nshot k2_badge.raw\ndump1 0xFE4 2\n"
s += leg("DOWN", 13)                     # back to the door, through (8,17)
s += bpair(2)
s += "frames 240\nloc\nshot k3_exit.raw\n"
s += "dump1 0x5226 2\nloc\n"
open('l13_gym.rig', 'w').write(s)
print('ON DISK:', 'k3_exit' in open('l13_gym.rig').read())
