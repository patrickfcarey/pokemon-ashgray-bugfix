#!/usr/bin/env python3
"""Build tvtest/d7_real.gba — lab-door -> Viridian PC (5.4) redirect for the FULL
in-situ D7 scene test (Misty entry scene, Joy arming 0x5030, TR ambush on the exit
trigger line, type-9 battle, real thundershock-cinematic continuation).
One change: Oak's lab (4.3) door warp dest -> 5.4 warpId 0. Everything else stock fork."""
import struct

ag = bytearray(open('../ashgray-fork/rom/ashgray.gba', 'rb').read())
ROM = 0x08000000

def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

banks = pf(0x5524C)
bank4 = pf(banks + 16)
hdr = pf(bank4 + 12)
ev = pf(hdr + 4)
nw = ag[ev+1]
pw = pf(ev+8)
assert nw == 1, nw
x, y = struct.unpack('<hh', ag[pw:pw+4])
el, wid, mn, mg = ag[pw+4:pw+8]
print(f'lab warp0: ({x},{y}) elev={el} was -> {mg}.{mn} warpId={wid}')
ag[pw+5] = 0    # warpId 0
ag[pw+6] = 4    # mapNum 4
ag[pw+7] = 5    # mapGroup 5
open('tvtest/d7_real.gba', 'wb').write(ag)
print(f'd7_real.gba: lab door ({x},{y}) now -> 5.4 warp0 (Viridian PC)')
