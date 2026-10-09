---
id: LG-9449
family: ledger
title: WK-1178 slice SL-1463 — FD-1458, a GLM scores through model_call (PL-1464), slice ledger
status: active
created: 2026-10-10
owner: executor
tree: f03792056c347429d0c2278cdbcec6208ee58921
phase: P2
work: WK-1178
slice: SL-1463
plans: [PL-1464]
corrected_by: []
relates: [PL-1464, FD-1458, RL-1263, FR-222, FR-193, FR-255, FR-239, NFR-489, NFR-491, WK-1178]
---

# LG-9449 — WK-1178 slice SL-1463: FD-1458, a GLM scores through `model_call`

**GO:** not yet given. Authoring ahead of the GO at the user's order ("2026-10-10 00:10:36 BST — USER: more than 10% of the weekly allowance is left … USE IT, up to 6 seats …", item A.5, in `to-lead.md`, a local file): code and tests are written on a branch from A-1's pushed head `f03792056c347429d0c2278cdbcec6208ee58921`; only small tests run (one file, no database), nothing merges before the GO, the full gate and the MERGE-ACK.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `SL-1463` in `docs/roadmap.md` (WK-1178, Option A, A-2). Its scope is `PL-1464` §"Scope" and §"Write set, and its contention", read at this branch's tree. Ruling record: the dated notes inside `PL-1464` (DP-1 to DP-5).

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1464`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1463`'s roadmap row at its head.

Write set: `PL-1464` §"Write set" only. Any other path is a stop to the lead.

**Serial after A-1.** This branch is cut from A-1's head (which sits on S4's head); the resolver is `WorkspaceResolver`, re-anchored by symbol.

### Task list

Order and acceptance checks are `PL-1464` §"Tasks" and §"Acceptance Standard". Each task below is added with its commit when it is pushed.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no heavy run during the authoring phase; the gate runs after the lead's "gate slot granted" for the head) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-10, authoring phase.** Branch `sl-1463-a2-glm-model-call`, from `f03792056c347429d0c2278cdbcec6208ee58921`. Stamps are BST.

