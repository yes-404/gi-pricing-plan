---
id: PL-741
family: plan
kind: leaf
title: EBM models via `interpret-core` — Implementation Plan (WK-661, FR-140)
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-21
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-21-ebm.md
---

# EBM models via `interpret-core` — Implementation Plan (WK-661, FR-140)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans — this plan is a sequence of small, individually verifiable tasks; follow it strictly, do not "improve" the shape of the data, and do not skip the gate steps. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal.** FR-140: fit an EBM (`interpret-core` 0.7.8) through the existing `model.fit` Job, where the fit result *is* the model — term shape functions exported verbatim as additive lookup tables (ADR-705 data, never a pickle), stored as JSONB on the model row, scorable by a process that never imports `interpret` (ADR-703), and transparent by construction (exported directly as tables, no approximation, still carrying the fidelity/diagnostic sections in the same contract shape).

**Architecture.** Third arm of the `ModelSpec`/`FitResult` discriminated unions (on `model_type`); `fit_ebm` in a new `packages/pricing-core/src/pricing_core/modelling/ebm.py`; `predict_ebm` in `predict.py` (the no-fitting-stack module); `compute_ebm_diagnostics` in `diagnostics.py` reusing the shared `_partition`; `build_ebm_shape_functions` in `transparency.py`; backend `_fit`/`_transparency` dispatch gains the EBM arm; contracts regenerated from the types (ADR-704). `spec_hash` moves 8→9; one new error code, `EBM_MONOTONE_CONSTRAINT_INCOMPLETE`, registered in the same commit that can raise it.

**Tech Stack.** Python 3.12+; Pydantic v2 (model-schema); `interpret-core==0.7.8` (pinned exact, NOT the `interpret` metapackage — it forces all extras: an 814 MB venv; bare interpret-core adds numpy+pandas+joblib, ≈115 MB incremental, with scikit-learn/scipy already present via glum); numpy/polars as today; pytest with `@pytest.mark.req`; no pandas in repo code (pandas arrives only as interpret-core's own dependency — an unavoidable library boundary); no new backend dependency; no alembic revision (EBM spec/fit/artifact ride existing JSONB columns).

**Spec.** `docs/specs/02-modelling.md` §3.6/§4.4/§4.8/§4.9/§5.1/§5.2/§8 amended in the first task (spec-first per `CLAUDE.md` §0). The EBM arm's objective vocabulary is `rmse`/`mae` (interpret's regression objectives, identity link); §7's actuarial families (poisson/gamma/tweedie/…) and binomial `log_loss` are **refused by name** under FR-207's staging rule with a dated note; custom objectives do not apply to EBM (`ObjectiveBackend` has no EBM member by design); offsets stay GLM-only (`EbmSpec` refuses every non-`none` offset at the type).

---

## Slice context — verified at planning time, 2026-08-21

Every anchor below was read at planning time; none is a guess:

- `packages/model-schema/src/model_schema/modelling.py`: `WeightSpec` (:720-732, kind `"none"|"column"` + column); `ModelSpecCommon` (:804-833, `model_family_slug`, `dataset_version_id`, `split_ref`, `peril`, `response`, `response_column`, `offset: OffsetSpec = OffsetSpec()`, `weight: WeightSpec = WeightSpec()`, `factors`, `loss_treatment`, `seed: int = 0`); `GlmSpec` (:1000); `GbmSpec` (:1292); unions `ModelSpec = Annotated[GlmSpec | GbmSpec, Field(discriminator="model_type")]` (:1603) and `FitResult` (:1608); `Model._the_fit_matches_the_specification` (:1745) compares `fit_result.model_type != self.spec.model_type` — works for EBM unchanged.
- `packages/model-schema/src/model_schema/transparency.py`: `TransparencyKind.EBM_SHAPE_FUNCTIONS = "ebm_shape_functions"` (:57, docstring "declared and produced by nothing"); `TransparencyArtifact` (:164-208) with `glm_approximation`/`shap_summary`, `kinds` property (:189-197), `_an_artifact_explains_something` (:199-208).
- `docs/contracts/schemas/transparency-artifact.schema.json` (:68-72) **already declares** `ebm_shape_functions {terms_blob: string}` — the type/schema divergence this slice reconciles (the hand-written schema ran ahead of the pydantic type; regeneration makes it type-derived).
- `packages/pricing-core/src/pricing_core/modelling/`: `glm.py` — `GlmFitError` (:84-94), the weight rule at :583-584 (`if spec.weight.kind == "column": weights = data[str(spec.weight.column)].cast(pl.Float64).to_numpy()`); `gbm.py` — `GbmFitError` (:140-151), `GBM_NO_FEATURES` raised at :323, `"seed": spec.seed` at :828 and :972, **no reference to `spec.weight` anywhere** (fit_gbm ignores weights — recorded, not built); `predict.py` — `score_fitted` (:334-380) dispatching `isinstance(fit, GbmFitResult)` else GLM asserts, `PredictionError` (:51); `diagnostics.py` — `unit_deviance` gaussian valid (:160-162), `_partition` (:328-338, takes `mu` + `family` + `power`), `_weights` (:122-128), `_family_of(fit, spec)` (:671-685, GbmSpec → `objective_family`, else GLM asserts), `backtest_model` (:688-753), `compute_gbm_diagnostics` (:908-1031); `transparency.py` — `build_glm_approximation` (:124), `fidelity_statement` (:388-427).
- `backend/src/app/worker/model_handlers.py`: `_fit` (:163-483) — locals `booster: bytes | None = None`, `covariance: bytes | None = None`, `glm_cv`, `eval_curve: tuple = ()`, `result: FitResult` are pre-initialised **before** the dispatch, so an EBM arm that sets only `result` leaves `store()` unchanged and safe (`if booster is not None` / `if covariance is not None` guards); dispatch `if isinstance(spec, GbmSpec): … else: fit_glm(...)` (:330-365); `except (GbmFitError, GlmFitError)` (:366-372); diagnostics dispatch (:385-410) with the else-guard's message ending "`ebm` is declared by `CLAUDE.md` §7 and built by no slice."; `store()` (:453-481) persists blob bytes then `record_fit(fit_result=result, diagnostics=diagnostics, …)`.
- `backend/src/app/platform/transparency.py`: `fitted_gbm_or_refuse` (:121-151) refuses only not-fitted (`MODEL_NOT_FITTED`) and GLM (`MODEL_ALREADY_TRANSPARENT`) — **an EBM already passes through it unchanged**; `record_transparency` (:46-84) builds with `id=new_uuid7()` (imported from model_schema, :23) and audits `kinds`; call sites `model_handlers.py:751`, `api/models.py:856`, `test_model_jobs_gbm.py:573`.
- `backend/src/app/platform/modelling.py`: `SPEC_HASH_VERSION: Final = 8` (:132); `spec_hash` (:135-153) canonicalises `spec.model_dump(mode="json")` with `sort_keys` — **new fields join the payload with no code change; only the version tag moves**.
- `backend/src/app/platform/model_specs.py`: `_objective_problems` (:323-359) returns `[]` for non-GBM specs; `complexity_or_refuse` is model-type-agnostic — **an `EbmSpec` passes `validate_spec` and `reserve_model` by construction**.
- `backend/src/app/errors.py`: `MODELLING_ERROR_CODES` frozenset (:100-209), dated comments per slice.
- Tests: `packages/model-schema/tests/test_gbm_spec.py` — `_spec()` (:39-58), `test_an_unknown_model_type_is_refused_by_the_discriminator` (:267-276, payload `model_type: "ebm"` expecting `ValidationError`, `match="model_type"` — **must flip in Task 2**), `test_a_model_cannot_hold_a_fit_from_another_model_type` (:280); `backend/tests/test_spec_hash.py` — `test_every_code_the_fit_path_can_raise_is_registered` (:107-145, AST-scan, **parametrised over `("pricing_core.modelling.glm", "GlmFitError")` and `("pricing_core.modelling.gbm", "GbmFitError")` — the ebm row is mandatory, no auto-discovery**), `test_the_algorithm_version_moved_with_the_new_field` (:163-184, asserts `== 8` and `v8:sha256:`); `backend/tests/test_model_jobs.py` helpers `_actuary`/`_dataset`/`_factor`/`_split`/`_spec`/`_validated_version` (:150-267); `backend/tests/test_model_jobs_gbm.py` `_gbm_spec`/`_fitted_gbm` (:71-114, `reserve_model` → `job_service.submit(JobKind.MODEL_FIT, …)` → `execute_job`); `backend/tests/test_glm_approximation_model.py` `_transparency_job` (:53-73) and `_transparency_refusal` (:76-112); `packages/pricing-core/tests/test_scoring_without_the_fitting_stack.py` — `BLOCKED = {"glum", "sklearn", "celery", "dagster"}` (:43), import-blocker + child-process pattern.
- Root invariants: `tests/test_repository_invariants.py::test_every_error_code_pricing_core_raises_is_registered_and_declared` (:196-265) AST-scans **every** `*.py` in `pricing_core/modelling` (a new `ebm.py` is auto-scanned), derives raisers from class names ending `Error`, checks raised ⊆ `MODELLING_ERROR_CODES` and raised ⊆ §5.1's catalogue paragraph — the paragraph starts at "**Error codes owned by this module:**" (:1630) and ends with `METRIC_NOT_FITTABLE.` (:1651); §5.1 may declare **ahead** of the code, the registry may not lag.
- Test counts (grep-counted, function-level): model-schema 204, pricing-core 445, backend 657, root invariants 14. CI gate: `uv sync --all-packages --dev`; `uv run ruff check .`; `uv run mypy`; `uv run lint-imports`; `uv run pytest -q`; `uv run python scripts/generate-contracts.py --check`; `uv run python scripts/req-coverage.py`.

**Spike facts (interpret-core 0.7.8, verified in a live venv by the main thread 2026-08-21; encode without re-verification):** fit API `ExplainableBoostingRegressor.fit(X, y, sample_weight=None)` with numpy arrays (string object arrays for categoricals); `random_state: int | None = 42` (deterministic — same seed → byte-identical `term_scores_`; **`intercept_` is data-determined and equal across seeds**, so a cross-seed test must compare term scores, not the intercept); `max_bins` (default 1024); `interactions` (ints 0/1/2 = univariate/pairs/triples); `max_rounds` (default 50000); `early_stopping_rounds` (default 100); `monotone_constraints` (exact spelling; a dict over **all** features; omission raises `ValueError`; numpy-input default feature names are `"feature 0"`, `"feature 1"`, …); objectives only `rmse`/`mae`, `link_ == "identity"`. Exports: `term_scores_` (per term: 1-D for univariate, 2-D grid for interactions), `bins_` (per FEATURE: numeric = `(1, n_cuts+1)` cut array; categorical = `(1,)` object dict `{level: 1-based index}`), `term_features_`, `term_names_`, `standard_deviations_`, `intercept_`, `bin_weights_` (zeros mark the base/trailing slots — the real-bin filter), `best_iteration_`. **Index rule:** numeric score index = `np.searchsorted(cuts, v, side="right") + 1` (index 0 is the unused base slot; above the last cut lands in the last populated bin); categorical = the 1-based dict value. **Slot layout (load-bearing):** with `c` cuts a numeric term has `c + 3` slots — 1 base + (`c` + 1) populated + 1 missing-value trailing slot (61 cuts → 64 slots, 62 nonzero weights); a categorical term with `l` levels has `l + 2` slots (1 base + `l` levels + 1 trailing). Identity verified: `predict(X) == intercept_ + eval_terms(X).sum(axis=1)` (identity link). **No `to_jsonable()`** (beta-warned — the artifact builds its own immutable JSON from the arrays), **no `predict_and_contrib`/`get_term_shapes`** in 0.7.8. Timing: 50k×9, `max_bins=64`, `interactions=0` → 10.0 s; `interactions=1` → 14.8 s; linear extrapolation to freMTPL2 (678 013 rows) ≈ 135–200 s (a sanity bound, not an NFR measurement).

