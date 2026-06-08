#!/usr/bin/env python3
"""Generate an IPS patch from clean FireRed -> modified ROM, so fork edits become
a distributable patch (apply to clean FireRed v1.0 to get the forked Ash Gray)."""
import sys
base = open('base/firered.gba', 'rb').read()
mod  = open(sys.argv[1] if len(sys.argv) > 1 else 'rom/ashgray.gba', 'rb').read()
dst  = sys.argv[2] if len(sys.argv) > 2 else 'patches/ashgray-fork.ips'
n = min(len(base), len(mod))
recs = bytearray(b'PATCH')
i = 0
while i < n:
    if base[i] != mod[i]:
        s = i
        while i < n and base[i] != mod[i] and (i - s) < 0xFFFF:
            i += 1
        off = s
        if off == 0x454F46:  # avoid 'EOF' offset
            off -= 1
        chunk = mod[off:i]
        recs += off.to_bytes(3, 'big') + len(chunk).to_bytes(2, 'big') + chunk
    else:
        i += 1
recs += b'EOF'
open(dst, 'wb').write(recs)
print(f'wrote {dst}  ({len(recs):,} bytes)')
