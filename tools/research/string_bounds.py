#!/usr/bin/env python3
"""Resolve each fixed string's containing-string START offset + decode it.
For in-place edits we scan back from the edit offset; for the relocated T2a we
search for the corrected word. Prints the start offset to point the TV at."""
import sys
data = open(sys.argv[1], 'rb').read()

CH = {' ': 0x00, "'": 0xB4, '!': 0xAB, '?': 0xAC, '.': 0xAD, ',': 0xB8, '/': 0xBA}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"): CH[c] = 0xBB + i
for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"): CH[c] = 0xD5 + i
def enc(s): return bytes(CH[c] for c in s)

REV = {v: k for k, v in CH.items()}
EXT = {0xFE: '\\n', 0xFB: '\\p', 0xFA: '\\l', 0x1B: 'é'}
def dec(o, n=200):
    out = []
    for b in data[o:o+n]:
        if b == 0xFF: break
        elif b == 0xFD: out.append('{VAR}');
        elif b in EXT: out.append(EXT[b])
        elif b in REV: out.append(REV[b])
        else: out.append(f'<{b:02X}>')
    return ''.join(out)

def start_of(off):
    """scan back to the byte after the previous 0xFF terminator"""
    i = off
    while i > 0 and data[i-1] != 0xFF:
        i -= 1
    return i

# (label, kind, value)
targets = [
    ("T1  the/the",  "off",  0x834CBF),
    ("T2a sacrifices","word", "sacrifices"),
    ("T2b received",  "off",  0x814026),
    ("T2c received",  "off",  0x867878),
]
for label, kind, val in targets:
    if kind == "off":
        # the recorded offset may be at the edit; nudge into the string then find start
        s = start_of(val)
    else:
        n = enc(val)
        i = data.find(n)
        s = start_of(i) if i >= 0 else -1
    if s < 0:
        print(f"{label}: NOT FOUND"); continue
    ptr = 0x08000000 + s
    print(f"{label}: start=0x{s:06X}  ptr=0x{ptr:08X}")
    print(f"     | {dec(s)}")
