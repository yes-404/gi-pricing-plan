# Regularisation and Cross-Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `GlmSpec` a documented elastic-net penalty path (FR-MODEL-20) and a
cross-validated alternative to fixed-alpha fitting (FR-MODEL-53) — declared fold
construction (`random` / `temporal` / `grouped_by_key`) with a persisted seed, and
per-fold metrics **and their dispersion**, not only the mean, persisted on the existing
`Diagnostics` artifact.

**Architecture:** `pricing_core.data.splits` gains `assign_folds()`, a K-fold
generalisation of the existing two-part `assign_parts()` (same three methods, same seeded
determinism). `pricing_core.modelling.glm.fit_glm()` gains a private `_fit_cv_path()` that
refits the elastic-net path across folds using `glum` directly and the existing
`deviance()` scorer from `pricing_core.modelling.diagnostics`, selecting the alpha with
the lowest mean held-out deviance. The result — the full path and the selected alpha's
per-fold scores — is threaded straight from `GlmFit.cv` through the `model.fit` job
handler into `Diagnostics.cross_validation`, exactly as `covariance`/`booster` bytes
already bypass `compute_diagnostics()`. No new HTTP endpoint: the existing
`GET /api/v1/models/{id}/diagnostics` already returns the whole `Diagnostics` artifact. No
frontend work: the Diagnostics view's "CV fold dispersion" item is owned by a later
workstream (W6b).

**Tech Stack:** Python 3.12, Pydantic v2 (`model-schema`), `glum`
(`GeneralizedLinearRegressor`), Polars, NumPy, pytest + `@pytest.mark.req`, SQLAlchemy 2.x
async (unchanged — no migration, `Diagnostics` is a single JSONB `payload` column).

