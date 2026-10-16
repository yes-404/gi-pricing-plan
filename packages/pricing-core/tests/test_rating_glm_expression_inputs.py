"""SL-1274 S4 (DP-1274-MULTI, ruled (a') at 2026-10-16 10:50:08 BST): an `expression` Factor's
model inputs are its SOURCE COLUMNS, and a predict-time guard refuses a column given two values.

Fit -> pin -> quote: a GLM fitted on a banded `driver_age + vehicle_age` Factor is pinned in a
Rating Version, compiled, and a quote scores to `predict_glm` on the same row. The graph
supplies the source columns (`feature_map` maps `driver_age` and `vehicle_age`, not the slug),
because `required_model_inputs` names the columns for an `expression` Factor (03 FR-222, FR-240).

The guard pair: a plain Factor's slug is renamed to its source column at score time, so a plain
Factor on `driver_age` and a raw `driver_age` key land on one frame column. Unequal values are
refused with `MODEL_CALL_FEATURE_COLLISION`; equal values are the ordinary shared-column case.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest
from test_rating_glm_model_call import (
    DATASET,
    MODEL_REF,
    GlmWorld,
    _value,
    compiled_bundle,
    glm_world,
)

from model_schema import Banding, BandingMethod, Factor, FactorType, GlmSpec, OffsetSpec
from pricing_core.modelling import fit_glm
from pricing_core.modelling.factors import required_model_inputs
from pricing_core.rating import runtime
from pricing_core.rating.runtime import MODEL_CALL_ERROR_KEY, load_bundle

COLLISION = "MODEL_CALL_FEATURE_COLLISION"

_INT_AGE = {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99}
_INT_VEHICLE = {"name": "vehicle_age", "type": "int", "nullable": False, "min": 0, "max": 30}
_EXPOSURE = {"name": "exposure_years", "type": "decimal", "nullable": False}


def _book(n: int = 8_000, seed: int = 20261016) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 78, n).astype(float)
    vehicle = rng.integers(0, 16, n).astype(float)
    exposure = rng.uniform(0.5, 1.0, n)
    total = age + vehicle
    base = np.where(total < 50, 0.10, np.where(total < 70, 0.075, 0.05))
    return pl.DataFrame(
        {
            "driver_age": age,
            "vehicle_age": vehicle,
            "exposure_years": exposure,
            "claim_count": rng.poisson(base * exposure).astype(float),
        }
    )


def _expression_world(
    expression: str, columns: tuple[str, ...], boundaries: tuple[float, ...], slug: str
) -> GlmWorld:
    """One banded `expression` Factor, cut over the formula's result (FR-95, FR-97)."""
    labels = tuple(f"e{i}" for i in range(len(boundaries) - 1))
    banding = Banding(
        id=uuid4(), slug=f"{slug}-steps", dataset_id=DATASET, version=1,
        source_expression=expression, method=BandingMethod.MANUAL,
        boundaries=boundaries, labels=labels,
    )
    factor = Factor(
        id=uuid4(), slug=slug, dataset_id=DATASET, version=1, type=FactorType.EXPRESSION,
        source_columns=columns, expression=expression, banding_id=banding.id,
    )
    spec = GlmSpec(
        model_family_slug="motor-freq-glm", dataset_version_id=DATASET,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=(factor.id,), family="poisson", link="log",
    )
    fit = fit_glm(_book(), spec, [factor], bandings={banding.id: banding})
    return GlmWorld(spec, fit.result, (factor,), (banding,), ())


def _algorithm(contract: list[dict[str, Any]], feature_map: dict[str, str]) -> dict[str, Any]:
    """One `model_call` over the contract's inputs, in the shape `algorithm_payload` builds."""
    names = [str(item["name"]) for item in contract]
    inputs = [
        {"step_id": f"s_{name}", "type": "input", "label": name, "input_name": name,
         "on_missing": "error", "produces": name}
        for name in names
    ]
    call = {
        "step_id": "s_risk", "type": "model_call", "label": "Risk", "model_ref": MODEL_REF,
        "mode": "exact", "feature_map": feature_map, "consumes": names, "produces": ["risk"],
        "result_type": "decimal",
    }
    return {
        "slug": "glm-golden", "version": 1, "input_contract": contract,
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": [
            *inputs, call,
            {"step_id": "s_out", "type": "output", "label": "Risk", "output_name": "risk_out",
             "rounding": {"mode": "half_even", "dp": 6}, "consumes": ["risk"]},
        ],
        "sub_graphs": [],
    }


