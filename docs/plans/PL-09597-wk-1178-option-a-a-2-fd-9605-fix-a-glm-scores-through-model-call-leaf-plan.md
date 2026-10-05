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
fixed in this slice, at the root (item 15).

**Dated note, 2026-10-05 (written 17:16:07 BST, pre-mint): DP-4 corrected to option (B).**
The 17:02:50 ruling's `money_minor` limb named a rounding that a `model_call` step cannot
declare. The maintainer (by delegation) corrected it in the entry headed *"2026-10-05
17:12:40 BST — CORRECTION to my 17:02:50 rounding ruling: OPTION (B); A-2 gains the
model-schema field; C4 stays (c); FR-249 carry text accepted"*, read in full by this
planner. Verbatim, its first three paragraphs:

> Verified at main (packages/model-schema/src/model_schema/rating.py): RatingExpressionStep (:293) declares `result_type: RatingResultType` (:296); RatingModelCallStep (:299) has NO result_type; only RatingOutputStep (:324) has `rounding: RoundSpec` (:327). 03 FR-226 (:112): "`output` steps declare rounding explicitly … Rounding is never implicit and never happens twice." My 17:02:50 "money_minor → the step's declared rounding (FR-226)" named a rounding a model_call cannot declare: WRONG mechanism, corrected here.

> RULING: OPTION (B). A model_call's output is ALWAYS an exact Decimal, never rounded at the model_call. ALL rounding stays on the output step, as FR-226 already says (no FR-226 amendment). RatingModelCallStep gains `result_type: RatingResultType` as a TYPE only (decimal | money_minor, for compile's FR-227 type checks; money_minor is a type label, not a rounding). Red first: a frequency GLM model_call returns the exact Decimal (~0.07, today 0); a money_minor-typed model_call feeding a non-money step is refused at compile as a type mismatch; the output step rounds once.

