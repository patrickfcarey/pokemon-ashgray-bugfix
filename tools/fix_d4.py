#!/usr/bin/env python3
"""D4 — Teachy TV is broken ("DON'T USE IT" per metapod's own list). REPRODUCED:
using it opens the vanilla TV menu; entering a lesson plays the Poke Dude demo over a
BLACK VOID (the hack overwrote the demo's backdrop resources) — at best garbage, at
worst a soft-lock, and the author himself warns players off.

Fork-appropriate fix: neuter the field-use. gItems[0x16E].fieldUseFunc (entry +28):
ItemUseOutOfBattle_TeachyTv (0x080A18ED) -> ItemUseOutOfBattle_CannotUse (0x080A2239,
the inert handler shared by 216 items: "OAK: {rival}! This isn't the time to use
that!"). The item itself stays in the bag (story prop); it just can't brick anyone.
"""
import struct

ag = bytearray(open('rom/ashgray.gba', 'rb').read())
e = 0x3DB028 + 44 * 0x16E + 28
old = struct.unpack('<I', ag[e:e+4])[0]
assert old == 0x080A18ED, f'expected Teachy TV fieldUseFunc 0x080A18ED, got {old:#x}'
ag[e:e+4] = struct.pack('<I', 0x080A2239)
open('rom/ashgray.gba', 'wb').write(ag)
print('D4 fixed: TEACHY TV fieldUseFunc -> CannotUse (broken TV program unreachable)')
