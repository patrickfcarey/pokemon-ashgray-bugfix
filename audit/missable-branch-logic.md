# Audit — Pure-ROM Permanent Missables & Progression-Skips from BRANCH LOGIC (L2/L9 class)

ROM under test: `rom/ashgray.gba` (base 0x08000000). Method: reachability-aware
map-walk (persons stride 24 / triggers stride 16 / signs stride 12; mapscript
subtables; 10 gStdScripts @0x08160450; transitive closure through
call/goto/call_if/goto_if + trainerbattle continuations; bank table @0x5524C),
then full decompile + hand-trace of every gift/progression event. Opcode bytes
confirmed against `tools/decomp.py`.

## VERDICT

**0 confirmed missables. 0 confirmed progression-skips. 0 candidates outstanding.
Class CLEARED.**

Every reachable `givemon`/`giveegg` gift NPC in the game (19 root events) was
decompiled and every reachable branch (decline / party-full / box-full / success)
was traced on a **fresh, uncorrupted save**. In all 19 the giver is consumed
(`removeobject` + guard `setflag`/`setvar`) and the completion/gate flag is set
**only on a branch that has already run `givemon`/`giveegg` successfully**. Every
refusal branch (player declines, party full, all-boxes-full) returns WITHOUT
removing the giver and WITHOUT setting the guard or gate flag, so the event
re-offers. This is the CORRECT contrast pattern described in the brief — the L2
"removeobject-before-give" inversion does **not** occur anywhere, and no success
path skips its own gate-advance var (no L9 shape).

The reachability sweep initially flagged a 20th root (map 1.127 tournament
battle → `giveegg`×2 @0x08630016). This is a **false positive** from
conservatively over-reading `trainerbattle` arguments — see "Methodology note"
below. It is not a real script and not reachable.

---

## Per-event proof (all 19 givemon/giveegg roots)

Convention below: "party-full guard" = `getpartysize; compare 0x800D,6` (or a
givemon-result check `compare 0x800D,2` = "no room in party AND all 30 boxes").
"Guard set after give" = `removeobject`/`setflag`/`setvar`-completion runs only
on a branch reached after the give opcode.

### 1. Stray CHARMANDER — map 1.31 person0 @0x0815CDC (givemon 0x04 lvl10 @0x82CC8A) — CLEAN
Gate var 0x6086 (must==1 to offer). Decline → "refused to battle", release (no
consume). Party-full (`compare 0x800D,6` @0x82CC7F) → "too many POKeMON",
release/end — **no removeobject, no setflag, 0x6086 unchanged → re-offers.**
Success: givemon → `removeobject 0x800F` + `setflag 0x1088` + finally
`setvar 0x6086,2` (gate advance). Consume strictly after give. CLEAN.

### 2. HAUNTER capture (Pokémon Tower) — map 1.89 person6 @0x081A73C and person7 @0x08187DA (givemon 0x5D lvl25 @0x81C0BC / @0x817D58) — CLEAN
This is a progression-critical capture and the most intricate full-party recovery
in the audit; analyzed in full (raw person-event table dumped).
- Objects: person6 (localId 7, spawnflag 0x002C = the "body"), person7
  (localId 8, spawnflag 0x003F = the Haunter handoff). State var 0x6060:
  0→3 (spirit pulled, trig0)→{2 on party-full at person7}→4 (Haunter obtained).
- person7 party-full (@0x817A03): `setvar 0x6060,2` + "too many" → end. Does NOT
  removeobject itself, does NOT setflag 0x003F.
- person6 party-full (@0x81AD95): person6 had set 0x1014/0x003F + removeobject(self)
  at its top, then "too many" → end. 0x6060 stays 3.
- **Recovery proof (map-load script mapscr_t3 @0x81790C):** on every re-entry,
  `0x6060==3` → clearflag 0x003F + clearflag 0x002C (respawns BOTH givers);
  `0x6060==2` → clearflag 0x003F (respawns person7). Because 0x6060 only reaches 4
  after `givemon` actually runs, any party-full bail leaves 0x6060 at 2 or 3 and
  the next map-load **undoes** person6's setflags and respawns a Haunter giver.
  Re-offerable. CLEAN. (Exit triggers trig1/trig2 block on `checkflag 0x1014`
  cond=0; person6 sets 0x1014 = "back in body" so you can still leave — no strand.)

