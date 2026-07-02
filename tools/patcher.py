#!/usr/bin/env python3
"""Minimal IPS / BPS / UPS patcher with CRC validation.
Usage: patcher.py <base_rom> <patch> <output_rom>
Refuses to write for BPS/UPS if the base ROM's CRC doesn't match what the
patch expects (i.e. wrong base version). IPS has no checksum, so it's applied
best-effort and flagged as unverified.
"""
import sys, zlib

def crc32(b):
    return zlib.crc32(b) & 0xffffffff

def read_vuint(data, pos):
    val = 0; shift = 1
    while True:
        b = data[pos]; pos += 1
        val += (b & 0x7f) * shift
        if b & 0x80:
            break
        shift <<= 7
        val += shift
    return val, pos

def apply_bps(source, patch):
    pos = 4
    _src_size, pos = read_vuint(patch, pos)
    dst_size, pos = read_vuint(patch, pos)
    meta_size, pos = read_vuint(patch, pos)
    pos += meta_size
    out = bytearray()
    src_rel = 0; dst_rel = 0
    end = len(patch) - 12
    while pos < end:
        cmd, pos = read_vuint(patch, pos)
        action = cmd & 3
        length = (cmd >> 2) + 1
        if action == 0:          # SourceRead
            start = len(out)
            out += source[start:start+length]
        elif action == 1:        # TargetRead
            out += patch[pos:pos+length]; pos += length
        elif action == 2:        # SourceCopy
            off, pos = read_vuint(patch, pos)
            src_rel += (-1 if off & 1 else 1) * (off >> 1)
            out += source[src_rel:src_rel+length]; src_rel += length
        else:                    # TargetCopy
            off, pos = read_vuint(patch, pos)
            dst_rel += (-1 if off & 1 else 1) * (off >> 1)
            if dst_rel + length <= len(out):   # non-overlapping -> slice
                out += out[dst_rel:dst_rel+length]; dst_rel += length
            else:                              # overlapping -> byte copy
                for _ in range(length):
                    out.append(out[dst_rel]); dst_rel += 1
    if len(out) != dst_size:
        print(f"  ERROR: output size {len(out)} != patch's declared target size {dst_size} -> malformed patch.")
        sys.exit(4)
    scrc = int.from_bytes(patch[-12:-8], 'little')
    dcrc = int.from_bytes(patch[-8:-4], 'little')
    return bytes(out), scrc, dcrc

def apply_ups(source, patch):
    pos = 4
    src_size, pos = read_vuint(patch, pos)
    dst_size, pos = read_vuint(patch, pos)
    out = bytearray(dst_size)
    n = min(src_size, dst_size)
    out[:n] = source[:n]
    out_pos = 0
    end = len(patch) - 12
    while pos < end:
        rel, pos = read_vuint(patch, pos)
        out_pos += rel
        while True:
            b = patch[pos]; pos += 1
            if b == 0:
                out_pos += 1
                break
            if out_pos < dst_size:
                out[out_pos] ^= b
            out_pos += 1
    scrc = int.from_bytes(patch[-12:-8], 'little')
    dcrc = int.from_bytes(patch[-8:-4], 'little')
    return bytes(out), scrc, dcrc

def apply_ips(source, patch):
    out = bytearray(source)
    pos = 5
    while True:
        if patch[pos:pos+3] == b'EOF':
            break
        offset = int.from_bytes(patch[pos:pos+3], 'big'); pos += 3
        size = int.from_bytes(patch[pos:pos+2], 'big'); pos += 2
        if offset > len(out):
            out.extend(b'\x00' * (offset - len(out)))
        if size == 0:
            rle = int.from_bytes(patch[pos:pos+2], 'big'); pos += 2
            val = patch[pos]; pos += 1
            for i in range(rle):
                idx = offset + i
                if idx < len(out): out[idx] = val
                else: out.append(val)
        else:
            chunk = patch[pos:pos+size]; pos += size
            for i in range(size):
                idx = offset + i
                if idx < len(out): out[idx] = chunk[i]
                else: out.append(chunk[i])
    return bytes(out)

def main():
    base_path, patch_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    source = open(base_path, 'rb').read()
    patch = open(patch_path, 'rb').read()
    print(f"base : {base_path.split('/')[-1]}  ({len(source)} bytes, crc {crc32(source):08x})")
    if patch[:4] in (b'BPS1', b'UPS1'):
        # both formats end with 12B footer whose last u32 = CRC of everything before it
        own = int.from_bytes(patch[-4:], 'little')
        got = crc32(patch[:-4])
        if got != own:
            print(f"  ERROR: patch self-CRC {got:08x} != stored {own:08x} -> corrupt/truncated patch file, not applying.")
            sys.exit(4)
    if patch[:4] == b'BPS1':
        out, scrc, dcrc = apply_bps(source, patch); fmt = 'BPS'
    elif patch[:4] == b'UPS1':
        out, scrc, dcrc = apply_ups(source, patch); fmt = 'UPS'
    elif patch[:5] == b'PATCH':
        out = apply_ips(source, patch); fmt = 'IPS'; scrc = dcrc = None
    else:
        print("  ERROR: unknown patch format"); sys.exit(2)

    if scrc is not None:
        if crc32(source) != scrc:
            print(f"  ERROR: base CRC {crc32(source):08x} != expected {scrc:08x} -> WRONG BASE ROM, not writing.")
            sys.exit(3)
        print(f"  base matches patch's expected source crc {scrc:08x}  [OK]")
        verified = (crc32(out) == dcrc)
        tag = "VERIFIED OK" if verified else f"TARGET CRC MISMATCH (got {crc32(out):08x}, want {dcrc:08x})"
    else:
        verified = True
        tag = "applied (IPS - no checksum to verify)"
    open(out_path, 'wb').write(out)
    print(f"  [{fmt}] -> {out_path.split('/')[-1]}  ({len(out)} bytes)  {tag}")
    if not verified:
        sys.exit(5)   # output written for inspection, but exit nonzero so scripts notice

if __name__ == '__main__':
    main()
