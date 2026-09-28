"""`PermutationImportance.shared_source_columns` (FR-177): additive, so an artifact written
before it existed still loads."""

from __future__ import annotations

import pytest

from model_schema import PermutationImportance


@pytest.mark.req("FR-177")
def test_a_permutation_importance_written_before_shared_columns_still_loads() -> None:
    old = PermutationImportance.model_validate(
        {"feature": "f", "baseline": 1.0, "permuted": 1.1, "degradation": 0.1,
         "repeats": 1, "seed": 0}
    )
    assert old.shared_source_columns == ()
