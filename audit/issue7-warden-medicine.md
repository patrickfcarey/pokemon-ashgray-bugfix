# Issue #7 — "deliver the medicine before helping the warden and Dragonair"

Static trace of the Safari-Zone **warden / Dragonair** event vs the **Sunny-Town medicine
delivery**, to decide whether a real out-of-order progression bug exists.

Method: FRLG script decompile (`tools/decomp.py`), pointer xref (`tools/xref.py`), full ROM
scans for `setvar/compare` on the story vars and `additem/removeitem/checkitem` on the items,
map event-table walks, and warp+connection topology (`tools/oi_map_graph.py`). All addresses
are **file offsets** unless prefixed `ROM` (ROM = file + 0x08000000). The dialogue dump
`audit/03-dialogue.md` indexes text at each `\p` boundary, so its addresses are mid-block; the
real `loadword` targets are the block heads found here.

---

## 1. Scripts found (live unless marked)

### Warden / Dragonair (Safari Zone) — variable **0x6095**
- **Dragonair-bomb cutscene** (post-Rocket-battle resolution), two position-variant copies:
  - `0x844A21: setvar 0x6095 = 1` … "WARDEN: This is … the same DRATINI…" / "It's the legendary DRAGONAIR! It's throwing the bomb back…"
  - `0x8456DB: setvar 0x6095 = 1` … (the other variant) → TEAM ROCKET blast-off → …
- **Warden reward tail** `0x845770`→`0x8457DE`: "WARDEN: You saved the DRATINI!" → `additem DRAGON SCALE (0xC9)` → "WARDEN: Thanks to you I was able to see my beloved DRAGONAIR again…" → **`0x8457D8: setvar 0x6095 = 2`**.
- **Trigger gating** (map **1.66**, coord events): `trig0/1 at (18,10/11) var=0x6095 val=0x0000 → script 0x844A78`. So the whole event fires **only while 0x6095 == 0** and is self-disabling.
- **TM02 finder** (map 1.71 person0, `0x84550A`): independent, gated on flag `0x0239`.
- **0x6095 state:** 0 = warden not done · 1 = Dragonair cutscene resolved · 2 = reward (Dragon Scale) collected.

### Medicine delivery — variable **0x6097**
- **LIVE delivery (Sunny-Town Pokémon-Center nurse)** = map **36.0 person0** (gfx 0x40 nurse at (7,2)) → script **`0x81E040`**:
  ```
  0x81E040: compare 0x6157 == 1  → goto 0x8223CB   (intro done → plain heal nurse)
  0x81E04B: goto 0x810000
    0x810000: compare 0x6097 == 1 → goto 0x8223CB  (already delivered → plain heal)
    0x81000B: goto 0x80F61F
      0x80F61F: compare 0x6097 == 3 → goto 0x80F630 ("transport system down") → 0x845DAF
      0x80F62A: goto 0x845DAF
        0x845DAF: compare 0x6097 == 1 → skip (0x8223CB)
        0x845DBA: compare 0x6097 == 3 → skip (0x8223CB)
        0x845DC5: [DELIVER] "Oh! You must be the one my sister sent from FUCHSIA! That sick
                   POKéMON really needs that medicine!" → removeitem MEDICINE(0x0161)
                   → "please keep that bike" → give BICYCLE(0x0168) → 0x845DF8: setvar 0x6097 = 1
  ```
  ⇒ delivery runs when **0x6157 ≠ 1 AND 0x6097 ∈ {0,2}**.
- **0x6097 is SHARED with the DUPLICA / "HOUSE OF IMITE" event** (same "Sunny Town" region):
  - DUPLICA win post-script `0x80F16C` / `0x81E004`: **setvar 0x6097 = 2**.
  - map **1.62** map-load (`0x845DFF`) uses 0x6097 (==2/3 → DUPLICA "after" object; else DUPLICA-trainer object).
  - map **36.0** map-load (`0x845E7D`) and the Sunny-Town coordinator (`0x845E8F` / `0x845FB8`) use 0x6097==3 + 0x6157 for nurse/NPC visibility.
  - map **3.35** weather triggers (`0x845D5D`, gated `var=0x6097 val=0`) and map **3.37** ("SUNNY TOWN") weather (`0x8CFD4E`, 0x6097==1) — cosmetic.
