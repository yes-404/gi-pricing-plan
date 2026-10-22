"""PL-8162 A-R2 / DP-T: the negative-binomial θ is declared, never defaulted.

θ is R/MASS `glm.nb`'s (variance μ + μ²/θ) and lives in `family_params["theta"]`. glum's
1.0 is never adopted by omission, and a θ on any other family is a declared parameter that
would be silently ignored (the FR-127 class), so it is refused too.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from model_schema import GlmSpec, OffsetSpec


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "family": "negative_binomial",
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


@pytest.mark.req("FR-110")
def test_a_negative_binomial_spec_with_a_declared_theta_is_built() -> None:
    assert _spec(family_params={"theta": 2.0}).family_params == {"theta": 2.0}


@pytest.mark.req("FR-110")
def test_a_negative_binomial_spec_without_theta_is_refused() -> None:
    with pytest.raises(ValidationError, match="theta"):
        _spec()
    with pytest.raises(ValidationError, match="theta"):
        _spec(family_params={"power": 1.5})


@pytest.mark.req("FR-110")
@pytest.mark.parametrize("theta", [0.0, -1.0, float("nan"), float("inf")])
def test_a_negative_binomial_theta_must_be_positive_and_finite(theta: float) -> None:
    with pytest.raises(ValidationError, match="theta"):
        _spec(family_params={"theta": theta})


@pytest.mark.req("FR-110")
@pytest.mark.parametrize("family", ["poisson", "gamma", "inverse_gaussian", "gaussian"])
def test_a_theta_on_another_family_is_refused(family: str) -> None:
    with pytest.raises(ValidationError, match="theta"):
        _spec(family=family, family_params={"theta": 2.0})
