#!/usr/bin/env python3
"""F3: parse the Butch & Cassidy trainerbattle + its inline continuation."""
ag = open('rom/ashgray.gba', 'rb').read()
o = 0x852C4B
print('raw:', ag[o:o+10].hex())
t = ag[o+1]; trainer = ag[o+2] | ag[o+3] << 8
p1 = int.from_bytes(ag[o+6:o+10], 'little')
print(f'trainerbattle type={t} trainer={trainer} defeat=0x{p1-0x08000000:06X}')
T = 0x23EAC8 + trainer*40
e = ag[T:T+40]
CH = {0x00: ' '}
for k in range(26): CH[0xBB+k] = chr(65+k)
nm = ''.join(CH.get(b, '?') for b in e[4:16] if b != 0xFF)
pptr = int.from_bytes(e[0x24:0x28], 'little')
print(f'  trainer{trainer}: name={nm!r} nmons={e[0x20]} flags={e[0]} ptr=0x{pptr:08X}')
if 0x08000000 <= pptr < 0x09000000:
    off = pptr - 0x08000000; sz = 16 if e[0] & 3 else 8
    for i in range(min(e[0x20], 6)):
        m = ag[off+i*sz: off+i*sz+sz]
        print(f'    mon{i}: lvl={m[2]|m[3]<<8} species={m[4]|m[5]<<8}')
print('continuation bytes:', ag[o+10:o+74].hex())
