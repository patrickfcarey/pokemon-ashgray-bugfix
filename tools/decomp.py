#!/usr/bin/env python3
"""FireRed event-script decompiler. Full Gen3/FireRed command table (opcode lengths
derived from pret/pokefirered asm/macros/event.inc). Recurses through call/goto/if
branches; stops only on the genuinely variable-length trainerbattle or a bad opcode.
Usage: decomp.py [bank,map | 0xOFFSET] ..."""
import sys
ag = open('rom/ashgray.gba', 'rb').read(); ROM = 0x08000000
def u16(o): return ag[o] | ag[o+1] << 8
def u32(o): return ag[o] | ag[o+1]<<8 | ag[o+2]<<16 | ag[o+3]<<24
def pf(o):
    if o+4 > len(ag): return None
    v = u32(o); return v-ROM if 0x08000000 <= v < 0x08000000+len(ag) else None
CH = {0x00:' '}
for i,c in enumerate('0123456789'): CH[0xA1+i]=c
for i in range(26): CH[0xBB+i]=chr(65+i)
for i in range(26): CH[0xD5+i]=chr(97+i)
CH.update({0xAB:'!',0xAC:'?',0xAD:'.',0xAE:'-',0xB0:'…',0xB8:',',0xBA:'/',0xB5:'♂',0xB6:'♀',
 0xF0:':',0xB1:'“',0xB2:'”',0xB4:'’',0xB3:'‘',0x1B:'é'})
def dtext(o):
    if o is None or o >= len(ag): return '<bad ptr>'
    s=[]; i=o; lim=o+300
    while 0 <= i < len(ag) and i < lim:
        b=ag[i]
        if b==0xFF: break
        if b==0xFE: s.append('\\n')
        elif b==0xFB: s.append('\\p')
        elif b==0xFA: s.append('\\l')
        elif b in (0xFD,0xFC): s.append('{%02X%02X}'%(b, ag[i+1] if i+1<len(ag) else 0)); i+=2; continue
        elif b in CH: s.append(CH[b])
        else: s.append('[%02X]'%b)
        i+=1
    return ''.join(s)

