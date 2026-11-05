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

- 2026-11-05 16:31 GMT (exec-sl8345f, to-lead "2026-11-05 16:24:09 GMT" (3); on e6d141ba, no re-merge). **`_format_value` exact and the precision read of the bulk transforms.**
  - **Red 387629a6** (`TestFormatValueIsExact`, test file `packages/pricing-core/tests/test_rate_table_bulk_ops.py`), by cause, log head=e6d141ba source: `4 failed, 3 passed, 84 deselected`, e.g. `assert '1234567890123456789012345679000000' == '1234567890123456789012345678901234.5678'` (the 38-digit value is rounded to 28 digits by the ambient context in `normalize()`). The 3 passes (`1E+40`, `0.000`, `0E+5`) are guards.
  - **Green b51638d0** (`operations.py` `_format_value` only: zero first, then `normalize(Context(prec=max(len(digits), 1), traps=[Inexact]))`): `test_rate_table_bulk_ops.py` 91 passed; `test_rate_table_operations.py` 60 passed; `test_rate_table_weights.py` 25 passed; `test_rating_score.py` 53 passed (pins `_CLEAN_WIRE_SHA256`); `ruff check .` rc=0. `ruff format --check` reports both files unformatted at the BASE too (pre-existing, untouched); mypy not run.
  - **Non-finite (a read, measured in a Python 3.12 shell):** `Infinity`/`-Infinity`/`NaN` pass through the same in the old and new form (`"Infinity"`, `"-Infinity"`, `"NaN"`); `sNaN` raised `InvalidOperation` before (ambient traps) and now returns `"NaN"` (the sized context traps only `Inexact`). `_validate_result` refuses a non-finite cell (`_value_issue`, `operations.py:325`) and the callers build `Decimal(row[...])` from stored text, so no op feeds one in. Zero: every zero now writes `"0"` (`-0` was `"-0"`); the callers skip `new == old`, so only `rebase_to_level` of a `0` cell by a negative reference could reach it, asserted nowhere.
  - **(1) The transforms** (read): `_transform_rows` (:722 at b51638d0, :714 at e6d141ba → caller `uplift_table` :757 `old * factor`; `floor_and_cap` :821 `max(floor, min(old, cap))`, no arithmetic); `uplift_by_filter` :789 (:781 at e6d141ba; `new = old * factor` at :785); `rebase_to_level` :864 (:856 at e6d141ba; quotient at :863: `Decimal(row[...]) / reference`, a quotient). `factor = Decimal(1) + percentage` at :756/:778. **Precision: the ambient context, always.** `grep -n "localcontext\|getcontext\|setcontext\|Context(\|quantize\|prec" operations.py` (before this change) found nothing; the only `localcontext` in `packages/pricing-core/src` is `rating/ladder.py` (6 uses), not on this path. No caller sets it, so it is Python's default, 28 significant digits. **Nothing is quantised.** `_format_value` only renders; so the old and the new form give identical text wherever the transform's own result is already ≤ 28 digits (it always is, at ambient 28).
  - **(2) Spec:** `grep -n -i -E "(decimal places|\bdp\b|round|quantis|quantiz|precision|significant digits)" docs/specs/03-rating-engine.md | grep -i -E "uplift|floor_and_cap|floor/cap|rebase|bulk"` and the same over `04-optimisation.md` return no line. FR-233 (03 line 126) says only "uplift a whole table by a percentage, uplift a subset by key filter, floor/cap values, and rebase to a chosen base level. Each records its parameters"; the §5.1 `bulk-operation` row (line 1101) says percentage, floor and cap are decimal strings. **No dp or rounding policy is stated for any op.**
  - **(3)/(4) Measured, not asserted** (`scratch/sl8345f/measure_precision.py`, head b51638d0 source with the old expression held in the script, ambient 28): a 29-digit cell `1234567890123456789012345.6789` through each op, old vs new `_format_value`, is **identical**: `uplift_table` and `uplift_by_filter` (50%) → `1851851835185185183518518.518` against the exact `...518.51835` (rounded to 28 digits by the **multiplication**, not by `_format_value`); `rebase` by 1.5 → `823045260082304526008230.4526` = exact; `floor_and_cap` keeps the text or writes floor/cap. The one op input where the old `_format_value` rounded on this path is a floor/cap wider than 28 digits: old `...678901234.5678` → `1234567890123456789012345679000000` refused as `RATE_TABLE_CELL_UNPARSEABLE`, new → the same refusal on the exact value. **Repeated × 1.0375 through `uplift_table` (percentage 0.0375, real op, ambient 28):** the exact product gains 4 digits a step (23 digits at step 5, 27 at step 6). From 0.1234: **step 7** is the first at which the mantissa reaches 28 digits and the first at which the stored text differs from the exact product (`0.1596731515941606426239013672` against exact `0.15967315159416064262390136718750`, 32 digits), and step 8 the same; from 1.0: step 7 `1.293947743874883651733398438` against `1.29394774387488365173339843750`. From **0.0123**: step 7 is **refused** by the op (`RATE_TABLE_CELL_UNPARSEABLE: value '0.01591555724966106891632080078'`: 29 decimal places; `cell_parses`, `rating/compile.py:820`, reads up to 29 digits and 28 dp, measured). Old and new `_format_value` give identical rows in all three series.
  - **A caller's ambient context moves the text:** a first draft of the measurement ran the op inside `localcontext(prec=400)` and the op stored `0.1596731515941606426239013671875` (exact) and was then refused, so the stored text is a function of the caller's context. Noted, not fixed.
  - **(5)** Draft finding: `scratch/sl8345f/fd-transform-precision.md`. No rounding rule invented: no quantize, no localcontext, no change to any transform.
  - **(6) Can a real cell get there? Yes, by repetition.** A realistic cell (0.1234) uplifted 7 times by 3.75% reaches a 28-digit rounded cell silently (no refusal, no note), and a cell below 0.1 is refused on the same step (a 7th 3.75% uplift of 0.0123). One rate change carrying 5+ decimal places, or 6–7 successive uplifts, is enough; the engine reads the rounded 28-digit text, so the rate it prices is the rounded one. This is the lead's to route: not softened, not fixed here.
  - **A16 (the clean-wire hash):** `test_rating_score.py::test_a_clean_table_has_a_byte_identical_wire` pins `eb5bac4364fe66f353fee30bc38337443a0f8f2519ebc63162e5216b5f229985` (`test_rating_score.py:1013`, same recipe as line A16): `53 passed` on b51638d0, the hash unchanged. `_format_value` is not on that path by a read: `to_wire` is `rating/runtime.py:561`; `grep -n "rate_table" rating/runtime.py` on the import lines returns nothing, and the only importer of `rate_tables.operations` under `pricing_core` outside the module is `rate_tables/weights.py:30` (the types `Cells`, `KeyTuple`), which `to_wire` does not call.

- 2026-11-05 GMT (exec-sl8345f, to-lead follow-up "Separate R2's refusal from the engine's limit"): **the wide-cell refusal is ZEN's, not R2's.** `scratch/sl8345f/measure_cell_parses_layers.py` runs the body of `cell_parses` before (the commit before 6291e196, c836b932) and after (6291e196 = e6d141ba): 29 integer digits and 0.+28 dp accepted, 30 digits and 0.+29 dp refused, identical in both bodies; the layer is `zen.evaluate_expression`: `RuntimeError: {"type":"parserError","source":"Incomplete parser output"}`. Over 28 candidate strings the two bodies differ only on `1+1`, `true`, `false` (accepted before, refused after: not decimal literals, R2's stated purpose). **No valid decimal literal accepted before is refused after R2's change.** Also measured: ZEN returns a float (`1.2222222222222222e+27` for the 28-digit integer, `0.1111111111111111` for 0.+28 dp), so the engine prices a 17-digit float of any wide accepted cell.

## PRs

(none: the slice ends unpushed; the lead pushes.)
