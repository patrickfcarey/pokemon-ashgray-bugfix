#!/usr/bin/env bash
set -uo pipefail
cd /tank/backups/media_3x/roms/consoles/pokemon_romhacks/ashgray-fork
mkdir -p base rom audit patches
NG=/tank/backups/media_3x/roms/consoles/nintendo_gba
7z e -y "$NG/Pokemon - FireRed Version (USA, Europe).7z" -o"base" >/dev/null 2>&1
FR=$(find base -iname '*firered*.gba' | head -1)
[ -n "$FR" ] && [ "$FR" != "base/firered.gba" ] && mv "$FR" base/firered.gba
cp "../gba/Pokemon Ash Gray (4.5.3).gba" rom/ashgray.gba 2>/dev/null
echo "=== files ==="; ls -la base rom
echo "=== CRC32 (FireRed should be dd88761c) ==="
for f in base/firered.gba rom/ashgray.gba; do
  [ -f "$f" ] && python3 -c "import zlib,sys;d=open(sys.argv[1],'rb').read();print('  %-20s %8d bytes  crc %08x'%(sys.argv[1],len(d),zlib.crc32(d)&0xffffffff))" "$f"
done
