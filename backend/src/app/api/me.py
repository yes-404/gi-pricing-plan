"""`GET /api/v1/me` — who am I, and what may I do (`06` §5.1, FR-GOV-2).

> The frontend hides what a user cannot do; it never *enforces* it.

This is what it hides *by*. The permissions returned are computed by the same function the
enforcement uses, so the UI cannot offer a control the backend will refuse — a second
implementation of "what may this principal do" would drift, and the drift is only visible
to a user who clicks the button.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.api.deps import Caller, require_caller
from app.api.responses import problems
from app.db.models import (
    RoleAssignmentRow,
    RoleRow,
    WorkspaceMemberRow,
    WorkspaceRow,
)
from app.db.session import Database
from app.platform import rbac
from model_schema import ActorKind, Permission

__all__ = ["router"]

router = APIRouter(tags=["governance"])

CallerDep = Annotated[Caller, Depends(require_caller)]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


class RoleAssignmentView(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: str
    scope_type: str
    scope_id: str | None = None
    break_glass: bool = False
    expires_at: str | None = None


class WorkspaceMembership(BaseModel):
    """One workspace this principal may act in, named (FR-PLAT-62, FR-PLAT-63)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workspace_id: str
    slug: str
    name: str


class Me(BaseModel):
    """The current principal, its roles, and its effective permissions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    principal_kind: ActorKind
    principal_id: str
    display: str | None = None
    workspace_id: str
    roles: tuple[RoleAssignmentView, ...] = ()
    permissions: tuple[Permission, ...] = Field(
        default=(),
        description="Workspace-wide effective permissions. Scoped assignments appear under "
        "`roles`; a permission held only on one artifact is not listed here, because a "
        "control enabled by it would be wrong on every other artifact.",
    )
    workspaces: tuple[WorkspaceMembership, ...] = Field(
        default=(),
        description="Every workspace this principal is a member of, each named. A principal "
        "with more than one names its choice in the `Workspace-Id` header (FR-PLAT-65); this "
        "is the list that choice is made from.",
    )


@router.get(
    "/me",
    summary="Current principal, roles and effective permissions",
    responses=problems(401, 403),
)
async def get_me(caller: CallerDep, database: DatabaseDep) -> Me:
    async with database.session() as session:
        permissions = await rbac.effective_permissions(
            session,
            workspace_id=caller.workspace_id,
            principal=caller.principal,
        )
        rows = (
            await session.execute(
                select(RoleAssignmentRow, RoleRow)
                .join(RoleRow, RoleRow.id == RoleAssignmentRow.role_id)
                .where(
                    RoleAssignmentRow.workspace_id == caller.workspace_id,
                    RoleAssignmentRow.principal_id == caller.principal.id,
                    RoleAssignmentRow.revoked_at.is_(None),
                )
            )
        ).all()

        # A Service Account has no `workspace_members` row — its workspace comes from the
        # account itself — so this list is empty for one. That is correct rather than a
        # gap: FR-PLAT-65 says a Service Account never sends the header, because it has
        # exactly one workspace by construction and nothing to choose between.
        memberships = (
            (
                await session.execute(
                    select(WorkspaceRow)
                    .join(
                        WorkspaceMemberRow,
                        WorkspaceMemberRow.workspace_id == WorkspaceRow.id,
                    )
                    .where(WorkspaceMemberRow.user_id == caller.principal.id)
                    .order_by(WorkspaceRow.name)
                )
            )
            .scalars()
            .all()
        )

    return Me(
        principal_kind=caller.principal.kind,
        principal_id=str(caller.principal.id),
        display=caller.principal.display,
        workspace_id=str(caller.workspace_id),
        roles=tuple(
            RoleAssignmentView(
                role=role.slug,
                scope_type=assignment.scope_type,
                scope_id=str(assignment.scope_id) if assignment.scope_id else None,
                break_glass=assignment.break_glass,
                expires_at=(assignment.expires_at.isoformat() if assignment.expires_at else None),
            )
            for assignment, role in rows
        ),
        permissions=tuple(sorted(permissions)),
        workspaces=tuple(
            WorkspaceMembership(workspace_id=str(w.id), slug=w.slug, name=w.name)
            for w in memberships
        ),
    )
