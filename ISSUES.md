# Ash Gray fork — issue tracker

Live tracker for the bug-fix fork of Pokémon Ash Gray (beta 4.5.3, by metapod23).
Research sources in `audit/05-known-bugs.md`. Add findings here as we go.

**Severity:** 🔴 critical (crash/softlock/blocks progression) · 🟠 high · 🟡 medium · 🟢 low/cosmetic
**Status:** `open` · `next` (queued) · `wip` · `fixed` · `wontfix` · `needs-repro`
**Fix-where:** `here` (byte/script/data edit) · `map` (event/warp struct edit, headless but more work) · `art` (needs human) · `engine` (battle/system, hard)

## Master list

| ID | Sev | Status | Area / trigger | Summary | Type | Fix-where |
|----|-----|--------|----------------|---------|------|-----------|
| **F1** | 🟠 | **reproduced** (engine-level) | Early forest scripted battles (Pidgeotto/Caterpie) | **REPRODUCED HEADLESSLY 2026-06-11** (`_emu/f1_proof.png`): the scripted-wild-battle wrapper (`setwildbattle; dowildbattle` — Caterpie `0x800277`, Pidgeotto `0x8170FC`, both decompile clean) **hard-freezes non-deterministically in the battle-end fade** — black screen, stale frame, input dead; same savestate completes fine on other runs. Timing-dependent, inside `dowildbattle` = Ash Gray's modified battle engine (ASM), beyond safe byte-patching. One-command repro: load `_emu/forest.ss` on `tvtest/forest_test.gba`, fight the Caterpie. The "camera scrolls too high"/"first hit" details in old reports = anecdotes around this same hang | freeze | engine (wontfix-for-now, repro documented) |
| **F2** | 🔴 | **fixed** ✅ | Underwater cave, after Dragonite tournament msg | Black-screen freeze | freeze | here |
| **F3** | 🟠 | **fixed** ✅ | Breeding center | Crash talking to Team Rocket (Jessie/James) | crash | here |
| **F4** | 🟠 | **fixed** ✅ | Grampa Canyon (map 1.101) | Crash/softlock getting pickaxe ("from scientist" = the rival handoff) | crash | here |
| **F5** | 🟠 | **no-mechanism** (audited) | Early Spearow vs Team Rocket | "Catch Spearow early + use it → heavy glitching." **No corruption path found:** SPEAROW's species data (base stats, learnset) is byte-clean vs vanilla; the scripted chase battle (`0x822362`) is a plain `setwildbattle SPEAROW lv5, no item`; and the outcome handler (`0x886D53`, `special 0xB4`) explicitly handles the **CAUGHT** outcome (7 → flock-help branch `0x886E16`, `setflag 0x1338`) — catching the scripted Spearow is graceful, the resulting mon is ordinary. Vague report, no reproducible mechanism in 4.5.3 | script/flag | n/a |
| **F6** | 🔴 | **fixed** ✅ | Tangelo Island arrival | Crash going through the back of a building | crash | here/map |
| **F7** | 🟡 | needs-repro (**investigated, no static repro** 2026-06-14) | 2nd Orange Island "lady" event | Crash report. **Investigated 4.5.3:** located the OI "lady" events — **Nastina/Tentacool** (script ~`0x882DF5D`: badge-flag checks 0x820-0x822 + msgbox + `setflag 0x1305` — **no crash pattern**) and the **Maiden's Peak** ghost (old-woman→Gastly, refs `0x8833C60`/`0x8834765`; custom-opcode scripts that don't cleanly decompile). **Ruled OUT an F1-class scripted-battle freeze** — there is **no `setwildbattle` of Tentacool(0x48)/Tentacruel(0x49) anywhere** in the ROM (the Tentacruel "attack" is a cutscene, not a battle). No dead-map warp or collision-march in what's parseable. The "lady after the plane crash" symptom = the **older beta's content-end** (game simply stopped there); 4.5.3 extends content through ~Gym 3, so that symptom is **likely already resolved** (content continues). Residual: a specific crash in the Maiden's Peak object-transformation can't be ruled out but is **unconfirmable without an in-engine repro** (needs OI late-game state). | crash | needs-repro |
| **L1** | 🟠 | **fixed** ✅ | Indigo Plateau gate | Guard says league hasn't started despite badges + exam | flag logic | here |
| **L2** | 🟠 | **fixed** ✅ | Prof Oak, full party (league day) | Can't receive Pokémon → next event won't trigger | give logic | here |
| **L3** | 🟡 | needs-repro | After Pikachu thundershocks Spearow | Ash stuck on Misty's bike — **natural path verified CLEAN headlessly** (scene → warp → player walks free). Full trace: steal scene `0x860574` gives BICYCLE (0x168) on map 3.67, which has `bikingAllowed=0` (can't mount during the chase); shock script `0x801E71` removes the item + warps. Only stuck-path = mount on a biking-allowed map and ride back in pre-shock — exotic/likely story-gated; probably a stale pre-4.5.3 report. No safe dismount special identified; defensive fix deferred | state flag | here |
| **L4** | 🟢 | **fixed** ✅ | Pallet Town + 43 more maps | Running shoes dead — map-header flags byte zeroed by metapod's editor; vanilla flags restored on all 44 affected vanilla-region maps; **verified live** (B-dash burst = 2 tiles/18f vs 1 walking) | map attr/flag | here |
| **L5** | 🟡 | **fixed** ✅ | Hidden Village + ROM-wide | Wrong mapping / traps with no exit — root cause = **dangling warp references** (sources asking for warpIds the edited destination no longer has → Gen3 spawns at garbage coordinates). Global audit (`tools/audit_warps.py`, 1513 warps) found 73 defects; all 21 on reachable maps fixed (`tools/fix_l5_warps.py`): 19 warpIds clamped to the dest's nearest real door (incl. the Hidden-Village cluster 1.55/1.56→1.49/1.50), 2 doors into corrupt-layout corpse maps (3.18→37.0 15×2058, 34.1→34.2 FFFF dims) sealed F6-style. Remaining 52 audit rows = zero-incoming orphans/corpse-internals, left as-authored (documented) | map data | here |
| **L6** | 🟠 | badge code sound; 4–5 gym paths **D1-gated**; not reproduced | Badge UI | Winning 6 badges shows as 5 — badge *award* logic is provably sound (8 distinct unconditional setters, zero `clearflag`, display counts by flag, `l6_proof.png`). Authoritative all-gyms map-trace (`trace_all_gyms.py`+`trace_gym_gates.py`): **Rainbow/Soul(Koga)/Earth = SAFE** (no D1 gate); **Boulder/Cascade/Marsh/Volcano badge paths ARE gated on Box-3 vars** (0x6082/0x6190+0x6113/0x6072+0x6074/0x6186) → Box-3 corruption can block/misroute those badges (same class as L14/L15). Effect dominantly a progression block, not a display desync. Earlier "Koga via 0x6155" retracted (=P1 Grand Prix). **Marsh LIVE-REPRODUCED** (`marsh_proof.png`): 0x6072>3 → Sabrina inert → Marsh unobtainable; 0x6072=0 → works. First D1 badge-block proven in-engine | flag/UI→data | see D1 |
| **L7** | 🟡 | needs-repro (**corroborated** 2026-06-13) | Safari Zone | "Team Rocket doesn't appear (event missing)." **Two players now report this** (see community cross-ref) → real player-facing gap, not noise. The Safari Zone is **reused vanilla FireRed** (all 63 "SAFARI" strings are stock FR text) — a Team-Rocket-in-the-Safari encounter is *not* FireRed content, so most likely **content never authored** (no source assets to restore) rather than an authored-then-broken event. Needs a real Safari playthrough to be certain | event | likely-unauthored |
| **L8** | 🟡 | needs-repro (low-conf) | Safari Zone | "Stuck without the bike (no escape route)." FireRed's Safari Zone is a **bike-free walking zone by design**; "stuck without bike" reads like expectation mismatch. No collision trap found in the reused-vanilla layout on inspection; needs a real Safari playthrough | progression | map |
| **L9** | 🔴 | **fixed** ✅ | Decline Dragonite's Mewtwo-island invite | Raft permanently breaks → soft-lock (can't progress *or* return; some report raft "gone") | flag logic | here |
| **D1** | 🔴 | **root-caused** (architectural) | Storage boxes | Bad Eggs — **REAL in-game mechanism found, not just cheats.** The hack's extended story vars (0x6xxx) overflow FireRed's 256-entry var array (`VarSet` is unbounded) and **physically land inside the PC storage buffer**. Demonstrated live: writing var `0x6079` appeared at **Box 3 / slot 0, byte +0x46** (the encrypted/checksummed region) → checksum fails → Bad Egg; var `0x6061` also sits in that same box. Mirror image = box-deposits clobber story vars (the community's "backtracking corrupts saves"). (A separate, smaller set of 7 lower `0x50xx` vars overflows into the SaveBlock1 interior instead — **unexamined**, and *not* the F2/F6 cause, contrary to an earlier note; see detail.) **Not cleanly byte-fixable** — needs relocating the var space + save-format migration = the "from-scratch" rework. We have NOT fixed this and don't claim to | data/arch | engine-rework |
| **D2** | 🟠 | **did-not-repro** (audited) | Eevee brothers event | "Deposit Squirtle to make room → Squirtle disappears." **Audited every script gift-mon event** (Eevee `0x810BA6`, Charmander `0x82CC8A`, Squirtle Squad `0x82FB13`/`0x873C8D`, +starter/Lapras): ALL use the identical correct gate — `getpartysize; compare 6; goto_if full → 0x82C77A (shared polite refusal); else givemon`. Freeing a party slot makes `givemon` fill **that party slot**; the deposited mon stays in the PC. No script writes a PC box slot, so nothing can "disappear." Likely a garbled echo of **"Make Room For Gloom"** (COMMUNITY-REPORTS line 170: *Fixed in 4.5.3*) or user error (released vs deposited) | storage event | n/a |
| **D3** | 🟡 | open | First Jessie & James battle | Switching Pokémon makes other mons invisible | battle/script | engine |
| **D4** | 🟢 | **fixed** ✅ | Teachy TV | "Broken — DON'T USE IT" (metapod's own list). **REPRODUCED:** USE opens the vanilla TV menu, but entering any lesson plays the Poke-Dude demo over a **black void** (the hack overwrote the demo's backdrop resources) — garbage at best, soft-lock risk at worst. **Fixed** (`tools/fix_d4.py`): repointed `gItems[0x16E].fieldUseFunc` from `ItemUseOutOfBattle_TeachyTv` to the shared inert `CannotUse` handler — the item stays in the bag but USE now safely says "OAK: …this isn't the time to use that!" instead of bricking. A/B-proven in-engine | item/data | here |
| **D5** | 🟢 | **engine** (not byte-fixable) | Route 1 | "Release glitch releasing Pidgeot while holding Pidgeotto." **No scripted Pidgeot-release event exists** — searched all `special 0x9F` (release-to-wild) sites; they belong to the anime release scenes (Butterfree/Pikachu-to-forest, the S1 events), none species-gated to Pidgeot. The combo is the **PC's built-in RELEASE function** (engine storage code) acting on two mons of one evolution line = a generic Gen-3 storage quirk, not an Ash Gray script. Out of scope for byte-patching | storage | engine |
| **D6** | 🟢 | wontfix | Pokédex | **Not a bug (verified):** Onix is correctly Rock/Ground in both FireRed & fork (gBaseStats @0x254784) | data | n/a |
| **G1** | 🟢 | open | Ash girl-disguise battle sprite | Mis-colored (shirt blue, hair white) | graphics | art |
| **T1** | 🟢 | **fixed** ✅ | Bulbasaur village line (0x834CBF) | Duplicated word "the the" | text | here |
| **T2** | 🟢 | **fixed** ✅ | Various dialogue | **3 fixed** (sacrfices→sacrifices @0x829FAC; recieved→received @0x814026 & @0x867878); rest pending proofread (`audit/04`) | text | here |
| **T3** | 🟢 | **fixed** ✅ | Indigo gate "all 8 badges" msg (text @0x881FC4) | "advance to the **INIDGO** PLATEAU" → INDIGO (in-place, same length) | text | here |
| **T4** | 🟢 | **retracted** | ~~Item "RAFTT"~~ | **Not a bug:** raw name bytes are `RAFT[FF]…` + a stray T *after* the terminator; in-game shows "RAFT". The double-T was an artifact of my dumper skipping 0xFF. | n/a | n/a |
| **L10** | 🟡 | **fixed** ✅ | "Can't get on/off the bike in certain outdoor areas" (metapod's own list, via COMMUNITY-REPORTS.md) | Same editor-zeroing class as L4, byte +0x18 (`bikingAllowed`): 16 vanilla-region maps (incl. Pallet 3.0, Route 1 3.19) lost biking permission. Vanilla values restored (`tools/fix_l10_biking.py`) | map attr | here |
| **L11** | 🟢 | needs-repro | "Message for computer in player's room stays opened" (community list) | **Did not reproduce in 4.5.3** — live rig test: bedroom PC opens item storage, exits, no lingering box (`_emu/pc3_after.png`). Likely fixed upstream (the original list strikethroughs were lost in plain-text paste). Same presumed for the Oak-Pokédex variant | UI | n/a |
| **L12** | 🟡 | **did-not-repro** (verified) | Lose to the Spearow flock at the start | "Stuck on wall" (French patcher's list) — **tested the loss path live, repeatedly, in 4.5.3: it recovers cleanly.** Wild-Spearow loss → whiteout → home (4.0 (8,5)) → mom heals, chase stage auto-reset, nag once ("You'd better hurry!") → walk out; on re-entering the chase map its own ON_TRANSITION even repairs the scene-object flags (flock re-hidden, lone Spearow restored). Whiteout/respawn architecture fully mapped (see details) — coherent. French fix targets an older beta (same already-fixed-upstream pattern as L11) | script | n/a |
| **L13** | 🟡 | **fixed** ✅ | Cerulean Gym pool (map 7.5) | **REPRODUCED + FIXED + A/B-proven.** The diving-board/pier tip (8,9) was stamped with a pool-RIM block (0x299, directional behavior 0xF4) at **water elevation (1)** at the end of the elevation-4 walkway: the rim behavior lets you step on, then the elevation mismatch vetoes every exit = one-step permanent softlock in a one-room gym. Fixed by cloning the full cell from (8,10) (block 0x2A4, elev 4, `tools/fix_l13.py` + `fix_l13b.py`); tip now bidirectional, water above still blocks, rest of the rim ring verified safe (deck-side entry rejected; sharer map 3.89 has no walkway adjacency) | map data | here |
| **D7** | 🟠 | **did-not-repro** (verified) | Pikachu faints vs Team Rocket (Viridian PC battle) | "Pikachu will no longer obey you" + **D1 Bad Eggs** blamed on this battle — **tested the FULL scene in-engine with a fainting Pikachu: everything is byte-clean** (party, storage, daycare, flags, vars). The `trainerbattle 9` (FIRST_BATTLE type, trainer 107) is *deliberate design* — Nurse Joy plays the in-battle tutor role — and its loss path works: faint → "TEAM ROCKET: No matter!" → thundershock cinematic → blastoff, story state correct. Only data delta = friendship 70→69 (standard faint penalty). See details | engine/script | n/a |
| **S1** | 🟡 | **wontfix** | Butterfree-breeding + Pikachu-release events | **Not live bugs (verified):** all cond>5 sites are unreachable dead code; see details below | script | n/a |
| **L14** | 🟠 | **explained by D1** (not separate) | "Route 1" Spearow loop (forest chase, map 3.67) | "Forced into the opening Spearow scene every time you re-enter." **Not a script bug** — decompiled the whole stage machine: chase var `0x6079` is **terminal at 3** (5 setvar sites; `ON_TRANSITION` `0x81DB67` removes the Spearow *only* at `0x6079==3`; nothing takes 3→<3 except the guarded whiteout reset `0x882811`). Post-completion re-arming therefore requires **external corruption of `0x6079`** — which physically lives in **Box 3 slot 0** (proven in D1). So: store a Pokémon in Box 3 → it clobbers the chase-completion var → re-entering re-forces the Spearow scene. A named, reported progression bug that is a direct **D1 manifestation** (the bidirectional half). Fix = the D1 workaround (avoid Box 3); no separate byte-patch | engine/data | see D1 |
| **L15** | 🟠 | **explained by D1** (not separate) | Mt. Moon area Zubat/Seymour loop (map 3.22) | "Zubat cutscene re-triggers even when the NPC is gone, trapping progress." Same shape as L14: the Seymour-rescue scene is gated on var **`0x6105`** = **Box 3 slot 4** (D1 range). The (19,6) coord trigger `0x827168` fires on `0x6105==0`; rescuing Seymour (`0x826F81`/`0x827109`) sets `0x6105` to 1/2. Post-rescue re-firing = `0x6105` clobbered back to 0 by a Box-3 deposit. **Second confirmed case of the same pattern → the whole "backtracking-reset / re-trigger" class is largely D1** (Box-3/6 story vars overwritten by PC storage). The (19,6) trigger is also latently fragile (sets no guard of its own), but the trigger var being a Box-3 var is the actual cause. Fix = D1 workaround | engine/data | see D1 |
| **L16** | 🟠 | **root-caused → D1** (new 2026-06-14) | "Teleport Marker Reset" (community list): custom **WARP SYSTEM** destinations stop working after story-flag resets | The WARP SYSTEM (PokéCenter PC fast-travel — menu @`0x86A320` → per-destination handlers @`0x885C7B4`+0x24·N → shared warp executor @`0x886C156`) **routes/gates destinations on `compare var 0x6194` and `compare var 0x7006`**, both **D1 hazard vars** (0x6194 = **Box 3** slot 8; 0x7006 = **Box 6** slot 10). A Pokémon deposited in Box 3/6 clobbers them → the executor's state dispatch (0x6194 ∈ {0,2,3}; 0x7006 == 3) lands wrong → destinations "stop working" / markers reset — same storage→logic class as L14/L15. **Already protected by the box-reserve fix** (reserves Box 3 + Box 6); no separate patch needed. *Third confirmed box-fix protection after L14/L15 (Box-3) and the OI-gym chain `0x7036` (Box-6).* | engine/data | see D1 |
| **M1** | 🟠 | **fixed** ✅ | Pallet Town, Oak's lab south wall (map 3.66) | **Found by our own audit:** ledge prison — the lab door tile (24,15) carries an east-jump ledge behavior; pressing UP from (24,16) hops the player into (25,16), a 1-tile pocket with no exit = permanent softlock 2 screens into the game. Fixed by making the landing tile itself solid (block 0x30DD→0x0405, `tools/fix_ledge_prison.py`); the jump no longer triggers, no routes changed | map data | here |
| **F8** | 🔴 | **fixed** ✅ (2026-06-15) | Talk to a garbage-pointer scene NPC (map 3.72 person33; map 1.59 person4) | **Hard freeze on talk.** A few scene-actor NPCs have a corrupt person-event script pointer (into erased ROM / engine code). Most are benign — the script VM **bounds-checks** opcodes (`RunScriptCommand@0x08069804`, 213-entry table `0x0815f9b4`–`0x0815fd08`), so a pointer decoding to an out-of-range opcode (e.g. starts with 0xFF) just stops. **But two decode to a *valid* `braillemessage` on a wild open-bus pointer first** → the braille text renderer infinite-loops on the non-terminating garbage string → game freezes (verified in-engine: 8M-step pure-software glyph loop, garbage braille box on screen). Fixed by NULLing the two dangerous pointers (`tools/fix_person33_freeze.py`, `tools/fix_person4_159_freeze.py`) so talking runs no script, like the game's many empty-script extras. ROM-wide sweep (`tools/scan_partial_exec.py`) confirms no others. | data | here |

> **All 4 text fixes (T1, T2a–c) visually verified rendering live in-engine** via the
> headless rig (`_emu/`): redirected the bedroom-TV pointer to each fixed string in a
> throwaway test ROM and screenshotted it — see `_emu/text_fixes_proof.png`. This also
> cross-validated every patch offset (the TV showed exactly the expected corrected text).

## Community bug report cross-reference (2026-06-13)

A real, **corroborated** PokéCommunity report (one player listed 8 items; a second
player quoted it and said the same things happened) — traced item by item. **Headline:
our fork already fixes both of this player's game-blocking crashes.**

| # | Reported | Trace verdict |
|---|----------|---------------|
| 1 | "get a pickaxe from a scientist … emulator crashes" | **= F4, FIXED ✅.** The Grampa Canyon rival/pickaxe scene `waitmovement` softlock (Gary's scripted march collides with the dig-site path → infinite retry → game dead). "Scientist" = forum wording; in-game it's the rival. |
| 2 | "i left it as it was" | narrative, not a bug. |
| 3 | "doll competition where rocket team is battling a Lickitung — i try to talk, crash" | **TRACED → F8, FIXED ✅ (2026-06-15).** The Lickitung/Princess-Festival scene scripts are clean (valid trainerbattles; no talkable TR/Lickitung object). The real "talk → crash" is a **freeze**: map 3.72 has a garbage-pointer NPC (person33, the released Machamp in the "release your POKéMON for the kids" crowd) whose script runs `braillemessage` on an open-bus pointer → braille renderer infinite-loops. Sibling in map 1.59 (person4). Both NULL'd → **F8**. *(First pass wrongly called the whole dangling-pointer class a "crash"; the VM bounds-checks opcodes, so only the ones hitting a valid pointer-deref command first actually freeze — corrected.)* |
| 4 | "secret of the breeding centre — talk to Jessie & James crashes; same for Butch & Cassidy; quicksave dies too; blocks Cinnabar (main quest)" | **= F3, FIXED ✅, and proven the ONLY one of its kind.** Original-vs-fork diff: the entire ROM has **exactly one** `call_if cond=6` site (`0x852c63`, the post-battle daycare-return). Both Rocket-duo interactions funnel into it; F3 (`cond 6→1`) eliminates it. The player's main-quest blocker is removed. |
| 5 | "TEAM ROCKET DOES NOT APPEAR IN SAFARI ZONE" | **Re-opens L7 (was low-conf).** Two players now report it → it's a real player-facing gap, not noise. Static finding still stands: the Safari Zone is reused-vanilla FireRed (63/63 stock "SAFARI" strings), so this is most likely **content never authored** (no assets to restore) rather than an authored-then-broken event. Needs a real Safari playthrough to be certain. Not a crash. |
| 6a | "won 6 badges, shows 5" | **L6, stays needs-repro.** All 8 badge-flag setters audited distinct + correct; display proven to count flags correctly (`_emu/l6_proof.png`). The corroboration keeps it open but I still have **no mechanism** — would need a real 6-badge save to catch a gym that skips its `setflag`. |
| 6b | "in Fuchsia, it says WINNING TRAINERS — ASH, GARY" | **Not a bug (cosmetic, intended).** The leaderboard sign template is `"WINNING TRAINERS:"` + runtime name buffers (`[fd][06]`/`[fd][01]`); it fills in the player + rival names. Showing ASH, GARY is working as designed (21 instances of the templated string). |
| 7 | "I can deliver the medicine before helping the warden and Dragonair" | **TRACED → NOT a softlock (2026-06-15); won't-fix.** The Sunny-Town nurse delivery (`0x845DAF`) gates only on delivery var `0x6097`, never the warden var `0x6095` — independent chains, so out-of-order can't block the warden/Dragonair/reward. Real (low-sev) defect: the nurse does `removeitem MEDICINE` with **no `checkitem`**, so you can "deliver" (and pocket a free **bicycle**) without the medicine. The medicine *is* obtainable (give-quest `0x80ED88` reachable via `checkflag 0x0824`). No softlock/crash → documented, not fixed. Detail: `audit/issue7-warden-medicine.md`. |
| 8 | "no screenshot, explained each" | narrative. |

**Net:** of the player's two hard crashes, **both are already fixed** in the fork (#1 F4,
#4 F3). #6b is a non-bug. #5/#6a are re-/kept-open at needs-repro. **#3 is now traced + fixed
(F8); #7 is traced (not a softlock, won't-fix)** — see the 2026-06-15 session record below.

## Session 2026-06-15 — freeze-class audit + worker sweep

Three background workers (warden/#7, doll-crash/#3, map-softlock audit) plus a follow-up freeze-class
sweep. Results:

- **F8 (NEW, fixed) — "talk → freeze" via garbage-pointer scene NPCs.** Decompiling the doll-competition
  map (3.72) for report #3 surfaced scene-actor NPCs with corrupt person-event script pointers (into the
  erased `0x16xxxx` region / engine code). **Correction of a wrong first call:** I initially declared the
  whole class "crash on talk." It isn't — `RunScriptCommand@0x08069804` bounds-checks opcodes against a
  213-entry table (`0x0815f9b4`–`0x0815fd08`), so a pointer decoding to an out-of-range opcode (e.g. one
  starting with `0xFF`) just stops the script = benign no-op. The **dangerous subset** is the few whose
  garbage decodes to a *valid* pointer-deref command first: **person33 (3.72)** and **person4 (1.59)** run
  `braillemessage` on an open-bus pointer, whose text renderer infinite-loops on a non-terminating string →
  hard freeze (verified in-engine: handler ran 8M steps in a pure-software glyph loop, garbage braille box
  on screen). Both fixed by NULLing the pointer. A ROM-wide sweep (`tools/scan_partial_exec.py`) found no
  other genuine cases — the remaining ~258 "wild-deref" hits are the hack's `0x08000000` empty-script
  sentinel (benign: 250+ always-present main-town NPCs use it in a *completable* game; the apparent
  `gotonative` is just the cartridge-header Nintendo-logo bytes mis-decoded). *Residual honesty:* I could
  not construct an in-engine crash for the sentinel class (`warpto` won't faithfully spawn these scene
  NPCs), so its benignity rests on the playability argument, not a direct null result.

- **#3 doll-competition data — clean.** Trainerbattles (gTrainers @`0x0823EAC8`; the Lickitung battle =
  CARL/trainer 157, valid party), `special` indices, and cutscene `applymovement`/movement data all valid;
  no F4-class softlock. The reported "talk → crash" is the F8 freeze above, not a script fault in the
  Lickitung scene itself. Detail: `audit/issue3-doll-crash.md`.

- **#7 warden/medicine — not a softlock (won't-fix).** See the #7 row. Out-of-order delivery is harmless
  (independent flag chains); the only real defect is a missing `checkitem` worth a free bike — low severity,
  patching live story logic isn't justified. Detail: `audit/issue7-warden-medicine.md`. *(That worker's
  "give-quest orphaned / medicine unobtainable" claim was wrong — the give-quest is reachable via
  `checkflag 0x0824`; corrected on my own re-trace.)*

- **Map-softlock audit — 0 new traps.** A full M1/L13-class sweep across all 540 reachable maps found
  nothing new that survives verification (it also caught + discarded a ~146-item phantom-pocket false
  positive caused by a wrong u16-vs-u32 metatile-behavior read; the real field is u32 at tileset+0x14).
  Detail: `audit/map-softlock-audit.md`.

*Process note:* this session reinforced "verify before asserting" twice — the retracted F8 "crash"
(VM actually bounds-checks) and worker A's retracted "medicine unobtainable" (give-quest is reachable).
Both were caught by going back to the bytes/engine instead of trusting the first plausible read.

*Second worker sweep (same session) — two more audit classes, both **clean / no fix**, each independently re-verified by me:*

- **Data-integrity (operand ranges) — clean.** Enumerated all reachable scripts (42,724 decoded
  bytes) and checked every `setwildbattle`(0xB6)/`givemon`(0x79)/`special`(0x25)/`specialvar`(0x26)
  operand. All species 1–411 / levels 1–100 in range. The only scary hit — Celadon Game Corner
  `givemon` "species 16385" — is a `VAR_0x4001` reference (handler `@0x0806BFD0` VarGets it),
  resolving to the valid prize set {35,63,123,137,147}. **I independently disassembled** the
  structural safety net: gSpecials `@0x0815FD60` = 444 entries (end `0x08160450`), and *both*
  dispatchers bounds-check the index (`cmp r1,end; bhs skip` at `0x08069F0E`/`0x08069F5E`) exactly
  like `RunScriptCommand`, so an OOB special index is a no-op, not a crash. Detail:
  `audit/data-integrity-audit.md`.

- **Progression dead-ends (L1/L2/L9 class) — no new dead-end.** Traced the OI-entry gate, the OI
  gym/ferry chain, and a ROM-wide orphan-gate scan (5,438 reachable blocks). The load-bearing gate —
  Orange-Islands entry — is rigged unmissable: a forced `setvar 0x6306,2` (ROM `0x08881CD9`) then the
  raffle's `compare 0x6306,2; goto_if cond=4(≥) → grand-prize/blimp 0x088874EC`. **I independently
  confirmed by byte-search**: the setter, *both* rigged raffle entries (`0x088B55CC` + `0x0889DD89`,
  same target), the condition table (`cond4 @0x083A7248` = `0 1 1` = ≥), and that `0x6306`'s state
  machine only ever climbs (1→2→3→4→5) so it stays ≥2 forever — no skip-window. Only two
  never-satisfiable gates exist ROM-wide (flag `0x150A` = disabled optional ICE HEAL gift; var
  `0x0FA1` = cosmetic Wartortle movement), both benign. The Trovita ferry (`0x7064==3`) is the one
  conditional in-OI gate but has a forced+recoverable setter (Bulbasaur-sewer quest) and an
  unconditional return ferry. Detail: `audit/progression-deadend-audit.md`. *(The worker's prose ROM
  addresses dropped a hex digit — "0x08B55CC" is really `0x088B55CC` — but every byte verified.)*

*Third worker sweep (same session) — **box-fix-IMMUNE** classes (pure-ROM faults that survive the box
reserve; "D1 could've done it" is NOT an available answer here), three more audits:*

- **Control-flow freezes (lock/release, waitstate, ON_TRANSITION) — CLEAN after a retraction.** A worker
  flagged a *"confirmed game-blocking freeze"* on the **first sleep** (map 4.1 bed dream: `lock` → dream →
  bare `end`, no `release`). **I RETRACTED it as a FALSE POSITIVE.** The byte pattern is real and
  **byte-identical to the completable clean 4.5.3** (diffed) — which was the red flag: a real first-sleep
  freeze would make the game unplayable. I drove the *genuine* dresser→bed sequence in-engine from the legit
  `checkpoint.ss` (NO flag-poking): real dresser sets `0x1166`, real bed runs the dream (`0x1006` 0→1), and
  after **fully** advancing the dialogue (`mashA 1800`) the player **wakes, stands out of bed, and walks
  freely** — LOC (3,5)→(4,5)→(4,4)→(3,4), screenshot `_emu/rt_mobility.png`. The apparent freeze was the
  dream's final `callstd 4` "…woke up from his restless sleep." textbox **waiting for a button press**: the
  original repro under-advanced it (`mashA 700`) then tested mobility with **direction keys, which can't
  dismiss a textbox**, so LOC looked stuck. Net: **0 confirmed freezes**; 16 lock/dispatch candidates
  correctly cleared as the benign vanilla "post-`0x7F` default `end`" idiom; 1 remaining **UNCONFIRMED**
  candidate (map 5.4 bridge trig — `lockall`→`goto_if cond=1`→`FF FF` on the post-flag-`0x575` path;
  reachability unproven, not reproduced — worth a later look). Detail: `audit/softlock-controlflow.md`.
  *Lesson reinforced (4th over-claim caught this session): an open textbox waiting for A is NOT a freeze —
  advance dialogue fully, then test mobility only after the box is gone.*

- **Missables / progression-skips (L2/L9 branch logic) — clean.** Reachability-aware sweep of all 54
  reachable givemon/giveegg sites across 19 gift events; every decline/party-full/box-full branch re-offers
  (no removeobject-before-give, no skipped gate). I independently re-traced the **Haunter** event (map 1.89):
  party-full bail leaves `0x6060`<4 and the map-load script re-shows the giver via visibility flag `0x3F`, so
  it stays re-gettable — verified. (Worker-1 and this worker independently counted the **same 54** givemon
  sites = the reachability walk is cross-validated.) Detail: `audit/missable-branch-logic.md`.

- **Warp / map-data validity — clean.** All 550 maps / 1513 warp events: 0 warps to a non-existent map; the
  36 out-of-range warp-ids + 8 warpsilent-into-0-warp-maps are non-crashing. **I disassembled the resolver**
  `SetPlayerCoordsFromWarp @0x080552FC` and confirmed the 3-tier graceful fallback (warpId<0 → fallback;
  warpId≥warpCount → fallback; bad explicit x/y → map-centre) — the same bounds-check-then-fallback pattern
  as the opcode/special dispatch. Detail: `audit/warp-map-validity.md`.

*Fourth worker sweep (same session) — "remaining leads," 3 more box-fix-immune classes:*

- **Lock-then-stop "freeze" class — EMPTY (no real freeze).** Settled the engine question the dream
  retraction raised: does `lock`/`lockall` + a graceful script-STOP (no `release`) freeze? **NO** — the engine
  **auto-releases when the script context stops** (the lock is tied to the running script task). Proven
  in-engine (player walks the entire map after the stop, `_emu/lockjump_575set_walkaway.png`) and corroborated
  by my own first-sleep dream test. Worker A's map-5.4 candidate is **benign**: map 5.4 is the **Viridian PC
  interior** (15×10, NOT a route/bridge); trig0/1/2 gate on **var 0x5025==0** and the script `setvar 0x5025,1`
  immediately → **self-disabling** (I dumped the trigger table to confirm; Worker A had misread the *value*
  field 0x0000 as the gate var). Even on the reachable `0x575`-set branch (0x575 = "trainer 0x75 defeated"),
  it's `lockall` → jump to a `0xFF` opcode → VM stop → **auto-release**, merely skipping the Misty cutscene.
  Full reachability closure (42,495 offsets) found exactly ONE instance of the class — this one — benign.
  (Confirms why **F8 braillemessage WAS** a real freeze: a software render-loop with no auto-release = a
  different class.) Detail: `audit/freeze-lockjump-class.md`.

- **Pokémon data tables (evolutions / learnsets / TM-HM / egg moves) — clean.** Every evolution target 1–411,
  every move id 1–354, every level 0–100, all learnset pointers in-ROM + terminated. Base offsets confirmed by
  signature (gBaseStats `0x254784` → Bulbasaur 45/49/49/45/65/65; gEvolutionTable `0x259754` → Bulba→Ivy
  method 4/param 16). Detail: `audit/pokemon-data-integrity.md`.

- **Wild-encounter tables — clean for Bad-Egg/crash; 1 low-severity typo → FIXED.**
  gWildMonHeaders relocated to `0x088CD1F8` (vanilla 0x3C9CB8 is 0xFF-padded); all 2617 slots have valid
  species (range 10–246). **One real defect:** map (0,17) Surf slot 2 (file `0x72BA88`) read `min=35,max=30`
  for Staryu — a one-byte typo (sibling map (0,16) reads `min=25`). Species valid → no Bad Egg/crash; only an
  underflowed wild-level range (a too-high / wrapped wild Staryu when surfing there). **FIXED** (file
  `0x72BA88`: `0x23`→`0x19`, `tools/fix_wild_0_17_level.py`) → fork build `43216f9f` → **`5cffa700`** (CRC
  `63478921`). Detail: `audit/wild-encounter-integrity.md`.

### #6a "won 6 badges, shows 5" — badge code SOUND; 3 gyms D1-safe (incl. Koga), 4–5 gyms' badge paths D1-gated; not reproduced (2026-06-13)

Hard re-audit at the byte level (`_emu/probe_badges.py` + decompiling all 6 reachable
gym epilogues). The badge flags are 0x820–0x827 at sb1+0xFE4; the card lights one icon
per set flag (`l6_proof.png`: poked 0x3F → 6 icons). Three failure modes that *would*
produce "6 won, 5 shown" — all ruled out:

- **No-setter (a badge unobtainable):** every flag 0x820–0x827 has ≥1 `setflag`. ❌ ruled out.
- **Collision (two gyms set one flag → undercount):** each badge has its own distinct
  setter(s); the multi-setter badges (Rainbow ×3, Volcano ×2, Earth ×2) are alternate
  paths to the *same* flag, not shared flags. ❌ ruled out.
- **Cleared after earning:** **zero `clearflag` on any badge flag** in the whole script
  bank (0x7F0000–0x8D0000). ❌ ruled out.

And every epilogue awards its flag **unconditionally** — straight-line
`special 0x173 → setflag 0x4Bx (leader) → setflag 0x82x (badge) → setvar 0x8008=ordinal`
(Boulder=1 … Marsh=6), with the first `goto_if` only *after* the badge is set (bag-space
check for the TM). Decompiled sites: Boulder 0x824234, Cascade 0x828ADF, Thunder 0x831771,
Rainbow 0x806B24, Soul 0x83FE0A, Marsh 0x83527C.

**Badge award code is sound (verified, stands):** the Soul badge (0x824) is set in exactly one
place — the *continuation pointer* of the first Koga battle (trainer 0x1a2 @0x83fd16, an 18-byte
type-1 trainerbattle whose 3rd pointer → 0x83fe01 → `setflag 0x824`). Winning that battle awards
the badge with **no gate between win and setflag**. There is also a separate Koga **rematch**
(trainer 0x1a1 @0x86eeb1) that deliberately doesn't re-award the badge (correct). These I traced
directly and they hold.

**CORRECTION (2026-06-13) — retracting the "Koga staged on 0x6155" mechanism.** An earlier pass
this day claimed the Koga gym selects its badge battle via `compare 0x6155` (Box 3 slot 6), making
#6a a confirmed Koga-D1 skip. **That was wrong.** `0x6155` is the **P1 Grand Prix** variable, not
a Koga selector: it's set to 1 at *"The path to CELADON CITY isn't quite done yet"* and to 2 at the
*ANTHONY* scene, and both dispatcher branches (`@0x840035`) lead to *"P1 CHAMPIONSHIP"* / *"BLACK
BELT reward for winning the P1"*. The error came from a **region scan** (`probe_koga.py` swept ROM
0x83fc00–0x840500 and called it "the Koga script region," but that span interleaves P1 Grand Prix
scripts) plus a single-sample text label I read through expectation. The var-IDs I listed as "Koga
state" (0x6155/0x6168/0x6173/0x6175/0x6180/0x6092/0x6029) are therefore **unreliable
attributions** — several are P1/Celadon, not Koga.

**Authoritative map-level trace (2026-06-13, `_emu/trace_koga_map.py` + decompiling map 11.3):**
the Fuchsia Gym is **map 11.3** (person1: *"My honored brother, KOGA, is the FUCHSIA CITY GYM
LEADER… hidden in this mansion"*). **Koga = person2, script @0x83FD16 = the bare battle** — no
leading `checkflag`/`compare` guard at all. Win → trainerbattle continuation 0x83fe01 →
`setflag 0x824`, unconditional. And the "beaten" state is in **non-storage** flags:
- Soul badge flag **0x824 → sb1+0xFE4** (safe flag region, no overflow).
- Koga trainer flag **0x6A2 → sb1+0xFB4** (safe), and it's **never** set/cleared/checked by any
  script (0 sites) — only the battle engine manages it, so it's coupled to the win = to the badge.

**Verdict: the Soul badge is NOT D1-skippable. Koga is ruled OUT as a #6a cause.** No story var
gates the award, and neither flag lives in PC storage, so no box deposit can produce "won Koga,
no Soul badge." The only D1-overlapping thing in the mansion is `0x6092` (Box 3 — a trap/cutscene
coord-trigger, `trig0 @0x8B533D`), which could break *navigating to* Koga (an L14/L15-style nav
softlock) but **cannot** skip the badge. My earlier "Koga badge skippable via 0x6155" was wrong
on both the var (0x6155 = P1 Grand Prix) **and** the conclusion (the badge is actually safe).

**So #6a remains: badge system provably sound, Koga authoritatively cleared, NOT reproduced** — and
the reporter being "in Fuchsia" is coincidence. But "some *other* gym" turned out to be the right
instinct: I traced **all 8** gyms the same authoritative way (`_emu/trace_all_gyms.py` →
`trace_gym_gates.py`), and they split:

| Badge | Gym (map) | Badge path gated on… | D1-exposed? |
|---|---|---|---|
| Rainbow | Erika, Celadon (3.6) | clean (no D1 var) | **SAFE** |
| Soul | Koga, Fuchsia (11.3) | bare battle | **SAFE** |
| Earth | Giovanni, Viridian (5.1) | clean | **SAFE** |
| Boulder | Brock, Pewter (6.2) | `0x6082==5` (Box 3 s1) → battle; else "come back stronger" | **EXPOSED** |
| Cascade | Misty/Daisy, Cerulean (7.5) | `0x6190>=3` (B3 s7) + `0x6113>=3` (B3 s4, =L13) gate the badge-*give* | **EXPOSED** |
| Marsh | Sabrina, Saffron (14.3) | `0x6072`/`0x6074` (Box 3 **slot 0** — first to corrupt) | **EXPOSED** |
| Volcano | Blaine, Cinnabar (12.0) | `0x6186` (B3 s7): `==2/4`→"FIRE BLAST" filler; else riddle advance | **EXPOSED** |
| Thunder | Surge, Vermilion (9.6) | entry on safe flag 0x231; a `0x6088` (B3 s1) compare downstream | **maybe** (ambiguous) |

**The corrected #6a verdict:** 3 badges (incl. Koga) are D1-safe; **4–5 gyms' badge paths ARE gated
on Box 3 story vars**, so storing Pokémon in Box 3 can misroute them. The dominant effect is a
**progression block** — the gym routes to filler / post-game / "come back" dialogue instead of the
battle or badge-give (e.g. Cascade's "ballet success," Volcano's "FIRE BLAST" line) — so the player
ends up a badge short on a gym they think they did. That's the same class as L14/L15 (D1 corrupting a
gym's state machine), now shown to reach the **badge count** via Boulder/Cascade/Marsh/Volcano. The
badge-*award* code stays sound; the exposure is in the *staging* that gates reaching it.

**Marsh static value-routing NAILED (2026-06-13, `_emu/marsh_values.py` + decompiling person5):**
Sabrina (Saffron, map 14.3 person5 @0x806505) dispatches on `0x6072` —
`<3`(=0/1/2, in-progress) → match offer → battle → badge; `==3`(legit done) → post-game rematch;
**`>3` → `release;end` (0x806516) = the NPC does NOTHING.** `0x6072` progresses 0→1→2→3 (=3 set at
"Thank you for all your help"). A corrupt Pokémon-data byte is `>3` ~252/256 of the time, and both
gate vars (`0x6072`,`0x6074`) sit in **Box 3 slot 0** (first slot filled). ⇒ **storing in Box 3 mid-
Saffron silently bricks Sabrina → Marsh badge unobtainable.** A hard progression block (inert NPC),
not a display desync — the L14/L15 class, most-exposed in the game.
**LIVE-REPRODUCED (2026-06-13, `_emu/marsh_proof.png`, rig `marsh_repro2.rig` on `tvtest/marsh_test.gba`):**
warped into Saffron gym 14.3, stood at (23,3) facing Sabrina (person5 @24,3). Same tile, same A-press,
only `0x6072` (sb1+0x50E4) differs: **=0x40 → Sabrina silent, no textbox (inert, badge unreachable);
=0 → "Hehehehe!" match offer (badge path live).** First D1 badge-block proven in-engine.

**Full per-gym analysis + fix → `audit/d1-gym-badge-blocks.md`.** Clean "6-shows-5" blockers — **all
three now LIVE-REPRODUCED** (`marsh_proof.png`, `boulder_proof.png`, `cascade_proof.png`): **Marsh**
(slot 0 → Sabrina inert), **Boulder** (slot 1, `0x6082≠5` → "Your POKéMON aren't powerful enough /
come back when you're stronger"), **Cascade** (slot 7, `0x6190≥3` → "the Underwater Ballet was a
success!" instead of handing over the badge). **Volcano** (slot 7) is
exposed but messier — corruption tends to *advance* Blaine's riddles, not hard-block. **Thunder** is
safe (its `0x6088` gates a `setrespawn`, not the battle); **Rainbow/Soul/Earth** safe. Because the
gate is a 16-bit var vs a tiny legit set, near-random box data trips the block branch *almost every
time* — not a rare edge case. **Fix:** real = D1 var relocation (fixes all of D1 at once); band-aid =
re-guard each exposed gym on its **badge flag** (sb1+0xFE4, not storage) so corruption can never
permanently block — per-gym free-space surgery, badge-symptom only. L13/L14/L15 stay valid
(live-verified); Cascade's gate var 0x6113 is literally the L13 var.

## Prioritized — details & fix plans
(Hypotheses to confirm by decompiling the exact script with `tools/decomp.py`.)

### L1 — Indigo Plateau guard (🟠)
*Repro:* all 8 badges + passed entrance exam, guard still says "league hasn't started."
*DIAGNOSIS (confirmed by decompile, 2026-06-09):* The gate is **not** a `checkflag` — it's a
**VAR_0x7014 state machine**. The gate script (reached from the relocated event table @0x723A80)
runs:
```
@0x869E5A  compare VAR_0x7014, 1 ; if == goto 0x8E9081  (enter; that branch sets 0x7014=2)
           compare VAR_0x7014, 2 ; if == goto 0x87FF97  (enter, stage 2)
           goto 0x82789A          → "I'm sorry, but the POKéMON LEAGUE hasn't begun yet…"
```
So 0x7014 must be 1 or 2 to pass. **0x7014 is set to 1 only in the video-phone / Prof-Oak
cluster** (`0x872FED`, `0x87371A`, `0x876111`) — i.e. the league is "started" by a phone/Oak
event, **not** by the exam. The whole exam region (0x84D000–0x851000) only manipulates badge/exam
flags `0x1194–0x1210` and **never writes 0x7014**. ⇒ A player who passes the exam + has badges but
hasn't triggered the (missable) league-start event stays at 0x7014==0 → permanently blocked.
*Open question for the fix:* which condition *should* open the gate — confirm the league-start
trigger is reachable/correct, or make the gate also open on an eligibility flag (badge/exam-pass).
The league-start script uses opcodes the v1 decompiler can't read yet (0x55/0xB7/0xC7) — needs the
fuller opcode table before a confident, low-risk patch. Candidate eligibility flag: 0x1200
("exam passed", set at 0x84EE7A+). **Fix carries progression-break risk; do not guess the flag.**

*FIX APPLIED (2026-06-09):* After completing the decompiler's opcode table, the full gate state
machine was traced. The `0x7014==1` branch (`0x8E9081`) **already contains the correct, complete
eligibility check** — `checkflag 0x1202` (exam passed) → advance, else require all 8 badge flags
`0x820–0x827`; on success it `setvar 0x7014=2` and the guard steps aside, on failure it shows the
game's own *"you don't have enough BADGES"* (`0x87FD10`). That whole check was simply **unreachable**
when `0x7014==0`. The fix rewrites the gate's 16-byte top dispatch (`@0x869E5A`, in place,
guard-checked against the known original) to:
```
compare 0x7014, 2 ; if == goto 0x87FF97   (already entered → "good luck", unchanged)
goto 0x8E9081                              (else → run the existing eligibility check)
```
So `0x7014==0` now runs the real requirement check instead of dead-ending. Unqualified players still
get *"not enough BADGES"*; no design change, just reachability. Tool: `tools/fix_l1.py`.
*Verified:* (a) decompile of the new dispatch is correct (`tools/decomp.py 0x869E5A`); (b) byte-guard
asserted the original before writing; (c) IPS round-trips (base FireRed + patch → fork CRC `5197d6e4`);
(d) boot regression — patched fork boots to the overworld unchanged.
*(e) **PROVEN IN-ENGINE (A/B), 2026-06-11:*** warped headlessly to the gate (warp-event redirect rig,
`_emu/`) and talked to the guard on two ROMs differing **only** in the 16 dispatch bytes, same 0-badge
save: **original** → "the POKéMON LEAGUE hasn't begun yet … Please come back later" (dead end);
**fork** → "you don't have enough BADGES to qualify for the LEAGUE" (the game's own eligibility check
now runs and gives the correct, informative gate). Proof sheet: `_emu/l1_proof.png`.
**Bonus typo found** in this branch — `0x8E90D7` reads "advance to the **INIDGO** PLATEAU" (should be
INDIGO). Logged as **T3** below.

### L2 — Prof Oak with a full party (🟠) — FIXED ✅
*ROOT CAUSE (2026-06-11):* On league day (`0x6192==4`, `0x7012==5`) Oak's lab script returns the
Pokémon he was watching, and ONLY the success path delivers the send-off ("Now get going…") +
`setvar 0x7013,1` — the league-departure progression state. The full-party branch ("You can't
take this POKéMON back if you've got no room for it", `0x871EC9`) jumped back to the menu top:
0x7013 never set → the next event never triggers. (A givemon audit confirmed the gift mons
elsewhere all check `0x800D` properly; this was the one progression-blocking stall.)
*FIX (`tools/fix_l2.py`):* the no-room branch now goes to a free-space stub (`0xC00140`) that
keeps Oak's refusal (the mon stays with him — still collectible later via the existing
"Would you like it back?" flow) but plays the send-off line and sets `0x7013=1`. Verified by
decompile of the new flow; IPS round-trips.

### L4 — running shoes dead (🟢) — FIXED ✅ (class bug, 44 maps)
*ROOT CAUSE:* metapod's map editor **zeroed the header flags byte** (+0x19: escape/run/show-name)
on every vanilla-region map it touched. 44 maps lost the run bit vanilla FireRed had — including
the reported Pallet Town (3.0). *FIX (`tools/fix_l4.py`):* restored the vanilla +0x19 byte on
exactly those 44 maps (value-copy from base ROM). *Verified live:* B+LEFT for 18 frames in
Ash Gray's Pallet covers 2 tiles (run) vs 1 tile without B (walk). *Note:* ~20 custom-header
outdoor maps also carry flags 0x00/0x01 (no run) — left as authored, since custom maps like 3.66
prove metapod set these deliberately when he cared; none are in the bug reports.

### L3 — stuck on Misty's bike (🟡) — needs-repro, natural path proven clean
*Repro (reported):* after Pikachu thundershocks the Spearow, Ash keeps riding the bike.
*EMPIRICAL FINDINGS (2026-06-11):* Full trace of the sequence, all on the big custom Route-1 map
**3.67**: steal scene (`0x860574`, frame `0x6080==1`) gives the BICYCLE item (0x168) + starts the
storm; shock scene (`0x801E71`, triggers (43-45,18) on `0x6079==2`) plays the Spearow confrontation,
`removeitem BICYCLE`, ends the storm, and `warpsilent`s in place. **Headless run of the natural
path is clean**: scene completes, player walks free immediately after (verified by post-scene
movement + position). Crucially 3.67 has `bikingAllowed=0` — the bike can never be MOUNTED during
the chase, so the natural player cannot be riding at the shock. The only stuck-construction:
mount on a `bikingAllowed=1` map (e.g. Viridian) and ride back through the connection before the
shock — Gen3 never auto-dismounts, and after `removeitem` there is no dismount control. That path
is exotic and likely story-gated; the report probably predates 4.5.3 (the 4.3.5-era bug list).
*Decision:* no patch — the only safe scripted dismount would require identifying an FR
special/function address (callnative), unjustified for a non-reproducible 🟡. Re-open if anyone
produces a 4.5.3 save stuck mounted.

### F2 — underwater cave black-screen freeze (🔴) — FIXED ✅
*Repro:* after Dragonite's tournament-invitation message, screen goes black and hangs.
*ROOT CAUSE (found + proven by headless bisection, 2026-06-11):* Map **1.72** (the underwater
cave reached when the raft splinters crossing to New Island — `warpsilent → 1.72 (36,3)` from
the raft script at `0x863725`, which also `removeitem`s the RAFT) has a first-entry swim script
(`0x818284`) that prints *"{PLAYER} grabbed onto the back of {STR_VAR_1} and began to swim!"* —
but **STR_VAR_1 is only filled by the raft script** (`bufferpartymonnick`). Entering the cave any
other way (doors from 1.73/1.74/2.36) — or with hostile leftover buffer contents — makes the text
printer walk an **unterminated garbage buffer** → memory corruption → white flash, black screen,
`gSaveBlock1Ptr` nulled, input dead. Reproduced on demand with the rig; pre-filling the buffer in
RAM eliminated the crash (smoking-gun experiment). A compounding bug: the map's **mapscript
tables overlapped** (type-4 ON_WARP_INTO_MAP read entries A+B; type-2 ON_FRAME started at B), so
the msgbox also ran during the warp transition — illegal context.
*FIX (two layers, `tools/fix_f2_v2.py` + `tools/fix_f2_v3.py`):*
1. Rebuilt map 1.72's mapscripts in free space, un-overlapping the tables: type-4 keeps only the
   harmless surf-state entry (`0x7001→0x8527DF`, proven innocent by single-arm test), type-2 keeps
   only the swim message.
2. Repointed the swim entry to a new script that **fills its own buffer**: uses the raft-chosen
   party slot when `var 0x8004 ≤ 5` (legit arrivals keep the exact anime behavior), else clamps to
   the lead mon. Then prints the original text and self-disarms (`setvar 0x6198,1`) as before.
*Verified:* control vs fixed A/B at the exact splinter landing — control dies (black, sb1 nulled),
fixed renders the cave + swim sprite + full message with input alive after (`_emu/f2_proof.png`);
IPS round-trips (fork CRC `2874ffea`); boot regression clean. *(Note: v1 — a once-only disarm of
the 0x7001 entry — was a wrong theory, reverted by v2; kept in git history.)*

### F3 — breeding-center crash (🟠) — FIXED ✅
*ROOT CAUSE (2026-06-11):* The breeding-center sequence (map **1.43**) is: break-in trigger
(6,15) → Jessie & James dialogue → COHORTS battle (trainer 361, data verified healthy) → post-battle
trigger column x=18 (`var 0x6184==1` → `0x82C79B`) → Butch & Cassidy ambush (trainer 365 "DUO") →
**daycare-mon return script** `0x852C55`. That script guards "party full → open make-room menu" with
```
0x852C5D: getpartysize
0x852C5E: compare 0x800D, 6
0x852C63: call_if cond=6 -> 0x852CA6   ← ILLEGAL: conditions are 0–5
```
The engine evaluates `sScriptConditionTable[cond][result] == 1`; row 6 is out-of-bounds (bytes
`00 00 43` @0x3A7248+18) — never 1 — so **the guard never fired**: with a full party the script
force-returned the daycare Pokémon into 6/6 mons → crash/mon loss. (metapod typed the compared
*value* into the condition byte. Same failure shape as **D2**.)
*FIX:* one byte (`tools/fix_f3.py`): cond `6 → 1` (take-when-EQUAL) — guard now runs exactly when
the party is full. *Verified:* break-in → battle-start → post-battle ambush all run clean headlessly
(`_emu/f3_proof.png`); the full-party branch semantics are proven by the engine's condition table
(row 1 = (0,1,0)); IPS round-trips (fork CRC `5c892f86`). Dynamic full-party repro needs a 6-mon
save (out of scope for the empty-party test checkpoint — noted honestly).

### S1 — malformed if-condition class (🟡) — `wontfix` (verified dead code, 2026-06-11)
ROM-wide scan (`tools/scan_badcond.py`) for if-commands with cond>5 found, besides F3, sites in
the Butterfree-breeding and Pikachu-release events with transposed operands. **Reachability
analysis shows none of them ever execute:**
- **Butterfree-A (`0x804E24`)**: zero references. The LIVE event (head `0x804DD2`, full decompile
  clean) routes via `goto 0x864974`, which contains the **corrected** check —
  `compare 0x8005, 0x000C (BUTTERFREE); goto_if EQ → mating scene; else "Huh? That's not a
  BUTTERFREE!"` — metapod fixed his own draft and left the broken original orphaned.
- **Butterfree-B (`0x80C6B1`)**: inside a junkyard of dead draft code (a stray loadword even
  points at those opcodes as if they were text). Only live head nearby = the "GRINGEY CITY" sign.
- **Pikachu (`0x8107E4`/`0x8107F9`)**: dead bytes after the "YAS GYM" sign script (which `end`s
  immediately); the three event-table refs all target the sign head only.
**Conclusion:** F3's `0x852C63` was the only *live* cond>5 site, and it is fixed. Patching dead
bytes would bloat the IPS for zero behavior change. (cond=103 scan hits were misparses —
`callstd 6` + `message` — also not bugs.)

### F6 — Tangelo Island "back of a building" crash (🔴) — FIXED ✅
*ROOT CAUSE (2026-06-11, two compounding bugs at the Pokémon Park, maps 33.0/33.2/3.83):*
1. **Void-march softlock (the live crash):** the park entrance hall (33.0) has an on-frame
   ejection script (`var 0x7035==0 → 0x8A0E99`, "Thank you for visiting POKéMON PARK") whose
   canned `applymovement`s are written for the back-door re-entry position (5,1)/(5,2) — the
   park (3.83, the area *behind the building*) arms `0x7035=0` on transition. But 0x7035 is a
   **deep-aliased var** (sb1+0x707x — storage-region memory), so fresh/unlucky saves read 0 on a
   *front-door* entry too: the escort marches the player through the wall into the void below the
   map — invisible, frozen, softlocked. Reproduced headlessly on the first try with a fresh save.
   *Fix (`tools/fix_f6b.py`):* frame entry repointed to a free-space wrapper —
   `getplayerxy; if y<3 goto original; setvar 0x7035,1; end` — legit back-door ejections preserved,
   wrong-position entries just disarm.
2. **Dead-map warp (hardening):* the other Tangelo building (33.2, custom layout) kept vanilla map
   33.3's back-door warp event — but Ash Gray's build **deleted 33.3's layout** (356 bytes FF'd at
   0x2D5998–0x2D5AFC: the 15×10 block data + layout struct; header also has a nulled mapscripts
   ptr). Loading it = a 0xFFFFFFFF×0xFFFFFFFF map → crash. The warp tile is inert on the custom
   layout (verified by walking across it), but *fix (`tools/fix_f6.py`)* redirects it to the island
   (3.13 warpId 1) anyway — only route into 33.3, now sealed (verified: no other warp events or
   script warp commands target 33.3).
