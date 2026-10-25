"""A `model_call` may not pin a GBM fitted on a banded or grouped Factor (SL 8071; FD 8073 (to be
filed after the probe run); FR-222 and FR-240 as amended 2026-10-16).

The defect, by reading at `a2f77b2d` (the maintainer's (by delegation) entry headed
"2026-10-16 10:59:28 BST"): `fit_gbm` bands the raw column and encodes the label ordinally into
`categorical_maps`, but a GBM pin carries no Bandings into the Bundle (`_carry_glm_inputs`) and
the runtime scores with `factors=()`. A raw value is therefore looked up as if it were the band
label. Case A: a raw `driver_age` is no label, so scoring raises `GbmFitError` (loud). Case C:
bands labelled "1", "2", "3" and a raw int 2 is another band's label, so it prices the wrong band
with no error (silent). The interim rule is to refuse the pin at compile with
`MODEL_CALL_GBM_TRANSFORMED_FACTOR`, and to turn a `GbmFitError` raised while scoring into the
named `MODEL_CALL_FAILED` failure rather than the engine's generic `NodeError`.

Fixtures: the fitted-GBM world and the `model_call` graph are the recipe of the probe's scratch
test, rebuilt here from the neighbouring modules' helpers; none is imported from the probe.
"""

from __future__ import annotations

import re
from functools import cache
from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest
from test_rating_glm_model_call import age_glm
from test_rating_runtime import _compiled as compiled_runtime_world

from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    OffsetSpec,
    SplitRef,
)
from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.modelling.gbm import GbmFitError, fit_gbm, predict_gbm
from pricing_core.rating import runtime
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import MODEL_CALL_ERROR_KEY

DATASET = uuid4()
MODEL_REF = "model:banded-gbm@1"
BACKENDS = ["xgboost", "lightgbm"]
CODE = r"^MODEL_CALL_GBM_TRANSFORMED_FACTOR: "


class GbmWorld:
    """A GBM really fitted on one banded Factor, as the worker persists it."""

    def __init__(self, backend: str, *, column: str, labels: tuple[str, ...],
                 boundaries: tuple[float, ...], lo: int, hi: int) -> None:
        self.column = column
        self.banding = Banding(
            id=uuid4(), slug=f"{column.replace('_', '-')}-bands", dataset_id=DATASET, version=1,
            column=column,
            method=BandingMethod.MANUAL, boundaries=boundaries, labels=labels,
        )
        self.factor = Factor(
            id=uuid4(), slug=f"{column}_band", dataset_id=DATASET, version=1,
            type=FactorType.BANDING, source_columns=(column,), banding_id=self.banding.id,
        )
        spec = GbmSpec(
            model_type=backend, model_family_slug="banded-gbm", dataset_version_id=DATASET,
            split_ref=SplitRef(split_artifact_id=uuid4()), response_column="severity",
            offset=OffsetSpec(kind="none"),
            objective=GbmFunctionRef(kind="builtin", name="reg:gamma"),
            categorical_handling="native",
            hyperparameters={"max_depth": 3, "eta": 0.3, "num_boost_round": 20},
            early_stopping=None, factors=(self.factor.id,),
        )
        rng = np.random.default_rng(20261016)
        raw = rng.integers(lo, hi, 2_000)
        step = np.searchsorted(np.array(boundaries[1:-1]), raw, side="right")
        book = pl.DataFrame({
            column: raw.astype(float),
            "severity": 100.0 * (1.0 + 2.0 * step) * rng.uniform(0.95, 1.05, 2_000),
            "claim_count": np.ones(2_000),
        })
        fit = fit_gbm(book, spec, [self.factor], bandings={self.banding.id: self.banding})
        self.payload: dict[str, Any] = {
            "model_family_slug": "banded-gbm", "version": 1, "status": "approved",
            "spec": spec.model_dump(mode="json"),
            "fit_result": {
                **fit.result.model_dump(mode="json"),
                "booster_content": fit.booster_bytes.decode("utf-8"),
            },
        }


