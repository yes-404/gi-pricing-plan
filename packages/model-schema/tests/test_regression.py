"""Regression Suite and Golden Quote shapes (03 §4.7, FR-260, FR-261; PL-1189 Task 2).

The five FR-261 property classes are stored as a structured union discriminated on
`kind` — never a free-text assertion — and the suite's content hash is the pin a Rating
Version's evidence carries (FR-260, amended 2026-09-28).
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from model_schema.rating import RatingVersionEvidence
from model_schema.refs import ArtifactRef
from model_schema.regression import (
    GoldenQuote,
    GoldenQuoteChange,
    GoldenQuoteCheck,
    GoldenQuoteExpected,
    GoldenQuoteNotChecked,
    RegressionProperty,
    RegressionSuite,
    RegressionSuiteContent,
    context_hash,
    suite_content_hash,
)

_CONTEXT: dict[str, Any] = {
    "purpose": "new_business",
    "quoted_at": "2026-09-28T09:00:00Z",
    "effective_date": "2026-10-01",
    "inputs": {"driver_age": 19, "postcode": "E1 6AN"},
}

_FIVE_KINDS: list[dict[str, Any]] = [
    {"kind": "premium_positive"},
    {"kind": "monotone", "input": "driver_age", "direction": "decreasing",
     "strict": False, "lower": "25", "upper": "70"},
    {"kind": "no_null_output"},
    {"kind": "ladder_reconciles"},
    {"kind": "premium_bounded", "lower_minor": 28000, "upper_minor": 2500000},
]


def _golden(name: str = "young-driver-london", premium: int = 112480,
            tolerance: int = 0) -> dict[str, Any]:
    return {
        "name": name,
        "context": _CONTEXT,
        "expected": {"payable_premium_minor": premium, "outcome": "quoted"},
        "tolerance": {"money_minor": tolerance},
    }


def _content(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "algorithm_slug": "motor-gb",
        "golden_quotes": [_golden()],
        "properties": [
            {"name": f"prop-{i}", "check": check} for i, check in enumerate(_FIVE_KINDS)
        ],
        "generation": {"cases": 5000, "seed": 20260814, "strategy": "input_contract_sampling"},
    }
    body.update(overrides)
    return body


@pytest.mark.req("FR-261")
@pytest.mark.parametrize("check", _FIVE_KINDS, ids=[c["kind"] for c in _FIVE_KINDS])
def test_each_of_the_five_property_kinds_round_trips(check: dict[str, Any]) -> None:
    prop = RegressionProperty.model_validate({"name": "a-property", "check": check})
    dumped = prop.model_dump(mode="json")
    assert dumped["check"]["kind"] == check["kind"]
    assert RegressionProperty.model_validate(dumped) == prop


@pytest.mark.req("FR-261")
def test_a_free_text_assertion_is_refused() -> None:
    with pytest.raises(ValidationError):
        RegressionProperty.model_validate(
            {"name": "premium-positive", "assertion": "payable_premium_minor > 0"}
        )
    with pytest.raises(ValidationError):
        RegressionProperty.model_validate(
            {"name": "premium-positive",
             "check": {"kind": "premium_positive", "assertion": "payable_premium_minor > 0"}}
        )


@pytest.mark.req("FR-261")
def test_an_unknown_kind_is_refused() -> None:
    with pytest.raises(ValidationError):
        RegressionProperty.model_validate({"name": "custom", "check": {"kind": "custom"}})


@pytest.mark.req("FR-261")
def test_premium_bounded_with_neither_bound_is_refused() -> None:
    with pytest.raises(ValidationError):
        RegressionProperty.model_validate(
            {"name": "bounded", "check": {"kind": "premium_bounded"}}
        )


@pytest.mark.req("FR-261")
def test_premium_bounded_with_crossed_bounds_is_refused() -> None:
    with pytest.raises(ValidationError):
        RegressionProperty.model_validate(
            {"name": "bounded",
             "check": {"kind": "premium_bounded", "lower_minor": 10, "upper_minor": 5}}
        )


@pytest.mark.req("FR-261")
def test_monotone_with_crossed_bounds_is_refused() -> None:
    with pytest.raises(ValidationError):
        RegressionProperty.model_validate(
            {"name": "mono",
             "check": {"kind": "monotone", "input": "driver_age", "direction": "increasing",
                       "lower": "70", "upper": "25"}}
        )


@pytest.mark.req("FR-260")
def test_duplicate_golden_quote_names_are_refused() -> None:
    with pytest.raises(ValidationError):
        RegressionSuiteContent.model_validate(
            _content(golden_quotes=[_golden(), _golden(premium=1)])
        )


@pytest.mark.req("FR-261")
def test_duplicate_property_names_are_refused() -> None:
    with pytest.raises(ValidationError):
        RegressionSuiteContent.model_validate(
            _content(properties=[
                {"name": "pp", "check": {"kind": "premium_positive"}},
                {"name": "pp", "check": {"kind": "no_null_output"}},
            ])
        )


@pytest.mark.req("FR-260")
def test_expected_premium_is_null_exactly_when_the_outcome_is_not_quoted() -> None:
    GoldenQuoteExpected.model_validate({"payable_premium_minor": None, "outcome": "declined"})
    with pytest.raises(ValidationError):
        GoldenQuoteExpected.model_validate({"payable_premium_minor": None, "outcome": "quoted"})
    with pytest.raises(ValidationError):
        GoldenQuoteExpected.model_validate({"payable_premium_minor": 100, "outcome": "declined"})


@pytest.mark.req("FR-260")
def test_money_and_tolerance_refuse_a_float() -> None:
    with pytest.raises(ValidationError):
        GoldenQuote.model_validate(_golden() | {"expected": {"payable_premium_minor": 112480.0,
                                                             "outcome": "quoted"}})
    with pytest.raises(ValidationError):
        GoldenQuote.model_validate(_golden() | {"tolerance": {"money_minor": 1.0}})
    with pytest.raises(ValidationError):
        GoldenQuote.model_validate(_golden(tolerance=-1))


@pytest.mark.req("FR-260")
def test_suite_content_hash_is_stable_under_key_order() -> None:
    content = RegressionSuiteContent.model_validate(_content())
    reordered = RegressionSuiteContent.model_validate(dict(reversed(list(_content().items()))))
    assert suite_content_hash(content) == suite_content_hash(reordered)
    assert suite_content_hash(content).startswith("sha256:")
    assert len(suite_content_hash(content)) == len("sha256:") + 64


@pytest.mark.req("FR-260")
def test_suite_content_hash_changes_on_an_expected_or_tolerance_edit() -> None:
    base = suite_content_hash(RegressionSuiteContent.model_validate(_content()))
    expected_edit = suite_content_hash(
        RegressionSuiteContent.model_validate(_content(golden_quotes=[_golden(premium=112481)]))
    )
    tolerance_edit = suite_content_hash(
        RegressionSuiteContent.model_validate(_content(golden_quotes=[_golden(tolerance=5)]))
    )
    assert len({base, expected_edit, tolerance_edit}) == 3


@pytest.mark.req("FR-260")
def test_context_hash_is_independent_of_key_order_and_sensitive_to_inputs() -> None:
    a = GoldenQuote.model_validate(_golden()).context
    b = GoldenQuote.model_validate(
        _golden() | {"context": dict(reversed(list(_CONTEXT.items())))}
    ).context
    c = GoldenQuote.model_validate(
        _golden() | {"context": _CONTEXT | {"inputs": {"driver_age": 20, "postcode": "E1 6AN"}}}
    ).context
    assert context_hash(a) == context_hash(b)
    assert context_hash(a) != context_hash(c)


@pytest.mark.req("FR-260")
def test_a_suite_version_carries_its_content_and_metadata() -> None:
    content = RegressionSuiteContent.model_validate(_content())
    suite = RegressionSuite.model_validate(
        _content() | {
            "slug": "motor-gb-core",
            "version": 1,
            "change_note": "first golden quotes",
            "content_hash": suite_content_hash(content),
            "created_at": "2026-09-28T09:00:00Z",
            "created_by": "0190c5d2-6a8e-7cc1-8f3e-7a1b2c3d4e5f",
        }
    )
    assert suite.content() == content
    with pytest.raises(ValidationError):
        RegressionSuite.model_validate(suite.model_dump(mode="json") | {"content_hash": "md5:x"})


@pytest.mark.req("FR-260")
def test_a_regression_suite_ref_is_an_artifact_ref() -> None:
    ref = ArtifactRef.model_validate("regression_suite:motor-gb-core@4")
    assert (ref.type, ref.slug, ref.version) == ("regression_suite", "motor-gb-core", 4)


@pytest.mark.req("FR-260")
def test_a_change_lists_changed_fields_exactly_when_it_is_changed() -> None:
    step = {"version": 2, "changed_fields": ["expected"],
            "author": "0190c5d2-6a8e-7cc1-8f3e-7a1b2c3d4e5f"}
    GoldenQuoteChange.model_validate(
        {"name": "q", "change": "changed", "changed_fields": ["expected"], "steps": [step]}
    )
    with pytest.raises(ValidationError):
        GoldenQuoteChange.model_validate(
            {"name": "q", "change": "changed", "changed_fields": [], "steps": [step]}
        )
    with pytest.raises(ValidationError):
        GoldenQuoteChange.model_validate(
            {"name": "q", "change": "added", "changed_fields": ["expected"],
             "steps": [step | {"changed_fields": ["added"]}]}
        )
    with pytest.raises(ValidationError):
        GoldenQuoteChange.model_validate(
            {"name": "q", "change": "added", "changed_fields": [], "steps": []}
        )


@pytest.mark.req("FR-260")
def test_the_evidence_is_either_checked_or_explicitly_not_checked() -> None:
    not_checked = {"status": "not_checked", "regression_suite": "none",
                   "message": "no golden quotes were checked",
                   "reason": "no_suite_for_algorithm"}
    evidence = RatingVersionEvidence.model_validate({"golden_quotes": not_checked})
    assert isinstance(evidence.golden_quotes, GoldenQuoteNotChecked)
    checked = {
        "status": "checked",
        "suite_ref": "regression_suite:motor-gb-core@4",
        "suite_content_hash": "sha256:" + "a" * 64,
        "bundle_hash": "sha256:" + "b" * 64,
        "results": [{"name": "q", "status": "pass", "expected_minor": 1,
                     "actual_minor": 1, "difference_minor": 0}],
        "delta": {"baseline_rating_version_ref": None, "baseline_suite_ref": None,
                  "baseline_suite_content_hash": None, "changes": []},
    }
    evidence = RatingVersionEvidence.model_validate({"golden_quotes": checked})
    assert isinstance(evidence.golden_quotes, GoldenQuoteCheck)
    assert RatingVersionEvidence.model_validate(evidence.model_dump(mode="json")) == evidence
    assert RatingVersionEvidence().golden_quotes is None
    with pytest.raises(ValidationError):
        RatingVersionEvidence.model_validate(
            {"golden_quotes": not_checked | {"message": "0 mismatches"}}
        )
