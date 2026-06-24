#!/usr/bin/env python3
"""F3 fix — breeding-center crash after the Butch & Cassidy fight.

The post-battle daycare-return script guards against a full party with:
    0x852C5D: getpartysize
    0x852C5E: compare 0x800D, 6
    0x852C63: call_if cond=6 -> 0x852CA6   (make-room loop: party menu until size < 6)
FireRed if-conditions are 0..5; the engine tests `sScriptConditionTable[cond][result]==1`
and row 6 (out of bounds, bytes 00 00 43 here) contains no 1s — so the guard NEVER fires.
With a full party the script then force-returns the daycare Pokémon into 6/6 mons →
glitch/crash (the reported F3; same shape as D2). metapod typed the compared VALUE (6)
into the condition byte; the intent is take-when-EQUAL.

Fix: one byte — condition 6 -> 1 (EQ). Guard now runs exactly when partysize == 6.
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())
AT = 0x852C63
OLD = bytes([0x07, 0x06, 0xA6, 0x2C, 0x85, 0x08])   # call_if 6 -> 0x08852CA6
NEW = bytes([0x07, 0x01, 0xA6, 0x2C, 0x85, 0x08])   # call_if 1 (==) -> same target
assert bytes(ag[AT:AT+6]) == OLD, f'unexpected bytes @0x{AT:06X}: {bytes(ag[AT:AT+6]).hex()}'
# context guard: the compare 0x800D,6 right before
assert bytes(ag[AT-5:AT]) == bytes([0x21, 0x0D, 0x80, 0x06, 0x00]), 'compare context moved!'
ag[AT:AT+6] = NEW
open('rom/ashgray.gba', 'wb').write(ag)
print(f'F3 fixed: call_if cond 6->1 @0x{AT:06X}')