> CONSEQUENCE for A-2 (#1178): it now includes a MODEL-SCHEMA change, RatingModelCallStep.result_type. By CLAUDE.md §2 that lands in ONE commit with docs/contracts regenerated (FR-451, the drift check), the frontend client regenerated (`pnpm --dir frontend generate:api` in its gate), the 03 FR-222/FR-227 T-text naming the field, and its tests. Default for existing stored algorithms: `decimal` (a stored model_call without the field loads as decimal, and a migration test proves it), so no stored algorithm changes meaning. skills-map.md changes only if a tech dependency changes (none expected; the planner confirms). planner-a12fold: release DP-4's hold and write it as (B).

**Item 15 is written to this correction, not to the 17:02:50 text.** The correction settles
DP-5 (i).

**Dated note, 2026-10-05 (written 17:27:09 BST, pre-mint): the round-2 readings are
accepted.** From the entry headed *"2026-10-05 17:22:01 BST — A-1/A-2 round 2: readings (1)–(4) ACCEPTED; one question on compile's numeric interchangeability"*, read in full by this planner, its A-2 line
and its Readings line, verbatim:

> #1178 A-2 @de6e9a29, option (B): the red tests, item 16 (a stored model_call without the field loads as decimal; JSON payload, no Alembic), item 17 (one commit: the field, generated.json plus the 3 sub-graph schemas, generate:api, tests; skills-map unchanged) and the fixture fact (motor-ad-frequency@7 only validates, so not re-declared) are ACCEPTED.

> Readings: (1) Task 6 drafts the FR-222/FR-227 T-texts: ACCEPTED, and I accept or amend the wording at the ACK. (2) A validator refuses any result_type other than decimal | money_minor on a model_call: ACCEPTED. (3) "Feeding a non-money step" = a non-money OUTPUT step (the only consumer FR-227 types today); typing expression INPUTS is wider and a STOP: ACCEPTED, the narrower reading is what I meant for A-2. (4) +0.5 executor-day (unmeasured): noted for the 9 Oct fit check.

**Dated note, 2026-10-05 (written 17:29:39 BST, pre-mint): item 13's readings R1 to R5 are
ruled.** From the entry headed *"2026-10-05 17:27:55 BST — FD 9572 CAUSE: the sink fan-in plus
whole-context passThrough; RULING: (c) ALONE is the emergency slice; (R-b) is the root, in
PL 9567; one more case to measure; A-2 readings"*, read in full by this planner, its A-2 line,
verbatim:

> A-2 (#1178 @c3982ed6; MODEL_CALL_FEATURE_MAP_INVALID, 422, free on main): R1 (an unresolvable model_ref is left to compile): ACCEPTED. R2 (the OFFSET column is accepted beside the Factor slugs): ACCEPTED, as DP-3 needs. R3 (a GBM is checked against its Factors, or its feature_order when it has none): ACCEPTED. R4 (peril_structure_ref steps are not checked): ACCEPTED for A-2, and A-3 checks a structure's component models' feature maps (add it to A-3's plan). R5, the GAP: POST /api/v1/sub-graphs (sub_graphs.py:104) also saves model_call steps, so the SAME check applies there, via the same function, with its own red test, in A-2.

So R1 to R4 stand as written, and R5 brings `POST /api/v1/sub-graphs` into this slice
(item 18).

**Dated note, 2026-10-05 (written 17:36:25 BST, pre-mint): the sub-graph version route is in.**
From the entry headed *"2026-10-05 17:34:25 BST — FD 9572 fan-in measurement accepted: (c)
ALONE stands; A-2 create_sub_graph_version IN"*, item 3, read in full by this planner,
verbatim:

> 3. A-2 #1178 @7114be2e: create_sub_graph_version (backend/src/app/api/sub_graphs.py:53-60 at origin/main; your :127 is the service-side line) is IN, through the SAME item-18 function, with its own red test. The reason is R5's: every save path that writes a model_call step gets the check. I checked origin/main: the router has exactly two POSTs, create_sub_graph :38/45 and create_sub_graph_version :53/60. The planner confirms that create_algorithm's version path (if it is a separate route) is covered too.

Item 19 carries it.

**Every save path that writes a `model_call` step, confirmed at `4d3be141`:**
- **Rating algorithms: one path, `create_algorithm`.** The router has one write,
  `@router.post("/rating-algorithms")` → `create_rating_algorithm`
  (`backend/src/app/api/rating_algorithms.py:28-34`), calling `service.create_algorithm`
  (`:47`). A new **version** of an algorithm is the same route: the body carries `slug` and
  `version`, and `create_algorithm` (`backend/src/app/platform/rating_algorithms.py:94`)
  refuses an existing `(slug, version)` with 409 (`:107-121`).
  `RatingAlgorithmRow(` is constructed only at `platform/rating_algorithms.py:123`. Every
  other `RatingAlgorithmRow` use in `backend/src` is a `select` (`rating_versions.py:450-452`,
  `regression_suites.py:109-112`, `rating_algorithms.py:111-113` and `:142-144`), and
  `git grep -n -E 'update\(RatingAlgorithmRow|insert\(RatingAlgorithmRow' 4d3be141 --
  backend/src scripts examples` prints nothing. **So the algorithm version path is item 13's
  path, covered by the same function. There is no separate version route.**
- **Sub-graphs: two paths, both in.** The router has two POSTs: `create_sub_graph` (`:38`/`:45`)
  and `create_sub_graph_version` (`:53`/`:60`, `"/{slug}/versions"`). Each reaches `_write`
  (`backend/src/app/platform/sub_graphs.py:59`) through its service, `create_sub_graph`
  (`:104`, `_write` at `:122`) or `create_version` (`:127`, `_write` at `:140`). No other
  caller of `_write` exists.

So T1 and T2 (and T3, added since) are applied with the wording the lead accepts or amends at
the ACK; item 15's validator and its narrower reading stand; the +0.5 day is the lead's. The
entry's question on `_NUMERIC` is answered to the lead separately. A-2 types only the
`model_call`, as ruled, whatever the answer.

**Dated note, 2026-10-05 (written 17:22:22 BST, pre-mint): DP-5 (ii) ruled (a).** From the
entry headed *"2026-10-05 17:14:54 BST — FD 9572 placement accepted; WK-673 S4/S5/S6, A-1,
A-2 and CR-838 DECISIONS (1–8)"*, item 5, read in full by this planner. Verbatim:

> 5. A-2 DP-5 (ii): (a). The BACKEND algorithm save resolves each model_call's model_ref and refuses a feature_map naming anything but that model's Factor slugs, with a NEW 03 code (named in the RL, registered in errors.py; it serialises on the owned-codes tail per my rules). validate_algorithm stays pure.

There is no A-2 `RL-`, so the code's name is drafted in Task 6's texts (T1 and T3) for the
lead's ACK: **`MODEL_CALL_FEATURE_MAP_INVALID`**, 422. `git grep -n MODEL_CALL_FEATURE_MAP
4d3be141` prints nothing, so the name is free. Item 13 is written to the ruling.

**The offset reaches the model through B4's `feature_map`.** From the entry headed
*"2026-10-05 17:08:35 BST — A-3 / A-4 DP memo (handover/dp-memo-a3-a4-2026-10-05.md) RULED;
the reconciliation TOLERANCE set"*, item 7, verbatim:

> 7. DP-A3-5: (a). The frequency GLM's offset (exposure_years) comes through B4's feature_map, else MODEL_OFFSET_MISSING: consistent with my A-2 DP-3 (17:03:45).

**No live rounding case.** From the entry headed *"2026-10-05 17:07:00 BST — Rounding: LATENT
(no live case), carried by A-2; WK-673 S4/S5: start the DM memo NOW; E1's owner gap"*, its
first paragraph, verbatim:

> ROUNDING (auditor-mc, read-only at origin/main): NO live case. examples/ and golden.py have 0 model_call; the freMTPL2 demo algorithm (examples/fremtpl2/model.py:317-343) is s_in → s_expr → s_out; model_calls exist only in fixtures (scripts/bench-rating.py:235 `bench-freq`, a synthetic target; backend/tests/test_rating_algorithms.py:40,88; the pricing-core test boosters); a pinned GLM fails closed. LATENT, carried by A-2's declared-result-type fix; no finding. One loose end for A-2's plan: trace whether test_rating_algorithms.py's `motor-ad-frequency@7` (a frequency model on a risk_premium_minor output) SCORES or only validates; if it scores, A-2 re-declares that fixture's output type as part of its red-first change. RL 9588's composition (a Decimal prediction × edited/seed ratios, rounded once at the money_minor step; B1 after A-2): right.

Traced by this planner at `4d3be141`: `backend/tests/test_rating_algorithms.py`'s
`motor-ad-frequency@7` step (in `PRE_EDIT_VALID_ALGORITHM`, `:40-44`, and `valid_algorithm()`,
`:88-92`) **only validates**. Every test in the module calls
`POST /api/v1/rating-algorithms` (save) or `GET /api/v1/rating-algorithms/motor-gb@2/diff`;
none compiles, pins or scores. `git show 4d3be141:backend/tests/test_rating_algorithms.py |
grep -c -E 'score|compile_bundle|rating-versions|load_bundle|predict'` prints 0. So the
red-first change does not re-declare it. Under (B) the fixture omits `result_type` and loads as
`decimal`, and its save tests (`test_a_valid_algorithm_saves` and the others) pass unchanged.
That is item 16's backend evidence. The step feeds `s_office`, an `expression`, and no
`output` directly, so item 15's type refusal does not reach it.

## Status

`draft`. **DP-1 to DP-4 are ruled** by the maintainer (by delegation) in the 17:02:50 and
17:03:45 BST entries quoted above, and DP-4 is corrected to option (B) at 17:12:40 BST (dated
notes, 2026-10-05). **DP-5 (i) is settled by that correction, and DP-5 (ii) is ruled (a)** at
17:14:54 BST: the backend algorithm save refuses a non-Factor `feature_map` with a new `03`
code. The plan moves to `active` only
through a separate activation PR, after every activation need below holds.

*Dated note, 2026-10-05 (pre-mint), on the 18:51:33 BST entry: the save check of items 13,
18 and 19 is membership-only, NOT a completeness check. Completeness is compile-time,
decided by that entry and carried by PL 9494 / SL 9495 (working ids, #1216); item 13's
readings carry the full note.*

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
4a. **The ruling on DP-5 (ii)** *(added 2026-10-05, pre-mint)*. Item 13 cannot be written as
   a test until DP-5 (ii) names the check site and the code. DP-5 (i) is settled (17:12:40
   BST, option (B)). Item 15 needs nothing more. *Dated note, 2026-10-05: **held**, (a) at
   17:14:54 BST item 5. The code's name is accepted at the ACK with Task 6's T1 and T3.*
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
    entry; DP-5 (ii) (a), the 17:14:54 BST entry, item 5).
    `test_a_feature_map_naming_a_raw_column_is_refused_at_save` in
    `backend/tests/test_rating_algorithms.py`: a GLM is fitted and persisted (its Factors with
    slugs), and an algorithm whose `model_call` pins it with a `feature_map` value naming a
    raw column (a Factor's source column, not its slug) is posted to
    `POST /api/v1/rating-algorithms`. It answers `422` with `code ==
    "MODEL_CALL_FEATURE_MAP_INVALID"`, and the detail names the step, the value and the
    Model's ref. No row is written. The control: the same map naming the Factor's slug answers
    `201`. **Where:** `create_algorithm` (`backend/src/app/platform/rating_algorithms.py:94`),
    after `_issues_to_error`, resolves each `model_call`'s `model_ref` to its Model and the
    Model's Factors (the loaders `prediction.py:130-140` uses) and refuses a value outside
    them. `validate_algorithm` stays pure (the ruling). The code is registered in
    `RATING_ERROR_CODES` (`backend/src/app/errors.py:309`) and appended to `03` §5.1's
    owned-codes list (T3). **Red first:** at the base the raw-column map saves `201`.
    *Readings R1 to R5, ruled at 17:27:55 BST (dated note, 2026-10-05): R1 to R4 accepted
    as written; R5 in scope (item 18). The check is one function, called from both save
    paths.*
    - **(R1) A `model_ref` that resolves to no Model at save** is not refused by this check.
      The compile resolver and its maturity check refuse it later (FR-237, FR-20).
      Reason: today an algorithm saves before its models exist, and the module's own
      `motor-ad-frequency@7` fixtures save with no such Model. Refusing would break
      `test_a_valid_algorithm_saves` and change what save means.
    - **(R2) The offset column.** DP-3's precision feeds the offset's value "through the
      feature_map (e.g. exposure → log exposure)", and the offset column is not a Factor
      slug. So the accepted values are the Model's Factor slugs plus the column its spec
      declares as a `log_column` or `column` offset. Read literally, "anything but that
      model's Factor slugs" refuses the offset, and DP-3 could not be met.
    - **(R3) A GBM** is checked the same way, against its Factors' slugs. A GBM with no
      Factors (`predict_gbm`'s `factors=()` fallback, keyed by `feature_order`) is checked
      against `feature_order`.
    - **(R4) A `peril_structure_ref` step** is not checked here: it has no single Model, and
      A-3 owns its scoring.
    - **(R5) The sub-graph save.** `POST /api/v1/sub-graphs` (`create_sub_graph`,
      `platform/sub_graphs.py:104`) also saves `model_call` steps (a `SubGraphBody` carries
      `RatingModelCallStep`). *(Dated note, 2026-10-05: first written as "not changed …
      reported to the lead as a gap". Ruled at 17:27:55 BST: "the SAME check applies there,
      via the same function, with its own red test, in A-2". Item 18.)*
    - *Dated note, 2026-10-05 (pre-mint), on the maintainer's (by delegation) entry
      "2026-10-05 18:51:33 BST — Save-time completeness: DECIDED NOW as (b), completeness at
      COMPILE" (`channel/to-lead.md`): **this check is MEMBERSHIP-ONLY and is NOT a
      completeness check.** It refuses a `feature_map` value that the pinned Model does not
      accept (R2, R3). It does not refuse a map that leaves one of the Model's Factors, or
      one `feature_order` entry, unmapped, and none of items 13, 18 and 19 tests that.
      Completeness is decided by that entry as compile-time: `compile_bundle` refuses it,
      per component for a Peril Structure, with this item's code reused. It is ruled by
      RL 9491 and carried by PL 9494 / SL 9495 (working ids, #1216), which run after this
      slice. Nothing in this slice's scope, items or write set changes.*
14. **The offset's value comes from the quote** (DP-3 (a) with the precision, the 17:03:45
    entry). `test_the_offset_moves_the_glm_by_exactly_the_exposure` (new pricing-core module,
    a GLM with a `log_column` exposure offset): the same quote at exposure 1.0 and at 0.5
    differs by exactly the offset. The offset column (for the frequency GLM, `exposure_years`)
    reaches the model only through the step's `feature_map`, as B4's `model_call` will feed
    it (17:08:35 BST item 7, consistent with DP-A3-5 (a)); the test's map names it. The step
    is `decimal`, so both values are exact Decimals (item 15), and the assertion is on the
    linear predictor:
    `ln(value_1.0) − ln(value_0.5) == ln(1.0) − ln(0.5)`. *"Exactly" is read to float
    precision (`math.isclose(rel_tol=1e-12)`), because `predict_glm` computes in float and
    `(a + b) − (a + c)` is not bitwise `b − c`. If the maintainer meant bitwise, the dispatch
    reports it.* A quote missing the offset input, or a `feature_map` that does not map the
    offset column, is refused with `MODEL_CALL_FAILED` naming `MODEL_OFFSET_MISSING`
    (FR-255; `_offset`, `modelling/predict.py:144-195`): item 3, whose vehicle is that case.
    Red first: at the base the GLM is refused.
15. **A `model_call`'s value is always an exact Decimal; `result_type` is a type only; the
    output step rounds once** (DP-4 as corrected to option (B), the 17:12:40 BST entry, for
    every `model_call`, GBM included, not only a GLM; FR-222, FR-227, FR-226).
    - **Red first (the value):** `test_a_frequency_glm_model_call_returns_its_exact_rate`: a
      frequency GLM (Poisson, log link, mean about 0.07) scores about 0.07, never 0. At the
      base it scores 0 (`round(prediction)`, `runtime.py:567`), or is refused before that as
      a GLM. The red is recorded with whichever line prints.
    - **Golden at full precision:**
      `test_a_model_call_equals_predict_glm_at_full_precision`: the handler's value is the
      exact Decimal of `predict_glm`'s float on the same row (`Decimal(repr(x))`, FR-244's
      boundary rule), with no quantize and no `round()`, whichever `result_type` the step
      declares.
    - **Red first (the type):** `test_a_money_minor_model_call_feeding_a_non_money_output_is_refused`:
      a `model_call` declared `money_minor` whose produced name feeds an `output` declared
      `relativity` is refused with `RATING_TYPE_MISMATCH`, by `validate_algorithm`
      (`compile.py:366`) and by the bundle-time check. The control: a `model_call` declared
      `decimal` feeding an `output` declared **`decimal`** saves. *(Dated note, 2026-10-05,
      written 17:56:21 BST, pre-mint: the control was "declared `decimal`, the same graph saves",
      that is, a `decimal` `model_call` into a `relativity` output. OQ 9556's decision
      (17:42:06 BST, B3) refuses `decimal` → `relativity`, so that control would fail under
      PL 9521, the FD 9549 fix. The maintainer (by delegation) adopted this pre-mint change in
      the entry headed *"2026-10-05 17:49:25 BST — PL 9521 #1202 @15698eae: A-2's control
      changed PRE-MINT (yes); the /score vs batch coercion: (c) conditional, PLUS one check that
      decides whether it is a SEPARATE finding"*, item 1, verbatim:*

      > 1. A-2's control: the PRE-MINT CHANGE is ADOPTED and supersedes the second-merger flip in my 17:47:06 item 4 for this control. #1178 item 15's control becomes a decimal model_call into a DECIMAL output (legal under B3), which still proves the rule is model_call-scoped. PL 9521 drops its flip line for this control and names the change instead. The same planner does both pre-mint.

      *The control still shows that the refusal comes from the `money_minor` declaration and not
      from the `model_call` itself: a `decimal` `model_call` into a legal output saves.)* At the base the step cannot declare the field (`extra="forbid"`), and
      a `money_minor` producer feeding `relativity` passes anyway, because `_compatible`
      treats every `_NUMERIC` type as interchangeable (`compile.py:57`, `:124`). The change:
      `producer_types` (`:95`) types a `model_call`'s produced names by its `result_type`,
      and the FR-227 output check (`_check_result_types`, `:158`, through
      `output_type_issues`, `:132`) refuses a `money_minor` value **produced by a
      `model_call`** that feeds an `output` declared other than `decimal` or `money_minor`.
      `_compatible` itself is not changed, so an `expression` producer keeps today's
      behaviour. *(Dated note, 2026-10-05, 17:28:44 BST: this said "`_compatible` refuses
      `money_minor` into any type other than …", which would also have retyped every
      `expression` producer. That is wider than the ruling ("A-2 only types the
      model_call", the 17:22:01 BST entry), and the expression case is reported to the lead
      as a gap with its own owner.)* *The planner's reading, accepted at 17:22:01 BST:
      "a non-money step" is an `output` consuming it. FR-227's check today compares only an
      `output`'s declared type with its producer, and an `expression` does not type its
      inputs. This slice adds no input typing to `expression`. If the ruling means that, it
      is a wider change: STOP and report it.*
    - **Red first (the single rounding):** `test_the_output_step_rounds_a_model_call_once`:
      a `money_minor` `model_call` (a severity GLM) feeds an `expression` that multiplies it
      by a non-integer factor, declared `money_minor`, which feeds an `output` declared
      `money_minor` with `rounding {"mode": "half_even", "dp": 0}`. The served output equals
      `(Decimal(repr(prediction)) × factor)` quantized once, half-even. At the base the handler
      has already rounded, so the base rounds twice. The test first asserts that, for its
      chosen prediction and factor, rounding twice and rounding once differ, so it cannot
      pass vacuously. For example, 1234.4 × 1.1 gives 1358 rounded once and 1357 rounded
      twice. The ledger records the values.
    - **The field (`model-schema`):** `RatingModelCallStep` (`model_schema/rating.py:299`)
      gains `result_type: RatingResultType = "decimal"`. It accepts `decimal` or
      `money_minor` and refuses any other value at validation, naming FR-227. *The planner's
      reading of the ruling's parenthetical "(decimal | money_minor, …)". No `rounding` field
      is added; FR-226 is unchanged.*
    - **The docstring:** the "provisional convention" text (`runtime.py:521-525`) is removed,
      and the handler's docstring cites the 17:12:40 BST entry by its header. Check:
      `git grep -n "provisional convention" -- packages/pricing-core/src/pricing_core/rating/runtime.py`
      prints nothing.
    - **How the exact value crosses back into the engine** (FR-273: the binding refuses a
      `Decimal` input and takes a `str` as a string; FR-244: outputs return as floats and
      `_round_minor` reads them with `Decimal(repr(x))`) is read at Task 0. The handler
      returns the unrounded value in the form the binding carries as a number. If no form
      carries it exactly, STOP and report it.
    - Existing tests that assert a GBM `model_call`'s integer value (the old `round()`) change
      under the ruling. Each is listed in the ledger with its old and new assertion.
16. **A stored algorithm without the field still means what it meant** (17:12:40 BST:
    "a stored model_call without the field loads as decimal, and a migration test proves
    it").
    `test_a_stored_model_call_without_result_type_loads_as_decimal` (in
    `packages/model-schema/tests/test_rating_algorithm.py`): a `RatingAlgorithm` payload
    written before the field (a `model_call` step with no `result_type`) validates, and its
    step's `result_type == "decimal"`. In `backend/tests/test_rating_algorithms.py`, a row
    stored with the old payload is read back through the service and its step is `decimal`.
    No Alembic migration is written, because the algorithm is stored as its JSON payload and
    the default is the model's. The test is that proof. **Red first:** at the base
    `RatingModelCallStep` has no `result_type`, so the read-back assertion fails with
    `AttributeError`.
17. **The contracts and the client are regenerated in the same commit as the field**
    (`CLAUDE.md` §2; FR-451). `uv run python scripts/generate-contracts.py --check` exits 0.
    The regenerated files are the ones `git grep -l RatingModelCallStep -- docs/contracts`
    lists at `4d3be141`: `docs/contracts/openapi/generated.json` and
    `docs/contracts/schemas/generated/sub-graph-body.schema.json`, `sub-graph-create.schema.json`
    and `sub-graph.schema.json`. `pnpm --dir frontend generate:api`, `type-check` and `build`
    pass; `frontend/src/api/generated` is VCS-ignored and not committed. The hand-written
    `docs/contracts/schemas/rating-algorithm.schema.json` already admits `result_type` on
    every step (`:50`). It is edited only if `backend/tests/test_contracts.py`'s guard
    requires it (`contract-guard`), and the ledger says which.
18. *(Added 2026-10-05, pre-mint, on the 17:27:55 BST ruling of R5.)* **The sub-graph save
    refuses a raw-column `feature_map` with the same code.**
    `test_a_sub_graph_whose_model_call_names_a_raw_column_is_refused` in
    `backend/tests/test_sub_graphs_api.py`: a GLM is fitted and persisted, and a
    `SubGraphCreate` whose `model_call` pins it with a `feature_map` value naming a raw column
    is posted to `POST /api/v1/sub-graphs`. It answers `422` with `code ==
    "MODEL_CALL_FEATURE_MAP_INVALID"`, the detail names the step, the value and the Model's
    ref, and no row is written. The control: the same map naming the Factor's slug answers
    `201`. **Red first:** at the base the raw-column map saves `201`. **One function:** the
    check item 13 adds is one function, defined once in
    `backend/src/app/platform/rating_algorithms.py` beside `create_algorithm`, taking the
    session, the workspace and the steps. `create_algorithm` and `create_sub_graph` both call
    it inside their unit of work, before the row is written. R1 to R4 hold for both callers.
    *(Dated note, 2026-10-05: this said `create_version` was "not ruled, reported to the
    lead". It was ruled in at 17:34:25 BST, item 3: item 19.)*
19. *(Added 2026-10-05, pre-mint, on the 17:34:25 BST entry's item 3.)* **The sub-graph
    version save refuses a raw-column `feature_map` with the same code.**
    `test_a_sub_graph_version_whose_model_call_names_a_raw_column_is_refused` in
    `backend/tests/test_sub_graphs_api.py`: a sub-graph's version 1 exists, a GLM is fitted
    and persisted, and a `SubGraphBody` whose `model_call` pins it with a `feature_map` value
    naming a raw column is posted to `POST /api/v1/sub-graphs/{slug}/versions`
    (`create_sub_graph_version`, `api/sub_graphs.py:53-60`). It answers `422` with `code ==
    "MODEL_CALL_FEATURE_MAP_INVALID"`, the detail names the step, the value and the Model's
    ref, and no version 2 is written. The control: the Factor-slug map answers `201` with
    version 2. **Red first:** at the base the raw-column map writes version 2. `create_version`
    (`platform/sub_graphs.py:127`) calls item 13's one function inside its unit of work,
    before `_write` (`:140`). R1 to R4 hold.

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
  DP-4's and is not changed silently. *(Dated note, 2026-10-05: DP-4 is ruled, corrected to
  option (B) at 17:12:40 BST. A `model_call`'s value is always an exact Decimal, and only an
  `output` step rounds, once (FR-226 unchanged, NFR-496). Item 15.)*
- **A `model-schema` shape changes in one commit** *(added 2026-10-05)* (`CLAUDE.md` §2): the
  field, the regenerated `docs/contracts/`, the `03` texts and the tests land together
  (items 15 to 17). `docs/skills-map.md` is not edited, because no tech dependency changes.
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
| `03` | FR-227 | A `model_call` declares `result_type` (`decimal` default, or `money_minor`), and a `money_minor` one feeding a non-money output is refused *(added 2026-10-05, DP-4 as corrected)* | `req("FR-227")` on items 15, 16 |
| `03` | FR-226 | A `model_call` is never rounded; the `output` step rounds once *(added 2026-10-05, DP-4 as corrected)* | `req("FR-226")` on item 15 |

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

*Dated note, 2026-10-05 (pre-mint; corrected 17:16:07 BST to DP-4 option (B)): the rulings
add writes. They supersede "Not written: `packages/model-schema/`" and "any `frontend/src`
file" above.*

| Path | Change *(added 2026-10-05)* |
|---|---|
| `packages/model-schema/src/model_schema/rating.py` | edited: `RatingModelCallStep` (`:299`) gains `result_type` (item 15) |
| `packages/model-schema/tests/test_rating_algorithm.py` | appended: item 16's model test, and item 15's field refusal |
| `docs/contracts/openapi/generated.json`, `docs/contracts/schemas/generated/sub-graph-body.schema.json`, `sub-graph-create.schema.json`, `sub-graph.schema.json` | regenerated (item 17) |
| `docs/contracts/schemas/rating-algorithm.schema.json` | read; edited only if the contract guard requires it (item 17) |
| `frontend/src/api/generated/` | regenerated in the gate; VCS-ignored, not committed |
| `packages/pricing-core/src/pricing_core/rating/compile.py` | edited: `producer_types` (`:95`), `_check_result_types` (`:158`) / `output_type_issues` (`:132`), for a `model_call` producer only; `_compatible` (`:124`) is not edited (item 15; dated note, 17:28:44 BST) |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | `_model_call_handler`: the GBM branch's `round()` too, and the docstring (item 15) |
| `backend/tests/test_rating_algorithms.py` | appended: item 16's read-back test. The `motor-ad-frequency@7` fixtures are not edited |
| `docs/specs/03-rating-engine.md` | FR-222 row (`:108`) and FR-227 row (`:113`), §3.2: one dated amendment each, text T1 and T2 (Task 6) |
| `backend/src/app/platform/rating_algorithms.py` | edited: `create_algorithm` (`:94`) gains the `feature_map` check after `_issues_to_error` (item 13; DP-5 (ii) (a)) |
| `backend/src/app/errors.py` | edited: `RATING_ERROR_CODES` (`:309`), `MODEL_CALL_FEATURE_MAP_INVALID` appended |
| `backend/tests/test_rating_algorithms.py` | appended: item 13's test and control, and item 16's read-back |
| `backend/src/app/platform/sub_graphs.py` | edited: `create_sub_graph` (`:104`) and `create_version` (`:127`) each call item 13's check before `_write` (items 18 and 19; R5, 17:27:55 BST; 17:34:25 BST item 3) |
| `backend/tests/test_sub_graphs_api.py` | appended: items 18's and 19's tests and controls |
| `docs/specs/03-rating-engine.md` §5.1 | the owned-codes list (`:928` onward), T3 appended at its tail |

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

*Rows added 2026-10-05 (17:16:07 BST, pre-mint) for the writes the rulings add. Each was
read from the plan file on its branch (open PRs listed at 17:15 BST), grepped for
`model_schema/rating.py`, `docs/contracts`, `generate-contracts` and `03-rating-engine` in its
write-set rows.*

| Other slice (Work; source) | Shared path | Them | Us | Class → consequence |
|---|---|---|---|---|
| **PL 9688**, FD 9707 fix (#1145; WK-673) | `03` §3.2 | FR-221 row (`:107`), a dated amendment | FR-222 (`:108`), FR-227 (`:113`) | adjacent rows of one section; the maintainer serialised the same adjacency for S5 (17:07:00 BST) → **SERIALISE** |
| **PL 9683**, FD 9708 fix (#1140; WK-1178) | `03` §3.2; `model_schema/rating.py` | FR-223 row (`:109`); `RatingVersionCreate` | FR-222, FR-227; `RatingModelCallStep` | already ahead of A-2 through A-1 (activation need 3) → no concurrency |
| **PL 9590**, WK-673 S5 (#1181) | `03` §3.2; `model_schema/rating.py`; `docs/contracts/` generated | FR-224 row (`:110`); `RatingVersionEvidence`; regenerated | FR-222, FR-227; `RatingModelCallStep`; regenerated | §3.2 adjacency → **SERIALISE**; the classes differ; generated files are regenerated, never hand-merged |
| **PL 9595**, A-3 (#1174; WK-1178) | `03` §3 step table (`:100`) | the `model_call` row | not edited (T1/T2 are on `:108`/`:113`) | **plan dependency**: A-3 consumes this slice, and its `:100` text must name the field this slice adds |
| **PL 9610**, WK-1250 S2 (#1170) | `model_schema/rating.py`; `rating-algorithm.schema.json` | `Pins`, `SubGraphRef`, `_graph_invariants`, `AlgorithmDiff`; the mount's port map | `RatingModelCallStep`; the hand-written schema only if the guard needs it | different classes → ALLOWED one-sided with the dispatch record; the hand-written schema, if both edit it → **SERIALISE** (already serialised on `compile_bundle`) |
| **PL 9609**, WK-1250 S3 (#1173) | `model_schema/rating.py`; `rating-algorithm.schema.json` | `SubGraphRef.purposes`; `purposes` on the mount | as above | as above |
| **PL 9713**, WK-675 S2 (#1131) | `model_schema/rating.py`; `rating-algorithm.schema.json` | `RatingAlgorithm` | as above | different classes → ALLOWED one-sided with the dispatch record; the hand-written schema → **SERIALISE** if both edit it |
| **PL 9689**, WK-673 S3 (#1138) | `model_schema/rating.py` | `AlgorithmDiff` | `RatingModelCallStep` | already serialised on `compile_bundle` |
| **The owned-codes tail and `RATING_ERROR_CODES`** *(added 2026-10-05, DP-5 (ii) (a))*: PL 9649 (#1152, `CONTROL_FACTOR_IN_RATEABLE_PATH`), PL 9683 (#1140, `MODEL_REFERENCE_MODE_INCONSISTENT`), PL 9578 (#1186, WK-675 S3, the same code), PL 9591 (#1176, `ATTRIBUTION_RECONCILIATION_FAILED`), PL 9689 (#1138, the list's tail), PL 9595 (#1174, `:933`) | `03` §5.1 owned-codes list; `errors.py` `RATING_ERROR_CODES` | one code appended each | `MODEL_CALL_FEATURE_MAP_INVALID` appended | the same existing object's tail → **SERIALISE**, as the 17:14:54 entry says ("it serialises on the owned-codes tail per my rules"); PL 9649 and PL 9683 already precede A-2 |
| **`create_algorithm`** *(added 2026-10-05)* | `backend/src/app/platform/rating_algorithms.py` | read in each plan file's write set (the same sweep as above): no open plan edits it | edited | none found; the dispatch re-reads it |
| **`create_sub_graph`** *(added 2026-10-05, 17:29:39 BST)* | `backend/src/app/platform/sub_graphs.py` | PL 9610 (#1170) cites the resolver (`:202-213`) as a fact and edits no function here; no other open plan names the file in a write-set row | edited | none found; the dispatch re-reads it (WK-1250 S2 and S3 are near this module) |
| **PL 9616**, FD-1416 fix (#1168; WK-1178) and **PL 9591**, WK-673 S4 (#1176) | `scripts/generate-contracts.py`; generated contracts | `GENERATED_SHAPES` keys; regenerated | not edited (`RatingModelCallStep` is in no `GENERATED_SHAPES` key; it reaches `generated.json` through referenced shapes); regenerated | generated files exempt (regenerate on the merge base); PL 9616 same Work → `RL 9620` (a)/(b) written |

Every other open plan (#1127 PL 9716, #1131 PL 9713, #1140 PL 9683, #1146 PL 9662, #1161 PL
9624, #1164 PL 9629, #1165 PL 9617, #1168 PL 9616) names none of this write set (each plan
file read from its branch at the snapshot above, grepped for every path in the table).

### Size

Medium: about one and a half executor days (the sizing memo's A-2 row, 1 / 1.5 / 2.5). Six
tasks after Task 0, one exclusive measurement, one full two-half gate run. The backend test
fits a GLM through the real Job, so it needs Postgres and MinIO.

*Dated note, 2026-10-05 (pre-mint): the 17:03:45 and 17:12:40 BST rulings add items 12 to 17,
including a `model-schema` field with regenerated contracts and the frontend client. The
estimate above predates them and is **not** re-sized here. The planner's estimate of the
increment is about +0.5 executor-day, unmeasured, for the lead and the Friday 9 Oct fit
check.*

## Decision points

*Dated note, 2026-10-05 (pre-mint):* **DP-1 to DP-4 are ruled** by the maintainer (by
delegation) in the 17:02:50 and 17:03:45 BST entries quoted in §"The maintainer's decisions
this plan rests on, quoted": DP-1 (a), DP-2 (b), DP-3 (a) with a precision, and DP-4 settled
at the root, against this plan's (a). The rows below were written before the rulings and are
kept as written. Items 12 to 17 carry what the rulings add. **DP-5 was added on the same
date. Its part (i) is settled by the 17:12:40 BST correction (option (B), item 15); part
(ii) is open.**

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | How a GLM pin's Factors, Bandings and Groupings travel in the Bundle | (a) `ResolvedArtifact` gains `bandings` and `groupings` beside PL 9649's `factors`; `compile_bundle` writes each under its own `ArtifactRef` string in `resolved_payloads`, for a GLM `model_call` pin only; (b) a new `Bundle` field holding them per model ref; (c) keys nested inside the model's payload | **(a)**: the Bundle's shape and `bundle_hash` are unchanged; each input is its `model-schema` class's dump under the reference grammar every payload already uses. (b) adds a second hand-written shape to `Bundle`; (c) is what PL 9649 Task 3b Step 3 refused (*"a key added beside it is a second, hand-written shape inside a Bundle"*) | decision-maker | Tasks 2, 3 |
| **DP-2** | What `feature_map`'s values name for a GLM. `03` §4.1's `RatingAlgorithm` example shows `{"driver_age": "driver_age", …}` (`03:267`); the GBM path keys the frame by Factor slug (`feature_order`); `resolve_factors` reads each Factor's `source_columns` | (a) for a GLM the values name the frame's columns, i.e. the Factors' `source_columns` and the offset column; (b) the values are Factor slugs for both kinds, and the runtime renames each slug to its Factor's source column(s) | **(b)**: one meaning for one field across model kinds, and the author maps to the model's own vocabulary (its Factors), which the Model already names. (a) gives `feature_map` two meanings by model type. Under (b), an interaction Factor is fed through its operands' slugs, and the offset column is mapped under its own column name; a `03` dated note words it (Task 6) | decision-maker | Task 4 |
| **DP-3** | A GLM whose spec has `offset.kind == "model"` (FR-116) | (a) carry the source model and its inputs too, and compute its `linear_predictor` per quote, as `/predict` does (`prediction.py:236-246`); (b) refuse at compile with a named code, and a dated note on FR-193 | **(a)**: FR-193 says *any* persisted Model scores, and the backend already resolves the source (`resolve_offset_model`, `modelling.py:950`). (b) narrows a requirement to fit a slice | decision-maker | Tasks 2, 3, item 6 |
| **DP-4** | The value a GLM `model_call` yields. The GBM convention is `round(prediction)`, provisional, on the assumption the model predicts on the money-minor scale (0.2). A frequency GLM's `μ` (claims per unit exposure) rounds to 0 | (a) keep the convention for a GLM, unchanged; this slice's golden uses a GLM on the money-minor scale (a severity or burning-cost model) and the frequency case is A-3's and AN's (the double-count ruling); (b) emit the unrounded value for a `model_call` and round only at a `money_minor` boundary | **(a)** for this slice: changing the money convention is FR-250/NFR-496 scope, not FD 9605's. The plan records the hazard for A-3, which composes frequency × severity through `assemble_risk_premium` before any rounding | decision-maker | item 1's expected value |
| **DP-5** *(added 2026-10-05, open)* | The two mechanisms the rulings rest on, which do not exist at `137bc817`. **(i)** DP-4 reads the `model_call` step's "DECLARED result type" and, for `money_minor`, "the step's declared rounding (FR-226)". The step declares neither (0.10). **(ii)** DP-2 refuses a raw-column `feature_map` "at save, with its code". Save-time validation does not resolve the pin that names the Factors (0.11), and no code is named | **(i)** (a) `RatingModelCallStep` gains a required `result_type: RatingResultType` and a `rounding: RoundSpec`, required when `money_minor` and refused otherwise. `03` §3's row names both, and every `model_call` fixture declares them. (b) The same, with `result_type` optional and defaulting to `money_minor` with half-even to the unit, which is today's behaviour. (c) No new field: a `model_call`'s value is always `decimal`, and only an `output` step rounds. **(ii)** (a) The backend's algorithm save resolves each `model_call`'s `model_ref` after `validate_algorithm`, and refuses with a new code added to `03`'s error catalogue. (b) The check runs at compile, the first point that resolves the pin, with a new code. (c) As (a) or (b), with the existing `VALIDATION_FAILED` | **(i) (a).** FR-227 already says "Every step declares its result type", and the contract already admits the field, so the gap is `model-schema`'s. (b) keeps a hidden default, the "provisional convention" the ruling removes. (c) drops the ruling's `money_minor` limb. **(ii) (a) with a new code.** It is the only option that is literally "at save". The step pins `model_ref` exactly, so the save can read the Model's Factor slugs. A named code follows FR-255's typing. (b) moves the refusal to compile. Both are the maintainer's (by delegation): each changes a shape or a catalogue | the maintainer (by delegation). *(Dated note, 2026-10-05: **(i) settled** at 17:12:40 BST as the lead's option (B), "model_call output always exact, rounding only at the output step", with a type-only `result_type`. That is none of (a) to (c) above, and items 15 to 17 carry it. **(ii) ruled (a)** at 17:14:54 BST item 5: the backend save, a new `03` code, item 13.)* | item 13; activation need 4a |

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
- [ ] **Step 3a:** *(Added 2026-10-05.)* Items 12 to 16, each red by its stated cause. Item
  13 is written to DP-5 (ii) (a), with the code T1 and T3 name, in
  `backend/tests/test_rating_algorithms.py` (Postgres and MinIO, for the fitted GLM). Item
  18 is written in `backend/tests/test_sub_graphs_api.py` *(added 2026-10-05, R5)*, and item 19
  beside it *(added 2026-10-05, 17:34:25 BST item 3)*. Item 15's field test and item 16 go in
  `packages/model-schema/tests/test_rating_algorithm.py`; item 16's read-back goes in
  `backend/tests/test_rating_algorithms.py`, beside the `motor-ad-frequency@7` fixtures,
  which are not edited (they only validate).
- [ ] **Step 3b:** *(Added 2026-10-05.)* One commit for the shape (items 15 to 17,
  `CLAUDE.md` §2): `RatingModelCallStep.result_type`; `uv run python
  scripts/generate-contracts.py`; `pnpm --dir frontend install --frozen-lockfile && pnpm
  --dir frontend generate:api`; Task 6's T1 and T2; item 16 green. Commit: `feat:
  model_call declares a type-only result_type, decimal by default (FR-227; FD 9605)`.
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
  column is taken from the quote through the `feature_map`, and the value is the exact
  Decimal, never rounded, item 15 (option (B)). The same rule replaces
  `round(prediction)` in the GBM branch.)* Any `ModellingError` or
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
  ledger says so. *(Dated note, 2026-10-05: DP-3 (b) was not taken. The 17:12:40 BST
  correction orders "the 03 FR-222/FR-227 T-text naming the field" and gives no wording.
  This planner **drafts** T1 and T2 below. They are proposals, applied byte for byte only
  once the lead's ACK or a ruling accepts them. If they are amended, the amended text is
  applied.)*
  - **T1, appended to FR-222's row (`03:108`):** *(Amended 2026-10-05, the maintainer's (by
    delegation) entry headed `2026-10-05 17:12:40 BST — CORRECTION to my 17:02:50 rounding
    ruling: OPTION (B); …`: a `model_call` step also declares `result_type`, `decimal` or
    `money_minor`, and a step stored without it is `decimal`. Its value is the model's
    prediction as an exact decimal, and it is never rounded at the step. `money_minor` is a
    type for FR-227's checks, not a rounding; every rounding is an `output` step's (FR-226).
    Amended 2026-10-05, the entry headed `2026-10-05 17:14:54 BST — FD 9572 placement
    accepted; …`, item 5, and the entry headed `2026-10-05 17:27:55 BST — FD 9572 CAUSE: …`
    (R2, R5), and the entry headed `2026-10-05 17:34:25 BST — FD 9572 fan-in measurement
    accepted: …`, item 3: when a Rating Algorithm, a Sub-graph or a Sub-graph version is
    created, each `model_call`'s
    `model_ref` is resolved, and a `feature_map` value that is neither one of that Model's
    Factor slugs nor the column its spec declares as the offset is refused with
    `MODEL_CALL_FEATURE_MAP_INVALID` (422).)*
  - **T2, appended to FR-227's row (`03:113`):** *(Amended 2026-10-05, the same entry: a
    `model_call` step's `result_type` types the names it produces for this check. A
    `money_minor` `model_call` whose value feeds an output declared with a type other than
    `decimal` or `money_minor` is refused with `RATING_TYPE_MISMATCH`.)*
  - **T3, appended at the tail of §5.1's owned-codes list (`03:928` onward):**
    `MODEL_CALL_FEATURE_MAP_INVALID` *(added 2026-10-05, WK-1178 A-2 — **422** at
    `POST /api/v1/rating-algorithms`, `POST /api/v1/sub-graphs` and
    `POST /api/v1/sub-graphs/{slug}/versions`: a `model_call`'s
    `feature_map` names something other than its Model's Factor slugs or its offset column
    (FR-222, amended); the entries headed `2026-10-05 17:14:54 BST — FD 9572 placement
    accepted; …`, item 5, `2026-10-05 17:27:55 BST — FD 9572 CAUSE: …` and `2026-10-05
    17:34:25 BST — FD 9572 fan-in measurement accepted: …`, item 3)*. The tail is serialised (§"Write set").

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
   written without a ruling (Task 6). *(Dated note, 2026-10-05: DP-1 to DP-4 ruled, DP-4
   corrected to option (B) at 17:12:40 BST; DP-5 added, its part (i) settled by that
   correction and part (ii) open. Task 6's T1 and T2 are drafts for acceptance. The anchors
   added at 17:08:21 were read at `137bc817`, and those added at 17:16:07 at `4d3be141`
   (`origin/main` after #1127, which touched only `docs/`).)*
4. **Repository literals read at `137bc817`:** every line in §"Task 0 at planning time" and
   §"Write set"; PL 9649's `ResolvedArtifact.factors` and Task 3b Step 3 read on its branch
   at `df8ba756`.
5. **What was not executed.** No test or code was run. The steps are sketches against names
   read at `137bc817` and PL 9649's branch; a step that does not run as written is a plan
   defect to report, not to work around.
