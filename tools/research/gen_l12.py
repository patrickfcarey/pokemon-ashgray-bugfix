#!/usr/bin/env python3
"""Generate l12_repro.rig — lose to a wild Spearow on Route 1 with the intro respawn
state live; observe where the whiteout puts us and whether we can move (wall check)."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

s = "# L12: Spearow-loss whiteout repro\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x020242DA 1\n"            # HP=1
s += "poke16 0x02026722 1\n"            # 0x40F7=1 (lab warp trigger)
s += "poke16 0x02026720 1\n"            # 0x40F6=1 (route1 battle trigger)
s += "poke32 0x02036E00 0x08C00280\n"   # stale lab header refresh
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 240\nloc\ndumpsb 64\n"     # on Route 1; lastHealLocation @ +0x1C
s += "shot w0_route1.raw\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"   # -> (8,21) battle
s += "frames 400\nshot w1_battle.raw\n"
s += apair(4)
for t in range(6):                       # Growl-only turns, no B (wild battle: B->RUN risk)
    s += apair(1)
    s += "tap A 4 45\ntap RIGHT 4 30\ntap A 4 45\nframes 650\n"
s += "shot w2_postturns.raw\nloc\n"
s += apair(8)                            # faint + whiteout + mom-handler texts
s += "frames 600\nloc\nshot w3_respawn.raw\ndumpsb 64\n"
s += apair(4) + "frames 300\nloc\nshot w4_settled.raw\n"
# movement probe: try all four directions
s += leg("UP", 1) + leg("DOWN", 1) + leg("LEFT", 1) + leg("RIGHT", 1)
s += "shot w5_probe.raw\nloc\ndump1 0x1000 0x20\n"
open('l12_repro.rig', 'w').write(s)
print('ON DISK:', 'w5_probe' in open('l12_repro.rig').read())
