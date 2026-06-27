# Headless verification harness (libmgba)

Boots the ROM, drives input, **warps to any map**, and screenshots frames with **no
display** — fixes get verified in-engine without anyone playing through the game.
Source archived here: **`tools/emu/rig.c`** + `tools/emu/rig.sh` (canonical copies). Build/working dir
is `_emu/` at the repo root (outside git) — `rig.sh` compiles `rig.c` against the local libmgba build.
Run: `bash _emu/rig.sh <rom> <script.rig> [state.ss]` (or `./rig <rom> <script.rig> [state.ss]` directly
with `LD_LIBRARY_PATH` set to `prefix/lib64`).

## Build (one-time)
Needs `gcc` + `cmake` (`pip install --user cmake`):
1. `git clone --depth 1 https://github.com/mgba-emu/mgba` → cmake with Qt/SDL/PNG/ffmpeg/
   libzip/sqlite OFF → `make` → `libmgba.so` + headers in `prefix/`.
2. Compile `rig.c` with the **same defines the lib used** (read them from the build's
   `CMakeFiles/mgba.dir/flags.make`) — mismatch shifts `struct mCore` and segfaults.

## rig.c script commands
`key/frames/tap` (input) · `mash`/`mashA` (intro blasting) · `shot` (framebuffer→raw)
· `peek8/16/32`, `poke8/16/32`, `deref`, `dumpsb`, `loc` (RAM) · `dump <addr> <len>`
(hexdump absolute) · `dump1 <off> <len>` (hexdump from *gSaveBlock1Ptr+off — follows sb1
relocation) · `save/load` (savestates, flags=0, files opened O_RDWR) · `savfile` (attach
128K .sav) · `flash1m` (force Flash-1M or in-game saves hang) · `warpto` (poke all
SaveBlock1 warp slots) · `reset` · `call <addr> [r0..r3]` (invoke a Thumb fn in isolation,
run to return, log r0/r1/steps).

### CPU introspection (added 2026-06-25, for localizing freezes)
`ARMRun()` steps one instruction *and* processes the event scheduler, so stepping it is timing-faithful.
- `regs` — dump r0–r15, cpsr, and the code halfwords around PC.
- `trace <n>` — step n instructions, print a **PC histogram** (hottest PCs + range). A real freeze =
  a few PCs in a tiny span (the spin loop); a healthy game = the broad main loop. Note: the generic
  main-loop wait (`0x080008ac`) and the battle main loop (`0x08011101`) both look "busy" — they do **not**
  distinguish frozen from healthy-waiting, so confirm state from a screenshot or `gMain.callback2`
  (`0x030030f4`: field-idle `0x080565b5` vs battle `0x08011101`), not the PC alone.
- `stepto <addr> [max]` — faithful software breakpoint: run until PC enters `[addr, addr+6]`.

### Flash-save persistence (fixed 2026-06-26) — save→reset→Continue now works
The in-game save writes the savedata buffer but leaves it `dirty`/unflushed; `core->reset()` then
re-reads the (empty) backing vfile and wipes it, so Continue saw "new game". Fix: **`reset` now flushes
savedata→vfile first** (`GBASavedataClean` + `vf->sync`). New helpers: `savedbg` (print type/size/dirty +
first bytes) and `savesync` (force flush). Gotchas: issue `savfile`+`flash1m` before the first save;
the in-game SAVE confirm needs ~130 frames for the save-info box before the YES (else the A is eaten);
a valid FRLG save shows 14 sectors with signature `0x08012025`.

### Staging a scripted battle/event from a field state (no navigation needed)
When a coord trigger can't be reached (forest ledge-maze) or won't arm (after `warpto`), invoke the
script directly: `call 0x08069AE5 <script_ptr>` runs **`ScriptContext1_SetupScript`** (FR U,
`@0x08069AE4`), which arms the overworld to execute that script over the next frames. e.g.
`call 0x08069AE5 0x088170FC; frames 220` runs the Pidgeotto wrapper (`setvar; setwildbattle;
dowildbattle`) → a real "Wild PIDGEOTTO appeared!" battle on whatever field state is loaded. (Sibling:
`RunScriptImmediately @0x08069B48` runs a script to completion synchronously — wrong for `dowildbattle`,
which is multi-frame.)

### Hard-won facts (D7/L12 campaigns, 2026-06-12)
- **Stale gMapHeader**: a savestate predating a ROM-side events repoint keeps the OLD
  events pointer in RAM. gMapHeader = `0x02036DFC` (FR U); poke32 `0x02036E00` (its
  events field) to the new table, or your injected triggers are invisible until a map
  reload. Map loads re-copy from ROM, so warped-into maps are always fresh.
