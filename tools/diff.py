#!/usr/bin/env python3
"""Map Ash Gray's footprint vs clean FireRed: coalesce changed byte ranges,
flag new-in-freespace vs in-place edits, and guess content type."""
import sys

fr = open('base/firered.gba', 'rb').read()
ag = open('rom/ashgray.gba', 'rb').read()
n = min(len(fr), len(ag))
GAP = 64  # merge changed runs separated by < GAP unchanged bytes

ranges = []
start = last = None
for i in range(n):
    if fr[i] != ag[i]:
        if start is None:
            start = last = i
        elif i - last <= GAP:
            last = i
        else:
            ranges.append((start, last)); start = last = i
if start is not None:
    ranges.append((start, last))

def classify(a, b):
    sfr, sag = fr[a:b+1], ag[a:b+1]
    L = len(sag)
    was_free = sfr.count(0xFF) / L          # region was 0xFF free space?
    ptr = sum(1 for k in range(0, L-3, 4)    # aligned ROM pointers 08/09xxxxxx
              if sag[k+3] in (0x08, 0x09)) / max(1, L//4)
    textish = sum(1 for x in sag if x == 0x00 or 0xA1 <= x <= 0xFE) / L
    terms = sag.count(0xFF) / L
    kind = 'NEW' if was_free > 0.7 else 'edit'
    guess = []
    if textish > 0.55 and 0.01 < terms < 0.25:
        guess.append('text')
    if ptr > 0.45:
        guess.append('pointer-table')
    if sag[:1] == b'\x10' or sag.count(0x10) > L*0.05 and a > 0x300000:
        guess.append('gfx?')
    if a < 0x300000 and kind == 'edit' and not guess:
        guess.append('engine/data')
    if not guess:
        guess.append('mixed/script-data')
    return kind, was_free, ' '.join(guess)

total = sum(b-a+1 for a, b in ranges)
ranges_sorted = sorted(ranges, key=lambda r: (r[1]-r[0]), reverse=True)

out = []
out.append('# Ash Gray — change footprint vs clean FireRed (U) v1.0\n')
out.append(f'- ROM size: {n:,} bytes (no expansion)')
out.append(f'- Bytes changed: **{total:,}** ({100*total/n:.1f}% of ROM)')
out.append(f'- Distinct changed regions (gap-coalesced): **{len(ranges)}**\n')
out.append('## Largest changed regions\n')
out.append('| # | offset | size | new/edit | was-free | content guess |')
out.append('|---|--------|------|----------|----------|---------------|')
for idx, (a, b) in enumerate(ranges_sorted[:30], 1):
    kind, wf, guess = classify(a, b)
    out.append(f'| {idx} | 0x{a:06X} | {b-a+1:,} | {kind} | {wf*100:.0f}% | {guess} |')

# region bucketing
buckets = {}
for a, b in ranges:
    key = a >> 20  # 1MB bucket
    buckets[key] = buckets.get(key, 0) + (b-a+1)
out.append('\n## Changed bytes by 1 MB region\n')
out.append('| MB region | changed bytes |')
out.append('|-----------|---------------|')
for k in sorted(buckets):
    out.append(f'| 0x{k:01X}00000–0x{k:01X}FFFFF | {buckets[k]:,} |')

open('audit/01-footprint.md', 'w').write('\n'.join(out) + '\n')

# console summary
print(f'changed {total:,} bytes ({100*total/n:.1f}%), {len(ranges)} regions')
print('top 12 regions:')
for a, b in ranges_sorted[:12]:
    kind, wf, guess = classify(a, b)
    print(f'  0x{a:06X}  {b-a+1:>8,}B  {kind:4}  free={wf*100:3.0f}%  {guess}')
print('-> audit/01-footprint.md')
