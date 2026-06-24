#!/usr/bin/env python3
"""L10 — "Can't get on/off the bike in certain outdoor areas" (metapod23's own bug list).

Same class as L4: the map editor zeroed header bytes — this time +0x18 (bikingAllowed).
16 vanilla-region maps lost biking permission vanilla FireRed had. Restore by value-copy
from the base ROM, exactly like fix_l4.py did for the +0x19 run/escape/name flags.
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())
fr = open('base/firered.gba', 'rb').read()
ROM = 0x08000000

def pf(d, o):
    v = d[o] | d[o+1] << 8 | d[o+2] << 16 | d[o+3] << 24
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

def plist(d, off, cap):
    r = []
    for i in range(cap):
        p = pf(d, off + 4*i)
        if p is None: break
        r.append(p)
    return r

banks = plist(ag, pf(ag, 0x5524C), 64)
n = 0
for b, bt in enumerate(banks):
    for m, h in enumerate(plist(ag, bt, 200)):
        if h is None or not (0x340000 <= h < 0x360000):
            continue
        if fr[h+0x18] == 1 and ag[h+0x18] == 0:
            ag[h+0x18] = 1
            n += 1
assert n == 16, f'expected 16 maps, found {n}'
open('rom/ashgray.gba', 'wb').write(ag)
print(f'L10 fixed: bikingAllowed restored on {n} maps')