- **Saveblock relocation copies the whole var arena**: markers at sb1+0x3D00…+0x5400 all
  survive a warp. Pokes to in-range AND beyond-array vars relocate with the block —
  poke at the CURRENT sb1 and they persist. (sb1 address still changes per warp/battle;
  use `dump1`, or read `loc` output, for post-relocation reads.)
- **Ride out post-battle/whiteout scenes with B-pairs, not A-pairs**: hold-A pairs
  re-engage facing NPCs the instant their talk script ends (mom's morning nag re-fired
  forever = fake "softlock"). B advances text and never engages.
- **Don't put injected triggers on tiles that scripted movements cross** (the home scene
  walks the player to (8,6) on 4.0; a trigger there fights the running script).
- Battles re-randomize sb1 too; for a fixed savestate + input sequence the new address
  is deterministic (replayable).

## Warping to arbitrary maps (the method that works)
**Redirect a warp event in a throwaway test ROM** (`_emu/mk_warp_test.py`): point the
bedroom-stairs warp (map 4.1 warp#0 @0x730604) at the target map/warpId; the engine then
performs a native, fully clean map load. From the bedroom checkpoint, first poke past the
intro gate (`var 0x4056=1`, `flag 0x1006`), step on-off-on the stair tile, and you're there.
Walk with collision-clamped holds (hold into a wall ~80-90 frames), not frame-counted taps.
Template: `_emu/gate_ab.rig`.

Note: save→reset→Continue warping **fails** on FireRed — the quest-log recap and
`SaveMapView` re-capture override saveblock pokes. Don't go down that road again.

## Verified with this rig
- ✅ 4 text fixes (T1, T2a–c) rendered live in-engine (TV-redirect trick, `text_fixes_proof.png`).
- ✅ **L1 Indigo-gate fix proven by A/B**: control vs fork ROM (only the 16 dispatch bytes
  differ), same save, same guard — "league hasn't begun" vs correct badge-check
  (`_emu/l1_proof.png`).
- ✅ **F2 underwater-cave crash reproduced AND fixed** (`_emu/f2_proof.png`): warped to the
  splinter landing (map 1.72), watched the game die (black screen, sb1 nulled), bisected the
  two mapscript entries by RAM-disarming their condition vars one at a time, proved the swim
  msgbox + unfilled STR_VAR_1 was the killer with a buffer-prefill experiment, then fixed
  (un-overlap tables + self-buffering swim script) and re-ran the same route clean.

## Bisection workflow (for the next freeze bug)
1. Warp to the crash site; reproduce + screenshot (loc/peek to detect corruption — sb1
   nulled / map id garbage are the telltales).
2. Dump the map's events + mapscript tables; RAM-poke each frame/warp entry's condition
   var to disarm them one at a time until the crash isolates.
3. Confirm the mechanism with a targeted RAM experiment (e.g. pre-fill the suspect buffer).
4. Fix in free space with guarded asserts; A/B with a control ROM; montage the proof.

- ✅ **F3 breeding-center crash diagnosed + fixed** (`_emu/f3_proof.png`): warped to map 1.43,
  drove the whole sequence (break-in → COHORTS battle → post-battle B&C ambush). Crash was an
  ILLEGAL if-condition byte (6; valid 0–5) on the party-full guard — the engine's condition
  table row 6 contains no 1s, so the guard never fired and a full party got a forced 7th mon.
  One-byte fix (cond 6→1). ROM-wide cond>5 scan also surfaced the S1 class (Butterfree/Pikachu
  events with transposed compare/cond operands).

- ✅ **F6 Tangelo Park void-march reproduced + fixed** (`_emu/f6_proof.png`): fresh-save front
  entry triggered the park-exit ejection from the wrong position, marching the player into the
  void (invisible/frozen). Fixed with a position-gated wrapper; also sealed a vestigial warp
  into map 33.3, whose entire layout Ash Gray's build deleted (0xFF'd) — a latent crash map.

- ✅ **L9 decline-soft-lock fixed + proven end-to-end** (`_emu/l9_proof.png`): drove the whole
  Dragonite invitation live (decline → storm → return to pier). Original: no re-offer, dead
  save. Fork: triggers re-gated on "has ticket" (4 bytes) → Dragonite re-offers, ticket
  obtainable. Input trick for long cutscenes: hold-button (fast-print) + tap (advance) pairs;
  B-pairs auto-decline at yes/no prompts, A-pairs auto-accept.

