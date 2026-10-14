"""`PartitionDiagnostics.rows_excluded_zero_weight` (`02` FR-111, FR-171; SL-1675).

The count is optional on purpose. A `Diagnostics` or `Backtest` stored before 2026-10-12 has
no such key and is immutable (ADR-705), so reading it back must still validate; `None` then
means "the artifact predates the rule", and `0` means "the rule ran and removed nothing".
Those are different statements and the type keeps them apart.
"""

from __future__ import annotations

import pydantic
import pytest

from model_schema import PartitionDiagnostics, Weighting

# A partition exactly as an artifact written before the field existed holds it.
STORED_BEFORE = {
    "weighting": "exposure",
    "rows": 1_000,
    "ae_overall": 1.01,
    "gini": 0.3,
    "gini_normalised": 0.4,
}


@pytest.mark.req("FR-171")
def test_a_stored_partition_written_before_the_count_still_validates() -> None:
    partition = PartitionDiagnostics.model_validate(STORED_BEFORE)

    assert partition.weighting is Weighting.EXPOSURE
    assert partition.rows_excluded_zero_weight is None


@pytest.mark.req("FR-171")
def test_zero_and_absent_are_different_statements() -> None:
    ran_and_removed_nothing = PartitionDiagnostics.model_validate(
        {**STORED_BEFORE, "rows_excluded_zero_weight": 0}
    )
    assert ran_and_removed_nothing.rows_excluded_zero_weight == 0
    assert ran_and_removed_nothing != PartitionDiagnostics.model_validate(STORED_BEFORE)


@pytest.mark.req("FR-171")
def test_a_negative_count_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError):
        PartitionDiagnostics.model_validate({**STORED_BEFORE, "rows_excluded_zero_weight": -1})
