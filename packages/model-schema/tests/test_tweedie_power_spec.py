"""FR-114: the profile-likelihood grid on `GlmSpec` — the declared shapes, and what
the type refuses (negative tests first, then the happy shapes)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from model_schema import (
    GlmCvSpec,
    GlmFitResult,
    GlmSpec,
    OffsetSpec,
    TweediePowerFit,
    TweediePowerSpec,
    TweedieProfilePoint,
)


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-114")
def test_estimation_declares_a_tweedie_family() -> None:
    """Negative: a grid nobody will scan — estimation is a statement about the Tweedie
    power, which a Poisson or Gamma model does not have."""
    with pytest.raises(ValidationError, match="not 'tweedie'"):
        _spec(tweedie=TweediePowerSpec())


@pytest.mark.req("FR-114")
def test_estimation_refuses_a_fixed_power_beside_the_grid() -> None:
    """Negative: two answers to what p is. A fixed power in family_params beside the grid
    is a second, unread answer — the same trap `cv`'s `alpha` refused under CV selection."""
    with pytest.raises(ValidationError, match="fixed power"):
        _spec(family="tweedie", family_params={"power": 1.5}, tweedie=TweediePowerSpec())


@pytest.mark.req("FR-114")
def test_estimation_and_cv_selection_are_refused_together() -> None:
    """Negative: the profile is penalty-dependent — a p estimated at one alpha describes
    that fit only. Both together would mean rescanning the grid at every scanned alpha;
    refused by name (FR-207 staging) rather than silently estimated against one."""
    with pytest.raises(ValidationError, match="select_by='cv'"):
        _spec(
            family="tweedie",
            select_by="cv",
            cv=GlmCvSpec(method="random", folds=4, alphas=(0.0, 0.1)),
            tweedie=TweediePowerSpec(),
        )


@pytest.mark.req("FR-114")
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


@pytest.mark.req("FR-114")
def test_a_fixed_power_spec_needs_no_estimation_block() -> None:
    """Happy path, the default shape: estimation is opt-in — today's fixed-power spec is
    today's spec, unchanged."""
    spec = _spec(family="tweedie", family_params={"power": 1.5})
    assert spec.tweedie is None


@pytest.mark.req("FR-114")
def test_the_default_grid_is_a_ten_point_scan_inside_the_family() -> None:
    spec = _spec(family="tweedie", tweedie=TweediePowerSpec())
    assert spec.tweedie is not None
    assert spec.tweedie.p_grid == (
        1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85, 1.95,
    )


@pytest.mark.req("FR-114")
def test_an_explicit_scan_is_kept_verbatim() -> None:
    spec = _spec(family="tweedie", tweedie=TweediePowerSpec(p_grid=(1.25, 1.5, 1.75)))
    assert spec.tweedie is not None
    assert spec.tweedie.p_grid == (1.25, 1.5, 1.75)


def _fit_block(**over: object) -> TweediePowerFit:
    base: dict[str, object] = {
        "estimated_power": 1.5,
        "ci_lower": 1.42,
        "ci_upper": 1.58,
        "curve": (
            TweedieProfilePoint(power=1.4, log_likelihood=-14.0),
            TweedieProfilePoint(power=1.5, log_likelihood=-10.0),
            TweedieProfilePoint(power=1.6, log_likelihood=-14.0),
        ),
    }
    base.update(over)
    return TweediePowerFit(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-114")
def test_the_estimate_must_be_a_point_on_the_curve() -> None:
    """Negative: the estimate is the curve's argmax, so it must appear on the curve — a
    value between grid points was never scanned, and no log-likelihood supports it."""
    with pytest.raises(ValidationError, match="one of the scanned grid points"):
        _fit_block(estimated_power=1.55)


@pytest.mark.req("FR-114")
def test_the_interval_must_bracket_the_estimate() -> None:
    """Negative: an uncertainty interval that excludes the estimate describes a different
    estimate than the one fitted."""
    with pytest.raises(ValidationError, match="bracket"):
        _fit_block(ci_lower=1.56, ci_upper=1.58)


@pytest.mark.req("FR-114")
def test_the_interval_must_be_ordered() -> None:
    with pytest.raises(ValidationError, match="ci_lower must be below"):
        _fit_block(ci_lower=1.6, ci_upper=1.4)


@pytest.mark.req("FR-114")
def test_the_interval_cannot_extend_beyond_the_scanned_grid() -> None:
    """Negative: an interval wider than the scan describes a maximum the scan did not
    locate — the interpolation is only defined between scanned points."""
    with pytest.raises(ValidationError, match="scanned grid"):
        _fit_block(ci_lower=0.9, ci_upper=1.1)


@pytest.mark.req("FR-114")
def test_a_curve_with_one_point_is_refused() -> None:
    with pytest.raises(ValidationError, match="at least two"):
        _fit_block(
            curve=(TweedieProfilePoint(power=1.5, log_likelihood=-10.0),),
        )


@pytest.mark.req("FR-114")
def test_a_non_finite_profile_log_likelihood_is_refused() -> None:
    """Negative: a profile log-likelihood is a real number — NaN or infinity cannot be
    compared, and persisting one would poison every downstream interval read."""
    with pytest.raises(ValidationError, match="finite"):
        TweedieProfilePoint(power=1.5, log_likelihood=float("nan"))


@pytest.mark.req("FR-114")
def test_a_negative_log_likelihood_is_accepted() -> None:
    """Happy path: profile log-likelihoods are normally negative — the curve descends
    from the maximum at the estimate, so a negative value is not an error."""
    point = TweedieProfilePoint(power=1.5, log_likelihood=-10.0)
    assert point.log_likelihood == -10.0


@pytest.mark.req("FR-114")
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
    assert [(p.power, p.log_likelihood) for p in restored.tweedie.curve] == [
        (1.4, -14.0), (1.5, -10.0), (1.6, -14.0),
    ]


@pytest.mark.req("FR-114")
def test_a_fixed_power_fit_has_no_estimate_block() -> None:
    fit = GlmFitResult(converged=True, iterations=11, fit_seconds=2.5)
    assert fit.tweedie is None
