#!/usr/bin/env python3
"""Create a BPS patch from source->target.
usage: make_bps.py <source.rom> <target.rom> <out.bps>
Uses SourceRead/TargetRead actions only (valid BPS; not delta-optimized, but correct)."""
import sys, zlib
try:
    import numpy as np
    HAVE_NP = True
except ImportError:
    HAVE_NP = False

def varint(n):
    out = bytearray()
    while True:
        x = n & 0x7f
        n >>= 7
        if n:
            out.append(x); n -= 1
        else:
            out.append(0x80 | x); break
    return out

src = open(sys.argv[1], 'rb').read()
tgt = open(sys.argv[2], 'rb').read()
patch = bytearray(b'BPS1')
patch += varint(len(src))
patch += varint(len(tgt))
patch += varint(0)  # metadata size

n = len(tgt)
# Build runs: where src==tgt -> SourceRead (cmd 0); else -> TargetRead (cmd 1, literal bytes)
if HAVE_NP and len(src) >= n:
    s = np.frombuffer(src[:n], np.uint8)
    t = np.frombuffer(tgt, np.uint8)
    mask = (s != t).astype(np.int8)           # 1 where differs
    edges = np.flatnonzero(np.diff(mask) != 0) + 1
    bounds = [0] + edges.tolist() + [n]
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        length = b - a
        if mask[a]:                            # differs -> TargetRead
            patch += varint(((length - 1) << 2) | 1)
            patch += tgt[a:b]
        else:                                  # matches -> SourceRead
            patch += varint(((length - 1) << 2) | 0)
else:
    i = 0
    while i < n:
        same = (i < len(src) and src[i] == tgt[i])
        j = i
        if same:
            while j < n and j < len(src) and src[j] == tgt[j]:
                j += 1
            patch += varint(((j - i - 1) << 2) | 0)
        else:
            while j < n and not (j < len(src) and src[j] == tgt[j]):
                j += 1
            patch += varint(((j - i - 1) << 2) | 1)
            patch += tgt[i:j]
        i = j

patch += zlib.crc32(src).to_bytes(4, 'little')
patch += zlib.crc32(tgt).to_bytes(4, 'little')
patch += zlib.crc32(bytes(patch)).to_bytes(4, 'little')
open(sys.argv[3], 'wb').write(patch)
print(f"wrote {sys.argv[3]}  {len(patch)} bytes  src_crc={zlib.crc32(src)&0xffffffff:08x} tgt_crc={zlib.crc32(tgt)&0xffffffff:08x}")
