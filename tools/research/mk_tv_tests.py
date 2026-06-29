#!/usr/bin/env python3
"""Build throwaway test ROMs that redirect the bedroom-TV string pointer (operand at
0x82018A) to each fixed string, so the rig can screenshot them rendered live in-engine.
These ROMs are TEST FIXTURES ONLY — not the shipped patch."""
import sys, os, shutil

FORK = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tvtest")
os.makedirs(OUT, exist_ok=True)

PTR_OPERAND = 0x82018A   # the 4-byte loadpointer operand the TV reads its text from
TESTS = [
    ("T1",  0x834CC0),   # "I like playing out in the streets!..."
    ("T2a", 0xC00000),   # "AJ: Today all my sacrifices and..."
    ("T2b", 0x814023),   # "{PLAYER} received the BIG MUSHROOM from CASSANDRA!"
    ("T2c", 0x867875),   # "{PLAYER} received the FERTILIZER from FLORINDA!"
]
base = open(FORK, "rb").read()
for label, start in TESTS:
    rom = bytearray(base)
    ptr = (0x08000000 + start).to_bytes(4, "little")
    rom[PTR_OPERAND:PTR_OPERAND+4] = ptr
    path = os.path.join(OUT, f"tv_{label}.gba")
    open(path, "wb").write(rom)
    print(f"{label}: TV -> 0x{0x08000000+start:08X}  wrote {path}")
print("done. (checkpoint.ss is reusable: only 4 ROM bytes differ, RAM state identical)")
