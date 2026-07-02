#!/usr/bin/env python3
"""L4 fix — running shoes dead on many maps (reported for Pallet Town / Route 1).

Ash Gray's map editor zeroed the header flags byte (+0x19: bit0 escape, bit1 RUN,
bit2 show-map-name) on every vanilla-region map it touched — 44 maps lost the run
bit that vanilla FireRed had (Pallet Town 3.0 is the one players notice first;
Route 1 itself survived in 4.5.3). Fix: restore the vanilla +0x19 byte for exactly
the affected maps (vanilla-region headers where vanilla had run and Ash Gray lost it).
Value-copy from the base ROM — no guessed semantics.
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
        a, v = ag[h+0x19], fr[h+0x19]
        if (v & 2) and not (a & 2):
            ag[h+0x19] = v
            n += 1
if n == 0:
    print('L4: no maps needed the run-flag restore (already applied) — no change')
    raise SystemExit(0)
assert n == 44, f'expected 44 maps, found {n}'
open('rom/ashgray.gba', 'wb').write(ag)
print(f'L4 fixed: restored vanilla header flags (+0x19) on {n} maps (run/escape/map-name)')
