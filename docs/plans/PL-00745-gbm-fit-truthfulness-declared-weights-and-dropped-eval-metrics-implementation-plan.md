---
id: PL-745
family: plan
kind: leaf
title: GBM Fit Truthfulness: Declared Weights and Dropped Eval Metrics — Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-22
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-22-gbm-weights-and-dropped-eval-metrics.md
---

# GBM Fit Truthfulness: Declared Weights and Dropped Eval Metrics — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans — this plan is a sequence of small, individually verifiable tasks; follow it strictly, do not "improve" the shape of the data, and do not skip the gate steps.

**Goal.** Close the two WK-661-owned defects in `fit_gbm` that share one shape — FR-159's own words for the class: *a spec accepted, silently ignored, and reported to the caller as configured*. (a) `spec.weight` is declared on `ModelSpecCommon`, honoured by `fit_glm`, `fit_ebm` and `compute_diagnostics`, and **ignored by both GBM backends** — so a severity GBM declaring FR-111's own default (`weight = claim_count`) fits unweighted while its diagnostics are computed *and labelled* claim-count-weighted (FR-184). (b) FR-161: when LightGBM early-stops on a Custom Metric, a declared **builtin** eval metric is dropped from the run and the fit says nothing; `GbmFitResult` gains `dropped_eval_metrics` so it does.

**Architecture.** Both halves are contained in `packages/pricing-core/src/pricing_core/modelling/gbm.py`'s fit path, and neither needs a backend handler change. For (a): a module-level `_weights(data, weight)` mirroring `_offset`'s shape, called once for the training frame and once for the holdout; the `valid` 3-tuple widens to a 4-tuple; `_fit_xgboost`'s `matrix()` closure gains a `weight` argument and `_fit_lightgbm`'s two `lgb.Dataset(...)` calls gain `weight=`. Every downstream consumer already reads the weights back — `make_xgb_objective`/`make_lgb_objective` call `get_weight()`, and both `_custom_feval` helpers do too — so **only construction is missing**; the fix makes existing plumbing live rather than adding any. For (b): `_builtin_eval_metric_names(spec.eval_metrics)` is already computed in the `else` arm of the `stopping_on_custom` branch; the `if` arm computes the same list and returns it as a fifth element, which `fit_gbm` places on `GbmFitResult`.

**Tech Stack.** Python 3.12; Pydantic v2 (model-schema); XGBoost 3.4.1 `xgb.DMatrix(weight=)`, LightGBM 4.7.0 `lgb.Dataset(weight=)`; NumPy; Polars; pytest with `@pytest.mark.req` and `monkeypatch`; no pandas.

**Spec.** `docs/specs/02-modelling.md` — FR-111 (weighting defaults), FR-184 (the weighting label on diagnostics), FR-159 (the silently-ignored-spec defect class), FR-160 (metric ordering), **FR-161** (the drop record, *"Owner: WK-661 … lands before WK-661 closes"*), FR-206 (`spec_hash` version discipline), FR-207 (declared-and-unbuilt staging).

## Decisions taken at planning time — maintainer acceptance required

Three judgment calls this plan makes rather than defers. Each is implemented as written below; **reject any of them and the corresponding task changes shape**, so read these before dispatching Task 1.

1. **`SPEC_HASH_VERSION` 9 → 10 (Task 3).** Every prior bump (v1→v9) was for a **payload** change: a field joined the canonicalised spec. This one is different in kind — the payload is unchanged, because `weight` has been inside `ModelSpec` and inside the digest all along. What changes is its **interpretation**: after Task 1, a stored `v9:` digest for a weighted GBM describes a fit this build would produce *differently*. `spec_hash`'s own docstring says the version exists so that "two algorithm versions cannot produce the same hash even for an identical spec", and `spec_hash_is_current` says a stale digest "is not wrong, it is **unmatchable**". That is exactly the state a weighted-spec GBM fitted before this slice is in: FR-204's dedup would otherwise hand the next caller an unweighted fit for a weighted spec, with no error to see. **Recommendation: bump.** The cost is the documented one every bump pays — every `v9:` digest goes stale and is findable with `LIKE 'v9:%'` — and it is paid by unweighted GLMs too, which is over-invalidation. The alternative, a targeted invalidation of weighted-GBM rows only, has no mechanism in this codebase and inventing one is larger than the slice.
2. **`dropped_eval_metrics` lives on `GbmFitResult` only, not on `GbmFit` as well (Tasks 4–5).** FR-161 reads "`GbmFit` and the persisted `GbmFitResult` gain `dropped_eval_metrics`". `GbmFit.result` **is** the `GbmFitResult`, so a second copy on the wrapper is a field that can disagree with itself, and `eval_curve` sits on `GbmFit` *because* it is deliberately not persisted (it belongs to `GbmDiagnostics`) — the opposite case. Callers reach it as `fit.result.dropped_eval_metrics`. **This is a code-proves-the-spec-wrong resolution under §0, so it lands as a dated amendment to FR-161 in Task 7 — not a quiet edit and not a second field.**
3. **A missing weight column raises Polars' own `ColumnNotFoundError`, not a named `GbmFitError` (Task 1).** `fit_glm` (glm.py:583-584) does exactly this today and has since it was written. Giving the GBM path a named error would make the platform answer the same malformed spec differently depending on model type. If a named code is wanted it belongs in a slice that gives it to both. **No new error code in this slice**, so no `errors.py` or §5.1 catalogue entry is needed.

## Slice context (verified at planning time, 2026-08-22)

