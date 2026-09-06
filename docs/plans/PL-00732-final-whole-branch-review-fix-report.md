---
id: PL-732
family: plan
kind: review
title: Final whole-branch review — fix report
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-19
owner: auditor
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-19-custom-metrics-final-review.md
---

# Final whole-branch review — fix report

**Branch** `worktree-custom-metrics` · **from** `f3689dd` · **2026-08-20**

Two commits, as briefed.

| Commit | Scope |
|---|---|
| `c59a283` | `fix(model): FR-155/159/160 — resolve template defaults, bind stopping by name` (C1 + C2) |
| `9d33539` | `docs(model): a docstring claiming a control the code lacks, and a self-contradicting roadmap` (I4 + I6) |

---

## C1 — `evaluate_metric` never resolved template defaults; the param validator was half-copied

**Fix A.** Extracted `resolve_template_params(template, params)` in
`packages/pricing-core/src/pricing_core/modelling/objectives.py`, lifted verbatim from
`compile_objective`'s loop rather than reinvented. `compile_objective` now calls it, and so
do all three sites in `packages/pricing-core/src/pricing_core/modelling/metrics.py` —
`evaluate_metric`, `certify_metric`'s `finiteness` grid, and its `smoke_evaluation`
hand-computable. The last two were unresolved as well; the brief named only the first.

The stored artifact is unchanged: `CustomMetric.params` still holds only the author's
choice, and the catalogue test asserts that after evaluation.

No new error code was introduced. The helper keeps `compile_objective`'s existing
`float(value)  # type: ignore[arg-type]` with the comment that both artifacts refuse a
missing required parameter at construction — which, after Fix B, is now true of both.

**Fix B.** Restored the missing-required half of
`CustomMetric._the_parameters_are_the_templates_own`
(`packages/model-schema/src/model_schema/metrics.py`), mirroring `CustomObjective`'s
structure and message. The API's 422 follows for free: `metrics._validated` already maps any
`ValueError` from the artifact to `VALIDATION_FAILED`.

**Tests.**
- `packages/pricing-core/tests/test_metrics.py` — three catalogue-iterating tests over
  `list(ObjectiveTemplate)`: every template *evaluates* with only its required parameters
  (asserting the value equals the resolved-parameter loss, and that `params` is unchanged),
  every template *certifies*, and every template with a no-default parameter is *refused at
  construction*. Valid parameter values are derived from `TemplateParameter` rather than
  tabulated, so a template added to §4.5 is covered on the day it lands.
- `backend/tests/test_custom_metrics_api.py` — `POST /api/v1/custom-metrics` with
  `capped_gamma` and `params: {}` now answers 422 `VALIDATION_FAILED` naming `'cap'`.
- All marked `@pytest.mark.req("FR-155")`.

---

## C2 — early stopping bound to the wrong metric, and to a guessed direction

`packages/pricing-core/src/pricing_core/modelling/gbm.py`.

**XGBoost.** The `else: early_stopping_rounds = stopping.rounds` shorthand is gone. Both
branches now build one `xgb.callback.EarlyStopping(metric_name=…, data_name="holdout",
maximize=…)`. `early_stopping_rounds` is no longer passed to `xgb.train` at all.

**LightGBM — explicit binding, not a pinned limitation.** Verified empirically that
LightGBM preserves `params["metric"]` order in `evaluation_result_list` (probe:
`["poisson","rmse"]` → `[(train,poisson),(train,rmse),(holdout,poisson),(holdout,rmse)]`,
and reversed for the reversed list). So the builtin branch now moves the spec's stopping
metric to the front of `params["metric"]`, and `first_metric_only` is `True` whenever
stopping is configured instead of `bool(feval_entries)`. The custom branch already ordered
`feval` that way and is unchanged.

One genuine library limitation is pinned rather than left silent: LightGBM always evaluates
builtin metrics *before* `feval`'s, so a spec that stops on a Custom Metric **and** declares
a builtin for the curve cannot have both — reporting the builtin would put it at position 0
and drive the stop. `_fit_lightgbm` suppresses the builtin (`metric: "None"`) rather than
stop on the wrong metric; XGBoost, which targets by name, reports both.
`test_lightgbm_drops_a_builtin_eval_metric_rather_than_stop_on_it` states the divergence and
the reason.

**Direction, on every path.** Custom stopping target → the artifact's `MetricDirection`
(unchanged). Builtin stopping target → `maximize=None`, delegating to XGBoost's own
higher-is-better table. That is delegation rather than a guess: `_METRICS`'s docstring makes
an unrecognised metric name backend-specific by design, so a direction table maintained in
`gbm.py` would go stale against names it has never heard of. LightGBM supplies
`is_higher_better` for its own builtins through the eval tuple.

**The narrowed refusal is untouched.** `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` still refuses
a builtin metric under a callable objective; both its tests stay green.

**Tests** in `packages/pricing-core/tests/test_gbm.py`, all asserting *which* metric drove
the stop by comparing `best_iteration` against the fit whose spec declares that metric alone:

- `test_a_second_declared_builtin_does_not_also_drive_early_stopping` — FR-159, both
  backends × both declaration orders. Stops on `mae`, declares `poisson-nloglik` alongside.
  The pair was chosen by measurement, not by taste: their holdout curves bottom out at 95 vs
  22 rounds on XGBoost and 66 vs 25 on LightGBM, and `mae` is the *later* of the two. `rmse`
  was tried first and discarded — it stalls at round 25 on LightGBM, exactly where
  `poisson-nloglik` does, so the test would have passed against the broken binding.
- `test_a_declared_custom_metric_does_not_capture_stopping_from_a_named_builtin` —
  FR-160, both backends. A `quantile` metric at `alpha=0.9` declaring
  `higher_is_better`, deliberately unlike the stopping builtin; a near-copy of
  `poisson-nloglik` would agree by coincidence and prove nothing.
