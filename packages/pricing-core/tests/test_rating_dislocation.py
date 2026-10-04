"""The Dislocation Run (03 FR-263, FR-264; §4.8's portfolio frame). WK-673 Slice 2, PL-1403."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import polars as pl
import pytest

from pricing_core.rating.analysis import PortfolioFrameError, read_portfolio


def _book(**columns: list[object]) -> pl.LazyFrame:
    base: dict[str, list[object]] = {
        "quote_id": ["Q1", "Q2", "Q3"],
        "exposure_years": [1.0, 0.5, 0.0],
        "driver_age": [34, 22, 70],
    }
    base.update(columns)
    return pl.DataFrame(base, strict=False).lazy()


def _refused(book: pl.LazyFrame, pattern: str, *, segments: tuple[str, ...] = ()) -> str:
    """The refusal is raised AT THE CALL (the frame is never collected here)."""
    with pytest.raises(PortfolioFrameError, match=pattern) as exc:
        read_portfolio(book, segments=segments)
    assert exc.value.code == "VALIDATION_FAILED"
    return str(exc.value)


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_purpose_column_by_name() -> None:
    """RL-1394: a portfolio column named `purpose` is refused, never silently overridden."""
    message = _refused(_book(purpose=["renewal", "renewal", "renewal"]), "purpose")
    assert "renewal" not in message


@pytest.mark.req("FR-263")
@pytest.mark.parametrize("name", ["effective_date", "rating_version_ref"])
def test_read_portfolio_refuses_each_other_stamped_column_by_name(name: str) -> None:
    _refused(_book(**{name: ["x", "x", "x"]}), name)


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_null_exposure_naming_the_column_and_count() -> None:
    """RL-1394 / RL-1361 §E: a null exposure is refused, never read as 0."""
    _refused(_book(exposure_years=[1.0, None, 0.5]), r"exposure_years.*\b1\b")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_nan_exposure() -> None:
    """RL-1402 DP-S2-7: a NaN is not null in Polars and passes `< 0`; refused with the nulls."""
    _refused(_book(exposure_years=[float("nan"), float("inf"), 0.5]), r"exposure_years.*\b2\b")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_negative_exposure() -> None:
    _refused(_book(exposure_years=[1.0, -0.5, -2.0]), r"exposure_years.*\b2\b")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_missing_exposure_column() -> None:
    book = pl.DataFrame({"quote_id": ["Q1"]}).lazy()
    _refused(book, "exposure_years")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_string_exposure_naming_its_dtype() -> None:
    _refused(_book(exposure_years=["1", "2", "3"]), r"exposure_years.*String")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_missing_quote_id_column() -> None:
    book = pl.DataFrame({"exposure_years": [1.0]}).lazy()
    _refused(book, "quote_id")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_null_quote_id() -> None:
    _refused(_book(quote_id=["Q1", None, "Q3"]), r"quote_id.*\b1\b")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_duplicated_quote_id() -> None:
    message = _refused(_book(quote_id=["Q1", "Q1", "Q3"]), r"quote_id.*\b2\b")
    assert "Q1" not in message


@pytest.mark.req("FR-264")
def test_read_portfolio_refuses_a_float_segment_column_naming_its_dtype() -> None:
    """RL-1402 DP-S2-6: a float level has no stable string."""
    _refused(
        _book(vehicle_value=[1.5, 2.5, 3.5]), r"vehicle_value.*Float64", segments=("vehicle_value",)
    )


@pytest.mark.req("FR-264")
def test_read_portfolio_refuses_an_absent_segment_column() -> None:
    _refused(_book(), "region", segments=("region",))


@pytest.mark.req("FR-264")
def test_read_portfolio_admits_every_stated_segment_dtype() -> None:
    book = _book(
        s=["a", "b", None],
        c=pl.Series(["a", "b", "a"], dtype=pl.Categorical),
        e=pl.Series(["a", "b", "a"], dtype=pl.Enum(["a", "b"])),
        b=[True, False, None],
        d=[date(2026, 1, 1), date(2026, 1, 2), None],
    )
    read_portfolio(book, segments=("driver_age", "s", "c", "e", "b", "d"))


@pytest.mark.req("FR-263")
def test_read_portfolio_reads_a_float_exposure_rounded_to_six_places() -> None:
    """RL-1402 DP-S2-7: `_stored_exposure`'s rule (FR-62), the freMTPL2 dtype (Task 0 Step 5)."""
    out = read_portfolio(_book(exposure_years=[0.1234567, 0.5, 0.0])).collect()
    assert out["exposure_years"].dtype == pl.Decimal(None, 6)
    assert out["exposure_years"].to_list() == [Decimal("0.123457"), Decimal("0.5"), Decimal("0")]


@pytest.mark.req("FR-263")
def test_read_portfolio_reads_an_integer_exposure_exactly() -> None:
    out = read_portfolio(_book(exposure_years=[1, 2, 0])).collect()
    assert out["exposure_years"].to_list() == [Decimal(1), Decimal(2), Decimal(0)]


@pytest.mark.req("FR-263")
def test_read_portfolio_keeps_every_column_unchanged() -> None:
    """RL-1361 §E's frame premise: an undeclared column survives; the reader drops nothing."""
    book = _book(region=["N", "S", "N"])
    out = read_portfolio(book).collect()
    assert out.columns == ["quote_id", "exposure_years", "driver_age", "region"]
    assert out["region"].to_list() == ["N", "S", "N"]
    assert out["quote_id"].to_list() == ["Q1", "Q2", "Q3"]
    assert out["driver_age"].to_list() == [34, 22, 70]
