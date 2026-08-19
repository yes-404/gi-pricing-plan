"""Profile shapes (`01` §4.7, FR-DATA-48, FR-DATA-49)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema import ColumnProfile, Histogram, LevelCount, SemanticType


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


@pytest.mark.req("FR-DATA-49")
def test_a_level_count_round_trips() -> None:
    level = LevelCount(level="petrol", count=1204, exposure_years="450.500")
    assert level.level == "petrol"
    assert level.count == 1204
    assert str(level.exposure_years) == "450.500"


@pytest.mark.req("FR-DATA-49")
def test_a_level_count_refuses_a_negative_count() -> None:
    with pytest.raises(ValidationError, match="count"):
        LevelCount(level="petrol", count=-1)


@pytest.mark.req("FR-DATA-49")
def test_exposure_years_accepts_an_exact_decimal_string() -> None:
    level = LevelCount(level="petrol", count=10, exposure_years="12.500")
    assert str(level.exposure_years) == "12.500"


@pytest.mark.req("FR-DATA-49")
def test_exposure_years_refuses_a_float_shaped_value() -> None:
    """A float has already lost whatever precision the source amount carried before

    pydantic ever sees it (FR-OVR-7's rule for the money and exposure path) — so this
    field must be reached with a string or `Decimal`, never a Python float, even one
    that has a whole-looking value like `12.0`.
    """
    with pytest.raises(ValidationError, match="exposure_years"):
        LevelCount(level="petrol", count=10, exposure_years=12.5)
    with pytest.raises(ValidationError, match="exposure_years"):
        LevelCount(level="petrol", count=10, exposure_years=12.0)


@pytest.mark.req("FR-DATA-49")
def test_top_levels_defaults_to_empty() -> None:
    column = ColumnProfile(
        name="fuel_type",
        dtype="Utf8",
        semantic_type=SemanticType.CATEGORICAL,
        row_count=10,
        null_count=0,
        null_rate=0.0,
        distinct_count=2,
    )
    assert column.top_levels == ()


@pytest.mark.req("FR-DATA-49")
def test_top_levels_is_capped_at_twenty() -> None:
    levels = tuple(LevelCount(level=f"level-{i}", count=1) for i in range(20))
    column = ColumnProfile(
        name="fuel_type",
        dtype="Utf8",
        semantic_type=SemanticType.CATEGORICAL,
        row_count=20,
        null_count=0,
        null_rate=0.0,
        distinct_count=20,
        top_levels=levels,
    )
    assert len(column.top_levels) == 20

    too_many = (*levels, LevelCount(level="level-20", count=1))
    with pytest.raises(ValidationError, match="top_levels"):
        ColumnProfile(
            name="fuel_type",
            dtype="Utf8",
            semantic_type=SemanticType.CATEGORICAL,
            row_count=21,
            null_count=0,
            null_rate=0.0,
            distinct_count=21,
            top_levels=too_many,
        )


@pytest.mark.req("FR-DATA-49")
def test_a_null_level_is_accepted_and_distinct_from_the_string_null() -> None:
    """The authored contract declares `level` as `["string", "null"]` (FR-DATA-49): a null

    level is a real category in a book with missing data, and collapsing it to the
    string `"null"` — as the engines' current `str(level)` coercion does for a genuine
    SQL NULL — would make it indistinguishable from the literal value `"null"`.
    """
    missing = LevelCount(level=None, count=7)
    literal = LevelCount(level="null", count=7)
    assert missing.level is None
    assert literal.level == "null"
    assert missing != literal
