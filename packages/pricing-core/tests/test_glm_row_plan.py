"""The one-row path's per-scorer plan (`GlmRowPlan`, FR-2143, FR-193).

A loaded GLM derives, once, what is the same for every quote: the behaviours map, the parsed dummy
terms and the producible-level verdict per `(slug, level, dtype)`. A quote then pays a set test per
categorical value and a lookup per numeric dummy. A planned quote gets the same refusals, in the
same order, with the same codes and texts as the frame path, and the cache is keyed by the column's
ACTUAL dtype at the call, so it cannot go stale across inputs.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import polars as pl
import pytest
from test_glm_scalar_predict import QUOTES, _synthetic_world

from model_schema import (
    Coefficient,
    Factor,
    FactorType,
    GlmFitResult,
    GlmSpec,
    OffsetSpec,
    RelativityLevel,
    UnseenLevelBehaviour,
)
from pricing_core.modelling.predict import (
    GlmRowPlan,
    PredictionError,
    linear_predictor_row,
    predict_glm,
    predict_glm_row,
)

DATASET = uuid4()


def _coefficient(term: str, estimate: float) -> Coefficient:
    return Coefficient(
        term=term, estimate=estimate, std_error=0.1, z=1.0, p_value=0.5,
        ci_95=(estimate - 0.2, estimate + 0.2),
    )


def _world(
    *, declared: bool = False
) -> tuple[GlmFitResult, GlmSpec, tuple[Factor, ...]]:
    """An identity Factor `veh_count` with ONE dummy term `veh_count[3]`: an `Int64` input produces
    `3`, a `Float64` one produces `3.0`, so the same level has a different verdict per dtype."""
    over: dict[str, Any] = {}
    if declared:
        over["unseen_level_behaviour"] = UnseenLevelBehaviour.MAP_TO_BASE
    factor = Factor(
        id=uuid4(), slug="veh_count", dataset_id=DATASET, version=1, type=FactorType.IDENTITY,
        source_columns=("veh_count",), **over,
    )
    spec = GlmSpec(
        model_family_slug="row-plan", dataset_version_id=DATASET, response_column="claims",
        offset=OffsetSpec(), factors=(factor.id,), family="gamma", link="log",
    )
    fit = GlmFitResult(
        converged=True, iterations=1, fit_seconds=0.0, rows=100,
        coefficients=(_coefficient("intercept", 0.5), _coefficient("veh_count[3]", 0.4)),
        relativities={
            "veh_count": (RelativityLevel(level="0", is_base=True), RelativityLevel(level="3"))
        },
    )
    return fit, spec, (factor,)


def _price(world: Any, value: Any, *, plan: GlmRowPlan | None) -> float:
    fit, spec, factors = world
    return predict_glm_row(fit, {"veh_count": value}, factors, spec, plan=plan)


def _refusal(call: Any) -> tuple[str, tuple[str, ...], str]:
    with pytest.raises(PredictionError) as raised:
        call()
    return raised.value.code, raised.value.terms, str(raised.value)


@pytest.mark.req("FR-193")
def test_a_planned_row_is_bit_identical_to_the_unplanned_row_and_the_frame() -> None:
    """On the parity world, every quote: the plan, no plan, and the frame path agree to the bit."""
    world = _synthetic_world(nulls=False)
    plan = GlmRowPlan(world.fit, world.factors)
    kwargs = world.kwargs()
    for quote in QUOTES[:5]:
        planned = linear_predictor_row(
            world.fit, quote, world.factors, world.spec, plan=plan, **kwargs
        )
        unplanned = linear_predictor_row(world.fit, quote, world.factors, world.spec, **kwargs)
        frame = world.frame_eta(quote)
        assert float(planned[0]).hex() == float(unplanned[0]).hex() == float(frame[0]).hex()
        assert (
            predict_glm_row(world.fit, quote, world.factors, world.spec, plan=plan, **kwargs).hex()
            == world.frame(quote).hex()
        )


@pytest.mark.req("FR-2143")
def test_a_planned_row_refuses_exactly_as_the_unplanned_one_does() -> None:
    """The same code, terms and text: the quote's level is not one the fit saw."""
    world = _world()
    plan = GlmRowPlan(*(world[0], world[2]))
    planned = _refusal(lambda: _price(world, 9, plan=plan))
    unplanned = _refusal(lambda: _price(world, 9, plan=None))
    assert planned == unplanned
    assert planned[0] == "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"
    assert planned[1] == ("veh_count",)


@pytest.mark.req("FR-2143")
def test_a_declared_map_to_base_is_planned_as_the_base_level() -> None:
    world = _world(declared=True)
    plan = GlmRowPlan(world[0], world[2])
    assert plan.checked == ()  # a declared Factor is not checked: all dummies 0 is its base
    assert _price(world, 9, plan=plan).hex() == _price(world, 9, plan=None).hex()


@pytest.mark.req("FR-193")
def test_one_scorer_fed_an_int_then_a_float_then_an_int_gets_the_right_verdict_each_time() -> None:
    """The verdict is keyed by the column's ACTUAL dtype at the call: `3` is producible from an
    `Int64` and not from a `Float64` (`3.0`), and a decimal input can arrive as either."""
    world = _world()
    plan = GlmRowPlan(world[0], world[2])

    first = _price(world, 3, plan=plan)  # Int64: producible, priced
    code, terms, _ = _refusal(lambda: _price(world, 3.0, plan=plan))  # Float64: refused
    again = _price(world, 3, plan=plan)  # Int64 again: still priced (no stale verdict)

    assert code == "MODEL_TERM_UNRESOLVED"
    assert terms == ("veh_count[3]",)
    assert first.hex() == again.hex() == _price(world, 3, plan=None).hex()
    # and the cache holds one verdict per dtype, for the one level of the one slug
    assert len(plan.verdicts) == 2
    assert sorted(str(dtype) for (_, _, dtype) in plan.verdicts) == ["Float64", "Int64"]


@pytest.mark.req("FR-193")
def test_a_plan_is_not_shared_between_models() -> None:
    """A plan belongs to its scorer: another model's plan holds its own verdicts."""
    one, other = _world(), _world()
    plan_one, plan_other = GlmRowPlan(one[0], one[2]), GlmRowPlan(other[0], other[2])
    _price(one, 3, plan=plan_one)
    assert plan_one.verdicts
    assert not plan_other.verdicts
    assert plan_one.verdicts is not plan_other.verdicts


@pytest.mark.req("FR-193")
def test_the_frame_path_is_unchanged_and_takes_no_plan() -> None:
    fit, spec, factors = _world()
    frame = pl.DataFrame({"veh_count": [3, 3]})
    assert [float(x).hex() for x in predict_glm(fit, frame, factors, spec)] == [
        _price((fit, spec, factors), 3, plan=None).hex()
    ] * 2
