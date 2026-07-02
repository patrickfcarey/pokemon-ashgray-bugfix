#!/usr/bin/env bash
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$(readlink -f "$0")")"
# PINNED: rig.c reaches into mgba INTERNAL structs (ARMCore, GBASavedata, memory fn
# pointers) — a different mgba revision can silently change their layout and corrupt
# results without failing the build. This is the commit the harness was verified on.
MGBA_COMMIT=92621ea01d7a809b0cd3b1a687f30f0ea8db7c7a
if [ ! -d mgba ]; then
  git init -q mgba
  git -C mgba remote add origin https://github.com/mgba-emu/mgba.git
  git -C mgba fetch --depth 1 origin "$MGBA_COMMIT" 2>&1 | tail -2
  git -C mgba checkout -q FETCH_HEAD
fi
cd mgba && mkdir -p build && cd build
echo "=== configure ==="
cmake .. -DCMAKE_INSTALL_PREFIX="$PWD/../../prefix" -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_QT=OFF -DBUILD_SDL=OFF -DBUILD_GL=OFF -DBUILD_GLES2=OFF -DBUILD_GLES3=OFF \
  -DBUILD_LIBRETRO=OFF -DBUILD_PYTHON=OFF -DBUILD_TEST=OFF -DBUILD_SUITE=OFF \
  -DUSE_FFMPEG=OFF -DUSE_PNG=OFF -DUSE_LIBZIP=OFF -DUSE_MINIZIP=OFF -DUSE_SQLITE3=OFF \
  -DUSE_ELF=OFF -DUSE_EDITLINE=OFF -DUSE_LZMA=OFF -DUSE_DISCORD_RPC=OFF -DUSE_EPOXY=OFF \
  -DENABLE_SCRIPTING=OFF -DBUILD_SHARED=ON -DBUILD_STATIC=OFF 2>&1 | tail -20
echo "=== build (lib only) ==="
make -j"$(nproc)" 2>&1 | tail -15
echo "=== install ==="
make install 2>&1 | tail -6
echo "=== artifacts ==="
find ../../prefix -name 'libmgba*' 2>/dev/null
ls ../../prefix/include/mgba/core/core.h 2>/dev/null && echo "headers OK"
