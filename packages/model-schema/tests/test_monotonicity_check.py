"""`MonotonicityCheck` after FR-177: exactly one of `holds` and `skipped`, and every
check written before `skipped` existed still loads.

No `req` marker beyond FR-177 itself: this is the schema half of a decision (DP-FR177-S1).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema import MonotonicityCheck, MonotonicitySkip, PermutationImportance


@pytest.mark.req("FR-177")
def test_a_check_written_before_skipped_existed_still_loads() -> None:
    old = MonotonicityCheck.model_validate(
        {"factor": "vehicle_age", "declared": "decreasing", "holds": True}
    )
    assert old.holds is True
    assert old.skipped is None


@pytest.mark.req("FR-177")
def test_a_skipped_check_carries_no_verdict() -> None:
    check = MonotonicityCheck(
        factor="area_x_fuel", declared="increasing", holds=None,
        skipped=MonotonicitySkip.UNORDERED_LEVELS,
    )
    assert check.holds is None


@pytest.mark.req("FR-177")
@pytest.mark.parametrize(
    "fields",
    [
        {"holds": True, "skipped": "unordered_levels"},
        {"holds": None},
        {"holds": None, "skipped": None},
    ],
)
def test_a_check_with_both_or_neither_of_holds_and_skipped_is_refused(
    fields: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        MonotonicityCheck.model_validate({"factor": "f", "declared": "increasing", **fields})


@pytest.mark.req("FR-177")
def test_a_permutation_importance_written_before_shared_columns_still_loads() -> None:
    old = PermutationImportance.model_validate(
        {"feature": "f", "baseline": 1.0, "permuted": 1.1, "degradation": 0.1,
         "repeats": 1, "seed": 0}
    )
    assert old.shared_source_columns == ()