**Spec:** `docs/specs/02-modelling.md` — FR-MODEL-20 and FR-MODEL-53 (§3, the GLM
functional requirements), read together with §4.4 (`GlmSpec`'s data contract), §4.9
(`Diagnostics`'s data contract) and §5.2 (`fit_glm` / `compute_diagnostics` signatures).
Exact requirement text, transcribed from the spec for this plan:

- **FR-MODEL-20**: "A GLM fit MAY apply elastic-net regularisation via `alpha` (overall
  penalty strength) and `l1_ratio` (the L1/L2 mix). The fit MUST support scanning a path
  of `alpha` values and persisting the full path, not only the alpha ultimately selected."
- **FR-MODEL-53**: "Where regularisation strength is chosen by cross-validation
  (`select_by: cv`), the fold construction MUST be declared (`random`, `temporal` or
  `grouped_by_key`, `01` FR-DATA-33's three methods) with a persisted seed, and the
  diagnostics MUST record per-fold metrics and their dispersion, not the mean alone."

**Spec ambiguity found while researching, recorded rather than silently resolved (per
`CLAUDE.md` §0):** neither FR-MODEL-53 nor FR-DATA-33 defines what a `temporal` *K*-fold
split means — FR-DATA-33 only defines a two-part cutoff split (`train`/`test`). This plan
resolves it as **contiguous time-ordered blocks**: sort ascending by `time_column`, cut
the sorted row order into `folds` equal-count blocks. This is a genuine design decision
this plan makes, not a fact the spec already stated — Task 1 documents it in the
docstring, and Task 10 carries it into `02-modelling.md` as the amendment that resolves
the gap for future readers.

**Second interaction found, also recorded rather than silently resolved:** `GlmSpec`'s
existing `uncertainty_basis` property (FR-MODEL-99) reads `self.alpha` to decide whether a
fit's standard errors used the plain (unpenalised) information matrix or the
naive-under-penalisation one. Under `select_by="cv"`, `alpha` is pinned to `0.0` (Task
3 — the effective penalty comes from `cv.alphas` instead), so reading `alpha` alone would
report a CV-selected, near-certainly-penalised fit as unpenalised. FR-MODEL-99 predates
CV selection entirely and says nothing about this case. Task 3 treats every `select_by="cv"`
fit as using the naive basis unconditionally — conservative rather than exact, and the
smallest change that keeps `uncertainty_basis` honest without expanding this plan's scope
into FR-MODEL-99 itself. Task 10 carries this into the spec as the amendment.

## Global Constraints

- Ruff line length 100; `mypy --strict` on `packages/` (`CLAUDE.md` §3, §11).
- `pricing-core` stays importable standalone with zero FastAPI/SQLAlchemy/Redis
  dependencies (`CLAUDE.md` §2 — standing architecture rule, do not reopen).
- `model-schema` is the single source of truth for shared data shapes; never define a
  shared shape anywhere else (`CLAUDE.md` §2, ADR-0002).
- Requirement IDs are permanent: never renumber, only append or mark superseded
  (`CLAUDE.md` §5).
- Every test claiming a requirement carries `@pytest.mark.req("FR-MODEL-NN")`, checked by
  `scripts/req-coverage.py` (`CLAUDE.md` §11, §13).
- Model and rating definitions are declarative JSON artifacts, never pickled objects
  (`CLAUDE.md` §2) — `_fit_cv_path` returns data (`CrossValidationDiagnostics`), never a
  fitted estimator.
- Diagnostics are computed once at fit time and read thereafter (FR-MODEL-49); nothing
  added by this plan recomputes on read.
- Money is integer minor units / `Decimal` in the rating path (`CLAUDE.md` §7) — not
  touched by this plan; noted because it is a project-wide constraint, not because any
  task here carries money.
- `docs/contracts/` is generated from `model-schema` and committed; CI fails on drift
  (FR-PLAT-48) — `uv run python scripts/generate-contracts.py --check` must pass after
  Task 4.
- Adding a field to a `ModelSpec` arm bumps `SPEC_HASH_VERSION` in the same commit
  (FR-MODEL-86) — Task 7.
- A new `GlmFitError`/`GbmFitError` code must be registered in
  `backend/src/app/errors.py`'s `MODELLING_ERROR_CODES`, enforced by an AST-parsing test
  that fails otherwise — Task 5.

---

### Task 1: `assign_folds()` — K-fold generalisation of the existing split methods

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/data/splits.py`
- Test: `packages/pricing-core/tests/test_splits.py`

**Interfaces:**
- Consumes: `SplitError`, `METHODS`, `_cumulative`, `_uniform_from_seed`, `_hash_unit` —
  all already defined in `splits.py`.
- Produces: `assign_folds(frame: pl.DataFrame, *, method: str, seed: int, folds: int, key_column: str | None = None, time_column: str | None = None) -> np.ndarray` —
  an `int64` NumPy array the same length as `frame`, each entry in `[0, folds)`. Consumed
  by Task 5's `_fit_cv_path`.

- [ ] **Step 1: Write the failing tests**

Append to `packages/pricing-core/tests/test_splits.py`:

```python
from pricing_core.data.splits import SplitError, assign_folds, assign_parts, partition


@pytest.mark.req("FR-MODEL-53")
def test_two_independent_calls_produce_the_same_fold_assignment() -> None:
    """The property `assign_parts` exists for, carried to folds: two Jobs computing CV for
    the same spec must agree on which rows are held out for fold `i`, and the only thing
    they share is `method`, `seed` and `folds`."""
    frame = _book()
    first = assign_folds(frame, method="random", seed=11, folds=4)
    second = assign_folds(frame, method="random", seed=11, folds=4)
    assert first.tolist() == second.tolist()


@pytest.mark.req("FR-MODEL-53")
def test_a_different_seed_produces_a_different_fold_assignment() -> None:
    frame = _book()
    a = assign_folds(frame, method="random", seed=1, folds=4)
    b = assign_folds(frame, method="random", seed=2, folds=4)
    assert a.tolist() != b.tolist()


@pytest.mark.req("FR-MODEL-53")
def test_every_row_gets_one_of_the_declared_folds() -> None:
    """Coverage, the fold equivalent of `test_the_parts_are_disjoint_and_cover_every_row`:
    a row with no fold is a row `_fit_cv_path` would silently never score or never train
    on, in whichever fold it should have belonged to."""
    frame = _book()
    folds = assign_folds(frame, method="random", seed=5, folds=4)
    assert folds.shape == (frame.height,)
    assert set(folds.tolist()) == {0, 1, 2, 3}
    assert folds.min() >= 0
    assert folds.max() < 4


@pytest.mark.req("FR-MODEL-53")
def test_a_grouped_fold_assignment_keeps_a_policy_whole() -> None:
    """The same leakage bug `assign_parts`'s grouped method exists to prevent, at K folds:
    a policy's twelve monthly rows split across two folds lets a model trained on fold A
    see rows from the very policy fold B holds out."""
    frame = _book()
    folds = assign_folds(frame, method="grouped_by_key", seed=3, folds=4, key_column="policy")
    tagged = frame.with_columns(pl.Series("fold", folds.tolist()))
    per_policy_fold_count = (
        tagged.group_by("policy").agg(pl.col("fold").n_unique().alias("n")).select("n")
    )
    assert per_policy_fold_count["n"].max() == 1


@pytest.mark.req("FR-MODEL-53")
def test_a_temporal_fold_assignment_orders_folds_by_time() -> None:
    """The gap this plan documents and resolves: FR-DATA-33/FR-MODEL-53 define no K-fold
    temporal semantics, so this fixes it as contiguous time-ordered blocks — the earliest
    rows land in fold 0, the latest in the last fold, and a block never straddles a fold
    boundary out of time order."""
    n = 400
    frame = pl.DataFrame({"row": list(range(n)), "day": list(range(n))})
    folds = assign_folds(frame, method="temporal", seed=0, folds=4, time_column="day")
    tagged = frame.with_columns(pl.Series("fold", folds.tolist())).sort("day")
    # Each fold's rows are a contiguous run once sorted by time.
    changes = (tagged["fold"] != tagged["fold"].shift(1)).sum()
    assert changes == 4  # one change per fold boundary, plus the initial "no previous"
    assert tagged["fold"][0] == 0
    assert tagged["fold"][-1] == 3


@pytest.mark.req("FR-MODEL-53")
def test_a_temporal_fold_assignment_without_a_time_column_is_refused() -> None:
    with pytest.raises(SplitError, match="time_column"):
        assign_folds(_book(), method="temporal", seed=1, folds=4)


@pytest.mark.req("FR-MODEL-53")
def test_fewer_than_two_folds_is_refused() -> None:
    """Negative: one fold has no held-out rows for itself to be scored against, and
    `_fit_cv_path` would divide the book into a training set with nothing to validate on."""
    with pytest.raises(SplitError, match="at least 2"):
        assign_folds(_book(), method="random", seed=1, folds=1)


@pytest.mark.req("FR-MODEL-53")
def test_an_unknown_fold_method_is_refused() -> None:
    with pytest.raises(SplitError, match="unknown split method"):
        assign_folds(_book(), method="stratified_by_vibes", seed=1, folds=3)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/pricing-core && uv run pytest tests/test_splits.py -k fold -v`
Expected: FAIL with `ImportError: cannot import name 'assign_folds'`.

- [ ] **Step 3: Write the minimal implementation**

In `packages/pricing-core/src/pricing_core/data/splits.py`, change the module docstring's
list of methods to add a fourth bullet after the `grouped_by_key` one:

```python
* `assign_folds` generalises all three from two named parts to `folds` numbered ones, for
  cross-validation (`02` FR-MODEL-53). K-fold `temporal` has no cutoff to inherit, so it is
  defined here as contiguous time-ordered blocks: sort ascending by `time_column`, cut the
  sorted row order into `folds` equal-count blocks. Neither `01` FR-DATA-33 nor `02`
  FR-MODEL-53 states this — it is this function's own design decision, not an inherited
  fact, and is recorded here for that reason.
```

Change `__all__` to `["SplitError", "assign_folds", "assign_parts", "partition"]`.

Append `assign_folds` after `assign_parts` and before `partition`:

```python
def assign_folds(
    frame: pl.DataFrame,
    *,
    method: str,
    seed: int,
    folds: int,
    key_column: str | None = None,
    time_column: str | None = None,
) -> np.ndarray:
    """The fold index (`0` to `folds - 1`) for every row, aligned to `frame`.

    Generalises `assign_parts` from two named parts to `folds` numbered ones, reusing the
    same seeded draw (`random`), keyed hash (`grouped_by_key`) or time order (`temporal`) —
    so a caller already trusting `assign_parts`'s determinism gets the same guarantee here:
    two independent calls with the same `frame`, `method`, `seed` and `folds` produce the
    same assignment, which is what lets two Jobs, run minutes apart, agree on which rows
    were held out for fold `i` (FR-MODEL-53).
    """
    if method not in METHODS:
        raise SplitError(f"unknown split method {method!r}; expected one of {METHODS}")
    if folds < 2:
        raise SplitError(
            f"folds must be at least 2, got {folds}. One fold has no held-out rows for "
            "itself to be validated against."
        )

    if method == "temporal":
        if not time_column:
            raise SplitError(
                "a temporal fold assignment needs `time_column`. Without it there is no "
                "time to order folds by, and falling back to a random assignment would "
                "record a method the data was not folded by."
            )
        if time_column not in frame.columns:
            raise SplitError(
                f"temporal fold assignment names {time_column!r}, which is not a column"
            )
        order = frame[time_column].arg_sort().to_numpy()
        rank = np.empty(frame.height, dtype=np.int64)
        rank[order] = np.arange(frame.height, dtype=np.int64)
        return np.minimum((rank * folds) // frame.height, folds - 1).astype(np.int64)

    if method == "grouped_by_key":
        if not key_column:
            raise SplitError("a grouped_by_key fold assignment needs `key_column`")
        if key_column not in frame.columns:
            raise SplitError(
                f"grouped fold assignment names {key_column!r}, which is not a column"
            )
        u = _hash_unit(frame[key_column].to_list(), seed)
    else:
        u = _uniform_from_seed(frame.height, seed)

    # A draw of exactly 1.0 is impossible from `random()`, but the guard costs nothing and
    # matches `assign_parts`'s own edge case: a row must land in the last fold rather than
    # in none.
    return np.minimum((u * folds).astype(np.int64), folds - 1)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd packages/pricing-core && uv run pytest tests/test_splits.py -v`
Expected: PASS, all tests including the 8 pre-existing ones.

- [ ] **Step 5: Commit**

```bash
git add packages/pricing-core/src/pricing_core/data/splits.py packages/pricing-core/tests/test_splits.py
git commit -m "feat(pricing-core): assign_folds — K-fold generalisation of the split methods (FR-MODEL-53)"
```

---

### Task 2: `CrossValidationDiagnostics` — the persisted CV shape on `model-schema`

**Files:**
- Modify: `packages/model-schema/src/model_schema/diagnostics.py`
- Test: `packages/model-schema/tests/test_cross_validation_diagnostics.py` (new file)

**Interfaces:**
- Consumes: `BaseModel`, `ConfigDict`, `Field`, `model_validator` (already imported in
  `diagnostics.py`); `PartitionDiagnostics`, `UniversalDiagnostics`, `ComplexityDiagnostic`,
  `Weighting`, `Diagnostics` (already defined in `diagnostics.py`).
- Produces: `CvPathPoint(alpha: float, mean_score: float, std_score: float)`,
  `CvFoldMetric(fold: int, rows: int, score: float)`,
  `CrossValidationDiagnostics(method: str, seed: int, folds: int, metric: str, selected_alpha: float, path: tuple[CvPathPoint, ...], fold_metrics: tuple[CvFoldMetric, ...])`,
  and `Diagnostics.cross_validation: CrossValidationDiagnostics | None`. Consumed by
  Task 3 (re-export), Task 4 (package `__init__.py` export), Task 5
  (`pricing_core.modelling.glm` constructs `CrossValidationDiagnostics`), Task 6 (the
  backend handler threads it into `Diagnostics`).

- [ ] **Step 1: Write the failing tests**

Create `packages/model-schema/tests/test_cross_validation_diagnostics.py`:

```python
"""FR-MODEL-20/FR-MODEL-53: the cross-validated penalty path, persisted on `Diagnostics`.

FR-MODEL-20 asks for the full scanned path, not only the alpha selected. FR-MODEL-53 asks
for per-fold metrics **and their dispersion**, not the mean alone — `path` carries the
first (`std_score` is the path's own dispersion across folds, at every alpha scanned),
`fold_metrics` carries the second (the raw per-fold scores, at the alpha actually
selected).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from model_schema import (
    ComplexityDiagnostic,
    CrossValidationDiagnostics,
    CvFoldMetric,
    CvPathPoint,
    Diagnostics,
    PartitionDiagnostics,
    UniversalDiagnostics,
    Weighting,
    new_uuid7,
)


def _path(*alphas: float) -> tuple[CvPathPoint, ...]:
    return tuple(
        CvPathPoint(alpha=a, mean_score=0.5 - 0.01 * i, std_score=0.02)
        for i, a in enumerate(alphas)
    )


def _fold_metrics(n: int) -> tuple[CvFoldMetric, ...]:
    return tuple(CvFoldMetric(fold=i, rows=100, score=0.48 + 0.001 * i) for i in range(n))


@pytest.mark.req("FR-MODEL-20")
def test_the_path_carries_every_scanned_alpha() -> None:
    cv = CrossValidationDiagnostics(
        method="random", seed=7, folds=3, metric="deviance",
        selected_alpha=0.01, path=_path(0.0, 0.01, 0.1), fold_metrics=_fold_metrics(3),
    )
    assert [p.alpha for p in cv.path] == [0.0, 0.01, 0.1]
    assert cv.selected_alpha == 0.01


@pytest.mark.req("FR-MODEL-20")
def test_a_selected_alpha_that_is_not_on_the_path_is_refused() -> None:
    """Negative: the selection must be a point the path actually scored, or the artifact
    claims a decision that was never made."""
    with pytest.raises(ValidationError, match="not one of the path"):
        CrossValidationDiagnostics(
            method="random", seed=7, folds=3, metric="deviance",
            selected_alpha=0.5, path=_path(0.0, 0.01, 0.1), fold_metrics=_fold_metrics(3),
        )


@pytest.mark.req("FR-MODEL-53")
def test_fold_metrics_carry_dispersion_not_only_the_mean() -> None:
    """The requirement's own phrase: per-fold metrics, not the mean alone."""
    metrics = _fold_metrics(4)
    cv = CrossValidationDiagnostics(
        method="grouped_by_key", seed=1, folds=4, metric="deviance",
        selected_alpha=0.1, path=_path(0.0, 0.1), fold_metrics=metrics,
    )
    assert len(cv.fold_metrics) == 4
    assert len({m.score for m in cv.fold_metrics}) > 1, "fold scores are not forced equal"


@pytest.mark.req("FR-MODEL-53")
def test_fold_metrics_missing_a_declared_fold_is_refused() -> None:
    """Negative: `folds=4` promises four folds' worth of dispersion; three is a fold that
    was never scored, silently dropped from the very number the requirement asks for."""
    with pytest.raises(ValidationError, match="never scored"):
        CrossValidationDiagnostics(
            method="random", seed=1, folds=4, metric="deviance",
            selected_alpha=0.1, path=_path(0.0, 0.1), fold_metrics=_fold_metrics(3),
        )


@pytest.mark.req("FR-MODEL-53")
def test_diagnostics_carries_cross_validation_when_the_fit_selected_by_cv() -> None:
    """`Diagnostics.cross_validation` was declared and always `None` (2026-08-18's note on
    the class); this is the slice that populates it, so the field must round-trip inside
    the artifact it was declared for."""
    partition = PartitionDiagnostics(
        weighting=Weighting.EXPOSURE, rows=1000, ae_overall=1.02, gini=0.3, gini_normalised=0.6,
    )
    diagnostics = Diagnostics(
        id=new_uuid7(),
        model_id=new_uuid7(),
        computed_at=datetime.now(UTC),
        universal=UniversalDiagnostics(train=partition, holdout=partition),
        complexity=ComplexityDiagnostic(factor_count=2, parameter_count=3),
        cross_validation=CrossValidationDiagnostics(
            method="random", seed=7, folds=3, metric="deviance",
            selected_alpha=0.1, path=_path(0.0, 0.1, 1.0), fold_metrics=_fold_metrics(3),
        ),
    )
    assert diagnostics.cross_validation is not None
    assert diagnostics.cross_validation.selected_alpha == 0.1
    dumped = diagnostics.model_dump(mode="json")
    assert Diagnostics.model_validate(dumped) == diagnostics


@pytest.mark.req("FR-MODEL-49")
def test_diagnostics_without_cv_still_carries_none() -> None:
    """FR-MODEL-49: computed once at fit time. A fixed-alpha GLM or a GBM was never
    cross-validated, and `None` is the honest reading of that — not an empty path
    standing in for a scan that never ran."""
    partition = PartitionDiagnostics(
        weighting=Weighting.EXPOSURE, rows=1000, ae_overall=1.02, gini=0.3, gini_normalised=0.6,
    )
    diagnostics = Diagnostics(
        id=new_uuid7(),
        model_id=new_uuid7(),
        computed_at=datetime.now(UTC),
        universal=UniversalDiagnostics(train=partition, holdout=partition),
        complexity=ComplexityDiagnostic(factor_count=2, parameter_count=3),
    )
    assert diagnostics.cross_validation is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/model-schema && uv run pytest tests/test_cross_validation_diagnostics.py -v`
Expected: FAIL with `ImportError: cannot import name 'CrossValidationDiagnostics'`.

- [ ] **Step 3: Write the minimal implementation**

In `packages/model-schema/src/model_schema/diagnostics.py`, update `__all__` to:

```python
__all__ = [
    "AeCell",
    "CalibrationBin",
    "ComplexityDiagnostic",
    "CrossValidationDiagnostics",
    "CvFoldMetric",
    "CvPathPoint",
    "Diagnostics",
    "FeatureImportance",
    "GbmDiagnostics",
    "GbmEvalPoint",
    "GlmDiagnostics",
    "LiftBin",
    "MonotonicityCheck",
    "PartialDependence",
    "PartialDependencePoint",
    "PartitionDiagnostics",
    "PermutationImportance",
    "QuantileCrossing",
    "ResidualSummary",
    "TypeIIITest",
    "UniversalDiagnostics",
    "Weighting",
]
```

Immediately above the existing `class Diagnostics(BaseModel):` definition, insert:

```python
class CvPathPoint(BaseModel):
    """One scanned alpha's aggregate cross-validated score (FR-MODEL-20).

    `std_score` is this alpha's dispersion across every fold — the curve FR-MODEL-20's
    "full path, not only the alpha selected" is. `CrossValidationDiagnostics.fold_metrics`
    carries the *unaggregated* per-fold scores FR-MODEL-53 also asks for, but only at the
    selected alpha: recording every fold at every alpha would multiply storage by
    `len(alphas)` for a curve this point's `std_score` already summarises.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    alpha: float = Field(ge=0.0)
    mean_score: float
    std_score: float = Field(ge=0.0)


class CvFoldMetric(BaseModel):
    """One fold's held-out score at the selected alpha (FR-MODEL-53).

    "Per-fold metrics and their dispersion... not the mean alone" is the requirement's own
    phrase — this is the *and*: `CrossValidationDiagnostics.path`'s `std_score` at the
    selected alpha is the dispersion computed from exactly these numbers, so the two report
    one fact two ways rather than two facts that could drift apart.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    fold: int = Field(ge=0)
    rows: int = Field(ge=0)
    score: float


class CrossValidationDiagnostics(BaseModel):
    """The penalty path and the selected alpha's fold dispersion (FR-MODEL-20, FR-MODEL-53).

    Populated only when the fit's `GlmSpec.select_by == "cv"`; `Diagnostics.cross_validation`
    is `None` for every fixed-alpha GLM and every GBM — the honest reading of "this fit was
    not cross-validated" rather than an empty path standing in for one (FR-MODEL-49: a
    diagnostic is computed once, at fit time, from what the fit actually did).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: `01` FR-DATA-33's fold-construction method, generalised from two parts to `folds` by
    #: `pricing_core.data.splits.assign_folds`.
    method: str
    #: The seed `assign_folds` was called with — `GlmSpec.seed`, copied here so the fold
    #: assignment is reproducible from this artifact alone, with no join back to the spec.
    seed: int
    folds: int = Field(ge=2)
    #: The scoring metric's name. Always `"deviance"` today — the fitted family's own
    #: deviance — recorded rather than assumed, so a reader is not left inferring which
    #: metric a number on the path was computed from.
    metric: str
    selected_alpha: float = Field(ge=0.0)
    path: tuple[CvPathPoint, ...]
    fold_metrics: tuple[CvFoldMetric, ...]

    @model_validator(mode="after")
    def _the_selected_alpha_is_a_point_on_the_path(self) -> CrossValidationDiagnostics:
        alphas = {p.alpha for p in self.path}
        if self.selected_alpha not in alphas:
            raise ValueError(
                f"selected_alpha={self.selected_alpha} is not one of the path's alphas "
                f"{sorted(alphas)}. The selection must be a point the path actually scored."
            )
        return self

    @model_validator(mode="after")
    def _every_fold_is_represented_at_the_selected_alpha(self) -> CrossValidationDiagnostics:
        seen = {m.fold for m in self.fold_metrics}
        expected = set(range(self.folds))
        if seen != expected:
            raise ValueError(
                f"fold_metrics covers folds {sorted(seen)}, expected {sorted(expected)}. A "
                "fold's dispersion cannot include a fold that was never scored."
            )
        return self
```

Then change `Diagnostics.cross_validation`'s field declaration from:

```python
    cross_validation: None = None
```

to:

```python
    cross_validation: CrossValidationDiagnostics | None = None
```

And update the class docstring paragraph that currently reads:

```
    `cross_validation` is still declared and always `None`: FR-MODEL-53 computes it **at fit
    time**, so this artifact is where it will land, and its producer is a later slice.
```

to:

```
    `cross_validation` is populated iff the fit's `GlmSpec.select_by == "cv"`
    (FR-MODEL-20, FR-MODEL-53, the regularisation-and-CV slice, 2026-08-21) and `None`
    otherwise — a fixed-alpha GLM or a GBM was never cross-validated, and `None` is the
    honest reading of that.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd packages/model-schema && uv run pytest tests/test_cross_validation_diagnostics.py -v`
Expected: FAIL still — `CrossValidationDiagnostics` etc. are defined in `diagnostics.py`
but not yet re-exported from `model_schema/__init__.py`. This is expected; Task 4 fixes
it. Confirm the failure is now an `ImportError` pointing at the *package* `__init__`,
not at `diagnostics.py`, by running:

Run: `cd packages/model-schema && uv run python -c "from model_schema.diagnostics import CrossValidationDiagnostics, CvFoldMetric, CvPathPoint; print('ok')"`
Expected: `ok` — proves Step 3's classes are correct before Task 4 wires the export.

- [ ] **Step 5: Commit**

```bash
git add packages/model-schema/src/model_schema/diagnostics.py packages/model-schema/tests/test_cross_validation_diagnostics.py
git commit -m "feat(model-schema): CrossValidationDiagnostics — the CV path and fold dispersion shape (FR-MODEL-20, FR-MODEL-53)"
```

(The test file still fails to import until Task 4 lands; that is expected and the next
task fixes it immediately. Do not skip Step 4's diagnostic check.)

---

### Task 3: `GlmCvSpec` and `GlmSpec.select_by`/`GlmSpec.cv`

**Files:**
- Modify: `packages/model-schema/src/model_schema/modelling.py`
- Test: `packages/model-schema/tests/test_glm_cv_spec.py` (new file)

**Interfaces:**
- Consumes: `Literal`, `BaseModel`, `ConfigDict`, `Field`, `model_validator` (already
  imported in `modelling.py`); `GlmSpec` (already defined there, being extended).
- Produces: `GlmCvSpec(method: Literal["random", "temporal", "grouped_by_key"] = "random", folds: int = 5, alphas: tuple[float, ...] = (0.0, 0.001, 0.01, 0.1, 1.0), key_column: str | None = None, time_column: str | None = None)`,
  `GlmSpec.select_by: Literal["fixed", "cv"] = "fixed"`, `GlmSpec.cv: GlmCvSpec | None = None`.
  Consumed by Task 4 (package export), Task 5 (`fit_glm` reads `spec.select_by`/`spec.cv`),
  Task 7 (`spec_hash` version bump), Task 8 (integration test constructs a `GlmCvSpec`).

- [ ] **Step 1: Write the failing tests**

Create `packages/model-schema/tests/test_glm_cv_spec.py`:

```python
"""FR-MODEL-20/FR-MODEL-53: the documented penalty path and CV selection on `GlmSpec`."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from model_schema import GlmCvSpec, GlmSpec, OffsetSpec


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-20")
def test_a_fixed_alpha_spec_needs_no_cv_block() -> None:
    spec = _spec(alpha=0.1, l1_ratio=0.5)
    assert spec.select_by == "fixed"
    assert spec.cv is None


@pytest.mark.req("FR-MODEL-53")
def test_cv_selection_declares_its_cv_spec() -> None:
    spec = _spec(select_by="cv", cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.1, 1.0)))
    assert spec.cv is not None
    assert spec.cv.folds == 4
    assert spec.alpha == 0.0


@pytest.mark.req("FR-MODEL-53")
def test_cv_selection_without_a_cv_block_is_refused() -> None:
    """Negative: `select_by='cv'` names a scan with nothing to scan."""
    with pytest.raises(ValidationError, match="cv is not set"):
        _spec(select_by="cv")


@pytest.mark.req("FR-MODEL-53")
def test_a_cv_block_under_fixed_selection_is_refused() -> None:
    """Negative: a scanned path with nothing selecting from it describes a fit that was
    never asked to run it — silently ignoring `cv` would let a caller believe their model
    was cross-validated when `select_by` never asked for that."""
    with pytest.raises(ValidationError, match="select_by='fixed'"):
        _spec(cv=GlmCvSpec())


@pytest.mark.req("FR-MODEL-53")
def test_cv_selection_with_a_nonzero_fixed_alpha_is_refused() -> None:
    """Negative: two answers to "how penalised is this fit" — a fixed `alpha` and a
    scanned `cv.alphas` — and only one of them is ever read under CV selection."""
    with pytest.raises(ValidationError, match="alpha is non-zero"):
        _spec(select_by="cv", alpha=0.2, cv=GlmCvSpec())


@pytest.mark.req("FR-MODEL-20")
def test_a_path_with_fewer_than_two_alphas_is_refused() -> None:
    """Negative: one alpha is a fixed fit, not a path to select from."""
    with pytest.raises(ValidationError, match="at least 2"):
        GlmCvSpec(alphas=(0.1,))


@pytest.mark.req("FR-MODEL-20")
def test_a_path_with_a_repeated_alpha_is_refused() -> None:
    with pytest.raises(ValidationError, match="repeats"):
        GlmCvSpec(alphas=(0.1, 0.1, 0.5))


@pytest.mark.req("FR-MODEL-53")
def test_a_grouped_cv_needs_its_key_column() -> None:
    with pytest.raises(ValidationError, match="key_column"):
        GlmCvSpec(method="grouped_by_key")


@pytest.mark.req("FR-MODEL-53")
def test_a_temporal_cv_needs_its_time_column() -> None:
    with pytest.raises(ValidationError, match="time_column"):
        GlmCvSpec(method="temporal")


@pytest.mark.req("FR-MODEL-99")
def test_cv_selection_uses_the_naive_uncertainty_basis() -> None:
    """FR-MODEL-99's `uncertainty_basis` reads `alpha`, and CV pins `alpha` to 0.0 — so
    without this, a CV-selected (near-certainly penalised) fit would report the plain
    information-matrix basis a genuinely unpenalised fit gets. Recorded in this plan's
    header as an interaction FR-MODEL-99 does not itself cover."""
    from model_schema.diagnostics import UncertaintyBasis

    spec = _spec(select_by="cv", cv=GlmCvSpec())
    assert spec.uncertainty_basis is UncertaintyBasis.UNPENALISED_INFORMATION_MATRIX
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/model-schema && uv run pytest tests/test_glm_cv_spec.py -v`
Expected: FAIL with `ImportError: cannot import name 'GlmCvSpec'`.

- [ ] **Step 3: Write the minimal implementation**

In `packages/model-schema/src/model_schema/modelling.py`, insert `GlmCvSpec` immediately
before `class GlmSpec(ModelSpecCommon):`:

```python
class GlmCvSpec(BaseModel):
    """FR-MODEL-20/FR-MODEL-53: the cross-validated penalty path `GlmSpec.cv` carries when
    `select_by == "cv"`.

    `seed` is **not** duplicated here: the seed that makes fold assignment reproducible is
    `ModelSpecCommon.seed` — the one seed the spec already carries and already versions
    into `spec_hash`. A second seed field on this nested block would let the two disagree,
    which is the shape-defined-twice trap `CLAUDE.md` §2 names.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: `01` FR-DATA-33's three fold-construction methods, generalised to K folds by
    #: `pricing_core.data.splits.assign_folds` (FR-MODEL-53).
    method: Literal["random", "temporal", "grouped_by_key"] = "random"
    folds: int = Field(default=5, ge=2)
    #: The elastic-net penalty strengths scanned (FR-MODEL-20). `l1_ratio` is fixed by
    #: `GlmSpec.l1_ratio` for every point on the path — only the overall strength is
    #: scanned, mirroring `glum`'s own `GeneralizedLinearRegressorCV` convention.
    alphas: tuple[float, ...] = (0.0, 0.001, 0.01, 0.1, 1.0)
    key_column: str | None = None
    time_column: str | None = None

    @model_validator(mode="after")
    def _the_path_has_at_least_two_distinct_points(self) -> GlmCvSpec:
        if len(self.alphas) < 2:
            raise ValueError(
                f"cv.alphas has {len(self.alphas)} point(s); at least 2 are needed for a "
                "path to select from — one alpha is a fixed fit, not a cross-validation."
            )
        if any(a < 0.0 for a in self.alphas):
            raise ValueError("cv.alphas contains a negative penalty strength")
        if len(set(self.alphas)) != len(self.alphas):
            raise ValueError(f"cv.alphas repeats a value: {self.alphas}")
        return self

    @model_validator(mode="after")
    def _the_method_names_what_it_needs(self) -> GlmCvSpec:
        if self.method == "grouped_by_key" and not self.key_column:
            raise ValueError(
                "cv.method is 'grouped_by_key' but cv.key_column is not set — without it "
                "there is no key to keep whole across folds."
            )
        if self.method == "temporal" and not self.time_column:
            raise ValueError(
                "cv.method is 'temporal' but cv.time_column is not set — without it there "
                "is no time to order folds by."
            )
        return self
```

In `GlmSpec`, add two fields immediately after `l1_ratio: float = Field(default=0.0, ge=0.0, le=1.0)`:

```python
    #: FR-MODEL-20/FR-MODEL-53. `"fixed"` fits once at `alpha`; `"cv"` scans `cv.alphas`
    #: and selects the alpha with the lowest mean cross-validated deviance instead.
    select_by: Literal["fixed", "cv"] = "fixed"
    #: Set iff `select_by == "cv"` (checked below); `None` under `"fixed"` selection.
    cv: GlmCvSpec | None = None
```

Add a fourth `@model_validator(mode="after")` method to `GlmSpec`, after
`_a_surrogate_says_so_in_both_places`:

```python
    @model_validator(mode="after")
    def _cv_selection_declares_its_cv_spec_and_nothing_else_does(self) -> GlmSpec:
        """FR-MODEL-20/FR-MODEL-53: `select_by`, `cv` and `alpha` must agree.

        `alpha` is refused non-zero under `select_by="cv"` on purpose: the effective
        penalty comes from `cv.alphas` instead, and a spec carrying both a fixed `alpha`
        and a scanned path has two answers to "how penalised is this fit" — one from a
        field nobody reads under CV selection, which is worse than an empty one.
        """
        if self.select_by == "cv":
            if self.cv is None:
                raise ValueError(
                    "select_by='cv' but cv is not set (FR-MODEL-20/FR-MODEL-53). "
                    "Cross-validation needs a path to scan and a fold strategy to scan "
                    "it with."
                )
            if self.alpha != 0.0:
                raise ValueError(
                    "select_by='cv' but alpha is non-zero. The effective penalty comes "
                    "from cv.alphas under CV selection; a fixed alpha here would be a "
                    "second, unread answer to how penalised this fit is."
                )
        elif self.cv is not None:
            raise ValueError(
                "cv is set but select_by='fixed'. A scanned path with nothing selecting "
                "from it describes a fit that was never asked to run it."
            )
        return self
```

Change the `uncertainty_basis` property's `return` statement from:

```python
        return (
            UncertaintyBasis.UNPENALISED_INFORMATION_MATRIX
            if self.alpha > 0.0
            else UncertaintyBasis.INFORMATION_MATRIX
        )
```

to:

```python
        # FR-MODEL-20/FR-MODEL-53 interaction, noted rather than silently resolved (this
        # plan's header carries the reasoning): under `select_by == "cv"`, `alpha` is
        # pinned to 0.0 by `_cv_selection_declares_its_cv_spec_and_nothing_else_does`
        # because the effective penalty comes from `cv.alphas` instead — so `alpha` alone
        # cannot answer this question for a CV fit. Treated as penalised unconditionally:
        # the elastic-net grid FR-MODEL-20 scans is a path that starts at zero and moves
        # away from it, so a fit that lands back on exactly zero is the rare point on the
        # path rather than the typical one, and the cost of the cautious label there is a
        # display caveat, not a wrong number.
        return (
            UncertaintyBasis.UNPENALISED_INFORMATION_MATRIX
            if self.alpha > 0.0 or self.select_by == "cv"
            else UncertaintyBasis.INFORMATION_MATRIX
        )
```

Add `"GlmCvSpec"` to `__all__`, alphabetically between `"GbmSpec"` and `"GlmFitResult"`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd packages/model-schema && uv run pytest tests/test_glm_cv_spec.py -v`
Expected: still FAIL on import — `GlmCvSpec` is defined in `modelling.py` but not yet
re-exported from `model_schema/__init__.py`. Confirm with:

Run: `cd packages/model-schema && uv run python -c "from model_schema.modelling import GlmCvSpec, GlmSpec; print('ok')"`
Expected: `ok`. Task 4 wires the package-level export next.

- [ ] **Step 5: Commit**

```bash
git add packages/model-schema/src/model_schema/modelling.py packages/model-schema/tests/test_glm_cv_spec.py
git commit -m "feat(model-schema): GlmCvSpec and GlmSpec.select_by/cv — the documented penalty path (FR-MODEL-20, FR-MODEL-53)"
```

---

### Task 4: Export the new types from `model_schema/__init__.py`

**Files:**
- Modify: `packages/model-schema/src/model_schema/__init__.py`

**Interfaces:**
- Consumes: `CrossValidationDiagnostics`, `CvFoldMetric`, `CvPathPoint` (Task 2's
  `diagnostics.py`); `GlmCvSpec` (Task 3's `modelling.py`).
- Produces: all four importable as `from model_schema import ...`, which every later task
  (and Task 2/3's tests, already written) depend on.

- [ ] **Step 1: Verify the currently-failing imports**

Run: `cd packages/model-schema && uv run pytest tests/test_cross_validation_diagnostics.py tests/test_glm_cv_spec.py -v`
Expected: FAIL, both files, `ImportError` from `model_schema` (the package), not from
`model_schema.diagnostics` / `model_schema.modelling` (which Tasks 2 and 3 already proved
correct).

- [ ] **Step 2: Add the imports and exports**

In `packages/model-schema/src/model_schema/__init__.py`, find the `from model_schema.diagnostics import (` block (confirmed at line 59, current content read fresh: `AeCell, CalibrationBin, ComplexityDiagnostic, Diagnostics, FeatureImportance, GbmDiagnostics, GbmEvalPoint, GlmDiagnostics, LiftBin, MonotonicityCheck, PartialDependence, PartialDependencePoint, PartitionDiagnostics, PermutationImportance, QuantileCrossing, ResidualSummary, TypeIIITest, UniversalDiagnostics, Weighting`). Insert the three new names alphabetically: `CrossValidationDiagnostics` after `ComplexityDiagnostic,`, then `CvFoldMetric,` and `CvPathPoint,` — both of which sort before `Diagnostics` (`"Cv" < "Di"`) — immediately after `CrossValidationDiagnostics,` and before `Diagnostics,`. The full block becomes:

```python
from model_schema.diagnostics import (
    AeCell,
    CalibrationBin,
    ComplexityDiagnostic,
    CrossValidationDiagnostics,
    CvFoldMetric,
    CvPathPoint,
    Diagnostics,
    FeatureImportance,
    GbmDiagnostics,
    GbmEvalPoint,
    GlmDiagnostics,
    LiftBin,
    MonotonicityCheck,
    PartialDependence,
    PartialDependencePoint,
    PartitionDiagnostics,
    PermutationImportance,
    QuantileCrossing,
    ResidualSummary,
    TypeIIITest,
    UniversalDiagnostics,
    Weighting,
)
```

(This mirrors `diagnostics.py`'s own `__all__` order exactly — copy that ordering rather
than re-deriving it, since Task 2 already fixed it there.)

Find the `from model_schema.modelling import (` block. Add `GlmCvSpec,` immediately
before `GlmFitResult,` (alphabetically: `Gbm... < GlmCvSpec < GlmFitResult < GlmSpec`).

In the module's `__all__` list (a flat alphabetical list of every re-exported name), add:
- `"CrossValidationDiagnostics"` — immediately after `"CredibilityModel"`, before
  `"Currency"`.
- `"CvFoldMetric"` and `"CvPathPoint"` — immediately after `"CustomObjective"`, before
  `"DataDictionaryEntry"`, in that order (`CvFoldMetric` < `CvPathPoint`).
- `"GlmCvSpec"` — immediately after `"GlmApproximation"`, before `"GlmDiagnostics"`.

- [ ] **Step 3: Run tests to verify they pass**

Run: `cd packages/model-schema && uv run pytest tests/test_cross_validation_diagnostics.py tests/test_glm_cv_spec.py -v`
Expected: PASS, all tests in both files.

Run: `cd packages/model-schema && uv run pytest -q`
Expected: PASS — the whole package's existing suite is undisturbed by an additive export
change.

Run: `cd packages/model-schema && uv run mypy --strict src/`
Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add packages/model-schema/src/model_schema/__init__.py
git commit -m "feat(model-schema): export CrossValidationDiagnostics, CvFoldMetric, CvPathPoint, GlmCvSpec"
```

---

### Task 5: `_fit_cv_path()` in `pricing_core.modelling.glm` — the penalty path reaching `glum`

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/modelling/glm.py`
- Modify: `backend/src/app/errors.py`
- Test: `packages/pricing-core/tests/test_glm_cv.py` (new file)

**Interfaces:**
- Consumes: `assign_folds` (Task 1, `pricing_core.data.splits`); `deviance` (already in
  `pricing_core.modelling.diagnostics`, `deviance(y, mu, *, family, power=1.5, weights=None) -> float`);
  `CrossValidationDiagnostics`, `CvFoldMetric`, `CvPathPoint`, `GlmCvSpec` (Task 2/3/4,
  `model_schema`); the existing `GlmFitError`, `GlmSpec`, `fit_glm`'s already-built `x`,
  `response`, `offset`, `weights`, `family`, `link` local variables.
- Produces: `GlmFit.cv: CrossValidationDiagnostics | None` (new field on the existing
  dataclass); `fit_glm()`'s behaviour under `spec.select_by == "cv"`. Consumed by Task 6
  (the backend handler reads `glm_fit.cv`).

- [ ] **Step 1: Write the failing tests**

Create `packages/pricing-core/tests/test_glm_cv.py`. Reuse the fixture pattern from
`packages/pricing-core/tests/test_glm.py` (`_factor()` returns a `Factor`, `_frequency_data()`
returns a Poisson book, `_spec()` builds a `GlmSpec`) — read that file's fixtures before
writing this one; do not redefine them differently.

```python
"""FR-MODEL-20/FR-MODEL-53: the elastic-net penalty path reaching `glum`, end to end.

Not a type-level test — a feature four sites agreeing on a shape can still not work
(`.claude/skills/python-test`), and the site that matters here is the actual refit against
`glum`, once per fold per alpha.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import Factor, FactorType, GlmCvSpec, GlmSpec, OffsetSpec
from pricing_core.modelling.glm import GlmFitError, fit_glm


def _factor(slug: str, column: str) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=uuid4(), version=1,
        type=FactorType.IDENTITY, source_columns=(column,),
    )


