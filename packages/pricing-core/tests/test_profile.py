"""Profiling and comparison (`01` §3.4, FR-DATA-25..28)."""

from __future__ import annotations

from uuid import uuid4

import polars as pl
import pytest

from model_schema import SemanticType
from pricing_core.data.profile import (
    compare_profiles,
    gamma_severity_interval,
    infer_semantic_type,
    one_way,
    poisson_frequency_interval,
    profile_frame,
    profile_parquet,
)

#: 400 rows, because the identifier heuristic needs enough of them for uniqueness to mean
#: anything — in a 40-row extract every driver age is distinct too.
_N = 400

FRAME = pl.DataFrame(
    {
        "policy_id": [f"P{i}" for i in range(_N)],
        "driver_age": [17 + (i % 60) for i in range(_N)],
        "vehicle_group": [f"G{i % 5}" for i in range(_N)],
        "exposure_years": [1.0] * _N,
        "claim_count": [1 if i % 4 == 0 else 0 for i in range(_N)],
        "claim_amount_minor": [150_000 if i % 4 == 0 else 0 for i in range(_N)],
        "premium_minor": [30_000] * _N,
    }
)


# -- FR-DATA-25: per-column statistics and semantic type ------------------------------------


@pytest.mark.req("FR-DATA-25")
def test_a_profile_reports_the_statistics_the_requirement_lists() -> None:
    profile = profile_frame(FRAME, dataset_version_id=uuid4())
    age = profile.column("driver_age")

    assert age is not None
    assert age.null_count == 0
    assert age.distinct_count == 60
    assert age.minimum == 17
    assert age.mean == pytest.approx(FRAME.get_column("driver_age").mean())
    assert set(age.quantiles) == {"p1", "p5", "p25", "p50", "p75", "p95", "p99"}


@pytest.mark.req("FR-DATA-25")
@pytest.mark.parametrize(
    ("column", "expected"),
    [
        ("policy_id", SemanticType.IDENTIFIER),
        ("vehicle_group", SemanticType.CATEGORICAL),
        ("driver_age", SemanticType.CONTINUOUS),
        ("premium_minor", SemanticType.MONEY),
    ],
)
def test_semantic_types_are_inferred(column: str, expected: SemanticType) -> None:
    """A dtype says `int32`; policy id, vehicle group and driver age are three different
    things to do with one, and only the third can be banded meaningfully."""
    series = FRAME.get_column(column)
    assert infer_semantic_type(series, row_count=FRAME.height) is expected


@pytest.mark.req("FR-DATA-25")
def test_a_low_cardinality_integer_is_ordinal_not_continuous() -> None:
    """Negative: banding NCD years into deciles merges levels an actuary rates on."""
    series = pl.Series("ncd_years", [0, 1, 2, 3, 4, 5] * 10)
    assert infer_semantic_type(series, row_count=60) is SemanticType.ORDINAL


@pytest.mark.req("FR-DATA-25")
def test_categorical_levels_are_capped_at_twenty() -> None:
    """A high-cardinality column must not put its whole domain in a persisted artifact."""
    frame = pl.DataFrame({"code": [f"C{i % 50}" for i in range(500)]})
    profile = profile_frame(frame, dataset_version_id=uuid4())
    assert len(profile.column("code").top_levels) == 20


# -- FR-DATA-26: one-way summaries with exact intervals --------------------------------------


@pytest.mark.req("FR-DATA-26")
def test_a_one_way_reports_exposure_claims_frequency_severity_and_burning_cost() -> None:
    summary = one_way(FRAME, column="vehicle_group")
    row = summary.rows[0]

    assert row.claim_count >= 0
    assert row.frequency == pytest.approx(row.claim_count / float(row.exposure_years))
    if row.claim_count:
        assert row.severity_minor == pytest.approx(row.claim_amount_minor / row.claim_count)
    assert row.burning_cost_minor == pytest.approx(
        row.claim_amount_minor / float(row.exposure_years)
    )


@pytest.mark.req("FR-DATA-26")
def test_the_poisson_interval_is_exact_not_a_normal_approximation() -> None:
    """The interval must stay positive at low counts.

    A normal approximation puts the lower bound below zero with nine claims — not a
    frequency any actuary will accept on a slide, and precisely the cell they scrutinise.
    """
    low, high = poisson_frequency_interval(9, 100.0)
    assert 0 < low < 0.09 < high
    normal_lower = (9 - 1.96 * 9**0.5) / 100.0
    assert low > 0
    assert low != pytest.approx(normal_lower, rel=0.01)


@pytest.mark.req("FR-DATA-26")
def test_a_zero_claim_cell_has_a_lower_bound_of_zero_and_a_positive_upper() -> None:
    low, high = poisson_frequency_interval(0, 500.0)
    assert low == 0.0
    assert high > 0


@pytest.mark.req("FR-DATA-26")
def test_the_interval_narrows_as_exposure_grows() -> None:
    """The property that makes an interval worth showing at all."""
    narrow = poisson_frequency_interval(1000, 10_000.0)
    wide = poisson_frequency_interval(10, 100.0)
    assert (narrow[1] - narrow[0]) < (wide[1] - wide[0])


