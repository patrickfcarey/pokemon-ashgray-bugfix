#!/usr/bin/env python3
"""F2 fix — underwater-cave (map 1.72) black-screen crash.

Map 1.72's on-frame table (@0x71F48B, reached after the raft-splinter warpsilent from
the New Island crossing) contains:
    var 0x7001 == 0  ->  0x8527DF:  setvar 0x4056,0x140 ; special 0x161 ; end
The script NEVER sets var 0x7001, so while that (aliased, often-zero) var reads 0 it
re-runs EVERY FRAME — `special 0x161` (surf/QL state) fired ~60x/s corrupts the game
within seconds: reproduced headlessly as white flash -> black screen, gSaveBlock1Ptr
nulled, input dead (the reported F2 freeze). Its sibling entry (var 0x6198 -> swim
message script 0x818284) correctly disarms itself with `setvar 0x6198,1`.

Fix: repoint the entry to a free-space script that does the SAME work once, then
disarms itself exactly like its sibling:
    setvar 0x4056,0x140 ; special 0x161 ; setvar 0x7001,1 ; end
(Nothing in the ROM compares 0x4056==320, and this is the only 0x7001 frame entry,
so the change is local. Verified by scan.)
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())

NEW_AT  = 0xC000B0                       # free space (0xFF region after T2a's string)
ENTRY_P = 0x71F48F                       # frame-table entry's script-pointer field
OLD_PTR = bytes.fromhex('df278508')      # 0x088527DF
NEW_PTR = (0x08000000 + NEW_AT).to_bytes(4, 'little')

script = bytes([
    0x16, 0x56, 0x40, 0x40, 0x01,        # setvar 0x4056, 0x0140
    0x25, 0x61, 0x01,                    # special 0x161
    0x16, 0x01, 0x70, 0x01, 0x00,        # setvar 0x7001, 0x0001  (disarm)
    0x02,                                # end
])

assert ag[NEW_AT:NEW_AT+len(script)] == b'\xff'*len(script), 'free space not free!'
assert bytes(ag[ENTRY_P:ENTRY_P+4]) == OLD_PTR, 'frame-table entry not as expected!'
assert bytes(ag[0x71F48B:0x71F48F]) == bytes([0x01,0x70,0x00,0x00]), 'entry var/val moved!'

ag[NEW_AT:NEW_AT+len(script)] = script
ag[ENTRY_P:ENTRY_P+4] = NEW_PTR
open('rom/ashgray.gba', 'wb').write(ag)
print(f'F2 fixed: frame entry @0x71F48B now -> 0x{0x08000000+NEW_AT:08X}')
print(f'  new script: {script.hex()}')