def _frequency_data(n: int = 400) -> pl.DataFrame:
    """A Poisson book with a real urban/rural signal — the same shape `test_glm.py` uses,
    large enough that 4 folds each carry a usable number of rows."""
    return pl.DataFrame(
        {
            "policy": [f"P{i}" for i in range(n)],
            "day": list(range(n)),
            "exposure_years": [1.0] * n,
            "area": ["urban" if i % 4 == 0 else "rural" for i in range(n)],
            "claim_count": [2 if i % 4 == 0 else 1 for i in range(n)],
        }
    )


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "factors": (),
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-20")
def test_cv_selection_fits_and_persists_the_full_path() -> None:
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.01, 0.1, 1.0)),
    )
    fit = fit_glm(data, spec, factors, seed=spec.seed)
    assert fit.cv is not None
    assert [p.alpha for p in fit.cv.path] == [0.0, 0.01, 0.1, 1.0]
    assert fit.cv.selected_alpha in {0.0, 0.01, 0.1, 1.0}
    assert fit.cv.folds == 4
    assert fit.cv.method == "random"
    assert fit.cv.seed == spec.seed
    # The estimator was actually refitted at the selected alpha, not left at the default.
    assert fit.result.coefficients


@pytest.mark.req("FR-MODEL-53")
def test_cv_selection_persists_per_fold_dispersion_at_the_selected_alpha() -> None:
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.1, 1.0)),
    )
    fit = fit_glm(data, spec, factors, seed=spec.seed)
    assert fit.cv is not None
    assert {m.fold for m in fit.cv.fold_metrics} == {0, 1, 2, 3}
    assert sum(m.rows for m in fit.cv.fold_metrics) == data.height
    # FR-MODEL-53: dispersion, not only the mean.
    assert len({round(m.score, 10) for m in fit.cv.fold_metrics}) > 1


