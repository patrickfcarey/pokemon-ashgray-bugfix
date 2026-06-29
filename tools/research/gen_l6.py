#!/usr/bin/env python3
"""L6 repro: escape Oak's speech, set 6 badge flags (0x820-0x825), open the trainer card."""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n
s = "# L6 6-badge trainer-card check\nframes 30\n"
s += apair(9)                       # finish Pokedex speech
s += "tap DOWN 4 20\n" + bpair(2)   # disengage from Oak
s += "frames 30\nloc\n"
s += "poke8 0x02026518 0x3F\n"       # badges 0x820-0x825 (6) at sb1(0x02025534)+0xFE4
s += "tap START 4 40\nframes 30\nshot l6_menu.raw\n"
# trainer card is the player-name entry; screenshot menu first to confirm position
s += "tap DOWN 4 16\ntap DOWN 4 16\ntap DOWN 4 16\nframes 16\nshot l6_cursor.raw\n"
s += "tap A 4 60\nframes 100\nshot l6_card.raw\n"
open('l6_badges.rig','w').write(s)
print('ON DISK:', 'l6_card' in open('l6_badges.rig').read())