@cache
def _age_world(backend: str) -> GbmWorld:
    """Case A's model: bands over `driver_age`, labelled as ranges."""
    return GbmWorld(
        backend, column="driver_age", labels=("17-37", "38-57", "58+"),
        boundaries=(17.0, 38.0, 58.0, 100.0), lo=17, hi=99,
    )


@cache
def _numeric_label_world(backend: str) -> GbmWorld:
    """Case C's model: bands over `veh_power` labelled "1", "2", "3" (the band index)."""
    return GbmWorld(
        backend, column="veh_power", labels=("1", "2", "3"),
        boundaries=(0.0, 5.0, 10.0, 20.0), lo=1, hi=19,
    )


def _algorithm(world: GbmWorld) -> dict[str, Any]:
    """One RAW input (`world.column`) -> a `model_call` mapping it onto the Factor slug."""
    column, slug = world.column, world.factor.slug
    return {
        "slug": "banded-gbm-probe", "version": 1,
        "input_contract": [
            {"name": column, "type": "int", "nullable": False, "min": 0, "max": 999}
        ],
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": column,
             "on_missing": "error", "produces": column},
            {"step_id": "s_risk", "type": "model_call", "label": "Risk", "model_ref": MODEL_REF,
             "mode": "exact", "feature_map": {column: slug}, "consumes": [column],
             "produces": ["risk"], "result_type": "decimal"},
            {"step_id": "s_out", "type": "output", "label": "Risk", "output_name": "risk_out",
             "rounding": {"mode": "half_even", "dp": 6}, "consumes": ["risk"]},
        ],
        "sub_graphs": [],
    }


def _algorithm_without_a_call(world: GbmWorld) -> dict[str, Any]:
    """The same pinned graph with NO `model_call`: the banded GBM is pinned and never scored."""
    column = world.column
    return {
        "slug": "banded-gbm-probe", "version": 1,
        "input_contract": [
            {"name": column, "type": "int", "nullable": False, "min": 0, "max": 999}
        ],
        "outputs": [{"name": "premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": column,
             "on_missing": "error", "produces": column},
            {"step_id": "s_x", "type": "expression", "label": "X", "expr": f"{column} * 100",
             "result_type": "money_minor", "consumes": [column], "produces": "x_minor"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["x_minor"]},
        ],
        "sub_graphs": [],
    }


def _version() -> RatingVersion:
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "banded-gbm-probe",
        "version": 1, "status": "draft", "dataset_version_id": str(uuid4()),
        "model_ref": MODEL_REF, "created_at": "2026-10-16T12:00:00Z",
        "created_by": str(uuid4()), "updated_at": "2026-10-16T12:00:00Z",
        "algorithm_ref": "rating_algorithm:banded-gbm-probe@1",
        "pins": {"rate_tables": [], "models": [MODEL_REF], "reference_tables": [],
                 "custom_objectives": []},
        "model_reference_mode": "exact",
    })


class _Resolver:
    """As the backend resolver does for a GBM pin: Factors loaded, nothing else carried."""

    def __init__(
        self, world: GbmWorld, *, factor: Factor | None = None, call: bool = True
    ) -> None:
        self._call = call
        self._world = world
        self._factor = factor or world.factor

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        if ref.type == "rating_algorithm":
            payload = (
                _algorithm(self._world) if self._call
                else _algorithm_without_a_call(self._world)
            )
            return ResolvedArtifact(status="no_maturity_concept", payload=payload)
        assert str(ref) == MODEL_REF, ref
        return ResolvedArtifact(
            status="approved", payload=self._world.payload, factors=(self._factor,),
            bandings=(self._world.banding,),
        )


@pytest.mark.req("FR-222", "FR-240")
@pytest.mark.parametrize("backend", BACKENDS)
async def test_case_c_numeric_looking_band_labels_are_refused_at_compile(backend: str) -> None:
    """Case C, the SILENT one: bands labelled "1", "2", "3" and a raw int 2 (which belongs to
    band "1") used to price band "2"'s code with no error. It is now refused before it can be
    pinned into a rating, naming the step, the model and the Factor."""
    world = _numeric_label_world(backend)
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), _Resolver(world))
    message = str(caught.value)
    assert "'s_risk'" in message
    assert MODEL_REF in message
    assert world.factor.slug in message