@pytest.mark.req("FR-MODEL-53")
def test_a_grouped_cv_keeps_a_policy_whole_across_folds() -> None:
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="grouped_by_key", folds=4, key_column="policy", alphas=(0.0, 0.1)),
    )
    fit = fit_glm(data, spec, factors, seed=spec.seed)
    assert fit.cv is not None
    assert fit.cv.method == "grouped_by_key"


@pytest.mark.req("FR-MODEL-53")
def test_a_temporal_cv_orders_folds_by_time() -> None:
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="temporal", folds=4, time_column="day", alphas=(0.0, 0.1)),
    )
    fit = fit_glm(data, spec, factors, seed=spec.seed)
    assert fit.cv is not None
    assert fit.cv.method == "temporal"


@pytest.mark.req("FR-MODEL-53")
def test_two_fits_with_the_same_seed_select_the_same_alpha() -> None:
    """Round-trip / reproducibility: `_fit_cv_path`'s fold assignment is a pure function of
    the seed, so two fits of the identical spec over the identical data must agree — the
    property `assign_folds` (Task 1) exists for, carried all the way to the selection."""
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.01, 0.1, 1.0)),
        seed=42,
    )
    first = fit_glm(data, spec, factors, seed=spec.seed)
    second = fit_glm(data, spec, factors, seed=spec.seed)
    assert first.cv is not None and second.cv is not None
    assert first.cv.selected_alpha == second.cv.selected_alpha
    assert [p.mean_score for p in first.cv.path] == [p.mean_score for p in second.cv.path]


