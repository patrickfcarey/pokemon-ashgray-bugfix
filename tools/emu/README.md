# Headless verification harness (libmgba)

Boots the ROM and screenshots frames with **no display** — so fixes can be checked
without anyone playing through the game.

## Build (one-time)
Needs `gcc` + `cmake` (`pip install --user cmake`). Built under `_emu/` at the repo root:
1. `git clone --depth 1 https://github.com/mgba-emu/mgba` → cmake with Qt/SDL/PNG/ffmpeg/
   libzip/sqlite OFF → `make` → `libmgba.so` + headers in `prefix/`.
2. Compile `shot.c` with the **same defines the lib used** —
   `-DENABLE_VFS -DENABLE_DIRECTORIES -DENABLE_DEBUGGERS -DM_CORE_GBA -DM_CORE_GB`.
   (Mismatch ⇒ `struct mCore` layout shifts and `core->init` resolves to NULL → segfault.
   Read the real defines from the build's `CMakeFiles/mgba.dir/flags.make`.)

## Use
    run.sh <rom> <frames> <out.png>
- `shot.c` — load ROM via `GBACoreCreate()`, run N frames, dump the 240×160 RGBA framebuffer.
  Sets a silent `mLogger` (mgba logs BIOS SWIs to stdout otherwise).
- `raw2png.py` — framebuffer → PNG in pure stdlib (we skipped libpng).

## Status / next
- ✅ boot + screenshot working (fork ROM renders the intro starfield).
- ⏭ inject key input + poke FireRed save-state RAM (map id / coords / story flags) to
  **warp to a specific NPC and screenshot its dialogue** → verify text fixes in-game and
  trigger logic/freeze bugs (L1–L9) headlessly.
