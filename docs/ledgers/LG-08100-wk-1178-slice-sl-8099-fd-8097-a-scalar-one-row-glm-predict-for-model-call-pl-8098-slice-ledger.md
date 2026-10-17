---
id: LG-8100
family: ledger
title: WK-1178 slice SL-8099 — FD 8097, a scalar one-row GLM predict for model_call, bit-identical to the polars path (PL-8098), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-17
owner: executor
tree: c62f1ff67b45022fde947ff67cd01be5ffe89fc5
phase: P2
work: WK-1178
slice: SL-8099
plans: [PL-8098]
corrected_by: []
relates: [PL-8098, SL-8099, FD-8097, FR-193, FR-222]
---

# LG-8100 — WK-1178 slice SL-8099: the scalar one-row GLM predict

**GO:** the maintainer's "plan + GO now" (~20:48 BST 2026-10-17, ruling item 2), relayed in the lead's brief `brief-executor-8099-2026-10-17.md` (2026-10-17 20:54:33 BST).
**MERGE-ACK:** not yet given.

## Tasks

Branch `sl-8099-glm-scalar-predict` (local) pushed to `pl-8098-glm-scalar-predict-2026-10-17`, worktree `.claude/worktrees/sl-8099`, cut from `c62f1ff67b45022fde947ff67cd01be5ffe89fc5`. Row: `SL-8099` in `docs/roadmap.md`. Plan: `PL-8098`.

| Task | What | Status |
|---|---|---|
| T1 | Red first: the parity test and a scalar entry point that raises `NotImplementedError` | done, `08bfad42` |
| T2 | The scalar path, exact equality | done |
| T3 | The wiring in `_GlmScorer`, the wiring test (the load-time choice is moot, see Deviations) | done |
| T4 | The diagnostic timing (ms/quote, both paths) | done |
| T5 | Census re-run and the gate (the lead's grant) | census done; gate owed (the lead's grant) |

## Build log

