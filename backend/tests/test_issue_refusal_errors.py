"""A compile-level refusal names the step in `errors[]`, never in the stored or logged text
(#1712 S7c; NFR-499, FR-1607). No database: `raise_first_issue` is a pure function of the issues.
"""

from __future__ import annotations

import pytest

from app.errors import PlatformError
from app.platform.rating_algorithms import raise_first_issue
from model_schema.rating import ValidationIssue

SENT = "sentinels7c91"


def test_the_first_issue_refusal_names_the_step_in_errors_and_not_in_detail() -> None:
    """The step id is the caller's own artifact: returned in the 422's `errors[]`, in no text."""
    issue = ValidationIssue(
        code="LADDER_CLAMP_UNPLACEABLE",
        message="a clamp step cannot be placed on the premium ladder (FR-240, FR-247)",
        step_id=f"s_clamp_{SENT}",
        field="produces",
    )
    with pytest.raises(PlatformError) as caught:
        raise_first_issue([issue, issue.model_copy(update={"step_id": "s_other"})])
    error = caught.value
    assert (error.code, error.status_code) == ("LADDER_CLAMP_UNPLACEABLE", 422)
    assert [(e.field, e.code) for e in error.errors] == [
        (f"steps.s_clamp_{SENT}.produces", "LADDER_CLAMP_UNPLACEABLE")
    ]
    for text in (error.detail, error.title, str(error), *(e.message for e in error.errors)):
        assert text is not None
        assert SENT not in text
    assert error.to_problem().errors == error.errors


def test_an_issue_with_no_step_is_located_by_its_field_alone() -> None:
    issue = ValidationIssue(
        code="EXPRESSION_SCALE_OVERFLOW",
        message="an input min needs more than 28 places",
        field="input_contract.min",
    )
    with pytest.raises(PlatformError) as caught:
        raise_first_issue([issue])
    assert [e.field for e in caught.value.errors] == ["input_contract.min"]


def test_an_empty_issue_list_does_not_refuse() -> None:
    raise_first_issue([])


def test_a_real_validation_refusal_has_a_literal_detail_and_the_step_only_in_errors() -> None:
    """Through `validate_algorithm`: the sentinel is in the step id and the expression text."""
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.compile import validate_algorithm

    data = {
        "slug": "motor-gb", "version": 1,
        "input_contract": [{"name": "driver_age", "type": "int", "nullable": False}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "age", "input_name": "driver_age",
             "on_missing": "error", "produces": "driver_age"},
            {"step_id": f"s_calc_{SENT}", "type": "expression", "label": "c",
             "expr": f"fn_{SENT}(driver_age) / 2", "result_type": "money_minor",
             "consumes": ["driver_age"], "produces": "premium"},
            {"step_id": "s_out", "type": "output", "label": "o",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["premium"]},
        ],
    }
    issues = validate_algorithm(RatingAlgorithm.model_validate(data))
    assert issues, "the plant must fire"
    with pytest.raises(PlatformError) as caught:
        raise_first_issue(issues)
    problem = caught.value.to_problem()
    assert SENT not in (problem.detail or "")
    assert SENT not in problem.title
    assert all(SENT not in e.message for e in problem.errors)
    assert [SENT in e.field for e in problem.errors] == [True]
