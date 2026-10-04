"""The Dislocation Run's portfolio reader (03 §4.8's frame, §5.2; FR-263, FR-264).

WK-673 Slice 2, `RL-1402`. `read_portfolio` checks the frame when it is called, so a caller gets
the refusal before it builds anything on the result. Messages name a column and a count, or a
column and its dtype, and never a portfolio value.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import Final

import polars as pl

__all__ = ["PortfolioFrameError", "read_portfolio"]

_STAMPED: Final[tuple[str, ...]] = ("purpose", "effective_date", "rating_version_ref")
_EXPOSURE_SCALE: Final = 6


class PortfolioFrameError(ValueError):
    """A portfolio that breaks §4.8's frame; the platform maps it to `VALIDATION_FAILED`."""

    code = "VALIDATION_FAILED"


def _is_segment_dtype(dtype: pl.DataType) -> bool:
    return (
        dtype.is_integer()
        or dtype in (pl.String, pl.Boolean, pl.Date, pl.Categorical)
        or isinstance(dtype, pl.Enum)
    )


def _exposure_decimal(value: float) -> Decimal:
    return Decimal(str(round(value, _EXPOSURE_SCALE)))


def read_portfolio(portfolio: pl.LazyFrame, *, segments: Sequence[str] = ()) -> pl.LazyFrame:
    """Check §4.8's frame now; return it, every column kept, `exposure_years` read as a Decimal."""
    schema = portfolio.collect_schema()
    for name in _STAMPED:
        if name in schema:
            raise PortfolioFrameError(
                f"portfolio column {name!r} is reserved and stamped, never read"
            )
    for name in ("quote_id", "exposure_years"):
        if name not in schema:
            raise PortfolioFrameError(f"portfolio column {name!r} is missing")
    exposure_dtype = schema["exposure_years"]
    is_float = exposure_dtype.is_float()
    if not (is_float or exposure_dtype.is_integer() or exposure_dtype.is_decimal()):
        raise PortfolioFrameError(f"column 'exposure_years' has dtype {exposure_dtype}")
    for name in segments:
        if name not in schema:
            raise PortfolioFrameError(f"segment column {name!r} is missing from the portfolio")
        if not _is_segment_dtype(schema[name]):
            raise PortfolioFrameError(f"segment column {name!r} has dtype {schema[name]}")

    exposure = pl.col("exposure_years")
    unusable = exposure.is_null()
    if is_float:
        unusable = unusable | exposure.is_nan() | exposure.is_infinite()
    counts = portfolio.select(
        quote_null=pl.col("quote_id").is_null().sum(),
        quote_duplicated=pl.col("quote_id").is_duplicated().sum(),
        exposure_unusable=unusable.sum(),
        exposure_negative=(exposure < 0).sum(),
    ).collect()
    for column, key, what in (
        ("quote_id", "quote_null", "null"),
        ("quote_id", "quote_duplicated", "duplicated"),
        ("exposure_years", "exposure_unusable", "null, NaN or infinite"),
        ("exposure_years", "exposure_negative", "negative"),
    ):
        count = counts[key][0]
        if count:
            raise PortfolioFrameError(f"column {column!r} has {count} {what} row(s)")

    if not is_float:
        return portfolio.with_columns(
            exposure.cast(pl.Decimal(None, _EXPOSURE_SCALE)).alias("exposure_years")
        )
    return portfolio.with_columns(
        exposure.map_elements(_exposure_decimal, return_dtype=pl.Decimal(None, _EXPOSURE_SCALE))
    )
