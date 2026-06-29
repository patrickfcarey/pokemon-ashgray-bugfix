#!/usr/bin/env python3
"""#3 doll/Lickitung scene: who points at the 'LICKITUNG! POKeBALL go!' text (0x84b038)?
#5 Safari Zone: enumerate map banks, find object-event scripts whose text mentions
   ROCKET/JESSIE/JAMES, report the owning map -> is there a TR object in Safari at all?"""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/', 0xFB: '|'})
def dec(o, n=60):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF: break
        s += cs.get(b, f'[{b:02x}]')
    return s
def pf(o):
    v = struct.unpack('<I', ag[o:o+4])[0]
    return v - ROM if 0x08000000 <= v < 0x09000000 else None
def plist(off, cap):
    r = []
    for k in range(cap):
        p = pf(off + 4*k)
        if p is None: break
        r.append(p)
    return r

# (A) #3 — references to 0x84b038 (Lickitung send-out line)
print("=== (A) refs to Lickitung scene text 0x84b038 ===")
tgt = struct.pack('<I', 0x84b038 + ROM)
i = -1
while True:
    i = ag.find(tgt, i+1)
    if i < 0: break
    print(f"  ptr @{i:#x} (in a script/loadword)")

# (B) walk ALL maps; for each object-event script, peek the first text it shows and
# flag any map whose objects reference JESSIE/JAMES/ROCKET. Report map bank.map.
def enc(t):
    inv = {v: k for k, v in cs.items()}
    return bytes(inv[c] for c in t)
rocket_pats = [enc("ROCKET"), enc("JESSIE"), enc("JAMES")]
def has_rocket(lo, hi):
    seg = ag[lo:hi]
    return any(p in seg for p in rocket_pats)

print("\n=== (B) maps with Rocket/Jessie/James in an object script (bank.map) ===")
banks = pf(0x5524C)
flagged = []
for b, bt in enumerate(plist(banks, 64)):
    for m, h in enumerate(plist(bt, 230)):
        if h + 0x1c > len(ag): continue
        ev = pf(h + 4)
        if ev is None or ev + 8 > len(ag): continue
        no = ag[ev]; po = pf(ev + 4)
        if not (po and no and no < 64): continue
        for k in range(no):
            base = po + 24*k
            if base + 24 > len(ag): continue
            sp = pf(base + 16)
            if sp is None: continue
            # peek the object script's first ~200 bytes for a Rocket name
            if has_rocket(sp, sp + 256):
                flagged.append((b, m, k, sp))
# de-dup by map
seen = set()
for b, m, k, sp in flagged:
    if (b, m) in seen: continue
    seen.add((b, m))
    print(f"  MAP {b}.{m}: obj script @{sp:#x} mentions Rocket — \"{dec(sp+1,40)}\"")
print(f"  ({len(seen)} maps total)")
