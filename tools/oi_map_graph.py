#!/usr/bin/env python3
"""Orange Islands map graph: for every map, resolve name (via the map-name table),
layout validity (corpse-map?), warps (dest bank.map.warpId) and connections.
Used to trace the OI progression boundary."""
import sys, struct
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
def u8(o): return ag[o] if 0 <= o < len(ag) else 0
def u16(o): return (ag[o] | ag[o+1] << 8) if 0 <= o and o+1 < len(ag) else 0
def u32(o): return int.from_bytes(ag[o:o+4], 'little') if 0 <= o and o+4 <= len(ag) else 0
def pf(o):
    if o is None or o < 0 or o+4 > len(ag): return None
    v = u32(o); return v - ROM if ROM <= v < ROM + len(ag) else None
def plist(off, cap):
    r = []
    for i in range(cap):
        p = pf(off + 4*i)
        if p is None: break
        r.append(p)
    return r

# --- bank/map tables ---
banks = plist(pf(0x5524C), 64)
maps = {b: plist(bt, 120) for b, bt in enumerate(banks)}

# --- map-name table: find via the VALENCIA string pointer 0x08720068 ---
def find_ptr(target):
    t = struct.pack('<I', target)
    return [i for i in range(0, len(ag), 4) if ag[i:i+4] == t]
val = find_ptr(0x08720068)          # VALENCIA ISLAND name string
NAMETBL = None; VAL_ID = None
if val:
    # the name table is an array of string pointers; the entry closest below 'val[0]'
    # is the table; the FRLG name table starts at some base, indexed by mapsec id.
    e = val[0]
    # walk back while previous words are also rom string-pointers (a contiguous ptr array)
    base = e
    while base-4 >= 0:
        p = pf(base-4)
        if p is None or not (0x700000 <= p < 0x900000): break
        base -= 4
    NAMETBL = base; VAL_ID = (e - base)//4
def mapname(nameid):
    if NAMETBL is None: return '?'
    p = pf(NAMETBL + 4*nameid)
    if p is None: return '?'
    # decode FRLG text
    CM = {0x00:' ',0xAD:'.',0xB8:',',0xBA:'-'}
    for v in range(0xBB,0xD5): CM[v]=chr(ord('A')+v-0xBB)
    for v in range(0xD5,0xEF): CM[v]=chr(ord('a')+v-0xD5)
    s=''
    for i in range(20):
        b=ag[p+i]
        if b==0xFF: break
        s+=CM.get(b,'?')
    return s.strip()

def warps(hdr):
    ev = pf(hdr+4)
    if ev is None: return []
    nW = u8(ev+1); wp = pf(ev+8)
    if wp is None: return []
    out=[]
    for i in range(nW):
        o=wp+8*i
        out.append((u16(o),u16(o+2),u8(o+5),u8(o+6),u8(o+7)))  # x,y,warpId,destMap,destBank
    return out
def conns(hdr):
    cp = pf(hdr+12)
    if cp is None: return []
    n=u32(cp); ap=pf(cp+4)
    if ap is None or n>20: return []
    DIRS={1:'down',2:'up',3:'left',4:'right',5:'dive',6:'emerge'}
    out=[]
    for i in range(n):
        o=ap+12*i
        out.append((DIRS.get(u32(o),str(u32(o))),u8(o+8),u8(o+9)))  # dir,destBank,destMap
    return out
def dims(hdr):
    lp=pf(hdr);
    if lp is None: return (None,None)
    return (u32(lp),u32(lp+4))

# locate each OI name string's table index (search the whole rom for its pointer, map to id)
OI = {0x720068:'VALENCIA',0x72022F:'MIKAN',0x727F76:'TANGELO',0x728B60:'PINKAN'}
oi_ids={}
for addr,nm in OI.items():
    hits=find_ptr(0x08000000+(addr-0)) if addr>=0x08000000 else find_ptr(0x08000000+addr)
    for h in hits:
        if NAMETBL is not None and (h-NAMETBL)%4==0 and h>=NAMETBL:
            oi_ids[(h-NAMETBL)//4]=nm
print(f"name table @0x{0x08000000+NAMETBL:08x}  OI name-ids: {oi_ids}" if NAMETBL else "name table NOT found")
banks_to_show = [int(x) for x in sys.argv[1:]] if len(sys.argv)>1 else list(range(30,46))
for b in banks_to_show:
    if b not in maps: continue
    for m,hdr in enumerate(maps[b]):
        w,h = dims(hdr); nid=u8(hdr+20)
        bad = (w is None or w>1000 or h>1000 or w==0)
        ws=warps(hdr); cs=conns(hdr)
        wsm=' '.join(f"{x},{y}->{db}.{dm}#{wid}" for (x,y,wid,dm,db) in ws)
        csm=' '.join(f"{d}:{db}.{dm}" for (d,db,dm) in cs)
        flag='CORPSE' if bad else ''
        nm = oi_ids.get(nid, mapname(nid))
        print(f"{b}.{m} nid={nid} [{nm}] {w}x{h} {flag}  warps[{len(ws)}]: {wsm}  conn: {csm}")
