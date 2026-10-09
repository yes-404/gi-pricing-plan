"""FD-1458 (PL-1464): a GLM `model_call` scores — the value is `predict_glm` on the quote's row.

Compile carries a pinned GLM's Factors, Bandings and Groupings inside the Bundle
(FR-239, NFR-491); the runtime rebuilds them once per loaded bundle and calls `predict_glm`
per quote (FR-222, FR-193). A `model_call`'s value is an exact number, never rounded at the
step (DP-4, option (B), item 15): only an `output` step rounds (FR-226).

The module also exports the fixture builders (`glm_world`, `GlmResolver`) that
`test_rating_runtime.py` and `test_rating_score.py` re-use, so a GLM is built one way.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorType,
    GlmFitResult,
    GlmSpec,
    Grouping,
    GroupingMethod,
    Model,
    ModelStatus,
    OffsetSpec,
    UnseenLevelBehaviour,
)
from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.modelling import fit_glm
from pricing_core.modelling.predict import predict_glm
from pricing_core.rating.compile import Bundle, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import MODEL_CALL_ERROR_KEY, load_bundle

DATASET = uuid4()
MODEL_REF = "model:motor-freq-glm@1"


@dataclass(frozen=True)
class GlmWorld:
    """A real fitted GLM and everything `predict_glm` needs to score it."""

    spec: GlmSpec
    fit: GlmFitResult
    factors: tuple[Factor, ...]
    bandings: tuple[Banding, ...]
    groupings: tuple[Grouping, ...]

    def model_payload(self) -> dict[str, Any]:
        # `model_construct`: the real validator wants diagnostics for an approved Model, which
        # a scoring fixture neither has nor reads; the dump is otherwise the real shape.
        model = Model.model_construct(
            id=uuid4(), model_family_slug=self.spec.model_family_slug, version=1,
            status=ModelStatus.APPROVED, spec=self.spec, spec_hash="0" * 64,
            fit_result=self.fit, dataset_version_id=DATASET,
        )
        return model.model_dump(mode="json")

    def frame(self, **row: Any) -> pl.DataFrame:
        return pl.DataFrame([row])

    def predict(self, **row: Any) -> float:
        return float(
            predict_glm(
                self.fit, self.frame(**row), self.factors, self.spec,
                bandings={b.id: b for b in self.bandings},
                groupings={g.id: g for g in self.groupings},
            )[0]
        )


def _book(n: int = 6_000, seed: int = 20261010) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 78, n).astype(float)
    exposure = rng.uniform(0.5, 1.0, n)
    region = rng.choice(["N1", "N2", "S1", "S2"], n)
    base = np.where(age < 38, 0.10, np.where(age < 58, 0.075, 0.05))
    base = base * np.where(np.isin(region, ["N1", "N2"]), 1.0, 1.4)
    return pl.DataFrame(
        {
            "driver_age": age,
            "region": region,
            "exposure_years": exposure,
            "claim_count": rng.poisson(base * exposure).astype(float),
            "severity_minor": rng.gamma(20.0, 75.0 * (1 + base * 4), n),
        }
    )


def glm_world(*, boundaries: tuple[float, ...] = (18.0, 38.0, 58.0, 78.0)) -> GlmWorld:
    """One banded numeric Factor, one grouped categorical Factor, a `log_column` offset."""
    banding = Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1, column="driver_age",
        method=BandingMethod.MANUAL, boundaries=boundaries,
        labels=tuple(f"b{i}" for i in range(len(boundaries) - 1)),
    )
    grouping = Grouping(
        id=uuid4(), slug="region-ns", dataset_id=DATASET, version=1, column="region",
        method=GroupingMethod.MANUAL,
        mapping={"N1": "NORTH", "N2": "NORTH", "S1": "SOUTH", "S2": "SOUTH"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
    )
    age = Factor(
        id=uuid4(), slug="age_band", dataset_id=DATASET, version=1, type=FactorType.BANDING,
        source_columns=("driver_age",), banding_id=banding.id,
    )
    region = Factor(
        id=uuid4(), slug="region_group", dataset_id=DATASET, version=1,
        type=FactorType.GROUPING, source_columns=("region",), grouping_id=grouping.id,
    )
    spec = GlmSpec(
        model_family_slug="motor-freq-glm", dataset_version_id=DATASET,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=(age.id, region.id), family="poisson", link="log",
    )
    fit = fit_glm(
        _book(), spec, [age, region],
        bandings={banding.id: banding}, groupings={grouping.id: grouping},
    )
    return GlmWorld(spec, fit.result, (age, region), (banding,), (grouping,))


def age_glm(*, offset: OffsetSpec | None = None) -> GlmWorld:
    """The smallest real GLM: one banded Factor, slug `age_years`. With no offset it is a
    gamma severity model on the money-minor scale; with one, a Poisson frequency model.
    `test_rating_runtime.py` and `test_rating_score.py` serve it where they used to serve an
    unscoreable stub."""
    banding = Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1, column="driver_age",
        method=BandingMethod.MANUAL, boundaries=(17.0, 38.0, 58.0, 100.0),
        labels=("17-37", "38-57", "58+"),
    )
    age = Factor(
        id=uuid4(), slug="age_years", dataset_id=DATASET, version=1, type=FactorType.BANDING,
        source_columns=("driver_age",), banding_id=banding.id,
    )
    spec = GlmSpec(
        model_family_slug="motor-freq-glm", dataset_version_id=DATASET,
        response_column="claim_count" if offset else "severity_minor",
        offset=offset or OffsetSpec(), factors=(age.id,),
        family="poisson" if offset else "gamma", link="log",
    )
    fit = fit_glm(_book(), spec, [age], bandings={banding.id: banding})
    return GlmWorld(spec, fit.result, (age,), (banding,), ())


#: The graph's input names are not the Factor slugs: `feature_map` maps a graph name to the
#: Model's own vocabulary — a Factor slug, or the offset column (DP-2 (b)).
FEATURE_MAP = {
    "driver_age": "age_band", "region": "region_group", "exposure_years": "exposure_years",
}


def algorithm_payload(
    *,
    feature_map: dict[str, str] | None = None,
    result_type: str | None = None,
    model_ref: str = MODEL_REF,
) -> dict[str, Any]:
    call: dict[str, Any] = {
        "step_id": "s_risk", "type": "model_call", "label": "Risk", "model_ref": model_ref,
        "mode": "exact", "feature_map": FEATURE_MAP if feature_map is None else feature_map,
        "consumes": ["driver_age", "region", "exposure_years"], "produces": ["risk"],
    }
    if result_type is not None:
        call["result_type"] = result_type
    return {
        "slug": "glm-golden", "version": 1,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
            {"name": "region", "type": "enum", "domain": ["N1", "N2", "S1", "S2"],
             "nullable": False},
            {"name": "exposure_years", "type": "decimal", "nullable": False},
        ],
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_age", "type": "input", "label": "Age", "input_name": "driver_age",
             "on_missing": "error", "produces": "driver_age"},
            {"step_id": "s_reg", "type": "input", "label": "Region", "input_name": "region",
             "on_missing": "error", "produces": "region"},
            {"step_id": "s_exp", "type": "input", "label": "Exposure",
             "input_name": "exposure_years", "on_missing": "error",
             "produces": "exposure_years"},
            call,
            {"step_id": "s_out", "type": "output", "label": "Risk", "output_name": "risk_out",
             "rounding": {"mode": "half_even", "dp": 6}, "consumes": ["risk"]},
        ],
        "sub_graphs": [],
    }


def version(model_ref: str = MODEL_REF) -> RatingVersion:
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "glm-golden", "version": 1,
        "status": "draft", "dataset_version_id": str(uuid4()), "model_ref": model_ref,
        "created_at": "2026-10-10T12:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-10-10T12:00:00Z",
        "algorithm_ref": "rating_algorithm:glm-golden@1",
        "pins": {"rate_tables": [], "models": [model_ref], "reference_tables": [],
                 "custom_objectives": []},
        "model_reference_mode": "exact",
    })


class GlmResolver:
    """Serves a GLM and, as the backend resolver does, its Factors, Bandings and Groupings."""

    def __init__(
        self, world: GlmWorld, algorithm: dict[str, Any] | None = None, model_ref: str = MODEL_REF
    ) -> None:
        self._world = world
        self._model_ref = model_ref
        self._algorithm = (
            algorithm if algorithm is not None else algorithm_payload(model_ref=model_ref)
        )

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        if ref.type == "rating_algorithm":
            return ResolvedArtifact(status="no_maturity_concept", payload=self._algorithm)
        assert str(ref) == self._model_ref, ref
        return ResolvedArtifact(
            status="approved", payload=self._world.model_payload(),
            factors=self._world.factors, bandings=self._world.bandings,
            groupings=self._world.groupings,
        )


async def compiled_bundle(
    world: GlmWorld, algorithm: dict[str, Any] | None = None, model_ref: str = MODEL_REF
) -> Bundle:
    return await compile_bundle(
        version(model_ref), GlmResolver(world, algorithm, model_ref)
    )


async def _value(compiled: Any, **row: Any) -> Any:
    out = await compiled.decision.async_evaluate(row)
    return out["result"]


QUOTES = (
    {"driver_age": 25, "region": "N1", "exposure_years": 1.0},
    {"driver_age": 45, "region": "S2", "exposure_years": 0.5},
    {"driver_age": 70, "region": "N2", "exposure_years": 0.75},
)


@pytest.fixture(scope="module")
def world() -> GlmWorld:
    return glm_world()


@pytest.mark.req("FR-222")
@pytest.mark.req("FR-193")
async def test_a_glm_model_call_equals_predict_glm_on_the_same_row(world: GlmWorld) -> None:
    compiled = load_bundle(await compiled_bundle(world))
    for quote in QUOTES:
        result = await _value(compiled, **quote)
        assert MODEL_CALL_ERROR_KEY not in result
        expected = world.predict(
            driver_age=float(quote["driver_age"]), region=quote["region"],
            exposure_years=quote["exposure_years"],
        )
        assert result["risk"] == pytest.approx(expected, rel=1e-12)


@pytest.mark.req("FR-222")
async def test_a_frequency_glm_model_call_returns_its_exact_rate(world: GlmWorld) -> None:
    """A frequency GLM's mean is about 0.07; `round()` at the step would make it 0."""
    compiled = load_bundle(await compiled_bundle(world))
    result = await _value(compiled, **QUOTES[0])
    assert 0.01 < result["risk"] < 1.0


