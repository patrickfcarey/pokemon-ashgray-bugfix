# Ash Gray (beta 4.5.3) — known bugs (community-reported) + fixability

Sources: [PokéCommunity dev thread 180722](https://www.pokecommunity.com/threads/pok%C3%A9mon-ashgray-version-beta-4-5-released.180722/),
[PC "b4.5.3 freezed" 436579](https://www.pokecommunity.com/threads/pokemon-ash-gray-b4-5-3-freezed.436579/),
[PC "4.3.5 bug" 444362](https://www.pokecommunity.com/threads/anyone-experience-this-bug-on-ash-grey-4-3-5.444362/),
[Vizzed 71285](https://www.vizzed.com/boards/thread.php?id=71285), Fandom wiki.

`fixable here` = byte/script/data edit + regenerate patch (no Windows tools).

## Freezes / crashes
| # | Bug | Class | Fixable here? |
|---|-----|-------|---------------|
| F1 | Freeze when Pikachu takes first hit in the **Pidgeotto** fight (camera scrolls too high) | script/camera | ✅ likely (script or map border) |
| F2 | **Black-screen freeze in the underwater cave** after Dragonite's tournament message | script | ✅ likely (bad ptr/special/missing waitstate) |
| F3 | **Crash talking to Team Rocket at the breeding center** | script | ✅ likely |
| F4 | **Crash/softlock getting the pickaxe** from the scientist (islands, after Grampa Canyon) | script | ✅ likely |
| F5 | Catch a **Spearow early** and use it vs Team Rocket → heavy glitching | script/flag | ✅ likely |

## Progression / logic
| # | Bug | Class | Fixable here? |
|---|-----|-------|---------------|
| L1 | **Indigo Plateau guard** says league hasn't started despite all badges + exam | flag check | ✅ yes (correct the checkflag/setflag) |
| L2 | **Full party + talk to Prof Oak** → can't receive Pokémon → blocks next event | give logic | ✅ yes (party check / msg) |
| L3 | **Ash stays on Misty's bike** after Pikachu thundershocks the Spearow | state flag | ✅ yes (clear bike state) |
| L4 | **Running shoes don't work** in Pallet Town / Route 1 | map attr / flag | ⚠️ map-attribute edit (doable) |
| L5 | **Hidden Village** wrong mapping / traps with no exit | map data | ⚠️ map/warp edit (doable, more work) |

## Inventory / storage / battle
| # | Bug | Class | Fixable here? |
|---|-----|-------|---------------|
| D1 | **Bad Eggs** appear in storage boxes | data/give | ✅ likely (bad give-species/flag) |
| D2 | Deposit Squirtle for the Eevee event → **Squirtle disappears** | storage event | ⚠️ needs script trace |
| D3 | Switch Pokémon in **first Jessie & James battle** → other mons invisible | battle/script | ⚠️ harder (battle engine) |
| D4 | **Teachy TV** broken | item/data | ✅ likely |

## Cosmetic
| # | Bug | Class | Fixable here? |
|---|-----|-------|---------------|
| C1 | Ash's **girl-disguise battle sprite** mis-colored (shirt blue, hair white) | graphics | ❌ needs human art |

## Text (from our scan, `audit/04`)
- `0x834CBF` **"playing out in the the streets"** — duplicated "the" (clear typo, safe in-place fix).
- Plus a handful of `space-before-punct` / `dup-word` candidates to confirm by hand.

**Best first targets** (high-confidence, headless): L1, L2, L3, the `the the` typo — then the freezes F2–F4 once the decompiler reads their scripts.
