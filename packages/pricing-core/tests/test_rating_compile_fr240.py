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

from model_schema.modelling import Factor, FactorIntent, ModelStatus
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
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle

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
    await compile_bundle(_version(), _model_fitted_on(FactorIntent.RISK))


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
