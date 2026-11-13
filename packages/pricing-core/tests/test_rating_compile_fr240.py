"""FR-240's transitive and control-intent clauses at compile (`PL-1471`, SL-1472).

An unapproved custom objective reached through a pinned model is refused with
`PIN_NOT_APPROVED`; a `control`-intent Factor in a rateable path is refused with
`CONTROL_FACTOR_IN_RATEABLE_PATH` (`02` FR-88). The helpers are `test_rating_compile_bundle`'s.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from test_rate_table_operations import _factor, _glm_model
from test_rating_compile_bundle import FakeResolver, _resolver, _version

# isort: split
from test_rating_compile_bundle import (
    NCD,
    _fragment_payload,
    _mounted_resolver,
    _mounted_version,
)

from model_schema.modelling import (
    Factor,
    FactorIntent,
    FactorType,
    Model,
    ModelStatus,
    RelativityLevel,
)
from model_schema.rating import (
    RateTable,
    RateTableKey,
    RateTableStorageMode,
    RateTableValue,
    RateTableValueType,
    RatingVersion,
)
from model_schema.refs import ArtifactRef
from pricing_core.rate_tables.operations import seed_from_model
from pricing_core.rating.compile import (
    ResolvedArtifact,
    _refuse_control_factor_features,
    _refuse_control_factor_keys,
    compile_bundle,
)

OBJ = "custom_objective:asym-loss@1"
MODEL = "model:motor-ad-frequency@7"


def _with_objective(status: str) -> FakeResolver:
    res = _resolver()
    res._payloads[MODEL]["spec"] = {
        "model_type": "gbm",
        "objective": {"kind": "custom", "ref": OBJ},
    }
    res._payloads[OBJ] = {"slug": "asym-loss", "version": 1}
    res._statuses[OBJ] = status
    return res


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
@pytest.mark.parametrize("status", ["certified", "review", "deprecated"])
async def test_an_unapproved_objective_reached_through_a_pinned_model_is_refused(
    status: str,
) -> None:
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED") as refused:
        await compile_bundle(_version(), _with_objective(status))
    message = str(refused.value)
    assert MODEL in message
    assert OBJ in message
    assert repr(status) in message


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
async def test_an_approved_objective_reached_through_a_pinned_model_compiles() -> None:
    bundle = await compile_bundle(_version(), _with_objective("approved"))
    # checked, not embedded: the objective's payload is not in the Bundle (FR-239).
    assert OBJ not in bundle.resolved_payloads


@pytest.mark.req("FR-240")
async def test_a_builtin_objective_needs_no_resolution() -> None:
    res = _resolver()
    res._payloads[MODEL]["spec"] = {
        "model_type": "gbm",
        "objective": {"kind": "builtin", "ref": None},
    }
    # `OBJ` has no payload: a resolve of it would `KeyError`, so passing proves no lookup.
    await compile_bundle(_version(), res)


# -- A control-intent Factor in a rateable path (FR-88, FR-240, DP-3, DP-4) ----------------

TABLE = "rate_table:motor-expense@3"


def _control(slug: str = "driver_age_band") -> Factor:
    return _factor(slug).model_copy(update={"intent": FactorIntent.CONTROL})


def _table_keyed_on(factor: Factor, *, rateable: bool) -> RateTable:
    """The table a seed would have made, built directly since the seed now refuses."""
    return RateTable(
        slug="motor-expense",
        version=3,
        rateable=rateable,
        storage=RateTableStorageMode.ROWS,
        keys=[
            RateTableKey(
                name=factor.slug,
                type="string",
                banding_ref=None,
                factor_ref=ArtifactRef(type="factor", slug=factor.slug, version=factor.version),
            )
        ],
        value=RateTableValue(
            name="relativity", type=RateTableValueType.RELATIVITY, unit="factor",
            min=None, max=None,
        ),
    )


def _with_keyed_table(factor: Factor, *, rateable: bool) -> FakeResolver:
    res = _resolver()
    res._payloads[TABLE] = _table_keyed_on(factor, rateable=rateable).model_dump(mode="json")
    res._payloads[f"factor:{factor.slug}@{factor.version}"] = factor.model_dump(mode="json")
    res._statuses[f"factor:{factor.slug}@{factor.version}"] = "no_maturity_concept"
    return res


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-230")
@pytest.mark.req("FR-240")
def test_seeding_from_a_control_factor_is_refused() -> None:
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH"):
        seed_from_model(
            _glm_model(ModelStatus.APPROVED),
            factor="driver_age_band",
            factors=[_control()],
            table_slug="motor-relativity",
            change_note="seed",
            seeded_at=datetime(2026, 10, 8, 10, 0, tzinfo=UTC),
        )


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.parametrize("rateable", [True, False])
async def test_a_pinned_table_keyed_on_a_control_factor_is_refused(rateable: bool) -> None:
    """DP-4 (a): whatever the table's `rateable` flag, "the flag is declarative"."""
    factor = _control()
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        await compile_bundle(_version(), _with_keyed_table(factor, rateable=rateable))
    message = str(refused.value)
    assert TABLE in message
    assert factor.slug in message
    assert f"factor:{factor.slug}@{factor.version}" in message


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_table_keyed_on_a_risk_factor_compiles() -> None:
    await compile_bundle(_version(), _with_keyed_table(_factor("driver_age_band"), rateable=True))


