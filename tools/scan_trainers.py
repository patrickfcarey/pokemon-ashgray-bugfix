#!/usr/bin/env python3
"""Validate every gTrainers entry for crash-causing data: bad party pointer, 0/huge party size,
out-of-range species or level. A trainerbattle against a malformed trainer crashes the battle engine.
gTrainers @ ROM 0x0823EAC8 (file 0x23EAC8), 40-byte entries; FRLG has 743 (0x2E7)."""
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
def u16(o): return ag[o] | ag[o+1] << 8
def u32(o): return ag[o] | ag[o+1]<<8 | ag[o+2]<<16 | ag[o+3]<<24
def pf(o):
    v = u32(o); return v-ROM if ROM <= v < ROM+len(ag) else None
CM = {0x00:' '}
for i,c in enumerate('0123456789'): CM[0xA1+i]=c
for i in range(26): CM[0xBB+i]=chr(65+i)
for i in range(26): CM[0xD5+i]=chr(97+i)
CM.update({0xAD:'.',0xAE:'-',0xBA:'/',0xB5:'M',0xB6:'F',0x1B:'e'})
def name(o):
    s=''
    for i in range(12):
        b=ag[o+i]
        if b==0xFF: break
        s+=CM.get(b,'?')
    return s
GT = 0x23EAC8; NTR = 743; MAXSPEC = 411
flagged = []
for tid in range(NTR):
    e = GT + tid*40
    flags = ag[e]; psize = u32(e+0x20); pp = pf(e+0x24)
    issues = []
    if pp is None:
        issues.append('party ptr 0x%08X not in ROM' % u32(e+0x24))
    if psize == 0 or psize > 6:
        issues.append('partySize=%d' % psize)
    if pp is not None and 1 <= psize <= 6:
        monsz = 16 if (flags & 1) else 8
        for i in range(psize):
            mb = pp + i*monsz
            spec = u16(mb+4); lvl = u16(mb+2)
            if spec == 0 or spec > MAXSPEC: issues.append('mon%d species=%d(0x%X)' % (i, spec, spec))
            if lvl == 0 or lvl > 100: issues.append('mon%d level=%d' % (i, lvl))
    if issues:
        flagged.append((tid, name(e+4), flags, psize, issues))
        print('trainer %3d "%-11s" flags=0x%02X size=%d: %s' % (tid, name(e+4), flags, psize, '; '.join(issues)))
print('\n%d/%d trainers flagged as malformed' % (len(flagged), NTR))
