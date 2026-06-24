# Community bug reports — paste-in file

Paste raw text from the sources below into the marked blocks (don't worry about
formatting — dumps, partial quotes, screenshots-transcribed, all fine). I'll triage
every line, match reports against the bugs already fixed/closed in `ISSUES.md`, and
investigate anything new with the headless rig.

**What makes a report most useful (any subset helps):**
- The hack **version** the reporter played (4.5.3? 4.2? 3.x?) — many old reports are already fixed upstream
- **Where** it happens (town/route/building) and what the player just did
- The **exact dialogue or message text** on screen (lets me grep the ROM directly)
- Whether it's a crash / black screen / stuck-can't-move / wrong behavior

---

## Highest-value targets (in order)

1. **PokéCommunity dev thread #180722 — the FIRST post (OP) only**
   <https://www.pokecommunity.com/threads/180722/>
   metapod23's own changelog + "Known Bugs" list. One page.

2. **The community "Bugs & Glitches guide"** (graded 🔴/🟡/🟢) — referenced in search
   results but never directly linked; likely a PokéCommunity or GameFAQs post.
   If you ever stumble on it, it's the jackpot.

3. **Fandom wiki — any "Bugs" / "Glitches" / "Trivia" section**
   <https://pokemon-fan-game.fandom.com/wiki/Pok%C3%A9mon_Ash_Gray> (or similar page)

4. Anything else: Reddit threads, GameFAQs, YouTube comments with specific repros —
   paste freely below.

---

## PASTE AREA 1 — PokéCommunity thread 180722 OP
Source URL (fill in if different):
 Red = Critical - game-crashing glitch
Yellow = Medium - may affect gameplay
Green = Odd bug, but doesn't harm gameplay in the least
Strikethrough = Bug fixed :)

- Running Shoes don't work in Pallet Town or Route 1?
- Ash stays on Misty's bike after Pikachu thundershocks the Spearow
- Bad Eggs appearing in your Storage Boxes (DO NOT move them)
- The Pokédex thinks Onix is part of the Diglett/Dugtrio family :/ - Not a bug - FireRed's Pokedex is just weird
- Can't get on/off the bike in certain outdoor areas
- Teachy TV is broken - DON'T USE IT
- Rival's face turns red if you try to name him
- Message for computer in player's room stays opened
- Message for Prof. Oak evaluating Pokédex stays opened
- Ashley backsprite is sometimes discolored and HP bar may be discolored during battles as Ashley
- Pallet Town berry system doesn't work quite right yet
- Slight hitch in Pallet Town Windmill

- Quite a few more, I'm sure
```
(paste here)
```

## PASTE AREA 2 — Bugs & Glitches guide
Source URL:
https://www.scribd.com/document/988520391/AshGray-Guide
this is the closest I could get
```
(paste here)
```

## PASTE AREA 3 — Fandom wiki bugs/trivia
Source URL:

```
(paste here)
Story

Pokémon Ash Gray follows the events of Season 1 of the Pokémon Anime.
Patching guide

Patch v4.5.3 onto a clean Pokémon FireRed using ROM Patcher JS.
Trivia

    Despite following the anime, the player can catch Pokémon that Ash never caught, like the Spearow that attacked Ash and Pikachu in the first episode
        It's also not necessary to release your Butterfree like Ash did in the anime (and the movie)
    For unknown reasons, bad eggs can appear in the storage boxes.
        Another glitch happens when switching Pokémon during the first battle with Jessie and James, your other Pokémon becomes invisible. This may be due to the fact that in the anime, Pikachu was Ash's only Pokémon at the time
    The game features content from banned episodes of the anime such as Beauty and the Beach, the Legend of Dratini (which were banned in America), and Electric Soldier Porygon
    The side story "Holiday Hi-Jynx" is available after the Porygon mission. as it was supposed to be in the original run of the Pokémon anime


no bugs section
```

## PASTE AREA 4 — anything else (Reddit / GameFAQs / YouTube / Discord)
Source URLs:

