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


def _suite(properties: list[dict[str, Any]], *, cases: int = 30, seed: int = 5,
           golden: list[GoldenQuote] | None = None) -> RegressionSuite:
    content = {
        "algorithm_slug": "score-fixture",
        "golden_quotes": [g.model_dump(mode="json") for g in golden or []],
        "properties": properties,
        "generation": {"cases": cases, "seed": seed, "strategy": "input_contract_sampling"},
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
    return case_holds(prop.check, _CTX, scorer, contract, seed=0)


@pytest.mark.req("FR-261")
def test_property_premium_positive() -> None:
    assert _holds({"kind": "premium_positive"}, lambda c: _result(5))
    assert not _holds({"kind": "premium_positive"}, lambda c: _result(0))
    assert not _holds({"kind": "premium_positive"}, lambda c: None)  # an engine refusal


@pytest.mark.req("FR-261")
def test_property_no_null_output() -> None:
    assert _holds({"kind": "no_null_output"}, lambda c: _result(5, outputs={"a": 1}))
    assert not _holds({"kind": "no_null_output"}, lambda c: _result(5, outputs={"a": None}))
    # a null output is OMITTED from `outputs`: a declared output that is missing is a null one
    check = RegressionProperty.model_validate({"name": "prop", "check": {"kind": "no_null_output"}})
    scorer = lambda c: _result(5, outputs={"a": 1})  # noqa: E731
    assert case_holds(check.check, _CTX, scorer, (), seed=0, outputs=["a"])
    assert not case_holds(check.check, _CTX, scorer, (), seed=0, outputs=["a", "b"])


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
def test_property_monotone_naming_an_absent_input_is_refused_before_generation(
    bundle: CompiledBundle, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pricing_core.rating import testing

    def boom(*a: Any, **k: Any) -> Any:
        raise AssertionError("generation must not start")

    monkeypatch.setattr(testing, "generate_contexts", boom)
    suite = _suite([_prop("mono", kind="monotone", input="no_such_input", direction="increasing")])
    with pytest.raises(ValueError, match="no_such_input"):
        run_regression(bundle, suite, rating_version_ref=_REF, now=_now)


@pytest.mark.req("FR-261")
def test_run_regression_records_a_pass_and_the_generation(bundle: CompiledBundle) -> None:
    suite = _suite([
        _prop("bounded", kind="premium_bounded", lower_minor=0, upper_minor=10**9),
        _prop("up", kind="monotone", input="driver_age", direction="increasing"),
        _prop("positive", kind="premium_positive"),
        _prop("nonull", kind="no_null_output"),
        _prop("ladder", kind="ladder_reconciles"),
    ], golden=[_golden("known")])
    run, log = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
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
    run, log = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
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
    run, _ = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
    (tight,) = run.property_results
    assert tight.status == "fail"
    assert tight.shrink == "stopped_on_limit"
    assert tight.counterexample_minimal is False


@pytest.mark.req("FR-261")
def test_the_same_seed_reproduces_the_run_and_the_counterexample(
    bundle: CompiledBundle,
) -> None:
    suite = _suite([_prop("tight", kind="premium_bounded", upper_minor=1)], seed=9)
    one, log1 = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
    two, log2 = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
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
    run, log = run_regression(unclamped, suite, rating_version_ref=_REF, now=_now)
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
        rating_version_ref=_REF, now=_now,
    )
    assert fixed.overall == "pass"


@pytest.mark.req("FR-261")
def test_the_seed_is_the_suites_and_there_is_no_override(bundle: CompiledBundle) -> None:
    """RS-1176 condition 2: the persisted seed is `suite.generation.seed`; `run_regression`
    takes no seed of its own, so a run cannot be made under one seed and recorded as another."""
    import inspect

    assert "seed" not in inspect.signature(run_regression).parameters
    runs = {}
    for seed in (5, 77):
        suite = _suite([_prop("fine", kind="premium_positive")], seed=seed)
        runs[seed] = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
        assert runs[seed][0].generation.seed == suite.generation.seed == seed
    assert runs[5][1] != runs[77][1]
    assert runs[5][0].cases_blob != runs[77][0].cases_blob


@pytest.mark.req("FR-261")
def test_an_int_input_with_no_bounds_is_sampled_over_negatives_too() -> None:
    """Auditor-a's generator-range finding: a property that fails only for negative values
    is reachable when the contract declares no `min`."""
    from model_schema.rating import InputContractField
    from pricing_core.rating.testing import generate_contexts

    contract = [InputContractField.model_validate({"name": "x", "type": "int"})]
    values = [c.inputs["x"] for c in generate_contexts(contract, 60, 1)]
    assert any(v < 0 for v in values)  # type: ignore[operator]
    assert any(v > 0 for v in values)  # type: ignore[operator]
    assert all(-1_000_000 <= v <= 1_000_000 for v in values)  # type: ignore[operator]


@pytest.mark.req("FR-261")
def test_a_three_place_decimal_bound_is_quantised_inward() -> None:
    """The bound's min is rounded UP and its max DOWN to 2 places before the strategy is
    built, so a generated value never lies outside the declared bound."""
    from decimal import Decimal

    from model_schema.rating import InputContractField
    from pricing_core.rating.testing import generate_contexts

    contract = [InputContractField.model_validate(
        {"name": "x", "type": "decimal", "min": "0.005", "max": "0.995"})]
    values = [Decimal(c.inputs["x"]) for c in generate_contexts(contract, 40, 1)]  # type: ignore[arg-type]
    assert values
    assert all(Decimal("0.01") <= v <= Decimal("0.99") for v in values)


@pytest.mark.req("FR-261")
def test_a_decimal_input_with_no_two_place_value_between_its_bounds_is_refused() -> None:
    from model_schema.rating import InputContractField
    from pricing_core.rating.testing import generate_contexts

    contract = [InputContractField.model_validate(
        {"name": "x", "type": "decimal", "min": "0.004", "max": "0.006"})]
    with pytest.raises(ValueError, match="x"):
        generate_contexts(contract, 5, 1)


# --- DP-S3-5/6/7: the monotone grid is uniform + sampled, and never passes vacuously -----------

_BAND_RISK = "driver_age >= {lo} and driver_age < {hi} ? 1000 : 1500"


class _VariantResolver(_FakeResolver):
    """The unclamped fixture with the model replaced by an authored risk expression, so the
    premium's shape in `driver_age` is exactly what a test writes down; and, optionally, a
    constraint that declines every quote."""

    def __init__(
        self, *, risk_expr: str, decline_all: bool = False,
        drop_steps: frozenset[str] = frozenset(), optional_output: str | None = None,
    ) -> None:
        super().__init__()
        key = "rating_algorithm:score-fixture@1"
        payload = dict(self._payloads[key])
        steps = [s for s in payload["steps"] if s["step_id"] not in _UNCLAMPED | drop_steps]
        steps = [
            {"step_id": "s_risk", "type": "expression", "label": "Risk premium",
             "expr": risk_expr, "result_type": "money_minor",
             "consumes": ["driver_age"], "produces": "risk_premium_minor"}
            if s["step_id"] == "s_risk" else s
            for s in steps
        ]
        if decline_all:
            steps.append({
                "step_id": "s_decl_all", "type": "constraint", "label": "Decline everything",
                "condition": "office_premium_minor < 0", "on_violation": "decline",
                "reason_code": "ALWAYS", "consumes": ["office_premium_minor"],
            })
        payload["steps"] = steps
        if optional_output is not None:
            # an optional, nullable input echoed to an optional output: null in, null out
            payload["outputs"] = [
                *payload["outputs"], {"name": optional_output, "type": "money_minor",
                                      "required": False},
            ]
            payload["input_contract"] = [
                *payload["input_contract"], {"name": "promo", "type": "int", "nullable": True},
            ]
            payload["steps"] = [
                *payload["steps"],
                {"step_id": "s_in_promo", "type": "input", "label": "Promo",
                 "input_name": "promo", "on_missing": "null", "produces": "promo"},
                {"step_id": "s_out_promo", "type": "output", "label": "Promo out",
                 "output_name": optional_output, "rounding": {"mode": "half_even", "dp": 0},
                 "consumes": ["promo"]},
            ]
        payload["input_contract"] = [
            f for f in payload["input_contract"] if f["name"] not in _CLAMP_INPUTS
        ]
        self._payloads[key] = payload


def _variant(**kw: Any) -> CompiledBundle:
    return load_bundle(asyncio.run(compile_bundle(_version(), _VariantResolver(**kw))))


_UP = _prop("age-up", kind="monotone", input="driver_age", direction="increasing")


@pytest.mark.req("FR-261")
def test_the_monotone_grid_is_uniform_plus_seeded_samples_inside_the_bounds(
    bundle: CompiledBundle,
) -> None:
    from model_schema.regression import MonotoneInInput
    from pricing_core.rating.properties import monotone_grid

    field = next(f for f in bundle.algorithm.input_contract if f.name == "driver_age")
    check = MonotoneInInput.model_validate(
        {"kind": "monotone", "input": "driver_age", "direction": "increasing"})
    grid = monotone_grid(field, check, seed=5)
    assert grid == sorted(set(grid))
    assert {17, 99} <= set(grid)  # the bounds
    assert all(17 <= g <= 99 for g in grid)
    assert len(grid) > 5  # the uniform five plus sampled points
    assert monotone_grid(field, check, seed=5) == grid  # reproducible
    assert monotone_grid(field, check, seed=6) != grid  # the suite's seed decides the samples


@pytest.mark.req("FR-261")
def test_a_wide_inverted_band_is_caught_where_a_sorted_random_check_misses_it() -> None:
    """DP-S3-5 condition 3 (red first): the premium dips inside 40-79 and recovers, so it is
    NOT non-decreasing in age. The grid sweeps one base context across the bounds and sees
    the fall; the old reading (sort random contexts by the input and compare neighbours)
    is shown here on a sample of ages that happens not to land in the band, and passes."""
    from pricing_core.rating.testing import generate_contexts

    bundle = _variant(risk_expr=_BAND_RISK.format(lo=40, hi=80))
    run, _ = run_regression(bundle, _suite([_UP], seed=5), rating_version_ref=_REF, now=_now)
    (up,) = run.property_results
    assert up.status == "fail"
    assert up.grid == "uniform+sampled"
    assert up.counterexample_points is not None
    assert len(up.counterexample_points) == 2
    assert up.counterexample_points[0] < up.counterexample_points[1]

    # the old reading: random contexts sorted by age, neighbours compared, on a sample that
    # misses the band
    from pricing_core.rating.properties import make_scorer, payable_minor

    score = make_scorer(bundle, _REF, bundle.algorithm.input_contract)
    sample = [c for c in generate_contexts(bundle.algorithm.input_contract, 40, 5)
              if not 40 <= c.inputs["driver_age"] < 80][:6]  # type: ignore[operator]
    ordered = sorted(sample, key=lambda c: c.inputs["driver_age"])  # type: ignore[arg-type,return-value]
    premiums = []
    for c in ordered:
        scored = score(c)
        assert scored is not None
        premiums.append(payable_minor(scored))
    channel_free = [
        p for c, p in zip(ordered, premiums, strict=True) if c.inputs["channel"] == "direct"
    ]
    assert channel_free == sorted(channel_free)  # sorted-random sees nothing wrong


@pytest.mark.req("FR-261")
def test_known_limit_a_band_narrower_than_the_grid_spacing_may_not_be_detected() -> None:
    """DP-S3-6: with no Banding pinned in the bundle there are no band edges to put in the
    grid, so an inversion narrower than the spacing between grid and sampled points can pass.
    This test PINS that weakness (OQ-1217 is the way out: pin Bandings with an input-to-band
    link so `grid: banding-edges` becomes possible). It must be deleted, not weakened, when
    that lands. The sampled points depend on the suite's seed and the input's name only, so
    they are the SAME for every base context: the grid is one fixed ten-point set, and a band
    that falls between its points is missed for every base."""
    bundle = _variant(risk_expr=_BAND_RISK.format(lo=45, hi=47))
    run, _ = run_regression(bundle, _suite([_UP], seed=5), rating_version_ref=_REF, now=_now)
    (up,) = run.property_results
    assert up.status == "pass"
    assert up.grid == "uniform+sampled"


@pytest.mark.req("FR-261")
def test_a_monotone_that_compares_nothing_does_not_pass() -> None:
    """DP-S3-7: an algorithm that declines the whole declared range gives no comparable
    quoted pair in any sweep, so the property FAILS with a distinct code, never a vacuous
    pass."""
    bundle = _variant(risk_expr=_BAND_RISK.format(lo=0, hi=0), decline_all=True)
    run, log = run_regression(bundle, _suite([_UP], seed=5), rating_version_ref=_REF, now=_now)
    (up,) = run.property_results
    assert up.status == "fail"
    assert up.error_code == "MONOTONE_NO_COMPARABLE_PAIRS"
    assert up.counterexample is None
    assert run.overall == "fail"
    assert log.counterexamples == {}


@pytest.mark.req("FR-261")
def test_a_monotone_compares_quoted_neighbours_across_a_declined_gap(
    unclamped: CompiledBundle,
) -> None:
    """DP-S3-7 (b): declined grid points are skipped, and the quoted points either side are
    compared. A scorer that declines the middle of the grid but rises across it passes; one
    that falls across the gap fails."""
    def scorer(rising: bool) -> Any:
        def score(ctx: QuoteContext) -> ScoringResult:
            age = ctx.inputs["driver_age"]
            if 40 <= age <= 60:  # type: ignore[operator]
                return _result(None)
            return _result((100 + age) if rising else (300 - age))  # type: ignore[operator]
        return score

    contract = unclamped.algorithm.input_contract
    inc = {"kind": "monotone", "input": "driver_age", "direction": "increasing"}
    assert _holds(inc, scorer(True), contract)
    assert not _holds(inc, scorer(False), contract)


# --- acceptance item 8 THROUGH THE RUN: each of the other three classes fails on a real bundle

def _only_failure(bundle: CompiledBundle, prop: dict[str, Any]) -> Any:
    run, log = run_regression(bundle, _suite([prop]), rating_version_ref=_REF, now=_now)
    (result,) = run.property_results
    return run, result, log


@pytest.mark.req("FR-261")
def test_run_premium_positive_fails_on_a_bundle_that_prices_below_zero() -> None:
    prop = _prop("positive", kind="premium_positive")
    bad = _variant(risk_expr="driver_age - 60")  # negative risk premium for a young driver
    run, result, log = _only_failure(bad, prop)
    assert (result.status, run.overall) == ("fail", "fail")
    assert result.counterexample is not None
    assert log.counterexamples["positive"].inputs["driver_age"] < 60  # type: ignore[operator]
    assert _only_failure(_variant(risk_expr="driver_age + 60"), prop)[1].status == "pass"


@pytest.mark.req("FR-261")
def test_run_no_null_output_fails_on_a_declared_output_nothing_produces() -> None:
    prop = _prop("nonull", kind="no_null_output")
    bad = _variant(risk_expr="driver_age + 60", optional_output="extra_minor")
    run, result, _ = _only_failure(bad, prop)
    assert (result.status, run.overall) == ("fail", "fail")
    assert _only_failure(_variant(risk_expr="driver_age + 60"), prop)[1].status == "pass"


@pytest.mark.req("FR-261")
@pytest.mark.req("FR-248")
def test_run_ladder_reconciles_fails_when_the_ladder_has_no_risk_premium_rung() -> None:
    prop = _prop("ladder", kind="ladder_reconciles")
    bad = _variant(risk_expr="driver_age + 60", drop_steps=frozenset({"s_out_risk"}))
    run, result, _ = _only_failure(bad, prop)
    assert (result.status, run.overall) == ("fail", "fail")
    assert _only_failure(_variant(risk_expr="driver_age + 60"), prop)[1].status == "pass"


@pytest.mark.req("FR-261")
def test_property_monotone_with_an_empty_range_is_refused_by_name_before_generation(
    bundle: CompiledBundle, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A lone `lower` above the contract's max leaves nothing to sweep: refused by input name
    before generation, never a raw `randint` error inside the Job."""
    from pricing_core.rating import testing

    def boom(*a: Any, **k: Any) -> Any:
        raise AssertionError("generation must not start")

    monkeypatch.setattr(testing, "generate_contexts", boom)
    suite = _suite([_prop("mono-range", kind="monotone", input="driver_age",
                          direction="increasing", lower="200")])
    with pytest.raises(ValueError, match=r"driver_age.*empty"):
        run_regression(bundle, suite, rating_version_ref=_REF, now=_now)


@pytest.mark.req("FR-261")
@pytest.mark.parametrize(("field_kw", "check_kw"), [
    ({"type": "int", "min": 17, "max": 99}, {"upper": "10"}),          # lone upper below min
    ({"type": "decimal", "min": "0.004", "max": "0.006"}, {}),          # no 2-place value
    ({"type": "decimal", "min": 0, "max": 5}, {"lower": "5.004", "upper": "5.006"}),
])
def test_monotone_field_refuses_an_empty_or_unquantisable_range(
    field_kw: dict[str, Any], check_kw: dict[str, Any]
) -> None:
    from model_schema.rating import InputContractField
    from model_schema.regression import MonotoneInInput
    from pricing_core.rating.properties import monotone_field

    field = InputContractField.model_validate({"name": "x", **field_kw})
    check = MonotoneInInput.model_validate(
        {"kind": "monotone", "input": "x", "direction": "increasing", **check_kw})
    with pytest.raises(ValueError, match=r"x.*(empty|two-place)"):
        monotone_field([field], check)


@pytest.mark.req("FR-261")
@pytest.mark.parametrize(("check_kw", "first", "last"), [
    ({"lower": "50"}, 50, 99),   # a lone lower: the upper is the contract's max
    ({"upper": "60"}, 17, 60),   # a lone upper: the lower is the contract's min
])
def test_a_lone_monotone_bound_sweeps_the_range_intersected_with_the_contract(
    bundle: CompiledBundle, check_kw: dict[str, str], first: int, last: int
) -> None:
    """The contract's `driver_age` is 17..99. A lone bound is a VALID declaration: the grid's
    first and last points are the expected ends, and a run over it passes."""
    from model_schema.regression import MonotoneInInput
    from pricing_core.rating.properties import monotone_field, monotone_grid

    contract = bundle.algorithm.input_contract
    check = MonotoneInInput.model_validate(
        {"kind": "monotone", "input": "driver_age", "direction": "increasing", **check_kw})
    field = monotone_field(contract, check)  # accepted, not refused
    grid = monotone_grid(field, check, seed=5)
    assert (grid[0], grid[-1]) == (first, last)
    assert all(first <= g <= last for g in grid)
    suite = _suite([_prop("lone-bound", kind="monotone", input="driver_age",
                          direction="increasing", **check_kw)], seed=5)
    run, _ = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
    assert run.property_results[0].status in {"pass", "fail"}  # ran; not refused
