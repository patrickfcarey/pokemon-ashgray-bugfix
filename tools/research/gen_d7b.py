#!/usr/bin/env python3
"""Generate d7_setup.rig (make d7_ready.ss: speech escaped, HP=1, trigger armed, header
poked, saved BEFORE the step) and d7_probe.rig (step onto trigger, then diagnose the
stalled FIRST_BATTLE lecture: no-input wait vs A-mash vs B-mash vs long idle vs spaced
taps — distinguishes hard-freeze / input-wait / timer-wait)."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n

s = "# D7 setup -> d7_ready.ss\nframes 30\n"
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\n"
s += "poke16 0x020242DA 1\npoke16 0x02026722 1\npoke32 0x02036E00 0x08C00280\n"
s += "save d7_ready.ss\nloc\n"
open('d7_setup.rig', 'w').write(s)

p = "# D7 probe: step + diagnose lecture stall\n"
p += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
p += "frames 900\nshot p1_noinput.raw\n"
p += "mashA 600\nshot p2_masha.raw\n"
p += "mash B 600\nshot p3_mashb.raw\n"
p += "frames 1800\nshot p4_idle.raw\n"
p += ("tap A 4 240\n") * 5 + "shot p5_taps.raw\n"
p += "loc\ndump1 0x1000 0x10\n"
open('d7_probe.rig', 'w').write(p)
print('ON DISK:', 'p5_taps' in open('d7_probe.rig').read(), 'd7_ready' in open('d7_setup.rig').read())
