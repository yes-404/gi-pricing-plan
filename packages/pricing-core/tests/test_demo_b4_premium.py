"""PL-1542 Task 4 / Acceptance 4: the demo algorithm's B4 premium is the ruled combination.

`examples/fremtpl2/algorithm.py` builds the algorithm the seed saves. With a Peril Structure it
prices a quote as the structure's risk premium times Π(pinned cell ÷ seed-origin cell) (DP-A4-1
(B), mechanism B1, `RL-1538`). This file compiles that REAL builder output with the real compiler
and scores it with the real engine, on two real fitted GLMs. Every expected value comes from
`predict_glm` (through `GlmWorld.predict`) and the table cells written here; none is read back
from the engine.

Two Factors (a banded `driv_age_band` over the raw `driv_age`, and a categorical `area`) stand
for the demo's seven: the builder is the same code for any number, and the DB-backed seed run is
the other half of the evidence.
"""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest
from test_rating_glm_model_call import GlmWorld

from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorType,
    GlmSpec,
    LargeLossKind,
    LargeLossTreatment,
    OffsetSpec,
    PerilStructure,
)
from model_schema.perils import PerilComponent, PerilMethod
from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.modelling import fit_glm
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import MODEL_CALL_ERROR_KEY, load_bundle

_ROOT = Path(__file__).resolve().parents[3]
_SPEC = importlib.util.spec_from_file_location(
    "fremtpl2_algorithm_b4", _ROOT / "examples" / "fremtpl2" / "algorithm.py"
)
assert _SPEC is not None
assert _SPEC.loader is not None
demo_algorithm = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(demo_algorithm)

DATASET = uuid4()
FREQUENCY = "model:fremtpl2-freq@1"
SEVERITY = "model:fremtpl2-sev@1"
STRUCTURE = "peril_structure:fremtpl2-ad@1"
ALGORITHM = "rating_algorithm:fremtpl2-rate@1"
LEVELS_AGE = ("18-37", "38-57", "58-77")
AREAS = ("A", "B", "C")
SEED_CELLS = {
    "driv_age_band": {"18-37": "1.30", "38-57": "1.00", "58-77": "0.85"},
    "area": {"A": "1.00", "B": "1.10", "C": "1.20"},
}
#: One cell edited: area C 1.20 -> 1.38, a ratio of exactly 1.15.
EDITED_AREA_C = "1.38"


def _book(n: int = 4_000, seed: int = 20261016) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 78, n).astype(float)
    area = rng.choice(list(AREAS), n)
    exposure = rng.uniform(0.5, 1.0, n)
    rate = 0.08 * np.where(age < 38, 1.5, 1.0) * np.where(area == "C", 1.4, 1.0)
    return pl.DataFrame(
        {
            "driv_age": age,
            "area": area,
            "exposure_years": exposure,
            "claim_count": rng.poisson(rate * exposure).astype(float),
            "severity_minor": rng.gamma(20.0, 60.0 * (1 + rate * 3), n),
        }
    )


#: ONE set of Factors for both models, as the seed's severity GLM copies the frequency GLM's
#: (`fit_severity_glm`): the bundle keys a Factor by `slug@version`, so two Factors that share
#: a slug and differ in id would shadow each other.
_BANDING = Banding(
    id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1, column="driv_age",
    method=BandingMethod.MANUAL, boundaries=(18.0, 38.0, 58.0, 78.0), labels=LEVELS_AGE,
)
_AGE = Factor(
    id=uuid4(), slug="driv_age_band", dataset_id=DATASET, version=1,
    type=FactorType.BANDING, source_columns=("driv_age",), banding_id=_BANDING.id,
)
_AREA = Factor(
    id=uuid4(), slug="area", dataset_id=DATASET, version=1,
    type=FactorType.IDENTITY, source_columns=("area",),
)


def _world(*, offset: bool) -> GlmWorld:
    banding, age, area = _BANDING, _AGE, _AREA
    spec = GlmSpec(
        model_family_slug="fremtpl2-freq" if offset else "fremtpl2-sev",
        dataset_version_id=DATASET,
        response_column="claim_count" if offset else "severity_minor",
        offset=OffsetSpec(kind="log_column", column="exposure_years") if offset
        else OffsetSpec(),
        factors=(age.id, area.id),
        family="poisson" if offset else "gamma",
        link="log",
    )
    fit = fit_glm(_book(), spec, [age, area], bandings={banding.id: banding})
    return GlmWorld(spec, fit.result, (age, area), (banding,), ())


