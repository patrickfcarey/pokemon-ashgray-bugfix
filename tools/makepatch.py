#!/usr/bin/env python3
"""Generate an IPS patch from clean FireRed -> modified ROM, so fork edits become
a distributable patch (apply to clean FireRed v1.0 to get the forked Ash Gray).
Guards: equal-size ROMs only (no silent tail drop), <=16 MiB (IPS offsets are
24-bit), no record at the 'EOF' offset 0x454F46 (such a record starts one byte
early instead), records re-split if that nudge would overflow the 0xFFFF cap."""
import sys
base = open('base/firered.gba', 'rb').read()
mod  = open(sys.argv[1] if len(sys.argv) > 1 else 'rom/ashgray.gba', 'rb').read()
dst  = sys.argv[2] if len(sys.argv) > 2 else 'patches/ashgray-fork.ips'
if len(base) != len(mod):
    sys.exit(f'ERROR: size mismatch (base {len(base):,} vs mod {len(mod):,} bytes) — '
             'refusing to emit a silently-partial patch')
if len(mod) > 0x1000000:
    sys.exit('ERROR: ROM exceeds 16 MiB — offsets beyond 0xFFFFFF are not representable in IPS')
n = len(mod)
recs = bytearray(b'PATCH')

def emit(off, chunk):
    while chunk:
        if off == 0x454F46:                    # record here would parse as 'EOF'
            off -= 1                           # start 1B early; that byte == base's, harmless
            chunk = mod[off:off+1] + chunk
        part, chunk = chunk[:0xFFFF], chunk[0xFFFF:]
        recs.extend(off.to_bytes(3, 'big') + len(part).to_bytes(2, 'big') + part)
        off += len(part)

i = 0
while i < n:
    if base[i] != mod[i]:
        s = i
        while i < n and base[i] != mod[i] and (i - s) < 0xFFFF:
            i += 1
        emit(s, mod[s:i])
    else:
        i += 1
recs += b'EOF'
open(dst, 'wb').write(recs)
print(f'wrote {dst}  ({len(recs):,} bytes)')
