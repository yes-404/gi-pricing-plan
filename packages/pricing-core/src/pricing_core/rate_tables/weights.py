"""The exposure weight behind each cell of a rate table version.

03 FR-231, `RL-1361`, `RL-1418` T5.

A pure join: it takes a portfolio frame that `read_portfolio` has already checked, the
current version's key declarations and cells, and every artifact those keys pin, and
returns Σ `exposure_years` per cell. It takes no database (ADR-703): the platform loads
the Factors, Bandings and Groupings and passes them in.

Each key is resolved by exactly one branch (`RL-1361` item 2): `resolve_factors` for a
`factor_ref`, `apply_banding` for a `banding_ref`, and the same-named column otherwise.
The comparison with a cell's stored key string is made in the key's declared type, so a
cell stored as `"03"` takes the weight of a portfolio value `3`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

import polars as pl

from model_schema import Banding, Factor, Grouping
from model_schema.rating import RateTableKey, RateTableKeyType
from pricing_core.modelling import FactorResolutionError, resolve_factors
from pricing_core.modelling.bandings import apply_banding
from pricing_core.rate_tables.operations import Cells, KeyTuple

__all__ = ["PortfolioWeights", "WeightJoinError", "exposure_weights"]

_EXPOSURE = "exposure_years"
_CELL = "_cell"


class WeightJoinError(ValueError):
    """A portfolio that cannot weight this table; the platform maps it to `VALIDATION_FAILED`.

    The message names the key, the column or the ref, never a portfolio value. A
    `FactorResolutionError`'s message is carried as it is, with its count and example
    value (`RL-1361` item 3).
    """

    code = "VALIDATION_FAILED"


@dataclass(frozen=True, slots=True)
class PortfolioWeights:
    """Σ exposure per stored key tuple, and the two coverage figures of `RateTableDiff`.

    `weights` omits any cell whose Σ is 0. It is a `Weights` and is passed unchanged to
    the diff functions, so the aggregate mean and the per-cell weights come from one map.
    """

    weights: dict[KeyTuple, Decimal]
    portfolio_exposure: Decimal
    matched_exposure: Decimal


def _find_banding(key: RateTableKey, bandings: Mapping[UUID, Banding]) -> Banding:
    ref = key.banding_ref
    assert ref is not None
    for banding in bandings.values():
        if banding.slug == ref.slug and banding.version == ref.version:
            return banding
    raise WeightJoinError(f"key {key.name!r}: banding {ref} was not supplied")


def _needed_columns(
    keys: Sequence[RateTableKey],
    factors: Mapping[str, Sequence[Factor]],
    bandings: Mapping[UUID, Banding],
) -> set[str]:
    needed = {_EXPOSURE}
    for key in keys:
        if key.factor_ref is not None:
            for factor in factors.get(str(key.factor_ref), ()):
                needed.update(factor.source_columns)
        elif key.banding_ref is not None:
            needed.add(_find_banding(key, bandings).column)
        else:
            needed.add(key.name)
    return needed


def _resolved_series(
    key: RateTableKey,
    frame: pl.DataFrame,
    factors: Mapping[str, Sequence[Factor]],
    bandings: Mapping[UUID, Banding],
    groupings: Mapping[UUID, Grouping],
) -> pl.Series:
    """The portfolio's value for one key, by the one branch its binding selects."""
    try:
        if key.factor_ref is not None:
            chain = factors.get(str(key.factor_ref))
            if not chain:
                raise WeightJoinError(
                    f"key {key.name!r}: factor {key.factor_ref} was not supplied"
                )
            matrix = resolve_factors(frame, chain, bandings=bandings, groupings=groupings)
            return matrix.frame[matrix.terms[chain[0].slug]].cast(pl.String)
        if key.banding_ref is not None:
            banding = _find_banding(key, bandings)
            if banding.column not in frame.columns:
                raise WeightJoinError(
                    f"key {key.name!r}: banded column {banding.column!r} is absent "
                    "from the portfolio"
                )
            column = frame[banding.column]
            if not column.dtype.is_numeric():
                raise WeightJoinError(
                    f"key {key.name!r}: banded column {banding.column!r} is not numeric"
                )
            return apply_banding(column, banding)
    except FactorResolutionError as exc:
        raise WeightJoinError(str(exc)) from exc
    if key.name not in frame.columns:
        raise WeightJoinError(f"key {key.name!r}: portfolio column {key.name!r} is absent")
    return frame[key.name]


