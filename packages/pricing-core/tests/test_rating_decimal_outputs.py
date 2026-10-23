"""SL-1569 (PL-1568, WK-1178): a declared decimal-family output is served as the engine's exact
`string()` read, rounded once with its output step's `RoundSpec`, written positionally with
exactly `dp` digits, on every scoring path (`RL-1343` rules 1-4).

The fixture is `test_rating_ladder_exact.py`'s chain algorithm (input `risk_premium_minor`)
plus one `expression` step `probe` of the declared `result_type` and one `output` step
`probe_out`; `risk_premium_minor` = 18 stands for the plan's `driver_age` = 18.
"""

from __future__ import annotations

import json
import re
from typing import Any

import pytest
from test_rating_ladder_exact import _chain_algorithm, _compile_payload, _context

from pricing_core.rating.score import score_one

_POSITIONAL = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")


async def _served(
    expr: str,
    *,
    declared: str = "decimal",
    result_type: str = "decimal",
    mode: str = "half_even",
    dp: int = 2,
    risk_premium_minor: Any = 18,
) -> Any:
    payload = _chain_algorithm(factors=[])
    payload["outputs"].append({"name": "probe_out", "type": declared, "required": False})
    payload["steps"].insert(
        -1,
        {
            "step_id": "s_probe",
            "type": "expression",
            "label": "probe",
            "expr": expr,
            "result_type": result_type,
            "consumes": ["risk_premium_minor"],
            "produces": "probe",
        },
    )
    payload["steps"].insert(
        -1,
        {
            "step_id": "s_out_probe",
            "type": "output",
            "label": "probe_out",
            "output_name": "probe_out",
            "rounding": {"mode": mode, "dp": dp},
            "consumes": ["probe"],
        },
    )
    return await score_one(
        await _compile_payload(payload), _context(risk_premium_minor=risk_premium_minor)
    )


def _wire(result: Any) -> Any:
    return json.loads(result.model_dump_json())["outputs"]["probe_out"]


@pytest.mark.req("FR-214")
async def test_a_whole_valued_decimal_output_is_a_string_at_the_declared_dp() -> None:
    """RL-1343 item 1: 27 (the engine's int) is served "27.00" at dp 2."""
    result = await _served("risk_premium_minor * 1.5")
    assert result.outputs["probe_out"] == "27.00"
    assert _wire(result) == "27.00"


@pytest.mark.req("FR-214")
async def test_a_fractional_decimal_output_is_a_string_at_the_declared_dp() -> None:
    result = await _served("risk_premium_minor * 1.1")
    assert result.outputs["probe_out"] == "19.80"
    assert _wire(result) == "19.80"


@pytest.mark.req("FR-226")
@pytest.mark.parametrize(
    ("expr", "mode", "expected"),
    [
        ("1.23456 + 0 * risk_premium_minor", "half_even", "1.23"),
        ("1.225 + 0 * risk_premium_minor", "half_even", "1.22"),
        ("1.225 + 0 * risk_premium_minor", "half_up", "1.23"),
    ],
)
async def test_the_declared_rounding_is_applied_once(expr: str, mode: str, expected: str) -> None:
    result = await _served(expr, mode=mode)
    assert result.outputs["probe_out"] == expected


@pytest.mark.req("FR-273")
async def test_a_value_beyond_float_precision_is_served_exactly() -> None:
    result = await _served("1234567.1234567890123456 + 0 * risk_premium_minor", dp=16)
    assert result.outputs["probe_out"] == "1234567.1234567890123456"


@pytest.mark.req("FR-214")
@pytest.mark.parametrize(
    ("expr", "dp", "expected"),
    [
        ("3.3 + 0 * risk_premium_minor", 4, "3.3000"),
        ("-0.001 + 0 * risk_premium_minor", 2, "0.00"),
        ("0.0000001 + 0 * risk_premium_minor", 7, "0.0000001"),
        ("0 * risk_premium_minor", 7, "0.0000000"),
        ("27 + 0 * risk_premium_minor", 0, "27"),
    ],
)
async def test_the_string_is_positional_with_exactly_dp_digits(
    expr: str, dp: int, expected: str
) -> None:
    result = await _served(expr, dp=dp)
    value = result.outputs["probe_out"]
    assert value == expected
    assert _POSITIONAL.match(value)


@pytest.mark.req("FR-214")
@pytest.mark.parametrize("declared", ["relativity", "percentage"])
@pytest.mark.parametrize(
    ("expr", "expected"),
    [("risk_premium_minor * 1.5", "27.00"), ("risk_premium_minor * 1.1", "19.80")],
)
async def test_relativity_and_percentage_share_the_producer(
    declared: str, expr: str, expected: str
) -> None:
    result = await _served(expr, declared=declared, result_type=declared)
    assert result.outputs["probe_out"] == expected
    assert _wire(result) == expected


@pytest.mark.req("FR-214")
async def test_a_null_decimal_output_stays_null() -> None:
    """Control, not a red (passes before and after). The plan expected the key served as None;
    at 4e399fd0 the engine's null source leaves the name out of `result`, so the output is
    omitted, and the producer must not turn that omission into a string or a float."""
    result = await _served("null")
    assert result.outputs.get("probe_out") is None
