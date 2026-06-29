#!/usr/bin/env python3
"""Does still-occurring story-var overflow into a RESERVED box read as empty (species 0)
to an all-box scan, or as a Bad Egg? Test GetBoxMonData(MON_DATA_SPECIES) on Box3 slot0."""
import struct
PIK = bytes.fromhex(
    "16223cff2c0ba224bbbbbbbbbbbbbbbbbbbb0202bbbbbbbbbbbbbb006ef80000"
    "3a299edb3a299edb3a299edb1729cadb3a299edb12379edb23299edb47299edb"
    "3a6f9edb3a719bf92cc78af03a299edb")
S = 0x0202a608   # Box3 (idx2) slot0  (gPokemonStorage+4 + 2*2400)
GBMD = 0x0803fd44
def pokeblk(addr, data):
    return ["poke32 0x%08x 0x%08x" % (addr+i, struct.unpack('<I', data[i:i+4])[0]) for i in range(0, len(data), 4)]
L = []
# (1) sanity: a VALID PIKACHU should report a non-zero species
L += pokeblk(S, PIK)
L.append("call 0x%08x 0x%08x 0xb 0" % (GBMD, S))          # expect PIKACHU species (0x19=25)
# (2) realistic: empty slot + sparse story-var writes (PID stays 0)
L.append("fill 0x%08x 0 80" % S)
L.append("poke16 0x%08x 3" % (S + 0x46))                  # var 0x6079=3 lands here
L.append("poke16 0x%08x 1" % (S + 0x10))
L.append("poke16 0x%08x 2" % (S + 0x2a))
L.append("poke16 0x%08x 4" % (S + 0x58))
L.append("call 0x%08x 0x%08x 0xb 0" % (GBMD, S))          # expect 0 (empty)
# (3) worst case: var bytes land in PID / checksum region
L.append("fill 0x%08x 0 80" % S)
L.append("poke16 0x%08x 1" % (S + 0x00))                  # PID
L.append("poke16 0x%08x 1" % (S + 0x1c))                  # checksum word
L.append("poke16 0x%08x 1" % (S + 0x20))                  # substruct0 (species field!)
L.append("call 0x%08x 0x%08x 0xb 0" % (GBMD, S))          # species?
# (4) 0xBB-filled slot — used to fake 'occupied' for the all-full test
L.append("fill 0x%08x 0xbb 80" % S)
L.append("call 0x%08x 0x%08x 0xb 0" % (GBMD, S))          # is a garbage-filled slot 'occupied'?
open("badegg_test.rig", "w").write("\n".join(L) + "\n")
print("wrote badegg_test.rig")
