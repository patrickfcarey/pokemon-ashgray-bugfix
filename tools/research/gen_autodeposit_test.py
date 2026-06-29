#!/usr/bin/env python3
"""Test auto-deposit (CopyMonToPC scan A @0x08040b90) skips hazard boxes:
fill BOX1, call the scan with a mon, verify it lands in BOX4 (not hazard BOX2)."""
import struct
BOX = bytes.fromhex(  # PIKACHU 80-byte BoxPokemon (non-zero species → slot 'occupied')
    "16223cff2c0ba224bbbbbbbbbbbbbbbbbbbb0202bbbbbbbbbbbbbb006ef80000"
    "3a299edb3a299edb3a299edb1729cadb3a299edb12379edb23299edb47299edb"
    "3a6f9edb3a719bf92cc78af03a299edb")
assert len(BOX) == 80, len(BOX)
STORAGE = 0x02029344            # gPokemonStorage (sb1+0x3DE8); currentBox @+0, boxes @+4
SLOT0 = STORAGE + 4
def slot_addr(box, slot): return SLOT0 + box * 2400 + slot * 80
MONPTR = 0x02024284             # gPlayerParty[0] — use as the mon-to-deposit source

lines = ["poke8 0x%08x 0" % STORAGE]   # currentBox = 0 (BOX1)
# put the mon-to-deposit at MONPTR (80 bytes)
for i in range(0, 80, 4):
    lines.append("poke32 0x%08x 0x%08x" % (MONPTR + i, struct.unpack('<I', BOX[i:i+4])[0]))
# fill BOX1 (box 0) all 30 slots so the scan must advance past it
for slot in range(30):
    base = slot_addr(0, slot)
    for i in range(0, 80, 4):
        lines.append("poke32 0x%08x 0x%08x" % (base + i, struct.unpack('<I', BOX[i:i+4])[0]))
# zero species of BOX2/3/4/5/6/7 slot0 to guarantee 'empty'
for b in (1, 2, 3, 4, 5, 6):
    lines.append("poke32 0x%08x 0" % slot_addr(b, 0))
lines.append("dump 0x%08x 4" % slot_addr(0, 0))   # BOX1 s0 (full)
lines.append("dump 0x%08x 4" % slot_addr(3, 0))   # BOX4 s0 (empty pre-call)
lines.append("call 0x08040b90 0x%08x" % MONPTR)   # scan A: deposit mon
lines.append("dump 0x%08x 4" % slot_addr(1, 0))   # BOX2 s0 — must stay empty
lines.append("dump 0x%08x 4" % slot_addr(2, 0))   # BOX3 s0 — must stay empty
lines.append("dump 0x%08x 4" % slot_addr(3, 0))   # BOX4 s0 — must get the mon (16 22 3c ff)
open("autodeposit_test.rig", "w").write("\n".join(lines) + "\n")
print("wrote autodeposit_test.rig (%d lines); BOX2 s0=0x%08x BOX4 s0=0x%08x" %
      (len(lines), slot_addr(1, 0), slot_addr(3, 0)))
