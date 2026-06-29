#!/usr/bin/env python3
"""The one edge: if a var write set the has-species sanity bit (BoxPokemon offset 0x13 bit1),
the slot reads 'occupied' and the Quest Log clear (ZeroBoxMon) would zero it — including the
overlapping story var. Demonstrate both: occupied detection + the var getting zeroed."""
S = 0x0202a608        # Box3 slot0
GBMDAT = 0x0808ba18   # GetBoxMonDataAt(box,slot,field)
CLEAR  = 0x0808bcb4   # the per-slot op -> ZeroBoxMon(slot)
L=[]
L.append("fill 0x%08x 0 80"%S)            # empty
L.append("poke8 0x%08x 0x02"%(S+0x13))    # set has_species sanity bit
L.append("poke16 0x%08x 0x0003"%(S+0x46)) # a 'story var' value living in this slot
L.append("call 0x%08x 2 0 5"%GBMDAT)      # field5 -> expect 1 (now 'occupied')
L.append("dump 0x%08x 4"%(S+0x44))        # var region before clear (should show 03 00)
L.append("call 0x%08x 2 0"%CLEAR)         # Quest Log clear of this slot
L.append("dump 0x%08x 4"%(S+0x44))        # var region after clear (zeroed == story var reset)
open("hasspecies_test.rig","w").write("\n".join(L)+"\n"); print("wrote hasspecies_test.rig")
