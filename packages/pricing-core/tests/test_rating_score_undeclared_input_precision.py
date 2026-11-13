"""SL 8432 question (a): an algorithm can read a key its input contract does not declare.

An `input` step naming a key that is absent from `input_contract` passes save-time validation
(`validate_algorithm` returns no issue) and compiles; `_validate_inputs` tolerates the extra key;
`_engine_context` then crosses its `Decimal` as a float without FR-273's round-trip guard. So a
value of more than 15 significant digits is priced there, where the same text in a declared
`decimal` input is refused with INPUT_CONTRACT_VIOLATION. RED until the maintainer rules which of
two fixes applies (refuse undeclared keys on the score routes, or guard every numeric key)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
from test_rating_score import _ctx, _FakeResolver, _version
from test_rating_score_decimal_input import _INPUTS

from model_schema.rating import RatingAlgorithm
from pricing_core.rating.compile import compile_bundle, validate_algorithm
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_one

_OVER_PRECISE = Decimal("0.1234567890123456789")


def _payload(resolver: _FakeResolver, *, declared: bool) -> dict[str, Any]:
    """The score fixture whose instalment step reads `ghost`, declared or not."""
    algorithm: dict[str, Any] = resolver._payloads["rating_algorithm:score-fixture@1"]
    if declared:
        algorithm["input_contract"].append({"name": "ghost", "type": "decimal", "nullable": False})
    algorithm["steps"].insert(
        0,
        {"step_id": "s_in_ghost", "type": "input", "label": "Ghost", "input_name": "ghost",
         "on_missing": "error", "produces": "ghost"},
    )
    for step in algorithm["steps"]:
        if step["step_id"] == "s_instalment":
            step["expr"] = "office_premium_minor * (1 + ghost)"
            step["consumes"] = ["office_premium_minor", "ghost"]
    return algorithm


async def _bundle(*, declared: bool) -> CompiledBundle:
    resolver = _FakeResolver()
    _payload(resolver, declared=declared)
    return load_bundle(await compile_bundle(_version(), resolver))


@pytest.mark.req("FR-273")
async def test_an_over_precise_value_in_a_declared_decimal_input_is_refused() -> None:
    """The control: the guard works where the input is declared."""
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION.*'ghost'"):
        await score_one(
            await _bundle(declared=True), _ctx(inputs={**_INPUTS, "ghost": _OVER_PRECISE})
        )


@pytest.mark.req("FR-273")
def test_save_time_validation_lets_an_input_step_name_an_undeclared_key() -> None:
    """The path exists: nothing at save time refuses an `input` step on an undeclared key."""
    resolver = _FakeResolver()
    payload = _payload(resolver, declared=False)
    assert validate_algorithm(RatingAlgorithm.model_validate(payload)) == []


@pytest.mark.req("FR-273")
async def test_an_over_precise_value_in_an_undeclared_input_is_refused_too() -> None:
    """RED: it prices instead (the float 0.12345678901234568 is read by the algorithm)."""
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION.*'ghost'"):
        await score_one(
            await _bundle(declared=False), _ctx(inputs={**_INPUTS, "ghost": _OVER_PRECISE})
        )
