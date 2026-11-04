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
from decimal import Decimal
from typing import Any

import polars as pl
import pytest
from test_rating_ladder_exact import _chain_algorithm, _compile_payload, _context
from test_rating_score_batch import _contexts, _ctx_to_row
from test_rating_score_batch_outputs import _probe_bundle

from pricing_core.rating import score as score_module
from pricing_core.rating.score import _coerce_output_value, score_batch, score_one

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


@pytest.mark.req("FR-214")
@pytest.mark.parametrize("declared", ["decimal", "relativity", "percentage"])
async def test_a_decimal_family_output_with_no_exact_read_is_refused_naming_no_value(
    declared: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RL-1343 rule 3.1: a non-null `result[name]` with no exact read is never served as the
    float; the `ValueError` names the output and its declared type, not the value (NFR-499)."""
    monkeypatch.setattr(score_module, "_exact", lambda result, name: None)
    with pytest.raises(ValueError, match="has no exact read") as caught:
        await _served("19.8 + 0 * risk_premium_minor", declared=declared, result_type=declared)
    assert "probe_out" in str(caught.value)
    assert declared in str(caught.value)
    assert "19.8" not in str(caught.value)


@pytest.mark.req("FR-254")
@pytest.mark.parametrize("declared_type", ["decimal", "relativity", "percentage"])
@pytest.mark.parametrize(
    "value",
    [27, 19.8, Decimal("19.8"), "1E-7", "-0.00"],
    ids=["int", "float", "Decimal", "exp", "negzero"],
)
def test_the_decimal_family_branch_refuses_anything_but_the_positional_string(
    declared_type: str, value: Any
) -> None:
    """RL-1343 rule 3.4: batch checks the producer's string and converts nothing, so the
    whole-valued 27 (the blind spot `ScoringResult` cannot see) is refused here too."""
    with pytest.raises(ValueError, match=declared_type):
        _coerce_output_value(declared_type, value)


@pytest.mark.req("FR-254")
@pytest.mark.parametrize("declared_type", ["decimal", "relativity", "percentage"])
def test_the_decimal_family_branch_returns_a_positional_string_unchanged(
    declared_type: str,
) -> None:
    assert _coerce_output_value(declared_type, "19.80") == "19.80"
    assert _coerce_output_value(declared_type, "0.00") == "0.00"


@pytest.mark.req("FR-214")
@pytest.mark.parametrize("declared", ["int", "count"])
async def test_a_whole_value_under_an_integral_type_is_served_as_the_integer(
    declared: str,
) -> None:
    """Entry (2), "3.0 -> 3". At 4e399fd0 the engine already returns the integer 3 for
    `3.0 + 0 * x` (probed), so this is a control, not a red: no whole-valued float reaches
    `_build_outputs` from the engine, and the exact-equality rule is carried by the refusal
    test below."""
    result = await _served("3.0 + 0 * risk_premium_minor", declared=declared, result_type=declared)
    assert result.outputs["probe_out"] == 3
    assert type(result.outputs["probe_out"]) is int
    assert '"probe_out":3}' in result.model_dump_json()


@pytest.mark.req("FR-214")
@pytest.mark.parametrize("declared", ["int", "count"])
async def test_a_near_integer_under_an_integral_type_is_refused_with_rating_type_mismatch(
    declared: str,
) -> None:
    """Entry (1), exact equality with no tolerance: `2.9999999999` is not integral. The
    refusal is a coded `ValueError` and names no value (NFR-499)."""
    with pytest.raises(ValueError, match="RATING_TYPE_MISMATCH") as caught:
        await _served(
            "2.9999999999 + 0 * risk_premium_minor", declared=declared, result_type=declared
        )
    assert "2.9999999999" not in str(caught.value)


@pytest.mark.req("FR-255")
@pytest.mark.parametrize("declared", ["int", "count"])
async def test_integral_batch_codes_a_near_integer_row_and_completes_the_run(
    declared: str,
) -> None:
    """RL-1567 DP-4 (a): one producer, so batch codes the fault as `/score` does. Q0 (age 18)
    gives 2.9999999999, the other rows 3.0."""
    compiled = await _probe_bundle(declared, "driver_age == 18 ? 2.9999999999 : 3.0")
    frame = pl.DataFrame([_ctx_to_row(c) for c in _contexts(3)]).lazy()
    rows = {r["quote_id"]: r for r in score_batch(compiled, frame).collect().to_dicts()}
    assert rows["Q0"]["outcome"] == "error"
    assert rows["Q0"]["error_code"] == "RATING_TYPE_MISMATCH"
    assert rows["Q0"]["outputs_json"] is None
    for quote_id in ("Q1", "Q2"):
        assert rows[quote_id]["outcome"] == "quoted"
        assert json.loads(rows[quote_id]["outputs_json"])["probe_out"] == 3
