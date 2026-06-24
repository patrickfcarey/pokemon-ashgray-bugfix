#!/usr/bin/env python3
"""Reachability BFS over the warp-event + map-connection graph. Reports which OI maps
are reachable from the start, and the frontier (reachable maps whose warps/conns point
to UNreachable or CORPSE maps = candidate progression seams)."""
import sys
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
def u8(o): return ag[o] if 0 <= o < len(ag) else 0
def u16(o): return (ag[o] | ag[o+1] << 8) if 0 <= o and o+1 < len(ag) else 0
def u32(o): return int.from_bytes(ag[o:o+4], 'little') if 0 <= o and o+4 <= len(ag) else 0
def pf(o):
    if o is None or o < 0 or o+4 > len(ag): return None
    v = u32(o); return v - ROM if ROM <= v < ROM + len(ag) else None
def plist(off, cap):
    r=[]
    for i in range(cap):
        p=pf(off+4*i)
        if p is None: break
        r.append(p)
    return r
banks = plist(pf(0x5524C), 64)
maps = {b: plist(bt, 120) for b, bt in enumerate(banks)}
def hdr(b,m):
    return maps[b][m] if b in maps and m < len(maps[b]) else None
def dims(h):
    lp=pf(h)
    return (u32(lp),u32(lp+4)) if lp else (None,None)
def corpse(b,m):
    h=hdr(b,m)
    if h is None: return True
    w,ht=dims(h); return w is None or w==0 or w>1000 or ht>1000
def edges(b,m):
    """all (destBank,destMap) this map can lead to: warps + connections."""
    h=hdr(b,m); out=set()
    if h is None: return out
    ev=pf(h+4)
    if ev:
        nW=u8(ev+1); wp=pf(ev+8)
        if wp:
            for i in range(min(nW,40)):
                o=wp+8*i
                out.add((u8(o+7),u8(o+6)))   # destBank,destMap
    cp=pf(h+12)
    if cp:
        n=u32(cp); ap=pf(cp+4)
        if ap and n<=20:
            for i in range(n):
                o=ap+12*i
                out.add((u8(o+8),u8(o+9)))
    return out

START=(eval(sys.argv[1]) if len(sys.argv)>1 else (4,1))   # bedroom start
seen=set([START]); q=[START]
while q:
    b,m=q.pop()
    for (db,dm) in edges(b,m):
        if (db,dm) not in seen and db in maps and dm < len(maps.get(db,[])):
            seen.add((db,dm)); q.append((db,dm))

OI_BANKS=set(range(30,43)); OI_OVERWORLD={(3,m) for m in (13,14,15,16,18)}
oi_all={(b,m) for b in OI_BANKS for m in range(len(maps.get(b,[])))} | OI_OVERWORLD
print(f"reachable maps total: {len(seen)}")
reach_oi=sorted(oi_all & seen); unreach_oi=sorted(oi_all - seen)
print(f"OI maps reachable: {len(reach_oi)}  unreachable: {len(unreach_oi)}")
print("UNREACHABLE OI maps:", [f"{b}.{m}" for b,m in unreach_oi])
print("\nFRONTIER — reachable OI maps whose edges hit UNreachable/CORPSE maps:")
for b,m in sorted(reach_oi):
    bad=[]
    for (db,dm) in edges(b,m):
        if (db,dm) not in seen: bad.append(f"{db}.{dm}(unreach)")
        elif corpse(db,dm): bad.append(f"{db}.{dm}(corpse)")
    if bad: print(f"  {b}.{m} -> {bad}")
