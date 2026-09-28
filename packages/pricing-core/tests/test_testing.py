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


# --- WK-672 Slice 3 (PL-1205 Task 4): the five property classes and run_regression -----------

from datetime import UTC, datetime  # noqa: E402
from uuid import uuid4  # noqa: E402

from model_schema.regression import (  # noqa: E402
    RegressionProperty,
    RegressionSuite,
    suite_content_hash,
)
from model_schema.scoring import LadderRung, QuoteContext, ScoringResult  # noqa: E402
from pricing_core.rating.properties import case_holds  # noqa: E402
from pricing_core.rating.testing import run_regression  # noqa: E402

_CLOCK_TICKS = iter(range(10**6))


def _now() -> datetime:
    return datetime(2026, 9, 28, 9, 0, next(_CLOCK_TICKS) % 60, tzinfo=UTC)


def _suite(properties: list[dict[str, Any]], *, cases: int = 30,
           golden: list[GoldenQuote] | None = None) -> RegressionSuite:
    content = {
        "algorithm_slug": "score-fixture",
        "golden_quotes": [g.model_dump(mode="json") for g in golden or []],
        "properties": properties,
        "generation": {"cases": cases, "seed": 5, "strategy": "input_contract_sampling"},
    }
    from model_schema.regression import RegressionSuiteContent

    digest = suite_content_hash(RegressionSuiteContent.model_validate(content))
    return RegressionSuite.model_validate({
        **content, "slug": "score-suite", "version": 2, "change_note": "test",
        "content_hash": digest, "created_at": "2026-09-28T09:00:00Z",
        "created_by": str(uuid4()),
    })


def _prop(name: str, **check: Any) -> dict[str, Any]:
    return {"name": name, "check": check}


def _result(premium: int | None, *, outputs: dict[str, object] | None = None,
            rungs: list[tuple[str, int]] | None = None) -> ScoringResult:
    ladder = rungs if rungs is not None else (
        [("risk_premium", 1000), ("payable_premium", premium)] if premium is not None else []
    )
    return ScoringResult(
        outcome="quoted" if premium is not None else "declined",
        rating_version_ref=_REF, bundle_hash="sha256:" + "0" * 64,
        premium_ladder=[LadderRung(rung=r, value_minor=v) for r, v in ladder],  # type: ignore[arg-type]
        outputs=outputs or {},
    )


_CTX = QuoteContext.model_validate({
    "purpose": "new_business", "quoted_at": "2026-01-01T12:00:00",
    "effective_date": "2026-01-01", "inputs": {"driver_age": 30},
})


def _holds(check: dict[str, Any], scorer: Any, contract: Any = ()) -> bool:
    prop = RegressionProperty.model_validate({"name": "prop", "check": check})
    return case_holds(prop.check, _CTX, scorer, contract)


@pytest.mark.req("FR-261")
def test_property_premium_positive() -> None:
    assert _holds({"kind": "premium_positive"}, lambda c: _result(5))
    assert not _holds({"kind": "premium_positive"}, lambda c: _result(0))
    assert not _holds({"kind": "premium_positive"}, lambda c: None)  # an engine refusal


@pytest.mark.req("FR-261")
def test_property_no_null_output() -> None:
    assert _holds({"kind": "no_null_output"}, lambda c: _result(5, outputs={"a": 1}))
    assert not _holds({"kind": "no_null_output"}, lambda c: _result(5, outputs={"a": None}))


@pytest.mark.req("FR-261")
@pytest.mark.req("FR-248")
def test_property_ladder_reconciles() -> None:
    assert _holds({"kind": "ladder_reconciles"}, lambda c: _result(5))
    off_ladder = [("office_premium", 999), ("risk_premium", 1000), ("payable_premium", 5)]
    assert not _holds({"kind": "ladder_reconciles"}, lambda c: _result(5, rungs=off_ladder))


