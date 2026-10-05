---
id: PL-9597
family: plan
kind: leaf
title: WK-1178 — Option A slice A-2, the FD 9605 fix, a GLM scores through model_call (FR-222, FR-193, FR-255, FR-239, NFR-489, NFR-491): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: planner
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-873, RL-874, RL-1263, PL-1371, CR-1212]
---

# PL 9597 (working id) — WK-1178: Option A slice A-2, the FD 9605 fix: a GLM scores through `model_call`, leaf plan

Filed under working id 9597 (this plan) and slice working id 9598 (its `SL-` row under
WK-1178 in [`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead in
`~/gi-pricing-plan.local/handover/eta.md` (rows "SL 9598 / PL 9597", 5 Oct 16:46:27). **The
`SL 9598` row is carried by A-1's plan PR** (PL 9599, working id, branch
`pl-9599-a1-peril-approval`), as the lead's brief orders ("the rows in the first"); this PR
adds the plan only. Nothing here is minted.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `python-package` (`pricing-core` stays standalone),
> `spec-change` (Task 6, only where the ruling carries text), `dev-commands` (the two-half
> gate; the benchmark's load-contention trap) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

A Rating Version whose `model_call` step pins an approved **GLM** scores: the step's value
equals `predict_glm` on the quote's row. Today `_model_call_handler`'s `else:` branch
(`packages/pricing-core/src/pricing_core/rating/runtime.py:568-579`) refuses every GLM,
because `Bundle.resolved_payloads` carries the Model's own dump and not the `Factor`,
`Banding` and `Grouping` versions `predict_glm` needs (`ModelSpecCommon.factors` holds bare
UUIDs). Compile now carries those versions inside the Bundle, and the runtime rebuilds
them once per loaded bundle and calls `predict_glm` per quote. This discharges FD 9605
(#1172) under its remedy (a), "Build it", which the maintainer chose by taking Option A.

**Architecture:** the backend resolver already knows how to load a GLM's inputs:
`prediction.py` loads them for `/predict` (`backend/src/app/platform/prediction.py:130-140`:
`model_service.load_factors`, `transform_service.load_bandings`,
`transform_service.load_groupings`). PL 9649's slice adds `factors: tuple[Factor, ...] = ()`
to `ResolvedArtifact` (`compile.py:434`) and fills it in `_Resolver.resolve`'s `model`
branch, read at compile and **not** carried into the Bundle (PL 9649 Task 3b Step 3). This
slice adds the Bandings and Groupings beside it and, for a GLM `model_call` pin, writes all
three into `resolved_payloads` under each artifact's own `ArtifactRef` (DP-1 (a)).
`factor`, `banding` and `grouping` are already `ARTIFACT_TYPES`
(`packages/model-schema/src/model_schema/refs.py:21-25`), and each shape is the
`model-schema` class's own dump (`Factor`, `Banding`, `Grouping`,
`model_schema/modelling.py:122`, `:339`, `:497`). `_model_call_handler`'s outer scope, which
`load_bundle` calls once, rebuilds each GLM pin's `GlmFitResult`, `GlmSpec`, Factors,
Bandings and Groupings; the per-request closure builds a one-row Polars frame and calls
`predict_glm` (`modelling/predict.py:230`). `load_bundle` itself is not edited.

**Tech Stack:** Python 3.12, Pydantic v2, Polars, NumPy, the `zen` engine binding, pytest;
the backend resolver under SQLAlchemy 2 async.

**Spec, finding and decision:**
- FD 9605 (working id; #1172 @`dee1a85c`),
  `docs/findings/FD-09605-a-glm-model-call-is-refused-at-score-though-fr-222-and-fr-193-say-any-model-scores.md`
  on that branch, §"Disposition", remedy **(a) Build it**: *"Compile embeds each pinned
  GLM's `Factor`, `Banding` and `Grouping` versions in `Bundle.resolved_payloads`; the
  runtime rebuilds them and calls `predict_glm`. Red first: a golden test that the
  `model_call` value equals `predict_glm` on the same row; `test_rating_runtime.py:377`
  flips."* **That remedy is this slice's scope.**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) FR-222 (`03:108`, *"`exact`
  invokes the model itself"*), FR-239, FR-255 (`03:167`), NFR-489 (`03:1330`), NFR-491
  (`03:1332`, *"A compiled bundle scores with **zero** database or network access;
  everything it needs is inside it"*);
- [`../specs/02-modelling.md`](../specs/02-modelling.md) FR-193 (`02:304`, *"`pricing-core`
  can score any persisted Model from its declarative artifact alone"*), FR-116 (the model
  offset).

## The maintainer's decisions this plan rests on, quoted

From `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed *"2026-10-05 16:43:31
BST — THE MAINTAINER'S DECISION (asked live): G2 takes OPTION A, WF-699's literal Peril
Structure path is BUILT IN P2; and the FD 9605 approval, now on the record"*, read in full
by this planner. Verbatim:

> 1. Four serial build slices under WK-1178, as sized: A-1 FD 9995 in full (the peril approval carry plus the _Resolver peril branch; it flips PL 9683's Acceptance 7); A-2 GLM via model_call (FD 9605); A-3 Peril Structure scoring (compile resolves and maturity-checks the component models; the runtime calls assemble_risk_premium, fixing the bare KeyError on payload["fit_result"] at runtime.py:540); A-4 the demo scope on PL 9624/PL 9629 (a severity GLM, the peril structure, reconcile, approve, the B4 model_call, the C1 pin). About 5 executor-days likely (3.5–8), a chain after PL 9683 and PL 9649.
> 2. SEVERITY: FD 9995 → HIGH, deadline before the P2 exit demo (now a G2 blocker). FD 9605 (#1172, the GLM model_call refusal) → HIGH, the same. Both take lanes under my 13:12:56 priority rule.
> 3. Planning starts now: leaf plans for A-1..A-4, red first, with contention against the in-flight plans.

> FD 9605 APPROVAL, on the record (it was sent by message only, and a record cannot cite a message, RFC-777): "(i) APPROVED: reserve an id and file the finding for the GLM model_call refusal (runtime.py:568-579; an implementation gap from #406 24b537df, contradicting 03 FR-222 'exact invokes the model itself' and 02 FR-193). Severity proposed at its mint." It was sent after 15:47:15 BST and is superseded on severity by item 2 above (HIGH). FD 9605 (#1172 @dee1a85c) cites THIS entry's header.

**The pinning tests flip deliberately.** From the entry headed *"2026-10-05 16:43:57 BST
— MERGE-ACK #1128 (RL-1418) at f43d793464064ea462b7e65208c9a983313c1391, expected tree
9489405370a1ce06c2b985ad88c7d471438febb1; answers to the queued items"*, ANSWERS, verbatim:

> - #1172 FD 9605: severity HIGH, owner WK-1178, before the P2 exit demo (Option A); it cites the entry above for its approval. The tests pinning the refusal (test_rating_runtime.py:377, test_rating_score.py:429) are flipped deliberately in A-2, named in A-2's plan.

They are named here: items 2 and 3.

## Status

`draft`. **Four decision points are open** (§"Decision points"), each with a
recommendation; they are the decision-maker's to rule. The plan moves to `active` only
through a separate activation PR, after every activation need below holds.

### Activation needs, in order

1. **FD 9605 minted** at HIGH (item 2 above).
2. **PL 9649's slice merged** (#1152, the FR-240 family fix). It adds
   `ResolvedArtifact.factors` and fills it in `_Resolver.resolve`'s `model` branch; this
   slice extends both. The sizing memo: *"A-2 can **reuse** PL 9649's `factor` resolver
   branch … but only after PL 9649 merges."*
3. **A-1 merged** (SL 9600 / PL 9599, working ids). The maintainer's item 1 lists the chain
   A-1 → A-2 → A-3; both slices edit `_Resolver.resolve` and `_model_call_handler`, so they
   serialise whatever the order. Neither consumes the other's output, so the lead may swap
   them only by a dated decision.
4. **The ruling on DP-1 to DP-4.** The approval to flip the two pinning tests is already
   dated (the 16:43:57 BST entry, quoted above).
5. **The lane and the dispatch GO**, under the maintainer's 13:12:56 BST priority rule.
   **Acceptance 9 measures NFR-489, so it runs alone** (`RL-1263` item 3, unchanged by
   `RL 9620`): no gate and no other measurement on the VM during it.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red
first" means the named test was run and failed **for the stated cause** before the code that
turns it green ([`README.md`](README.md) rule 2). Each red is recorded in the slice's ledger
with the failure line as printed.

1. **Golden: a GLM `model_call` equals `predict_glm` on the same row (FR-222, FR-193).**
   `test_a_glm_model_call_equals_predict_glm_on_the_same_row` in
   `packages/pricing-core/tests/test_rating_glm_model_call.py` (new): a GLM fitted by
   `fit_glm` (`modelling/glm.py:523`) on a small frame with one banded numeric Factor, one
   grouped categorical Factor and a `log_column` exposure offset, dumped as a `Model`,
   pinned by a `model_call` step and compiled by `compile_bundle` through a fake resolver
   that carries its inputs as the backend does (DP-1). For three quote contexts,
   `score_one`'s step value equals the rounding DP-4 rules applied to `predict_glm(fit,
   frame, factors, spec, bandings=…, groupings=…)` on the same one-row frame. Red first: at
   the base the score raises `MODEL_CALL_FAILED` naming "predict_glm has no such fallback".
2. **The refusal test is flipped (`test_rating_runtime.py:377`).**
   `test_a_glm_model_call_is_refused_with_a_named_code` becomes
   `test_a_glm_model_call_scores`: `_FakeResolver(glm=True)` serves a real GLM dump and its
   inputs, and the handler's output carries `risk_premium_minor` and no
   `MODEL_CALL_ERROR_KEY`. Red first: the renamed test fails at the base on the sentinel.
3. **FR-255's `MODEL_CALL_FAILED` keeps a test (`test_rating_score.py:429`).**
   `test_a_model_call_failure_is_refused_with_the_real_message` used the GLM refusal as its
   vehicle. Its vehicle becomes a GLM whose spec declares a `log_column` offset that the
   step's `feature_map` does not supply: `predict_glm` raises `MODEL_OFFSET_MISSING`
   (`predict.py:144`, `_offset`), and `score_one` raises `ValueError` matching both
   `MODEL_CALL_FAILED` and `MODEL_OFFSET_MISSING`. Red first: at the base the message names
   the old refusal, not `MODEL_OFFSET_MISSING`.
4. **The Bundle carries the inputs, and only for a GLM pin (FR-239, NFR-491).**
   `test_a_glm_pin_carries_its_factors_bandings_and_groupings` (new module): after
   `compile_bundle`, `resolved_payloads` holds `factor:<slug>@<v>`, `banding:<slug>@<v>` and
   `grouping:<slug>@<v>` for each input of the GLM, each validating as its `model_schema`
   class; a GBM pin adds none (`test_a_gbm_pin_carries_no_glm_inputs`). `bundle_hash` is
   unchanged for the same pins and graph (`test_the_bundle_hash_ignores_the_carried_inputs`):
   the inputs are fixed by the pinned model version. Red first: the keys are absent.
5. **The backend resolver fills them (end to end).**
   `test_a_rating_version_pinning_a_fitted_glm_compiles_and_scores` in
   `backend/tests/test_rating_glm_model_call.py` (new): a GLM fitted through the real Job,
   approved with `approved_rows.mark_approved`, pinned by a `model_call`, compiled through
   `_run_compile_job`; `POST /api/v1/score` returns 200 and the step's traced value equals
   `POST /api/v1/models/{id}/predict`'s `expected` for the same row, under DP-4's rounding.
   Red first: `/score` answers the `MODEL_CALL_FAILED` problem.
6. **A model-offset GLM** (DP-3). Under (a): `test_a_model_offset_glm_scores_with_its_source_model`,
   the source model's inputs carried too and the value equal to `/predict`'s. Under (b):
   `test_a_model_offset_glm_is_refused_at_compile` with the ruled code. Red first either
   way.
7. **No database or network at score (NFR-491).** The existing NFR-491 test, if one guards
   `load_bundle` and `score_one` against I/O, passes unchanged with a GLM bundle; if none
   exists at the dispatch tree, item 1's test runs `score_one` with the resolver dropped
   and no session in scope, and the ledger says which.
8. **The refusal text is gone.** `git grep -n "predict_glm has no such fallback" --
   packages backend` prints nothing, and `score.py`'s module docstring item 2
   (`rating/score.py:33-41`) no longer says a GLM is not scored.
9. **NFR-489, measured for a GLM `model_call`.** `scripts/bench-rating.py` gains a GLM
   scenario (Task 5). Its component p99 over the same sample size as the GBM run is
   recorded in the ledger beside the GBM figure, against NFR-489's 50 ms. The run is alone
   on the VM (`pgrep -af 'pytest|vitest|flock'` empty, both gate slots free, recorded). A
   p99 at or above 50 ms is a STOP: report it to the lead as a finding candidate, do not
   tune in this slice.
10. **The gate.** The full two-half gate passes on the merge tree, run once, holding the one
    gate slot. The ledger records each rc and the tree.
11. **The write set.** `git diff --stat origin/main...HEAD` names only §"Write set"'s paths.

## Global Constraints

- **`pricing-core` stays importable standalone**, with no FastAPI, SQLAlchemy or Redis
  dependency (`CLAUDE.md` §2): the runtime reads the carried inputs from the Bundle, never
  from a database (NFR-491).
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2):
  each carried input is its `model-schema` class's dump; the runtime validates it with the
  same class, and the GLM's own spec and fit with `MODEL_SPEC_ADAPTER` and
  `FIT_RESULT_ADAPTER` (`model_schema/modelling.py:1965`, `:1972`).
- **No pandas** (`CLAUDE.md` §3).
- **Money is integer minor units** (`CLAUDE.md` §7); the `model_call` output convention is
  DP-4's and is not changed silently.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13): items 1–6 are red
  first.
- **NFRs are measured, not asserted** (`CLAUDE.md` §13): item 9.
- **Shared files** (`RL-1263`, amended by `RL 9620`): two concurrent build slices may not
  both change the same existing function, class, spec section or policy table.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | FR-222 | `exact` invokes a GLM itself | `req("FR-222")` on items 1, 2, 5 |
| `02` | FR-193 | `pricing-core` scores a persisted GLM from its declarative artifact alone | `req("FR-193")` on items 1, 4 |
| `02` | FR-116 | A model-offset GLM is scored with its source model, or refused by name (DP-3) | `req("FR-116")` on item 6 |
| `03` | FR-239 | The Bundle is self-contained, its hash reproducible from pins and graph | `req("FR-239")` on item 4 |
| `03` | FR-255 | `MODEL_CALL_FAILED` stays typed and reasoned | existing marker on item 3 |
| `03` | NFR-491 | Zero database or network access at score | `req("NFR-491")` on item 7 |
| `03` | NFR-489 | The scoring p99 budget, measured for a GLM `model_call` | ledger only (item 9) |

Out of scope, named so no reader assumes it: a Peril Structure's scoring (A-3, which
calls this slice's GLM path for each component); `approximation` mode (FR-222's other half,
unchanged); `predict_glm_interval` (uncertainty at score is not asked for); the demo's
severity GLM (A-4); the double-count design point (the maintainer's item 4).

### Task 0 at planning time (read, not run)

Read at `137bc817` by this planner; no code was run.

| # | Fact | Where | Consequence |
|---|---|---|---|
| 0.1 | The refusal is `_model_call_handler`'s `else:` (`:568-579`), after the `xgboost`/`lightgbm` branch (`:549`); a GBM scores through `predict_gbm(..., factors=(), nthread=1)` | `rating/runtime.py` | the GLM branch replaces the `else:`; an unknown `model_type` still refuses |
| 0.2 | The value is `round(prediction)`, *"a documented, provisional convention … on the assumption the pinned model was itself fitted to predict on the money-minor scale"* (the handler's docstring, `:515-526`) | same | DP-4: a frequency GLM's `μ` rounds to 0 |
| 0.3 | `load_bundle` (`:646`) calls `_load_boosters` then `_model_call_handler(algorithm, payloads, boosters)` once | same | the GLM inputs are rebuilt in `_model_call_handler`'s outer scope, not in `load_bundle` |
| 0.4 | `predict_glm(fit, data, factors, spec, *, model_offset, bandings, groupings)` (`:230`); `_offset` raises `MODEL_OFFSET_MISSING` for an absent offset column (`:144-195`) | `modelling/predict.py` | item 3's vehicle |
| 0.5 | `resolve_factors` reads each Factor's `source_columns` from the frame and refuses a missing one (FR-87) | `modelling/factors.py:106` | DP-2: what `feature_map`'s values name |
| 0.6 | `prediction.py` loads Factors, Bandings and Groupings for `/predict`, and a model offset through `resolve_offset_model` (`:130-140`, `:236-246`; `modelling.py:950`) | `backend/src/app/platform/` | the resolver reuses both; DP-3 |
| 0.7 | `ResolvedArtifact` is `status` + `payload` (`compile.py:434-440`); `compile_bundle` writes `payloads[str(ref)] = resolved.payload` per pin (`:624-631`) | `rating/compile.py` | DP-1 (a) adds the inputs there |
| 0.8 | `_glm_model_payload` (`tests/test_rating_runtime.py:72-81`) has no `spec` and empty `coefficients` | test fixture | item 2 needs a real GLM dump |
| 0.9 | The example `feature_map` is `{"driver_age": "age_years"}` (`test_rating_runtime.py`, step `s_risk`), a graph name to a feature slug | same | DP-2 |

### Write set, and its contention (`RL-1263`, `RL 9620`)

| Path | Change |
|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | edited: `ResolvedArtifact` (`:434`; `bandings`, `groupings` appended beside PL 9649's `factors`, each defaulted `()`) *(DP-1 a)*, `compile_bundle` (the pin loop `:624-631`: a GLM pin's inputs written under their refs) |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | edited: `_model_call_handler` (`:512`, the GLM branch replaces `:568-579`; its docstring) |
| `packages/pricing-core/src/pricing_core/rating/score.py` | edited: the module docstring's item 2 (`:33-41`) |
| `backend/src/app/platform/rating_versions.py` | edited: `_Resolver.resolve`'s `model` branch (`:464-485` at `137bc817`): Bandings and Groupings loaded for a GLM, and *(DP-3 a)* the offset source |
| `packages/pricing-core/tests/test_rating_runtime.py` | edited: `_glm_model_payload` (`:72`), `_FakeResolver` (`:171`), `test_a_glm_model_call_is_refused_with_a_named_code` (`:377`, renamed, item 2) |
| `packages/pricing-core/tests/test_rating_score.py` | edited: `test_a_model_call_failure_is_refused_with_the_real_message` (`:428`) and `_compiled`'s GLM fixture (`:137`) (item 3) |
| `packages/pricing-core/tests/test_rating_glm_model_call.py`, `backend/tests/test_rating_glm_model_call.py` | added (new modules) |
| `scripts/bench-rating.py` | edited: the fixture builder gains a GLM scenario (item 9) |
| `docs/specs/03-rating-engine.md`, `docs/specs/02-modelling.md` | only as the ruling words it (DP-2's `feature_map` meaning; DP-3 (b)'s note on FR-193) |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated |

**Not written:** `packages/model-schema/` (every carried shape exists), `load_bundle`,
`CompiledBundle`, `Bundle`, `bundle_hash`, any `frontend/src` file, any migration.

**Contention.** Classes as in `docs/process/delivery-process.core.json`'s `no_shared_files`.
**Snapshot: open PRs at `137bc817`, 2026-10-05 between 16:52 and 17:40 BST; each plan's write
set read from its branch at the head named.** `PL-1371` §5 rule 4 (`:290-294`) serialises
`compile_bundle` outright for WK-673 S3, WK-1250 S2, WK-1250 S3 and WK-675 S3; this slice
joins that set, as the sizing memo says.

| Other slice (lane; Work; source read) | Shared path | Them | Us | Class → consequence |
|---|---|---|---|---|
| **PL 9649**, the FR-240 family fix (#1152 @`df8ba756`; WK-673) | `compile.py` `ResolvedArtifact`, `compile_bundle`; `rating_versions.py` `model` branch | adds `factors`; three checks after the pin loop; the `model` branch carries Factors | extends both | **plan dependency** (activation need 2) → never concurrent |
| **A-1**, PL 9599 (working id; WK-1178) | `rating_versions.py` `_Resolver.resolve`; `runtime.py` `_model_call_handler` | a `peril_structure` branch; DP-3's early peril refusal | the `model` branch; the GLM branch | same methods → **SERIALISE**: A-1 first (activation need 3) |
| **A-3**, PL 9595 (working id; WK-1178) | `runtime.py` `_model_call_handler`; `compile.py` `compile_bundle` | the peril branch calls this slice's GLM path per component | the GLM path | **plan dependency**: A-3 consumes this slice's output |
| **WK-1250 S2**, PL 9610 (#1170 @`ca407ed9`) | `compile.py` `compile_bundle`; `rating_versions.py` `_Resolver`; `test_rating_runtime.py`, `test_rating_score.py` | G1, mount resolution, `all_refs`; a `sub_graph` branch; appended tests only | the pin loop; the `model` branch; edits of named fixtures and tests | `compile_bundle`: **SERIALISE** (rule 4); `_Resolver`: same class, different branches → serialise with it; tests: our edits are existing-test edits, named here |
| **WK-1250 S3**, PL 9609 (#1173 @`7c8736fd`) | `compile.py` `compile_bundle`; `test_rating_score.py` `:438-507` | `Bundle`, `compile_bundle`, `bundle_hash`; interim tests rewritten | the pin loop; `:428` and `_compiled` | `compile_bundle`: **SERIALISE** (rule 4); `test_rating_score.py`: different tests, `_compiled` read by both → the dispatch record names it |
| **WK-673 S3**, PL 9689 (#1138 @`e810b785`) | `compile.py` | reads `compile_bundle`, not edited | edited | rule 4 names the pair → **SERIALISE** |
| **PL 9688**, the FD 9707 fix (#1145 @`2f3269c8`; WK-673) | `compile.py`; `runtime.py`; `score.py`; `test_rating_runtime.py`; `test_rating_score.py` | `ALGORITHM_CHECKS`, `_check_lookup_as_at`; `_decision_table_node`, module docstring `:22-35`; `score_one`, `_score_context_sync`; `test_lookup_step_wire_translation_matches_by_key`; `test_a_reference_lookup_miss_is_refused` | `ResolvedArtifact`, the pin loop; `_model_call_handler`; docstring item 2 `:33-41`; other tests | different definitions → ALLOWED one-sided only with the dispatch record naming each path and its check; `score.py`'s module docstring is one definition edited by both (theirs `runtime.py`'s, ours `score.py`'s — different files) |
| **PL 9776**, F35 (#1051 @`ecbb82ab`; WK-1178) | `runtime.py`; `score.py`; `compile.py`; `test_rating_score.py` | `to_wire`, `_expression_node`, `_decision_table_node`, `_constraint_node`, `CompiledBundle`, `load_bundle`; `_build_trace`, `build_scoring_result`; `ALGORITHM_CHECKS`; `_algorithm_payload` and one trace test | `_model_call_handler`; docstring item 2; `ResolvedArtifact`, the pin loop; `:428`, `_compiled` | name-disjoint → ALLOWED one-sided with the dispatch record; **same Work**, so `RL 9620` (a) and (b) are written ((b): neither consumes the other's output) |
| **PL 9728**, the NFR-489 remedy (#1113 @`3ad98fe2`; WK-1178) | `scripts/bench-rating.py` | its `--http` full-path mode | a GLM component scenario | same file; **same Work** → the dispatch record names the definitions; if both edit the fixture builder, **SERIALISE** |

Every other open plan (#1127 PL 9716, #1131 PL 9713, #1140 PL 9683, #1146 PL 9662, #1161 PL
9624, #1164 PL 9629, #1165 PL 9617, #1168 PL 9616) names none of this write set (each plan
file read from its branch at the snapshot above, grepped for every path in the table).

### Size

Medium: about one and a half executor days (the sizing memo's A-2 row, 1 / 1.5 / 2.5). Six
tasks after Task 0, one exclusive measurement, one full two-half gate run. The backend test
fits a GLM through the real Job, so it needs Postgres and MinIO.

## Decision points

None is decided. Each is the decision-maker's.

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | How a GLM pin's Factors, Bandings and Groupings travel in the Bundle | (a) `ResolvedArtifact` gains `bandings` and `groupings` beside PL 9649's `factors`; `compile_bundle` writes each under its own `ArtifactRef` string in `resolved_payloads`, for a GLM `model_call` pin only; (b) a new `Bundle` field holding them per model ref; (c) keys nested inside the model's payload | **(a)**: the Bundle's shape and `bundle_hash` are unchanged; each input is its `model-schema` class's dump under the reference grammar every payload already uses. (b) adds a second hand-written shape to `Bundle`; (c) is what PL 9649 Task 3b Step 3 refused (*"a key added beside it is a second, hand-written shape inside a Bundle"*) | decision-maker | Tasks 2, 3 |
| **DP-2** | What `feature_map`'s values name for a GLM. `03` §4.1's `RatingAlgorithm` example shows `{"driver_age": "driver_age", …}` (`03:267`); the GBM path keys the frame by Factor slug (`feature_order`); `resolve_factors` reads each Factor's `source_columns` | (a) for a GLM the values name the frame's columns, i.e. the Factors' `source_columns` and the offset column; (b) the values are Factor slugs for both kinds, and the runtime renames each slug to its Factor's source column(s) | **(b)**: one meaning for one field across model kinds, and the author maps to the model's own vocabulary (its Factors), which the Model already names. (a) gives `feature_map` two meanings by model type. Under (b), an interaction Factor is fed through its operands' slugs, and the offset column is mapped under its own column name; a `03` dated note words it (Task 6) | decision-maker | Task 4 |
| **DP-3** | A GLM whose spec has `offset.kind == "model"` (FR-116) | (a) carry the source model and its inputs too, and compute its `linear_predictor` per quote, as `/predict` does (`prediction.py:236-246`); (b) refuse at compile with a named code, and a dated note on FR-193 | **(a)**: FR-193 says *any* persisted Model scores, and the backend already resolves the source (`resolve_offset_model`, `modelling.py:950`). (b) narrows a requirement to fit a slice | decision-maker | Tasks 2, 3, item 6 |
| **DP-4** | The value a GLM `model_call` yields. The GBM convention is `round(prediction)`, provisional, on the assumption the model predicts on the money-minor scale (0.2). A frequency GLM's `μ` (claims per unit exposure) rounds to 0 | (a) keep the convention for a GLM, unchanged; this slice's golden uses a GLM on the money-minor scale (a severity or burning-cost model) and the frequency case is A-3's and AN's (the double-count ruling); (b) emit the unrounded value for a `model_call` and round only at a `money_minor` boundary | **(a)** for this slice: changing the money convention is FR-250/NFR-496 scope, not FD 9605's. The plan records the hazard for A-3, which composes frequency × severity through `assemble_risk_premium` before any rounding | decision-maker | item 1's expected value |

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm activation needs 1–4 on `origin/main`. Re-read every line cite at
  the dispatch tree and re-anchor by symbol; PL 9649's and A-1's merges move
  `rating_versions.py`, `compile.py` and `runtime.py`.
- [ ] **Step 2:** Re-read the write set of every slice in flight against §"Write set", and
  give the lead the `RL 9620` (a)/(b) lines for each same-Work pair.

### Task 1: The reds (items 1–5)

**Files:** Create `packages/pricing-core/tests/test_rating_glm_model_call.py`,
`backend/tests/test_rating_glm_model_call.py`; Modify
`packages/pricing-core/tests/test_rating_runtime.py`,
`packages/pricing-core/tests/test_rating_score.py`.

- [ ] **Step 1:** A fixture that fits a real GLM with `fit_glm` on a small Polars frame
  (one banded numeric Factor, one grouped categorical Factor, a `log_column` offset) and
  dumps it as a `Model` with its spec; a fake resolver that serves it and, under DP-1 (a),
  its inputs on `ResolvedArtifact`. Write items 1 and 4. Expected red: `MODEL_CALL_FAILED`
  ("predict_glm has no such fallback"); the input keys absent.
- [ ] **Step 2:** Items 2 and 3: replace `_glm_model_payload` with the real dump, rename and
  re-assert the `:377` test, re-vehicle the `:428` test. Expected red: the sentinel is
  present; the message is the old refusal.
- [ ] **Step 3:** Item 5 (backend). Expected red: `/score` answers `MODEL_CALL_FAILED`.
- [ ] **Step 4:** Commit (red): `test: FD 9605 — a GLM model_call is refused at score (FR-222, FR-193)`.

### Task 2: The resolver carries the inputs (items 4, 5)

**Files:** Modify `backend/src/app/platform/rating_versions.py`.

- [ ] **Step 1:** In the `model` branch, for a GLM (`model_obj.fit_result` a
  `GlmFitResult`), load Bandings and Groupings for the Factors PL 9649 already loads, as
  `prediction.py:133-140` does, and set them on the `ResolvedArtifact`. *(DP-3 a)* For a
  `model` offset, resolve the source with `resolve_offset_model` and carry its fit, spec and
  inputs under its own ref.

### Task 3: Compile writes them (item 4)

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/compile.py`.

- [ ] **Step 1:** `ResolvedArtifact` gains `bandings: tuple[Banding, ...] = ()` and
  `groupings: tuple[Grouping, ...] = ()` (defaults keep every `FakeResolver` valid). In the
  pin loop, for a ref whose payload's `fit_result.model_type == "glm"`, write each Factor,
  Banding and Grouping as `payloads[f"{type}:{x.slug}@{x.version}"] = x.model_dump(mode="json")`.
  `bundle_hash` is not touched.
- [ ] **Step 2:** Run item 4's tests; green. Commit:
  `feat: compile carries a GLM pin's factors, bandings and groupings (FR-239, NFR-491; FD 9605)`.

### Task 4: The runtime scores a GLM (items 1–3, 5–8)

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/runtime.py`,
`packages/pricing-core/src/pricing_core/rating/score.py`.

- [ ] **Step 1:** In `_model_call_handler`'s outer scope, for each `model_call` step whose
  pinned payload is a GLM, build once: `FIT_RESULT_ADAPTER` → `GlmFitResult`,
  `MODEL_SPEC_ADAPTER` → `GlmSpec`, the Factors (spec order, `spec.factors` ids matched to
  the carried `Factor`s), and the Bandings and Groupings keyed by id. A missing input is a
  load-time `ValueError` naming the ref (the Bundle is malformed, not the quote).
- [ ] **Step 2:** Replace the `else:` refusal with a `glm` branch: the one-row frame under
  DP-2's ruling, `predict_glm(...)`, the value under DP-4's ruling. Any `ModellingError` or
  `PredictionError` returns `_model_call_failure(step, <its code and message>)`. An unknown
  `model_type` keeps a named refusal.
- [ ] **Step 3:** Correct the handler's docstring and `score.py`'s item 2. Run the pricing-core
  tests; green. Commit: `fix: a GLM scores through model_call (FD 9605; FR-222, FR-193, FR-255)`.
- [ ] **Step 4:** Run item 5's backend test; green.

### Task 5: The measurement (item 9)

**Files:** Modify `scripts/bench-rating.py`.

- [ ] **Step 1:** Add a GLM scenario beside the GBM fixture: the same algorithm with its
  `model_call` pinning a GLM built as in Task 1 Step 1.
- [ ] **Step 2:** Check `pgrep -af 'pytest|vitest|flock'` is empty and both gate slots are
  free (`flock -n /tmp/slots/gate-1 true`, `gate-2`); record both. Run the GBM and GLM
  scenarios back to back, same sample size, and record p50, p99 and the tree.

### Task 6: The spec texts, verbatim from the ruling

- [ ] **Step 1:** Apply the ruling's text, if any (DP-2's `feature_map` meaning; DP-3 (b)'s
  note), under `spec-change`; run `python3 scripts/audit-docs.py`; commit. If none, the
  ledger says so.

### Task 7: The gate and the ledger (items 10, 11)

- [ ] **Step 1:** The full two-half gate through the gate-runner, holding the one gate
  slot. Record each rc and the tree.
- [ ] **Step 2:** The `LG-` ledger: every red with its printed line, item 9's figures, and
  `git diff --stat origin/main...HEAD` against §"Write set".

## Hand-off

1. The lead mints PL 9597 at the merge turn (SL 9598 mints with A-1's PR) and dispatches only
   after §"Activation needs" hold, in a separate activation PR.
2. When this slice merges, FD 9605's event is discharged (*"a merged fix under (a) … the
   discharge test is `test_a_glm_model_call_is_refused_with_a_named_code` flipped"*); the
   auditor closes it.
3. A-3 (PL 9595, working id) builds each component's prediction through this slice's GLM
   path, and inherits DP-4's hazard: a frequency component must not be rounded before it is
   composed.
4. **For the lead:** the sizing memo names "NFR-490 p99" for this measurement; the scoring
   p99 budget is **NFR-489** (`03:1330`). NFR-490 is the tracing overhead (`03:1331`). This
   plan measures NFR-489.

## Self-review

1. **Coverage of FD 9605's remedy (a), clause by clause.** "Compile embeds each pinned GLM's
   Factor, Banding and Grouping versions in `Bundle.resolved_payloads`": Tasks 2, 3, item 4.
   "the runtime rebuilds them and calls `predict_glm`": Task 4, item 1. "a golden test that
   the `model_call` value equals `predict_glm` on the same row": item 1. "`:377` flips":
   item 2. The sizing memo's "NFR-490 p99 is measured": item 9, corrected to NFR-489.
2. **The second pinning test** (`test_rating_score.py:429`) is flipped, and FR-255 keeps a
   real vehicle (item 3), so the flip loses no coverage.
3. **Every open design choice is a DP with an owner** (DP-1 to DP-4). No spec text is
   written without a ruling (Task 6).
4. **Repository literals read at `137bc817`:** every line in §"Task 0 at planning time" and
   §"Write set"; PL 9649's `ResolvedArtifact.factors` and Task 3b Step 3 read on its branch
   at `df8ba756`.
5. **What was not executed.** No test or code was run. The steps are sketches against names
   read at `137bc817` and PL 9649's branch; a step that does not run as written is a plan
   defect to report, not to work around.
