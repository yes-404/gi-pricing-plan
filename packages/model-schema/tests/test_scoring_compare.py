"""Quote Sandbox compare shapes (FR-262, `03` §4.10; PL-1213 Task 2)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from model_schema.scoring import (
    ScoreCompareRequest,
    StepChange,
    TraceDiff,
)


def _request(**context: Any) -> dict[str, Any]:
    return {
        "context": {
            "purpose": "new_business",
            "quoted_at": datetime(2026, 1, 1, tzinfo=UTC).isoformat(),
            "effective_date": date(2026, 1, 2).isoformat(),
            **context,
        },
        "base": "rating_version:motor-gb@27",
        "comparison": "rating_version:motor-gb@28",
    }


def test_own_change_description_fixes_the_meaning_of_false() -> None:
    """The deputy's F5 condition: `false` is never worded as "unchanged"."""
    description = StepChange.model_fields["own_change"].description
    assert description is not None
    assert "no own change attributable from the traces" in description
    assert "unchanged" not in description.lower()


def test_a_context_naming_its_own_version_is_refused() -> None:
    body = _request(options={"rating_version_ref": "rating_version:motor-gb@1"})
    with pytest.raises(ValidationError, match="rating_version_ref must be omitted"):
        ScoreCompareRequest.model_validate(body)


def test_a_context_without_a_version_is_accepted() -> None:
    assert ScoreCompareRequest.model_validate(_request(options={"trace": True})).base


def test_an_unknown_key_is_refused() -> None:
    with pytest.raises(ValidationError):
        ScoreCompareRequest.model_validate({**_request(), "extra": 1})


def test_a_step_change_round_trips() -> None:
    change = StepChange(
        step_id="s_rate", change="changed", changed_fields=["produced"], own_change=True
    )
    diff = TraceDiff(steps=[change], unchanged=3)
    assert TraceDiff.model_validate_json(diff.model_dump_json()) == diff
