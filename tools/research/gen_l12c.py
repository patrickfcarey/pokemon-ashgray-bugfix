#!/usr/bin/env python3
"""Generate l12_stage2.rig — whiteout at stage 2 (post-win state), then re-entry:
expect the flock row to wall the funnel at y=51 (flags not reset by the handler).
All pokes pre-warp at old sb1 0x02025534 (everything relocates; proven to +0x5400):
  +0x10E8 = 0x04   flag 0x1041 CLEAR (flock visible), 0x1042 SET (Spearow hidden)
  +0x50F2 = 2      var 0x6079 (stage 2)
  +0x3020 = 2      var 0x5010
  +0x11E8 = 1      var 0x40F4 (3.67 battle trigger arm)
  +0x11EA = 1      var 0x40F5 (house return trigger arm)
  +0x11EE = 1      var 0x40F7 (lab warp trigger arm)"""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

s = "# L12 stage-2 whiteout repro\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x020242DA 1\n"            # Pikachu HP=1
s += "poke8 0x0202661C 0x04\n"          # flags: flock visible / Spearow hidden
s += "poke16 0x0202A626 2\n"            # 0x6079=2
s += "poke16 0x02028554 2\n"            # 0x5010=2
s += "poke16 0x0202671C 1\n"            # 0x40F4 battle trigger
s += "poke16 0x0202671E 1\n"            # 0x40F5 house trigger
s += "poke16 0x02026722 1\n"            # 0x40F7 lab trigger
s += "poke32 0x02036E00 0x08C00280\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 240\nloc\nshot y0_arrive.raw\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"   # (15,46) battle
s += "frames 400\nshot y1_battle.raw\n"
s += apair(4)
for t in range(6):
    s += apair(1)
    s += "tap A 4 45\ntap RIGHT 4 30\ntap A 4 45\nframes 650\n"
s += apair(8)
s += "frames 400\nloc\nshot y2_home.raw\n"
s += leg("DOWN", 1)                      # house (8,6) -> warp back
s += "frames 240\nloc\nshot y3_back.raw\n"
s += leg("DOWN", 5)                      # toward the funnel; expect block at y<=50
s += "shot y4_wall.raw\nloc\n"
s += leg("DOWN", 2)
s += "shot y5_wall2.raw\nloc\n"
s += "tap DOWN 4 20\ntap A 4 40\n" + apair(2)   # try talking to the wall birds
s += "shot y6_talk.raw\nloc\n"
s += leg("LEFT", 2) + leg("RIGHT", 4)
s += "shot y7_probe.raw\nloc\n"
s += "dump1 0x10E8 2\ndump1 0x50F2 2\ndump1 0x3020 2\n"
open('l12_stage2.rig', 'w').write(s)
print('ON DISK:', 'y7_probe' in open('l12_stage2.rig').read())
