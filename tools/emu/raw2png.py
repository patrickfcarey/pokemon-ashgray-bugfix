#!/usr/bin/env python3
"""Convert mGBA raw framebuffer (W*H * 4-byte pixels) to a PNG (pure stdlib)."""
import sys, zlib, struct
raw = open(sys.argv[1], 'rb').read()
W, H, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
order = sys.argv[5] if len(sys.argv) > 5 else 'RGB'   # try RGB or BGR if colors look wrong

def chunk(t, d):
    return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)

rows = bytearray()
for y in range(H):
    rows.append(0)  # filter: none
    base = y * W * 4
    for x in range(W):
        p = raw[base + x*4: base + x*4 + 4]
        if order == 'BGR': rows += bytes([p[2], p[1], p[0]])
        else:              rows += bytes([p[0], p[1], p[2]])
png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(bytes(rows), 9))
       + chunk(b'IEND', b''))
open(out, 'wb').write(png)
print('wrote', out, W, 'x', H, order)