- **0x6157** ("Sunny-Town PC intro done"): set once at `0x845F8F` (a cutscene + warp); thereafter the nurse is a plain heal nurse.

### Medicine ACQUISITION (the give-quest) — **ORPHANED / dead code (UNVERIFIED-live = NOT reachable)**
- `0x80ED88` (reached only from `0x80ECCF: compare 0x6095==1 → 0x80ECD4: goto_if cond=1`):
  "Excuse me… **I heard how you helped the WARDEN!** … deliver this MEDICINE I made to the
  POKéMON CENTER in SUNNY TOWN" → `additem MEDICINE(0x0161)` + `additem BICYCLE(0x0168)`
  → goto `0x80F003: setvar 0x6095 = 3`.
- **No live event points to it.** `xref 0x80ECCF / 0x80ECD4 / 0x80ED88` → the only real referrer
  is the internal `goto_if` at `0x80ECD4` (whose own head `0x80ECCF` has **0 inbound pointers**);
  the lone other hit (`0x8B52FB`) is a coincidental byte pattern inside unrelated battle data.
  It is not a person/trigger/sign in any live map header.
- **It is the ONLY medicine-item source in the ROM.** ROM-wide `additem 0x0161 qty=1` exists only
  at `0x80EDA7` / `0x80EDB8` (both inside this orphaned block); the only `removeitem 0x0161 qty=1`
  is the delivery at `0x845DCD`. ⇒ **The medicine item (0x0161) is not obtainable through any
  traced live script.**

---

## 2. Dependency chain (what gates what)

```
WARDEN/DRAGONAIR (Safari)            MEDICINE DELIVERY (Sunny-Town PC nurse)
  var 0x6095: 0 → 1 → 2               var 0x6097: 0 → 1 (delivered)   [shared w/ DUPLICA: →2]
  trigger gate: 0x6095 == 0           nurse gate: 0x6157 != 1  AND  0x6097 ∈ {0,2}
  reward: Dragon Scale / TM02         action: removeitem 0x0161 (NO checkitem), give bike, 0x6097=1
        │                                    ▲
        │  (intended, per dialogue:          │  ❌ NO read of 0x6095 anywhere on the nurse path
        │   "I heard how you helped the      │  ❌ NO checkitem 0x0161 before removeitem
        ▼   WARDEN" → warden first)          │
  give-quest 0x80ED88 (DEAD CODE) ──gives──> MEDICINE 0x0161 + BIKE, requires 0x6095==1
```

- The **only** thing that could enforce "warden → medicine" is that the give-quest (which would
  hand you the medicine + a bike) is gated `0x6095 == 1`. **That give-quest is dead code**, so
  the intended gate never runs.
- The **live** delivery path reads only `0x6157` and `0x6097` — it **never checks the warden var
  0x6095**, and it **never checks that you hold the medicine** before `removeitem`.

## 3. Topology (can the nurse be reached pre-warden?)

- Warden/Dragonair lives in the Safari sub-complex (maps **1.63–1.71**), entered only via the
  Safari **gate** (`11.0 → 1.63`). It is **not** on the route between Fuchsia and Sunny Town.
- Sunny-Town overworld (**3.37**) connects `left → 3.38 → 3.32/3.33` (the western Kanto overworld)
  in addition to the Fuchsia bike-bridge (maps 25/26). Warp+connection BFS with the bridge **and**
  the Safari blocked still reaches 3.37 (and the PC at 36.0). ⇒ topologically the nurse is
  reachable **without the bike-bridge and without the Safari/warden**, with `0x6097 == 0`.
- (Whether the western approach is actually open this early in *story* order is not proven
  statically — **UNVERIFIED**. It does not change the script verdict below.)

---

## 4. VERDICT

**There is a real ordering / gating defect, but it is NOT the simple "softlock if you deliver
before the warden" the report implies — and the engine does not crash or hard-lock.**

What is actually true, from the live scripts:

