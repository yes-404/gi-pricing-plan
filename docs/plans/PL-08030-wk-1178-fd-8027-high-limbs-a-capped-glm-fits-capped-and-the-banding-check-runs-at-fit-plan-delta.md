---
id: PL-8030
family: plan
kind: map
title: WK-1178 — FD 8027's two HIGH limbs, a capped GLM spec fits capped (FR-127) and the banding check runs at fit (FR-100), SL-8031 — a dated Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: 8eaf6d5f9cd4204e1e077b44069d4afd395f1461
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1542, SL-1543, PL-1674, SL-1675]
---

# PL-8030 — WK-1178: FD 8027's two HIGH limbs. A capped GLM spec fits capped (FR-127), and the banding check runs at fit (FR-100) (SL-8031)

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
> - `contract-schema` and `contract-guard`: Task 6, only if DP-B2 is ruled (a);
> - `fastapi-service`: Task 7's error mapping;
> - `dev-commands`: `uv sync --all-packages`, `scripts/run-small.sh` for the one-file runs, and
>   both gate halves;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

Filed under **working id 8030**. Its slice row is **working id 8031** (`draft`). Both were
reserved by the lead in `handover/eta.md` (team-lead to planner-fd8027, 2026-10-14, "PL 8030 /
SL 8031 reserved for you"). Written 2026-10-14 by the planner (seat planner-fd8027).
**Tree read:** `origin/main` `8eaf6d5f9cd4204e1e077b44069d4afd395f1461` (#1300, committed
2026-10-14T11:25:34+01:00). Every `file:line` below is at that tree unless marked otherwise. The
executor re-reads each one at its base (Task 0). The finding is FD 8027 (working id, not yet
minted), read in full at `origin/fd-8027-closure-gap-p1-2026-10-14` @`00b683ee`.

## Authority

All three entries are the maintainer's (by delegation), in `to-lead.md`. Each was read in full
at 2026-10-14 11:41:12 BST.

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
  MEDIUM limb of FD 8027 and go into a separate WK-1178 delta.

## The SL-1543 guard test and the G2 path (stated, per the 11:29:53 entry)

1. **This slice does not edit SL-1543's guard test**, which asserts that the A-4 severity spec
   has `loss_treatment.kind == "none"` and that the AD structure's `large_loss` is uncapped. That
   test's file is outside this slice's write set. The guard stays green on this slice's tree,
   because the slice changes no spec that the seed declares.
2. **If DP-A4-3 later switches to (y), capped,** the guard test changes **only in the same merge
   as this slice, or after it**. Both LGs cite that pairing: this slice's LG and the LG of the
   slice that changes the guard. Before this slice merges, a capped A-4 severity GLM would fit
   uncapped, which is the FD 8027 defect itself.
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
   written, and DP-G1 orders the merge on the result.

## Goal

A `GlmSpec` whose `loss_treatment` is `capped` is fitted on the capped response: the same
coefficients as a `none` spec fitted on data capped by hand. The cap reaches every consumer of the
response inside `fit_glm`: the Tweedie profile, cross-validation, the fit, the separation check
and the dispersion. `spliced` and `excess` are refused by name with `LOSS_TREATMENT_UNIMPLEMENTED`,
as `fit_gbm` refuses them. Nothing fits uncapped while its spec and `spec_hash` say capped.
**Every fit runs FR-100's check.** For each Banding that a fitted factor applies, the frame being
fitted is checked. An empty band always refuses the fit with `BAND_EMPTY`. A thin band refuses
with `BAND_BELOW_MIN_EXPOSURE` when the Banding's `minimums.on_violation` is `fail`, and warns
(where DP-B2 rules) when it is `warn`. The fit Job surfaces each refusal as a `409` problem that
carries its `02` §5.1 code, as it already does for `FACTOR_RESOLUTION_FAILED`.

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
- **The EBM arm has the same gap. It is not in FD 8027.** `EbmSpec` (`modelling.py:1446`)
  inherits `loss_treatment`, and `fit_ebm` reads the response at `ebm.py:209` and never reads the
  treatment (`git grep -nEi "loss_treatment" -- packages/pricing-core/src/pricing_core/modelling/ebm.py`
  prints nothing). DP-L2 covers it.

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
  (`:1631`) and `EbmFitResult` (`:1790`) carry none. DP-B2 covers this.

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
   shows the FR-127 note (Task 2) and the FR-100 clause (Task 5) landing in a commit before or
   with the code, never after.
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
7. **The EBM arm, only if DP-L2 is ruled (a) (R4, red on main).** Acceptance 4 and 6, applied to
   `fit_ebm`.
8. **One function, one module (DP-L1).**
   `git grep -nE "def apply_loss_treatment" -- packages` prints exactly one line, and every arm
   imports it. `test_gbm.py`'s FR-127 tests (`:601`, `:628`) stay green unchanged, as guards.
9. **An empty band refuses every fit (R5, red on main).** For each of `fit_glm`, `fit_gbm`
   (both backends) and `fit_ebm`, a banding factor whose Banding was derived on one frame is
   fitted on a frame where one band is reached by no row. The fit raises `BandingError` with
   `code == "BAND_EMPTY"`. This is the 11:28:56 entry's *"a banding whose data moved is refused at
   fit"*. On main every arm fits, and `pytest.raises` reports *DID NOT RAISE*.
10. **A thin band under `on_violation="fail"` refuses (R6, red on main)**, with
    `BAND_BELOW_MIN_EXPOSURE`. The same frame under `warn` fits, and its warning is recorded where
    DP-B2 rules (R7). On main R7 fails because nothing is recorded. If DP-B2 is ruled (a), that
    failure is an `AttributeError` on the absent field, and the LG names it as that cause.
11. **The fit Job surfaces the refusal (R8, red on main).** A fit Job over a Banding with an empty
    band ends with status **`failed`**, its stored error code is **`BAND_EMPTY`**, and the problem
    status is `409`. On main the Job **succeeds**, so the assert on `failed` is the red. A test
    that asserts only a terminal state is not this test.
12. **The guards stay green, at base and at head.** A `none` GLM fit has coefficients identical
    to main's. A Banding that fits its frame reports nothing (`test_bandings.py:410`). FR-111's
    weight-0 exclusion runs **before** the banding check, so a band reached only by weight-0 rows
    is empty. The LG records each of these as a guard.
13. **SL-1543's guard test is untouched.** `git diff --stat origin/main...<slice branch>` lists
    no file of SL-1543's write set. This item is void only if DP-A4-3 has switched to (y), and
    then the pairing in "The SL-1543 guard test" item 2 is cited in the LG.
14. **The contract, only if DP-B2 is ruled (a).**
    `uv run python scripts/generate-contracts.py --check` exits 0, and the hand-authored fit-result
    schemas agree with the generated ones (`backend/tests/test_contracts.py`). A fit result stored
    before the slice, with no warnings field, still validates.
15. **The gate is green on the merge tree.** Both halves of the `CLAUDE.md` §11 commands pass,
    named against `origin/main...<slice branch>`.

## Global Constraints

- **`pricing-core` owns both rules** (ADR-703; `CLAUDE.md` §2). A notebook that calls `fit_glm`
  directly gets the cap and the banding check, as the fit Job does. This follows the
  `weights.py` pattern from SL-1675: one module, the arm's own error class passed in.
- **Order at each fit entry:** FR-111's `require_usable_weights`, then FR-100's check over the
  rows that remain, then `resolve_factors`. The loss treatment is applied where the response is
  read (`glm.py:577`, `gbm.py:645`, and `ebm.py:209` if DP-L2 is ruled (a)). The holdout
  response is treated as `gbm.py:684-686` treats it.
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
| 1 | SL-8031 — FD 8027's HIGH limbs: a capped GLM fits capped, and the banding check runs at fit | Tasks 0 to 8 below | `02` §3.5: FR-127 (the GLM arm, the EBM arm if DP-L2 is ruled (a)); `02` §3.2: FR-100 (the fit-time check); read only: FR-128, FR-111, FR-204 | this delta minted; FD 8027 minted; DP-B1, DP-B2, DP-G1 ruled, DP-L2 ruled before Task 3 | 2 |

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
  Banding's result in the LG, verbatim. **Any `BAND_EMPTY` is a STOP to the lead** before Task 4.
- [ ] **Step 4.** Read `to-lead.md` from 11:41:12 BST on this date for any entry on FD 8027,
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
- [ ] Run `scripts/run-small.sh` on `test_glm.py -k loss_treatment` at the base. **Record each red
  line verbatim, and its cause.** R1 and R2 must fail on the equality to the hand-capped fit.
  R3 must fail with *DID NOT RAISE*.

### Task 2 — FR-127 in the spec (`spec-change`)

- [ ] A dated note under the `02-modelling.md:2659-2661` paragraph: the GLM arm (and the EBM arm,
  under DP-L2 (a)) now applies `apply_loss_treatment` at the response read, and the function's
  module is now the one DP-L1 rules. The FR-127 row itself is unchanged, because it already
  requires this.

### Task 3 — FR-127 in the code

- [ ] Move `apply_loss_treatment` into its own module under DP-L1. It takes the arm's error class
  as `weights.require_usable_weights` does (`weights.py:91-97`). `gbm.py` imports it, and
  `modelling/__init__.py` keeps exporting the name.
- [ ] Apply it at `glm.py:577`, before the `x = design.to_numpy()` line, so all five consumers
  see the treated response.
- [ ] Under DP-L2 (a), also apply it at `ebm.py:209`, with R4 red first in `test_ebm.py`.
- [ ] R1 to R3 (and R4) green, and `test_gbm.py`'s FR-127 tests green unchanged.
- [ ] **DP-S1's split line.** Tasks 1 to 3 are one commit set that passes the gate alone.

### Task 4 — the FR-100 reds, on main

- [ ] **R5** (`test_glm.py`, `test_gbm.py` over `BACKENDS`, `test_ebm.py`;
  `@pytest.mark.req("FR-100")`). Derive a Banding on a frame with `propose_banding`. Then fit on a
  frame from which every row of one band has been removed (the data moved). Expect
  `BandingError` with `.code == "BAND_EMPTY"`.
- [ ] **R6.** A Banding with `minimums=(min_exposure_per_band=…, on_violation="fail")` and a band
  below the floor: expect `BAND_BELOW_MIN_EXPOSURE`.
- [ ] **R7.** The same Banding under `warn` fits, and its warning is recorded where DP-B2 rules.
- [ ] **Guard G-W.** A band reached only by weight-0 rows (FR-111) is `BAND_EMPTY`. This guard
  is green after Task 5 only. Record it as a guard of the ordering, not as a red of this slice.
- [ ] Run `scripts/run-small.sh` per file at the base, and record each red line and its cause.

### Task 5 — FR-100 in the spec (`spec-change`)

- [ ] One dated clause on the FR-100 row. It is the decision-maker's text from the RL that rules
  DP-B1, DP-B2 and DP-B3. It states which frame is checked, where a warning lands, and which
  columns the floors read. The `§5.2` `check_banding` signature (`02-modelling.md:2382-2388`)
  is unchanged.

### Task 6 — FR-100's warnings field (only if DP-B2 is ruled (a))

- [ ] Add one typed field to the fit result, as DP-B2 (a) names it, defaulting to empty so that
  stored results still validate. `contract-schema`: regenerate `docs/contracts/` and update the
  hand-authored fit-result schemas. `contract-guard`: `test_contracts.py` stays green.

### Task 7 — FR-100 in the code

- [ ] One helper beside `check_banding` in `bandings.py`. It takes the fitted rows, the factors
  and the bandings mapping, and runs `check_banding` once per distinct Banding that a factor
  (or an interaction operand, per Task 0 Step 2) applies. It returns the warnings.
- [ ] Each fit entry calls it after `require_usable_weights` and before `resolve_factors`.
- [ ] In `model_handlers.py:395-416`, map `BandingError` to `PlatformError(exc.code, …, 409, str(exc))`,
  as the `FactorResolutionError` clause does. Mapping `ModellingError` at that point would also
  catch `FactorResolutionError` and change its detail text, so name `BandingError`.
- [ ] **R8** (`backend/tests/test_model_jobs.py`, beside the `FACTOR_RESOLUTION_FAILED` test at
  `:596`). A fit Job over a Banding with an empty band is `failed`, with code `BAND_EMPTY`. Red
  at base first.
- [ ] R5 to R8 green, and G-W green.

### Task 8 — close

- [ ] `uv run python scripts/req-coverage.py`, the gate (both halves), the `LG-`'s closing acts,
  and, if DP-G1 was ruled (b) or (c), a re-run of the WF-699 journey test on the merge tree.

### Write set

- `docs/specs/02-modelling.md` (the FR-127 note; the FR-100 clause);
- `packages/pricing-core/src/pricing_core/modelling/` (`glm.py`, `gbm.py`, `bandings.py`,
  `__init__.py`, the new module DP-L1 names, and `ebm.py` under DP-L2 (a));
- `packages/pricing-core/tests/` (`test_glm.py`, `test_gbm.py`, `test_bandings.py`, and
  `test_ebm.py` under DP-L2 (a));
- `backend/src/app/worker/model_handlers.py` (the `BandingError` clause only);
- `backend/tests/test_model_jobs.py`;
- under DP-B2 (a): `packages/model-schema/src/model_schema/modelling.py` (the fit results),
  `docs/contracts/` (regenerated, plus the hand-authored schemas), and
  `backend/tests/test_contracts.py` if a guard needs a new path;
- the `LG-`.

**Not in it:** SL-1543's files and its guard test (see "The SL-1543 guard test and the G2 path");
`examples/fremtpl2/`; `frontend/src/` (a view of the warnings is a follow-on row, as with
SL-1675's DP-Z1); `LossTreatment` and `BandingMinimums` shapes; FR-110's limb.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-L1 | Where does `apply_loss_treatment` live once two or three arms call it? | (a) its own module, `pricing_core/modelling/loss_treatment.py`, taking the arm's error class as `weights.require_usable_weights` does (`weights.py:91-97`); `gbm.py` and `__init__.py` re-export it. (b) `glm.py` imports it from `gbm.py`; the GLM path then raises `GbmFitError`, the wrong arm's class. (c) a copy in `glm.py`. | **(a).** `CLAUDE.md` §2 forbids a shape defined twice, which rules out (c). (b) couples the GLM arm to the GBM module and names the wrong arm in every refusal. (a) is the pattern SL-1675 set two days ago. The spec already says *"it belongs beside the fit rather than inside it"* (`02:2659-2661`). | design | no — default (a), resolved at Task 3 Step 1 | — |
| DP-L2 | `EbmSpec` inherits `loss_treatment` and `fit_ebm` ignores it (`ebm.py:209`), which is the same silent class. FD 8027 names only the GLM limb. Does this slice fix the EBM arm too? | (a) yes: one call, one red (R4), and the auditor adds the limb to FD 8027 before it is minted, or files it. (b) no: the lead has an auditor file it as its own finding, and a later slice fixes it. | **(a).** With DP-L1 (a) the fix is one line and one test. Leaving it would close FD 8027's FR-127 limb while a capped `EbmSpec` still fits uncapped. The scope of a finding is the lead's to rule, so this is not picked here. | scope | yes, for Task 3's EBM step only | — |
| DP-B1 | Which frame does the fit-time check read? FR-100 says *"the Dataset Version"*; the fit receives the training partition. | (a) the rows the arm fits: the training frame after FR-111's weight-0 exclusion. (b) the whole Dataset Version, both partitions, which the fit entries do not receive. (c) both (a) and the holdout. | **(a).** A coefficient is estimated from the rows fitted, so a band empty in those rows is the *"coefficient estimated from no data"* that `check_banding`'s docstring names (`bandings.py:536-538`). (b) needs the handler to pass a frame `pricing-core` does not otherwise see, and it passes a band reached only in the holdout. A dated FR-100 clause records the reading (Task 5). | design | yes | — |
| DP-B2 | Where does a thin-band **warning** land? `check_banding` returns it, and no fit result has a field for it. | (a) a typed field on the three fit results (a tuple of strings, default empty), persisted with the model and in the generated contract. (b) the Job's progress message and the worker log only. (c) not in this slice: the slice ships the two refusals, and a warning is a follow-on row. | **(a).** FR-100's default mode is *"fitting warns"*, and a warning that reaches no artifact is the silent class FD 8027 is about. SL-1675's DP-Z1 ruling set the precedent: *"The persisted typed field is the \"never silent\" record"*. (a) adds Task 6 and the contract half. (c) is the smaller choice if the lead wants the HIGH limb narrow. | design | yes | — |
| DP-B3 | Which columns does the thin check read? `check_banding` defaults to `exposure_years` and `claim_count`, and `one_way` reads an absent column as 0 (`data/profile.py:372-377`). A fit frame without those columns would read every band as thin. | (a) the defaults, which the `BandingProposal` the Banding was proposed with also uses (`modelling.py:599-600`); a non-zero floor whose column is absent from the frame is refused by name, never read as 0. (b) derive from the spec: exposure from `spec.offset.column`, claims from the response or weight column. (c) add the two column names to `BandingMinimums`, a Banding shape change. | **(a).** It is what the proposal measured, so the floor and the stats that set it read the same columns. The refusal closes the absent-column trap. (b) is right for frequency and wrong for burning cost. (c) changes a stored shape for a fact the proposal already fixes. With floors of 0, the seed's case, the columns are not read at all. | design | no — default (a), resolved at Task 7 Step 1 | — |
| DP-G1 | When may the FR-100 limb merge relative to SL-1543 (G2)? The 11:29:53 entry put only the FR-127 limb off the G2 path. | (a) after SL-1543 merges, so G2 does not take the check's risk; this slice then re-runs the WF-699 journey. (b) before, if Task 0 Step 3's probe prints no `BAND_EMPTY` for any seed Banding. (c) whichever is ready first, the second re-merging `main` and re-running the journey, again only on a clean probe. | **The probe decides.** On a clean probe, (c): no seed fit changes outcome, and the floors are 0. On any `BAND_EMPTY`, STOP to the lead. The seed's Banding or its severity frame then has to change, and that is a G2 decision, not this slice's. | scope | yes | — |
| DP-S1 | If the 11:29:53 condition fires (the FR-127 limb joins G2) while DP-B1, DP-B2 or DP-G1 is still open, how does the FR-127 limb ship ahead? | (a) the lead asks the planner for a re-cut delta: SL-8031 keeps FR-100, and a new row takes Tasks 1 to 3 unchanged. (b) the slice merges whole, waiting for the FR-100 rulings. | **(a), only if the condition fires.** Tasks 1 to 3 are cut to pass the gate alone. Until then, one slice as the lead ordered. | scope | no — the default is one slice, reopened only by the condition | — |

A plan is *"`draft` while decision points are open, `active` on freeze"* (`document-ids.md`
§1.6). DP-L2, DP-B1, DP-B2 and DP-G1 are blocking and open, so this delta is `draft`. The
decision-maker rules them in one `RL-`. The plan is then frozen at its merge and made `active` by
a dated line. No status is set here (the maintainer gives the GO).

## The row, cut

SL-8031 is cut under `### WK-1178` in `docs/roadmap.md`, after `SL-1683`, as `draft`. No line is
written on `SL-1543`'s row. The guard pairing and DP-G1 live here and in this slice's LG, and the
lead writes any dated line on SL-1543 at dispatch.

## Hand-off (not this plan's writes)

- **The lead:** rule or route DP-L2 (the scope of FD 8027), and route DP-B1, DP-B2 and DP-G1 to
  the decision-maker; mint FD 8027 before this delta; GO the executor.
- **The auditor (FD 8027's owner):** under DP-L2 (a), add the EBM limb before the mint, or file
  it.
- **FR-110 (FD 8027, MEDIUM):** a separate WK-1178 delta, with the NB θ decision point and Task 0's
  `power(k)` check in the pinned glum, per the 11:28:56 entry.
- **DP-B2 (a)'s follow-on:** a WK-675 frontend row that shows the warnings on the model page. It
  gets its id when it is cut.

## Self-review

- **Spec coverage.** FR-127 (GLM arm, and the EBM arm under DP-L2) and FR-100 are each named
  with their section. FR-128, FR-111 and FR-204 are read only. No requirement id is added or
  changed.
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
  - `ebm.py`: `:121`, `:123`, `:209`;
  - `bandings.py`: `:49`, `:524`, `:558-563`, `:579-583`;
  - `weights.py:91-97`, `errors.py:53`, and `modelling/__init__.py`: `:10`, `:37`, `:99`, `:106`;
  - `model_schema/modelling.py`: `:325-342`, `:599-600`, `:740-787`, `:836`, `:1022`, `:1446`,
    `:1561`, `:1631`, `:1790`;
  - `model_handlers.py:395-416`, `backend/src/app/errors.py:124-125`, and
    `test_model_jobs.py:596`;
  - `test_gbm.py:601`, `:628`, and `test_bandings.py:344`, `:360`, `:375`, `:410`;
  - `02-modelling.md`: `:108`, `:183`, `:458-464`, `:2107`, `:2382-2388`, `:2659-2661`;
  - `examples/fremtpl2/model.py:229-262`.

  The name of the new module and the field are the rulings', not literals.
- **Convention 4.** `to-lead.md` was read after 11:29:53 BST at 2026-10-14 11:41:12 BST. The
  entries of 11:31:17, 11:34:03 and 11:34:58 do not rule on this subject. `gh pr list` was not
  run (no GitHub posts by brief). Task 0 Step 4 re-reads at dispatch.
- **Placeholders.** `<slice head>` and `<slice branch>` are values read when the slice runs.
