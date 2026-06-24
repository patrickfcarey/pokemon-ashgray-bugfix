#!/usr/bin/env python3
"""T3 — "advance to the INIDGO PLATEAU" -> INDIGO (badge-check message @0x881FC4).
Same-length in-place letter swap; single occurrence in the ROM."""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())
ENC = {c: 0xBB+i for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}
def enc(s): return bytes(ENC[c] for c in s)
AT = 0x881FC4
assert bytes(ag[AT:AT+6]) == enc('INIDGO'), f'unexpected: {bytes(ag[AT:AT+6]).hex()}'
ag[AT:AT+6] = enc('INDIGO')
open('rom/ashgray.gba', 'wb').write(ag)
print('T3 fixed: INIDGO -> INDIGO @0x881FC4')