# opcode -> (name, total byte length incl. opcode).  Full FireRed table.
T={
0x00:('nop',1),0x01:('nop1',1),0x02:('end',1),0x03:('return',1),0x04:('call',5),0x05:('goto',5),
0x06:('goto_if',6),0x07:('call_if',6),0x08:('gotostd',2),0x09:('callstd',2),0x0A:('gotostd_if',3),
0x0B:('callstd_if',3),0x0C:('returnram',1),0x0D:('endram',1),0x0E:('setmysteryeventstatus',2),
0x0F:('loadword',6),0x10:('loadbyte',3),0x11:('setptr',6),0x12:('loadbytefromptr',6),0x13:('setptrbyte',6),
0x14:('copylocal',3),0x15:('copybyte',9),0x16:('setvar',5),0x17:('addvar',5),0x18:('subvar',5),
0x19:('copyvar',5),0x1A:('setorcopyvar',5),0x1B:('cmp_ll',3),0x1C:('cmp_lv',3),0x1D:('cmp_lp',6),
0x1E:('cmp_pl',6),0x1F:('cmp_pv',6),0x20:('cmp_pp',9),0x21:('compare',5),0x22:('compare_vv',5),
0x23:('callnative',5),0x24:('gotonative',5),0x25:('special',3),0x26:('specialvar',5),0x27:('waitstate',1),
0x28:('delay',3),0x29:('setflag',3),0x2A:('clearflag',3),0x2B:('checkflag',3),0x2C:('initclock',5),
0x2D:('dotimebasedevents',1),0x2E:('gettime',1),0x2F:('playse',3),0x30:('waitse',1),0x31:('playfanfare',3),
0x32:('waitfanfare',1),0x33:('playbgm',4),0x34:('savebgm',3),0x35:('fadedefaultbgm',1),0x36:('fadenewbgm',3),
0x37:('fadeoutbgm',2),0x38:('fadeinbgm',2),0x39:('warp',8),0x3A:('warpsilent',8),0x3B:('warpdoor',8),
0x3C:('warphole',3),0x3D:('warpteleport',8),0x3E:('setwarp',8),0x3F:('setdynamicwarp',8),0x40:('setdivewarp',8),
0x41:('setholewarp',8),0x42:('getplayerxy',5),0x43:('getpartysize',1),0x44:('additem',5),0x45:('removeitem',5),
0x46:('checkitemspace',5),0x47:('checkitem',5),0x48:('checkitemtype',3),0x49:('addpcitem',5),0x4A:('checkpcitem',5),
0x4B:('adddecoration',3),0x4C:('removedecoration',3),0x4D:('checkdecor',3),0x4E:('checkdecorspace',3),
0x4F:('applymovement',7),0x50:('applymovement_at',9),0x51:('waitmovement',3),0x52:('waitmovement_at',5),
0x53:('removeobject',3),0x54:('removeobject_at',5),0x55:('addobject',3),0x56:('addobject_at',5),
0x57:('setobjectxy',7),0x58:('showobjectat',5),0x59:('hideobjectat',5),0x5A:('faceplayer',1),
0x5B:('turnobject',4),0x5C:('trainerbattle',0),0x5D:('dotrainerbattle',1),0x5E:('gotopostbattlescript',1),
0x5F:('gotobeatenscript',1),0x60:('checktrainerflag',3),0x61:('settrainerflag',3),0x62:('cleartrainerflag',3),
0x63:('setobjectxyperm',7),0x64:('copyobjectxytoperm',3),0x65:('setobjectmovementtype',4),0x66:('waitmessage',1),
0x67:('message',5),0x68:('closemessage',1),0x69:('lockall',1),0x6A:('lock',1),0x6B:('releaseall',1),
0x6C:('release',1),0x6D:('waitbuttonpress',1),0x6E:('yesnobox',3),0x6F:('multichoice',5),
0x70:('multichoicedefault',6),0x71:('multichoicegrid',6),0x72:('drawbox',1),0x73:('erasebox',5),
0x74:('drawboxtext',5),0x75:('showmonpic',5),0x76:('hidemonpic',1),0x77:('showcontestpainting',2),
0x78:('braillemessage',5),0x79:('givemon',12),0x7A:('giveegg',3),0x7B:('setmonmove',5),0x7C:('checkpartymove',3),
0x7D:('bufferspeciesname',4),0x7E:('bufferleadmonspeciesname',2),0x7F:('bufferpartymonnick',4),
0x80:('bufferitemname',4),0x81:('bufferdecorationname',4),0x82:('buffermovename',4),0x83:('buffernumberstring',4),
0x84:('bufferstdstring',4),0x85:('bufferstring',6),0x86:('pokemart',5),0x87:('pokemartdecoration',5),
0x88:('pokemartdecoration2',5),0x89:('playslotmachine',3),0x8A:('setberrytree',4),0x8B:('choosecontestmon',1),
0x8C:('startcontest',1),0x8D:('showcontestresults',1),0x8E:('contestlinktransfer',1),0x8F:('random',3),
0x90:('addmoney',6),0x91:('removemoney',6),0x92:('checkmoney',6),0x93:('showmoneybox',4),0x94:('hidemoneybox',3),
0x95:('updatemoneybox',4),0x96:('getpokenewsactive',3),0x97:('fadescreen',2),0x98:('fadescreenspeed',3),
0x99:('setflashlevel',3),0x9A:('animateflash',2),0x9B:('messageautoscroll',5),0x9C:('dofieldeffect',3),
0x9D:('setfieldeffectargument',4),0x9E:('waitfieldeffect',3),0x9F:('setrespawn',3),0xA0:('checkplayergender',1),
0xA1:('playmoncry',5),0xA2:('setmetatile',9),0xA3:('resetweather',1),0xA4:('setweather',3),0xA5:('doweather',1),
0xA6:('setstepcallback',2),0xA7:('setmaplayoutindex',3),0xA8:('setobjectsubpriority',5),
0xA9:('resetobjectsubpriority',4),0xAA:('createvobject',8),0xAB:('turnvobject',3),0xAC:('opendoor',5),
0xAD:('closedoor',5),0xAE:('waitdooranim',1),0xAF:('setdooropen',5),0xB0:('setdoorclosed',5),
0xB1:('addelevmenuitem',8),0xB2:('showelevmenu',1),0xB3:('checkcoins',3),0xB4:('addcoins',3),0xB5:('removecoins',3),
0xB6:('setwildbattle',6),0xB7:('dowildbattle',1),0xB8:('setvaddress',5),0xB9:('vgoto',5),0xBA:('vcall',5),
0xBB:('vgoto_if',6),0xBC:('vcall_if',6),0xBD:('vmessage',5),0xBE:('vbuffermessage',5),0xBF:('vbufferstring',6),
0xC0:('showcoinsbox',3),0xC1:('hidecoinsbox',3),0xC2:('updatecoinsbox',3),0xC3:('incrementgamestat',2),
0xC4:('setescapewarp',8),0xC5:('waitmoncry',1),0xC6:('bufferboxname',4),0xC7:('textcolor',2),0xC8:('loadhelp',5),
0xC9:('unloadhelp',1),0xCA:('signmsg',1),0xCB:('normalmsg',1),0xCC:('comparestat',6),
0xCD:('setmonmodernfatefulencounter',3),0xCE:('checkmonmodernfatefulencounter',3),0xCF:('trywondercardscript',1),
0xD0:('setworldmapflag',3),0xD1:('warpspinenter',8),0xD2:('setmonmetlocation',4),0xD3:('getbraillestringwidth',5),
0xD4:('bufferitemnameplural',6),
}
TERM={0x02,0x03,0x05,0x08,0x0C,0x0D,0x24,0xB9}   # end/return/goto/gotostd/returnram/endram/gotonative/vgoto
SUB={0x04,0x05,0x06,0x07}                        # call/goto/goto_if/call_if -> recurse into pointer

