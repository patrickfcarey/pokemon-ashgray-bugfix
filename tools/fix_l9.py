#!/usr/bin/env python3
"""L9 fix — declining Dragonite's invitation is an unwinnable dead state.

The invite scene (0x876B3F -> 0x861D2A, triggers at (10,24)/(11,24)) ends with
`setvar 0x6195,1` on BOTH branches, and the triggers fire on `0x6195==0` — so the scene
never re-offers. Declining (NO) skips the NEO TICKET + `setvar 0x6196,1` entirely:
no ticket, storm started, no way to ever get the invitation -> progression dead
(New Island's gate requires the ticket; the storm only clears after the island event).

Fix: re-gate the two triggers on **var 0x6196 == 0** ("doesn't have the ticket") instead
of 0x6195 ("scene played"). Declined players get re-asked when they walk the pier again;
accepting still permanently disarms the scene (0x6196=1). No script bytes change; 0x6195
semantics (storm weather logic @0x864CC4) are untouched. Verified: 0x6196 has no other
readers, the scene is idempotent on re-run (re-adds the Dragonite object, re-runs weather).
"""
ag = bytearray(open('rom/ashgray.gba', 'rb').read())
for t in (0x726A98, 0x726AA8):
    var_at = t + 6
    assert bytes(ag[var_at:var_at+2]) == bytes([0x95, 0x61]), \
        f'trigger var @0x{var_at:06X} unexpected: {bytes(ag[var_at:var_at+2]).hex()}'
    assert bytes(ag[t+12:t+16]) == bytes.fromhex('3f6b8708'), 'trigger script ptr moved!'
    ag[var_at:var_at+2] = bytes([0x96, 0x61])
    print(f'trigger @0x{t:06X}: var 0x6195 -> 0x6196')
open('rom/ashgray.gba', 'wb').write(ag)
print('L9 fixed: invite re-offers until the NEO TICKET is accepted')
