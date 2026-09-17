---
id: RL-874
family: ruling
title: the loaded-booster seam does not exist: `predict_gbm` re-loads the booster on every call
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slice1-rulings.md
---

## RL-874 — the loaded-booster seam does not exist: `predict_gbm` re-loads the booster on every call

**The claim in the frozen plan that does not hold, named first.** Task 1.3 instructs the
executor to build `CompiledBundle` holding *"any GBM boosters loaded from
`Bundle.resolved_payloads` into live `Booster` objects **via the existing
`predict_gbm`/`predict_glm` loaders**"* (`2026-08-29-w11-scoring.md:322-326`, emphasis
added). **There are no such loaders.** `predict_gbm` is a predictor, not a loader:
`def predict_gbm(result: GbmFitResult, booster: bytes, data: pl.DataFrame, ...) -> pl.Series`
(`../../packages/pricing-core/src/pricing_core/modelling/gbm.py:1185-1192`; the same
signature in `../specs/02-modelling.md:2345-2348`). It takes **bytes**, and on the XGBoost
branch constructs a fresh handle and deserialises into it on every invocation —

```python
loaded = xgb.Booster()
loaded.load_model(bytearray(booster))
```

(`gbm.py:1248-1250`) — and on the LightGBM branch does the same with
`lgb.Booster(model_str=booster.decode())` (`gbm.py:1269`). It returns predictions and never
the handle, so there is nothing for a `CompiledBundle` to hold. `predict_glm` takes a
`GlmFitResult` and no bytes (`../../packages/pricing-core/src/pricing_core/modelling/predict.py:230-239`), so the GLM half needs
nothing; the gap is the GBM half only.

**Why this is a decision and not an executor detail.** Following the instruction as written
puts a full booster deserialisation on the per-quote hot path, which is the exact cost
`FR-243` exists to remove — it requires boosters *"loaded from `resolved_payloads` into
**live objects**"* (`../specs/03-rating-engine.md:139`) — and the exact cost RL-867's
rationale rejected option (a) for. `NFR-489` is p99 < 50 ms with one `exact` GBM call;
`NFR-501` (`:789`) measures the `nthread=1` prediction itself at p99 1.626 ms on this
machine, so a per-call `load_model` is not a rounding error against that budget, it is the
budget. Resolving it changes a shipped `pricing-core` public signature and therefore
`02-modelling.md` §5.2, which is a spec change, not a local refactor.

**Options:**

- **(a) As the plan says** — `score_one`'s `model_call` calls `predict_gbm(result,
  booster_bytes, ...)` per quote. Zero new surface; defeats `FR-243` and spends the
  latency budget on work `CompiledBundle` exists to have already done.
- **(b) Split the seam** — a loader that returns the live booster object, and a prediction
  entry point that accepts one. `predict_gbm` keeps its present signature as a thin
  `load + predict` wrapper over the two, so **no existing caller changes** and no test moves.
- **(c) Memoise inside `predict_gbm`**, keyed on the bytes or their hash.

**Ruled: (b).**

Rationale:

- **(c) is the hidden cache RL-867 already rejected**, one level down. Its words:
  *"That hidden cache would just be option (b) again, minus the type system saying so —
  worse for testability (nothing distinguishes 'freshly deserialised' from 'already loaded'
  at the type level)"* (`2026-08-29-w11-prework-rulings.md:297-300`). The argument transfers
  intact from `Bundle`/`CompiledBundle` to `bytes`/`Booster`; ruling it differently here
  would make the same platform hold two contradictory positions on the same question.
- **(b) is the only option under which `FR-243`'s "live objects" clause has a
  referent.** Under (a) `CompiledBundle` holds bytes it re-parses per call, which is what
  `Bundle` already holds.
- **`predict_gbm`'s signature is preserved deliberately.** It has been corrected twice
  already (`../specs/02-modelling.md:2481` and `:2516`, 2026-08-16 and 2026-08-17), each time by a slice
  that found its behaviour wrong; a third change to its shape while WK-671 is mid-flight would
  put every existing caller and diagnostic in the blast radius of a rating-engine slice.
  Wrapping is strictly cheaper than changing.

**Disposition — the executor's, and *not* pre-written here.** The seam's function names,
the loaded type's name, and whether the loader lives in
`pricing_core/modelling/gbm.py` beside `predict_gbm` or in `pricing_core/rating/runtime.py`
beside `CompiledBundle` are Task 1.3's design, constrained only by the two clauses above.
This ruling deliberately writes no signature into `02-modelling.md` §5.2, because naming a
function before it is designed is how a spec acquires a signature nothing implements —
`FR-243` and `CompiledBundle` were that exact failure, and RL-867 exists because of
it. **The obligation instead: the PR that adds the loader appends its signature to
`../specs/02-modelling.md` §5.2 in the same commit**, per `CLAUDE.md` §2 (spec and code land
together) and §5's ten-section standard, where §5.2 is the `pricing-core` interface list.

**Acceptance test, stated as the violation that must become impossible.** A test asserting
that scoring N quotes against one `CompiledBundle` performs exactly **one** booster
deserialisation, not N. Written to fail against the plan-as-written implementation (a)
first — a probe that has never gone red has not been tested (`CLAUDE.md` §13).

**Clarification added 2026-08-29, with RL-879: which `NFR-501` figure this ruling makes
the right comparator.** Raised by the planner, who spotted that a per-call-load measurement is
not comparable to the number it is checked against — correct, and the remedy they first
proposed is not. `docs/research/w8-spike-resolution.md:76-80` publishes three rows, and
**none of them includes booster load**: `nthread=1 (incl. DMatrix)` **1.626 ms**,
`all-cores (incl. DMatrix)` 4.737 ms, and `predict-only (nthread=1)` 0.308 ms. Under this
ruling `CompiledBundle` holds the booster already loaded, and `score_one` still builds a
`DMatrix` per quote from that quote's features — so the shipping per-quote path is exactly
the *incl. DMatrix* shape and **1.626 ms is the correct comparator**, as `NFR-501`'s own
amended row already states. **0.308 ms is not the missing shape and must not be substituted
for it**: predict-only excludes `DMatrix` construction, which `score_one` genuinely performs,
so measuring against it would demand real work be free. What the plan's Task 1.4 Step 5
actually measures is a **fourth** shape — load + `DMatrix` + predict — that WK-668 never measured
and that is strictly larger than 1.626 ms, so it would read as a FAIL caused by the
implementation the ruling removes. The figure should be cited **with its shape** ("incl.
`DMatrix`, booster pre-loaded"), which is the durable fix; switching the number is not.

---
