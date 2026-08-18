"""Resolving Factors against a Dataset Version (`02` FR-MODEL-1, FR-MODEL-2).

A Factor is defined against a **Dataset** and resolved against a **version**, so this is
where "the column moved or changed type" is discovered. `02` FR-MODEL-2 says resolution
fails loudly, and the reason is that the alternative is a model fitted on a column that is
no longer the column the factor meant.

Three of FR-MODEL-1's eight types resolve today: `identity`, `banding` and `grouping`. The
other five arrive with the slices that implement them; a resolver that silently returned
the raw column for a `spline` would produce a fit nobody could tell from a correct one.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from uuid import UUID

import polars as pl

from model_schema import Banding, Factor, FactorIntent, FactorType, Grouping
from pricing_core.modelling.bandings import apply_banding
from pricing_core.modelling.errors import FactorResolutionError
from pricing_core.modelling.groupings import apply_grouping

__all__ = ["FactorMatrix", "FactorResolutionError", "rateable", "resolve_factors"]


@dataclass(frozen=True, slots=True)
class FactorMatrix:
    """The design columns a fit consumes, and what each one came from.

    `terms` maps a factor slug to the column it contributed, so a coefficient can be traced
    back to the factor that produced it rather than matched by name later.

    `frame` is the caller's frame **plus** any column a transformation produced, so a
    banded factor's levels are groupable — the relativity table weights them by exposure,
    and the pre-banding column cannot answer that.
    """

    frame: pl.DataFrame
    terms: dict[str, str]
    categorical: tuple[str, ...] = ()

    @property
    def columns(self) -> tuple[str, ...]:
        return tuple(self.terms.values())


def resolve_factors(
    frame: pl.DataFrame,
    factors: Sequence[Factor],
    *,
    bandings: Mapping[UUID, Banding] | None = None,
    groupings: Mapping[UUID, Grouping] | None = None,
) -> FactorMatrix:
    """Build the design columns for `factors` against this frame.

    `bandings` and `groupings` are the artifacts the factors pin, passed in by id for the
    same reason `fit_glm` takes its factors explicitly: resolving an id needs a database,
    which ADR-0001 forbids this package. A factor whose artifact is missing from the map is
    a refusal, not a fallback to the raw column.

    Refuses rather than warns on:

    * a **prohibited** factor (FR-MODEL-5) — the refusal is the point of the flag;
    * a missing source column (FR-MODEL-2);
    * a banding or grouping whose artifact was not supplied, or which describes a different
      column from the one the factor sources;
    * a factor type not yet implemented, named explicitly rather than skipped.
    """
    bandings = bandings or {}
    groupings = groupings or {}
    produced: dict[str, pl.Series] = {}
    terms: dict[str, str] = {}
    categorical: list[str] = []

    by_id = {factor.id: factor for factor in factors}
    #: Every factor named as an operand of some interaction in this call. Such a factor is
    #: resolved — the cross needs its levels — but contributes **no term of its own**
    #: (FR-MODEL-91). The cross is a *combined* factor spanning every cell, so its operands'
    #: main effects are collinear with it; designing on both is a rank deficiency dressed up
    #: as a richer model. A caller wanting `age` on its own asks for a model without the
    #: cross, which is a different Model Spec and a comparison between the two.
    operand_ids = {
        operand
        for factor in factors
        if factor.type is FactorType.INTERACTION
        for operand in factor.operand_factor_ids
    }
    resolved: dict[UUID, pl.Series] = {}

    for factor in factors:
        if factor.prohibited:
            raise FactorResolutionError(
                f"factor {factor.slug!r} is prohibited ({factor.prohibited_reason}). "
                "FR-MODEL-5: a prohibited factor cannot enter a Model Spec."
            )
        missing = [c for c in factor.source_columns if c not in frame.columns]
        if missing:
            raise FactorResolutionError(
                f"factor {factor.slug!r} needs {missing}, which this dataset version does "
                "not have (FR-MODEL-2). A factor is defined against a Dataset and resolved "
                "against a version; this is that resolution failing."
            )

        # Interactions are resolved in a second pass: an operand may appear anywhere in the
        # sequence, or after the factor that crosses it, and a resolution that depended on
        # the caller's ordering would be a fit that depended on it.
        if factor.type is FactorType.INTERACTION:
            continue

        source = factor.source_columns[0]
        if factor.type is FactorType.IDENTITY:
            series = frame[source]
        elif factor.type is FactorType.BANDING:
            banding = _banding(bandings, factor)
            _column_matches(banding.column, source, factor, kind="banding")
            series = apply_banding(frame[source], banding)
        elif factor.type is FactorType.GROUPING:
            grouping = _grouping(groupings, factor)
            _column_matches(grouping.column, source, factor, kind="grouping")
            series = apply_grouping(frame[source], grouping)
        else:
            raise FactorResolutionError(
                f"factor {factor.slug!r} is of type {factor.type.value!r}, which this "
                "build does not resolve yet. Returning the raw column instead would "
                "produce a fit nobody could tell from a correct one."
            )

        # A transformed factor contributes a **new** column under the factor's own slug,
        # never the source column: two bandings of `driver_age` are two factors, and both
        # writing back to `driver_age` would leave the second silently overwriting the
        # first in the design matrix.
        column = source if factor.type is FactorType.IDENTITY else f"{factor.slug}__resolved"
        if factor.type is not FactorType.IDENTITY:
            produced[column] = series.alias(column)
        resolved[factor.id] = series
        if factor.id in operand_ids:
            # Resolved for the cross that needs it, and deliberately not a term. See
            # `operand_ids` above.
            continue
        terms[factor.slug] = column
        if series.dtype in (pl.String, pl.Categorical, pl.Enum, pl.Boolean):
            categorical.append(column)

    for factor in factors:
        if factor.type is not FactorType.INTERACTION:
            continue
        column = f"{factor.slug}__resolved"
        series = _cross(factor, by_id, resolved)
        produced[column] = series.alias(column)
        terms[factor.slug] = column
        categorical.append(column)

    out = frame.with_columns(list(produced.values())) if produced else frame
    return FactorMatrix(frame=out, terms=terms, categorical=tuple(categorical))


#: What separates two operands' levels in a crossed level label. A pipe with spaces rather
#: than an `x`: band labels contain hyphens and digits and group labels can contain almost
#: anything, and a separator that could occur *inside* a level makes the cross ambiguous to
#: read back — which the rate table, the relativity table and the model document all do.
CROSS_SEPARATOR = " | "


def _cross(
    factor: Factor, by_id: Mapping[UUID, Factor], resolved: Mapping[UUID, pl.Series]
) -> pl.Series:
    """One interaction's design column: its operands' levels, crossed (FR-MODEL-91).

    Only **observed** combinations become levels, which is what string concatenation gives
    for free. A full Cartesian product would put a coefficient on cells with no exposure —
    and on any real cross most cells have none, so that is the ordinary case rather than a
    corner.
    """
    parts: list[pl.Series] = []
    for operand_id in factor.operand_factor_ids:
        operand = by_id.get(operand_id)
        if operand is None:
            raise FactorResolutionError(
                f"factor {factor.slug!r} crosses factor {operand_id}, which was not "
                "supplied. Resolving the cross without one of its sides would produce the "
                "other side alone, under this factor's name."
            )
        if operand.type is FactorType.INTERACTION:
            raise FactorResolutionError(
                f"factor {factor.slug!r} crosses {operand.slug!r}, which is itself an "
                "interaction. Declare a three-way interaction as one factor over three "
                "operands: nesting gives two names for one design column."
            )
        series = resolved[operand_id]
        if series.dtype not in (pl.String, pl.Categorical, pl.Enum, pl.Boolean):
            raise FactorResolutionError(
                f"factor {factor.slug!r} crosses {operand.slug!r}, which resolves to "
                f"{series.dtype} rather than to levels. Crossing a continuous factor is a "
                "varying slope, and a rate table has no cell for one — band or group it "
                "first, then cross the result (OQ-MODEL-12)."
            )
        parts.append(series.cast(pl.String))

    crossed = parts[0]
    for part in parts[1:]:
        crossed = crossed + CROSS_SEPARATOR + part
    return crossed


def _banding(available: Mapping[UUID, Banding], factor: Factor) -> Banding:
    """The pinned Banding, or a refusal naming what is missing.

    `Factor` already refuses a `banding` type with no `banding_id`, so reaching here with
    `None` is impossible — but the map can still be short of it, which is the ordinary case
    of a caller that loaded the factors and forgot the transformations.
    """
    if factor.banding_id is None or factor.banding_id not in available:
        raise FactorResolutionError(
            f"factor {factor.slug!r} is a banding and its banding ({factor.banding_id}) "
            f"was not supplied. Resolving it as the raw {factor.source_columns[0]!r} would "
            "be a different model wearing this one's name."
        )
    return available[factor.banding_id]


def _grouping(available: Mapping[UUID, Grouping], factor: Factor) -> Grouping:
    if factor.grouping_id is None or factor.grouping_id not in available:
        raise FactorResolutionError(
            f"factor {factor.slug!r} is a grouping and its grouping "
            f"({factor.grouping_id}) was not supplied. Resolving it as the raw "
            f"{factor.source_columns[0]!r} would be a different model wearing this one's "
            "name."
        )
    return available[factor.grouping_id]


def _column_matches(declared: str, source: str, factor: Factor, *, kind: str) -> None:
    if declared != source:
        raise FactorResolutionError(
            f"factor {factor.slug!r} sources {source!r} and pins a {kind} of "
            f"{declared!r}. The two must be the same column — a banding of driver age "
            "applied to vehicle age produces bands, a fit, and nonsense."
        )


def rateable(factors: Sequence[Factor]) -> tuple[Factor, ...]:
    """The factors a Rating Version may use (FR-MODEL-3).

    `control` factors are fitted and never rated on — year of account being the standard
    case. Selecting them here rather than in `03` keeps the intent with the definition.
    """
    return tuple(f for f in factors if f.intent is FactorIntent.RISK)
