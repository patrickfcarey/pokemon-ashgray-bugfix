# Open investigations — handoff for the next agent

The Ash Gray bug-fix fork has **no known remaining game-blocking bug** (all 🔴/🟠 crashes & softlocks are fixed and A/B-verified — see `ISSUES.md`). What's left is a short tail of items that are **open** or stuck at **needs-repro**: mostly community reports we could not *reproduce statically*. This doc is a scoped starting point for a fresh agent to try to crack them.

## Orientation (read first)
- **`ISSUES.md`** is the live tracker (master list + per-issue detail + session logs). Every claim there is backed by an in-engine test or a byte-level trace.
- **`audit/`** holds the deep dives referenced below.
- **`tools/emu/`** is the headless libmgba rig (`bash _emu/rig.sh <rom> <script.rig> [preload.ss]`). It can `load`/`save` savestates, `poke8/16/32` & `peek16/32` RAM, step `frames`, `shot` (screenshot), `tap`/`key`/`mash` input, `call <addr>` a routine, and `warpto`. It also has CPU introspection (`regs`, `trace <n>`, `stepto <addr>`) — a real freeze shows a tiny PC range; a menu waiting for input does not.
- **Branch:** do all work on **`1.1`** (the active dev branch; `main` is the frozen v1.0 release). Verify `git branch --show-current` is `1.1`.

## The key insight
These items are unresolved not because they were dismissed, but because reproducing them needs a **specific game state** that early-game savestates + static analysis can't reach. The rig can **construct** that state — set the story vars/flags, `call` the scene's setup script, `warpto` the map — then A/B it. That state-construction is the unlock.

## ⚠️ Discipline (this project's hard-won lesson)
This repo has a track record of **retracted false positives** (F1 forest-battle "freeze", the first-sleep "freeze", "medicine unobtainable"). An open **textbox/menu waiting for A is NOT a freeze** — advance dialogue *fully* (`mash`) and test responsiveness with a **real action**, not direction keys on an open box. Confirm a real freeze with `trace`/`stepto` (tiny PC range), not a stuck-looking screenshot. Never claim a fix without an in-engine A/B proof **and** a patch round-trip.

---

## Priority queue

### 1. D3 — Jessie & James battle: switching hides other party sprites  `open` · most tractable
**Symptom:** in the first Jessie & James battle, switching a Pokémon makes the *other* party mons' sprites go invisible. Reported, not yet diagnosed; flagged engine/script level.
**Why it's tractable:** it's a *specific scripted battle* — fully reproducible in-engine, no rare state needed. This is the best candidate for a capable agent.
**Approach:** stage the battle directly with the rig's battle-setup wrapper (same technique used to stage the Pidgeotto fight: `call ScriptContext1_SetupScript(<battle-setup-script>)` at `0x08069AE4/…E5` on a movable field). Give the player a **≥2-mon party**, open the battle, **switch**, and `shot` the party/battler OAM frame-by-frame. Determine whether the missing sprites are a **graphics-decompression/OAM** problem (sprites never loaded / tiles freed) or a **script** problem (a `hidesprite`/state flag). Locate the exact battle script by decompiling the relevant map (`tools/decomp.py`). If it's a byte/script fix, patch + A/B-prove like the others; if it's deep engine OAM behavior, document it honestly as engine-level.

### 2. F7 — Orange Islands "lady" event crash  `needs-repro` · needs late-game OI state
**Status:** investigated (2026-06-14, `audit/oi-progression-map.md`). Ruled OUT an F1-class scripted-battle freeze — there is **no `setwildbattle` of Tentacool/Tentacruel anywhere** in the ROM; the Nastina/Tentacool script (`~0x882DF5D`) is a clean flag/msgbox scene. **Residual unknown:** the **Maiden's Peak** old-woman→Gastly **object-transformation** uses custom opcodes that don't cleanly decompile, and can't be ruled out **without OI late-game in-engine state**.
**Approach:** construct OI late-game state (set the OI progression vars per `audit/oi-progression-map.md`), `warpto` Maiden's Peak, trigger the ghost transformation, and watch for a real crash with `trace`/`stepto`. If it survives clean, F7 can move to won't-repro with a definitive statement.