@pytest.mark.req("FR-MODEL-53")
def test_more_folds_than_rows_in_a_group_is_refused() -> None:
    """Negative: `GLM_CV_FOLD_EMPTY`. A grouped CV over few distinct keys with `folds` set
    higher than the key count leaves some fold with no held-out rows at all — a fold that
    cannot be scored, silently skipped, is a dispersion computed over fewer folds than
    `folds` claims."""
    data = pl.DataFrame(
        {
            "policy": ["P1"] * 50 + ["P2"] * 50,
            "day": list(range(100)),
            "exposure_years": [1.0] * 100,
            "area": ["urban" if i % 2 == 0 else "rural" for i in range(100)],
            "claim_count": [1] * 100,
        }
    )
    factors = (_factor("area", "area"),)
    spec = _spec(
        factors=(factors[0].id,),
        select_by="cv",
        cv=GlmCvSpec(method="grouped_by_key", folds=5, key_column="policy", alphas=(0.0, 0.1)),
    )
    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, spec, factors, seed=spec.seed)
    assert refused.value.code == "GLM_CV_FOLD_EMPTY"


@pytest.mark.req("FR-MODEL-20")
def test_a_fixed_alpha_fit_still_carries_no_cv_diagnostics() -> None:
    """Negative, the other direction: `select_by='fixed'` (the default) must not
    accidentally run or report a CV path — `fit.cv` stays `None`."""
    data = _frequency_data()
    factors = (_factor("area", "area"),)
    spec = _spec(factors=(factors[0].id,), alpha=0.05, l1_ratio=0.5)
    fit = fit_glm(data, spec, factors, seed=spec.seed)
    assert fit.cv is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/pricing-core && uv run pytest tests/test_glm_cv.py -v`
Expected: FAIL — `AttributeError: 'GlmFit' object has no attribute 'cv'` (or a `TypeError`
from `GlmSpec(select_by=...)` if Task 3/4 are not yet merged; confirm Tasks 1-4 are
committed first).

- [ ] **Step 3: Write the minimal implementation**

In `backend/src/app/errors.py`, add a new code to `MODELLING_ERROR_CODES`, immediately
after the existing `"METRIC_NOT_FITTABLE",` line and before the closing `}`:

```python
        # The regularisation-and-CV slice, 2026-08-21 (FR-MODEL-20, FR-MODEL-53). Raised
        # by `_fit_cv_path` when a fold has no held-out rows (or no training rows) at some
        # alpha on the scanned path — `key_column`/`time_column` skew that a fold count
        # chosen against the whole book does not guarantee against, per fold.
        "GLM_CV_FOLD_EMPTY",
