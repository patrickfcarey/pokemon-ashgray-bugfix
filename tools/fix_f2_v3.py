#!/usr/bin/env python3
"""F2 fix v3 (final layer) — make the swim message self-sufficient.

Proven by experiment (headless rig):
  Map 1.72's swim script prints "{PLAYER} grabbed onto the back of {STR_VAR_1}…", but
  STR_VAR_1 is only filled by the raft-splinter script. Entering the cave any other way
  prints an unterminated/garbage buffer -> text printer runs away -> black screen, dead
  game (gSaveBlock1Ptr nulled). Pre-filling the buffer in RAM made the cave + message
  work perfectly, confirming the mechanism.

Fix: repoint the (v2-rebuilt) ON_FRAME entry to a new script that guarantees the buffer:
    compare 0x8004, 6 ; if < goto buffer     ; raft script left a valid slot 0..5
    setvar 0x8004, 0                          ; otherwise clamp to lead mon
  buffer:
    bufferpartymonnick STR_VAR_1, var 0x8004  ; same call the raft path used
    loadword 0, <original swim text>
    callstd 4 ; closemessage ; setvar 0x6198,1 ; end
Legit splinter arrivals keep the exact anime behavior (named water mon); every other
entry gets the lead mon's name instead of a crash. Requires fix_f2_v2 applied (tables
un-overlapped; T2 entry @0xC000E0).
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())

NEW   = 0xC000F0                  # new swim script (free space)
T2E   = 0xC000E0                  # v2's ON_FRAME entry for var 0x6198
TEXT  = 0x08862208                # original swim string
LEGIT = 0x08000000 + NEW + 16     # skip the clamp: 5(compare)+6(goto_if)+5(setvar)=16

script = bytes([
    0x21, 0x04, 0x80, 0x06, 0x00,                      # compare 0x8004, 6
    0x06, 0x00, *LEGIT.to_bytes(4, 'little'),          # goto_if < -> legit
    0x16, 0x04, 0x80, 0x00, 0x00,                      # setvar 0x8004, 0
    # legit:
    0x7F, 0x00, 0x04, 0x80,                            # bufferpartymonnick STR_VAR_1, var 0x8004
    0x0F, 0x00, *TEXT.to_bytes(4, 'little'),           # loadword 0, swim text
    0x09, 0x04,                                        # callstd 4
    0x68,                                              # closemessage
    0x16, 0x98, 0x61, 0x01, 0x00,                      # setvar 0x6198, 1
    0x02,                                              # end
])

assert ag[NEW:NEW+len(script)] == b'\xff'*len(script), 'free space not free!'
assert bytes(ag[T2E:T2E+8]) == bytes([0x98,0x61,0x00,0x00]) + bytes.fromhex('84828108'), \
    'v2 T2 entry not as expected (apply fix_f2_v2 first)'

ag[NEW:NEW+len(script)] = script
ag[T2E+4:T2E+8] = (0x08000000+NEW).to_bytes(4, 'little')
open('rom/ashgray.gba', 'wb').write(ag)
print(f'F2 v3: swim script self-buffers; ON_FRAME entry -> 0x{0x08000000+NEW:08X} ({len(script)} bytes)')
