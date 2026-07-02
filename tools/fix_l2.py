#!/usr/bin/env python3
"""L2 fix — full party + talk to Prof Oak blocks the league departure.

On league day (0x6192==4, 0x7012==5) Oak gives back the Pokémon he was watching and
ONLY the success path delivers the send-off ("Now get going…") + `setvar 0x7013,1`
(the league-departure progression state). The full-party branch says "You can't take
this POKéMON back if you've got no room for it" and `goto 0x8216DF` (menu top) —
0x7013 is never set, the next event never triggers (the reported L2 stall).

Fix: repoint that goto to a free-space stub that keeps Oak's refusal (the mon stays
with him; the existing 0x6192==4 "Would you like it back?" flow remains for later
pickup) but still plays the send-off and sets the progression var:
    loadword 0, "Now get going…" (existing text 0x87201E) ; callstd 2 ;
    setvar 0x7013,1 ; release ; end
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())

STUB = 0xC00140
GOTO = 0x871ED1
stub = bytes([0x0F, 0x00, 0x1E, 0x20, 0x87, 0x08,   # loadword 0, 0x0887201E
              0x09, 0x02,                           # callstd 2
              0x16, 0x13, 0x70, 0x01, 0x00,         # setvar 0x7013, 1
              0x6C,                                 # release
              0x02])                                # end
if bytes(ag[GOTO:GOTO+5]) == bytes([0x05]) + (0x08000000+STUB).to_bytes(4, 'little'):
    print('L2 already applied (no-room branch already goes to the stub) — no change')
    raise SystemExit(0)
assert ag[STUB:STUB+len(stub)] == b'\xff'*len(stub), 'free space not free!'
assert bytes(ag[GOTO:GOTO+5]) == bytes([0x05, 0xDF, 0x16, 0x82, 0x08]), \
    f'goto bytes unexpected: {bytes(ag[GOTO:GOTO+5]).hex()}'
# context: the refusal msgbox right before (loadword @0x871EC9, callstd 4 @0x871ECF)
assert ag[GOTO-2] == 0x09 and ag[GOTO-1] == 0x04, 'refusal callstd context moved!'

ag[STUB:STUB+len(stub)] = stub
ag[GOTO:GOTO+5] = bytes([0x05]) + (0x08000000+STUB).to_bytes(4, 'little')
open('rom/ashgray.gba', 'wb').write(ag)
print(f'L2 fixed: no-room branch now sends the player off (0x7013=1); mon stays with Oak')
