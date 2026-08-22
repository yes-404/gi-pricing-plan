# Tweedie Power by Profile Likelihood Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans — this plan is a sequence of small, individually verifiable tasks; follow it strictly, do not "improve" the shape of the data, and do not skip the gate steps.

**Goal.** FR-MODEL-22: let `GlmSpec` request that the Tweedie power `p` be estimated by profile likelihood over a grid, persist the profile curve, and record the estimate with its own 95% profile-likelihood CI — never silently baked in as a constant. Delivered as `GlmSpec.tweedie: TweediePowerSpec | None` (spec), `_estimate_tweedie_power()` in pricing-core (fit-time maths, refitting glum at each grid point), and `GlmFitResult.tweedie: TweediePowerFit | None` (persisted artifact). The backend fit job handler needs zero changes; `record_fit` already stores the fit result.

**Architecture.** The grid is a property of the fitted question, so it lives on the spec (`tweedie.p_grid`), enters `spec_hash` (bumped v6→v7), and drives fit-time behaviour only. Estimation is a private pricing-core helper called from `fit_glm`'s GLM branch: it refits `GeneralizedLinearRegressor(tweedie(p))` at every grid point, scores each refit by `deviance(...)` (the profile), takes the argmin as the estimate, computes the 95% profile-likelihood CI from the χ²_0.95(1) deviance cutoff with linear interpolation, and refuses a minimum at the grid edge (`GLM_TWEEDIE_POWER_GRID_EDGE`). The estimate is carried on `GlmFitResult.tweedie`; every downstream deviance consumer (`compute_diagnostics`, type-III refits, `backtest_model`) reads power from the fit result via a new `_power_of(fit, spec)` helper instead of the spec's constant default — the mechanism that kills the "silently baked in" defect. The estimate is a by-product of the fit, not a separate endpoint.

**Tech Stack.** Python 3.12; Pydantic v2 (model-schema); glum `GeneralizedLinearRegressor` + `TweedieLink` (estimation refits); NumPy; Polars; SciPy `scipy.stats.chi2.ppf(0.95, 1)` for the CI cutoff (already imported in glm.py, and in the §8 tech-deps table); pytest with `@pytest.mark.req`; no pandas.

**Spec.**
- `GlmSpec.tweedie: TweediePowerSpec | None = None` — estimation is opt-in; the default (`None`) is today's fixed-power behaviour, byte-for-byte.
- `TweediePowerSpec` (frozen, `extra="forbid"`): `p_grid: tuple[float, ...] = (1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85, 1.95)`. Validators: ≥2 points; all finite; all strictly inside (1, 2); strictly increasing. Refusals on the parent `GlmSpec`: family ≠ "tweedie"; `"power"` present in `family_params`; `select_by == "cv"` (each with a dated rationale in the message).
- `TweedieProfilePoint` (frozen): `power: float`, `deviance: float` (ge=0).
- `TweediePowerFit` (frozen, `extra="forbid"`): `estimated_power: float`, `ci_lower: float`, `ci_upper: float`, `level: float = 0.95`, `curve: tuple[TweedieProfilePoint, ...]`. Validators: ≥2 curve points; all inside (1,2); estimate is a point on the curve; `ci_lower < ci_upper`; interval brackets the estimate; interval within the curve's power range.
- `GlmFitResult.tweedie: TweediePowerFit | None = None`.
- Fit-time behaviour: if `spec.tweedie` is set, `fit_glm` estimates p over `p_grid` before the final fit; the final `GeneralizedLinearRegressor` uses the estimated power; `GlmFitResult.tweedie` is the filled block; a profile minimum at either grid edge raises `GlmFitError("GLM_TWEEDIE_POWER_GRID_EDGE", ...)`.
- Downstream: `_power_of(fit, spec)` in diagnostics.py; `compute_diagnostics` and `_partition`-adjacent power reads use it; `_type_iii` gains a `power: float` parameter and builds reduced specs with `tweedie=None` + `family_params={"power": power}` for Tweedie models (type-III refits hold p fixed at the estimate); `_family_of` becomes `_family_of(fit, spec)` so `backtest_model`'s residuals use the estimate.
- Docs: FR-MODEL-22 row gains the uncertainty definition (95% profile-likelihood CI) and the estimation×CV refusal as dated amendments; §4.4 gains the `tweedie` block; §4.8 gains `fit_result.tweedie`; §5.1 gains `GLM_TWEEDIE_POWER_GRID_EDGE`; FR-MODEL-87's staged list gains "Tweedie estimation — live 2026-08-21". Roadmap row 3 struck with a DELIVERED note.

## Slice context (verified at planning time, 2026-08-21)