@pytest.mark.req("FR-222", "FR-240", "FR-95")
async def test_a_banded_two_column_expression_quote_equals_predict_glm() -> None:
    """Fit -> pin -> quote: the graph supplies `driver_age` and `vehicle_age`, and the value is
    `predict_glm` on the same row (DP-1274-MULTI (a'))."""
    world = _expression_world(
        "driver_age + vehicle_age", ("driver_age", "vehicle_age"),
        (10.0, 50.0, 70.0, 120.0), "total_age",
    )
    algorithm = _algorithm(
        [_INT_AGE, _INT_VEHICLE, _EXPOSURE],
        {"driver_age": "driver_age", "vehicle_age": "vehicle_age",
         "exposure_years": "exposure_years"},
    )
    compiled = load_bundle(await compiled_bundle(world, algorithm))
    seen = set()
    for driver, vehicle, exposure in ((25, 3, 1.0), (40, 10, 0.5), (70, 12, 0.75)):
        result = await _value(
            compiled, driver_age=driver, vehicle_age=vehicle, exposure_years=exposure
        )
        assert MODEL_CALL_ERROR_KEY not in result
        expected = world.predict(
            driver_age=float(driver), vehicle_age=float(vehicle), exposure_years=exposure
        )
        assert result["risk"] == pytest.approx(expected, rel=1e-12)
        seen.add(round(expected, 12))
    assert len(seen) > 1  # the bands differ, so a fit that ignored the formula would not pass


@pytest.mark.req("FR-222", "FR-240", "FR-95")
async def test_a_banded_one_column_expression_quote_equals_predict_glm() -> None:
    """The same rule for one column (the probe's `driver_age * 2`): the source column, not the
    slug, is the model's input."""
    world = _expression_world("driver_age * 2", ("driver_age",), (34.0, 76.0, 116.0, 160.0), "x2")
    algorithm = _algorithm(
        [_INT_AGE, _EXPOSURE],
        {"driver_age": "driver_age", "exposure_years": "exposure_years"},
    )
    compiled = load_bundle(await compiled_bundle(world, algorithm))
    seen = set()
    for driver, exposure in ((20, 1.0), (45, 0.5), (70, 0.75)):
        result = await _value(compiled, driver_age=driver, exposure_years=exposure)
        assert MODEL_CALL_ERROR_KEY not in result
        expected = world.predict(driver_age=float(driver), exposure_years=exposure)
        assert result["risk"] == pytest.approx(expected, rel=1e-12)
        seen.add(round(expected, 12))
    assert len(seen) > 1


@pytest.mark.req("FR-222", "FR-240")
def test_required_model_inputs_names_an_expression_factors_source_columns() -> None:
    """The one definition: an `expression` Factor contributes its source columns, once each,
    in order; a plain Factor keeps its slug."""
    two = _expression_world(
        "driver_age + vehicle_age", ("driver_age", "vehicle_age"), (10.0, 50.0, 70.0, 120.0), "t"
    ).factors
    assert required_model_inputs(two, ("ignored",)) == ("driver_age", "vehicle_age")
    plain = glm_world().factors
    assert required_model_inputs(plain, ()) == ("age_band", "region_group")
    shared = (*two, *plain)
    assert required_model_inputs(shared, ()) == (
        "driver_age", "vehicle_age", "age_band", "region_group",
    )


#: Two graph inputs, one frame column: `age` reaches the plain Factor `age_band` (renamed to its
#: source column `driver_age`), `age_raw` reaches the raw key `driver_age`.
_COLLIDING = _algorithm(
    [
        _INT_AGE,
        {"name": "age_raw", "type": "int", "nullable": False, "min": 17, "max": 99},
        {"name": "region", "type": "enum", "domain": ["N1", "N2", "S1", "S2"],
         "nullable": False},
        _EXPOSURE,
    ],
    {"driver_age": "age_band", "age_raw": "driver_age", "region": "region_group",
     "exposure_years": "exposure_years"},
)


@pytest.mark.req("FR-222", "FR-255")
async def test_two_inputs_on_one_column_with_unequal_values_are_refused_by_name() -> None:
    world = glm_world()
    compiled = load_bundle(await compiled_bundle(world, _COLLIDING))
    result = await _value(
        compiled, driver_age=30, age_raw=50, region="N1", exposure_years=1.0
    )
    assert COLLISION in result[MODEL_CALL_ERROR_KEY]
    assert "risk" not in result


@pytest.mark.req("FR-222", "FR-255")
async def test_two_inputs_on_one_column_with_equal_values_score_normally() -> None:
    world = glm_world()
    compiled = load_bundle(await compiled_bundle(world, _COLLIDING))
    result = await _value(
        compiled, driver_age=30, age_raw=30, region="N1", exposure_years=1.0
    )
    assert MODEL_CALL_ERROR_KEY not in result
    expected = world.predict(driver_age=30.0, region="N1", exposure_years=1.0)
    assert result["risk"] == pytest.approx(expected, rel=1e-12)


@pytest.mark.req("FR-222", "FR-255", "NFR-499")
async def test_the_collision_error_names_the_column_and_never_the_values() -> None:
    """At the scorer: the refusal is a coded `PredictionError` that names the column and
    carries neither value (NFR-499)."""
    from pricing_core.modelling.predict import PredictionError

    world = glm_world()
    bundle = await compiled_bundle(world, _COLLIDING)
    scorer = runtime._glm_scorer(MODEL_REF, bundle.resolved_payloads)
    row = {"age_band": 31.0, "driver_age": 57.0, "region_group": "N1", "exposure_years": 1.0}
    with pytest.raises(PredictionError) as excinfo:
        scorer.predict(row)
    assert excinfo.value.code == COLLISION
    assert "driver_age" in str(excinfo.value)
    assert "31" not in str(excinfo.value)
    assert "57" not in str(excinfo.value)
