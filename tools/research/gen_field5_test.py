#!/usr/bin/env python3
"""Decisive: does a var-garbage RESERVED-box slot read as 'occupied' to the Quest Log's
clear-loop? It calls GetBoxMonDataAt(box,slot,FIELD 5) and erases the slot if !=0.
Test field-5 for: valid mon, empty slot, sparse var-garbage, worst-case var-garbage."""
import struct
PIK = bytes.fromhex(
    "16223cff2c0ba224bbbbbbbbbbbbbbbbbbbb0202bbbbbbbbbbbbbb006ef80000"
    "3a299edb3a299edb3a299edb1729cadb3a299edb12379edb23299edb47299edb"
    "3a6f9edb3a719bf92cc78af03a299edb")
S = 0x0202a608           # Box3 (idx2) slot0
GBMDAT = 0x0808ba18      # GetBoxMonDataAt(box, slot, field)
def pk(addr,d): return ["poke32 0x%08x 0x%08x"%(addr+i,struct.unpack('<I',d[i:i+4])[0]) for i in range(0,len(d),4)]
L=[]
# (1) valid PIKACHU
L += pk(S, PIK); L.append("call 0x%08x 2 0 5"%GBMDAT)          # field5 of a real mon
# (2) truly empty
L.append("fill 0x%08x 0 80"%S); L.append("call 0x%08x 2 0 5"%GBMDAT)
# (3) realistic sparse var-garbage (PID stays 0)
L.append("fill 0x%08x 0 80"%S)
for off,val in ((0x46,3),(0x10,1),(0x2a,2),(0x58,4)): L.append("poke16 0x%08x %d"%(S+off,val))
L.append("call 0x%08x 2 0 5"%GBMDAT)
# (4) worst case: var bytes in the sanity/flag region near the start
L.append("fill 0x%08x 0 80"%S)
for off in (0x00,0x13,0x14,0x1c,0x20): L.append("poke16 0x%08x 1"%(S+off))
L.append("call 0x%08x 2 0 5"%GBMDAT)
open("field5_test.rig","w").write("\n".join(L)+"\n"); print("wrote field5_test.rig")
