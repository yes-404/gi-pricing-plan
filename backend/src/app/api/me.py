"""`GET /api/v1/me` — who am I, and what may I do (`06` §5.1, FR-GOV-2).

> The frontend hides what a user cannot do; it never *enforces* it.

This is what it hides *by*. The permissions returned are computed by the same function the
enforcement uses, so the UI cannot offer a control the backend will refuse — a second
implementation of "what may this principal do" would drift, and the drift is only visible
to a user who clicks the button.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.api.deps import (
    WORKSPACE_ID_DESCRIPTION,
    Caller,
    IdentityDep,
    require_caller,
)
from app.api.responses import problems
from app.db.models import (
    RoleAssignmentRow,
    RoleRow,
    WorkspaceMemberRow,
    WorkspaceRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import rbac, workspace_switch
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


class SwitchWorkspaceRequest(BaseModel):
    """The workspace a principal chooses to act in (FR-PLAT-63's fourth obligation)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workspace_id: UUID


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
            # The same set the enforcement uses (Ruling 38). `effective_permissions` is
            # deliberately one computation for both the UI and the gate — omitting the
            # credential's own grants here would have `/me` under-report what its caller
            # may actually do, which is the mirror of the control-then-refused defect the
            # function's docstring exists to prevent.
            credential_permissions=caller.permissions,
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
                expires_at=(
                    assignment.expires_at.isoformat() if assignment.expires_at else None
                ),
            )
            for assignment, role in rows
        ),
        permissions=tuple(sorted(permissions)),
        workspaces=tuple(
            WorkspaceMembership(workspace_id=str(w.id), slug=w.slug, name=w.name)
            for w in memberships
        ),
    )


@router.get(
    "/me/workspaces",
    summary="The workspaces this principal may act in",
    responses=problems(401),
)
async def list_workspaces(
    identity: IdentityDep, database: DatabaseDep
) -> tuple[WorkspaceMembership, ...]:
    # The same join the `/me` memberships query runs (above), keyed on
    # identity.principal.id and ordered by name — but deliberately NOT scoped: this is the
    # list a first selection is made from, and there is no selection yet (FR-PLAT-63's
    # second amendment, PR #237). A Service Account has no `workspace_members` row, so the
    # list is empty for one — the designed state, not an error (see above).
    async with database.session() as session:
        rows = (
            (
                await session.execute(
                    select(WorkspaceRow)
                    .join(
                        WorkspaceMemberRow,
                        WorkspaceMemberRow.workspace_id == WorkspaceRow.id,
                    )
                    .where(WorkspaceMemberRow.user_id == identity.principal.id)
                    .order_by(WorkspaceRow.name)
                )
            )
            .scalars()
            .all()
        )
    return tuple(
        WorkspaceMembership(workspace_id=str(w.id), slug=w.slug, name=w.name)
        for w in rows
    )


@router.post(
    "/me/workspace",
    summary="Choose the workspace to act in",
    responses=problems(401, 403, 422),
)
async def switch_workspace(
    body: SwitchWorkspaceRequest,
    identity: IdentityDep,
    database: DatabaseDep,
    workspace_id: Annotated[
        str | None, Header(alias="Workspace-Id", description=WORKSPACE_ID_DESCRIPTION)
    ] = None,
) -> WorkspaceMembership:
    """A switch is a human act, and it is audited into both chains (OQ-PLAT-12).

    The absent header is the first selection after login: there is no chain to leave, and
    `record_switch` takes `left=None` for it (FR-PLAT-63's fourth obligation). A malformed
    header is a typed platform refusal, never a bare `422` — the header parses as `str`
    then `UUID`, mirroring `deps.py`'s handling of the same header.
    """
    left: UUID | None = None
    if workspace_id is not None:
        try:
            left = UUID(workspace_id)
        except ValueError as exc:
            raise PlatformError(
                "WORKSPACE_SCOPE_DENIED",
                "Workspace scope denied",
                403,
                "The Workspace-Id header must be a UUID.",
            ) from exc

    # The choice is checked against the memberships the platform holds, never trusted
    # (FR-PLAT-65) — for both the workspace left and the workspace entered.
    if body.workspace_id not in identity.workspaces:
        raise PlatformError(
            "WORKSPACE_SCOPE_DENIED",
            "Workspace scope denied",
            403,
            "The requested workspace is not a membership of this principal. The "
            "selection is checked against the memberships the platform holds "
            "(07 FR-PLAT-65); it is never taken on trust.",
        )
    if left is not None and left not in identity.workspaces:
        raise PlatformError(
            "WORKSPACE_SCOPE_DENIED",
            "Workspace scope denied",
            403,
            "The Workspace-Id header names a workspace this principal is not a member "
            "of. The selection is checked against the memberships the platform holds "
            "(07 FR-PLAT-65); it is never taken on trust.",
        )

    async with database.unit_of_work() as session:
        await workspace_switch.record_switch(
            session,
            principal=identity.principal,
            left=left,
            entered=body.workspace_id,
        )
        entered_row = await session.get(WorkspaceRow, body.workspace_id)
    assert entered_row is not None  # a membership names a workspace that exists

    return WorkspaceMembership(
        workspace_id=str(entered_row.id), slug=entered_row.slug, name=entered_row.name
    )
