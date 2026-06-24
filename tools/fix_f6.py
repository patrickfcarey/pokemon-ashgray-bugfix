#!/usr/bin/env python3
"""F6 fix — Tangelo Island crash through the back of a building.

Root cause: the custom Tangelo building (map 33.2) kept vanilla map 33.3's back-door
warp (warp#1 @(1,6) -> 33.3 warpId 0), but Ash Gray's build FREED vanilla 33.3's layout
data (0x2D5998–0x2D5AFC now 0xFF: the 15x10 block data + the layout struct itself) and
nulled its mapscripts pointer. Warping there loads a 0xFFFFFFFF-dimension map -> crash.
Confirmed: that warp event is the ONLY route into 33.3 (no other warp events, no script
warp commands).

Fix: redirect 33.2's back-door warp to the island outside the building's front door
(map 3.13, warpId 1) — stepping out the back now puts you safely outside instead of
crashing. 3 bytes in the warp struct @0x73101C (destWarpId, mapNum, mapGroup).
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())
W = 0x73101C
OLD = bytes([0x01,0x00, 0x06,0x00, 0x04, 0x00, 0x03, 0x21])  # x=1 y=6 elev=4 warpId=0 -> map 33.3
NEW = bytes([0x01,0x00, 0x06,0x00, 0x04, 0x01, 0x0D, 0x03])  # same pos -> map 3.13 warpId 1
assert bytes(ag[W:W+8]) == OLD, f'warp struct unexpected: {bytes(ag[W:W+8]).hex()}'
ag[W:W+8] = NEW
open('rom/ashgray.gba', 'wb').write(ag)
print(f'F6 fixed: 33.2 back door @0x{W:06X} now -> map 3.13 warpId 1 (island, front of building)')
