---
id: PL-8030
family: plan
kind: map
title: WK-1178 — FD-1723's two HIGH limbs, a capped GLM spec fits capped (FR-127) and the banding check runs at fit (FR-100), SL-8031 — a dated Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: 8eaf6d5f9cd4204e1e077b44069d4afd395f1461
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1542, SL-1543, PL-1674, SL-1675, FD-1723]
---

# PL-8030 — WK-1178: FD-1723's two HIGH limbs. A capped GLM spec fits capped (FR-127), and the banding check runs at fit (FR-100) (SL-8031)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1674`, this delta `relates:` the records it builds on:
> `PL-1542` and `SL-1543` (A-4, whose guard test this slice interacts with), and `PL-1674` and
> `SL-1675` (the FR-111 weight rule, whose `weights.py` is this slice's pattern and whose
> exclusion runs before both new checks). It adds **one slice row**, SL-8031 (working id), under
> `### WK-1178` in [`../roadmap.md`](../roadmap.md). REQUIRED SUB-SKILL:
> subagent-driven-development (recommended) or executing-plans, task by task. Steps use checkbox
> (`- [ ]`) syntax. The executor also binds:
> - `test-driven-development`: every red below is seen red **by its cause** on main before the
>   code that turns it green;
> - `python-test`: the `req` marker and the negative tests;
> - `python-package`: `pricing-core` stays standalone (ADR-703);
> - `spec-change`: Tasks 2 and 5;
> - `contract-schema` and `contract-guard`: Task 6 (DP-B2 (a), ruled);
> - `vue-frontend`: Task 6's generated-types step only (the generated client is never
>   hand-written; no file under `frontend/src/` is edited);
> - `fastapi-service`: Task 7's error mapping;
> - `dev-commands`: `uv sync --all-packages`, `scripts/run-small.sh` for the one-file runs, and
>   both gate halves (the frontend half is not optional here: Task 6 changes the generated
>   contract the frontend compiles against);
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

