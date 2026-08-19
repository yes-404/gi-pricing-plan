"""Profiling and comparison (`01` §3.4, FR-DATA-25..28)."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import numpy as np
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
        assert row.mean_severity == pytest.approx(row.claim_amount_minor / row.claim_count)
    assert row.mean_burning_cost == pytest.approx(
        row.claim_amount_minor / float(row.exposure_years)
    )


@pytest.mark.req("FR-DATA-46")
def test_the_one_way_means_are_named_as_means_not_as_minor_units() -> None:
    """FR-OVR-7 reserves `_minor` for integer minor units; both of these are float means."""
    summary = one_way(
        FRAME,
        column="vehicle_group",
        exposure_column="exposure_years",
        claim_count_column="claim_count",
        claim_amount_column="claim_amount_minor",
    )
    row = summary.rows[0]

    assert row.mean_severity is not None
    assert row.mean_burning_cost is not None
    assert not hasattr(row, "severity_minor")
    assert not hasattr(row, "burning_cost_minor")


@pytest.mark.req("FR-DATA-26")
def test_the_profile_records_which_column_weighted_its_one_ways() -> None:
    """`weight_column` must record the *argument*, not restate its own default.

    The field defaults to `"exposure_years"`, which is also the column almost every caller
    passes — so an assertion made against a default-named column passes whether or not
    anything wired it, and would still pass if `weight_column=exposure_column` were deleted
    outright. This profiles a frame whose exposure column is deliberately named something
    else, which is the only arrangement that can tell the two apart.

    It matters because a reader of `one_ways` alone — the frontend, or an actuary reading a
    stored artifact months later — has no other way to learn what "exposure" meant here.
    """
    renamed = FRAME.rename({"exposure_years": "earned_years"})

    profile = profile_frame(
        renamed,
        dataset_version_id=uuid4(),
        one_way_columns=("vehicle_group",),
        exposure_column="earned_years",
    )

    assert profile.weight_column == "earned_years"


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


@pytest.mark.req("FR-DATA-27")
def test_the_two_profiling_paths_agree(tmp_path: Path) -> None:
    """FR-DATA-27: a Profile records what is in a dataset, not which engine read it.

    `profile_frame` runs in Polars and `profile_parquet` in DuckDB. If they disagree, then
    "what is the p99 claim amount?" has two answers and the honest reply to an actuary is
    "which screen are you looking at?". Every divergence this test once caught was a real
    defect: ties in `top_levels` broken by grouping order, null counted as a distinct
    value on one side only, and each engine's own default quantile interpolation.
    """
    rng = np.random.default_rng(7)
    rows = 5_000
    frame = pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(rows)],
            "vehicle_group": [f"G{i % 40}" for i in range(rows)],
            "driver_age": (18 + rng.integers(0, 60, rows)).astype("int64"),
            "exposure_years": rng.uniform(0.1, 1.0, rows),
            "claim_count": rng.poisson(0.1, rows).astype("int64"),
            "claim_amount_minor": (
                rng.poisson(0.1, rows) * rng.integers(1, 500_000, rows)
            ).astype("int64"),
            "nullable": pl.Series(
                [None if i % 7 == 0 else float(i) for i in range(rows)]
            ),
        }
    )
    path = tmp_path / "exposure.parquet"
    frame.write_parquet(path)
    one_way_columns = ["vehicle_group", "driver_age"]

    from_frame = profile_frame(
        frame, dataset_version_id=uuid4(), one_way_columns=one_way_columns
    )
    from_parquet = profile_parquet(
        [str(path)], dataset_version_id=uuid4(), one_way_columns=one_way_columns
    )

    volatile = {"id", "dataset_version_id", "computed_at", "library_versions"}
    left = from_frame.model_dump(mode="json", exclude=volatile)
    right = from_parquet.model_dump(mode="json", exclude=volatile)

    # `std` is the one statistic left to differ, in the last one or two bits: the engines
    # sum in different thread orders and float addition is not associative. Everything
    # else — including every derived ratio — must match exactly.
    for profile in (left, right):
        for column in profile["columns"]:
            column["std"] = None if column["std"] is None else round(column["std"], 6)

    assert left == right


@pytest.mark.req("FR-DATA-26")
def test_a_one_way_row_is_internally_consistent() -> None:
    """A reader who divides the published claim count by the published exposure gets the
    published frequency back. The ratios are derived from the stored Decimal rather than
    the raw sum precisely so this holds."""
    frame = pl.DataFrame(
        {
            "vehicle_group": ["G1"] * 30 + ["G2"] * 30,
            "exposure_years": [0.1234567] * 60,
            "claim_count": [1, 0] * 30,
            "claim_amount_minor": [250_000, 0] * 30,
        }
    )
    summary = one_way(frame, column="vehicle_group")
    for row in summary.rows:
        assert row.frequency == pytest.approx(row.claim_count / float(row.exposure_years))
        assert row.mean_burning_cost == pytest.approx(
            row.claim_amount_minor / float(row.exposure_years)
        )


@pytest.mark.req("NFR-DATA-3")
def test_the_parquet_profiler_never_materialises_the_dataset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """NFR-DATA-3: profiling aggregates in DuckDB; its memory must not scale with rows.

    Asserted structurally rather than by timing or RSS, both of which are noisy enough on
    a shared runner to be re-run rather than believed. If `profile_parquet` ever again
    reaches for the in-memory profiler — the original implementation ran `SELECT *` and
    handed the frame over, peaking at 2.1 GB on a 1.1 GB payload — this fails immediately.
    """
    frame = pl.DataFrame(
        {
            "vehicle_group": [f"G{i % 5}" for i in range(400)],
            "exposure_years": [0.5] * 400,
            "claim_count": [1, 0] * 200,
            "claim_amount_minor": [100_000, 0] * 200,
        }
    )
    path = tmp_path / "exposure.parquet"
    frame.write_parquet(path)

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise AssertionError(
            "profile_parquet loaded the whole dataset into profile_frame — NFR-DATA-3 "
            "requires the statistics be aggregated in DuckDB"
        )

    monkeypatch.setattr("pricing_core.data.profile.profile_frame", refuse)

    profile = profile_parquet(
        [str(path)], dataset_version_id=uuid4(), one_way_columns=["vehicle_group"]
    )
    assert profile.row_count == 400
    assert profile.one_ways[0].rows


@pytest.mark.req("FR-DATA-26")
def test_one_way_columns_are_chosen_from_the_inferred_semantic_types() -> None:
    """FR-DATA-26: one-ways go "per candidate rating column", decided from what the
    profiler inferred rather than from a list of names.

    Shaped on freMTPL2, whose rating factors are `area`, `veh_power`, `veh_brand`,
    `veh_gas` and `region`. A list of English defaults matched exactly one of them, so
    twelve of thirteen columns had no one-way and `02`'s factor workbench would have had
    almost nothing to read.
    """
    rows = 400
    frame = pl.DataFrame(
        {
            "policy_id": [f"P{i}" for i in range(rows)],
            "exposure_years": [1.0] * rows,
            "claim_count": [i % 2 for i in range(rows)],
            "claim_amount_minor": [(i % 2) * 250_000 for i in range(rows)],
            "area": [f"A{i % 6}" for i in range(rows)],
            "veh_power": [4 + i % 12 for i in range(rows)],
            "veh_brand": [f"B{i % 11}" for i in range(rows)],
            "veh_gas": ["Diesel" if i % 2 else "Regular" for i in range(rows)],
            "region": [f"R{i % 22}" for i in range(rows)],
            "density": [float(i) for i in range(rows)],
        }
    )
    profile = profile_frame(frame, dataset_version_id=uuid4(), one_way_columns="auto")
    chosen = {summary.column for summary in profile.one_ways}

    assert chosen == {"area", "veh_power", "veh_brand", "veh_gas", "region"}
    # The measures are excluded: a one-way of claim count *by* claim count answers nothing.
    assert "claim_count" not in chosen
    assert "claim_amount_minor" not in chosen
    assert "exposure_years" not in chosen
    # An identifier has one row per level, and a continuous column needs banding first —
    # which is `02`'s factor workbench, not this.
    assert "policy_id" not in chosen
    assert "density" not in chosen


@pytest.mark.req("FR-DATA-26")
def test_a_column_with_too_many_levels_is_not_a_rating_factor() -> None:
    """A one-way is a summary. Two hundred bars is already unreadable, and a column with
    more levels than that is not a factor anyone rates on without banding it first."""
    from pricing_core.data.profile import MAX_ONE_WAY_LEVELS, candidate_rating_columns

    rows = 600
    frame = pl.DataFrame(
        {
            "exposure_years": [1.0] * rows,
            "claim_count": [0] * rows,
            # 300 distinct string levels: categorical by dtype, useless as a one-way.
            "postcode": [f"PC{i % 300}" for i in range(rows)],
            "region": [f"R{i % 12}" for i in range(rows)],
        }
    )
    profile = profile_frame(frame, dataset_version_id=uuid4())
    chosen = candidate_rating_columns(profile.columns)

    assert "region" in chosen
    assert "postcode" not in chosen, f"300 levels exceeds {MAX_ONE_WAY_LEVELS}"


# -- FR-DATA-48: histograms ------------------------------------------------------------


@pytest.mark.req("FR-DATA-48")
def test_a_numeric_column_gets_a_histogram() -> None:
    profile = profile_frame(FRAME, dataset_version_id=uuid4())
    age = profile.column("driver_age")

    assert age is not None
    assert age.histogram is not None
    assert len(age.histogram.edges) == len(age.histogram.counts) + 1
    assert age.histogram.edges[0] == age.minimum
    assert age.histogram.edges[-1] == age.maximum
    # Every non-null row lands in exactly one bin, the maximum included.
    assert sum(age.histogram.counts) == FRAME.height - age.null_count


@pytest.mark.req("FR-DATA-48")
def test_an_identifier_and_a_categorical_get_no_histogram() -> None:
    profile = profile_frame(FRAME, dataset_version_id=uuid4())
    policy_id, vehicle_group = profile.column("policy_id"), profile.column("vehicle_group")

    assert policy_id is not None
    assert policy_id.histogram is None
    assert vehicle_group is not None
    assert vehicle_group.histogram is None


@pytest.mark.req("FR-DATA-48")
def test_the_maximum_lands_in_the_last_bin_not_past_it() -> None:
    """The closed last bin. Without it the maximum falls in bin 20 of 20 and is lost."""
    frame = pl.DataFrame({"x": [float(i) for i in range(101)]})
    column = profile_frame(frame, dataset_version_id=uuid4()).column("x")

    assert column is not None
    assert column.histogram is not None
    assert sum(column.histogram.counts) == 101
    assert column.histogram.counts[-1] > 0


@pytest.mark.req("FR-DATA-48")
def test_a_constant_column_is_one_bin_not_twenty_empty_ones() -> None:
    frame = pl.DataFrame({"x": [3.0] * 50})
    column = profile_frame(frame, dataset_version_id=uuid4()).column("x")

    assert column is not None
    assert column.histogram is not None
    assert column.histogram.counts == (50,)
    assert column.histogram.edges == (3.0, 4.0)


@pytest.mark.req("FR-DATA-48")
def test_the_histogram_carries_exposure_when_the_column_is_present() -> None:
    age = profile_frame(FRAME, dataset_version_id=uuid4()).column("driver_age")

    assert age is not None
    assert age.histogram is not None
    assert len(age.histogram.exposure) == len(age.histogram.counts)
    # FRAME carries exactly 1.0 exposure year per row, so bin exposure equals bin count.
    assert [float(e) for e in age.histogram.exposure] == [float(c) for c in age.histogram.counts]


@pytest.mark.req("FR-DATA-48")
def test_no_exposure_column_means_no_weights_not_zeroes() -> None:
    frame = pl.DataFrame({"x": [1.0, 2.0, 3.0]})
    column = profile_frame(frame, dataset_version_id=uuid4()).column("x")

    assert column is not None
    assert column.histogram is not None
    assert column.histogram.exposure == ()


@pytest.mark.req("FR-DATA-48")
def test_nulls_are_excluded_from_every_bin() -> None:
    frame = pl.DataFrame({"x": [1.0, 2.0, None, 4.0]})
    column = profile_frame(frame, dataset_version_id=uuid4()).column("x")

    assert column is not None
    assert column.histogram is not None
    assert sum(column.histogram.counts) == 3


@pytest.mark.req("FR-DATA-48")
def test_both_engines_bin_a_column_identically(tmp_path: Path) -> None:
    frame = pl.DataFrame(
        {
            "driver_age": [17 + (i % 60) for i in range(400)],
            "exposure_years": [0.5 + (i % 3) / 4 for i in range(400)],
        }
    )
    path = tmp_path / "ages.parquet"
    frame.write_parquet(path)

    from_frame = profile_frame(frame, dataset_version_id=uuid4()).column("driver_age")
    from_parquet = profile_parquet([str(path)], dataset_version_id=uuid4()).column("driver_age")

    assert from_frame is not None
    assert from_parquet is not None
    assert from_frame.histogram == from_parquet.histogram