### 3. L6 — "won 6 badges, shows 5"  badge code proven sound; 4–5 gyms D1-gated; not reproduced
**Status:** the badge **award** code is provably sound (8 distinct unconditional setters, zero `clearflag`, display counts flags at sb1+0xFE4). The "6 shows 5" is **dominantly a D1 manifestation** — 4–5 gyms' badge *paths* gate on Box-3 story vars, so PC-storage corruption misroutes them (Marsh/Boulder/Cascade **live-reproduced**, `audit/d1-gym-badge-blocks.md`).
**Residual unknown:** is there *any* **non-D1** mechanism (a gym that skips its own `setflag` under some legit path)? No mechanism found, but never reproduced with a real 6-badge save.
**Approach:** construct a genuine 6-badge save with the rig (set badge flags `0x820–0x827` minus one; set the gyms' completion vars to legit values), open the trainer card, and confirm the count. Then A/B each D1-exposed gym (clean vs corrupt Box-3 slot 0/1/7) to bound the effect. Expected verdict: "count desync is the D1 box-reserve manifestation; award code sound" — but prove it with a real 6-badge state.

### 4. L7 — Safari Zone: Team Rocket doesn't appear  `needs-repro` · corroborated ×2 · likely unauthored
**Status:** two players report it, so it's a real player-facing gap, not noise. But the Safari Zone is **reused-vanilla FireRed** (63/63 stock "SAFARI" strings) — a Team-Rocket-in-Safari encounter is *not* FireRed content, so the most likely truth is **content never authored** (no asset to restore), not an authored-then-broken event.
**Approach:** settle it definitively — scan every Safari map's scripts/objects for *any* TR actor, `setwildbattle`, or gated event referencing Rocket, and confirm absence. If truly absent, close as **won't-fix (unauthored)** with a clear statement (two reporters deserve a definitive answer). Only a real Safari playthrough could prove a *gated* event exists; static absence is strong evidence it doesn't.

### 5. L8 — Safari Zone: "stuck without the bike"  `needs-repro` · low-confidence
FireRed's Safari is a **bike-free walking zone by design**; "stuck without bike" reads as expectation mismatch. No collision trap found on inspection. Quick to close with a Safari walk-through confirming no dead-end. Low ROI.

### 6. L3 — stuck on Misty's bike after the Spearow shock  `needs-repro`
Natural path **proven clean headlessly** (scene → warp → player walks free; the chase map has `bikingAllowed=0` so you can't be mounted at the shock). Only an exotic "mount on a biking-allowed map and ride back pre-shock" construction reproduces — likely a stale pre-4.5.3 report. Re-open only if someone produces a real 4.5.3 save stuck mounted. Low ROI.

### 7. L11 — bedroom-PC "message stays open"  `needs-repro`
**Did not reproduce** in 4.5.3 (live rig test: PC opens storage, exits clean). Likely fixed upstream / a lost strikethrough from the original plain-text bug list. Low ROI.

### G1 — girl-disguise battle sprite mis-colored  `open` · needs a human (art)
Shirt blue / hair white on the disguise battle sprite — a **palette/art fix that needs a spriter**, not an analysis agent. Out of scope for an investigation pass; flag for a human contributor.

---

## Suggested order for an analysis agent
**D3** (reproducible now) → **L6** and **F7** (construct the state, then A/B) → **L7/L8** (settle the Safari reports definitively, likely won't-fix) → **L3/L11** (low ROI, close if convenient). **G1** and the **D1 architectural cure** (save-format relocation) need a human / a large rework and are not repro tasks.
