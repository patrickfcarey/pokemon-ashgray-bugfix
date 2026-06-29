#!/usr/bin/env python3
"""Generate d7_faint.rig — run on tvtest/d7_test.gba with pikachu.ss preloaded.

Flow: finish Oak's Pokedex speech (9 A-pairs), disengage (DOWN + 2 B-pairs), dump party
+ vars + flags (PRE), set Pikachu HP=1, arm trigger var 0x40F7=1, step DOWN onto (4,9)
-> trainerbattle 9 (trainer 107, Ekans+Koffing lv5). Pick a move, get hit, faint, mash
through the loss. Dump everything again (POST). Diff tells us if the loss path corrupts
the party (D1 Bad Eggs) or flags/vars (D7 obedience).

pikachu.ss fixed addresses (sb1=0x02025534 pre-battle):
  var 0x40F7   = 0x02026722   (sb1+0x1000+2*0xF7)
  party count  = 0x02024029
  party slot0  = 0x02024284   (HP u16 @ +0x56 = 0x020242DA)
  flag 0x56B   = 0x020264C1 bit3 (trainer 107 defeated)
"""
def apair(n): return ("key A\nframes 220\nkey -\nframes 10\ntap A 4 14\n") * n
def bpair(n): return ("key B\nframes 220\nkey -\nframes 10\ntap B 4 14\n") * n

s = "# D7 faint test: trainerbattle 9 loss-path corruption probe\nframes 30\n"
# escape the Pokedex speech (documented recipe)
s += apair(9)
s += "tap DOWN 4 20\n" + bpair(2)
s += "frames 30\nloc\nshot d7_pre.raw\n"
# PRE dumps
s += "peek8 0x02024029\npeek8 0x020264C1\n"
s += "dump 0x02024284 0x258\n"
s += "dump1 0x1000 0x200\ndump1 0xEE0 0x120\n"
# arm: HP=1, trigger var=1, refresh stale in-RAM gMapHeader.events (savestate predates
# the ROM-side events repoint; trigger lookups go through the RAM copy @0x02036DFC+4)
s += "poke16 0x020242DA 1\npoke16 0x02026722 1\npoke32 0x02036E00 0x08C00280\n"
# step onto (4,9)
s += "tap DOWN 4 12\nkey DOWN\nframes 20\nkey -\nframes 30\nloc\n"
# battle intro (sprites + intro text), then rounds: FIGHT -> move 1
s += "mash B 700\nshot d7_battle1.raw\n"
for i in range(5):
    s += "tap B 4 30\ntap B 4 30\ntap A 4 60\ntap A 4 60\nframes 500\n"
s += "shot d7_faint.raw\n"
# clear loss text / end-of-battle
s += "mash B 1200\nframes 120\n"
# POST dumps
s += "loc\nshot d7_post.raw\n"
s += "peek8 0x02024029\n"
s += "dump 0x02024284 0x258\n"
s += "dump1 0x1000 0x200\ndump1 0xEE0 0x120\n"
open('d7_faint.rig', 'w').write(s)
print('ON DISK:', 'd7_post' in open('d7_faint.rig').read())
