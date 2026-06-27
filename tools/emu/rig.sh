#!/usr/bin/env bash
# Build (if needed) and run the command-driven rig.
#   rig.sh <rom> <script> [preload.ss]
# Compiles rig.c with the SAME defines the libmgba build used (struct-ABI must match).
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd /tank/backups/media_3x/roms/consoles/pokemon_romhacks/_emu
PFX="$PWD/prefix"; export LD_LIBRARY_PATH="$PFX/lib64:$PFX/lib:${LD_LIBRARY_PATH:-}"
DEFS="-DENABLE_VFS -DENABLE_DIRECTORIES -DENABLE_DEBUGGERS -DM_CORE_GBA -DM_CORE_GB -D_GNU_SOURCE"
if [ ! -x rig ] || [ rig.c -nt rig ]; then
  echo "=== compile rig ==="
  gcc -O2 $DEFS rig.c -I"$PFX/include" -L"$PFX/lib64" -L"$PFX/lib" -lmgba -lm -lz -o rig 2>&1 | tail -25 || { echo COMPILE-FAIL; exit 1; }
fi
ROM="$1"; SCRIPT="$2"; PRE="${3:-}"
echo "=== run: $(basename "$ROM") < $SCRIPT ==="
./rig "$ROM" "$SCRIPT" $PRE > dims.txt 2> rig.log; rc=$?
cat rig.log
[ $rc -ne 0 ] && { echo "rig rc=$rc"; exit $rc; }
# Convert every .raw shot produced this run to PNG
read -r W H < dims.txt
shopt -s nullglob
for r in *.raw; do
  png="${r%.raw}.png"
  python3 raw2png.py "$r" "$W" "$H" "$png" RGB >/dev/null 2>&1 && echo "png: $png"
done
true
