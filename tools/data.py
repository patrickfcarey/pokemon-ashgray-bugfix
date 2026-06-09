#!/usr/bin/env python3
"""Locate gBaseStats (via Bulbasaur's stat signature) and compare Pokémon types
between clean FireRed and the fork — to confirm/deny D6 (Onix type wrong)."""
fr = open('base/firered.gba','rb').read(); ag = open('rom/ashgray.gba','rb').read()
TYPE = ['Normal','Fight','Flying','Poison','Ground','Rock','Bug','Ghost','Steel','???',
        'Fire','Water','Grass','Electric','Psychic','Ice','Dragon','Dark']
sig = bytes([45,49,49,45,65,65,12,3])   # Bulbasaur HP,Atk,Def,Spd,SpA,SpD,type1(Grass),type2(Poison)
i = fr.find(sig)
base = i - 28                            # species 1 = Bulbasaur; species 0 is the dummy entry
print(f'gBaseStats @0x{base:06X} (FireRed)')
def types(rom, idx):
    o = base + idx*28
    return TYPE[rom[o+6]], TYPE[rom[o+7]]
for idx, name in [(1,'Bulbasaur'),(74,'Geodude'),(95,'Onix'),(208,'Steelix')]:
    f = types(fr, idx); a = types(ag, idx)
    flag = '   <-- DIFFERS' if f != a else ''
    print(f'  #{idx:3} {name:10}  FireRed {f}   AshGray {a}{flag}')
