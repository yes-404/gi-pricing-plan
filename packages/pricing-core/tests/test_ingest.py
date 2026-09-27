"""Deterministic ingestion helpers (FR-29, FR-30, FR-32).

Pure functions, so these run without a database, a broker or a platform — which is
ADR-703's promise and the reason they are here rather than in the backend.
"""

from __future__ import annotations

import polars as pl
import pytest

from pricing_core.data.ingest import (
    REJECT_REASON_COLUMN,
    ColumnNameCollisionError,
    infer_schema,
    normalise_column_name,
    normalise_columns,
    partition_rejects,
)

# -- FR-30: normalisation --------------------------------------------------------------


@pytest.mark.req("FR-30")
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("policy_id", "policy_id"),
        ("Policy ID", "policy_id"),
        ("PolicyID", "policy_id"),
        ("  vehicle-group (ABI)  ", "vehicle_group_abi"),
        ("Gross Premium £", "gross_premium"),
        ("NCD%", "ncd"),
        ("exposure.years", "exposure_years"),
        ("2026_exposure", "col_2026_exposure"),
        ("prämie", "pramie"),
        ("HTTPStatus", "http_status"),
    ],
)
def test_names_normalise_to_snake_case(raw: str, expected: str) -> None:
    assert normalise_column_name(raw) == expected


@pytest.mark.req("FR-30")
def test_normalisation_is_deterministic() -> None:
    """FR-30 says deterministic, so the same input gives the same output every time —
    including across processes, which rules out anything hash-ordered."""
    names = ["Policy ID", "Vehicle Group", "Gross Premium £"]
    assert [normalise_column_name(n) for n in names] == [
        normalise_column_name(n) for n in names
    ]


@pytest.mark.req("FR-30")
def test_a_collision_is_an_error_not_a_silent_rename() -> None:
    """The negative test FR-30 exists for.

    Without it the second column overwrites the first and an actuary fits on data that
    silently lost a field.
    """
    with pytest.raises(ColumnNameCollisionError) as exc:
        normalise_columns(["Policy ID", "policy id", "exposure"])
    assert exc.value.normalised == "policy_id"
    assert {exc.value.first, exc.value.second} == {"Policy ID", "policy id"}


@pytest.mark.req("FR-30")
def test_the_source_name_is_retained() -> None:
    """FR-30: the original goes in the Data Dictionary as `source_name`."""
    mapping = normalise_columns(["Policy ID", "Gross Premium £"])
    assert mapping.source_names == {
        "policy_id": "Policy ID",
        "gross_premium": "Gross Premium £",
    }
    assert mapping.rename_map == {
        "Policy ID": "policy_id",
        "Gross Premium £": "gross_premium",
    }


@pytest.mark.req("FR-30")
def test_a_name_that_normalises_to_nothing_is_refused() -> None:
    with pytest.raises(ValueError, match="normalises to nothing"):
        normalise_column_name("£$%")


# -- FR-29: schema inference -----------------------------------------------------------


@pytest.mark.req("FR-29")
def test_inference_reports_dtype_nullability_and_cardinality() -> None:
    frame = pl.DataFrame(
        {
            "policy_id": ["P1", "P2", "P3"],
            "vehicle_group": [10, 20, None],
            "exposure_years": [1.0, 0.5, 0.25],
        }
    )
    schema = infer_schema(frame)
    by_name = {c.name: c for c in schema.columns}

    assert schema.row_count == 3
    assert by_name["policy_id"].nullable is False
    assert by_name["policy_id"].distinct_count == 3
    assert by_name["vehicle_group"].nullable is True
    assert by_name["vehicle_group"].null_count == 1
    assert "Int" in by_name["vehicle_group"].dtype


@pytest.mark.req("FR-29")
def test_a_unique_non_null_column_is_a_candidate_key() -> None:
    frame = pl.DataFrame({"policy_id": ["P1", "P2"], "peril": ["AD", "AD"]})
    schema = infer_schema(frame)
    assert schema.candidate_keys == ("policy_id",)


@pytest.mark.req("FR-29")
def test_a_single_row_frame_proposes_no_keys() -> None:
    """Negative: every column of a one-row sample is 'unique'. Proposing all of them as
    keys would make the first upload of a sample file suggest nonsense."""
    schema = infer_schema(pl.DataFrame({"a": [1], "b": ["x"]}))
    assert schema.candidate_keys == ()