## Global Constraints

- **Read-only planning is over; the executor edits only the files each task names.** No file is touched outside the listed paths.
- **Spec-first:** `CLAUDE.md` §0 — the spec amendment (Task 1) commits before any code.
- **One commit per task** (or per step where a task says so), Conventional Commits with the `Co-Authored-By: Claude <noreply@anthropic.com>` trailer on every commit; no PR, no merge — the slice closes with the roadmap record and the full gate, both halves.
- **Negative test before positive** wherever a refusal exists; every new/edited test carries `@pytest.mark.req("FR-…")`; `scripts/req-coverage.py` reports drift.
- **Same-commit error registration:** any code `pricing-core` can raise must be in `MODELLING_ERROR_CODES` and in §5.1's catalogue in the same commit (the AST-scan invariant enforces both; §5.1 may declare ahead, the registry may not lag).
- **ADR-703:** `pricing-core` does no I/O and resolves no refs; **ADR-705:** fit results are data, never pickles. `interpret` is imported at call-site scope inside `fit_ebm`; the scoring path must not grow an import of the fitting stack (`test_scoring_without_the_fitting_stack.py` blocks `glum`/`sklearn`/`celery`/`dagster` and gains `interpret`).
- **Contracts follow the code** (ADR-704): `scripts/generate-contracts.py` after every model-schema change that alters a generated shape; `--check` in the final gate.
- No pandas in repo code; ruff line length 100; `mypy --strict`; `lint-imports` green; no alembic revision.
- Every task ends with its commit and a green run of the tests it touched, unless the task says otherwise.

---

## Task 0 — Decisions and scope (settled; encode, do not reopen)

Task 0 produces **no commit**; it is the record of decisions this plan encodes. The executor must not re-litigate them.

**0.1 Dependency: `interpret-core==0.7.8` in `packages/pricing-core` (not `interpret`).** The metapackage pulls notebooks/visualisation extras; only the core regressor is needed. ~115 MB incremental; `scikit-learn>=1.5,<2` is satisfied by the workspace's sklearn 1.9.0 (spike-verified). Rationale recorded in Task 6's commit message and in the Task 14 slice record: one requirement (FR-140), one model type, pin exact.

**0.2 Objective vocabulary.** EBM objectives are `rmse` and `mae` only (identity link — spike: `link_ == "identity"`). §7's actuarial families (`poisson`, `gamma`, `tweedie`, …) and binomial `log_loss` are **refused by name** at the type, under FR-207's staging rule, with a dated note in the Task 1 amendment. **No `EBM_OBJECTIVE_UNSUPPORTED` error code is created** — the `Literal` refuses at spec construction, exactly as `GlmSpec.family`'s literal needs no runtime code; a refusal the type performs needs no platform error. Only **one** new code exists: `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` (Task 11).

**0.3 Custom objectives do not apply to EBM.** `ObjectiveBackend` (`packages/model-schema/src/model_schema/objectives.py:101`) has members `XGBOOST`, `LIGHTGBM`, `GLM` and no EBM member — correct as-is; recorded in the Task 14 slice record, no code change.

**0.4 Weights.** `WeightSpec` already lives on `ModelSpecCommon` (:829). `fit_ebm` honors `spec.weight.kind == "column"` identically to `fit_glm` (:583-584) via `sample_weight`. **Recorded, not built:** `fit_gbm` ignores `spec.weight` (verified — no reference in `gbm.py`); that gap keeps its own note in the Task 14 record.

**0.5 Seed.** `ModelSpecCommon.seed` (default 0) is the effective seed — it is what `spec_hash` pins, and `fit_glm`/`fit_gbm` both draw on it. `fit_ebm(..., seed: int = 0)` mirrors `fit_glm`'s vestigial kwarg for call-site symmetry (backend passes `seed=spec.seed` per `model_handlers.py:346`); the estimator gets `random_state=spec.seed`. The spec's seed, not the kwarg, is the reproducibility source.

