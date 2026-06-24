#!/usr/bin/env python3
"""Check item ids used by the Rocket scripts against FR's gItems table (@0x3DB028)."""
ag = open('rom/ashgray.gba', 'rb').read()
CH = {0x00: ' ', 0xB4: "'", 0xAD: '.', 0xAE: '-'}
for k in range(26): CH[0xBB+k] = chr(65+k)
for k in range(26): CH[0xD5+k] = chr(97+k)
for k in range(10): CH[0xA1+k] = chr(48+k)
GI = 0x3DB028

def iname(i):
    e = ag[GI+i*44: GI+i*44+44]
    nm = ''.join(CH.get(b, '?') for b in e[:14] if b != 0xFF)
    idx = e[14] | e[15] << 8
    pocket = e[26]
    return nm.strip(), idx, pocket

print('items used by scripts:')
for i in (0x10C, 0x162, 0x163, 0x164, 0x165, 0x166):
    nm, idx, pk = iname(i)
    flag = '' if idx == i else '   <-- index mismatch (suspicious)'
    print(f'  item 0x{i:03X} ({i:3}): name={nm!r:20} index={idx} pocket={pk}{flag}')
print()
print('table end probe (FR has 375 items, 0-374):')
for i in (372, 373, 374, 375, 376):
    nm, idx, pk = iname(i)
    print(f'  item {i}: name={nm!r:20} index={idx} pocket={pk}')
