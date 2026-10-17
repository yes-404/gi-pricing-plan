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
**Gate:** gate 1 @`d1884116` (16:24 to 17:28 BST, `scratch/sl1734-gate/`) RED: the `_fit` banding sink, the input-free raise at `modelling.py:365`, four frontend fixtures; fixed at `5e08d5ce` (executor-1734f). Gate 2 @`5e08d5ce` (tree `22c1e8d065fac74be3d8c4fbdf079fdb93456d76`, 16:53:27 to 17:54:18Z, `scratch/sl1734b-gate/`): ruff, mypy, import_linter, req_coverage, contracts rc 0; frontend install, generate:api, lint, type-check, test, build rc 0; demo designed stop, `--journey wf-699` rc 0; audit_docs rc 1 (the working-id check 31, expected); pytest rc 1 `14 failed, 5901 passed, 4 skipped` = 13 docs-check cascade plus `test_worker_raise_sites` (the census missed `safe_error_detail(exc)`). `a261c2bf` (executor-1734g) is a test-list change only, accepted with no re-gate by the maintainer ("2026-10-17 18:56:17 BST", condition met at "2026-10-17 18:59:23 BST").
**MERGE-ACK:** not yet given.
**Audit:** written below (auditor-1734, 2026-10-17, head `a261c2bf`); proposed verdict only.

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