**0.6 Storage: JSONB, not blob.** `EbmFitResult` is a JSONB payload on the model row (the row's `fit_result` column is already JSONB). Size argument: at the default `max_bins=64`, a numeric univariate term holds 1 + (63+1) + 1 = 66 floats → 9 features ≈ 5 KB. `max_bins=1024` with `interactions=0` → ≤1,027 floats/term ≈ 75 KB total — fine. `interactions>0` at 1024 bins is 1024² ≈ 1 M cells ≈ 8 MB **per pair** — so the spec validator refuses `interactions > 0 and max_bins > 256` (256² = 65,536 cells ≈ 0.5 MB per pair, bounded by construction). `EbmTerm.bin_weights` arrays are stored precisely so the real-bin mask and the complexity count survive after the estimator is gone (ADR-703: `pricing-core` returns data; the estimator is discarded at the end of `fit_ebm`).

**0.7 Transparency: exact export, never approximation.** `build_ebm_shape_functions(result)` serialises the artifact's own tables verbatim into the `terms_blob` JSON document — the tables *are* the model, so there is no fidelity loss to measure. The `fidelity_statement` is exact-by-construction prose; `monotonicity_verified` is `None` when the spec declares no constraints, else checked from the exported tables in the declared directions (FR-174 semantics: taken from the evidence, not recomputed differently). No surrogate model is reserved (no `approximates_model_id`), no sample, no scoring pass.

**0.8 Diagnostics: the universal path with family "gaussian".** `compute_ebm_diagnostics` reuses `_partition` (FR-171's "all model types" taken literally) with `family="gaussian"` (identity link; gaussian is valid in `unit_deviance`, `diagnostics.py:160-162`); complexity `parameter_count` = total real bins across terms (`bin_weights != 0`); `glm=None`, `gbm=None` — the `Diagnostics` model allows both. No eval curve, no importances, no partial dependence, no permutation importance — an EBM's dependence structure *is* the exported tables, and duplicating it as a diagnostic would be a second statement of one fact.

**0.9 `fitted_gbm_or_refuse` keeps its name.** It already admits EBM (it refuses only not-fitted and `model_type == "glm"`). Renaming would churn 4 files for cosmetics; Task 12 amends its docstring to state the EBM admission. The `_transparency` handler's *own* `MODEL_TYPE_UNSUPPORTED` guard (:756-762) is where the EBM branch goes.

**0.10 Offsets stay GLM-only.** `EbmSpec` inherits `OffsetSpec` from `ModelSpecCommon`; an `EbmSpec` with `offset.kind != "none"` is refused by name (validator, Task 2) — `interpret` has no offset path and inventing one would be a silent model change.

**0.11 Interactions are pairs at most.** `interactions` is limited to 0..1 (univariate / all pairs). `interactions=2` (triples) is **declared-and-unbuilt** under FR-207: `EbmTerm`'s score grids are 2-D, and a triple grid at even 64 bins is 262k cells with a cubic growth envelope the JSONB storage argument cannot bound (main-thread review correction, 2026-08-21). The dated note in Task 1 says so; the validator refuses `2` by name.

**0.12 FR-115 correction (delivered, roadmap stale).** Markers exist at `packages/pricing-core/tests/test_glm.py:134,:429` and `backend/tests/test_spec_hash.py:92,:107`; `GLM_SEPARATION_DETECTED` is registered and declared. Roadmap lines :2598 and :2773 ("FR-115 remains unbuilt" / "FR-115's fit-error surfacing remains unbuilt") are **stale** and corrected in Task 14. The remainder — bare non-`LinAlgError` `ValueError`s from glum still unwrapped — is recorded as unbuilt, owner WK-661, in the same correction.

**0.13 FR-161 (dropped eval metric recorded on the fit).** Owed by WK-661 before close, **not this slice** — verdict recorded in Task 14 with owner WK-661 standing. No code here.

**0.14 FR-173 (diagnostics contract divergence).** Delivered — the pin was deleted and `diagnostics` joined the compared slugs — but no `@pytest.mark.req("FR-173")` marker exists anywhere (grep-verified). **Recommendation: YES** — Task 14b adds the one-line marker on `backend/tests/test_contracts.py:554` (`test_every_eligible_schema_is_compared`), its own commit. `req-coverage` then shows FR-173 marked.

**0.15 NFR gap (NFR-482).** Recorded as-is at `roadmap.md:2579`: the export/import round-trip NFR remains unevidenced for the suite; this slice's EBM round-trip tests are evidence for the EBM artifact only, not the general NFR — the record says so rather than claiming closure.

**0.16 Interpret-internals facts the executor cannot re-derive from the repo** (from the spike): `max_bins` must be a power of two within [16, 32768]; `max_rounds` default 50000; `monotone_constraints` keys for numpy input are interpret's default feature names (`"feature 0"`, `"feature 1"`, …). The spec validator encodes the first two (Task 2); the fit builds the key dict accordingly (Task 6) — if a pinned interpret version's convention ever differs, the Task 6 pre-check and backstop fail loudly at fit time and the fix is one dict comprehension, never a weakened test.

---

## Task 1 — Spec amendment (spec-first, docs only)

**Files:** `docs/specs/02-modelling.md`; `docs/roadmap.md` (one line only, below).

**Interfaces added to the spec (§5.2, mirroring the existing rows at :1804-1873):**

```
# pricing_core/modelling/ebm.py
def fit_ebm(data: pl.DataFrame, spec: EbmSpec, factors: Sequence[Factor], *,
            seed: int = 0,
            bandings: Mapping[UUID, Banding] | None = None,
            groupings: Mapping[UUID, Grouping] | None = None,
            progress: ProgressCallback | None = None) -> EbmFitResult

# pricing_core/modelling/predict.py
def predict_ebm(fit: EbmFitResult, data: pl.DataFrame, factors: Sequence[Factor], *,
                bandings: Mapping[UUID, Banding] | None = None,
                groupings: Mapping[UUID, Grouping] | None = None) -> NDArray[float64]

# pricing_core/modelling/diagnostics.py
def compute_ebm_diagnostics(result: EbmFitResult, spec: EbmSpec, factors: Sequence[Factor], *,
                            train: pl.DataFrame, holdout: pl.DataFrame,
                            bandings=None, groupings=None,
                            max_factor_count: int | None = None,
                            min_exposure_per_parameter: float | None = None,
                            progress: ProgressCallback | None = None) -> DiagnosticsResult

# pricing_core/modelling/transparency.py
def build_ebm_shape_functions(result: EbmFitResult) -> EbmShapeFunctions
def ebm_fidelity_statement() -> str
def ebm_monotonicity_verified(result: EbmFitResult, spec: EbmSpec) -> bool | None
```

**Steps:**

- [ ] 1.1 **§4.4** — add an `EbmSpec` block after the `GbmSpec` block (~:607): fields `model_type: "ebm"`, `objective: "rmse" | "mae"` (default `rmse`), `interactions: int 0..1` (default 0; `2` — triples — declared-and-unbuilt, FR-207), `max_bins: int` (default 64, power of two in [16, 32768]), `max_rounds: int` (default 50000), `monotone_constraints: dict[str, int] | None` (values in {-1, 0, 1}; coverage of every factor checked at fit time, not here — factor slugs resolve at fit time); common block inherited (factors, split, response, weight, seed, loss treatment). Dated note (2026-08-21, FR-207): §7's families and binomial `log_loss` are **declared-and-refused by name** as `objective` values; custom objectives do not apply to EBM; `offset` kinds other than `none` are refused by name (offsets stay GLM-only); FR-206: the EBM fields join the `spec_hash` payload and the tag moves 8→9.
- [ ] 1.2 **§4.8** — add the `EbmFitResult` block: `model_type: "ebm"`, `objective`, `link: "identity"`, `intercept`, `feature_order`, per-feature `bins` (numeric `cuts` or categorical `levels`, with the index rule `searchsorted(cuts, v, side="right") + 1`, index 0 the unused base slot), `terms` (per-term `term_features`/`term_name`/`scores`/`standard_deviations`/`bin_weights`), `best_iteration`, `rows`, `fit_seconds`, `library_versions`. State: **the fit result IS the model** — additive lookups, no blob, no estimator, ADR-705; scoring reproduces `intercept + Σ term scores`.
- [ ] 1.3 **§4.9 / §3.6** — `TransparencyArtifact` gains the `ebm_shape_functions` block (`terms_blob: str`), the third kind, and the reconciliation note: the contract schema declared this block before the type did; the EBM slice aligns them (the type becomes the source). FR-140's requirement text stays as the contract: transparent by construction, same fidelity/diagnostic shape.
- [ ] 1.4 **§5.1 catalogue** — append `` `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` `` to the existing catalogue **paragraph** (it ends ``…`METRIC_NOT_FITTABLE`.`` at :1651 — insert before the full stop, backticked, so the AST-scan regex sees it) plus a dated blockquote: "Added 2026-08-21 (WK-661, the EBM slice). It refuses an EBM fit whose `monotone_constraints` name a slug that is not among the fitted factors, or declare a direction on a categorical (non-ordinal) feature — `interpret` itself raises a bare `ValueError` for the second and would abort the process; named here so the refusal arrives as a code, not a stack trace."
- [ ] 1.5 **§8 tech-deps** — the `interpret (EBM)` row (:2177): mark resolved with pin `interpret-core==0.7.8`, installed with the EBM slice.
- [ ] 1.6 **roadmap.md :2572** — the WK-661 outstanding row 5: append "*(2026-08-21: delivered by the EBM slice — see the slice record.)*" (full record in Task 14). No pipes inside the cell (audit-docs counts table cells).
- [ ] 1.7 §4.4 model_type vocabulary — already `"glm | xgboost | lightgbm | ebm"` (:509); no change.

**Verification:**

```bash
git diff --stat                      # 02-modelling.md + roadmap.md only
uv run pytest -q tests/test_repository_invariants.py      # 14 passed — catalogue may run ahead of code
git add docs/specs/02-modelling.md docs/roadmap.md
git commit -m "docs(02): declare the EBM arm of ModelSpec and its fit/transparency shapes (FR-140)"
```

**Expected: 14 passed, 0 failed.** Note: `test_every_error_code_pricing_core_raises_is_registered_and_declared` stays green — it checks raised ⊆ declared, and nothing raises `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` yet.

---

## Task 2 — `EbmSpec` + validators (model-schema)

**Files:** `packages/model-schema/src/model_schema/modelling.py`; new `packages/model-schema/tests/test_ebm_spec.py`; `packages/model-schema/tests/test_gbm_spec.py` (flip one test).

**Interface** (placed after `GbmSpec` ~:1292; union at :1603 gains the arm):

```python
class EbmSpec(ModelSpecCommon):
    """`02` §4.4's EBM arm (FR-140): additive lookups, transparent by construction."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_type: Literal["ebm"] = "ebm"
    #: The only objectives `interpret`'s regressor exposes, both with an identity link.
    #: §7's families (poisson, gamma, tweedie, ...) and binomial `log_loss` are refused
    #: by name here, under FR-207's staging rule (dated note in `02` §4.4).
    objective: Literal["rmse", "mae"] = "rmse"
    #: 0 = univariate terms only; 1 = all pairs. 2 (triples) is declared-and-unbuilt:
    #: a triple grid grows cubically and the JSONB envelope below cannot bound it
    #: (dated note in `02` §4.4, FR-207).
    interactions: int = Field(default=0, ge=0, le=1)
    #: `interpret` requires a power of two; the bounds are the library's own. Kept
    #: small by default: the fit result is JSONB, and 1024² cells per pair would be
    #: ~8 MB — see `_the_interaction_grid_stays_in_the_jsonb_envelope`.
    max_bins: int = Field(default=64, ge=16, le=32768)
    #: `interpret`'s own default; early stopping runs inside the library.
    max_rounds: int = Field(default=50000, ge=1)
    #: Direction per factor slug: -1 decreasing, 0 none, 1 increasing. Partial dicts are
    #: allowed here — factors resolve at fit time — and coverage is checked there
    #: (`EBM_MONOTONE_CONSTRAINT_INCOMPLETE`).
    monotone_constraints: dict[str, int] | None = None

    @field_validator("max_bins")
    @classmethod
    def _max_bins_is_a_power_of_two(cls, value: int) -> int:
        if value.bit_count() != 1:
            raise ValueError(
                f"max_bins must be a power of two (got {value}): `interpret` binning "
                "works on a dyadic grid, and anything else is the library's own refusal "
                "translated to a spec problem (FR-140)."
            )
        return value

    @model_validator(mode="after")
    def _the_interaction_grid_stays_in_the_jsonb_envelope(self) -> EbmSpec:
        if self.interactions > 0 and self.max_bins > 256:
            raise ValueError(
                f"interactions={self.interactions} with max_bins={self.max_bins}: a "
                "grid of that size is ~8 MB per pair inside the fit result's JSONB "
                "envelope. Cap max_bins at 256 with interactions, or use 0 (FR-140)."
            )
        return self

    @field_validator("monotone_constraints")
    @classmethod
    def _monotone_constraints_are_directions(
        cls, value: dict[str, int] | None
    ) -> dict[str, int] | None:
        if value is None:
            return None
        for slug, direction in value.items():
            if direction not in (-1, 0, 1):
                raise ValueError(
                    f"monotone constraint on {slug!r} has direction {direction}; only "
                    "-1 (decreasing), 0 (none) and 1 (increasing) exist (FR-122)."
                )
        return value

    @model_validator(mode="after")
    def _an_ebm_has_no_offset(self) -> EbmSpec:
        if self.offset.kind != "none":
            raise ValueError(
                f"offset kind {self.offset.kind!r} is GLM-only (FR-140): an EBM's "
                "lookups are additive on the identity link and `interpret` has no offset "
                "path — declaring one and ignoring it would be a silent model change."
            )
        return self
```

Union: `ModelSpec = Annotated[GlmSpec | GbmSpec | EbmSpec, Field(discriminator="model_type")]`.

**Flip** `test_gbm_spec.py::test_an_unknown_model_type_is_refused_by_the_discriminator` (:267-276): `ebm` is no longer the unknown — the test now asserts `"catboost"` is refused and keeps its `@pytest.mark.req("FR-119")` marker; a sibling assertion is added in `test_ebm_spec.py` that an `ebm` payload discriminates to `EbmSpec`.

**New tests** in `packages/model-schema/tests/test_ebm_spec.py` (module docstring in the style of the existing spec test files; `_spec(**over)` builder with `model_type="ebm"`, `model_family_slug`, `dataset_version_id`, `response_column`, `offset=OffsetSpec(kind="none")`):

1. `test_the_objective_vocabulary_is_rmse_and_mae` — `@pytest.mark.req("FR-140")`; `objective="poisson"` raises `ValidationError` matching `poisson`.
2. `test_the_families_and_binomial_log_loss_are_refused_by_name` — `@pytest.mark.req("FR-207")`; parametrised over `"poisson", "gamma", "tweedie", "inverse_gaussian", "negative_binomial", "log_loss"` each refused.
3. `test_max_bins_is_a_power_of_two_between_16_and_32768` — `@pytest.mark.req("FR-140")`; `32` ok; `50`, `8` and `65536` refused.
4. `test_the_interaction_grid_stays_in_the_jsonb_envelope` — `@pytest.mark.req("FR-140")`; `interactions=1, max_bins=512` refused; `interactions=1, max_bins=256` accepted.
5. `test_interactions_are_zero_or_one` — `@pytest.mark.req("FR-207")`; `2` refused (triples declared-and-unbuilt).
6. `test_monotone_constraints_are_directions` — `@pytest.mark.req("FR-122")`; `{"age": 2}` refused; `{"age": 1, "area": 0}` accepted; `{}` accepted.
7. `test_an_ebm_declares_no_offset` — `@pytest.mark.req("FR-140")`; `OffsetSpec(kind="log_column", column="exposure_years")` refused (match `GLM-only`).
8. `test_an_ebm_spec_round_trips_through_the_adapter` — `@pytest.mark.req("FR-119")`; `MODEL_SPEC_ADAPTER.validate_python` on a dumped spec is an `EbmSpec`.
9. `test_the_common_block_flows_into_the_ebm_arm` — `@pytest.mark.req("FR-140")`; `weight=WeightSpec(kind="column", column="n_claims")` and `seed=7` carried; `split_ref` accepted (FR-183 needs the holdout).
10. `test_an_ebm_spec_cannot_hold_a_glm_fit` — `@pytest.mark.req("FR-119")`; `Model(spec=EbmSpec, fit_result=GlmFitResult(...))` raises `ValidationError` (mirror of :280).

**Verification:**

```bash
uv run --package model-schema pytest -q packages/model-schema/tests/test_ebm_spec.py packages/model-schema/tests/test_gbm_spec.py
# expected: 10 + 25 = 35 passed, 0 failed (the flipped test passes in its new form)
uv run ruff check packages/model-schema && uv run mypy packages/model-schema
git add packages/model-schema/src/model_schema/modelling.py packages/model-schema/tests/test_ebm_spec.py packages/model-schema/tests/test_gbm_spec.py
git commit -m "feat(model-schema): add the EBM arm of ModelSpec with its refused-by-name vocabulary (FR-140)"
```

---

## Task 3 — `EbmFitResult` + union + paired check (model-schema)

**Files:** `packages/model-schema/src/model_schema/modelling.py` (extend `test_ebm_spec.py`).

**Interfaces** (placed beside `GbmFitResult` :1497; union at :1608 gains the arm):

```python
class EbmNumericBins(BaseModel):
    """A numeric feature's lookup bins: the cut array `interpret` fitted.

    `EbmFitResult` stores it verbatim from `bins_[f][0]` — length is not re-derived.
    The index of value `v` is `np.searchsorted(cuts, v, side="right") + 1`; slot 0 is
    the unused base slot. Slot layout (0.7.8, pinned): with `c` cuts the matching term
    carries `c + 3` slots — base (0), the `c + 1` populated bins, and one trailing
    missing-value slot — so `len(scores) == len(cuts) + 3`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal["numeric"] = "numeric"
    cuts: tuple[float, ...] = Field(min_length=1)


class EbmCategoricalBins(BaseModel):
    """A categorical feature's lookup bins: the levels in their fitted order.

    The level at position `i` has index `i + 1` — the same relationship the fitted
    estimator's `bins_[f]` dict (level -> 1-based index) records, written through
    verbatim. Slot 0 is the unused base slot; the term carries `len(levels) + 2`
    slots — base, the levels, and one trailing missing-value slot.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal["categorical"] = "categorical"
    levels: tuple[str, ...] = Field(min_length=1)


EbmFeatureBins = Annotated[EbmNumericBins | EbmCategoricalBins, Field(discriminator="kind")]


class EbmTerm(BaseModel):
    """One additive term: a univariate lookup or an interaction grid (FR-140)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: Indices into `EbmFitResult.feature_order`; length 1 (univariate) or 2 (pair).
    term_features: tuple[int, ...]
    term_name: str = Field(min_length=1)
    #: One score per slot, written verbatim from `term_scores_`. For a univariate
    #: numeric term there are `len(cuts) + 3` slots (slot 0 unused, one trailing
    #: missing-value slot); for an interaction, a rectangular grid with one row per
    #: bin of the first feature.
    scores: tuple[float, ...] | tuple[tuple[float, ...], ...]
    standard_deviations: tuple[float, ...] | tuple[tuple[float, ...], ...]
    #: Zeros mark the unused base slot, the trailing missing-value slot and any empty
    #: bins — the real-bin filter both the blob export and the complexity count rely on.
    bin_weights: tuple[float, ...] | tuple[tuple[float, ...], ...]
```

`EbmFitResult`: `model_type: Literal["ebm"] = "ebm"`, `objective: Literal["rmse", "mae"]`, `link: Literal["identity"] = "identity"`, `intercept: float`, `feature_order: tuple[str, ...]`, `bins: tuple[EbmFeatureBins, ...]`, `terms: tuple[EbmTerm, ...]`, `best_iteration: int = Field(ge=0)`, `rows: int = Field(default=0, ge=0)`, `fit_seconds: float = Field(ge=0.0)`, `library_versions: dict[str, str] = Field(default_factory=dict)` — all frozen, `extra="forbid"`. Four `model_validator(mode="after")` checks:

- `_bins_align_with_the_feature_order` — `len(bins) == len(feature_order)`, message naming both lengths (the `GbmFitResult` :1560 style — positional data whose length is unchecked is a silent mis-scoring).
- `_every_term_names_existing_features` — every index in every `term_features` `< len(feature_order)` and term length ∈ {1, 2}.
- `_the_lookup_shapes_match_the_bins` — per term: `len(scores) == len(standard_deviations) == len(bin_weights)` and, against the feature's bins, **`len(scores) == len(cuts) + 3` (numeric) or `len(scores) == len(levels) + 2` (categorical)** — the pinned 0.7.8 slot layout (base + populated + missing-value trailing); 2-D → rectangular grid whose dims equal the two features' slot counts. Comment records the formula source (the 2026-08-21 spike's structure note: 61 cuts → 64 slots, 62 nonzero weights) and that the fit writes verbatim, so drift surfaces as a failing fit-side round-trip test rather than a silent re-shape.
- `_the_base_slot_is_never_a_real_bin` — for 1-D terms `bin_weights[0] == 0.0` (and for 2-D, `bin_weights[0][0] == 0.0`); refusal message: a nonzero weight on the unused slot would make the complexity count lie about the real bins.

Union: `FitResult = Annotated[GlmFitResult | GbmFitResult | EbmFitResult, Field(discriminator="model_type")]`.

**New tests** (continue `test_ebm_spec.py`, with an `_fit(**over)` builder returning an `EbmFitResult` whose shapes satisfy the validators — 2 numeric features, 1 categorical, 1 univariate term per feature, `feature_order=("speed", "age_band", "area")`, `bins` numeric with e.g. `cuts` of length 61 and terms of 64 scores, or categorical with 3 levels and 5 scores):

11. `test_the_bins_align_with_the_feature_order` — `@pytest.mark.req("FR-140")`; mismatch raises.
12. `test_a_term_names_only_existing_features` — `@pytest.mark.req("FR-140")`; `term_features=(7,)` raises.
13. `test_the_lookup_shapes_match_the_bins` — `@pytest.mark.req("FR-140")`; scores length ≠ `len(cuts)+3` raises; scores length ≠ `len(levels)+2` raises.
14. `test_an_interaction_grid_is_rectangular` — `@pytest.mark.req("FR-140")`; ragged 2-D raises; dims mismatching the pair's slot counts raise.
15. `test_the_base_slot_is_never_a_real_bin` — `@pytest.mark.req("FR-140")`; `bin_weights[0] = 1.0` raises.
16. `test_a_fit_result_discriminates_on_model_type` — `@pytest.mark.req("FR-119")`; `FIT_RESULT_ADAPTER.validate_python` on the dumped fit is an `EbmFitResult`.
17. `test_a_model_cannot_hold_a_fit_from_another_model_type` — `@pytest.mark.req("FR-119")`; `Model(EbmSpec, GlmFitResult)` and `Model(GlmSpec, EbmFitResult)` both raise (mirror of :280).

**Verification:**

```bash
uv run --package model-schema pytest -q packages/model-schema/tests/test_ebm_spec.py
# expected: 17 passed, 0 failed
uv run ruff check packages/model-schema && uv run mypy packages/model-schema
git commit -m "feat(model-schema): add the EBM fit result with additive lookup tables (FR-140)"
```

---

## Task 4 — `TransparencyArtifact.ebm_shape_functions` + third kind (model-schema)

**Files:** `packages/model-schema/src/model_schema/transparency.py`; tests in `packages/model-schema/tests/test_glm_approximation.py` (the transparency-artifact test file).

**Interface:**

```python
class EbmShapeFunctions(BaseModel):
    """FR-140's export: the model itself, as tables.

    A JSON document, deliberately: the artifact row stores a JSONB payload and the
    tables ARE the model — this block is a pointer to the document rather than a
    nested copy that could drift from it. Built by `build_ebm_shape_functions`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    terms_blob: str = Field(min_length=1)
```

`TransparencyArtifact` gains `ebm_shape_functions: EbmShapeFunctions | None = None` after `shap_summary` (:179); the `kinds` property (:189-197) gains:

```python
        if self.ebm_shape_functions is not None:
            present.append(TransparencyKind.EBM_SHAPE_FUNCTIONS)
```

and `_an_artifact_explains_something` (:199-208) message updated to name all three forms ("neither a GLM approximation, a SHAP summary nor an EBM shape-functions export"). `TransparencyKind.EBM_SHAPE_FUNCTIONS`'s docstring (:46-57) is rewritten: no longer "declared and produced by nothing" — it is produced by `build_ebm_shape_functions` from the EBM slice, with the dated note.

**Tests** (in `packages/model-schema/tests/test_glm_approximation.py`):

1. `test_an_ebm_artifact_names_the_kind` — `@pytest.mark.req("FR-140")`; artifact with only `ebm_shape_functions` → `kinds == (TransparencyKind.EBM_SHAPE_FUNCTIONS,)`; artifact with both `glm_approximation` and `ebm_shape_functions` lists both (kinds is derived, never stored).
2. `test_an_ebm_artifact_needs_no_approximation_or_shap` — `@pytest.mark.req("FR-132")`; the EBM block alone satisfies "at least one form" (this is the whole of "transparent by construction").
3. `test_an_artifact_with_no_block_is_still_refused` — `@pytest.mark.req("FR-132")`; existing test updated only if its message asserts the two-form list (if it matches "neither a GLM approximation nor a SHAP summary" update the match string to the three-form message).

**Verification:**

```bash
uv run --package model-schema pytest -q packages/model-schema/tests/test_glm_approximation.py packages/model-schema/tests/test_ebm_spec.py
# expected: 10 + 17 = 27 passed, 0 failed
uv run ruff check packages/model-schema && uv run mypy packages/model-schema
git commit -m "feat(model-schema): carry the EBM shape-functions export on the transparency artifact (FR-140)"
```

---

## Task 5 — model-schema exports

**Files:** `packages/model-schema/src/model_schema/__init__.py`.

Add `EbmCategoricalBins`, `EbmFeatureBins`, `EbmFitResult`, `EbmNumericBins`, `EbmSpec`, `EbmTerm` to the `model_schema.modelling` import block (alphabetical) and `EbmShapeFunctions` to the transparency import block; all to `__all__`. `FitResult`/`ModelSpec` unions already flow through their adapters. (The pricing-core export lines land with Task 6's commit, after `ebm.py` exists.)

**Verification:**

```bash
uv run --package model-schema pytest -q packages/model-schema/tests
# expected: ~230 passed (204 + 17 + ~3 + flipped), 0 failed
uv run ruff check packages/model-schema && uv run mypy packages/model-schema
git commit -m "chore(model-schema): export the EBM arm from the package root (FR-140)"
```

---

## Task 6 — `interpret-core` dependency + `fit_ebm` (pricing-core)

**Files:** `packages/pricing-core/pyproject.toml`; `uv.lock` (via `uv sync`); new `packages/pricing-core/src/pricing_core/modelling/ebm.py`; new `packages/pricing-core/tests/test_ebm.py`; pricing-core `__init__.py` (export lines).

**Dependency:** `interpret-core==0.7.8` added to `[project.dependencies]` (after `scikit-learn>=1.5,<2`; pinned exact — one requirement, one model type; the metapackage `interpret` is deliberately not used). Commit message carries the spike rationale (≈115 MB incremental; sklearn 1.9.0 satisfies the requirement).

**`ebm.py`** — module docstring: "The EBM arm of fitting (FR-140). `interpret` is imported at call-site scope: the scoring path (`predict.py`) must never grow an import of the fitting stack (`07` NFR-535, `test_scoring_without_the_fitting_stack.py`)."

```python
class EbmFitError(RuntimeError):
    """A fit that cannot be returned as a result (FR-140).

    `code` is the platform error code the API surfaces. Named rather than a bare
    `ValueError` for the reason `GlmFitError` gives: the caller has to distinguish
    "this spec cannot be fitted" from "this library raised something".
    """

    def __init__(self, code: str, message: str, *, terms: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.terms = tuple(terms)
```

`fit_ebm(data, spec, factors, *, seed=0, bandings=None, groupings=None, progress=None) -> EbmFitResult`. Steps, in order:

1. `report = progress or NullProgress()`; `report.check_cancelled()`; `report.update(0.05, "ebm: encoding")`.
2. `matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)`; walk `factors` in spec order collecting `X` columns and `feature_types`: a categorical column → `series.cast(pl.String).to_numpy()` **verbatim** (the levels themselves — `interpret` builds its own dict `{level: 1-based index}`, which the artifact records by reading it back, so ordering never needs to match); `feature_types.append("categorical")`. Else numeric → `series.cast(pl.Float64).to_numpy()`, `"continuous"`. Empty column set → `EbmFitError("GBM_NO_FEATURES", ...)` — reuse the existing code (it is "no features to fit on", already registered and declared) rather than inventing an EBM twin; message mentions the EBM arm. **Bandings are ordinal and pass as categorical levels — the same "a banding is ordinal" rule `gbm._encode` documents (:262-273)** — the monotone-constraint check below allows a banding to be constrained because its levels are ordered.
3. **Monotone constraints pre-check** (before the estimator exists): for `slug, direction in (spec.monotone_constraints or {}).items()`: if `slug` not in the factor slugs → `EbmFitError("EBM_MONOTONE_CONSTRAINT_INCOMPLETE", f"monotone constraint names {slug!r}, which is not among the fitted factors ...", terms=[slug])`; if the factor is a categorical **and not a banding** → same code, "a monotone constraint cannot reach a continuous feature: ... is categorical and `interpret` refuses constraints on categoricals" (FR-122). Then build the full dict interpret demands: `{f"feature {i}": spec.monotone_constraints.get(factor.slug, 0) for i, factor in enumerate(factors)}` — interpret's keys are its own positional default names for numpy input; omission of any raises a bare `ValueError`, and this construction makes that impossible.
4. `report.update(0.25, "ebm: fitting")`; weights: `sample_weight = data[str(spec.weight.column)].cast(pl.Float64).to_numpy() if spec.weight.kind == "column" else None` — the `glm.py:583-584` rule.
5. `y = data[spec.response_column].cast(pl.Float64).to_numpy()`.
6. `import interpret` inside the function; `start = time.monotonic()`; construct and fit:

```python
        estimator = ExplainableBoostingRegressor(
            interactions=spec.interactions,
            max_bins=spec.max_bins,
            max_rounds=spec.max_rounds,
            monotone_constraints=constraints,     # full dict, built above
            random_state=spec.seed,               # the spec's seed is what spec_hash pins
            feature_types=feature_types,
        )
```

   wrapped in `try: estimator.fit(X, y, sample_weight=sample_weight) except ValueError as exc: raise EbmFitError("EBM_MONOTONE_CONSTRAINT_INCOMPLETE", f"interpret refused the EBM fit: {exc}") from exc` — the backstop for any library-side refusal the pre-checks did not cover (the pre-checks are the named path; the `except` is a translation so a library `ValueError` never surfaces as a stack trace, the FR-115 lesson). `random_state=spec.seed` — the `seed` kwarg mirrors `fit_glm`'s vestigial one (Task 0.5); a docstring note says so.
7. **Write the artifact verbatim** (no reshaping, no recomputation — the round-trip test owns the "tables reproduce interpret" claim): `feature_order = tuple(f.slug for f in factors)`; `bins` — numeric: `EbmNumericBins(cuts=tuple(float(v) for v in np.ravel(estimator.bins_[i][0])))`; categorical: `EbmCategoricalBins(levels=tuple(str(k) for k in estimator.bins_[i].keys()))` — **note:** `bins_[i]` for a categorical feature is the `(1,)` object array holding the dict; index `[0]` first; per term (in `term_features_` order): `term_features=tuple(int(i) for i in tf)`, `term_name=estimator.term_names_[t]`, `scores=tuple(...)` / nested tuples for 2-D (`estimator.term_scores_[t]` — `.tolist()` then tuple()s; **nested tuples for interaction grids, rows = bins of the first feature**), same for `standard_deviations_` and `bin_weights_`; `intercept=float(estimator.intercept_)`; `best_iteration=int(estimator.best_iteration_)`; `objective=spec.objective`; `link="identity"`; `rows=data.height`; `fit_seconds=time.monotonic() - start`; `library_versions={"interpret": importlib.metadata.version("interpret-core")}`. Return the `EbmFitResult` **directly** — no wrapper dataclass: the `GlmFit`/`GbmFit` wrappers exist to carry bytes beside the artifact, and this artifact has no bytes (Task 0.6). Document that asymmetry at the return statement.

Progress calls at 0.05/0.25/0.85/1.0 ("ebm: encoding", "ebm: fitting", "ebm: exporting tables", "ebm complete") — the `_fit` handler's `ScaledProgress` wraps this like any other fit.

**`test_ebm.py`** — module docstring: "The EBM arm of the fit (`02` §5.2). What is proven here is the fit: tables exported verbatim, the round-trip identity, constraints, weights, seed. The platform seam is `backend/tests/test_ebm_model_jobs.py`." A `_book(n=2000)` synthetic frame (numeric `speed`, categorical `area` A/B/C, banding `age_band` via `Banding`, plus `exposure_years`, `claim_count`), and a `_spec(**over)` EbmSpec builder mirroring `test_gbm.py`'s. Tests:

1. `test_fit_returns_the_expected_tables` — `@pytest.mark.req("FR-140")`; 3 univariate terms (one per factor), `feature_order` correct, numeric term has `len(scores) == len(cuts) + 3`, categorical term `len(scores) == len(levels) + 2`, `bin_weights[0] == 0.0`, `intercept` finite, `best_iteration >= 0`, `library_versions["interpret"] == "0.7.8"`, `rows == data.height`.
2. `test_the_exported_tables_reproduce_interpret_predict` — `@pytest.mark.req("FR-140")`, `@pytest.mark.req("NFR-535")`; **the round trip**: rebuild `intercept + Σ(term scores at each row's bins)` **inline in the test** via `np.searchsorted(cuts, v, side="right") + 1` (numeric) and the 1-based level dict (categorical) — `assert np.allclose(rebuilt, estimator.predict(X), atol=1e-9)` on data covering below-first-cut, mid, and above-last-cut values. This is where the spike's index rule and slot layout are enforced against 0.7.8; if the cuts/scores relationship is off by one it fails HERE, before any backend code exists, and the fix is a dated one-liner in the export (see Self-Review) — never a weakened tolerance.
3. `test_an_interaction_fit_exports_a_rectangular_grid` — `@pytest.mark.req("FR-140")`; `interactions=1` produces one 2-D term with dims matching the pair's slot counts; grid values reproduce `estimator.predict` via the two-level lookup.
4. `test_a_monotone_constraint_lands_on_the_right_feature` — `@pytest.mark.req("FR-122")`; `monotone_constraints={"speed": 1}` → the fitted speed term's real-bin scores are non-decreasing (`np.diff <= 1e-9`); the other terms unchanged in shape.
5. `test_a_monotone_constraint_on_a_categorical_feature_is_refused_by_name` — `@pytest.mark.req("FR-140")`; `{"area": 1}` → `EbmFitError` with `code == "EBM_MONOTONE_CONSTRAINT_INCOMPLETE"`.
6. `test_a_monotone_constraint_naming_an_unknown_slug_is_refused_by_name` — `@pytest.mark.req("FR-140")`; `{"no_such_factor": 1}` → same code.
7. `test_weights_reach_the_estimator` — `@pytest.mark.req("FR-184")`; fitting with `weight=WeightSpec(kind="column", column="n_claims")` (a column deliberately skewed) yields terms differing from the unweighted fit.
8. `test_the_fit_is_reproducible_under_the_spec_seed` — `@pytest.mark.req("FR-140")`; two fits, same seed → identical `terms` and `intercept`; `seed=1` vs `seed=2` → **different term scores** (compare a numeric term's `scores` — the spike found `intercept_` is data-determined and equal across seeds, so the intercept is not the discriminator).
9. `test_fit_seconds_and_library_versions_are_recorded` — `@pytest.mark.req("FR-140")`; `fit_seconds >= 0.0`, `library_versions` non-empty.

**Verification:**

```bash
uv sync --all-packages --dev          # installs interpret-core==0.7.8, updates uv.lock
uv run --package pricing-core pytest -q packages/pricing-core/tests/test_ebm.py
# expected: 9 passed, 0 failed
uv run ruff check packages/pricing-core && uv run mypy packages/pricing-core
uv run lint-imports
git add packages/pricing-core/pyproject.toml uv.lock packages/pricing-core/src/pricing_core/modelling/ebm.py \
        packages/pricing-core/src/pricing_core/modelling/__init__.py packages/pricing-core/tests/test_ebm.py
git commit -m "feat(pricing-core): fit EBM models via interpret-core and export their tables verbatim (FR-140)"
```

---

## Task 7 — `build_ebm_shape_functions` (pricing-core transparency.py)

**Files:** `packages/pricing-core/src/pricing_core/modelling/transparency.py`; `packages/pricing-core/tests/test_transparency.py`.

**Interfaces:**

```python
#: Version of the exported document. A reader that cannot parse it must refuse to
#: display it, not guess — an actuary reading tables under an unknown layout is
#: reading a different model.
EBM_SHAPE_BLOB_VERSION = "ebm-shape-functions/1"


def build_ebm_shape_functions(result: EbmFitResult) -> EbmShapeFunctions:
    """FR-140 — the model exported as tables, which is the model.

    No approximation, no scoring, no data: everything a reader of the blob needs is
    already in `result`, and copying anything else into the document would give the
    second statement of one fact a chance to disagree with the first.
    """


def ebm_fidelity_statement() -> str:
    """FR-136's statement for an EBM, which needs no measurement to make.

    The tables are the model — there is no surrogate whose divergence to report —
    so the statement says exactly that, rather than quoting a number that would
    read as a measured fidelity.
    """


def ebm_monotonicity_verified(result: EbmFitResult, spec: EbmSpec) -> bool | None:
    """FR-174's check for the EBM arm, read off the exported tables.

    `None` when the spec declared no constraints — distinct from `False`, which
    would say a constraint was checked and failed. For a constrained feature, every
    term that contains it must be monotone in the declared direction along that
    feature's axis: the univariate term's real-bin scores, or each row/column of an
    interaction grid. Same tolerance as the GBM arm (`worst <= 1e-9`).
    """
```

The blob is `json.dumps({...}, sort_keys=True)` of: `export_version`, `link: "identity"`, `intercept`, `best_iteration`, `terms: [...]` — per term `{"name": term.term_name, "features": [feature_order[i] for i in term.term_features], "kind": "numeric"|"categorical"|"interaction", "cuts" or "levels" (per feature, from result.bins), "scores", "standard_deviations", "real_bins"}` where `real_bins` is the `bin_weights != 0` mask (1-D list, or nested for grids). Floats serialise as JSON numbers (`float(x)` — the tables are float64 lookups; note in the docstring that this is the model's own precision). `ebm_fidelity_statement`'s prose (exact wording is the contract): "This EBM's term shape functions are exported directly as rateable tables. There is no approximation step and no fidelity to measure: the exported tables are the fitted model, so a Rating Version that rates on them rates on the model itself (FR-140)."

**Tests** (in `packages/pricing-core/tests/test_transparency.py`, importing `fit_ebm` plus a `_book`/`_spec` per that file's conventions):

1. `test_an_ebm_exports_its_shape_functions_verbatim` — `@pytest.mark.req("FR-140")`; fit a small book, build the blob, parse it: per term, `features` match `feature_order` indices, scores equal the artifact's tuples, `real_bins` marks exactly the nonzero `bin_weights`, `export_version == "ebm-shape-functions/1"`.
2. `test_the_ebm_fidelity_statement_is_exact_by_construction` — `@pytest.mark.req("FR-136")`; non-empty, contains "no fidelity to measure", and — the point — **does not quote a number**.
3. `test_monotonicity_verified_reads_the_exported_tables` — `@pytest.mark.req("FR-174")`; no constraints → `None`; a fit with `{"speed": 1}` → `True`; a hand-built `EbmFitResult` whose constrained term is decreasing → `False`; a grid whose second row violates an increasing constraint along the constrained axis → `False`.

**Verification:**

```bash
uv run --package pricing-core pytest -q packages/pricing-core/tests/test_transparency.py packages/pricing-core/tests/test_ebm.py
# expected: existing transparency tests + 3 new + 9 = all green, 0 failed
uv run ruff check packages/pricing-core && uv run mypy packages/pricing-core
git commit -m "feat(pricing-core): export an EBM's shape functions as the transparency blob (FR-140)"
```

---

## Task 8 — `predict_ebm` + `score_fitted`/backtest arms (pricing-core)

**Files:** `packages/pricing-core/src/pricing_core/modelling/predict.py`; `packages/pricing-core/src/pricing_core/modelling/diagnostics.py` (`_family_of`); `packages/pricing-core/tests/test_ebm.py`; `packages/pricing-core/tests/test_backtests.py`; `packages/pricing-core/tests/test_scoring_without_the_fitting_stack.py`.

**`predict.py`** — the module's identity is "what it does **not** import"; `predict_ebm` imports nothing but numpy/polars/model_schema.

```python
def predict_ebm(
    fit: EbmFitResult,
    data: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> npt.NDArray[np.float64]:
    """`μ` for an EBM, from its additive lookup tables alone (FR-140, ADR-705).

    No `interpret` import, no spec, no offset, no link inversion: the tables are the
    model, the link is identity, and `μ = intercept + Σ term scores`. The index rule
    is the one the fit recorded: numeric `np.searchsorted(cuts, v, side="right") + 1`
    (slot 0 is the unused base slot — below-range values land in bin 1, above-range
    in the last populated bin, no clamping), categorical by position in `levels` plus
    one. A level the fit never saw has no slot, and inventing one would score it as
    whichever level shares the number — `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` (the
    `gbm._encode` rule, FR-131).
    """
```

Implementation: `matrix = resolve_factors(data, factors, bandings=bandings, groupings=groupings)`; build per-slug index arrays once: numeric → `np.searchsorted(np.asarray(bins.cuts), v, side="right") + 1` (non-finite values follow `np.searchsorted` semantics exactly — the same rule the fitted estimator applied, so scoring agrees with `interpret` on every input by construction); categorical → a dict `{level: i + 1}` built from `fit.bins[f].levels`, unknown level → `PredictionError("UNSEEN_LEVEL_BEHAVIOUR_REQUIRED", f"factor {slug!r} carries level {level!r} that the fitted model never saw (FR-131).", terms=[slug])` — the code is already registered and declared (`gbm.py:295`, §5.1). Then `eta = np.full(data.height, fit.intercept)`; per term: univariate → `eta += scores[idx]`; interaction → `eta += scores[idx_a][idx_b]` (2-D lookup). Return `eta` (identity — this *is* the mean).

`score_fitted` (:334-380): add before the GLM assert —

```python
    if isinstance(fit, EbmFitResult):
        return predict_ebm(fit, data, factors, bandings=bandings, groupings=groupings)
```

(docstring updated: the dispatch now covers three kinds; `booster` is required only for a GBM, and `model_offset` only for a GLM — both already impossible on the EBM arm by type.) `_family_of` (`diagnostics.py:671-685`): add `if isinstance(spec, EbmSpec): return "gaussian", 1.5` (identity link; the power is unused by gaussian and kept for the shared signature). `backtest_model` then works unchanged.

**Tests:**

1. `test_scoring_matches_interpret_on_a_held_out_frame` — `@pytest.mark.req("FR-140")`; fit on a train split, `np.allclose(predict_ebm(fit, test_frame, ...), estimator.predict(X_test), atol=1e-9)` — the same tolerance as the Task 6 identity: identical arithmetic, so `1e-9` absolute is justified (a reproduction-tolerance, not a model-tolerance).
2. `test_an_unseen_level_is_refused_by_name` — `@pytest.mark.req("FR-131")`; score a frame carrying `area="Q"` → `PredictionError` with `code == "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"`.
3. `test_a_scored_term_resolves_from_the_artifact_alone` — `@pytest.mark.req("FR-140")`; drop the `factors`/`data` used at fit time, score a fresh frame with the same factor slugs (the artifact's `feature_order` and `bins` are the only ground truth).
4. `test_an_ebm_backtests_through_the_shared_path` — `@pytest.mark.req("FR-187")`; `backtest_model(fit, spec, factors, later_frame, model_ref=..., dataset_version_ref=..., fitted_on_ref=...)` → `BacktestSummary` with a partition (A/E, lift, gini, calibration present) — the shared `_partition` over `score_fitted` + `_family_of` (add to `packages/pricing-core/tests/test_backtests.py`).
5. `test_an_ebm_scores_in_a_process_where_interpret_cannot_be_imported` — `@pytest.mark.req("NFR-535")`, `@pytest.mark.req("FR-140")`; extend `test_scoring_without_the_fitting_stack.py`: add `"interpret"` to `BLOCKED`, and a third test mirroring the GLM child — fit with interpret here, hand the artifact JSON to a child where `import interpret` raises, score with `predict_ebm`, assert the totals reproduce the in-process scoring. The strongest ADR-705 statement in the suite: the tables ARE the model, in a process that cannot import the fitting stack.

**Verification:**

```bash
uv run --package pricing-core pytest -q packages/pricing-core/tests/test_ebm.py \
       packages/pricing-core/tests/test_backtests.py packages/pricing-core/tests/test_scoring_without_the_fitting_stack.py
# expected: all green (test_ebm 9→13, test_backtests 5→6, scoring-stack 2→3), 0 failed
uv run ruff check packages/pricing-core && uv run mypy packages/pricing-core
uv run lint-imports
git commit -m "feat(pricing-core): score EBM models from their exported tables alone (FR-140)"
```

---

## Task 9 — `compute_ebm_diagnostics` (pricing-core diagnostics.py)

**Files:** `packages/pricing-core/src/pricing_core/modelling/diagnostics.py`; `packages/pricing-core/tests/test_diagnostics.py`.

**Interface** (beside `compute_gbm_diagnostics` :908):

```python
def compute_ebm_diagnostics(
    result: EbmFitResult,
    spec: EbmSpec,
    factors: Sequence[Factor],
    *,
    train: pl.DataFrame,
    holdout: pl.DataFrame,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
    max_factor_count: int | None = None,
    min_exposure_per_parameter: float | None = None,
    progress: ProgressCallback | None = None,
) -> DiagnosticsResult:
    """Everything `02` §3.8 asks of an EBM fit (FR-MODEL-49, 50, 54, 55, 81).

    The universal block is the *same code* as the GLM's and GBM's — `_partition`
    takes `mu` and knows nothing about how it was produced. The EBM's family is
    gaussian (identity link); its complexity is the number of real bins across the
    exported tables, counted off `bin_weights` — the estimator is gone by the time
    this runs, and the tables are the model (ADR-705). `glm` and `gbm` blocks are
    `None`: this model has no coefficient vector, no trees, no eval curve, and its
    dependence structure *is* the transparency artifact.
    """
```

Body: `family, power = "gaussian", 1.5`; `train_part = _partition(train, spec, factors, mu=predict_ebm(result, train, factors, bandings=..., groupings=...), family=family, power=power, ...)`; same for `holdout_part` (progress 0.05/0.30, mirroring :937-955); complexity: `parameter_count = sum over terms of int((bin_weights != 0).sum())` (1-D and grid alike), `factor_count = len(factors)`, `exposure_per_parameter`/`claims_per_parameter` via `_weights(spec, train)` and the response column — the :1002-1015 pattern; return `DiagnosticsResult(universal=..., complexity=..., glm=None, gbm=None)`.

**Tests** (in `packages/pricing-core/tests/test_diagnostics.py`):

1. `test_an_ebm_reports_universal_diagnostics_and_no_glm_or_gbm_block` — `@pytest.mark.req("FR-171")`, `@pytest.mark.req("FR-183")`; train and holdout partitions both populated; `glm is None`, `gbm is None`; `complexity.factor_count == len(factors)`.
2. `test_ebm_complexity_counts_the_real_bins` — `@pytest.mark.req("FR-185")`; `parameter_count` equals the hand-counted nonzero `bin_weights` total (build one 2-D term to prove grids count cells, not terms).
3. `test_the_ebm_arm_uses_the_same_partition_as_the_gbm_arm` — `@pytest.mark.req("FR-171")`; an EBM fit and a same-factors GBM fit on one book produce `UniversalDiagnostics` of the same shape (fields identical, values differ).

**Verification:**

```bash
uv run --package pricing-core pytest -q packages/pricing-core/tests/test_diagnostics.py packages/pricing-core/tests/test_ebm.py
# expected: existing diagnostics tests + 3 new + 13 = all green, 0 failed
uv run ruff check packages/pricing-core && uv run mypy packages/pricing-core
git commit -m "feat(pricing-core): universal diagnostics for EBM fits through the shared partition (FR-171)"
```

---

## Task 10 — `SPEC_HASH_VERSION` 8 → 9

**Files:** `backend/src/app/platform/modelling.py`; `backend/tests/test_spec_hash.py`.

- `SPEC_HASH_VERSION: Final = 9` (:132) with the docstring block gaining: `#: **v9, 2026-08-21** — EbmSpec joined the union (FR-140): model_type, objective, interactions, max_bins, max_rounds, monotone_constraints. Every v8: digest is now stale and must be findable with LIKE 'v9:%'.` The canonicaliser needs no code change — `spec.model_dump(mode="json")` with `sort_keys` picks up the new fields (verified, :135-153).
- `test_spec_hash.py::test_the_algorithm_version_moved_with_the_new_field` (:163-184): assert `== 9`, digest `v9:sha256:`, `spec_hash_is_current("v8:sha256:" + "0"*64) is False`; the `v7 -> v8` comment gains the `v8 -> v9 (2026-08-21, FR-140)` line; add `@pytest.mark.req("FR-140")`.
- New test `test_an_ebm_spec_hashes_distinctly` — `@pytest.mark.req("FR-204")`, `@pytest.mark.req("FR-140")`; an `EbmSpec` and a same-skeleton `GlmSpec` (same family slug, dataset, response, factors) hash differently; two EbmSpecs differing only in `max_bins` differ; two differing only in `objective` differ.

**Verification:**

```bash
uv run --package backend pytest -q backend/tests/test_spec_hash.py
# expected: existing + 1 new = all green, 0 failed
uv run ruff check backend && uv run mypy backend
git commit -m "feat(backend): move the spec hash version to v9 with the EBM fields (FR-206)"
```

---

## Task 11 — Backend fit arm + error registration

**Files:** `backend/src/app/errors.py`; `backend/src/app/worker/model_handlers.py`; `backend/tests/test_spec_hash.py`; new `backend/tests/test_ebm_model_jobs.py`.

**1. `errors.py`** — `MODELLING_ERROR_CODES` gains `"EBM_MONOTONE_CONSTRAINT_INCOMPLETE"` with a dated comment (2026-08-21, the EBM slice; refused-by-name constraint coverage/direction on categoricals).

**2. `test_spec_hash.py::test_every_code_the_fit_path_can_raise_is_registered`** (:107-145) — the parametrisation gains `("pricing_core.modelling.ebm", "EbmFitError")` with a comment mirroring the FR-159/160 note. **This test does not auto-discover new modules** — the row is mandatory. The root invariant test scans `modelling/*.py` automatically, so nothing else is needed there.

**3. `model_handlers.py::_fit`** —
- imports: `EbmFitError, EbmSpec` added.
- Dispatch (:330-365) restructured to if/elif/else:

```python
        if isinstance(spec, GbmSpec):
            fit = fit_gbm(...)          # unchanged
            result, booster, eval_curve = fit.result, fit.booster_bytes, fit.eval_curve
        elif isinstance(spec, EbmSpec):
            # No wrapper, no bytes: an EBM's fit result IS the model (Task 0.6), so
            # `booster`/`covariance` keep their pre-initialised None values and
            # `store()` writes no blob.
            result = fit_ebm(
                frame, spec, factors, seed=spec.seed,
                bandings=transformations.bandings,
                groupings=transformations.groupings,
                progress=fitting,
            )
        else:
            glm_fit = fit_glm(...)      # unchanged
```

  (No `model_offset` on the EBM arm — `EbmSpec` refuses offsets at the type, Task 2.)
- `except (GbmFitError, GlmFitError)` (:366) → `except (EbmFitError, GbmFitError, GlmFitError)` — the message already says "The {spec.model_type} model could not be fitted", which reads correctly for `ebm`.
- Diagnostics dispatch (:385-410):

```python
    if isinstance(spec, GbmSpec) and isinstance(result, GbmFitResult) and booster:
        computed = compute_gbm_diagnostics(...)          # unchanged
    elif isinstance(spec, EbmSpec) and isinstance(result, EbmFitResult):
        computed = compute_ebm_diagnostics(
            result, spec, factors,
            train=frame, holdout=holdout,
            bandings=transformations.bandings,
            groupings=transformations.groupings,
            progress=diagnostic_progress,
        )
    elif isinstance(spec, GlmSpec) and isinstance(result, GlmFitResult):
        ...   # unchanged
    else:  # pragma: no cover - the unions are checked together at the type
        raise PlatformError(
            "MODEL_TYPE_UNSUPPORTED",
            "This model type cannot be fitted",
            409,
            f"{spec.model_type!r} has a spec arm and no fit path.",
        )
```

  The else-guard's message drops the "`ebm` is declared by `CLAUDE.md` §7 and built by no slice" sentence — the else is now unreachable by construction (all three arms covered). `gbm_diagnostics = computed.gbm` is `None` on the EBM arm — the `Diagnostics` row then carries `glm=None, gbm=None, universal=..., complexity=...`, which the model allows.
- `store()` (:453-481): **no change** — `booster`/`covariance` are `None` on the EBM arm (pre-initialised locals), so no blob is stored; `record_fit(fit_result=result)` persists the JSONB payload.

**4. `backend/tests/test_ebm_model_jobs.py`** — imports and helpers mirror `test_model_jobs_gbm.py` exactly: `_actuary, _dataset, _factor, _split, _validated_version` from `test_model_jobs`; a `_ebm_spec(version_id, factor_ids, **over)` builder (`model_type="ebm"`, `objective="rmse"`, `offset=OffsetSpec(kind="none")`); `_fitted_ebm(database, blob_store, workspace_id, **over) -> tuple[UUID, JobStatus]` — `reserve_model` → `job_service.submit(JobKind.MODEL_FIT, {"workspace_id": ..., "actor": ..., "model_id": ...})` → `execute_job` (the :98-114 pattern). Tests:

1. `test_an_ebm_fits_through_the_same_job_as_a_glm` — `@pytest.mark.req("FR-140")`; status `SUCCEEDED`; the model row's `fit_result` validates as `EbmFitResult` via `FIT_RESULT_ADAPTER`; spec round-trips via `MODEL_SPEC_ADAPTER`; status is `fitted`.
2. `test_an_ebm_records_universal_diagnostics_and_no_glm_or_gbm_block` — `@pytest.mark.req("FR-170")`, `@pytest.mark.req("FR-174")`; `diagnostics_service.load_diagnostics` → `glm is None`, `gbm is None`, `universal.train`/`holdout` populated, `complexity.parameter_count >= 1`.
3. `test_an_ebm_with_a_bad_monotone_constraint_fails_the_job_with_the_named_code` — `@pytest.mark.req("FR-115")`, `@pytest.mark.req("FR-140")`; spec with `monotone_constraints={"area": 1}` (area is an identity categorical) → `execute_job` returns `FAILED` and the stored job error contains `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` (read the job row's error payload — the pattern `test_model_jobs_gbm.py:234` uses).
4. `test_the_ebm_fit_job_stores_no_blob` — `@pytest.mark.req("FR-140")`; after a successful fit, the blob-store row count is unchanged (an EBM has no booster and no covariance — the JSONB row is the whole model).
5. `test_an_ebm_with_interactions_fits_through_the_job` — `@pytest.mark.req("FR-140")`; `interactions=1, max_bins=64` on two factors → the fit result carries one 2-D term (small book keeps it fast).

**Verification:**

```bash
uv run --package backend pytest -q backend/tests/test_ebm_model_jobs.py backend/tests/test_spec_hash.py
# expected: 5 + existing spec-hash tests = all green, 0 failed
uv run pytest -q tests/test_repository_invariants.py    # 14 passed — the new code is registered AND declared
uv run ruff check backend && uv run mypy backend
git commit -m "feat(backend): fit EBM specs through model.fit with the named constraint refusal (FR-140)"
```

---

## Task 12 — Backend transparency arm

**Files:** `backend/src/app/worker/model_handlers.py` (`_transparency` :710-943); `backend/src/app/platform/transparency.py` (docstrings); tests in `backend/tests/test_ebm_model_jobs.py`.

**`_transparency`** — after `fitted_gbm_or_refuse` (:751) and the adapter validation, replace the `MODEL_TYPE_UNSUPPORTED` guard (:756-762) with an EBM branch:

```python
            if isinstance(spec, EbmSpec) and isinstance(result, EbmFitResult):
                artifact = TransparencyArtifact(
                    id=new_uuid7(),
                    model_id=model_id,
                    created_at=datetime.now(UTC),
                    job_id=job_id,
                    ebm_shape_functions=build_ebm_shape_functions(result),
                    fidelity_statement=ebm_fidelity_statement(),
                    monotonicity_verified=ebm_monotonicity_verified(result, spec),
                )
            elif isinstance(spec, GbmSpec) and isinstance(result, GbmFitResult):
                ... # the existing GBM path, unchanged, with its MODEL_TYPE_UNSUPPORTED
                    # raised only for a spec/result mismatch (the guard keeps its text)
            else:
                raise PlatformError(
                    "MODEL_TYPE_UNSUPPORTED", "This model type has no transparency builder",
                    409, f"{spec.model_type!r} is neither a gradient boosting nor an EBM model.",
                )
```

The EBM branch returns early before the GBM machinery (`sample`, split frames, booster read, approximation): the export needs nothing but the fit result and the spec — Task 0.7. The persistence that follows uses the existing `record_transparency` (which already audits `kinds` and `monotonicity_verified`, `transparency.py:72-84`). Docstring of `_transparency` gains the EBM sentence.

**`fitted_gbm_or_refuse`** (platform/transparency.py:121-151) — docstring amended: the two refusals apply to any non-GLM transparency build; **an EBM passes through unchanged** (it already does — the GLM check is `row.spec.get("model_type") == "glm"`). Module docstring and `load_transparency`'s 404 prose mention the EBM form. Name retained (Task 0.9).

**Tests** (in `backend/tests/test_ebm_model_jobs.py`, mirroring `test_glm_approximation_model.py`'s helpers — import `_transparency_job`/`_transparency_refusal` from there; they are module-level and reusable):

1. `test_an_ebm_transparency_artifact_is_built_and_read_back` — `@pytest.mark.req("FR-140")`, `@pytest.mark.req("FR-132")`, `@pytest.mark.req("FR-139")`; after `_fitted_ebm`, run `_transparency_job` → `artifact.kinds == (TransparencyKind.EBM_SHAPE_FUNCTIONS,)`, `fidelity_statement` non-empty, `monotonicity_verified is None`, `glm_approximation is None`, `shap_summary is None`, `ebm_shape_functions.terms_blob` parses as JSON with `export_version == "ebm-shape-functions/1"`.
2. `test_an_ebm_with_constraints_verifies_monotonicity_from_the_tables` — `@pytest.mark.req("FR-174")`, `@pytest.mark.req("FR-140")`; fit with `monotone_constraints={"speed": 1}` (a numeric factor) → `artifact.monotonicity_verified is True`.
3. `test_an_unfitted_ebm_is_refused_a_transparency_artifact` — `@pytest.mark.req("FR-132")`; reserve an EBM model without fitting → `_transparency_refusal` → `PlatformError.code == "MODEL_NOT_FITTED"`.
4. `test_a_second_artifact_appends_rather_than_replacing` — `@pytest.mark.req("FR-132")`, `@pytest.mark.req("FR-139")`; two `_transparency_job` runs → `load_transparency` returns the latest and both rows exist (the FR-132 "several artifacts" property, `test_model_jobs_gbm.py:606` pattern).

**Verification:**

```bash
uv run --package backend pytest -q backend/tests/test_ebm_model_jobs.py
# expected: 5 + 4 = 9 passed, 0 failed
uv run ruff check backend && uv run mypy backend
git commit -m "feat(backend): build the EBM shape-functions transparency artifact through model.transparency (FR-140)"
```

---

## Task 13 — Contracts regenerate (ADR-704)

**Files:** `docs/contracts/schemas/transparency-artifact.schema.json`, `docs/contracts/schemas/model.schema.json`, `docs/contracts/openapi/generated.json` (regenerated); `scripts/generate-contracts.py` unchanged.

**Steps:**

- [ ] 13.1 `uv run python scripts/generate-contracts.py` — the checked-in `transparency-artifact.schema.json` (:68-72) already hand-declares `ebm_shape_functions {terms_blob: string}`; regeneration now produces that arm **from the type** (with `EbmShapeFunctions`'s real shape), reconciling the divergence Task 1 recorded. `model.schema.json` gains the `EbmSpec`/`EbmFitResult` arms; the OpenAPI `generated.json` gains them under the model-spec/model endpoints.
- [ ] 13.2 Inspect the diff: the transparency schema's `ebm_shape_functions` block should now be generated output, not a hand edit; nothing else unexpected.
- [ ] 13.3 `uv run python scripts/generate-contracts.py --check` must pass (CI's ADR-704 step).

**Verification:**

```bash
uv run python scripts/generate-contracts.py
git diff --stat docs/contracts/
uv run python scripts/generate-contracts.py --check      # exit 0
uv run --package backend pytest -q backend/tests/test_contracts.py
# expected: 20 passed, 0 failed — includes test_every_eligible_schema_is_compared
git commit -m "chore(contracts): regenerate the schemas with the EBM arm from the types (ADR-704)"
```

---

## Task 14 — Docs, roadmap slice record, FR-173 marker

**Files:** `docs/roadmap.md`; `backend/tests/test_contracts.py` (one marker line).

**Commit 14a — roadmap corrections (the FR-140 row was touched in Task 1; this commit completes the record):**
- FR-140 row (:1717): "**Delivered 2026-08-21 (WK-661, the EBM slice).** `interpret-core==0.7.8`; term shape functions exported verbatim as additive lookup tables; transparency artifact built from the export with no approximation; universal diagnostics through the shared partition; scoring from the tables alone (ADR-705). The third heavy dependency is now installed, so the 'one requirement for a model type nothing fits' objection is discharged."
- WK-661 outstanding row 5 (:2572): mark delivered with the same date.
- FR-115 corrections: :2598 "FR-115 remains unbuilt" → "FR-115 is delivered: markers at `test_glm.py:134,:429` and `test_spec_hash.py:92,:107`, `GLM_SEPARATION_DETECTED` registered and declared — the 'remains unbuilt' lines were stale. The remainder — a bare non-`LinAlgError` `ValueError` from glum still reaches the job unwrapped — is recorded 2026-08-21 as unbuilt, owner WK-661." Same correction at :2773.
- FR-161 (:2725): verdict recorded — "owned by WK-661, due before WK-661 closes; explicitly NOT this (EBM) slice" — the task records the verdict and does not build it.
- NFR gap (:2579): recorded as-is; NFR-482's export/import round-trip remains unevidenced for the suite — the EBM round-trip tests (Task 6/8) are evidence for the EBM artifact only, and the record says exactly that.
- Weights gap (from Task 0.4): `fit_gbm` ignores `spec.weight` — recorded with a dated note, owner WK-661.
- Objectives (Task 0.2/0.3): EBM objective vocabulary is `rmse`/`mae`; §7 families + binomial `log_loss` refused by name (FR-207, dated note in §4.4); `interactions=2` (triples) declared-and-unbuilt; custom objectives do not apply to EBM (`ObjectiveBackend` has no EBM member by design).
- The `06` §3.3 custom-metric evidence-row gap and OQ-639 remain as they were — unchanged by this slice.

**Commit 14b — FR-173 marker backfill:** `backend/tests/test_contracts.py:554` (`test_every_eligible_schema_is_compared` — the test the FR-173 correction directly changed) gains `@pytest.mark.req("FR-173")`. One line, its own commit (Task 0.14). Then `scripts/req-coverage.py` shows FR-173 marked.

**Verification:**

```bash
uv run --package backend pytest -q backend/tests/test_contracts.py        # 20 passed
uv run python scripts/req-coverage.py                                      # FR-173 and FR-140 now marked
git commit -m "docs(roadmap): record the EBM slice, correct the FR-115 verdicts, record the WK-661 verdicts"
git commit -m "test(backend): backfill the FR-173 marker on the contracts comparison"
```

---

## Task 15 — Full gate, both halves

**Commands (the CI gate run locally; the EBM job tests use the same fixtures as `test_model_jobs_gbm`, so the existing local test setup applies — export `GIP_TEST_DATABASE_URL`/`GIP_DATABASE_URL` and `uv run alembic upgrade head` per `task_plan.md`'s environment block):**

```bash
uv sync --all-packages --dev
uv run ruff check .                                            # 0 warnings/errors
uv run mypy                                                    # 0 errors (--strict, repo config)
uv run lint-imports                                            # 0 violations
uv run pytest -q                                               # full python suite, 0 failed
uv run python scripts/audit-docs.py                            # 0 findings
uv run python scripts/generate-contracts.py --check            # exit 0
uv run python scripts/req-coverage.py                          # FR-140 marked; totals reported
```

**Expected: all green, both halves.** No alembic revision exists in this slice: `ModelRow.spec`/`fit_result` and `TransparencyArtifactRow.payload` are JSONB columns, unchanged. Frontend: nothing (WK-664 owns any view that renders an EBM) — the slice is API-only, stated in the slice record.

---

## Self-Review (run at planning time)

**Spec coverage.** FR-140's obligations map: (i) "treated as transparent by construction — term shape functions exported directly as tables, no approximation" → Task 4/7 (artifact block + verbatim blob, fidelity statement exact-by-construction, no surrogate model); (ii) "still carry the fidelity/diagnostic sections in the same contract shape" → Task 7 (`fidelity_statement`/`monotonicity_verified` on the same artifact) and Task 9 (universal diagnostics via the shared `_partition`, family gaussian); (iii) model vocabulary (`CLAUDE.md` §7, `02` §4.4 `model_type: ... | ebm`) → Task 2 (union arm) with §7 families + binomial `log_loss` + triples refused by name under FR-207. Supporting requirements: FR-204/206 (Task 10 hash bump with the fields), FR-115 (named refusal path for the one EBM code, and the roadmap corrections), FR-122 (monotone directions at the type; categorical refusal at fit), FR-131 (unseen-level refusal, code reused), FR-132/136/139 (artifact, kinds, readback), FR-170/171/183/184/185 (diagnostics), FR-187 (backtest through the shared path), NFR-535/ADR-705 (child-process scoring test).

**Placeholder scan.** Every function named in the plan exists at the cited anchor (each was read, not assumed) or is created by the task that first uses it. No invented helpers: the backend tests reuse `_actuary/_dataset/_factor/_split/_validated_version` (test_model_jobs.py), `_fitted_gbm`'s reserve/submit/execute pattern (test_model_jobs_gbm.py:98-114), and `_transparency_job/_transparency_refusal` (test_glm_approximation_model.py:53-112) — all verified to exist. The one deliberate asymmetry: `fit_ebm` returns `EbmFitResult` directly (no `GlmFit`/`GbmFit`-style wrapper) because the wrappers exist to carry bytes and an EBM has none — documented in Task 6.

**Type consistency.** `EbmSpec`/`EbmFitResult` join both discriminated unions on `model_type`; `Model._the_fit_matches_the_specification` (:1745) needs no change; `score_fitted`'s EBM arm needs no booster and no `model_offset` (both excluded by type — `EbmSpec` refuses offsets); `_family_of` returns `("gaussian", 1.5)`; `Diagnostics` allows `glm=None, gbm=None`; `validate_spec`/`reserve_model` accept EBM by construction (`_objective_problems` returns `[]` for non-GBM, `complexity_or_refuse` is type-agnostic — both verified). `EbmTerm` shapes are at most 2-D because `interactions` is capped at 1.

**Review corrections applied before saving** (main-thread review of the Plan agent's draft, 2026-08-21):

1. **Slot-layout formula corrected.** The draft's `len(scores) == len(cuts) + 1` / `len(levels) + 1` contradicted the spike's structure note (61 cuts → 64 slots; 62 nonzero weights). Corrected to `len(cuts) + 3` (numeric) / `len(levels) + 2` (categorical) in the `EbmNumericBins`/`EbmCategoricalBins` docstrings, `_the_lookup_shapes_match_the_bins`, test 13, and Task 6 test 1 — the layout is pinned to interpret-core 0.7.8 (base slot + populated bins + trailing missing-value slot).
2. **`interactions` capped at 1.** The draft allowed 0..2, but triples contradict the 2-D `EbmTerm` shape and the JSONB envelope validator (256³ ≈ 130 MB per triple). `le=1`; `2` refused by name under FR-207 (Task 1 note, Task 2 test 5, Task 0.11).
3. **Different-seed test fixed.** The draft asserted different intercepts across seeds; the spike found `intercept_` data-determined and equal across seeds. Task 6 test 8 now compares term scores.
4. **Anchor corrected.** The FR-173 marker backfill targets `backend/tests/test_contracts.py:554` (the function), not :542 (a comment referencing it).
5. **Flagged, not fixed:** interpret's `monotone_constraints` key convention (`f"feature {i}"` = numpy-input default names) comes from the spike but was not re-verified against the library's source; the Task 6 pre-check + backstop fail loudly if it ever differs, and the fix is one dict comprehension.

**Verified vs unverified.** Verified by reading the repo: every anchor listed in Slice context, both `__init__` export blocks, the §5.1 catalogue paragraph boundaries, the AST-scan invariants' exact mechanics (auto-scan of `modelling/*.py`, catalogue-may-run-ahead, `test_spec_hash.py:107` parametrisation does NOT auto-discover), the `Diagnostics` model, `complexity_or_refuse`, `test_scoring_without_the_fitting_stack.py`'s BLOCKED set and child pattern, roadmap line numbers and stale texts, CI gate commands. **Not verifiable in this environment** (interpret is not installed in the repo env; the spike facts come from the main thread's live scratch venv): interpret's exact slot layout and index rule — the plan's load-bearing formulas follow from the spike's structure note, and the Task 6 round-trip test is the enforcement: if 0.7.8 disagrees, the failure is loud, localised to one validator line and one comment, and must be fixed with a dated note, never by weakening the test. Also from the spike: `max_bins` power-of-two range [16, 32768], `max_rounds` default 50000, the `monotone_constraints` key convention, and the timing (~10 s / 50k×9 at `max_bins=64`; ≈135–200 s extrapolated to freMTPL2) — recorded in Task 6's commit message, not asserted in a test.

**Risks.** (1) The off-by-one/slot-layout risk above — mitigated by verbatim writing (never re-shape) and the round-trip test. (2) interpret's internal early-stopping split — reproducible under `random_state=spec.seed`; `best_iteration_` recorded; no split is exposed, matching the settled field list. (3) JSONB size at `interactions=1, max_bins=256` (36 pairs × ~0.5 MB worst case) — bounded by the envelope validator; the default path is ~5 KB. (4) EBM fit runtime on freMTPL2-sized books (~135–200 s spike extrapolation) — the `ScaledProgress` window already exists; no timing test added.
