import re, sys
d = open(sys.argv[1], "rb").read()
pats = [b'FLASH1M_V', b'FLASH_V', b'FLASH512_V', b'SRAM_V', b'SRAM_F_V', b'EEPROM_V']
found = False
for p in pats:
    idxs = [m.start() for m in re.finditer(re.escape(p), d)]
    if idxs:
        found = True
        s = idxs[0]; end = d.find(b'\0', s)
        print(f"{p.decode()}: {len(idxs)} hit(s); first='{d[s:end].decode(errors='replace')}' @0x{s:06X}")
if not found:
    print("NO save-type string found -> mgba cannot auto-detect; saves will hang.")
