#!/usr/bin/env python3
"""Zero SaveBlock1.mapView (+0x34..+0x233) inside a Gen3 .sav and fix the sector checksum.
The in-game save re-captures mapView after any RAM poke, so it must be cleared offline;
an empty mapView makes Continue skip pasting stale blocks over the warped-to map."""
import sys
p = sys.argv[1]
d = bytearray(open(p, "rb").read())
SEC = 0x1000
SIG = 0x08012025

def fold(total):
    return ((total >> 16) + (total & 0xFFFF)) & 0xFFFF
def csum(data, ln):
    t = 0
    for i in range(0, ln, 4):
        t = (t + int.from_bytes(data[i:i+4], "little")) & 0xFFFFFFFF
    return fold(t)

# find the most-recent sector with id==1 (SaveBlock1 chunk 0)
best = None
for s in range(len(d)//SEC):
    b = s*SEC
    if int.from_bytes(d[b+0xFF8:b+0xFFC], "little") != SIG: continue
    sid = int.from_bytes(d[b+0xFF4:b+0xFF6], "little")
    cnt = int.from_bytes(d[b+0xFFC:b+0x1000], "little")
    if sid == 1 and (best is None or cnt > best[0]):
        best = (cnt, s)
if not best:
    sys.exit("no SaveBlock1 sector found")
b = best[1]*SEC
stored = int.from_bytes(d[b+0xFF6:b+0xFF8], "little")
# detect checksummed length by matching the stored checksum
ln = next((L for L in (0xF80, 0xFF4, 0xF24, 0xF2C) if csum(d[b:b+0x1000], L) == stored), None)
if ln is None:
    sys.exit(f"could not match stored checksum 0x{stored:04X} with any known length")
print(f"sector {best[1]} (counter {best[0]}): checksum len=0x{ln:X}, stored=0x{stored:04X} OK")
d[b+0x34:b+0x234] = bytes(0x200)                  # zero mapView
new = csum(d[b:b+0x1000], ln)
d[b+0xFF6:b+0xFF8] = new.to_bytes(2, "little")
open(p, "wb").write(d)
print(f"mapView zeroed; new checksum=0x{new:04X}; written {p}")
