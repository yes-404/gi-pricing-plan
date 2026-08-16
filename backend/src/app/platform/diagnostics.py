"""Persisting and reading model diagnostics (`02` FR-MODEL-49, §4, §5.1).

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
from model_schema import Diagnostics

__all__ = ["load_diagnostics", "to_diagnostics"]


def to_diagnostics(row: DiagnosticsRow) -> Diagnostics:
    """The stored document, re-validated on the way out.

    Re-validated rather than trusted: the payload was written by a build that may not be
    this one, and a shape change that slipped past a migration should surface here as a
    loud failure rather than as a screen with missing numbers.
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
    """The diagnostics for one model, or a `404` that says which model (FR-MODEL-49)."""
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
