#!/usr/bin/env python3
"""D1 box-reserve fix: make PSS skip hazard boxes {1,2,5} (=Box 2/3/6) during
manual L/R box navigation, so a Pokemon can never be placed in a slot that
overlaps the 0x6xxx story vars. Patches the two inline UI step handlers to call
free-space skip-hazard helpers. usage: fix_boxreserve.py in.gba out.gba"""
import sys, struct

IN, OUT = sys.argv[1], sys.argv[2]
rom = bytearray(open(IN, 'rb').read())

HELPERS_VA = 0x08197600          # free space (43KB FF run @0x08197594), 4-aligned
def off(va): return va - 0x08000000

def bl(src_va, dst_va):
    """Thumb-1 BL (two halfwords, little-endian bytes) from src_va to dst_va."""
    o = dst_va - (src_va + 4)
    assert -0x400000 <= o < 0x400000, f'BL out of range: 0x{src_va:08x} -> 0x{dst_va:08x} (offset {o:#x}, limit ±4MB)'
    h1 = 0xF000 | ((o >> 12) & 0x7FF)
    h2 = 0xF800 | ((o >> 1) & 0x7FF)
    return struct.pack('<HH', h1, h2)

# ---- helper bodies (Thumb), r0 = cur box in/out; leaf, only touches r0 ----
# NextSafeFwd: do { box=(box+1); if box>13 box=0 } while box in {1,2,5}
NEXT = bytes.fromhex("0130 0d28 00dd 0020 0128 f9d0 0228 f7d0 0528 f5d0 7047".replace(" ", ""))
# PrevSafeBwd: do { box=(box-1); if box<0 box=13 } while box in {1,2,5}
PREV = bytes.fromhex("0138 0028 00da 0d20 0128 f9d0 0228 f7d0 0528 f5d0 7047".replace(" ", ""))
NEXT_VA = HELPERS_VA
PREV_VA = HELPERS_VA + len(NEXT)

# ---- call-site original bytes (sanity check) ----
RIGHT_VA = 0x0808d46e   # adds r0,#1; ldr r2,=2ca; adds r1,r1,r2; strh; cmp/ble/movs0/strh  (16B)
LEFT_VA  = 0x0808d4a6   # subs r0,#1; ...; cmp/bge/movs13/strh                                 (16B)
RIGHT_ORIG = bytes.fromhex("0130074a891808800d2801dd00200880")
LEFT_ORIG  = bytes.fromhex("0138074a89180880002801da0d200880")

def check(va, want):
    got = bytes(rom[off(va):off(va)+len(want)])
    if got != want:
        print(f"!! mismatch @{va:08x}\n  want {want.hex()}\n  got  {got.hex()}")
        sys.exit(1)

# ---- new call-site bytes: BL helper; ldr r2,[pc,#0x1c]; ldr r1,[r4]; adds r1,r1,r2; strh r0,[r1]; nop;nop
TAIL = bytes.fromhex("074a 2168 8918 0880 c046 c046".replace(" ", ""))   # 12 bytes
right_new = bl(RIGHT_VA, NEXT_VA) + TAIL
left_new  = bl(LEFT_VA,  PREV_VA) + TAIL
assert len(right_new) == 16 and len(left_new) == 16

# ---- auto-deposit (CopyMonToPC-style) box-scan wraps: replace inline
#      "adds rBox,#1; cmp rBox,#0xe; bne; movs rBox,#0" (8B) with
#      "mov r0,rBox; bl NextSafeFwd; mov rBox,r0" so a caught mon never lands in a hazard box.
DEP_A_VA, DEP_A_REG = 0x08040c1a, 5   # scan A @0x08040b90 (give-mon module)
DEP_B_VA, DEP_B_REG = 0x080cc85e, 4   # scan B @0x080cc7f8 (storage helper)
DEP_A_ORIG = bytes.fromhex("01350e2d00d10025")
DEP_B_ORIG = bytes.fromhex("01340e2c00d10024")
def deposit_hook(wrap_va, boxreg):
    mov_in  = struct.pack('<H', 0x1C00 | (boxreg << 3))   # adds r0, rBox, #0
    mov_out = struct.pack('<H', 0x1C00 | boxreg)          # adds rBox, r0, #0
    return mov_in + bl(wrap_va + 2, NEXT_VA) + mov_out     # 2 + 4 + 2 = 8 bytes
depA_new = deposit_hook(DEP_A_VA, DEP_A_REG)
depB_new = deposit_hook(DEP_B_VA, DEP_B_REG)
assert len(depA_new) == 8 and len(depB_new) == 8