# -- A control-intent Factor through a `model_call` (FD 9639, DP-7) ------------------------


class _FactorsResolver(FakeResolver):
    """A `FakeResolver` that also hands a pinned model its Factors, as the platform does."""

    def __init__(self, base: FakeResolver, factors: dict[str, tuple[Factor, ...]]) -> None:
        super().__init__(base._payloads, base._statuses)
        self._factors = factors

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        resolved = await super().resolve(ref)
        return ResolvedArtifact(
            status=resolved.status,
            payload=resolved.payload,
            factors=self._factors.get(str(ref), ()),
        )


def _model_fitted_on(year_intent: FactorIntent) -> _FactorsResolver:
    res = _resolver()
    res._payloads[MODEL]["fit_result"] = {
        "model_type": "xgboost",
        "feature_order": ["driver_age", "year_of_account"],
    }
    year = _factor("year_of_account").model_copy(update={"intent": year_intent})
    return _FactorsResolver(res, {MODEL: (_factor("driver_age"), year)})


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_model_call_over_a_gbm_fitted_on_a_control_factor_is_refused() -> None:
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        await compile_bundle(_version(), _model_fitted_on(FactorIntent.CONTROL))
    message = str(refused.value)
    assert MODEL in message
    assert "year_of_account" in message
    assert "year_of_account@1" in message


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_model_call_over_risk_factors_compiles() -> None:
    res = _model_fitted_on(FactorIntent.RISK)
    # FR-240's completeness clause (SL-1541): the map supplies every feature the model was
    # fitted on, `year_of_account` through the step's second graph name.
    step = next(
        s for s in res._payloads["rating_algorithm:motor-gb@14"]["steps"] if s["step_id"] == "s_rp"
    )
    step["feature_map"] = {"driver_age": "driver_age", "rating_area": "year_of_account"}
    await compile_bundle(_version(), res)


# -- FD-1495's GLM arm: the consumed Factors come from the fields each arm carries (SL-1985) --

OFFSET_MODEL = "model:offset-glm@2"


def _coefficient(term: str) -> dict[str, object]:
    return {
        "term": term, "estimate": 0.1, "std_error": 0.01, "z": 10.0, "p_value": 0.0,
        "ci_95": [0.08, 0.12],
    }


def _glm_fit(*terms: str) -> dict[str, object]:
    return {"model_type": "glm", "coefficients": [_coefficient(t) for t in terms]}


class _GlmOffsetResolver(_FactorsResolver):
    """A `_FactorsResolver` that also hands a pinned GLM the model its offset reads."""

    def __init__(
        self, base: _FactorsResolver, offset_factors: tuple[Factor, ...],
        offset_fit: dict[str, object],
    ) -> None:
        super().__init__(base, base._factors)
        self._offset_factors = offset_factors
        self._offset_fit = offset_fit

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        resolved = await super().resolve(ref)
        if str(ref) != MODEL:
            return resolved
        return ResolvedArtifact(
            status=resolved.status,
            payload={
                **resolved.payload,
                "spec": {"model_type": "glm", "offset": {
                    "kind": "model", "offset_model_ref": OFFSET_MODEL,
                }},
            },
            factors=resolved.factors,
            offset_source=ResolvedArtifact(
                status="approved",
                payload={"fit_result": self._offset_fit},
                factors=self._offset_factors,
            ),
        )


