#!/usr/bin/env python3
"""Map 3.72 person33 (a Machamp in the 'release your Pokemon for the kids' crowd) has a garbage
person-event script pointer 0x08160DDF. That script is `bufferitemname; braillemessage(0x70304308); 0xF0`
— the FIRST opcodes are VALID, so the bounds-checked script VM executes braillemessage on an open-bus
pointer; the braille text renderer (0x08002C48) infinite-loops drawing garbage glyphs that never hit a
0xFF terminator -> the overworld script task never returns -> HARD FREEZE when the player talks to it.
(Verified in-engine: the handler ran 8,000,000 steps in a pure-software glyph loop, no hardware wait,
with a garbage braille box on screen.)

FIX: repoint the person-event script pointer to NULL (file 0x7BFDC0) -> talking runs no script, exactly
like the many NULL-script scene-extra NPCs in this and other maps. Minimal 4-byte data edit; byte-guarded.

Siblings person25/29 (scripts start with 0xFF) are genuinely benign (VM stops instantly) and left as-is.
"""
import struct
ROM = 'rom/ashgray.gba'
OFF = 0x7BFDC0                      # map 3.72 events@0x7BFA98 + person33(33*24) + script(+16)
EXPECT = 0x08160DDF
data = bytearray(open(ROM, 'rb').read())
orig = struct.unpack('<I', data[OFF:OFF+4])[0]
if orig == 0:
    print('person33 fix already applied (ptr already NULL) — no change')
    raise SystemExit(0)
assert orig == EXPECT, 'GUARD: person33 script ptr @0x%06X is 0x%08X, expected 0x%08X' % (OFF, orig, EXPECT)
data[OFF:OFF+4] = struct.pack('<I', 0x00000000)
open(ROM, 'wb').write(data)
chk = struct.unpack('<I', open(ROM, 'rb').read()[OFF:OFF+4])[0]
print('person33 script ptr @file 0x%06X: 0x%08X -> 0x%08X  %s' % (OFF, orig, chk, 'OK' if chk == 0 else 'FAIL'))
