"""Profiling and profile comparison (`01` §3.4, §5.2, FR-60, FR-61, FR-62, FR-63).

Computed once after ingestion and read many times — by the distributional validation layer,
by `02`'s factor workbench, and by anyone asking what is in a dataset. FR-62 forbids
the UI recomputing one, because two answers to "what is the mean severity?" is one too many.

**Confidence intervals are exact, not normal approximations** (FR-61). A Poisson
interval from a normal approximation is wrong precisely where an actuary is most careful —
the low-count cells, where a young-driver band with nine claims can look either significant
or noise depending on the method. The exact interval costs a chi-square quantile.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Final, Literal
from uuid import UUID, uuid4

import polars as pl
from scipy import stats

from model_schema import (
    ColumnComparison,
    ColumnProfile,
    Histogram,
    LevelCount,
    OneWayRow,
    OneWaySummary,
    Profile,
    ProfileComparison,
    SemanticType,
)

__all__ = [
    "DEFAULT_QUANTILES",
    "HISTOGRAM_BINS",
    "MAX_ONE_WAY_LEVELS",
    "RATEABLE_TYPES",
    "candidate_rating_columns",
    "compare_profiles",
    "gamma_severity_interval",
    "infer_semantic_type",
    "one_way",
    "poisson_frequency_interval",
    "profile_frame",
    "profile_parquet",
    "psi_from_weights",
    "semantic_type_of",
]

DEFAULT_QUANTILES: Final[tuple[float, ...]] = (0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99)

#: FR-60 caps categorical detail at the top 20 levels. A high-cardinality column would
#: otherwise put its entire domain into a persisted artifact.
TOP_LEVELS: Final = 20

#: Bins in a column histogram (FR-65). Twenty is enough to show a mode and a tail on a
#: card-sized chart and few enough that an empty bin is visible rather than a hairline.
HISTOGRAM_BINS: Final = 20

#: Above this many levels a one-way stops being a summary. `01` §5.3 renders it as a chart
#: and a table; 200 bars is already unreadable, and the artifact would carry every level of
#: a column that is not really a rating factor.
MAX_ONE_WAY_LEVELS: Final = 200

#: The semantic types a one-way is meaningful for (FR-61, "candidate rating column").
#: A continuous column needs banding first, which is `02`'s factor workbench; an identifier
#: has one row per level; money is a measure rather than a factor.
RATEABLE_TYPES: Final[frozenset[SemanticType]] = frozenset(
    {SemanticType.CATEGORICAL, SemanticType.ORDINAL, SemanticType.BOOLEAN}
)

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
    """What a column *means*, which its dtype does not say (FR-60).

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


def candidate_rating_columns(
    columns: Sequence[ColumnProfile],
    *,
    exposure_column: str = "exposure_years",
    claim_count_column: str = "claim_count",
    claim_amount_column: str = "claim_amount_minor",
) -> tuple[str, ...]:
    """The columns a one-way is worth computing for (FR-61).

    "Per candidate rating column", decided from what the profiler has already inferred
    rather than from a list of names. A hard-coded list is wrong for every dataset that
    did not choose the same words: freMTPL2's rating factors are `area`, `veh_power`,
    `veh_brand`, `veh_gas` and `region`, and a list of English defaults matched exactly one
    of them — so twelve of thirteen columns had no one-way and the factor workbench would
    have had nothing to show.

    The measures are excluded because a one-way *of* claim count *by* claim count answers
    nothing, and continuous columns are excluded because they need banding first — which is
    `02`'s factor workbench, not this.
    """
    measures = {exposure_column, claim_count_column, claim_amount_column}
    return tuple(
        column.name
        for column in columns
        if column.semantic_type in RATEABLE_TYPES
        and column.name not in measures
        and column.distinct_count <= MAX_ONE_WAY_LEVELS
    )


