"""SL 2118 question (a): an algorithm can read a key its input contract does not declare.

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
        {
            "step_id": "s_in_ghost",
            "type": "input",
            "label": "Ghost",
            "input_name": "ghost",
            "on_missing": "error",
            "produces": "ghost",
        },
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


# --- SL 2118 option (ii): FR-273's guard covers every numeric value, nested included ---------


async def _score_ghost(value: Any, *, declared: bool = False) -> Any:
    return await score_one(
        await _bundle(declared=declared), _ctx(inputs={**_INPUTS, "ghost": value})
    )


@pytest.mark.req("FR-273")
async def test_a_nested_over_precise_value_is_refused_naming_the_key_path() -> None:
    """The guard refuses even a key no step reads, naming the nested path, not the value."""
    bundle = await _bundle(declared=False)
    ctx = _ctx(inputs={**_INPUTS, "ghost": 0.5, "extra_list": [1.5, {"a": _OVER_PRECISE}]})
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION.*'extra_list\[1\]\.a'") as info:
        await score_one(bundle, ctx)
    assert "0.1234567890123456789" not in str(info.value)  # NFR-499


@pytest.mark.req("FR-273")
@pytest.mark.parametrize("text", ["1e-400", "1e-330", "1e400", "-1e-400", "NaN"])
async def test_an_underflowing_or_overflowing_undeclared_value_is_refused(text: str) -> None:
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION.*'ghost'"):
        await _score_ghost(Decimal(text))


@pytest.mark.req("FR-273")
@pytest.mark.parametrize("text", ["5e-324", "1e-321", "-5e-324", "1e-29", "1e29", "-1e300"])
async def test_a_value_the_engines_decimal_cannot_hold_is_refused_in_an_undeclared_key(
    text: str,
) -> None:
    """Amended by the maintainer's S2 round 3 ruling (to-lead 2026-11-13 21:00:31 GMT): these
    were tolerated by the guard and then failed inside the engine (FD 2122); the guard now
    refuses them, naming the key path."""
    ctx = _ctx(inputs={**_INPUTS, "ghost": 0.5, "unread": Decimal(text)})
    with pytest.raises(ValueError, match=r"INPUT_CONTRACT_VIOLATION.*'unread'") as info:
        await score_one(await _bundle(declared=False), ctx)
    assert text not in str(info.value)  # NFR-499


@pytest.mark.req("FR-273")
@pytest.mark.parametrize("text", ["0.0", "-0.0", "0.5", "-1.5", "1e-28", "7.9e28"])
async def test_a_value_the_float_holds_exactly_is_tolerated_in_an_undeclared_key(
    text: str,
) -> None:
    """The guard accepts it (the float holds it exactly and the engine's decimal holds the
    float) and the engine evaluates it."""
    from pricing_core.rating.score import decimals_as_floats

    assert decimals_as_floats(Decimal(text), "k") == float(text)
    ctx = _ctx(inputs={**_INPUTS, "ghost": 0.5, "unread": Decimal(text)})
    await score_one(await _bundle(declared=False), ctx)


@pytest.mark.req("FR-273")
async def test_integer_and_non_numeric_values_are_untouched_by_the_guard() -> None:
    from pricing_core.rating.score import decimals_as_floats

    value = {"a": 7, "b": True, "c": "x", "d": None, "e": [1, "y", 2.5]}
    assert decimals_as_floats(value, "k") == value


@pytest.mark.req("FR-273")
async def test_score_batch_refuses_an_over_precise_extra_column_row_by_name() -> None:
    import polars as pl
    from test_rating_score_batch import _ctx_to_row

    from pricing_core.rating.score import score_batch

    bundle = await _bundle(declared=False)
    ok = _ctx_to_row(_ctx(inputs={**_INPUTS, "ghost": 0.5}))
    bad = _ctx_to_row(_ctx(inputs={**_INPUTS, "ghost": 0.5}))
    ok["quote_id"], bad["quote_id"] = "OK", "BAD"
    ok["ghost"], bad["ghost"] = Decimal("0.5"), _OVER_PRECISE
    frame = pl.DataFrame([ok, bad], schema_overrides={"ghost": pl.Decimal(scale=19)}).lazy()
    rows = {r["quote_id"]: r for r in score_batch(bundle, frame).collect().to_dicts()}
    assert rows["OK"]["outcome"] in ("quoted", "declined")
    assert rows["BAD"]["outcome"] == "error"
    assert rows["BAD"]["error_code"] == "INPUT_CONTRACT_VIOLATION"
    assert "'ghost'" in rows["BAD"]["error_message"]
    assert "0.1234567890123456789" not in rows["BAD"]["error_message"]