def _glm_fitted_on(year_intent: FactorIntent, *terms: str) -> _FactorsResolver:
    res = _resolver()
    res._payloads[MODEL]["fit_result"] = _glm_fit(*terms)
    year = _factor("year_of_account").model_copy(update={"intent": year_intent})
    base = _FactorsResolver(res, {MODEL: (_factor("driver_age"), year)})
    step = next(
        s for s in res._payloads["rating_algorithm:motor-gb@14"]["steps"] if s["step_id"] == "s_rp"
    )
    step["feature_map"] = {"driver_age": "driver_age", "rating_area": "year_of_account"}
    return base


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_model_call_over_a_glm_fitted_on_a_control_factor_is_refused() -> None:
    res = _glm_fitted_on(
        FactorIntent.CONTROL, "intercept", "driver_age", "year_of_account[2024]"
    )
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        await compile_bundle(_version(), res)
    message = str(refused.value)
    assert MODEL in message
    assert "year_of_account" in message
    assert "year_of_account@1" in message


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_model_call_over_a_glm_fitted_on_risk_factors_compiles() -> None:
    res = _glm_fitted_on(
        FactorIntent.RISK, "intercept", "driver_age", "year_of_account[2024]"
    )
    await compile_bundle(_version(), res)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_model_call_over_a_glm_whose_offset_model_is_fitted_on_a_control_factor_is_refused() -> None:  # noqa: E501
    pin = _glm_fitted_on(FactorIntent.RISK, "intercept", "driver_age", "year_of_account[2024]")
    control = _factor("vehicle_age").model_copy(update={"intent": FactorIntent.CONTROL})
    res = _GlmOffsetResolver(pin, (control,), _glm_fit("intercept", "vehicle_age"))
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        await compile_bundle(_version(), res)
    message = str(refused.value)
    assert OFFSET_MODEL in message
    assert "vehicle_age@1" in message


def _gbm_fit(**fields: object) -> dict[str, object]:
    return {"model_type": "xgboost", **fields}


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.parametrize(
    "fit_result",
    [
        pytest.param({"model_type": "glm"}, id="glm-no-coefficients"),
        pytest.param(_glm_fit("intercept"), id="glm-intercept-only"),
        pytest.param(_gbm_fit(), id="gbm-no-feature_order"),
        pytest.param(_gbm_fit(feature_order=[]), id="gbm-empty-feature_order"),
    ],
)
async def test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused(
    fit_result: dict[str, object],
) -> None:
    res = _glm_fitted_on(FactorIntent.RISK, "intercept", "driver_age")
    res._payloads[MODEL]["fit_result"] = fit_result
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        await compile_bundle(_version(), res)
    message = str(refused.value)
    assert MODEL in message
    assert "cannot be derived" in message


# -- G1's objective clause through a pinned sub-graph (WK-1250 Slice 2, RL-1309 G1) ----------

PLANTED = "model:planted@1"


def _planted_in_a_sub_graph(objective_status: str) -> tuple[RatingVersion, FakeResolver]:
    """A fragment whose `model_call` names a model that is pinned and whose custom objective has
    `objective_status`. The parent algorithm has no `model_call` of its own to that model."""
    step = {
        "step_id": "s_rp", "type": "model_call", "label": "m", "model_ref": PLANTED,
        "mode": "exact", "feature_map": {"ncd_years": "ncd_years"},
        "consumes": ["ncd_years"], "produces": "ncd_factor",
    }
    version = _mounted_version()
    pins = version.pins
    assert pins is not None
    version = version.model_copy(update={
        "pins": pins.model_copy(update={"models": [*pins.models, ArtifactRef.parse(PLANTED)]}),
    })
    resolver = _mounted_resolver(fragments={NCD: _fragment_payload(steps=[step])})
    resolver._payloads[PLANTED] = {
        "model_type": "gbm", "status": "approved", "feature_map": {"ncd_years": "ncd_years"},
        "fit_result": {"model_type": "xgboost", "feature_order": ["ncd_years"]},
        "spec": {"model_type": "gbm", "objective": {"kind": "custom", "ref": OBJ}},
    }
    resolver._payloads[OBJ] = {"slug": "asym-loss", "version": 1}
    resolver._statuses[OBJ] = objective_status
    return version, resolver


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-217")
@pytest.mark.parametrize("status", ["certified", "review", "deprecated"])
async def test_g1_an_unapproved_objective_planted_in_a_pinned_sub_graph_is_refused(
    status: str,
) -> None:
    version, resolver = _planted_in_a_sub_graph(status)
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED") as refused:
        await compile_bundle(version, resolver)
    assert PLANTED in str(refused.value)
    assert OBJ in str(refused.value)


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-217")
async def test_g1_an_approved_objective_in_a_pinned_sub_graph_compiles() -> None:
    version, resolver = _planted_in_a_sub_graph("approved")
    bundle = await compile_bundle(version, resolver)
    assert "m_ncd__s_rp" in bundle.graph.nodes


