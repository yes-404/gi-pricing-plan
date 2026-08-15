"""Bandings: continuous columns cut into levels an actuary can rate on (`02` §3.2).

Four requirements shape everything here:

* **FR-MODEL-8** — bands are ordered, exhaustive and non-overlapping, with *explicit*
  handling of nulls and out-of-range values. The explicitness is the requirement: a
  silently clamped driver age of 3 is a data defect that has become a price.
* **FR-MODEL-9** — the platform *proposes*; the actuary edits; what is stored is what was
  accepted. So `propose_banding` returns a complete `Banding` rather than a set of numbers,
  and nothing here writes anything.
* **FR-MODEL-10** — the proposal carries its evidence: per-band exposure, claim count,
  frequency, severity and burning cost with intervals, as of derivation. Computed with
  `01`'s own `one_way`, because a band is a level and `01` FR-DATA-26 already defines what
  a level's statistics are. Two implementations of "the frequency of this cell" would
  disagree in the fourth digit and nobody would know which screen was right.
* **FR-MODEL-11** — a band that meets neither the minimum exposure nor the minimum claim
  count is reported; an **empty** band always fails.

**Where the last band ends.** Under `closed="left"` band *i* is `[bᵢ, bᵢ₊₁)`, except the
last, which is `[bₙ₋₁, bₙ]` — closed at both ends. Without that the observed maximum falls
*outside* every band of a banding derived from the observed range, and a proposal would
declare its own source data out of range. `closed="right"` is the mirror image.
"""

from __future__ import annotations

import math
from typing import Literal
from uuid import UUID

import numpy as np
import polars as pl

from model_schema import (
    AboveRangePolicy,
    Banding,
    BandingMethod,
    BandingProposal,
    BelowRangePolicy,
    OneWayRow,
    new_uuid7,
)
from pricing_core.data.profile import one_way
from pricing_core.modelling.errors import BandingError, FactorResolutionError

__all__ = [
    "apply_banding",
    "band_statistics",
    "check_banding",
    "propose_banding",
]

#: `credibility` merging stops here rather than at one band. A single band is not a
#: banding; it is the column removed from the model, which is a decision an actuary makes
#: rather than one a merge loop reaches.
_MIN_BANDS = 2


def propose_banding(
    frame: pl.DataFrame,
    proposal: BandingProposal,
    *,
    dataset_id: UUID,
    slug: str,
) -> Banding:
    """Propose boundaries for `proposal.column` by its method (FR-MODEL-9).

    `dataset_id` and `slug` are passed in rather than read from the proposal: a `Banding`
    is an artifact with an identity, and identity is the platform's to allocate.
    `02` §5.2's two-argument signature is unimplementable for the same reason `fit_glm`'s
    was — it needs facts that live in a database, which ADR-0001 keeps out of this package.

    The result is a complete, **editable** `Banding`. Nothing is persisted; FR-MODEL-9 is
    explicit that the final boundaries are whatever the actuary accepted.
    """
    if proposal.method is BandingMethod.MANUAL:
        raise BandingError(
            "FACTOR_RESOLUTION_FAILED",
            "a `manual` banding has nothing to propose — its boundaries are the actuary's "
            "judgement, and inventing some to be edited would put the platform's name on "
            "them. Persist the boundaries directly instead.",
        )
    if proposal.method is BandingMethod.TREE:
        raise BandingError(
            "FACTOR_RESOLUTION_FAILED",
            "`tree` boundaries need a shallow decision tree on the response "
            "(FR-MODEL-9), which needs a tree learner this build does not depend on. "
            "Named rather than silently substituted: quantile boundaries returned under "
            "the label `tree` would be a method recorded as one it is not.",
        )

    column = proposal.column
    if column not in frame.columns:
        raise FactorResolutionError(
            f"cannot band {column!r}: this dataset version does not have it (FR-MODEL-2)."
        )

    values = frame[column].cast(pl.Float64)
    finite = values.drop_nulls().drop_nans()
    if finite.len() == 0:
        raise BandingError(
            "FACTOR_RESOLUTION_FAILED",
            f"{column!r} has no non-null numeric values in this dataset version, so there "
            "is no range to cut.",
        )

    exposure = (
        frame[proposal.exposure_column].cast(pl.Float64)
        if proposal.exposure_column in frame.columns
        else None
    )
    claims = (
        frame[proposal.claim_count_column].cast(pl.Float64)
        if proposal.claim_count_column in frame.columns
        else None
    )

    boundaries = _boundaries(
        values, exposure=exposure, claims=claims, proposal=proposal
    )
    banding = Banding(
        id=new_uuid7(),
        slug=slug,
        dataset_id=dataset_id,
        version=1,
        column=column,
        method=proposal.method,
        method_params={
            "n_bands": float(len(boundaries) - 1),
            **{k: float(v) for k, v in proposal.method_params.items()},
        },
        derived_on_dataset_version_id=proposal.dataset_version_id,
        boundaries=tuple(boundaries),
        closed=proposal.closed,
        labels=_labels(boundaries, closed=proposal.closed),
        null_level=proposal.null_level,
        below_range=proposal.below_range,
        above_range=proposal.above_range,
    )
    return banding.model_copy(
        update={
            "band_stats": band_statistics(
                frame,
                banding,
                exposure_column=proposal.exposure_column,
                claim_count_column=proposal.claim_count_column,
                claim_amount_column=proposal.claim_amount_column,
            )
        }
    )