- `test_lightgbm_drops_a_builtin_eval_metric_rather_than_stop_on_it` — FR-160, the
  pinned limitation.

### Enforcement proven against deliberately broken input (§13 rule 4)

Every fix was reverted in place and the corresponding test watched to fail:

| Break | Result |
|---|---|
| `evaluate_metric` back to `dict(metric.params)` | 6 of 12 catalogue cases fail — `KeyError: 'p'`, `'w_under'`, `'alpha'`, `'gamma'`, … |
| Validator's missing-required half removed | 5 negative cases: `DID NOT RAISE ValidationError` |
| LightGBM `first_metric_only=bool(feval_entries)` | `[last-lightgbm]` fails, `assert 25 == 66` |
| LightGBM stopping-metric reorder removed | `[last-lightgbm]` fails, `assert 25 == 66` |
| XGBoost back to the `early_stopping_rounds=` shorthand | `[first-xgboost]` fails `assert 27 == 95`; the custom-capture test fails `assert 6 == 22` |

`[last-xgboost]` passes against the pre-fix code, which is correct and expected: the
shorthand takes the last metric declared, so it happens to be right in exactly that one
ordering. That is why the test is parametrized over both.

### Spec

`docs/specs/02-modelling.md` §3 — dated amendments appended to FR-159's and
FR-160's requirement rows, recording the binding rule, the two backends' opposite
positional shorthands, and the LightGBM reporting limitation. The spec already required the
correct behaviour; what it gained is the finding.

---

## I4 — a docstring claiming a control the code does not have

`backend/src/app/platform/metrics.py`, `_require_evidence`. The claim that editing
`metric_certificate` out of a workspace policy "will 422 here with `EVIDENCE_INCOMPLETE`"
was false and has been replaced with what is true:

- `custom_metric` is absent from `EVIDENCE_FLOOR` because `06` §3.3 has no row for it, so
  `below_floor()` returns nothing and the edit is accepted. `custom_objective` **is** in the
  floor and is protected.
- What protects a metric today is the lifecycle: submit requires status `certified`, only
  `record_certificate` sets that status, it sets it alongside a `certificate_id`, and the
  `certified_metric_has_a_certificate` CHECK (verified in `backend/src/app/db/models.py`)
  refuses the pair coming apart below the ORM.
- The `06` §3.3 row is named as owed, with the reason it was not added here.

`EVIDENCE_FLOOR` was **not** touched, per the brief.

---

## I6 — the roadmap contradicted itself

`docs/roadmap.md`, `#### WK-661 — outstanding work, derived 2026-08-19`. Not deleted; superseded
with a dated note in this repository's established style.

Counts re-derived by running the commands, as printed:

- `uv run python scripts/scope-audit.py MODEL --endpoints` → `declared: 40 · published: 40
  (100%) · every declared endpoint is published in the contract`
- `uv run python scripts/scope-audit.py MODEL` → `in scope: 120 · with evidence: 101 (84%) ·
  NO EVIDENCE for 19`
- `uv run python scripts/req-coverage.py` → `requirements specified : 489 · requirements
  marked : 235 (48.1%)`

The counts table now carries both columns — 2026-08-19 beside 2026-08-20 — rather than
overwriting what was believed on the day the plan was made. The requirement total rose by
six (FR-155…108, all evidenced); the unevidenced 19 and their verdicts are unchanged.

"Five buildable slices remain" is struck through and corrected to **four**. Slice 1, custom
metrics, is struck through and marked **DELIVERED 2026-08-20**, with a note that the
deferral's own reasoning turned out to be the argument for building it inside WK-661 —
FR-160 made a Custom Metric the only way to early-stop under a callable objective.

The evidence-floor gap was added to the slice record's **Not delivered** list with **WK-661** as
owner and the ordering constraint stated (`06` §3.3 row first, then `EVIDENCE_FLOOR`), since
it was deferred during the slice and then fell out of the record entirely. The slice
record's own "four other buildable slices" wording was corrected in the same pass.

---

## Gate — run locally, in the foreground, each command's own exit code

| Command | Result |
|---|---|
| `uv run ruff check .` | `All checks passed!` — **0** |
| `uv run mypy` | `Success: no issues found in 129 source files` — **0** |
| `uv run lint-imports` | `Contracts: 3 kept, 0 broken` — **0** |
| `uv run pytest -q` | **1449 passed, 0 skipped, 0 failed** in 276 s — **0** |
| `python3 scripts/audit-docs.py` | `All checks passed` — 489 requirements, 72 open questions all mirrored, 131 error codes ownership-exclusive, 54 JSON schemas — **0** |
| `uv run python scripts/req-coverage.py` | `235 of 489 marked (48.1%)` — **0** |
| `uv run python scripts/generate-contracts.py --check` | `23 generated contracts match the models` — **0** |
| `uv run python scripts/scope-audit.py MODEL --endpoints` | `40 declared, 40 published (100%)` — **0** |

1412 → **1449** tests (+37: 24 catalogue cases, 5 negative-construction cases, 6 early-stopping
cases, 1 LightGBM limitation, 1 backend 422).

Frontend skipped: no generated contract changed (`--check` clean), and nothing under
`frontend/` was touched.

Working tree clean; both commits on `worktree-custom-metrics`.

## Still open

- `06` §3.3's `custom_metric` evidence row and the matching `EVIDENCE_FLOOR` entry — owner
  WK-661, recorded in the slice record. Deliberately out of this fix wave.
- The 19 unevidenced MODEL requirements and the 11-of-12 NFR gap are unchanged by this wave;
  their verdicts stand as written on 2026-08-19.