- **Post-EBM (#129, HEAD `c2c54a6`) MODEL axis:** 124 requirements in scope, 107 evidenced (86%), 17 unevidenced; endpoints 40/40. Of the 6 unevidenced **FR**-MODEL requirements, five are gated — FR-91 (Phase 3), FR-95 and FR-144 (Phase 2, WK-690), FR-117 (gated on "when a workflow needs one"), FR-138 (gated on the job-latency measurement). **FR-161 is the only unevidenced FR-MODEL requirement WK-661 owes with nothing in front of it.**
- **The weight defect is real and GBM is the sole outlier.** `fit_gbm` (gbm.py:600-660) resolves `base_margin` and the response and never mentions `spec.weight`; `grep -n "spec.weight" gbm.py` returns nothing. `fit_glm` honours it (glm.py:583-584), `fit_ebm` honours it via `sample_weight` (recorded in the EBM slice, roadmap.md:2797), and `diagnostics.py`'s `_weighting()`/`_weights()` (112-131) return `Weighting.CLAIM_COUNT` and the column whenever `spec.weight.kind == "column"` — **for a GBM too**. So a GBM's diagnostics are weighted and labelled under FR-184 while the model was fitted unweighted: the label is true of the metric and false of the model. Diagnostics need no change; the bug is entirely in the fit path.
- **FR-111 nonetheless reads green** in `scope-audit`, because all three of its `@pytest.mark.req` markers live in `test_glm.py`. This is CLAUDE.md §13's "a marker is a claim, not a proof" case exactly, and it is why the slice was found by reading code rather than by reading the coverage report.
- **The readback plumbing already exists.** `make_xgb_objective` (objectives.py:728-729) and `make_lgb_objective` (759-760) both do `weight = np.asarray(d.get_weight(), ...); w = weight if weight.size == y.size else np.ones_like(y)`, and `_xgb_custom_feval` (gbm.py:790-798) / `_lgb_custom_feval` (940-948) do the same. Nothing has ever set the weights, so **every custom objective fitted to date received `w = ones`** — while `make_lgb_objective`'s docstring (objectives.py:747) asserts *"The weights are read off the dataset instead, so nothing is dropped; §5.2 carries the dated correction."* That sentence is false today and Task 2 corrects it.
- **The change is contained.** `valid` has exactly 6 use sites (gbm.py:643, 650, 656, 661, 808, 852-857, 959, 1048-1051), and both training-set constructions are single expressions: `xgb.DMatrix(...)` inside the `matrix()` closure at 845-848, and `lgb.Dataset(...)` at 1044-1047 with the holdout at 1048-1051.
- **FR-161 is unbuilt**, verified: `dropped_eval_metrics` appears nowhere in the tree. The drop site is gbm.py:1004-1017, where `params["metric"] = "None"` is set under `stopping_on_custom` with a comment naming the consequence and the test that pins it (`test_lightgbm_drops_a_builtin_eval_metric_rather_than_stop_on_it`).
- **A bookkeeping discrepancy to correct, not merely note.** roadmap.md:2811-2812 records the weight gap as *"dated note 2026-08-21, owner WK-661"* — but no such note exists in `02-modelling.md`. `git log -S "dated note 2026-08-21"` shows the string entered the repository only in `c2c54a6`, and only in `docs/roadmap.md`. **The FR-207 obligation was recorded as discharged and never was.** This slice discharges it by *building* the field rather than by writing the note, and Task 8 corrects the roadmap's claim.
- **No backend handler change.** `model_handlers.py:347` reads `fit.result, fit.booster_bytes, fit.eval_curve` by attribute; a new field on `GbmFitResult` is persisted by the existing `record_fit` path with zero handler edits.
- **Also carried by Task 7** (cheap, adjacent, and otherwise orphaned): `02` §4.4's `spec_hash` lineage never recorded the v6 and v7 transitions, though `backend/src/app/platform/modelling.py`'s comment block does.

## Global Constraints

- **Workspace:** single uv workspace — `uv sync --all-packages --dev`. `--all-packages` is not optional.
- **Ruff** line length 100; **mypy --strict** on `packages/`; **lint-imports** (pricing-core imports `model_schema` only, never `backend`).
- **No pandas**; **Pydantic v2**; frozen models with `extra="forbid"` for anything persisted.
- **Every test** carries `@pytest.mark.req(...)` naming the requirement it satisfies, and **a negative or control test precedes every positive one** for each invariant.
- **House test conventions in `packages/pricing-core/tests/test_gbm.py`:** `BACKENDS = ["xgboost", "lightgbm"]` (:52), `EXPOSURE` (:54), `_factor` (:57), `FACTORS` (:66), `_frequency_data(n=8_000, seed=20260817)` (:69), `_spec(backend, **over)` (:90), `_custom` (:682), `_custom_spec` (:712), `_METRIC_REF = "custom_metric:poisson-nll@1"` (:996), `_metric` (:999). Every test is `@pytest.mark.parametrize("backend", BACKENDS)` and carries a docstring naming the failure mode it prevents. **There is no severity fixture and there are zero weight tests** — Task 1 adds both.
- **Determinism:** every fit in this plan pins `seed`; NFR-481 requires `tree_method: "hist"` (XGBoost) and `deterministic` + `force_row_wise` (LightGBM), which `_shared_params` already sets. Do not add tolerance-free equality assertions across differing row counts — LightGBM's `min_data_in_leaf` counts rows, not weight, so a duplicate-rows-vs-weights equivalence does **not** hold and must not be tested.
- **Contracts:** `uv run python scripts/generate-contracts.py` after any model-schema change (FR-451); `--check` fails CI on drift. `model.schema.json`, `diagnostics.schema.json` and `openapi/generated.json` are expected to change in Task 6; authored contracts are untouched.
- **If code proves the spec wrong**, amend the spec with a dated note saying which side was wrong and why — never a quiet edit (§0). Task 7 is where that lands.
- **Conventional Commits** (`feat(pricing-core):`, `feat(model-schema):`, `feat(backend):`, `chore(contracts):`, `docs(spec):`, `docs(roadmap):`), each naming its FR numbers, with the `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` trailer on every commit.
- No PR, no merge — the last task closes with the roadmap record and the full gate, both halves.

---

## Task 1 — `spec.weight` reaches both GBM backends

**Files**
- Modify: `packages/pricing-core/src/pricing_core/modelling/gbm.py` (add `_weights` near `_offset` at :200; `fit_gbm` :600-665; `_fit_xgboost` :803-860; `_fit_lightgbm` :955-1055)
- Modify: `packages/pricing-core/tests/test_gbm.py`

**Interfaces**
- Consumes: `WeightSpec` (`model_schema.modelling`, :721-733 — `kind: Literal["none", "column"]`, `column: str | None`), already reachable as `spec.weight` via `ModelSpecCommon` (:829). `_offset(data, offset, *, what) -> np.ndarray | None` (gbm.py:200) as the shape to mirror.
- Produces:
  - `_weights(data: pl.DataFrame, weight: WeightSpec) -> np.ndarray | None` (module-level in gbm.py).
  - `valid` widens everywhere from `tuple[np.ndarray, np.ndarray, np.ndarray | None] | None` to **`tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None] | None`** — element 3 is the holdout weights.
  - `_fit_xgboost` and `_fit_lightgbm` each gain a **`weights: np.ndarray | None`** parameter positioned immediately after `base_margin`. Return types are unchanged by this task.
  - Test helpers `_severity_data(n=..., seed=...) -> pl.DataFrame` and `_severity_spec(backend, **over) -> GbmSpec` in `test_gbm.py`.

**Steps**

- [ ] **1.1 Write the control test — an all-ones weight column must change nothing.**

Append to `packages/pricing-core/tests/test_gbm.py`. This test **passes before the fix and must still pass after it**: it is what proves the new plumbing is inert when the spec asks for nothing.

```python
@pytest.mark.req("FR-111")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_weight_column_of_ones_fits_identically_to_no_weight(backend: str) -> None:
    """The control for the weighting plumbing.

    A uniform weight is mathematically no weight at all. If these two fits differ, the
    weights are reaching the backend as something other than a multiplier on each row's
    contribution — and every assertion in the tests below about *non*-uniform weights
    would then be measuring the wrong thing.
    """
    data = _frequency_data().with_columns(pl.lit(1.0).alias("ones"))
    unweighted = fit_gbm(data, _spec(backend), FACTORS)
    weighted = fit_gbm(data, _spec(backend, weight=WeightSpec(kind="column", column="ones")), FACTORS)
    assert weighted.result.booster_blob.sha256 == unweighted.result.booster_blob.sha256, (
        "a uniform weight changed the booster; the weights are not entering as row multipliers"
    )
```

- [ ] **1.2 Write the failing test — non-uniform weights must change the fit.**

```python
@pytest.mark.req("FR-111")
@pytest.mark.parametrize("backend", BACKENDS)
def test_non_uniform_weights_change_the_fit(backend: str) -> None:
    """`spec.weight` was accepted and ignored by both GBM backends until 2026-08-22.

    `fit_glm` has honoured it since it was written and `fit_ebm` since the EBM slice, so
    the same spec meant one thing for a GLM and another for a GBM. The symptom is silent:
    the fit succeeds, and `compute_diagnostics` then labels its metrics claim-count-
    weighted (FR-184) on the strength of a `spec.weight` the fit never read.
    """
    data = _frequency_data().with_columns(
        (pl.col("exposure_years") * 10.0 + 1.0).alias("claim_count")
    )
    unweighted = fit_gbm(data, _spec(backend), FACTORS)
    weighted = fit_gbm(
        data, _spec(backend, weight=WeightSpec(kind="column", column="claim_count")), FACTORS
    )
    assert weighted.result.booster_blob.sha256 != unweighted.result.booster_blob.sha256, (
        "a non-uniform weight column left the booster byte-identical; spec.weight is being "
        "ignored by the fit path"
    )
```

Add `WeightSpec` to `test_gbm.py`'s `model_schema.modelling` import if it is not already there.

- [ ] **1.3 Run both to confirm 1.1 passes and 1.2 fails**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -k "weight_column_of_ones or non_uniform_weights" -q`
Expected: 2 PASS (1.1, both backends), 2 FAIL (1.2, both backends) with the "left the booster byte-identical" message.

- [ ] **1.4 Add `_weights` to gbm.py**

Insert immediately after `_offset` ends (before the next `def`, around :230). Add `WeightSpec` to the `model_schema.modelling` import block at the top of the file.

```python
def _weights(data: pl.DataFrame, weight: WeightSpec) -> np.ndarray | None:
    """The weight column as a float array, or `None` for `kind: "none"` (FR-111).

    Two lines, mirroring `fit_glm`'s (glm.py) deliberately: severity weights by claim
    count and burning cost by exposure are properties of the *response*, not of the
    estimator, so the same spec must mean the same thing for a GLM, a GBM and an EBM. A
    missing column raises Polars' own `ColumnNotFoundError` here exactly as it does there
    — a named `GbmFitError` would make the platform answer one malformed spec differently
    depending on which model type happened to read it.
    """
    if weight.kind == "none":
        return None
    return data[str(weight.column)].cast(pl.Float64).to_numpy()
```

- [ ] **1.5 Resolve the weights in `fit_gbm` and widen `valid`**

In `fit_gbm`, after `base_margin = _offset(data, spec.offset, what="this fit")` (:605):

```python
    weights = _weights(data, spec.weight)
```

Widen the `valid` declaration at :643 and its assignment at :650:

```python
    valid: tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None] | None = None
    if holdout is not None:
        holdout_matrix = resolve_factors(holdout, factors, bandings=bandings, groupings=groupings)
        vx = _encode(holdout_matrix, factors, maps=encodings, bandings=bandings).x
        vy = apply_loss_treatment(
            holdout[spec.response_column].cast(pl.Float64).to_numpy(), spec.loss_treatment
        )
        # The holdout is weighted too, and for the same reason FR-183 gives for
        # reporting both partitions: a curve whose train half is weighted and whose
        # holdout half is not is two different quantities plotted on one axis, and the
        # divergence early stopping exists to catch would be read off the difference
        # between the weightings rather than off the model.
        valid = (vx, vy, _offset(holdout, spec.offset, what="the holdout"),
                 _weights(holdout, spec.weight))