def _boundaries(
    values: pl.Series,
    *,
    exposure: pl.Series | None,
    claims: pl.Series | None,
    proposal: BandingProposal,
) -> list[float]:
    """Cut points for the requested method, strictly increasing and covering the range."""
    method = proposal.method
    n = proposal.n_bands

    if method is BandingMethod.EQUAL_WIDTH:
        cuts = _equal_width(values, n)
    elif method is BandingMethod.QUANTILE:
        cuts = _weighted_quantiles(values, weights=None, n=n)
    elif method is BandingMethod.EXPOSURE_QUANTILE:
        if exposure is None:
            raise BandingError(
                "FACTOR_RESOLUTION_FAILED",
                f"`exposure_quantile` needs {proposal.exposure_column!r}, which this "
                "dataset version does not have. Row-count quantiles are a different "
                "method and would be recorded under the wrong name.",
            )
        cuts = _weighted_quantiles(values, weights=exposure, n=n)
    elif method is BandingMethod.CREDIBILITY:
        cuts = _credibility(values, exposure=exposure, claims=claims, proposal=proposal)
    else:  # pragma: no cover — MANUAL and TREE are refused above
        raise BandingError(
            "FACTOR_RESOLUTION_FAILED", f"unhandled banding method {method.value!r}"
        )

    cuts = _deduplicate(cuts)
    if len(cuts) < 2:
        raise BandingError(
            "FACTOR_RESOLUTION_FAILED",
            f"{proposal.column!r} takes too few distinct values to cut into bands: every "
            "proposed boundary collapsed onto the same point. Treat it as a categorical "
            "factor, or band it manually.",
        )
    return cuts


def _equal_width(values: pl.Series, n: int) -> list[float]:
    low, high = float(values.min()), float(values.max())  # type: ignore[arg-type]
    if not math.isfinite(low) or not math.isfinite(high) or high <= low:
        raise BandingError(
            "FACTOR_RESOLUTION_FAILED",
            f"the column spans [{low}, {high}], which is not a range that can be cut into "
            "bands of equal width.",
        )
    return [float(x) for x in np.linspace(low, high, n + 1)]


def _weighted_quantiles(
    values: pl.Series, *, weights: pl.Series | None, n: int
) -> list[float]:
    """Cut points at equal shares of weight — of rows, or of exposure.

    Exposure-weighted quantiles are the actuarial default and are **not** row quantiles: a
    book whose young drivers hold a third of the policies and a tenth of the exposure gets
    materially different cut points, and it is the exposure share that decides how much a
    band's estimate can be trusted.
    """
    frame = pl.DataFrame({"v": values})
    if weights is not None:
        frame = frame.with_columns(w=weights)
    else:
        frame = frame.with_columns(w=pl.lit(1.0))
    frame = frame.drop_nulls().filter(pl.col("v").is_not_nan() & (pl.col("w") > 0)).sort("v")
    if frame.height == 0:
        raise BandingError(
            "FACTOR_RESOLUTION_FAILED",
            "no row carries both a value and a positive weight, so there is no "
            "distribution to take quantiles of.",
        )

    v = frame["v"].to_numpy()
    cumulative = np.cumsum(frame["w"].to_numpy())
    total = float(cumulative[-1])
    targets = [total * k / n for k in range(1, n)]
    interior = [float(v[int(np.searchsorted(cumulative, t, side="left"))]) for t in targets]
    return [float(v[0]), *interior, float(v[-1])]


