"""Deterministic ingestion helpers (`01` FR-29, FR-30, FR-32).

Three pure functions the platform needs before a Dataset Version can exist:

* **`normalise_columns`** — `snake_case`, deterministic, and **collision-detecting**.
  FR-30 is explicit that a collision is an ingestion error rather than a silent rename,
  because a silent rename means two source columns quietly become one and the second wins.
* **`infer_schema`** — the candidate schema FR-29 presents for confirmation.
* **`partition_rejects`** — the quarantine split FR-32 requires. Rows that cannot be
  parsed are *kept*, not dropped: an unparseable row is evidence about the feed, and
  discarding it is how a broken upstream export goes unnoticed for a quarter.

All three take frames and return values. The caller reads the file (ADR-703).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Final

import polars as pl

__all__ = [
    "ColumnMapping",
    "ColumnNameCollisionError",
    "InferredColumn",
    "InferredSchema",
    "RejectPartition",
    "infer_schema",
    "normalise_column_name",
    "normalise_columns",
    "partition_rejects",
]

#: Anything that is not a lowercase letter, digit or underscore becomes a separator.
_SEPARATOR: Final = re.compile(r"[^a-z0-9]+")
#: `PolicyID` → `policy_id`, `HTTPStatus` → `http_status`. Applied before lowercasing.
_CAMEL_BOUNDARY: Final = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

#: Sampled rather than scanned for candidate keys and cardinality: a candidate key on 5 M
#: rows is a `n_unique` over the whole column, which is affordable, but date-format sniffing
#: over every value is not and buys nothing beyond the first few hundred.
_FORMAT_SAMPLE_ROWS: Final = 500

_DATE_FORMATS: Final[tuple[str, ...]] = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%d %b %Y",
    "%Y-%m-%dT%H:%M:%S",
)


class ColumnNameCollisionError(ValueError):
    """Two source columns normalise to the same name (FR-30, `COLUMN_NAME_COLLISION`).

    Carries both originals, because the fix is a decision about the source: which column
    did the author mean, and what should the other be called?
    """

    def __init__(self, normalised: str, first: str, second: str) -> None:
        super().__init__(
            f"{first!r} and {second!r} both normalise to {normalised!r}. A collision is an "
            "ingestion error, not a silent rename (FR-30) — the second column would "
            "otherwise overwrite the first."
        )
        self.normalised = normalised
        self.first = first
        self.second = second


def normalise_column_name(name: str) -> str:
    """`snake_case` a single column name, deterministically.

    >>> normalise_column_name("Policy ID")
    'policy_id'
    >>> normalise_column_name("  vehicle-group (ABI)  ")
    'vehicle_group_abi'
    >>> normalise_column_name("GrossPremium£")
    'gross_premium'
    >>> normalise_column_name("2026_exposure")
    'col_2026_exposure'

    Accents are folded rather than stripped so `prämie` and `pramie` do not become
    different columns; a leading digit is prefixed because it is not a usable identifier
    downstream.
    """
    folded = unicodedata.normalize("NFKD", name)
    ascii_only = folded.encode("ascii", "ignore").decode("ascii")
    spaced = _CAMEL_BOUNDARY.sub(" ", ascii_only)
    lowered = spaced.lower()
    cleaned = _SEPARATOR.sub("_", lowered).strip("_")
    if not cleaned:
        raise ValueError(f"column name {name!r} normalises to nothing")
    if cleaned[0].isdigit():
        cleaned = f"col_{cleaned}"
    return cleaned


@dataclass(frozen=True)
class ColumnMapping:
    """Normalised name to the source name FR-30 keeps in the Data Dictionary."""

    normalised: dict[str, str] = field(default_factory=dict)

    @property
    def source_names(self) -> dict[str, str]:
        """`{normalised: source_name}` — what the Data Dictionary records."""
        return dict(self.normalised)

    @property
    def rename_map(self) -> dict[str, str]:
        """`{source_name: normalised}`, for `DataFrame.rename`.

        A property, like `source_names` beside it. One of the pair being a method was an
        inconsistency with no reason behind it, and it read as an attribute at every call
        site — `frame.rename(mapping.rename_map)` silently passes the *function*, which
        Polars accepts as a callable renamer and applies to nothing.
        """
        return {source: norm for norm, source in self.normalised.items()}


def normalise_columns(names: list[str]) -> ColumnMapping:
    """Normalise a set of column names, refusing collisions (FR-30)."""
    mapping: dict[str, str] = {}
    for name in names:
        normalised = normalise_column_name(name)
        if normalised in mapping:
            raise ColumnNameCollisionError(normalised, mapping[normalised], name)
        mapping[normalised] = name
    return ColumnMapping(normalised=mapping)


@dataclass(frozen=True)
class InferredColumn:
    """One column of the candidate schema FR-29 presents for confirmation."""

    name: str
    source_name: str
    dtype: str
    nullable: bool
    null_count: int
    distinct_count: int
    is_candidate_key: bool
    date_format: str | None = None
    sample: tuple[str, ...] = ()


@dataclass(frozen=True)
class InferredSchema:
    """The whole candidate schema.

    *Candidate*, not final: FR-29 requires it to be presented for confirmation and lets
    the user correct any inference before the version leaves `draft`. Inference is a
    starting point offered to an actuary, not a decision made on their behalf — getting a
    date format wrong silently is how a year of exposure lands in the wrong period.
    """

    columns: tuple[InferredColumn, ...]
    row_count: int

    @property
    def candidate_keys(self) -> tuple[str, ...]:
        return tuple(c.name for c in self.columns if c.is_candidate_key)


def infer_schema(frame: pl.DataFrame, *, sample_values: int = 3) -> InferredSchema:
    """Infer the candidate schema for a frame whose columns are already normalised.

    A column is a **candidate key** when it has no nulls and every value is distinct. On one
    column that is a candidate; the composite key a table actually uses is confirmed by the
    user, because guessing it from data means proposing whichever combination happens to be
    unique in this extract.
    """
    columns: list[InferredColumn] = []
    height = frame.height

    for name in frame.columns:
        series = frame.get_column(name)
        null_count = int(series.null_count())
        distinct = int(series.n_unique())
        sample = tuple(
            str(v) for v in series.drop_nulls().head(sample_values).to_list()
        )
        columns.append(
            InferredColumn(
                name=name,
                source_name=name,
                dtype=str(series.dtype),
                nullable=null_count > 0,
                null_count=null_count,
                distinct_count=distinct,
                # A single-row frame makes every column "unique"; requiring more than one
                # row stops the first upload of a sample file proposing nonsense keys.
                is_candidate_key=height > 1 and null_count == 0 and distinct == height,
                date_format=_sniff_date_format(series),
                sample=sample,
            )
        )
    return InferredSchema(columns=tuple(columns), row_count=height)


def _sniff_date_format(series: pl.Series) -> str | None:
    """The first format that parses every sampled value, or `None`.

    Ambiguity is real and not resolvable from data: `03/04/2026` is both `%d/%m/%Y` and
    `%m/%d/%Y`. The order of `_DATE_FORMATS` puts the ISO form first and the British form
    before the American one, and FR-29 makes the user confirm — which is the only
    honest resolution.
    """
    if series.dtype != pl.String:
        return None
    values = series.drop_nulls().head(_FORMAT_SAMPLE_ROWS)
    if values.is_empty():
        return None
    for candidate in _DATE_FORMATS:
        parsed = values.str.strptime(pl.Datetime, candidate, strict=False)
        if parsed.null_count() == 0:
            return candidate
    return None


@dataclass(frozen=True)
class RejectPartition:
    """The clean rows and the quarantined ones (FR-32)."""

    clean: pl.DataFrame
    rejected: pl.DataFrame

    @property
    def reject_rate(self) -> float:
        total = self.clean.height + self.rejected.height
        return 0.0 if total == 0 else self.rejected.height / total


#: The column added to quarantined rows saying why they were rejected. Underscore-prefixed
#: so it cannot collide with a normalised source column, which never starts with one.
REJECT_REASON_COLUMN: Final = "_reject_reason"


def partition_rejects(
    frame: pl.DataFrame, *, required_non_null: list[str] | None = None
) -> RejectPartition:
    """Split rows that cannot be used from rows that can (FR-32).

    A row is rejected when a **required** column is null — an unparseable date in a required
    date column arrives here as a null, having failed non-strict parsing upstream.

    Rejected rows are returned, never dropped. A version with rejects can still be
    validated; the `ingest.reject_rate` rule is what fails it above a threshold, and that
    is a decision for the rule set rather than for this function.
    """
    required = required_non_null or []
    if not required:
        return RejectPartition(clean=frame, rejected=frame.head(0).with_columns(
            pl.lit(None, dtype=pl.String).alias(REJECT_REASON_COLUMN)
        ))

    missing = [c for c in required if c not in frame.columns]
    if missing:
        raise ValueError(f"required columns absent from the frame: {missing}")

    reason = pl.lit(None, dtype=pl.String)
    for column in reversed(required):
        reason = (
            pl.when(pl.col(column).is_null())
            .then(pl.lit(f"{column} is null"))
            .otherwise(reason)
        )

    annotated = frame.with_columns(reason.alias(REJECT_REASON_COLUMN))
    rejected = annotated.filter(pl.col(REJECT_REASON_COLUMN).is_not_null())
    clean = annotated.filter(pl.col(REJECT_REASON_COLUMN).is_null()).drop(
        REJECT_REASON_COLUMN
    )
    return RejectPartition(clean=clean, rejected=rejected)
