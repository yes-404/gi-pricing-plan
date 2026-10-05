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
  the finding file under `docs/findings/` on that branch, whose name begins with the working id
  (`…09605-a-glm-model-call-is-refused-at-score-…`; the full name is not written here, because
  check 32 reads an id in it, and the id is not minted), §"Disposition", remedy **(a) Build it**: *"Compile embeds each pinned
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

**Dated note, 2026-10-05 (written 17:08:21 BST, pre-mint): DP-1 to DP-4 ruled.** Two entries
in the same file, each read in full by this planner. From the entry headed *"2026-10-05
17:02:50 BST — A-1/A-2 plans and batch 5 noted; the model_call ROUNDING is fixed IN A-2 by
declared result type, not worked around in A-3"*, verbatim:

> Verified at main: packages/pricing-core/src/pricing_core/rating/runtime.py:567 `value: int = round(prediction)`, whose docstring (:521-525) calls it "a documented, provisional convention (`round()` to the nearest whole unit, on the assumption the pinned model was itself fitted to predict on the money-minor scale already)", pending "Task 1.4's FR-250 golden test". Under Option A, B4's model_call scores frequency and severity models, so a frequency μ (~0.07) rounds to 0: the provisional assumption is FALSE for exactly the path G2 needs.

> RULING: A-2 (#1178 PL 9597) settles it at the ROOT, not A-3 by composing before rounding (that would leave every other model_call wrong). A model_call's output follows its step's DECLARED result type (03 FR-227): \`decimal\` → an exact Decimal, no integer rounding; \`money_minor\` → the step's declared rounding (FR-226); any other declared type → refused at save as a type mismatch. Red first: a frequency GLM model_call declared \`decimal\` returns ~0.07 (today: 0). A golden test against predict_glm at full precision. The docstring's "provisional" note is removed, citing this entry. A-3 composes frequency × severity on Decimals and rounds once, at the money step. dm-doublecount and dm-a34 are told: B1's ratio and A-3's composition sit on Decimal model outputs. If the planner finds a G2-independent reason to defer this, it comes to me; otherwise it is in A-2.

> A-2's DPs 1–4: send me the plan's recommendations in one line each; I rule them in the reply.

> Flags (2) NFR-489 not 490 (right) and (3) the same-Work pairs (A-1 with PL 9616 and PL 9776; A-2 with PL 9776 and PL 9728), each written with RL 9620 lines at dispatch: noted.

From the entry headed *"2026-10-05 17:03:45 BST — A-2 (#1178 PL 9597) DP-1..3 RULED (DP-4 at
17:02:50)"*, verbatim:

> DP-1: (a). The GLM's Factor, Banding and Grouping travel as their own resolved_payloads entries under their own refs (reusing PL 9649's ResolvedArtifact.factors); no new Bundle shape; the content hash covers them as pins, so a changed banding changes the bundle hash (a test asserts it).

> DP-2: (b). The feature_map names Factor slugs (what predict_glm consumes); the Factor carries its source column and banding, so the raw quote value is banded inside predict_glm, never pre-banded by the caller. A red test: a feature_map naming a raw column instead of a Factor slug is refused at save, with its code.

> DP-3: (a), with one precision. The source model's offset DEFINITION travels as a pinned payload, but the offset's VALUE for a quote comes from the quote context through the feature_map (e.g. exposure → log exposure), never from the fit data. A quote missing the offset input is refused with MODEL_CALL_FAILED (FR-255; the test A-2 already moves to a missing offset column). A golden test: the same quote at exposure 1.0 and 0.5 differs by exactly the offset.

> A planner folds these and the DP-4 rounding ruling into #1177/#1178 now.

DP-1 (a), DP-2 (b) and DP-3 (a) are this plan's recommendations, each with an addition
(items 12 to 14). DP-4 is ruled **against** this plan's recommendation (a): the rounding is
fixed in this slice, at the root (item 15). Two of the rulings rest on a mechanism that does
not exist at `137bc817`: a `model_call` step declares no result type and no rounding, and
save-time validation does not resolve a pin. This plan does not choose one. It records both
as **DP-5**, open (§"Decision points").

## Status

