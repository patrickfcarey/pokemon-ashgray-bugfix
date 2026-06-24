# Pokémon Ash Gray — Foolproof HARDCORE RetroAchievements Guide

*For RA set #5245 "~Hack~ Pokémon AshGray Version" — 139 achievements / 686 points, GBA, beta 4.5.3.*

This guide is built from two sources, kept honestly separate:
- **Our reverse-engineering audit** of the game's code (authoritative on the *bugs* — exactly which
  boxes corrupt saves, where the crashes are, and the precise player-side action that dodges each).
- **The RA community guide** (RA forum topic 2211 + the official achievement list) — authoritative on
  the *missables and order*. Where the community couldn't confirm something, it's flagged UNVERIFIED.

> **The core trade you've accepted:** Hardcore credit requires the *unmodified* ROM, so every bug
> we patched in the fork is still live here. This guide turns each of our fixes into a thing **you**
> do by hand. The single most bulletproof option would be to play our fork (all bugs fixed) — but
> that forfeits credit. For *credited hardcore*, discipline replaces the patch. That's what this is.

---

## ⭐ THE SURVIVAL CARD (read this even if you read nothing else)

1. **NEVER store a Pokémon in the 2nd, 3rd, or 6th box** (BOX 2 / BOX 3 / BOX 6). Use 1, 4, 5, 7–14.
   This one rule prevents the save-corruption that silently breaks gym badges, story events, and
   fast-travel, and spawns Bad Eggs. It is the #1 cause of "my game broke and I don't know why."
2. **In-game SAVE before every gym, cutscene, named event, and achievement attempt.** Keep rotating
   **backup copies of your `.sav` file** between sessions (the community endorses this for this set).
3. **Do EVERY Kanto achievement and beat the Elite Four BEFORE leaving for the Orange Islands.**
   There is **no way back to Kanto.** Don't go wandering south with Surf+Cut until Kanto is 100% done.
4. **Keep a party slot open** at the Breeding Centre Team Rocket scene (full party = crash).
5. **Don't evolve** Charmander / Squirtle / Pidgeotto until their event fires (see §5). *(Bulbasaur — evolve anytime.)*
6. **Don't let Pikachu faint** in a Team Rocket battle — it permanently stops obeying you.

> 📋 **Just want to follow along while you play?** Jump to **§8 — the Sequential Play-Order Checklist** at
> the bottom: it interleaves every catch, evolution, crash, missable, and save point in game order.
> §1–§5 are the reference / *why* behind it.

---

## 1. Setup — make sure it actually counts

1. **Get the RA-supported ROM.** The standard Ash Gray **4.5.3** ROM (commonly-cited MD5
   `92262059190c05a5615be6b98612fb14`) is what the set targets. **Do NOT use our fork** — its hash is
   `04d28f01…`, which RA will not recognize, so nothing would count.
   - **Foolproof check:** load the ROM in your RA emulator. If it's recognized (you see the game title
     and "139 achievements"), you have the right file. If it says *unknown/unsupported*, your ROM is
     the wrong dump — get the RA-supported version (RA distributes the correct file/patch).
2. **Emulator:** an RA-enabled one — **RetroArch** with the **mGBA** core and the Achievements option
   enabled, or an official RA standalone. **Turn Hardcore Mode ON** and log into your RA account
   *before* loading the game (toggling hardcore mid-session resets the game).
