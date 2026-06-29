#!/usr/bin/env python3
"""Classify every storage-overlapping story var as GATE / MARKER / STATE.
GATE  = read in a branch (compare 0x21 -> goto_if/call_if 0x06/07 w/ valid ptr).
        storage->logic: corrupting this slot MISROUTES the game (Koga-class).
MARKER= written (setvar 0x16) but never read in a branch.
        logic->storage: the script CLOBBERS whatever Pokemon sits in that slot.
STATE = both (misroutes AND clobbers).
Maps each to its PC box/slot and ranks by deposit-exposure (low box, low slot first)."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM, LO, HI = 0x08000000, 0x800000, 0x8D0000
SB1_TO_STORAGE, STORAGE_SIZE, BOXES_OFF, MON, BOXNAMES_OFF = 0x3DE8, 0x83D0, 4, 80, 0x8344

def storage_off(vid):
    o = (0x1000 + 2*(vid-0x4000)) - SB1_TO_STORAGE
    return o if 0 <= o < STORAGE_SIZE else None
def box_slot(vid):
    o = storage_off(vid)
    if o is None or o < BOXES_OFF or o >= BOXNAMES_OFF: return None
    s = (o - BOXES_OFF)//MON
    return s//30, s%30, (o-BOXES_OFF)%MON

# --- collect validated GATES (compare -> goto_if/call_if w/ valid script ptr) ---
gates = {}        # vid -> [sites]
i = LO
while i < HI-10:
    if ag[i] == 0x21:
        vid = struct.unpack('<H', ag[i+1:i+3])[0]
        if 0x4100 <= vid < 0x8000 and ag[i+5] in (0x06,0x07):
            p = struct.unpack('<I', ag[i+7:i+11])[0]
            if 0x08000000 <= p < 0x08000000+len(ag):
                gates.setdefault(vid, []).append(i)
    i += 1
# --- collect SETVARs (val<0x80 noise filter) ---
writes = {}
i = LO
while i < HI-5:
    if ag[i] == 0x16:
        vid = struct.unpack('<H', ag[i+1:i+3])[0]
        val = struct.unpack('<H', ag[i+3:i+5])[0]
        if 0x4100 <= vid < 0x8000 and val < 0x80:
            writes.setdefault(vid, []).append(i)
    i += 1

universe = sorted(set(gates) | set(writes))
ov = [v for v in universe if storage_off(v) is not None]
def cls(v):
    g, w = v in gates, v in writes
    return 'STATE' if (g and w) else 'GATE' if g else 'MARKER'

from collections import Counter
print(f"universe (gate|setvar, 0x4100-0x7FFF): {len(universe)}; storage-overlapping: {len(ov)}")
print(f"  GATEs (read->misroute): {sum(1 for v in ov if v in gates)}")
print(f"  MARKERs (write-only->clobber): {sum(1 for v in ov if v not in gates and v in writes)}")
# box-level summary
boxsum = {}
for v in ov:
    b = box_slot(v)
    if not b: continue
    boxsum.setdefault(b[0], {'GATE':0,'MARKER':0,'STATE':0,'slots':[]})
    k = 'GATE' if v in gates else 'MARKER'
    boxsum[b[0]][k]+=1
    boxsum[b[0]]['slots'].append((b[1], v, cls(v)))
print("\n=== BY BOX (1-indexed): gates misroute, markers clobber ===")
for b in sorted(boxsum):
    d = boxsum[b]
    ng = d['GATE']+d['STATE']; print(f"  Box {b+1}: {ng} gate-capable, {d['MARKER']} marker-only")
print("\n=== EXPOSED GATES ranked by deposit order (low box, low slot first) ===")
rows = [(box_slot(v)[0], box_slot(v)[1], box_slot(v)[2], v, cls(v), len(gates.get(v,[])), gates.get(v,[None])[0])
        for v in ov if v in gates]
for box, slot, byte, v, c, n, site in sorted(rows):
    print(f"  Box {box+1} slot {slot:2d} +{byte:2d}: 0x{v:04X} {c:6s} ({n} gate site(s)) e.g.@{site:#x}")