```

Pass `weights` through both dispatch calls (:656, :661), immediately after `base_margin`:

```python
        payload, best, curve, versions = _fit_xgboost(
            spec, x, response, base_margin, weights, valid, order, constraints,
            unordered, xgb_objective, rounds, resolved_metrics, metric_link,
        )
    else:
        payload, best, curve, versions = _fit_lightgbm(
            spec, x, response, base_margin, weights, valid, order, constraints,
            unordered, lgb_objective, rounds, resolved_metrics, metric_link,
        )
```

- [ ] **1.6 Thread the weights into XGBoost**

In `_fit_xgboost`, add the parameter and widen `valid` (:806-808):

```python
    base_margin: np.ndarray | None,
    weights: np.ndarray | None,
    valid: tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None] | None,
```

Give the `matrix()` closure a weight argument (:845-848) and use it at both call sites:

```python
    def matrix(
        features: np.ndarray, label: np.ndarray, margin: np.ndarray | None,
        weight: np.ndarray | None,
    ) -> Any:
        return xgb.DMatrix(
            features, label=label, base_margin=margin, weight=weight,
            feature_names=list(order), feature_types=feature_types, enable_categorical=True,
        )

    dtrain = matrix(x, y, base_margin, weights)
```

and in the `evals` construction (:857):

```python
        evals = [(dtrain, "train"), (matrix(valid[0], valid[1], valid[2], valid[3]), "holdout")]
```

- [ ] **1.7 Thread the weights into LightGBM**

In `_fit_lightgbm`, add the parameter and widen `valid` (:958-959) identically to 1.6. Then the two `lgb.Dataset` calls (:1044-1051):

```python
    train_set = lgb.Dataset(
        x, label=y, init_score=base_margin, weight=weights, feature_name=list(order),
        categorical_feature=categorical_indices, free_raw_data=False,
    )
```

```python
        valid_sets = [
            train_set,
            lgb.Dataset(valid[0], label=valid[1], init_score=valid[2], weight=valid[3],
                        reference=train_set, feature_name=list(order),
                        categorical_feature=categorical_indices, free_raw_data=False),
        ]
```

- [ ] **1.8 Run the two tests to verify both now pass**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -k "weight_column_of_ones or non_uniform_weights" -q`
Expected: 4 PASS.

- [ ] **1.9 Add the severity fixture and the actuarial test**

`test_gbm.py` has no severity fixture. Add both helpers next to `_frequency_data`/`_spec`, then the test. The construction is deliberate: within each region, half the rows carry a claim severity of 1.0 and half 9.0 — an unweighted mean of 5.0 — and the claim counts weight them 9:1, giving a claim-count-weighted mean of `(9*1 + 1*9) / 10 = 1.8`. The gap between 5.0 and 1.8 is far larger than any tree-fitting noise, so the assertion is a real actuarial statement and cannot flake.

```python
def _severity_data(n: int = 4_000, seed: int = 20260822) -> pl.DataFrame:
    """A severity book whose claim-count weighting is knowable in closed form.

    Within every region, the severities are 1.0 and 9.0 in equal numbers — an unweighted
    mean of 5.0 — and the claim counts are 9 on the 1.0 rows and 1 on the 9.0 rows, so
    the claim-count-weighted mean is 1.8. FR-111 makes claim-count weighting the
    severity default, and the two numbers are far enough apart that no fitting noise can
    confuse them.
    """
    rng = np.random.default_rng(seed)
    region = rng.integers(0, 3, size=n)
    small = np.arange(n) % 2 == 0
    return pl.DataFrame(
        {
            "region": [f"r{value}" for value in region],
            "severity": np.where(small, 1.0, 9.0),
            "claim_count": np.where(small, 9.0, 1.0),
            "exposure_years": np.ones(n),
        }
    )


def _severity_spec(backend: str, **over: object) -> GbmSpec:
    """FR-111's severity defaults on a GBM: Gamma objective, claim-count weights."""
    return _spec(
        backend,
        response_column="severity",
        objective="reg:gamma" if backend == "xgboost" else "gamma",
        offset=OffsetSpec(kind="none"),
        **over,
    )
```

Check `_spec`'s signature at test_gbm.py:90 before writing `_severity_spec` — if it names `objective`/`offset`/`response_column` as explicit keyword parameters rather than routing them through `**over`, pass them the way `_spec` expects. `SEVERITY_FACTORS` is a one-entry tuple over `region`, built with the existing `_factor` helper.

```python
@pytest.mark.req("FR-111")
@pytest.mark.req("FR-184")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_gamma_severity_fit_weighted_by_claim_count_predicts_the_weighted_mean(
    backend: str,
) -> None:
    """FR-111's severity default, end to end, on the number it changes.

    Unweighted the book's mean severity is 5.0; weighted by claim count it is 1.8. Before
    2026-08-22 a GBM declaring `weight = claim_count` produced the first number while
    `compute_diagnostics` labelled its metrics claim-count-weighted (FR-184) — the
    label true of the metric and false of the model that produced it.
    """
    data = _severity_data()
    fit = fit_gbm(
        data,
        _severity_spec(backend, weight=WeightSpec(kind="column", column="claim_count")),
        SEVERITY_FACTORS,
    )
    predicted = predict_gbm(fit.result, _booster_blob(fit), data, SEVERITY_FACTORS)
    assert 1.5 < float(np.mean(predicted)) < 2.2, (
        f"claim-count-weighted severity should sit near 1.8, not {float(np.mean(predicted)):.3f}; "
        "5.0 means the weights never reached the objective"
    )
```