def _credibility(
    values: pl.Series,
    *,
    exposure: pl.Series | None,
    claims: pl.Series | None,
    proposal: BandingProposal,
) -> list[float]:
    """Merge adjacent bands until each meets a minimum claim count (FR-MODEL-9).

    Starts from a fine cut — exposure quantiles where exposure exists, row quantiles
    otherwise — and repeatedly dissolves the thinnest band into the *smaller* of its
    neighbours, which is what keeps the merge from sweeping the whole tail into one band.
    """
    if claims is None:
        raise BandingError(
            "FACTOR_RESOLUTION_FAILED",
            f"`credibility` banding needs {proposal.claim_count_column!r} to count claims "
            "per band, and this dataset version does not have it.",
        )
    minimum = float(proposal.method_params.get("min_claims_per_band", 200.0))
    cuts = _deduplicate(_weighted_quantiles(values, weights=exposure, n=proposal.n_bands))

    frame = (
        pl.DataFrame({"v": values, "c": claims})
        .drop_nulls()
        .filter(pl.col("v").is_not_nan())
    )
    v = frame["v"].to_numpy()
    c = frame["c"].to_numpy()

    while len(cuts) - 1 > _MIN_BANDS:
        counts = _claims_per_band(v, c, cuts)
        thinnest = int(np.argmin(counts))
        if counts[thinnest] >= minimum:
            break
        # Dissolve the thinnest band by removing the boundary it shares with its smaller
        # neighbour. At either end there is only one boundary that can go.
        if thinnest == 0:
            cuts.pop(1)
        elif thinnest == len(counts) - 1:
            cuts.pop(len(cuts) - 2)
        else:
            left, right = counts[thinnest - 1], counts[thinnest + 1]
            cuts.pop(thinnest if left <= right else thinnest + 1)
    return cuts


def _claims_per_band(v: np.ndarray, c: np.ndarray, cuts: list[float]) -> np.ndarray:
    """Claim count per band, with the last band closed on both ends."""
    index = np.searchsorted(np.asarray(cuts[1:-1], dtype=np.float64), v, side="right")
    return np.asarray(
        [float(c[index == band].sum()) for band in range(len(cuts) - 1)], dtype=np.float64
    )


def _deduplicate(cuts: list[float]) -> list[float]:
    """Drop repeated cut points, keeping order.

    A tied quantile is the norm on a column like `vehicle_age`, where a third of the book
    is at zero: two boundaries land on the same value and the band between them is empty.
    Dropping the duplicate is the honest outcome — the proposal returns fewer bands than
    asked for, which `method_params.n_bands` records, rather than an empty one that
    FR-MODEL-11 would fail anyway.
    """
    out: list[float] = []
    for cut in cuts:
        if not out or cut > out[-1]:
            out.append(float(cut))
    return out


def _labels(boundaries: list[float], *, closed: str) -> tuple[str, ...]:
    """Names a reader recognises, from the cut points.

    Whole-number boundaries on a left-closed banding get the actuarial form — `17-20`,
    `21-24`, `76+` — because that is how an age band is written and `02` §4.2's own example
    writes it that way. Anything else gets `lo-hi` with the boundary values as they are,
    where the upper end is exclusive.
    """
    integral = closed == "left" and all(float(b).is_integer() for b in boundaries)
    labels: list[str] = []
    for i in range(len(boundaries) - 1):
        low, high = boundaries[i], boundaries[i + 1]
        last = i == len(boundaries) - 2
        if integral:
            labels.append(f"{int(low)}+" if last else f"{int(low)}-{int(high) - 1}")
        else:
            labels.append(f"{low:g}+" if last else f"{low:g}-{high:g}")
    return tuple(labels)


def apply_banding(series: pl.Series, banding: Banding) -> pl.Series:
    """Map a numeric column onto its band labels (FR-MODEL-8).

    Every value gets a level or an error; nothing is dropped. Out-of-range values and nulls
    follow the policies the artifact declares, and where the policy is `error` the refusal
    names the offending values — the point of declaring the policy is that the silent case
    does not exist.
    """
    values = series.cast(pl.Float64)
    interior = np.asarray(banding.boundaries[1:-1], dtype=np.float64)
    first, last = banding.boundaries[0], banding.boundaries[-1]
    raw = values.to_numpy()
    present = ~np.isnan(raw)

    # The outermost bands are closed at both ends (see the module docstring), so a value is
    # out of range only when it falls strictly outside the boundaries — under either
    # convention. Without that, a banding derived from the observed range would declare its
    # own maximum out of range.
    below = present & (raw < first)
    above = present & (raw > last)

    side: Literal["left", "right"] = "right" if banding.closed == "left" else "left"
    index = np.searchsorted(interior, raw, side=side)
    index = np.clip(index, 0, len(banding.labels) - 1)
    labels = np.asarray(banding.labels, dtype=object)[index]

    out = np.asarray(labels, dtype=object)
    out = _resolve_edge(
        out, below, banding.below_range, banding, series, first, edge="below"
    )
    out = _resolve_edge(
        out, above, banding.above_range, banding, series, last, edge="above"
    )

    missing = ~present
    if missing.any():
        if banding.null_level is None:
            raise FactorResolutionError(
                f"banding {banding.slug!r} met {int(missing.sum())} null value(s) in "
                f"{banding.column!r} and declares no `null_level` (FR-MODEL-8). A missing "
                "value is not a band; give the banding a null level or filter the rows."
            )
        out[missing] = banding.null_level

    return pl.Series(name=series.name, values=out.tolist(), dtype=pl.String)