# -- A stored cell the engine cannot read (FD-1648, SL-2020, PL-2019 R1.3) -----------------


def _with_cells(*raws: str) -> FakeResolver:
    res = _resolver()
    res._payloads[TABLE] = {
        "rateable": True,
        "keys": [{"name": "driver_age_band", "type": "string"}],
        "value": {"name": "relativity"},
        "rows": [
            {"driver_age_band": f"band-{at}", "relativity": raw} for at, raw in enumerate(raws)
        ],
    }
    return res


@pytest.mark.req("FR-234")
@pytest.mark.req("FR-240")
@pytest.mark.parametrize("raw", ["1E+2", "1.36E-7", ".5", "true", "false", "1+1"])
async def test_a_stored_cell_the_engine_cannot_read_does_not_compile(raw: str) -> None:
    """The backstop for a version saved before the write-time refusal existed."""
    with pytest.raises(ValueError, match="RATE_TABLE_CELL_UNPARSEABLE") as refused:
        await compile_bundle(_version(), _with_cells("1.5", raw))
    message = str(refused.value)
    assert TABLE in message
    assert "band-1" in message
    assert repr(raw) in message


@pytest.mark.req("FR-234")
@pytest.mark.req("FR-240")
@pytest.mark.parametrize("raw", ["1.36e-7", "1_000", "100"])
async def test_a_stored_cell_the_engine_reads_compiles(raw: str) -> None:
    await compile_bundle(_version(), _with_cells("1.5", raw))


# -- FD-1495's interaction limb (SL 8429): a `control` OPERAND of a `risk` interaction ---------
#
# A cross is a design column of its own and its operands get no term (`02` FR-92), so a pinned
# model that prices through `<cross>[a | x]` consumes only the cross's slug. FR-88's "never
# rated on" and FR-240's "fitted on a control Factor" reach the operands, at any depth.

def _interaction(slug: str, *operands: Factor) -> Factor:
    return Factor(
        id=_factor(slug).id,
        slug=slug,
        dataset_id=operands[0].dataset_id,
        version=1,
        type=FactorType.INTERACTION,
        source_columns=(),
        operand_factor_ids=tuple(operand.id for operand in operands),
    )


def _controlled(slug: str) -> Factor:
    return _factor(slug).model_copy(update={"intent": FactorIntent.CONTROL})


CROSS_TERMS = ("intercept", "region_x_yoa[A | 2010]", "region_x_yoa[B | 2011]")


def _crossed() -> tuple[Factor, Factor, Factor]:
    region, yoa = _factor("region"), _controlled("yoa")
    return _interaction("region_x_yoa", region, yoa), region, yoa


