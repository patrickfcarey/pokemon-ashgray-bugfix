# Warp / Map / Object DATA-validity audit (Pokémon Ash Gray fork)

Class: pure-ROM map/warp data that black-screens, loads garbage, or crashes on a
**fresh save**, independent of save state. Box-fix-IMMUNE.
Sub-patterns audited: (1) warp-EVENT-table validity, (2) script warp commands,
(3) object-event data sanity.

ROM under test: `rom/ashgray.gba` (base 0x08000000, 16 MiB).
Bank table @ file 0x5524C → 0x0873E2F4. 43 banks, 550 maps. Warp-event stride 8 bytes
(x:u16, y:u16, elevation:u8, destWarpId:u8, destMap:u8, destBank:u8); warp count = events+1,
warps ptr = events+8 — both **confirmed against the live engine** (see §Engine).

---

## VERDICT

**No invalid warps or objects in this class. 0 confirmed bugs, 0 candidates carried forward.**

- Sub-pattern 1 (warp events): 36 entries have `destWarpId >= destination warpCount` after
  excluding the 0x7F/0xFF/dynamic sentinels. **None are a crash.** The engine bounds-checks
  the warp id and falls back gracefully (explicit coords, else map-center). All 36 are
  **byte-for-byte identical** to the shipped, widely-completed upstream *Ash Gray 4.5.3*, so the
  fork introduced none of them and they have never black-screened in practice. There are **zero
  warp events whose destination BANK/MAP does not exist** — every destBank/destMap resolves to a
  real map.
- Sub-pattern 2 (script warps): every reachable `warp*` command resolves to an **existing**
  destination map; 0 dest-missing. A handful of `warpsilent` commands use `warpId` 0/0xFF into
  0-warp maps but supply **valid explicit x/y** — that is the intentional FRLG "warp to coords"
  idiom and lands the player exactly where scripted. (My first linear pass produced 4
  "dest-missing" hits — all proven to be the decoder walking type-2/4 mapscript {var,val,script}
  sub-table bytes as code; corrected with the recursive decompiler.)
- Sub-pattern 3 (object events): max graphicsId in use is **0x97**, well inside the FRLG object
  table; 0 out-of-range graphicsId, 0 garbage spawns.

Confidence: **high.** The decisive item — engine behavior on out-of-range warpId — was confirmed
by disassembling the fork's own resolver, not assumed.

---

## Engine fact (confirmed in-binary, not from memory)

`gMapHeader` lives at EWRAM 0x02036DFC. The warp-arrival resolver **SetPlayerCoordsFromWarp** is
at file 0x0552FC (ROM 0x080552FC):

```
080552FC  push {r4,r5,lr}
08055302  ldrsb r1,[r2,#6]     ; r1 = sWarpDestination.warpId  (SIGNED byte)
08055308  cmp r1,#0
0805530A  blt 0x8055334        ; warpId < 0  -> fallback
0805530C  ldr r3,=0x02036DFC   ; gMapHeader
0805530E  ldr r0,[r3,#4]       ; gMapHeader.events
08055310  ldrb r5,[r0,#1]      ; events->warpCount
08055312  cmp r1,r5
08055314  bge 0x8055334        ; warpId >= warpCount -> fallback   <== THE BOUNDS CHECK
08055316  ldr r0,[r0,#8]       ; events->warps      (events+8; matches data layout)
08055318  lsls r1,r1,#3        ; warpId * 8         (stride 8;     matches data layout)
0805531A  ...                  ; player x,y <- warps[warpId]
; ---- fallback @0x08055334 ----
08055334  ldr r1,[r4]          ; if sWarpDestination.x>=0 && .y>=0: use explicit coords
   ...    (uses warp.x / warp.y when both >= 0)
08055350  ldr ... =0x02036DFC  ; else: x = mapLayout->width/2, y = mapLayout->height/2
   ...    (signed /2 of layout width & height -> MAP CENTRE)
0805536C  pop {r4,r5}; bx
```

