"""SL-1543 (A): the demo algorithm's `exposure_years` is bounded by the model's training domain.

Pure - no database. The bounds come from `algorithm.MIN_EXPOSURE` / `algorithm.MAX_EXPOSURE`, the
cleaned training sample's own range, so a quote the model never saw is refused rather than priced.
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parent))


def _demo_algorithm() -> Any:
    from algorithm import build_fremtpl2_algorithm

    from model_schema import ArtifactRef, RatingAlgorithm

    payload = build_fremtpl2_algorithm(
        tables={}, bandings={}, base_minor=1, domains={},
        peril_structure_ref=ArtifactRef(type="peril_structure", slug="demo-perils", version=1),
    )
    return RatingAlgorithm.model_validate(payload)


@pytest.mark.req("FR-111")
@pytest.mark.parametrize("exposure", ["0.0011", "0.0000", "1.0617", "2.0123"])
def test_an_exposure_outside_the_training_domain_is_refused_by_name(exposure: str) -> None:
    """INPUT_CONTRACT_VIOLATION names the input, never the value."""
    from pricing_core.rating.score import _validate_inputs

    algorithm = _demo_algorithm()
    with pytest.raises(Exception, match="INPUT_CONTRACT_VIOLATION") as refused:
        _validate_inputs(algorithm, {"bonus_malus": 50, "exposure_years": Decimal(exposure)})
    assert "exposure_years" in str(refused.value)
    assert exposure not in str(refused.value)


@pytest.mark.req("FR-111")
def test_the_exposure_bounds_are_the_training_domain_constants() -> None:
    from algorithm import MAX_EXPOSURE, MIN_EXPOSURE

    field = next(i for i in _demo_algorithm().input_contract if i.name == "exposure_years")
    assert (field.min, field.max) == (Decimal(MIN_EXPOSURE), Decimal(str(MAX_EXPOSURE)))
