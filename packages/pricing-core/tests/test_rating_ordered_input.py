"""`RL-1613` (WK-675 S5): an `ordered` enum takes part in a `monotone` property, and an
unordered input leaves every bundle hash unchanged (FR-213, FR-261)."""

from __future__ import annotations

import asyncio
import copy
from typing import Any

import pytest
from test_rating_score import _algorithm_payload, _FakeResolver, _version
from test_rating_shadowed_inputs import _SCORE_FIXTURE_HASH
from test_testing import _CTX, _result

from model_schema.rating import InputContractField, RatingAlgorithm
from model_schema.regression import MonotoneInInput
from pricing_core.rating.compile import compile_bundle, to_jdm
from pricing_core.rating.properties import (
    UnsweepableProperty,
    counterexample_points,
    monotone_field,
    monotone_grid,
    monotone_sweep,
)

_LEVELS = ["low", "mid", "high"]


def _ordered(**kw: Any) -> InputContractField:
    return InputContractField.model_validate(
        {"name": "band", "type": "enum", "domain": _LEVELS, "ordered": True, **kw})


def _check(**kw: Any) -> MonotoneInInput:
    return MonotoneInInput.model_validate(
        {"kind": "monotone", "input": "band", "direction": "increasing", **kw})


# --- the hash condition (RL-1613 ruling item 2 (i)-(iv)) -----------------------------------


class _Resolver(_FakeResolver):
    def __init__(self, *, ordered: bool | None) -> None:
        super().__init__()
        if ordered is not None:
            key = "rating_algorithm:score-fixture@1"
            payload = copy.deepcopy(self._payloads[key])
            channel = next(f for f in payload["input_contract"] if f["name"] == "channel")
            channel["ordered"] = ordered
            self._payloads[key] = payload


def _hash(*, ordered: bool | None) -> str:
    return asyncio.run(compile_bundle(_version(), _Resolver(ordered=ordered))).content_hash


@pytest.mark.req("FR-213")
def test_an_explicit_ordered_false_hashes_as_an_input_that_never_declared_it() -> None:
    """(ii) The omission: the dump drops `ordered: false`, so the hash is the value recorded at
    the slice's base (`_SCORE_FIXTURE_HASH`), not merely equal to another hash that moved too."""
    assert _hash(ordered=None) == _SCORE_FIXTURE_HASH
    assert _hash(ordered=False) == _SCORE_FIXTURE_HASH


@pytest.mark.req("FR-213")
def test_ordered_true_enters_the_hash() -> None:
    """(iv) Opt-in changes the hash."""
    assert _hash(ordered=True) != _hash(ordered=None)


@pytest.mark.req("FR-213")
def test_the_graph_dump_carries_ordered_only_when_true() -> None:
    algo = RatingAlgorithm.model_validate(_algorithm_payload())
    assert all("ordered" not in f for f in to_jdm(algo).model_dump()["input_contract"])


# --- the sweep (FR-261 case (4), amended) --------------------------------------------------


@pytest.mark.req("FR-261")
def test_an_ordered_enum_is_admitted_and_its_grid_is_every_level_in_declared_order() -> None:
    field = _ordered()
    assert monotone_field([field], _check()) is field
    assert monotone_grid(field, _check(), 1) == _LEVELS
    assert monotone_grid(field, _check(), 2) == _LEVELS  # no sampled points
    from pricing_core.rating.properties import monotone_grid_kind

    assert monotone_grid_kind(field, _check()) == "levels"


@pytest.mark.req("FR-261")
def test_a_numeric_grid_keeps_its_label() -> None:
    field = InputContractField.model_validate({"name": "n", "type": "int", "min": 0, "max": 9})
    from pricing_core.rating.properties import monotone_grid_kind

    assert monotone_grid_kind(field, _check(input="n")) == "uniform+sampled"


@pytest.mark.req("FR-261")
@pytest.mark.parametrize("kw", [
    {"type": "enum", "domain": _LEVELS},                  # unordered: stays refused
    {"type": "enum", "domain": _LEVELS, "ordered": False},
    {"type": "string"},
    {"type": "date"},
    {"type": "bool"},
], ids=["unordered-enum", "ordered-false", "string", "date", "bool"])
def test_every_other_non_numeric_input_stays_refused(kw: dict[str, Any]) -> None:
    field = InputContractField.model_validate({"name": "band", **kw})
    with pytest.raises(UnsweepableProperty, match=r"band.*not orderable"):
        monotone_field([field], _check())


@pytest.mark.req("FR-261")
@pytest.mark.parametrize("bound", [{"lower": "1"}, {"upper": "2"}])
def test_lower_and_upper_mean_nothing_on_levels_and_are_refused(bound: dict[str, str]) -> None:
    with pytest.raises(UnsweepableProperty, match=r"band.*lower.*upper"):
        monotone_field([_ordered()], _check(**bound))


def _by_level(premiums: dict[str, int]) -> Any:
    return lambda ctx: _result(premiums[ctx.inputs["band"]])


@pytest.mark.req("FR-261")
def test_a_sweep_follows_declared_order_not_alphabetical_order() -> None:
    field = _ordered()
    rising = _by_level({"low": 100, "mid": 200, "high": 300})  # alphabetical: high < low < mid
    assert monotone_sweep(_check(), field, _CTX, rising, 0).broken_at is None
    falling = monotone_sweep(_check(direction="decreasing"), field, _CTX, rising, 0)
    assert falling.broken_at == ("low", "mid")


@pytest.mark.req("FR-261")
def test_a_planted_inversion_names_the_two_adjacent_levels() -> None:
    inverted = _by_level({"low": 100, "mid": 300, "high": 200})
    assert counterexample_points(_check(), [_ordered()], _CTX, inverted, 0) == ["mid", "high"]