def _typed_portfolio(series: pl.Series, key_type: RateTableKeyType) -> pl.Series:
    """The portfolio's values in the key's declared type; a value of another type is null."""
    if key_type is RateTableKeyType.INT:
        if series.dtype.is_integer():
            return series.cast(pl.Int64)
        # A fractional value is not an integer key, so it matches nothing.
        number = pl.col("v")
        return (
            series.cast(pl.Float64, strict=False)
            .to_frame("v")
            .select(pl.when(number == number.floor()).then(number).cast(pl.Int64))
            .to_series()
        )
    if key_type is RateTableKeyType.BOOL:
        if series.dtype == pl.Boolean:
            return series
        if series.dtype in (pl.String, pl.Categorical, pl.Enum):
            lowered = series.cast(pl.String).str.to_lowercase()
            return lowered.replace_strict(
                {"true": True, "false": False}, default=None, return_dtype=pl.Boolean
            )
        return series.cast(pl.Boolean, strict=False)
    if key_type is RateTableKeyType.DATE:
        if series.dtype == pl.Date:
            return series
        if series.dtype == pl.Datetime:
            return series.dt.date()
        return series.cast(pl.String).str.to_date(strict=False)
    return series.cast(pl.String)


def _typed_cells(name: str, key_type: RateTableKeyType, stored: list[str]) -> pl.Series:
    """The stored key strings of every cell, parsed in the key's declared type."""
    try:
        if key_type is RateTableKeyType.INT:
            return pl.Series(name, [int(v) for v in stored], dtype=pl.Int64)
        if key_type is RateTableKeyType.BOOL:
            parsed = [v.casefold() for v in stored]
            if any(v not in ("true", "false") for v in parsed):
                raise ValueError
            return pl.Series(name, [v == "true" for v in parsed], dtype=pl.Boolean)
        if key_type is RateTableKeyType.DATE:
            return pl.Series(name, [date.fromisoformat(v) for v in stored], dtype=pl.Date)
    except ValueError as exc:
        raise WeightJoinError(
            f"key {name!r}: a stored cell value is not a valid {key_type.value}"
        ) from exc
    return pl.Series(name, stored, dtype=pl.String)


def exposure_weights(
    portfolio: pl.LazyFrame,
    keys: Sequence[RateTableKey],
    cells: Cells,
    *,
    factors: Mapping[str, Sequence[Factor]],
    bandings: Mapping[UUID, Banding],
    groupings: Mapping[UUID, Grouping],
) -> PortfolioWeights:
    """FR-231's exposure weight per cell of the current version (`RL-1418` T5)."""
    schema = portfolio.collect_schema()
    wanted = [c for c in _needed_columns(keys, factors, bandings) if c in schema]
    frame = portfolio.select(wanted).collect()

    key_columns = [f"k{i}" for i in range(len(keys))]
    resolved = [
        _typed_portfolio(
            _resolved_series(key, frame, factors, bandings, groupings), key.type
        ).alias(col)
        for key, col in zip(keys, key_columns, strict=True)
    ]
    exposure = frame[_EXPOSURE]
    portfolio_exposure = exposure.sum()
    left = pl.DataFrame(resolved).with_columns(exposure)

    cell_frame = pl.DataFrame(
        [
            _typed_cells(col, key.type, [row[key.name] for row in cells])
            for key, col in zip(keys, key_columns, strict=True)
        ]
        + [pl.Series(_CELL, range(len(cells)), dtype=pl.Int64)]
    )
    joined = left.join(cell_frame, on=key_columns, how="inner")
    if joined.height == 0:
        names = ", ".join(repr(key.name) for key in keys)
        raise WeightJoinError(f"no portfolio row maps to a cell of the table (keys {names})")

    sums = joined.group_by(_CELL).agg(pl.col(_EXPOSURE).sum()).sort(_CELL)
    weights: dict[KeyTuple, Decimal] = {}
    for index, total in zip(sums[_CELL].to_list(), sums[_EXPOSURE].to_list(), strict=True):
        if total != 0:
            weights[tuple(cells[index][key.name] for key in keys)] = total
    return PortfolioWeights(
        weights=weights,
        portfolio_exposure=Decimal(portfolio_exposure or 0),
        matched_exposure=Decimal(joined[_EXPOSURE].sum() or 0),
    )
