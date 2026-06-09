#!/usr/bin/env bash
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd /tank/backups/media_3x/roms/consoles/pokemon_romhacks/_emu
PFX="$PWD/prefix"
export LD_LIBRARY_PATH="$PFX/lib64:$PFX/lib:${LD_LIBRARY_PATH:-}"
if [ ! -x shot ] || [ shot.c -nt shot ]; then
  echo "=== compile ==="
  DEFS="-DENABLE_VFS -DENABLE_DIRECTORIES -DENABLE_DEBUGGERS -DM_CORE_GBA -DM_CORE_GB -D_GNU_SOURCE"
  gcc -O2 $DEFS shot.c -I"$PFX/include" -L"$PFX/lib64" -L"$PFX/lib" -lmgba -lm -lz -o shot 2>&1 | tail -25 || { echo COMPILE-FAIL; exit 1; }
fi
ROM="$1"; FRAMES="${2:-300}"; OUT="${3:-out.png}"; ORDER="${4:-RGB}"
echo "=== run: $(basename "$ROM") for $FRAMES frames ==="
./shot "$ROM" "$FRAMES" frame.raw > dims.txt 2> shot.log; rc=$?
cat shot.log
[ $rc -ne 0 ] && { echo "shot rc=$rc"; exit $rc; }
read -r W H < dims.txt
python3 raw2png.py frame.raw "$W" "$H" "$OUT" "$ORDER"