def profile_frame(
    frame: pl.DataFrame,
    *,
    dataset_version_id: UUID,
    one_way_columns: Sequence[str] | Literal["auto"] = (),
    exposure_column: str = "exposure_years",
    claim_count_column: str = "claim_count",
    claim_amount_column: str = "claim_amount_minor",
    job_id: UUID | None = None,
) -> Profile:
    """Profile a frame (FR-60, FR-61).

    `one_way_columns="auto"` picks the candidate rating columns from the semantic types
    this function has just inferred — which is what FR-61 asks for, and what a caller
    naming columns by hand cannot do for a dataset it has not seen.

    The frame-based entry point exists so profiling is testable and notebook-runnable;
    `profile_parquet` is the DuckDB path FR-62 requires for real versions.

    `job_id` is recorded on the returned artifact (FR-6) when the caller has one; a
    frame profiled from a notebook or a test fixture has none.
    """
    columns: list[ColumnProfile] = []
    height = frame.height

    for name in frame.columns:
        series = frame.get_column(name)
        semantic = infer_semantic_type(series, row_count=height)
        null_count = int(series.null_count())

        numeric = series.dtype.is_numeric() and semantic is not SemanticType.IDENTIFIER
        # Never weight a column by itself, and tolerate the exposure column being absent —
        # the same rule the histogram below applies, shared here so both consumers agree.
        weighted_exposure_column = (
            exposure_column
            if exposure_column in frame.columns and exposure_column != name
            else None
        )
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

        top: tuple[LevelCount, ...] = ()
        if semantic in {SemanticType.CATEGORICAL, SemanticType.ORDINAL, SemanticType.BOOLEAN}:
            aggregates = [pl.len().alias("_n")]
            if weighted_exposure_column:
                aggregates.append(
                    pl.col(weighted_exposure_column).cast(pl.Float64).sum().alias("_e")
                )
            counts = (
                frame.group_by(name)
                .agg(aggregates)
                # Level name breaks the tie, and nulls sort last on both engines. Without
                # the tie-break, forty groups of exactly 125 come back in whatever order
                # the engine grouped them, and the same dataset profiled twice shows a
                # different top-20 — which is indistinguishable from the data having
                # changed. Without a pinned null order, a null level (a real category, not
                # the string "None") sorts first here and last in DuckDB on a tied count.
                .sort(["_n", name], descending=[True, False], nulls_last=True)
                .head(TOP_LEVELS)
            )
            top = tuple(
                LevelCount(
                    level=_as_level(row[name]),
                    count=int(row["_n"]),
                    exposure_years=(
                        _stored_exposure(float(row["_e"] or 0.0))
                        if weighted_exposure_column
                        else None
                    ),
                )
                for row in counts.iter_rows(named=True)
            )

        histogram = None
        if numeric and height and minimum is not None and maximum is not None:
            histogram = _histogram_frame(
                frame,
                name,
                minimum=minimum,
                maximum=maximum,
                exposure_column=weighted_exposure_column,
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
                histogram=histogram,
                top_levels=top,
            )
        )

    wanted = (
        candidate_rating_columns(
            columns,
            exposure_column=exposure_column,
            claim_count_column=claim_count_column,
            claim_amount_column=claim_amount_column,
        )
        if one_way_columns == "auto"
        else one_way_columns
    )
    one_ways = tuple(
        one_way(
            frame,
            column=column,
            exposure_column=exposure_column,
            claim_count_column=claim_count_column,
            claim_amount_column=claim_amount_column,
        )
        for column in wanted
        if column in frame.columns
    )

    return Profile(
        id=uuid4(),
        dataset_version_id=dataset_version_id,
        computed_at=datetime.now(UTC),
        job_id=job_id,
        row_count=height,
        columns=tuple(columns),
        one_ways=one_ways,
        weight_column=exposure_column,
        library_versions={"polars": pl.__version__},
    )


def poisson_frequency_interval(
    claim_count: int, exposure: float, *, confidence: float = 0.95
) -> tuple[float, float]:
    """Exact Poisson interval for a frequency (FR-61).

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
    """Interval for a mean severity under a Gamma assumption (FR-61).

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
    """Exposure, claims, frequency, severity and burning cost by level (FR-61)."""
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


def _as_level(value: Any) -> str | None:
    """A `top_levels` entry's level, without collapsing a null into the string `"None"`
    (FR-66).

    A SQL `NULL` / Polars null is a genuine category — a row where the column was not
    recorded — and stays `None` so it cannot be confused with a level someone actually
    wrote as the text "None". Anything else becomes its string form, exactly as every
    non-null level always has.
    """
    return None if value is None else str(value)


def _stored_exposure(value: float) -> Decimal:
    """Exposure as the exact decimal that is *stored*, not the raw float sum.

    Six decimal places. Two engines summing the same column in different orders differ in
    the last bit, and a published figure that depends on which engine read the file is what
    FR-62 exists to prevent. `_one_way_row` and the histogram share this so they cannot
    drift apart.
    """
    return Decimal(str(round(value, 6)))


def _histogram_edges(minimum: float, maximum: float) -> tuple[float, ...]:
    """Equal-width bin edges over the observed range (FR-65).

    Computed here rather than by Polars' `hist` or DuckDB's `histogram`, so both engines bin
    against the same numbers. A constant column is one bin of unit width: zero width would
    divide by zero, and twenty bins of one value is nineteen empty bars.
    """
    if not maximum > minimum:
        return (minimum, minimum + 1.0)
    width = (maximum - minimum) / HISTOGRAM_BINS
    return (*(minimum + width * i for i in range(HISTOGRAM_BINS)), maximum)


