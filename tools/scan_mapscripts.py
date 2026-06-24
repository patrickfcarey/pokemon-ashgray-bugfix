#!/usr/bin/env python3
"""Find F2-class mapscript-table defects: overlapping/ malformed map-script subtables.
F2 (map 1.72) froze because its ON_WARP_INTO_MAP (type 4) and ON_FRAME (type 2) subtables overlapped,
so a msgbox ran during the warp transition. Map-script header @ map_header+8 = list of {u8 type, u32 ptr}
until type 0. Types 2 & 4 point to subtables of {u16 var, u16 value, u32 script} terminated by var==0.
Usage: scan_mapscripts.py [rom]   (default fork; pass the clean ROM to validate against F2's original)."""
import sys
ROMFILE = sys.argv[1] if len(sys.argv) > 1 else 'rom/ashgray.gba'
ag = open(ROMFILE, 'rb').read(); ROM = 0x08000000
def u16(o): return ag[o] | ag[o+1] << 8
def u32(o): return ag[o] | ag[o+1]<<8 | ag[o+2]<<16 | ag[o+3]<<24
def pf(o):
    if o is None or o+4 > len(ag): return None
    v = u32(o); return v-ROM if ROM <= v < ROM+len(ag) else None
def plist(off, cap):
    r=[]
    for i in range(cap):
        p=pf(off+4*i)
        if p is None: break
        r.append(p)
    return r
def subtable_extent(p):
    """parse {u16 var, u16 val, u32 script}* until var==0; return (start, end_incl_terminator, n)."""
    j = p; n = 0
    while j+8 <= len(ag) and u16(j) != 0 and n < 64:
        j += 8; n += 1
    return p, j+2, n   # +2 for the u16(0) terminator

banks = plist(pf(0x5524C), 64)
nover = 0; nbad = 0
for b, bt in enumerate(banks):
    for m, h in enumerate(plist(bt, 160)):
        ms = pf(h+8)
        if not ms: continue
        # parse mapscript header entries
        ents = []; i = ms
        while i+5 <= len(ag) and ag[i] != 0 and len(ents) < 12:
            t = ag[i]; p = pf(i+1); ents.append((t, p, i)); i += 5
        subs = []
        for (t, p, at) in ents:
            if t > 7:                       # malformed type
                print('MAP %d.%d header@0x%06X: bad mapscript type 0x%02X' % (b, m, h, t)); nbad += 1
            if t in (2, 4) and p is not None:
                s, e, n = subtable_extent(p)
                subs.append((t, s, e, n))
        # overlap check between subtables
        for a in range(len(subs)):
            for c in range(a+1, len(subs)):
                t1, s1, e1, n1 = subs[a]; t2, s2, e2, n2 = subs[c]
                if s1 != s2 and s1 < e2 and s2 < e1:
                    print('MAP %d.%d: OVERLAP type%d[0x%06X..0x%06X n=%d] & type%d[0x%06X..0x%06X n=%d]'
                          % (b, m, t1, ROM+s1, ROM+e1, n1, t2, ROM+s2, ROM+e2, n2)); nover += 1
print('\n%s: %d overlapping-subtable maps, %d malformed-type entries' % (ROMFILE.split('/')[-1], nover, nbad))
