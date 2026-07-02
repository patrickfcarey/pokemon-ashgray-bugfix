#!/usr/bin/env python3
"""F6 fix part 2 (the real crash) — Pokémon Park entrance hall (map 33.0) void-march.

Map 33.0's on-frame entry (var 0x7035==0 -> 0x8A0E99) plays the "Thank you for visiting
POKéMON PARK" ejection: canned applymovements that walk the player out — written for the
BACK-DOOR re-entry position (5,1)/(5,2) (returning from the park, map 3.83, which arms
0x7035=0 on transition). 0x7035 is a deep-aliased var, so on fresh/unlucky saves it ALSO
reads 0 when entering through the FRONT door — the canned steps then march the player
through the wall into the void below the room: invisible, frozen, softlocked (reproduced
headlessly; the reported F6 "crash going through the back of a building").

Fix: repoint the frame entry to a wrapper that runs the ejection ONLY from the back-door
position (y < 3); any other entry just disarms the var and does nothing:
    getplayerxy ; compare 0x4001,3 ; goto_if < -> 0x8A0E99 ; setvar 0x7035,1 ; end
(fix_f6.py already sealed the unrelated dead back-warp of building 33.2.)
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())

NEW   = 0xC00120
ENTRY = 0x731B6A                                  # frame-table entry's script ptr field
ORIG  = bytes.fromhex('990e8a08')                 # 0x088A0E99

wrapper = bytes([
    0x42,                                          # getplayerxy (x->0x4000, y->0x4001)
    0x21, 0x01, 0x40, 0x03, 0x00,                  # compare 0x4001, 3
    0x06, 0x00, 0x99, 0x0E, 0x8A, 0x08,            # goto_if <  -> original ejection
    0x16, 0x35, 0x70, 0x01, 0x00,                  # setvar 0x7035, 1   (disarm, no scene)
    0x02,                                          # end
])

if bytes(ag[ENTRY:ENTRY+4]) == (0x08000000+NEW).to_bytes(4, 'little'):
    print('F6b already applied (entry repointed to the wrapper) — no change. '
                     'NOTE: this v1 wrapper is BUGGY (bare getplayerxy); fix_f6b_v2.py replaces it.')
    raise SystemExit(0)
assert ag[NEW:NEW+len(wrapper)] == b'\xff'*len(wrapper), 'free space not free!'
assert bytes(ag[ENTRY:ENTRY+4]) == ORIG, f'frame entry ptr unexpected: {bytes(ag[ENTRY:ENTRY+4]).hex()}'
assert bytes(ag[ENTRY-4:ENTRY]) == bytes([0x35,0x70,0x00,0x00]), 'entry var/val moved!'

ag[NEW:NEW+len(wrapper)] = wrapper
ag[ENTRY:ENTRY+4] = (0x08000000+NEW).to_bytes(4, 'little')
open('rom/ashgray.gba', 'wb').write(ag)
print(f'F6b fixed: 33.0 ejection gated on back-door position; entry -> 0x{0x08000000+NEW:08X}')
