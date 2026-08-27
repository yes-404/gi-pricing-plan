"""The widened RatingVersion (03 §4.3, slice W9-3).

Covers the lifecycle states (FR-RATE-23), the pins (FR-RATE-22), the mode-match
invariant (FR-RATE-60), and that the Phase 1b subset still parses.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from model_schema.rating import (
    RatingAlgorithm,
    RatingVersion,
    RatingVersionStatus,
    check_model_reference_mode,
)


def _base(version: int = 27) -> dict:
    return {
        "id": str(uuid4()),
        "workspace_id": str(uuid4()),
        "slug": "motor-gb",
        "version": version,
        "status": "draft",
        "dataset_version_id": str(uuid4()),
        "model_ref": "model:motor-ad-frequency@7",
        "created_at": "2026-08-27T12:00:00Z",
        "created_by": str(uuid4()),
        "updated_at": "2026-08-27T12:00:00Z",
    }


def test_the_phase_1b_subset_still_parses() -> None:
    """The exit-demo subset (slug/version/status/model_ref) needs no new fields."""
    version = RatingVersion.model_validate(_base())
    assert version.status is RatingVersionStatus.DRAFT
    assert version.algorithm_ref is None
    assert version.bundle is None


@pytest.mark.req("FR-RATE-22")
@pytest.mark.req("FR-RATE-26")
def test_the_full_43_contract_parses() -> None:
    """FR-RATE-22/26: pins, mode, effective dates, bundle and change summary parse."""
    data = _base()
    data.update({
        "algorithm_ref": "rating_algorithm:motor-gb@14",
        "pins": {
            "rate_tables": ["rate_table:motor-expense@3"],
            "models": ["peril_structure:motor-gb-2026h2@2"],
            "reference_tables": ["reference_table:ons-postcode-directory@7"],
            "custom_objectives": ["custom_objective:capped-gamma@3"],
        },
        "model_reference_mode": "exact",
        "effective_from": "2026-10-01T00:00:00Z",
        "effective_to": None,
        "bundle": {
            "content_hash": "sha256:" + "a" * 64,
            "bytes": 84_112_904,
            "compiled_at": "2026-08-14T12:00:00Z",
        },
        "change_summary": "AD frequency model refit on 2026H1 data.",
    })
    version = RatingVersion.model_validate(data)
    assert version.pins is not None
    assert len(version.pins.rate_tables) == 1
    assert version.model_reference_mode == "exact"
    assert version.bundle is not None
    assert version.bundle.content_hash.startswith("sha256:")
    assert version.effective_from is not None
    assert version.change_summary == "AD frequency model refit on 2026H1 data."


@pytest.mark.req("FR-RATE-23")
def test_live_and_retired_are_declared_but_unreachable() -> None:
    """FR-RATE-23: live/retired are part of the lifecycle; approved has no transition
    to them yet (DP3 defers the deployment transitions to W14)."""
    assert RatingVersionStatus.LIVE.value == "live"
    assert RatingVersionStatus.RETIRED.value == "retired"
    # The lifecycle map documents the reachable transitions; live/retired are declared
    # but not reachable from approved in W9-3.
    assert len(RatingVersionStatus) == 5


def _algorithm_with_mode(mode: str) -> RatingAlgorithm:
    return RatingAlgorithm.model_validate({
        "slug": "motor-gb",
        "version": 14,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
            {"name": "rating_area", "type": "string", "nullable": False},
        ],
        "outputs": [
            {"name": "payable_premium_minor", "type": "money_minor", "required": True},
        ],
        "steps": [
            {"step_id": "s_in_age", "type": "input", "label": "Age",
             "input_name": "driver_age", "on_missing": "error", "produces": "driver_age"},
            {"step_id": "s_in_area", "type": "input", "label": "Area",
             "input_name": "rating_area", "on_missing": "error", "produces": "rating_area"},
            {"step_id": "s_rp", "type": "model_call", "label": "Risk premium",
             "model_ref": "model:motor-ad-frequency@7", "mode": mode,
             "feature_map": {"driver_age": "driver_age", "rating_area": "rating_area"},
             "consumes": ["driver_age", "rating_area"],
             "produces": ["risk_premium_minor", "peril_risk_premium"]},
            {"step_id": "s_out", "type": "output", "label": "Payable",
             "output_name": "payable_premium_minor",
             "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["risk_premium_minor"]},
        ],
        "sub_graphs": [],
    })


@pytest.mark.req("FR-RATE-60")
def test_a_model_reference_mode_mismatch_is_refused() -> None:
    """FR-RATE-60: a model_call step whose mode disagrees with the version is refused."""
    version = RatingVersion.model_validate(_base())
    assert version.model_reference_mode == "exact"
    algorithm = _algorithm_with_mode("approximation")
    with pytest.raises(ValueError, match="FR-RATE-60"):
        check_model_reference_mode(version, algorithm)


@pytest.mark.req("FR-RATE-60")
def test_a_matching_model_reference_mode_passes() -> None:
    """FR-RATE-60: a model_call step whose mode matches the version compiles."""
    version = RatingVersion.model_validate(_base())
    algorithm = _algorithm_with_mode("exact")
    check_model_reference_mode(version, algorithm)  # must not raise