```
(paste here)

Bugs/Glitches

    *** Bad Eggs appear in your Storage Boxes. DO NOT MOVE THEM!
    *** Teachy TV is broken. DO NOT USE IT!
    Can’t get on/off the bike in certain areas
    Ashley’s backsprite/HP bar is sometimes discolored
    Pallet Town berry system doesn’t work right
    Slight hitch in Pallet Town Windmill
    During the first battle against Jessie and James, switching Pokémon can make your active Pokémon appear invisible
Some players report save errors depending on emulator/save-type settings
"Something I noticed: if Pikachu faints against Team Rocket it will no longer obey you. Let's assume this bug cannot be fixed so make sure you have some savestates at hand."
this guy posted he has a patched version - "
Hey everyone, I finished the game and revamped but also translated it in french. If I have the permission of the pokecommunity moderation, I could share the patch (I tried to contact metapod23 but sadly I think he definitely disappeared). Then if I can share my actual french patch, I would probably make an english and spanish version for all the Pokémon Ash Gray fans! You'll finally be able to finish the adventure!
 
 I patched several bugs like the beginning when lose against spearows and stuck on wall, or stuck on cerulean city gym pool etc... I think my actual version really worth sharing, and if it's not here it can be shared in a brand new thread, but I'm waiting for permission from the moderation team (on Discord I still haven't had a response for this specific request). Thanks in advance.
 
 Sadly bad eggs can't be patched and they appears since the beginning of the adventure, more precisely after the team rocket first battle on Viridian Pokémon Center. I just added a message of Nurse Joy after the battle telling to Ash to not manipulate it because it can cause save corruption and it's because of Team Rocket technology! Recreate ash gray from vanilla would be too much work! I patched the maximum of bugs I could. Especially the ones which stucks the adventure."
 

    Confirmed Bugs / Glitches
Bug	Description	Status
Bad Eggs in PC Boxes	Random Bad Eggs can appear in storage boxes. Players are generally advised not to interact with them.	Confirmed
Invisible Pokémon in Jessie & James Battle
Switching Pokémon during the first Jessie & James battle can make the active Pokémon invisible.
Confirmed
Save Error / Cannot Save
Some players report "Save error, cannot save" depending on emulator settings or save type.
Reported
Saffron City Access Glitch
Players reported becoming unable to enter Saffron City in Beta 3.61.
Reported
Teachy TV Bug
Teachy TV reportedly does not function correctly.
Reported by community documentation
Bicycle Lock Bug
Getting on/off the bike can fail in certain locations.
Community-reported
Ashley Sprite Color Bug
Ashley's backsprite or HP display can show incorrect colors.
Community-reported
Pallet Town Berry Bug
Berry system in Pallet Town may not function properly.
Community-reported
Pallet Town Windmill Graphics Bug
Minor graphical issues around the windmill.
Community-reported
    
    Likely Lost Reports

The original PokéCommunity development thread reportedly contained hundreds of pages of bug reports, but much of that information is difficult to access today. Many reports involved:

Orange Islands progression locks
Event flags not triggering
NPCs disappearing
Script softlocks
Emulator-specific crashes
Save corruption from incorrect save types
    
Confirmed Developer-Acknowledged Bugs

These were either listed by the developers or later fixed in patch notes.

Bug	Version
Bad Eggs appearing in PC storage boxes	All known versions
Teachy TV crashes/breaks the game	All known versions
Can't get on/off bike in certain areas	Reported in 4.x
Ashley backsprite/HP bar discoloration	Reported in 4.x
Pallet Town berry system malfunction	Reported in 4.x
Pallet Town windmill graphical hitch	Reported in 4.x
Agatha event bug	Fixed in 4.5.2
Snorlax tree-cutting event bug	Fixed in 4.5.2
Krabby not appearing	Fixed in 4.51
North Pole progression bugs	Fixed in 4.51
"Make Room For Gloom" event activation bug	Fixed in 4.5.3
Script / Progression Bugs

These are the most serious bugs because they can softlock a save.

Charmander Event Not Triggering

Multiple players reported the abandoned Charmander episode failing to activate, preventing progression.

Squirtle Squad Event Not Triggering

Several reports mention the Squirtle Squad storyline not firing when it should.

Misty Progress Reset

Backtracking can reportedly make the game believe Misty was never defeated, preventing the player from leaving Cerulean City.

Zubat Event Re-triggering

A Zubat cutscene near Mt. Moon can repeatedly attempt to trigger even when the NPC is gone, trapping progress.

Teleport Marker Reset Bug

Some teleport destinations stop working after story flags reset.

Pallet Town Progress Checker Bug

One report describes being blocked from leaving Pallet Town due to corrupted story progression checks.

Saffron City Entry Bug

Older beta users reported becoming unable to enter Saffron City.

Event Trigger Bugs

These occur when anime-style scripted events fire incorrectly.

Route 1 Spearow Loop

One player reported continuously being forced into the opening Spearow attack sequence every time they entered Route 1.

Metapod Replacement Bug

A Pokémon in the party was reportedly replaced by Metapod when a Metapod event triggered.

Brock Challenge Check Failure

Players have reported Brock refusing battles even with sufficiently leveled Pokémon.

Progress Flags Breaking After Backtracking

Community consensus is that excessive backtracking can corrupt event flags and story progression.

Battle-Related Bugs
Jessie & James Invisible Pokémon Bug

Switching Pokémon during the first Team Rocket battle can cause the active Pokémon sprite to disappear.

Ashley Battle Graphics Bug

HP bar and battle sprites occasionally use incorrect palettes.

Storage / Save Corruption Bugs
Bad Eggs

The most infamous Ash Gray bug.

Symptoms:

Bad Eggs appear in storage boxes.
Moving them can crash the game.
Some users reported multiplication of Bad Eggs.
Save corruption may follow interaction.
Save Error Bug

Some emulators produce:

Save error. Please exchange the backup memory.

Usually caused by incorrect save type configuration.

Emulator-Specific Bugs
Black Screen on Startup

Reported by Delta, VBA, and mobile emulator users when:

ROM was improperly patched.
Save type was wrong.
Unsupported emulator settings were used.
Sound Issues

Some users reported audio glitches despite the game otherwise functioning normally.

Community-Wide Warning

The strongest pattern I found wasn't one specific bug—it was a repeated warning from long-time players:

Ash Gray does not handle backtracking well.

Numerous progression locks, event resets, and story-flag corruption issues appear tied to revisiting old areas or doing things in an order the anime storyline did not expect.

Reconstructed "Most Likely Complete" Bug Count

From all surviving sources, I could verify approximately:

6 graphical bugs
3 save/storage bugs
2 battle bugs
8–10 event trigger bugs
5–7 progression softlocks
2 emulator compatibility bugs

for roughly 26–30 distinct reported issues across the lifespan of Ash Gray.    
    
    I went deeper and found a few more reports from archived discussions, Reddit, and old forum posts. What follows is the closest thing to a reconstructed Ash Gray bug tracker that currently exists publicly.

Tier 1: Confirmed Reproducible Bugs

These were reported multiple times or acknowledged through fixes.

Bad Egg Generation
Bad Eggs appear in Box 3 or other PC boxes.
Some players report invisible Bad Eggs.
Moving or interacting with them can cause instability.
Reports span multiple versions including 4.5.3.
Jessie & James Invisible Pokémon
Switching Pokémon during the first Team Rocket battle can make the active Pokémon sprite disappear.
Teachy TV Bug
Teachy TV functionality is broken and can cause issues.
Long-standing known issue.
Bike State Bug
Mounting/dismounting the bike can fail in certain maps.
Player becomes stuck in incorrect movement state.
Save Type Error
"Save Error. Please exchange the backup memory."
Caused by incorrect emulator Flash settings.
Extremely common on VBA and mobile emulators.
Tier 2: Story Progression Softlocks

These are the most dangerous because they can permanently block completion.

Charmander Event Never Starts
Story flag sometimes fails.
Prevents progression into later anime events.
Squirtle Squad Event Failure
Trigger sometimes never activates.
Reported on fresh saves as well.
Misty Flag Reset
Returning to Cerulean can cause the game to think Misty was never beaten.
Player cannot leave town afterward.
Zubat Entrance Event Loop
Mt. Moon entrance repeatedly attempts to run a cutscene.
NPC responsible for event is missing.
Player becomes trapped.
Teleport Marker Corruption
Warp destinations reset unexpectedly.
Fast-travel locations disappear.
Pallet Town Progress Checker Lock
Story checker incorrectly blocks movement.
Report mentions being unable to leave Pallet Town.
Saffron City Entry Bug
Known Beta 3.61 issue.
Gate scripts fail and prevent entry.
Team Rocket Before Ritchie Battle
At least one player reports a battle glitch that prevented progression.
Lavender Town Gym Access Bug
Player lost repeatedly and afterward the gym entrance stopped functioning.
Tier 3: Event-Specific Softlocks

These appear tied to specific anime episodes.

Tentacruel Battle Lock
Player trapped in a battle they could not win.
Could not retreat or continue.
Multiple reports years apart.
Butterfree Release Event Lock
Butterfree departure sequence can stall progression.
Multiple users independently reported getting stuck there.
Squirtle Super Potion Sequence
Using Teleport during this event can permanently break progression.
Snorlax Tree-Cutting Event
Officially fixed in 4.5.2.
Previously capable of blocking progress.
Agatha Event
Fixed in 4.5.2.
North Pole Event Chain
Multiple bugs fixed in 4.51.
Make Room For Gloom
Event activation bug fixed in 4.5.3.
Tier 4: Graphics & Visual Bugs
Ashley Palette Bug
Wrong sprite colors.
HP bar palette corruption.
Windmill Graphics Error
Visual artifact near Pallet Town windmill.
Invisible Battle Sprites
Usually associated with Team Rocket battle scripts.
Missing NPC During Triggered Event
Seen with the Zubat event.
Script still activates despite absent NPC.
Tier 5: Progress Flag Corruption

This appears to be Ash Gray's underlying problem.

Players repeatedly describe:

Story flags resetting
Story flags never activating
Previously completed events becoming incomplete
Anime episodes occurring out of order
NPCs believing events never happened
Returning to old maps causing corruption

One experienced player summarized it by saying:

the game does NOT like backtracking

and described multiple independent progression resets across a full playthrough.

Bugs Officially Fixed by Version
Beta 4.2
General bug fixes (not individually documented).
Beta 4.51
North Pole bugs
Krabby not appearing
Other undocumented glitches
Beta 4.5.2
Agatha bug
Snorlax tree-cutting bug
Beta 4.5.3
Make Room For Gloom activation bug
My estimate after digging

I can verify 34 distinct bug reports/issues with sources.

Of those:

~12 are progression blockers
~8 are event-script failures
~4 are save/Bad Egg related
~4 are graphics issues
~6 are fixed historical bugs

The missing piece is the original PokéCommunity thread. If somebody were to manually scrape the archived thread pages, I would expect the total historical bug count to be closer to 60–100 reported issues, because many one-off reports from 2010–2015 are no longer indexed by search engines. The biggest cluster of reports appears to have been event flags and softlocks rather than graphical glitches.
    
```