```

In `packages/pricing-core/src/pricing_core/modelling/glm.py`:

Add `import math` to the top-of-file imports (alphabetically, after `import json` and
before `import time`).

Change the `from model_schema import (` block to:

```python
from model_schema import (
    Banding,
    BlobRef,
    Coefficient,
    CrossValidationDiagnostics,
    CvFoldMetric,
    CvPathPoint,
    Factor,
    GlmCvSpec,
    GlmFitResult,
    GlmSpec,
    Grouping,
    RelativityLevel,
)
```

Add a new import line immediately after it:

```python
from pricing_core.data.splits import assign_folds
from pricing_core.modelling.diagnostics import deviance
from pricing_core.modelling.factors import FactorMatrix, resolve_factors
```

(`resolve_factors`/`FactorMatrix` stay where they were; the two new lines are inserted
above that existing one, keeping the block alphabetically sorted by module path.)

Change the `GlmFit` dataclass to add a fourth field:

```python
@dataclass(frozen=True)
class GlmFit:
    """What a GLM fit returns: the artifact, the covariance bytes it addresses, and — when
    `spec.select_by == "cv"` — the cross-validation diagnostics (FR-MODEL-20, FR-MODEL-53).

    ...
    """

    result: GlmFitResult
    covariance_bytes: bytes
    cv: CrossValidationDiagnostics | None = None
```

(Keep the existing docstring body; only the field list changes, with `cv` appended.)

Insert a new private function before `fit_glm`, immediately after the `GlmFit` dataclass
and its helper functions but before `def fit_glm(`:

```python
def _fit_cv_path(
    data: pl.DataFrame,
    x: np.ndarray,
    response: np.ndarray,
    *,
    spec: GlmSpec,
    family: str,
    link: Any,
    offset: np.ndarray | None,
    weights: np.ndarray | None,
    report: ProgressCallback,
) -> tuple[float, CrossValidationDiagnostics]:
    """Score every alpha in `spec.cv.alphas` over `spec.cv.folds` held-out folds, and
    return the alpha with the lowest mean held-out deviance alongside the full scanned
    path (FR-MODEL-20, FR-MODEL-53).

    Refits `len(cv.alphas) * cv.folds` times against the same design `fit_glm` already
    built for the final fit — CV selects the penalty a single fit at that alpha would use,
    so the folds are drawn from `x`/`response`/`offset`/`weights` directly. `data` is
    passed only so `assign_folds` can read `key_column`/`time_column` by name; the fold
    index it returns is what actually slices the arrays.
    """
    from glum import GeneralizedLinearRegressor  # type: ignore[import-untyped]

    cv = spec.cv
    assert cv is not None  # GlmSpec's validator guarantees this whenever select_by == "cv"

    fold_of_row = assign_folds(
        data,
        method=cv.method,
        seed=spec.seed,
        folds=cv.folds,
        key_column=cv.key_column,
        time_column=cv.time_column,
    )

    power = float(spec.family_params.get("power", 1.5)) if spec.family == "tweedie" else 1.5

    path: list[CvPathPoint] = []
    fold_metrics_at_selected: tuple[CvFoldMetric, ...] = ()
    best_alpha = cv.alphas[0]
    best_mean = math.inf

    for step, alpha in enumerate(cv.alphas):
        report.check_cancelled()
        report.update(
            0.16 + 0.13 * (step / len(cv.alphas)),
            f"cross-validating alpha={alpha:g} ({step + 1}/{len(cv.alphas)})",
        )
        scores: list[float] = []
        metrics_this_alpha: list[CvFoldMetric] = []
        for fold in range(cv.folds):
            test_mask = fold_of_row == fold
            train_mask = ~test_mask
            if not test_mask.any() or not train_mask.any():
                raise GlmFitError(
                    "GLM_CV_FOLD_EMPTY",
                    f"fold {fold} of {cv.folds} has no held-out rows (or no training rows) "
                    f"at alpha={alpha:g}. A fold cannot be scored, or trained, on nothing "
                    "— widen the fold count or check `key_column`/`time_column` for skew.",
                )
            fold_estimator = GeneralizedLinearRegressor(
                family=family, link=link, alpha=alpha, l1_ratio=spec.l1_ratio,
                max_iter=spec.max_iter, gradient_tol=spec.tolerance, fit_intercept=True,
            )
            fold_offset = offset[train_mask] if offset is not None else None
            fold_weights = weights[train_mask] if weights is not None else None
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fold_estimator.fit(
                    x[train_mask], response[train_mask],
                    sample_weight=fold_weights, offset=fold_offset,
                )
            held_offset = offset[test_mask] if offset is not None else None
            mu = fold_estimator.predict(x[test_mask], offset=held_offset)
            held_weights = weights[test_mask] if weights is not None else None
            denom = float(held_weights.sum()) if held_weights is not None else float(test_mask.sum())
            score = deviance(
                response[test_mask], mu, family=spec.family, power=power, weights=held_weights,
            ) / denom
            scores.append(score)
            metrics_this_alpha.append(
                CvFoldMetric(fold=fold, rows=int(test_mask.sum()), score=score)
            )
        mean_score = float(np.mean(scores))
        std_score = float(np.std(scores, ddof=0))
        path.append(CvPathPoint(alpha=alpha, mean_score=mean_score, std_score=std_score))
        if mean_score < best_mean:
            best_mean = mean_score
            best_alpha = alpha
            fold_metrics_at_selected = tuple(metrics_this_alpha)

    return best_alpha, CrossValidationDiagnostics(
        method=cv.method, seed=spec.seed, folds=cv.folds, metric="deviance",
        selected_alpha=best_alpha, path=tuple(path), fold_metrics=fold_metrics_at_selected,
    )
```

In `fit_glm`, immediately after the existing block that builds `weights` (the
`if spec.weight.kind == "column": weights = ...` block, right before the `# glum takes
the power **positionally**` comment) and before the `family`/`link` translation, no change
is needed there — the translation must run *before* CV, since `_fit_cv_path` needs the
already-translated `family`/`link` strings. Instead, insert the CV call **between** the
existing `link: Any = TweedieLink(2) if spec.link == "inverse" else spec.link` line and
the `estimator = GeneralizedLinearRegressor(` construction. Replace:

```python
    estimator = GeneralizedLinearRegressor(
        family=family,
        link=link,
        alpha=spec.alpha,
        l1_ratio=spec.l1_ratio,
        max_iter=spec.max_iter,
        gradient_tol=spec.tolerance,
        fit_intercept=True,
    )
```

with:

```python
    cv_diagnostics: CrossValidationDiagnostics | None = None
    fit_alpha = spec.alpha
    if spec.select_by == "cv":
        report.check_cancelled()
        report.update(0.16, f"cross-validating over {len(spec.cv.alphas)} alpha(s)")  # type: ignore[union-attr]
        fit_alpha, cv_diagnostics = _fit_cv_path(
            data, x, response, spec=spec, family=family, link=link,
            offset=offset, weights=weights, report=report,
        )

    estimator = GeneralizedLinearRegressor(
        family=family,
        link=link,
        alpha=fit_alpha,
        l1_ratio=spec.l1_ratio,
        max_iter=spec.max_iter,
        gradient_tol=spec.tolerance,
        fit_intercept=True,
    )
```

Finally, change the function's `return` statement from:

```python
    return GlmFit(
        result=GlmFitResult(
            ...
        ),
        covariance_bytes=covariance_bytes,
    )
```

to the same body with `cv=cv_diagnostics,` appended after `covariance_bytes=covariance_bytes,`:

```python
    return GlmFit(
        result=GlmFitResult(
            converged=True,
            iterations=int(getattr(estimator, "n_iter_", 0) or 0),
            fit_seconds=round(elapsed, 3),
            coefficients=coefficients,
            relativities=relativities,
            dispersion=_dispersion(estimator, x, response, weights=weights, offset=offset),
            deviance=None,
            rows=data.height,
            library_versions=_versions(),
            covariance_blob=_covariance_ref(covariance_bytes),
        ),
        covariance_bytes=covariance_bytes,
        cv=cv_diagnostics,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd packages/pricing-core && uv run pytest tests/test_glm_cv.py -v`
Expected: PASS, all 7 tests.

Run: `cd packages/pricing-core && uv run pytest -q`
Expected: PASS — `test_glm.py`'s existing fixed-alpha tests are unaffected (`fit_alpha`
equals `spec.alpha` whenever `select_by == "fixed"`, so the estimator construction is
unchanged on that path).

Run: `cd packages/pricing-core && uv run mypy --strict src/`
Expected: no errors. (The `# type: ignore[union-attr]` above `spec.cv.alphas` inside the
`if spec.select_by == "cv":` branch is needed because mypy cannot narrow
`spec.cv: GlmCvSpec | None` from `spec.select_by == "cv"` alone; it is the plan's own
value, present so this step is not a placeholder — confirm mypy is clean with it in place
before moving on, and if a later mypy version narrows this correctly, remove it as a
follow-up rather than leaving a stale ignore.)

Run: `cd backend && uv run pytest tests/test_spec_hash.py::test_every_code_the_fit_path_can_raise_is_registered -v`
Expected: PASS — `GLM_CV_FOLD_EMPTY` is now registered and the AST scan finds it.

- [ ] **Step 5: Commit**

```bash
git add packages/pricing-core/src/pricing_core/modelling/glm.py packages/pricing-core/tests/test_glm_cv.py backend/src/app/errors.py
git commit -m "feat(pricing-core): _fit_cv_path — the elastic-net penalty path reaching glum (FR-MODEL-20, FR-MODEL-53)"
```

---

### Task 6: Wire `GlmFit.cv` into the `model.fit` job handler

**Files:**
- Modify: `backend/src/app/worker/model_handlers.py`
- Test: none new — exercised end to end by Task 8's integration test.

**Interfaces:**
- Consumes: `GlmFit.cv` (Task 5); `Diagnostics.cross_validation` (Task 2).
- Produces: `Diagnostics.cross_validation` populated on every stored `Diagnostics` row
  from a `select_by="cv"` GLM fit. Consumed by Task 8's integration test and by the
  existing `GET /api/v1/models/{id}/diagnostics` endpoint (no endpoint change needed).

- [ ] **Step 1: Make the change**

In `backend/src/app/worker/model_handlers.py`, add `CrossValidationDiagnostics` to the
`from model_schema import (` block, alphabetically between `CustomObjective,` and
`Diagnostics,`:

```python
from model_schema import (
    FIT_RESULT_ADAPTER,
    MODEL_SPEC_ADAPTER,
    Banding,
    CrossValidationDiagnostics,
    CustomMetric,
    CustomObjective,
    Diagnostics,
    Factor,
    FitResult,
    GbmEvalPoint,
    GbmFitResult,
    GbmSpec,
    GlmFitResult,
    GlmSpec,
    Grouping,
    JobKind,
    JobResult,
    ModelSpec,
    PerilStructure,
    QuantileCrossing,
    ReconciledPeril,
    Reconciliation,
    SamplingSpec,
    TransparencyArtifact,
    new_uuid7,
)
```

Change the line `covariance: bytes | None = None` (immediately before the fit `try:`
block) to add a sibling initialisation right after it:

```python
    booster: bytes | None = None
    covariance: bytes | None = None
    glm_cv: CrossValidationDiagnostics | None = None
    eval_curve: tuple[GbmEvalPoint, ...] = ()
```

Change the line `result, covariance = glm_fit.result, glm_fit.covariance_bytes` (inside
the `else:` branch that handles a `GlmSpec` fit) to:

```python
            result, covariance = glm_fit.result, glm_fit.covariance_bytes
            glm_cv = glm_fit.cv
```

Change the `Diagnostics(...)` construction:

```python
    diagnostics = Diagnostics(
        id=new_uuid7(),
        model_id=model_id,
        computed_at=datetime.now(UTC),
        job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
        universal=computed.universal,
        complexity=computed.complexity,
        glm=computed.glm,
        gbm=gbm_diagnostics,
    )
```

to:

```python
    diagnostics = Diagnostics(
        id=new_uuid7(),
        model_id=model_id,
        computed_at=datetime.now(UTC),
        job_id=UUID(parameters["job_id"]) if parameters.get("job_id") else None,
        universal=computed.universal,
        complexity=computed.complexity,
        glm=computed.glm,
        gbm=gbm_diagnostics,
        cross_validation=glm_cv,
    )
```

- [ ] **Step 2: Run the existing handler tests to verify nothing broke**

Run: `cd backend && uv run pytest tests/test_model_jobs.py -v`
Expected: PASS, all pre-existing tests — `glm_cv` is `None` for every one of them (none
sets `select_by="cv"`), so `Diagnostics.cross_validation` stays `None`, matching their
existing behaviour.

Run: `cd backend && uv run mypy --strict src/app/worker/model_handlers.py`
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add backend/src/app/worker/model_handlers.py
git commit -m "feat(backend): thread GlmFit.cv into the persisted Diagnostics artifact (FR-MODEL-20, FR-MODEL-53)"
```

---

### Task 7: Bump `SPEC_HASH_VERSION`

**Files:**
- Modify: `backend/src/app/platform/modelling.py`
- Modify: `backend/tests/test_spec_hash.py`

**Interfaces:**
- Consumes: `SPEC_HASH_VERSION` (existing constant), `spec_hash()`, `spec_hash_is_current()`
  (existing functions, unchanged bodies).
- Produces: `SPEC_HASH_VERSION == 6`; every digest computed from this commit onward is
  `v6:sha256:...`; every prior `v5:...` digest is stale (FR-MODEL-86).

- [ ] **Step 1: Write the failing test change**

In `backend/tests/test_spec_hash.py`, change `test_the_algorithm_version_moved_with_the_new_field`:

```python
@pytest.mark.req("FR-MODEL-86")
@pytest.mark.req("FR-MODEL-100")
def test_the_algorithm_version_moved_with_the_new_field() -> None:
    """FR-MODEL-86: adding a spec field increments `n` in the same commit as the field.

    Asserted on the constant as well as on a digest. A digest-only test passes just as well
    after a hand-edit that added the field and forgot the constant — which is the exact
    mistake the requirement exists to catch, because its symptom is silent: every stored
    digest stops matching its own spec and FR-MODEL-66's dedup ends with no error to see.
    """
    assert SPEC_HASH_VERSION == 6, (
        "GlmSpec.select_by/cv joined the payload (FR-MODEL-20, FR-MODEL-53); the tag "
        "moves with it"
    )
    assert spec_hash(_bound()).startswith("v6:sha256:")
    assert spec_hash_is_current("v5:sha256:" + "0" * 64) is False, (
        "every v5 digest is now stale and must be findable with LIKE 'v5:%'"
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_spec_hash.py::test_the_algorithm_version_moved_with_the_new_field -v`
Expected: FAIL — `assert 5 == 6`.

- [ ] **Step 3: Bump the constant**

In `backend/src/app/platform/modelling.py`, change:

```python
SPEC_HASH_VERSION: Final = 5
```

to:

```python
SPEC_HASH_VERSION: Final = 6
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_spec_hash.py -v`
Expected: PASS, all tests in the file.

Run: `cd backend && uv run pytest -q`
Expected: PASS — a `spec_hash` version bump changes every digest's prefix but not the
comparison logic anything else relies on, so no other test should be sensitive to the
literal string.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/platform/modelling.py backend/tests/test_spec_hash.py
git commit -m "feat(backend): bump SPEC_HASH_VERSION to 6 for GlmSpec.select_by/cv (FR-MODEL-86)"
```

---

### Task 8: End-to-end integration test through the real `model.fit` Job

**Files:**
- Modify: `backend/tests/test_model_jobs.py`

**Interfaces:**
- Consumes: every helper already defined in the file (`_actuary`, `_dataset`, `_factor`,
  `_spec`, `_split`, `_validated_version`), `GlmCvSpec` (Task 4's export),
  `diagnostics_service.load_diagnostics` (already imported as `diagnostics_service`).
- Produces: proof that `select_by="cv"` reaches `glum` through the worker's real
  `execute_job` path and lands on the stored `Diagnostics` row — the same standard every
  other test in this file holds the fixed-alpha path to.

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_model_jobs.py`, after the existing
`test_a_fitted_model_cannot_be_rewritten_in_the_database` function:

```python
@pytest.mark.req("FR-MODEL-20")
@pytest.mark.req("FR-MODEL-53")
async def test_a_cv_selected_model_fits_and_records_its_fold_dispersion(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-20/FR-MODEL-53 end to end: `select_by="cv"` reaches `glum` through the
    handler a worker actually runs, and the selected alpha's per-fold deviance — not only
    its mean — lands on the persisted `Diagnostics`.
    """
    from model_schema import GlmCvSpec

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(
                version_id, (area,), split_ref=split,
                select_by="cv",
                cv=GlmCvSpec(method="random", folds=3, alphas=(0.0, 0.01, 0.1)),
            ),
        )
        assert should_fit is True
        model_id = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor,
            workspace_id=workspace_id,
        )

    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))
    assert model.status is ModelStatus.FITTED

    async with database.session() as session:
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )
    assert diagnostics.cross_validation is not None
    cv = diagnostics.cross_validation
    assert cv.method == "random"
    assert cv.folds == 3
    assert {p.alpha for p in cv.path} == {0.0, 0.01, 0.1}
    assert cv.selected_alpha in {0.0, 0.01, 0.1}
    assert {m.fold for m in cv.fold_metrics} == {0, 1, 2}
    # FR-MODEL-53: dispersion, not only the mean — every fold at the selected alpha
    # carries its own score, and they are not all forced equal.
    assert len({round(m.score, 12) for m in cv.fold_metrics}) > 1


@pytest.mark.req("FR-MODEL-20")
async def test_a_fixed_alpha_model_still_records_no_cross_validation(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Negative, the other direction: the default `select_by="fixed"` path must not gain a
    `cross_validation` block it never computed — proven end to end, not only at the type
    level Task 5's unit test already covers, because the handler is a second place the two
    could be wired together wrong.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )
        model_id = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )
    assert diagnostics.cross_validation is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && uv run pytest tests/test_model_jobs.py -k cv -v`
Expected: FAIL before Tasks 5-6 are committed (`GlmCvSpec` unimportable / `cross_validation`
always `None`). If Tasks 1-7 are already committed at this point, the first test should
already PASS and only serves as the integration proof; keep both tests regardless — the
second is the negative Task 6's own test suite does not cover end to end.

- [ ] **Step 3: Run tests to verify they pass**

(No implementation step: Tasks 1-7 are the implementation. This task only adds the
integration proof.)

Run: `cd backend && uv run pytest tests/test_model_jobs.py -v`
Expected: PASS, every test in the file including the two new ones.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_model_jobs.py
git commit -m "test(backend): a CV-selected model fits through the real Job and records fold dispersion (FR-MODEL-20, FR-MODEL-53)"
```

---

### Task 9: Regenerate the OpenAPI/JSON Schema contracts

**Files:**
- Modify (generated, committed): `docs/contracts/**` — whichever files
  `scripts/generate-contracts.py` touches for `GlmSpec`, `GlmCvSpec` and `Diagnostics` /
  `CrossValidationDiagnostics` / `CvFoldMetric` / `CvPathPoint`.

**Interfaces:**
- Consumes: every `model-schema` type from Tasks 2-4 (already exported).
- Produces: `docs/contracts/` matching the new shapes; `generate-contracts.py --check`
  passes in CI. No new endpoint — `GET /api/v1/models/{id}/diagnostics`'s existing
  response schema simply gains the populated `cross_validation` shape it already declared
  as `null`-typed.

- [ ] **Step 1: Confirm the contract is currently stale**

Run: `uv run python scripts/generate-contracts.py --check`
Expected: FAIL, reporting drift in the `Diagnostics` and/or `GlmSpec` schema (the new
fields exist in `model-schema` but not yet in the committed contract files).

- [ ] **Step 2: Regenerate**

Run: `uv run python scripts/generate-contracts.py`
Expected: exits 0, rewrites the affected file(s) under `docs/contracts/`.

- [ ] **Step 3: Verify against the requirement, not only against its own source**

Open the regenerated `Diagnostics` schema (or the relevant `docs/contracts/` file) and
confirm by inspection:
- `cross_validation` is `{"anyOf": [{"$ref": ".../CrossValidationDiagnostics"}, {"type": "null"}]}`
  (or the equivalent OpenAPI 3.1 nullable form) — not still typed as a bare `null`.
- `CrossValidationDiagnostics.path` and `.fold_metrics` are both arrays of object refs,
  not a single object.
- `GlmSpec.select_by` is an enum of exactly `["fixed", "cv"]`.

This is the check `CLAUDE.md` §13.4 requires ("a generated artifact matching its source
proves neither is correct — check generated output against the requirement"): a
`generate-contracts.py` bug that dropped a field would still produce a self-consistent
diff against `model-schema` if both were wrong the same way, which they cannot be since
one is hand-written Pydantic and the other is generated from it — but the check itself
must be against FR-MODEL-20/53's actual shape, not only "the file changed".

- [ ] **Step 4: Confirm the check now passes and re-run typecheck/frontend generation is unaffected**

Run: `uv run python scripts/generate-contracts.py --check`
Expected: exits 0.

No `frontend/` work is in scope for this plan (the Diagnostics view's CV screen is owned
by workstream W6b per `02-modelling.md` §5.3's Contents column) — do **not** run
`pnpm --dir frontend generate:api` as part of this task; that regeneration belongs to
whichever slice actually builds the CV screen, so the git-ignored generated client is not
churned by a slice that touches no frontend code.

- [ ] **Step 5: Commit**

```bash
git add docs/contracts/
git commit -m "chore(contracts): regenerate for GlmSpec.select_by/cv and Diagnostics.cross_validation"
```

---

### Task 10: Spec amendment — `docs/specs/02-modelling.md`

**Files:**
- Modify: `docs/specs/02-modelling.md`

**Interfaces:** none (documentation only).

- [ ] **Step 1: Update the `GlmSpec` JSON example (§4.4)**

Find §4.4's `GlmSpec` example JSON block. Add `"select_by": "fixed"` and `"cv": null`
(or, if the example is annotated rather than a bare literal, a one-line note) alongside
the existing `alpha`/`l1_ratio` fields, so the example stays a faithful rendering of the
type Task 3 defines.

- [ ] **Step 2: Add the dated amendment note resolving the K-fold temporal gap**

Immediately after FR-MODEL-53's requirement text (§3), add:

```markdown
> **Amendment, 2026-08-21 (the regularisation-and-CV slice).** Neither this requirement
> nor `01` FR-DATA-33 defined K-fold `temporal` semantics — FR-DATA-33 only defines a
> two-part cutoff split. Resolved as **contiguous time-ordered blocks**: sort ascending by
> `time_column`, cut the sorted row order into `folds` equal-count blocks. Implemented in
> `pricing_core.data.splits.assign_folds`.
```

- [ ] **Step 3: Add the dated amendment note resolving the FR-MODEL-99 interaction**

Find FR-MODEL-99's requirement text (`uncertainty_basis`). Immediately after it, add:

```markdown
> **Amendment, 2026-08-21 (the regularisation-and-CV slice).** This requirement predates
> `select_by == "cv"` and says nothing about it. Under CV selection, `GlmSpec.alpha` is
> pinned to `0.0` (the effective penalty comes from `cv.alphas` instead), so
> `uncertainty_basis` cannot read the selected alpha from the spec alone. Resolved as:
> every `select_by == "cv"` fit is treated as using the naive (penalised-fit) information
> matrix unconditionally, regardless of which alpha the scan selects. Conservative rather
> than exact — the elastic-net grid FR-MODEL-20 scans starts at zero and moves away from
> it, so a fit landing back on exactly zero is the rare point on the path, and the
> cautious label costs a display caveat rather than a wrong number on the common one.
```

- [ ] **Step 4: Add `GlmCvSpec` to §4.4's data contract**

In the §4.4 section documenting `GlmSpec`'s fields, add a subsection for `GlmCvSpec`
mirroring `GbmSpec`'s existing `EarlyStopping` nested-block documentation style: field
name, type, default, and the three named fold-construction methods it accepts (§4.4
already documents `01` FR-DATA-33's vocabulary for the dataset-split feature; cross-
reference it rather than re-describing the three methods from scratch).

- [ ] **Step 5: Add `GLM_CV_FOLD_EMPTY` to the error-code catalogue**

Find §5.1's (or wherever `02`'s error-code catalogue lives — the same catalogue
`backend/src/app/errors.py`'s `MODELLING_ERROR_CODES` comments cite by dated slice name)
list of codes owned by this module. Add, following the existing dated-note convention:

```markdown
| `GLM_CV_FOLD_EMPTY` | 409 | A fold has no held-out (or no training) rows at some alpha on the CV path. Added 2026-08-21 (W5, the regularisation-and-CV slice). |
```

- [ ] **Step 6: Run the docs audit**

Run: `python3 scripts/audit-docs.py`
Expected: exits 0 — no broken cross-references, no requirement-id violations, no glossary
drift introduced by this edit.

- [ ] **Step 7: Commit**

```bash
git add docs/specs/02-modelling.md
git commit -m "docs(spec): amend 02-modelling for the regularisation-and-CV slice (FR-MODEL-20, FR-MODEL-53)"
```

---

### Task 11: Roadmap update — `docs/roadmap.md`

**Files:**
- Modify: `docs/roadmap.md`

**Interfaces:** none (documentation only).

- [ ] **Step 1: Mark the W5 slice delivered**

Find the `#### W5 — outstanding work, derived 2026-08-19` section's entry for
"Regularisation and cross-validation" (the exact text quoted in this plan's own header).
Following this repository's established strikethrough/DELIVERED pattern for a closed
slice (match the formatting already used for the custom-metrics and GBM slices in the
same section), mark it delivered with a dated note:

```markdown
~~Regularisation and cross-validation — `select_by: cv` lives in the penalty path...~~
**DELIVERED 2026-08-21.** `GlmSpec.select_by`/`GlmSpec.cv` (FR-MODEL-20), `GlmCvSpec`'s
three fold-construction methods via `pricing_core.data.splits.assign_folds` (FR-MODEL-53),
`_fit_cv_path` in `pricing_core.modelling.glm`, and `Diagnostics.cross_validation`
(`CrossValidationDiagnostics`/`CvPathPoint`/`CvFoldMetric`) persisting the full path and
the selected alpha's per-fold dispersion. No new HTTP endpoint (the existing
`GET /api/v1/models/{id}/diagnostics` surfaces it) and no frontend work (the Diagnostics
view's CV screen remains W6b's). Two spec interactions found and resolved by dated
amendment in `02-modelling.md`: K-fold `temporal` semantics (undefined by FR-DATA-33/
FR-MODEL-53; resolved as contiguous time-ordered blocks) and FR-MODEL-99's
`uncertainty_basis` under CV selection (resolved as unconditionally naive/penalised).
```

- [ ] **Step 2: Run the docs audit**

Run: `python3 scripts/audit-docs.py`
Expected: exits 0.

- [ ] **Step 3: Commit**

```bash
git add docs/roadmap.md
git commit -m "docs(roadmap): W5's regularisation-and-CV slice, delivered"
```

---

## Self-Review

**1. Spec coverage.** FR-MODEL-20 (elastic-net `alpha`/`l1_ratio`, scanned path,
full-path persistence): Tasks 2, 3, 5, 9 — `CvPathPoint`, `GlmCvSpec.alphas`,
`_fit_cv_path`'s path construction, the regenerated contract. FR-MODEL-53 (`select_by:
cv`, declared fold construction with a persisted seed, per-fold metrics and their
dispersion): Tasks 1 (`assign_folds`'s three methods), 3 (`GlmSpec.select_by`/`cv`), 5
(`_fit_cv_path`'s per-fold scoring and `GLM_CV_FOLD_EMPTY`), 2 (`CvFoldMetric`, the
dispersion shape). Both requirements' end-to-end path (spec → job → stored artifact):
Task 8. Contract/doc discipline the roadmap slice implies even though not separately
numbered: Tasks 4, 6, 7, 9, 10, 11. No gaps found.

**2. Placeholder scan.** Every step carries complete code, not a description of code —
checked against the "No Placeholders" list: no `TBD`/`TODO`, no "add appropriate error
handling" without the actual `raise`, no "similar to Task N" without the literal
repetition (Task 8's two tests are written in full despite structural overlap with
Task 5's unit tests, on purpose — they exercise a different site, the handler wiring, not
the same one twice). The one narrowly-scoped exception is Task 9 Step 1's expected
contract diff, which cannot be stated exactly without running the generator against a
future state of `model-schema` this plan itself produces — the step names precisely what
to check for instead of a vague "verify it looks right".

**3. Type/signature consistency.** `assign_folds(frame, *, method, seed, folds, key_column=None, time_column=None) -> np.ndarray`
is declared once in Task 1 and used with exactly that signature in Task 5's
`_fit_cv_path`. `GlmFit.cv: CrossValidationDiagnostics | None` (Task 5) matches
`Diagnostics.cross_validation: CrossValidationDiagnostics | None` (Task 2) and the
`glm_cv` local variable Task 6 threads between them. `GlmCvSpec.method`/`folds`/`alphas`/
`key_column`/`time_column` (Task 3) are read with those exact names by `_fit_cv_path`
(Task 5) and constructed with those exact names by Task 8's integration test. `deviance()`'s
existing signature (`y, mu, *, family, power=1.5, weights=None`) is used unmodified in
Task 5, confirmed against `pricing_core/modelling/diagnostics.py`'s current definition
rather than assumed. `SPEC_HASH_VERSION` moves from 5 to 6 consistently across Task 7's
constant change and its three hardcoded test assertions (`v6:sha256:`, `v5:...` now
stale). No mismatches found.
