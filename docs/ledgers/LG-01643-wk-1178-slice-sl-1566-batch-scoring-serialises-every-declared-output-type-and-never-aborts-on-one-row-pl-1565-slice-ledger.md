---
id: LG-1643
family: ledger
title: WK-1178 slice SL-1566 — batch scoring serialises every declared output type and never aborts on one row (PL-1565), slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-11            # original date 2026-10-11, set at the draft; minted 2026-10-11
owner: executor
tree: 02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a
phase: P2
work: WK-1178
slice: SL-1566
plans: [PL-1565]
corrected_by: []
relates: [FD-1561, RL-1567, RL-1343, RL-923, FD-1333, SL-1569, FR-214, FR-254, FR-255, NFR-499]
---

# LG-1643 — WK-1178 slice SL-1566: batch serialises every declared output type

Executed by `executor-sl1566` from PL-1565 (a leaf plan; WK-1178 has no Work plan, so L5's
one-plan-per-Work reads as PL-1565 itself). Authored on branch `sl-1566-wk1178-batch-serialise`,
cut from `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7` and merged with `origin/main`
`02f23b4a74cfdf81ff4ac875e1ff7ab2db777c4a` (SL-1600). Times are BST (`TZ=Europe/London date`).

**GO:** `to-lead.md` "2026-10-11 11:45:03 BST — WK-1178 tail: GO SL-1566; SL-1563 write-set (a) YES; SL-1517 fold YES, DP-6 → the decision-maker; ONE delta PL 9813; SL-1569 last" (the maintainer, by delegation), item 1; activation record `from-lead-2026-10-09.md` "2026-10-11 11:45:36 BST — Lead: DISPATCH SL-1566 (PL-1565, WK-1178, FD-1561) — activation record; GO per the maintainer's "2026-10-11 11:4x BST — WK-1178 tail …" item 1". The GO arrived after the authoring commits were pushed (4ec75c85), so the activation is this ledger's later commit, not its first.
**MERGE-ACK:** added at merge.

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
- [x] Task 4 — the gate and these records. Full two-half gate at `f13f606a` (Gate, below): one OWN red, fixed by the widening in deviation 4; the targeted re-gate at `5dac9dff` is green (Gate, below). The slot scripts are `~/gi-pricing-plan.local/scratch/sl1566/slot.sh` and `slot-targeted.sh`.

Deviations from the plan, all disclosed:

