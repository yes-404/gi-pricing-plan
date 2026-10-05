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

## Addendum 2 — 2026-10-01 05:50 BST: every hit of the widened predicate, one row each

Appended in answer to the lead's Delta 7 ruling (1) and (2): the maintainer's addition asks for each hit and whether a test
pins it exactly. Nothing above is rewritten.

**The predicate (the lead accepted it in Delta 7, superseding the Delta 5 predicate):**
`grep -rnP '\{[^{}]*:[^{}]*[geEf%]\}' packages/*/src backend/src`. Tree: branch head `5b7b24dd` (the producers are
unchanged since `origin/main` `8933a29e`; `git diff 8933a29e 5b7b24dd -- packages/*/src backend/src` is empty). **Count: 155.**

**Method, runnable.** The generator is a short Python script run from the repository root; it is not committed (the table
below is its output). It reads the 155 `file:line` hits, parses each file with `ast`, and for each hit:
1. **kind.** `failure-only` when the interpolation sits inside a `raise` or a call whose name ends `Error`, `Exception`,
   `abort`, `warn` or `log`; `input` when its expression names a range, parameter, budget, step, limit, tolerance or
   threshold; otherwise `measured`. A hit that no `f"..."` holds (a dict or set literal such as `{column: value}`, a comment or a
   docstring: the predicate matches `:`...`f}` inside them) is `not a format spec`. Hand corrections: the objectives.py rows
   are set by hand from reading each check's body (the producers are named in LG-1353 Task 5), `metrics.py:153` is `measured`,
   and any expression containing `error` is `measured`. **The kind is a heuristic and the expression column is shown so a reader
   can overrule it.**
2. **pinned.** The anchor is the 14 to 40 characters of literal text before the interpolation (or after it, or the longest
   literal piece of the string when both are short). `grep -rlF --include=*.py --include=*.json --include=*.md -- <anchor>
   packages/*/tests backend/tests` names the test files that hold it. **Blind spots:** an anchor found in a test may be prose
   and not a pin (checked by hand below for each `yes` outside `objectives.py`); an anchor not found does not rule out a test
   that matches a regex, a fragment of another piece, or the figure through a computation; a wrapped anchor can miss;
   `unknown` means every literal piece was under 14 characters.

**Result.** 87 are not a format spec, 40 measured, 15 input, 13 failure-only (sum 155). Of the 68 that are format specs:
- **Pinned and measured: all in `objectives.py`**, pinned by `_BEFORE` (`template_certificates_before_wk690s2.json`) and fixed
  in this PR: `:1141`, `:1150`, `:1293`, `:1341`, `:1434`, `:1466`, `:1467`, `:1580`, `:1581`, `:1582` (every one is
  normalised; the guard test fails if one is missed). The inputs `:1142`, `:1151`, `:1168-1170`, `:1181-1182`, `:1296`, `:1446`
  are pinned and deterministic, and kept.
- **`yes` outside `objectives.py`, checked by hand:** `data/validate.py:1098` (the anchor `mean severity is` is prose in a
  test docstring, `test_gbm.py:1730`; not a pin); `worker/scoring_handlers.py:261` (a failure message; `test_scoring_handlers.py:353`
  asserts `"0.5" in detail`, the rate of a fixed stub, which is deterministic, and `test_worker_raise_sites.py:189` is prose).
  Neither is a runner-dependent pin.
- **`unknown`:** `diagnostics.py:1213` and `bandings.py:415` are axis labels built from data values (`f"{value:g}"`); the
  label text is data-derived, and I did not find a test pinning one. Not verified further.
- **Measured and not found pinned, outside the write set:** the 30 `measured` rows outside `objectives.py` in the table below (including the three discussed above), in
  `data/validate.py`, `transparency.py`, `metrics.py`, `bandings.py`, `glm.py`, `worker/progress.py` and `api/health.py`.
  **Owned item: WK-1178, the `measured` rows below outside `objectives.py`**, to be re-read when a test first pins one of them;
  `metrics.py:122,135,152,153` is the closest relative of this defect (a certificate detail) and is the first of them.
  No `test_objectives.py` hit was found that the fix does not cover, so the gate was not re-run for that reason.

