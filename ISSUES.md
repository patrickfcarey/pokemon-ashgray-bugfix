# Ash Gray fork — issue tracker

Live tracker for the bug-fix fork of Pokémon Ash Gray (beta 4.5.3, by metapod23).
Research sources in `audit/05-known-bugs.md`. Add findings here as we go.

**Severity:** 🔴 critical (crash/softlock/blocks progression) · 🟠 high · 🟡 medium · 🟢 low/cosmetic
**Status:** `open` · `next` (queued) · `wip` · `fixed` · `wontfix` · `needs-repro`
**Fix-where:** `here` (byte/script/data edit) · `map` (event/warp struct edit, headless but more work) · `art` (needs human) · `engine` (battle/system, hard)

## Master list

| ID | Sev | Status | Area / trigger | Summary | Type | Fix-where |
|----|-----|--------|----------------|---------|------|-----------|
| **F1** | 🟠 | open | Pidgeotto fight (early) | Freeze when Pikachu takes first hit; camera scrolls too high | freeze/camera | here/map |
| **F2** | 🔴 | next | Underwater cave, after Dragonite tournament msg | Black-screen freeze | freeze | here |
| **F3** | 🟠 | next | Breeding center | Crash talking to Team Rocket (Jessie/James) | crash | here |
| **F4** | 🟠 | next | Islands after Grampa Canyon | Crash/softlock getting pickaxe from scientist | crash | here |
| **F5** | 🟠 | open | Early Spearow vs Team Rocket | Catch Spearow early + use it → heavy glitching | script/flag | here |
| **F6** | 🔴 | open | Tangelo Island arrival | Crash going through the back of a building | crash | here/map |
| **F7** | 🟠 | open | 2nd Orange Island, Nastina doll-competition lady | Crash on that event (persists across patches) | crash | here |
| **L1** | 🟠 | next | Indigo Plateau gate | Guard says league hasn't started despite badges + exam | flag logic | here |
| **L2** | 🟠 | next | Prof Oak, full party | Can't receive Pokémon → next event won't trigger | give logic | here |
| **L3** | 🟡 | next | After Pikachu thundershocks Spearow | Ash stuck on Misty's bike | state flag | here |
| **L4** | 🟢 | open | Pallet Town / Route 1 | Running shoes don't work | map attr/flag | here/map |
| **L5** | 🟡 | open | Hidden Village | Wrong mapping / traps with no exit (need Escape Rope/Dig) | map data | map |
| **L6** | 🟡 | open | Badge UI | Winning 6 badges shows as 5 | flag/UI | here |
| **L7** | 🟡 | open | Safari Zone | Team Rocket doesn't appear (event missing) | event | here |
| **L8** | 🟡 | needs-repro | Safari Zone | Stuck without the bike (no escape route) | progression | map |
| **D1** | 🟡 | open | Storage boxes | Bad Eggs appear (often cheat-induced) | data | here |
| **D2** | 🟠 | open | Eevee brothers event | Deposit Squirtle to make room → Squirtle disappears | storage event | here |
| **D3** | 🟡 | open | First Jessie & James battle | Switching Pokémon makes other mons invisible | battle/script | engine |
| **D4** | 🟢 | open | Teachy TV | Broken / non-functional | item/data | here |
| **D5** | 🟢 | open | Route 1 | Release glitch when releasing Pidgeot while holding Pidgeotto | storage | here |
| **D6** | 🟢 | open | Pokédex | Onix's type listed incorrectly | data | here |
| **G1** | 🟢 | open | Ash girl-disguise battle sprite | Mis-colored (shirt blue, hair white) | graphics | art |
| **T1** | 🟢 | **fixed** ✅ | Bulbasaur village line (0x834CBF) | Duplicated word "the the" | text | here |
| **T2** | 🟢 | open | Various dialogue | Typo candidates (dup-word / space-before-punct) — see `audit/04` | text | here |

## Prioritized — details & fix plans
(Hypotheses to confirm by decompiling the exact script with `tools/decomp.py`.)

### L1 — Indigo Plateau guard (🟠)
*Repro:* all 8 badges + passed entrance exam, guard still says "league hasn't started."
*Hypothesis:* guard's `checkflag` tests a "league open" flag the exam-pass event never `setflag`s (or tests the wrong flag id). Possibly related to **L6** (badge-count miscount feeding a `compare`).
*Plan:* decompile the Indigo gate guard person-script + the exam-pass script → align the flag/`compare`.

### L2 — Prof Oak with a full party (🟠)
*Repro:* full party when the story wants to hand you a Pokémon → nothing happens, event stalls.
*Hypothesis:* script uses `givepokemon` with no full-party fallback; the progression flag is set *after* the give, so a silent give-failure also blocks the flag.
*Plan:* add a party-space / `givepokemon`-result check + "your party is full" message and send-to-box; ensure the progression `setflag` runs regardless.

### L3 — stuck on Misty's bike (🟡)
*Repro:* after Pikachu thundershocks the Spearow, Ash keeps riding the bike.
*Hypothesis:* the bike scene sets an "on bike"/movement-override state that the post-event script forgets to clear.
*Plan:* decompile the Spearow/thundershock aftermath script → `clearflag` / reset player movement state (`special` that restores normal movement).

### F2 — underwater cave black-screen freeze (🔴)
*Repro:* after Dragonite's tournament-invitation message, screen goes black and hangs.
*Hypothesis:* a `special`/warp with no `waitstate`, a `goto` into non-script bytes, or a fade with no fade-in. Classic causes of black-screen hangs.
*Plan:* decompile the Dragonite-message script and the following warp/transition → find the dangling opcode/pointer.

### F3 / F4 — breeding-center & pickaxe-scientist crashes (🟠)
*Hypothesis:* a bad command (corrupt pointer, `applymovement` to a non-existent object, or a `trainerbattle`/`special` with bad args) in those NPC scripts.
*Plan:* decompile each NPC's person-script; compare structure to a working analogue; patch the offending opcode.

## By design — NOT bugs (FAQ, so we don't "fix" them)
- **HMs are replaced by key items** — Hatchet = Cut, Raft = Surf, etc. Cut/Surf "not working" is expected.
- **"Stuck, don't know where to go"** — Ash Gray follows the anime; many gates are story-flag based, not bugs.
- **Bad Eggs / freezes from cheats** — using GameShark/all-badges cheats causes much of the instability (see D1).

## Sources
PokéCommunity dev thread 180722; PC 436579 (freeze), 444362 (4.3.5 bugs), 493681 (unplayable glitch);
Vizzed 71285 / 45433; Fandom *Pokémon Ash Gray*; Quora (input-freeze report); chaptercheats walkthrough (event locations).