def note_for(op, o):
    if op in (0x0F,): return '  text="%s"' % dtext(pf(o+2))
    if op in (0x67,0xBD): return '  text="%s"' % dtext(pf(o+1))
    if op in (0x29,0x2A,0x2B): return '  flag=0x%04X' % u16(o+1)
    if op in (0x60,0x61,0x62): return '  trainerflag=0x%04X' % u16(o+1)
    if op == 0x25: return '  special=0x%04X' % u16(o+1)
    if op == 0x26: return '  var=0x%04X special=0x%04X' % (u16(o+1), u16(o+3))
    if op in (0x16,0x17,0x18,0x19,0x1A,0x21,0x22): return '  var=0x%04X val=0x%04X' % (u16(o+1), u16(o+3))
    if op in (0x08,0x09): return '  std=%d' % ag[o+1]
    if op in (0x06,0x07,0x0A,0x0B): return '  cond=%d' % ag[o+1]
    if op in (0x44,0x45,0x46,0x47,0x49,0x4A): return '  item=0x%04X qty=%d' % (u16(o+1), u16(o+3))
    if op == 0x4F: return '  obj=0x%04X movm=0x%06X' % (u16(o+1), (pf(o+3) or 0))
    if op == 0x6E: return '  yesno'
    return ''

def decompile(start, out, visited, depth=0):
    if start is None or start in visited or depth > 60: return
    visited.add(start)
    out.append(f'\n; ---- @0x{start:06X} ----')
    o = start
    while 0 <= o < len(ag):
        op = ag[o]
        if op not in T:
            out.append(f'  0x{o:06X}: ??? 0x{op:02X}  (not a known opcode — stop)'); break
        name, ln = T[op]
        if op == 0x5C:  # trainerbattle: type-dependent length, don't guess
            out.append(f'  0x{o:06X}: trainerbattle type=0x{ag[o+1]:02X} (variable len — stop branch)'); break
        note = note_for(op, o)
        sub = pf(o + (2 if op in (0x06,0x07) else 1)) if op in SUB else None
        if sub is not None: note += '  ->0x%06X' % sub
        out.append(f'  0x{o:06X}: {name}{note}')
        if sub is not None: decompile(sub, out, visited, depth+1)
        if op in TERM: break
        o += ln

LIT = 0x5524C
def plist(off, cap):
    r=[]
    for i in range(cap):
        p=pf(off+4*i)
        if p is None: break
        r.append(p)
    return r
def header(bank, mp): return plist(plist(pf(LIT),64)[bank],150)[mp]
def scripts(hoff):
    res=[]; ev=pf(hoff+4); ms=pf(hoff+8)
    if ev:
        nP,nT,nS=ag[ev],ag[ev+2],ag[ev+3]; pP,pT,pS=pf(ev+4),pf(ev+12),pf(ev+16)
        if pP:
            for i in range(min(nP,80)):
                sp=pf(pP+i*24+16); res.append(('person%d'%i,sp)) if sp else None
        if pT:
            for i in range(min(nT,80)):
                sp=pf(pT+i*16+12); res.append(('trig%d'%i,sp)) if sp else None
        if pS:
            for i in range(min(nS,80)):
                oo=pS+i*12
                if oo+12<=len(ag) and ag[oo+5]<5:
                    sp=pf(oo+8); res.append(('sign%d'%i,sp)) if sp else None
    if ms:
        i=ms
        while i+5<=len(ag) and ag[i]!=0:
            p=pf(i+1); res.append(('mapscr_t%d'%ag[i],p)) if p else None; i+=5
    return res

args = sys.argv[1:] or ['3,0']
out=['# Ash Gray — decompiled scripts (full FireRed opcode table)\n']
for a in args:
    if ',' in a:
        b,m=map(int,a.split(',')); h=header(b,m)
        scrs=scripts(h)
        out.append(f'\n## map {b}.{m} (header 0x{h:06X}) — {len(scrs)} script refs')
        vis=set()
        for lbl,off in scrs:
            out.append(f'\n### {lbl} @0x{off:06X}')
            decompile(off,out,vis)
    else:
        off=int(a,16); decompile(off,out,set())
open('audit/06-decompile.md','w').write('\n'.join(out)+'\n')
print('-> audit/06-decompile.md\n'); print('\n'.join(out[:120]))