def _structure_payload() -> dict[str, Any]:
    structure = PerilStructure(
        id=uuid4(), slug="fremtpl2-ad", version=1,
        perils=(
            PerilComponent(
                peril="AD",
                method=PerilMethod.FREQUENCY_SEVERITY,
                frequency_model=ArtifactRef.model_validate(FREQUENCY),
                severity_model=ArtifactRef.model_validate(SEVERITY),
                large_loss=LargeLossTreatment(kind=LargeLossKind.NONE),
            ),
        ),
        created_at=datetime(2026, 10, 16, tzinfo=UTC),
    )
    return structure.model_dump(mode="json")


def _table(factor: str, cells: dict[str, str]) -> dict[str, Any]:
    return {
        "slug": f"fremtpl2-{factor.replace('_', '-')}", "version": 1, "rateable": True,
        "storage": "rows",
        "keys": [{"name": factor, "type": "string", "banding_ref": None}],
        "value": {"name": "relativity", "type": "relativity", "unit": "factor",
                  "min": None, "max": None},
        "default_row": None,
        "rows": [{factor: level, "relativity": value} for level, value in cells.items()],
    }


def _ref(factor: str, version: int) -> ArtifactRef:
    return ArtifactRef(
        type="rate_table", slug=f"fremtpl2-{factor.replace('_', '-')}", version=version
    )


class _Resolver:
    """The algorithm, the structure, both GLMs with their Factors, and the pinned tables."""

    def __init__(self, payloads: dict[str, Any], worlds: dict[str, GlmWorld]) -> None:
        self._payloads = payloads
        self._worlds = worlds

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        key = str(ref)
        if ref.type == "rating_algorithm":
            return ResolvedArtifact(status="no_maturity_concept", payload=self._payloads[key])
        world = self._worlds.get(key)
        if world is not None:
            return ResolvedArtifact(
                status="approved", payload=self._payloads[key], factors=world.factors,
                bandings=world.bandings, groupings=world.groupings,
            )
        return ResolvedArtifact(status="approved", payload=self._payloads[key])


async def _engine(
    freq: GlmWorld, sev: GlmWorld, *, edited: bool, premium_suffix: str = ""
) -> Any:
    """The compiled, loaded bundle of the builder's own algorithm, over unedited seed tables
    (`edited` False) or with `area` pinned at an edited version 2 against its seed origin 1."""
    banding = freq.bandings[0]
    seed_refs = {factor: _ref(factor, 1) for factor in SEED_CELLS}
    pinned = dict(seed_refs)
    payloads: dict[str, Any] = {
        FREQUENCY: freq.model_payload(), SEVERITY: sev.model_payload(),
        STRUCTURE: _structure_payload(),
    }
    for factor, cells in SEED_CELLS.items():
        payloads[str(seed_refs[factor])] = _table(factor, cells)
    if edited:
        pinned["area"] = _ref("area", 2)
        payloads[str(pinned["area"])] = _table("area", {**SEED_CELLS["area"], "C": EDITED_AREA_C})
    algorithm = demo_algorithm.build_fremtpl2_algorithm(
        tables=pinned,
        bandings={"driv_age_band": banding},
        base_minor=0,
        domains={"area": list(AREAS)},
        peril_structure_ref=ArtifactRef.model_validate(STRUCTURE),
        origin_tables=seed_refs,
    )
    for step in algorithm["steps"]:
        if step["step_id"] == "s_premium":  # what the journey does: `f"{expr} * ncd_factor"`
            step["expr"] += premium_suffix
    payloads[ALGORITHM] = algorithm
    version = RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "fremtpl2-demo", "version": 1,
        "status": "draft", "dataset_version_id": str(uuid4()), "model_ref": FREQUENCY,
        "created_at": "2026-10-16T12:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-10-16T12:00:00Z", "algorithm_ref": ALGORITHM,
        "pins": {
            "rate_tables": sorted({str(r) for r in (*seed_refs.values(), *pinned.values())}),
            "models": [STRUCTURE], "reference_tables": [], "custom_objectives": [],
        },
        "model_reference_mode": "exact",
    })
    resolver = _Resolver(payloads, {FREQUENCY: freq, SEVERITY: sev})
    return load_bundle(await compile_bundle(version, resolver))  # type: ignore[arg-type]


ROWS = (  # (driv_age, area, exposure_years): the last two sit in area C, the edited cell
    (22.0, "A", 1.0),
    (45.0, "B", 0.75),
    (70.0, "A", 0.5),
    (30.0, "C", 1.0),
    (62.0, "C", 0.6),
)


