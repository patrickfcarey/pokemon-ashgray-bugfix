#!/usr/bin/env bash
set -uo pipefail
cd /tank/backups/media_3x/roms/consoles/pokemon_romhacks/ashgray-fork
cp ../gba/_patches/patcher.py tools/patcher.py 2>/dev/null || true

echo "=== generate patch ==="
python3 tools/makepatch.py rom/ashgray.gba patches/ashgray-fork.ips

echo "=== round-trip verify (FireRed + patch == Ash Gray?) ==="
python3 tools/patcher.py base/firered.gba patches/ashgray-fork.ips rom/_verify.gba >/dev/null 2>&1
python3 -c "import zlib
a=zlib.crc32(open('rom/ashgray.gba','rb').read())&0xffffffff
b=zlib.crc32(open('rom/_verify.gba','rb').read())&0xffffffff
print('  round-trip:', 'OK %08x'%a if a==b else 'MISMATCH %08x vs %08x'%(a,b))"
rm -f rom/_verify.gba
ls -lh patches/

echo "=== git ==="
git init -q && echo "  initialized"
GA="git -c user.email=patrickfcarey@gmail.com -c user.name=patrickfcarey"
$GA add -A
$GA commit -q -m "Ash Gray bug-fix fork: workspace + audit tooling (footprint/maps/dialogue) + IPS patch pipeline"
$GA log --oneline | head
echo "=== tracked files ==="; git ls-files | head -40
