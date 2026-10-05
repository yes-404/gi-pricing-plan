"""The Dislocation Run's portfolio reader (03 §4.8's frame, §5.2; FR-263, FR-264).

WK-673 Slice 2, `RL-1402`. `read_portfolio` checks the frame when it is called, so a caller gets
the refusal before it builds anything on the result. Messages name a column and a count, or a
column and its dtype, and never a portfolio value.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from fractions import Fraction
from itertools import pairwise
from typing import Any, Final

import polars as pl

from model_schema.dislocation import (
    DislocationBand,
    DislocationOutcomes,
    DislocationRun,
    DislocationSpec,
    DislocationTotals,
    ErrorSample,
    ErrorTally,
    RungContribution,
    SegmentSlice,
)
from model_schema.scoring import LadderRung
from pricing_core.rating.ladder import RUNG_ORDER
from pricing_core.rating.runtime import CompiledBundle
from pricing_core.rating.score import score_batch

__all__ = [
    "PortfolioFrameError",
    "dislocate",
    "dislocation_frame",
    "read_portfolio",
    "select_movers",
    "summarise_dislocation",
]

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


# ---------------------------------------------------------------------------
# The summary (RL-1402 S1, S3-S5, Amendment N2; 03 §4.6). Money is an `int`; every ratio is a
# `Fraction` of ints rounded once; a float appears only at the model boundary.
# ---------------------------------------------------------------------------

_SAMPLE_SIZE: Final = 10
_SHARE_PLACES: Final = 6


def _rounded_float(ratio: Fraction, places: int) -> float:
    """Round the exact ratio once (half-even), exactly to a `Decimal`, and only then to a float."""
    r = round(ratio, places)
    return float(Decimal(r.numerator) / Decimal(r.denominator))


def _pct(change: int, baseline: int) -> float | None:
    """Σ change ÷ Σ baseline x 100 to 2 places; null when the denominator is 0."""
    return None if baseline == 0 else _rounded_float(Fraction(change, baseline) * 100, 2)


def _share(part: Decimal, whole: Decimal) -> float | None:
    return None if whole == 0 else _rounded_float(Fraction(part) / Fraction(whole), _SHARE_PLACES)


def _compared(frame: pl.DataFrame) -> pl.DataFrame:
    return frame.filter(
        (pl.col("baseline_outcome") == "quoted") & (pl.col("candidate_outcome") == "quoted")
    )


def _banded(frame: pl.DataFrame) -> pl.DataFrame:
    """The compared policies with a positive baseline (RL-1402, Amendment N2)."""
    return _compared(frame).filter(pl.col("baseline_minor") > 0)


def select_movers(frame: pl.DataFrame, spec: DislocationSpec) -> pl.DataFrame:
    """FR-263's movers: banded policies whose |change %| is at least `mover_threshold_pct`,
    decided on ints; by |pct| descending, |change_minor| descending, then `quote_id`."""
    threshold = Fraction(str(spec.mover_threshold_pct))
    kept = [
        row
        for row in _banded(frame).iter_rows(named=True)
        if 100 * abs(row["change_minor"]) >= threshold * row["baseline_minor"]
    ]
    kept.sort(
        key=lambda r: (
            -Fraction(abs(r["change_minor"]), r["baseline_minor"]),
            -abs(r["change_minor"]),
            r["quote_id"],
        )
    )
    return pl.DataFrame(kept, schema=frame.schema)


def _edge_text(edge: Decimal) -> str:
    text = format(edge.normalize(), "f")
    return f"+{text}" if edge > 0 else text


def _band_labels(edges: Sequence[Decimal]) -> list[str]:
    text = [_edge_text(e) for e in edges]
    return [
        f"< {text[0]}%",
        *(f"{a}% to {b}%" for a, b in pairwise(text)),
        f"≥ {text[-1]}%",
    ]


def _sum_decimal(values: Iterable[Decimal]) -> Decimal:
    return sum(values, Decimal(0))


def _level_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _level_sort_key(value: object) -> tuple[Any, ...]:
    """Native order, the null level last (`false` before `true` falls out of `bool`'s order)."""
    return (value is None, value) if value is not None else (True,)


def _group_stats(rows: Sequence[dict[str, Any]]) -> tuple[int, int, int, Decimal]:
    return (
        len(rows),
        sum(r["change_minor"] for r in rows),
        sum(r["baseline_minor"] for r in rows),
        _sum_decimal(r["exposure_years"] for r in rows),
    )


def summarise_dislocation(frame: pl.DataFrame, spec: DislocationSpec) -> DislocationRun:
    """Fold the per-policy frame into the run's summary (03 §4.6; RL-1402 S3-S5)."""
    rows = list(frame.iter_rows(named=True))
    compared = list(_compared(frame).iter_rows(named=True))
    banded = [r for r in compared if r["baseline_minor"] > 0]

    # Totals: integer sums over the compared set.
    base_total = int(sum(r["baseline_minor"] for r in compared))
    cand_total = int(sum(r["candidate_minor"] for r in compared))
    totals = DislocationTotals(
        baseline_premium_minor=base_total,
        candidate_premium_minor=cand_total,
        change_pct=_pct(cand_total - base_total, base_total),
    )

    # Outcomes: each policy once.
    errored = [r for r in rows if "error" in (r["baseline_outcome"], r["candidate_outcome"])]
    pair = [(r["baseline_outcome"], r["candidate_outcome"]) for r in rows]
    outcomes = DislocationOutcomes(
        quoted_both=len(compared),
        quoted_to_declined=sum(p == ("quoted", "declined") for p in pair),
        declined_to_quoted=sum(p == ("declined", "quoted") for p in pair),
        declined_both=sum(p == ("declined", "declined") for p in pair),
        error=len(errored),
        zero_baseline=sum(r["baseline_minor"] == 0 for r in compared),
        negative_baseline=sum(r["baseline_minor"] < 0 for r in compared),
    )

    # Errors: one tally per code, under the baseline's code where that pass errored.
    by_code: dict[str, list[str]] = {}
    for r in errored:
        code = (
            r["baseline_error_code"]
            if r["baseline_outcome"] == "error"
            else r["candidate_error_code"]
        )
        by_code.setdefault(code, []).append(r["quote_id"])
    errors = [
        ErrorTally(
            code=code,
            count=len(ids),
            sample=[ErrorSample(quote_id=i) for i in sorted(ids)[:_SAMPLE_SIZE]],
        )
        for code, ids in sorted(by_code.items())
    ]

    # Bands over the banded set, half-open [lo, hi); an edge belongs to the band above it.
    edges = [Fraction(str(edge)) for edge in spec.band_edges_pct]
    labels = _band_labels(spec.band_edges_pct)
    members: list[list[dict[str, Any]]] = [[] for _ in labels]
    for r in banded:
        pct = Fraction(r["change_minor"], r["baseline_minor"]) * 100
        members[sum(pct >= e for e in edges)].append(r)
    banded_exposure = _sum_decimal(r["exposure_years"] for r in banded)
    distribution = []
    for label, group in zip(labels, members, strict=True):
        n, change, baseline, exposure = _group_stats(group)
        distribution.append(
            DislocationBand(
                band=label,
                policies=n,
                exposure_share=_share(exposure, banded_exposure),
                mean_change_pct=_pct(change, baseline),
            )
        )

    # Segments over the compared set: native level order, the null level last.
    compared_exposure = _sum_decimal(r["exposure_years"] for r in compared)
    by_segment: list[SegmentSlice] = []
    for factor in spec.segments:
        levels = {r[factor] for r in compared}
        for level in sorted(levels, key=_level_sort_key):
            n, change, baseline, exposure = _group_stats(
                [r for r in compared if r[factor] == level]
            )
            by_segment.append(
                SegmentSlice(
                    factor=factor,
                    level=_level_text(level),
                    policies=n,
                    mean_change_pct=_pct(change, baseline),
                    exposure_share=_share(exposure, compared_exposure),
                )
            )

    # Rungs: the change of the compared policies each rung originates, over Σ baseline.
    by_ladder_rung = [
        RungContribution(
            rung=rung,
            contribution_pct=_pct(
                sum(r["change_minor"] for r in compared if r["origin_rung"] == rung), base_total
            ),
        )
        for rung in RUNG_ORDER
        if any(r["origin_rung"] == rung for r in compared)
    ]

    total_exposure = _sum_decimal(r["exposure_years"] for r in rows)
    return DislocationRun(
        baseline_ref=spec.baseline_ref,
        candidate_ref=spec.candidate_ref,
        portfolio_dataset_version_id=spec.portfolio_dataset_version_id,
        policy_count=len(rows),
        exposure_years=total_exposure.quantize(Decimal("0.000001"), ROUND_HALF_EVEN),
        totals=totals,
        outcomes=outcomes,
        distribution=distribution,
        by_segment=by_segment,
        by_ladder_rung=by_ladder_rung,
        errors=errors,
    )


def dislocate(
    baseline: CompiledBundle,
    candidate: CompiledBundle,
    portfolio: pl.LazyFrame,
    spec: DislocationSpec,
) -> DislocationRun:
    """Both passes, then the summary (RL-1402 S1)."""
    return summarise_dislocation(dislocation_frame(baseline, candidate, portfolio, spec), spec)
