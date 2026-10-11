"""`number(x)` (FR-244 as corrected by RL-1322): a lookup step's output is always a string, so
arithmetic on it goes through `number()`. Written to the engine's actual behaviour: a numeric
string (padded, or in exponent form), a number and a boolean convert; any other string and null
fail the quote with `RATING_EVALUATION_FAILED`, never a bare `RuntimeError` and never a price.

The lookup steps here are `on_miss="default"`: a consumer of an `on_miss="error"` lookup's
output that fails for another reason reads `REFERENCE_LOOKUP_MISS` (RL-1313's stated residual,
fail-closed), which is not what these cases test.
"""

from __future__ import annotations

import pytest
from test_rating_pin_membership import (
    _EXTRA,
    _LOOKUP_1,
    _lookup_algo,
    _ref_table_payload,
    _resolver,
    _with_pins,
)
from test_rating_score import _ctx

from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import load_bundle
from pricing_core.rating.score import score_one


async def _price(
    payload_value: str | None, expr: str | None = None, *, table: dict | None = None
) -> int:
    algo = _lookup_algo()
    if expr is not None:
        next(s for s in algo["steps"] if s["step_id"] == "s_office")["expr"] = expr
    extra = dict(_EXTRA)
    if payload_value is not None:
        extra["reference_table:expense@1"] = _ref_table_payload(payload_value, payload_value)
    if table is not None:
        extra["reference_table:expense@1"] = table
    version = _with_pins(rate_tables=[], reference_tables=_LOOKUP_1)
    bundle = await compile_bundle(version, _resolver(extra, algo))
    result = await score_one(load_bundle(bundle), _ctx())
    return int(result.outputs["payable_premium_minor"])


@pytest.mark.req("FR-244")
async def test_a_lookup_string_is_used_in_arithmetic_through_number() -> None:
    """The capability RL-1322 restores; 1507 is the #988 control (channel `direct`, `1.1`)."""
    assert await _price("1.1") == 1_507


@pytest.mark.req("FR-244")
@pytest.mark.parametrize(("padded", "plain"), [(" 1.5 ", "1.5"), ("1e3", "1000")])
async def test_a_padded_or_exponent_string_converts_like_its_plain_form(
    padded: str, plain: str
) -> None:
    assert await _price(padded) == await _price(plain)


@pytest.mark.req("FR-244")
@pytest.mark.parametrize(("string_form", "literal"), [
    ("number(' 1.5 ')", "1.5"),
    ("number('1e3')", "1000"),
    ("number('1.1')", "1.1"),
])
async def test_a_numeric_string_converts_to_the_ruled_exact_decimal(
    string_form: str, literal: str
) -> None:
    """RL-1322: the outcome is the plain literal's, asserted directly."""
    assert await _price("1.1", expr=f"risk_premium_minor * {string_form}") == await _price(
        "1.1", expr=f"risk_premium_minor * {literal}"
    )


@pytest.mark.req("FR-244")
async def test_a_missing_lookup_row_takes_the_default() -> None:
    """`number(v ?? '1.0')` defaults a missing value; no row means the output is null.

    The value is the lookup's own DECLARED output, with no row for the quote's channel. (It was
    an undeclared name; FR-246 now refuses that at compile, covered by
    `test_rating_declared_reads.py`.)"""
    broker_only = {"rows": [{"key": "broker", "payload": {"expense_factor": "1.5"},
                             "effective_from": "2020-01-01", "effective_to": None}]}
    expr = "risk_premium_minor * number(expense_factor ?? '1.0')"
    assert await _price(None, expr=expr, table=broker_only) == 1_370


@pytest.mark.req("FR-244")
@pytest.mark.parametrize(("expr", "same_as"), [
    ("risk_premium_minor * number(5)", "risk_premium_minor * 5"),
    ("risk_premium_minor * number(true)", "risk_premium_minor * 1"),
    ("risk_premium_minor * number(false) + 1", "risk_premium_minor * 0 + 1"),
])
async def test_a_number_and_a_boolean_convert(expr: str, same_as: str) -> None:
    assert await _price("1.1", expr=expr) == await _price("1.1", expr=same_as)


@pytest.mark.req("FR-244")
@pytest.mark.parametrize("value", ["abc", "", "1,07"])
async def test_a_non_numeric_lookup_value_fails_the_quote_with_a_coded_error(value: str) -> None:
    with pytest.raises(ValueError, match=r"^RATING_EVALUATION_FAILED:"):
        await _price(value)


@pytest.mark.req("FR-244")
async def test_null_fails_the_quote_with_a_coded_error() -> None:
    with pytest.raises(ValueError, match=r"^RATING_EVALUATION_FAILED:"):
        await _price("1.1", expr="risk_premium_minor * number(null)")
