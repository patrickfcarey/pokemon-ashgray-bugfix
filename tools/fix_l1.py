#!/usr/bin/env python3
"""L1 fix — Indigo Plateau gate softlock.

The gate trigger (@0x869E5A, pointed to by the relocated event table @0x723A80) gated
league entry on VAR_0x7014:
    compare 0x7014,1 ; if== goto 0x8E9081   (eligibility check: exam flag 0x1202 OR 8 badges)
    compare 0x7014,2 ; if== goto 0x87FF97   ("good luck")
    goto 0x82789A                            ("...the LEAGUE hasn't begun yet")
0x7014 is only set to 1 by missable anime story events (OTOSHI etc.). A player who reaches
the gate with all badges / exam passed but without that var set is told the league hasn't
begun and can never enter — the existing eligibility check at 0x8E9081 is unreachable.

Fix: route 0x7014!=2 to that existing eligibility check instead of dead-ending. Unqualified
players still get the game's own "you don't have enough BADGES" message (from 0x8E9081); the
fix only makes the real requirement check reachable. In-place, 16 bytes, same entry pointer.
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())
AT = 0x869E5A

OLD = bytes([0x21,0x14,0x70,0x01,0x00,   # compare 0x7014, 1
             0x06,0x01,0x81,0x90,0x8E,0x08,  # goto_if ==1 -> 0x8E9081
             0x21,0x14,0x70,0x02,0x00])   # compare 0x7014, 2  (start of next cmd)
NEW = bytes([0x21,0x14,0x70,0x02,0x00,   # compare 0x7014, 2
             0x06,0x01,0x97,0xFF,0x87,0x08,  # goto_if ==1 -> 0x87FF97  ("good luck")
             0x05,0x81,0x90,0x8E,0x08])   # goto      -> 0x8E9081  (eligibility check)

cur = bytes(ag[AT:AT+len(OLD)])
if cur == NEW:
    print(f'L1 already applied @0x{AT:06X} — no change')
    raise SystemExit(0)
if cur != OLD:
    print('ABORT: bytes @0x%06X are not the expected original guard dispatch.' % AT)
    print('  expected:', OLD.hex())
    print('  found:   ', cur.hex())
    raise SystemExit(1)
assert len(NEW) == len(OLD), 'length must match for in-place edit'
ag[AT:AT+len(NEW)] = NEW
open('rom/ashgray.gba', 'wb').write(ag)
print('L1 fixed: rewrote %d bytes @0x%06X' % (len(NEW), AT))
print('  old:', OLD.hex())
print('  new:', NEW.hex())
