---
id: LG-8346
family: ledger
title: WK-1178 slice SL-8345 — FD-1648 limb (iii): a bad cell is a hard error, and a refusal says why (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05
owner: executor
tree: 8c823fc7           # sl-8345-r2-cell-hard-error head 5db73f7e this was written against (base 662867bb)
slice: SL-8345
phase: P2
work: WK-1178
plans: [PL-8321]
corrected_by: []
relates: [FD-1648, FD-1659, FD-1478, PL-8321, FR-255, FR-239]
---

# LG-8346 — WK-1178 slice SL-8345 (R2): a bad cell is a hard error, and a refusal says why

**GO:** to-lead "2026-11-05 11:39:12 GMT" (R2 now, branch from R1's gated-to-be head 662867bb, not its merge). FD 8354 added by "2026-11-05 11:16:36 GMT" (2).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

`PL-8321` R2 (SL 8345), items A12 to A18. Requirements: `03` FR-255 (clause first), FR-239 (the ruled dated clause, in the code's commit), NFR-489 (read only). FD-1648, FD-1659, FD-1478 close at the audit; FD 8354 (MEDIUM) rides this slice.

Write set: the plan's R2 write set, plus for FD 8354 `packages/pricing-core/src/pricing_core/modelling/predict.py` and `packages/pricing-core/tests/test_glm_scalar_predict.py`; and `backend/src/app/api/score.py` (`_PER_QUOTE_CODES` lives there).

### Task list

- **R2.0** FR-255 clause alone: `930e7bd4` (A13). R2.0's async premise: `evaluate` (sync) of the guarded decision from inside `score_one`'s running loop works with a real bundle's `customHandler` (T5/T7 green through `score_one`).
- **R2.1** reds T5, T6, T7, T12: `1359a77d`.
- **R2.2-R2.5** sentinel, post-evaluation check `_check_unparseable_cells`, guard nodes, `PurposeEvaluation.diagnose`, `_reraise_engine_failure(evaluation, context, exc)`, with the FR-239 clause: `2447be87`. Fix `62b9b4d7`: `CompiledBundle.diagnose`, since `evaluation_for`'s base fallback built a `PurposeEvaluation` with the no-op diagnose.
- **FD 8354**: red `3c2810e3`, green `bd494bb6` (`predict.py` `_row_frame`: a non-finite `Decimal` is carried as its float into the one-row frame; the one site both GLM scoring paths and the offset source reach).
- Test fixes `5db73f7e`: T5's pins validated; T12's constant filled; import order.

**A12, the existing-test changes (exactly three):** (1) `test_the_stated_residual_still_reports_the_miss_code` renamed `test_a_failure_in_a_step_consuming_a_table_is_not_a_miss`, inverted to `RATING_EVALUATION_FAILED` (FD-1478 orders it); (2) the four direct callers of `_reraise_engine_failure` (`test_rating_score.py` x3, `test_safe_error.py` x1) take `(evaluation, {}, exc)` with a stub `diagnose=lambda _: None`; (3) the `test_wf699_journey.py` comment. No assert removed. Additive: `_hand_compiled` gained `expense_rows`, `pins`, `extra_payloads` keywords; one `_check_unparseable_cells` line in `test_quote_input_raise_sites.py`'s count table.

**Departures and notes**
- T12's base hash is measured (below). T5's first red (`1359a77d`) was a fixture error (`Pins.model_copy` leaves strings); its red by cause is below, taken with the fixture fixed (`5db73f7e`) against the base source.
- FD 8354's frame-path reference in the test builds its own `pl.DataFrame`, so the `Decimal` case runs the scalar path only (the float case runs both).
- `test_rating_number.py`'s docstring still names the closed residual; it is outside the write set and not edited.
- `_PER_QUOTE_CODES` gains the code, so a bad cell is a 422 where `RATING_EVALUATION_FAILED` is not in that set (unchanged).
- **Process slip:** the first part of the session ran Bash calls opening with `cd <worktree>` against the brief's NO-CD ban; nothing outside the worktree was written. Thereafter `git -C` and absolute paths.

### Gate

(owed: the SOLO full gate, the lead's.) The `test_wf699_journey.py`, `test_score.py`, `test_score_compare.py`, `test_api_rate_tables.py` lane is not run here.

Runs through `run-heavy.sh --over-load "2026-11-05 13:58:21 GMT"`, load1 ~17-22, tree = worktree `sl-8345` (logs `/tmp/sl8345/`):
- `ruff check .` rc 0; `mypy` "Success: no issues found in 252 source files" rc 0; `lint-imports` "Contracts: 4 kept, 0 broken." rc 0. `ruff format --check` on the changed files reports reformatting, as the base's own copies of the same files do (not a regression).
- Head `5db73f7e` plus the edits committed after: test_rating_score 53 passed; test_safe_error 18 passed; test_quote_input_raise_sites 19 passed; test_glm_scalar_predict 36 passed, 4 skipped; test_rating_runtime 14 passed; test_rating_score_batch_outputs 55 passed.

### Audit

(the auditor's.)

### Build log

- **Red lines, by cause** (base source 662867bb, tests of `1359a77d`):
  - `9 failed, 44 passed in 18.82s` for T5, T6, T7 (3 cases + batch row), T12 (x2). T6 `test_a_failure_in_a_step_consuming_a_table_is_not_a_miss`: `RATE_TABLE_MISS` where `RATING_EVALUATION_FAILED` is expected. T7: `Actual message: "RATE_TABLE_MISS: the engine failed evaluating step 's_office' (FR-255); an on_miss='error' step it consumes most likely found no matching row"` for consumed; unconsumed and default_tolerant ended in a quote (no raise). T12: `'TO-BE-MEASUR...' != 'eb5bac43...'` (placeholder) and `('s_expense','r0','1.1','1.36E-7') != (..., '"__UNPARSEABLE_CELL__"')`.
  - T5 (fixture fixed): `1 failed, 1 passed`; the_lookup_missed: `RATE_TABLE_MISS: the engine failed evaluating step 's_office' ...` for a lookup miss (the_table_missed passes, as it must: the control).
  - FD 8354, base source: `1 failed, 1 passed, 38 deselected in 7.43s`; `pyo3_runtime.PanicException: called Result::unwrap() on an Err value: PyErr { type: <class 'TypeError'>, value: TypeError("'str' object cannot be interpreted as an integer") ...}` at `polars/_utils/construction/dataframe.py:719` (`PyDataFrame.from_dicts`), the float NaN case passing.
- **Green:** the runs under Gate. T12 is a guard, green at base.
- **A16:** `sha256(json.dumps(to_wire(graph, payloads), sort_keys=True))` for `_algorithm_payload()` with the `motor-expense` rows of `_rate_table_payload()`: base 662867bb source `eb5bac4364fe66f353fee30bc38337443a0f8f2519ebc63162e5216b5f229985` (the module path printed `/tmp/sl8345/base/...`), head source the same. A table with one bad cell differs in that cell's `o0` only (T12b).
- **A17 (a note, not an NFR reading):** `score_one` on the score fixture, 1000 calls per run, five runs, µs per call, load1 ~17-20 on an 8-vCPU box beside a gate: base 3628-4526 (min 3628) and 8833-12126; head 4289-9523 (min 4289) and 5784-7079. The noise exceeds the difference; the one addition is `_check_unparseable_cells`, a loop over the steps. Cell parse at load: `zen.evaluate_expression` ~1.1 µs a cell (the plan's RUN), not re-measured.
- Scripts: `/tmp/sl8345/`.

- 2026-11-05 16:19 GMT (exec-r2b, to-lead "2026-11-05 14:18:33 GMT" (2) and "16:14:12 GMT"; reachability not claimed): red a72dbe7e `decimal_snan` FAILED (`ValueError: cannot convert signaling NaN to float` at `_row_frame`; `Decimal('Infinity')`/`('-Infinity')` already passed), green d6d5ffa0 (`test_glm_scalar_predict.py` 39 passed, 4 skipped; ruff rc=0). Red c836b932 `[true]`,`[false]`,`[1+1]` FAILED (3 failed, 3 passed), green: `test_rating_compile_fr240.py` 31 passed, `test_rating_score.py` 53 passed (pinned clean-wire sha `eb5bac43...` unchanged), `test_rate_table_bulk_ops.py` 84 passed, ruff rc=0, mypy rc=0. `1_000` still reads (`Decimal('1_000')` accepts it): no ruling needed.

## PRs

(none: the slice ends unpushed; the lead pushes.)
