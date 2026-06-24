#!/usr/bin/env python3
"""L3: context for each special-0x157 site — preceding setvar 0x4055 value if present."""
ag = open('rom/ashgray.gba', 'rb').read()
sites = [0x806585,0x80D2C8,0x83B6B1,0x83FB45,0x840832,0x845D54,0x85CEFE,0x86059B,0x8AFE76,0x8B0BBA,0x8E7E99]
for s in sites:
    back = ag[s-32:s]
    j = back.rfind(bytes([0x16,0x55,0x40]))   # setvar 0x4055
    val = None
    if j >= 0:
        val = back[j+3] | back[j+4] << 8
    print(f'special157 @0x{s:06X}: setvar 0x4055,{val if val is not None else "—(not nearby)"}  pre16={back[-16:].hex()}')
# all setvar/compare 0x4055
print('all 0x4055 ops:')
vb=(0x4055).to_bytes(2,'little')
i=0x800000
while True:
    j=ag.find(vb,i)
    if j<0 or j>0x900000: break
    if ag[j-1] in (0x16,0x21):
        print(f'  @0x{j-1:06X} {"setvar" if ag[j-1]==0x16 else "compare"} 0x4055, {ag[j+2]|ag[j+3]<<8}')
    i=j+1
