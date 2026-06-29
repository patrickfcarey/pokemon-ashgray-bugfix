#!/usr/bin/env python3
"""Does Box 2 slot 28 (var 0x6029) also break the Koga gym / badge path?
A var only matters as a BRANCH GATE if it's COMPARED (read), not merely setvar'd (written).
Find every touch of 0x6029 vs 0x6155 ROM-wide, with opcode, and flag compares (gates)."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
OPN = {0x16:'setvar',0x17:'addvar',0x18:'subvar',0x19:'copyvar',0x1A:'setorcopyvar',
       0x21:'COMPARE(gate)',0x22:'compare_vars'}
def scan(var):
    lo = bytes([var & 0xFF, (var>>8)&0xFF])
    print(f"\n=== var {var:#x} touches (script bank) ===")
    i = -1
    while True:
        i = ag.find(lo, i+1)
        if i < 0: break
        if not (0x7F0000 <= i < 0x8D0000): continue
        op = ag[i-1]
        if op in OPN:
            val = struct.unpack('<H', ag[i+2:i+4])[0]
            # what follows a COMPARE? a goto_if/call_if (06/07) = it gates a branch
            nxt = ag[i+4] if op == 0x21 else None
            gate = ''
            if op == 0x21 and nxt in (0x06,0x07):
                tgt = struct.unpack('<I', ag[i+6:i+10])[0]-0x08000000
                gate = f'  -> {"goto_if" if nxt==0x06 else "call_if"} cond={ag[i+5]} -> {tgt:#x}'
            print(f"  @{i-1:#x}: {OPN[op]:14s} var={var:#x} val={val:#x}{gate}")
scan(0x6029)
scan(0x6155)
