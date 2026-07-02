#!/usr/bin/env python3
"""F6b v2 — repair the malformed position-gate wrapper installed by fix_f6b.py.

The v1 wrapper emitted a BARE `getplayerxy` (0x42), assuming a 1-byte implicit
form that writes x/y to 0x4000/0x4001. FireRed's getplayerxy is 5 bytes — the
handler (@0x0806B010) reads TWO var-ID halfwords — so the engine consumed the
following `compare` as its arguments (x/y went to GetVarPointer(0x0121)/(0x0340)
= NULL, silently dropped on GBA), executed the compare's last byte as a nop, and
ran `goto_if <` on a STALE ctx->comparisonResult (InitScriptContext @0x080697AC
initializes every field EXCEPT offset 2). Net effect: the y<3 back-door gate
never evaluated — the ejection-vs-disarm choice was decided by whatever compare
ran last in the global script context, not by the player's position.

PROVEN LIVE (2026-07-02, headless rig): staged the wrapper on a field state with
the SAME player y=5 twice, poking sScriptContext1.comparisonResult (0x03000EB2)
to 0 vs 1 between runs — outcome flipped (stale=0: ejection runs, player force-
walked 3 tiles; stale=1: silent disarm). Position was irrelevant.

v2 wrapper (22 bytes, same location 0xC00120; frame-entry pointer unchanged):
    getplayerxy 0x4000, 0x4001     ; the real 5-byte form; y -> VAR_TEMP_1
    compare 0x4001, 3
    goto_if <  -> 0x088A0E99       ; back-door position (y < 3): run the ejection
    setvar 0x7035, 1               ; anywhere else: disarm, no scene
    end
VAR_TEMP_0/1 (0x4000/0x4001) are engine temp vars, zeroed on map load — safe.
Fits 0xC00120..0xC00135; the next allocation (fix_l2's stub) starts at 0xC00140.

usage: fix_f6b_v2.py [rom]   (default rom/ashgray.gba, patches in place)
"""
import sys
rom = sys.argv[1] if len(sys.argv) > 1 else 'rom/ashgray.gba'
ag = bytearray(open(rom, 'rb').read())

AT    = 0xC00120                     # wrapper (free-space allocation from fix_f6b)
ENTRY = 0x731B6A                     # map 33.0 frame-table entry's script-pointer field
OLD = bytes([0x42,                                   # (mis-assembled 1-byte getplayerxy)
             0x21, 0x01, 0x40, 0x03, 0x00,
             0x06, 0x00, 0x99, 0x0E, 0x8A, 0x08,
             0x16, 0x35, 0x70, 0x01, 0x00,
             0x02])
NEW = bytes([0x42, 0x00, 0x40, 0x01, 0x40,           # getplayerxy 0x4000, 0x4001
             0x21, 0x01, 0x40, 0x03, 0x00,           # compare 0x4001, 3
             0x06, 0x00, 0x99, 0x0E, 0x8A, 0x08,     # goto_if <  -> 0x088A0E99 (ejection)
             0x16, 0x35, 0x70, 0x01, 0x00,           # setvar 0x7035, 1 (disarm)
             0x02])                                  # end

if bytes(ag[AT:AT+len(NEW)]) == NEW:
    print('F6b v2 already applied — no change')
    raise SystemExit(0)
assert bytes(ag[ENTRY:ENTRY+4]) == (0x08000000+AT).to_bytes(4, 'little'), \
    f'frame entry ptr not -> wrapper: {bytes(ag[ENTRY:ENTRY+4]).hex()} (apply fix_f6b.py first)'
assert bytes(ag[AT:AT+len(OLD)]) == OLD, \
    f'unexpected wrapper bytes @0x{AT:06X}: {bytes(ag[AT:AT+len(OLD)]).hex()}'
assert all(b == 0xFF for b in ag[AT+len(OLD):AT+len(NEW)]), 'tail free space not free!'
ag[AT:AT+len(NEW)] = NEW
open(rom, 'wb').write(ag)
print(f'F6b v2: wrapper @0x{AT:06X} rebuilt with the real 5-byte getplayerxy; '
      'the y<3 back-door gate now actually evaluates')
