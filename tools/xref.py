#!/usr/bin/env python3
"""Find 32-bit little-endian pointers to a target ROM address (xref finder).
Usage: xref.py 0x0884b038 [rom]   (default rom = rom/ashgray.gba)
Reports every 4-byte-aligned-or-not location holding the pointer, as ROM addresses."""
import sys, struct, os
target = int(sys.argv[1], 16)
rom = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', 'rom', 'ashgray.gba')
ag = open(rom, 'rb').read(); ROM = 0x08000000
pat = struct.pack('<I', target)
hits = []
i = ag.find(pat)
while i != -1:
    hits.append(i); i = ag.find(pat, i + 1)
print(f"{len(hits)} pointer(s) to 0x{target:08x} in {os.path.basename(rom)}:")
for h in hits[:60]:
    aligned = " (4-aligned)" if h % 4 == 0 else ""
    print(f"  @0x{ROM+h:08x}  file 0x{h:06x}{aligned}")