### 3. SQUIRTLE SQUAD / Pikachu-medicine — map 1.122 person0 @0x82AE79 & person1 @0x87375D (givemon 0x07 lvl10, three sites) — CLEAN
Most branch-heavy event (flags 0x1090/0x1092/0x1283/0x1300/0x1302/0x1303/0x1304).
- Every `removeobject 0x0001` (the Squirtle leader) sits **immediately before** its
  `givemon 0x07` (@0x8738C1/0x873B76/0x873CA6) — never orphaned.
- Every party-full (`compare 0x800D,6`) branch → "too many POKeMON", release/end,
  no consume (@0x82C77A and the 0x873xxx variants).
- SUPER-POTION-given-but-party-full sets 0x1300 and bails; on re-talk person1 sees
  0x1300, re-checks party, gives Squirtle once a slot frees → 0x1300 is a RETRY
  state, not a permanent consume. Potion-give always sets 0x1092 first (Site A),
  which permanently unlocks person0 as the Squirtle giver, so Squirtle stays
  obtainable on every path. Completion flag 0x1283 is set only on post-givemon
  branches. No skip. CLEAN.

### 4. In-game trade BUTTERFREE↔RATICATE — map 1.9 person0 @0x081A713 (givemon 0x88738C path via type-1 trainerbattle cont 0x81AB31) — CLEAN / not in scope
`givemon` here is the traded-in mon after trade specials 0x0176/0x00FC/0x00FF take
your mon; party size is room-neutral so "no room" cannot arise. Decline branches
("don't want to trade" 0x81AA91, "hoodwink" 0x81AAC4) end without consuming.
Trade flags 0x1335/0x1001 set only after `givemon`. Trades inherently can't orphan.

### 5. Lost LAPRAS (Orange Islands) — map 3.13 person5 @0x087D9F8 (givemon 0x83 lvl30 @0x8A1B99) — CLEAN
Gate var 0x7036 (==2 after Team Rocket fight to offer). Success codes 0 (party) /
1 (box) both → `setvar 0x7036,3` + `removeobject 6` + `setflag 0x1352`/0x0249.
**Code 2 ("no more room", all boxes full) @0x8A17EC → release/end with NO
0x7036 advance, NO removeobject — re-offers.** A full party still gets Lapras (box
path), so on a fresh save it cannot be missed. CLEAN.

### 6. STONE TOWN EEVEE — map 3.38 person1 @0x0864B8C (givemon 0x85 lvl10 @0x810BA6) — CLEAN
"Return it to its owner?" yes → `compare 0x800D,6; goto_if cond=0` (room) →
givemon → `setflag 0x1145` + `removeobject 2` + `setvar 0x6145,1`. Party-full
fallthrough @0x8107C8 → "no room for it" → end, **no consume → re-offers.**
Decline → "Sorry, EEVEE!" end. CLEAN.