Consequences for this class:
- destBank/destMap **must** exist (the resolver dereferences `gMapHeader.events` of the
  *destination* map after it is loaded; a non-existent bank/map is the only true garbage-load
  path). **Every** warp in the ROM passes this — 0 violations.
- destWarpId out of range (or 0xFF / negative such as 0x8A): **no crash.** Player is placed at the
  warp command's explicit x/y if valid, otherwise at the destination map's centre. This matches
  the well-known pokefirered `SetPlayerCoordsFromWarp` semantics. Out-of-range warpId is therefore
  **not in this audit's class** (cosmetic arrival-spot at worst).

This is consistent with the session's other verified engine facts (RunScriptCommand bounds-checks
opcodes; gSpecials dispatch bounds-checks) — the engine's posture is defensive throughout.

---

## Sub-pattern 1 — warp EVENT table

Scan: every map's warp-event table; for each entry verify destBank<43, destMap exists, and
destWarpId < destination warpCount. Excluded sentinels (counted, not flagged):
`(127,127,127)` dynamic-warp ×14, `(255,255,255)` all-FF ×14, plus any field == 0x7F/0xFF.

Total warp events: 1513. destBank/destMap missing: **0**. destWarpId >= dest count (non-sentinel):
**36**, listed below. All 36 verified identical to upstream Ash Gray 4.5.3 (same source bytes AND
same destination warp counts).

| Source map | warp idx | dest (bank.map) | destWarpId | dest warpCount | why engine-safe |
|---|---|---|---|---|---|
| 1.30 | 0,1,2,3 | 3.25 | 0,0,0,1 | 0 | 3.25 is a CONNECTION map (left→1.34, right→3.10, down→0.11); arrival = map centre |
| 1.32 | 0,1,2,3 | 3.25 | 0,0,0,1 | 0 | same as 1.30 |
| 1.33 | 0,1,2,3 | 3.25 | 0,0,0,1 | 0 | same |
| 1.35 | 0,1,2,3 | 3.25 | 0,0,0,1 | 0 | same |
| 2.20 | 0,2 | 2.13 | 3,1 | 1 | centre fallback; 2.20/2.23 are Mt.-tunnel rooms |
| 2.23 | 0 | 2.13 | 3 | 1 | centre fallback |
| 2.34 | 0,1 | 3.49 | 0,1 | 0 | 3.49 is a CONNECTION map (up→3.48, down→1.121) |
| 10.8 | 3 | 0.8 | 138 (0x8A) | 8 | source coords (65535,16127) are OFF-MAP → warp unreachable; also warpId<0 |
| 10.11 | 0,1,2 | 10.10 | 2 | 2 | off-by-one; centre fallback |
| 16.1 | 0 | 16.0 | 3 | 3 | off-by-one (16.0 has warps 0–2); centre fallback |
| 20.0 | 0,1 | 3.10 | 10 | 9 | off-by-one; 3.10 = Celadon dept-store-style hub |
| 20.0 | 2,3 | 3.26 | 1 | 0 | 3.26 is a CONNECTION map (left→3.10, right→3.4) |
| 21.1 | 0 | 21.0 | 3 | 3 | off-by-one; centre fallback |
| 25.2 | 0 | 25.1 | 4 | 3 | off-by-one; centre fallback |
| 27.0 | 0 | 3.37 | 4 | 4 | off-by-one; centre fallback |
| 35.2 | 0 | 35.1 | 1 | 1 | off-by-one; centre fallback |
| 37.1 | 0 | 36.0 | 3 | 3 | off-by-one; centre fallback |
| 42.0 | 0 | 3.64 | 1 | 1 | off-by-one; centre fallback |