def _glm_pin(factors: tuple[Factor, ...], *terms: str) -> ResolvedArtifact:
    return ResolvedArtifact(
        status="approved", payload={"fit_result": _glm_fit(*terms)}, factors=factors
    )


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_the_feature_guard_refuses_a_risk_interaction_over_a_control_operand() -> None:
    cross, region, yoa = _crossed()
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        _refuse_control_factor_features(MODEL, _glm_pin((cross, region, yoa), *CROSS_TERMS))
    message = str(refused.value)
    assert "yoa@1" in message  # the OPERAND ...
    assert "region_x_yoa" in message  # ... and the cross that carries it
    assert MODEL in message


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_the_feature_guard_passes_a_risk_interaction_over_risk_operands() -> None:
    region, plan = _factor("region"), _factor("plan")
    cross = _interaction("region_x_yoa", region, plan)
    _refuse_control_factor_features(MODEL, _glm_pin((cross, region, plan), *CROSS_TERMS))


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_the_feature_guard_expands_a_nested_interaction_to_its_leaves() -> None:
    """Depth 2: `outer = inner x plan`, `inner = region x yoa(control)`.

    `_cross` refuses an interaction operand at resolution, so a nested cross cannot be scored;
    the guard still expands it, so no pin can be shown clean by the resolver refusing first.
    """
    cross, region, yoa = _crossed()
    plan = _factor("plan")
    outer = _interaction("outer_x", cross, plan)
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        _refuse_control_factor_features(
            MODEL,
            _glm_pin((outer, cross, region, yoa, plan), "intercept", "outer_x[a | b]"),
        )
    assert "yoa@1" in str(refused.value)
    assert "outer_x" in str(refused.value)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_the_feature_guard_refuses_an_operand_that_is_not_among_the_pins_factors() -> None:
    """Fail closed: an operand the pin does not carry cannot be shown not to be `control`."""
    cross, region, _yoa = _crossed()
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        _refuse_control_factor_features(MODEL, _glm_pin((cross, region), *CROSS_TERMS))
    assert "region_x_yoa" in str(refused.value)
    assert str(_yoa.id) in str(refused.value)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_the_feature_guard_refuses_a_control_operand_in_the_offset_model() -> None:
    """The `offset_source` branch of the same function."""
    cross, region, yoa = _crossed()
    pin = ResolvedArtifact(
        status="approved",
        payload={
            "fit_result": _glm_fit("intercept", "driver_age"),
            "spec": {"offset": {"kind": "model", "offset_model_ref": OFFSET_MODEL}},
        },
        factors=(_factor("driver_age"),),
        offset_source=_glm_pin((cross, region, yoa), *CROSS_TERMS),
    )
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        _refuse_control_factor_features(MODEL, pin)
    assert OFFSET_MODEL in str(refused.value)
    assert "yoa@1" in str(refused.value)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
def test_the_feature_guard_refuses_a_missing_operand_in_the_offset_model() -> None:
    cross, region, _yoa = _crossed()
    pin = ResolvedArtifact(
        status="approved",
        payload={
            "fit_result": _glm_fit("intercept", "driver_age"),
            "spec": {"offset": {"kind": "model", "offset_model_ref": OFFSET_MODEL}},
        },
        factors=(_factor("driver_age"),),
        offset_source=_glm_pin((cross, region), *CROSS_TERMS),
    )
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH"):
        _refuse_control_factor_features(MODEL, pin)


def _interaction_resolver(
    operands_intent: FactorIntent, *, carry_operands: bool = True
) -> _FactorsResolver:
    """`compile_bundle`'s harness with a GLM over `region_x_yoa`, fed through the model_call."""
    region = _factor("region")
    yoa = _factor("yoa").model_copy(update={"intent": operands_intent})
    cross = _interaction("region_x_yoa", region, yoa)
    res = _resolver()
    res._payloads[MODEL]["fit_result"] = _glm_fit(*CROSS_TERMS)
    step = next(
        s for s in res._payloads["rating_algorithm:motor-gb@14"]["steps"] if s["step_id"] == "s_rp"
    )
    step["feature_map"] = {"driver_age": "region", "rating_area": "yoa", "channel": "region_x_yoa"}
    step["consumes"] = ["driver_age", "rating_area", "channel"]
    res._payloads[MODEL]["feature_map"] = {
        "region": "region", "yoa": "yoa", "region_x_yoa": "region_x_yoa",
    }
    pinned = (cross, region, yoa) if carry_operands else (cross, region)
    return _FactorsResolver(res, {MODEL: pinned})


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_model_call_over_a_glm_with_a_control_operand_interaction_is_refused() -> None:
    res = _interaction_resolver(FactorIntent.CONTROL)
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        await compile_bundle(_version(), res)
    message = str(refused.value)
    assert MODEL in message
    assert "yoa@1" in message
    assert "region_x_yoa" in message


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_model_call_over_a_glm_with_a_risk_operand_interaction_compiles() -> None:
    """The positive control: the same harness, risk operands, compiles."""
    await compile_bundle(_version(), _interaction_resolver(FactorIntent.RISK))


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_a_model_call_over_a_glm_whose_interaction_operand_is_missing_is_refused() -> None:
    res = _interaction_resolver(FactorIntent.RISK, carry_operands=False)
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH"):
        await compile_bundle(_version(), res)


def _table_keyed_on_the_cross(cross: Factor) -> dict[str, object]:
    return _table_keyed_on(cross, rateable=True).model_dump(mode="json")


