#!/usr/bin/env python3
"""Scan Ash Gray's dialogue for high-precision text-error candidates."""
import re
ag = open('rom/ashgray.gba', 'rb').read()
CH = {0x00: ' '}
for i, c in enumerate('0123456789'): CH[0xA1+i] = c
for i in range(26): CH[0xBB+i] = chr(ord('A')+i)
for i in range(26): CH[0xD5+i] = chr(ord('a')+i)
CH.update({0xAB:'!',0xAC:'?',0xAD:'.',0xAE:'-',0xB0:'…',0xB1:'“',0xB2:'”',0xB3:'‘',
 0xB4:'’',0xB5:'♂',0xB6:'♀',0xB7:'$',0xB8:',',0xB9:'×',0xBA:'/',0xF0:':'})
CTRL = {0xFE:'\\n',0xFB:'\\p',0xFA:'\\l'}

def decode(o):
    s=[]; i=o
    while i < len(ag):
        b=ag[i]
        if b==0xFF: return ''.join(s), i+1
        if b in CTRL: s.append(CTRL[b]); i+=1; continue
        if b==0xFD: s.append('{V}'); i+=2; continue
        if b==0xFC: s.append('{C}'); i+=2; continue
        if b in CH: s.append(CH[b]); i+=1; continue
        return None, i
    return None, i

MISSPELL = {'teh':'the','recieve':'receive','seperate':'separate','occured':'occurred',
 'definately':'definitely','wich':'which','thier':'their','untill':'until','goin':'going',
 'becuase':'because','tommorow':'tomorrow','beleive':'believe','wierd':'weird',
 'arent':"aren't",'youre':"you're"}

flags=[]
i=0x700000
while i<0xA00000:
    txt,nxt=decode(i)
    if txt and sum(c.isalpha() for c in txt)>=10 and ('\\n' in txt or '\\p' in txt):
        norm=txt.replace('\\n',' ').replace('\\p',' ').replace('\\l',' ')
        issues=[]
        if re.search(r'(?<=\S)  +', txt): issues.append('double-space')
        m=re.search(r'\b(\w+)\s+\1\b', norm, re.I)
        if m and m.group(1).lower() not in ('that','had','no','ho'): issues.append(f'dup-word "{m.group(1)}"')
        if re.search(r'[A-Za-z] [.,!?]', txt): issues.append('space-before-punct')
        for w in re.findall(r'[A-Za-z]+', norm.lower()):
            if w in MISSPELL: issues.append(f'misspell "{w}"->"{MISSPELL[w]}"')
        if issues:
            flags.append((i, issues, txt))
        i=nxt; continue
    i+=1

out=['# Ash Gray — dialogue text-error candidates\n', f'Flagged: **{len(flags)}** strings (high-precision filters).\n']
for off,iss,txt in flags:
    out.append(f'- `0x{off:06X}` [{", ".join(iss)}]  —  {txt.replace(chr(92)+"n"," / ").replace(chr(92)+"p"," // ")[:140]}')
open('audit/04-typo-candidates.md','w').write('\n'.join(out)+'\n')
print(f"flagged {len(flags)} strings -> audit/04-typo-candidates.md")
for off,iss,txt in flags[:30]:
    print(f"  0x{off:06X} {','.join(iss):28} {txt.replace(chr(92)+'n',' / ')[:80]}")
