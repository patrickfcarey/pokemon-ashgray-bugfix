#!/usr/bin/env python3
"""L5 + warp-audit class fix — dangling warp references on reachable maps.

audit_warps.py found 73 structural warp defects. The reachable, player-facing ones:
(a) sources asking for warpIds the (deliberately edited) destination no longer has —
    Gen3 reads past the dest warp table and spawns at garbage coordinates (void/walls;
    the L5 "wrong mapping / traps with no exit" class — incl. the Hidden Village area
    cluster 1.55/1.56 -> 1.49/1.50);
(b) two reachable doors into corpse maps whose layouts the build destroyed
    (3.18 -> 37.0 [15x2058], 34.1 -> 34.2 [0xFFFFFFFF dims]) — F6-class crash doors.

Fixes:
(a) clamp each out-of-range dest warpId to the dest's last valid id (nearest real door);
(b) retarget the two corpse doors back to the source map's own warp#0 (harmless blink,
    same as the F6 hardening).
FFFF warp entries on gutted-but-sane maps (1.85/10.7/10.8) sit at tile (65535,...) —
unreachable positions, no player can trigger them — left as-is. Zero-incoming sources
(orphaned gates the new routes bypass) also left as-is.
Every edit byte-guarded against the audited current value.
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read()); ROM = 0x08000000

def pf(o):
    v = ag[o] | ag[o+1] << 8 | ag[o+2] << 16 | ag[o+3] << 24
    return v - ROM if 0x08000000 <= v < 0x09000000 else None

def plist(off, cap):
    r = []
    for i in range(cap):
        p = pf(off + 4*i)
        if p is None: break
        r.append(p)
    return r

banks = plist(pf(0x5524C), 64)
def warpstruct(g, n, w):
    h = plist(banks[g], 200)[n]
    ev = pf(h+4)
    return pf(ev+8) + w*8

# (source g,n,warp#, expected old dest (g,n,warpId), new warpId)
CLAMPS = [
    (1,55,2,  (1,49,4),  2),   # Hidden Village cluster
    (1,56,1,  (1,50,3),  1),
    (1,56,2,  (1,50,5),  1),
    (1,56,4,  (1,50,4),  1),
    (1,61,3,  (1,59,7),  6),
    (1,61,4,  (1,59,8),  6),
    (1,61,6,  (1,59,8),  6),
    (2,21,1,  (2,13,4),  0),
    (2,21,2,  (2,13,1),  0),
    (2,21,3,  (2,13,2),  0),
    (2,22,0,  (2,13,1),  0),
    (2,40,0,  (2,39,1),  0),
    (2,55,0,  (2,54,1),  0),
    (3,115,3, (3,116,4), 3),
    (12,7,0,  (3,8,4),   3),
    (12,7,2,  (3,8,4),   3),
    (23,0,1,  (3,30,2),  1),
    (23,0,2,  (3,30,3),  1),
    (23,0,3,  (3,30,3),  1),
]
changed = False
for sg, sn, sw, (dg, dn, dw), new in CLAMPS:
    o = warpstruct(sg, sn, sw)
    if ag[o+7] == dg and ag[o+6] == dn and ag[o+5] == new:
        print(f'already clamped {sg}.{sn} warp#{sw}'); continue
    assert ag[o+7] == dg and ag[o+6] == dn and ag[o+5] == dw, \
        f'{sg}.{sn} w{sw}: expected ->{dg}.{dn} id{dw}, found ->{ag[o+7]}.{ag[o+6]} id{ag[o+5]}'
    ag[o+5] = new
    changed = True
    print(f'clamped {sg}.{sn} warp#{sw}: ->{dg}.{dn} warpId {dw} -> {new}')

# corpse-door seals: retarget to the source's own warp#0
SEALS = [
    (3,18,1,  (37,0,0)),   # route door into gutted interior 37.0
    (34,1,1,  (34,2,0)),   # back room into gutted 34.2
]
for sg, sn, sw, (dg, dn, dw) in SEALS:
    o = warpstruct(sg, sn, sw)
    if ag[o+7] == sg and ag[o+6] == sn and ag[o+5] == 0:
        print(f'already sealed {sg}.{sn} warp#{sw}'); continue
    assert ag[o+7] == dg and ag[o+6] == dn and ag[o+5] == dw, \
        f'{sg}.{sn} w{sw}: expected ->{dg}.{dn} id{dw}, found ->{ag[o+7]}.{ag[o+6]} id{ag[o+5]}'
    ag[o+5] = 0
    ag[o+6] = sn
    ag[o+7] = sg
    changed = True
    print(f'sealed {sg}.{sn} warp#{sw}: ->{dg}.{dn} now -> {sg}.{sn} warp#0')

if not changed:
    print('L5 already applied (all clamps + seals in place) — no change')
    raise SystemExit(0)
open('rom/ashgray.gba', 'wb').write(ag)
print('done: 19 clamps + 2 seals')