@pytest.mark.req("FR-261")
def test_property_premium_bounded() -> None:
    check = {"kind": "premium_bounded", "lower_minor": 10, "upper_minor": 20}
    assert _holds(check, lambda c: _result(15))
    assert not _holds(check, lambda c: _result(21))
    assert not _holds(check, lambda c: _result(9))
    assert _holds(check, lambda c: _result(None))  # a decline has no premium to bound


@pytest.mark.req("FR-261")
def test_property_monotone_passes_and_fails_along_the_grid(bundle: CompiledBundle) -> None:
    contract = bundle.algorithm.input_contract
    inc = {"kind": "monotone", "input": "driver_age", "direction": "increasing"}
    scorer = _by_age(lambda age: 100 + age)
    assert _holds(inc, scorer, contract)
    assert not _holds({**inc, "direction": "decreasing"}, scorer, contract)
    assert not _holds({**inc, "strict": True}, _by_age(lambda age: 100), contract)
    assert not _holds(inc, _by_age(lambda age: 200 - age), contract)


def _by_age(fn: Any) -> Any:
    return lambda ctx: _result(fn(ctx.inputs["driver_age"]))


@pytest.mark.req("FR-261")
def test_a_monotone_naming_an_absent_input_is_refused_before_generation(
    bundle: CompiledBundle, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pricing_core.rating import testing

    def boom(*a: Any, **k: Any) -> Any:
        raise AssertionError("generation must not start")

    monkeypatch.setattr(testing, "generate_contexts", boom)
    suite = _suite([_prop("mono", kind="monotone", input="no_such_input", direction="increasing")])
    with pytest.raises(ValueError, match="no_such_input"):
        run_regression(bundle, suite, seed=1, rating_version_ref=_REF, now=_now)


@pytest.mark.req("FR-261")
def test_run_regression_records_a_pass_and_the_generation(bundle: CompiledBundle) -> None:
    suite = _suite([
        _prop("bounded", kind="premium_bounded", lower_minor=0, upper_minor=10**9),
        _prop("up", kind="monotone", input="driver_age", direction="increasing"),
        _prop("positive", kind="premium_positive"),
        _prop("nonull", kind="no_null_output"),
        _prop("ladder", kind="ladder_reconciles"),
    ], golden=[_golden("known")])
    run, log = run_regression(bundle, suite, seed=5, rating_version_ref=_REF, now=_now)
    assert run.overall == "pass", run.property_results
    assert [p.status for p in run.property_results] == ["pass"] * 5
    assert run.golden_results[0].status == "pass"
    assert run.bundle_hash == bundle.content_hash
    assert (run.generation.seed, run.generation.cases) == (5, 30)
    assert run.suite_ref.slug == "score-suite"
    assert run.suite_content_hash == suite.content_hash
    assert len(log.cases) == 30
    assert log.counterexamples == {}
    from model_schema.regression import cases_log_bytes, cases_log_sha256

    assert run.cases_blob.sha256 == cases_log_sha256(log)
    assert run.cases_blob.bytes_ == len(cases_log_bytes(log))


@pytest.mark.req("FR-261")
def test_a_failing_property_is_shrunk_and_recorded(bundle: CompiledBundle) -> None:
    suite = _suite([
        _prop("tight", kind="premium_bounded", upper_minor=1),
        _prop("fine", kind="premium_positive"),
    ])
    run, log = run_regression(bundle, suite, seed=5, rating_version_ref=_REF, now=_now)
    assert run.overall == "fail"
    tight, fine = run.property_results
    assert (tight.status, fine.status) == ("fail", "pass")
    assert tight.error_code == "PROPERTY_ASSERTION_FAILED"
    assert tight.shrink == "completed"
    assert tight.counterexample_minimal is True
    assert set(log.counterexamples) == {"tight"}
    assert tight.counterexample == log.counterexamples["tight"].inputs


@pytest.mark.req("FR-261")
def test_a_shrink_stopped_on_a_limit_is_reported_unminimised(
    bundle: CompiledBundle, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RS-1176 condition 5, forced: with `MAX_SHRINKS` at 1 hypothesis stops shrinking."""
    import hypothesis.internal.conjecture.engine as engine

    monkeypatch.setattr(engine, "MAX_SHRINKS", 1)
    suite = _suite([_prop("tight", kind="premium_bounded", upper_minor=1)])
    run, _ = run_regression(bundle, suite, seed=5, rating_version_ref=_REF, now=_now)
    (tight,) = run.property_results
    assert tight.status == "fail"
    assert tight.shrink == "stopped_on_limit"
    assert tight.counterexample_minimal is False


@pytest.mark.req("FR-261")
def test_the_same_seed_reproduces_the_run_and_the_counterexample(
    bundle: CompiledBundle,
) -> None:
    suite = _suite([_prop("tight", kind="premium_bounded", upper_minor=1)])
    one, log1 = run_regression(bundle, suite, seed=9, rating_version_ref=_REF, now=_now)
    two, log2 = run_regression(bundle, suite, seed=9, rating_version_ref=_REF, now=_now)
    assert log1 == log2
    assert one.property_results == two.property_results
    assert one.cases_blob == two.cases_blob


# --- a purpose-built minimal bundle: premium depends on driver_age only, nothing clamps it ----

from test_rating_score import _FakeResolver, _version  # noqa: E402

from pricing_core.rating.compile import compile_bundle  # noqa: E402
from pricing_core.rating.runtime import load_bundle  # noqa: E402

_UNCLAMPED = {"s_clamp", "s_decl_cap", "s_decl_floor"}
_CLAMP_INPUTS = {"min_premium_minor", "sanity_cap_minor", "sanity_floor_minor"}


class _UnclampedResolver(_FakeResolver):
    """`test_rating_score`'s fixture without its clamp and decline constraints, so the payable
    premium is a function of `driver_age` (and `channel`'s expense factor) alone: 1 507 up to
    age 30-ish, 1 958 from 58 on — non-decreasing in age, never clamped by a random input."""

    def __init__(self) -> None:
        super().__init__()
        key = "rating_algorithm:score-fixture@1"
        payload = dict(self._payloads[key])
        payload["steps"] = [s for s in payload["steps"] if s["step_id"] not in _UNCLAMPED]
        payload["input_contract"] = [
            f for f in payload["input_contract"] if f["name"] not in _CLAMP_INPUTS
        ]
        self._payloads[key] = payload


@pytest.fixture(scope="module")
def unclamped() -> CompiledBundle:
    return load_bundle(asyncio.run(compile_bundle(_version(), _UnclampedResolver())))


@pytest.mark.req("FR-261")
def test_run_regression_finds_a_monotone_failure_and_passes_the_fixed_variant(
    unclamped: CompiledBundle,
) -> None:
    suite = _suite([
        _prop("age-down", kind="monotone", input="driver_age", direction="decreasing"),
        _prop("age-up", kind="monotone", input="driver_age", direction="increasing"),
        _prop("age-strict", kind="monotone", input="driver_age", direction="increasing",
              strict=True),
    ])
    run, log = run_regression(unclamped, suite, seed=5, rating_version_ref=_REF, now=_now)
    down, up, strict = run.property_results
    assert (down.status, up.status, strict.status) == ("fail", "pass", "fail")
    assert down.shrink == "completed"
    assert down.counterexample_minimal is True
    assert set(log.counterexamples) == {"age-down", "age-strict"}
    assert run.overall == "fail"
    # the fixed variant: the increasing direction alone is a passing run
    fixed, _ = run_regression(
        unclamped, _suite([_prop("age-up", kind="monotone", input="driver_age",
                                 direction="increasing")]),
        seed=5, rating_version_ref=_REF, now=_now,
    )
    assert fixed.overall == "pass"
