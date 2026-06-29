#!/usr/bin/env python3
"""Build warp-redirect test ROMs: bedroom stairs (map 4.1 warp#0 @0x730604) -> any map.
Optionally revert the L1 fix to get a control ROM. TEST FIXTURES ONLY — not shipped.
usage: mk_warp_test.py <fork.gba> <out.gba> <group> <num> <warpId> [revert-l1]"""
import sys

fork, out = sys.argv[1], sys.argv[2]
g, n, w = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
revert = len(sys.argv) > 6 and sys.argv[6] == "revert-l1"

rom = bytearray(open(fork, "rb").read())

# bedroom warp#0 struct @0x730604: x(2) y(2) elev(1) warpId(1) mapNum(1) mapGroup(1)
W0 = 0x730604
assert rom[W0:W0+4] == bytes([0x0A, 0x00, 0x02, 0x00]), "bedroom warp#0 struct moved!"
rom[W0+5] = w
rom[W0+6] = n
rom[W0+7] = g
print(f"stairs -> map {g}.{n} warpId {w}")

if revert:
    AT = 0x869E5A
    NEW = bytes([0x21,0x14,0x70,0x02,0x00, 0x06,0x01,0x97,0xFF,0x87,0x08, 0x05,0x81,0x90,0x8E,0x08])
    OLD = bytes([0x21,0x14,0x70,0x01,0x00, 0x06,0x01,0x81,0x90,0x8E,0x08, 0x21,0x14,0x70,0x02,0x00])
    assert rom[AT:AT+16] == NEW, "L1 fix bytes not found — wrong base ROM?"
    rom[AT:AT+16] = OLD
    print("L1 fix REVERTED (control ROM: original guard dispatch)")

open(out, "wb").write(rom)
print(f"wrote {out}")
