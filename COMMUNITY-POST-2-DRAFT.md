# Community post 2 — DRAFT (follow-up reply, PokéCommunity Ash Gray thread)

> Companion to the Bad Egg post. Same personal-Claude-fork framing, diagnosis-focused, no fork
> release / no "ask me for it" pitch. These are the 5 genuine run-enders out of the ~16 bugs
> tracked down. Swap any from the back-pocket list if you'd rather feature different ones.

---

**Following up on the Bad Egg post — while I was in there, the same setup (Claude + a headless emulator, all reproducible) tracked down the actual *causes* of a handful of other long-standing bugs, and I fixed them in my personal build. Here are the 5 most critical — the ones that can genuinely end a run, not just annoy you.**

**1. The Pallet Town softlock, basically at the start.** There's a tile right next to Oak's lab door that's mis-stamped with a "ledge jump." Walk up into it from below and the game hops you east into a one-tile pocket that's walled on all four sides — no warp, no exit, nothing. A permanent softlock about *two screens into the game*. The fix is one tile: block the landing so the jump can't fire.

**2. Declining Dragonite's invite makes the game unwinnable.** When Dragonite offers to take you to Mewtwo's island, the *decline* branch and the *accept* branch both set the same "scene's done" flag — and the pier re-offer is gated on that flag. So if you say no, you never get the ticket, the storm never clears, you can't reach the island, and the offer can never come back. Dead save. The fix re-gates the re-offer on "no ticket yet" so declining just re-prompts you later.

**3. The Cerulean gym pool trap.** (This one's been reported before — "stuck on the Cerulean gym pool.") The tip of the diving-platform walkway is a pool-edge tile placed at *water* height at the end of a normal-height walkway. The edge behavior lets you step onto it, but the height mismatch then blocks every direction including he way back. One step = permanent softlock in a one-room gym. Fixed by replacing that one tile with a proper walkway tile.

**4. The Indigo Plateau gate won't let you in with all 8 badges.** You finish the whole game, pass the entrance exam, show up with every badge — and the guard still insists the league hasn't started. It's a logic error in the guard's eligibility check; the conditions it tests never line up with "ready," so the endgame is walled off after 30+ hours of play. Fixed in the guard's script.

**5. The Tangelo Island arrival crash.** Right as you reach the Orange Islands, going through the back of one of the buildings hard-crashes the game — the doorway warps to an invalid destination (plus a related broken trigger on the same map). Since Tangelo is the gateway to the entire second half, a crash there is a wall. Fixed by pointing the warp at the correct map and repairing the trigger.

All five reproduce on a clean ROM, and I'm happy to go into the exact tiles/scripts/offsets on any of them for anyone who wants to verify or dig in.
