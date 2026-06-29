#!/usr/bin/env python3
"""Compose N raw GBA framebuffers (240x160 RGBA) into a vertical proof-sheet PNG.
usage: montage.py out.png scale raw1 raw2 ...  (pure stdlib)"""
import sys, zlib, struct
out = sys.argv[1]; scale = int(sys.argv[2]); raws = sys.argv[3:]
W, H = 240, 160
SEP = 3  # black separator rows between frames
def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t+d) & 0xffffffff)

frames = [open(r, 'rb').read() for r in raws]
OW = W * scale
OH = (H * len(frames) + SEP * (len(frames) - 1)) * scale
rows = bytearray()
def push_line(rgb_line):
    for _ in range(scale):
        rows.append(0)
        rows.extend(rgb_line)
for fi, raw in enumerate(frames):
    for y in range(H):
        line = bytearray()
        base = y * W * 4
        for x in range(W):
            p = raw[base + x*4: base + x*4 + 4]
            line += bytes([p[0], p[1], p[2]]) * scale   # RGB order, nearest-neighbor
        push_line(line)
    if fi != len(frames) - 1:
        black = bytes([0, 0, 0]) * OW
        for _ in range(SEP):
            push_line(black)
png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', struct.pack('>IIBBBBB', OW, OH, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(bytes(rows), 9))
       + chunk(b'IEND', b''))
open(out, 'wb').write(png)
print('wrote', out, OW, 'x', OH)