Filed under **working id 8030**. Its slice row is **working id 8031** (`draft`). Both were
reserved by the lead in `handover/eta.md` (team-lead to planner-fd8027, 2026-10-14, "PL 8030 /
SL 8031 reserved for you"). Written 2026-10-14 by the planner (seat planner-fd8027).
**Tree read:** `origin/main` `8eaf6d5f9cd4204e1e077b44069d4afd395f1461` (#1300, committed
2026-10-14T11:25:34+01:00). Every `file:line` below is at that tree unless marked otherwise. The
executor re-reads each one at its base (Task 0). The finding is FD-1723 (working id FD 8027 when this plan was
written; minted in D17, #1307), read in full at `origin/fd-8027-closure-gap-p1-2026-10-14` @`00b683ee`.

## Authority

All six entries are the maintainer's (by delegation), in `to-lead.md`. The first three were read
in full at 2026-10-14 11:41:12 BST, when the plan was first written; the fourth, which rules this
plan's decision points, was read in full after it was logged; the fifth, which corrects DP-B2's
reading, was read in full after it was logged, for this amendment (seat planner-fd8040); the sixth, which rules
Task 5's FR-100 clause, likewise.

- **"2026-10-14 11:06:52 BST — D-list line-read RULED"**, item 2: *"CLOSED-PHASE PARTIAL → ONE
  closure-gap FD … **Any HIGH limb is fixed in P2.**"*, with FR-100 named first: *"`check_banding`
  has no caller in the fit path, so a fit may use bands that no longer match the data (RL-1615's
  stale-band class)"*.
- **"2026-10-14 11:28:56 BST — FD 8027 severity → HIGH"**, which says of the two limbs:
  > - **FR-127 GLM limb:** glm.py never reads `loss_treatment`; a capped GlmSpec fits UNCAPPED while its spec and spec_hash say capped. That is silent wrong-model evidence, the FD-1660 class.
  > - **FR-100:** `check_banding` has no fit-path caller (the stale-band class).
  >
  > Both are FIXED IN P2 under WK-1178, red first (a capped GlmSpec fit asserts capped behaviour, red on main; a banding whose data moved is refused at fit, red on main).

  That entry also **rules the FD's apply-or-refuse choice for `capped`**: *"a capped GlmSpec fit
  asserts capped behaviour"*. The cap is applied, as `fit_gbm` applies it. Only `spliced` and
  `excess` are refused by name, as `fit_gbm` refuses them. This is not a decision point here.
- **"2026-10-14 11:29:53 BST — G2 check result ACCEPTED: the FR-127 GLM fix stays OFF the G2
  path, conditionally; the guard ADOPTED"**, quoted in full:
  > Accepted on your cited evidence: PL-1542:426-431 declares no `loss_treatment` (so `kind = "none"`, modelling.py:759/:836); DP-A4-3 ruled (x), large loss UNCAPPED on the STRUCTURE's `large_loss` (perils.py:143/:214), not the GlmSpec; SL-1543 prep a0acb7a6 declares neither. No model says capped while fitting uncapped.
  > **Condition (binding):** if Task 0 Step 4's DP-A4-3 probe fails (|ratio − 1| > 0.05) and (y) capped becomes the answer, SL-1543 STOPs. The FR-127 GLM fix JOINS the G2 path and merges BEFORE SL-1543 resumes, and the G2 ETA is restated.
  > **Guard ADOPTED** in the SL-1543 GO brief and as a slice test: assert the A-4 severity spec's `loss_treatment.kind == "none"` AND the AD structure's `large_loss` is the uncapped treatment. A capped choice therefore fails a test rather than slipping in. If DP-A4-3 later switches to (y), the test changes only together with the FR-127 fix's merge, cited in the LG.

  The FR-110 lines of the 11:28:56 entry (NB θ, `power(k)`) are **not this slice's**. They are a
  MEDIUM limb of FD-1723 and go into a separate WK-1178 delta.
- **"2026-10-14 11:52:51 BST — PL 8030/SL 8031 DPs ruled; SL-1543 fixture fix accepted; NEW
  candidate: the recipe cast silently nulls unparseable values (re lead 11:51:03 / 11:52:02)"**,
  item (2), quoted in full (items (1), (3) and (4) are not this plan's):
  > **(2) PL 8030 + SL 8031 @ffc67de7 (FD 8027's HIGH limbs):**
  > - DP-L1 → its own module, taking the arm's error class (the weights.py:91-97 pattern). OK.
  > - **DP-L2 → (a) fix EBM here** (ebm.py:209 ignores loss_treatment, the same FR-127 class); an auditor adds the EBM limb to FD 8027 before mint.
  > - **DP-B1 → (a)** the training rows actually fitted, after FR-111's weight-0 exclusion.
  > - **DP-B2 → (a) a typed field on the fit results.** 02 FR-100: "every band must meet configurable minimum exposure and minimum claim count, or fitting **warns (default)** or fails (if configured). Empty bands always fail." The warning IS the default behaviour, so (c) "defer warnings" would leave FR-100's default unbuilt. Through model-schema, with the contract regenerated; the API ACK checks the shape.
  > - DP-B3 → (a). OK.
  > - **DP-G1 →** the Task 0 Step 3 probe decides; on ANY BAND_EMPTY for the A-4 severity GLM → STOP to me before code (a G2 interaction).
  > - DP-S1 → OK.

- **"2026-10-14 12:05:33 BST — The rename confirmed working; DP-B2's field must be STRUCTURED;
  run-small verdicts OK; audit:read closed (re lead 12:05:11)"**, its PL 8030 bullet, quoted in
  full (the other bullets are not this plan's). It **corrects** this plan's reading of the
  11:52:51 DP-B2 ruling, which had typed the field `tuple[str, ...]`:
  > - **PL 8030 DP-B2: `banding_warnings: tuple[str, ...]` is NOT what I ruled.** "A typed field" means a model-schema type a reviewer or UI can act on, not free text. Define `BandingWarning` in model-schema with: banding ref, band label/index, `measure` (exposure | claim_count, an enum), observed value, configured minimum (Decimal or int as the measure requires; no float for a count). The fit results carry `banding_warnings: tuple[BandingWarning, ...]`, empty when none. FR-100's text is unchanged. The contract is regenerated and checked at the ACK (response shape). A non-A-4 BAND_EMPTY → STOP to you: OK.

- **"2026-10-14 12:12:51 BST — PL 8030 @5657d85e: the BandingWarning union ACCEPTED; FR-100
  gets a dated CLARIFICATION clause for DP-B1/B3 (not DP-B2) (re lead 12:12:28)"**, quoted in
  part (its first paragraph accepts the type as Task 6 defines it):
  > **FR-100's row: a dated CLARIFICATION clause IS permitted, for DP-B1 and DP-B3 only.** My 12:05:33 "FR-100's text is unchanged" meant the requirement's SUBSTANCE (thresholds, warn by default, fail if configured, empty always fails) is not amended. It did not forbid recording how the row is read. […]
  > **DP-B2's typed shape does NOT go on the row:** it is a data contract, so it goes to 02 §4 (the data contracts section, beside `PartitionDiagnostics` / the fit result types) and the §5.2 signature note. Task 5 is amended accordingly.

  [Elided: the entry's two bullets, which define DP-B1's and DP-B3's readings; Task 5 restates
  them.]

  Every decision point below is therefore ruled, and the plan below is written to those rulings.
  The EBM limb is **FD-1723's**, added by an auditor before the mint (DP-L2 (a)); this plan
  does not write it, and the SL-8031 row's activation needs wait for it. FD-1723's file now
  travels in the D17 batch (the entry "2026-10-14 11:57:51 BST", item 2), not on the branch read
  when this plan was first written.

## The SL-1543 guard test and the G2 path (stated, per the 11:29:53 entry)

1. **This slice does not edit SL-1543's guard test**, which asserts that the A-4 severity spec
   has `loss_treatment.kind == "none"` and that the AD structure's `large_loss` is uncapped. That
   test's file is outside this slice's write set. The guard stays green on this slice's tree,
   because the slice changes no spec that the seed declares.
2. **If DP-A4-3 later switches to (y), capped,** the guard test changes **only in the same merge
   as this slice, or after it**. Both LGs cite that pairing: this slice's LG and the LG of the
   slice that changes the guard. Before this slice merges, a capped A-4 severity GLM would fit
   uncapped, which is the FD-1723 defect itself.
3. **The binding condition.** If PL-1542 Task 0 Step 4's probe fails (|ratio − 1| > 0.05) and
   (y) becomes the answer, SL-1543 STOPs. The FR-127 limb of this slice (Tasks 1 to 3) then joins
   the G2 path and merges **before** SL-1543 resumes. Tasks 1 to 3 are cut so that they can ship
   alone, which DP-S1 covers.
4. **FR-100 can also reach the G2 path. The 11:29:53 entry does not cover this.** The freMTPL2
   seed fits its frequency and severity GLMs through the platform's fit Job, over Bandings
   proposed on the full validated version (`examples/fremtpl2/model.py:229-262`,
   `BandingProposal` with no `minimums`, so the default floors are 0 and `warn`). After Task 4,
   every such fit runs `check_banding`. A band that the **claims-only** severity frame does not
   reach (`PL-1542` Task 1 Step 2) would refuse that fit with `BAND_EMPTY`. That refusal is
   correct under FR-100, and it would stop G2. Task 0 Step 3 measures this before any code is
   written. Under DP-G1 as ruled, the probe decides: any `BAND_EMPTY` for the A-4 severity GLM
   STOPs the slice to the maintainer before any code (a G2 interaction); on a clean probe, this
   slice and SL-1543 merge in whichever order they are ready, and the second re-merges `main` and
   re-runs the WF-699 journey (Task 8).

## Goal

A `GlmSpec` or `EbmSpec` whose `loss_treatment` is `capped` is fitted on the capped response:
the same fit as a `none` spec fitted on data capped by hand. The cap reaches every consumer of
the response inside `fit_glm`: the Tweedie profile, cross-validation, the fit, the separation
check and the dispersion. `spliced` and `excess` are refused by name with
`LOSS_TREATMENT_UNIMPLEMENTED` on both arms, as `fit_gbm` refuses them. Nothing fits uncapped
while its spec and `spec_hash` say capped.
**Every fit runs FR-100's check** over the rows it actually fits, after FR-111's weight-0
exclusion (DP-B1 (a)). For each Banding that a fitted factor applies, those rows are checked. An
empty band always refuses the fit with `BAND_EMPTY`. A thin band refuses with
`BAND_BELOW_MIN_EXPOSURE` when the Banding's `minimums.on_violation` is `fail`. When it is `warn`
(the default), the fit succeeds and the warning is recorded in a typed `banding_warnings` field
on the fit result, defined in `model-schema` and published in the regenerated contract (DP-B2
(a)). The fit Job surfaces each refusal as a `409` problem that carries its `02` §5.1 code, as it
already does for `FACTOR_RESOLUTION_FAILED`.

## Evidence at `8eaf6d5f` (the owning code, read)

**FR-127, GLM limb.**
- `apply_loss_treatment` is defined at `gbm.py:178-201`. It is a no-op for `none`, applies
  `np.minimum(response, cap_minor)` for `capped`, and raises `GbmFitError("LOSS_TREATMENT_UNIMPLEMENTED", …)`
  for the other kinds (`:195-201`).
- It is called on the training response at `gbm.py:645` and on the holdout response at
  `gbm.py:684-686`. It is exported through `gbm.py:92` and `modelling/__init__.py:37` and `:99`.
- `fit_glm` (`glm.py:524`) reads the response once, at `glm.py:577`. It never reads
  `loss_treatment`: `git grep -nEi "loss_treatment" -- packages/pricing-core/src/pricing_core/modelling/glm.py`
  prints nothing.
- That one `response` array feeds the Tweedie profile (`:618`), CV (`:634`), the fit (`:654`),
  the separation check (`:714`) and the dispersion (`:731`). Treating it at `:577` therefore
  reaches all five.
- `loss_treatment` sits on `ModelSpecCommon` (`model_schema/modelling.py:836`), and `GlmSpec`
  (`:1022`) inherits it. `LossTreatment` (`:740-787`) requires `restoration_loading` with
  `capped`. No validator refuses a treatment by `model_type`.
- The spec records the debt at `02-modelling.md:2659-2661`: *"it belongs beside the fit rather than
  inside it, because the GLM path will need the same function"*.
- **The EBM arm has the same gap, and it is in scope (DP-L2 (a), ruled).** `EbmSpec`
  (`modelling.py:1446`) inherits `loss_treatment`, and `fit_ebm` reads the response at
  `ebm.py:209` and never reads the treatment
  (`git grep -nEi "loss_treatment" -- packages/pricing-core/src/pricing_core/modelling/ebm.py`
  prints nothing). The arm's error class is `EbmFitError` (`ebm.py:41`). The limb is added to
  FD-1723 by an auditor before the mint.

**FR-100.**
- The requirement (`02-modelling.md:108`, `§3.2`, read in full; no dated amendment sits on the row)
  says: *"A Banding validates against the Dataset Version at fit time: every band must meet
  configurable minimum exposure and minimum claim count, or fitting warns (default) or fails (if
  configured). Empty bands always fail."*
- `§4.2` (`:458-464`) adds: *"emptiness is a fact about a Dataset Version, not about the artifact,
  so `check_banding` answers it at fit time and a banding that is fine on one version can be
  empty on the next."* The `minimums` note is at `:476-480`, and the defaults correction is at
  `:1918-1926`.
- `check_banding` is at `bandings.py:524-584`. It raises `BandingError("BAND_EMPTY")` at
  `:558-563` whatever the configuration says, and `BandingError("BAND_BELOW_MIN_EXPOSURE")` at
  `:579-583` when thin and `fail`. Otherwise it **returns** the warnings as `tuple[str, ...]`.
  Its thresholds fall back to `banding.minimums` (`modelling.py:325-342`).
- Its thin test reads `exposure_column="exposure_years"` and `claim_count_column="claim_count"`.
  `one_way` (`data/profile.py:372-377`) **reads an absent column as 0**, which is the DP-B3 trap.
- It has no fit-path caller. `git grep -nE "check_banding" -- packages backend` finds only
  `bandings.py:49`, `:524`, `modelling/__init__.py:10` and `:106`, and the tests
  (`test_bandings.py:344`, `:360`, `:375`, `:410`).
- The three fit entries resolve factors right after the FR-111 weight rule:
  `glm.py:559/:562`, `gbm.py:630/:636` and `ebm.py:121/:123`.
- `BandingError` is a `ModellingError` (`modelling/errors.py:53`). The fit handler
  (`backend/src/app/worker/model_handlers.py:395-416`) maps `EbmFitError`, `GbmFitError`,
  `GlmFitError`, `NonFiniteDerivativeError`, `RoundBudgetExceededError` and
  `FactorResolutionError`, and **not** `BandingError`. A `BandingError` raised inside the fit
  would leave the handler unmapped.
- Both codes are registered in `backend/src/app/errors.py:124-125` and catalogued in
  `02-modelling.md:2107`.
- **No fit result has a warnings field.** `GlmFitResult` (`modelling.py:1561`), `GbmFitResult`
  (`:1631`) and `EbmFitResult` (`:1790`) carry none. DP-B2 (a) adds one (Task 6).
- **The contract chain the field travels** (`CLAUDE.md` §2's one-way rule: `model-schema` →
  `docs/contracts/` → `frontend/src/api/generated`). The three fit results are published in
  `docs/contracts/openapi/generated.json` and `docs/contracts/schemas/generated/model.schema.json`,
  both written by `scripts/generate-contracts.py`; `docs/contracts/schemas/model.schema.json` is
  the hand-authored contract that `backend/tests/test_contracts.py` compares against them, with
  `fit_result` at `:19`. The frontend reads the fit results only as aliases of the generated
  types (`frontend/src/api/models.ts:6`, `:166`, `:167`), which `pnpm --dir frontend generate:api`
  writes from `generated.json` (`frontend/package.json:13`) into
  `frontend/src/api/generated/`, a VCS-ignored directory (`.gitignore:37-38`).
- **A new fit-result field is a staged-contract event.** `02` FR-207 (`02-modelling.md:372`) lists
  each field that went live, with its date; `dropped_eval_metrics` on `GbmFitResult` is the
  tenth, *"empty on … every artifact written before that date"*, and FR-161
  (`02-modelling.md:227`) is the precedent for a fit-result field that tells the caller rather
  than staying silent.

## Acceptance Standard

Each item is checked by a command that a fresh reviewer can run from the repository root on the
slice's merge tree.

1. **This delta passes the docs checks on its own branch.** At the branch head,
   `python3 scripts/audit-docs.py` prints no line naming this file or the SL-8031 row, apart
   from the working-id lines of checks 31 and 32, which are expected until the ids are minted.
   After minting, `python3 scripts/audit-docs.py`, `python3 scripts/doc-index.py --check` and
   `python3 scripts/register-lint.py` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids.
3. **Spec first.** `git log --format=%s origin/main..<slice head> -- docs/specs/02-modelling.md`
   shows the FR-127 note (Task 2), and the FR-100 clarification (DP-B1 and DP-B3), the `§4.8` shape, the `§5.2` note and the FR-207 note (Task 5), landing
   in a commit before or with the code, never after.
4. **A capped GLM fits capped (R1, red on main).** A capped `GlmSpec` fitted on raw data has
   every coefficient equal, to `1e-10`, to a `none` spec fitted on the same data capped by hand.
   Its coefficients differ from the uncapped fit's. On main the first assert fails, because the
   treated fit **equals the uncapped one**. A failure from any other cause is a plan defect.
5. **Every consumer of the response sees the cap (R2, red on main).** R1 is parametrised over
   `select_by="cv"` and a `tweedie` spec with a `p_grid`. The selected alpha or power and the
   coefficients equal those of the hand-capped fit.
6. **`spliced` and `excess` are refused by name on a `GlmSpec` (R3, red on main).** The fit
   raises `GlmFitError` with `code == "LOSS_TREATMENT_UNIMPLEMENTED"` and the kind in the
   message. On main, `pytest.raises` reports *DID NOT RAISE*.
7. **The EBM arm (DP-L2 (a); R4, red on main).** Acceptance 4 and 6, applied to `fit_ebm`: a
   capped `EbmSpec` has every term score equal, to `1e-10`, to a `none` spec fitted on the same
   data capped by hand, at the same `random_state`, and differs from the uncapped fit's; `spliced`
   and `excess` raise `EbmFitError` with `code == "LOSS_TREATMENT_UNIMPLEMENTED"`. On main the
   first assert fails on the equality, and the refusal reports *DID NOT RAISE*.
8. **One function, one module (DP-L1).**
   `git grep -nE "def apply_loss_treatment" -- packages` prints exactly one line, in
   `pricing_core/modelling/loss_treatment.py`, and `glm.py`, `gbm.py` and `ebm.py` each import it. `test_gbm.py`'s FR-127 tests (`:601`, `:628`) stay green unchanged, as guards.
9. **An empty band refuses every fit (R5, red on main).** For each of `fit_glm`, `fit_gbm`
   (both backends) and `fit_ebm`, a banding factor whose Banding was derived on one frame is
   fitted on a frame where one band is reached by no row. The fit raises `BandingError` with
   `code == "BAND_EMPTY"`. This is the 11:28:56 entry's *"a banding whose data moved is refused at
   fit"*. On main every arm fits, and `pytest.raises` reports *DID NOT RAISE*.
10. **A thin band under `on_violation="fail"` refuses (R6, red on main)**, with
    `BAND_BELOW_MIN_EXPOSURE`. The same frame under `warn` fits, and the fit result's
    `banding_warnings` carries the `BandingWarning` that `check_banding` returned (R7): its
    `banding` ref, `band_label`, `band_index`, `measure`, and an `observed` and `minimum` typed as
    the measure requires (an `int` for a claim count, a `Decimal` for exposure; never a `float`,
    never a string of prose). On main R7 fails with an `AttributeError` on the absent field, and
    the LG names it as that cause. *(Amended 2026-10-14, on the 12:05:33 entry.)*
11. **The fit Job surfaces the refusal (R8, red on main).** A fit Job over a Banding with an empty
    band ends with status **`failed`**, and its stored error code is **`BAND_EMPTY`**. On main the
    Job **succeeds**, so the assert on `failed` is the red. A test that asserts only a terminal
    state is not this test. The `409` is the status of the `PlatformError` that Task 7's mapping
    raises in the handler; the Job does not store it (`JobError` carries `code`, `message`,
    `retryable`, `detail` and `trace_id`, `packages/model-schema/src/model_schema/jobs.py:173-187`,
    and the worker stores `exc.code`, `backend/src/app/worker/tasks.py:197-232`, both at `0877e6e7`),
    and no HTTP response carries a fit Job's refusal, so R8 does not assert it. *(Amended
    2026-10-16, before the mint, by the planner (seat planner-p1b), on the lead's brief of
    2026-10-16 item 2: the line read "and the problem status is `409`", which a Job-level test
    cannot observe. Task 7's mapping and R8 are unchanged.)*
12. **The guards stay green, at base and at head.** A `none` GLM fit has coefficients identical
    to main's. A Banding that fits its frame reports nothing (`test_bandings.py:410`). FR-111's
    weight-0 exclusion runs **before** the banding check, so a band reached only by weight-0 rows
    is empty. The LG records each of these as a guard.
13. **SL-1543's guard test is untouched.** `git diff --stat origin/main...<slice branch>` lists
    no file of SL-1543's write set. This item is void only if DP-A4-3 has switched to (y), and
    then the pairing in "The SL-1543 guard test" item 2 is cited in the LG.
14. **The contract (DP-B2 (a), as corrected by the 12:05:33 entry).**
    `uv run python scripts/generate-contracts.py --check` exits 0, and this prints `OK` on the
    slice's merge tree (and a `KeyError` on main, the red):
    ```bash
    python3 -c "import json; s=json.load(open('docs/contracts/openapi/generated.json'))['components']['schemas']
    for fr in ('GlmFitResult','GbmFitResult','EbmFitResult'):
        items=s[fr]['properties']['banding_warnings']['items']; assert 'oneOf' in items or '\$ref' in items, (fr, items)
    e=s['ExposureBandingWarning']['properties']; c=s['ClaimCountBandingWarning']['properties']
    assert e['observed']['type']=='string' and e['minimum']['type']=='string', e
    assert c['observed']['type']=='integer' and c['minimum']['type']=='integer', c
    assert set(e) == set(c) == {'banding','band_label','band_index','measure','observed','minimum'}, (e, c)
    print('OK')"
    ```
    The three fit results' `banding_warnings` are arrays of the `BandingWarning` union, never
    of `{"type": "string"}`; the exposure arm's values are JSON strings (`DecimalStr`) and the
    claim-count arm's are integers; `measure` is an enum. If the executor took the single-class
    form (Task 6), the LG gives the equivalent check against its one component, with the same
    asserts on the field set and on the per-measure value types. The hand-authored fit-result
    schemas agree with the generated ones (`backend/tests/test_contracts.py` green). A fit result
    stored before the slice, with no `banding_warnings` key, still validates (a test loads one
    through `model-schema`). The lead's API ACK checks the **response shape** (the 11:52:51 and
    12:05:33 entries): a fit result read back through the API carries a structured
    `BandingWarning`, not a string.
15. **The generated frontend types carry it, and nothing is hand-written.**
    `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api` writes a
    `frontend/src/api/generated/schema.d.ts` in which each of `GlmFitResult`, `GbmFitResult` and
    `EbmFitResult` has `banding_warnings` typed as an array of the generated `BandingWarning`
    union (not `string[]`), with `measure` a union of the two string literals, and
    `pnpm --dir frontend type-check` and
    `pnpm --dir frontend test` exit 0. `git diff --stat origin/main...<slice branch> -- frontend/`
    prints nothing.
16. **The probe gated the code (DP-G1).** The LG carries Task 0 Step 3's per-Banding output
    verbatim, and its first code commit is after it. If any line is `BAND_EMPTY` for the A-4
    severity GLM, the LG records the STOP to the maintainer and no code commit follows it without
    the maintainer's dated ruling.
17. **The gate is green on the merge tree.** Both halves of the `CLAUDE.md` §11 commands pass,
    named against `origin/main...<slice branch>`.

## Global Constraints

- **`pricing-core` owns both rules** (ADR-703; `CLAUDE.md` §2). A notebook that calls `fit_glm`
  directly gets the cap and the banding check, as the fit Job does. This follows the
  `weights.py` pattern from SL-1675: one module, the arm's own error class passed in.
- **Order at each fit entry:** FR-111's `require_usable_weights`, then FR-100's check over the
  rows that remain, then `resolve_factors`. The loss treatment is applied where the response is
  read (`glm.py:577`, `gbm.py:645` and `ebm.py:209`). The holdout
  response is treated as `gbm.py:684-686` treats it.
- **The check reads the rows fitted** (DP-B1 (a)): the training frame after FR-111's weight-0
  exclusion, never the holdout and never the whole Dataset Version.
- **The thin check reads `check_banding`'s default columns** (DP-B3 (a)), `exposure_years` and
  `claim_count`, the ones the `BandingProposal` measured (`modelling.py:599-600`). A non-zero
  floor whose column is absent from the fitted rows is refused by name, never read as 0.
- **One contract, one way** (`CLAUDE.md` §2). `banding_warnings`, `BandingWarning` and
  `BandingMeasure` are each defined once, in `model-schema` (amended 2026-10-14, on the 12:05:33
  entry); `pricing-core` imports them, as it imports `Banding`. `docs/contracts/` changes only by `scripts/generate-contracts.py`, apart from
  the hand-authored `docs/contracts/schemas/model.schema.json` that `test_contracts.py` compares;
  `frontend/src/api/generated/` is regenerated and never committed or hand-written.
- **No change to the shape of `LossTreatment`, to `spec_hash`, or to any stored spec.** A spec
  that said `capped` keeps its hash. What changes is that its model is now fitted as it says.
- **FR-128's reconciliation is untouched.** The restoration loading is not applied by the fit,
  as it is not today in `fit_gbm`.
- **`BAND_EMPTY` is never configurable.** No setting, flag or override reaches it, whatever the
  `minimums` say (FR-100: *"Empty bands always fail"*).
- **The barred word.** Write "the maintainer (by delegation)", and elide quoted text with a
  bracketed elision note.

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | SL-8031 — FD-1723's HIGH limbs: a capped GLM (and EBM) fits capped, and the banding check runs at fit | Tasks 0 to 8 below | `02` §3.5: FR-127 (the GLM arm and the EBM arm, DP-L2 (a)); `02` §3.2: FR-100 (the fit-time check and its `warn` record); `02` FR-207 (the staged-contract note for `banding_warnings`); read only: FR-128, FR-111, FR-161, FR-204 | this delta minted; FD-1723 minted with its EBM limb; every DP ruled (2026-10-14 11:52:51 BST); Task 0 Step 3's probe clean for the A-4 severity GLM, or the maintainer's ruling on it | 2 |

### Task 0 — re-read at the base, enumerate, and probe (convention 4)

- [ ] **Step 1.** Re-read every `file:line` in "Evidence" at the slice base. Record each moved
  line in the LG.
- [ ] **Step 2. Enumerate every fit entry.** Run `git grep -nE "resolve_factors\(" -- packages/pricing-core/src`
  and sort each hit into **fit** or **score/diagnose**. The fit hits are expected to be
  `glm.py:562`, `gbm.py:636` and `ebm.py:123`. Any other fit hit joins Tasks 3 and 4. The LG
  tables every hit.
- [ ] **Step 3. The G2 probe (DP-G1), read-only, one script, not committed.** For each seed
  Banding (`examples/fremtpl2/model.py:229-262`), run `check_banding` against the seed's
  frequency **training** frame and the claims-only severity training frame (`PL-1542` Task 1
  Step 2). Run it through `scripts/run-small.sh` and never beside a held gate. Record each
  Banding's result in the LG, verbatim. **DP-G1 as ruled:** any `BAND_EMPTY` for the A-4
  severity GLM is a **STOP to the maintainer before any code** (Task 1 onward), sent through the
  lead; it is a G2 interaction and its resolution is the maintainer's. A `BAND_EMPTY` on any other
  seed fit is a STOP to the lead, who routes it. On a clean probe the slice proceeds, and its
  merge order against SL-1543 is whichever is ready first (Task 8).
- [ ] **Step 4.** Read `to-lead.md` from the entry "2026-10-14 11:52:51 BST" onward for any entry on FD-1723 (FD 8027 before its mint),
  FR-127, FR-100, SL-1543 or this plan. Name each entry in the LG.

### Task 1 — the FR-127 reds, on main

- [ ] **R1** (`test_glm.py`, `@pytest.mark.req("FR-127")`). Use a Gamma severity frame whose
  response in minor units exceeds `cap_minor` on at least 10 % of rows. Compare a
  `LossTreatment(kind="capped", cap_minor=…, restoration_loading=…)` fit against a `none` fit of
  the frame clipped by hand (`pl.col(...).clip(upper_bound=…)`): coefficients equal to `1e-10`.
  Also assert that the coefficients differ from the uncapped fit's. Mirror
  `test_gbm.py:601-623`; do not reinvent its fixtures.
- [ ] **R2.** R1 parametrised over `select_by="cv"` and a `tweedie` spec with a `p_grid`.
- [ ] **R3.** `spliced` and `excess` each raise `GlmFitError`, with
  `code == "LOSS_TREATMENT_UNIMPLEMENTED"` and the kind in the message.
- [ ] **R4** (`test_ebm.py`, `@pytest.mark.req("FR-127")`; DP-L2 (a)). R1 and R3 for `fit_ebm`:
  a capped `EbmSpec` against a `none` fit of the hand-clipped frame at the same `random_state`,
  every term score equal to `1e-10` and different from the uncapped fit's; `spliced` and `excess`
  each raise `EbmFitError` with `code == "LOSS_TREATMENT_UNIMPLEMENTED"`.
- [ ] Run `scripts/run-small.sh` on `test_glm.py -k loss_treatment` and on
  `test_ebm.py -k loss_treatment` at the base. **Record each red line verbatim, and its cause.**
  R1, R2 and R4's equality must fail on the equality to the hand-capped fit. R3 and R4's
  refusals must fail with *DID NOT RAISE*.

### Task 2 — FR-127 in the spec (`spec-change`)

- [ ] A dated note under the `02-modelling.md:2659-2661` paragraph: the GLM arm and the EBM arm
  now apply `apply_loss_treatment` at the response read, and the function now lives in
  `pricing_core/modelling/loss_treatment.py`, taking the arm's error class (DP-L1, ruled). The
  FR-127 row itself is unchanged, because it already requires this.

### Task 3 — FR-127 in the code

- [ ] Move `apply_loss_treatment` into its own module, `pricing_core/modelling/loss_treatment.py`
  (DP-L1, ruled). It takes the arm's error class as `weights.require_usable_weights` does
  (`weights.py:91-97`). `gbm.py` imports it, and `modelling/__init__.py` keeps exporting the name.
- [ ] Apply it at `glm.py:577`, before the `x = design.to_numpy()` line, so all five consumers
  see the treated response, passing `GlmFitError`.
- [ ] Apply it at `ebm.py:209`, passing `EbmFitError` (DP-L2 (a), ruled).
- [ ] R1 to R4 green, and `test_gbm.py`'s FR-127 tests green unchanged.
- [ ] **DP-S1's split line.** Tasks 1 to 3 are one commit set that passes the gate alone.

### Task 4 — the FR-100 reds, on main

- [ ] **R5** (`test_glm.py`, `test_gbm.py` over `BACKENDS`, `test_ebm.py`;
  `@pytest.mark.req("FR-100")`). Derive a Banding on a frame with `propose_banding`. Then fit on a
  frame from which every row of one band has been removed (the data moved). Expect
  `BandingError` with `.code == "BAND_EMPTY"`.
- [ ] **R6.** A Banding with `minimums=(min_exposure_per_band=…, on_violation="fail")` and a band
  below the floor: expect `BAND_BELOW_MIN_EXPOSURE`.
- [ ] **R7.** The same Banding under `warn` fits, and the fit result's `banding_warnings` equals
  the tuple of `BandingWarning` that `check_banding` returns for those rows (DP-B2 (a), as
  corrected 12:05:33). The test asserts the structure, not a string: the warning's `banding` is
  the Banding's `banding:{slug}@{version}` ref, its `band_label` and `band_index` name the thin
  band, `measure` is `BandingMeasure.CLAIM_COUNT` (or `EXPOSURE`) as the floor breached, and
  `observed` and `minimum` are an `int` for a claim count and a `Decimal` for exposure, never a
  `float`. One arm per file, all three arms. On main it fails with an `AttributeError` on the
  absent field.
- [ ] **Guard G-W.** A band reached only by weight-0 rows (FR-111) is `BAND_EMPTY`. This guard
  is green after Task 5 only. Record it as a guard of the ordering, not as a red of this slice.
- [ ] Run `scripts/run-small.sh` per file at the base, and record each red line and its cause.

### Task 5 — FR-100 in the spec (`spec-change`)

- [ ] *(Amended 2026-10-14, on the maintainer's (by delegation) entry "2026-10-14 12:12:51 BST",
  which rules this task's FR-100 clause.)* **One dated CLARIFICATION clause on the FR-100 row,
  for DP-B1 and DP-B3 only**, in the form *"Clarified 2026-10-14, SL-8031, on the entry
  "2026-10-14 12:12:51 BST""*. It records the two readings that decide warn against fail:
  - DP-B1: the band minimums are evaluated over the rows actually fitted, after FR-111's
    weight-0 exclusion;
  - DP-B3: the default columns are `exposure_years` and `claim_count`, and a missing column
    under a non-zero floor is refused by name.

  The requirement's substance is not amended: its thresholds, warn by default, fail if
  configured, and empty always fails (the entry: *"'unchanged' meant the requirement's
  SUBSTANCE … is not amended"*). **DP-B2's typed shape does not go on the row.**
- [ ] **DP-B2's typed shape goes to `02` §4, the data contracts** (the 12:12:51 entry). In
  `§4.8` (`02-modelling.md:1206` onward), beside the fit result's `dropped_eval_metrics` text
  (`:1409`, the example at `:1437`), add `BandingWarning` and `BandingMeasure` with their fields
  and per-measure value types (Task 6), and `banding_warnings` on the three fit results.
- [ ] The `§5.2` `check_banding` signature (`02-modelling.md:2382-2388`) **changes**, with a
  dated note in place: it returns `tuple[BandingWarning, ...]` instead of `tuple[str, ...]`, and
  its two floor overrides become `min_exposure: Decimal | None` and `min_claims: int | None`
  (no float for a count, and the exposure compared exactly). The 12:12:51 entry accepts these
  forced consequences.
- [ ] A dated note on FR-207 (`02-modelling.md:372`): `banding_warnings` goes live on
  `GlmFitResult`, `GbmFitResult` and `EbmFitResult`, empty on every fit with no `warn` violation
  and on every artifact written before that date, in the form of the `dropped_eval_metrics` entry.
- [ ] Task 0 Step 1 re-reads the `§4.8` fit-result text at the base
  (`git grep -n "FitResult\|dropped_eval_metrics" -- docs/specs/02-modelling.md`), and the LG
  records the lines the shape lands at.

### Task 6 — FR-100's warnings field, through the contract (DP-B2 (a), ruled)

- [ ] **Red first** (`packages/model-schema/tests/test_banding_warnings.py`,
  `@pytest.mark.req("FR-100")`, in the form of `test_dropped_eval_metrics.py`). A test that `GlmFitResult`, `GbmFitResult` and
  `EbmFitResult` each accept `banding_warnings` and default it to `()`; on main it fails on the
  absent field (`EbmFitResult` forbids extra fields, `02-modelling.md:1396`). Also a stored fit
  result without the key validates (the guard). *(Amended 2026-10-14, on the 12:05:33 entry:)*
  the same file also asserts the type: a `BandingWarning` round-trips through JSON; an exposure
  warning's `observed` and `minimum` are `Decimal` on the model and JSON strings on the wire; a
  claim-count warning's are `int`; a `float` for either measure's value is refused, as
  `DecimalStr` refuses one (`model_schema/money.py:20`); a free-text string in
  `banding_warnings` is refused; and a `measure` outside the enum is refused. On main it fails
  on the import of `BandingWarning`.
- [ ] `packages/model-schema/src/model_schema/modelling.py` *(amended 2026-10-14, on the
  12:05:33 entry, which corrects the `tuple[str, ...]` this item first named)*:
  - a `BandingMeasure(enum.StrEnum)` with `EXPOSURE = "exposure"` and
    `CLAIM_COUNT = "claim_count"`, in the form of `BandingMethod` (`modelling.py:284-297` at
    `a3fc2e8d`, the same lines at `8eaf6d5f`);
  - `BandingWarning`, defined once, beside `BandingMinimums` (`:320-337`), frozen with
    `extra="forbid"` as every model in the file is (`:330`). Its fields:
    - `banding: ArtifactRef` — the Banding version checked, on the wire the ID-3 string
      `banding:{slug}@{version}` (`model_schema/refs.py:78-99`; `"banding"` is in
      `ARTIFACT_TYPES`, `refs.py:23-26`), built from the Banding's `slug` and `version`
      (`modelling.py:356`, `:358`); a validator refuses a ref whose `type` is not `banding`;
    - `band_label: str` (one of `Banding.labels`, `:370`) and `band_index: int` (`ge=0`, its
      position in `labels`, which are unique by `:402-404`);
    - `measure: BandingMeasure`;
    - `observed` and `minimum`, typed **as the measure requires**: `DecimalStr` for `exposure`,
      as `min_exposure_per_band` is (`:335`) and as `OneWayRow.exposure_years` is
      (`model_schema/profiles.py:149`); `int` with `ge=0` for `claim_count`, as
      `min_claims_per_band` is (`modelling.py:336`) and `OneWayRow.claim_count` is
      (`profiles.py:150`). The plan's form: two arms, `ExposureBandingWarning` and
      `ClaimCountBandingWarning`, each with `measure: Literal[BandingMeasure.<member>]`, and
      `BandingWarning = Annotated[ExposureBandingWarning | ClaimCountBandingWarning,
      Field(discriminator="measure")]`, the pattern of `EbmFeatureBins` (`:1768`). The type
      then refuses a `Decimal` count or a `float` exposure with no validator, and the generated
      contract shows each arm's value type. If the executor finds a single class with a
      validator simpler at the base, it records why in the LG; the field set and the value types
      above are fixed either way;
  - `banding_warnings: tuple[BandingWarning, ...] = ()` on the three fit results, in the form of
    `dropped_eval_metrics: tuple[DroppedEvalMetric, ...] = ()` (`:1695`), the structured
    record FR-161 put on `GbmFitResult`. It is declared once if the three share a base at the
    slice's base tree, else once on each with the same type and default; Task 0 Step 1 records
    which. `BandingMeasure` and `BandingWarning` are exported where `DroppedEvalMetric` is (`model_schema/__init__.py:162`, `:538`), and
    no second shape is hand-written anywhere else (`CLAUDE.md` §2).
- [ ] `pricing_core/modelling/bandings.py`: `check_banding` (`:524-584`) returns
  `tuple[BandingWarning, ...]`, one per breached floor per band, built from the
  `band_statistics` row (`OneWayRow`): exposure compared as `Decimal` (no `float(...)` cast, as
  `:546` and `:567` cast today), claim count as `int`. Its two override keywords become
  `min_exposure: Decimal | None` and `min_claims: int | None` (Task 5's §5.2 note). The
  `BAND_BELOW_MIN_EXPOSURE` message renders the same warnings, so its text stays readable.
  `test_bandings.py:365` and `:403` keep their asserts (a non-empty tuple); `:386`, `:406` and
  `:413` keep `== ()`.
- [ ] `contract-schema`: run `uv run python scripts/generate-contracts.py` to regenerate
  `docs/contracts/` (never hand-edit a generated file), then add the property to the
  hand-authored `docs/contracts/schemas/model.schema.json` `fit_result` arms (`:19`) where
  `test_contracts.py`'s comparison requires it. `uv run python scripts/generate-contracts.py --check`
  exits 0. `contract-guard`: `test_contracts.py` stays green, and a new path is added only if a
  walker does not reach the field.
- [ ] **The frontend consequence.** `pnpm --dir frontend install --frozen-lockfile &&
  pnpm --dir frontend generate:api` regenerates the VCS-ignored `frontend/src/api/generated/`.
  `models.ts:6`, `:166` and `:167` alias the generated types, so they carry the field with no
  edit; `pnpm --dir frontend lint`, `type-check` and `test` (which runs
  `src/api/__tests__/models.test-d.ts`) exit 0. No file under `frontend/` is committed (Acceptance
  15). A view of the warnings is the follow-on row in "Hand-off".

### Task 7 — FR-100 in the code

- [ ] One helper beside `check_banding` in `bandings.py`. It takes the fitted rows, the factors
  and the bandings mapping, and runs `check_banding` once per distinct Banding that a factor
  (or an interaction operand, per Task 0 Step 2) applies, over the rows the arm fits (DP-B1 (a)),
  reading the default columns and refusing a non-zero floor on an absent column by name
  (DP-B3 (a)). It returns the warnings, a `tuple[BandingWarning, ...]` (Task 6, as corrected by
  the 12:05:33 entry).
- [ ] Each fit entry calls it after `require_usable_weights` and before `resolve_factors`, and
  writes the returned `BandingWarning`s into the fit result's `banding_warnings`, unchanged (no
  string is rendered on the way).
- [ ] In `model_handlers.py:395-416`, map `BandingError` to `PlatformError(exc.code, …, 409, str(exc))`,
  as the `FactorResolutionError` clause does. Mapping `ModellingError` at that point would also
  catch `FactorResolutionError` and change its detail text, so name `BandingError`.
- [ ] **R8** (`backend/tests/test_model_jobs.py`, beside the `FACTOR_RESOLUTION_FAILED` test at
  `:596`). A fit Job over a Banding with an empty band is `failed`, with code `BAND_EMPTY`. Red
  at base first.
- [ ] R5 to R8 green, and G-W green.

### Task 8 — close

- [ ] `uv run python scripts/req-coverage.py`, the gate (both halves, the frontend half after
  Task 6's regeneration), the `LG-`'s closing acts, and the WF-699 journey test re-run on the
  merge tree by whichever of this slice and SL-1543 merges second, after re-merging `main`
  (DP-G1 as ruled, on a clean probe).

### Write set

- `docs/specs/02-modelling.md` (the FR-127 note; the FR-100 clarification clause, DP-B1 and DP-B3
  only; the `§4.8` `BandingWarning` shape and the `§5.2` `check_banding` note; the FR-207 note; the §4
  fit-result field);
- `packages/pricing-core/src/pricing_core/modelling/` (`glm.py`, `gbm.py`, `ebm.py`,
  `bandings.py`, `__init__.py`, and the new `loss_treatment.py`);
- `packages/pricing-core/tests/` (`test_glm.py`, `test_gbm.py`, `test_ebm.py`, `test_bandings.py`);
- `packages/model-schema/src/model_schema/modelling.py` (`BandingMeasure`, `BandingWarning` and the
  three fit results' `banding_warnings`) and `packages/model-schema/src/model_schema/__init__.py`
  (the two exports; amended 2026-10-14, on the 12:05:33 entry)
  and a new `packages/model-schema/tests/test_banding_warnings.py` (Task 6's red, in the form of
  `test_dropped_eval_metrics.py`, FR-161's field test);
- `docs/contracts/`: the files `scripts/generate-contracts.py` regenerates (written by the
  script only), and `docs/contracts/schemas/model.schema.json` (hand-authored, the `fit_result`
  arms only);
- `backend/tests/test_contracts.py`, only if a walker needs a new path;
- `backend/src/app/worker/model_handlers.py` (the `BandingError` clause only);
- `backend/tests/test_model_jobs.py`;
- the `LG-`.

**Regenerated, never committed:** `frontend/src/api/generated/` (`pnpm --dir frontend
generate:api`; VCS-ignored, `.gitignore:37-38`).

**Not in it:** SL-1543's files and its guard test (see "The SL-1543 guard test and the G2 path");
`examples/fremtpl2/`; every committed file under `frontend/` (a view of the warnings is a
follow-on row, as with SL-1675's DP-Z1); `LossTreatment` and `BandingMinimums` shapes; FR-110's
limb.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-L1 | Where does `apply_loss_treatment` live once three arms call it? | **(a), ruled:** its own module, `pricing_core/modelling/loss_treatment.py`, taking the arm's error class as `weights.require_usable_weights` does (`weights.py:91-97`); `gbm.py` and `__init__.py` re-export it. | The ruling: *"its own module, taking the arm's error class (the weights.py:91-97 pattern). OK."* `CLAUDE.md` §2 forbids a shape defined twice, and the spec says *"it belongs beside the fit rather than inside it"* (`02:2659-2661`). | design | no — ruled | Ruled 2026-10-14 by the maintainer (by delegation), entry 2026-10-14 11:52:51 BST |
| DP-L2 | `EbmSpec` inherits `loss_treatment` and `fit_ebm` ignores it (`ebm.py:209`), the same silent class. Does this slice fix the EBM arm too? | **(a), ruled:** yes — one call (Task 3), one red (R4, Task 1), and an auditor adds the EBM limb to FD-1723 before it is minted. | The ruling: *"fix EBM here (ebm.py:209 ignores loss_treatment, the same FR-127 class); an auditor adds the EBM limb to FD 8027 before mint."* | scope | no — ruled; FD-1723's EBM limb is an activation need | Ruled 2026-10-14 by the maintainer (by delegation), entry 2026-10-14 11:52:51 BST |
| DP-B1 | Which frame does the fit-time check read? FR-100 says *"the Dataset Version"*; the fit receives the training partition. | **(a), ruled:** the training rows actually fitted, after FR-111's weight-0 exclusion. | A coefficient is estimated from the rows fitted, so a band empty in those rows is the *"coefficient estimated from no data"* that `check_banding`'s docstring names (`bandings.py:536-538`). The FR-100 clarification clause records the reading (Task 5). | design | no — ruled | Ruled 2026-10-14 by the maintainer (by delegation), entry 2026-10-14 11:52:51 BST |
| DP-B2 | Where does a thin-band **warning** land? `check_banding` returns it, and no fit result has a field for it. | **(a), ruled, as corrected:** a typed field on the three fit results, `banding_warnings: tuple[BandingWarning, ...] = ()`, empty when none. `BandingWarning` is a `model-schema` type with the banding ref (`ArtifactRef`, `banding:{slug}@{version}`), `band_label` and `band_index`, `measure` (the enum `BandingMeasure`: `exposure` or `claim_count`), and `observed` and `minimum` typed as the measure requires (`DecimalStr` for exposure, `int` for a claim count, never a float). `check_banding` returns the same type. Persisted with the model, published in the regenerated contract, and reaching the frontend's generated types (Task 6). This plan first wrote `tuple[str, ...]`; the 12:05:33 entry corrects that reading. | The ruling: FR-100's *"warns (default)"* is the default behaviour, so deferring the warning would leave it unbuilt; *"Through model-schema, with the contract regenerated; the API ACK checks the shape."* The correction: *"'A typed field' means a model-schema type a reviewer or UI can act on, not free text."* | design | no — ruled | Ruled 2026-10-14 by the maintainer (by delegation), entry 2026-10-14 11:52:51 BST; corrected by the entry 2026-10-14 12:05:33 BST, which corrects 11:52:51's DP-B2 as this plan had read it |
| DP-B3 | Which columns does the thin check read? `one_way` reads an absent column as 0 (`data/profile.py:372-377`). | **(a), ruled:** `check_banding`'s defaults, `exposure_years` and `claim_count`, which the `BandingProposal` also uses (`modelling.py:599-600`); a non-zero floor whose column is absent from the rows is refused by name, never read as 0. | The floor and the stats that set it read the same columns, and the refusal closes the absent-column trap. | design | no — ruled | Ruled 2026-10-14 by the maintainer (by delegation), entry 2026-10-14 11:52:51 BST |
| DP-G1 | When may the FR-100 limb merge relative to SL-1543 (G2)? The 11:29:53 entry put only the FR-127 limb off the G2 path. | **Ruled: the probe decides.** Task 0 Step 3's probe runs before any code. Any `BAND_EMPTY` for the A-4 severity GLM is a STOP to the maintainer before code (a G2 interaction). On a clean probe, whichever of this slice and SL-1543 is ready first merges first, and the second re-merges `main` and re-runs the WF-699 journey (Task 8). | The ruling: *"the Task 0 Step 3 probe decides; on ANY BAND_EMPTY for the A-4 severity GLM → STOP to me before code (a G2 interaction)."* | scope | yes, until the probe is clean or the maintainer rules on it | Ruled 2026-10-14 by the maintainer (by delegation), entry 2026-10-14 11:52:51 BST |
| DP-S1 | If the 11:29:53 condition fires (the FR-127 limb joins G2), how does the FR-127 limb ship ahead? | **(a), ruled:** the lead asks the planner for a re-cut delta: SL-8031 keeps FR-100, and a new row takes Tasks 1 to 3 unchanged. | Tasks 1 to 3 are cut to pass the gate alone. Until the condition fires, one slice, as the lead ordered. | scope | no — ruled; reopened only by the condition | Ruled 2026-10-14 by the maintainer (by delegation), entry 2026-10-14 11:52:51 BST |

A plan is *"`draft` while decision points are open, `active` on freeze"* (`document-ids.md`
§1.6). Every decision point is ruled, by the maintainer's (by delegation) entry
"2026-10-14 11:52:51 BST", item (2); DP-G1's ruling leaves one gate inside the slice, Task 0
Step 3's probe, which stops the slice rather than the plan. This delta stays `draft` here: it is
frozen at its merge and made `active` by a dated line. No status is set here (the maintainer
gives the GO).

## The row, cut

SL-8031 is cut under `### WK-1178` in `docs/roadmap.md`, after `SL-1683`, as `draft`. No line is
written on `SL-1543`'s row. The guard pairing and DP-G1 live here and in this slice's LG, and the
lead writes any dated line on SL-1543 at dispatch.

## Hand-off (not this plan's writes)

- **The lead:** mint FD-1723, with its EBM limb, before this delta; GO the executor; relay
  Task 0 Step 3's probe result, and any STOP, to the maintainer (DP-G1); run the API ACK on
  `banding_warnings`' shape (DP-B2).
- **An auditor (DP-L2 (a), ruled):** add the EBM limb (`ebm.py:209`) to FD-1723 before the mint.
- **FR-110 (FD-1723, MEDIUM):** a separate WK-1178 delta, with the NB θ decision point and Task 0's
  `power(k)` check in the pinned glum, per the 11:28:56 entry.
- **DP-B2 (a)'s follow-on:** a WK-675 frontend row that shows the warnings on the model page. It
  gets its id when it is cut.

## Self-review

- **Spec coverage.** FR-127 (the GLM arm and the EBM arm, DP-L2 (a)) and FR-100 (the fit-time
  check and its `warn` record) are each named with their section; FR-207 takes a dated note for
  the new field. FR-128, FR-111, FR-161 and FR-204 are read only. No requirement id is added or
  changed.
- **The 11:52:51 rulings at every site** (amended 2026-10-14, after the entry was logged):
  - DP-L1 (a), the module `loss_treatment.py`: Tasks 2 and 3, Acceptance 8, the write set;
  - DP-L2 (a), the EBM arm in scope: Goal, Evidence, R4 in Task 1, Task 3, Acceptance 7, the
    write set, the Tasks row, the hand-off (an auditor adds FD-1723's EBM limb before the mint),
    and the SL-8031 row's activation needs;
  - DP-B1 (a), the rows fitted after the weight-0 exclusion: Goal, Global Constraints, Tasks 5
    and 7, guard G-W, Acceptance 12;
  - DP-B2 (a), the typed field through `model-schema`: Goal, Evidence (the contract chain),
    Global Constraints, R7, Tasks 5, 6 and 7, Acceptance 10, 14 and 15, the write set, the
    hand-off (the API ACK);
  - DP-B3 (a): Global Constraints, Tasks 5 and 7;
  - DP-G1, the probe decides: "The SL-1543 guard test" item 4, Task 0 Step 3, Task 8,
    Acceptance 16, the Tasks row, the hand-off;
  - DP-S1 (a): "The SL-1543 guard test" item 3 and the DP table.
  Each DP row now carries only its ruled option, and its "Resolved by" cell the ruling line.
- **The 12:05:33 correction of DP-B2 at every site** (amended 2026-10-14, seat planner-fd8040):
  `BandingWarning` (banding ref, band label and index, the `BandingMeasure` enum, `observed` and
  `minimum` typed per measure) and `banding_warnings: tuple[BandingWarning, ...] = ()` replace
  `tuple[str, ...]` in: the Authority section (the entry quoted), the DP-B2 row, R7, Task 5 (the
  §5.2 `check_banding` signature now changes, with a dated note, where it said "unchanged"),
  Task 6 (the red's type asserts, the two types, `check_banding`'s return), Task 7 (the helper
  returns and stores the structured warnings), Acceptance 10, 14 (a runnable shape check of the
  generated contract, red on main) and 15 (the generated frontend type is not `string[]`),
  Global Constraints (each shape defined once) and the write set (`model_schema/__init__.py`).
  Nothing else in the plan changed. The new citations were read at `origin/main` `a3fc2e8d`;
  `git diff --stat 8eaf6d5f a3fc2e8d` lists no change to `model_schema/modelling.py`,
  `bandings.py` or `02-modelling.md`, so they hold at the plan's tree too:
  `model_schema/modelling.py:284-297`, `:320-337`, `:330`, `:335`, `:336`, `:356`, `:358`,
  `:370`, `:402-404`, `:1695`, `:1768`; `model_schema/refs.py:23-26`, `:78-99`;
  `model_schema/profiles.py:149`, `:150`; `model_schema/money.py:20`;
  `model_schema/__init__.py:162`, `:538`; `bandings.py:524-584`, `:546`, `:567`;
  `test_bandings.py:365`, `:386`, `:403`, `:406`, `:413`;
  `docs/contracts/openapi/generated.json` (`components.schemas` holds `DroppedEvalMetric` and the
  three fit results by those names).
- **The 12:12:51 ruling at every site** (amended 2026-10-14, seat planner-fd8040): the
  Authority section, Task 5 (the FR-100 clause now carries only DP-B1 and DP-B3; DP-B2's shape
  goes to `§4.8` and the `§5.2` note), Acceptance 3, the write set and the DP-B1 row. The `§4.8`
  lines `02-modelling.md:1206`, `:1409` and `:1437` were read at `a3fc2e8d`.
- **The 11:28:56 and 11:29:53 conditions at every site** (convention 5):
  - red first on main: R1 to R8, and Acceptance 4 to 11;
  - *"a capped GlmSpec fit asserts capped behaviour"*: R1, R2 and Acceptance 4;
  - *"a banding whose data moved is refused at fit"*: R5 and Acceptance 9;
  - the guard test changes only with this fix's merge: "The SL-1543 guard test" items 1 and 2,
    and Acceptance 13;
  - the binding condition: item 3 and DP-S1.
- **Literals verified at `8eaf6d5f`** (conventions 1 and 3), each by `grep -n` or `sed -n`:
  - `gbm.py`: `:92`, `:178-201`, `:630`, `:636`, `:645`, `:684-686`;
  - `glm.py`: `:88`, `:524`, `:559`, `:562`, `:577`, `:618`, `:634`, `:654`, `:714`, `:731`;
  - `ebm.py`: `:41`, `:121`, `:123`, `:209`;
  - `bandings.py`: `:49`, `:524`, `:558-563`, `:579-583`;
  - `weights.py:91-97`, `errors.py:53`, and `modelling/__init__.py`: `:10`, `:37`, `:99`, `:106`;
  - `model_schema/modelling.py`: `:325-342`, `:599-600`, `:740-787`, `:836`, `:1022`, `:1446`,
    `:1561`, `:1631`, `:1790`;
  - `model_handlers.py:395-416`, `backend/src/app/errors.py:124-125`, and
    `test_model_jobs.py:596`;
  - `test_gbm.py:601`, `:628`, and `test_bandings.py:344`, `:360`, `:375`, `:410`;
  - `02-modelling.md`: `:108`, `:183`, `:227`, `:372`, `:458-464`, `:1396`, `:2107`,
    `:2382-2388`, `:2659-2661`;
  - `docs/contracts/schemas/model.schema.json:19`; `frontend/src/api/models.ts:6`, `:166`,
    `:167`; `frontend/package.json:13`; `.gitignore:37-38`;
    `packages/model-schema/tests/test_dropped_eval_metrics.py` (exists);
  - `examples/fremtpl2/model.py:229-262`.

  The module name is DP-L1 (a)'s, as the option named it. The field name `banding_warnings` is
  this plan's: the ruling fixed a typed field on the fit results, not its name, and the executor
  does not rename it without the lead.
- **Convention 4.** `to-lead.md` was read after 11:29:53 BST at 2026-10-14 11:41:12 BST, when the
  plan was first written; the entries of 11:31:17, 11:34:03 and 11:34:58 do not rule on this
  subject. For this amendment it was read through the entry "2026-10-14 12:00:14 BST"; of the
  entries after 11:41:12, only "2026-10-14 11:52:51 BST" item (2) rules on this plan, and
  "2026-10-14 11:57:51 BST" item 2 places FD-1723's file in the D17 batch. For the DP-B2
  correction it was read through the entry "2026-10-14 12:05:33 BST" (its last entry when read);
  of the entries after 12:00:14, only 12:05:33's PL 8030 bullet rules on this plan. `gh pr list`
  was not run (no GitHub posts by brief). Task 0 Step 4 re-reads at dispatch.
- **Placeholders.** `<slice head>` and `<slice branch>` are values read when the slice runs.