# ---- "Deposit in which BOX?" selector (ChooseBoxMenu) — its OWN box-step handlers,
#      box index @ *(0x020397ac)+0x244. Forward @0x0808cc10, backward @0x0808cc44.
#      A manual deposit could otherwise target hazard Box 2/3 (verified live).
NOP = bytes.fromhex("c046")
# Forward: at 0x0808cc1c `ldrb r0,[r1]` leaves r0=box, r1=&box. Replace 0x0808cc1e..35 (24B).
CB_F_VA = 0x0808cc1e
CB_F_ORIG = bytes.fromhex("013008700006000e0d2805d9106891218900401800210170")
cbF_new = bl(CB_F_VA, NEXT_VA) + bytes.fromhex("0870") + NOP * 9       # bl; strb r0,[r1]; nop*9
# Backward: mirror the (working) forward pattern, BUT 0x0808cc5c..5f holds the handler's own
#   literal-pool word 0x020397ac (read by `ldr r0,[pc,#0x14]` @0x0808cc46) — must be preserved, and
#   branched over (not executed). Replace 0x0808cc4e..69 (28B):
#   adds r1,r2,r1; ldrb r0,[r1]; bl PrevSafeBwd; strb r0,[r1]; b 0x0808cc6a; pad; <literal>; nop*5
CB_B_VA = 0x0808cc4e
CB_B_ORIG = bytes.fromhex("50180078002804d0411e03e00000ac9703020d2191239b00d0180170")
LITERAL = bytes.fromhex("ac970302")   # 0x020397ac, must stay @0x0808cc5c (offset 14 in this region)
cbB_new = (bytes.fromhex("5118") + bytes.fromhex("0878") + bl(0x0808cc52, PREV_VA)
           + bytes.fromhex("0870") + bytes.fromhex("07e0") + bytes.fromhex("0000")
           + LITERAL + NOP * 5)
assert cbB_new[14:18] == LITERAL, cbB_new[14:18].hex()
assert len(cbF_new) == 24 and len(cbB_new) == 28

# ---- already applied? (all 8 regions carry the new bytes) -> pass input through ----
def region(va, n): return bytes(rom[off(va):off(va)+n])
if (region(NEXT_VA, len(NEXT)) == NEXT and region(PREV_VA, len(PREV)) == PREV
        and region(RIGHT_VA, 16) == right_new and region(LEFT_VA, 16) == left_new
        and region(DEP_A_VA, 8) == depA_new and region(DEP_B_VA, 8) == depB_new
        and region(CB_F_VA, 24) == cbF_new and region(CB_B_VA, 28) == cbB_new):
    open(OUT, 'wb').write(rom)
    print('box-reserve already applied — output written unchanged')
    sys.exit(0)

# ---- original-byte guards (all call sites) ----
check(RIGHT_VA, RIGHT_ORIG)
check(LEFT_VA,  LEFT_ORIG)
check(DEP_A_VA, DEP_A_ORIG)
check(DEP_B_VA, DEP_B_ORIG)
check(CB_F_VA, CB_F_ORIG)
check(CB_B_VA, CB_B_ORIG)

# ---- verify helper free space is FF ----
for va, body in ((NEXT_VA, NEXT), (PREV_VA, PREV)):
    region = rom[off(va):off(va)+len(body)]
    if any(b != 0xFF for b in region):
        print(f"!! helper space @{va:08x} not free: {region.hex()}"); sys.exit(1)

# ---- apply ----
rom[off(NEXT_VA):off(NEXT_VA)+len(NEXT)] = NEXT
rom[off(PREV_VA):off(PREV_VA)+len(PREV)] = PREV
rom[off(RIGHT_VA):off(RIGHT_VA)+16] = right_new
rom[off(LEFT_VA):off(LEFT_VA)+16]   = left_new
rom[off(DEP_A_VA):off(DEP_A_VA)+8]  = depA_new
rom[off(DEP_B_VA):off(DEP_B_VA)+8]  = depB_new
rom[off(CB_F_VA):off(CB_F_VA)+24]   = cbF_new
rom[off(CB_B_VA):off(CB_B_VA)+28]   = cbB_new

open(OUT, 'wb').write(rom)
print(f"NextSafeFwd @{NEXT_VA:08x}  PrevSafeBwd @{PREV_VA:08x}")
print(f"RIGHT hook @{RIGHT_VA:08x}: {right_new.hex()}")
print(f"LEFT  hook @{LEFT_VA:08x}: {left_new.hex()}")
print(f"depA  hook @{DEP_A_VA:08x}: {depA_new.hex()}")
print(f"depB  hook @{DEP_B_VA:08x}: {depB_new.hex()}")
print(f"cbFwd hook @{CB_F_VA:08x}: {cbF_new.hex()}")
print(f"cbBwd hook @{CB_B_VA:08x}: {cbB_new.hex()}")
print(f"wrote {OUT}")