@pytest.mark.req("FR-222", "FR-240")
@pytest.mark.parametrize("backend", BACKENDS)
async def test_case_a_a_raw_value_into_a_banded_gbm_is_refused_at_compile(backend: str) -> None:
    """Case A, the LOUD one: a raw `driver_age` into a GBM fitted on its band raised
    `GbmFitError` on every quote. It is now refused at compile, not discovered per quote."""
    world = _age_world(backend)
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), _Resolver(world))
    message = str(caught.value)
    assert "'s_risk'" in message
    assert world.factor.slug in message
    assert "banding" in message


@pytest.mark.req("FR-222", "FR-240", "NFR-499")
async def test_the_gbm_factor_refusal_message_is_exactly_its_structural_fields() -> None:
    """The raise site is `_INPUT_FREE` in test_quote_input_raise_sites.py: the text is the step id,
    the pinned model ref and the Factor slug and kind, so no quote-row value can appear in it.

    RED at main: the text there says "fitted on banded or grouped Factors"; S4 (FD-1754, the
    maintainer's decision (2) of 2026-10-25 13:07:06 GMT) re-words it to "fitted on transformed
    Factors [<slug> (<kind>), ...]" because every non-IDENTITY Factor type is now refused."""
    world = _age_world("xgboost")
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), _Resolver(world))
    assert str(caught.value) == (
        f"MODEL_CALL_GBM_TRANSFORMED_FACTOR: step 's_risk': {MODEL_REF} is a GBM fitted on "
        f"transformed Factors [{world.factor.slug} (banding)], which a model_call cannot score: "
        "a GBM is fitted on the Factors' transformed values and the Bundle carries only the raw "
        "inputs (FR-222, FR-240)"
    )


@pytest.mark.req("FR-222", "FR-240")
async def test_a_grouped_factor_is_refused_too() -> None:
    """The same defect for a grouped Factor (a raw level equal to a group name)."""
    world = _age_world("xgboost")
    grouped = world.factor.model_copy(
        update={"type": FactorType.GROUPING, "banding_id": None, "grouping_id": uuid4()}
    )
    resolver = _Resolver(world, factor=grouped)
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), resolver)
    assert "grouping" in str(caught.value)


@pytest.mark.req("FR-222", "FR-240")
async def test_a_banded_gbm_pinned_but_never_called_still_compiles() -> None:
    """The refusal is keyed on a `model_call` STEP, never on a pin: WF-699 pins the banded demo
    GBM (C1) and recompiles it (C5) with no `model_call` reaching it (journey.py skips B4/C1')."""
    bundle = await compile_bundle(_version(), _Resolver(_age_world("xgboost"), call=False))
    assert bundle.content_hash


@pytest.mark.req("FR-222", "FR-240")
async def test_a_gbm_on_plain_factors_still_compiles() -> None:
    """The control: the refusal is on the Factor's type. A GBM whose Factors are `identity`
    pins as before (the runtime fixture's GBM has none, and `compiled_runtime_world` builds it
    through the real `compile_bundle`)."""
    compiled = await compiled_runtime_world()
    out = await compiled.decision.async_evaluate({"driver_age": 34, "channel": "direct"})
    assert MODEL_CALL_ERROR_KEY not in out["result"]


@pytest.mark.req("FR-222", "FR-240")
async def test_a_glm_on_a_banded_factor_still_compiles() -> None:
    """The control: a GLM carries its Bandings into the Bundle, so a banded GLM is not
    refused (`age_glm`'s one Factor is a banding)."""
    glm = age_glm()
    assert any(factor.type is FactorType.BANDING for factor in glm.factors)
    compiled = await compiled_runtime_world(glm=True)
    out = await compiled.decision.async_evaluate({"driver_age": 34, "channel": "direct"})
    assert MODEL_CALL_ERROR_KEY not in out["result"]