- ✅ **S1 closed as not-a-bug**: reachability analysis proved every remaining cond>5 site is
  orphaned dead code (the live Butterfree event even contains metapod's own corrected check).
  Lesson: scan hits need reachability verification before repair. T4 ("RAFTT") likewise
  retracted — a dumper artifact (stray byte after the 0xFF terminator). T3 (INIDGO→INDIGO)
  was real and is fixed in place.

- ✅ **F4 Grampa Canyon pickaxe softlock reproduced + fixed** (`_emu/f4_proof.png`): the rival's
  scripted exit walk collided with the path → infinite blocked-step retry → waitmovement hang
  after the give. 10-byte fix (instant departure + jump to cleanup). New diagnostic: a
  movement-data terminator check (`0xFE` scan) and watching an NPC freeze mid-route on screen.

- ✅ **L2 fixed** (league-day full-party stall: no-room branch now still sets the departure
  state; mon stays with Oak, collectible later). ✅ **L4 fixed as a class** (44 maps had their
  header flags byte zeroed — run bit restored from vanilla; verified live by the 2-tiles-vs-1
  burst test). **L6 audited** — all 8 badge setters correct, needs-repro. **L3 partially
  traced** — needs the force-mount special identified.

- ✅ **L3 investigated to ground truth**: drove the full steal→storm→thundershock sequence
  headlessly (injected a warp into the warpless map 3.67 for entry). Natural path is CLEAN —
  the chase map forbids mounting, so the reported stuck-on-bike state needs an exotic
  mount-elsewhere-and-ride-in construction. Closed as needs-repro/likely-stale with full trace.

- ✅ **Global warp audit + L5 class fix**: `audit_warps.py` validated all 1513 warp events —
  73 structural defects found; all 21 on reachable maps fixed (`fix_l5_warps.py`: 19 dangling
  warpIds clamped to the dest's nearest real door incl. the Hidden Village cluster, 2 doors
  into corrupt-layout corpse maps sealed). Remaining rows = zero-incoming orphans, documented.
- **F1 traced to the battle engine** (scripted wild Pidgeotto battle; event chain is clean).
  Battle bugs need a save WITH Pikachu — next session: drive the Oak's-lab give flow once and
  save a post-Pikachu checkpoint (`pikachu.ss`), unlocking F1/F5/D-series testing.

- ✅ **pikachu.ss BUILT + VALIDATED** (`_emu/pikachu.ss`): party count = 1 (PIKACHU, nick
  "AAAAA"), saved in Oak's lab (4.3 @(4,8)) right after the give; loads fine under the real
  fork ROM (state is mid-Pokédex-speech: ~9 A-pairs finish it, then 1 DOWN + 2 B-pairs
  disengage from Oak). Built via: lab-warp test ROM + pokes (starters-taken flags 0x38 @
  sb1+0x10EC, lab state var 0x7000=1 @sb1+0x7000) + counted A/B phases (`pika_full.rig`).
  New tools: `tools/walkmap.py` (collision ASCII), `tools/pathfind.py` (BFS → move legs).
- **F1 rig 90% ready** (`f1_repro.rig` + `tvtest/forest_test.gba` with lab-exit→forest
  redirect): blocked on the lab's exit-tile behavior (warp#0 @(11,6) fires neither on
  step-on nor south-press; actual exit = likely the staircase tile nearby — find it, or
  redirect a different reachable warp). Forest route to the Pidgeotto trigger is computed
  (warp#2 (4,11) → (7,34), 14 legs); trigger var 0x6108=1 poke = @sb1+0x5210.
- Map gotchas discovered: Pallet 3.66 has ledge tiles BFS can't see (the (24,15) door sits
  ON an east-ledge = dead door; (25,16) is a 1-tile inescapable ledge pocket — log as map
  bug); lab region geographically sealed from the house (intro cutscene normally moves you).

## F1 RESOLVED-AS-REPRODUCED (engine-level)
The scripted-wild freeze is captured (`_emu/f1_proof.png`): from `forest.ss`, the Caterpie
battle (same `setwildbattle; dowildbattle` wrapper as Pidgeotto; both scripts clean)
non-deterministically hard-freezes in its end fade — black screen, stale frame, input dead;
other runs of the same state complete. Root cause is inside Ash Gray's modified battle
engine (ASM) — documented as engine-level wontfix-for-now with a one-command repro.
Checkpoints: `pikachu.ss` (lab, party=1), `forest.ss` (mid-Caterpie-battle, party=1 —
ironically the perfect F1 repro state). Long runs need Bash timeout 540000 (the default
120s killed marathons mid-flight — that was the "dead process").

