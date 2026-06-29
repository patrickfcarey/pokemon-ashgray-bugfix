#!/usr/bin/env python3
ag = open('../ashgray-fork/rom/ashgray.gba','rb').read()
names = {0x00:'face_down',0x01:'face_up',0x02:'face_left',0x03:'face_right',
         0x08:'walk_slow_down',0x09:'walk_slow_up',0x0A:'walk_slow_left',0x0B:'walk_slow_right',
         0x10:'walk_down',0x11:'walk_up',0x12:'walk_left',0x13:'walk_right',
         0x1D:'walk_fast_down',0x1E:'walk_fast_up',0x1F:'walk_fast_left',0x20:'walk_fast_right',
         0x4A:'face_player',0x62:'emote_!',0x63:'emote_?',0xFE:'END'}
for label, a in (('mom post-talk 0x820409', 0x820409), ('scene-A mom move 0x8203F2', 0x8203F2)):
    seq = []
    o = a
    while ag[o] != 0xFE and o < a+30:
        seq.append(names.get(ag[o], f'{ag[o]:#04x}'))
        o += 1
    print(f'{label}: {" ".join(seq)} END')
