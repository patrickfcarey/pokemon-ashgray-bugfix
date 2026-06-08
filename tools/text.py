#!/usr/bin/env python3
"""Decode FireRed-encoded strings in Ash Gray's new-content region (the anime
dialogue) so it can be proofread for typos/grammar — a fixable class of bug."""
ag = open('rom/ashgray.gba', 'rb').read()

# FireRed character table
CH = {0x00: ' '}
for i, c in enumerate('0123456789'): CH[0xA1+i] = c
for i in range(26): CH[0xBB+i] = chr(ord('A')+i)
for i in range(26): CH[0xD5+i] = chr(ord('a')+i)
CH.update({0xAB:'!',0xAC:'?',0xAD:'.',0xAE:'-',0xB0:'…',0xB1:'“',0xB2:'”',0xB3:'‘',
 0xB4:'’',0xB5:'♂',0xB6:'♀',0xB7:'$',0xB8:',',0xB9:'×',0xBA:'/',0xF0:':',0xF1:'Ä',
 0xF2:'Ö',0xF3:'Ü',0xF4:'ä',0xF5:'ö',0xF6:'ü',0xAF:'·',0xBA:'/'})
CTRL = {0xFE:'\\n', 0xFB:'\\p', 0xFA:'\\l'}   # newline / paragraph / scroll
VARS = {0x01:'{PLAYER}',0x06:'{RIVAL}',0x07:'{...}'}

def decode(o):
    s=[]; i=o
    while i < len(ag):
        b = ag[i]
        if b == 0xFF: return ''.join(s), i+1
        if b in CTRL: s.append(CTRL[b]); i+=1; continue
        if b == 0xFD:                       # variable/buffer
            code = ag[i+1] if i+1<len(ag) else 0
            s.append(VARS.get(code, '{V%02X}'%code)); i+=2; continue
        if b == 0xFC:                       # extended control: consume 1 sub-byte
            s.append('{C%02X}'%(ag[i+1] if i+1<len(ag) else 0)); i+=2; continue
        if b in CH: s.append(CH[b]); i+=1; continue
        return None, i                       # invalid -> not a string
    return None, i

START, END = 0x700000, 0xA00000
strings = []
i = START
while i < END:
    txt, nxt = decode(i)
    if txt is not None:
        letters = sum(c.isalpha() for c in txt)
        if letters >= 6:                     # filter junk
            strings.append((i, txt))
            i = nxt
            continue
    i += 1

# dump
out = ['# Ash Gray — anime dialogue dump (region 0x700000–0xA00000)\n',
       f'Strings found: **{len(strings)}**. Proofread for typos/grammar; each is editable in‑place.\n']
for off, txt in strings:
    show = txt.replace('\\n', ' / ').replace('\\p', ' // ').replace('\\l', ' / ')
    out.append(f'- `0x{off:06X}` {show}')
open('audit/03-dialogue.md', 'w').write('\n'.join(out)+'\n')

print(f"decoded {len(strings)} strings -> audit/03-dialogue.md")
print("--- first 25 ---")
for off, txt in strings[:25]:
    print(f"  0x{off:06X}  {txt[:90].replace(chr(92)+'n',' / ')}")