- Commit 1: `PL-1464`'s `status:` line `draft` to `active` and this file (`99f511d8`).
- **Task 1b (helper, item 20), 2026-10-10.** `required_model_inputs` in `pricing_core/modelling/factors.py` (`d33ee7bb`). RED: `flock -w 300 /tmp/slots/small-test -c "nice -n 19 timeout 150 uv run --directory <wt> pytest -q packages/pricing-core/tests/test_factor_resolution.py -k required_model_inputs"` rc 2, `ImportError: cannot import name 'required_model_inputs'`. GREEN: same file, 16 passed.
- **Task 1 reds (items 1, 4, 12, 14, 15), `d0807c50`.** New `packages/pricing-core/tests/test_rating_glm_model_call.py` (a real `fit_glm` GLM: banded numeric Factor, grouped categorical Factor, `log_column` offset; fake resolver as the backend resolver serves it). RED: 7 failed, 1 passed: `MODEL_CALL_FAILED: … predict_glm has no such fallback`; `KeyError: 'factor:age_band@1'`; `assert 0.01 < 0`.
- **Shape (items 15 to 17), `36d7f940`.** `RatingModelCallStep.result_type` (`decimal` default; `decimal` or `money_minor` only, naming FR-227); three model-schema tests; the three sub-graph schemas regenerated. RED (field reverted): `AttributeError: 'RatingModelCallStep' object has no attribute 'result_type'`; `Extra inputs are not permitted`. GREEN: 17 passed. **`docs/contracts/openapi/generated.json` is NOT regenerated**: this branch's base (S4 + A-1) already carries about 4300 lines of unregenerated openapi drift, so regenerating here would fold S4's drift into this slice. Owed at the merge tree: `uv run python scripts/generate-contracts.py`. The untracked `dislocation-run.schema.json` the generator also wrote is S4's and was not committed.
- **Tasks 3 and 4 (compile carries, runtime scores), `501de165`.** `ResolvedArtifact` gains `bandings`, `groupings`, `offset_source`; `compile_bundle` writes a GLM pin's Factors, Bandings, Groupings (and a model-offset source) under their own refs, none for a GBM; `runtime.py` rebuilds a `_GlmScorer` per GLM pin once in `load_bundle` (`_load_glm_scorers`) and calls `predict_glm` per quote; the value is the unrounded prediction for GBM and GLM (item 15). GREEN: 8 passed.
- **Items 2, 3 (flips), `8408cb25`.** `test_a_glm_model_call_scores` (was `…_is_refused_with_a_named_code`); the FR-255 vehicle is a `log_column` offset the `feature_map` does not supply, matching `MODEL_CALL_FAILED.*MODEL_OFFSET_MISSING`. RED against the base `runtime.py`/`compile.py` (`git checkout f0379205 -- …`, restored): `assert '$model_call_error' not in {…predict_glm has no such fallback…}`; `Regex pattern did not match … Actual message: "MODEL_CALL_FAILED: … predict_glm has no such fallback…"`. GREEN: 12 and 40 passed. Old and new assertions: the first asserted the sentinel present and `"MODEL_CALL_FAILED"` in it; it now asserts the sentinel absent and the value equal to `predict_glm`. The shared fixtures moved to `age_glm` (gamma severity, no offset; Poisson with an offset when one is given).
- **Items 6, 7, 8, `41b02a06`.** Model-offset test (source model under its own ref, value equals the residual `predict_glm` with the source's linear predictor as `model_offset`); the NFR-491 socket guard repeated with a GLM pin; `score.py` module docstring item 2 rewritten. RED vs the base runtime/compile: `assert 'model:motor-freq-glm@1' in {…}` and `CodedError: MODEL_CALL_FAILED: …`. GREEN: 9 and 41 passed. Item 8: `git grep -n "predict_glm has no such fallback" -- packages backend` prints nothing (0 lines).
- **Task 2 and the save check (items 13, 18, 19 code), `6f8daf67`.** `WorkspaceResolver.resolve`'s `model` branch loads Bandings and Groupings and, for `offset.kind == "model"`, the source via `resolve_offset_model`; `check_model_call_feature_maps` in `rating_algorithms.py` is called by `create_algorithm`, `create_sub_graph` and `create_version`; `MODEL_CALL_FEATURE_MAP_INVALID` is in `RATING_ERROR_CODES`. A model-offset source's own required inputs are also accepted (DP-3 (a): the source's inputs come through the `feature_map`).
- **Backend tests, `033ecd8d`.** `backend/tests/test_rating_glm_model_call.py` (items 5, 6), appended to `test_rating_algorithms.py` (items 13, 16, 21) and `test_sub_graphs_api.py` (items 18, 19). **Authored, not run**: every one needs Postgres, which the small-test rule bars. They collect (56 tests) and `ruff` is clean; `test_required_model_inputs_is_defined_once` passes. **Red-by-cause is owed for all of them** at the first gate-slot window.
- **Task 6 (spec texts), `912fd81a`.** `03` FR-222 and FR-227 rows and the owned-codes tail carry T1, T2, T3 (dated 2026-10-10). `audit-docs` owed.
- **Task 5 (bench), `9532fbd4`.** `scripts/bench-rating.py` gains the GLM scenario (`--glm` is not a flag: it always runs after the no-GBM block). Smoke only (compile and `score_one` once, outcome `quoted`). **The NFR-489 measurement is owed**: it runs alone on the VM after the lead's grant.
- **Item 15 type check and single rounding, `12726abe`.** `producer_types` types a `model_call` by `result_type`; `model_call_money_issues` refuses a `money_minor` `model_call` value feeding an output declared other than `decimal` or `money_minor` (`validate_algorithm` and the sub-graph fragment check); `_compatible` is not edited. RED vs the previous compile: `assert [] == ['RATING_TYPE_MISMATCH']`. GREEN: 16 passed.

### Deviations and open items

1. **Item 15, engine precision.** The ZEN engine carries a handler's float at 15 significant digits (`0.058819825927370374` returns `0.0588198259273704`); a `str` value cannot enter `v * 2`. No form crosses bit-exactly, so the golden asserts 1e-14 relative. Reported to the lead.
2. **Four existing tests outside the write set fail under the plan's own item 15** (reported, not touched, awaiting the lead): `test_rating_wire_order.py::test_the_bundle_hash_is_unchanged` (the defaulted `result_type` enters `to_jdm`'s dump and changes every hash; recommended fix: `to_jdm` omits it when it is the default), `test_rating_ladder_exact.py` (2 tests, 1435 against 1436) and `test_rating_dislocation.py::test_dislocation_frame_origin_rung_is_the_first_differing_rung`. Each passes with `round(prediction)` restored in the handler.
3. Item 1 and 14 use `compiled.decision.async_evaluate`, not `score_one`, for the step value: the ladder rounds money rungs, and the golden compares the step's own value.
4. Load discipline: ten rating test files were run in one loop with the box above load 4.0 (5.5 to 9.0, other seats' work); each ran niced under the small-test flock. The later failing files were re-run at load 3.8.

### Owed after the authoring phase

Red-by-cause for every backend test; `mypy`, `lint-imports`, `audit-docs`, the full gate; regeneration of `docs/contracts/openapi/generated.json` and `pnpm --dir frontend generate:api`; item 9 (the NFR-489 measurement, alone on the VM); the lead's rulings on deviations 1 and 2; the `SL-1463` roadmap row and this ledger close at the mint step.

## PRs
