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
