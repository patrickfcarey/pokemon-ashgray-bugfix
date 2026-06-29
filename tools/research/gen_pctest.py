#!/usr/bin/env python3
"""Generate pc_test.rig: bedroom checkpoint -> PC at (1,1) -> use -> exit -> walk away
-> check for lingering message box."""
def leg(d, n): return (f"key {d}\nframes 5\nkey -\nframes 12\n") + (f"key {d}\nframes 14\nkey -\nframes 22\n")*n + "loc\n"
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n")*n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n")*n
s = "# PC message-stays-open test\nflash1m\npoke16 0x020265E4 1\npoke8 0x02026618 0x40\n"
for d, n in [("LEFT",2),("UP",1),("LEFT",2),("UP",1),("LEFT",1),("UP",2)]:
    s += leg(d, n)
s += "key UP\nframes 8\nkey -\nframes 12\n"
s += "tap A 4 40\n" + apair(2) + "shot pc1_open.raw\nloc\n"
s += bpair(4) + "shot pc2_exited.raw\nloc\n"
s += leg("DOWN", 2)
s += "shot pc3_after.raw\nloc\n"
open('pc_test.rig', 'w').write(s)
print('ON DISK:', 'pc3_after' in open('pc_test.rig').read())
