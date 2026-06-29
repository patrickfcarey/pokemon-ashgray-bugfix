#!/usr/bin/env python3
"""Third trace pass:
(A) every call_if/goto_if cond=6 in the script bank — the F3 crash family.
    F3 patched ONE site (0x852C63). Are there siblings (J&J breeding, doll comp)?
(B) doll competition: Lickitung text refs + surrounding script.
(C) Safari Zone Team Rocket: Jessie/James refs in the Safari map-script range."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000
cs = {0xBB + j: chr(65 + j) for j in range(26)}
cs.update({0xD5 + j: chr(97 + j) for j in range(26)})
cs.update({0x00: ' ', 0xAD: '.', 0xB4: ',', 0xAC: '!', 0xF0: ':', 0xFE: '/', 0xFB: '|'})

def dec(o, n=70):
    s = ''
    for b in ag[o:o + n]:
        if b == 0xFF: break
        s += cs.get(b, f'[{b:02x}]')
    return s
def enc(t):
    inv = {v: k for k, v in cs.items()}
    return bytes(inv[c] for c in t)
def findall(pat, lo=0, hi=None):
    hi = hi or len(ag); out = []; i = lo - 1
    while True:
        i = ag.find(pat, i + 1)
        if i < 0 or i >= hi: break
        out.append(i)
    return out

# (A) call_if cond=6  (07 06 .. .. .. 08)  and goto_if cond=6  (06 06 .. .. .. 08)
print("=== (A) cond=6 branch family (the F3 class) ===")
for op, name in ((0x07, 'call_if'), (0x06, 'goto_if')):
    for h in findall(bytes([op, 0x06])):
        if not (0x800000 <= h < 0x8d0000): continue
        if ag[h+5] != 0x08: continue   # arg must be a ROM pointer
        tgt = struct.unpack('<I', ag[h+2:h+6])[0] - ROM
        if not (0x800000 <= tgt < 0x8d0000): continue
        tag = '  <-- F3 PATCH SITE' if h == 0x852C63 else ''
        print(f"  {name} cond=6 @{h:#x} -> {tgt:#x}{tag}")

# (B) doll competition — Lickitung refs; print decoded text + look for nearby pointer-to text
print("\n=== (B) doll competition / Lickitung ===")
for h in findall(enc("LICKITUNG")):
    print(f"  LICKITUNG text @{h:#x}: \"{dec(h,50)}\"")
# Jessie's Lickitung scripted scene: find 'DOLL' in dialogue range w/ Rocket context
for h in findall(enc("DOLL")):
    if 0x1f0000 <= h < 0x260000:
        t = dec(h, 60)
        if any(w in t for w in ('contest','COMPETITION','Contest','prize','PRIZE','win','WIN')):
            print(f"  DOLL ctx @{h:#x}: \"{t}\"")

# (C) Safari Zone Team Rocket — Safari maps are bank 32 (0x20) in FRLG. find JESSIE/JAMES
# pointers referenced from the Safari script region. Just report JESSIE/JAMES hit spread.
print("\n=== (C) Safari Zone Rocket (JESSIE/JAMES hit spread) ===")
for label in ("JESSIE", "JAMES"):
    hits = findall(enc(label))
    buckets = {}
    for h in hits:
        buckets.setdefault(h >> 16, []).append(h)
    print(f"  {label}: " + ", ".join(f"{k:#x}xxxx:{len(v)}" for k, v in sorted(buckets.items())))