`predict_gbm`'s exact call shape — in particular how the booster bytes are handed back to it — is already exercised by the existing prediction tests in `test_gbm.py`. Copy that call verbatim from the nearest one rather than inventing `_booster_blob`; if the file already has such a helper, use it under its real name.

- [ ] **1.10 Run the severity test**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -k severity_fit_weighted -q`
Expected: 2 PASS. If either backend lands near 5.0, the weights are not reaching that backend's objective — do not widen the bounds.

- [ ] **1.11 Run the full GBM suite for regressions**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -q`
Expected: all PASS. Any pre-existing test that now fails is a real behaviour change and must be understood, not adjusted — every existing test uses `weight` at its `"none"` default, so none of them should move.

- [ ] **1.12 Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/gbm.py packages/pricing-core/tests/test_gbm.py
git commit -m "$(cat <<'EOF'
feat(pricing-core): FR-111 — spec.weight reaches both GBM backends

fit_gbm accepted spec.weight and ignored it, while fit_glm, fit_ebm and
compute_diagnostics all honour it. A severity GBM declaring the requirement's
own default fitted unweighted and was then labelled claim-count-weighted by
FR-184's diagnostics — the label true of the metric, false of the model.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2 — the custom objective and custom metric receive the declared weights

**Files**
- Modify: `packages/pricing-core/src/pricing_core/modelling/objectives.py:739-766` (docstring only)
- Modify: `packages/pricing-core/tests/test_gbm.py`

**Interfaces**
- Consumes: Task 1's `_weights` plumbing; `gbm.make_xgb_objective` / `gbm.make_lgb_objective` (imported into gbm's namespace and called bare at gbm.py:618-619, so both are monkeypatchable on the `gbm` module); `gbm.evaluate_metric` (imported at gbm.py:64, signature `evaluate_metric(metric, y, f, w) -> float`); the existing `_custom` (:682), `_custom_spec` (:712), `_METRIC_REF` (:996) and `_metric` (:999) helpers.
- Produces: no new production symbols. This task proves Task 1's plumbing reaches the two consumers whose readback code already existed, and deletes a false claim from a docstring.

**Steps**

- [ ] **2.1 Write the failing test — a custom objective must receive the declared weights**

This is the decisive test for the defect, and it cannot flake: it records the exact array the backend hands the objective, and compares it to the column.

```python
@pytest.mark.req("FR-111")
@pytest.mark.req("FR-146")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_custom_objective_receives_the_declared_weights(
    backend: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`make_*_objective` reads `get_weight()` off the dataset — nothing ever set it.

    Both wrappers fall back to `np.ones_like(y)` when the array they read is the wrong
    size, and an unset weight reads as size zero, so every custom objective fitted before
    2026-08-22 computed its gradient and hessian against uniform weights while the spec
    said otherwise. `make_lgb_objective`'s docstring asserted the opposite in as many
    words; step 2.4 corrects it.
    """
    data = _frequency_data().with_columns(
        (pl.col("exposure_years") * 10.0 + 1.0).alias("claim_count")
    )
    expected = data["claim_count"].to_numpy()
    seen: list[np.ndarray] = []

    maker = "make_xgb_objective" if backend == "xgboost" else "make_lgb_objective"
    real = getattr(gbm, maker)

    def recording(fns: object) -> object:
        inner = real(fns)

        def objective(predt: np.ndarray, dataset: Any) -> Any:
            seen.append(np.asarray(dataset.get_weight(), dtype=np.float64).copy())
            return inner(predt, dataset)

        return objective

    monkeypatch.setattr(gbm, maker, recording)
    fit_gbm(
        data,
        _custom_spec(backend, weight=WeightSpec(kind="column", column="claim_count")),
        FACTORS,
        objective=_custom(),
    )

    assert seen, "the recording objective was never called; the monkeypatch missed"
    np.testing.assert_allclose(seen[0], expected)
```

`test_gbm.py` must import the `gbm` module itself (`from pricing_core.modelling import gbm`) and `Any` for this to type-check; add both if absent. Check `_custom_spec`'s signature and `fit_gbm`'s objective keyword at test_gbm.py:712 and copy the call shape from the nearest existing custom-objective test.