- **T1 red (acceptance iii).** Commit `08bfad4261a1b095bd2f3820b6db38cd182a5c5b`, tree `4c0ac372d4a387c97ee33047bd9b91338f966220`. `run-small.sh <wt> packages/pricing-core/tests/test_glm_scalar_predict.py`: rc 1, `28 failed in 10.14s`; every one of the 28 fails on `E       NotImplementedError` (`grep "^E  " | sort | uniq -c` gives `28 E       NotImplementedError`, nothing else). First FAILED line: `FAILED packages/pricing-core/tests/test_glm_scalar_predict.py::test_every_factor_kind_scores_bit_identically[0]`. The demo fixture (the demo GLM fitted in-process with no database, from `examples/fremtpl2/data`) built and ran to the stub, so the goldens and the 19 985 seed rows are reachable without a DB.
- **Design.** `resolve_factors` is split: `resolve_factor_columns` (the one resolution and every refusal; returns what the factors add) and the append of those columns to the frame. `predict.py`'s coefficient walk is `_design_columns`, the sum `_accumulate`; `linear_predictor` and `linear_predictor_row` call the same two and the same `_offset`; `predict_glm_row` inverts with `_inverse_link` on the shape-(1,) array. `_GlmScorer.predict` and its `offset_source` call the scalar path. Because the scalar path reads the frame path's own resolution there is no second banding or grouping rule.
- **Deviation 1: no load-time choice (PL-8098 constraint 5).** The scalar path has no factor logic of its own, so no kind is uncovered: a kind `resolve_factor_columns` refuses (`spline`, `polynomial`, `offset`, `expression` on this base) is refused identically on both paths; `test_a_factor_kind_the_resolver_refuses_is_refused_identically_on_both_paths` holds that. SL-1274's `expression` kind lands in `resolve_factor_columns`, so the scalar path inherits it; whichever of the two merges second adds parity cases for it, not a list.
- **Deviation 2: `apply_grouping` is touched (`modelling/groupings.py`).** The first scalar path (resolution only) measured **no faster** on this loaded box (`synthetic frame 6.2 ms, scalar 7.3 ms`): cProfile put 4 lazy `collect`s per quote in `apply_grouping` (`Series.unique`, `Series.replace_strict`, two groupings). `apply_grouping` now reads a single value directly and a column through `unique` + `replace_strict`, both from one new `_targets` (the unseen-level rule, one statement). Old against new: `diffgroup.py` (scratch) ran `apply_grouping` from `HEAD` `c62f1ff6` and from this tree on 1 401 random series (0, 1, 2 or 5 values over strings, ints, floats, bool, null; the three unseen-level behaviours): identical result or identical refusal text on all 1 401. `test_a_grouping_maps_one_value_exactly_as_it_maps_a_column` keeps the single/column equality. Tests of `groupings.py` itself (`test_groupings*.py`) were not run: outside the brief's three files, the lead's OK is needed.
- **Also shared:** `_design_columns` casts a factor's column to text once per call, not once per dummy (a pure saving, same values).
- **Negative control for the wiring test.** `runtime.py` reverted to `HEAD` with the test file kept: `2 failed, 33 passed` (`test_a_model_call_scores_without_the_frame_resolution`, `test_a_model_offset_scorer_scores_without_the_frame_resolution`); restored, all pass.
- **Final small runs** (tree = `de424206cba7efcad37da8a4da06a3a384b240a0` plus this commit's uncommitted edits), one file each: `test_glm_scalar_predict.py` rc 0 `37 passed in 201.35s`; `test_rating_peril_scoring.py` rc 0 `25 passed in 5.63s`; `test_quote_input_raise_sites.py` rc 0 `19 passed in 6.77s`. `ruff check` (5 touched files) rc 0; `mypy` rc 0 (`no issues found in 240 source files`); `lint-imports` rc 0 (`4 kept, 0 broken`). `ruff format --check` is rc 1 on all 5 files, and also on the same files at `HEAD` before this slice (the repo does not hold these files to the formatter); no reformat was applied.
- **Parity (acceptance i).** `float.hex` equality (so `-0.0` != `0.0`, NaN == NaN), against the production reference (`pl.DataFrame([row])` through `predict_glm`): 3 demo goldens (`demo_golden_cases` with the in-process fit), **all 19 985 seed portfolio rows** (`PORTFOLIO_VALIDATED_ROWS`), 6 synthetic quotes over identity (continuous and categorical), banding, grouping and interaction factors (incl. int inputs, a clamped out-of-range value, a null on a null-level banding, an unseen grouping level mapped to default), 16 link x offset cases (`log, identity, logit, inverse` x `none, column, log_column, model`). Refusals with equal code on both paths: `MODEL_TERM_UNRESOLVED` (x2), `MODEL_OFFSET_MISSING` (missing column, non-positive exposure, model offset absent), `MODEL_LINK_UNSUPPORTED`, `MODEL_CALL_FEATURE_COLLISION` (scorer), and equal `FactorResolutionError` text for a missing source column and an unseen level under `error`. The reference is a one-row frame, not a batch: a batch `np.exp` may use other SIMD lanes than a shape-(1,) one.
- **Timing (acceptance ii), nothing asserted.** Box: `nproc=8`, load1 4 to 8 from other seats' work, so these are for reading, not comparing across runs. `scratch/timing3.py` (synthetic world, 1 000 quotes, three columns; baseline = `HEAD`'s `apply_grouping` put back for the frame path): `POLARS_MAX_THREADS` unset: baseline frame 4.07 ms/quote, frame path now 1.11, scalar 0.63 (6.5x vs baseline); earlier runs of the same script: 3.92/1.20/0.65 (6.0x), 4.12/1.39/0.64 (6.4x), 4.69/1.33/0.56 (8.4x), 5.15/1.36/0.57 (9.0x). **(C) `POLARS_MAX_THREADS=1`, as data only:** baseline 2.27, frame now 1.01, scalar 0.54 (4.2x). In-test print (`test_print_the_per_quote_cost_of_both_paths`, load1 4.0 and 5.3), the seed portfolio's demo GLM (no grouping, so its frame column is the same code as the baseline's): frame 3.94 ms/quote, scalar 1.97 (2.0x) over 19 985 quotes; other runs of that print gave 3.05/2.85 (load1 20), 2.26/1.36 (load1 5). The demo GLM scores ~40 level indicators, one polars `==` each; the scalar path leaves those (replacing them with Python comparisons would be a second implementation of the level test, and null handling would have to be re-proved). FD 8097's 16.9 ms was a loaded-box sample (main 2.0 ms): this slice removes the grouping `collect`s and the per-call `with_columns`; the residual is the per-term polars calls.
- **Census (iv)** at `origin/main` `9469721d` (unmoved), predicate verbatim from PL-8098, each branch read at `origin/<branch>`: SL-1274 `bba2e0ae` overlaps `factors.py` (+151), `bandings.py` (+113), `runtime.py` (23 lines), as the plan found; SL-1341 `f269c5ca` overlaps `runtime.py` (75); SL-1543 now `281afb5d` (plan: `4c948c8a`), none of `runtime.py`, `predict.py`, `factors.py`, `groupings.py`; SL-1547 and SL-1258 none. **New:** none of the five touches `groupings.py` (this slice's added file). SL-1274 is the one to resolve: both change `resolve_factors`' body (it moves into `resolve_factor_columns` here).
- **Gate-2 docs block** (under `flock -w 900 /tmp/slots/gate-2`, tree = this branch's head before this line): `doc-index.py` rc 0 and `--check` rc 0 (`OK (byte-stable)`); `register-lint.py` rc 0 (`OK (0 violations)`); `audit-docs.py` rc 1, which is the unminted-id state plus a base that is red already: by check, this tree `2:5 5:5 30:71 31:1 32:246 35:27 36:497`; the planner's tree `pl-8098` @`c62f1ff6` (same base, plan only) `2:5 5:5 30:71 31:1 32:245 35:27 36:497`. The one difference is this ledger's `FD-8097 does not resolve in docs/INDEX.md` (check 32); check 31 is `gap in the full allocation between 1771 and 8098` on both. Check 37 (the ledger's missing `PRs` section) was red on the first run and is fixed.

## PRs

PR number and merge commit: filled at the PR open and the merge (the lead opens and merges).
