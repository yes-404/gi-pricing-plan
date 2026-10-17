"""FD-8070 (WK-1178, SL-8074): two model inputs that land on one source column never price silently.

A `model_call` maps graph names to feature slugs; `_GlmScorer.predict` renames each slug to its
Factor's source column, so two slugs on one column used to collapse to the LAST value with no
error. Predict refuses UNEQUAL values with `MODEL_CALL_FEATURE_COLLISION` (equal values are the
ordinary shared-column case); compile refuses what the graph shows with
`MODEL_CALL_FEATURE_MAP_INVALID` (FR-222, FR-240). RED-FIRST: written before the guards.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from test_rating_glm_model_call import (
    DATASET,
    MODEL_REF,
    GlmWorld,
    _book,
    compiled_bundle,
)

from model_schema import Banding, BandingMethod, Factor, FactorType, GlmSpec, OffsetSpec
from pricing_core.modelling import fit_glm
from pricing_core.modelling.predict import PredictionError
from pricing_core.rating import compile as compile_module
from pricing_core.rating import runtime

COLLISION = "MODEL_CALL_FEATURE_COLLISION"
INVALID = r"^MODEL_CALL_FEATURE_MAP_INVALID: "


def two_factors_one_column_world() -> GlmWorld:
    """Two banding Factors, `age_fine` (cut 38) and `age_coarse` (cut 30), both on `driver_age`."""
    bandings = [
        Banding(
            id=uuid4(), slug=slug, dataset_id=DATASET, version=1, column="driver_age",
            method=BandingMethod.MANUAL, boundaries=(18.0, cut, 78.0), labels=(f"{p}0", f"{p}1"),
        )
        for slug, cut, p in (("fine-steps", 38.0, "f"), ("coarse-steps", 30.0, "c"))
    ]
    factors = [
        Factor(
            id=uuid4(), slug=slug, dataset_id=DATASET, version=1, type=FactorType.BANDING,
            source_columns=("driver_age",), banding_id=b.id,
        )
        for slug, b in (("age_fine", bandings[0]), ("age_coarse", bandings[1]))
    ]
    spec = GlmSpec(
        model_family_slug="motor-freq-glm", dataset_version_id=DATASET,
        response_column="severity_minor", offset=OffsetSpec(),
        factors=tuple(f.id for f in factors), family="gamma", link="log",
    )
    fit = fit_glm(_book(), spec, factors, bandings={b.id: b for b in bandings})
    return GlmWorld(spec, fit.result, tuple(factors), tuple(bandings), ())


def algorithm(feature_map: dict[str, str]) -> dict[str, Any]:
    """input `driver_age` -> expressions `driver_age_adj` (+20), `driver_age_hi` (+30) -> call.

    An expression step is present only when `feature_map` reads its name.
    """
    extra = [
        {"step_id": f"s_{name}", "type": "expression", "label": name,
         "expr": f"driver_age + {plus}", "result_type": "int",
         "consumes": ["driver_age"], "produces": name}
        for name, plus in (("driver_age_adj", 20), ("driver_age_hi", 30))
        if name in feature_map
    ]
    return {
        "slug": "glm-golden", "version": 1,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
        ],
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_age", "type": "input", "label": "Age", "input_name": "driver_age",
             "on_missing": "error", "produces": "driver_age"},
            *extra,
            {"step_id": "s_risk", "type": "model_call", "label": "Risk",
             "model_ref": MODEL_REF, "mode": "exact", "result_type": "decimal",
             "feature_map": feature_map,
             "consumes": sorted(feature_map), "produces": ["risk"]},
            {"step_id": "s_out", "type": "output", "label": "Risk", "output_name": "risk_out",
             "rounding": {"mode": "half_even", "dp": 6}, "consumes": ["risk"]},
        ],
        "sub_graphs": [],
    }


@pytest.fixture(scope="module")
def world() -> GlmWorld:
    return two_factors_one_column_world()


async def _bundle_bypassing_the_compile_guard(
    world: GlmWorld, monkeypatch: pytest.MonkeyPatch
) -> Any:
    """A bundle whose map the compile guard would refuse, as one compiled before the guard was."""
    monkeypatch.setattr(compile_module, "check_model_call_columns", lambda *_: None)
    fmap = {"driver_age": "age_fine", "driver_age_adj": "age_coarse"}
    return await compiled_bundle(world, algorithm(fmap))


@pytest.mark.req("FR-240", "FR-222")
async def test_two_factors_on_one_column_fed_different_graph_names_is_refused_at_compile(
    world: GlmWorld,
) -> None:
    """The FD's constructed case: the later value used to win for both Factors, silently."""
    fmap = {"driver_age": "age_fine", "driver_age_adj": "age_coarse"}
    with pytest.raises(ValueError, match=INVALID) as caught:
        await compiled_bundle(world, algorithm(fmap))
    message = str(caught.value)
    assert "'s_risk'" in message
    assert "age_fine" in message
    assert "age_coarse" in message
    assert "driver_age" in message  # the shared column is named


@pytest.mark.req("FR-240", "FR-222")
async def test_two_graph_names_onto_one_feature_is_refused_at_compile(world: GlmWorld) -> None:
    """`feature_row` is keyed by the feature, so the second graph name used to replace the first."""
    fmap = {"driver_age": "age_fine", "driver_age_adj": "age_fine", "driver_age_hi": "age_coarse"}
    with pytest.raises(ValueError, match=INVALID) as caught:
        await compiled_bundle(world, algorithm(fmap))
    message = str(caught.value)
    assert "'s_risk'" in message
    assert "age_fine" in message


@pytest.mark.req("FR-222", "FR-255")
async def test_unequal_values_for_one_column_are_refused_by_name_at_predict(
    world: GlmWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A bundle that bypassed compile: the scorer itself never picks one value silently."""
    bundle = await _bundle_bypassing_the_compile_guard(world, monkeypatch)
    scorer = runtime._glm_scorer(MODEL_REF, bundle.resolved_payloads)
    with pytest.raises(PredictionError) as caught:
        scorer.predict({"age_fine": 25.0, "age_coarse": 45.0})
    assert caught.value.code == COLLISION
    assert "driver_age" in str(caught.value)
    assert "25" not in str(caught.value)  # NFR-499
    assert "45" not in str(caught.value)


@pytest.mark.req("FR-222")
async def test_equal_values_for_one_column_score_normally_at_predict(
    world: GlmWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = await _bundle_bypassing_the_compile_guard(world, monkeypatch)
    scorer = runtime._glm_scorer(MODEL_REF, bundle.resolved_payloads)
    got = scorer.predict({"age_fine": 33.0, "age_coarse": 33.0})
    assert got == pytest.approx(world.predict(driver_age=33.0), rel=1e-12)
