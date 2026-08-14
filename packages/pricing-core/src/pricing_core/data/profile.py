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
    "semantic_type_of",
]

DEFAULT_QUANTILES: Final[tuple[float, ...]] = (0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99)

#: FR-DATA-25 caps categorical detail at the top 20 levels. A high-cardinality column would
#: otherwise put its entire domain into a persisted artifact.
TOP_LEVELS: Final = 20

#: Quantiles are linearly interpolated in both profiling paths. Stated here because it is
#: a definition rather than an implementation detail: `nearest` and `linear` give different
#: p99s on the same column, and a Profile must not record which engine computed it.
QUANTILE_INTERPOLATION: Final = "linear"

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
    return semantic_type_of(
        series.name,
        series.dtype,
        distinct_count=int(series.drop_nulls().n_unique()),
        row_count=row_count,
    )


def semantic_type_of(
    column: str, dtype: pl.DataType | Any, *, distinct_count: int, row_count: int
) -> SemanticType:
    """The same rule, from statistics rather than a Series.

    `profile_parquet` computes its distinct count in SQL and never holds the column, so it
    cannot call the Series form. Sharing the rule is what stops the two profiling paths
    from disagreeing about what a column is — and a column that is `identifier` in one and
    `continuous` in the other would be banded by one screen and hidden by the next.
    """
    name = column.lower()

    if name.endswith(_MONEY_SUFFIX):
        return SemanticType.MONEY
    if dtype == pl.Boolean:
        return SemanticType.BOOLEAN
    if dtype in (pl.Date, pl.Datetime):
        return SemanticType.DATE

    distinct = distinct_count
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
                    f"p{int(q * 100)}": float(
                        casted.quantile(q, interpolation="linear") or 0.0
                    )
                    for q in DEFAULT_QUANTILES
                }

        top: tuple[tuple[str, int], ...] = ()
        if semantic in {SemanticType.CATEGORICAL, SemanticType.ORDINAL, SemanticType.BOOLEAN}:
            counts = (
                frame.group_by(name)
                .len()
                # Level name breaks the tie. Without it, forty groups of exactly 125 come
                # back in whatever order the engine grouped them, and the same dataset
                # profiled twice shows a different top-20 — which is indistinguishable
                # from the data having changed.
                .sort(["len", name], descending=[True, False])
                .head(TOP_LEVELS)
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
                distinct_count=int(series.drop_nulls().n_unique()),
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
        rows.append(
            _one_way_row(
                level=record[column],
                exposure=float(record.get("_exposure") or 0.0),
                claims=int(record.get("_claims") or 0),
                amount=int(record.get("_amount") or 0),
                confidence=confidence,
            )
        )
    return OneWaySummary(column=column, rows=tuple(rows))


def _identifier(name: str) -> str:
    """Quote a SQL identifier. Column names reach here from a user's file, so `"` in a
    header is not exotic — it is a Tuesday."""
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def profile_parquet(
    paths: Sequence[str],
    *,
    dataset_version_id: UUID,
    one_way_columns: Sequence[str] = (),
    exposure_column: str = "exposure_years",
    claim_count_column: str = "claim_count",
    claim_amount_column: str = "claim_amount_minor",
) -> Profile:
    """Profile parquet files with DuckDB (FR-DATA-27, NFR-DATA-3).

    Every statistic is computed **in SQL**; nothing but aggregates crosses back into
    Python. This is the difference between profiling a dataset version and loading one —
    an earlier build ran `SELECT *` and handed the frame to `profile_frame`, which peaked
    at 2.1 GB on a 1.1 GB payload and would have needed ~11 GB at the 10M-row scale
    NFR-DATA-3 is written against. Profiling is the one operation guaranteed to touch
    every row, so it is the one that must not hold them.

    The paths are supplied by the caller, which is how ADR-0001 survives — this function
    opens no object store and holds no credential.
    """
    import duckdb

    if not paths:
        raise ValueError("no parquet paths supplied")

    # Polars reads the footer alone, so the dtypes are free and — more importantly —
    # identical to the ones `profile_frame` would report. Deriving them from DuckDB's own
    # type names instead would make the same column read `VARCHAR` here and `String`
    # there, and a Profile should not record which code path produced it.
    schema = pl.read_parquet_schema(paths[0])

    connection = duckdb.connect(":memory:")
    try:
        files = ", ".join(f"'{path}'" for path in paths)
        connection.execute(f"CREATE VIEW src AS SELECT * FROM read_parquet([{files}])")
        counted = connection.execute("SELECT count(*) FROM src").fetchone()
        if counted is None:  # pragma: no cover — a scalar aggregate always returns a row
            raise ValueError("DuckDB returned no row for a count aggregate")
        row_count = int(counted[0])

        columns = [
            _profile_column(connection, name, dtype, row_count=row_count)
            for name, dtype in schema.items()
        ]
        one_ways = tuple(
            _one_way_sql(
                connection,
                column=column,
                exposure_column=exposure_column if exposure_column in schema else None,
                claim_count_column=claim_count_column if claim_count_column in schema else None,
                claim_amount_column=(
                    claim_amount_column if claim_amount_column in schema else None
                ),
            )
            for column in one_way_columns
            if column in schema
        )
    finally:
        connection.close()

    return Profile(
        id=uuid4(),
        dataset_version_id=dataset_version_id,
        computed_at=datetime.now(UTC),
        row_count=row_count,
        columns=tuple(columns),
        one_ways=one_ways,
        library_versions={"polars": pl.__version__, "duckdb": duckdb.__version__},
    )


def _profile_column(
    connection: Any, name: str, dtype: Any, *, row_count: int
) -> ColumnProfile:
    """One column's profile, from at most three aggregate queries."""
    quoted = _identifier(name)
    counts = connection.execute(
        f"SELECT count(*) FILTER (WHERE {quoted} IS NULL), count(DISTINCT {quoted}) FROM src"
    ).fetchone()
    if counts is None:  # pragma: no cover — a scalar aggregate always returns a row
        raise ValueError(f"DuckDB returned no row when counting {name!r}")
    null_count, distinct_count = int(counts[0]), int(counts[1])

    semantic = semantic_type_of(
        name, dtype, distinct_count=distinct_count, row_count=row_count
    )
    numeric = dtype.is_numeric() and semantic is not SemanticType.IDENTIFIER

    minimum = maximum = mean = std = None
    quantiles: dict[str, float] = {}
    if numeric and row_count:
        # Linear interpolation, matching `profile_frame`. Left to their defaults the two
        # engines disagree — Polars rounds to the nearest observation, DuckDB's
        # `quantile_disc` picks a different one — and FR-DATA-27 exists precisely so
        # there is one answer to "what is p99 of this column?".
        wanted = ", ".join(str(q) for q in DEFAULT_QUANTILES)
        row = connection.execute(
            f"SELECT min({quoted}), max({quoted}), avg({quoted}), stddev_samp({quoted}), "
            f"quantile_cont({quoted}, [{wanted}]) FROM src WHERE {quoted} IS NOT NULL"
        ).fetchone()
        if row is not None and row[0] is not None:
            minimum, maximum = float(row[0]), float(row[1])
            mean = float(row[2])
            std = float(row[3]) if row[3] is not None else 0.0
            quantiles = {
                f"p{int(q * 100)}": float(value or 0.0)
                for q, value in zip(DEFAULT_QUANTILES, row[4], strict=True)
            }

    top: tuple[tuple[str, int], ...] = ()
    if semantic in {SemanticType.CATEGORICAL, SemanticType.ORDINAL, SemanticType.BOOLEAN}:
        levels = connection.execute(
            f"SELECT {quoted}, count(*) AS n FROM src GROUP BY 1 "
            f"ORDER BY n DESC, {quoted} ASC LIMIT ?",
            [TOP_LEVELS],
        ).fetchall()
        top = tuple((str(level), int(count)) for level, count in levels)

    return ColumnProfile(
        name=name,
        dtype=str(dtype),
        semantic_type=semantic,
        row_count=row_count,
        null_count=null_count,
        null_rate=null_count / row_count if row_count else 0.0,
        distinct_count=distinct_count,
        minimum=minimum,
        maximum=maximum,
        mean=mean,
        std=std,
        quantiles=quantiles,
        top_levels=top,
    )


def _one_way_sql(
    connection: Any,
    *,
    column: str,
    exposure_column: str | None,
    claim_count_column: str | None,
    claim_amount_column: str | None,
    confidence: float = 0.95,
) -> OneWaySummary:
    """A one-way grouped in SQL. Only the levels come back, never the rows behind them."""
    quoted = _identifier(column)
    selects = [f"{quoted} AS level", "count(*) AS rows"]
    selects.append(
        f"sum(CAST({_identifier(exposure_column)} AS DOUBLE))" if exposure_column else "0.0"
    )
    selects.append(
        f"sum(CAST({_identifier(claim_count_column)} AS BIGINT))" if claim_count_column else "0"
    )
    selects.append(
        f"sum(CAST({_identifier(claim_amount_column)} AS BIGINT))"
        if claim_amount_column
        else "0"
    )
    grouped = connection.execute(
        f"SELECT {', '.join(selects)} FROM src GROUP BY 1 ORDER BY 1"
    ).fetchall()

    rows = [
        _one_way_row(
            level=level,
            exposure=float(exposure or 0.0),
            claims=int(claims or 0),
            amount=int(amount or 0),
            confidence=confidence,
        )
        for level, _rows, exposure, claims, amount in grouped
    ]
    return OneWaySummary(column=column, rows=tuple(rows))


def _one_way_row(
    *, level: Any, exposure: float, claims: int, amount: int, confidence: float
) -> OneWayRow:
    """The statistics of a one-way level, shared by both paths so they cannot drift."""
    # Every ratio is derived from the exposure the row *stores*, not from the raw sum.
    # Two engines summing the same column in different orders differ in the last bit, and
    # a reader who divides the published claim count by the published exposure should get
    # the published frequency back — not something that disagrees at the sixteenth digit.
    stored = Decimal(str(round(exposure, 6)))
    basis = float(stored)
    return OneWayRow(
        level=str(level),
        exposure_years=stored,
        claim_count=claims,
        claim_amount_minor=amount,
        frequency=claims / basis if basis > 0 else None,
        frequency_ci=(
            poisson_frequency_interval(claims, basis, confidence=confidence)
            if basis > 0
            else None
        ),
        severity_minor=amount / claims if claims else None,
        severity_ci=gamma_severity_interval(amount, claims, confidence=confidence),
        burning_cost_minor=amount / basis if basis > 0 else None,
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
