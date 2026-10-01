---
id: FD-1354
family: finding
title: The template-certificate test pins a runner-dependent error figure
status: active
created: 2026-10-01
owner: executor
tree: 7190787f494a921f89339ae62f8e3ae666bc4e2b
corrected_by: []
relates: [WK-1178, LG-1350]
---

# FD-1354 — The template-certificate test pins a runner-dependent error figure

**Minted 2026-10-01 as FD-1354** (the lead allocated it, dispatch record Delta 2); it was filed under working id 9792. Filed under working id 9792 by executor-hotfix790 in the WK-1178 hotfix SL-1352 (working id 9790; ledger LG-1353, working id 9791). The `tree:` is `origin/main^{tree}` at `8933a29e`.

## Finding

**Severity: LOW; owner WK-1178.** `packages/pricing-core/tests/test_objectives.py::test_template_certificate_unchanged`
compared the whole detail string of each check with a reference pinned in
`packages/pricing-core/tests/data/template_certificates_before_wk690s2.json`. The detail carries
`max relative error <x>`, the finite-difference error of the analytic gradient and Hessian. That figure is a
measurement and it depends on the runner. Main's push CI (run 36801276738, `8933a29e`) failed six of the twelve
parametrised cases, `tweedie`, `asymmetric_squared`, `asymmetric_poisson`, `huber`, `pseudo_huber` and `quantile`:
`analytic_vs_numeric_hessian` read `max relative error 2.28e-12` on that runner and `3.21e-12` in the reference.
#1025's PR CI was green at its own head, so the figure differs between runners of the same workflow. The step is
`GATE: FAIL — 1 of 8 stages failed: pytest`, 6 failed and 4411 passed. #1034 (run 36804433191) failed the same six.

## Evidence