@pytest.mark.req("FR-222", "FR-255", "NFR-499")
async def test_a_gbm_fit_error_while_scoring_is_the_named_model_call_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`GbmFitError` is neither a `ModellingError` nor a `PredictionError`, so it escaped the
    `model_call` handler and surfaced as the zen binding's generic `NodeError`, with no code.
    It is now the `MODEL_CALL_FAILED` failure naming the error's own code, and the error's text
    (which can carry a quote's value) is never passed on."""

    def _failing(*args: Any, **kwargs: Any) -> Any:
        raise GbmFitError("UNSEEN_LEVEL_BEHAVIOUR_REQUIRED", "level 'SENTINEL-3c9d' unseen")

    monkeypatch.setattr(runtime, "predict_gbm", _failing)
    compiled = await compiled_runtime_world()

    out = await compiled.decision.async_evaluate({"driver_age": 34, "channel": "direct"})
    message = out["result"][MODEL_CALL_ERROR_KEY]
    assert message.startswith("MODEL_CALL_FAILED: UNSEEN_LEVEL_BEHAVIOUR_REQUIRED")
    assert "SENTINEL" not in message


# ---------------------------------------------------------------------------
# S4 (PL 8227; FD-1754's open limb): EXPRESSION and INTERACTION Factors on a pinned GBM.
#
# A GBM `model_call` scores with `factors=()` over the graph's values keyed by the model's
# feature slugs, i.e. every feature is read as its RAW value under its slug. That is right only
# for an IDENTITY Factor. The maintainer's decision (1) of 2026-10-25 13:07:06 GMT: refuse every
# non-IDENTITY type for a pinned GBM in a model_call. The probe rule below is the invariant that
# decision protects: a `model_call` on a pinned GBM is either refused at compile with
# MODEL_CALL_GBM_TRANSFORMED_FACTOR, or it prices exactly as `predict_gbm(factors=<real>)` does
# on the same quote, with no MODEL_CALL_ERROR_KEY. Fixtures mirror the ones above.
# ---------------------------------------------------------------------------

EXPR_SOURCE = "veh_power + 0"


class _FactorWorld:
    """A GBM really fitted on a given tuple of Factors (and Bandings) over a given book."""

    def __init__(
        self,
        backend: str,
        factors: tuple[Factor, ...],
        bandings: tuple[Banding, ...],
        book: pl.DataFrame,
    ) -> None:
        self.factors = factors
        self.bandings = bandings
        spec = GbmSpec(
            model_type=backend,
            model_family_slug="banded-gbm",
            dataset_version_id=DATASET,
            split_ref=SplitRef(split_artifact_id=uuid4()),
            response_column="severity",
            offset=OffsetSpec(kind="none"),
            objective=GbmFunctionRef(kind="builtin", name="reg:gamma"),
            categorical_handling="native",
            hyperparameters={"max_depth": 3, "eta": 0.3, "num_boost_round": 20},
            early_stopping=None,
            factors=tuple(f.id for f in factors),
        )
        self.fit = fit_gbm(book, spec, list(factors), bandings={b.id: b for b in bandings})
        self.payload: dict[str, Any] = {
            "model_family_slug": "banded-gbm",
            "version": 1,
            "status": "approved",
            "spec": spec.model_dump(mode="json"),
            "fit_result": {
                **self.fit.result.model_dump(mode="json"),
                "booster_content": self.fit.booster_bytes.decode("utf-8"),
            },
        }

    def predict(self, quote: dict[str, Any]) -> float:
        """`predict_gbm` with the REAL Factors over the quote's raw source columns."""
        frame = pl.DataFrame({name: [value] for name, value in quote.items()})
        series = predict_gbm(
            self.fit.result,
            self.fit.booster_bytes,
            frame,
            self.factors,
            bandings={b.id: b for b in self.bandings},
            nthread=1,
        )
        return float(series[0])


@cache
def _expression_world(backend: str, *, slug: str) -> _FactorWorld:
    """`veh_power` through the expression `veh_power + 0`, banded "1", "2", "3" (as Case C).
    `slug == "veh_power"` is E-b (the Factor's slug IS its one source column); any other slug
    is E-a."""
    banding = Banding(
        id=uuid4(),
        slug="veh-power-expr-bands",
        dataset_id=DATASET,
        version=1,
        column=None,
        source_expression=EXPR_SOURCE,
        method=BandingMethod.MANUAL,
        boundaries=(0.0, 5.0, 10.0, 20.0),
        labels=("1", "2", "3"),
    )
    factor = Factor(
        id=uuid4(),
        slug=slug,
        dataset_id=DATASET,
        version=1,
        type=FactorType.EXPRESSION,
        source_columns=("veh_power",),
        expression=EXPR_SOURCE,
        banding_id=banding.id,
    )
    rng = np.random.default_rng(20261025)
    raw = rng.integers(1, 19, 2_000)
    step = np.searchsorted(np.array(banding.boundaries[1:-1]), raw, side="right")
    book = pl.DataFrame(
        {
            "veh_power": raw.astype(float),
            "severity": 100.0 * (1.0 + 2.0 * step) * rng.uniform(0.95, 1.05, 2_000),
            "claim_count": np.ones(2_000),
        }
    )
    return _FactorWorld(backend, (factor,), (banding,), book)


@cache
def _cross_world(backend: str) -> _FactorWorld:
    """`area` and `zone` (identity, strings "A"/"B") and their INTERACTION `area_x_zone`. The
    cell "A | B" is dearer (x3) than the other three, so a wrong cell prices apart."""
    area, zone = (
        Factor(
            id=uuid4(),
            slug=name,
            dataset_id=DATASET,
            version=1,
            type=FactorType.IDENTITY,
            source_columns=(name,),
        )
        for name in ("area", "zone")
    )
    cross = Factor(
        id=uuid4(),
        slug="area_x_zone",
        dataset_id=DATASET,
        version=1,
        type=FactorType.INTERACTION,
        operand_factor_ids=(area.id, zone.id),
    )
    rng = np.random.default_rng(20261025)
    areas = rng.choice(["A", "B"], 2_000)
    zones = rng.choice(["A", "B"], 2_000)
    dear = (areas == "A") & (zones == "B")
    book = pl.DataFrame(
        {
            "area": areas,
            "zone": zones,
            "severity": 100.0 * np.where(dear, 3.0, 1.0) * rng.uniform(0.95, 1.05, 2_000),
            "claim_count": np.ones(2_000),
        }
    )
    return _FactorWorld(backend, (area, zone, cross), (), book)


def _probe_algorithm(inputs: dict[str, str], feature_map: dict[str, str]) -> dict[str, Any]:
    """Each graph input (name -> `int` or `string`) feeds one `model_call`, mapped by
    `feature_map` (graph name -> model slug)."""
    return {
        "slug": "banded-gbm-probe",
        "version": 1,
        "input_contract": [
            {
                "name": name,
                "type": kind,
                "nullable": False,
                **({"min": 0, "max": 999} if kind == "int" else {}),
            }
            for name, kind in inputs.items()
        ],
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": [
            *(
                {
                    "step_id": f"s_in_{name}",
                    "type": "input",
                    "label": name,
                    "input_name": name,
                    "on_missing": "error",
                    "produces": name,
                }
                for name in inputs
            ),
            {
                "step_id": "s_risk",
                "type": "model_call",
                "label": "Risk",
                "model_ref": MODEL_REF,
                "mode": "exact",
                "feature_map": feature_map,
                "consumes": list(inputs),
                "produces": ["risk"],
                "result_type": "decimal",
            },
            {
                "step_id": "s_out",
                "type": "output",
                "label": "Risk",
                "output_name": "risk_out",
                "rounding": {"mode": "half_even", "dp": 6},
                "consumes": ["risk"],
            },
        ],
        "sub_graphs": [],
    }


