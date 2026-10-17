---
id: LG-8082
family: ledger
title: WK-1178 slice SL-1734 — FD-1723's HIGH limbs, a capped GLM and EBM fit capped (FR-127) and the banding check runs at fit (FR-100), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-17
owner: executor
phase: P2
work: WK-1178
slice: SL-1734
plans: [PL-1733]
corrected_by: []
relates: [SL-1734, PL-1733, FD-1723]
---

# LG-8082 — WK-1178 slice SL-1734: FD-1723's HIGH limbs (FR-127 GLM and EBM, FR-100 at fit)

**GO:** the maintainer's entry "2026-10-17 13:23:18 BST" in `to-lead.md` (GO SL-1734, PL-1733: needs 1–2 met, Task 0 Step 3's G2 probe first as the in-slice STOP, census mechanical, contracts regenerate on the later PR).
**Gate:** none granted to this seat; the full gate (both halves) and the DB tests below are owed.
**MERGE-ACK:** not yet given.
**Audit:** not yet.

## Tasks

Branch `sl-8031-wk1178-fd8027-prep` (its prep name), worktree `.claude/worktrees/sl-8031-prep` (the branch was already checked out there, clean at `cab355ad`, so `sl-1734` could not be added), re-merged with `origin/main` `6bdd2571`.

### Task 0

- **Step 1, the cites at the base.** The premises hold: `git grep -nEi "loss_treatment" -- …/glm.py …/ebm.py` prints nothing; `loss_treatment.py` was absent; `BandingWarning` was undefined; `check_banding` at `bandings.py:524`; `fit_glm` at `glm.py:524`; the response read at `glm.py:577`; `apply_loss_treatment` at `gbm.py:178`, called at `gbm.py:645` and `:684`. The prep branch already held the red tests (`496954c8`, `cab355ad`).
- **Step 2, every `resolve_factors(` hit** (`git grep -nE "resolve_factors\(" -- packages/pricing-core/src`, at the base):

| hit | kind |
|---|---|
| `glm.py:562` (`fit_glm`) | fit |
| `gbm.py:636` (`fit_gbm`, training) and `gbm.py:682` (`fit_gbm`, holdout) | fit |
| `ebm.py:123` (`fit_ebm`) | fit |
| `gbm.py:1293` (`predict_gbm`) | score |
| `predict.py:109`, `:357` (`_term_vectors`, `predict_ebm`) | score |
| `diagnostics.py:370`, `:592`, `:1074`, `:1146`; `transparency.py:283`, `:450` | diagnose |
| `rate_tables/weights.py:103` (`_resolved_series`) | score |
| `factors.py:112` | the definition |

No other fit hit. The holdout resolve at `gbm.py:682` is not banding-checked: DP-B1 reads the rows fitted.
- **Step 3, the G2 probe (DP-G1), CLEAN.** A throwaway test file (not committed; its source is outside the repo) run through `run-small.sh <worktree> backend/tests/test_zz_g2_probe.py`, rc 0. It builds the seed's table with `examples/fremtpl2/seed.py`'s `build_csv(None)` over the sha256-pinned freMTPL2 files, applies the seed recipe's rename, cast and `exposure_years <= 1.05` filter, splits with `pricing_core.data.splits.partition(method="random", seed=20260827, fractions={"train": 0.75, "test": 0.25})`, proposes each seed Banding with `propose_banding` (QUANTILE × 5, on the validated table, as `create_demo_bandings` does) and runs `check_banding` against the frequency training frame and the claims-only (`claim_count > 0`) severity training frame. Output, verbatim:

```text
raw rows 678013
validated v2 rows 677442
train 508364; claims-only severity train 25621
driv_age_band: boundaries=[18.0, 32.0, 40.0, 48.0, 57.0, 100.0] labels=['18-31', '32-39', '40-47', '48-56', '57+'] minimums=min_exposure_per_band=Decimal('0') min_claims_per_band=0 on_violation='warn'
  frequency-train: OK warnings=()
  severity-claims-only-train: OK warnings=()
veh_age_band: boundaries=[0.0, 2.0, 4.0, 8.0, 12.0, 100.0] labels=['0-1', '2-3', '4-7', '8-11', '12+'] minimums=min_exposure_per_band=Decimal('0') min_claims_per_band=0 on_violation='warn'
  frequency-train: OK warnings=()
  severity-claims-only-train: OK warnings=()
veh_power_band: boundaries=[4.0, 5.0, 6.0, 7.0, 8.0, 15.0] labels=['4-4', '5-5', '6-6', '7-7', '8+'] minimums=min_exposure_per_band=Decimal('0') min_claims_per_band=0 on_violation='warn'
  frequency-train: OK warnings=()
  severity-claims-only-train: OK warnings=()
```