- **The probe file** (`backend/tests/test_zz_g2_probe.py` while it ran, then moved out of the tree and deleted from it; sha256 `2dc627852d0a7858841bf1b58ae8da61a8e26ebba43726e7bea4d5b7f233bdc1` of the content below, in which the `OUT` path is the seat's scratchpad):

```python
"""SL-1734 Task 0 Step 3 G2 probe. READ-ONLY, NOT COMMITTED."""
import io, sys, uuid
from pathlib import Path
import polars as pl

WT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WT / "examples" / "fremtpl2"))
sys.path.insert(0, str(WT / "backend" / "src"))
OUT = Path("/tmp/claude-1000/-home-puzhenhao1989-gi-pricing-plan/a0ce4038-148b-4ee1-855a-3f3d3ef0d61f/scratchpad/g2-probe.txt")


def test_probe():
    import seed
    import model as seedmodel
    seed.DATA_DIR = Path("/home/puzhenhao1989/gi-pricing-plan/examples/fremtpl2/data")
    from pricing_core.data.splits import partition
    from pricing_core.modelling.bandings import check_banding, propose_banding
    from model_schema import BandingProposal, BandingMethod

    lines = []
    raw = pl.read_csv(io.BytesIO(seed.build_csv(None)), infer_schema=False)
    import re
    snake = lambda c: re.sub(r"(?<!^)(?=[A-Z])", "_", c).lower()
    cols = {c: seed.RENAMES.get(snake(c), snake(c)) for c in raw.columns}
    df = raw.rename({k: v for k, v in cols.items() if k != v})
    casts = {"float": pl.Float64, "int": pl.Int64}
    df = df.with_columns([pl.col(c).cast(casts[t]) for c, t in seed.NUMERIC.items() if c in df.columns])
    lines.append(f"columns: {df.columns}")
    lines.append(f"raw rows {df.height}")
    df = df.filter(pl.col("exposure_years") <= seed.MAX_EXPOSURE)
    lines.append(f"validated v2 rows {df.height}")
    parts = partition(df, method="random", seed=seedmodel.SPLIT_SEED, fractions={"train": 0.75, "test": 0.25})
    train = parts["train"]
    sev = train.filter(pl.col("claim_count") > 0)
    lines.append(f"train {train.height}; claims-only severity train {sev.height}")
    for slug, col in seedmodel.CONTINUOUS_FACTORS:
        b = propose_banding(
            df,
            BandingProposal(dataset_version_id=uuid.uuid4(), column=col, method=seedmodel.BANDING_METHOD, n_bands=seedmodel.BAND_COUNT),
            dataset_id=uuid.uuid4(), slug=f"probe-{col}",
        )
        lines.append(f"{slug}: boundaries={list(b.boundaries)} labels={list(b.labels)} minimums={b.minimums}")
        for name, fr in (("frequency-train", train), ("severity-claims-only-train", sev)):
            try:
                w = check_banding(fr, b)
                lines.append(f"  {name}: OK warnings={w!r}")
            except Exception as e:  # noqa: BLE001
                lines.append(f"  {name}: RAISED {type(e).__name__} code={getattr(e,'code',None)} {e}")
    OUT.write_text("\n".join(lines) + "\n")
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
- **Named delta: `packages/pricing-core/tests/test_bandings.py:369`.** The plan task that makes `check_banding` return typed records is Task 6, the `pricing_core/modelling/bandings.py` item; that item says `:365` and `:403` keep their asserts (a non-empty tuple) and `:386`, `:406`, `:413` keep `== ()`, and it does not mention `:369`. Old line, verbatim: `    assert all("below the minimum" in w for w in warnings)`. New line: `    assert all(w.measure == "claim_count" and w.observed < w.minimum for w in warnings)`. A `BandingWarning` is not a string, so the old assert cannot hold. The new one is not looser: it asserts the measure and that each record is truly below its floor, which the text check did not. The `:365` assert (`assert warnings`) is unchanged.
- **Proof so far (all through `run-small.sh`):** `test_glm.py` + `test_ebm.py` + `test_gbm.py` 235 passed; `test_bandings.py` + `test_banding_warnings.py` + `backend/tests/test_contracts.py` 209 passed, 2 skipped. `ruff check packages backend` clean; `mypy` clean over 241 files.
- **DP-1734-A ruled (a) at 2026-10-17 13:48:36 BST:** reuse `FACTOR_RESOLUTION_FAILED` for a non-zero banding floor on an absent column; `check_banding`'s detail now names the column and the floor value; `test_bandings.py::test_a_non_zero_floor_on_an_absent_column_is_refused_naming_column_and_floor` asserts the code and the column, red first (cause: the detail named `claim_count` but not the floor `37`), then green (`test_bandings.py` 29 passed).
- **R8 (the DB window, `small-test` slot, one hold, 2026-10-17 13:55 BST; script `~/gi-pricing-plan.local/scratch/sl1734b-dbwin.sh`):** `test_a_fit_over_a_banding_with_an_empty_band_fails_with_band_empty`. At the base `7aa2b6e0` (the slice's parent before `9270bb0d`, detached worktree, tree `c555bac4`) RED by cause: `assert <JobStatus.SUCCEEDED> is <JobStatus.FAILED>` (the Job succeeds over an empty band). At head `fff53c72` (tree `2b5b85fb`) GREEN: 1 passed. Method delta: the template database holds 33 `blobs` rows whose objects are absent from the test bucket, so the fixture's `put` dedups to a missing object (`BLOB_NOT_FOUND` in the ingest Job, red by the wrong cause); the window truncates `blobs` CASCADE in its own cloned database and uses its own bucket (`GIP_TEST_BUCKET`).

## PRs

Not opened yet; the lead opens the PR.

## Owed

- **The 13 docs-check cascade pytest failures** resolve when the working ids are minted at the PR (`audit-docs` check 31 green after the mint); re-check on the minted tree.
- **WF-699 journey re-run** on the merge tree by whichever of this slice and SL-1543 merges second (Task 8).
- **Full PR CI** on the opened PR (the maintainer, "2026-10-17 18:56:17 BST").

## Gate-red fixes (after the first gate)

- **`5e08d5ce`** (executor-1734f): R1 `BandingError` is also a `CodedError` and `_fit` persists `safe_error_detail(exc)` (sentinel test `test_a_banding_refusal_in_a_fit_keeps_its_text_and_no_row_value`); R2 the banding-warning reference message in `errors.py`/`modelling.py` is a literal; R3 `banding_warnings` has a default (case (a) of the maintainer's "2026-10-17 17:31:25 BST" item 3), so four frontend fixtures gain `banding_warnings: []`, no contract change.
- **Named delta against Acceptance 15** (`git diff --stat origin/main...<slice branch> -- frontend/` must print nothing): it prints three test/fixture files (`EbmShapePanel.test.ts`, `GbmFitPanel.test.ts`, `views/__tests__/fixtures.ts`), authorised by item 3(a) of that entry; no non-test `frontend/` file is edited.
- **`a261c2bf`** (executor-1734g): `test_worker_raise_sites.py` `_SITES` for `model_handlers.py::_fit` gains `safe_error_detail(exc)`; `safe_error.py:180-186` read.

## Audit

*(Written by `auditor-1734`, 2026-10-17, on head `a261c2bf4a79437d9fedf171eb61d2a070f2923e`, range `origin/main...a261c2bf` (merge-base `6bdd2571`; `origin/main` is now `9469721d`, so main has moved and the re-merge at mint is owed). Code read-only; no test run by the auditor; gate logs in `gi-pricing-plan.local/scratch/sl1734-gate/` and `sl1734b-gate/`.)*

**1. Change set** (`git diff --stat origin/main...a261c2bf`, 28 paths, +1298 −71): `loss_treatment.py` (new), `glm.py`, `ebm.py`, `gbm.py`, `bandings.py`, `errors.py`, `modelling/__init__.py`, model-schema `modelling.py` and `__init__.py`, `model_handlers.py`, spec `02-modelling.md`, the two regenerated contracts, tests (`test_glm`, `test_ebm`, `test_gbm`, `test_bandings`, `test_banding_warnings`, `test_model_jobs`, `test_error_sinks`, `test_worker_raise_sites`), three frontend test fixtures, this ledger, INDEX, roadmap and PL-1733's `draft` to `active`. No file of SL-1543's write set (`git diff --name-only` filtered for it: none).

**2. Obligations, derived from PL-1733's Acceptance Standard, FD-1723's Disposition (FR-127 GLM and EBM, FR-100: "FIXED IN P2 under WK-1178, red first") and the rulings, then evidenced** (verdict per row; the lead's to adopt):
- **A4/A5 capped GLM fits capped (fixed, cv, tweedie):** `glm.py:582` applies `apply_loss_treatment`; `test_glm.py:963` asserts coefficients equal the hand-capped fit to atol 1e-10, differ from uncapped, and the cv alpha and tweedie power equal. Red by cause recorded at base (coefficients `[6.0979, -0.5692]` against `[5.5265, -0.2125]`). **Met.**
- **A6 `spliced`/`excess` refused by name on GLM:** `test_glm.py:1004`. **Met.**
- **A7 EBM arm:** `ebm.py:213`; `test_ebm.py:553` (term scores equal hand-capped, differ from uncapped) and `:570` (refusal by name, code asserted). **Met.**
- **A8 one function:** `git grep -nE "def apply_loss_treatment" -- packages` prints one line, `loss_treatment.py:20`; `glm.py:58`, `gbm.py:66`, `ebm.py:36` import it; `test_gbm.py:603, :630` unchanged. **Met.**
- **A9 empty band refuses every fit:** `test_glm.py:1035`, `test_ebm.py:586`, `test_gbm.py:2635` (both backends) assert `BAND_EMPTY`. **Met.**
- **A10 thin band: fail refuses, warn records a typed warning:** `test_glm.py:1059, :1077` (type of `observed`/`minimum` asserted `int` / `Decimal`), and the EBM and GBM equivalents. **Met.**
- **A11 the fit Job fails with `BAND_EMPTY`:** `test_model_jobs.py:603` asserts `FAILED` (not merely terminal); red at base and green at head recorded in the Tasks section (R8). The auditor did not re-run it. **Met** on the ledger's record (delivered, evidence is the lead's DB window, not re-measured).
- **A12 guards:** weight-0 band `test_glm.py:1045`; a band that fits reports nothing `test_bandings.py:422`. The "a `none` GLM fit is identical to main's" guard rests on the existing GLM suite staying green (gate 2: no GLM failure), not on a dedicated before/after comparison. **Met, thinly** (finding F3).
- **A13 SL-1543's guard untouched:** no write-set file in the diff. **Met.**
- **A14 contract:** the plan's python check printed `OK` on this tree; `generate-contracts.py --check` rc 0 in gate 2; `test_banding_warnings.py:69` loads a pre-slice record with no key. **Met.**
- **A15 frontend:** gate 2 frontend install, generate:api, type-check, test, build rc 0 on `5e08d5ce`. The literal `git diff --stat ... -- frontend/` is not empty (finding F2). **Met with a ruled delta.**
- **A16 probe gated the code:** ledger Task 0 Step 3 carries the per-Banding output verbatim, all `OK`; first code commit `e7b96a8d` is after it. **Met.**
- **A3 spec first:** NOT met as written (finding F1).
- **A17 the gate is green on the merge tree:** not met on a single tree: gate 2 ran at `5e08d5ce` (tree `22c1e8d0`), 14 pytest failures (13 working-id cascade, expected until the mint, plus `test_worker_raise_sites`, fixed by `a261c2bf` and verified only by the lead's single-file runs, which the auditor did not repeat). **Deferred with owner:** the lead, at the mint tree and full PR CI.
- **A1/A2 docs checks on the plan:** see section 4.

**3. Red-first record.** Prep commits `496954c8`, `905dc150`, `cab355ad` (tests, unrun) precede the code commits `e7b96a8d` (FR-127) and `9270bb0d` (FR-100); `git merge-base --is-ancestor` for each of `496954c8 cab355ad e7b96a8d 7aa2b6e0 9270bb0d 86d5425e fff53c72 5e08d5ce a261c2bf` against `a261c2bf`: plus `6f41adf5`: all rc 0, run by the auditor. `6f41adf5` (red) precedes `fff53c72` (fix) for DP-1734-A.

**4. Safe-error read (the maintainer's 18:56:17 condition, read independently).** `pricing_core/safe_error.py:180-186`: `safe_error_detail` returns `_validation_detail(exc)` for a `ValidationError` (built from the error count, title and `include_input`-free bounds), `str(exc)` for a `CodedError`, else `""`. `BandingError(ModellingError, CodedError)` (`errors.py`), so its detail is `str(exc)`, the message alone. The 15 `BandingError(` sites in `bandings.py` (lines 87, 102, 183, 195, 201, 213, 238, 266, 327, 334, 349, 375, 567, 583, 605) were each read: messages carry the code, a column name, a banding slug, band labels, the floor value (an actuary-set minimum) and, at `:213-215`, the min and max of the training column (an aggregate range, not a row), and `_describe` carries a band label, an aggregate exposure or claim count and the floor. None interpolates a value from a quote input; the fit path takes a training frame, not a Quote Context. **No banding message can carry a quote input value.** Pre-existing sites (`:87-375`) are unchanged in this diff except where noted.

**5. Findings.**
- **F1 (LOW, acceptance deviation):** Acceptance 3 requires the spec commits before or with the code. Code `e7b96a8d` precedes spec `7aa2b6e0` (FR-127 note), and `9270bb0d` precedes `86d5425e` (FR-100, §4.8, §5.2, FR-207). The slice squash-merges as one PR, so the merged state is consistent. Proposed: lead accepts as a recorded delta; no rework.
- **F2 (LOW, ruled delta, now recorded):** Acceptance 15's empty `frontend/` diff is false: three test/fixture files change (4 lines), authorised by the maintainer's "2026-10-17 17:31:25 BST" item 3(a). Recorded above under "Gate-red fixes".
- **F3 (LOW, test strength):** (a) `test_a_banding_refusal_in_a_fit_keeps_its_text_and_no_row_value` puts its sentinel in an unrelated column of an all-null frame, so it proves the allow-list keeps the refusal text and drops nothing it was never given; it does not exercise a refusal whose message could interpolate a row value. The safety argument rests on the section 4 read, not on that test. (b) The A12 "`none` fit identical to main" guard has no dedicated before/after test. Neither blocks the merge. Proposed: carry as a note; no new FD.
- **F4 (INFO):** `BandingError` now has two bases whose `__init__` differ; `CodedError`'s docstring says the text is `CODE: message`, while `BandingError`'s `str` is the message alone (the code is a separate attribute). Consumers using `safe_error_detail` get the message; none was found that expects the prefix. Not widened here.
- **F5 (fixed in this commit):** the ledger's Gate line, Audit line and Owed list were stale (said "none granted", "not yet", frontend half and full gate "owed"); the gate record and the post-gate fixes (`5e08d5ce`, `a261c2bf`) were absent. Updated above; the ledger has no `tree` front-matter field, and its re-merge note names `origin/main` `6bdd2571`, which is the merge-base, not the current `9469721d`.
- **F6 (owned):** the 13 docs-check cascade pytest failures resolve at the mint (check 31); the lead re-checks on the minted tree.

**6. Proposed verdict:** all PL-1733 obligations delivered and evidenced, with A3 and A15 as recorded deltas (F1, F2) and A17 deferred to the lead's mint-tree gate and full PR CI. No requirement without a verdict. Proposal only: the MERGE-ACK stays "not yet given"; status stays `active`.
