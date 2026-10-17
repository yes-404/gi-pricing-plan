"""FD-8070 (WK-1178, SL-8074): two model inputs that land on one source column never price silently.

A `model_call` maps graph names to feature slugs; `_GlmScorer.predict` renames each slug to its
Factor's source column, so two slugs on one column used to collapse to the LAST value with no
error. Predict refuses UNEQUAL values with `MODEL_CALL_FEATURE_COLLISION` (equal values are the
ordinary shared-column case); compile refuses what the graph shows with
`MODEL_CALL_FEATURE_MAP_INVALID` (FR-222, FR-240). RED-FIRST: written before the guards.
"""

from __future__ import annotations

from datetime import UTC, datetime
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
from model_schema.perils import (
    LargeLossKind,
    LargeLossTreatment,
    PerilComponent,
    PerilMethod,
    PerilStructure,
)
from model_schema.rating import RatingAlgorithm
from model_schema.refs import ArtifactRef
from pricing_core.modelling import fit_glm
from pricing_core.modelling.predict import PredictionError
from pricing_core.rating import compile as compile_module
from pricing_core.rating import runtime
from pricing_core.rating.compile import ResolvedArtifact, check_model_call_columns

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


def algorithm(
    feature_map: dict[str, str], aliases: tuple[tuple[str, str, str], ...] = ()
) -> dict[str, Any]:
    """input `driver_age` -> expressions `driver_age_adj` (+20), `driver_age_hi` (+30) -> call.

    An expression step is present only when `feature_map` reads its name. Each alias is an extra
    `input` step: (produced name, `input_name`, `on_missing`).
    """
    extra = [
        {"step_id": f"s_{name}", "type": "expression", "label": name,
         "expr": f"driver_age + {plus}", "result_type": "int",
         "consumes": ["driver_age"], "produces": name}
        for name, plus in (("driver_age_adj", 20), ("driver_age_hi", 30))
        if name in feature_map
    ]
    extra += [
        {"step_id": f"s_{produces}", "type": "input", "label": produces, "input_name": input_name,
         "on_missing": on_missing, "produces": produces}
        for produces, input_name, on_missing in aliases
    ]
    return {
        "slug": "glm-golden", "version": 1,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
            {"name": "vehicle_age", "type": "int", "nullable": False, "min": 0, "max": 40},
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


ALIAS_MAP = {"driver_age": "age_fine", "driver_age_b": "age_coarse"}


@pytest.mark.req("FR-240", "FR-222")
async def test_two_input_steps_with_one_input_name_and_on_missing_compile(world: GlmWorld) -> None:
    """RL ruling Q1 (i): an identical value-determining definition is one value."""
    alias = (("driver_age_b", "driver_age", "error"),)
    await compiled_bundle(world, algorithm(ALIAS_MAP, alias))


@pytest.mark.req("FR-240", "FR-222")
async def test_two_input_steps_with_one_input_name_and_different_on_missing_are_refused(
    world: GlmWorld,
) -> None:
    """Q1 (ii): a missing input yields a default or a null, so the values can differ."""
    alias = (("driver_age_b", "driver_age", "null"),)
    with pytest.raises(ValueError, match=INVALID) as caught:
        await compiled_bundle(world, algorithm(ALIAS_MAP, alias))
    assert "driver_age_b" in str(caught.value)


@pytest.mark.req("FR-240", "FR-222")
async def test_two_input_steps_with_different_input_names_are_refused(world: GlmWorld) -> None:
    """Q1 (iii): two raw inputs are independent values."""
    alias = (("driver_age_b", "vehicle_age", "error"),)
    with pytest.raises(ValueError, match=INVALID):
        await compiled_bundle(world, algorithm(ALIAS_MAP, alias))


# --- Q2: a Peril Structure step is grouped per component model ---------------------------------

FREQ = "model:ad-freq@1"
SEV = "model:ad-sev@1"
STRUCTURE = "peril_structure:motor-perils@1"


def _factor(slug: str) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=DATASET, version=1, type=FactorType.IDENTITY,
        source_columns=("driver_age",),
    )


def _pin(*slugs: str) -> ResolvedArtifact:
    return ResolvedArtifact(
        status="approved", payload={"fit_result": {"feature_order": []}},
        factors=tuple(_factor(slug) for slug in slugs),
    )


def _peril_pins(freq: tuple[str, ...], sev: tuple[str, ...]) -> dict[str, ResolvedArtifact]:
    structure = PerilStructure(
        id=uuid4(), slug="motor-perils", version=1,
        perils=(
            PerilComponent(
                peril="AD", method=PerilMethod.FREQUENCY_SEVERITY,
                frequency_model=ArtifactRef.model_validate(FREQ),
                severity_model=ArtifactRef.model_validate(SEV),
                large_loss=LargeLossTreatment(kind=LargeLossKind.NONE),
            ),
        ),
        created_at=datetime(2026, 10, 1, tzinfo=UTC),
    )
    return {
        STRUCTURE: ResolvedArtifact(status="approved", payload=structure.model_dump(mode="json")),
        FREQ: _pin(*freq),
        SEV: _pin(*sev),
    }


def _peril_algorithm(feature_map: dict[str, str]) -> RatingAlgorithm:
    payload = algorithm(feature_map)
    step = next(s for s in payload["steps"] if s["step_id"] == "s_risk")
    del step["model_ref"]
    step["peril_structure_ref"] = STRUCTURE
    return RatingAlgorithm.model_validate(payload)


@pytest.mark.req("FR-240", "FR-222")
def test_frequency_and_severity_banding_one_column_differently_compile() -> None:
    """Q2: each component scorer renames only its own slugs, so the two never share a frame."""
    pins = _peril_pins(freq=("age_fine",), sev=("age_coarse",))
    fmap = {"driver_age": "age_fine", "driver_age_adj": "age_coarse"}
    check_model_call_columns(_peril_algorithm(fmap), pins)  # no raise


@pytest.mark.req("FR-240", "FR-222")
def test_a_collision_inside_one_component_is_refused() -> None:
    pins = _peril_pins(freq=("age_fine", "age_coarse"), sev=("age_sev",))
    fmap = {"driver_age": "age_fine", "driver_age_adj": "age_coarse", "driver_age_hi": "age_sev"}
    with pytest.raises(ValueError, match=INVALID) as caught:
        check_model_call_columns(_peril_algorithm(fmap), pins)
    assert str(FREQ) in str(caught.value)
    assert "age_coarse" in str(caught.value)
