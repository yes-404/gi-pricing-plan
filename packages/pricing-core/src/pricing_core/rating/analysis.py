"""The Dislocation Run's portfolio reader (03 §4.8's frame, §5.2; FR-263, FR-264).

WK-673 Slice 2, `RL-1402`. `read_portfolio` checks the frame when it is called, so a caller gets
the refusal before it builds anything on the result. Messages name a column and a count, or a
column and its dtype, and never a portfolio value.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from decimal import Decimal
from typing import Any, Final

import polars as pl

from model_schema.dislocation import DislocationSpec
from model_schema.scoring import LadderRung
from pricing_core.rating.ladder import RUNG_ORDER
from pricing_core.rating.runtime import CompiledBundle
from pricing_core.rating.score import score_batch

__all__ = ["PortfolioFrameError", "dislocation_frame", "read_portfolio"]

_STAMPED: Final[tuple[str, ...]] = ("purpose", "effective_date", "rating_version_ref")
_EXPOSURE_SCALE: Final = 6
#: The frame's own columns (RL-1402 S2) but `quote_id`; a portfolio column named as one is refused.
_FRAME_COLUMNS: Final[tuple[str, ...]] = (
    "baseline_outcome",
    "candidate_outcome",
    "baseline_minor",
    "candidate_minor",
    "change_minor",
    "baseline_error_code",
    "candidate_error_code",
    "origin_rung",
)


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


def _origin_rung(baseline: Sequence[LadderRung], candidate: Sequence[LadderRung]) -> str | None:
    """The first rung, in `RUNG_ORDER`, present in one ladder only or differing in `value_minor`
    or in `unrounded_minor` (a `Decimal`: `Decimal("100") == Decimal("100.0")`)."""
    base = {r.rung: r for r in baseline}
    cand = {r.rung: r for r in candidate}
    for name in RUNG_ORDER:
        b, c = base.get(name), cand.get(name)
        if b is None and c is None:
            continue
        if b is None or c is None or b.value_minor != c.value_minor:
            return name
        if b.unrounded_minor != c.unrounded_minor:  # Decimal values; None only equals None
            return name
    return None


def _score_pass(
    bundle: CompiledBundle,
    portfolio: pl.LazyFrame,
    columns: Sequence[str],
    spec: DislocationSpec,
    ref: object,
) -> dict[str, dict[str, Any]]:
    """One pass: only `quote_id` and the contract's declared inputs reach the engine (RL-1394)."""
    declared = [f.name for f in bundle.algorithm.input_contract if f.name in columns]
    frame = portfolio.select(["quote_id", *declared]).with_columns(
        pl.lit(spec.purpose).alias("purpose"),
        pl.lit(spec.as_at.isoformat()).alias("effective_date"),
        pl.lit(str(ref)).alias("rating_version_ref"),
    )
    out: dict[str, dict[str, Any]] = {}
    for row in score_batch(bundle, frame).collect().iter_rows(named=True):
        ladder: list[LadderRung] = []
        premium: int | None = None
        if row["outcome"] == "quoted":
            ladder = [LadderRung.model_validate(r) for r in json.loads(row["premium_ladder_json"])]
            payable = [r for r in ladder if r.rung == "payable_premium"]
            if not payable:
                raise ValueError("dislocation: a quoted row carries no payable_premium rung")
            premium = int(payable[0].value_minor)
        out[row["quote_id"]] = {
            "outcome": row["outcome"],
            "error_code": row["error_code"],
            "minor": premium,
            "ladder": ladder,
        }
    return out


def dislocation_frame(
    baseline: CompiledBundle,
    candidate: CompiledBundle,
    portfolio: pl.LazyFrame,
    spec: DislocationSpec,
) -> pl.DataFrame:
    """One row per policy, sorted by `quote_id` (RL-1402 DP-S2-1, S2): both passes' outcome,
    payable premium in integer minor units, the change, the rung it originated at, then every
    portfolio column. Each pass is given only its own contract's declared inputs."""
    schema = portfolio.collect_schema()
    for name in _FRAME_COLUMNS:
        if name in schema:
            raise PortfolioFrameError(f"portfolio column {name!r} collides with the run's frame")
    checked = read_portfolio(portfolio, segments=spec.segments).collect()
    columns = schema.names()
    base = _score_pass(baseline, portfolio, columns, spec, spec.baseline_ref)
    cand = _score_pass(candidate, portfolio, columns, spec, spec.candidate_ref)

    rows: list[dict[str, Any]] = []
    for quote_id in sorted(base):
        b, c = base[quote_id], cand[quote_id]
        both = b["minor"] is not None and c["minor"] is not None
        rows.append(
            {
                "quote_id": quote_id,
                "baseline_outcome": b["outcome"],
                "candidate_outcome": c["outcome"],
                "baseline_minor": b["minor"],
                "candidate_minor": c["minor"],
                "change_minor": c["minor"] - b["minor"] if both else None,
                "baseline_error_code": b["error_code"],
                "candidate_error_code": c["error_code"],
                "origin_rung": _origin_rung(b["ladder"], c["ladder"]) if both else None,
            }
        )
    frame = pl.DataFrame(
        rows,
        schema={
            "quote_id": pl.String,
            "baseline_outcome": pl.String,
            "candidate_outcome": pl.String,
            "baseline_minor": pl.Int64,
            "candidate_minor": pl.Int64,
            "change_minor": pl.Int64,
            "baseline_error_code": pl.String,
            "candidate_error_code": pl.String,
            "origin_rung": pl.String,
        },
    )
    return frame.join(checked, on="quote_id", how="left", maintain_order="left").sort("quote_id")