def _bin_index_expression(column: str, edges: tuple[float, ...]) -> pl.Expr:
    """Which bin a value falls in — the same arithmetic the SQL path uses.

    Half-open bins with a closed last one, expressed as a clamp rather than a comparison:
    the maximum computes to index `n` and is pulled back to `n - 1`, which is what "the last
    bin is closed" means in one operation.
    """
    bins = len(edges) - 1
    width = (edges[-1] - edges[0]) / bins
    return (
        ((pl.col(column).cast(pl.Float64) - edges[0]) / width)
        .floor()
        .clip(0, bins - 1)
        .cast(pl.Int64)
        .alias("_bin")
    )


def _histogram_frame(
    frame: pl.DataFrame,
    column: str,
    *,
    minimum: float,
    maximum: float,
    exposure_column: str | None,
) -> Histogram:
    edges = _histogram_edges(minimum, maximum)
    bins = len(edges) - 1

    aggregates = [pl.len().alias("_n")]
    if exposure_column:
        aggregates.append(pl.col(exposure_column).cast(pl.Float64).sum().alias("_e"))

    grouped = (
        frame.filter(pl.col(column).is_not_null())
        .with_columns(_bin_index_expression(column, edges))
        .group_by("_bin")
        .agg(aggregates)
    )

    # Seeded with zeroes and filled from the groups: an empty bin is a fact about the
    # distribution, and a group-by only returns the bins that have rows.
    counts = [0] * bins
    weights = [Decimal(0)] * bins
    for row in grouped.iter_rows(named=True):
        counts[row["_bin"]] = int(row["_n"])
        if exposure_column:
            weights[row["_bin"]] = _stored_exposure(float(row["_e"]))

    return Histogram(
        edges=edges,
        counts=tuple(counts),
        exposure=tuple(weights) if exposure_column else (),
    )


