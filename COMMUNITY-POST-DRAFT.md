# Community post — DRAFT (reply inside the existing Ash Gray thread, PokéCommunity)

> A single reply for the existing Ash Gray thread. NOT a fork announcement, no fork teaser —
> framed as a personal fork made to play, with the Bad Egg finding shared as the byproduct.
> Names Claude plainly. Deliberately does NOT claim to be the first to find this.

---

**I've been using Claude (the AI) to build a personal bug-fix fork of Ash Gray — honestly just to clean it up enough to finally play through it myself — and in the process it turned up what I'm fairly sure is the actual cause of the "Bad Eggs," plus exactly which PC Boxes to avoid to never get hit.**

Stating the AI part plainly up front, because it matters to people: this was Claude driving a headless emulator (libmgba), reproducing and testing against an unmodified Ash Gray ROM. But none of the conclusion rests on trusting Claude or me — the Bad Egg mechanism reproduces in any emulator and the whole analysis is checkable. If you'd rather verify it than take my word, please do; that's the point.

(All credit to metapod23 for the hack — still one of my favorites, which is why I wanted to actually finish it.)

**TL;DR — if you read nothing else:** the Bad Eggs (and probably a lot of the "my save randomly corrupted / backtracking broke my game" reports) come from the game's story progress physically overlapping your PC storage. Practical takeaway:

**Don't keep Pokémon you care about in Box 3 or Box 6, and don't completely fill Box 2. Boxes 1, 4, 5, and 7–14 are safe.**

That's the whole practical bit. The rest is the why.

**The mechanism:** FireRed stores story flags in a fixed array of 256 "variables," and `VarSet`/`VarGet` never bounds-check the ID. Ash Gray's story needs far more than 256, so it uses variable IDs well past the end of that array. Those writes overflow past the end of SaveBlock1 and land *physically inside the PC storage buffer* (`gPokemonStorage`, which sits right after SaveBlock1 in EWRAM). The same bytes end up doing two jobs:

- Story advances → it writes one of those variables → it overwrites part of a Pokémon sitting in the overlapping box → that Pokémon fails its checksum → **Bad Egg.**
- You deposit a Pokémon into one of those boxes → its data overwrites a story variable → **corrupted progression.** (Almost certainly behind a chunk of the "backtracking/long play breaks my save" reports — same flaw, opposite direction.)

It's probabilistic, which is why it feels random: a story flag writing into an *empty* slot is harmless; the damage happens once you've actually stored Pokémon in the overlapping boxes — usually later, in the middle boxes, after a lot of play. Exactly the pattern people describe.

**How I confirmed it:** in the emulator I set a specific story variable and watched its bytes land inside a Pokémon's data in **Box 3** — right in the checksummed region. Then I mapped every story variable the game both sets and checks to the exact box slot it overflows into. The map points at **Box 3** as the main hot spot — the box people have always reported. The save-file reports and the raw memory math independently land on the same box, which is what makes me confident it's right. There's a second cluster that maps to **Box 6** (don't think that one was ever reported), plus the tail of **Box 2.**

**Honest caveats:**

- **Cheats are a separate source.** GameShark/all-badges codes can make Bad Eggs anywhere; this explains the *non-cheat* ones — and likely a lot of the "it just corrupted on its own" cases.
- **This is a diagnosis + workaround, not a fix.** A real fix means relocating the game's whole variable system and changing the save format — effectively a from-scratch rebuild — which is why it could never just be byte-patched away.
- I'm not claiming nobody ever knew this. I couldn't find it documented anywhere, so it seemed worth putting somewhere public, right or wrong.

Happy to share the full technical detail — exact variable IDs, the complete variable→box map, and the emulator repro steps — with anyone who wants to verify it for themselves.