@pytest.mark.req("FR-DATA-26")
def test_severity_has_no_interval_below_two_claims() -> None:
    """Negative: an interval from one observation carries no information, and showing one
    invites a decision it cannot support."""
    assert gamma_severity_interval(150_000, 1) is None
    assert gamma_severity_interval(300_000, 2) is not None


@pytest.mark.req("FR-DATA-26")
def test_the_severity_interval_brackets_the_mean() -> None:
    interval = gamma_severity_interval(1_000_000, 10)
    assert interval is not None
    assert interval[0] < 100_000 < interval[1]


# -- FR-DATA-27: DuckDB over parquet ----------------------------------------------------------


@pytest.mark.req("FR-DATA-27")
def test_a_profile_is_computed_from_parquet_with_duckdb(tmp_path) -> None:
    path = tmp_path / "exposure.parquet"
    FRAME.write_parquet(path)

    profile = profile_parquet(
        [str(path)], dataset_version_id=uuid4(), one_way_columns=["vehicle_group"]
    )
    assert profile.row_count == _N
    assert profile.column("driver_age") is not None
    assert profile.one_ways[0].column == "vehicle_group"
    assert "duckdb" in profile.library_versions


@pytest.mark.req("FR-DATA-27")
def test_profiling_no_files_is_an_error_not_an_empty_profile() -> None:
    """Negative: an empty profile would report a dataset as having no columns."""
    with pytest.raises(ValueError, match="no parquet paths"):
        profile_parquet([], dataset_version_id=uuid4())


# -- FR-DATA-28: comparison ---------------------------------------------------------------------


@pytest.mark.req("FR-DATA-28")
def test_a_comparison_reports_psi_shifts_and_level_changes() -> None:
    reference = profile_frame(FRAME, dataset_version_id=uuid4())
    shifted = FRAME.with_columns(
        pl.when(pl.col("vehicle_group") == "G0")
        .then(pl.lit("G9"))
        .otherwise(pl.col("vehicle_group"))
        .alias("vehicle_group")
    )
    current = profile_frame(shifted, dataset_version_id=uuid4())

    comparison = compare_profiles(current, reference)
    group = comparison.column("vehicle_group")

    assert group is not None
    assert group.new_levels == ("G9",)
    assert group.vanished_levels == ("G0",)
    assert group.psi is not None
    assert group.psi > 0


@pytest.mark.req("FR-DATA-28")
def test_an_unchanged_dataset_has_a_psi_of_zero() -> None:
    reference = profile_frame(FRAME, dataset_version_id=uuid4())
    current = profile_frame(FRAME, dataset_version_id=uuid4())
    group = compare_profiles(current, reference).column("vehicle_group")
    assert group.psi == pytest.approx(0.0, abs=1e-9)
    assert group.new_levels == ()


@pytest.mark.req("FR-DATA-28")
def test_a_null_rate_shift_is_reported() -> None:
    """The clearest signal a feed has broken."""
    reference = profile_frame(FRAME, dataset_version_id=uuid4())
    with_nulls = FRAME.with_columns(
        pl.when(pl.col("driver_age") < 30)
        .then(None)
        .otherwise(pl.col("driver_age"))
        .alias("driver_age")
    )
    current = profile_frame(with_nulls, dataset_version_id=uuid4())
    age = compare_profiles(current, reference).column("driver_age")
    assert age.null_rate_shift > 0


@pytest.mark.req("FR-DATA-28")
def test_the_row_count_ratio_is_reported() -> None:
    reference = profile_frame(FRAME, dataset_version_id=uuid4())
    current = profile_frame(FRAME.head(_N // 2), dataset_version_id=uuid4())
    assert compare_profiles(current, reference).row_count_ratio == pytest.approx(0.5)


@pytest.mark.req("FR-DATA-28")
def test_a_rare_new_level_does_not_report_infinite_psi() -> None:
    """Negative: an infinite PSI reports "everything changed" for one rare code appearing,
    which is a warning nobody can act on."""
    reference = profile_frame(
        pl.DataFrame({"code": ["A"] * 100}), dataset_version_id=uuid4()
    )
    current = profile_frame(
        pl.DataFrame({"code": ["A"] * 99 + ["B"]}), dataset_version_id=uuid4()
    )
    psi = compare_profiles(current, reference).column("code").psi
    assert psi is not None
    assert psi < 100


@pytest.mark.req("FR-DATA-25")
def test_a_small_extract_does_not_mistake_a_rating_factor_for_an_identifier() -> None:
    """Negative, and a real misfire this heuristic had.

    In a 40-row sample every driver age is distinct. Calling that an identifier would hide
    the most important rating factor in motor from the factor workbench, so uniqueness only
    counts once there are enough rows for it to mean something.
    """
    small = pl.DataFrame({"driver_age": list(range(17, 57))})
    assert infer_semantic_type(small.get_column("driver_age"), row_count=40) is (
        SemanticType.CONTINUOUS
    )
