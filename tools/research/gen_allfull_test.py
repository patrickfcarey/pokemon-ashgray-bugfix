#!/usr/bin/env python3
"""Gap (c): when all 11 USABLE boxes are full, the auto-deposit scan must return 'full'
and must NOT dump the mon into a reserved box (1/2/5). Fill all boxes, empty the reserved
ones, call scan A, confirm r0=2 (full) and reserved boxes stay empty."""
import struct
PIK = bytes.fromhex(
    "16223cff2c0ba224bbbbbbbbbbbbbbbbbbbb0202bbbbbbbbbbbbbb006ef80000"
    "3a299edb3a299edb3a299edb1729cadb3a299edb12379edb23299edb47299edb"
    "3a6f9edb3a719bf92cc78af03a299edb")
STORAGE = 0x02029344
SLOT0 = STORAGE + 4
def box_addr(b): return SLOT0 + b * 2400
MONPTR = 0x02024284
HAZ = (1, 2, 5)   # reserved box indices

L = ["poke8 0x%08x 0" % STORAGE]                     # currentBox = 0 (safe)
L += ["poke32 0x%08x 0x%08x" % (MONPTR+i, struct.unpack('<I', PIK[i:i+4])[0]) for i in range(0,80,4)]
L.append("fill 0x%08x 0xbb %d" % (box_addr(0), 14*2400))   # ALL 14 boxes 'full' (0xBB reads occupied)
for b in HAZ:
    L.append("fill 0x%08x 0 2400" % box_addr(b))           # reserved boxes empty (free slots)
L.append("call 0x08040b90 0x%08x" % MONPTR)               # scan A — should find NO room (safe boxes full)
L.append("dump 0x%08x 4" % box_addr(1))                   # reserved Box2 slot0 — must stay 0
L.append("dump 0x%08x 4" % box_addr(2))                   # reserved Box3 slot0 — must stay 0
L.append("dump 0x%08x 4" % box_addr(5))                   # reserved Box6 slot0 — must stay 0
open("allfull_test.rig", "w").write("\n".join(L) + "\n")
print("wrote allfull_test.rig; reserved Box2/3/6 slot0 = 0x%08x 0x%08x 0x%08x" %
      (box_addr(1), box_addr(2), box_addr(5)))