async def _premium(engine: Any, age: float, area: str, exposure: float) -> Any:
    out = await engine.decision.async_evaluate({
        "driv_age": int(age), "area": area, "exposure_years": exposure, "bonus_malus": 100,
    })
    result = out["result"]
    assert MODEL_CALL_ERROR_KEY not in result, result
    return result


def _prediction(freq: GlmWorld, sev: GlmWorld, age: float, area: str, exposure: float) -> Decimal:
    """frequency x severity, each from `predict_glm`; the large-loss treatment is `none`."""
    return Decimal(repr(freq.predict(driv_age=age, area=area, exposure_years=exposure))) * Decimal(
        repr(sev.predict(driv_age=age, area=area))
    )


@pytest.fixture(scope="module")
def freq() -> GlmWorld:
    return _world(offset=True)


@pytest.fixture(scope="module")
def sev() -> GlmWorld:
    return _world(offset=False)


@pytest.mark.req("FR-222", "FR-249")
async def test_premium_is_the_ruled_combination_unedited(freq: GlmWorld, sev: GlmWorld) -> None:
    """With unedited tables every ratio is exactly 1, so the premium is the structure's
    prediction, and the raw `model_call` value is a second declared output.

    Red first, by cause: on slice (a)'s algorithm (no `peril_structure_ref`) the premium is
    `base x Π relativities`, which is not the prediction."""
    engine = await _engine(freq, sev, edited=False)
    for age, area, exposure in ROWS:
        result = await _premium(engine, age, area, exposure)
        expected = _prediction(freq, sev, age, area, exposure)
        assert float(result["premium_unrounded"]) == pytest.approx(float(expected), rel=1e-12)
        assert float(result["model_premium"]) == pytest.approx(float(expected), rel=1e-12)


@pytest.mark.req("FR-222", "FR-249")
async def test_premium_is_the_ruled_combination_with_an_edited_cell(
    freq: GlmWorld, sev: GlmWorld
) -> None:
    """With `area` C edited 1.20 -> 1.38 the premium is the prediction x 1.15 on rows in that
    cell and the prediction elsewhere (Acceptance 4's second bullet)."""
    engine = await _engine(freq, sev, edited=True)
    ratio = Decimal(EDITED_AREA_C) / Decimal(SEED_CELLS["area"]["C"])
    assert ratio == Decimal("1.15")
    edited_rows = 0
    for age, area, exposure in ROWS:
        result = await _premium(engine, age, area, exposure)
        factor = ratio if area == "C" else Decimal(1)
        edited_rows += area == "C"
        expected = _prediction(freq, sev, age, area, exposure) * factor
        assert float(result["premium_unrounded"]) == pytest.approx(float(expected), rel=1e-12)
        # The raw model_call value is NOT scaled: it is the structure's own prediction.
        assert float(result["model_premium"]) == pytest.approx(
            float(_prediction(freq, sev, age, area, exposure)), rel=1e-12
        )
    assert edited_rows >= 1


@pytest.mark.req("FR-222")
async def test_a_factor_appended_to_the_premium_expression_multiplies_the_whole(
    freq: GlmWorld, sev: GlmWorld
) -> None:
    """The journey forks the algorithm and appends `* ncd_factor` and `* expense_loading` to
    `s_premium`'s expression. The guard's ternary must not swallow the factor into its `else`."""
    engine = await _engine(freq, sev, edited=False, premium_suffix=" * 2")
    age, area, exposure = ROWS[0]
    result = await _premium(engine, age, area, exposure)
    expected = _prediction(freq, sev, age, area, exposure) * 2
    assert float(result["premium_unrounded"]) == pytest.approx(float(expected), rel=1e-12)


@pytest.mark.req("FR-222")
def test_the_goldens_helper_matches_predict_glm(freq: GlmWorld, sev: GlmWorld) -> None:
    """`structure_premium_minor` (what the seed's golden quotes use, from the two fits'
    coefficients) equals the `predict_glm` product, half-even to a minor unit."""
    levels = {"driv_age_band": "38-57", "area": "B"}
    helper = demo_algorithm.structure_premium_minor(
        (freq.fit.coefficients, freq.fit.relativities),
        (sev.fit.coefficients, sev.fit.relativities),
        levels,
    )
    expected = _prediction(freq, sev, 45.0, "B", 1.0).quantize(Decimal(1), ROUND_HALF_EVEN)
    assert helper == int(expected)
