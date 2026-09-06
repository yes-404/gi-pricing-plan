"""Workspace rows (`07` FR-395).

A Workspace is created by provisioning, which `06` owns and which does not exist yet. What
exists here is the idempotent ensure the seeds and the test suite need, modelled on
`rbac.seed_builtin_roles` for the same reason: the row must arrive with the workspace, and
there is no other moment that owns doing it.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserRow, WorkspaceMemberRow, WorkspaceRow

__all__ = ["ensure_member", "ensure_workspace"]


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


async def ensure_member(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    user_id: UUID,
    issuer: str,
    subject: str,
    email: str | None = None,
    display_name: str | None = None,
) -> UserRow:
    """Make an OIDC identity a member of a workspace, as a given principal (FR-398).

    Two rows, and each is load-bearing for a different reason:

    * the `users` row **with `id=user_id`**, because `authenticate_bearer` returns
      `UserRow.id` as the principal and a caller's role assignments are written against the
      principal id it already uses -- a defaulted id yields a member of the workspace who
      may do nothing in it;
    * the `workspace_members` row, because `FR-390` grants no access by default and
      `authenticate_bearer` reads workspaces from that table alone.

    **The workspace must already exist**: `workspace_members.workspace_id` is a foreign key
    to `workspaces.id`, so call `ensure_workspace` first. It is not called from here because
    the caller owns the workspace's name, and `ensure_workspace` returns an existing row
    untouched -- naming it afterwards silently does nothing.

    Idempotent, like `ensure_workspace` and `seed_builtin_roles`: a seed is re-run against an
    existing database routinely, and both `uq_workspace_members_user_workspace` and
    `uq_users_issuer_subject` make a second blind insert an error rather than a no-op.
    """
    user = await session.get(UserRow, user_id)
    if user is None:
        user = UserRow(id=user_id, issuer=issuer, subject=subject)
        session.add(user)
    # Only overwrite what the caller actually supplied: a re-run passing no email must not
    # blank one an earlier run set.
    if email is not None:
        user.email = email
    if display_name is not None:
        user.display_name = display_name

    existing = (
        await session.execute(
            select(WorkspaceMemberRow).where(
                WorkspaceMemberRow.user_id == user_id,
                WorkspaceMemberRow.workspace_id == workspace_id,
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        session.add(WorkspaceMemberRow(user_id=user_id, workspace_id=workspace_id))

    await session.flush()
    return user