3. **Hardcore rules** (what you're allowed):
   - ✅ Allowed: in-game **Save**, **Soft Reset**, fast-forward, and **backing up your `.sav` file**
     between sessions.
   - ❌ Forbidden: **savestates**, cheats/codes/Game Genie, rewind, slowdown. (Loading a savestate
     instantly drops you to softcore for the session.)

---

## 2. ⚠️ BOX DISCIPLINE — the save-killer (D1). This is rule #1 for a reason.

**Never store a Pokémon in the 2nd, 3rd, or 6th box of the PC.** Safe boxes: **1, 4, 5, 7, 8, 9, 10,
11, 12, 13, 14.** When *depositing*, also don't let the "Deposit in which BOX?" selector land on box
2/3/6 — pick a safe box explicitly.

**Why (the mechanism we proved):** Ash Gray stores its extended story-progress *variables* in memory
that **physically overlaps the PC box storage**. Depositing a Pokémon into box 2/3/6 overwrites those
variables. Confirmed consequences (several reproduced in-engine):

- **Gym badges break.** Boulder, Cascade, Marsh, and Volcano badge paths are gated on box-3 variables.
  Corrupt them and the gym routes to filler dialogue instead of the battle/badge — you end up a badge
  short on a gym you *thought* you beat. (We live-reproduced Sabrina going completely inert.)
- **Events re-trigger / soft-lock.** The opening Spearow chase re-forces forever; the Mt. Moon /
  Seymour scene re-fires; the PokéCenter fast-travel ("teleport markers") stops working.
- **Orange-Islands gym progress** lives in **box 6** — corrupt it and the OI gym chain breaks.
- **Bad Eggs.** A real Pokémon parked in a hazard box gets its data overwritten → checksum fails →
  Bad Egg.

> The RA community guide only warns about **box 3**. Our audit found **box 2's tail and box 6 are
> hazards too** — so this guide reserves all three. (Box 6 is the Orange-Islands one, which matters
> for the late game.) Following this rule makes you *safer than the community's own advice.*

---

## 3. SAVE DISCIPLINE — surviving the crashes & soft-locks

Universal rule: **Save in-game before every event, and keep rotating `.sav` backups.** Below is the
audit-derived landmine map with the *specific* action that dodges each one. (Confidence note: these
bugs are confirmed in beta 4.5.3, which is what the RA set is based on. The RA-distributed build
*might* have patched a few — if you never hit one, great; saving first costs nothing.)

| # | Hazard | Where / when | **What YOU do to survive it** |
|---|--------|--------------|-------------------------------|
| M1 | **Ledge-prison softlock** (permanent, ~2 screens in!) | Pallet Town, the south wall of Oak's Lab | **Don't press UP against the lab wall one tile to the right of the door.** That tile ledge-hops you east into a 1-tile dead pocket with no exit. Enter the lab from directly below the door. |
| F1 | **Forest battle freeze** (engine-level, intermittent) | Viridian Forest scripted Caterpie / Pidgeotto battles | **Save before entering the forest.** If it freezes (black screen, input dead), **soft reset** and refight — it's non-deterministic and clears on a retry. |
| L5 | **Hidden Village pit** (no exit) | Hidden Village (Bulbasaur area) — off-color grass patches | **Carry an Escape Rope** (or a Pokémon with Dig). Avoid the differently-colored grass; if you fall in, Escape Rope out. |
| L2 | **Oak full-party stall** (blocks league departure) | Prof. Oak's lab, league day, getting your watched Pokémon back | **Have an open party slot** when you talk to Oak that day, so he can hand the Pokémon over and trigger the send-off. |
| L1 | **Indigo gate: "league hasn't begun"** (blocks the E4) | Indigo Plateau gate, after badges + exam | The gate opens on a **league-start event** (a video-phone / Prof. Oak scene), *not* the exam. Make sure you've triggered that story beat; don't skip the pre-league phone call. |
| F3 | **Breeding Centre crash** (blocks Cinnabar/main quest) | "Secret of the Breeding Centre" — talking to Jessie & James, then Butch & Cassidy | **Keep a party slot open (≤5 Pokémon)** before talking to them. The crash only fires with a full party. |
| F4 | **Excavation pickaxe softlock** | Grampa Canyon, getting the pickaxe (the rival hands it over) | **Save right before.** If the rival walks off and you can't move, **soft reset** and retry. (Honest: this is a scripted-movement collision; reset-retry is the clean-ROM tool. See the emergency hatch in §6 if it won't clear.) |
| F2 | **Underwater-cave freeze** (black screen) | New Island / Dragonite arc, the raft crossing | **Take the normal story raft crossing** (it sets up the scene correctly) and **save before** the crossing. Don't try to reach that cave by side doors. |
| L9 | **Raft soft-lock** (unwinnable) | Dragonite's invitation to Mewtwo's island | **Accept the invitation.** Declining leaves the raft/island in a dead state with no recovery — you can neither progress nor return. |
| L13 | **Cerulean Gym pier softlock** (one step) | Cerulean Gym (Misty), the diving-board / pier tip over the water | Don't step out onto the very tip of the diving board over the pool; the rim tile there can trap you in a one-room gym. Save before the gym. |
| F6 | **Tangelo Park "back of building" void** | Orange Islands — the Pokémon Park building | **Save before.** If you get escorted through a wall into the void, soft reset. |
| F7 | **OI "lady" event crash** (unconfirmed) | Orange Islands — the Nastina/Tentacruel or Maiden's-Peak lady scenes | Precautionary: **save before Orange-Islands cutscenes.** We could not confirm a hard crash here, but the report exists; a save costs nothing. |

