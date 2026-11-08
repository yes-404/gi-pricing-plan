---
id: FD-8415
family: finding
title: 02's §5.2 signatures, §5.3 views and §4.5 unit statement disagree with the code in ten places, and no side has been judged
status: active
created: 2026-11-08
owner: auditor
tree: 374a22bf33ad
corrected_by: []
relates: [FR-145, FR-150, FR-1840, OQ-587, FD-1723, FD-2034]
---

# FD-8415 — 02's §5.2 signatures, §5.3 views and §4.5 unit statement disagree with the code in ten places

*(Working id 8415, born open, filed 2026-11-08 by the auditor on the P28 recon of module 02 and the §14 review accepted at to-lead "2026-11-08 09:02:21 GMT". Severity LOW: no limb names a wrong number or a price. Owner Work: P3-C.)*

## Finding

`docs/specs/02-modelling.md` does not match the code at the tree below in ten places. **Which side is wrong is the owning P3 Work's first act, per limb**; this record judges neither side.

- **Predicate and corpus.** One row per (spec locus, code locus) pair that disagrees, over `02`'s §5.2 signatures, §5.3 view Contents and the §4.5 template catalogue. Count 10 (4 view or behaviour, 4 signature, 1 undeclared unit, 1 hand-written-shape candidate), by hand, no script. §5.1 was not re-run. The recon's 15 declared §5.3 routes all exist.
- **Tree.** `374a22bf33ad`.

| Limb | Spec says | Code does | Consequence |
|---|---|---|---|
| 1 | `02:2596-2597` `parse_expression(text, bound, params)` and `derive_derivatives(loss, wrt)` in `pricing_core/modelling/objectives.py`; `:2875` "declared and unbuilt" | Neither name exists under `packages/pricing-core/src`. Built entry points: `pricing_core/data/expressions.py:288` `parse_expression(expression, profile, *, symbols=None, limits=...)` and `modelling/expression_objective.py:100` `derive(loss, *, parameters=())` | A caller copying the spec imports names that do not exist. "Unbuilt" is contradicted by WK-690 (FR-150 amended 2026-10-04, FR-1840 2026-10-21). |
| 2 | `02:2878` "`compile_objective` refuses a non-template objective by name" | `modelling/objectives.py:735-745` returns `_compile_stored_expression` for `ObjectiveKind.EXPRESSION` | The opposite of the spec for expression objectives; same cause as limb 1, separate claim. |
| 3 | §5.3 "Objective certificate": "convexity heatmap … smoke-fit result" | `frontend/src/views/ObjectiveCertificateView.vue:19-22` "No convexity heatmap"; no "smoke" string in the view | Contents entry not rendered; the row carries no amendment note. The view cites FR-24 / OQ-587. Whether `smoke_fit` renders as one of nine checks is unverified. |
| 4 | §5.3 "Custom metric library": "link to the metric certificate (FR-162)" | `MetricLibraryView.vue:6-7` "No link to a metric certificate" | The row's 2026-08-27 note withdraws the editor only. |
| 5 | §5.3 "Built 2026-08-15" note: monotonic-direction and intent controls "not built" | `FactorCreateForm.vue:70` posts `monotonic_direction`; mounted in `FactorWorkbenchView.vue:337-348` | The spec is behind the code. The note's other departures were not re-checked. |
| 6 | `02:2577-2578` `load_gbm_booster(model_type, booster, nthread=None)` | `modelling/gbm.py:1172` `nthread` is keyword-only | `load_gbm_booster("xgboost", b, 4)` copied from the page raises `TypeError`. |
| 7 | `02:2634-2635` `unit_deviance(y, mu, *, family, power=1.5)`, `deviance(…, weights=None)` | `modelling/diagnostics.py:156-163, :217-225` add `theta: float \| None = None` | A signature omission: the page does not show `theta`. Omitting it is **not** silent: `diagnostics.py:183-188` (in `unit_deviance`) raises `ValueError` for `negative_binomial` when `theta` is `None` or not positive (the recon said silent; re-read at this tree). |
| 8 | `02:2602-2605` `make_xgb_objective(fns)`, `make_lgb_objective(fns)` | `modelling/objectives.py:886, :913` add `round_budget_s: float = DEFAULT_ROUND_BUDGET_S`; second callable argument typed `Any` | An undeclared wall-clock budget on arbitrary code is not on the page (`CLAUDE.md` §3, the four governance rules). |
| 9 | `02:2674-2676` `reconcile(assembled, *, observed, exposure, tolerance, treatments)` | `modelling/perils.py:157` adds `claim_count: NDArray \| None = None` | Minor. |
| 10 | §4.5 (`02:929-945`): `cap` and `threshold` "(minor units)"; `huber` / `pseudo_huber` `delta` no unit | `packages/model-schema/src/model_schema/objectives.py:360-380`: `cap`, `threshold` AND `delta` are all `kind="money_minor"`; bounds are floats; `compile_objective` takes `params: Mapping[str, float]` | Two limbs: **(a) typing precision** — `compile_objective` and `resolve_template_params` type the parameter values `Mapping[str, float]` (`objectives.py:636`, `:711`) while a `money_minor` value must be an `int`; the signature's honest type is `int \| float`; **(b) the spec omits the unit for `delta`**, so a caller supplying pounds mis-scales the loss. |

**Candidate, not counted:** `frontend/src/views/ModelSpecBuilderView.vue:96` `ref<"rmse" \| "mae">("rmse")` is a hand-written EBM objective vocabulary in the frontend (`CLAUDE.md` §2). The file says a `.test-d.ts` pin covers it (about line 99), so it may be a pinned mirror and not a divergence. The first act of P3-C reads it.

**Limb 10 is NOT a `CLAUDE.md` §7 finding** (the maintainer's ruling, relayed by the lead for this batch). The recon had flagged "money-valued parameters carried as float" as a candidate. `packages/model-schema/src/model_schema/objectives.py:222` refuses a non-int `money_minor` value at the boundary (`if self.kind == "money_minor" and not isinstance(value, int)`, after the bool refusal at `:220-221`), so a money parameter cannot enter as a float; and the loss itself is a float-domain numeric kernel outside the rating path (`CLAUDE.md` §7: money is integer pence, or Decimal in the rating path). What remains is limb 10(a) and 10(b).

## Evidence

The recon is `~/gi-pricing-plan.local/scratch/p28/recon-02.md` (local, not committed). The auditor re-read at `374a22bf33ad` the `def` lines of `load_gbm_booster`, `make_xgb_objective` and `reconcile` and the `money_minor` lines of `model_schema/objectives.py` (`git grep -n -E "money_minor" 374a22bf33ad -- packages/model-schema/src/model_schema/objectives.py`: `:204`, `:222`, `:360`, `:364`, `:377`, `:380`). The other quotations are the recon's. Not checked by the recon: return types of `ObjectiveFns.stabilise` and `.inverse_link`; `GlmFit` / `GbmFit` attributes; the Diagnostics, Model detail, Backtest and Prediction Contents (keyword only); a frontend hand-written-shape sweep beyond the one candidate.

## Disposition

**deferred with an owner: P3-C.** The Work's first act is, per limb, to decide which side was wrong, then amend the spec (with a dated line) or the code. Limbs 1 and 2 are the most consequential (a copied import fails). Limb 10 is not a §7 finding; its (a) and (b) are a typing precision and a missing unit.
