#!/usr/bin/env bash
# Build (if needed) and run the command-driven rig.
#   rig.sh <rom> <script> [preload.ss]
# Compiles rig.c with the SAME defines the libmgba build used (struct-ABI must match).
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$(readlink -f "$0")")"
PFX="$PWD/prefix"; export LD_LIBRARY_PATH="$PFX/lib64:$PFX/lib:${LD_LIBRARY_PATH:-}"
DEFS="-DENABLE_VFS -DENABLE_DIRECTORIES -DENABLE_DEBUGGERS -DM_CORE_GBA -DM_CORE_GB -D_GNU_SOURCE"
if [ ! -x rig ] || [ rig.c -nt rig ]; then
  echo "=== compile rig ==="
  gcc -O2 $DEFS rig.c -I"$PFX/include" -L"$PFX/lib64" -L"$PFX/lib" -lmgba -lm -lz -o rig 2>&1 | tail -25 || { echo COMPILE-FAIL; exit 1; }
fi
ROM="$1"; SCRIPT="$2"; PRE="${3:-}"
echo "=== run: $(basename "$ROM") < $SCRIPT ==="
MARK="$(mktemp)"                       # timestamp marker: .raw shots written after this = this run's
./rig "$ROM" "$SCRIPT" $PRE > dims.txt 2> rig.log; rc=$?
cat rig.log
[ $rc -ne 0 ] && { rm -f "$MARK"; echo "rig rc=$rc"; exit $rc; }
# Convert ONLY the .raw shots produced THIS run (newer than MARK) -> PNG, quietly.
# (The old loop re-converted ALL ~600 .raw every run: hundreds of output lines that
#  flooded the caller, plus hundreds of wasted python startups. That caused the
#  "e.includes" Bash-tool glitch and made every run slow.)
read -r W H < dims.txt
shopt -s nullglob
n=0
for r in *.raw; do
  [ "$r" -nt "$MARK" ] || continue
  python3 raw2png.py "$r" "$W" "$H" "${r%.raw}.png" RGB >/dev/null 2>&1 && { echo "  png: ${r%.raw}.png"; n=$((n+1)); }
done
rm -f "$MARK"
echo "=== $n shot(s) converted this run ==="
true