No `BAND_EMPTY`, so no STOP. Not measured: the `--rows` sampled seed. The seed's default minimums are 0, so nothing is thin either.
- **Step 4, `to-lead.md` entries since "2026-10-14 11:52:51 BST" on FD-1723 (FD 8027), FR-127, FR-100, SL-1543 or this plan:** "2026-10-14 11:52:51 BST" (DPs ruled), "2026-10-14 12:12:51 BST" (FR-100 clarification clause for DP-B1 and DP-B3; the typed `BandingWarning`), "2026-10-14 13:55:54 BST" (FD 8027 severities, the severity rule), and "2026-10-17 13:23:18 BST" (the GO).

### Tasks 1 to 3, FR-127

- **Reds at the base** (`run-small.sh` on `test_glm.py`, `test_ebm.py`, `test_banding_warnings.py`, before any code): the capped GLM tests failed on the coefficient equality to the hand-capped fit (`array([6.0979, -0.5692])` against `array([5.5265, -0.2125])` for `fixed`; the same shape for `cv` and `tweedie`); the EBM capped test failed the same way; the `spliced` and `excess` refusals did not raise. One prep defect, not a cause red: the `_factor` helper in `test_glm.py` passed `type` twice (`TypeError … multiple values for keyword argument 'type'`), fixed on its own in `f2e60935`.
- **Fix:** `pricing_core/modelling/loss_treatment.py` (new), `apply_loss_treatment(response, treatment, error)`; `gbm.py` imports it and passes `GbmFitError` at both reads; `fit_glm` applies it at the response read passing `GlmFitError`; `fit_ebm` passes `EbmFitError`; `modelling/__init__.py` still exports the name. Green: `test_glm.py`, `test_ebm.py`, `test_gbm.py` 235 passed together, with the FR-100 reds then still red (14 failed before Tasks 6 and 7).

### Tasks 5 to 7, FR-100

- **Model-schema:** `BandingMeasure`, `ExposureBandingWarning`, `ClaimCountBandingWarning`, `BandingWarning` (the discriminated union of the plan's form), and `banding_warnings: tuple[BandingWarning, ...] = ()` declared once on each of the three fit results (no shared base exists). The claim-count arm is **strict** `int`: pydantic's lax `int` accepted `Decimal("3")`, which `test_a_malformed_warning_is_refused[bad2]` refuses.
- **pricing-core:** `check_banding` returns `tuple[BandingWarning, ...]` with `Decimal` and `int` floors; `check_fit_bandings` (new) runs it once per distinct Banding the fitted factors use, and each fit entry calls it after `require_usable_weights`, before `resolve_factors`, writing the result into `banding_warnings` unchanged. A non-zero floor whose column is absent is refused by name with `BandingError("FACTOR_RESOLUTION_FAILED")`, the code `propose_banding` already uses for a banding it cannot work on (DP-B3).
- **Backend:** `model_handlers.py` maps `BandingError` to `PlatformError(exc.code, …, 409, str(exc))`, ahead of the `FactorResolutionError` clause.
- **Contracts:** `scripts/generate-contracts.py` regenerated `docs/contracts/openapi/generated.json` and `docs/contracts/schemas/generated/model.schema.json`; `--check` rc 0; `test_contracts.py` needed no hand-authored change.
- **Spec (`02-modelling.md`):** the dated clarification on the FR-100 row (DP-B1, DP-B3); the `banding_warnings` paragraph and the `"banding_warnings": []` field in the §4.8 GBM example; the §5.2 `check_banding` signature amended in place and `check_fit_bandings` added; the FR-207 staged-contract entry; the FR-127 dated note under the `apply_loss_treatment` paragraph.
- **Deltas against the plan, named:** (1) `test_bandings.py` asserted the warning *text* (`"below the minimum" in w`), which a typed record cannot satisfy; that one assertion now checks `measure == "claim_count"` and `observed < minimum` (the plan said the asserts at `:365` and `:403` keep a non-empty tuple, which they do). (2) The warnings are built by `check_banding` itself, so the refusal text for `BAND_BELOW_MIN_EXPOSURE` is rendered by a private `_describe`.
- **Proof so far (all through `run-small.sh`):** `test_glm.py` + `test_ebm.py` + `test_gbm.py` 235 passed; `test_bandings.py` + `test_banding_warnings.py` + `backend/tests/test_contracts.py` 209 passed, 2 skipped. `ruff check packages backend` clean; `mypy` clean over 241 files.

## PRs

Not opened yet; the lead opens the PR.

## Owed (the lead's grant)

- **DB-needing:** R8 `backend/tests/test_model_jobs.py::` the fit Job over an empty band (written in the prep, not run: it needs the per-worktree database).
- **Frontend half:** `pnpm --dir frontend install --frozen-lockfile`, `generate:api`, `lint`, `type-check`, `test` (`models.test-d.ts` reads the regenerated types); no `frontend/` file is edited.
- **The full Python gate**, and the WF-699 journey re-run on the merge tree by whichever of this slice and SL-1543 merges second (Task 8).
