#!/usr/bin/env python3
"""D1 LIVE REPRO — the Spearow loop (L14) reproduced by writing to PC storage.

Var 0x6079 (chase-complete stage) physically lives at Box 3 slot 0, byte +0x46
(post-warp address 0x0202A666 = sb1 0x02025574 + 0x50F2). The "You can't leave
without PIKACHU!" barrier coord at (15,49) on map 3.67 re-checks 0x6079 every step:
fires only when 0x6079 in {0,1}, free when ==3 (chase done).

Demo (on l12b_test.gba, lab(4,9)->3.67 warp, from pikachu.ss):
  1. set 0x6079=3 (chase complete), warp to 3.67, walk south through (15,49) -> FREE.
  2. write to Box 3 slot 0 (0x0202A666 = the var's storage byte) = store a Pokemon ->
     0x6079 corrupted to 1.  step onto (15,49) -> BARRIER returns. Chase re-armed.
"""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n") * n + "loc\n"

s = "# D1 live repro: Spearow loop via PC-storage write\nframes 30\n"
s += apair(9) + "tap DOWN 4 20\n" + bpair(2) + "frames 30\nloc\n"
# chase complete: 0x6079=3 (pre-warp 0x0202A626 + post-warp 0x0202A666), arm lab trigger
s += "poke16 0x0202A626 0x0003\npoke16 0x0202A666 0x0003\n"
s += "poke16 0x02026722 1\npoke32 0x02036E00 0x08C00280\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"   # -> warp to 3.67 (15,45)
s += "frames 60\nloc\npeek16 0x0202A666\n"                           # confirm 0x6079=3 post-warp
# walk SOUTH through the barrier line (15,49) -> free passage (no Spearow, chase done)
s += leg("DOWN", 5)
s += "shot d1_free.raw\nloc\n"
# step back north off the trigger line
s += leg("UP", 3)
s += "loc\n"
# *** store a Pokemon in Box 3 slot 0: write to its storage byte -> corrupts 0x6079 ***
s += "peek16 0x0202A666\npoke16 0x0202A666 0x0001\npeek16 0x0202A666\n"
# step back south onto (15,49) -> the barrier is back
s += "key DOWN\nframes 5\nkey -\nframes 12\n" * 3
s += "key DOWN\nframes 16\nkey -\nframes 40\n"
s += "shot d1_barrier.raw\nloc\n"
open('d1repro.rig', 'w').write(s)
print('ON DISK:', 'd1_barrier' in open('d1repro.rig').read())