**Also expect, by design (not bugs):** Charizard won't obey until the Orange-Islands "Charizard
Chills" event ("Defeat Tad…"); some Pokémon refuse orders in specific scripted fights. Don't reset
over these — they're intended.

---

## 4. MISSABLE DISCIPLINE — the point of no return & the checklist

### The one hard wall
**Finish 100% of Kanto — every sidequest achievement — and beat the Elite Four BEFORE you leave for
the Orange Islands.** The game *"was never completed past the Orange Islands and there is no way back
to Kanto."* Worse, the transition is **not a locked door** — once you have **Surf + Cut** you can
physically wander into Orange-Islands water and strand yourself with Kanto achievements unearned. So:
**don't explore the southern sea routes until your Kanto checklist is done.** Everything after the
**"Where it all began"** achievement (the post-Championship sky battle) is Orange-Islands content.

### The authoritative 42 missables (RA "missable" filter — confirmed 2026-06-14)

Grouped in rough play order. **⚠️ = needs a specific Pokémon, a deliberate loss, or a one-time choice.**
Save before every one of these, no exceptions.

**A. Kanto journey (14)**

| Achievement | What it needs | Watch-out |
|---|---|---|
| **Prepare for Trouble…** | Defeat Team Rocket in the **Viridian Pokémon Center** | Very early (the Pikachu-vs-TR scene). *Not the forest — that's the non-missable "Make It Double."* |
| **Give Me Back My Pokémon!** | Get your **Metapod back from the Beedrill** | Viridian Forest — don't rush through |
| **Unbeaten** | Defeat **AJ** in his mini-gym | One-time roadside gym (AJ's win streak) |
| **Elder vs. Child** ⚠️ | **LOSE** to **Lt. Surge** 1-on-1 with **Pikachu** | Deliberate loss — do it *before* winning the gym |
| **Worth the $500** ⚠️ | **Choose Magikarp** from the salesman / vs Team Rocket on the **St. Anne** | One-time choice, no rematch |
| **The Kraken** | Defeat the **giant Tentacruel** | Porta Vista / Nastina sea event |
| **Shed a Tear** ⚠️ | Look at **all 4 Pokémon in the abandoned house** *without adopting any* | Don't adopt, don't leave early — exact |
| **No More Monkey Business** ⚠️ | **Capture** the **Primeape** that stole your hat | Catch it, don't just beat it |
| **Sludge Monster** ⚠️ | **Capture** the **Muk** in the Power Plant | You need this Muk for League R4 (below) |
| **Santa Is Real** | Meet **Santa** in the North Pole | One-time event |
| **Cold Together** | Bring a **friend** (keep a party slot) to a **Snow Island** cave | — |
| **An Absolute Unit** ⚠️ | **Capture Snorlax** and end the drought | Catch it (Wake-Up-Snorlax dam) |
| **Wrong Meowth** ⚠️ | Catch the **wrong Meowth** (in the grass) for Tommy | The "correct" one is by the house; you want the grass one |
| **Pokémon Whiz Kid** ⚠️ | Pass the **Pokémon-League exam** with a **perfect score** | Can't retake; reported flaky — save & verify the pop |

**B. Mewtwo's New Island — "Pokémon Palace" (5)**

> ⚠️ **ACCEPT Dragonite's invitation.** Declining both strands you (our **L9** soft-lock) **and** skips all 5 of these one-time battles.

| Achievement | What it needs |
|---|---|
| **Water Battle** | Defeat **Fergus** in the Pokémon Palace |
| **Not The Right Mix** | Defeat **Corey** in the Pokémon Palace |
| **Not-So-Normal Type** | Defeat **Neesha** in the Pokémon Palace |
| **Giant Onix** | Help **Bruno** capture an Onix |
| **Become a Pokéhuman** | Get **trapped in a giant Pokéball** |

**C. Cinnabar / Blaine (3) — order-sensitive**

| Achievement | What it needs |
|---|---|
| **Just Like in the Game** | Defeat **Blaine in the volcano** |
| **Freezer Bomb** | Defeat **Team Rocket in the volcano** |
| **Just Like in the Anime** ⚠️ | Beat **Blaine on TOP** of the volcano with **Charizard** — you must **lose once** to unlock the top fight |

**D. The Indigo League gauntlet (17) — almost half the missable list**

One long chain of one-time battles. **Enter the League with all five of these ready: Kingler · an un-evolved Squirtle · Pikachu · Muk · Charizard.** Each tournament round pairs a "win" with a "win using a specific Pokémon":

| Achievement | What it needs |
|---|---|
| **First Taste Of Success** | Beat **Mandi** (round 1) |
| **Easy League Start** ⚠️ | Beat **Mandi** (R1) **with Kingler** |
| **Acting Like He Won the Competition** | Beat **Kevin** (round 2) |
| **Skull Bashing Kevin** ⚠️ | Beat **Kevin** (R2) **with Squirtle** |
| **Ice Field Triumph** | Beat **Pete** (round 3) |
| **Water and Electricity** ⚠️ | Beat **Pete** (R3) **with Pikachu** |
| **Beltastic** | Beat **Jeanette** (round 4) |
| **Fourth Round Muk Day** ⚠️ | Beat **Jeanette** (R4) **with Muk** |
| **We Really Won?** ⚠️ | Beat **Richie** (round 5) |
| **Oh, We Lost…** ⚠️ | **LOSE** to **Richie** (R5) using **Charizard last** |
| **Beat the One Who Beat Gary** | Beat **Melissa** (semifinal) |
| **You Are the Champion!** | Beat **Gideon** (final) |
| **Ice-Cold Master** | Beat **Lorelei** (Elite Four) |
| **Solid-Ground Fighter** | Beat **Bruno** (Elite Four) |
| **Spirit-Tamed Elder** | Beat **Agatha** (Elite Four) |
| **Dragon-Fierce Warrior** | Beat **Lance** (Elite Four) |
| **You Were Ready!** | Beat **Slate** (the Champion) |

> ⚠️ **The Richie fork — your single most important backup-save point.** *We Really Won?* (win) and
> *Oh, We Lost…* (lose with Charizard last) are **opposite outcomes of the same one-time battle** — you
> cannot get both in one run normally, and losing likely ends your tournament run (skipping
> Melissa/Gideon/Elite Four). **Back up your `.sav` right before round 5:** throw the match on the backup
> for *Oh, We Lost…*, then restore and win through on your main file. (Same gray-area `.sav` practice as §6 —
> the purist alternative is a second playthrough.)

**E. Post-Championship → Orange Islands (3)**

| Achievement | What it needs | Watch-out |
|---|---|---|
| **Where It All Began** ⚠️ | Defeat **Fearow** in the **sky battle** | Need a **Pidgeot** in your party after the Championship, or it won't fire — the gateway out of Kanto |
| **Seadra Challenge** ⚠️ | Beat **Cissy** (Mikan gym) with **Squirtle** | Carry the **un-evolved Squirtle** across the point of no return |
| **How Hungry?** ⚠️ | Catch the **Snorlax** on **Grapaberry Island** (stop it eating berries) | Orange Islands — catch it |

> **This is the complete 42** (pulled straight from RA's missable filter, 2026-06-14). 14+5+3+17+3 = 42.
>
> **NOT missable — stop worrying about these:** *Bye Bye Butterfree* (yellow-scarf release), *The Movie of
> the Century* (Lights-Camera-Quack-tion), *Set Off the Sprinklers* (Pewter Gym), *Make It Double* (Team
> Rocket in Viridian Forest), and gaining *the trust of Lapras* are all **non-`[m]`** — you can't permanently
> lose them. The old community guide's *"Haha A Baby"* and *"Stand up for Bulbasaur"* are **not** in the
> current 42 (likely renamed) — don't chase them.
>
> **Don't confuse this set with the separate hack "~Hack~ Pokémon: Orange Islands" (RA #14483)** — its
> achievements (I'm Really Thad, Fields of Victory, Master of Many, Wave Rider / Coral-Eye Badge, etc.) are
> **NOT** in Ash Gray.

---

## 5. TEAM PLANNING — Pokémon you must catch / not evolve (now tied to the real 42)

The authoritative missable list pins down *exactly* which Pokémon you must have ready, and which to keep
un-evolved. Build toward this:

- **Squirtle — keep it UN-EVOLVED** all the way into the Orange Islands. Two missables need the *species*
  Squirtle: **Skull Bashing Kevin** (League round 2) and **Seadra Challenge** (Cissy, OI Gym 1). Carry it
  un-evolved across the point of no return.
- **Charmander → Charizard — have Charizard by Cinnabar/League.** Needed for **Just Like in the Anime**
  (Blaine's top fight) and **Oh, We Lost…** (the Richie loss). Community timing: don't evolve until the
  North Pole cave event, and have it as Charizard by the Grampa Canyon excavation.
- **Pidgeotto → Pidgeot — have a Pidgeot in your party after the Championship** for **Where It All Began**
  (the Fearow sky battle). No Pidgeot, no sky battle.
- **Catch a Muk** (Power Plant) — that's **Sludge Monster**, *and* you need it for **Fourth Round Muk Day**
  (League round 4).
- **Have a Kingler** (evolve a Krabby) for **Easy League Start** (League round 1).
- **Keep Pikachu** central — **Elder vs. Child** (lose to Surge with Pikachu) and **Water and Electricity**
  (beat Pete with Pikachu) both need it.

> Correction vs the old community guide: **Bulbasaur evolution timing is NOT enforced by a missable** —
> "Stand up for Bulbasaur" isn't in the real 42, so you can evolve Bulbasaur whenever. (Holding evolutions
> until after an anime-significant Pokémon's signature event is still a safe habit, just not required here.)

---

## 6. Emergency anti-brick hatch (gray area — last resort only)

If a clean-ROM **crash/softlock won't clear with reset-retry** (the realistic risk is F4 excavation),
there is a recovery path that loses you *nothing* legitimately:

Because our fork and the clean ROM share an **identical save format**, the **same `.sav` file loads in
both**. So you can: copy your `.sav` → open it in **our fork** (which fixes that exact bug) → walk
through *only* the one broken event → save → copy the `.sav` back to the clean ROM and continue your
hardcore run.

**Honesty flag:** this earns **no achievement** on the fork — it only un-bricks you past a developer
bug. RA cannot detect it (a `.sav` is the game's own battery save, not a savestate, and no unlock
happens on the fork). But it *is* using a modified binary to pass an obstacle, which hardcore purists
would frown on. Use it **only** to rescue a run from an otherwise-unrecoverable softlock — never to
gain an advantage. If purity matters more to you than the run, the alternative is to abandon and
restart from your last good `.sav` backup.

---

## 7. Sources & confidence

- **Bugs, box discipline, crash avoidances:** our own reverse-engineering audit
  (`ISSUES.md`, `audit/d1-pss-reserve-scoping.md`, `audit/d1-gym-badge-blocks.md`). Many items
  (box-3 badge blocks, M1, F2–F6, L9, L13) were reproduced in-engine on the headless rig.
- **Missables, order, evolution timing:** RA community guide —
  [forum topic 2211](https://retroachievements.org/viewtopic.php?t=2211&c=160218) ·
  [RA game #5245](https://retroachievements.org/game/5245) ·
  [beta 4.5.3 walkthrough (Google Doc)](https://docs.google.com/document/d/e/2PACX-1vQDOjM985v0brdtgbUGdwdzj_qa53Nq8ZxdkqwG6OgEFswwN3lyctTJv_frllYfTDJd3Kn5W6GUKW3W/pub).
- **Honest gaps:** all 42 `[m]` missables are now enumerated (§4, straight from RA's filter). What's
  still soft: the RA-distributed build *may* have patched a subset of the §3 crashes; the exact in-game
  order of the late game (§8 stops 19–26) is anime-order + our audit, since the walkthrough cut off at
  Cinnabar; and "Shed a Tear" couldn't be pinned to a precise stop. None of these affect the
  box-discipline or point-of-no-return rules, which are the run-savers.

---

## 8. SEQUENTIAL PLAY-ORDER CHECKLIST — follow this top-to-bottom

Everything above, merged into one timeline. **Kanto (stops 1–18) is from the authoritative 4.5.3
walkthrough; the late game (19–26) is anime-order + our audit because the walkthrough cut off at
Cinnabar — confirm exact sequence in-game there.** Legend: 🎯 missable · 🎣 catch · 🧬 evolution timing ·
⚠️ crash/softlock · 💾 save · 🟥 box rule.

> 🟥 **Standing rule for the entire game:** never deposit a Pokémon in **BOX 2 / 3 / 6.** It's not repeated below — just never do it.

**1. Pallet Town** — get Pikachu from Oak.
- ⚠️ M1: don't press UP against the lab wall one tile *right* of the door (permanent softlock). Enter from directly below the door.

**2. Route 1 → Viridian City (Pokémon Center)**
- 💾 🎯 **Prepare for Trouble…** — beat Team Rocket in the Viridian PC.
- ⚠️ Don't let **Pikachu faint** in this (or any) Team Rocket fight — permanent disobedience.

**3. Route 2 / Viridian Forest**
- 💾 ⚠️ **F1:** save before the forest; if it black-screens, soft reset & refight (intermittent).
- 🎣 Catch **Pidgeotto** (→ your future Pidgeot). 🎯 **Give Me Back My Pokémon!** — get your Metapod back from the Beedrill.

**4. Pewter City — Brock.** Freebie (non-missable): **Set Off the Sprinklers**.

**5. Mt. Moon → Cerulean City — Misty**
- ⚠️ **L13:** don't step onto the tip of the diving board over the pool (one-step softlock). 💾 Save before the gym.

**6. Route 19 — AJ.** 🎯 **Unbeaten** — defeat AJ's undefeated mini-gym.

**7. Route 20 (Tech Institute) → Route 5**
- 🎣 Catch **Charmander** (the abandoned one) + **Bulbasaur**. 🧬 **Don't evolve Charmander yet** (Bulbasaur: anytime).

**8. Hidden Village.** ⚠️ **L5:** carry an **Escape Rope** (or Dig); avoid the off-color grass pits.

**9. Bill's Lighthouse → Vermilion City — Lt. Surge**
- 🎯 **Elder vs. Child** ⚠️ — **LOSE** to Surge 1-on-1 with **Pikachu** *first*, then win the gym.
- 🧬 Once you get **Squirtle** (Squirtle Squad, around here), **keep it un-evolved all game** *(exact pickup point varies)*.

**10. S.S. Anne.** 🎯 **Worth the $500** ⚠️ — **choose Magikarp** from the salesman. Grab **Cut** here.

**11. Pokémon Island → Porta Vista.** 🎯 **The Kraken** — defeat the giant Tentacruel.

**12. Maiden's Peak.** ⚠️ F7 (precaution): 💾 save before the ghost/lady scene.

**13. Route 7 → Saffron — Sabrina (lose) → Lavender/Pokémon Tower (Haunter) → Saffron rematch (win)**
- Freebie: **Bye Bye Butterfree** (Route 7 release).
- 🟥 Extra-critical here: a Box-3 deposit makes **Sabrina go inert → no Marsh Badge.**

**14. Route 7 (revisit).** 🎯 **No More Monkey Business** ⚠️ — **capture** the Primeape that stole your hat.

**15. Celadon — Erika → P1 Grand Prix (Route 13) → Gringey City (Power Plant)**
- 🎯 **Sludge Monster** ⚠️ — **capture the Muk.** 🎣 Keep it — League round 4 needs it.

**16. Diglett's Tunnel → Route 9 — Koga → Fuchsia → Safari Zone**
- 🎯 **Wrong Meowth** ⚠️ — catch the **grass** Meowth for Tommy (*not* the one by the house).
- 🎣 Get a **Krabby → Kingler** around here (League round 1 needs Kingler).

**17. Route 11 → Sunny Town → North Pole**
- 🎯 **Santa Is Real** (meet Santa) · 🎯 **Cold Together** (bring a party-mate into a Snow Island cave).
- 🧬 **Charmander evolution window opens** (North Pole cave) — start evolving toward Charizard.

**18. Route 12 cluster — Pikachu reunion → Eevee Bros → Snorlax dam → Dark City → Grampa Canyon**
- 🎯 **An Absolute Unit** ⚠️ — **capture Snorlax** (end the drought).
- ⚠️ **F4 (Grampa Canyon):** 💾 save right before the pickaxe handoff; if you freeze after, soft reset & retry (§6 hatch if truly stuck).
- 🧬 **Have Charizard by the end of this cluster** (needed at Cinnabar & the League).

> ⛏️ *Walkthrough cuts off here. Stops 19–26 are anime-order + audit — order may shuffle; confirm in-game.*

**19. Pokémon League exam (The Ultimate Test).** 🎯 **Pokémon Whiz Kid** ⚠️ — **perfect score.** 💾 Save before; reported flaky — verify the pop; no retake.

**20. Secret of the Breeding Centre.** ⚠️ **F3:** **keep a party slot open (≤5)** before talking to Jessie & James / Butch & Cassidy (full party = crash that blocks Cinnabar).

**21. Cinnabar Island — Blaine** (order-sensitive). 💾 Save before each:
- 🎯 **Just Like in the Game** (Blaine in the volcano) · 🎯 **Freezer Bomb** (Team Rocket in the volcano) · 🎯 **Just Like in the Anime** ⚠️ (Blaine **on top** with **Charizard** — you must **lose once** to open the top fight).

**22. Viridian Gym — Giovanni / Earth Badge / Mewtwo intro.**

**23. Mewtwo's New Island — "Pokémon Palace"** *(placement uncertain — may fall around/after the League)*
- ⚠️ **L9:** **ACCEPT Dragonite's invitation** (declining = unwinnable). ⚠️ **F2:** take the normal raft crossing; 💾 save before.
- 🎯 5 one-time battles: **Water Battle** (Fergus) · **Not The Right Mix** (Corey) · **Not-So-Normal Type** (Neesha) · **Giant Onix** (help Bruno) · **Become a Pokéhuman** (giant Pokéball).

**24. League day — Prof. Oak → Indigo gate**
- ⚠️ **L2:** **keep a party slot open** so Oak can return your watched Pokémon (else the send-off won't fire).
- ⚠️ **L1:** make sure the **league-start event** (phone/Oak scene) happened, or the gate guard blocks you despite badges.
- 🧬 Confirm a **Pidgeot** is in your party for after the Championship.

**25. Indigo League — bring Kingler · un-evolved Squirtle · Pikachu · Muk · Charizard**
- R1 Mandi → **First Taste Of Success** + **Easy League Start** (Kingler)
- R2 Kevin → **Acting Like He Won the Competition** + **Skull Bashing Kevin** (Squirtle)
- R3 Pete → **Ice Field Triumph** + **Water and Electricity** (Pikachu)
- R4 Jeanette → **Beltastic** + **Fourth Round Muk Day** (Muk)
- ⚠️ **R5 Richie — 💾 BACK UP YOUR SAVE FIRST.** **We Really Won?** (win) and **Oh, We Lost…** (lose with **Charizard last**) are mutually exclusive: lose on the backup, restore, win on the main file.
- Melissa → **Beat the One Who Beat Gary** · Gideon → **You Are the Champion!**
- E4: Lorelei **Ice-Cold Master** · Bruno **Solid-Ground Fighter** · Agatha **Spirit-Tamed Elder** · Lance **Dragon-Fierce Warrior** · Slate **You Were Ready!**

**26. Post-Championship (Pallet Party Panic)**
- 🎯 **Where It All Began** ⚠️ — defeat **Fearow** in the **sky battle** (needs **Pidgeot**). This is the door out of Kanto.
- 🛑 **STOP — confirm every Kanto missable above is done. There is NO way back.**

**→ Orange Islands** (the finish line of what exists)
- 🎯 **Seadra Challenge** ⚠️ — beat **Cissy** (Mikan) with your un-evolved **Squirtle**.
- 🎯 **How Hungry?** ⚠️ — catch the **Snorlax** on **Grapaberry Island**.
- ⚠️ F6 (Tangelo Pokémon Park) & F7 (OI lady scenes): 💾 save before. Content ends ~Gym 3 (Rudy); no Gym 4 / Drake finale exists.

> ⚠️ **One missable I couldn't pin to a stop:** **Shed a Tear** — in an **abandoned/deserted Pokémon
> house**, look at **all 4** Pokémon **without adopting any** and without leaving early. It falls somewhere
> mid-Kanto; watch for the house.
