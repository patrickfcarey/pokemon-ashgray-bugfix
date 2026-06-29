#!/usr/bin/env python3
"""Map the PC storage system: disassemble a range (Thumb), mark function starts (push {..,lr}),
resolve pc-relative literal loads (ldr rX,[pc,#N]) to the actual constant. usage: disasm_pss.py 0xVA 0xLEN"""
import capstone, struct, sys
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB); md.detail = True
va = int(sys.argv[1], 16); ln = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x100
off = va - 0x08000000
def lit(addr):
    o = addr - 0x08000000
    return struct.unpack('<I', ag[o:o+4])[0]
for ins in md.disasm(ag[off:off+ln], va):
    note = ''
    # resolve ldr rX, [pc, #imm]  -> literal value
    if ins.mnemonic == 'ldr' and '[pc' in ins.op_str:
        imm = int(ins.op_str.split('#')[-1].rstrip(']'), 16)
        litaddr = (ins.address + 4 & ~3) + imm
        note = f'  ; =0x{lit(litaddr):08x}'
    if ins.mnemonic == 'push' and 'lr' in ins.op_str:
        note = '   <<< fn start'
    print(f'{ins.address:08x}: {ins.bytes.hex():12s} {ins.mnemonic:8s} {ins.op_str}{note}')
