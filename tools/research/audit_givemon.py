#!/usr/bin/env python3
"""Audit every givemon (0x79) gift event: is it guarded by a getpartysize<6 check,
or does it rely on givemon's box-fallback (the path that can confuse players who
deposit a mon to 'make room')? Print species, level, and the preceding ~16 bytes so
we can see the guard."""
import struct
ag = open('../ashgray-fork/rom/ashgray.gba', 'rb').read()
ROM = 0x08000000

SPECIES = {1:'BULBASAUR',4:'CHARMANDER',7:'SQUIRTLE',25:'PIKACHU',44:'GLOOM',
           133:'EEVEE',147:'DRATINI',106:'HITMONLEE',107:'HITMONCHAN',138:'OMANYTE',
           140:'KABUTO',131:'LAPRAS',137:'PORYGON',143:'SNORLAX'}

def name(sp):
    return SPECIES.get(sp, f'#{sp}')

hits = []
i = 0x700000
while i < 0xC11000:
    i = ag.find(b'\x79', i + 1)
    if i < 0 or i >= 0xC11000:
        break
    sp = struct.unpack('<H', ag[i+1:i+3])[0]
    lvl = ag[i+3]
    # plausible givemon: species 1..411, level 1..100, and item u16 follows
    if 1 <= sp <= 411 and 1 <= lvl <= 100:
        # require the next bytes look like givemon tail (item u16 then 3 zero bytes commonly)
        pre = ag[i-12:i]
        # heuristic guard detection: getpartysize(0x4F? no) -> getpartysize op = 0x59? Actually
        # 'getpartysize' special. In FR scripts it's 'special 0x...'/ 'getpartysize'=0x4F? We saw
        # 0x8107BC: getpartysize was a single opcode. Let's just print context.
        hits.append((i, sp, lvl, pre))
    if len(hits) > 200:
        break
seen = set()
for off, sp, lvl, pre in hits:
    key = (sp, lvl)
    tag = name(sp)
    # only show recognizable gift species or ones with a getpartysize-like guard nearby
    print(f'@{off:#x}: givemon {tag} lvl={lvl}  pre={pre.hex(" ")}')
