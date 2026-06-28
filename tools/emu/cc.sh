#!/usr/bin/env bash
# Compile rig.c against the local libmgba build (same defines as the lib).
cd /tank/backups/media_3x/roms/consoles/pokemon_romhacks/_emu
PFX="$PWD/prefix"
DEFS="-DENABLE_VFS -DENABLE_DIRECTORIES -DENABLE_DEBUGGERS -DM_CORE_GBA -DM_CORE_GB -D_GNU_SOURCE"
gcc -O2 $DEFS rig.c -I"$PFX/include" -L"$PFX/lib64" -L"$PFX/lib" -lmgba -lm -lz -o rig 2>&1 | tail -8
echo "compile rc=${PIPESTATUS[0]}"
