#!/usr/bin/env python3
"""Find SaveBlock1.location in a Gen3 .sav (most-recent slot) and report it.
Gen3 flash: 32 sectors x 0x1000. Footer @0xFF4: id(2),chk(2),sig(4)=0x08012025,counter(4).
SaveBlock1 starts in the sector whose id==1; location is at SaveBlock1+0x04."""
import sys
d = open(sys.argv[1], "rb").read()
SEC = 0x1000
best = None  # (counter, physical_sector)
for s in range(min(32, len(d)//SEC)):
    base = s*SEC
    sig = int.from_bytes(d[base+0xFF8:base+0xFFC], "little")
    if sig != 0x08012025:
        continue
    sid = int.from_bytes(d[base+0xFF4:base+0xFF6], "little")
    cnt = int.from_bytes(d[base+0xFFC:base+0x1000], "little")
    if sid == 1:
        if best is None or cnt > best[0]:
            best = (cnt, s)
def warp(b):
    return f"map {b[0]}.{b[1]} warpId={b[2]} pos=({int.from_bytes(b[4:6],'little')},{int.from_bytes(b[6:8],'little')})"
if best:
    base = best[1]*SEC
    pos = d[base+0:base+4]
    loc = d[base+4:base+0x0C]
    cgw = d[base+0x0C:base+0x14]
    print(f"most-recent SaveBlock1 (sector id=1) @physical sector {best[1]}, counter {best[0]}")
    print(f"  pos      = ({int.from_bytes(pos[0:2],'little')},{int.from_bytes(pos[2:4],'little')})")
    print(f"  location = {warp(loc)}   raw={loc.hex()}")
    print(f"  warp@0x0C= {warp(cgw)}   raw={cgw.hex()}")
else:
    print("no SaveBlock1 sector (id=1) found")
