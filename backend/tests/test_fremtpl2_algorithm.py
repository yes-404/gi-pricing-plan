"""The freMTPL2 demo's rating algorithm builder (PL-1525, WK-1178 exit-demo slice (a)).

`examples/fremtpl2/algorithm.py` builds the algorithm the seed saves and slice (b)'s journey
reuses. These tests are pure: no database, no Job. The band expression is the one part of the
algorithm the engine does not already own (the engine has no banding step, `runtime.py`), so
it is checked against `apply_banding` itself on every edge.
"""

from __future__ import annotations

import importlib.util
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
import zen

from model_schema import (
    AboveRangePolicy,
    ArtifactRef,
    Banding,
    BandingMethod,
    BelowRangePolicy,
)
from model_schema.rating import RatingAlgorithm
from pricing_core.modelling.bandings import apply_banding

_SPEC = importlib.util.spec_from_file_location(
    "demo_algorithm",
    Path(__file__).resolve().parents[2] / "examples" / "fremtpl2" / "algorithm.py",
)
assert _SPEC is not None
assert _SPEC.loader is not None
demo_algorithm = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(demo_algorithm)

_DATASET = UUID("00000000-0000-0000-0000-0000000000d5")


def _banding(
    column: str,
    boundaries: tuple[float, ...],
    labels: tuple[str, ...],
    *,
    closed: str = "left",
    below: BelowRangePolicy = BelowRangePolicy.ERROR,
    above: AboveRangePolicy = AboveRangePolicy.ERROR,
    null_level: str | None = None,
) -> Banding:
    return Banding(
        id=UUID("00000000-0000-0000-0000-0000000000b1"),
        slug=f"{column}-banding",
        dataset_id=_DATASET,
        version=1,
        column=column,
        method=BandingMethod.MANUAL,
        boundaries=boundaries,
        closed=closed,  # type: ignore[arg-type]
        labels=labels,
        below_range=below,
        above_range=above,
        null_level=null_level,
    )


def _evaluate(expression: str, column: str, value: float) -> Any:
    return zen.evaluate_expression(expression, {column: value})


@pytest.mark.req("FR-97")
@pytest.mark.parametrize("closed", ["left", "right"])
def test_band_expression_maps_each_edge(closed: str) -> None:
    """Just below, at and just above every boundary, the generated ternary gives the label
    `apply_banding` gives. The engine has no banding step, so this is the proof that the
    algorithm's band step and the model's band assignment are one function."""
    import polars as pl

    banding = _banding(
        "driv_age", (18.0, 25.0, 40.0, 60.0, 99.0), ("18-24", "25-39", "40-59", "60+"),
        closed=closed,
    )
    expression = demo_algorithm.band_expression("driv_age", banding)
    values = [
        value
        for boundary in banding.boundaries
        for value in (boundary - 0.5, boundary, boundary + 0.5)
        if banding.boundaries[0] <= value <= banding.boundaries[-1]
    ]
    expected = apply_banding(pl.Series("driv_age", values), banding).to_list()
    got = [_evaluate(expression, "driv_age", value) for value in values]
    assert got == expected


@pytest.mark.req("FR-97")
def test_band_expression_follows_the_declared_out_of_range_policies() -> None:
    """Under `error` the algorithm's input contract refuses the value first, so the chain is
    never asked; `null_level` sends the value to the declared level, as `apply_banding` does."""
    banding = _banding(
        "veh_age", (0.0, 5.0, 10.0), ("new", "old"),
        below=BelowRangePolicy.NULL_LEVEL, above=AboveRangePolicy.NULL_LEVEL,
        null_level="other",
    )
    expression = demo_algorithm.band_expression("veh_age", banding)
    assert _evaluate(expression, "veh_age", -1) == "other"
    assert _evaluate(expression, "veh_age", 11) == "other"
    assert _evaluate(expression, "veh_age", 10) == "old"
    assert _evaluate(expression, "veh_age", 0) == "new"


@pytest.mark.req("FR-97")
def test_band_expression_refuses_a_label_it_cannot_quote() -> None:
    banding = _banding("veh_age", (0.0, 5.0, 10.0), ("it's", "old"))
    with pytest.raises(ValueError, match="label"):
        demo_algorithm.band_expression("veh_age", banding)


def test_base_premium_is_exp_intercept_times_mean_claim_cost_to_whole_minor_units() -> None:
    """DP-a2: `exp(intercept) x mean claim cost`, in Decimal, half-even to a whole minor unit."""
    got = demo_algorithm.base_premium_minor(Decimal("0"), Decimal("197600.5"))
    assert got == 197600  # 197600.5 -> half-even -> the even neighbour
    assert isinstance(got, int)
    assert demo_algorithm.base_premium_minor(Decimal("-3"), Decimal("200000")) == int(
        (Decimal("-3").exp() * Decimal(200000)).quantize(Decimal(1))
    )


def _fixture_algorithm() -> dict[str, Any]:
    bandings = {
        "driv_age_band": _banding(
            "driv_age", (18.0, 25.0, 99.0), ("18-24", "25+")
        ),
    }
    tables = {
        "driv_age_band": ArtifactRef(type="rate_table", slug="fremtpl2-driv-age-band", version=1),
        "veh_gas": ArtifactRef(type="rate_table", slug="fremtpl2-veh-gas", version=1),
    }
    return demo_algorithm.build_fremtpl2_algorithm(
        tables=tables,
        bandings=bandings,
        base_minor=25000,
        domains={"veh_gas": ["Diesel", "Regular"]},
    )


@pytest.mark.req("FR-213")
def test_the_built_algorithm_validates() -> None:
    """The builder returns a dict that `RatingAlgorithm` accepts, with one input per raw
    column (a banded factor's input is its source column, not the factor) plus `bonus_malus`,
    the base step and one output."""
    payload = _fixture_algorithm()
    algorithm = RatingAlgorithm.model_validate(payload)
    assert algorithm.slug == demo_algorithm.FREMTPL2_ALGORITHM_SLUG
    inputs = {field.name: field for field in algorithm.input_contract}
    # The eighth input, `bonus_malus`, is a rating-table input and no step consumes it.
    assert set(inputs) == {"driv_age", "veh_gas", "bonus_malus"}
    assert not any("bonus_malus" in str(step.consumes) for step in algorithm.steps)
    assert inputs["driv_age"].type == "int"
    assert (inputs["driv_age"].min, inputs["driv_age"].max) == (18, 99)
    assert inputs["veh_gas"].domain == ["Diesel", "Regular"]
    step_types = [step.type for step in algorithm.steps]
    assert step_types.count("output") == 1
    base = next(step for step in algorithm.steps if step.step_id == "s_base")
    assert base.note is not None
    assert "a simplification (frequency GLM × mean severity; no severity model)" in base.note


@pytest.mark.req("FR-226")
def test_the_demo_algorithm_declares_no_decimal_output() -> None:
    """`PL-1371` §7, `RL-1343` §4: until the RL-1343 fix merges every declared output is
    `money_minor`. Removed by the slice that merges that fix."""
    algorithm = RatingAlgorithm.model_validate(_fixture_algorithm())
    assert [output.type for output in algorithm.outputs] == ["money_minor"]
    assert [output.name for output in algorithm.outputs] == ["payable_premium_minor"]
