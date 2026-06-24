#!/usr/bin/env python3
"""L3: find every Bicycle-item (0x168) operation and special 0x157 site."""
ag = open('rom/ashgray.gba', 'rb').read()
OPS = {0x44: 'additem', 0x45: 'removeitem', 0x47: 'checkitem'}
print('item 0x168 (BICYCLE) ops:')
for i in range(0x800000, 0x900000):
    if ag[i] in OPS and ag[i+1] == 0x68 and ag[i+2] == 0x01:
        print(f'  @0x{i:06X} {OPS[ag[i]]}')
print('special 0x157 sites:')
for i in range(0x800000, 0x900000):
    if ag[i] == 0x25 and ag[i+1] == 0x57 and ag[i+2] == 0x01:
        print(f'  @0x{i:06X}')
