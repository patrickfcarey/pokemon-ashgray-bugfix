#!/usr/bin/env python3
"""F3: inspect the Jessie/James trainerbattle pieces — defeat text, trainer 361 party."""
ag = open('rom/ashgray.gba', 'rb').read()
CH = {0x00:' ', 0xB4:"'", 0xAB:'!', 0xAC:'?', 0xAD:'.', 0xB8:',', 0x1B:'e', 0xF0:':', 0xFE:'/', 0xFB:'//'}
for k in range(26): CH[0xBB+k] = chr(65+k)
for k in range(26): CH[0xD5+k] = chr(97+k)
for k in range(10): CH[0xA1+k] = chr(48+k)

def dec(o, n=140):
    s = []
    for b in ag[o:o+n]:
        if b == 0xFF: s.append('[END]'); break
        s.append(CH.get(b, '<%02X>' % b))
    return ''.join(s)

print('defeat text @0x852967:', dec(0x852967))

T = 0x23EAC8 + 361*40
e = ag[T:T+40]
print('trainer361 raw:', e.hex())
partyFlags = e[0]; cls = e[1]; pic = e[3]
name = ''.join(CH.get(b, '?') for b in e[4:16] if b != 0xFF)
nmons = e[0x20]; pptr = int.from_bytes(e[0x24:0x28], 'little')
print(f'class={cls} pic={pic} name={name!r} nmons={nmons} partyPtr=0x{pptr:08X} partyFlags={partyFlags}')
if 0x08000000 <= pptr < 0x09000000:
    off = pptr - 0x08000000
    sz = 16 if partyFlags & 1 else 8   # 16B only for CUSTOM_MOVESET (bit0); held-item-only stays 8B
    print(f'party entries (entry size {sz}):')
    for i in range(min(nmons, 6)):
        m = ag[off+i*sz: off+i*sz+sz]
        iv = m[0] | m[1] << 8; lvl = m[2] | m[3] << 8; spec = m[4] | m[5] << 8
        print(f'  mon{i}: iv={iv} lvl={lvl} species={spec} raw={m.hex()}')
else:
    print('PARTY POINTER INVALID!')

# also: neighboring trainers for comparison (Butch/Cassidy fight is probably 362)
for tid in (360, 362, 363):
    T = 0x23EAC8 + tid*40
    e = ag[T:T+40]
    nm = ''.join(CH.get(b, '?') for b in e[4:16] if b != 0xFF)
    pptr = int.from_bytes(e[0x24:0x28], 'little')
    print(f'trainer{tid}: name={nm!r} nmons={e[0x20]} ptr=0x{pptr:08X} flags={e[0]}')
