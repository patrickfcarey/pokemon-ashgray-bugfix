#!/usr/bin/env python3
"""Targeted dialogue fixes.
 - same-length word swap  -> in-place byte overwrite
 - length-changing word   -> rewrite whole string into free space, repoint its
   loadpointer (0F) references. Old string left orphaned (harmless)."""
ag = bytearray(open('rom/ashgray.gba', 'rb').read()); ROM = 0x08000000
CH = {0x00:' ', 0xFE:'\\n', 0xFB:'\\p', 0xFA:'\\l'}
for i,c in enumerate('0123456789'): CH[0xA1+i]=c
for i in range(26): CH[0xBB+i]=chr(65+i)
for i in range(26): CH[0xD5+i]=chr(97+i)
CH.update({0xAB:'!',0xAC:'?',0xAD:'.',0xAE:'-',0xB0:'…',0xB8:',',0xBA:'/',0xB5:'♂',0xB6:'♀',
 0xF0:':',0xB1:'“',0xB2:'”',0xB4:'’',0xB3:'‘'})
ENC = {v:k for k,v in CH.items()}
def encw(w): return bytes(ENC[c] for c in w)

def find_all(seq, lo=0):
    out=[]; i=lo
    while True:
        j=ag.find(seq, i)
        if j<0: break
        out.append(j); i=j+1
    return out

def strbounds(p):
    s=p
    while s>0 and ag[s-1]!=0xFF: s-=1
    e=p
    while e<len(ag) and ag[e]!=0xFF: e+=1
    return s, e
def show(p):
    s,e = strbounds(p)
    return ''.join(CH.get(b,'[%02X]'%b) for b in ag[s:e])

# free-space cursor (verified 0xFF)
def find_free(size):
    run=0; start=None
    for o in range(0xC00000, len(ag)):
        if ag[o]==0xFF:
            if start is None: start=o
            run+=1
            if run>=size: return start
        else:
            start=None; run=0
    raise RuntimeError('no free space')
CUR=[find_free(0x2000)]
def alloc(n):
    o=CUR[0]; assert all(b==0xFF for b in ag[o:o+n]); CUR[0]=o+n; return o

def inplace(bad, good):
    assert len(bad)==len(good)
    b,g=encw(bad),encw(good); hits=find_all(b)
    for h in hits:
        print(f'  [inplace] 0x{h:06X}  "{show(h)}"')
        ag[h:h+len(g)]=g
        print(f'        ->  "{show(h)}"')
    return len(hits)

def repoint(bad, good):
    b=encw(bad); hits=find_all(b); n=0
    for h in hits:
        s,e=strbounds(h)
        print(f'  [repoint] string 0x{s:06X}  "{show(h)}"')
        new=bytes(ag[s:e]).replace(b, encw(good))
        no=alloc(len(new)+1); ag[no:no+len(new)]=new; ag[no+len(new)]=0xFF
        oldp=(ROM+s).to_bytes(4,'little'); newp=(ROM+no).to_bytes(4,'little')
        upd=sum(1 for r in find_all(oldp) if r>=2 and ag[r-2]==0x0F and (ag.__setitem__(slice(r,r+4),newp) or True))
        print(f'        -> moved to 0x{no:06X}, {upd} loadpointer ref(s) updated:  "{show(no)}"')
        n+=1
    return n

print('=== recieved -> received (same length, in-place) ===')
inplace('recieved', 'received')
print('=== sacrfices -> sacrifices (longer, repoint) ===')
repoint('sacrfices', 'sacrifices')
open('rom/ashgray.gba','wb').write(ag)
print('written rom/ashgray.gba')