**1. Red.** At `8933a29e` after `uv sync --all-packages`, with `3.21e-12` in the reference changed to `2.28e-12` (the
runner's figure; a `sed` on the data file, reverted after):
`uv run pytest -q packages/pricing-core/tests/test_objectives.py -k test_template_certificate_unchanged` →
`1 failed, 11 passed`; the failing case is `tweedie` and the diff is at the `analytic_vs_numeric_hessian` detail.
**2. Fix (test-only).** The comparison normalises each `max relative error <x>` figure on both sides, like the elapsed
seconds, and asserts each parsed figure is at most the engine's own tolerance for the status the check carries:
`_TOLERANCE_PASS` for `pass`, `_TOLERANCE_WARN` otherwise (both in
`packages/pricing-core/src/pricing_core/modelling/objectives.py`; the engine exposes private symbols only, imported by
the test). With the same planted `2.28e-12` the run is `12 passed`.
**3. Planted mutation.** In `objectives.py` the hessian detail printed `{h_error + 1e-5:.3g}` (status unchanged,
`pass`); the `tweedie` case failed with `AssertionError: ('analytic_vs_numeric_hessian', '1e-05', 1e-06)`. Reverted;
`git status --porcelain` showed only the test file.

## Sweep for other pinned measured floats

**Predicate:** a literal `max relative error <digit>` in a test file or test data file (the form this test pinned),
and separately an `==` or `!=` against a float literal with four or more decimals, not under `pytest.approx`.
**Corpus:** `packages/*/tests` and `backend/tests`, `*.py` and `*.json`, tree `8933a29e`.
**Commands:**
`grep -rnoE 'max relative error [0-9]' packages/*/tests backend/tests --include=*.py --include=*.json | wc -l` → 26;
`grep -rnE '(==|!=) *-?[0-9]+\.[0-9]{4,}' packages/*/tests backend/tests --include=*.py | grep -vc approx` → 0.
Also `grep -rlE 'elapsed|[0-9]+\.[0-9]+s"' packages/*/tests/data backend/tests` for timing literals.
**Hits (26 of the first command):**
- 24 in `template_certificates_before_wk690s2.json`: fixed here (normalised before comparison; the file is unchanged).
- `packages/model-schema/tests/test_objectives.py:247`, `max relative error 8.9e-7`: a hand-built `CertificateCheck`
  input, not a measurement. No action.
- `backend/tests/test_custom_objectives.py:378`, `max relative error 4.1e-01 at y=3, f=2.0`: a hand-built fixture
  string, not a measurement. No action.
- Timing literals: `backend/tests/test_api_datasets.py:473` bounds a measured time (`< 2_500` ms), not a pin;
  `elapsed_us=41` and `3` in `test_traces.py` and `test_traces_api.py` are constructed inputs. No action.
- The zero-decimal-figure hits (`max relative error 0`) are 5 of the 24 JSON hits, covered by the same normalisation.
No other pinned measured float was found. The sweep reads literals; a measurement compared through a computed
expression would not match, which this sweep does not claim to cover.

## Disposition

Fixed in the same PR as this record (SL-1352), so the register row carries `fix before close` already discharged by
that PR's merge. Residual: the data file still holds one runner's figures; they are now ignored by the comparison and
bounded by the tolerance assertion.

## Addendum 2026-10-01 05:40 BST: the producer sweep, and the first predicate's miss

Appended after CI run 36812617020 at `5a4beb63` failed on a second runner-dependent figure. The text above is not
rewritten. **The first sweep's miss:** its predicate, `max relative error <digit>`, matched the phrase of the bug already
found, not the class. It read the consumer (the pinned text) for one known phrase, so it could not see
`max |f* - log y| = 1.8e-16` (the figure at `objectives.py:1434`), which fails the same way: the test went red on the runner
(`2.08e-16` against `1.8e-16`), and the earlier green at `d651e33b` (run 36810512763) was luck.

**Producer predicate.** The lead's, verbatim: `grep -nP '\{[^{}]*:\.[0-9]+[geE]\}' packages/pricing-core/src/pricing_core/modelling/objectives.py`.
Tree: `origin/main` `8933a29e` (tree `7190787f494a921f89339ae62f8e3ae666bc4e2b`). **Count: 12 lines**; the same command at the
branch tree gives 12. Over all `packages/*/src` and `backend/src`:
`grep -rnP '\{[^{}]*:\.[0-9]+[geE]\}' packages/*/src backend/src` gives **18 lines** (12 in `objectives.py`; 4 lines in
`metrics.py` (`:122`, `:135`, `:152`, `:153`); 1 each in `groupings.py` and `backend/src/app/platform/prediction.py`).
**It misses `%` and `.1f` specs.** The widened predicate `grep -rnP '\{[^{}]*:[^{}]*[geEf%]\}' packages/*/src backend/src` gives
**155 lines**, of which 24 are in `objectives.py`; that is the figure to read next to the 18.

**Per-hit verdicts for the 18 (kind; whether a test pins the rendered text; grep).** Pin grep:
`grep -rnE "value at f=log|constant population of 1,000|value changes by a factor|which is not positive|worst gap|one unit away|orders over|of the sampled y lie|hessian < 0 at|recovered a relativity|\|f\* - log y\|" packages/*/tests backend/tests --include=*.py`
(its only hits are in `test_objectives.py`, where the pinned text is the `_BEFORE` reference).
- `objectives.py:1141`, `:1150` (max relative error): measured; pinned in `_BEFORE`; **fixed** (normalised, bounded by `_TOLERANCE_PASS`/`_TOLERANCE_WARN`).
- `objectives.py:1434` (deviation), `:1467` (gradient min and max), `:1580` (recovered relativity): measured; pinned in `_BEFORE`; **fixed** (normalised, status only, reasons in LG-1353 Task 5).
- `objectives.py:1168-1170`, `:1181-1182`: inputs, deterministic (the sampling spec and the bad-point range); pinned and kept; the guard exempts them by shape.
- `objectives.py:821-822`: failure-only (an elapsed time in the per-round budget error); no test pins its text.
- `metrics.py:122`, `:135`, `:152`, `:153` (a metric certificate's `direction_holds`, `scale_behaviour`, `smoke_evaluation`): measured; **no test pins the text** (`test_metrics.py:110` compares two in-process runs, both from one runner). Not fixed: not in this write set and not pinned. **Owned item: WK-1178, `packages/pricing-core/src/pricing_core/modelling/metrics.py:122,135,152-153`**, to guard before any test pins a metric certificate's text.
- `groupings.py:142` (Buhlmann-Straub variance in a refusal): measured, failure-only; `test_groupings.py:507` matches the fragment `"not positive"`, not the figure. No action.
- `backend/src/app/platform/prediction.py:403` (worst crossing gap in a 409): measured, failure-only; `backend/tests/test_paired_quantile_models.py:782` matches `"1.5"`, but the gap there is a monkeypatched constant (`lambda lower, upper: (2, 1.5)`), not a measurement. No action.
**Four more measured figures the widened predicate found in the same certificate producers (not in the lead's 12):** `objectives.py:1293` (negative-hessian share), `:1341` (share of y above a branch), `:1466` (orders spanned), `:1581` (smoke-fit percentage error). All four are pinned in `_BEFORE`; **all fixed here** (normalised, status only).
**Not reviewed.** The remaining widened hits outside the certificate producers (for example `data/validate.py` 35, `bandings.py` 7, `transparency.py` 4, and the backend platform modules) are validation-report and message text over a dataset, not figures printed from floating-point noise in a pinned certificate; this addendum did not classify each. **Owned item: WK-1178, the widened-predicate hits outside `objectives.py` and `metrics.py` (155 minus 28), to be classified when a test first pins one.**

**The guard.** `test_no_measured_figure_survives_normalisation_in_a_template_certificate` in `test_objectives.py` now fails
deterministically if any float survives normalisation in any template's rendered detail, so a further pinned measured figure
in a template certificate fails every run, not one run in N. It covers the template certificate only; the metric certificate
is the owned item above.

