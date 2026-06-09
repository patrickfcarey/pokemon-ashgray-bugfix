# Fork text changes — review list (no playthrough needed)

Each fix is objectively verifiable here: the corrected spelling is unambiguous, and the
game renders the *same* character bytes shown below. (The decoder reads the ROM the same
way the GBA text engine does, so "what you read here" = "what shows on screen".)

`\n` = line-break, `\p` = new text box.

| ID | Offset | Before (in original Ash Gray) | After (fork) |
|----|--------|-------------------------------|--------------|
| T1 | `0x834CBF` | …playing out in **the the**\nstreets! It's so fun! | …playing out in **the**\nstreets! It's so fun! |
| T2a | `0x829FAC` | AJ: Today all my **sacrfices** and\nhard work have finally paid off! | AJ: Today all my **sacrifices** and\nhard work have finally paid off! |
| T2b | `0x814026` | {PLAYER} **recieved** the\nBIG MUSHROOM from CASSANDRA! | {PLAYER} **received** the\nBIG MUSHROOM from CASSANDRA! |
| T2c | `0x867878` | {PLAYER} **recieved** the FERTILIZER\nfrom FLORINDA! | {PLAYER} **received** the FERTILIZER\nfrom FLORINDA! |

## How each was verified (without running the game)
- **T1 / T2b / T2c** — same-length or shorter edits, written in-place. Re-decoding the
  string at its offset shows the corrected text (above). The string's pointer is unchanged.
- **T2a (sacrfices→sacrifices)** — one byte longer, so the whole line was rewritten into
  free space (0xC00000) and its **single loadpointer reference was repointed** to it.
  Verified: the new location decodes to the corrected line, and exactly 1 reference updated.
- **Patch integrity** — `firered.gba + ashgray-fork.ips` round-trips to the fork ROM
  (CRC `c241bb99`) every build, so nothing else changed.

No other bytes in the text regions were touched — these 4 lines are the only dialogue edits.