- FR-MODEL-22 is unevidenced and open (roadmap "W5 — outstanding work" row 3). `GlmSpec` today only validates `1.0 < p < 2.0` (`_a_tweedie_power_lies_between_the_two_families_it_spans`, modelling.py:932); nothing estimates or persists a profile.
- No new endpoint: the estimate rides on `GlmFitResult.tweedie`, which `record_fit` already stores and `to_model` already returns via `GET /api/v1/models/{id}` (Model.fit_result is `FitResult | None`, modelling.py:1514).
- The CV slice (#124) established the exact pattern reused here: nested spec block (`GlmSpec.cv: GlmCvSpec`), fit-time computation in pricing-core (`_fit_cv_path`), result threaded to the backend handler which persists it, `SPEC_HASH_VERSION` bump in the same commit, error codes registered in both `errors.py` and the §5.1 catalogue (enforced by `tests/test_repository_invariants.py::test_every_error_code_pricing_core_raises_is_registered_and_declared`), and the roadmap struck-row record.
- Design decisions: uncertainty = 95% profile-likelihood CI (χ²_0.95(1) = 3.841 cutoff, linear interpolation) — resolved by dated spec amendment, not an OQ (the §8 tech table already commits to SciPy profile likelihood); persistence on `GlmFitResult`, not `Diagnostics`, because p feeds every deviance recomputation, all of which receive the fit as first argument; grid-edge minimum refused by name; estimation × CV selection refused by name (the profile is penalty-dependent).

## Global Constraints

- **Workspace:** single uv workspace — `packages/pricing-core`, `packages/model-schema`, `backend`, all with `--all-packages --dev`.
- **Ruff** line length 100; **mypy --strict** on all packages; **lint-imports** (no new cross-package leaks — pricing-core imports model_schema only, never backend).
- **No pandas** anywhere; **glum** is the estimator; **Pydantic v2**.
- **Money** stays integer minor units where money appears — the backend test book's `burning_cost_minor` response is integer minor units; pricing-core fixtures are real-valued (maths, not the rating path).
- **Every test** carries `@pytest.mark.req("FR-MODEL-22")` (or the relevant number); **a negative test precedes every positive one** for each invariant.
- **Spec-change discipline:** any change to what a model *is* bumps `SPEC_HASH_VERSION` in the same commit (6 → 7, FR-MODEL-86); any new error code is registered in `backend/src/app/errors.py` **and** the §5.1 backtick catalogue **in the same commit** (enforced by `tests/test_repository_invariants.py::test_every_error_code_pricing_core_raises_is_registered_and_declared`).
- **Contracts:** `scripts/generate-contracts.py` must be run after model-schema changes (FR-PLAT-48); authored contracts are untouched (comparison is on shared paths only); `docs/contracts/schemas/generated/model-spec.schema.json` and `model.schema.json` will change.
- **If code proves the spec wrong**, amend the spec with a dated note — never a quiet edit (see Task 9).
- **Conventional Commits** (`feat(model-schema):`, `feat(pricing-core):`, `feat(backend):`, `chore(contracts):`, `docs(spec):`, `docs(roadmap):`), each tagged with the FR numbers, with the `Co-Authored-By: Claude <noreply@anthropic.com>` trailer on every commit.
- No PR, no merge — the last task closes with the roadmap record and the full gate, both halves.

---

## Task 1 — `TweediePowerSpec` and `GlmSpec.tweedie` (model-schema)

**Files**
- Modify: `packages/model-schema/src/model_schema/modelling.py`
- Create: `packages/model-schema/tests/test_tweedie_power_spec.py`

**Interfaces**
- Consumes: `GlmCvSpec` (validator style, `math.isfinite`), existing `GlmSpec` validators.
- Produces:
  - `class TweediePowerSpec(BaseModel)` — frozen, `extra="forbid"`; `p_grid: tuple[float, ...] = (1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85, 1.95)`; `@model_validator(mode="after") def _the_grid_has_at_least_two_points_strictly_inside_the_family(self) -> TweediePowerSpec`.
  - `GlmSpec.tweedie: TweediePowerSpec | None = None` (after `cv`); `@model_validator(mode="after") def _tweedie_estimation_declares_a_tweedie_family_and_no_fixed_power(self) -> GlmSpec`.

**Steps**

- [ ] 1.1 Write the negative tests first in `test_tweedie_power_spec.py` (mirror `test_glm_cv_spec.py`'s layout: `_spec(**over)` builder with `motor-ad-frequency` base + `OffsetSpec(kind="log_column", column="exposure_years")`, `uuid4()` ids; `family` defaults to `"poisson"` in the base — tweedie specs must pass `family="tweedie"`):

```python
"""FR-MODEL-22: the profile-likelihood grid on `GlmSpec` — the declared shapes, and what
the type refuses (negative tests first, then the happy shapes)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from model_schema import GlmCvSpec, GlmSpec, OffsetSpec, TweediePowerSpec


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-22")
def test_estimation_declares_a_tweedie_family() -> None:
    """Negative: a grid nobody will scan — estimation is a statement about the Tweedie
    power, which a Poisson or Gamma model does not have."""
    with pytest.raises(ValidationError, match="not 'tweedie'"):
        _spec(tweedie=TweediePowerSpec())


@pytest.mark.req("FR-MODEL-22")
def test_estimation_refuses_a_fixed_power_beside_the_grid() -> None:
    """Negative: two answers to what p is. A fixed power in family_params beside the grid
    is a second, unread answer — the same trap `cv`'s `alpha` refused under CV selection."""
    with pytest.raises(ValidationError, match="fixed power"):
        _spec(family="tweedie", family_params={"power": 1.5}, tweedie=TweediePowerSpec())


@pytest.mark.req("FR-MODEL-22")
def test_estimation_and_cv_selection_are_refused_together() -> None:
    """Negative: the profile is penalty-dependent — a p estimated at one alpha describes
    that fit only. Both together would mean rescanning the grid at every scanned alpha;
    refused by name (FR-MODEL-87 staging) rather than silently estimated against one."""
    with pytest.raises(ValidationError, match="select_by='cv'"):
        _spec(
            family="tweedie",
            select_by="cv",
            cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.1)),
            tweedie=TweediePowerSpec(),
        )


@pytest.mark.req("FR-MODEL-22")
@pytest.mark.parametrize(
    "grid",
    [
        (1.5,),                       # one point is a fixed fit, not a scan
        (1.0, 1.5),                   # the family boundary is not inside (1, 2)
        (1.5, 2.0),
        (1.5, 1.4),                   # a scan must be ordered
        (1.5, 1.5),                   # a duplicate point scans nothing
        (1.5, float("nan")),          # a non-finite point
    ],
)
def test_the_grid_has_at_least_two_points_strictly_inside_the_family(
    grid: tuple[float, ...],
) -> None:
    with pytest.raises(ValidationError):
        TweediePowerSpec(p_grid=grid)


@pytest.mark.req("FR-MODEL-22")
def test_a_fixed_power_spec_needs_no_estimation_block() -> None:
    """Happy path, the default shape: estimation is opt-in — today's fixed-power spec is
    today's spec, unchanged."""
    spec = _spec(family="tweedie", family_params={"power": 1.5})
    assert spec.tweedie is None


@pytest.mark.req("FR-MODEL-22")
def test_the_default_grid_is_a_ten_point_scan_inside_the_family() -> None:
    spec = _spec(family="tweedie", tweedie=TweediePowerSpec())
    assert spec.tweedie is not None
    assert spec.tweedie.p_grid == (
        1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85, 1.95,
    )


@pytest.mark.req("FR-MODEL-22")
def test_an_explicit_scan_is_kept_verbatim() -> None:
    spec = _spec(family="tweedie", tweedie=TweediePowerSpec(p_grid=(1.25, 1.5, 1.75)))
    assert spec.tweedie is not None
    assert spec.tweedie.p_grid == (1.25, 1.5, 1.75)
```

- [ ] 1.2 Run `cd /home/puzhenhao1989/gi-pricing-plan/packages/model-schema && uv run pytest tests/test_tweedie_power_spec.py -q` — expect a **collection error**: `TweediePowerSpec` is not imported. No test imports until the class exists — that is fine, the module fails at import.

- [ ] 1.3 Implement `TweediePowerSpec` in `modelling.py`, placed immediately before `GlmSpec` (after the `GlmCvSpec` block):

```python
class TweediePowerSpec(BaseModel):
    """FR-MODEL-22: the grid over which the Tweedie power `p` is estimated by profile
    likelihood, and the boundary of that estimate. `GlmSpec.tweedie` being set is the
    spec's request for estimation; the estimated value and its uncertainty are fit-time
    facts and ride on `GlmFitResult.tweedie` — never a constant baked into the spec.

    A scan, not a choice: one point would be a fixed fit, and a minimum at the edge of
    the scan is refused at fit time (`GLM_TWEEDIE_POWER_GRID_EDGE`) because it reports
    the scan's boundary as the answer.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    p_grid: tuple[float, ...] = (
        1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85, 1.95,
    )

    @model_validator(mode="after")
    def _the_grid_has_at_least_two_points_strictly_inside_the_family(self) -> TweediePowerSpec:
        if len(self.p_grid) < 2:
            raise ValueError(
                f"p_grid has {len(self.p_grid)} point(s); at least 2 are needed for a "
                "profile to have a minimum — one point is a fixed fit, not an estimate."
            )
        if not all(math.isfinite(p) for p in self.p_grid):
            raise ValueError("p_grid contains a non-finite value")
        if not all(1.0 < p < 2.0 for p in self.p_grid):
            raise ValueError(
                f"p_grid must lie inside (1, 2), got {self.p_grid} — at 1 the family is "
                "Poisson and at 2 it is Gamma; the scan stays inside the family "
                "FR-MODEL-22 estimates."
            )
        if any(b <= a for a, b in zip(self.p_grid, self.p_grid[1:])):
            raise ValueError(
                "p_grid must be strictly increasing — a scanned path is an ordered set, "
                "and the profile interval is read between consecutive points."
            )
        return self
```

- [ ] 1.4 Add the field and validator to `GlmSpec` (field after `cv`; validator after `_cv_selection_declares_its_cv_spec_and_nothing_else_does`):

```python
    # FR-MODEL-22: set to estimate the Tweedie power by profile likelihood over this grid.
    tweedie: TweediePowerSpec | None = None
```

```python
    @model_validator(mode="after")
    def _tweedie_estimation_declares_a_tweedie_family_and_no_fixed_power(self) -> GlmSpec:
        """FR-MODEL-22: the estimation block, the family and the fixed power must agree.

        Each direction is a different defect. Estimation on a non-Tweedie family is a
        grid nobody will scan; a fixed power in `family_params` beside the grid is a
        second, unread answer to what p is; and estimation under `select_by == "cv"`
        would need the profile recomputed at every scanned alpha, since the profile is
        penalty-dependent — the pair is refused by name rather than silently estimated
        against one of them (FR-MODEL-87 staging).
        """
        if self.tweedie is None:
            return self
        if self.family != "tweedie":
            raise ValueError(
                f"tweedie estimation is set but family is {self.family!r}, not 'tweedie' "
                "(FR-MODEL-22): the grid estimates the Tweedie power, and a non-Tweedie "
                "family has no power to estimate."
            )
        if "power" in self.family_params:
            raise ValueError(
                "family_params carries a fixed power beside a profile-likelihood grid "
                "(FR-MODEL-22): a fixed p beside an estimated p is two answers to what "
                "p is — remove the fixed power or drop the estimation block."
            )
        if self.select_by == "cv":
            raise ValueError(
                "select_by='cv' and tweedie estimation are refused together (FR-MODEL-22): "
                "the profile likelihood is penalty-dependent, so a p estimated at one "
                "alpha describes a fit at that alpha only — supporting both would mean "
                "rescanning the grid at every scanned alpha."
            )
        return self
```

- [ ] 1.5 Run the tests again: `uv run pytest tests/test_tweedie_power_spec.py -q` — expect 12 passed. Then the schema's existing suite: `uv run pytest tests/ -q` — expect all pass (existing `GlmSpec` tests construct specs without `tweedie`; the default keeps them green).

- [ ] 1.6 Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add packages/model-schema/src/model_schema/modelling.py packages/model-schema/tests/test_tweedie_power_spec.py && git commit -m "feat(model-schema): TweediePowerSpec grid on GlmSpec.tweedie (FR-MODEL-22)

The grid over which the Tweedie power p is estimated by profile likelihood, with
the mutual exclusions (non-Tweedie family, fixed power beside the grid, CV
selection) refused by name. The estimate itself is fit-time and rides on the fit
result — never a constant baked into the spec.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Task 2 — `TweedieProfilePoint`, `TweediePowerFit`, and `GlmFitResult.tweedie` (model-schema)

**Files**
- Modify: `packages/model-schema/src/model_schema/modelling.py`
- Modify: `packages/model-schema/tests/test_tweedie_power_spec.py`

**Interfaces**
- Consumes: `GlmFitResult` (frozen, `extra="forbid"`); Field from pydantic.
- Produces:
  - `class TweedieProfilePoint(BaseModel)` — frozen; `power: float`; `deviance: float = Field(ge=0.0)`.
  - `class TweediePowerFit(BaseModel)` — frozen, `extra="forbid"`; `estimated_power: float`; `ci_lower: float`; `ci_upper: float`; `level: float = 0.95`; `curve: tuple[TweedieProfilePoint, ...]`; validator `_the_estimate_is_the_curves_argmin_and_the_interval_brackets_it`.
  - `GlmFitResult.tweedie: TweediePowerFit | None = None` (new optional field, last in the block).

**Steps**

- [ ] 2.1 Append the negative tests to `test_tweedie_power_spec.py` (before the positive ones, per the skill):

```python
def _fit_block(**over: object) -> TweediePowerFit:
    base: dict[str, object] = {
        "estimated_power": 1.5,
        "ci_lower": 1.42,
        "ci_upper": 1.58,
        "curve": (
            TweedieProfilePoint(power=1.4, deviance=14.0),
            TweedieProfilePoint(power=1.5, deviance=10.0),
            TweedieProfilePoint(power=1.6, deviance=14.0),
        ),
    }
    base.update(over)
    return TweediePowerFit(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-22")
def test_the_estimate_must_be_a_point_on_the_curve() -> None:
    """Negative: the estimate is the curve's argmin, so it must appear on the curve — a
    value between grid points was never scanned, and no deviance supports it."""
    with pytest.raises(ValidationError, match="one of the scanned grid points"):
        _fit_block(estimated_power=1.55)


@pytest.mark.req("FR-MODEL-22")
def test_the_interval_must_bracket_the_estimate() -> None:
    """Negative: an uncertainty interval that excludes the estimate describes a different
    estimate than the one fitted."""
    with pytest.raises(ValidationError, match="bracket"):
        _fit_block(ci_lower=1.56, ci_upper=1.58)


@pytest.mark.req("FR-MODEL-22")
def test_the_interval_must_be_ordered() -> None:
    with pytest.raises(ValidationError, match="ci_lower must be below"):
        _fit_block(ci_lower=1.6, ci_upper=1.4)


@pytest.mark.req("FR-MODEL-22")
def test_the_interval_cannot_extend_beyond_the_scanned_grid() -> None:
    """Negative: an interval wider than the scan describes a minimum the scan did not
    locate — the interpolation is only defined between scanned points."""
    with pytest.raises(ValidationError, match="scanned grid"):
        _fit_block(ci_lower=0.9, ci_upper=1.1)


@pytest.mark.req("FR-MODEL-22")
def test_a_curve_with_one_point_is_refused() -> None:
    with pytest.raises(ValidationError, match="at least two"):
        _fit_block(
            curve=(TweedieProfilePoint(power=1.5, deviance=10.0),),
        )


@pytest.mark.req("FR-MODEL-22")
def test_a_negative_profile_deviance_is_refused() -> None:
    """Negative: deviance is a non-negative divergence from the fit — a negative value is
    not a deviance, and persisting one would poison every downstream display."""
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        TweedieProfilePoint(power=1.5, deviance=-1.0)


@pytest.mark.req("FR-MODEL-22")
def test_a_fit_result_round_trips_the_estimated_power_block() -> None:
    """Happy path, the persisted shape: JSON round-trip through the exact carrier the
    backend stores (GlmFitResult on ModelRow.fit_result)."""
    fit = GlmFitResult(converged=True, iterations=11, fit_seconds=2.5, tweedie=_fit_block())
    restored = GlmFitResult.model_validate(fit.model_dump(mode="json"))
    assert restored.tweedie is not None
    assert restored.tweedie.estimated_power == 1.5
    assert restored.tweedie.ci_lower == pytest.approx(1.42)
    assert restored.tweedie.ci_upper == pytest.approx(1.58)
    assert restored.tweedie.level == 0.95
    assert [(p.power, p.deviance) for p in restored.tweedie.curve] == [
        (1.4, 14.0), (1.5, 10.0), (1.6, 14.0),
    ]


@pytest.mark.req("FR-MODEL-22")
def test_a_fixed_power_fit_has_no_estimate_block() -> None:
    fit = GlmFitResult(converged=True, iterations=11, fit_seconds=2.5)
    assert fit.tweedie is None
```

(Update the import line to include `GlmFitResult, TweediePowerFit, TweedieProfilePoint`.)

- [ ] 2.2 Run `uv run pytest tests/test_tweedie_power_spec.py -q` — expect a **collection error** (the module fails to import: `TweediePowerFit` / `TweedieProfilePoint` do not exist). Confirm the error is only the missing names.

- [ ] 2.3 Implement the three classes in `modelling.py` — `TweedieProfilePoint` and `TweediePowerFit` immediately after `TweediePowerSpec`; the `tweedie` field on `GlmFitResult` after `library_versions`:

```python
class TweedieProfilePoint(BaseModel):
    """FR-MODEL-22: one scanned power and the deviance of the model refitted at it —
    one point of the profile curve that is persisted with the estimate."""

    model_config = ConfigDict(frozen=True)

    power: float
    deviance: float = Field(ge=0.0)


class TweediePowerFit(BaseModel):
    """FR-MODEL-22: the estimated Tweedie power, persisted as an estimate with its own
    uncertainty — the 95% profile-likelihood interval read from the deviance curve
    (dev(p) - min <= chi2_0.95(1)), interpolated linearly between scanned points — and
    the curve itself, so the estimate can be re-examined after the fit.

    Carried on `GlmFitResult`, not on Diagnostics: unlike alpha, the estimated power
    enters every deviance recomputation (diagnostics, type-III refits, backtests), all
    of which receive the fit result as their first argument.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    estimated_power: float
    ci_lower: float
    ci_upper: float
    level: float = 0.95
    curve: tuple[TweedieProfilePoint, ...]

    @model_validator(mode="after")
    def _the_estimate_is_the_curves_argmin_and_the_interval_brackets_it(self) -> TweediePowerFit:
        powers = [p.power for p in self.curve]
        if len(powers) < 2:
            raise ValueError(
                "the profile curve needs at least two scanned powers — one point has no "
                "interval to read."
            )
        if not all(1.0 < p < 2.0 for p in powers):
            raise ValueError("the scanned powers must lie inside (1, 2)")
        if self.estimated_power not in powers:
            raise ValueError(
                f"the estimated power {self.estimated_power} is not one of the scanned "
                f"grid points {tuple(powers)} — the estimate is the curve's argmin, so "
                "it must appear on the curve."
            )
        if not self.ci_lower < self.ci_upper:
            raise ValueError(
                f"ci_lower must be below ci_upper (ci_lower={self.ci_lower}, "
                f"ci_upper={self.ci_upper})"
            )
        if not self.ci_lower <= self.estimated_power <= self.ci_upper:
            raise ValueError(
                f"the interval must bracket the estimated power: "
                f"[{self.ci_lower}, {self.ci_upper}] does not contain "
                f"{self.estimated_power}."
            )
        if self.ci_lower < powers[0] or self.ci_upper > powers[-1]:
            raise ValueError(
                "the interval cannot extend beyond the scanned grid: an interval wider "
                "than the scan describes a minimum the scan did not locate."
            )
        return self
```

and on `GlmFitResult`:

```python
    # FR-MODEL-22: set when the spec requested profile-likelihood estimation — the
    # estimated power, its 95% profile-likelihood interval, and the persisted curve.
    # None under a fixed-power spec: estimation is opt-in.
    tweedie: TweediePowerFit | None = None
```

- [ ] 2.4 Run `uv run pytest tests/test_tweedie_power_spec.py -q` — expect 20 passed (12 from Task 1 + 8 new). Then `uv run pytest tests/ -q` — expect the full schema suite green.

- [ ] 2.5 Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add packages/model-schema/src/model_schema/modelling.py packages/model-schema/tests/test_tweedie_power_spec.py && git commit -m "feat(model-schema): TweediePowerFit on GlmFitResult.tweedie (FR-MODEL-22)

The persisted estimate block: estimated power, 95% profile-likelihood interval
(chi2_0.95(1) cutoff, interpolated), and the profile curve itself. Carried on the
fit result, not Diagnostics — the estimate feeds every deviance recomputation,
and all of those receive the fit as their first argument.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Task 3 — export the new names (model-schema `__init__`)

**Files**
- Modify: `packages/model-schema/src/model_schema/__init__.py`

**Interfaces**
- Consumes: the import blocks and `__all__`.
- Produces: `TweediePowerFit`, `TweedieProfilePoint`, `TweediePowerSpec` importable from `model_schema` and listed in `__all__`.

**Steps**

- [ ] 3.1 Add `TweediePowerSpec` beside `GlmCvSpec` and the other spec classes, and `TweediePowerFit, TweedieProfilePoint` beside `GlmFitResult`, in the import block — and all three names to `__all__` in the same alphabetical position as their siblings.

- [ ] 3.2 Run `cd /home/puzhenhao1989/gi-pricing-plan/packages/model-schema && uv run python -c "from model_schema import TweediePowerFit, TweediePowerSpec, TweedieProfilePoint; print('ok')"` — expect `ok`.

- [ ] 3.3 Run `uv run pytest tests/ -q` — expect green.

- [ ] 3.4 Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add packages/model-schema/src/model_schema/__init__.py && git commit -m "feat(model-schema): export the Tweedie power names (FR-MODEL-22)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Task 4 — `_estimate_tweedie_power` in pricing-core, wired into `fit_glm`

**Files**
- Modify: `packages/pricing-core/src/pricing_core/modelling/glm.py`
- Modify: `backend/src/app/errors.py`
- Modify: `docs/specs/02-modelling.md` (§5.1 catalogue, one line)
- Create: `packages/pricing-core/tests/test_tweedie_power.py`

**Interfaces**
- Consumes: `deviance` from `pricing_core.modelling.diagnostics` (signature: `deviance(y, mu, *, family, power=1.5, weights=None)`); `stats.chi2.ppf` (scipy — already imported in glm.py line 34); `GeneralizedLinearRegressor` (glum, imported inside functions per existing convention); `TweediePowerSpec`, `TweediePowerFit`, `TweedieProfilePoint` from model_schema; `ProgressCallback` (has `check_cancelled()` and `update(fraction, label, terms=...)` — glm.py:291-292 is the pattern).
- Produces:
  - `PROFILE_CI_CUTOFF: float = float(stats.chi2.ppf(0.95, 1))` — module constant (~3.84).
  - `def _estimate_tweedie_power(data, x, response, *, spec, link, offset, weights, report: ProgressCallback) -> TweediePowerFit` — private helper; grid loop, profile, argmin, edge refusal, CI interpolation.
  - `GlmFitResult.tweedie` populated by `fit_glm`; power for the final fit read from the estimate.
  - `GlmFitError("GLM_TWEEDIE_POWER_GRID_EDGE", ...)`.

**Steps**

- [ ] 4.1 Create `test_tweedie_power.py` — negative test first (the edge refusal), then the fixed-power no-estimate test, then the recovery test:

```python
"""FR-MODEL-22: the Tweedie power estimated by profile likelihood over a grid, end to end.

Not a type-level test — a feature four sites agreeing on a shape can still not work
(`.claude/skills/python-test`), and the site that matters here is the actual refit against
`glum` at every grid point, and the persistence of the curve on the fit result.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import Factor, FactorType, GlmSpec, OffsetSpec, TweediePowerSpec
from pricing_core.modelling.glm import GlmFitError, fit_glm


def _factor(slug: str, column: str) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=uuid4(), version=1,
        type=FactorType.IDENTITY, source_columns=(column,),
    )


def _tweedie_data(n: int = 60_000, power: float = 1.5, seed: int = 20260821) -> pl.DataFrame:
    """A compound-Poisson-Gamma book with a known power (FR-MODEL-22's target).

    Drawn directly from the Tweedie distribution: N ~ Pois(mu^(2-p) / ((2-p)*phi)) and Y
    is the sum of N Gamma(shape=1, scale=(p-1)*phi*mu^(p-1)) draws — so E[Y] = mu and
    Var(Y) = phi*mu^p, and the sum of N iid Gamma(1, s) draws is one Gamma(N, s) draw.
    phi = 1, exposure = 1, mu = exp(1 + 0.5*[urban]). The noise matters: a noiseless book
    has deviance exactly 0 at every p (unit_deviance(y, y, p) == 0 for all p), so the
    profile would be flat and every grid point would tie.
    """
    rng = np.random.default_rng(seed)
    urban = rng.integers(0, 2, n)
    mu = np.exp(1.0 + 0.5 * urban)
    phi = 1.0
    lam = mu ** (2.0 - power) / ((2.0 - power) * phi)
    scale = (power - 1.0) * phi * mu ** (power - 1.0)
    counts = rng.poisson(lam)
    y = rng.gamma(shape=counts, scale=scale)  # shape=0 yields 0.0
    return pl.DataFrame(
        {
            "exposure_years": np.ones(n),
            "area": ["urban" if u else "rural" for u in urban],
            "burning_cost": y,
        }
    )


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-burning-cost",
        "dataset_version_id": uuid4(),
        "response_column": "burning_cost",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "family": "tweedie",
        "link": "log",
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-22")
@pytest.mark.parametrize(
    ("power", "grid"),
    [
        (1.05, (1.55, 1.65, 1.75, 1.85, 1.95)),  # Poisson-like truth below the scan
        (1.95, (1.05, 1.15, 1.25, 1.35, 1.45)),  # Gamma-like truth above the scan
    ],
)
def test_a_profile_minimum_at_the_grid_edge_is_refused(power: float, grid: tuple[float, ...]) -> None:
    """Negative, first: an estimate at the boundary of the scan is not an estimate. The
    truth is far outside the scan, the deviance gaps are huge, and the argmin lands at the
    edge — returning it would report the scan's edge as the fit's answer (FR-MODEL-22:
    a named error, not a silently degenerate result)."""
    data = _tweedie_data(power=power, n=20_000)
    with pytest.raises(GlmFitError) as refused:
        fit_glm(data, _spec(tweedie=TweediePowerSpec(p_grid=grid)), [_factor("area", "area")])
    assert refused.value.code == "GLM_TWEEDIE_POWER_GRID_EDGE"
    assert "tweedie.p_grid" in str(refused.value)


@pytest.mark.req("FR-MODEL-22")
def test_a_fixed_power_spec_records_no_estimate() -> None:
    """Negative, the other direction: no estimation block, no estimate — the unchanged
    fixed-power path, proven not to regress."""
    data = _tweedie_data()
    fit = fit_glm(data, _spec(family_params={"power": 1.5}), [_factor("area", "area")])
    assert fit.result.tweedie is None
    assert fit.result.converged is True


@pytest.mark.req("FR-MODEL-22")
def test_the_profile_recovers_the_power_the_data_was_drawn_from() -> None:
    """The profile-likelihood estimate lands on the power the data was drawn from, and the
    curve and interval are persisted on the fit result — FR-MODEL-22's three obligations:
    the grid, the persisted curve, the estimate with its own uncertainty.

    The grid brackets the truth exactly (1.25, 1.5, 1.75), so deviance is minimised at
    1.5; the chi2_0.95(1) = 3.841 cutoff then brackets 1.5 from below and above. If the
    argmin ever lands at a grid edge for this seed, raise n or widen the grid rather than
    weakening the assertion."""
    data = _tweedie_data(power=1.5)
    fit = fit_glm(
        data,
        _spec(tweedie=TweediePowerSpec(p_grid=(1.25, 1.5, 1.75))),
        [_factor("area", "area")],
    )
    tweedie = fit.result.tweedie
    assert tweedie is not None
    assert tweedie.estimated_power == pytest.approx(1.5)
    assert tweedie.ci_lower <= 1.5 <= tweedie.ci_upper
    assert 1.0 < tweedie.ci_lower < tweedie.ci_upper < 2.0
    assert [p.power for p in tweedie.curve] == [1.25, 1.5, 1.75]
    assert all(p.deviance > 0.0 for p in tweedie.curve)
    best = min(tweedie.curve, key=lambda p: p.deviance)
    assert best.power == tweedie.estimated_power
    assert fit.result.converged is True
```

- [ ] 4.2 Run `cd /home/puzhenhao1989/gi-pricing-plan/packages/pricing-core && uv run pytest tests/test_tweedie_power.py -q` — expect **3 failed, 1 passed**: the fixed-power negative passes already (`tweedie` defaults to `None`); the two edge cases and the recovery test fail because `fit_glm` has no estimation path yet.

- [ ] 4.3 Implement `_estimate_tweedie_power` in `glm.py`. Follow the `_fit_cv_path` shape (refit per grid point with warnings suppressed, deviance scoring, progress via `check_cancelled()` + `update(...)` — there is no `report.fraction` setter). Place it after `_fit_cv_path`; add the three model-schema names to the existing `from model_schema import ...` line; add `PROFILE_CI_CUTOFF` near the top (scipy `stats` is already imported at glm.py:34, and `warnings` at line 25 — no new imports):

```python
PROFILE_CI_CUTOFF: float = float(stats.chi2.ppf(0.95, 1))
# FR-MODEL-22: a 95% profile-likelihood interval is the set of powers whose deviance
# lies within chi2_0.95(1) of the minimum — one degree of freedom, the power itself.
```

```python
def _estimate_tweedie_power(
    data: pl.DataFrame,
    x: pl.DataFrame,
    response: pl.Series,
    *,
    spec: GlmSpec,
    link: Any,
    offset: pl.Series | None,
    weights: pl.Series | None,
    report: ProgressCallback,
) -> TweediePowerFit:
    """FR-MODEL-22: the Tweedie power by profile likelihood over `spec.tweedie.p_grid`.

    Refits the GLM once per scanned power with the power fixed (the profile of the
    deviance), takes the argmin as the estimate, and reads the 95% profile-likelihood
    interval from the deviance curve at the `chi2_0.95(1)` cutoff, interpolating linearly
    between scanned points. A minimum at either edge of the scan is refused — the scan
    found no interior minimum, and the edge is not an estimate.
    """
    assert spec.tweedie is not None
    grid = spec.tweedie.p_grid
    y = response

    from glum import GeneralizedLinearRegressor

    profile: list[TweedieProfilePoint] = []
    for step, p in enumerate(grid):
        family = f"tweedie({float(p)})"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fit_ = GeneralizedLinearRegressor(
                family=family, link=link, alpha=spec.alpha, l1_ratio=spec.l1_ratio,
                max_iter=spec.max_iter, gradient_tol=spec.tolerance, fit_intercept=True,
            ).fit(x, y, offset=offset, sample_weight=weights)
        mu = np.asarray(fit_.predict(x))
        profile.append(
            TweedieProfilePoint(
                power=p, deviance=deviance(y, mu, family="tweedie", power=p, weights=weights),
            )
        )
        report.check_cancelled()
        report.update(
            0.16 + 0.13 * (step + 1) / len(grid),
            f"profiling tweedie power {step + 1}/{len(grid)}",
        )
    curve = tuple(profile)
    best = min(curve, key=lambda point: point.deviance)
    if best is curve[0] or best is curve[-1]:
        raise GlmFitError(
            "GLM_TWEEDIE_POWER_GRID_EDGE",
            f"the profile over tweedie.p_grid={tuple(grid)} is minimised at its "
            f"{'first' if best is curve[0] else 'last'} point ({best.power}), so the "
            "minimum lies at or beyond the scan's edge — not an estimate. Widen the grid "
            "towards the minimum or reconsider the model (FR-MODEL-22).",
        )
    lo, hi = _profile_ci(curve, best.deviance + PROFILE_CI_CUTOFF, best.power)
    return TweediePowerFit(
        estimated_power=best.power, ci_lower=lo, ci_upper=hi, level=0.95, curve=curve,
    )


def _profile_ci(
    curve: tuple[TweedieProfilePoint, ...],
    cutoff: float,
    estimate: float,
) -> tuple[float, float]:
    """FR-MODEL-22: the powers where the profile crosses the cutoff, linearly interpolated
    between scanned points. The profile is convex around the minimum on a fine enough grid,
    so exactly two crossings exist; the interval is clipped to the scanned range, which the
    TweediePowerFit validator re-checks."""
    powers = [point.power for point in curve]
    deviances = [point.deviance for point in curve]

    def crossing(lo: int, hi: int) -> float:
        a, b = deviances[lo], deviances[hi]
        frac = (cutoff - a) / (b - a) if b != a else 0.5
        return float(powers[lo] + frac * (powers[hi] - powers[lo]))

    lower, upper = powers[0], powers[-1]
    for i in range(len(curve) - 1):
        a, b = deviances[i], deviances[i + 1]
        if a <= cutoff <= b:
            lower = crossing(i, i + 1)
        if b <= cutoff <= a:
            upper = crossing(i, i + 1)
    if lower > estimate or upper < estimate:
        # The curve never re-crossed below/above the cutoff within the scan: the
        # interval is one-sided and the scan must widen — refuse rather than persist a
        # CI the validator would reject anyway.
        raise GlmFitError(
            "GLM_TWEEDIE_POWER_GRID_EDGE",
            f"the profile interval is not bracketed within tweedie.p_grid={tuple(powers)} "
            "at the chi2_0.95(1) cutoff — the scan is too narrow around the minimum.",
        )
    return lower, upper
```

- [ ] 4.4 Wire into `fit_glm` (in the GLM branch, before the family-string build): after the CV branch, when `spec.tweedie is not None`, run the estimation and use its power for the final fit, and carry the block on the result:

```python
    tweedie_fit = None
    if spec.tweedie is not None:
        tweedie_fit = _estimate_tweedie_power(
            data, x, response, spec=spec, link=link, offset=offset,
            weights=weights, report=report,
        )
    power = (
        tweedie_fit.estimated_power
        if tweedie_fit is not None
        else float(spec.family_params.get("power", 1.5))
    )
    family = f"tweedie({power})"
```

(the existing `family = f"tweedie({float(spec.family_params.get('power', 1.5))})"` line is replaced by the two lines above), and on the returned `GlmFitResult` add `tweedie=tweedie_fit`. Update the docstring of `fit_glm` (one line: when the spec carries `tweedie`, the power is estimated by profile likelihood over `tweedie.p_grid` and recorded with its CI on `.result.tweedie`).

- [ ] 4.5 Register the error code — `backend/src/app/errors.py`, inside `MODELLING_ERROR_CODES` after `GLM_CV_FOLD_EMPTY`, with the dated comment (mirror the CV entry):

```python
    # GLM_TWEEDIE_POWER_GRID_EDGE (2026-08-21, FR-MODEL-22): the profile over
    # tweedie.p_grid is minimised at a scan edge, so the estimate would report the
    # scan's boundary as the answer.
    "GLM_TWEEDIE_POWER_GRID_EDGE",
```

and in `docs/specs/02-modelling.md` §5.1, one line inside the backtick catalogue after `` `GLM_CV_FOLD_EMPTY` ``:

```
    `GLM_TWEEDIE_POWER_GRID_EDGE`
```

**The invariant test requires both edits in this commit** — `tests/test_repository_invariants.py::test_every_error_code_pricing_core_raises_is_registered_and_declared` AST-scans pricing-core and cross-checks both registries.

- [ ] 4.6 Run `uv run pytest tests/test_tweedie_power.py -q` — expect 4 passed. Then the whole pricing-core suite: `uv run pytest tests/ -q` — expect green (fixed-power tests are untouched). Then the invariant: `cd /home/puzhenhao1989/gi-pricing-plan && uv run pytest tests/test_repository_invariants.py::test_every_error_code_pricing_core_raises_is_registered_and_declared -q` — expect 1 passed.

- [ ] 4.7 Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add packages/pricing-core/src/pricing_core/modelling/glm.py packages/pricing-core/tests/test_tweedie_power.py backend/src/app/errors.py docs/specs/02-modelling.md && git commit -m "feat(pricing-core): estimate the Tweedie power by profile likelihood (FR-MODEL-22)

fit_glm refits the GLM at every tweedie.p_grid point, takes the deviance argmin as
the estimate, reads the 95% profile-likelihood interval from the deviance curve at
the chi2_0.95(1) cutoff with linear interpolation, and refuses a minimum at a scan
edge (GLM_TWEEDIE_POWER_GRID_EDGE). The estimate rides on GlmFitResult.tweedie;
the fixed-power path is unchanged. Code registered in errors.py and the spec
catalogue in the same commit (repository invariant).

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Task 5 — downstream consumers read power from the fit, not the constant

**Files**
- Modify: `packages/pricing-core/src/pricing_core/modelling/diagnostics.py`
- Modify: `packages/pricing-core/tests/test_tweedie_power.py`

**Interfaces**
- Consumes: `GlmFitResult`, `ModelSpec`, `GlmSpec` (already imported); existing `compute_diagnostics(fit, spec, factors, *, train, holdout, ...)` (diagnostics.py:542), `_type_iii` (446), `_partition` (328), `_family_of(spec)` (637), `backtest_model` (653). The defect being fixed is visible at diagnostics.py:568: `power=float(spec.family_params.get("power", 1.5))`.
- Produces:
  - `def _power_of(fit: GlmFitResult, spec: ModelSpec) -> float` — `fit.tweedie.estimated_power` when the fit carries an estimate, else the spec's `family_params.get("power", 1.5)` (family = "tweedie").
  - `_type_iii(data, spec, factors, full_deviance, *, power: float, bandings=None, groupings=None)` — new keyword parameter; the Tweedie branch builds reduced specs with `tweedie=None` and `family_params={"power": power}` so refits hold p at the estimate.
  - `compute_diagnostics(...)` — computes `power = _power_of(fit, spec)` once (line ~568), uses it for deviance/partition (lines ~576/583), and passes it to `_type_iii`.
  - `_family_of(fit: GlmFitResult, spec: ModelSpec) -> tuple[str, float]` — signature change; `backtest_model` passes `fit` (its `fit: FitResult` first argument) at the single call site.

**Steps**

- [ ] 5.1 Append the two downstream tests to `test_tweedie_power.py` (imports: `backtest_model, compute_diagnostics, deviance, predict_glm, unit_deviance`):

```python
@pytest.mark.req("FR-MODEL-22")
def test_diagnostics_are_computed_under_the_estimated_power() -> None:
    """FR-MODEL-22's 'not silently baked in as a constant': the diagnostics' deviance is
    the deviance under the fitted estimate, not under the spec's 1.5 default — and the
    type-III sweep refits with p held at the estimate."""
    data = _tweedie_data(power=1.7)
    factors = [_factor("area", "area")]
    spec = _spec(tweedie=TweediePowerSpec(p_grid=(1.5, 1.7, 1.9)))
    fit = fit_glm(data, spec, factors)
    assert fit.result.tweedie is not None
    computed = compute_diagnostics(fit.result, spec, factors, train=data, holdout=data)
    assert computed.glm is not None
    y = data["burning_cost"].cast(pl.Float64).to_numpy()
    mu = predict_glm(fit.result, data, factors, spec)
    expected = deviance(y, mu, family="tweedie", power=fit.result.tweedie.estimated_power)
    assert computed.glm.deviance == pytest.approx(expected)
    assert computed.glm.deviance != pytest.approx(deviance(y, mu, family="tweedie", power=1.5))
    assert computed.glm.type_iii_tests


@pytest.mark.req("FR-MODEL-22")
def test_a_backtest_of_an_estimated_power_model_uses_the_estimate() -> None:
    """The backtest's residuals are the deviance residuals under the fitted estimate —
    the value the fit used, read from the fit result rather than the spec's constant."""
    data = _tweedie_data(power=1.7)
    factors = [_factor("area", "area")]
    spec = _spec(tweedie=TweediePowerSpec(p_grid=(1.5, 1.7, 1.9)))
    fit = fit_glm(data, spec, factors)
    assert fit.result.tweedie is not None
    summary = backtest_model(
        fit.result, spec, factors, data,
        model_ref="model:burning@1",
        dataset_version_ref="dataset_version:book@1",
        fitted_on_ref="dataset_version:book@1",
    )
    residuals = summary.partition.residual_summary
    assert residuals is not None
    y = data["burning_cost"].cast(pl.Float64).to_numpy()
    mu = predict_glm(fit.result, data, factors, spec)
    unit = np.sign(y - mu) * np.sqrt(
        np.maximum(
            unit_deviance(y, mu, family="tweedie", power=fit.result.tweedie.estimated_power),
            0.0,
        )
    )
    assert residuals.mean == pytest.approx(float(np.mean(unit)))
```

- [ ] 5.2 Run `uv run pytest tests/test_tweedie_power.py -q` — expect the two new tests to fail (the diagnostics/backtest paths still read the spec constant; the `!=` assertion is the one that fails — proving the defect).

- [ ] 5.3 Implement in `diagnostics.py`:

```python
def _power_of(fit: GlmFitResult, spec: ModelSpec) -> float:
    """The Tweedie power a fit is described by: the profile-likelihood estimate when the
    spec asked for one (FR-MODEL-22 — an estimate with its own uncertainty, not a
    constant), else the spec's declared power. Every downstream deviance consumer must
    read p here; the spec's 1.5 default is a fallback for legacy specs, not an answer."""
    if fit.tweedie is not None:
        return fit.tweedie.estimated_power
    return float(spec.family_params.get("power", 1.5))
```

- [ ] 5.4 In `compute_diagnostics`, replace the inline `float(spec.family_params.get("power", 1.5))` reads (lines ~568, 576, 583) with one binding `power = _power_of(fit, spec)`; pass `power=power` into `_type_iii` and the `_partition` call. In `_type_iii`, add the keyword parameter and change the Tweedie reduced-spec construction:

```python
def _type_iii(
    data: pl.DataFrame,
    spec: GlmSpec,
    factors: Sequence[Factor],
    full_deviance: float,
    *,
    power: float,
    bandings: Mapping[str, Banding] | None = None,
    groupings: Mapping[str, Grouping] | None = None,
) -> tuple[TypeIIITest, ...]:
```

with, in the Tweedie arm, the reduced spec built so the refit holds p fixed at the estimate (remove the `family_params` copy of the original, which may carry `power` or not):

```python
        if reduced_spec.family == "tweedie":
            reduced_spec = reduced_spec.model_copy(
                update={"family_params": {"power": power}, "tweedie": None}
            )
```

- [ ] 5.5 Change `_family_of` to take the fit: `def _family_of(fit: GlmFitResult, spec: ModelSpec) -> tuple[str, float]`, with the GLM arm `return spec.family, _power_of(fit, spec)`; update the single call site in `backtest_model` to `_family_of(fit, spec)`. `backtest_model`'s own signature is unchanged — its caller in `backend/src/app/worker/model_handlers.py` needs no edits.

- [ ] 5.6 Run `uv run pytest tests/test_tweedie_power.py -q` — expect 6 passed. Then the full pricing-core suite `uv run pytest tests/ -q` — expect green (all fixed-power sites behave identically: `_power_of` falls back to the same value).

- [ ] 5.7 Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add packages/pricing-core/src/pricing_core/modelling/diagnostics.py packages/pricing-core/tests/test_tweedie_power.py && git commit -m "feat(pricing-core): downstream deviance reads the estimated power (FR-MODEL-22)

compute_diagnostics, the type-III sweep and backtest_model now read p from the fit
result via _power_of — the estimate, with its uncertainty — instead of the spec's
1.5 default. The type-III refits hold p fixed at the estimate by stripping the
estimation block and pinning family_params. This is the fix for the 'silently
baked in as a constant' defect.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Task 6 — `SPEC_HASH_VERSION` 6 → 7

**Files**
- Modify: `backend/src/app/platform/modelling.py`
- Modify: `backend/tests/test_spec_hash.py`

**Interfaces**
- Consumes: `SPEC_HASH_VERSION: Final = 6` (modelling.py:116), the v2..v6 docstring block, `test_the_algorithm_version_moved_with_the_new_field`.
- Produces: `SPEC_HASH_VERSION: Final = 7` with a `v6 → v7` entry in the docstring block; the test asserting 7 and `spec_hash(_bound()).startswith("v7:sha256:")`.

**Steps**

- [ ] 6.1 Update the test first — the assertion is the contract:

```python
    assert SPEC_HASH_VERSION == 7
    # v6 -> v7 (2026-08-21, FR-MODEL-22): tweedie estimation carries its own grid, and
    # two specs differing there must not share a digest or FR-MODEL-66 hands the second
    # caller the first caller's model.
```

- [ ] 6.2 Run `cd /home/puzhenhao1989/gi-pricing-plan/backend && uv run pytest tests/test_spec_hash.py -q` — expect 1 failure (`assert 6 == 7`).

- [ ] 6.3 Bump the constant and append the entry after the v6 block:

```python
#: `tweedie` moved it `v6` to `v7` (2026-08-21, FR-MODEL-22): a model whose power is
#: estimated over `tweedie.p_grid` is a different fitted question than one with a fixed
#: power — the grid is part of the question, and two specs differing there must not
#: share a digest or FR-MODEL-66 answers the second caller with the first caller's
#: model. Every `v6:` digest is now stale and findable with `LIKE 'v6:%'`.
SPEC_HASH_VERSION: Final = 7
```

- [ ] 6.4 Run `uv run pytest tests/test_spec_hash.py -q` — expect all passed. Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add backend/src/app/platform/modelling.py backend/tests/test_spec_hash.py && git commit -m "feat(backend): spec hash v7 for the tweedie grid (FR-MODEL-22, FR-MODEL-86)

The estimation grid is part of the fitted question: two specs differing only in
tweedie.p_grid must not share a digest or FR-MODEL-66 hands the second caller the
first caller's model. Every v6: digest is stale, findable with LIKE 'v6:%'.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Task 7 — backend job integration: an estimated-p model fits through the worker

**Files**
- Modify: `backend/tests/test_model_jobs.py`

**Interfaces**
- Consumes (all existing in the file, verified at planning time): the `database` / `blob_store` / `workspace_id` fixtures; async helpers `_actuary(database, workspace_id)`, `_dataset(database, blob_store, workspace_id, actor)`, `_validated_version(database, blob_store, workspace_id, actor, dataset_id, book=...)` (takes CSV **bytes**), `_factor(database, workspace_id, actor, dataset_id, slug, column)`, `_split(database, blob_store, workspace_id, actor, version_id)`, `_spec(version_id, factor_ids, **over)`; `model_service.reserve_model(session, workspace_id=..., actor=..., spec=...) -> (row, should_fit)` inside `database.unit_of_work()`; `job_service.submit(session, JobKind.MODEL_FIT, {...}, actor, workspace_id=...)`; `execute_job(database, job.id, blob_store) -> JobStatus`; `model_service.to_model(row)`; `diagnostics_service.load_diagnostics(session, workspace_id=..., model_id=...)`. Module-level imports already present: `JobKind`, `JobStatus`, `ModelStatus`, `ModelRow`, `new_uuid7`, `numpy as np`.
- Produces: `TWEEDIE_RNG = np.random.default_rng(20260821)` and `TWEEDIE_BOOK: bytes` (a 400-row CSV in `CV_BOOK`'s style, columns `policy_id,exposure_years,area,burning_cost_minor` — integer minor units per the money convention; the seeded validation rule only checks `exposure_years` positivity, so these columns validate).

**Steps**

- [ ] 7.1 Add the fixture next to `CV_BOOK` (line ~92):

```python
TWEEDIE_RNG = np.random.default_rng(20260821)


def _tweedie_csv() -> bytes:
    """A burning-cost book drawn from a Tweedie(1.5) compound Poisson-Gamma, in integer
    minor units (the money convention): N ~ Pois(mu^(2-p) / ((2-p)*phi)) with p = 1.5 and
    phi = 1, Y = Gamma(N, (p-1)*phi*mu^(p-1)) (0 when N == 0), mu = 200_000 urban /
    100_000 rural. 400 rows and a 3-point grid keep the profile cheap; the assertions are
    structural (the estimate exists, the curve is persisted, the fit succeeded) — the
    estimation's accuracy is pricing-core's test.

    Drawn from the distribution itself, not noiselessly: costs constant per level give
    deviance exactly 0 at every scanned power, a flat profile where every grid point
    ties — the same trap #124's slice hit with noiseless CV data.
    """
    n = 400
    urban = TWEEDIE_RNG.integers(0, 2, n)
    mu = np.where(urban == 1, 200_000.0, 100_000.0)
    lam = 2.0 * np.sqrt(mu)          # p = 1.5, phi = 1
    scale = 0.5 * np.sqrt(mu)
    counts = TWEEDIE_RNG.poisson(lam)
    cost = TWEEDIE_RNG.gamma(shape=counts, scale=scale)
    return b"policy_id,exposure_years,area,burning_cost_minor\n" + b"".join(
        f"P{i},1.0,{'urban' if u else 'rural'},{int(round(c))}\n".encode()
        for i, (u, c) in enumerate(zip(urban, cost), start=1)
    )


TWEEDIE_BOOK = _tweedie_csv()
```

- [ ] 7.2 Add the integration test after the CV integration test (line ~620), mirroring it exactly (reserve inside `unit_of_work` → submit → `execute_job` → read back):

```python
@pytest.mark.req("FR-MODEL-22")
async def test_an_estimated_power_model_fits_and_persists_the_profile(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-22 end to end: a spec with a `tweedie` block fits through the handler a
    worker actually runs — no new endpoint, no handler change — and the persisted fit
    result carries the estimate, its 95% profile-likelihood interval and the curve
    itself, readable through the same `to_model` path `GET /api/v1/models/{id}`
    serialises. If the argmin ever lands at a grid edge for this seed, raise the row
    count rather than weakening the assertions.
    """
    from model_schema import GlmFitResult, TweediePowerSpec

    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id, book=TWEEDIE_BOOK
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(
                version_id, (area,), split_ref=split,
                model_family_slug=f"burn-{new_uuid7().hex[-6:]}",
                response_column="burning_cost_minor",
                family="tweedie",
                link="log",
                tweedie=TweediePowerSpec(p_grid=(1.2, 1.5, 1.8)),
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
    assert isinstance(model.fit_result, GlmFitResult)
    tweedie = model.fit_result.tweedie
    assert tweedie is not None
    assert tweedie.level == 0.95
    assert tweedie.estimated_power in (1.2, 1.5, 1.8)  # the profile's argmin, on the grid
    assert [p.power for p in tweedie.curve] == [1.2, 1.5, 1.8]
    assert all(p.deviance > 0.0 for p in tweedie.curve)
    assert 1.0 < tweedie.ci_lower < tweedie.estimated_power < tweedie.ci_upper < 2.0

    async with database.session() as session:
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )
    assert diagnostics.glm is not None
```

- [ ] 7.3 Run `cd /home/puzhenhao1989/gi-pricing-plan/backend && uv run pytest tests/test_model_jobs.py -q` — expect the new test to fail at import (`TweediePowerSpec` not imported in the test file). Add the import, rerun — expect 1 passed (and the whole file green: `uv run pytest tests/ -q` in the backend).

- [ ] 7.4 Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add backend/tests/test_model_jobs.py && git commit -m "test(backend): an estimated-p model fits through the job worker (FR-MODEL-22)

A spec with a tweedie block runs through the unchanged fit job; the persisted fit
result carries the estimate, the 95% interval and the profile curve, fetchable via
the same to_model path every fit uses.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Task 8 — regenerate the contracts

**Files**
- Generated (no authored edits): `docs/contracts/schemas/generated/model-spec.schema.json`, `docs/contracts/schemas/generated/model.schema.json`

**Interfaces**
- Consumes: `scripts/generate-contracts.py` (FR-PLAT-48; `MODEL_SPEC_ADAPTER` and `Model` in GENERATED_SHAPES). Diagnostics schema is untouched — the estimate is not on Diagnostics.

**Steps**

- [ ] 8.1 Run `cd /home/puzhenhao1989/gi-pricing-plan && uv run python scripts/generate-contracts.py` — expect the two generated schema files to be rewritten (diff shows `tweedie` on both the spec adapter and the model's `fit_result`).

- [ ] 8.2 Verify: `uv run python scripts/generate-contracts.py --check` — expect exit 0, no diff. And `uv run pytest backend/tests/test_contracts.py -q` — expect green (comparison on shared paths only; no authored contract edits needed).

- [ ] 8.3 Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add docs/contracts && git commit -m "chore(contracts): regenerate for the tweedie block (FR-MODEL-22, FR-PLAT-48)

model-spec.schema.json and model.schema.json gain the tweedie estimation block on
GlmSpec and GlmFitResult; diagnostics.schema.json is untouched.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Task 9 — amend the spec

**Files**
- Modify: `docs/specs/02-modelling.md`

**Interfaces**
- Consumes: FR-MODEL-22 row (line 141), §4.4 GlmSpec JSON block, §4.8 fit_result JSON, §5.1 catalogue (edited in Task 4), FR-MODEL-87's staged list.

**Steps**

- [ ] 9.1 Under the FR-MODEL-22 row, add a dated amendment paragraph: the estimate is the profile-likelihood argmin over `tweedie.p_grid`; "its own uncertainty" is the 95% profile-likelihood interval from the deviance curve (dev(p) − min ≤ χ²_0.95(1) = 3.841, linearly interpolated between scanned points), persisted as `ci_lower`/`ci_upper`; a minimum at a scan edge is refused with `GLM_TWEEDIE_POWER_GRID_EDGE`; estimation and `select_by="cv"` are refused together (the profile is penalty-dependent); `family_params.power` beside the grid is refused. Format: `> **Amendment 2026-08-21 (FR-MODEL-22 slice):** ...`

- [ ] 9.2 In §4.4, add the `tweedie` field to the `GlmSpec` JSON block with the nested `TweediePowerSpec` shape (`p_grid`, default ten points) and a dated note that the estimate is fit-time and never a spec constant.

- [ ] 9.3 In §4.8, add `fit_result.tweedie` to the model artifact block with the `TweediePowerFit` shape (estimated_power, ci_lower, ci_upper, level 0.95, curve of power/deviance points) and a note that diagnostics/type-III/backtest deviance reads use the estimate.

- [ ] 9.4 In §5.1, add a dated note for `GLM_TWEEDIE_POWER_GRID_EDGE` (mirror the `GLM_CV_FOLD_EMPTY` note's wording).

- [ ] 9.5 In the FR-MODEL-87 staging list, add: "Tweedie power estimation — live 2026-08-21 (FR-MODEL-22); the estimation × CV-selection pair is refused by name, not built."

- [ ] 9.6 Verify the doc is consistent: `grep -n "GLM_TWEEDIE_POWER_GRID_EDGE" docs/specs/02-modelling.md` shows both the catalogue line and the note; `grep -n "Amendment 2026-08-21" docs/specs/02-modelling.md` shows the FR-MODEL-22 amendment. Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add docs/specs/02-modelling.md && git commit -m "docs(spec): FR-MODEL-22 amendment — profile-likelihood estimation of p (FR-MODEL-22)

Defines 'its own uncertainty' as the 95% profile-likelihood interval read from the
deviance curve (chi2_0.95(1) cutoff, interpolated); records the grid, the persisted
curve, the grid-edge refusal, and the estimation x CV-selection refusal by name.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Task 10 — roadmap record and full gate

**Files**
- Modify: `docs/roadmap.md`

**Interfaces**
- Consumes: W5 outstanding table row 3 (line 2568), the "three requirements had no verdict" paragraph (line 2592).

**Steps**

- [ ] 10.1 Strike row 3 exactly as rows 1-2 were struck, with the DELIVERED note:

```
~~| 3. Tweedie power by profile likelihood | FR-MODEL-22 | ... |~~ — **DELIVERED 2026-08-21**: `GlmSpec.tweedie` carries the grid; `fit_glm` estimates p by profile likelihood (refit at each point, deviance argmin), persists the curve on `GlmFitResult.tweedie`, and records the estimate with its 95% profile-likelihood CI — never a constant; a minimum at a scan edge is refused (`GLM_TWEEDIE_POWER_GRID_EDGE`); estimation × CV selection refused by name (FR-MODEL-87).
```

- [ ] 10.2 Amend the "three requirements had no verdict" paragraph with one sentence: FR-MODEL-22's verdict is delivered by the 2026-08-21 slice; FR-MODEL-23 and FR-MODEL-24 remain unbuilt.

- [ ] 10.3 Full gate (CLAUDE.md §11), **both halves**, from the repo root — read each command's own exit code:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && uv sync --all-packages --dev && \
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q && \
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py && \
uv run python scripts/generate-contracts.py --check && \
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && \
pnpm --dir frontend lint && pnpm --dir frontend type-check && \
pnpm --dir frontend test && pnpm --dir frontend build
```

— expect all green: ruff 0 issues, mypy --strict clean, lint-imports clean, full pytest suite passed (incl. `test_spec_hash.py`, the invariant test, `test_model_jobs.py`, `test_glm.py`, `test_tweedie_power.py`, `test_contracts.py`), audit-docs clean (the docs changed in Tasks 4, 9 and 10), req-coverage reports FR-MODEL-22 covered, contracts match, frontend lint/type-check/tests/build green.

- [ ] 10.4 Commit:

```bash
cd /home/puzhenhao1989/gi-pricing-plan && git add docs/roadmap.md && git commit -m "docs(roadmap): W5 row 3 delivered — Tweedie power by profile likelihood (FR-MODEL-22)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Self-Review (run at planning time)

**Spec coverage, per obligation.** FR-MODEL-22's three obligations map 1:1 onto tasks: "estimated by profile likelihood over a grid" — Tasks 1 + 4 (`tweedie.p_grid`, `_estimate_tweedie_power` refitting glum at every point, deviance argmin); "with the profile curve persisted" — Task 2 (`TweediePowerFit.curve` on the stored `GlmFitResult`, JSON round-trip test, backend persistence test, contracts regenerated); "recorded as an estimate with its own uncertainty, not silently baked in as a constant" — Task 2 (CI validators) + Task 5 (`_power_of` killing the 1.5 fallback in diagnostics, type-III refits and backtests) + Task 9 (amendment defining the uncertainty). Roadmap row 3's "Missing: the grid, the persisted profile curve, and recording an estimated p" is closed by the same three. FR-MODEL-23 and FR-MODEL-24 remain unbuilt and are recorded as such (Task 10.2).

**Placeholder scan.** No TBD, no "add validation", no "similar to Task N": every task names exact files, exact signatures, real test code with `@pytest.mark.req("FR-MODEL-22")`, exact pytest/git commands. The only conditional language is in test docstrings ("if the argmin lands at an edge for this seed, raise n or widen the grid") — an instruction for the rare seed-dependent case, matching the CV slice's convention.

**Type consistency.** `TweediePowerSpec`/`TweediePowerFit` are frozen with `extra="forbid"` like their `GlmCvSpec`/`CrossValidationDiagnostics` siblings; `_estimate_tweedie_power` returns `TweediePowerFit` and `fit_glm` threads it as `GlmFitResult.tweedie: TweediePowerFit | None`; `_power_of(fit, spec) -> float` returns `float` from both arms; `_family_of` returns `tuple[str, float]` unchanged in type, changed in source (fit first arg) with its single caller updated; `_type_iii`'s new keyword `power: float` is passed from `compute_diagnostics`'s single `_power_of` binding; `PROFILE_CI_CUTOFF: float` is float-typed. All model-schema types stay JSON-serialisable (tuples of floats), which the round-trip test proves. Backend handler untouched — the fit result flows through `record_fit` unchanged.

**Review corrections applied before saving** (main-thread review of the agent draft, 2026-08-21): test totals corrected in Steps 1.5/2.4 (12 + 8 = 20); Step 4.2's expected result corrected (3 failed / 1 passed, not a collection error); Task 4's progress reporting corrected from a non-existent `report.fraction` setter to the real `check_cancelled()` + `update()` pattern (glm.py:291-292); Task 7 rewritten against the real backend-test scaffolding (async helpers with `(database, blob_store, workspace_id, actor)`, `model_service.reserve_model(session, ...)`, CSV-**bytes** book with integer-minor-unit `burning_cost_minor`, `to_model` read-back with `isinstance(GlmFitResult)` narrowing) — the draft's `reserve_model(job_service, ...)` helper does not exist; Task 10's gate extended to both halves (audit-docs + frontend).


---

## Execution corrections — applied during the 2026-08-21 execution (append to the plan's Self-Review)

These were found while executing the plan above; each is recorded here so the review
sees the plan-as-executed, not the plan-as-written.

1. **MECHANISM REPLACED (decided by the maintainer 2026-08-21, mid-slice).** The plan's
   estimator — deviance argmin over `p_grid` with a χ²₀.95(1) cutoff on the deviance
   curve — is not a profile-likelihood estimator for Tweedie: `D(p) = 2φ(ℓ_sat(p) −
   ℓ(p, μ̂))`, and `ℓ_sat(p)` plus the p-dependent normaliser do not cancel out of the
   argmin. Measured at the plan's pinned seeds: deviance argmin ≈ truth + 0.25, landing
   at a grid edge in ALL three planned test scenarios (recovery truth 1.5 → 1.75; Task 5
   truth 1.7 → 1.9; backend book → 1.8); EQL (Nelder–Pregibon) compensates but biases the
   other way (truth 1.7 → left edge). The maintainer chose **true profile likelihood**:
   score each grid refit by `L(p) = Σ log f(yᵢ; μ̂ᵢ(p), φ̂(p), p)` with the Dunn–Smyth
   series density (`tweedie_density.py`) and `φ̂(p) = D(p)/n`; estimate = argmax; CI =
   `{p : 2(L_max − L(p)) ≤ 3.841}` linearly interpolated. Ripples: spec amendment first
   (commit f4f8641, inserted before the schema/implementation commits — §0's spec-first
   rule), `TweedieProfilePoint.deviance` → `log_likelihood` (8323597), estimator rework
   (f43e0a1), contracts and docs wording throughout. With the true mechanism, the
   recovery test passes at the pinned seed and Task 5's truth-1.7 scenario is interior.
2. **Plan code bug — `_profile_ci` had lower/upper swapped.** As written it raised
   GRID_EDGE on every properly bracketed interval (the descending-side crossing is the
   lower bound; the plan assigned it to `upper`). Fixed in f43e0a1, re-derived for the
   log-likelihood hill (ascending arm = lower, descending = upper).
3. **Plan test bug — `TweediePowerFit` validator order.** The plan's order (bracket
   before grid) made its own `test_the_interval_cannot_extend_beyond_the_scanned_grid`
   (fixture 0.9, 1.1) fail with the bracket message. Fixed by checking order → grid →
   bracket (8323597); all plan test code kept byte-identical.
4. **Plan data bug — the generator was not Tweedie at p ≠ 1.5.** The compound
   representation needs claim shape `(2−p)/(p−1)`; the plan hardcoded shape 1, so its
   "truth 1.7" data was Tweedie(1.5) — which the new estimator correctly reported, and
   which the deviance mechanism could never have surfaced. Generator corrected
   (f43e0a1); at p = 1.5 the shape factor is exactly 1, so the recovery test is
   bit-identical at the pinned seed.
5. **Backend book (Task 7).** The plan's φ = 1 book gave an edge argmax on every probed
   seed (no zero-cost rows at λ ≈ 632–894); φ raised to 2000 (mu unchanged) for
   p-information — argmax 1.5 interior on all four probed seeds. The ingest recipe
   required `claim_count`/`claim_amount_minor` columns the plan's book lacked (added;
   `burning_cost_minor` still the response). `int(round(c))` → `round(c)` (RUF046;
   `round(np.float64)` already returns int).
6. **Task 5 forced deviations.** Backtest refs: the plan's `dataset_version_ref ==
   fitted_on_ref` violates FR-MODEL-57's own invariant — changed to `:book@2`.
   `_type_iii` has a `len(factors) < 2` guard, so the plan's single-factor test could
   never exercise the sweep — a second (inert, post-drawn) `region` factor added.
   mypy-strict narrowing asserts in `_power_of`/`_family_of`.
7. **Task 1–3 notes.** B905 forced `zip(..., strict=False)` (repo convention). Exports
   were staged uncommitted during Tasks 1–2 so the intermediate test-run counts held,
   then committed in Task 3 only. §5.1's catalogue line landed with the implementation
   commit (f43e0a1) rather than the amendment commit, keeping the repository invariant
   green at every commit.
8. **Spec-hash, contracts, roadmap** landed as planned (88e78f1, 801d198 — which also
   regenerated `docs/contracts/openapi/generated.json`, insertions only — and the
   roadmap strike, per-cell per rows 1–2's format to satisfy audit-docs' pipe-count
   check).