@pytest.mark.req("FR-29")
def test_a_nullable_column_is_not_a_candidate_key() -> None:
    frame = pl.DataFrame({"maybe_id": ["A", None, "C"]})
    assert infer_schema(frame).candidate_keys == ()


@pytest.mark.req("FR-29")
@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (["2026-01-01", "2026-06-30"], "%Y-%m-%d"),
        (["31/12/2025", "01/06/2026"], "%d/%m/%Y"),
        (["2026-01-01T09:00:00", "2026-06-30T17:30:00"], "%Y-%m-%dT%H:%M:%S"),
        (["not a date", "either"], None),
    ],
)
def test_date_formats_are_sniffed(values: list[str], expected: str | None) -> None:
    frame = pl.DataFrame({"d": values})
    assert infer_schema(frame).columns[0].date_format == expected


@pytest.mark.req("FR-29")
def test_an_ambiguous_date_resolves_to_the_british_form() -> None:
    """`03/04/2026` is both `%d/%m/%Y` and `%m/%d/%Y`, and data cannot say which.

    The order is a documented default for a UK/EU platform, and FR-29 makes the user
    confirm — which is the only honest resolution. Asserted so the default cannot change
    silently.
    """
    frame = pl.DataFrame({"d": ["03/04/2026", "05/06/2026"]})
    assert infer_schema(frame).columns[0].date_format == "%d/%m/%Y"


@pytest.mark.req("FR-29")
def test_inference_carries_a_sample_for_the_confirmation_screen() -> None:
    frame = pl.DataFrame({"peril": ["AD", "TP", "FT", "WS"]})
    column = infer_schema(frame, sample_values=2).columns[0]
    assert column.sample == ("AD", "TP")


# -- FR-32: quarantine -----------------------------------------------------------------


@pytest.mark.req("FR-32")
def test_rows_missing_a_required_value_are_quarantined_not_dropped() -> None:
    """The point of FR-32: an unparseable row is evidence about the feed."""
    frame = pl.DataFrame(
        {
            "policy_id": ["P1", "P2", "P3"],
            "exposure_start": ["2026-01-01", None, "2026-03-01"],
        }
    )
    partition = partition_rejects(frame, required_non_null=["exposure_start"])

    assert partition.clean.height == 2
    assert partition.rejected.height == 1
    assert partition.rejected.get_column("policy_id").to_list() == ["P2"]
    assert (
        partition.rejected.get_column(REJECT_REASON_COLUMN).to_list()
        == ["exposure_start is null"]
    )


@pytest.mark.req("FR-32")
def test_no_rows_are_lost_between_clean_and_rejected() -> None:
    """Negative: the whole requirement is that nothing disappears silently."""
    frame = pl.DataFrame(
        {"a": list(range(10)), "b": [None if i % 3 == 0 else i for i in range(10)]}
    )
    partition = partition_rejects(frame, required_non_null=["b"])
    assert partition.clean.height + partition.rejected.height == frame.height


@pytest.mark.req("FR-32")
def test_the_reject_rate_is_reported_for_the_threshold_rule() -> None:
    """`ingest.reject_rate` is a rule; this function reports, it does not decide."""
    frame = pl.DataFrame({"a": [1, 2, 3, 4], "b": [None, None, 3, 4]})
    partition = partition_rejects(frame, required_non_null=["b"])
    assert partition.reject_rate == 0.5


@pytest.mark.req("FR-32")
def test_the_reason_names_the_first_failing_column() -> None:
    frame = pl.DataFrame({"a": [None], "b": [None]})
    partition = partition_rejects(frame, required_non_null=["a", "b"])
    assert partition.rejected.get_column(REJECT_REASON_COLUMN).to_list() == ["a is null"]


@pytest.mark.req("FR-32")
def test_a_frame_with_no_required_columns_rejects_nothing() -> None:
    frame = pl.DataFrame({"a": [1, None]})
    partition = partition_rejects(frame)
    assert partition.clean.height == 2
    assert partition.rejected.height == 0
    assert partition.reject_rate == 0.0


@pytest.mark.req("FR-32")
def test_a_missing_required_column_is_an_error() -> None:
    """Negative: silently rejecting every row because a column is absent would look like
    a catastrophic data problem rather than a configuration mistake."""
    with pytest.raises(ValueError, match="required columns absent"):
        partition_rejects(pl.DataFrame({"a": [1]}), required_non_null=["b"])
