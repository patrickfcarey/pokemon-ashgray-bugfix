# Research & reproduction toolchain

These are the working scripts used to **find, reproduce, and verify** the bugs
this patch fixes — the investigation half of the project. The scripts that
actually *produce* the patch live one level up in [`tools/`](../) (the
`fix_*.py` fixers, `patcher.py`, `makepatch.py`); the headless emulator harness
is in [`tools/emu/`](../emu/).

**These document method, not a turnkey pipeline.** Many reference a local
working ROM (`firered.gba` / `forest_test.gba`), savestates (`.ss`), or test
binaries that are **not** included here (no ROM is distributed — see the repo
[`NOTICE`](../../NOTICE)). They're published so the analysis behind each fix is
inspectable, not because they run standalone. Several are one-off or iterative
(e.g. `gen_l12b..f` are successive cuts at the same repro) — kept as-is rather
than tidied into a false story of linear progress.

> Some audit writeups still refer to these by their original development path
> (`_emu/<name>.py`). Same files — they now live here.

## By prefix

- **`gen_*.py` / `mk_*.py`** — reproduction builders: write a savestate or a
  patched test ROM that drops the engine into the exact state a bug needs
  (e.g. `gen_badegg_test.py`, `gen_autodeposit_test.py`, `gen_field5_test.py`,
  `mk_warp_test.py`, `mk_d7real.py`).
- **`probe_*.py`** — targeted state inspectors run against an affected build
  (badges, boxes, daycare, specific trainers/encounters: `probe_badges.py`,
  `probe_box2.py`, `probe_daycare.py`, `probe_koga.py`, …).
- **`find_*.py`** — locators: `find_bl.py` (alignment-correct Thumb-BL caller
  finder), `find_boxidx.py`, `find_pss_callers.py`, `find_tv.py`.
- **`map_*.py`** — the variable↔storage / map-data mapping behind the Bad-Egg
  analysis (`map_var_boxes*.py`, `map_sb1_interior.py`, `map_dump.py`,
  `map_flag_var.py`).
- **`trace_*.py`** — control-flow tracing for the gym/badge-gate softlocks
  (`trace_all_gyms.py`, `trace_gym_gates.py`, `trace_koga_map.py`).
- **`var_*.py` / `*_classify.py`** — story-variable classification
  (`var_classify.py`, `var_zone_summary.py`, `verify_high_vars.py`,
  `label_vars.py`).
- **`disasm_pss.py`** — Thumb disassembler + literal-pool resolver for the PC
  storage system; the box-reserve fix (`../fix_boxreserve.py`) was built on it.
- **misc helpers** — `checksav.py` / `savetype.py` / `check_box45.py` (Gen-3
  save sanity), `decode_moves.py`, `string_bounds.py`, `grid.py` /
  `montage.py` (screenshot tiling), `gym_values.py`, `marsh_values.py`,
  `maze_explore.py` / `maze_solve.py`.

## See also

- [`../`](../) — the fixers that produce `patches/ashgray-fork.ips`.
- [`../emu/`](../emu/) — the libmgba verification harness (`rig.c` + wrappers).
- [`../../audit/`](../../audit/) — the writeups these scripts produced.
