#!/usr/bin/env python3
"""Generate l12_loop.rig — real-scene Spearow loss + post-loss re-entry probe."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

s = "# L12 full loop: real scene loss + re-entry\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x020242DA 1\n"            # HP=1
s += "poke16 0x02026722 1\n"            # 0x40F7 lab trigger
s += "poke16 0x0202671E 1\n"            # 0x40F5 house trigger (survives relocation)
s += "poke32 0x02036E00 0x08C00280\n"
s += "poke16 0x0202A626 0\n"            # 0x6079=0 at CURRENT sb1 (deep-alias)
s += "poke16 0x0202A666 0\n"            # 0x6079=0 at FUTURE sb1 (0x02025574+0x50F2):
                                        # deep region doesn't relocate; ON_TRANSITION
                                        # reads it before any post-arrival poke could land
s += "poke16 0x02028554 0\n"            # 0x5010=0 (inside sb1, relocates fine)
# scene object flags alias INTO sb1 (+0x10E8) and relocate with it: set BEFORE warp.
# canonical pre-scene state: flag 0x1041 SET (flock hidden), 0x1042 CLEAR (Spearow visible)
s += "poke8 0x0202661C 0x02\npeek8 0x0202661C\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 240\nloc\nshot x0_arrive.raw\n"
s += "peek8 0x0202665C\npeek16 0x0202A666\n"   # diagnostics: flag byte + 0x6079 post-load
s += leg("DOWN", 4)                      # cross (15,49) 0x6079==0 -> scene
s += apair(10)                           # scene text/moves; battle may auto-launch
s += "shot x1_scene.raw\nloc\n"
s += "tap DOWN 4 20\ntap A 4 40\n"       # if battle needs talking to the Spearow
s += apair(4)
s += "shot x2_battle.raw\n"
for t in range(6):                       # Growl turns -> faint
    s += apair(1)
    s += "tap A 4 45\ntap RIGHT 4 30\ntap A 4 45\nframes 650\n"
s += apair(8)                            # whiteout + mom scene
s += "frames 400\nloc\nshot x3_home.raw\n"
s += leg("DOWN", 1)                      # house (8,6) -> warp back to 3.67
s += "frames 240\nloc\nshot x4_back.raw\n"
s += leg("DOWN", 4)                      # re-enter the line (0x6079=0 again, 0x5010=1)
s += apair(10)
s += "shot x5_rescene.raw\nloc\n"
s += leg("DOWN", 2) + leg("DOWN", 2)
s += "shot x6_after.raw\nloc\n"
s += leg("UP", 1) + leg("LEFT", 1) + leg("RIGHT", 1) + leg("DOWN", 1)
s += "shot x7_probe.raw\nloc\n"
s += "dump1 0x3020 0x10\ndump1 0x50F0 0x10\n"   # 0x5010 @sb1+0x3020, 0x6079 @sb1+0x50F2
open('l12_loop.rig', 'w').write(s)
print('ON DISK:', 'x7_probe' in open('l12_loop.rig').read())
