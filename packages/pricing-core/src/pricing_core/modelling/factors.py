"""Resolving Factors against a Dataset Version (`02` FR-MODEL-1, FR-MODEL-2).

A Factor is defined against a **Dataset** and resolved against a **version**, so this is
where "the column moved or changed type" is discovered. `02` FR-MODEL-2 says resolution
fails loudly, and the reason is that the alternative is a model fitted on a column that is
no longer the column the factor meant.

Only `identity` resolves today. The other seven types in FR-MODEL-1's closed set arrive
with the slices that implement them; a resolver that silently returned the raw column for
a `banding` would produce a fit nobody could tell from a correct one.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import polars as pl

from model_schema import Factor, FactorIntent, FactorType

__all__ = ["FactorMatrix", "FactorResolutionError", "resolve_factors"]


class FactorResolutionError(RuntimeError):
    """A factor could not be resolved against this version (`FACTOR_RESOLUTION_FAILED`)."""


@dataclass(frozen=True, slots=True)
class FactorMatrix:
    """The design columns a fit consumes, and what each one came from.

    `terms` maps a factor slug to the column it contributed, so a coefficient can be traced
    back to the factor that produced it rather than matched by name later.
    """

    frame: pl.DataFrame
    terms: dict[str, str]
    categorical: tuple[str, ...] = ()

    @property
    def columns(self) -> tuple[str, ...]:
        return tuple(self.terms.values())


def resolve_factors(frame: pl.DataFrame, factors: Sequence[Factor]) -> FactorMatrix:
    """Build the design columns for `factors` against this frame.

    Refuses rather than warns on:

    * a **prohibited** factor (FR-MODEL-5) — the refusal is the point of the flag;
    * a missing source column (FR-MODEL-2);
    * a factor type not yet implemented, named explicitly rather than skipped.
    """
    terms: dict[str, str] = {}
    categorical: list[str] = []

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
        if factor.type is not FactorType.IDENTITY:
            raise FactorResolutionError(
                f"factor {factor.slug!r} is of type {factor.type.value!r}, which this "
                "build does not resolve yet. Returning the raw column instead would "
                "produce a fit nobody could tell from a correct one."
            )

        column = factor.source_columns[0]
        terms[factor.slug] = column
        if frame.schema[column] in (pl.String, pl.Categorical, pl.Enum, pl.Boolean):
            categorical.append(column)

    return FactorMatrix(frame=frame, terms=terms, categorical=tuple(categorical))


def rateable(factors: Sequence[Factor]) -> tuple[Factor, ...]:
    """The factors a Rating Version may use (FR-MODEL-3).

    `control` factors are fitted and never rated on — year of account being the standard
    case. Selecting them here rather than in `03` keeps the intent with the definition.
    """
    return tuple(f for f in factors if f.intent is FactorIntent.RISK)