1. **The medicine delivery is NOT gated on the warden at all.** The Sunny-Town nurse
   (`0x81E040 → 0x810000 → 0x845DAF`) checks only `0x6157` and `0x6097`. The intended
   "warden-first" gate lived on the **give-quest**, which is **orphaned dead code** — so it never
   takes effect. ⇒ You can trigger the delivery cutscene with the warden event still pending
   (`0x6095 == 0`). The report's headline ("deliver medicine before helping the warden") is
   therefore **confirmed possible**.

2. **Consequence is NOT a softlock.** The warden event is independently gated on `0x6095 == 0`
   and shares no variable with the nurse path, so delivering first does **not** block the warden,
   the Dragonair cutscene, or the Dragon Scale/TM02 reward. No progression is lost.

3. **The genuine bugs exposed are two robustness holes, both cosmetic/again-flavor, not blocking:**
   - **(a) Phantom delivery + free bike.** The deliver branch does `removeitem 0x0161` with **no
     `checkitem` guard** and the medicine item is **otherwise unobtainable** (give-quest dead). So
     a first-time visitor "hands over" a medicine they never had and is **given a free BICYCLE**,
     with the script narrating a fetch-quest that was never started.
   - **(b) Shared-variable clobber with DUPLICA.** `0x6097` doubles as the DUPLICA/HOUSE-OF-IMITE
     progress var. The deliver branch fires for `0x6097 ∈ {0,2}` and overwrites it to **1**. If the
     player beats DUPLICA first (`0x6097 = 2`) and then triggers the delivery, `0x6097` is reset
     `2 → 1`, which the map-1.62 load script reads as "DUPLICA not beaten," **re-spawning the
     DUPLICA trainer** (a repeatable battle / state regression). This is the only concrete
     state-break, and it requires DUPLICA-before-delivery, not warden ordering.

**Severity: low.** Out-of-order is possible and the delivery is logically broken (phantom item,
free bike), but it does not soft-lock or skip required progression; the worst case is the DUPLICA
re-spawn from the 0x6097 collision.

> Honesty note / non-claims: I could not find a live event that reaches the give-quest, so I treat
> the medicine *item* as unobtainable and the give-quest as dead code (**UNVERIFIED** that any
> native/`special` routine reaches it). Whether the western approach to Sunny Town is open before
> the Safari in normal story order is **UNVERIFIED** (topology allows it; story-flag order not
> traced). The "phantom delivery" and "DUPLICA clobber" are proven from the bytes; the *in-engine*
> reproduction was not run.

---

## 5. Minimal proposed fix

The robust, low-risk fix targets the live delivery branch (`0x845DAF` / `0x845DC5`) rather than
trying to resurrect the dead give-quest. Two independent guards; either alone removes the
phantom-delivery class, both together fully harden it:

1. **Require possession of the medicine** before delivering. Insert, immediately before the
   `removeitem` at `0x845DCD`, a `checkitem 0x0161, 1` + `compare 0x800D, 1` + `goto_if !=`
   to a "you don't have anything to deliver" exit (or just skip to the generic nurse `0x8223CB`).
   This stops the no-item phantom delivery and the free bike.

2. **Gate the delivery on the warden** to restore intended order: add `checkflag`/`compare
   0x6095 >= 1` (warden done) as a precondition of the deliver branch; if not met, route to the
   plain heal nurse `0x8223CB`. (Use `0x6095 >= 1`, i.e. compare ==0 → skip, since the reward
   path leaves it at 2.)

3. **Fix the shared-var clobber** (independent of ordering): the delivery should not write the
   DUPLICA-shared `0x6097`. Either move the "delivered" flag to a free flag bit (e.g. a `0x1xxx`
   flag) instead of `setvar 0x6097 = 1`, **or** only run the deliver branch when `0x6097 == 0`
   (drop the `== 2` case) so beating DUPLICA can never re-enter delivery. The second option is a
   one-operand change (the entry compares already exist) and is the smallest safe patch.

Because the give-quest that would supply the medicine is dead code, the **simplest player-correct
fix** is #1 (medicine-possession check) + #3 (don't clobber 0x6097) — that makes the nurse inert
unless a medicine is actually carried, which (given the dead give-quest) means the broken errand
simply stops mis-firing, with no progression dependency added.
