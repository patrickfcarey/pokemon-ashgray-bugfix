#!/usr/bin/env python3
"""Verify tools/oplen.py against the engine itself (needs `pip install capstone`).

Disassembles all 213 FireRed script-command handlers (dispatch table @0x0815F9B4
in base/firered.gba) and derives each command's true length:

    1 + 2*(bl ScriptReadHalfword) + 4*(bl ScriptReadWord) + inline scriptPtr advances

Inline advances are detected as `str rX,[rCtx,#8]` writebacks (scriptPtr lives at
ctx+8). Two handler shapes fool that heuristic, so they are hand-adjudicated from
their disassembly (recorded below):
  - jump commands that STORE a new scriptPtr (a jump, not an arg read)
  - fused advances (`scriptPtr += N` compiled as one add+store, not N of them)

The readers are located empirically, not by hardcoded address:
  handler[0x16] setvar calls ScriptReadHalfword twice  -> the doubled bl target
  handler[0x0F] loadword calls ScriptReadWord once     -> the other reader target
(For FireRed rev 0 they resolve to 0x080698F8 / 0x08069910.)

Exit 0 = oplen.py matches the engine. Exit 1 = drift (listed).
"""
import bisect
import sys
from collections import Counter

try:
    import capstone
except ImportError:
    sys.exit("capstone not installed (pip install capstone) — cannot verify")

from oplen import LEN

ROM = 0x08000000
TBL = 0x15F9B4          # gScriptCmdTable (file offset), 213 entries
N = 213

# Hand-adjudicated handlers where the str-[ctx,#8] heuristic misreads (see module doc).
# op: (true_len, why)
ADJUDICATED = {
    0x5C: (0, 'trainerbattle: type-dependent variable length'),
    0x5E: (1, 'gotopostbattlescript: str [ctx,#8] is a JUMP, consumes no args'),
    0x5F: (1, 'gotobeatenscript: same jump-store shape'),
    0x73: (5, 'erasebox: fused scriptPtr += 4 (one store)'),
    0x95: (4, 'updatemoneybox: fused scriptPtr += 3 (two stores)'),
    0xC1: (3, 'hidecoinsbox: fused scriptPtr += 2 (one store)'),
    0xC2: (3, 'updatecoinsbox: fused scriptPtr += 2 (one store)'),
}

rom = open('base/firered.gba', 'rb').read()

def u32(o):
    return int.from_bytes(rom[o:o+4], 'little')

handlers = [(u32(TBL + 4*i) - ROM) & ~1 for i in range(N)]
assert all(0 < h < len(rom) for h in handlers), 'handler pointers out of range'
uniq = sorted(set(handlers))

def extent(h):
    i = bisect.bisect_right(uniq, h)
    return min(uniq[i] if i < len(uniq) else h + 0x200, h + 0x200)

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

def scan(start, end):
    """(bl targets, inline str-[r?,#8] count) over a linear Thumb sweep."""
    bls, inline, o = [], 0, start
    while o + 2 <= end:
        hi = int.from_bytes(rom[o:o+2], 'little')
        if o + 4 <= end:
            lo = int.from_bytes(rom[o+2:o+4], 'little')
            if (hi & 0xF800) == 0xF000 and (lo & 0xF800) == 0xF800:
                k = hi & 0x7FF
                if k & 0x400:
                    k -= 0x800
                bls.append((o + 4) + (k << 12) + ((lo & 0x7FF) << 1))
                o += 4
                continue
        if (hi & 0xFFC0) == 0x6080:      # str Rd,[Rb,#8]
            inline += 1
        o += 2
    return bls, inline

# locate ScriptReadHalfword / ScriptReadWord empirically
h16 = handlers[0x16]
c = Counter(scan(h16, extent(h16))[0])
read_half = c.most_common(1)[0][0]
assert c[read_half] >= 2, 'setvar handler did not show a doubled bl target'
h0f = handlers[0x0F]
others = [t for t in scan(h0f, extent(h0f))[0] if t != read_half]
assert len(others) == 1, f'loadword handler unexpected: {others}'
read_word = others[0]
print(f'ScriptReadHalfword = 0x{read_half+ROM:08X}   ScriptReadWord = 0x{read_word+ROM:08X}')

bad = []
for op in range(N):
    coded = LEN.get(op)
    if op in ADJUDICATED:
        true_len = ADJUDICATED[op][0]
        if coded != true_len:
            bad.append((op, coded, true_len, ADJUDICATED[op][1]))
        continue
    h = handlers[op]
    bls, inline = scan(h, extent(h))
    derived = 1 + 2*sum(t == read_half for t in bls) + 4*sum(t == read_word for t in bls) + inline
    if coded != derived:
        bad.append((op, coded, derived, f'handler @0x{h+ROM:08X}'))

if bad:
    print(f'\nDRIFT: {len(bad)} opcode length(s) disagree with the engine:')
    for op, coded, derived, note in bad:
        print(f'  0x{op:02X}: oplen.py={coded}  engine={derived}   ({note})')
    sys.exit(1)
print(f'OK: all {N} opcode lengths match the engine '
      f'({len(ADJUDICATED)} hand-adjudicated, listed in this file).')
