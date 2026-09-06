---
id: LG-724
family: ledger
title: WK-661 — diagnostics, and the holdout that was not one
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-16
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — diagnostics, and the holdout that was not one, 2026-08-16 *(in progress, not closed)*

The fourth slice. `02` §3.8 was 0 of 10 and `02` §4.8's invariant — `status ≥ fitted ⟹
diagnostics_id` — was unmeetable, which OQ-582 had cited as its own worked example.

**Two defects found before a line of the slice was written, both in closed work:**

| Found | What it was |
|---|---|
| **`record_split` had no route** | FR-76's service function, its table and its negative tests have existed since WK-660; no HTTP route reached it and `01` §5.1 declared none. The endpoint audit compares the spec's table against the published contract, so an endpoint missing from *both* is invisible to it — the same blind spot that hid `01`'s reference publish lifecycle, and WK-660 closed through it. Now `POST`/`GET /dataset-versions/{id}/splits`, with the §5.1 rows |
| **Derived versions inherited their parent's data** | `dataset.derive` recorded the operation and set `child.tables = parent.tables`, conflating FR-74's "inherits schema, Data Dictionary and Rule Set" with inheriting the *rows*. A 1 % sample held 100 % of the rows; a train/test split produced two versions each containing everything. A model "fitted on train" was fitted on all of it, and its holdout contained every training row — diagnostics that look excellent and mean nothing. **`split` is materialised now** (FR-77); `sample`, `filter`, `join` and `aggregate` are **not**, and were OQ-563 — **decided 2026-08-17**: each is materialised in the slice that first needs it, and refused with `DERIVATION_NOT_MATERIALISED` until then (FR-78), so no version can claim an operation nobody performed |

| Delivered | Evidence |
|---|---|
| `compute_diagnostics` — universal (FR-171) and GLM (FR-172), train and holdout side by side | Built on a book with known relativities, so the tests assert what the numbers *are*. Train A/E is exactly 1.0 for a Poisson log-link fit with an intercept — the identity `Σy = Σμ`, which only holds if design columns, base level and offset are all reconstructed correctly |
| **The type-III test separates signal from noise** | A real factor returns p < 1e-10 and a column drawn independently of the response returns p > 0.01, on the same fit. Without both halves the p-value is decoration. Degrees of freedom are asserted too: levels − 1, and a wrong df gives a wrong p-value from a right statistic |
| `predict_glm` / `linear_predictor` (FR-193, point predictions) | Scoring from the artifact alone, no `glum` — ADR-705. Written because diagnostics need predictions on two frames; exposing it rather than hiding it avoids writing the same arithmetic twice when `03` calls it |
| **Deviance, computed at last** | `GlmFitResult.deviance` was declared by the spine and always `None`. Now computed per family from the unit deviance, with AIC and BIC from an exact log-likelihood |
| **A Tweedie fit reports no AIC rather than a wrong one** | Tweedie's density has no closed form. `aic`/`bic` are `None` with the reason stated, not a deviance-based stand-in that would differ from every other tool's AIC by an additive constant and read as a disagreement between two correct numbers |
| `split_ref` and `diagnostics_id` live; `spec_hash` → `v2` | OQ-582's "re-widen as the slices land", and the version tag the previous slice built doing its job: every `v1:` digest is findable with `LIKE 'v1:%'` |
| The invariant, at three layers | The type refuses a `Model` beyond `draft` with no `diagnostics_id`; a database CHECK refuses it against a direct `INSERT`; the fit path writes model and diagnostics in **one transaction**. A fit with no split is refused with `MODEL_SPLIT_REQUIRED` before compute is spent |
| `GET /models/{slug}/diagnostics`, `POST`/`GET /dataset-versions/{id}/splits` | Published in the contract, not merely routed — asserted against `docs/contracts/openapi/generated.json`, the file the endpoint audit reads |
| `diagnostics` is insert-only | `GRANT SELECT, INSERT` and `REVOKE UPDATE, DELETE` for `gip_app`, asserted from `information_schema`. FR-170 makes diagnostics computed once and read thereafter; a row that could be updated would let the evidence behind an approval change after the approval |

**A defect the fixture found.** The deterministic test book fits exactly, so its deviance
is 0 — and floating-point accumulation returned **−4.7e-17**. Deviance cannot be negative.
It is clamped within a scaled tolerance and **raises** beyond it, because silently zeroing a
genuinely negative total would turn a wrong unit-deviance formula into a plausible number.

**The money-discipline scan was narrowed, and the narrowing was proved.** FR-185's
`exposure_per_parameter` is a ratio, not an exposure, and the name-based scan flagged it.
Excluded by `_per_parameter` — a rule rather than two more names on the allow-list OQ-544
objects to — and deliberately *not* a general `_per_\w+`, since `premium_per_policy` is
money. Injecting a float `exposure_years` into a generated schema still fails the check.

**Not delivered.** `scope-audit MODEL --endpoints` reads **13 of 27** and 31 of 95
requirements; §3.8 is 6 of 10. The verdicts:

| Requirement | Verdict |
|---|---|
| FR-174 — GBM diagnostics | ~~**Not started.**~~ **Delivered 2026-08-17** — the gradient-boosting slice, which is what "owned by the GBM slice" resolved to; §3.5 closed at 13 of 13 and §3.8 at 11 of 11, with six markers across `test_gbm.py` and `test_transparency.py`. Struck 2026-08-22 by the audit-remediation slice, which found it in the same table as the five rows below and **not** in the closure audit that listed them. *Believed on the day:* Nothing fits a GBM yet; the roadmap's own risk row makes FR-171 the gate and 51/52 incremental. Owned by the GBM slice |
| FR-182 — cross-validation | ~~**Not started.**~~ **Delivered 2026-08-21** — the regularisation-and-CV slice. Interacts with FR-112's unimplemented regularisation path, which is where `select_by: cv` lives. Owned with it |
| FR-186 — model comparison | ~~**Not started.**~~ **Delivered 2026-08-17** — the model-comparison slice, with `02` §4.11's artifact (which the spec did not define until that slice) and its two endpoints; 26 markers across the three packages. *Believed on the day:* Its own endpoint and artifact; `WF-698` E1 needs it |
| FR-187 — backtest | ~~**Not started.**~~ **Delivered 2026-08-18** — its own artifact (`02` §4.12), two endpoints and a migration. The record is this file's backtest slice |
| FR-MODEL-63, 77, 78 — prediction intervals | ~~**Not started.**~~ **All three delivered** — 63 on 2026-08-18 by the prediction slice, when the covariance blob finally reached the signature; 77 and 78 on 2026-08-19 by the paired-quantile slice, which is where the `quantile` template and the GBM this row waited on both arrived. *Believed on the day:* 63 needs the covariance blob the fit stores but this signature does not receive; 77/78 need a GBM and the `quantile` template |
| FR-202 — the rest of the lifecycle | ~~**Partial.**~~ **Complete 2026-08-17** — the model-lifecycle slice, which is what "the submission slice" resolved to. All six states are enforced by a CHECK constraint at a layer a direct `UPDATE` cannot walk past, and `review`, `approved`, `superseded` and `archived` all have transitions; 21 markers. *Believed on the day:* `draft → fitted` is enforced at three layers; `review`, `approved`, `superseded` and `archived` have no transitions. Owned by the submission slice |
| FR-205 — `dataset_invalidated` | ~~**Not started.** Unowned~~ **Delivered 2026-08-17** — the model-lifecycle slice; the flag is computed at read rather than stored, and an invalidated dataset blocks `approved` (`test_a_model_whose_dataset_lost_its_standing_cannot_be_approved`). *"Unowned" was true when written and was answered nine slices later, which is the case for writing a verdict down rather than leaving silence.* |
| FR-185 — complexity | **Corrected 2026-08-16.** This record read as delivered and was **half** delivered: the diagnostic was recorded, the *gate* was not, and the requirement counted as evidenced because a test marked it. The gate landed in the next slice. Left here rather than edited away, because which was believed is the thing a governed system cannot afford to lose (`CLAUDE.md` §0) |

> **Six of this table's verdicts were stale, struck 2026-08-22 by the audit-remediation
> slice.** Every one was answered by a later WK-661 slice between 2026-08-17 and 2026-08-19, and
> none of those slices came back to this table — which is the same mechanism that left the
> slice count and the buildable-slice counter stale: **a slice updates the row that describes
> *it*, and a verdict table written by an *earlier* slice is a second place nothing
> reconciles.** The closure audit that found five of the six missed FR-174 entirely,
> and read FR-202's "Partial." as "Not started" — so the audit of the stale table was
> itself slightly stale, which is the argument for deriving these from `scope-audit.py`
> rather than reading them off a page.