## F1 campaign state (deep progress, resume here)
- Lab exit SOLVED: warp events need door-behavior tiles, but **injected coord triggers fire
  on any tile** — `tvtest/forest_test.gba` has trigger (11,7) on 4.3 (var 0x6108==1) whose
  script warps to forest 1.0. (Also: encounter rate for 1.0 zeroed in the test ROM; the
  three forest trainers pre-defeated via flag pokes 0x714/0x566/0x568.)
- Proven in-engine: live trainer battle (Metapod, took hits — no freeze), scripted wild
  Caterpie battle fires at (10,21) and resolves; the story then auto-plays the NIGHT CAMP
  cutscene chain (escort + "BEEDRILL swarm" dialogue) — minutes long, taps barely advance it.
- Battle macro that works: `tap B 4 30 ×2; tap A 4 60; tap RIGHT 4 30; tap A 4 60; frames
  820` (B-prefix collapses backlog; cursor remembers THUNDERSHOCK so RIGHT becomes no-op).
- NEXT SESSION: drive the camp chain to completion with generous apair batches, **save
  forest.ss immediately after** (so iterations stop replaying 5 minutes), then walk to
  (7,34) → Pidgeotto battle (trigger var 0x6108==1 already set) → watch for the F1 freeze
  when Pikachu takes a hit. All routes/macros in `_emu/f1_repro.rig` (v9).
- WARNING: bash heredoc edits get glitch-eaten ~30% of the time — ALWAYS verify rig
  content on disk (grep a marker) before running; prefer the Write tool.

## D7 + L12 campaigns CLOSED (2026-06-12, both did-not-reproduce with full evidence)
- **D7/D1**: full Viridian-PC scene driven in situ (`tvtest/d7_real2.gba`, script-warp
  lab→5.4): Misty entry, Joy decline (her script arms 0x5030 before the prompt), exit-line
  ambush, type-9 battle (deliberate: Joy = in-battle tutor), 1-HP Growl-only faint-loss,
  real thundershock cinematic. Party/storage/daycare/flags/vars byte-clean; only delta =
  friendship 70→69. Artifacts: `d7_ready.ss`, `d7_pc.ss`, `_emu/d7_final_sheet.png`.
- **L12**: whiteout system fully mapped (hook @0x1A8DD9, per-PC story dispatcher
  @0x83E1D4, setrespawn+0x405A/B/C triplet convention). Live Spearow-loss runs recover
  cleanly; chase map self-heals its scene flags on re-entry. Three false repro alarms
  were all harness artifacts — see "Hard-won facts". `_emu/l12_clean_sheet.png`.

## L13 + D4 fixed; D2/F5/D5 triaged (2026-06-12)
- **L13** (Cerulean gym pool, map 7.5) FIXED: pier tip (8,9) had a rim block at water
  elevation = one-way trap; cloned cell from (8,10) (`tools/fix_l13.py`+`fix_l13b.py`).
  A/B-proven `_emu/l13_proof.png`. CRC `18d75e55`.
- **D4** (Teachy TV) FIXED: USE played the Poke-Dude demo over a black void; repointed
  `gItems[0x16E].fieldUseFunc` → shared `CannotUse` (`0x080A2239`) via `tools/fix_d4.py`.
  A/B-proven `_emu/d4_proof.png`. CRC `0cc1dfb9` (then-current; build is now `5cffa700`).
- **D2** did-not-repro: every script gift-mon (Eevee `0x810BA6`, Charmander `0x82CC8A`,
  Squirtle Squad `0x82FB13`/`0x873C8D`) uses the same clean gate `getpartysize; compare 6;
  goto_if full→0x82C77A; else givemon`. Freeing a slot fills the party; deposited mon stays.
- **F5** no-mechanism: SPEAROW data byte-clean, scripted catch handled (`special 0xB4`→7).
- **D5** engine (PC release), **L7/L8** Safari = reused-vanilla FireRed, low-confidence.

## Next (remaining are engine/vague/art)
D1 Bad Eggs + D3 invisible-mon (engine/battle ASM), F7 (needs Orange-Islands repro),
G1 (Ashley palette art). No clean byte-fix path identified for these.
