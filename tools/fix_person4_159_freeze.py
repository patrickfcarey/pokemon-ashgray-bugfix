#!/usr/bin/env python3
"""Map 1.59 person4 (flag-0x0953 scene NPC, gfx 0x1F) has a garbage script pointer 0x0816223D into the
erased 0x16xxxx region. The garbage decodes to commands including TWO braillemessage on wild pointers
(0x87777801, 0x00777777) -> the same braille-render-loop HARD FREEZE as person33 (that command class was
verified in-engine to infinite-loop the renderer). person4 is reachable: flag 0x0953 is an active story
flag (5 setflag / 1 clearflag sites) and map 1.59 has a valid layout, so the NPC spawns during normal play.
(Reachability is strongly inferred from the flag/map data; not in-engine confirmed, as warpto can't
faithfully spawn scene NPCs in this map.)

FIX: NULL the person-event script pointer (file 0x74078C), like person33 and the game's empty-script NPCs.
Byte-guarded 4-byte edit. Adjacent person0 (script 0x162226) is also garbage but stops before any deref
command (benign, like the 0xFF-first dangling scripts) -> left as-is.
"""
import struct
ROM = 'rom/ashgray.gba'; OFF = 0x74078C; EXPECT = 0x0816223D
data = bytearray(open(ROM, 'rb').read())
orig = struct.unpack('<I', data[OFF:OFF+4])[0]
if orig == 0:
    print('person4 fix already applied (ptr already NULL) — no change')
    raise SystemExit(0)
assert orig == EXPECT, 'GUARD: 0x%06X is 0x%08X, expected 0x%08X' % (OFF, orig, EXPECT)
data[OFF:OFF+4] = struct.pack('<I', 0)
open(ROM, 'wb').write(data)
print('1.59 person4 script ptr @0x%06X: 0x%08X -> 0x00000000  OK' % (OFF, orig))