class _ProbeResolver:
    """As the backend resolver does for a GBM pin: Factors and Bandings loaded."""

    def __init__(self, world: _FactorWorld, algorithm: dict[str, Any]) -> None:
        self._world = world
        self._algorithm = algorithm

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        if ref.type == "rating_algorithm":
            return ResolvedArtifact(status="no_maturity_concept", payload=self._algorithm)
        assert str(ref) == MODEL_REF, ref
        return ResolvedArtifact(
            status="approved",
            payload=self._world.payload,
            factors=self._world.factors,
            bandings=self._world.bandings,
        )


def _e_b(backend: str) -> tuple[_FactorWorld, dict[str, Any], dict[str, Any]]:
    world = _expression_world(backend, slug="veh_power")
    return (
        world,
        _probe_algorithm({"veh_power": "int"}, {"veh_power": "veh_power"}),
        {"veh_power": 2},
    )  # raw 2 is band "1"; "2" is another band's label


def _e_a(backend: str) -> tuple[_FactorWorld, dict[str, Any], dict[str, Any]]:
    world = _expression_world(backend, slug="veh_power_expr")
    return (
        world,
        _probe_algorithm({"veh_power": "int"}, {"veh_power": "veh_power"}),
        {"veh_power": 2},
    )  # the slug is no input: required inputs are the source columns


