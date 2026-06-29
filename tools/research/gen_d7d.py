#!/usr/bin/env python3
"""Generate d7_loss.rig — GUARANTEED-loss probe from d7_ready.ss.

Drive every turn as FIGHT -> RIGHT (cursor to Growl) -> A: Pikachu deals zero damage, so
Ekans/Koffing chip the 1-HP Pikachu down -> faint -> the type-9 loss path runs cold (no
thundershock-cinematic continuation in the test ROM, just setvar 0x40F7=3).
Outputs: screenshots through the loss text + post dumps. Calibration from the win-ish
run: flag 0x56B got set, party healed, continuation ran. If THIS run differs (flag
clear? no heal? corruption?), the delta is the loss-path signature."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n

s = "# D7 guaranteed-loss run (Growl only)\n"
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
s += "frames 600\n"
s += apair(14)                      # ride out intro + Oak lecture
s += "shot s1_postlecture.raw\n"
for t in range(8):                  # 8 Growl turns; Wrap connects long before that
    s += "tap B 4 30\n" + apair(1)
    s += "tap A 4 45\ntap RIGHT 4 30\ntap A 4 45\nframes 650\n"
    if t in (1, 3, 5):
        s += f"shot s2_turn{t}.raw\n"
s += "shot s3_postturns.raw\n"
s += apair(8)                       # faint + loss text + battle end
s += "shot s4_postloss.raw\nloc\n"
s += "frames 600\nshot s5_settle.raw\nloc\n"
s += "peek8 0x02024029\n"
s += "dump 0x02024284 0x258\n"
s += "dump1 0x1000 0x200\ndump1 0xEE0 0x120\n"
open('d7_loss.rig', 'w').write(s)
print('ON DISK:', 's5_settle' in open('d7_loss.rig').read())