*Verified:* A/B headless — control: instant ejection → void softlock on front entry; fork: normal
hall + working park attendant ("Welcome to POKéMON PARK!"), `_emu/f6_proof.png`. IPS round-trips
(fork CRC `009a1eda`); boot regression clean.

### F4 — Grampa Canyon pickaxe softlock (🟠) — FIXED ✅
*ROOT CAUSE (reproduced + fixed 2026-06-11):* The PICKAXE handoff is the **rival scene** on
Grampa Canyon (map 1.101) — frame script `0x89D1B1`, armed by the on-transition `x==10` check
(`setvar 0x6158,1`; scene ends `0x6158=2`). The give itself is clean (item 0x116, proper
giveitem/additem). The hang is the EXIT: every branch funnels into
`0x81508F: applymovement obj8(GARY), movm 0x8C6D70 (down×5,left,down×4); waitmovement` — and
Gary's 12-step march **collides with the dig-site path**; the blocked scripted step retries
forever, `waitmovement` never returns, the script never releases → input dead after
"Smell ya' later!" (screenshot-verified: Gary stranded mid-route, no menu).
*Fix (`tools/fix_f4.py`, 10 bytes in place):* `removeobject 8 ; goto 0x86DFFF ; nop nop` —
instant departure, straight to the script's own cleanup (`fadedefaultbgm; setvar 0x6158,2;
release`). The x==15/16 pre-positioning movements (short, verified-terminated) still play.
*Verified A/B* (`_emu/f4_proof.png`): control = locked forever post-give; fork = player walks
and opens the START menu. IPS round-trips (fork CRC `34a3b81d`); boot regression clean.
*Side notes:* the bug-list "scientist" wording came from forum reports — in-game it's the rival.
Dead-draft copies of an older give script exist around `0x814D81-0x814E60` (one even uses
`applymovement` pointing at script bytes) — unreferenced, harmless, left untouched. The
on-transition helper `0x814C9D` contains a context-questionable `waitstate` that is empirically
benign (the canyon loads and plays fine); documented here, not patched.

### L9 — raft soft-lock from declining Dragonite's invite (🔴)
*Repro:* decline Dragonite's invitation to Mewtwo's island → the raft stops working, Nurse Joy won't let you in, and you can't return to Pallet. Some players report the raft item is "gone."
*Hypothesis:* the **decline** dialogue branch leaves a travel/state flag in a dead state with no recovery path (only the *accept* branch re-enables the raft warp).
*LEADS from the F2 dig (2026-06-11):* the raft-crossing script (`0x863725`) **consumes the RAFT**
(`removeitem 0x010C`) before warping to the cave — that's the literal "raft is gone" mechanism.
The crossing yes/no lives at `0x8621D3` → `0x863797` (per-slot water-mon check `0x862293`, 32
species → ride; else "You'd better bring a WATER POKéMON…"). New Island state var is **0x6197**
(only setter: `0x865059` → 2, post-event); wharf gate flag `0x1260` set by Officer Jenny script
`0x8621AD`. The decline branch of the note (`0x861D64` y/n, scripts `0x861D2A`/`0x861CD9`, caller
`0x876B44` region) still needs decompiling to find the dead state.
*Plan:* decompile the decline branch from `0x876B44`'s head → make decline re-offerable (the note
should re-prompt or the raft/ferry stay usable), and consider refunding the RAFT on the cave path.

*FIX APPLIED + PROVEN (2026-06-11):* Decompiled the full invite scene (`0x876B3F → 0x861D2A`,
pier triggers at (10,24)/(11,24) on wharf map 3.56, armed by flag `0x1247`): **accept** gives the
NEO TICKET + `setvar 0x6196,1`; **decline** skips both; BOTH branches end with `setvar 0x6195,1`
and Dragonite leaves + the storm starts — and the triggers fired on `0x6195==0`, so the scene
could never re-offer. Declining = no ticket (New Island gate refuses entry), storm never clears
(needs the island event) → **unwinnable**, exactly as reported. The "raft is gone" detail is the
splinter crossing's deliberate `removeitem RAFT` — harmless once recoverable, since the stormy
crossing prompt doesn't `checkitem` the raft.
*Fix (`tools/fix_l9.py`, 4 bytes):* re-gate the two triggers on **`0x6196==0`** ("no ticket yet")
instead of `0x6195==0` ("scene played"). Decline → re-asked on the next pier visit; accept →
permanently done. No script bytes changed; 0x6195's storm-weather consumer (`0x864CC4`) untouched;
0x6196 verified to have no other readers; the scene is idempotent on re-run.
*Verified A/B in-engine* (`_emu/l9_proof.png`): decline → storm; **original**: empty rainy pier,
re-walking the trigger does nothing, ever; **fork**: Dragonite returns ("has something for you"),
second offer accepted → "put the NEO TICKET in the KEY ITEMS". IPS round-trips (fork CRC
`1fa7faf5`); boot regression clean.

### M1 — Pallet ledge prison at the lab door (🟠) — FIXED ✅ (found by our own audit)
*Found 2026-06-11 while path-probing Pallet (map 3.66) for the F1 campaign:* the lab's south
door tile **(24,15)** carries an **east-jump ledge behavior**. Press UP from (24,16) (i.e. walk
at the lab wall one tile right of the real door) → the player ledge-hops east into **(25,16)**,
a 1-tile pocket that is solid on all four sides. No warp, no trigger, no exit — a **permanent
softlock two screens into the game**, before the player has ESCAPE ROPE-class options. The door
warp on (24,15) itself is unreachable/dead (the real entrance is (24,16)→up at (24,14)'s door…
the block was clearly mis-stamped by the map editor).
*Fix (`tools/fix_ledge_prison.py`, one u16):* make the landing tile (25,16) itself solid by
copying the block from (26,16) — `0x30DD → 0x0405`. The ledge behavior on the door tile still
exists but a ledge jump with a blocked landing **doesn't trigger** (engine checks collision at
the landing square), so UP now just bumps. No new routes, nothing else on the map touched.
First attempt targeted re-stamping (24,15) itself, but the byte-guard caught that it's already
`col=1` (solid) — the ledge *behavior* bits are what fire, and they fire **through** solidity;
blocking the landing is the minimal correct fix.
*Verified:* boot regression clean (`map=4.1 pos=(6,6)`), IPS round-trips from clean FireRed,
fork CRC `d1a0cdc6`.

### D7/D1 — Pikachu disobedience + Bad Eggs after the Viridian PC battle (🟠) — DID NOT REPRODUCE (verified in-engine)
*Community repro (COMMUNITY-REPORTS.md):* if Pikachu **faints** in the first Team Rocket battle
at the Viridian Pokémon Center, it stops obeying afterward; the French patcher additionally pins
**D1 Bad Eggs** as appearing right after this same battle.
*Scene anatomy (traced 2026-06-11/12):* Viridian PC = **map 5.4**. Entry trigger line
(door tiles + (7,7), `0x5025==0`) → Misty bike-confrontation (`0x800680→0x80036F`). Nurse Joy
(`0x81832F`) sets `0x5030=1` *before* the heal prompt. Walking back onto the exit line with
`0x5030==1` → TR ambush (`0x800C9D→0x800AA1`, one-shot flag `0x580`): motto →
**`trainerbattle 9` @`0x80049C`** (trainer 107 "TEAM ROCKET COHORTS", Ekans+Koffing lv5) →
`goto 0x818C55` thundershock cinematic → TR blasts off, `setvar 0x5030,2; setflag 0x205`.
*Why type 9 (FireRed `EARLY_RIVAL`/FIRST_BATTLE):* it is **deliberate design**, not a mistake —
the FIRST_BATTLE machinery gives in-battle tutor commentary, recast as **Nurse Joy** ("Let me
help you!", "Lowering the foe's stats will put you at an advantage.", "Oh, dear! Now what?"),
and a loss continues the script instead of whiting out (the anime flow needs Pikachu to lose
believably and still thundershock TR afterward). The engine also **auto-heals the party** at
this battle's end, vanilla first-battle style.
*Faint-test (2026-06-12, headless rig, 3 runs):* bare battle cold-launched twice
(`tvtest/d7_test.gba`, injected lab trigger) + **the full faithful scene** on the real map
(`tvtest/d7_real2.gba`, script-warp lab→5.4; Misty scene, Joy talk with heal DECLINED, ambush,
battle) with Pikachu at **1 HP, Growl-only turns → guaranteed faint-loss**, real cinematic
continuation. Before/after dumps of: full party (600 B), storage head, daycare region
(sb1+0x2F00), all flags (sb1+0xEE0), all vars (sb1+0x1000), deep-alias area (sb1+0x3000).
**Result: byte-clean everywhere.** Only deltas: friendship 70→69 (standard faint penalty,
decrypted+verified), post-battle heal to 19/19, and the scene's own flags/vars (0x56B, 0x580,
0x205, 0x5025=1, 0x5030=2). No Bad Eggs, no OT/personality change, no obedience-relevant state.
Loss path visually verified: faint → "TEAM ROCKET: No matter!" → Pikachu's scripted
thundershock → blastoff (`_emu/d7_final_sheet.png`).
*Verdict:* the faint-corruption claim **does not reproduce** in 4.5.3. Likely explanations for
the reports: Ash Gray's *designed* disobedience mechanics (Charizard-style ID tricks, "Pikachu
refuses vs Misty") read as bugs, and Bad Eggs from cheat devices (see FAQ). The `9→1` fix idea
is **withdrawn** — it would delete Joy's tutor dialogue and the no-whiteout loss for zero gain.

### L12 — "lose to the Spearows, stuck on wall" (🟡) — DID NOT REPRODUCE (architecture mapped + loss path live-tested)
*Claim (French community patcher):* losing to the Spearows at the start leaves you stuck.
*The hack's whiteout/respawn system (fully reverse-engineered 2026-06-12):*
- Vanilla's after-whiteout script is **hooked at `0x1A8DD9`**: `compare 0x405A,4` → intro
  handler `0x87398F`; else → dispatcher `0x83E1D4` (six per-PC story scenes: Joy's
  Thunderstone offer after losing to Surge w/ respawn-id `0x109`, Brock's taunt `0x206`,
  the exam-fail flow `0x1D02`, … fall-through = plain vanilla heal, benign).
- Every "checkpoint" sets `setrespawn N` (vanilla healspot — actual placement) plus a
  bookkeeping triplet: `0x405A` = (mapNum<<8)|mapGroup of the respawn PC, `0x405B/C` = x/y
  (~60 sites). Intro sets healspot 1 / id 4 → home (4.0) at (8,5).
- Intro handler: stage `0x6079 < 3` → reset stage + set `0x5010=1` → **mom heals you**
  ("MOM: {player}! Your POKéMON are very weak!…"), one-time "You'd better hurry!" nag.
*Live loss tests (rig, multiple runs):* wild-Spearow loss at chase stages 0–2 → whiteout →
home → heal → reset → walk out → re-enter chase → **the chase map's own ON_TRANSITION
repairs the scene flags** (flock 0x1041 re-hidden, lone Spearow 0x1042 restored) → scene
re-doable. No stuck state reachable. (`_emu/l12_clean_sheet.png`)
*Bonus engineering fact (measured):* FR's saveblock anti-cheat relocation **copies the
whole var arena** (markers at sb1+0x3D00…+0x5400 all survive a warp) — the hack's
beyond-array var convention (0x5xxx/0x6xxx) is stable across warps/battles, retiring our
earlier "deep-alias = per-warp garbage" theory for this range.
*Note for harness work:* three false repro alarms were chased down — backwards map entry
with unseeded scene state, synthetic object-flag state, and A-pair text-riding
re-engaging mom's talk script forever (ride out post-battle scenes with **B**-pairs).

### L13 — Cerulean gym pool trap (🟡) — FIXED ✅ (reproduced live, A/B-proven)
*Report:* "Stuck on Cerulean city gym pool" (French patcher's list).
*Reproduced (2026-06-12):* warped to the gym hall (map 7.5, the anime pool with the
numbered diving platforms). Walking up the center pier, one step onto the tip **(8,9)**
permanently strands the player — every direction including the way back refuses.
One-room interior, nothing to interact with from there = hard softlock.
*Root cause:* the tip cell is stamped with a pool-RIM block (0x299, directional edge
behavior 0xF4) at **elevation 1 — the water level** — at the end of the elevation-4
walkway. The rim behavior permits stepping on despite the mismatch; every exit is then
vetoed by the normal elevation check. (The rest of the rim ring is safe — deck-side
entry is rejected, verified by live probes at (4,17) and (2,8); the only other map
sharing this tileset (3.89) has no walkway adjacent to rim tiles. The gym's exit-block
trigger — "You'd better get the CASCADE BADGE from DAISY before you leave" at
`0x6113==3` — and Daisy's `==3` badge-give branch are coherent, not part of the bug.)
*Fix (`tools/fix_l13.py` + `tools/fix_l13b.py`, one u16):* clone the full cell from
(8,10) → tip becomes block 0x2A4, col 0, **elev 4** — a normal bidirectional walkway
end. First attempt kept the old elev bits and merely sealed the tile (the byte-guarded
A/B caught it); the finalize clones elevation too.
*Verified A/B in-engine:* pre-fix: step on tip → all exits dead forever; post-fix: mount
the tip and walk back off ((8,9)→(8,11)→(8,17)), water above still blocks (no new
routes). Boot regression clean, IPS round-trips, fork CRC `18d75e55`.
(`_emu/l13_proof.png`)

### D1 — Bad Eggs / save corruption (🔴) — ROOT-CAUSED (architectural, not byte-fixable)
> **Consolidated catalog → `audit/d1-reproduced-catalog.md`** — every D1 finding (var, box slot,
> what corruption does, proof image) in one authoritative table. Deep dives:
> `audit/d1-var-classification.md` (the 134-var class) and `audit/d1-gym-badge-blocks.md` (the gyms).

*The infamous one.* Community wisdom blames cheats — partly right, but there is also a
**real in-game mechanism**, confirmed live (2026-06-12):
*Mechanism:* FireRed's `VarSet`/`VarGet` index a fixed **256-entry** array at `sb1+0x1000`
(var IDs 0x4000–0x40FF) with **no bounds check**. Ash Gray uses story var IDs far above
that — 0x5xxx and especially **0x6xxx** (0x6061, 0x6079, 0x6113, 0x6147, 0x6192, 0x6196,
0x6198, 0x6306, …). Each overflows the array: `addr = sb1 + 0x1000 + 2*(id − 0x4000)`.
- 0x4100–0x56F3 land elsewhere **inside** SaveBlock1 — the deep tail past the var array
  (sb1+0x3020+, the daycare/records/roamer region). A *separate, UNEXAMINED* overflow zone
  (7 real 0x50xx vars). **NOT** the cause of F2/F6 — see the Fixability correction note.
- **0x56C4+ overflow past SaveBlock1 entirely** (vanilla size 0x3D88) into the adjacent
  **PC storage buffer** (`gPokemonStoragePtr`, right after SaveBlock1 in EWRAM).
*Proof (rig, `_emu/badegg_demo.rig`):* `gSaveBlock1Ptr=0x02025534`, `gPokemonStoragePtr=
0x0202931C`. Var 0x6079's address = `sb1+0x50F2 = 0x0202A626` = storage offset `0x130A` =
**Box 3 (0-indexed box 2), slot 0, BoxPokemon byte +0x46** — inside the encrypted/checksum
region. Poking 0xCAFE "as var 0x6079" made `fe ca` appear there; var 0x6061 (=1) was already
sitting in that box. So: **story progress writes into box-Pokémon data → checksum fails →
Bad Egg**, and conversely **storing Pokémon in boxes 1–3 overwrites story vars → progression
corruption** (the community's "backtracking breaks the game"). One root cause, both symptom
families. Matches "Bad Eggs in Box 3" exactly.
*Why it's mostly playable:* the collisions are probabilistic — a one-shot `setvar` into an
*empty* box slot is harmless; trouble appears once you've actually stored Pokémon in the
overlapping slots (later boxes, extended play) — exactly the reported pattern.
*Which boxes (static analysis, 2026-06-12):* mapped every real story-var (set∩compare in the
script bank 0x80xxxx–0x8Cxxxx, noise-filtered) to its box slot. The author allocated vars in
two blocks that overlap storage: **0x60xx–0x63xx → Box 3** (the bulk; matches the community's
"Bad Eggs in Box 3" exactly) plus the **tail of Box 2** (slots ~27–29, vars 0x6000–0x6049);
and **0x70xx → Box 6** (slots ~10–13). Highest real var = 0x7072. **Boxes 1, 4, 5, 7–14 are
NOT written by any story var** — clean. So there's a real *behavioral* workaround even with no
code fix: keep Pokémon you care about out of **Box 3, Box 6, and the end of Box 2**; the rest
are untouched. (Bidirectional: storing in those boxes also overwrites the vars → can corrupt
story progress, not just the Pokémon.) Caveat: this is the statically-detectable var set;
stragglers would fall in the same allocation blocks → same boxes, so the box-level conclusion
is robust. Cheat-induced Bad Eggs are a separate source and can land anywhere.
*Scope — this IS the "backtracking" reputation (2026-06-13):* quantified the whole story-var
system. **136** real custom story vars (set∩compare in the script bank, range 0x5010–0x7072).
**129 of them (95%) physically overlap PC storage** — 86 in Box 3, 40 in Box 6, 3 in the tail
of Box 2; only **7** land in the SaveBlock1 interior instead (a separate, *unexamined* overflow
zone — **not** the F2/F6 cause; see the Fixability correction). (Special vars
0x8000+ are engine-scratch, not stored, excluded.) So the hack's *entire* story-progression
system is co-located with PC box memory. This is the root of the community's "Ash Gray doesn't
handle backtracking" consensus — but the framing is subtly wrong: **backtracking doesn't cause
the corruption, it reveals it.** Box usage corrupts a story var (or a story var corrupts a
boxed Pokémon → Bad Egg); the damage surfaces later when you revisit a map that reads the
now-corrupted var. Confirmed instances: Route 1 Spearow loop (**L14**, var 0x6079) and Mt. Moon
Zubat loop (**L15**, var 0x6105), both Box-3 vars; Cerulean gym (0x6113) and the Charmander
event (0x6086) are Box-3-gated too. **Most "progression softlock / event-reset / re-trigger"
community reports are this same D1 — not separate script bugs.** (Caveat: every case examined is
D1; can't rule out a genuine logic-reset script in an unexamined event, but none found.)
*Fixability:* **not a byte-patch.** The 0x6xxx vars also persist via the storage save
sectors, so var data and box data are entangled in RAM *and* in the .sav. A real fix means
relocating the var space (patch `VarSet`/`VarGet` to a new bounds-checked array in free
EWRAM) **and** migrating the save format — the "rebuild from scratch" work the project owner
already judged near-impossible. Documented, not attempted.
*Correction (2026-06-13):* earlier notes loosely called the SaveBlock1-interior overflow "the
F2/F6 crash class." **That was wrong.** F2 and F6 were *unrelated* bugs — F2 = a mapscript-table
overlap + an unfilled string buffer; F6 = a dangling warp to a freed map, plus one **Box-6** var
(0x7035) defaulting to 0 (a storage-class deep-alias issue, defensively guarded with a position
check). **The 7 SaveBlock1-interior `0x50xx` vars were never examined.** They overflow into the
deep SaveBlock1 tail (sb1+0x3020–0x3A24, at/past the daycare). In an anime hack that tail is
mostly unused (no roamers / link battles / mystery-gift), so it's *probably* repurposed dead
space — but the daycare proximity, plus the fact that the hack has a live breeding center (F3),
mean it is **unverified, not fixed**. Lower-profile than the PC-storage overlap (7 vars vs 129,
no reported crash cluster pinned to it) but a genuine open gap worth a proper look.
*Investigated to closure (2026-06-13):* the full SaveBlock1-interior write-set is **~29 vars**
(not 7) spanning sb1+0x1600–0x3A26. Mapped against the live save dump:
- **Mailbox** (FireRed `mail[16]` @sb1+0x2E00): vars 0x4F00/0x4F08 (+neighbours to ~0x501F)
  land here. **Verified dormant** — zero `additem` of any mail item (0x79–0x84) in all scripts;
  no Pokémon ever holds mail → the mailbox is never populated *or* read by gameplay.
- **enigmaBerry** (@sb1+0x30EC, contains *ROM function pointers* — the one real crash vector):
  **NOT hit by any var.** No crash-via-corrupted-pointer risk.
- **"Daycare"**: the breeding center (F3) is a **Team Rocket battle** — Cassidy & Butch; the
  "leave your POKéMON in the DAYCARE… might not be legit" text is the scam setup. **There is no
  deposit** → the daycare struct is never written. Dormant.
- **Tail** (vars 0x5025–0x5513 → sb1+0x304A–0x3A26: roamer/berry/mystery-gift/reserved): reads
  zero on a fresh save, and the heavy members are set *16+ times across normal play* with **zero
  observable corruption** — if any hit a live engine-read field the game would visibly break. So
  these offsets are effectively dead space (peripheral FireRed features inactive in the Kanto-
  anime content).
**Conclusion: CLOSED — the SaveBlock1-interior overflow is real but fires no live feature in this
game.** The author's var IDs land in FireRed features the anime hack doesn't use (mail, daycare,
berries, roamer). No crash vector, no Bad-Egg equivalent. The **PC-storage overlap (D1/Bad Eggs)
remains the only real-impact instance** of the unbounded-var-overflow architecture. *Honest
caveat:* mailbox + daycare are definitively verified; the minor tail features (berry/roamer) are
strongly-but-not-exhaustively confirmed inert via the heavy-use-no-crash argument.

*✅ RESERVE MITIGATION — BUILT, PROVEN, SHIPPED (2026-06-13) → `audit/d1-pss-reserve-scoping.md`,
`_emu/fix_boxreserve.py`.* The "reserve" half is now in `patches/ashgray-fork.ips`. The storage UI
**is** patchable: I drove the box UI in-engine (PokéCenter PC → `OAK'S LAB`) and hooked every box-
selection path to **skip hazard boxes {Box 2, Box 3, Box 6}** so a Pokémon can never be placed in a
var-overlapping slot — 6 Thumb hooks calling two free-space skip helpers (`NextSafeFwd`/`PrevSafeBwd`
@0x08197600). Coverage proven: manual L/R box-cycle (UI), the "Deposit in which BOX?" selector (UI —
a *separate* `ChooseBoxMenu` that would otherwise have allowed Box 2/3, caught only by live testing),
and the party-full auto-deposit `CopyMonToPC` scan (runtime — a full BOX1 sends the mon to BOX4, not
BOX2). Usable boxes 14→11. Did NOT do the var-**consolidation** half (the risky var-ID remapping
below) — full-box reserve of all three hazard boxes is simpler and needs no var rewrites. Migration
caveat: protects NEW placements only; a pre-patch save with a mon already in a hazard box isn't healed.
*Read-side investigated to closure (2026-06-14) — BENIGN.* Checked whether anything that scans all boxes
would surface the var-garbage. The one all-box scan in the ROM is the **FireRed Quest Log** ("Previously
on your quest.." recap, module `0x0811xxxx`); its state-clear erases each *occupied* box slot. Occupancy
is the **has-species sanity bit** (field 5), which reads **empty** for var-garbage (verified realistic +
worst-case) — so the Quest Log (and any sanity-gated scan) skips the reserved boxes and never touches the
overlapping vars. A *real* Bad Egg needs a *real* Pokémon in a hazard box whose data a var-write corrupts;
this fix prevents that, and the leftover var-garbage in the empty hazard boxes is inert. (Corrects an
earlier note that read the wrong field — `MON_DATA_SPECIES` decodes to junk `0x19c`, but the game's
occupancy check is the sanity bit, which reads empty.) Detail → `audit/d1-pss-reserve-scoping.md`.

*Original idea (consolidation half — still NOT attempted):* (1) **consolidate** the
overflow vars into the fewest boxes — e.g. remap the tiny Box-2 cluster (3 IDs: 0x6000,
0x6047, 0x6049) into the 0x70xx/Box-6 block, ideally squeezing everything toward one box;
(2) **reserve** the resulting hazard box(es) in the PC UI so the player can never deposit
there *and* the box view never renders the variable-garbage as a Bad Egg. Then vars write to
slots that hold no Pokémon (harmless) and no deposit ever clobbers a var.
- *Gating: RESOLVED — the storage UI IS patchable* (reserve half shipped, above). Consolidation
  remains optional: full-box reserve already closes the deposit vector without it.
- *Remapping risk:* var-ID rewrites must be **atomic and complete** — every setvar/addvar/
  copyvar(src+dst)/compare AND every map **frame-table** `var==val` entry (raw structs in map
  data at 0x70xxxx, invisible to opcode scans). One missed reference splits the var → its gate
  never matches → fresh progression softlock (worse than the Bad Egg). Need structural
  frame-table enumeration from map headers + cross-check, not byte scans.
- *Note:* any NEW scratch var added for a fix should land at a SAFE SaveBlock1-range address
  (away from storage), never in the hazard boxes. No evidence story vars are actually
  "missing" — progression bugs seen so far are logic errors, not var shortage.
- *Scope reduction vs full rework:* save-format-compatible (boxes stay; just unused), touches
  the storage UI + a bounded set of var refs instead of the whole var system + save migration.
  Still real engineering with real risk; only addresses the storage-overlap Bad-Egg class, not
  the separate event-logic "backtracking" bugs (those are per-script fixes like L9/L1).

### D1 var classification — gate vs marker (2026-06-13) → `audit/d1-var-classification.md`

Classified all 192 storage-overlapping story vars by *how* corruption hurts (`_emu/var_classify.py`,
labels via `_emu/label_vars.py`). A var read in a branch (`compare → goto_if`) = **GATE**:
corrupting its slot **misroutes the game** (the L13/L14/L15 mechanism). A var only
`setvar`'d = **MARKER**: the script **clobbers a Pokémon parked in that slot** (Bad Egg) but
can't redirect logic. **The classification (counts, box/slot) is solid; the event LABELS below are
unreliable hints** — the auto-labeler mislabeled `0x6155` as "Koga" when it's the P1 Grand Prix var
(see #6a correction), and even tags known-good `0x6113`/Cerulean as "Valencia Island."

- **134 GATE-capable** vs **58 marker-only.** So the "backtracking breaks the game" class isn't a
  handful of scripts — it's **~134 story beats**, all one root cause (D1). Only **L13/L14/L15** are
  *confirmed* members (live-verified separately); the rest are exposures of the identical mechanism,
  not individually reproduced.
- **Box map:** Box 3 = 89 gates (slots 0,1,4,5,6,7,8,10,17), Box 6 = 42 gates (slots 10–13, the
  0x70xx vars), Box 2 = 3 gates (tail slots 27/29: 0x6000,0x6047,0x6049) + 5 markers. Boxes
  1,4,5,7–14 clean.
- **Deposit-exposure timeline:** Box 1 fully safe; Box 2 safe through slot 26; **first corruption =
  Box 2 slot 27 → 0x6000** ("can't warp where you haven't been") — i.e. **~57 stored Pokémon before
  anything breaks**, which is exactly why only heavy/long-save players hit it. Box 3 slot 0 corrupts
  the opening Spearow chase (0x6079).
- **Other events this MIGHT expose** (label hints only — *unverified*, treat with suspicion given the
  0x6155 mislabel): a possible Celadon/Erika-gym tie (0x7012), P1 Grand Prix (0x6167/0x6069),
  Snorlax/Poké Flute (0x6143), well/Shellder (0x6194), Kaz-Yas feud (0x6137), video-phone (0x6117/
  0x6306). None of these are confirmed; each would need a real map-script trace. Two **master vars** —
  **0x6173** (83 refs) and **0x6300** (92 refs), both Box 3 — are referenced game-wide; corrupting them is
  the most destructive single hit.
- *Caveat:* GATE = structurally misroutable; only L13/L14/L15/#6a are individually reproduced. Labels
  are one-sample hints (master vars span many scenes). Mitigation unchanged: remapping must cover all
  192 (gates **and** markers), not just the 3 Box-2 gates the earlier note named.

## By design — NOT bugs (FAQ, so we don't "fix" them)
- **HMs are replaced by key items** — Hatchet = Cut, Raft = Surf, etc. Cut/Surf "not working" is expected.
- **Brock's first battle is a scripted loss** — even if you beat Onix, the story treats it as a loss (anime-accurate).
- **Pikachu refuses to battle Misty** — must use other Pokémon for the Cerulean gym (anime-accurate).
- **Charmander/Charizard disobeys** — its ID is deliberately changed so it disobeys after evolving (anime-accurate).
- **"Stuck, don't know where to go"** — Ash Gray follows the anime; many gates are story-flag based, not bugs.
- **Bad Eggs / freezes from cheats** — cheats cause *some* instability, but Bad Eggs also have a confirmed *in-game* cause (story vars overflowing into PC storage); this is architectural, not a cheat artifact. See **D1** for the root-cause analysis. NOT in the "harmless by design" category — it's a real, unfixable-without-rework bug.
- **Trade evolutions are adapted** — you can't trade in a single-player hack, so Kadabra/Machoke/Haunter/Graveler evolve by level or other means; not a bug.

## Known limitation (not fixable — no content exists) → `audit/oi-progression-map.md`
- **The hack is unfinished**, ending partway through the Orange Islands / Orange League. **Precise reach
  (ROM-wide name search + map graph, 2026-06-14):** built through **Gym 3** — Valencia (Ivy/GS Ball) →
  Tangelo (Tracey) → **Cissy/Mikan, Danny/Navel, Rudy/Trovita** (all with badges), plus filler islands
  (Pinkan, Mandarin, Moro) and the Nastina/Maiden's-Peak sea episodes. **Gym 4 (Luana/Kumquat) and the
  entire finale (Drake/Pummelo Stadium) were never authored** (0 ROM hits) — so the saga's *final boss*
  does not exist. The empty stub map `3.18`/bank 37 is the dev's frontier (unbuilt next island), not a
  designed ending. Nothing to fix here unless new content is authored.
- *Within the reachable arc:* the three gyms are structurally built and crash-free in script (real
  `trainerbattle` + badge-flag/`var 0x7036` completion logic; no corpse-warps, no broken gate found).
  Not statically provable is whether the custom gym mini-games are *winnable* (needs in-engine late-game
  play) and whether every island unlocks from the prior badge (custom ferry routine @`0x087534B8`, not
  fully reversed). **F7** (a "lady event" crash) remains unpinned (needs a real repro).
- **★ Cross-link to D1:** the OI gym-progress var **`0x7036` physically lives in Box 6** (a D1 hazard
  box). So depositing a Pokémon in Box 6 can clobber the gym chain — the OI arc is **protected by the
  box-reserve fix** (which reserves Box 6). See the D1 reserve-mitigation note above.

## Sources
PokéCommunity dev thread 180722; PC 436579 (freeze), 444362 (4.3.5 bugs), 493681 (unplayable glitch);
Vizzed 71285 / 45433; Fandom *Pokémon Ash Gray*; Quora (input-freeze report); chaptercheats walkthrough (event locations).

## Research status — blocked sources & exactly what I need from you

The ~25 issues above are everything the **open web** exposes. The richest remaining bug
lists are behind anti-bot walls I cannot fetch (confirmed this session):

| Source | Status | Why it matters |
|--------|--------|----------------|
| **PokéCommunity dev thread #180722** | 🚫 HTTP 403 (Cloudflare) | metapod23's **first post** holds the changelog + a "known bugs" list |
| **Fandom — *Pokémon Ash Gray*** wiki | 🚫 HTTP 403 | likely a Bugs / Trivia section |
| **Internet Archive / Wayback** | 🚫 fetch blocked | would snapshot the above |
| pokemoncoders / Fandom mirrors | 🚫 HTTP 403 | secondary write-ups |
| RetroAchievements forum #2211 | ⚠️ flaky / low value | mostly achievement notes |

### You do NOT need to grab hundreds of posts — just one of these:
1. **The FIRST post (OP) of PokéCommunity thread 180722** — copy/paste its text (or screenshot). It usually contains the full changelog + any "Known Bugs" list. *(One page.)*
2. **Any "Bugs" / "Glitches" / "Trivia" section** of the Fandom Ash Gray page. *(One section.)*
3. **Best of all:** the community **"Bugs & Glitches guide"** that grades issues 🔴/🟡/🟢 (referenced in search results but never linked) — if you can locate that single post, it's the jackpot.

➡ **Paste anything you find into [`COMMUNITY-REPORTS.md`](COMMUNITY-REPORTS.md)** — it has
marked paste blocks per source plus an "already handled" cheat-sheet so you can skip
known items while skimming. I'll triage every line from there into this tracker.

