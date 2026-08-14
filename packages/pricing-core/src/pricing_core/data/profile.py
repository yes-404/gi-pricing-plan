"""Profiling and profile comparison (`01` §3.4, §5.2, FR-DATA-25..28).

Computed once after ingestion and read many times — by the distributional validation layer,
by `02`'s factor workbench, and by anyone asking what is in a dataset. FR-DATA-27 forbids
the UI recomputing one, because two answers to "what is the mean severity?" is one too many.

**Confidence intervals are exact, not normal approximations** (FR-DATA-26). A Poisson
interval from a normal approximation is wrong precisely where an actuary is most careful —
the low-count cells, where a young-driver band with nine claims can look either significant
or noise depending on the method. The exact interval costs a chi-square quantile.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Final
from uuid import UUID, uuid4

import polars as pl
from scipy import stats

from model_schema import (
    ColumnComparison,
    ColumnProfile,
    OneWayRow,
    OneWaySummary,
    Profile,
    ProfileComparison,
    SemanticType,
)

__all__ = [
    "DEFAULT_QUANTILES",
    "compare_profiles",
    "gamma_severity_interval",
    "infer_semantic_type",
    "one_way",
    "poisson_frequency_interval",
    "profile_frame",
    "profile_parquet",
]

DEFAULT_QUANTILES: Final[tuple[float, ...]] = (0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99)

#: FR-DATA-25 caps categorical detail at the top 20 levels. A high-cardinality column would
#: otherwise put its entire domain into a persisted artifact.
TOP_LEVELS: Final = 20

#: Above this share of distinct values a column looks like an identifier rather than a
#: category. Banding a policy id produces a chart with five million bars.
IDENTIFIER_UNIQUENESS: Final = 0.98

#: …but only once there are enough rows for uniqueness to mean anything. In a 40-row
#: extract every driver age is distinct, and calling that column an identifier would hide
#: the most important rating factor in motor from the factor workbench. Below this the
#: column is judged on its dtype alone.
IDENTIFIER_MIN_ROWS: Final = 200

_MONEY_SUFFIX: Final = "_minor"


def infer_semantic_type(series: pl.Series, *, row_count: int) -> SemanticType:
    """What a column *means*, which its dtype does not say (FR-DATA-25).

    `int32` is a dtype; policy id, vehicle group and driver age are three different things
    to do with one, and only the third can be banded meaningfully.
    """
    name = series.name.lower()
    dtype = series.dtype

    if name.endswith(_MONEY_SUFFIX):
        return SemanticType.MONEY
    if dtype == pl.Boolean:
        return SemanticType.BOOLEAN
    if dtype in (pl.Date, pl.Datetime):
        return SemanticType.DATE

    non_null = series.drop_nulls()
    distinct = int(non_null.n_unique())
    if (
        row_count >= IDENTIFIER_MIN_ROWS
        and distinct / max(row_count, 1) >= IDENTIFIER_UNIQUENESS
        and distinct > 20
    ):
        return SemanticType.IDENTIFIER
    if dtype.is_numeric():
        # Few distinct integer values is an ordinal scale (NCD years, vehicle group), not a
        # continuum — banding it into deciles would merge levels an actuary rates on.
        if not dtype.is_float() and distinct <= 20:
            return SemanticType.ORDINAL
        return SemanticType.CONTINUOUS
    return SemanticType.CATEGORICAL


def profile_frame(
    frame: pl.DataFrame,
    *,
    dataset_version_id: UUID,
    one_way_columns: Sequence[str] = (),
    exposure_column: str = "exposure_years",
    claim_count_column: str = "claim_count",
    claim_amount_column: str = "claim_amount_minor",
) -> Profile:
    """Profile a frame (FR-DATA-25, FR-DATA-26).

    The frame-based entry point exists so profiling is testable and notebook-runnable;
    `profile_parquet` is the DuckDB path FR-DATA-27 requires for real versions.
    """
    columns: list[ColumnProfile] = []
    height = frame.height

    for name in frame.columns:
        series = frame.get_column(name)
        semantic = infer_semantic_type(series, row_count=height)
        null_count = int(series.null_count())

        numeric = series.dtype.is_numeric() and semantic is not SemanticType.IDENTIFIER
        quantiles: dict[str, float] = {}
        minimum = maximum = mean = std = None
        if numeric and height:
            casted = series.cast(pl.Float64, strict=False).drop_nulls()
            if casted.len():
                # Polars types these as broad unions covering every dtype it can hold; the
                # cast above guarantees Float64, so narrowing here is a typing statement
                # rather than a conversion.
                minimum = float(casted.min())  # type: ignore[arg-type]
                maximum = float(casted.max())  # type: ignore[arg-type]
                mean = float(casted.mean())  # type: ignore[arg-type]
                std = float(casted.std()) if casted.len() > 1 else 0.0  # type: ignore[arg-type]
                quantiles = {
                    f"p{int(q * 100)}": float(casted.quantile(q) or 0.0)
                    for q in DEFAULT_QUANTILES
                }

        top: tuple[tuple[str, int], ...] = ()
        if semantic in {SemanticType.CATEGORICAL, SemanticType.ORDINAL, SemanticType.BOOLEAN}:
            counts = (
                frame.group_by(name).len().sort("len", descending=True).head(TOP_LEVELS)
            )
            top = tuple(
                (str(level), int(count)) for level, count in counts.iter_rows()
            )

        columns.append(
            ColumnProfile(
                name=name,
                dtype=str(series.dtype),
                semantic_type=semantic,
                row_count=height,
                null_count=null_count,
                null_rate=null_count / height if height else 0.0,
                distinct_count=int(series.n_unique()),
                minimum=minimum,
                maximum=maximum,
                mean=mean,
                std=std,
                quantiles=quantiles,
                top_levels=top,
            )
        )

    one_ways = tuple(
        one_way(
            frame,
            column=column,
            exposure_column=exposure_column,
            claim_count_column=claim_count_column,
            claim_amount_column=claim_amount_column,
        )
        for column in one_way_columns
        if column in frame.columns
    )

    return Profile(
        id=uuid4(),
        dataset_version_id=dataset_version_id,
        computed_at=datetime.now(UTC),
        row_count=height,
        columns=tuple(columns),
        one_ways=one_ways,
        library_versions={"polars": pl.__version__},
    )


def poisson_frequency_interval(
    claim_count: int, exposure: float, *, confidence: float = 0.95
) -> tuple[float, float]:
    """Exact Poisson interval for a frequency (FR-DATA-26).

    The Garwood interval, from chi-square quantiles. A normal approximation is wrong where
    it matters — with nine claims it can put the lower bound below zero, which is not a
    frequency any actuary will accept on a slide.
    """
    if exposure <= 0:
        return (0.0, 0.0)
    alpha = 1.0 - confidence
    lower = 0.0 if claim_count == 0 else stats.chi2.ppf(alpha / 2, 2 * claim_count) / 2
    upper = stats.chi2.ppf(1 - alpha / 2, 2 * claim_count + 2) / 2
    return (float(lower) / exposure, float(upper) / exposure)


def gamma_severity_interval(
    total_amount: float, claim_count: int, *, confidence: float = 0.95
) -> tuple[float, float] | None:
    """Interval for a mean severity under a Gamma assumption (FR-DATA-26).

    Modelled as a Gamma with shape `n` and mean `total/n`: the sum of `n` Gamma severities
    is Gamma with shape `n`, so the interval on the mean follows directly. `None` below two
    claims, because an interval from one observation is a number with no information in it,
    and showing one invites a decision it cannot support.
    """
    if claim_count < 2 or total_amount <= 0:
        return None
    alpha = 1.0 - confidence
    mean = total_amount / claim_count
    lower = stats.gamma.ppf(alpha / 2, a=claim_count, scale=mean / claim_count)
    upper = stats.gamma.ppf(1 - alpha / 2, a=claim_count, scale=mean / claim_count)
    return (float(lower), float(upper))


def one_way(
    frame: pl.DataFrame,
    *,
    column: str,
    exposure_column: str = "exposure_years",
    claim_count_column: str = "claim_count",
    claim_amount_column: str = "claim_amount_minor",
    confidence: float = 0.95,
) -> OneWaySummary:
    """Exposure, claims, frequency, severity and burning cost by level (FR-DATA-26)."""
    aggregations = [pl.len().alias("_rows")]
    if exposure_column in frame.columns:
        aggregations.append(pl.col(exposure_column).cast(pl.Float64).sum().alias("_exposure"))
    if claim_count_column in frame.columns:
        aggregations.append(pl.col(claim_count_column).cast(pl.Int64).sum().alias("_claims"))
    if claim_amount_column in frame.columns:
        aggregations.append(pl.col(claim_amount_column).cast(pl.Int64).sum().alias("_amount"))

    grouped = frame.group_by(column).agg(aggregations).sort(column)
    rows: list[OneWayRow] = []

    for record in grouped.iter_rows(named=True):
        exposure = float(record.get("_exposure") or 0.0)
        claims = int(record.get("_claims") or 0)
        amount = int(record.get("_amount") or 0)

        frequency = claims / exposure if exposure > 0 else None
        severity = amount / claims if claims else None
        rows.append(
            OneWayRow(
                level=str(record[column]),
                exposure_years=Decimal(str(round(exposure, 6))),
                claim_count=claims,
                claim_amount_minor=amount,
                frequency=frequency,
                frequency_ci=(
                    poisson_frequency_interval(claims, exposure, confidence=confidence)
                    if exposure > 0
                    else None
                ),
                severity_minor=severity,
                severity_ci=gamma_severity_interval(amount, claims, confidence=confidence),
                burning_cost_minor=amount / exposure if exposure > 0 else None,
            )
        )
    return OneWaySummary(column=column, rows=tuple(rows))


def profile_parquet(
    paths: Sequence[str],
    *,
    dataset_version_id: UUID,
    one_way_columns: Sequence[str] = (),
    **kwargs: Any,
) -> Profile:
    """Profile parquet files with DuckDB (FR-DATA-27).

    DuckDB reads the files directly rather than the caller loading them into memory: a
    dataset version is hundreds of millions of rows, and profiling is the one operation
    guaranteed to touch every one of them.

    The paths are supplied by the caller, which is how ADR-0001 survives — this function
    opens no object store and holds no credential.
    """
    import duckdb

    if not paths:
        raise ValueError("no parquet paths supplied")

    connection = duckdb.connect(":memory:")
    try:
        files = ", ".join(f"'{p}'" for p in paths)
        frame = connection.execute(f"SELECT * FROM read_parquet([{files}])").pl()
    finally:
        connection.close()

    profile = profile_frame(
        frame,
        dataset_version_id=dataset_version_id,
        one_way_columns=one_way_columns,
        **kwargs,
    )
    return profile.model_copy(
        update={"library_versions": {**profile.library_versions, "duckdb": duckdb.__version__}}
    )


def compare_profiles(
    current: Profile, reference: Profile, *, buckets: int = 10
) -> ProfileComparison:
    """PSI, mean shift, null-rate shift and level changes (FR-DATA-28).

    The same computation the distributional validation layer consumes, so a `VR-DST-*`
    verdict and the comparison screen an actuary is reading cannot disagree.
    """
    comparisons: list[ColumnComparison] = []

    for column in current.columns:
        before = reference.column(column.name)
        if before is None:
            continue

        mean_shift = (
            column.mean - before.mean
            if column.mean is not None and before.mean is not None
            else None
        )
        current_levels = {level for level, _ in column.top_levels}
        reference_levels = {level for level, _ in before.top_levels}

        comparisons.append(
            ColumnComparison(
                column=column.name,
                psi=_psi(column, before),
                mean_shift=mean_shift,
                null_rate_shift=column.null_rate - before.null_rate,
                new_levels=tuple(sorted(current_levels - reference_levels)),
                vanished_levels=tuple(sorted(reference_levels - current_levels)),
            )
        )

    ratio = (
        current.row_count / reference.row_count if reference.row_count else None
    )
    return ProfileComparison(
        current_version_id=current.dataset_version_id,
        reference_version_id=reference.dataset_version_id,
        columns=tuple(comparisons),
        row_count_ratio=ratio,
    )


#: Substituted for a zero share when computing PSI. A level present in one version and
#: absent in the other makes the ratio infinite, and an infinite PSI reports "everything
#: changed" for one rare code appearing — which is a warning nobody can act on.
_PSI_FLOOR: Final = 1e-6


def _psi(current: ColumnProfile, reference: ColumnProfile) -> float | None:
    """Population Stability Index over the profiled level shares.

    Computed from the top-level counts both profiles already hold, which is what makes the
    distributional layer cheap enough to run on every validation (FR-DATA-24's intent).
    """
    if not current.top_levels or not reference.top_levels:
        return None

    current_total = sum(count for _, count in current.top_levels)
    reference_total = sum(count for _, count in reference.top_levels)
    if not current_total or not reference_total:
        return None

    current_share = {level: count / current_total for level, count in current.top_levels}
    reference_share = {level: count / reference_total for level, count in reference.top_levels}

    import math

    psi = 0.0
    for level in current_share.keys() | reference_share.keys():
        actual = max(current_share.get(level, 0.0), _PSI_FLOOR)
        expected = max(reference_share.get(level, 0.0), _PSI_FLOOR)
        psi += (actual - expected) * math.log(actual / expected)
    return psi
