#!/usr/bin/env python3
"""Find where the UI-local box index (sStorage[0x020397b0] + 0x2CA) is written — the box-cycle.
Search the PSS region for the literal 0x2CA and the sStorage ptr literal, disasm around each."""
import capstone, struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
LO, HI = 0x8c000, 0x94000
# literal 0x000002CA and the sStorage ptr 0x020397b0
for label, lit in (('0x2CA box-index offset', b'\xca\x02\x00\x00'), ('sStorage ptr 0x020397b0', b'\xb0\x97\x03\x02')):
    hits = []
    i = LO - 1
    while True:
        i = ag.find(lit, i + 1)
        if i < 0 or i >= HI: break
        hits.append(i)
    print(f'{label}: {len(hits)} literal-pool hits in PSS -> {[hex(0x08000000+h) for h in hits]}')
# disasm a window around each 0x2CA literal pool to see the function using it (read vs write)
print()
i = LO - 1
seen = set()
while True:
    i = ag.find(b'\xca\x02\x00\x00', i + 1)
    if i < 0 or i >= HI: break
    # the literal is loaded by a ldr earlier; disasm ~0x30 before the literal
    start = (i - 0x30) & ~1
    for ins in md.disasm(ag[start:i+4], 0x08000000 + start):
        if ins.mnemonic in ('strb', 'strh', 'str') and ('r' in ins.op_str):
            print(f'  WRITE near 0x2CA-lit@{0x08000000+i:#x}: {ins.address:#x} {ins.mnemonic} {ins.op_str}')