| file:line | kind | interpolated expression | pinned by a test (anchor found) |
|---|---|---|---|
| ms:validation.py:516 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| ms:refs.py:149 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/splits.py:61 | failure-only | `total` | no |
| pc:data/profile.py:844 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/profile.py:845 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/ingest.py:112 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:70 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:133 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:172 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:290 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:291 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:322 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:323 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:362 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:389 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:390 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:424 | measured | `rate` | no |
| pc:data/validate.py:533 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:570 | measured | `covered` | no |
| pc:data/validate.py:664 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:943 | measured | `share` | no |
| pc:data/validate.py:987 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:990 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:1007 | measured | `absolute` | no |
| pc:data/validate.py:1073 | measured | `frequency` | no |
| pc:data/validate.py:1098 | measured | `severity` | yes: test_gbm.py |
| pc:data/validate.py:1159 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:1243 | measured | `share` | no |
| pc:data/validate.py:1370 | measured | `shift * 100` | no |
| pc:data/validate.py:1398 | measured | `ratio` | no |
| pc:data/validate.py:1487 | measured | `psi` | no |
| pc:data/validate.py:1488 | measured | `psi` | no |
| pc:data/validate.py:1607 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:1664 | measured | `moved` | no |
| pc:data/validate.py:1732 | measured | `moved` | no |
| pc:data/validate.py:1784 | measured | `psi` | no |
| pc:data/validate.py:1785 | measured | `psi` | no |
| pc:data/validate.py:2100 | failure-only | `timeout_s` | no |
| pc:data/validate.py:2122 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:2130 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:data/validate.py:2220 | input | `budget_s` | no |
| pc:rating/properties.py:237 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:rating/score.py:831 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:rating/runtime.py:254 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:rating/runtime.py:322 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:modelling/transparency.py:570 | measured | `approximation.r_squared * 100` | no |
| pc:modelling/transparency.py:571 | measured | `approximation.deviance_explained * 100` | no |
| pc:modelling/transparency.py:578 | measured | `worst.exposure_share * 100` | no |
| pc:modelling/transparency.py:579 | measured | `worst.mean_abs_error_pct` | no |
| pc:modelling/diagnostics.py:221 | failure-only | `tolerance` | no |
| pc:modelling/diagnostics.py:1076 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:modelling/diagnostics.py:1213 | measured | `value` | unknown (anchor too short) |
| pc:modelling/gbm.py:866 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:modelling/comparison.py:313 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:modelling/groupings.py:142 | failure-only | `vhm` | no |
| pc:modelling/metrics.py:122 | measured | `at_truth` | no |
| pc:modelling/metrics.py:135 | measured | `span` | no |
| pc:modelling/metrics.py:152 | measured | `observed` | no |
| pc:modelling/metrics.py:153 | measured | `expected` | no |
| pc:modelling/bandings.py:332 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| pc:modelling/bandings.py:415 | measured | `low` | unknown (anchor too short) |
| pc:modelling/bandings.py:482 | failure-only | `boundary` | no |
| pc:modelling/bandings.py:483 | failure-only | `float(offending[0])` | no |
| pc:modelling/bandings.py:570 | measured | `exposure` | no |
| pc:modelling/bandings.py:571 | input | `min_exposure` | no |
| pc:modelling/bandings.py:576 | input | `min_claims` | no |
| pc:modelling/glm.py:308 | measured | `alpha` | no |
| pc:modelling/glm.py:319 | failure-only | `alpha` | no |
| pc:modelling/objectives.py:821 | failure-only | `elapsed` | no |
| pc:modelling/objectives.py:822 | failure-only | `round_budget_s` | no |
| pc:modelling/objectives.py:1141 | measured | `g_error` | yes: template_certificates_before_wk690s2.json, test_custom_objectives.py, test_objectives.py |
| pc:modelling/objectives.py:1142 | input | `_STEP` | yes: template_certificates_before_wk690s2.json |
| pc:modelling/objectives.py:1150 | measured | `h_error` | yes: template_certificates_before_wk690s2.json, test_custom_objectives.py, test_objectives.py |
| pc:modelling/objectives.py:1151 | input | `_STEP` | yes: template_certificates_before_wk690s2.json |
| pc:modelling/objectives.py:1168 | input | `y_range[0]` | unknown (anchor too short) |
| pc:modelling/objectives.py:1169 | input | `sampling.f_range[0]` | unknown (anchor too short) |
| pc:modelling/objectives.py:1170 | input | `sampling.w_range[0]` | unknown (anchor too short) |
| pc:modelling/objectives.py:1181 | input | `y[bad].min()` | no |
| pc:modelling/objectives.py:1182 | input | `f[bad].min()` | no |
| pc:modelling/objectives.py:1235 | input | `f_lo` | no |
| pc:modelling/objectives.py:1241 | input | `f_lo` | no |
| pc:modelling/objectives.py:1293 | measured | `share` | yes: template_certificates_before_wk690s2.json, test_objectives.py |
| pc:modelling/objectives.py:1296 | input | `fns.hessian_min` | yes: template_certificates_before_wk690s2.json |
| pc:modelling/objectives.py:1341 | measured | `above` | yes: template_certificates_before_wk690s2.json |
| pc:modelling/objectives.py:1388 | input | `sampling.f_range[0]` | no |
| pc:modelling/objectives.py:1434 | measured | `deviation` | yes: template_certificates_before_wk690s2.json |
| pc:modelling/objectives.py:1446 | input | `s` | unknown (anchor too short) |
| pc:modelling/objectives.py:1466 | measured | `orders` | yes: template_certificates_before_wk690s2.json |
| pc:modelling/objectives.py:1467 | measured | `magnitude.min()` | yes: template_certificates_before_wk690s2.json, test_objectives.py |
| pc:modelling/objectives.py:1580 | measured | `recovered` | yes: template_certificates_before_wk690s2.json |
| pc:modelling/objectives.py:1581 | measured | `error` | yes: template_certificates_before_wk690s2.json |
| pc:modelling/objectives.py:1582 | measured | `elapsed` | yes: template_certificates_before_wk690s2.json |
| be:worker/tasks.py:108 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:worker/tasks.py:115 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:worker/tasks.py:135 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:worker/tasks.py:220 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:worker/model_handlers.py:509 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:worker/model_handlers.py:1122 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:worker/scoring_handlers.py:261 | failure-only | `stats.failure_rate` | yes: test_scoring_handlers.py, test_worker_raise_sites.py |
| be:worker/scoring_handlers.py:262 | failure-only | `effective_threshold` | no |
| be:worker/progress.py:65 | measured | `elapsed_s` | no |
| be:data/ingestion.py:171 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:data/ingestion.py:426 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:data/ingestion.py:472 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:db/models.py:134 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:db/models.py:286 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:db/models.py:825 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:db/models.py:906 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:db/models.py:984 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:db/models.py:2274 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:api/models.py:1022 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:api/score.py:443 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:api/health.py:89 | measured | `_PROBE_TIMEOUT_S` | no |
| be:api/health.py:91 | measured | `_PROBE_TIMEOUT_S` | no |
| be:api/rate_tables.py:310 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:api/settings.py:99 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/validation.py:54 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/validation.py:139 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/validation.py:328 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/validation.py:329 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/prediction.py:403 | failure-only | `worst_gap` | no |
| be:platform/perils.py:266 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/perils.py:349 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/rating_versions.py:372 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/rating_versions.py:373 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/datasets.py:144 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/datasets.py:300 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/datasets.py:515 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/datasets.py:592 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/datasets.py:713 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/datasets.py:714 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/metrics.py:470 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/metrics.py:537 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/metrics.py:613 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/metrics.py:648 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/metrics.py:794 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/modelling.py:1173 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/modelling.py:1365 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/modelling.py:1427 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/modelling.py:1463 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/modelling.py:1464 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/jobs.py:151 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/jobs.py:225 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/jobs.py:258 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/jobs.py:295 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/jobs.py:296 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/blobs.py:261 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/backtests.py:203 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/objectives.py:543 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/objectives.py:611 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/objectives.py:685 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/objectives.py:840 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/model_specs.py:132 | failure-only | `per_parameter` | no |
| be:platform/approvals.py:521 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
| be:platform/approvals.py:522 | not a format spec (dict or set literal, comment or docstring) |  | n/a |
