---
id: FD-9792
family: finding
title: The template-certificate test pins a runner-dependent error figure
status: active
created: 2026-10-01
owner: executor
tree: 7190787f494a921f89339ae62f8e3ae666bc4e2b
corrected_by: []
relates: [WK-1178, LG-1350]
---

# FD-9792 — The template-certificate test pins a runner-dependent error figure

**Filed 2026-10-01 under working id 9792**, by executor-hotfix790 in the WK-1178 hotfix SL 9790 (ledger LG working id
9791). The lead mints the final id. The `tree:` is `origin/main^{tree}` at `8933a29e`.

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

Fixed in the same PR as this record (SL 9790), so the register row carries `fix before close` already discharged by
that PR's merge. Residual: the data file still holds one runner's figures; they are now ignored by the comparison and
bounded by the tolerance assertion.