`draft`. **DP-1 to DP-4 are ruled** by the maintainer (by delegation) in the 17:02:50 and
17:03:45 BST entries quoted above (dated note, 2026-10-05). **DP-5 is open**: the two
mechanisms those rulings rest on, with options and a recommendation, for the maintainer (by
delegation). The plan moves to `active` only
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
   dated (the 16:43:57 BST entry, quoted above). *Dated note, 2026-10-05 (pre-mint):
   **held**, by the 17:02:50 and 17:03:45 BST entries; no `RL-` is written. The dispatch
   record cites both entries by their headers.*
4a. **The ruling on DP-5** *(added 2026-10-05, pre-mint)*. Items 13 and 15 cannot be written
   as tests until DP-5 names the field and the check site.
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
   frame, factors, spec, bandings=…, groupings=…)` on the same one-row frame. *(Dated note,
   2026-10-05: DP-4 is ruled, so "the rounding DP-4 rules" is the step's declared result
   type. With `decimal`, the value is the exact Decimal of the prediction, with no
   rounding (item 15).)* Red first: at
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
   reproducible from the same pins and graph (FR-239,
   `test_the_bundle_hash_is_reproducible_from_the_pins_and_the_graph`): the inputs are
   fixed by the pinned model version. Red first: the keys are absent. *(Dated note,
   2026-10-05: renamed from `test_the_bundle_hash_ignores_the_carried_inputs`. DP-1's
   ruling says "the content hash covers them as pins", and item 12 asserts it.)*
5. **The backend resolver fills them (end to end).**
   `test_a_rating_version_pinning_a_fitted_glm_compiles_and_scores` in
   `backend/tests/test_rating_glm_model_call.py` (new): a GLM fitted through the real Job,
   approved with `approved_rows.mark_approved`, pinned by a `model_call`, compiled through
   `_run_compile_job`; `POST /api/v1/score` returns 200 and the step's traced value equals
   `POST /api/v1/models/{id}/predict`'s `expected` for the same row, under DP-4 as ruled
   (the step's declared result type, item 15).
   Red first: `/score` answers the `MODEL_CALL_FAILED` problem.
6. **A model-offset GLM** (DP-3). Under (a): `test_a_model_offset_glm_scores_with_its_source_model`,
   the source model's inputs carried too and the value equal to `/predict`'s. Under (b):
   `test_a_model_offset_glm_is_refused_at_compile` with the ruled code. Red first either
   way. *(Dated note, 2026-10-05: ruled (a); the (b) test is not written. The source model's
   offset inputs come from the quote through the `feature_map`, never from the fit data,
   item 14.)*
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

*Items 12 to 15 were added 2026-10-05 (pre-mint), from the 17:02:50 and 17:03:45 BST rulings
quoted above. Each is red first.*

12. **A changed banding changes the bundle hash** (DP-1 (a), the 17:03:45 entry).
    `test_a_changed_banding_changes_the_bundle_hash` (new pricing-core module): two GLMs
    fitted with the same Factors except that one Factor's Banding is re-cut (`banding:<slug>@1`
    and `@2`), each pinned by the same graph, compile to two Bundles. Their `content_hash`es
    differ, and each Bundle carries only its own `banding:<slug>@<v>` key. *The planner's
    reading, for the dispatch to confirm: the hash covers the inputs **through the model
    pin**. A Model pins the Banding version it was fitted with (the `Banding` docstring,
    `model_schema/modelling.py:347`, and `Factor.banding_id`, `:154`), so a re-cut banding is
    a new Model version and a new pin. `bundle_hash` stays "reproducible from the pins and
    the graph" (FR-239) and is not edited. If the ruling means the inputs enter the hash
    beyond the pins, that is a `bundle_hash` and FR-239 change: STOP and report it.* Red
    first: the second Bundle has no `banding:` key at the base.
13. **A raw-column `feature_map` is refused at save, with its code** (DP-2 (b), the 17:03:45
    entry). `test_a_feature_map_naming_a_raw_column_is_refused_at_save`: a `model_call` on a
    GLM whose `feature_map` value names a raw column (a Factor's source column, not the
    Factor's slug) is refused, and the response carries the code DP-5 (ii) rules. The
    control: the same map naming the Factor's slug saves. *The spec's offset column is the
    one non-Factor value the map may name, as DP-2's recommendation (b) says ("the offset
    column is mapped under its own column name") and DP-3's precision needs ("exposure → log
    exposure").* Red first: at the base the raw-column map saves.
14. **The offset's value comes from the quote** (DP-3 (a) with the precision, the 17:03:45
    entry). `test_the_offset_moves_the_glm_by_exactly_the_exposure` (new pricing-core module,
    a GLM with a `log_column` exposure offset): the same quote at exposure 1.0 and at 0.5
    differs by exactly the offset. The step is declared `decimal`, so both values are exact
    Decimals (item 15), and the assertion is on the linear predictor:
    `ln(value_1.0) − ln(value_0.5) == ln(1.0) − ln(0.5)`. *"Exactly" is read to float
    precision (`math.isclose(rel_tol=1e-12)`), because `predict_glm` computes in float and
    `(a + b) − (a + c)` is not bitwise `b − c`. If the maintainer meant bitwise, the dispatch
    reports it.* A quote missing the offset input is refused with `MODEL_CALL_FAILED`
    (FR-255): item 3, whose vehicle is that case. Red first: at the base the GLM is refused.
15. **A `model_call`'s value follows its step's declared result type (FR-227, FR-226)**
    (DP-4, the 17:02:50 entry, for every `model_call`, not only a GLM).
    - **Red first:** `test_a_frequency_glm_declared_decimal_returns_its_unrounded_rate`: a
      frequency GLM (Poisson, log link, mean about 0.07), its step declared `decimal`, scores
      about 0.07. At the base it scores 0 (`round(prediction)`, `runtime.py:567`), or is
      refused before that as a GLM. The red is recorded with whichever line prints.
    - **Golden at full precision:**
      `test_a_decimal_model_call_equals_predict_glm_at_full_precision`: the value is the exact
      Decimal of `predict_glm`'s float on the same row (`Decimal(repr(x))`, FR-244's boundary
      rule), with no quantize.
    - **`money_minor`:** a step declared `money_minor` yields its prediction rounded once with
      the step's declared rounding (FR-226).
    - **Any other declared type** is refused at save with `RATING_TYPE_MISMATCH`
      (`compile.py:146`, `output_type_issues`).
    - **The docstring:** the "provisional convention" text (`runtime.py:521-525`) is removed,
      and the handler's docstring cites the 17:02:50 entry by its header. Check:
      `git grep -n "provisional convention" -- packages/pricing-core/src/pricing_core/rating/runtime.py`
      prints nothing.
    - The field, the rounding and the check site are DP-5 (i)'s. **How the exact Decimal
      crosses back into the engine** (FR-273: the binding refuses a `Decimal` input and takes
      a `str` as a string) is read at Task 0. If neither a number nor a string carries the
      value exactly, STOP and report it.

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
  DP-4's and is not changed silently. *(Dated note, 2026-10-05: DP-4 is ruled. The output
  follows the step's declared result type, so `decimal` gives an exact Decimal and
  `money_minor` gives one declared rounding, never two (FR-226, NFR-496). Item 15.)*
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
| `03` | FR-227 | A `model_call`'s value follows its declared result type, checked at save *(added 2026-10-05, DP-4 ruled)* | `req("FR-227")` on item 15 |
| `03` | FR-226 | A `money_minor` `model_call` is rounded once, by its declared rounding *(added 2026-10-05, DP-4 ruled)* | `req("FR-226")` on item 15 |

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
| 0.10 | *(Added 2026-10-05.)* `RatingModelCallStep` (`model_schema/rating.py:299`) has `model_ref`, `peril_structure_ref`, `mode` and `feature_map`, and no `result_type` or `rounding`. Only `RatingExpressionStep` declares `result_type` (`:296`), and only `RatingOutputStep` declares `rounding`. `03` §3's step table names the same fields for `model_call` (`03:100`). The hand-written contract admits `result_type` on every step (`docs/contracts/schemas/rating-algorithm.schema.json:50`), but the model is `extra="forbid"` | `packages/model-schema/` | DP-4's ruling has no field to read: **DP-5 (i)** |
| 0.11 | *(Added 2026-10-05.)* Save-time validation is pure: `validate_algorithm` (`compile.py:366`) resolves no pin, and `producer_types` (`:95`) leaves a `model_call`'s output untyped because "save-time validation cannot resolve" the pinned artifacts ("checked at bundle time") | `rating/compile.py` | DP-2's "refused at save" cannot see the Model's Factor slugs there: **DP-5 (ii)** |
| 0.12 | *(Added 2026-10-05.)* "A Model pins the Banding version it was fitted with" (`Banding`'s docstring, `model_schema/modelling.py:347`); a Factor pins its Banding by id (`Factor.banding_id`, `:154`) | `model_schema/modelling.py` | item 12: a re-cut banding is a new pin |

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

*Dated note, 2026-10-05 (pre-mint): DP-4's ruling adds writes, and DP-5 decides some of
them. Ruled now: `runtime.py` `_model_call_handler` (the value by declared type and its
docstring); `compile.py` save-time typing of a `model_call` (`producer_types`,
`validate_algorithm`, for items 13 and 15). If DP-5 (i) is ruled (a):
`packages/model-schema/src/model_schema/rating.py` `RatingModelCallStep`, the regenerated
`docs/contracts/` files (`generate-contracts.py`), `03` §3's step-table row (`03:100`), and
every existing `model_call` fixture: at `137bc817`, the files under `tests/` among those
`git grep -l '"model_call"\|type="model_call"' 137bc817 -- backend packages` lists (ten files;
the other three are `model_schema/rating.py`, `model_schema/scoring.py` and `runtime.py`) are
`backend/tests/test_rating_algorithms.py`,
`packages/model-schema/tests/test_rating_algorithm.py`,
`packages/model-schema/tests/test_rating_version.py`,
`packages/pricing-core/tests/test_rating_compile.py`,
`packages/pricing-core/tests/test_rating_compile_bundle.py`,
`packages/pricing-core/tests/test_rating_runtime.py` and
`packages/pricing-core/tests/test_rating_score.py`. If DP-5 (ii) is ruled (a), the backend
algorithm-save route's module is added too. The contention table below was cut before these
writes. Task 0 Step 2 re-reads it against them, and `model_schema/rating.py` against every
in-flight plan.*

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

*Dated note, 2026-10-05 (pre-mint):* **DP-1 to DP-4 are ruled** by the maintainer (by
delegation) in the 17:02:50 and 17:03:45 BST entries quoted in §"The maintainer's decisions
this plan rests on, quoted": DP-1 (a), DP-2 (b), DP-3 (a) with a precision, and DP-4 settled
at the root, against this plan's (a). The rows below were written before the rulings and are
kept as written. Items 12 to 15 carry what the rulings add. **DP-5 was added on the same
date and is open.**

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | How a GLM pin's Factors, Bandings and Groupings travel in the Bundle | (a) `ResolvedArtifact` gains `bandings` and `groupings` beside PL 9649's `factors`; `compile_bundle` writes each under its own `ArtifactRef` string in `resolved_payloads`, for a GLM `model_call` pin only; (b) a new `Bundle` field holding them per model ref; (c) keys nested inside the model's payload | **(a)**: the Bundle's shape and `bundle_hash` are unchanged; each input is its `model-schema` class's dump under the reference grammar every payload already uses. (b) adds a second hand-written shape to `Bundle`; (c) is what PL 9649 Task 3b Step 3 refused (*"a key added beside it is a second, hand-written shape inside a Bundle"*) | decision-maker | Tasks 2, 3 |
| **DP-2** | What `feature_map`'s values name for a GLM. `03` §4.1's `RatingAlgorithm` example shows `{"driver_age": "driver_age", …}` (`03:267`); the GBM path keys the frame by Factor slug (`feature_order`); `resolve_factors` reads each Factor's `source_columns` | (a) for a GLM the values name the frame's columns, i.e. the Factors' `source_columns` and the offset column; (b) the values are Factor slugs for both kinds, and the runtime renames each slug to its Factor's source column(s) | **(b)**: one meaning for one field across model kinds, and the author maps to the model's own vocabulary (its Factors), which the Model already names. (a) gives `feature_map` two meanings by model type. Under (b), an interaction Factor is fed through its operands' slugs, and the offset column is mapped under its own column name; a `03` dated note words it (Task 6) | decision-maker | Task 4 |
| **DP-3** | A GLM whose spec has `offset.kind == "model"` (FR-116) | (a) carry the source model and its inputs too, and compute its `linear_predictor` per quote, as `/predict` does (`prediction.py:236-246`); (b) refuse at compile with a named code, and a dated note on FR-193 | **(a)**: FR-193 says *any* persisted Model scores, and the backend already resolves the source (`resolve_offset_model`, `modelling.py:950`). (b) narrows a requirement to fit a slice | decision-maker | Tasks 2, 3, item 6 |
| **DP-4** | The value a GLM `model_call` yields. The GBM convention is `round(prediction)`, provisional, on the assumption the model predicts on the money-minor scale (0.2). A frequency GLM's `μ` (claims per unit exposure) rounds to 0 | (a) keep the convention for a GLM, unchanged; this slice's golden uses a GLM on the money-minor scale (a severity or burning-cost model) and the frequency case is A-3's and AN's (the double-count ruling); (b) emit the unrounded value for a `model_call` and round only at a `money_minor` boundary | **(a)** for this slice: changing the money convention is FR-250/NFR-496 scope, not FD 9605's. The plan records the hazard for A-3, which composes frequency × severity through `assemble_risk_premium` before any rounding | decision-maker | item 1's expected value |
| **DP-5** *(added 2026-10-05, open)* | The two mechanisms the rulings rest on, which do not exist at `137bc817`. **(i)** DP-4 reads the `model_call` step's "DECLARED result type" and, for `money_minor`, "the step's declared rounding (FR-226)". The step declares neither (0.10). **(ii)** DP-2 refuses a raw-column `feature_map` "at save, with its code". Save-time validation does not resolve the pin that names the Factors (0.11), and no code is named | **(i)** (a) `RatingModelCallStep` gains a required `result_type: RatingResultType` and a `rounding: RoundSpec`, required when `money_minor` and refused otherwise. `03` §3's row names both, and every `model_call` fixture declares them. (b) The same, with `result_type` optional and defaulting to `money_minor` with half-even to the unit, which is today's behaviour. (c) No new field: a `model_call`'s value is always `decimal`, and only an `output` step rounds. **(ii)** (a) The backend's algorithm save resolves each `model_call`'s `model_ref` after `validate_algorithm`, and refuses with a new code added to `03`'s error catalogue. (b) The check runs at compile, the first point that resolves the pin, with a new code. (c) As (a) or (b), with the existing `VALIDATION_FAILED` | **(i) (a).** FR-227 already says "Every step declares its result type", and the contract already admits the field, so the gap is `model-schema`'s. (b) keeps a hidden default, the "provisional convention" the ruling removes. (c) drops the ruling's `money_minor` limb. **(ii) (a) with a new code.** It is the only option that is literally "at save". The step pins `model_ref` exactly, so the save can read the Model's Factor slugs. A named code follows FR-255's typing. (b) moves the refusal to compile. Both are the maintainer's (by delegation): each changes a shape or a catalogue | the maintainer (by delegation) | items 13, 15; activation need 4a |

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
- [ ] **Step 3a:** *(Added 2026-10-05.)* Items 12 to 15, each red by its stated cause. Items
  13 and 15 are written in the shape DP-5 rules.
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
  DP-2's ruling, `predict_glm(...)`, the value under DP-4's ruling. *(Dated note, 2026-10-05:
  ruled. The frame's columns are each Factor's `source_columns`, taken from the quote values
  that the `feature_map` maps to the Factor's slug; `predict_glm` bands them. The offset
  column is taken from the quote, and the value follows the step's declared result type,
  item 15. The same rule replaces `round(prediction)` in the GBM branch.)* Any `ModellingError` or
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
  ledger says so. *(Dated note, 2026-10-05: the 17:02:50 and 17:03:45 BST entries carry no
  spec text. DP-3 (b) was not taken. DP-5's ruling may carry text for `03` §3's
  `model_call` row and the error catalogue. This planner writes none.)*

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
   composed. *(Dated note, 2026-10-05: DP-4 is ruled at the root (the 17:02:50 entry), so
   the hazard is removed here, not carried. A-3 composes frequency × severity on the
   Decimal model outputs this slice yields, and rounds once, at the money step. B1's ratio
   sits on the same Decimals.)*
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
   written without a ruling (Task 6). *(Dated note, 2026-10-05: DP-1 to DP-4 ruled; DP-5
   added, open, for the two mechanisms the rulings need. Each anchor added on that date was
   read at `137bc817`, which was still `origin/main`.)*
4. **Repository literals read at `137bc817`:** every line in §"Task 0 at planning time" and
   §"Write set"; PL 9649's `ResolvedArtifact.factors` and Task 3b Step 3 read on its branch
   at `df8ba756`.
5. **What was not executed.** No test or code was run. The steps are sketches against names
   read at `137bc817` and PL 9649's branch; a step that does not run as written is a plan
   defect to report, not to work around.