1. **Item 12 is a unit test as well as an integration test.** The plan's integration item needs
   the engine to return a `float` `3.0`; FD-1561's probe shows it returns the Python `int` `27`
   for a whole value, so an integration test cannot reach the float path. FD-1561's probe, quoted: `[relativity] REALTIME wire outputs = {"payable_premium_minor": 1507, "probe_out": 27}   probe_out JSON type = int` (expr `driver_age * 1.5`, whole), and `[decimal] ... "probe_out": 19.8 ... JSON type = float` (expr `driver_age * 1.1`). The lead accepted this deviation (message of 2026-10-11, after the activation) and discloses it at the ACK. Item 12's integration
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
4. **Widening of PL-1565 item 11 (the lead's, from-lead "2026-10-11 21:57:43 BST", option A):** one file,
   `backend/tests/test_error_sinks.py`, the `_SINKS` rows only. Task 1 extracted `_batch_error_row`, so the
   NFR-499 sink census saw `_score_batch_row` at 1 (was 2) and `_batch_error_row` at 1 (new). Red first:
   `uv run pytest backend/tests/test_error_sinks.py` at `f13f606a` printed `1 failed, 6 passed`, differing items
   `(…score.py, _score_batch_row, error_message key): 1 != 2` and `(…, _batch_error_row, …): 1` extra. After the
   edit (a `_batch_error_row` row at 1, `_score_batch_row` at 1, each with its reason; the new one cites
   `test_an_error_row_from_serialisation_carries_no_value`, SENTINEL-9513 not in error_message): `7 passed`.
   **The maintainer's (by delegation) two conditions** (`to-lead.md` "2026-10-11 21:58:07 BST", relayed by the lead): (1) *the census total is unchanged*: one row moves and none is added. Before (`f13f606a`) → after: `(…/rating/score.py, _score_batch_row, "error_message key")` 2 → 1; `(…/rating/score.py, _batch_error_row, "error_message key")` absent (0) → 1; the `_SINKS` total over all rows, and the `error_message key` total in `score.py`, is the same before and after (the second row's +1 is the first's −1). No sink was added: the count of `{"error_message": …}` dict keys in `score.py` is 2 at the base `02f23b4a` (`_score_batch_row`'s error dict and its success dict) and 2 at `f13f606a` and now (`_batch_error_row`'s and the success dict); the evidence is Task 1's sentinel test, `test_an_error_row_from_serialisation_carries_no_value` (`SENTINEL-9513` not in `error_message`). A changed count would be a new sink and a stop to the lead. (2) *the targeted re-gate holds only if* `git diff --stat f13f606a..<head>` touches only `backend/tests/test_error_sinks.py` plus this ledger; INDEX, roadmap and every mint-turn file stay out.

### Gate

Full two-half gate, one hold of gate-1, `slot.sh` (sources `handover/slot-preflight.sh`), HEAD `f13f606add187e9dc7192d13aa9a5c376be9351d`,
tree `2440428566746a243e62a2bf32be180616a2d0db`, 21:11:55 → 21:56:35 BST. Logs: `~/gi-pricing-plan.local/scratch/sl1566/gatelogs/`, `slot.out`.

| stage | rc | reading |
|---|---|---|
| red_t1_pricing_core | 1 | RED by cause: the injected `ValueError`/`TypeError`/`KeyError`/`SENTINEL-9513` raised out of `score_batch` (base `score.py`), not an assertion |
| red_t1_backend | 1 | RED by cause: `ValueError: injected serialisation failure` out of the handler (item 4) |
| red_t2 | 1 | RED by cause: `assert 'ValueError' is None` (the type refusal, with Task 1's code only) |
| green_new, green_backend, green_item9 | 0 | items 1–8, 12, 13; item 4 (DB); item 9 unchanged |
| break_item3_catch_notimplemented | 1 | `DID NOT RAISE NotImplementedError` |
| break_no_integrality_check | 1 | `'quoted' == 'error'` |
| break_isinstance_instead | 1 | `3.0` refused: "a int output must be integral, got float" |
| break_tolerance | 1 | `'quoted' == 'error'` and `DID NOT RAISE ValueError` |
| ruff, mypy, import_linter, req_coverage, contracts | 0 | |
| pytest | 1 | 14 failed / 5644 passed (41:26): 13 are the audit-on-tree modules (`tests/test_audit_docs_*`, `test_doc_index`, `test_register_lint`, `test_register_owed`, `test_repository_invariants`), the same set as SL-1600's gate; **1 OWN**, `test_error_sinks.py` (deviation 4) |
| audit_docs | 1 | `FAILED (1)`: check 31, gap in the allocation between 1636 and 9816 = the then-unminted working id LG 9816, minted as LG-1643 (mint artefact); the check-35 stamp lines and the rest are the disclosed non-fatal population, none in this slice's files |
| fe_install, fe_generate, fe_lint, fe_typecheck, fe_build | 0 | |
| fe_test | 1 | 688/689; `DagDesigner.test.ts` "emits an edited draft…" (WK-675's, rule 6). Alone ×1 on this head under the small-test flock: 4 passed of 4 |

Barred-word added lines: 0.

Targeted re-gate after the widening (the lead's form, from-lead "2026-10-11 21:57:43 BST"; grant "2026-10-11 21:59:49 BST"): `~/gi-pricing-plan.local/scratch/sl1566/slot-targeted.sh`, HEAD `5dac9dff6ccd2bf395ed602843ef74f6a7d55d9f`, 22:44:11 → 22:44:50 BST, `end … rc=0`; logs `gatelogs-targeted/`, `slot-targeted.out`. `git diff --stat f13f606a..5dac9dff` touched only `backend/tests/test_error_sinks.py` and this ledger (the maintainer's (by delegation) condition 2, `to-lead.md` "2026-10-11 21:58:07 BST").

| stage | rc | reading |
|---|---|---|
| error_sinks | 0 | `backend/tests/test_error_sinks.py`: 7 passed; the census is green with the moved row, total unchanged |
| item4_backend | 0 | `backend/tests/test_scoring_handlers.py -k serialisation_raises` (DB): 1 passed |
| batch_outputs | 0 | `test_rating_score_batch_outputs.py`: 53 passed |
| batch_item9 | 0 | `test_rating_score_batch.py`: 11 passed (item 9, unchanged) |
| mypy | 0 | Success, no issues in 236 source files |
| ruff | 0 | `ruff check .`: all checks passed |

The full gate's other stages are carried from `f13f606a`, the targeted diff touching no source they cover.

### Audit

Not yet given.

Lead verdict: (pending)

### Build log

- 2026-10-11 — worktree `.claude/worktrees/sl-1566` from `origin/main` `d699a561`; `uv sync --all-packages`.
- 2026-10-11 — `74fb7b69` Task 1 tests (reds not yet run); `30fd08ac` Task 1 code.
- 2026-10-11 — `79031a66` Task 2 tests; `56eebd5a` Task 2 code; `cd3b5bcf` the spec text.
- 2026-10-11 — merged `origin/main` `02f23b4a` (SL-1600: `safe_error.py`, `model_schema/rating.py`;
  no overlap with `score.py`); `ruff check` and `mypy` (whole config) clean on the branch.
- 2026-10-11 — re-seat: merged `origin/main` `372fa92a` (`docs/INDEX.md` the only conflict, regenerated by `scripts/doc-index.py`; `score.py` and the batch path untouched by main since `02f23b4a`, so Task 1–3 stand as written). Targeted proof via `run-small.sh`: `test_rating_score_batch_outputs.py` + `test_rating_score_batch.py` 64 passed; `ruff` on the three touched files clean; whole-config `mypy` 0 issues in 236 files. `slot.sh` re-templated to source `handover/slot-preflight.sh` (serial gate, per-stage START/END); wrong head exits 90.
- 2026-10-11 — gate at `f13f606a` (above); OWN red fixed by the lead-named widening (deviation 4).
- 2026-10-11 — targeted re-gate at `5dac9dff` green (Gate). Mint turn (from-lead "2026-10-11 22:45:46 BST"): merged `origin/main` `4af5997e` (`docs/INDEX.md` the only conflict, regenerated by `scripts/doc-index.py`); LG 9816 minted as LG-1643; this ledger and the SL-1566 row closed. PL-1565 stays `active`, as PL-1535 did after SL-1536 closed.

## PRs

#1286 — `SL-1566: batch scoring serialises every declared output type and never aborts on one row (LG-1643)`, branch `sl-1566-wk1178-batch-serialise`. Merge order: SL-1503 (LG-1642) first.
