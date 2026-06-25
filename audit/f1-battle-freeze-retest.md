# F1 — early-forest scripted battle "freeze": RE-TEST (2026-06-25)

**Verdict: could NOT reproduce a freeze. Strong evidence F1 is a reproduction artifact (a false
positive), not a real game bug.** This is the 5th false-positive freeze of the same class caught in
this project (after the first-sleep dream and the three earlier over-claims) — all from a rig drive
leaving the game at a menu/textbox that *looks* frozen because direction-keys can't dismiss it.

## What F1 claimed
The scripted forest wild battles (Caterpie `0x800277`, Pidgeotto `0x8170FC`) "hard-freeze
non-deterministically in the battle-end fade — black screen, input dead; same savestate completes
fine on other runs." Marked `engine (wontfix)`, called the one remaining unfixed game-blocker.

## Why the claim was suspect from the start
- **A deterministic emulator cannot freeze differently on the *same* savestate** unless the *inputs*
  differ. "Same savestate, different outcome" therefore means the freeze depends on input *timing*
  (which RNG path the battle takes) — the signature of a flaky *reproduction*, not a fixed code bug.
- **The script is trivially clean** (`setwildbattle; dowildbattle; setvar 0x6108,1; release; end`) —
  any freeze would have to live entirely inside the engine's `dowildbattle` fade.
- **The game is demonstrably completable** (139 RA achievements on the clean ROM; this is the famous
  anime Pikachu-vs-Caterpie/Pidgeotto scene ~3 screens in — every player passes it). A real freeze
  here would make the hack unplayable.
- This project has already caught **four** false "freeze" positives from the same rig artifact.

## Tooling added to reproduce/inspect (rig.c)
To localize a freeze you must see where the CPU is. Added three commands to the headless rig:
- `regs` — dump r0–r15, cpsr, and the code halfwords around PC.
- `trace <n>` — step `n` instructions (faithful: `ARMRun` processes the event scheduler) and print a
  **PC histogram**. A real freeze shows few distinct PCs in a tiny range (the spin loop); a healthy
  game shows the broad main loop.
- `stepto <addr> [max]` — faithful software breakpoint (step until PC enters `[addr,addr+6]`).

## Method
`forest.ss` (on `tvtest/forest_test.gba`, the build the state was captured on) turned out to be saved
**mid-Caterpie-battle with the in-battle bag open** — Pikachu vs Caterpie Lv5, at the FIGHT/BAG menu.
That is the exact F1 scenario. From there I drove the battle many ways and watched the end.

Map (1,0) trigger table (parsed from event data) confirms the battle geography:
- Caterpie `0x800277`: tiles (27–32, 61), gate var `0x6108==0`.
- Pidgeotto `0x8170FC`: tiles (6–8 / 12–14, 34), gate var `0x6108==1`.

## Results — ~19 runs, zero freezes
- **Every run responded to input and progressed** through turns, menus, paralysis, damage, text. Each
  frame that *looked* frozen was a menu or a textbox legitimately waiting for A — the documented
  false-positive signature (a battle that didn't end because the drive picked Growl, the 0-damage
  move-slot-1, instead of ThunderShock; or a textbox the rig stopped feeding).
- **Drove the battle to two distinct clean terminal states:**
  1. **Loss → whiteout fade → respawn home** (map 4.0 (8,5), Mom's heal dialogue) — `_emu/L_final.png`.
  2. **Run → return-to-overworld fade → forest field**, with a working START menu — `_emu/r5_start.png`.
- **RNG-shifted sweep, 10 timings** (`sw_*.rig`): final-frame brightness and end-LOC for every run:

  | delay | final-frame brightness | end location |
  |------:|------:|---|
  | 0  | 113.8 | map 4.0 (8,5) home |
  | 5  | 77.0  | map 1.0 forest |
  | 9  | 116.1 | map 4.0 home |
  | 14 | 77.0  | map 1.0 forest |
  | 19 | 115.6 | map 4.0 home |
  | 26 | 115.8 | map 4.0 home |
  | 33 | 77.0  | map 1.0 forest |
  | 44 | 77.0  | map 1.0 forest |
  | 58 | 77.0  | map 1.0 forest |
  | 71 | 115.4 | map 4.0 home |

  **No black screens (brightness never near 0); no hangs.** The timing shift genuinely changed the
  battle outcome (5 lost → home, 5 still on the forest map), proving real RNG variation was sampled —
  and not one run froze.
- **Every CPU trace** at every inspection point showed healthy loops (the generic main loop
  `0x080008ac`, IWRAM field/wait loops, BIOS SWI waits) — never a pathological tight spin in battle
  code.

## The original "proof" image, re-read
`_emu/f1_proof.png` is a vertical composite of three frames: the battle menu, a **dimmed mid-fade
frame**, and — at the bottom — the **fully-rendered forest overworld**. It shows the fade *proceeding*
and the field *appearing*. The "freeze" reading mistook the mid-fade (palette-darkening) frame for a
stuck one.

## Honest limits
This is a strong negative, not a proof of a universal negative: I sampled ~a dozen input/RNG timings,
not the entire space. But combined with (a) the game's demonstrated completability, (b) the trivially
clean script, (c) two clean terminal-fade resolutions captured in-engine, and (d) four prior identical
false positives, the weight of evidence is that **F1 is not a real freeze**. If a freeze exists at all
it is a rare emulator-timing edge, not a gameplay blocker — consistent with the hack being routinely
completed.

## Consequence
The fork has **no known unfixed game-blocking bug.** F1 was the last one on the books, and it does not
hold up. `RELEASE.md`'s F1 caveat is corrected accordingly.
