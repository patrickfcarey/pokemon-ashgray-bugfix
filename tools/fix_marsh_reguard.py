#!/usr/bin/env python3
"""PROTOTYPE band-aid for the Marsh (Sabrina) D1 badge-block (#6a / D1 gym-block class).

The Saffron-gym leader script (person5 @0x806505) dispatches on story var 0x6072, which lives
in Box 3 slot 0 (D1). A Box-3 deposit corrupts it to a garbage value > 3, hitting the dead-end
`release; end` at 0x806516 -> Sabrina goes inert -> Marsh badge unreachable.

Fix: re-guard the dispatcher on the BADGE FLAG (0x825 @ sb1+0xFE4, which is NOT in PC storage and
so cannot be corrupted), preserving the original staging for the normal values:

    @0x806505:  goto 0xC00150            ; redirect to the re-guarded dispatcher (rest nop)
    @0xC00150:  checkflag 0x825
                goto_if SET  -> 0x80D67C  ; have the badge -> post-game rematch (corruption-proof)
                compare 0x6072, 3
                goto_if <    -> 0x805406  ; 0..2  -> match offer  (ORIGINAL behaviour, unchanged)
                goto_if ==   -> 0x80D67C  ; 3     -> rematch       (ORIGINAL behaviour, unchanged)
                goto         -> 0x805406  ; >3 (corrupt) -> match offer  (THE FIX: engage, not dead-end)

So normal play is byte-for-byte identical; a corrupted var now routes to "engage" (you can still
fight Sabrina and earn it) instead of the inert dead-end, and a player who already has the badge
short-circuits to the done/rematch dialogue. NOTE: this is a per-gym band-aid for the *badge* only;
the real fix for D1 is relocating the var space. Same shape applies to Boulder/Cascade/Volcano.

usage: fix_marsh_reguard.py <rom>   (patches in place)
"""
import sys
rom = sys.argv[1] if len(sys.argv) > 1 else 'rom/ashgray.gba'
ag = bytearray(open(rom, 'rb').read())

ENTRY = 0x806505
FREE  = 0xC00150
OLD = bytes([0x21,0x72,0x60,0x03,0x00, 0x06,0x00,0x06,0x54,0x80,0x08,
             0x06,0x01,0x7C,0xD6,0x80,0x08, 0x6C, 0x02])          # compare/goto_if/goto_if/release/end
if bytes(ag[ENTRY:ENTRY+5]) == bytes([0x05,0x50,0x01,0xC0,0x08]):
    print('Marsh re-guard already applied — no change')
    raise SystemExit(0)
assert bytes(ag[ENTRY:ENTRY+19]) == OLD, f'unexpected dispatcher bytes: {bytes(ag[ENTRY:ENTRY+19]).hex()}'
assert all(b == 0xFF for b in ag[FREE:FREE+32]), 'free space @0xC00150 not empty'

# entry: goto 0xC00150, then nop-fill the rest of the original 19 bytes (unreachable)
ag[ENTRY:ENTRY+19] = bytes([0x05,0x50,0x01,0xC0,0x08]) + bytes([0x00])*14

# re-guarded dispatcher in free space
ag[FREE:FREE+31] = bytes([
    0x2B,0x25,0x08,                       # checkflag 0x825
    0x06,0x01,0x7C,0xD6,0x80,0x08,         # goto_if SET -> 0x80D67C  (have badge -> done)
    0x21,0x72,0x60,0x03,0x00,              # compare 0x6072, 3
    0x06,0x00,0x06,0x54,0x80,0x08,         # goto_if <  -> 0x805406   (0..2 -> match offer)
    0x06,0x01,0x7C,0xD6,0x80,0x08,         # goto_if == -> 0x80D67C   (3 -> rematch)
    0x05,0x06,0x54,0x80,0x08,              # goto      -> 0x805406    (>3 corrupt -> match offer; THE FIX)
])
open(rom, 'wb').write(ag)
print(f'Marsh re-guard applied to {rom}: entry @0x{ENTRY:06X} -> 0x{FREE:06X}; badge-flag gate + corrupt->engage')
