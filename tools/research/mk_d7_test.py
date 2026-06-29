#!/usr/bin/env python3
"""Build tvtest/d7_test.gba — D7/D1 faint-test harness.

Injects a coord trigger into Oak's lab (4.3) at (4,9) — one step below the pikachu.ss
start tile — gated on var 0x40F7==1. Its script runs the EXACT trainerbattle bytes from
the Viridian-PC Team Rocket scene (0x80049C: type 9 / EARLY_RIVAL, trainer 107), with
marker setvars around it instead of the thundershock-cinematic goto:

    setvar 0x40F7, 2        # battle launched
    trainerbattle 9, 107, 3, 0x88231E0, 0x8818BAB
    setvar 0x40F7, 3        # script resumed after battle (loss did NOT whiteout)
    end

Trigger var 0x40F7 is a real in-range vanilla var (sb1+0x11EE) so the arming poke lands
INSIDE sb1 — no deep-alias storage scribble that could confound the Bad-Egg check.
Free space (test ROM only): script @0xC00200, coords @0xC00240, events @0xC00280.
"""
import struct

ag = bytearray(open('../ashgray-fork/rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

banks = pf(0x5524C)
bank4 = pf(banks + 16)
hdr = pf(bank4 + 12)              # map 4.3 header
ev = pf(hdr + 4)
no, nw, nc, nb = ag[ev], ag[ev+1], ag[ev+2], ag[ev+3]
po, pw, pc, pb = (struct.unpack('<I', ag[ev+4+4*i:ev+8+4*i])[0] for i in range(4))
assert (no, nw, nc, nb) == (1, 1, 2, 10), (no, nw, nc, nb)

SCRIPT, COORDS, EVENTS = 0xC00200, 0xC00240, 0xC00280
tb = bytes(ag[0x80049C:0x80049C+14])
assert tb == bytes.fromhex('5c096b000300e0318208ab8b8108'), tb.hex()

scr = bytes.fromhex('16f7400200') + tb + bytes.fromhex('16f7400300') + b'\x02'
ag[SCRIPT:SCRIPT+len(scr)] = scr

old = bytes(ag[pc-ROM:pc-ROM+nc*16])
new = struct.pack('<hhBBHHH', 4, 9, 3, 0, 0x40F7, 1, 0) + struct.pack('<I', ROM+SCRIPT)
ag[COORDS:COORDS+len(old)+16] = old + new

ag[EVENTS:EVENTS+20] = bytes([no, nw, nc+1, nb]) + struct.pack('<IIII', po, pw, ROM+COORDS, pb)
ag[hdr+4:hdr+8] = struct.pack('<I', ROM+EVENTS)

open('tvtest/d7_test.gba', 'wb').write(ag)
print('d7_test.gba: trigger (4,9) var 0x40F7==1 -> setvar2; trainerbattle9(107); setvar3; end')