@pytest.mark.req("FR-226")
async def test_a_model_call_equals_predict_glm_at_full_precision(world: GlmWorld) -> None:
    """No quantize and no `round()` at the step, whichever `result_type` it declares.

    **Deviation from item 15's "exact Decimal of the float", reported to the lead.** The
    engine carries a handler's float at 15 significant digits (`0.0588198259273704` for
    `0.058819825927370374`, probed live; a `str` value cannot enter `v * 2`), so no form
    crosses the binding bit-exactly. The assertion is therefore 1e-14 relative: tight enough
    that any rounding to the unit, cent or `dp` would fail it.
    """
    quote = QUOTES[1]
    expected = world.predict(
        driver_age=float(quote["driver_age"]), region=quote["region"],
        exposure_years=quote["exposure_years"],
    )
    assert expected != round(expected, 6)  # the comparison below cannot pass by rounding
    for result_type in (None, "decimal", "money_minor"):
        algorithm = algorithm_payload(result_type=result_type)
        compiled = load_bundle(await compiled_bundle(world, algorithm))
        assert (await _value(compiled, **quote))["risk"] == pytest.approx(expected, rel=1e-14)


@pytest.mark.req("FR-239")
async def test_a_glm_pin_carries_its_factors_bandings_and_groupings(world: GlmWorld) -> None:
    bundle = await compiled_bundle(world)
    payloads = bundle.resolved_payloads
    for factor in world.factors:
        assert Factor.model_validate(payloads[f"factor:{factor.slug}@{factor.version}"]) == factor
    for banding in world.bandings:
        key = f"banding:{banding.slug}@{banding.version}"
        assert Banding.model_validate(payloads[key]) == banding
    for grouping in world.groupings:
        key = f"grouping:{grouping.slug}@{grouping.version}"
        assert Grouping.model_validate(payloads[key]) == grouping


