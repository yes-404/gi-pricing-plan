---
id: PL-1674
family: plan
kind: map
title: WK-1178 — rows whose declared weight is 0 are excluded from the fit and from every diagnostic, the slice before SL-1543's severity path (SL-1675): a dated Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1542, SL-1543, PL-1544, RL-1263]
---

# PL-1674 — WK-1178: rows whose declared weight is 0 are excluded from the fit and from every diagnostic (SL-1675)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1667`, this delta `relates:` the records it builds on:
> `PL-1542` and `SL-1543` (A-4, which this slice precedes). It adds **one slice row**, SL-1675
> (minted from working id 9887), under `### WK-1178` in [`../roadmap.md`](../roadmap.md). REQUIRED SUB-SKILL:
> subagent-driven-development (recommended) or executing-plans, task by task. Steps use checkbox
> (`- [ ]`) syntax. The executor also binds:
> - `test-driven-development`: every acceptance item is seen red **by its cause** on main before
>   the code that turns it green;
> - `python-test`: the `req` marker and the negative tests;
> - `python-package`: `pricing-core` stays standalone;
> - `spec-change`: Task 1;
> - `contract-schema` and `contract-guard`: Task 3's field;
> - `dev-commands`: `uv sync --all-packages` and both gate halves;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

*(Minted 2026-10-12 as PL-1674 from working id 9886, and its slice row as SL-1675 from working id
9887, early, in their own docs PR, on the maintainer's GO in the entry "2026-10-12 05:47:19 BST"
and the lead's allocation in the from-lead entry "2026-10-12 05:47:57 BST" (`doc-id.py next`
printed 1674 at `604ea084`). Quoted entries keep their working ids as written.)*

