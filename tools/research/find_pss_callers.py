#!/usr/bin/env python3
"""Find callers of the box-navigation primitives to confirm the hook choke point."""
import capstone
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
targets = {0x808ba00: 'SetCurrentBox', 0x808b9f4: 'GetCurrentBoxIndex', 0x808b9d8: 'accessor_b9d8'}
callers = {t: [] for t in targets}
for off0 in (0, 2):
    for ins in md.disasm(ag[off0:0x180000], 0x08000000 + off0):
        if ins.mnemonic == 'bl' and ins.op_str.startswith('#'):
            try:
                tgt = int(ins.op_str[1:], 16)
            except ValueError:
                continue
            if tgt in targets and ins.address not in [c[0] for c in callers[tgt]]:
                callers[tgt].append((ins.address, ins.mnemonic))
for t, nm in targets.items():
    print(f'{nm} @{t:#x}: {len(callers[t])} BL call sites')
    for a, m in sorted(set(callers[t]))[:12]:
        print(f'   {m} from {a:#x}')