def _i_cell_swapped(backend: str) -> tuple[_FactorWorld, dict[str, Any], dict[str, Any]]:
    world = _cross_world(backend)
    algorithm = _probe_algorithm(
        {"area": "string", "zone": "string", "cross": "string"},
        {"area": "area", "zone": "zone", "cross": "area_x_zone"},
    )
    # area=A, zone=B is the dear cell "A | B"; the graph supplies the OTHER observed cell.
    return world, algorithm, {"area": "A", "zone": "B", "cross": "B | A"}


PROBES = {"E-b": _e_b, "E-a": _e_a, "I-cell-swapped": _i_cell_swapped}


@pytest.mark.req("FR-222", "FR-240")
@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("case", sorted(PROBES))
async def test_a_gbm_model_call_prices_as_predict_gbm_or_is_refused(
    backend: str, case: str
) -> None:
    """The probe rule (FD-1754, S4): a `model_call` on a pinned GBM is refused at compile with
    MODEL_CALL_GBM_TRANSFORMED_FACTOR, or prices exactly as `predict_gbm(factors=<real>)`.

    RED at main, per case: E-b compiles and prices band "2"'s code for a band "1" value
    (silent); E-a compiles and fails every quote with `MODEL_CALL_FAILED:
    SCORING_FEATURES_MISMATCH` (loud, but neither refused nor priced); I-cell-swapped compiles
    and prices the cell "B | A" the graph supplied instead of the quote's "A | B" (silent).
    Green once `gbm_transformed_factors` refuses every non-IDENTITY type."""
    world, algorithm, quote = PROBES[case](backend)
    try:
        compiled = await compile_bundle(_version(), _ProbeResolver(world, algorithm))
    except ValueError as refusal:
        refused = str(refusal)
    else:
        refused = ""
    if refused:
        assert re.match(CODE, refused), refused
        return
    out = await compiled.decision.async_evaluate(quote)
    assert MODEL_CALL_ERROR_KEY not in out["result"], out["result"].get(MODEL_CALL_ERROR_KEY)
    expected = world.predict(quote)
    assert float(out["result"]["risk_out"]) == pytest.approx(expected, rel=1e-6, abs=1e-6)


@pytest.mark.req("FR-222", "FR-240")
@pytest.mark.parametrize("backend", BACKENDS)
async def test_case_e_an_expression_factor_on_a_gbm_is_refused_at_compile(backend: str) -> None:
    """RED at main: an EXPRESSION Factor (E-b, slug == its source column) compiles, so
    `pytest.raises` finds nothing. Refused once the filter is "any type other than IDENTITY"."""
    world, algorithm, _ = _e_b(backend)
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), _ProbeResolver(world, algorithm))
    message = str(caught.value)
    assert "'s_risk'" in message
    assert MODEL_REF in message
    assert "veh_power (expression)" in message


@pytest.mark.req("FR-222", "FR-240")
@pytest.mark.parametrize("backend", BACKENDS)
async def test_case_i_an_interaction_factor_on_a_gbm_is_refused_at_compile(backend: str) -> None:
    """RED at main: an INTERACTION Factor compiles (its cross value is taken as supplied). The
    refusal lists the cross, not its IDENTITY operands, which a model_call scores correctly."""
    world, algorithm, _ = _i_cell_swapped(backend)
    with pytest.raises(ValueError, match=CODE) as caught:
        await compile_bundle(_version(), _ProbeResolver(world, algorithm))
    message = str(caught.value)
    assert "'s_risk'" in message
    assert MODEL_REF in message
    assert "area_x_zone (interaction)" in message
    assert "(identity)" not in message
