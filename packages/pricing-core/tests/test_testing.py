"""`evaluate_golden_quotes` (03 §5.2, FR-260, FR-273; PL-1189 Task 3).

The pure re-score behind the submit gate: every golden quote is scored on the synchronous
engine path `score_batch` uses, and compared exactly in integer minor units within its
declared tolerance. Reuses Task 1.4's fixtures (`_compiled`, `_ctx`) from
`test_rating_score.py`, the established convention in this suite. The fixture prices the
default context (driver age 34) to a payable premium of 1 507 minor units.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from test_rating_score import _compiled, _ctx

from model_schema.refs import ArtifactRef
from model_schema.regression import GoldenQuote
from pricing_core.rating.runtime import CompiledBundle
from pricing_core.rating.testing import evaluate_golden_quotes

_REF = ArtifactRef.model_validate("rating_version:motor-gb@27")
_KNOWN_PREMIUM = 1_507


def _golden(
    name: str,
    *,
    premium: int | None = _KNOWN_PREMIUM,
    outcome: str = "quoted",
    tolerance: int = 0,
    inputs: dict[str, Any] | None = None,
) -> GoldenQuote:
    ctx = _ctx(options=None) if inputs is None else _ctx(options=None, inputs=inputs)
    return GoldenQuote.model_validate(
        {
            "name": name,
            "context": ctx.model_dump(mode="json"),
            "expected": {"payable_premium_minor": premium, "outcome": outcome},
            "tolerance": {"money_minor": tolerance},
        }
    )


@pytest.fixture(scope="module")
def bundle() -> CompiledBundle:
    return asyncio.run(_compiled())


@pytest.mark.req("FR-260")
def test_an_exact_match_passes(bundle: CompiledBundle) -> None:
    (result,) = evaluate_golden_quotes(bundle, [_golden("exact")], rating_version_ref=_REF)
    assert result.status == "pass"
    assert (result.expected_minor, result.actual_minor, result.difference_minor) == (
        _KNOWN_PREMIUM, _KNOWN_PREMIUM, 0,
    )


@pytest.mark.req("FR-260")
@pytest.mark.req("FR-273")
def test_one_minor_unit_over_a_zero_tolerance_fails(bundle: CompiledBundle) -> None:
    (result,) = evaluate_golden_quotes(
        bundle, [_golden("one-under", premium=_KNOWN_PREMIUM - 1)], rating_version_ref=_REF
    )
    assert result.status == "fail"
    assert result.difference_minor == 1
    assert isinstance(result.difference_minor, int)


@pytest.mark.req("FR-260")
def test_a_difference_inside_the_declared_tolerance_passes(bundle: CompiledBundle) -> None:
    results = evaluate_golden_quotes(
        bundle,
        [
            _golden("inside", premium=_KNOWN_PREMIUM - 3, tolerance=3),
            _golden("outside", premium=_KNOWN_PREMIUM - 4, tolerance=3),
        ],
        rating_version_ref=_REF,
    )
    assert [(r.name, r.status, r.difference_minor) for r in results] == [
        ("inside", "pass", 3), ("outside", "fail", 4),
    ]


@pytest.mark.req("FR-260")
def test_an_outcome_mismatch_fails(bundle: CompiledBundle) -> None:
    """`quoted` expected, `declined` actual: both sanity constraints fire."""
    declining = {
        "driver_age": 34, "channel": "direct", "min_premium_minor": 0,
        "sanity_cap_minor": 1, "sanity_floor_minor": 999_999_999,
    }
    results = evaluate_golden_quotes(
        bundle,
        [
            _golden("expected-quote", inputs=declining),
            _golden("expected-decline", premium=None, outcome="declined", inputs=declining),
        ],
        rating_version_ref=_REF,
    )
    assert [(r.name, r.status) for r in results] == [
        ("expected-quote", "fail"), ("expected-decline", "pass"),
    ]
    assert results[0].actual_minor is None
    assert results[0].difference_minor is None


@pytest.mark.req("FR-260")
def test_an_input_contract_violation_is_that_quotes_fail_not_an_abort(
    bundle: CompiledBundle,
) -> None:
    broken = {"channel": "direct", "min_premium_minor": 0,
              "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0}
    results = evaluate_golden_quotes(
        bundle,
        [_golden("broken", inputs=broken), _golden("fine")],
        rating_version_ref=_REF,
    )
    assert [(r.name, r.status, r.actual_minor) for r in results] == [
        ("broken", "fail", None), ("fine", "pass", _KNOWN_PREMIUM),
    ]


@pytest.mark.req("FR-260")
def test_it_is_a_plain_synchronous_function_with_no_event_loop(
    bundle: CompiledBundle,
) -> None:
    with pytest.raises(RuntimeError):
        asyncio.get_running_loop()
    results = evaluate_golden_quotes(bundle, [], rating_version_ref=_REF)
    assert results == []
    (result,) = evaluate_golden_quotes(bundle, [_golden("sync")], rating_version_ref=_REF)
    assert result.status == "pass"