def _resolve_edge(
    out: np.ndarray,
    mask: np.ndarray,
    policy: BelowRangePolicy | AboveRangePolicy,
    banding: Banding,
    series: pl.Series,
    boundary: float,
    *,
    edge: str,
) -> np.ndarray:
    if not mask.any():
        return out
    if policy in (BelowRangePolicy.ERROR, AboveRangePolicy.ERROR):
        offending = series.cast(pl.Float64).to_numpy()[mask]
        raise FactorResolutionError(
            f"banding {banding.slug!r}: {int(mask.sum())} value(s) of "
            f"{banding.column!r} fall {edge} the banded range (boundary {boundary:g}, "
            f"e.g. {float(offending[0]):g}), and `{edge}_range` is `error` "
            "(FR-MODEL-8). The policy exists so this cannot pass silently."
        )
    if policy in (BelowRangePolicy.NULL_LEVEL, AboveRangePolicy.NULL_LEVEL):
        if banding.null_level is None:
            raise FactorResolutionError(
                f"banding {banding.slug!r} sends {edge}-range values to its null level and "
                "declares none. A policy pointing at a level that does not exist is not a "
                "policy."
            )
        out[mask] = banding.null_level
        return out
    out[mask] = banding.labels[0] if edge == "below" else banding.labels[-1]
    return out


def band_statistics(
    frame: pl.DataFrame,
    banding: Banding,
    *,
    exposure_column: str = "exposure_years",
    claim_count_column: str = "claim_count",
    claim_amount_column: str = "claim_amount_minor",
) -> tuple[OneWayRow, ...]:
    """Per-band exposure, claims, frequency, severity and burning cost (FR-MODEL-10).

    In **band order**, not the alphabetical order a group-by returns: `10-14` sorts before
    `5-9` as text, and a relativity chart with its bands shuffled is read as noise.
    """
    banded = frame.with_columns(apply_banding(frame[banding.column], banding).alias("_band"))
    summary = one_way(
        banded,
        column="_band",
        exposure_column=exposure_column,
        claim_count_column=claim_count_column,
        claim_amount_column=claim_amount_column,
    )
    by_level = {row.level: row for row in summary.rows}
    return tuple(by_level[level] for level in banding.levels if level in by_level)


def check_banding(
    frame: pl.DataFrame,
    banding: Banding,
    *,
    min_exposure: float | None = None,
    min_claims: float | None = None,
    exposure_column: str = "exposure_years",
    claim_count_column: str = "claim_count",
    fail_on_thin: bool | None = None,
) -> tuple[str, ...]:
    """FR-MODEL-11, against a specific Dataset Version.

    **An empty band always raises**, whatever the configuration says: a level no row reaches
    contributes no information and gets a coefficient anyway, estimated from nothing. Thin
    bands warn by default and fail when configured, which is the requirement's own wording.

    The thresholds default to the **banding's own** `minimums` (`banding.schema.json`), so
    the configured floor is a property of the artifact a reviewer can read rather than an
    argument at one call site. The keyword arguments override it, which is what a
    what-if evaluation needs.
    """
    minimums = banding.minimums
    min_exposure = float(minimums.min_exposure_per_band) if min_exposure is None else min_exposure
    min_claims = minimums.min_claims_per_band if min_claims is None else min_claims
    fail_on_thin = (minimums.on_violation == "fail") if fail_on_thin is None else fail_on_thin
    stats = band_statistics(
        frame,
        banding,
        exposure_column=exposure_column,
        claim_count_column=claim_count_column,
    )
    reached = {row.level for row in stats}
    empty = [level for level in banding.labels if level not in reached]
    if empty:
        raise BandingError(
            "BAND_EMPTY",
            f"banding {banding.slug!r} has band(s) {empty} that no row of this dataset "
            "version reaches (FR-MODEL-11). An empty band is still a level in the design "
            "matrix, and a coefficient estimated from no data is not an estimate.",
        )

    warnings: list[str] = []
    for row in stats:
        exposure = float(row.exposure_years)
        if min_exposure > 0 and exposure < min_exposure:
            warnings.append(
                f"band {row.level!r} holds {exposure:,.1f} exposure years, below the "
                f"minimum of {min_exposure:,.1f}."
            )
        if min_claims > 0 and row.claim_count < min_claims:
            warnings.append(
                f"band {row.level!r} holds {row.claim_count} claim(s), below the minimum "
                f"of {min_claims:,.0f}."
            )
    if warnings and fail_on_thin:
        raise BandingError(
            "BAND_BELOW_MIN_EXPOSURE",
            f"banding {banding.slug!r} has bands below the configured minimums and this "
            f"workspace fails rather than warns (FR-MODEL-11): {'; '.join(warnings)}",
        )
    return tuple(warnings)
