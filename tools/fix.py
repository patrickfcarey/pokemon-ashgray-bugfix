#!/usr/bin/env python3
"""Length-safe in-place text fix: remove a duplicated word from a 0xFF-terminated
string (shift tail left, move terminator, zero the freed slack). Demo: 'the the'."""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())
CH = {0x00:' ', 0xFE:'\\n', 0xFB:'\\p', 0xFA:'\\l'}
for i,c in enumerate('0123456789'): CH[0xA1+i]=c
for i in range(26): CH[0xBB+i]=chr(65+i)
for i in range(26): CH[0xD5+i]=chr(97+i)
CH.update({0xAB:'!',0xAC:'?',0xAD:'.',0xB4:'’'})
ENC = {c: 0xD5+i for i, c in enumerate('abcdefghijklmnopqrstuvwxyz')}  # a-z = 0xD5..0xEE

def show(o):
    s=[]; i=o
    while i < len(ag) and ag[i]!=0xFF:
        s.append(CH.get(ag[i], '[%02X]'%ag[i])); i+=1
    return ''.join(s), i

START = 0x834CBF
before, ff = show(START)
print('BEFORE 0x%06X:  %s' % (START, before))
the = bytes([ENC['t'],ENC['h'],ENC['e']])
buf = ag[START:ff]
idx = -1
for p in range(len(buf)-7):
    if buf[p:p+3]==the and buf[p+3] in (0x00,0xFE) and buf[p+4:p+7]==the:
        idx = p; break
if idx < 0:
    print('pattern "the<sep>the" not found — aborting (no change)')
else:
    cut = 4                                   # drop "the" + its separator
    newbuf = buf[:idx] + buf[idx+cut:]
    ag[START:START+len(newbuf)] = newbuf
    ag[START+len(newbuf)] = 0xFF              # new terminator
    for k in range(START+len(newbuf)+1, ff+1): ag[k] = 0x00   # zero freed slack
    after, _ = show(START)
    print('AFTER  0x%06X:  %s' % (START, after))
    open('rom/ashgray.gba','wb').write(ag)
    print('written rom/ashgray.gba  (removed %d bytes, slack zeroed)' % cut)
