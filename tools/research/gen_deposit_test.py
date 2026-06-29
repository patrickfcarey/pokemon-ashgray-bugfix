#!/usr/bin/env python3
"""Emit a .rig that injects a PIKACHU party mon then drives DEPOSIT mode to test box cycling."""
import struct
MON_HEX = ("16223cff2c0ba224bbbbbbbbbbbbbbbbbbbb0202bbbbbbbbbbbbbb006ef80000"
           "3a299edb3a299edb3a299edb1729cadb3a299edb12379edb23299edb47299edb"
           "3a6f9edb3a719bf92cc78af03a299edb0000000005ff130013000b0008000e00"
           "0b000a00")
mon = bytes.fromhex(MON_HEX)
assert len(mon) == 100, len(mon)
base = 0x02024284
lines = []
lines.append("poke8 0x02024029 2")              # gPlayerPartyCount = 2 (so deposit isn't "last mon")
for slot in (0, 1):
    for i in range(0, 100, 4):
        val = struct.unpack('<I', mon[i:i+4])[0]
        lines.append(f"poke32 0x{base+slot*100+i:08x} 0x{val:08x}")
# from pc_submenu.ss cursor is on WITHDRAW. DOWN to DEPOSIT, select, pick party mon, reach box view.
nav = """frames 8
key DOWN
frames 8
key -
frames 8
tap A 4 30
frames 45
shot s1_panel.raw
tap A 4 30
frames 30
shot s2_ctxmenu.raw
tap A 4 30
frames 50
shot s3_chooseBox.raw
save chooseBox.ss
"""
open("deposit_test.rig", "w").write("\n".join(lines) + "\n" + nav)
print("wrote deposit_test.rig", len(lines), "poke lines")
