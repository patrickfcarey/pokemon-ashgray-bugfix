#!/usr/bin/env python3
"""Generate d7_run2.rig — full faint run from d7_ready.ss using HOLD-A pairs (Ash Gray
text only speeds up under held buttons; mashing is useless). 40 pairs ~= 9800 frames:
lecture pages, FIGHT->move-1 picks, Ekans hits 1-HP Pikachu, faint, loss text, battle
end. Then screenshots + full dumps (party/vars/flags) for the corruption diff."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n

s = "# D7 full faint run (hold-A driven)\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 600\n"
s += apair(40)
s += "shot r1_after40.raw\nloc\n"
s += "frames 600\nshot r2_settle.raw\nloc\n"
s += "peek8 0x02024029\n"
s += "dump 0x02024284 0x258\n"
s += "dump1 0x1000 0x200\ndump1 0xEE0 0x120\n"
open('d7_run2.rig', 'w').write(s)
print('ON DISK:', 'r2_settle' in open('d7_run2.rig').read())
