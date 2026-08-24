"""Workspace rows (`07` FR-PLAT-62).

A Workspace is created by provisioning, which `06` owns and which does not exist yet. What
exists here is the idempotent ensure the seeds and the test suite need, modelled on
`rbac.seed_builtin_roles` for the same reason: the row must arrive with the workspace, and
there is no other moment that owns doing it.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WorkspaceRow

__all__ = ["ensure_workspace"]


async def ensure_workspace(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    slug: str | None = None,
    name: str | None = None,
) -> WorkspaceRow:
    """Create the workspace's row if it is absent, and return it either way.

    Idempotent, like `seed_builtin_roles`: called on a path that may run twice, and a second
    call must not raise. The derived slug and name match the migration's backfill so that a
    workspace created here and one backfilled there are indistinguishable.
    """
    existing = await session.get(WorkspaceRow, workspace_id)
    if existing is not None:
        return existing
    bare = workspace_id.hex
    row = WorkspaceRow(
        id=workspace_id,
        slug=slug or f"ws-{bare}",
        name=name or f"Workspace {bare[:8]}",
    )
    session.add(row)
    await session.flush()
    return row