- [ ] **2.2 Run it to verify it fails**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -k custom_objective_receives -q`
Expected: **2 PASS** if Task 1 is complete — this test has no production change of its own, and Task 1 is what makes it pass. Confirm it *would have* failed by stashing Task 1's `weight=` arguments:

Run: `git stash push packages/pricing-core/src/pricing_core/modelling/gbm.py && uv run pytest packages/pricing-core/tests/test_gbm.py -k custom_objective_receives -q; git stash pop`
Expected: FAIL with a shape or value mismatch against an array of ones, then PASS again after the pop. **Do not skip this step** — a test that was green before the fix proves nothing about the fix.

- [ ] **2.3 Write the custom-metric test**

```python
@pytest.mark.req("FR-155")
@pytest.mark.req("FR-111")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_custom_eval_metric_receives_the_declared_weights(
    backend: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FR-155 calls the metric an exposure-weighted mean; it was an unweighted one.

    Both `_custom_feval` helpers read `get_weight()` and fall back to ones exactly as the
    objective wrappers do, so a declared weight column left the reported metric weighted
    by nothing at all — while `compute_diagnostics` reported its own metrics weighted.
    """
    data = _frequency_data().with_columns(
        (pl.col("exposure_years") * 10.0 + 1.0).alias("claim_count")
    )
    expected = data["claim_count"].to_numpy()
    seen: list[np.ndarray] = []
    real = gbm.evaluate_metric

    def recording(metric: Any, y: np.ndarray, f: np.ndarray, w: np.ndarray) -> float:
        seen.append(np.asarray(w, dtype=np.float64).copy())
        return real(metric, y, f, w)

    monkeypatch.setattr(gbm, "evaluate_metric", recording)
    fit_gbm(
        data,
        _spec(
            backend,
            eval_metrics=(GbmFunctionRef(kind="custom", ref=_METRIC_REF),),
            weight=WeightSpec(kind="column", column="claim_count"),
        ),
        FACTORS,
        metrics={_METRIC_REF: _metric()},
    )

    assert seen, "the recording metric was never called; the monkeypatch missed"
    train = [array for array in seen if array.size == expected.size]
    assert train, f"every weight array reaching the metric had the wrong size: {[a.size for a in seen]}"
    np.testing.assert_allclose(train[0], expected)
```

Copy the `eval_metrics` / `metrics=` call shape verbatim from the nearest existing custom-metric test (`test_gbm.py` around :996-1060) — including the exact spelling of `GbmFunctionRef`'s `ref` field, which the surrounding tests already use correctly.

- [ ] **2.4 Correct the false docstring in `make_lgb_objective`**

`objectives.py:747` currently claims the weights are read off the dataset "so nothing is dropped". That was aspirational for the whole time both GBM backends ignored `spec.weight`. Replace the sentence with a dated correction in the house style:

```python
    LightGBM's objective signature carries no weight argument, so the weights are read off
    the dataset (`get_weight()`) rather than handed in. *(Corrected 2026-08-22, WK-661: this
    docstring previously said "so nothing is dropped", which was false from the day it was
    written — `fit_gbm` never set the weights on either backend's dataset, so the fallback
    to `np.ones_like(y)` below fired on every custom-objective fit the platform had ever
    run. The construction was added in the same slice as this correction; the fallback now
    means "the spec declared no weight" rather than "nobody supplied one".)*
```

Read `make_xgb_objective`'s docstring (:716-736) in the same pass and apply the same correction if it makes the same claim; leave it alone if it does not.

- [ ] **2.5 Run both new tests and the full GBM suite**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -q`
Expected: all PASS.

- [ ] **2.6 Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/objectives.py packages/pricing-core/tests/test_gbm.py
git commit -m "$(cat <<'EOF'
feat(pricing-core): FR-111/155 — custom objectives and metrics see the declared weights

Both readback paths existed and both fell back to ones, so every custom
objective and custom eval metric fitted before this slice was uniform-weighted.
make_lgb_objective's docstring asserted the opposite; corrected with a dated note.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3 — `SPEC_HASH_VERSION` 9 → 10

**Files**
- Modify: `backend/src/app/platform/modelling.py:95-137` (the lineage comment block and the constant)
- Modify: `backend/tests/test_spec_hash.py:186-199`

**Interfaces**
- Consumes: nothing from earlier tasks at the type level; depends on Task 1 having changed what a weighted GBM spec *means*.
- Produces: `SPEC_HASH_VERSION: Final = 10`; every `spec_hash` result now prefixed `v10:`; `spec_hash_is_current("v9:...")` returns `False`.

**Steps**

- [ ] **3.1 Update the pin test first**

`test_spec_hash.py:193` asserts the constant and a digest prefix, and its docstring explains why both: a digest-only test passes after a hand-edit that forgot the constant. Extend the comment block above the assertions and move all three:

```python
    # v9 -> v10 (2026-08-22, FR-111/206): the **first bump for an interpretation
    # change rather than a payload one**. `weight` has been inside `ModelSpec` and inside
    # this digest since it was written, but `fit_gbm` ignored it until this date — so
    # every `v9:` digest over a weighted GBM spec describes a fit this build produces
    # differently. FR-204 would otherwise hand the next caller the unweighted fit for
    # a weighted spec, with nothing to see. A future reader should not conclude from the
    # v1..v9 lineage that this tag tracks fields; it tracks what a digest promises.
    assert SPEC_HASH_VERSION == 10, (
        "fit_gbm began honouring spec.weight (FR-111); the tag moves with the meaning"
    )
    assert spec_hash(_bound()).startswith("v10:sha256:")
    assert spec_hash_is_current("v9:sha256:" + "0" * 64) is False, (
        "every v9 digest is now stale and must be findable with LIKE 'v9:%'"
    )
```

- [ ] **3.2 Run it to verify it fails**

Run: `uv run pytest backend/tests/test_spec_hash.py -q`
Expected: FAIL on `assert SPEC_HASH_VERSION == 10`.

- [ ] **3.3 Bump the constant and extend the lineage comment**

In `backend/src/app/platform/modelling.py`, append to the `#:` block immediately before the constant, then change the constant:

```python
#: **v10, 2026-08-22** — the first bump for an **interpretation** change rather than a
#: payload one (FR-111). `weight` was already in the payload; what changed is that
#: `fit_gbm` began honouring it, having accepted and ignored it since the GBM slice. So a
#: `v9:` digest over a weighted GBM spec names a fit this build produces differently, and
#: FR-204's dedup would answer the next caller with an unweighted fit for a weighted
#: spec. Every `v9:` digest is now stale and findable with `LIKE 'v9:%'`. The cost is the
#: documented one and is over-paid: an unweighted GLM's digest goes stale too, for a change
#: that cannot have affected it. A targeted invalidation has no mechanism here, and
#: inventing one is larger than the defect it would spare.
SPEC_HASH_VERSION: Final = 10
```

- [ ] **3.4 Run the spec-hash suite**

Run: `uv run pytest backend/tests/test_spec_hash.py -q`
Expected: all PASS.

- [ ] **3.5 Run the backend suite for anything pinning `v9:`**

Run: `uv run pytest backend/tests -q -k "spec_hash or model"`
Expected: all PASS. A fixture with a hard-coded `v9:` digest is a real find — update it to `v10:` and note it in the commit body.

- [ ] **3.6 Commit**

```bash
git add backend/src/app/platform/modelling.py backend/tests/test_spec_hash.py
git commit -m "$(cat <<'EOF'
feat(backend): FR-206 — spec_hash v9 -> v10 for the GBM weighting change

The payload is unchanged; the interpretation is not. A v9 digest over a
weighted GBM spec names a fit this build produces differently, and FR-204
would hand the next caller the unweighted one. First bump for a meaning change
rather than a field, recorded as such in the lineage.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4 — `DroppedEvalMetric` and `GbmFitResult.dropped_eval_metrics`

**Files**
- Modify: `packages/model-schema/src/model_schema/modelling.py` (new class near `GbmFunctionRef` at :1187; new field on `GbmFitResult` at :1569)
- Modify: `packages/model-schema/src/model_schema/__init__.py` (export)
- Create: `packages/model-schema/tests/test_dropped_eval_metrics.py`

**Interfaces**
- Consumes: `GbmFitResult`'s existing conventions — `ConfigDict(frozen=True, extra="forbid")`, `@model_validator(mode="after")` returning `self`.
- Produces:
  - `class DroppedEvalMetric(BaseModel)` — frozen, `extra="forbid"`; `name: str`; `reason: Literal["builtin_evaluated_before_custom_stopping_metric"]`.
  - `GbmFitResult.dropped_eval_metrics: tuple[DroppedEvalMetric, ...] = ()`.
  - `GbmFitResult._a_dropped_metric_is_named_once(self) -> GbmFitResult`.

**Steps**

- [ ] **4.1 Write the failing tests**

```python
"""FR-161: a declared eval metric a backend could not evaluate is recorded."""

import pytest
from pydantic import ValidationError

from model_schema.modelling import DroppedEvalMetric, GbmFitResult


@pytest.mark.req("FR-161")
def test_a_dropped_metric_names_a_reason_from_the_closed_set() -> None:
    """One reason exists today (FR-160). A free-text field would let a second be
    invented at a call site instead of declared in the contract the frontend generates
    from, which is how a status enum turns into prose."""
    with pytest.raises(ValidationError):
        DroppedEvalMetric(name="poisson-nll", reason="because")


@pytest.mark.req("FR-161")
def test_the_same_metric_cannot_be_dropped_twice() -> None:
    """A name appearing twice is a bug in the producer, not two facts about the fit."""
    dropped = DroppedEvalMetric(
        name="poisson-nll", reason="builtin_evaluated_before_custom_stopping_metric"
    )
    with pytest.raises(ValidationError, match="named once"):
        _result(dropped_eval_metrics=(dropped, dropped))


@pytest.mark.req("FR-161")
def test_a_fit_result_drops_nothing_by_default() -> None:
    """The overwhelmingly common case, and the one every artifact written before this
    field existed is in: no metric was dropped, and the tuple says so rather than being
    absent."""
    assert _result().dropped_eval_metrics == ()
```

`_result(**over)` is a module-level builder for a minimal valid `GbmFitResult`. Copy its field set from the nearest existing `GbmFitResult` construction in `packages/model-schema/tests/` — the model is `extra="forbid"` with several required fields (`model_type`, `booster_blob`, `booster_format`, `feature_order`, `base_margin`, `best_iteration`, `fit_seconds`) and two cross-field validators, so an invented one will not construct.

- [ ] **4.2 Run to verify all three fail**

Run: `uv run pytest packages/model-schema/tests/test_dropped_eval_metrics.py -q`
Expected: 3 FAIL — the first two on `ImportError: cannot import name 'DroppedEvalMetric'`.

- [ ] **4.3 Add `DroppedEvalMetric`**

Place it immediately before `GbmFitResult` in `modelling.py`:

```python
class DroppedEvalMetric(BaseModel):
    """A declared eval metric the backend could not evaluate (FR-161, OQ-593).

    FR-159's objection is to a spec "reported to the caller as configured" when it
    was not. The cheapest honest answer here is neither to refuse an otherwise-valid fit
    nor to punish a portable spec for one backend's evaluation ordering, but to say so on
    the artifact — so a reader comparing two fits can see why one curve has a series the
    other lacks, instead of inferring a bug.

    `reason` is a closed set with one member because exactly one reason exists today. A
    free-text field would let the second be invented at a call site rather than declared
    in the contract the frontend generates from.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: The declared metric's name, exactly as `eval_metrics` spelled it.
    name: str = Field(min_length=1)
    #: FR-160: LightGBM evaluates builtin metrics before `feval`'s, so a builtin
    #: declared alongside a custom stopping target would take position 0 and drive the
    #: stop. `params["metric"] = "None"` prevents that and drops the builtin with it.
    reason: Literal["builtin_evaluated_before_custom_stopping_metric"]
```

- [ ] **4.4 Add the field and its validator to `GbmFitResult`**

After `library_versions` (:1631):

```python
    #: FR-161. Empty on every fit that evaluated everything it was asked for, which
    #: is all of them but the LightGBM-stopping-on-a-custom-metric case, and on every
    #: artifact written before 2026-08-22.
    dropped_eval_metrics: tuple[DroppedEvalMetric, ...] = ()
```

and, beside the existing validators:

```python
    @model_validator(mode="after")
    def _a_dropped_metric_is_named_once(self) -> GbmFitResult:
        """FR-161: a repeated name is a producer bug, not two facts about the fit."""
        names = [dropped.name for dropped in self.dropped_eval_metrics]
        if len(names) != len(set(names)):
            raise ValueError(
                f"{sorted(names)} contains a duplicate; each dropped metric is named once"
            )
        return self
```

- [ ] **4.5 Export `DroppedEvalMetric`**

Add it to `packages/model-schema/src/model_schema/__init__.py` alongside the other GBM names, keeping the file's existing alphabetical or grouped ordering and its `__all__` entry.

- [ ] **4.6 Run the tests and mypy**

Run: `uv run pytest packages/model-schema/tests/test_dropped_eval_metrics.py -q && uv run mypy`
Expected: 3 PASS, mypy clean.

- [ ] **4.7 Commit**

```bash
git add packages/model-schema/src/model_schema/modelling.py packages/model-schema/src/model_schema/__init__.py packages/model-schema/tests/test_dropped_eval_metrics.py
git commit -m "$(cat <<'EOF'
feat(model-schema): FR-161 — GbmFitResult.dropped_eval_metrics

A declared eval metric a backend could not evaluate is recorded on the fit
rather than silently absent. One reason exists today and the field says which,
from a closed set.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5 — `_fit_lightgbm` reports what it dropped

**Files**
- Modify: `packages/pricing-core/src/pricing_core/modelling/gbm.py` (`_fit_xgboost` :803-932, `_fit_lightgbm` :955-1076, `fit_gbm` :655-700)
- Modify: `packages/pricing-core/tests/test_gbm.py`

**Interfaces**
- Consumes: Task 4's `DroppedEvalMetric`; Task 1's parameter ordering; the existing `_builtin_eval_metric_names(eval_metrics) -> list[str]` (gbm.py:408) and `_is_custom_metric_ref`.
- Produces: both `_fit_*` functions return a **5-tuple** — `tuple[bytes, int, tuple[GbmEvalPoint, ...], dict[str, str], tuple[DroppedEvalMetric, ...]]`. `_fit_xgboost` always returns `()` as the fifth element. `GbmFitResult.dropped_eval_metrics` is populated by `fit_gbm`. **`GbmFit` gains no field** — see planning decision 2.

**Steps**

- [ ] **5.1 Write the failing test**

The existing `test_lightgbm_drops_a_builtin_eval_metric_rather_than_stop_on_it` pins the drop *behaviour*; this pins the *record*. Find it in `test_gbm.py` and place the new test beside it, copying its spec construction verbatim so the two describe the same fit.

```python
@pytest.mark.req("FR-161")
def test_lightgbm_records_the_builtin_eval_metric_it_dropped() -> None:
    """The drop was correct and silent; FR-161 makes it correct and legible.

    LightGBM evaluates builtin metrics before `feval`'s, so a builtin declared alongside
    a custom stopping target would take position 0 and drive the stop — the defect the
    `metric: None` line exists to prevent. Until 2026-08-22 the caller's declared metric
    simply never appeared in the curve, with nothing on the artifact to say why.
    """
    data = _frequency_data()
    spec = _spec(
        "lightgbm",
        eval_metrics=(
            GbmFunctionRef(kind="builtin", name="poisson"),
            GbmFunctionRef(kind="custom", ref=_METRIC_REF),
        ),
        early_stopping=EarlyStoppingSpec(on="holdout", rounds=5, metric=_METRIC_REF),
    )
    fit = fit_gbm(
        data, spec, FACTORS, holdout=_frequency_data(n=2_000, seed=20260823),
        metrics={_METRIC_REF: _metric()},
    )
    assert fit.result.dropped_eval_metrics == (
        DroppedEvalMetric(
            name="poisson", reason="builtin_evaluated_before_custom_stopping_metric"
        ),
    )


@pytest.mark.req("FR-161")
@pytest.mark.parametrize("backend", BACKENDS)
def test_a_fit_that_evaluated_everything_drops_nothing(backend: str) -> None:
    """The control. A non-empty tuple on an ordinary fit would make the field noise, and
    a reader who has seen it fire spuriously once will not trust it when it matters."""
    fit = fit_gbm(_frequency_data(), _spec(backend), FACTORS)
    assert fit.result.dropped_eval_metrics == ()
```

The `early_stopping` construction, the holdout keyword and `EarlyStoppingSpec`'s real field names must be copied from the existing drop test rather than taken from here — that test already builds this exact configuration correctly.

- [ ] **5.2 Run to verify**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -k "records_the_builtin or evaluated_everything" -q`
Expected: the control PASSes (the field defaults to `()`); the record test FAILs on an empty tuple.

- [ ] **5.3 Return the drop from `_fit_lightgbm`**

Change the return annotation (:967) to the 5-tuple. At the top of the function body add:

```python
    dropped: tuple[DroppedEvalMetric, ...] = ()
```

In the `if stopping_on_custom:` arm (:1004-1017), immediately after `params["metric"] = "None"`:

```python
        # FR-161: the builtins suppressed by the line above were *declared*, and a
        # caller who cannot see them in the curve is owed the reason rather than left to
        # infer one. The same list the `else` arm passes to `params["metric"]`.
        dropped = tuple(
            DroppedEvalMetric(
                name=name, reason="builtin_evaluated_before_custom_stopping_metric"
            )
            for name in _builtin_eval_metric_names(spec.eval_metrics)
        )
```

and the return (:1076):

```python
    return payload, best, curve, {"lightgbm": lgb.__version__}, dropped
```

- [ ] **5.4 Return an empty tuple from `_fit_xgboost`**

Change its return annotation (:816) to the same 5-tuple and its return (:932):

```python
    return payload, best + 1, curve, {"xgboost": xgb.__version__}, ()
```

XGBoost drops nothing: `eval_metric` takes the full builtin list and `custom_metric` runs beside it, so both are evaluated. Add a one-line comment above the return saying so, since an unexplained constant `()` reads as a stub.

- [ ] **5.5 Unpack and persist in `fit_gbm`**

Both dispatch calls (:656, :661) gain a fifth name:

```python
        payload, best, curve, versions, dropped = _fit_xgboost(
```
```python
        payload, best, curve, versions, dropped = _fit_lightgbm(
```

and the `GbmFitResult(...)` construction gains, beside `library_versions`:

```python
            dropped_eval_metrics=dropped,
```

Add `DroppedEvalMetric` to gbm.py's `model_schema.modelling` import block.

- [ ] **5.6 Run the new tests, then the full GBM suite**

Run: `uv run pytest packages/pricing-core/tests/test_gbm.py -q`
Expected: all PASS, including the pre-existing `test_lightgbm_drops_a_builtin_eval_metric_rather_than_stop_on_it`, which must be untouched — the drop behaviour has not changed, only its visibility.

- [ ] **5.7 Verify the field survives the backend's persistence path**

Run: `uv run pytest backend/tests -q -k "gbm or model_handler"`
Expected: all PASS with no handler edit. `model_handlers.py:347` reads `fit.result` by attribute and `record_fit` persists the whole result, so the field rides along. **If any backend test fails, stop** — the persistence assumption in this plan's Architecture note is wrong and needs resolving before proceeding.

- [ ] **5.8 Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/gbm.py packages/pricing-core/tests/test_gbm.py
git commit -m "$(cat <<'EOF'
feat(pricing-core): FR-161 — LightGBM records the builtin eval metric it dropped

A builtin declared alongside a custom stopping target is suppressed so it
cannot take position 0 and drive the stop. The drop was correct and silent;
the fit result now names it and says why.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6 — regenerate the contracts

**Files**
- Modify (generated): `docs/contracts/schemas/generated/model.schema.json`, `docs/contracts/schemas/generated/diagnostics.schema.json`, `docs/contracts/openapi/generated.json` — whichever the script actually rewrites.

**Interfaces**
- Consumes: Task 4's `DroppedEvalMetric` and `GbmFitResult.dropped_eval_metrics`.
- Produces: committed contract JSON matching model-schema, so `--check` passes in CI (FR-451).

**Steps**

- [ ] **6.1 Confirm the check currently fails**

Run: `uv run python scripts/generate-contracts.py --check`
Expected: non-zero exit naming the drifted files. **Read the exit code itself**, not a piped tail.

- [ ] **6.2 Regenerate**

Run: `uv run python scripts/generate-contracts.py`

- [ ] **6.3 Read the diff before committing it**

Run: `git diff --stat docs/contracts/ && git diff docs/contracts/ | head -80`
Expected: `DroppedEvalMetric` appears as a new definition with `name` and a single-member `reason` enum, and `dropped_eval_metrics` as an array on the GBM fit result, defaulting to empty. **A generated artifact matching its source proves neither is correct** (CLAUDE.md §13 rule 4) — check the emitted shape against FR-161's words, not only against the Python. Anything else in the diff is unrelated drift and must be understood before it is committed.

- [ ] **6.4 Verify the check now passes**

Run: `uv run python scripts/generate-contracts.py --check`
Expected: exit 0.

- [ ] **6.5 Commit**

```bash
git add docs/contracts/
git commit -m "$(cat <<'EOF'
chore(contracts): regenerate for GbmFitResult.dropped_eval_metrics (FR-161)

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7 — amend the spec

**Files**
- Modify: `docs/specs/02-modelling.md` — FR-111 (:138), FR-207 (:~150), FR-161 (:220), §4.4 common block (:495-510) and its `spec_hash` lineage, §4.8 fit_result examples (:1118-1155)

**Interfaces**
- Consumes: everything Tasks 1–6 built.
- Produces: no code. This is where the slice's findings land, because the spec is what the next stage is built against (CLAUDE.md §14 question 4).

**Steps**

- [ ] **7.1 Amend FR-111 with the dated note that was recorded as written and never was**

Append to the FR-111 row, in the house amendment style (see FR-137 at :192 for the pattern — parenthesised, dated, naming which side was wrong):

```
*(Amended 2026-08-22, WK-661.* **Built for GBMs.** *Until this date `fit_gbm` accepted `spec.weight` and never read it, while `fit_glm`, `fit_ebm` and `compute_diagnostics` all honoured it — so a severity GBM declaring this requirement's own default fitted unweighted, and FR-184 then labelled its diagnostics claim-count-weighted on the strength of a spec the fit had ignored: the label true of the metric and false of the model. The roadmap's EBM slice record states a dated note to this effect was written on 2026-08-21; no such note existed — `git log -S` shows the phrase entered the repository only in `c2c54a6`, and only in `docs/roadmap.md`. FR-207's obligation is discharged here by building the field rather than by staging it: both backends now weight the training and holdout datasets, and the custom objective and custom eval metric paths — whose `get_weight()` readbacks had existed unfed since the GBM slice — receive the declared column. The interpretation change moves `spec_hash` `v9` to `v10` (FR-206).)*
```

- [ ] **7.2 Amend FR-161 — built, and where the field actually lives**

Append to the FR-161 row:

```
*(Amended 2026-08-22, WK-661, building this requirement.* **Built.** *`DroppedEvalMetric` (`name`, and `reason` from a closed set whose one member is `builtin_evaluated_before_custom_stopping_metric`) and `GbmFitResult.dropped_eval_metrics` carry it; `_fit_lightgbm` populates it from the same `_builtin_eval_metric_names` list the non-stopping arm passes to `params["metric"]`, and `_fit_xgboost` returns empty because it evaluates both lists. One correction to the wording above: the field is on `GbmFitResult` and **not** additionally on `GbmFit`. `GbmFit.result` is the `GbmFitResult`, so callers reach it as `fit.result.dropped_eval_metrics`; a second copy on the wrapper would be a field that can disagree with itself. `eval_curve` sits on `GbmFit` for the opposite reason — FR-174 makes it a diagnostic and it is deliberately not persisted — which is what made "both" look symmetric when this requirement was written.)*
```

- [ ] **7.3 Update FR-207's staged list**

FR-207 enumerates the fields that have gone live under the staging rule, numbered in order. Read the row's current tail, find the highest ordinal in use, and append `dropped_eval_metrics` as the next one with the date `2026-08-22` and its requirement (FR-161), matching the existing sentences' construction exactly.

- [ ] **7.4 Add `dropped_eval_metrics` to §4.8's fit_result example**

The §4.8 GBM `fit_result` example (:1118-1155) shows the persisted shape a reader copies. Add the field to it. Show it as `[]` in the ordinary example, and if §4.8 carries a second GBM example with early stopping, show the populated form there:

```json
"dropped_eval_metrics": [
  {"name": "poisson", "reason": "builtin_evaluated_before_custom_stopping_metric"}
]
```

- [ ] **7.5 Bring §4.4's `spec_hash` lineage up to date**

§4.4 records the `spec_hash` version lineage and stopped short of the backend's comment block: the **v6 and v7 transitions were never recorded there**. Add all three in one pass, matching the section's existing sentence shape:

- **v6 → v7** (2026-08-21, FR-114): `tweedie` joined the payload — a power estimated over a grid is a different fitted question than a fixed one.
- **v7 → v8** (2026-08-21, FR-116): `offset_model_ref` joined the payload — the offset a fit names is part of what the fit means.
- **v9 → v10** (2026-08-22, FR-111): the first bump for an interpretation change rather than a payload one — `weight` was always in the payload; `fit_gbm` began honouring it.

Confirm §4.4 already records v8 → v9 (EbmSpec, FR-140) before writing; if it does not, add that too.

- [ ] **7.6 Run the docs audit**

Run: `python3 scripts/audit-docs.py`
Expected: exit 0. Watch for the anchor-phrase trap — a bolded audit-docs anchor phrase inside an FR row breaks check 10. If an amendment trips it, rephrase the amendment; do not weaken the check.

- [ ] **7.7 Commit**

```bash
git add docs/specs/02-modelling.md
git commit -m "$(cat <<'EOF'
docs(spec): FR-111/207/161 — the GBM weighting gap and the drop record

FR-111 gains the dated note the roadmap claimed existed and did not,
discharged by building rather than staging. FR-161 is marked built, with
a correction: the field is on GbmFitResult only, reachable as fit.result.
Section 4.4's spec_hash lineage catches up on v6, v7 and v10.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8 — roadmap record, and the two claims it gets wrong

**Files**
- Modify: `docs/roadmap.md` (the WK-661 slice records around :2784-2830, the deferral paragraph at :2811-2812, the WK-661 row at :2882)

**Interfaces**
- Consumes: Tasks 1–7.
- Produces: the slice's closure record, in the same shape as the EBM record above it.

**Steps**

- [ ] **8.1 Write the slice record**

Append a new record after the EBM slice's, following its structure exactly (heading, the table of what was built, the "Recorded, not built, with owners" paragraph). It must state:

- **Built:** `spec.weight` honoured by both GBM backends on training and holdout datasets, and reaching the custom objective and custom eval metric paths; `GbmFitResult.dropped_eval_metrics` with `DroppedEvalMetric`; `spec_hash` v9 → v10.
- **The measurement that matters:** an unweighted vs claim-count-weighted Gamma severity fit over the same book, 5.0 against 1.8 — cite the test by name rather than describing it.
- **What this slice did not do**, with owners: the eleven unevidenced `NFR-MODEL` requirements (four buckets, unowned by this slice); FR-115's remainder (a bare non-`LinAlgError` glum `ValueError` reaches the job unwrapped); the `06` §3.3 custom-metric `EVIDENCE_FLOOR` gap (spec change first, then code, in that order); FR-386; FR-117(c), sequenced behind (a); the `interactions=2` EBM triples, which **no workstream has ever been named for** — itself an FR-207 defect and worth stating as one; and the constraint-level contract-drift guard.

- [ ] **8.2 Correct the false deferral claim at :2811-2812**

The EBM slice record says the weight gap has a *"dated note 2026-08-21, owner WK-661"*. Do not delete the sentence — amend it in place, so the record of what was believed survives (§0):

```
**Recorded, not built, with owners.** `fit_gbm` ignores `spec.weight` — verified, no
reference in `gbm.py`; dated note 2026-08-21, owner WK-661. *(Corrected 2026-08-22: the note
was never written. `git log -S "dated note 2026-08-21"` shows the phrase entering the
repository only in `c2c54a6`, and only in this file — so FR-207's obligation was
recorded as discharged while nothing in `02-modelling.md` said the field was unbuilt. The
gap is closed by building it rather than by writing the note; FR-111 carries the
amendment.)*
```

Apply the same treatment to the FR-161 sentence that follows it, marking it delivered with this slice.

- [ ] **8.3 Correct the WK-661 row's requirement count**

`docs/roadmap.md:2882` reads "All 78 `MODEL` requirements — the largest single workstream". The spec-derived count is **124**. Before editing, re-derive it rather than trusting this plan:

Run: `uv run python scripts/scope-audit.py MODEL`
Then set the row to the derived number, with a parenthetical noting the count was 78 when the row was written and that requirement IDs only ever accumulate (§5).

- [ ] **8.4 Re-run the audit**

Run: `python3 scripts/audit-docs.py`
Expected: exit 0.

- [ ] **8.5 Commit**

```bash
git add docs/roadmap.md
git commit -m "$(cat <<'EOF'
docs(roadmap): WK-661 slice record — GBM weights and dropped eval metrics

Records what was built, and corrects two claims: the FR-207 note for the
weight gap was recorded as written and never was, and the WK-661 row's "78 MODEL
requirements" is a count from before the requirement set grew to its current
size.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 9 — the full gate, both halves

**Files** — none modified unless the gate finds something.

**Interfaces**
- Consumes: Tasks 1–8.
- Produces: a per-command exit-code record proving the slice is reproducible outside CI.

**Steps**

- [ ] **9.1 Run the Python and docs half**

Delegate to the `gate-runner` agent, which runs both halves and returns a per-command exit-code table with only the failing excerpt — the raw output is hundreds of lines that would otherwise sit in context for the rest of the session. If running inline instead, read **each command's own exit code**; `cmd | tail -1 && echo ok` reports `tail`'s and has produced a false clean here before:

```bash
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
```

- [ ] **9.2 Run the frontend half**

The contract changed, so the generated client changes with it. This is not optional — a "gate" covering only Python has been green here while the frontend was red.

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

- [ ] **9.3 Confirm the requirement coverage moved**

Run: `uv run python scripts/scope-audit.py MODEL`
Expected: FR-161 now evidenced; the unevidenced FR count drops from 6 to 5, all five gated (FR-MODEL-6, 40, 82, 110, 112). FR-111 was already green and stays green — but now for a reason that includes the GBM path, which is the point of the slice and worth stating in the closing summary rather than letting the unchanged number imply nothing happened.

- [ ] **9.4 Confirm the tree is clean and the demo guide still derives**

```bash
uv run pytest backend/tests/test_demo_guide.py -q
git status --porcelain
```
Expected: PASS, and empty output from `git status`.

- [ ] **9.5 Report**

Summarise: the exit-code table from 9.1 and 9.2; the severity measurement (5.0 unweighted against 1.8 claim-count-weighted); the `spec_hash` v9 → v10 invalidation and that every `v9:` row is findable with `LIKE 'v9:%'`; the coverage change; and — explicitly — the list from step 8.1 of what this slice did **not** do, with owners. No PR, no merge.

---

## Self-Review

**Spec coverage.** FR-111 → Tasks 1, 2, 7. FR-184 → Task 1 (test 1.9 asserts the number the label describes). FR-155 → Task 2.3. FR-161 → Tasks 4, 5, 6, 7. FR-206 → Task 3. FR-207 → Task 7.3. FR-159/160 are the rationale rather than deliverables and are cited in the code comments and spec amendments, not implemented. **Deliberately not covered, with owners recorded in Task 8.1:** the eleven `NFR-MODEL` requirements, FR-115's remainder, the `06` §3.3 `EVIDENCE_FLOOR` gap, FR-386, FR-117(c), the `interactions=2` triples, and the contract-drift guard.

**Placeholder scan.** No TBD, no "add appropriate error handling", no "similar to Task N" — Task 5's XGBoost arm repeats the full return line rather than referring back to Task 1. Four steps deliberately say *copy the call shape from the adjacent existing test* (1.9, 2.1, 2.3, 5.1) rather than inventing constructor arguments for `predict_gbm`, `_custom_spec`, `GbmFunctionRef` and `EarlyStoppingSpec`; those files are open to the implementer and a guessed keyword that fails at collection time is worse than an instruction to read the neighbour. Every one names the file and the line range to copy from.

**Type consistency.** `_weights(data: pl.DataFrame, weight: WeightSpec) -> np.ndarray | None` is spelled identically in Tasks 1.4, 1.5 and 1.7. The `valid` 4-tuple `tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None] | None` is identical at all four declaration sites (1.5, 1.6, 1.7). The `weights` parameter sits immediately after `base_margin` in both `_fit_*` signatures and in both `fit_gbm` dispatch calls. The `_fit_*` return type is a 4-tuple through Tasks 1–4 and a 5-tuple from Task 5, changed in both functions and both call sites in the same task. `DroppedEvalMetric(name=..., reason="builtin_evaluated_before_custom_stopping_metric")` is spelled identically in Tasks 4.3, 4.1, 5.1, 5.3 and 7.4. `dropped_eval_metrics` is on `GbmFitResult` only, consistently, in Tasks 4, 5, 6 and 7.
