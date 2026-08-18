"""Profile shapes (`01` §4.7, FR-DATA-48)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema import ColumnProfile, Histogram, SemanticType


@pytest.mark.req("FR-DATA-48")
def test_a_histogram_has_one_more_edge_than_it_has_bins() -> None:
    histogram = Histogram(edges=(0.0, 1.0, 2.0), counts=(4, 6))
    assert len(histogram.edges) == len(histogram.counts) + 1


@pytest.mark.req("FR-DATA-48")
def test_a_histogram_with_a_missing_edge_is_refused() -> None:
    with pytest.raises(ValidationError, match="one more edge"):
        Histogram(edges=(0.0, 1.0), counts=(4, 6))


@pytest.mark.req("FR-DATA-48")
def test_edges_must_increase() -> None:
    with pytest.raises(ValidationError, match="increasing"):
        Histogram(edges=(0.0, 2.0, 1.0), counts=(4, 6))


@pytest.mark.req("FR-DATA-48")
def test_exposure_is_absent_or_one_weight_per_bin() -> None:
    Histogram(edges=(0.0, 1.0, 2.0), counts=(4, 6))
    Histogram(edges=(0.0, 1.0, 2.0), counts=(4, 6), exposure=("1.5", "2.25"))
    with pytest.raises(ValidationError, match="one exposure weight per bin"):
        Histogram(edges=(0.0, 1.0, 2.0), counts=(4, 6), exposure=("1.5",))


@pytest.mark.req("FR-DATA-48")
def test_a_column_profile_carries_no_histogram_by_default() -> None:
    column = ColumnProfile(
        name="driver_age",
        dtype="Int64",
        semantic_type=SemanticType.CONTINUOUS,
        row_count=10,
        null_count=0,
        null_rate=0.0,
        distinct_count=10,
    )
    assert column.histogram is None