---

## Already handled — no need to re-report these
Quick reference so you can skip known items while skimming threads
(full detail in `ISSUES.md`):

- **Fixed & verified:** Indigo gate "league hasn't begun" (L1) · Oak full-party stall (L2)
  · running shoes dead in Pallet (+43 more maps) (L4) · Hidden Village trap warps (L5)
  · decline-Dragonite soft-lock / "raft gone" (L9) · underwater-cave black screen (F2)
  · breeding-center crash (F3) · Grampa Canyon pickaxe softlock (F4) · Tangelo Park
  void/crash (F6) · "the the" / "sacrfices" / "recieved" ×2 / "INIDGO" typos (T1-T3)
- **Reproduced, engine-level (documented, not yet fixable by byte-patch):** early-forest
  scripted-battle freeze — the "Pidgeotto fight freeze" (F1)
- **Verified not-bugs:** Onix Rock/Ground typing (D6) · "RAFTT" item name (T4) · badge
  flags audit found all 8 correct (L6) · stuck-on-Misty's-bike natural path is clean (L3)
- **By design (anime-accurate, not bugs):** HMs replaced by key items · Brock scripted
  loss · Pikachu refuses vs Misty · Charizard disobedience · trade evolutions adapted ·
  the hack simply *ends* mid-Orange-Islands (unfinished content, not a freeze)
