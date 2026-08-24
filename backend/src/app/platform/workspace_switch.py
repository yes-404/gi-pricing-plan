"""Auditing a workspace switch into both chains (`07` FR-PLAT-63)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WorkspaceRow
from app.platform import audit
from model_schema import JobSource, Principal

__all__ = ["record_switch"]


async def record_switch(
    session: AsyncSession, *, principal: Principal, left: UUID | None, entered: UUID
) -> None:
    """Record the departure and the arrival, one event in each workspace's chain.

    `06` FR-GOV-24 chains audit events **per workspace**, so an event written only in the
    workspace entered is invisible from the workspace left — and "when did this principal
    stop acting here" is asked of the chain of the place they left. `left is None` is the
    first selection after login: there is no chain to leave, and one event is the whole
    record rather than half of one.

    The two events are written **in id order**. Each `audit.record` takes a per-workspace
    advisory lock inside this transaction, and two principals switching in opposite
    directions between the same pair would otherwise take the same two locks in opposite
    orders, which is a deadlock rather than a slow request.

    `entity_ref` is spelled `workspace:<slug>@1` and does not parse as an `ArtifactRef`:
    `workspace` is not in `ARTIFACT_TYPES`. That is the column's normal condition rather
    than a new breakage — 20 of the 39 spellings the backend writes already fail to parse,
    13 of them on a type outside the frozenset. Nothing parses this column, which is why.
    The measurement and the three options are `OQ-PLAT-14`; widening `ARTIFACT_TYPES` to
    admit this one string is the option that row exists to refuse.
    """
    entries: list[tuple[UUID, str]] = [(entered, "workspace.entered")]
    if left is not None and left != entered:
        entries.append((left, "workspace.left"))

    for workspace_id, action in sorted(entries):
        row = await session.get(WorkspaceRow, workspace_id)
        assert row is not None, f"no workspace row for {workspace_id}"
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=principal,
            source=JobSource.API,
            action=action,
            entity_ref=f"workspace:{row.slug}@1",
        )