@pytest.mark.req("FR-239")
async def test_the_bundle_hash_is_reproducible_from_the_pins_and_the_graph(
    world: GlmWorld,
) -> None:
    first = await compiled_bundle(world)
    second = await compiled_bundle(world)
    assert first.content_hash == second.content_hash


@pytest.mark.req("FR-239")
async def test_a_changed_banding_changes_the_bundle_hash() -> None:
    """A re-cut Banding is a new Banding version, hence a new Model version and pin, and
    each Bundle carries only its own `banding:<slug>@<v>` key (item 12)."""
    original = glm_world()
    recut = glm_world(boundaries=(18.0, 30.0, 58.0, 78.0))
    recut_banding = recut.bandings[0].model_copy(update={"version": 2})
    recut = GlmWorld(recut.spec, recut.fit, recut.factors, (recut_banding,), recut.groupings)
    one = await compiled_bundle(original)
    two = await compiled_bundle(recut, model_ref="model:motor-freq-glm@2")
    assert "banding:age-steps@1" in one.resolved_payloads
    assert "banding:age-steps@1" not in two.resolved_payloads
    assert "banding:age-steps@2" in two.resolved_payloads
    assert one.content_hash != two.content_hash


@pytest.mark.req("FR-222")
async def test_the_offset_moves_the_glm_by_exactly_the_exposure(world: GlmWorld) -> None:
    """The offset reaches the model through the step's `feature_map` only (item 14)."""
    compiled = load_bundle(await compiled_bundle(world))
    full = await _value(compiled, driver_age=45, region="S2", exposure_years=1.0)
    half = await _value(compiled, driver_age=45, region="S2", exposure_years=0.5)
    assert math.isclose(
        math.log(full["risk"]) - math.log(half["risk"]),
        math.log(1.0) - math.log(0.5), rel_tol=1e-12,
    )


@pytest.mark.req("FR-255")
async def test_a_glm_whose_offset_is_not_mapped_is_refused_naming_the_offset(
    world: GlmWorld,
) -> None:
    no_offset = {"driver_age": "age_band", "region": "region_group"}
    compiled = load_bundle(await compiled_bundle(world, algorithm_payload(feature_map=no_offset)))
    result = await _value(compiled, **QUOTES[0])
    assert "MODEL_OFFSET_MISSING" in result[MODEL_CALL_ERROR_KEY]
