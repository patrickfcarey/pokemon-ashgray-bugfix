#!/usr/bin/env python3
"""Wild-encounter level typo: map (0,17) Surf slot 2 (file 0x72BA88) reads min=35, max=30 for
STARYU (species 120) -> min>max. FRLG ChooseWildMonLevel computes range=(max-min+1) as u8, so
30-35+1 wraps to 252, yielding a too-high / wrapped wild level instead of the intended 25-30.
Species is valid (no Bad Egg / no crash), so this is a low-severity balance/cosmetic defect.
The sibling water map (0,16), byte-identical for this slot, reads min=25 (0x19) -> the correct value.

FIX: minLevel byte at file 0x72BA88: 0x23 (35) -> 0x19 (25). Byte-guarded single-byte edit.
(maxLevel 0x1E=30 and species 0x0078=120 are correct and untouched.)
"""
ROM = 'rom/ashgray.gba'; OFF = 0x72BA88; EXPECT = 0x23; NEW = 0x19
data = bytearray(open(ROM, 'rb').read())
if data[OFF] == NEW and data[OFF+1] == 0x1E and data[OFF+2] == 0x78:
    print('wild-level fix already applied — no change')
    raise SystemExit(0)
assert data[OFF] == EXPECT, 'GUARD: byte @0x%06X is 0x%02X, expected 0x%02X' % (OFF, data[OFF], EXPECT)
assert data[OFF+1] == 0x1E and data[OFF+2] == 0x78, 'GUARD: slot maxLevel/species changed (got %02X %02X)' % (data[OFF+1], data[OFF+2])
data[OFF] = NEW
open(ROM, 'wb').write(data)
print('(0,17) Surf slot2 minLevel @0x%06X: 0x%02X -> 0x%02X  (now min=25 <= max=30, STARYU)  OK' % (OFF, EXPECT, NEW))
