#!/usr/bin/env bash
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$(readlink -f "$0")")"
[ -d mgba ] || git clone --depth 1 https://github.com/mgba-emu/mgba.git 2>&1 | tail -2
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
