#!/usr/bin/env python3
"""Third overlap facet: the hack's high FLAGS overflow FireRed's flag array into the
VARIABLE array. FireRed flags live at sb1+0xEE0 (0x120 bytes = flags 0x000-0x8FF). The
hack uses flags 0x1xxx; flag F -> bit (F&7) of byte sb1+0xEE0+(F>>3). For F>=0x900 that
byte is >=0x1000 = inside the 256-var array (vars 0x4000-0x40FF live at sb1+0x1000).
So a high flag and a low var can share a byte. A write to the VAR clobbers the FLAG bit
(persistent flag corrupted by a transient var write) and vice-versa. Map the collisions."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
LO, HI = 0x800000, 0x8D0000
FLAG_BASE = 0xEE0
VARS_BASE, VARS_END = 0x1000, 0x1200   # the 256-var array (vars 0x4000-0x40FF)

def flag_byte(f):
    return FLAG_BASE + (f >> 3)

def var_at_byte(off):
    if VARS_BASE <= off < VARS_END:
        return 0x4000 + (off - VARS_BASE) // 2
    return None

# collect SET flags (0x29) and CLEAR (0x2A) in the script bank; high ones (>=0x900)
flags = {}
i = LO
while i < HI - 3:
    if ag[i] in (0x29, 0x2A, 0x2B):  # setflag/clearflag/checkflag
        f = struct.unpack('<H', ag[i+1:i+3])[0]
        if 0x900 <= f <= 0x1900:
            flags.setdefault(f, set()).add({0x29:'set',0x2A:'clr',0x2B:'chk'}[ag[i]])
    i += 1

# collect WRITTEN vars 0x4000-0x40FF (setvar/addvar/copyvar/setorcopyvar dest), plausible
written = {}
i = LO
while i < HI - 4:
    if ag[i] in (0x16,0x17,0x18,0x19,0x1A):
        v = struct.unpack('<H', ag[i+1:i+3])[0]
        if 0x4000 <= v <= 0x40FF:
            if ag[i] in (0x16,0x17,0x18):
                val = struct.unpack('<H', ag[i+3:i+5])[0]
                if val > 0x200:
                    i += 1; continue
            written[v] = written.get(v, 0) + 1
    i += 1

print(f"high flags used by the hack (0x900-0x18FF): {len(flags)}")
print(f"written temp/early vars 0x4000-0x40FF: {sorted(hex(v) for v in written)}\n")
print("COLLISIONS — a flag whose byte overlaps a WRITTEN var (the dangerous case):")
ncol = 0
for f in sorted(flags):
    b = flag_byte(f)
    v = var_at_byte(b)
    if v is not None and v in written:
        ncol += 1
        print(f"  flag 0x{f:04X} [{','.join(sorted(flags[f]))}] -> byte sb1+0x{b:04X} = var 0x{v:04X} "
              f"(written x{written[v]})  *** COLLISION ***")
if ncol == 0:
    print("  (none — every high flag lands on a var the hack never writes)")
print(f"\ntotal high-flag/written-var collisions: {ncol}")