def profile_parquet(
    paths: Sequence[str],
    *,
    dataset_version_id: UUID,
    one_way_columns: Sequence[str] | Literal["auto"] = (),
    exposure_column: str = "exposure_years",
    claim_count_column: str = "claim_count",
    claim_amount_column: str = "claim_amount_minor",
    job_id: UUID | None = None,
) -> Profile:
    """Profile parquet files with DuckDB (FR-62, NFR-467).

    Every statistic is computed **in SQL**; nothing but aggregates crosses back into
    Python. This is the difference between profiling a dataset version and loading one —
    an earlier build ran `SELECT *` and handed the frame to `profile_frame`, which peaked
    at 2.1 GB on a 1.1 GB payload and would have needed ~11 GB at the 10M-row scale
    NFR-467 is written against. Profiling is the one operation guaranteed to touch
    every row, so it is the one that must not hold them.

    The paths are supplied by the caller, which is how ADR-703 survives — this function
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
            _profile_column(
                connection,
                name,
                dtype,
                row_count=row_count,
                exposure_column=exposure_column if exposure_column in schema else None,
            )
            for name, dtype in schema.items()
        ]
        wanted = (
            candidate_rating_columns(
                columns,
                exposure_column=exposure_column,
                claim_count_column=claim_count_column,
                claim_amount_column=claim_amount_column,
            )
            if one_way_columns == "auto"
            else one_way_columns
        )
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
            for column in wanted
            if column in schema
        )
    finally:
        connection.close()

    return Profile(
        id=uuid4(),
        dataset_version_id=dataset_version_id,
        computed_at=datetime.now(UTC),
        job_id=job_id,
        row_count=row_count,
        columns=tuple(columns),
        one_ways=one_ways,
        weight_column=exposure_column,
        library_versions={"polars": pl.__version__, "duckdb": duckdb.__version__},
    )


def _profile_column(
    connection: Any,
    name: str,
    dtype: Any,
    *,
    row_count: int,
    exposure_column: str | None = None,
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
        # `quantile_disc` picks a different one — and FR-62 exists precisely so
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

    histogram = None
    if numeric and row_count and minimum is not None and maximum is not None:
        edges = _histogram_edges(minimum, maximum)
        bins = len(edges) - 1
        width = (edges[-1] - edges[0]) / bins
        weighted = exposure_column is not None and exposure_column != name
        # The same arithmetic as `_bin_index_expression`, in SQL. `least(..., bins - 1)` is
        # the closed last bin; `greatest(0, ...)` guards a value that lands a hair below the
        # minimum after the subtraction.
        index = (
            f"greatest(0, least({bins - 1}, "
            f"floor(({quoted} - {edges[0]!r}) / {width!r})::BIGINT))"
        )
        weight = (
            f", sum({_identifier(exposure_column)})"
            if weighted and exposure_column is not None
            else ", NULL"
        )
        binned = connection.execute(
            f"SELECT {index} AS bin, count(*){weight} FROM src "
            f"WHERE {quoted} IS NOT NULL GROUP BY 1"
        ).fetchall()

        counts = [0] * bins
        weights = [Decimal(0)] * bins
        for bin_index, count, exposure_sum in binned:
            counts[int(bin_index)] = int(count)
            if weighted and exposure_sum is not None:
                weights[int(bin_index)] = _stored_exposure(float(exposure_sum))

        histogram = Histogram(
            edges=edges,
            counts=tuple(counts),
            exposure=tuple(weights) if weighted else (),
        )

    top: tuple[LevelCount, ...] = ()
    if semantic in {SemanticType.CATEGORICAL, SemanticType.ORDINAL, SemanticType.BOOLEAN}:
        # Same rule as the histogram's `weighted` above: never weight a column by itself,
        # tolerate the exposure column being absent. Recomputed rather than shared because
        # an ordinal column is numeric too and reaches the histogram branch above under its
        # own `weighted`, scoped to that block.
        weighted_levels = exposure_column is not None and exposure_column != name
        exposure_select = (
            f", sum(CAST({_identifier(exposure_column)} AS DOUBLE))"
            if weighted_levels and exposure_column is not None
            else ""
        )
        # `NULLS LAST` pinned explicitly: DuckDB already defaults to it, but Polars'
        # `.sort()` defaults the other way, and a level tied on count must land in the same
        # position on both engines (`test_the_two_profiling_paths_agree`).
        levels = connection.execute(
            f"SELECT {quoted}, count(*) AS n{exposure_select} FROM src GROUP BY 1 "
            f"ORDER BY n DESC, {quoted} ASC NULLS LAST LIMIT ?",
            [TOP_LEVELS],
        ).fetchall()
        top = tuple(
            LevelCount(
                level=_as_level(row[0]),
                count=int(row[1]),
                exposure_years=(
                    _stored_exposure(float(row[2] or 0.0)) if weighted_levels else None
                ),
            )
            for row in levels
        )

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
        histogram=histogram,
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
    stored = _stored_exposure(exposure)
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
        mean_severity=amount / claims if claims else None,
        severity_ci=gamma_severity_interval(amount, claims, confidence=confidence),
        mean_burning_cost=amount / basis if basis > 0 else None,
    )


def compare_profiles(
    current: Profile, reference: Profile, *, buckets: int = 10
) -> ProfileComparison:
    """PSI, mean shift, null-rate shift and level changes (FR-63).

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
        # `ColumnComparison.new_levels`/`vanished_levels` are non-null strings; a null
        # level is a real category but is not something that "newly appeared" or
        # "vanished" in the sense those two fields report, so it is excluded here rather
        # than compared against the literal text "None" (the old `str(level)` coercion).
        current_levels = {lc.level for lc in column.top_levels if lc.level is not None}
        reference_levels = {lc.level for lc in before.top_levels if lc.level is not None}

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
    distributional layer cheap enough to run on every validation (FR-54's intent). A
    null level is excluded, the same as `new_levels`/`vanished_levels` above — there is no
    string key to weight it under now that it is not coerced to the literal text "None".
    """
    return psi_from_weights(
        {lc.level: float(lc.count) for lc in current.top_levels if lc.level is not None},
        {lc.level: float(lc.count) for lc in reference.top_levels if lc.level is not None},
    )


def psi_from_weights(
    current: Mapping[str, float], reference: Mapping[str, float]
) -> float | None:
    """PSI between two level-weight maps — counts, or exposure (VR-DST-1, VR-DST-8).

    Public because the distributional validation layer needs exactly this and must not
    have its own copy: a `VR-DST-*` verdict and the comparison screen an actuary reads
    would then be able to disagree about the same two versions, which is the failure the
    module docstring promises against.

    Weights rather than counts, because VR-DST-8 asks for PSI on the **exposure** across a
    factor and not on row counts — a book that writes the same number of policies with
    half the exposure in young drivers has shifted, and counting rows would not see it.
    """
    current_total = sum(current.values())
    reference_total = sum(reference.values())
    if not current or not reference or not current_total or not reference_total:
        return None

    current_share = {level: value / current_total for level, value in current.items()}
    reference_share = {level: value / reference_total for level, value in reference.items()}

    import math

    psi = 0.0
    for level in current_share.keys() | reference_share.keys():
        actual = max(current_share.get(level, 0.0), _PSI_FLOOR)
        expected = max(reference_share.get(level, 0.0), _PSI_FLOOR)
        psi += (actual - expected) * math.log(actual / expected)
    return psi