def _keyed_resolver(cross: Factor, chain: tuple[Factor, ...]) -> _FactorsResolver:
    res = _resolver()
    ref = f"factor:{cross.slug}@{cross.version}"
    res._payloads[TABLE] = _table_keyed_on_the_cross(cross)
    res._payloads[ref] = cross.model_dump(mode="json")
    res._statuses[ref] = "no_maturity_concept"
    return _FactorsResolver(res, {ref: chain})


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_the_key_guard_refuses_a_table_keyed_on_an_interaction_of_a_control_operand() -> None:
    cross, region, yoa = _crossed()
    resolver = _keyed_resolver(cross, (cross, region, yoa))
    version = _version()
    payloads = {TABLE: _table_keyed_on_the_cross(cross)}
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        await _refuse_control_factor_keys(version, payloads, resolver)
    message = str(refused.value)
    assert TABLE in message
    assert "yoa@1" in message
    assert "region_x_yoa" in message


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_the_key_guard_expands_a_nested_interaction_to_its_leaves() -> None:
    cross, region, yoa = _crossed()
    plan = _factor("plan")
    outer = _interaction("outer_x", cross, plan)
    resolver = _keyed_resolver(outer, (outer, cross, region, yoa, plan))
    payloads = {TABLE: _table_keyed_on_the_cross(outer)}
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        await _refuse_control_factor_keys(_version(), payloads, resolver)
    assert "yoa@1" in str(refused.value)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_the_key_guard_refuses_an_interaction_whose_operand_is_not_resolved() -> None:
    cross, region, _yoa = _crossed()
    resolver = _keyed_resolver(cross, (cross, region))
    payloads = {TABLE: _table_keyed_on_the_cross(cross)}
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH"):
        await _refuse_control_factor_keys(_version(), payloads, resolver)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
async def test_the_key_guard_passes_an_interaction_of_risk_operands() -> None:
    region, plan = _factor("region"), _factor("plan")
    cross = _interaction("region_x_plan", region, plan)
    resolver = _keyed_resolver(cross, (cross, region, plan))
    payloads = {TABLE: _table_keyed_on_the_cross(cross)}
    await _refuse_control_factor_keys(_version(), payloads, resolver)


def _cross_model() -> Model:
    levels = (RelativityLevel(level="A | 2010", relativity=1.1, estimate=0.1),)
    return _glm_model(ModelStatus.APPROVED, relativities={"region_x_yoa": levels})


def _seed_cross(factors: list[Factor]) -> None:
    seed_from_model(
        _cross_model(),
        factor="region_x_yoa",
        factors=factors,
        table_slug="motor-relativity",
        change_note="seed",
        seeded_at=datetime(2026, 11, 13, 10, 0, tzinfo=UTC),
    )


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-230")
@pytest.mark.req("FR-240")
def test_seeding_from_an_interaction_of_a_control_operand_is_refused() -> None:
    cross, region, yoa = _crossed()
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
        _seed_cross([cross, region, yoa])
    assert "yoa@1" in str(refused.value)
    assert "region_x_yoa" in str(refused.value)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-230")
@pytest.mark.req("FR-240")
def test_seeding_from_a_nested_interaction_expands_to_the_leaves() -> None:
    cross, region, yoa = _crossed()
    plan = _factor("plan")
    outer = _interaction("region_x_yoa", cross, plan)  # the bound slug is the outer one
    inner = cross.model_copy(update={"slug": "inner_x"})
    outer = outer.model_copy(update={"operand_factor_ids": (inner.id, plan.id)})
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH"):
        _seed_cross([outer, inner, region, yoa, plan])


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-230")
@pytest.mark.req("FR-240")
def test_seeding_from_an_interaction_with_a_missing_operand_is_refused() -> None:
    cross, region, _yoa = _crossed()
    with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH"):
        _seed_cross([cross, region])


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-230")
@pytest.mark.req("FR-240")
def test_seeding_from_an_interaction_of_risk_operands_succeeds() -> None:
    region, plan = _factor("region"), _factor("plan")
    _seed_cross([_interaction("region_x_yoa", region, plan), region, plan])


@pytest.mark.req("FR-88")
def test_rateable_drops_an_interaction_whose_closure_holds_a_control_factor() -> None:
    """G5: `rateable()` is the one definition, so it reads the operands too."""
    from pricing_core.modelling.factors import rateable

    cross, region, yoa = _crossed()
    plan = _factor("plan")
    fine = _interaction("region_x_plan", region, plan)
    assert rateable([cross, region, yoa, plan, fine]) == (region, plan, fine)
