---
id: LG-9816
family: ledger
title: WK-1178 slice SL-1566 — batch scoring serialises every declared output type and never aborts on one row (PL-1565), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-11
owner: executor
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a
phase: P2
work: WK-1178
slice: SL-1566
plans: [PL-1565]
corrected_by: []
relates: [FD-1561, RL-1567, RL-1343, RL-923, FD-1333, SL-1569, FR-214, FR-254, FR-255, NFR-499]
---

# LG-9816 — WK-1178 slice SL-1566: batch serialises every declared output type

Executed by `executor-sl1566` from PL-1565 (a leaf plan; WK-1178 has no Work plan, so L5's
one-plan-per-Work reads as PL-1565 itself). Authored on branch `sl-1566-wk1178-batch-serialise`,
cut from `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7` and merged with `origin/main`
`02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a` (SL-1600). Times are BST (`TZ=Europe/London date`).

**GO:** not recorded here yet. The lead's dispatch brief (`brief-executor-sl1566-2026-10-11.md`)
says AUTHOR now and activate only on the maintainer's GO; this ledger quotes the GO header when the
lead relays it. Until then `SL-1566` and `PL-1565` stay `draft` (no activation commit).
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1565`, the leaf plan for the row `SL-1566` in `docs/roadmap.md`: "WK-1178 fix slice — batch
scoring serialises every declared output type and never aborts on one row". Finding `FD-1561`
(MEDIUM, LATENT). Rulings it builds on: `RL-1567` (DP-1 (b), DP-2 (ii), DP-3, integrality by
exact equality, T1/T2) and the maintainer's entries quoted in PL-1565.

Requirements held: `03` FR-255 (a row's serialisation failure is that row's `"error"` row),
FR-254 (the type vocabulary is one list), FR-214 (`relativity`/`percentage` take the `decimal`
string form), NFR-499 (no value in an error row).

Write set (PL-1565 §"Write set"): `packages/pricing-core/src/pricing_core/rating/score.py`;
`packages/pricing-core/tests/test_rating_score_batch_outputs.py` (new);
`backend/tests/test_scoring_handlers.py` (appended); `docs/specs/03-rating-engine.md` (the
`outputs_json` row and the FR-214 row, from `RL-1567` T1/T2 byte for byte); this ledger;
`docs/INDEX.md`.

Not in scope: `RL-1343` rules 3 and 4 and the `/score` half for `relativity`/`percentage`
(`SL-1569`); the save-time type rule (`PL-1562`).

### Task list

- [x] Task 0 — preconditions: `FD-1561` minted; `SL-1427` merged (b6dd96fd, #1219); DP-1/2/3 ruled
  (`RL-1567`); `RL-1567` minted. Line numbers moved since the plan (SL-1427, SL-1448 additions):
  `_KNOWN_OUTPUT_TYPES` now `score.py:992`, `_coerce_output_value` `:995`, `_outputs_json` `:1036`,
  `_batch_error_code` `:1051`, `_score_batch_row` `:1128`. The logic is unchanged. Contention:
  no unmerged branch writes `score.py`, `test_scoring_handlers.py` or the new test file (the
  planner's readiness memo, re-checked by `git merge-tree` of this branch against `origin/main`,
  rc 0).
- [x] Task 1 — the row escape (PL-1565 items 1–4). Tests first `74fb7b69`; code `30fd08ac`:
  a second `try` around `_ladder_json` and `_outputs_json`; `_batch_error_row` is the one place an
  error row is written; `NotImplementedError` still propagates.
- [x] Task 2 — the four declared types (items 5–8, 12, 13). Tests first `79031a66`; code `56eebd5a`:
  `_KNOWN_OUTPUT_TYPES` gains `int`, `count`, `relativity`, `percentage`; `int`/`count` are written as
  a JSON integer by exact equality (`value == int(value)`, no tolerance, `3.0` → `3`, `bool` and
  non-finite refused, message names the type and never the value); `relativity`/`percentage` take
  `decimal`'s string form.
- [x] Task 3 — spec text `cd3b5bcf`: `RL-1567` T1 on the `outputs_json` row and T2 on FR-214,
  byte for byte from the record's code blocks. T2 is applied here because `SL-1569` has not merged.
  Counts (`str.count`): T1 find 1 → 0 and new text 0 → 1; T2 find 1 → 0 and new text 0 → 1.
- [ ] Task 4 — the gate and these records: the slot script is
  `~/gi-pricing-plan.local/scratch/sl1566/slot.sh` (head guard, preflight, reds by cause, breaks, the
  full two-half gate in one hold). Not run: no gate before the lead's "GATE GRANTED <head>".

Deviations from the plan, all disclosed:

1. **Item 12 is a unit test as well as an integration test.** The plan's integration item needs
   the engine to return a `float` `3.0`; FD-1561's probe shows it returns the Python `int` `27`
   for a whole value, so an integration test cannot reach the float path. Item 12's integration
   test uses `driver_age * 1.5` (whole `27`), and `test_integral_means_exact_equality_with_the_integer_part`
   drives `_coerce_output_value` with `3.0`, `-2.0`, `0.0` and `1e15` directly; the
   `isinstance` break (below) turns the float cases red.
2. **Extra tests beyond the plan's list:** non-finite floats, `bool`, strings and `None` under
   `int`/`count` are refused without the value (`NFR-499`); `relativity`/`percentage` equal the
   `decimal` form for the same value; a declared type the row does not name (`float`) is still
   refused, not stringified (`RL-923` §5(i)).
3. **The non-DB reds were not run at authoring time** (a gate slot was held by another seat, and
   the brief bars small tests beside it). They run in this slice's slot, by cause, against the base
   source swapped in (`slot.sh`), and their printed lines are recorded under Gate.

### Gate

Not run. Pending the lead's "GATE GRANTED <head>". The table is filled from
`~/gi-pricing-plan.local/scratch/sl1566/gatelogs/` when it runs.

### Audit

Not yet given.

### Build log

- 2026-10-11 — worktree `.claude/worktrees/sl-1566` from `origin/main` `d699a561`; `uv sync --all-packages`.
- 2026-10-11 — `74fb7b69` Task 1 tests (reds not yet run); `30fd08ac` Task 1 code.
- 2026-10-11 — `79031a66` Task 2 tests; `56eebd5a` Task 2 code; `cd3b5bcf` the spec text.
- 2026-10-11 — merged `origin/main` `02f23b4a` (SL-1600: `safe_error.py`, `model_schema/rating.py`;
  no overlap with `score.py`); `ruff check` and `mypy` (whole config) clean on the branch.

## PRs

None yet.
