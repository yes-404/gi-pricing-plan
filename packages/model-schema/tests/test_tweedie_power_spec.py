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
