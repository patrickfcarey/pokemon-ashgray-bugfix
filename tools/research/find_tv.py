#!/usr/bin/env python3
"""Locate the bedroom-TV string in the fork ROM and every pointer that references it."""
import sys

ROM = sys.argv[1]
data = open(ROM, 'rb').read()

# FireRed text charset (subset we need to encode "It's a live")
CH = {' ': 0x00, "'": 0xB4}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"): CH[c] = 0xBB + i
for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"): CH[c] = 0xD5 + i

def enc(s): return bytes(CH[c] for c in s)

needle = enc("It's a live")
off = data.find(needle)
print(f"TV string 'It\\'s a live...' found at ROM offset: 0x{off:06X}" if off >= 0 else "NOT FOUND")
if off < 0:
    sys.exit(1)

# Decode a chunk to confirm it's the TV line
REV = {v: k for k, v in CH.items()}
EXT = {0xFE: '\\n', 0xFB: '\\p', 0xFA: '\\l', 0xFF: '[END]'}
# add é and the rest of lowercase/upper for readability
def dec(o, n=80):
    out = []
    for b in data[o:o+n]:
        if b in EXT:
            out.append(EXT[b])
            if b == 0xFF: break
        elif b in REV: out.append(REV[b])
        elif b == 0x1B: out.append('é')   # é often 0x1B in FR table variants
        else: out.append(f'<{b:02X}>')
    return ''.join(out)
print("decoded:", dec(off))

ptr = 0x08000000 + off
pb = ptr.to_bytes(4, 'little')
print(f"pointer value (LE) to search: 0x{ptr:08X}  bytes={pb.hex()}")
hits = []
start = 0
while True:
    i = data.find(pb, start)
    if i < 0: break
    hits.append(i)
    start = i + 1
print(f"references found ({len(hits)}):")
for h in hits:
    # show 8 bytes of context before (loadpointer opcode 0x0F 0xNN precedes the ptr)
    ctx = data[max(0,h-4):h].hex()
    print(f"  @0x{h:06X}  preceding={ctx}  (loadpointer operand if preceded by 0F xx)")
