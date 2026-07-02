#!/usr/bin/env python3
"""Scan for script if-commands with an out-of-range condition byte (>5).
goto_if (0x06) / call_if (0x07): cond(1) + ptr(4) — flag if cond>5 AND ptr is a sane
script pointer (0x08xxxxxx into the script region). gotostd_if/callstd_if (0x0A/0x0B):
cond(1)+std(1) — too noisy to scan blindly; skipped.
To cut false positives, require the candidate to be PRECEDED by a plausible compare
(0x21 var,val = 5 bytes) or another if-chain command ending right before."""
ag = open('rom/ashgray.gba', 'rb').read()

hits = []
for i in range(0x7F0000, min(len(ag), 0x900000)):   # full script bank (starts 0x7F0000)
    op = ag[i]
    if op not in (0x06, 0x07): continue
    cond = ag[i+1]
    if cond <= 5 or cond == 0xFF: continue
    ptr = int.from_bytes(ag[i+2:i+6], 'little')
    if not (0x08800000 <= ptr < 0x08900000 or 0x08C00000 <= ptr < 0x08C10000): continue
    # context: a compare (0x21) 5 bytes back, or compare_vv (0x22), or specialvar (0x26)+compare
    prev5 = ag[i-5] if i >= 5 else 0
    ctx = prev5 in (0x21, 0x22)
    hits.append((i, op, cond, ptr - 0x08000000, ctx))

print(f'{len(hits)} candidate(s) with cond>5:')
for i, op, cond, tgt, ctx in hits:
    name = 'goto_if' if op == 0x06 else 'call_if'
    pre = ag[i-5:i].hex() if ctx else ag[max(0,i-8):i].hex()
    print(f'  @0x{i:06X} {name} cond={cond} -> 0x{tgt:06X}  prevcmp={"Y" if ctx else "n"} pre={pre}')