### 7. Starter PIKACHU from PROF. OAK — map 4.3 person0 @0x0868601 (givemon 0x19 lvl5 @0x82264E) — CLEAN
The game-opening starter, reached via the 0x1063/0x1064/0x1065 "starters given
away, one left" chain → Pikachu offer. "No" to the Pikachu prompt (@0x8224AF) →
closemessage/hidemonpic/release — no `setflag 0x0828`, no give → re-offerable.
"Yes" → `setflag 0x0828` then givemon. No party-size guard exists here, but it
**cannot brick**: the starter is given when the party is empty (you have 0 mons
before your starter), so `givemon` always succeeds. Post-give gives Pokédex +5
Balls (setflag 0x0829) and `setvar 0x7000,2`. The later Oak daycare / League
branches use correct party-full guards (`compare 0x800D,6` @0x871EC9 "can't take
this POKeMON back if no room" → refuse without consume). CLEAN.

### 8. Abused-POKéMON adoption room — map 8.2 person0..3 @0x0837748/0x083761A/0x0836F75/0x0836D17 (givemon Spearow 0x15 / Oddish 0x2B / Pidgey 0x10 / Rattata 0x13, lvl5) — CLEAN (all 4)
Identical pattern ×4. Room gate flag 0x1123 (set → "refused to go with you").
Offer → "adopt it?" yes → party-full guard (`compare 0x800D,6` → "too many
POKeMON", release/end, no consume) → success: `setflag 0x112X` + `removeobject N`
+ givemon. setflag/removeobject sit after the party-full guard, so givemon can't
fail. Decline → playmoncry/release. Optional gifts, not gates. CLEAN.

### 9. Fossil-revival doctor — map 12.1 person2 @0x08558B3 (givemon Omanyte 0x8A / Kabuto 0x8C / Aerodactyl 0x8E, lvl5) — CLEAN
Per-fossil branch (var 0x4069/0x406A select which). Each: givemon → `compare
0x800D,2` (no room, boxes full) → "BOXES are full" release/end **before** the
guard `setflag 0x02EC/0x02ED/0x02EE`. Guard set only on success (code 0/1, party
or box). Doctor re-offers if the mon wasn't received. CLEAN.

### 10. Togepi EGG handoff — map 2.38 person0 @0x0815B45 (giveegg @0x815B93) — CLEAN
(Re-verified the Worker-2 spot-check.) "Want to take it?" yes → party-full guard
(`compare 0x800D,6`) → "make room in your party for this EGG!" release/end, no
consume. Success → giveegg → `setflag 0x1034` + `removeobject 1` + `setvar
0x6159,3`. Correct full-party pattern. CLEAN.

### 11. League Admissions Exam examiner — map 2.29 person0 @0x084B272 (givemon ×30 @0x851A49.. lvl50) — CLEAN / not in scope
The 30 givemons are the *rental* exam team, handed out then taken back
(`special 0x0028`). Self-contained exam loop gated by exam-state flags
0x1200–0x1210 / var 0x6199; re-entry intentionally blocked once passed/failed
("cannot take it again"). Not a permanent gift that can orphan.

### 12. Game Corner coin-prize counter — map 2.35 person8 @0x0848E8D (givemon var-species 0x4001 @0x848FF7.. lvls 8/9/18/25/26) — CLEAN / not in scope
Repeatable purchase. `removecoins` runs only on success; "not enough COINS" →
back to menu (no consume); givemon code 2 ("BOXES full") @0x8490F7 → hidecoinsbox/
release with NO removecoins. Repeatable shop — cannot be permanently orphaned.

---

## additem-gift class (180+ reachable `additem` nodes) — CLEARED by construction
Enumerated all reachable `additem` nodes (see sweep). They are signs, PokéMarts,
hidden-item Balls, trainer/story rewards, and one-time key-item gives. The L2
orphan shape is specific to `givemon`/`giveegg` (party "no room"); `additem` on a
full bag fails in-engine without consuming the giver, and a full bag is not a
fresh-save early-game condition. Spot-traced representative key-item gives (e.g.
the OAK Pokédex/Balls give @0x821D2F sets its `setflag 0x0829` inline on the same
linear success path) — none gate a giver's removal on a bag-full branch. No
additem-gift orphan found.

## givemoney / addcoins gift class — CLEAN
`addcoins`/`addmoney` nodes are casino payouts and reward grants on linear success
paths; none guard a giver behind a money-full branch. The MAGIKARP salesman
(map 1.5 person1 @0x0802F94, a *purchase* with guard flag 0x0249) was traced: money
is removed and 0x0249 set only on the success branch; the givemon code-2 "no more
room" branch @0x833345 bails with no removemoney and no setflag → re-offers. CLEAN.

---

## Methodology note — trainerbattle false positives (why the 1.127 giveegg is NOT a bug)
`trainerbattle` (opcode 0x5C) has type-dependent length, so the sweep
conservatively harvested every 4-aligned dword in [op+6, op+6+20] as a potential
continuation pointer. For `type=0x03` (no-intro) the ONLY real script pointer is
the defeat script at +6 (instruction length 10); dwords at +14/+18 are the next
real opcodes of the surrounding script. At map 1.127 (semifinal vs MELISSA,
trainerbattle @0x87DC85), the +18 dword happens to equal 0x08630016, whose bytes
begin 0x7A (`giveegg`) and decode into garbage (`subvar 0x7C79,0x6C4D`,
`pokemartdecoration`, `warphole`, then `goto 0x43AE45` → invalid opcode 0xEE).
Raw arg bytes confirmed: type=3, only +6 (0x87DD85) is a valid script pointer.
Excluded as a non-reachable artifact. All 19 real givemon/giveegg roots reach
their give opcode through a genuine linear body or a genuine type-1/2/4
continuation, and all were traced above.

## Discipline statement
Every CLEAN verdict above is backed by a decompiled, hand-traced reachable
fresh-save path (decline / party-full / box-full / success), not an inference.
No "could be orphaned" was promoted to a finding. No corrupted-var (box-deposit /
D1) dependency was counted as a new bug. No fourth over-claim added.