Notes proving benign:
- **All destination maps EXIST.** The only true garbage path (missing dest map) has 0 occurrences.
- The recurring "off-by-one" group (16.1, 21.1, 35.2, 37.1 all share interior layout 0x009; 10.11,
  20.0, 25.2, 27.0, 42.0) is the FRLG building-interior idiom where the back/upstairs warp indexes
  one past the ground-floor table; the resolver's bounds-check turns it into a centre arrival.
- 10.8 warp3 is **dead data**: its trigger tile is at (65535,16127), outside the 15×20 layout, so
  the player can never step on it; its warpId 0x8A is also negative-as-s8 (−118) → fallback.
- 15 of the 17 source maps are not themselves reached by any warp event (`warped-into-by: none`),
  i.e. they are unused/cut interiors inherited from base FRLG — never entered in normal play.

Verification commands used: structural dump of each source + destination map's warp tables;
fork-vs-upstream byte diff of all 17 source warp tables and all 19 distinct destination warp
counts (100% identical); off-map reachability test of source coordinates.

---

## Sub-pattern 2 — script warp commands

Reachable-walk: persons (stride 24, ptr@+16), triggers (stride 16, ptr@+12), signs
(stride 12, ptr@+8, type<5), mapscripts @ header+8 (types 2/4 resolved to their {var,val,script}
sub-table targets — NOT walked as code), gStdScripts @0x08160450 ×10, plus call/goto/call_if/goto_if
closure. Warp opcodes validated: 0x39 warp, 0x3A warpsilent, 0x3B warpdoor, 0x3D warpteleport,
0xD1 warpspinenter, 0x3E/0x3F/0x40/0x41 set*warp, 0xC4 setescapewarp (operands: bank@+1, map@+2,
warpId@+3, x:u16@+4, y:u16@+6). Opcode lengths/layout confirmed against tools/decomp.py.

Result: **dest-map-MISSING = 0.** Reachable `warpsilent` commands with warpId past the dest count,
all into EXISTING maps and all carrying valid explicit x/y (intentional "warp-to-coords"):

| Script @ROM | dest | warpId | explicit (x,y) | note |
|---|---|---|---|---|
| 0x0886DFCC | 3.73 | 0 | (116,6) | 0-warp map; lands at scripted coords |
| 0x0885FEBC | 3.67 | 0xFF | (19,9) | 0xFF sentinel + explicit coords |
| 0x088822C0 | 3.67 | 0xFF | VAR_0x4000/0x4001 | variable-coord warp |
| 0x08881912 | 3.73 | 0 | (116,6) | scripted coords |
| 0x088821BF | 3.67 | 0 | (15,50) | scripted coords |
| 0x088B466E | 3.107 | 0 | VAR_0x4000/0x4001 | variable-coord warp |
| 0x088B3EF0 | 3.107 | 0 | (25,20) | scripted coords |
| 0x08831741 | 1.4 | 0xFF | (32,14) | 0xFF sentinel + explicit coords |

All resolve through the engine fallback to explicit coordinates → land exactly where the script
intends. No crash, no garbage. The four false "dest-missing" hits from the naive linear pass
(reported then retracted) were the decoder reading type-2/4 mapscript sub-table pointer-bytes as
opcodes; the recursive decompiler (which follows real control flow) reaches none of them.

---

## Sub-pattern 3 — object-event data

Persons stride 24, graphicsId@+1, movementType@+9. Scanned all 550 maps. Max graphicsId in use =
**0x97**; no value >= 0xE0; **0** out-of-range graphicsId, **0** clearly-garbage movement/trainer
refs. (gTrainers @0x0823EAC8 ×743 — the trainer-ref range was already cleared by
tools/scan_trainers.py this session and is not re-litigated here.) Clean.

---

## Already-mitigated / out-of-scope notes
- The D1 var-corruption (box-deposit) class is separate and already mitigated; nothing here
  depends on var corruption — these are static-data findings on a fresh save.
- mapscript ON_WARP overlaps (F2/2.36/3.93) and the 540-map collision/softlock sweep were prior
  work and did not cover DATA validity; this audit closes that gap and finds it clean.
