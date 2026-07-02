#!/usr/bin/env python3
"""F4 fix — Grampa Canyon pickaxe-give softlock.

Reproduced headlessly: the rival pickaxe scene (frame script 0x89D1B1 on map 1.101,
armed by the on-transition x==10 check) plays fully through "Smell ya' later!", then
hangs forever: every exit path funnels into
    0x81508F: applymovement obj8(GARY), movm 0x8C6D70  (down x5, left, down x4)
    0x815096: waitmovement
and Gary's 12-step march collides with the dig-site path — a blocked scripted step
retries forever, waitmovement never returns, the script never releases. Screenshot
evidence: textbox closed, Gary stranded mid-route, input dead (k5).

Fix (same 10 bytes, in place): replace the colliding march + wait with an instant
departure and jump to the existing cleanup (fadedefaultbgm; setvar 0x6158,2; release):
    removeobject 8 ; goto 0x86DFFF ; nop nop
The x==15/16 pre-positioning movements (short, verified-terminated) still play first.
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())
AT = 0x81508F
OLD = bytes([0x4F, 0x08, 0x00, 0x70, 0x6D, 0x8C, 0x08,   # applymovement obj8, 0x8C6D70
             0x51, 0x08, 0x00])                          # waitmovement obj8
NEW = bytes([0x53, 0x08, 0x00,                           # removeobject 8
             0x05, 0xFF, 0xDF, 0x86, 0x08,               # goto 0x86DFFF (cleanup+release)
             0x00, 0x00])                                # nop nop (padding)
if bytes(ag[AT:AT+10]) == NEW:
    print(f'F4 already applied @0x{AT:06X} — no change')
    raise SystemExit(0)
assert bytes(ag[AT:AT+10]) == OLD, f'unexpected bytes @0x{AT:06X}: {bytes(ag[AT:AT+10]).hex()}'
ag[AT:AT+10] = NEW
open('rom/ashgray.gba', 'wb').write(ag)
print(f'F4 fixed: Gary departs instantly @0x{AT:06X}; script reaches cleanup/release')
