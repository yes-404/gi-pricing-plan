"""The numeric-level check runs for EVERY dummy term of a column (`MODEL_TERM_UNRESOLVED`, FR-193).

A dummy `slug[level]` whose level the column's numeric type cannot produce (`3+` on an `Int64`)
has an indicator of 0 on every row. Both paths refuse it for every dummy term of the column, in
whatever order the coefficients are listed, before the unseen-level rule and whatever the Factor
declares.
"""

from __future__ import annotations

import math
from typing import Any
from uuid import uuid4

import polars as pl
import pytest

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
from pricing_core.modelling.predict import PredictionError, predict_glm, predict_glm_row

DATASET = uuid4()
B0, B_ONE, B_THREE_PLUS = 0.5, 0.2, 0.7


def _coefficient(term: str, estimate: float) -> Coefficient:
    return Coefficient(
        term=term, estimate=estimate, std_error=0.1, z=1.0, p_value=0.5,
        ci_95=(estimate - 0.2, estimate + 0.2),
    )


def _world(
    order: tuple[str, ...], *, declared: bool = False
) -> tuple[GlmFitResult, GlmSpec, tuple[Factor, ...]]:
    over: dict[str, Any] = {}
    if declared:
        over["unseen_level_behaviour"] = UnseenLevelBehaviour.MAP_TO_BASE
    factor = Factor(
        id=uuid4(), slug="veh_count", dataset_id=DATASET, version=1, type=FactorType.IDENTITY,
        source_columns=("veh_count",), **over,
    )
    spec = GlmSpec(
        model_family_slug="numeric-terms", dataset_version_id=DATASET, response_column="claims",
        offset=OffsetSpec(), factors=(factor.id,), family="gamma", link="log",
    )
    estimates = {"veh_count[1]": B_ONE, "veh_count[3+]": B_THREE_PLUS}
    fit = GlmFitResult(
        converged=True, iterations=1, fit_seconds=0.0, rows=100,
        coefficients=(
            _coefficient("intercept", B0), *(_coefficient(t, estimates[t]) for t in order)
        ),
        relativities={
            "veh_count": (
                RelativityLevel(level="0", is_base=True),
                RelativityLevel(level="1"),
                RelativityLevel(level="3+"),
            )
        },
    )
    return fit, spec, (factor,)


def _frame_price(world: tuple[GlmFitResult, GlmSpec, tuple[Factor, ...]], value: Any) -> float:
    fit, spec, factors = world
    return float(predict_glm(fit, pl.DataFrame({"veh_count": [value]}), factors, spec)[0])


def _row_price(world: tuple[GlmFitResult, GlmSpec, tuple[Factor, ...]], value: Any) -> float:
    fit, spec, factors = world
    return predict_glm_row(fit, {"veh_count": value}, factors, spec)


SECOND = ("veh_count[1]", "veh_count[3+]")
FIRST = ("veh_count[3+]", "veh_count[1]")


@pytest.mark.req("FR-193")
@pytest.mark.parametrize("price", [_frame_price, _row_price], ids=["frame", "row"])
@pytest.mark.parametrize("declared", [False, True], ids=["undeclared", "map_to_base"])
def test_an_unproducible_numeric_term_listed_second_is_refused(price: Any, declared: bool) -> None:
    """(i) Listed second, the term is refused, whatever the Factor declares: `map_to_base` does
    not turn such a term into a base price."""
    with pytest.raises(PredictionError) as raised:
        price(_world(SECOND, declared=declared), 4)
    assert raised.value.code == "MODEL_TERM_UNRESOLVED"
    assert raised.value.terms == ("veh_count[3+]",)


@pytest.mark.req("FR-193")
@pytest.mark.parametrize("price", [_frame_price, _row_price], ids=["frame", "row"])
def test_an_unproducible_numeric_term_listed_first_is_refused(price: Any) -> None:
    """(ii) Listed first, the term is refused too: the answer does not depend on the order."""
    with pytest.raises(PredictionError) as raised:
        price(_world(FIRST), 4)
    assert raised.value.code == "MODEL_TERM_UNRESOLVED"
    assert raised.value.terms == ("veh_count[3+]",)


@pytest.mark.req("FR-193")
@pytest.mark.parametrize("order", [SECOND, FIRST], ids=["second", "first"])
def test_a_text_column_prices_the_hand_computed_values(order: tuple[str, ...]) -> None:
    """(iii) A text column produces any level, so `3+` is a level and nothing is refused: the
    values are computed by hand and both paths agree to the bit, in either coefficient order."""
    world = _world(order)
    fit, spec, factors = world
    expected = {"1": math.exp(B0 + B_ONE), "3+": math.exp(B0 + B_THREE_PLUS), "0": math.exp(B0)}
    for value, price in expected.items():
        frame = float(
            predict_glm(fit, pl.DataFrame({"veh_count": [value]}), factors, spec)[0]
        )
        row = predict_glm_row(fit, {"veh_count": value}, factors, spec)
        assert frame.hex() == row.hex()
        assert frame == pytest.approx(price, rel=1e-12)
