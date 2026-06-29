#!/usr/bin/env python3
# Drive the rig one step at a time, using the live game as the movement oracle.
# BFS over a best-effort collision/elevation model; when a step doesn't land where
# planned, mark that edge blocked and re-plan. Stops when the player reaches a
# Pidgeotto trigger tile (which fires the scripted battle via natural stepping).
import subprocess, re, sys, os, shutil
from collections import deque

ROM='tvtest/forest_test.gba'
START='field.ss'; CUR='cur.ss'
GOALS={(6,34),(7,34),(8,34),(12,34),(13,34),(14,34)}
ENV=dict(os.environ); ENV['LD_LIBRARY_PATH']=os.getcwd()+'/prefix/lib64:'+os.getcwd()+'/prefix/lib'

ag=open(ROM,'rb').read()
u16=lambda o: ag[o]|ag[o+1]<<8
u32=lambda o: int.from_bytes(ag[o:o+4],'little')
off=lambda a: a-0x08000000 if a and 0x08000000<=a<0x08000000+len(ag) else None
bankarr=off(u32(0x5524C)); maparr=off(u32(bankarr+4)); hdr=off(u32(maparr)); lay=off(u32(hdr))
W=u32(lay+0); H=u32(lay+4); grid=off(u32(lay+0xC))
evp=off(u32(hdr+4)); nObj=ag[evp]; objp=off(u32(evp+4))
objt=set((u16(objp+24*i+4),u16(objp+24*i+6)) for i in range(nObj))
def tl(x,y): return u16(grid+2*(y*W+x)) if 0<=x<W and 0<=y<H else None
def cz(x,y):
    t=tl(x,y); return -1 if t is None else (t>>10)&3
def ev(x,y):
    t=tl(x,y); return -1 if t is None else (t>>12)&0xF
def walk(x,y): return cz(x,y)==0 and (x,y) not in objt
blocked=set()  # discovered blocked edges (a,b)
def can(a,b):
    if not walk(*b): return False
    if (a,b) in blocked: return False
    ea,eb=ev(*a),ev(*b)
    return ea==eb or ea==0 or eb==0
DIRS={'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}
def bfs(src):
    prev={src:None}; q=deque([src])
    while q:
        c=q.popleft()
        if c in GOALS:
            path=[]
            while prev[c] is not None: p,d=prev[c]; path.append((d,c)); c=p
            return path[::-1]
        for d,(dx,dy) in DIRS.items():
            n=(c[0]+dx,c[1]+dy)
            if n not in prev and can(c,n): prev[n]=(c,d); q.append(n)
    return None

def step(direction):
    open('step.rig','w').write("flash1m\nkey %s\nframes 16\nkey -\nframes 26\nloc\nsave %s\n"%(direction,CUR))
    r=subprocess.run(['./rig',ROM,'step.rig',CUR],env=ENV,capture_output=True,text=True)
    m=re.findall(r'pos=\((\d+),(\d+)\)',r.stderr)
    return (int(m[-1][0]),int(m[-1][1])) if m else None

shutil.copy(START,CUR)
# initial pos
open('step.rig','w').write("flash1m\nloc\n")
r=subprocess.run(['./rig',ROM,'step.rig',CUR],env=ENV,capture_output=True,text=True)
m=re.findall(r'pos=\((\d+),(\d+)\)',r.stderr); pos=(int(m[-1][0]),int(m[-1][1]))
print('start',pos,flush=True)
for it in range(300):
    if pos in GOALS:
        print('REACHED TRIGGER',pos,'after',it,'steps',flush=True); break
    path=bfs(pos)
    if not path: print('NO PATH from',pos,flush=True); break
    d,expect=path[0]
    new=step(d)
    if new is None: print('step err',flush=True); break
    if new==pos:
        blocked.add((pos,expect)); print('blocked',pos,'->',expect,'(%s)'%d,flush=True)
    elif new!=expect:
        # slid/overshot; accept actual, drop stale plan
        print('moved',pos,'->',new,'(planned %s)'%expect,flush=True); pos=new
    else:
        pos=new
        if pos in GOALS: print('REACHED TRIGGER',pos,flush=True); break
    if it%10==0: print('  at',pos,'goal-dist',min(abs(pos[0]-g[0])+abs(pos[1]-g[1]) for g in GOALS),flush=True)
print('FINAL',pos,flush=True)