Filed under **working id 9886**. Its slice row is **working id 9887** (`draft`). Both were
reserved by the lead (team-lead to planner-wk674-s4, 2026-10-12, the task "plan the
zero-weight exclusion slice"). Written 2026-10-12 by the planner (seat planner-wk674-s4).
**Tree read:** `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a` (#1291). Every
`file:line` below is at that tree unless it is marked otherwise. The executor re-reads each one at
its base (Task 0).

## Authority

**The maintainer's (by delegation) entry, quoted in full** (`to-lead.md`, "2026-10-12 05:39:20
BST"):

> ## 2026-10-12 05:39:20 BST — SL-1543 severity block: (i) a small PRECEDING WK-1178 slice ACCEPTED; the diagnostics finding is RESTATED (your "actual weighted, expected not" does not match the code); S4 beat-as-fixture reading OK
> (i) ACCEPTED: exclude weight-0 rows from the fit AND from every diagnostic statistic. Reasoning:
> - FR-111 sets severity's weight to claim_count, so a non-claimant row carries weight 0, meaning no information.
> - Excluding it leaves the coefficients unchanged (your spike: 1e-15).
> - The severity GLM then shares dataset_version, split and holdout_part with frequency, so FR-190's holdout rule stands untouched. No placeholder response anywhere.
> (ii) is refused for now: it changes FR-190's meaning. (iii) is refused: the structure is A-4's point.
> Conditions on the slice:
> - Spec first (spec-change skill). One dated FR-111 clause: "rows whose declared weight is 0 are excluded from the fit and from every diagnostic (FR-171/FR-183)". It also states that a weight-0 row is excluded BEFORE the family's response-domain check, so a non-claimant's 0 never reaches Gamma.
> - Transparency: the diagnostics report the count of rows excluded for weight 0, per partition. Never silent.
> - A NEGATIVE weight, or a null weight, is still refused loudly. Only exact 0 is excluded.
> - Red first on main: the severity GLM on the full book with weight = claim_count gives today's refusal → green after; plus a diagnostics red showing rows and A/E including the weight-0 rows today.
> - G2 slips by this slice. SL-1543 continues only its non-severity Task 0 steps; record the slip in eta.
> THE FINDING, RESTATED. I read diagnostics.py at main:
> - _partition :358-363: y = the raw response, ae_overall = Σy / Σmu, BOTH UNWEIGHTED;
> - by-level A/E :373-374: both unweighted;
> - calibration :408: divides by bin_exposure (weighted, via _weights :131-138).
> So "actual weighted, expected unweighted" is NOT what the code does. The real defect is that the declared weighting scheme (_weighting :124-128, claim count for severity) is applied to SOME statistics (calibration) and not others (A/E overall and by level). For severity, A/E is per ROW, not per CLAIM, so a book where claim counts vary per row reads a different A/E than an actuary's Σw·y/Σw·μ. FR-183 is silent on weighting.
> - File it MEDIUM (a statistic inconsistent with its own declared scheme; not shown wrong against a spec), owner WK-1178.
> - An OQ asks which A/E the platform defines (per row, or weighted by the declared scheme), options + recommendation, spec text by ruling.
> - The (i) slice fixes ONLY the weight-0 exclusion. It does NOT change the A/E definition, so it does not pre-empt the OQ.
> S4 (your second message): beat as a one-off test fixture from S4's image, with SL 9883 repeating the proof against the real scheduler service. Correct reading.

**The evidence it rests on:** the lead's entries "2026-10-12 05:36:12 BST — SL-1543 PLAN DEFECT
(executor Task 0, read at 604ea084)" and "2026-10-12 05:38:06 BST — SL-1543 SPIKE RESULT (scratch,
no commits; fit_glm + compute_diagnostics directly = what the fit job calls,
model_handlers.py:374/:446; synthetic 20k frame)" (`from-lead-2026-10-09.md`). The spike's
figures, quoted: option A "FITS (coefs = claims-only to ~1e-15) but CORRUPTS holdout diagnostics:
PartitionDiagnostics.rows counts placeholder rows (14,000 vs 1,939), ae_overall 0.139 vs 0.999
claims-only, … lift bins 0/0"; and "NO fit-time row filter / exclusion / null-response handling
in code … or spec (02 FR-111, ModelSpecCommon)".

**The GO, the correction and DP-Z1:** the maintainer's (by delegation) entry "2026-10-12 05:47:19 BST — PL 9886/SL 9887: GO to activate and mint early, after ONE T-text correction; DP-Z1 = (a); SL-1549's three struck bullets accepted". Its correction is applied at the T-text
(Task 1), at R1 and Acceptance 4 (the CV scope), and at R1-GBM and R1-EBM (a claims-only fit).

**Not this slice — the A/E definition.** The entry's restated finding is filed separately in D14,
as FD 9889 (working, MEDIUM, owner WK-1178) and OQ 9891 (working: which A/E the platform defines).
This slice **does not change** how `ae_overall`, the by-level A/E or calibration are weighted. It
removes weight-0 rows from the populations those statistics are computed over, and nothing else.
A test that asserts a weighted A/E is out of scope, and so is a change to `_weighting` or
`_weights`. Either would pre-empt OQ 9891.

## Goal

A model whose spec declares a weight column (`spec.weight.kind == "column"`) treats every row whose
weight is **exactly 0** as absent. Such a row does not reach the fit, the family's response-domain
check, or any diagnostic. Each partition's diagnostics report how many rows were excluded. A
negative or a null weight is refused, as it is today. For severity under FR-111
(`weight = claim_count`), the full book now fits on the same `dataset_version`, split and
`holdout_part` as frequency. Its coefficients equal the claims-only fit's, and its diagnostics are
the claims-only frame's diagnostics plus the excluded count. That unblocks `SL-1543`'s severity
path without touching FR-190.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's
merge tree.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` exit 0 at the
   branch head (the ids are minted, so check 31 has no working-id line to except).
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids.
3. **Spec first.** `git log --format=%s origin/main..<slice head> -- docs/specs/02-modelling.md`
   shows the FR-111 clause landing in a commit before or with the code, never after.
   `git grep -n 'excluded from the fit and from every diagnostic' -- docs/specs/02-modelling.md`
   prints the FR-111 row.
4. **The severity full-book fit (red on main).** The severity GLM over a full book with
   `weight = claim_count` and weight-0 rows is refused on main with `GLM_FIT_FAILED`, and the
   cause in the message is the family's response domain (Task 2, R1). On the slice it fits, and,
   for the GLM without cross-validation, every coefficient equals the claims-only fit's to
   `1e-10`. With CV it holds only under the same folds, and otherwise it is not claimed (05:47:19).
   `uv run pytest -q packages/pricing-core/tests -k zero_weight` exits 0. The `LG-` quotes each
   red line.
5. **The diagnostics (red on main).** On main, `PartitionDiagnostics.rows` and `ae_overall`
   include the weight-0 rows (R2). On the slice, every field of every diagnostic the enumeration
   (Task 0) lists equals the same diagnostic computed over the frame with those rows removed.
   The one exception is the new count, which equals the number removed, per partition.
6. **The refusals stay loud.** A negative weight and a null weight are each refused on main and
   on the slice, with the same code (guards; green at base and head, and recorded as guards).
7. **The contract.** `uv run python scripts/generate-contracts.py --check` exits 0, and the
   hand-authored `docs/contracts/schemas/diagnostics.schema.json` agrees with the generated one
   (`backend/tests/test_contracts.py`). A stored `Diagnostics` JSON written before the slice, with
   no count field, still validates.
8. **The gate is green on the merge tree**, both halves of the `CLAUDE.md` §11 commands, named
   against `origin/main...<slice branch>`.

## Global Constraints

- **The rule is exact zero.** The mask is `weight == 0.0` on the weight column cast to `Float64`.
  It is never `<= 0`, never a tolerance, and never a null test. A negative weight is not 0, and a
  null weight cast to `Float64` is NaN, which is not equal to 0, so both pass through to today's
  refusal (Acceptance 6).
- **Only a declared weight column.** The rule reads `spec.weight` and nothing else. FR-111's
  frequency **offset** (`offset = log(exposure)`) is not a weight. Its zero-exposure refusal,
  `OFFSET_REQUIRED_FOR_FREQUENCY` (`glm.py:576-584`), is unchanged, and a guard test asserts it.
  Burning cost's `weight = exposure` *is* a declared weight, so its weight-0 rows are excluded too.
  Task 1's spec text says so.
- **Before the response-domain check, and before anything else reads the row.** The filter runs
  at the entry of each public function, before factor resolution. Then an excluded row does not
  influence base-level choice (`glm.py:204-231`, `_levels`, which uses the exposure series), the
  CV folds (`:261-343`), the Tweedie power profile (`:384-430`), the dispersion (`:894-920`) or
  GBM binning. An excluded row's response is never read, whatever it holds (0, a negative, a
  null).
- **`pricing-core` owns the rule** (ADR-703; `CLAUDE.md` §2: "`pricing-core` stays importable
  standalone"). A notebook calling `fit_glm` directly gets the same behaviour as the fit Job. The
  backend handler (`backend/src/app/worker/model_handlers.py:302-460`) is **not** changed. It
  already passes the full `frame` and `holdout` to the fit and diagnostics calls, and the FR-116
  model-offset arrays it computes at `:317-330` are aligned to those full frames. Filtering in the
  handler as well would make every count read 0.
- **No placeholder response anywhere** (05:39:20 (i)), and no change to FR-190 or to
  `_refuse_unshared_holdout` (`backend/src/app/platform/perils.py:639`).
- **The A/E definition is untouched** (Authority, last paragraph).

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | SL-1675 — weight-0 rows excluded from the fit and every diagnostic | Tasks 0 to 4 below | `02` §3.2: FR-111 (the dated clause); `02` §3.8: FR-171, FR-183, FR-184 (unchanged in meaning; each diagnostic's population), FR-187 (a backtest uses the same `_partition`) | nothing in code; this delta minted (D14); DP-Z1 ruled | 1 |

### Task 0 — re-read at the base, and enumerate every site (convention 4)

- [ ] **Step 1 — the enumeration, at the base, quoted in the `LG-`.** Every function that reads a
  frame's rows, for fit or diagnostics, and so must see the filtered frame. At `604ea084` it is
  this list, which the executor re-derives with
  `git grep -n -E 'def (fit_glm|fit_gbm|fit_ebm|compute_diagnostics|compute_gbm_diagnostics|compute_ebm_diagnostics|backtest_model|_partition)\b' -- packages/pricing-core/src`
  plus `git grep -n '_partition(' -- packages/pricing-core/src`. Any site beyond this list is
  added to the `LG-` and treated the same way.

  | Site (`packages/pricing-core/src/pricing_core/modelling/…`) | What reads the rows |
  |---|---|
  | `glm.py:523` `fit_glm` | factor resolution and `_levels` base choice; the response and the domain check (`:649` → `GLM_FIT_FAILED` `:688`); the offset and `model_offset` (FR-116); the weights (`:591-593`); the CV path; the Tweedie profile; dispersion; the covariance |
  | `gbm.py` `fit_gbm` | `_weights(data, …)` (`:634`) and the holdout's `_weights(holdout, …)` for early stopping (`:686`); the encoding and binning |
  | `ebm.py` `fit_ebm` | the weight column (`:201-202`) |
  | `diagnostics.py:338` `_partition` | `rows` (`:445`); `ae_overall` (`:360-363`); the by-level A/E cells (`:366-393`); lift and calibration bins (`:399-419`, binned by `mu / exposure`, where a weight-0 row lands in bin 1 at rate 0); residuals (`:425-440`); `gini` (`:442`) |
  | `diagnostics.py:604` `compute_diagnostics` | both partitions (`:634`, `:645`); deviance and null deviance (`:655-659`; the null uses `mean(y)` over the rows); log-likelihood, AIC and BIC (`:663-671`; BIC uses `train.height`); `_type_iii` (`:683`, refitting on `train`); `degrees_of_freedom` (`:711`); complexity's `exposure_total` and `claims_total` (`:690-698`) |
  | `diagnostics.py:739` `backtest_model` | its one partition (`:790`) |
  | `diagnostics.py:1267` `compute_gbm_diagnostics` | both partitions (`:1300`, `:1309`); permutation importances (`:876`, weights `:904`); `_sweep` (`:1154`, weights `:1205`); complexity (`:1384`) |
  | `diagnostics.py:1416` `compute_ebm_diagnostics` | both partitions (`:1443`, `:1452`); complexity (`:1469`) |

- [ ] **Step 2 — the base behaviour of the refusals.** On a small synthetic severity frame, the
  executor runs each arm (`fit_glm`, `fit_gbm`, `fit_ebm`) once with one negative weight and once
  with one null weight, and quotes the code and the cause. **If any arm does not refuse a
  negative or a null weight at the base**, the executor stops and reports. That is a separate
  defect, and the guard of Acceptance 6 cannot be green at the base.
- [ ] **Step 3 — the shared-path census.** `git diff --name-only origin/main...origin/<branch>`
  for each branch in flight. The `LG-` names every shared path. `docs/contracts/` is the likely
  one: `SL-1669` (gate running at this tree) and `SL-1549` both regenerate
  `docs/contracts/openapi/generated.json`. The later PR re-runs `generate-contracts.py` after the
  earlier one merges.

### Task 1 — the spec, first (`spec-change`)

- [ ] Append to FR-111's row in `docs/specs/02-modelling.md` (`:143` at `604ea084`) this dated
  clause, verbatim (the T-text). It lands in the same commit as Task 2's code, or in an earlier
  one:

  > *(Amended 2026-10-12, WK-1178, SL-1675, on the maintainer's (by delegation) entry
  > "2026-10-12 05:39:20 BST", (i).)* **Rows whose declared weight is 0 are excluded from the
  > fit and from every diagnostic (FR-171/FR-183).** A row whose weight column holds exactly 0
  > carries no information: a non-claimant under severity's `weight = claim_count`, or a
  > zero-exposure row under burning cost's `weight = exposure`. Under a weighted likelihood a
  > weight-0 row contributes nothing; excluding it also removes it from the steps that do not
  > read the weight (binning, cross-validation folds, row counts), which is intended: a row with
  > no information should not shape them. The exclusion is applied **before the family's response-domain check**,
  > so a non-claimant's 0 never reaches the Gamma family. It is also applied before anything else
  > reads the row, and an excluded row's response is never read. Only an exact 0 is excluded. A
  > negative or a null weight is still refused. FR-111's frequency offset is not a weight, and a
  > zero exposure there is still refused (`OFFSET_REQUIRED_FOR_FREQUENCY`). Each partition's
  > diagnostics report the number of rows excluded for weight 0
  > (`PartitionDiagnostics.rows_excluded_zero_weight`), so the exclusion is never silent. This
  > clause does not change how any diagnostic is weighted (FR-184).

- [ ] In `02` §4's Diagnostics example (`:1700-1711`, the `train` partition), add
  `"rows_excluded_zero_weight": 0` beside `"rows"`. Then add one sentence under the example: the
  field is the per-partition count of FR-111's weight-0 exclusions, and it is `null` on an
  artifact written before 2026-10-12.
- [ ] `python3 scripts/audit-docs.py` before the commit (`CLAUDE.md` §0).

### Task 2 — the fit, red first on main

- [ ] **R1 (red on main, by cause):** in `packages/pricing-core/tests/test_glm.py`, mirroring its
  neighbours' fixtures, build a severity spec (Gamma, log link, `weight = claim_count`) over a
  synthetic book in which some rows have `claim_count = 0`. Use two variants: a response of 0 on
  those rows, and a null response on those rows.
  - On main, `fit_glm` raises `GlmFitError` with code `GLM_FIT_FAILED`, and the quoted cause is
    the family's domain ("out of the valid range"). A `GLM_FIT_FAILED` whose cause is anything
    else is a test defect (convention 2).
  - Green after: the fit succeeds, and every coefficient equals the claims-only frame's fit to
    `1e-10`. **This parity is claimed for the GLM without cross-validation only** (the R1 spec
    selects no penalty by CV). Where CV selects the penalty, it holds only under the same folds,
    so the test either fixes the folds to the claims-only rows or states the parity as not
    claimed. Excluding a row changes the fold assignment, which is intended (05:47:19; the T-text).
  - Marked `req("FR-111")`.
- [ ] **R1-GBM, R1-EBM — equality with a CLAIMS-ONLY fit (red on main):** in `test_gbm.py` and
  `test_ebm.py`, the same book with the weight-0 rows given a *non-zero* response, so the fit
  runs on main. The comparison is with a fit over the **claims-only** frame, **not** with today's
  fit over the full frame (05:47:19). On main, the full-book fit's predictions over the
  claims-only rows differ from the claims-only fit's, because GBM's and EBM's binning see the
  extra rows. Green after: they equal the claims-only fit's, to the arm's tolerance, which the test
  states. If they are already equal on main for an arm, that arm's test is recorded as a guard,
  not a red.
- [ ] **R1-all-zero:** every training row has weight 0. After the change, each arm refuses with
  its existing code, and the message says that every row was excluded for weight 0. No new error
  code is added.
- [ ] **Guards (green on main and after):** a negative weight is refused, and a null weight is
  refused, with the codes Task 0 Step 2 quoted. A zero exposure under the frequency **offset** is
  still `OFFSET_REQUIRED_FOR_FREQUENCY`.
- [ ] **The code:**
  - One function in `pricing_core.modelling` (module placement per `python-package`) returns
    the row mask and the excluded count for a spec and a frame. It reads `spec.weight` only.
  - `fit_glm`, `fit_gbm` (train **and** its holdout) and `fit_ebm` apply it at entry, before
    `resolve_factors`, and filter `model_offset` with the same mask.
  - `diagnostics._weights` and `gbm._weights` are not merged in this slice.

### Task 3 — every diagnostic, red first on main, and the count

- [ ] **R2 (red on main):** in `packages/pricing-core/tests/test_diagnostics.py`, a severity fit
  on the claims-only frame, then `compute_diagnostics` over train and holdout frames that **also**
  hold weight-0 rows. On main, `rows` counts them and `ae_overall` differs from the claims-only
  value (the spike's 14,000 vs 1,939 and 0.139 vs 0.999 are the shape). Marked `req("FR-171")`
  and `req("FR-183")`.
- [ ] **R3, the parity test (red on main):** for each diagnostic entry point in Task 0's table
  (`compute_diagnostics`, `compute_gbm_diagnostics`, `compute_ebm_diagnostics`,
  `backtest_model`), compare the result over the frame with weight-0 rows against the result over
  the frame without them.
  - Compare **every** field, walked from the result models' `model_fields`, so a field added
    later cannot escape the comparison. Floats use a stated tolerance.
  - The only allowed difference is `rows_excluded_zero_weight`, which equals the count removed
    from that partition. Train and holdout get **different** counts in the fixture, so a swapped
    count is caught.
  - Marked `req("FR-187")` for the backtest case.
- [ ] **The contract field:**
  - `PartitionDiagnostics` (`packages/model-schema/src/model_schema/diagnostics.py:142-170`)
    gains `rows_excluded_zero_weight: int | None = Field(default=None, ge=0)`, with a comment.
    `None` means the artifact predates the rule. `0` means the rule ran and excluded nothing.
  - It is optional because stored `Diagnostics` artifacts written before the slice must still
    validate (Acceptance 7). A test loads a pre-slice JSON fixture without the field.
  - `_partition` takes the count from its caller, and each entry point filters its frames (and
    `model_offset_train`/`_holdout`) at entry, before predicting.
  - `docs/contracts/` is regenerated (`scripts/generate-contracts.py`). The hand-authored
    `docs/contracts/schemas/diagnostics.schema.json` gains the property (`contract-schema`).
    `backend/tests/test_contracts.py` stays green.
- [ ] **One backend test**, in `backend/tests/test_diagnostics.py`, mirroring its neighbours. A
  severity fit Job over a dataset version with weight-0 rows completes, and the stored artifact's
  two partitions carry their counts. This is the path `model_handlers.py:374/:446` runs, which
  the spike called directly.

### Task 4 — close

- [ ] `uv run python scripts/req-coverage.py`, the gate (both halves), the `LG-`'s closing acts,
  and a dated line on `SL-1543`'s row that its severity path is unblocked (the lead's, at merge).

### Write set

- `docs/specs/02-modelling.md` (FR-111's row; §4's example);
- `packages/pricing-core/src/pricing_core/modelling/` (`glm.py`, `gbm.py`, `ebm.py`,
  `diagnostics.py`, and the one helper);
- `packages/model-schema/src/model_schema/diagnostics.py`;
- `docs/contracts/` (regenerated, plus the hand-authored `schemas/diagnostics.schema.json`);
- `packages/pricing-core/tests/` (`test_glm.py`, `test_gbm.py`, `test_ebm.py`,
  `test_diagnostics.py`, `test_backtests.py`);
- `backend/tests/test_diagnostics.py`;
- the `LG-`.

**Not in it:** `backend/src/` (Global Constraints); `frontend/src/` (DP-Z1, ruled (a)); `_weighting`,
`_weights` and the A/E formulas (OQ 9891).

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-Z1 | Does the Diagnostics view show the new count in this slice? The artifact and the API carry it either way (Task 3). | (a) not in this slice. The count is in the artifact and in the generated client types, and showing it is a follow-on frontend row. (b) in this slice: one line per partition in the Diagnostics view (`/models/:slug/diagnostics`), with a component test. | **(a).** G2 slips by this slice (05:39:20), so it stays as small as the rule allows. The maintainer's condition, "the diagnostics report the count … never silent", is met by the persisted, typed field that every reader of the artifact sees. (b) adds a frontend gate half, a lane and a view owner to a G2-path fix. The follow-on is named in the Hand-off so it is not lost. | scope | no longer: ruled | **ruled (a)** by the maintainer's (by delegation) entry "2026-10-12 05:47:19 BST — PL 9886/SL 9887: GO to activate and mint early, after ONE T-text correction; DP-Z1 = (a); SL-1549's three struck bullets accepted": "DP-Z1 = (a): artifact and API now, the view later in a WK-675 frontend row, given an id when it is cut, so it is not orphaned. The persisted typed field is the \"never silent\" record." |

A plan is "`draft` while decision points are open, `active` on freeze" (`document-ids.md` §1.6).
DP-Z1 is ruled (05:47:19), so no decision point is open. This delta is minted early, at the
maintainer's GO in the same entry ("Mint PL 9886 + SL 9887 early as a tiny docs PR: yes"). It
is merged `draft` and frozen at that merge. It goes `active` by its status line in SL-1675's
activation commit, and SL-1675 stays `draft` until its executor's activation.

## The row, cut

SL-1675 is cut under `### WK-1178` in `docs/roadmap.md`, after `SL-1669`, as `draft`. A dated line
on `SL-1543`'s row records the new need: SL-1675 merges before its severity steps
(05:39:20, "G2 slips by this slice").

## Hand-off (not this plan's writes)

- **The lead:**
  - record G2's slip in `eta` (05:39:20);
  - GO the executor;
  - at merge, write the dated line that `SL-1543`'s severity path is unblocked.
- **The D14 minter:** FD 9889 and OQ 9891, which are not this slice's (Authority).
- **DP-Z1 (a), the follow-on:** a WK-675 frontend row (the Diagnostics view) shows
  `rows_excluded_zero_weight` per partition, labelled as FR-111's exclusion. It gets its id when it
  is cut (05:47:19), so it is not orphaned.

## Self-review

- **Spec coverage.** FR-111 gets the dated clause. FR-171, FR-183, FR-184 and FR-187 are named as
  the requirements whose populations change and whose meaning does not. No requirement id is added
  or changed.
- **The 05:39:20 conditions at every site** (convention 5):
  - spec first: Task 1 and Acceptance 3;
  - before the response-domain check: Global Constraints, Task 1's text and R1;
  - the count per partition: Task 3, Acceptance 5 and the contract;
  - negative or null still refused: Global Constraints, Task 0 Step 2, the guards and Acceptance 6;
  - red first on main, for both the fit and the diagnostics: R1, R2, R3 and Acceptances 4 and 5;
  - the A/E definition untouched: Authority, Global Constraints and the Write set.
- **Literals verified at `604ea084`** (conventions 1 and 3):
  - `diagnostics.py` `_weighting` `:118-129`, `_weights` `:132-138`, `_partition` `:338-455`
    (`ae_overall` `:360-363`; `rows=data.height` `:445`), `compute_diagnostics` `:604-716`,
    `backtest_model` `:739`, `_partition` callers `:634/:645/:790/:1300/:1309/:1443/:1452`;
  - `glm.py` `fit_glm` `:523`, the offset refusal `:576-584`, weights `:591-593`,
    `GLM_FIT_FAILED` `:688`; `gbm.py:634/:686`; `ebm.py:201-202`;
  - `PartitionDiagnostics` `:142-170`; FR-111 at `02:143`; the §4 example `:1700-1711`;
  - `model_handlers.py:317-330/:374/:446`.
  The helper's name and module are the executor's.
- **Convention 4.** `to-lead.md` was read for the 05:39:20 entry, and `from-lead-2026-10-09.md`
  for 05:36:12 and 05:38:06. No other entry on this subject was found when read at 2026-10-12 05:45:02 BST.
- **Placeholders.** `<slice head>`, `<slice branch>` and `<branch>` are values read when the slice
  runs.
