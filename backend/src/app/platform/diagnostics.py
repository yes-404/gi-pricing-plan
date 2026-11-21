"""Persisting and reading model diagnostics (`02` FR-170, §4, §5.1).

Diagnostics are written **in the transaction that marks the model fitted**, not after it.
`02` §4.8 makes `diagnostics_id` a condition of `status >= fitted`, so two transactions
would leave a window in which a `fitted` model has no evidence — and a window a reader can
observe is a state the system has, whatever the invariant says.

Reading is by model, because that is the only way anything asks for them: a diagnostics
artifact has no independent life, which is why it has no slug and no version of its own.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DiagnosticsRow
from app.errors import PlatformError
from model_schema import Diagnostics, FactorFinerLevels, FieldError

__all__ = ["load_diagnostics", "select_finer_level", "to_diagnostics"]


def select_finer_level(diagnostics: Diagnostics, level: str) -> Diagnostics:
    """The stored diagnostics with FR-109's finer level narrowed to `level` (`02` §5.1).

    A filter on what the fit stored, never a computation (FR-170): each chained Factor that has
    `level` keeps that level alone, and a Factor whose chain has no such level is left out.
    Train and holdout carry the same levels (FR-183), so they narrow alike.

    The levels the fit stored are every level of every chain on the model's groupings (a level
    whose column is absent is stored too, as its "not available" row), so a `level` none of them
    names is not a level of any chain: `422 VALIDATION_FAILED`, which lists the levels there
    are. A model fitted before the finer level was stored has nothing to select from and keeps
    its `None`, "not available", whatever `level` says: its chain may well have that level.
    """
    stored = diagnostics.finer_level_ae
    if stored is None:
        return diagnostics
    known = sorted({lv.name for entry in stored.holdout for lv in entry.levels})
    if level not in known:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Not a finer level of this model's groupings",
            422,
            "`level` must name a level of a grouping chain this model's Factors are fitted on "
            f"(FR-109); this model has {', '.join(known) if known else 'none'}.",
            errors=(
                FieldError(
                    field="level",
                    code="VALIDATION_FAILED",
                    message="not a finer level of a grouping chain on this model",
                ),
            ),
        )

    def narrowed(entries: tuple[FactorFinerLevels, ...]) -> tuple[FactorFinerLevels, ...]:
        kept = (
            (entry, tuple(lv for lv in entry.levels if lv.name == level)) for entry in entries
        )
        return tuple(
            entry.model_copy(update={"levels": levels}) for entry, levels in kept if levels
        )

    return diagnostics.model_copy(
        update={
            "finer_level_ae": stored.model_copy(
                update={"train": narrowed(stored.train), "holdout": narrowed(stored.holdout)}
            )
        }
    )


def to_diagnostics(row: DiagnosticsRow) -> Diagnostics:
    """The stored document, re-validated on the way out.

    Re-validated rather than trusted: the payload was written by a build that may not be
    this one, and a shape change that slipped past a migration should surface here as a
    loud failure rather than as a screen with missing numbers.

    A payload stored before FR-109's finer level was recorded (#1506 slice 5) has no
    `finer_level_ae` key, and reads with the field `None`: "not available", never an empty
    table. Nothing fills it in here, because nothing is computed on read (FR-170).
    """
    return Diagnostics.model_validate(
        {
            **row.payload,
            "id": str(row.id),
            "model_id": str(row.model_id),
            "computed_at": row.computed_at.isoformat(),
            "job_id": str(row.job_id) if row.job_id else None,
        }
    )


async def load_diagnostics(
    session: AsyncSession, *, workspace_id: UUID, model_id: UUID
) -> Diagnostics:
    """The diagnostics for one model, or a `404` that says which model (FR-170)."""
    row = (
        await session.execute(
            select(DiagnosticsRow).where(
                DiagnosticsRow.model_id == model_id,
                DiagnosticsRow.workspace_id == workspace_id,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "No diagnostics for this model",
            404,
            f"Model {model_id} has no diagnostics. A model at `fitted` or beyond always "
            "has them (`02` §4.8); a `draft` has not been fitted yet.",
        )
    return to_diagnostics(row)
