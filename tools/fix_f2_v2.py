#!/usr/bin/env python3
"""F2 fix v2 (the real one) — underwater-cave (map 1.72) black-screen crash.

Root cause (proven by headless bisection):
  Map 1.72's mapscript tables OVERLAP: type-4 (ON_WARP_INTO_MAP, runs during the black
  warp transition) reads entries [A: 0x7001->0x8527DF][B: 0x6198->0x818284]; type-2
  (ON_FRAME, runs after fade-in) starts at B. Entry B is a MSGBOX (the swim message) —
  running a textbox inside the warp transition corrupts the engine: white flash ->
  black screen, gSaveBlock1Ptr nulled, input dead. Single-arm tests: B alone crashes;
  A alone (even original, un-disarmed) is clean.

Fix: un-overlap the tables in free space —
  type-4: [A only][term]   (original 0x8527DF kept: re-runs per warp-in to set surf state)
  type-2: [B only][term]   (swim msgbox runs after fade-in, self-disarms via 0x6198=1)
and point map 1.72's header mapscripts at the rebuilt block. Also reverts the v1 edit
(once-only A variant), which was based on a wrong loop theory.
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())

# --- revert v1 (if present): entry-A pointer back to 0x8527DF, free-space script FF'd
V1_AT, V1_LEN = 0xC000B0, 14
ENTRY_P = 0x71F48F
if bytes(ag[ENTRY_P:ENTRY_P+4]) == (0x08C000B0).to_bytes(4, 'little'):
    ag[ENTRY_P:ENTRY_P+4] = bytes.fromhex('df278508')
    ag[V1_AT:V1_AT+V1_LEN] = b'\xff' * V1_LEN
    print('v1 edit reverted')
assert bytes(ag[ENTRY_P:ENTRY_P+4]) == bytes.fromhex('df278508'), 'entry A ptr unexpected'

MS  = 0xC000C0   # mapscripts block: 04 <T4> 02 <T2> 00
if bytes(ag[0x34F9FC:0x34FA00]) == (0x08000000+MS).to_bytes(4, 'little'):
    print('F2 v2 already applied (map 1.72 mapscripts already rebuilt) — no change')
    raise SystemExit(0)

# --- new structures in free space
T4  = 0xC000D0   # [01 70 00 00 | DF 27 85 08][00 00]
T2  = 0xC000E0   # [98 61 00 00 | 84 82 81 08][00 00]
HDR = 0x34F9F4   # map 1.72 header; mapscripts ptr at +8

ms  = bytes([4]) + (0x08000000+T4).to_bytes(4,'little') \
    + bytes([2]) + (0x08000000+T2).to_bytes(4,'little') + bytes([0])
t4  = bytes([0x01,0x70,0x00,0x00]) + bytes.fromhex('df278508') + bytes([0,0])
t2  = bytes([0x98,0x61,0x00,0x00]) + bytes.fromhex('84828108') + bytes([0,0])

for at, blob, name in ((MS,ms,'MS'),(T4,t4,'T4'),(T2,t2,'T2')):
    assert ag[at:at+len(blob)] == b'\xff'*len(blob), f'{name} free space not free!'
    ag[at:at+len(blob)] = blob

old_ms = bytes(ag[HDR+8:HDR+12])
assert old_ms == (0x0871F480).to_bytes(4,'little'), f'header mapscripts ptr unexpected: {old_ms.hex()}'
ag[HDR+8:HDR+12] = (0x08000000+MS).to_bytes(4,'little')

open('rom/ashgray.gba','wb').write(ag)
print(f'F2 v2: map 1.72 mapscripts -> 0x{0x08000000+MS:08X} (T4@0x{T4:06X} A-only, T2@0x{T2:06X} swim-only)')
