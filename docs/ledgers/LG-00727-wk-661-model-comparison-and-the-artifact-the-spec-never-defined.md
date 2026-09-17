---
id: LG-727
family: ledger
title: WK-661 — model comparison, and the artifact the spec never defined
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-17
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — model comparison, and the artifact the spec never defined, 2026-08-17 *(in progress, not closed)*

The seventh slice. `WF-698` E1/E2 — the actuary compares candidates on a shared holdout and
selects one — and the first slice whose **artifact had to be designed rather than
implemented**: `02` §5.2 named `ModelComparison` as a return type from Phase 0 and no section
defined it. No §4 subsection, no type, no contract. §4.11 is that design, and
`model-comparison.schema.json` is the first generated contract here with no hand-authored
Phase-0 counterpart — the others exist to compare a written promise against the emitted
shape, and this shape had no written promise to check.

| Delivered | Evidence |
|---|---|
| `ModelComparison` (§4.11) | Every invariant is a choice with its reason recorded: two or more models, a baseline inside the set, a value for every model with null where a metric does not apply, and `leader = null` on a tie as well as on an unordered metric |
| `MetricDirection` has three arms, not a boolean | `closer_to_one_is_better` exists because A/E has no better direction — 1.4 and 0.6 are equally wrong, and every higher-is-better table would rank 1.4 first |
| `compare_models` in `pricing-core` | Aligned metrics, double lift, factor-by-factor relativity differences. The Gini and binning helpers are **imported** from `diagnostics`: a second exposure-weighted Gini would let the comparison disagree with the diagnostics each model already carries |
| Double lift, binned by the **ratio** | Sorting by either prediction gives two lift curves side by side; the ratio answers "where they disagree, which one does the data support?" — what a selection turns on. The tests pin it: the ratio increases across bins and the bins partition the holdout exactly |
| `POST /models/compare` → 202 + Job | The comparison reads the holdout and scores every candidate, which is work. `POST /models` draws the same line |
| `GET /models/comparisons/{id}` | **Added to `02` §5.1** — the table declared the `POST` and no read, and a 202 whose artifact nothing can fetch is complete to the endpoint audit and unusable to a caller |
| Four refusals, before a Job exists | `MODELS_NOT_COMPARABLE`, each naming the specific thing that differs — both split ids in the message, because "these are not comparable" without saying which two things is a refusal nobody can act on. Checked **again** in `pricing-core`: `reserve_model`'s reason, plus `compare_models` being reachable from a notebook where the platform is not |
| The artifact is insert-only | `model_comparisons` grants `SELECT, INSERT` and revokes the rest (FR-43). `06` §3.3 makes a comparison required evidence for a Model approval where a predecessor exists |
| `MODEL` endpoints **18 of 29**, was 16 of 28 | `scope-audit.py MODEL --endpoints` |

**Three defects fixed that predate the slice**, all found by building it:

* **§5.2's `compare_models` signature could not be written** — the *third* instance of one
  defect. It took `Sequence[Model]`, and a `Model` carries references whose resolution needs a
  database ADR-703 forbids `pricing-core`. `predict_glm` and `compute_diagnostics` were
  corrected the same way on 2026-08-16. That three signatures were written this way says the
  §5.2 table was drafted before the ADR's consequence was concrete; the remaining unbuilt
  signatures should be read with that in mind rather than trusted.
* **`PartitionDiagnostics.double_lift` was populated by nothing, and nothing could populate
  it.** FR-171 listed double lift among *universal* diagnostics, but it is pairwise, the
  comparison model is unknown at fit time, and FR-170 makes diagnostics computed once and
  read thereafter — so the field could not be filled later either. Removed, FR-171
  amended, and the removal is assertable because `extra="forbid"` refuses it as an input. A
  field that is structurally always null is worse than an absent one: a reader takes it for a
  measurement that came out empty.
* **The Job runner never told a handler which Job it was.** Three handlers read
  `parameters.get("job_id")` to stamp the artifact they produce, and no caller ever put it in
  the payload — `job_identity` carries the actor and the workspace, `fit_payload` carries the
  model — so `diagnostics.job_id` and `models.job_id` were **silently always NULL** and the
  trail from an artifact back to the run that made it did not exist. Fixed in `tasks.py`, so
  the next handler cannot be written without it, and tested there rather than per handler. The
  runner overrides a payload-supplied id: an artifact stamped with somebody else's Job is
  worse than one stamped with nothing.

**A test premise that was wrong, kept because the correction is the interesting part.** Two
fits of one factor differing only in regularisation **tie on Gini** — it is computed from the
ordering of predicted rates, and shrinkage moves both levels toward the grand mean without
ever swapping them. `holdout_deviance` separates them, being sensitive to magnitude. The test
now asserts both, which is only possible because a tie yields no leader rather than whatever
dictionary order gave.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| A GBM among the candidates (`WF-698` E1 compares a GLM *and* an XGBoost) | **Deferred — §3.5 is 0/12 and no GBM exists to compare.** `ComparisonCandidate` is shaped so a non-`glm` model is a new arm rather than a new subsystem. Owner: the GBM slice |
| FR-187's backtest | ~~**Not started**~~ **Delivered 2026-08-18**, its own requirement, artifact and two endpoints |
| `02` §5.3's comparison view (`/models/compare?ids=`) | **WK-664**, a Vue view |
| OQ-639's evidence floor | **Still open, and now cheaper.** This slice created the second evidence kind the floor needs; the recommendation stands and the decision is the maintainer's |
| An intercept-only "null model" baseline | **Not available, and noticed here.** `fit_glm` refuses a spec with no factors — "the design matrix has no columns" — so the standard actuarial baseline of comparing against a constant-rate model cannot be built. No requirement asks for it; recorded because a comparison feature is where someone will look for it |
