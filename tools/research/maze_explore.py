#!/usr/bin/env python3
# Resumable forest explorer using the live game as ground truth, resilient to wild
# encounters (map 1.0 has grass): after each step detect a battle via gMain.callback2;
# if a wild battle fired, RUN from it to recover a clean field state. Landing on a
# Pidgeotto trigger tile fires the scripted battle -> saved as ss/pidg_trigger.ss.
import subprocess, re, os, shutil, pickle
from collections import deque

ROM='tvtest/forest_test.gba'
GOALS={(6,34),(7,34),(8,34),(12,34),(13,34),(14,34)}
FIELD_CB2=0x080565b5
ENV=dict(os.environ); ENV['LD_LIBRARY_PATH']=os.getcwd()+'/prefix/lib64:'+os.getcwd()+'/prefix/lib'
DIRS=['DOWN','RIGHT','LEFT','UP']; CAP=700
os.makedirs('ss',exist_ok=True)

def rig(ss_in, script, ss_out):
    open('ex.rig','w').write("flash1m\n"+script+"loc\npeek32 0x030030f4\nsave %s\n"%ss_out)
    r=subprocess.run(['./rig',ROM,'ex.rig',ss_in],env=ENV,capture_output=True,text=True).stderr
    p=re.findall(r'pos=\((\d+),(\d+)\)',r); cb=re.findall(r'0x030030f4 = 0x([0-9a-f]+)',r)
    loc=(int(p[-1][0]),int(p[-1][1])) if p else None
    cb2=int(cb[-1],16) if cb else 0
    return loc,cb2

def ssf(t): return 'ss/%d_%d.ss'%t
RUN_BATTLE=("frames 140\nkey RIGHT\nframes 10\nkey -\nframes 10\nkey DOWN\nframes 10\nkey -\nframes 10\n"
            "key A\nframes 8\nkey -\nframes 110\nkey A\nframes 8\nkey -\nframes 80\n")

def probe(src_t, d):
    loc,cb2=rig(ssf(src_t),"frames 30\nkey %s\nframes 16\nkey -\nframes 20\n"%d,'ss/tmp.ss')
    if loc is None: return ('blocked',None)
    if loc in GOALS:
        shutil.copy('ss/tmp.ss','ss/pidg_trigger.ss'); return ('GOAL',loc)
    if loc==src_t and cb2==FIELD_CB2: return ('blocked',None)
    if cb2==FIELD_CB2: return (loc,'ss/tmp.ss')
    # wild encounter fired on the step: run away to recover a clean field state at loc
    loc2,cb2b=rig('ss/tmp.ss',RUN_BATTLE,'ss/tmp2.ss')
    if cb2b==FIELD_CB2 and loc2 is not None: return (loc2,'ss/tmp2.ss')
    return ('blocked',None)  # couldn't escape; skip this edge

if os.path.exists('search.pkl'):
    visited,frontier,parent,total=pickle.load(open('search.pkl','rb')); pq=deque(frontier)
    print('resume visited',len(visited),'frontier',len(pq),'total',total,flush=True)
else:
    shutil.copy('field.ss','ss/start.ss')
    pos,_=rig('ss/start.ss',"",'ss/start.ss'); shutil.copy('ss/start.ss',ssf(pos))
    visited={pos}; pq=deque([pos]); parent={pos:None}; total=0; print('start',pos,flush=True)

gd=lambda t: min(abs(t[0]-g[0])+abs(t[1]-g[1]) for g in GOALS)
found=None; calls=0
while pq and calls<CAP:
    t=pq.popleft()
    for d in DIRS:
        res,info=probe(t,d); calls+=1; total+=1
        if res=='GOAL': parent[info]=t; found=info; print('*** TRIGGER',info,'via',d,'from',t,flush=True); break
        if res=='blocked': continue
        new=res
        if new not in visited:
            visited.add(new); parent[new]=t; shutil.copy(info,ssf(new)); pq.append(new)
            if len(visited)%15==0: print(' visited',len(visited),'fr',len(pq),'at',new,'gd',gd(new),flush=True)
    if found: break

pickle.dump((visited,list(pq),parent,total),open('search.pkl','wb'))
if found:
    path=[]; c=found
    while parent[c] is not None: path.append(c); c=parent[c]
    open('PIDG_PATH.txt','w').write(repr(path[::-1])); print('FOUND len',len(path),flush=True)
else:
    b=min(visited,key=gd); print('chunk done probes',calls,'visited',len(visited),'fr',len(pq),'closest',b,'gd',gd(b),flush=True)
