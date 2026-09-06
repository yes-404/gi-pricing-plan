"""Permission resolution and enforcement (`06` §3.1).

> **FR-343** — Permissions are checked in the backend on every request against
> `(principal, permission, resource, scope)`.

The whole module answers one question: *may this principal do this thing to this
resource?* Everything else — roles, assignments, scopes, break-glass — is machinery for
computing that answer, and none of it is consulted anywhere but here.

Three rules shape the design:

* **Deny by default.** An unknown role, an expired grant, a scope that does not cover the
  resource: all mean no. There is no branch that returns "allowed" because nothing matched.
* **Scope is part of the question.** A principal with `approval:decide` workspace-wide and
  one with it on a single Rating Algorithm are different answers to the same permission
  (FR-345).
* **No self-elevation.** A principal cannot grant a permission it does not itself hold
  (FR-348), which is checked here rather than in the route, so every future grant path
  inherits it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RoleAssignmentRow, RoleRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit
from model_schema import (
    BUILTIN_ROLES,
    JobSource,
    Permission,
    Principal,
    ScopeType,
)

__all__ = [
    "MAX_BREAK_GLASS_HOURS",
    "PermissionDeniedError",
    "ResourceRef",
    "effective_permissions",
    "grant_break_glass",
    "grant_role",
    "has_permission",
    "holds_anywhere",
    "require_permission",
    "seed_builtin_roles",
]

_log = get_logger("app.rbac")

#: FR-349 wants break-glass time-boxed. A grant measured in days is not an emergency
#: measure, it is a role change with a shorter paper trail.
MAX_BREAK_GLASS_HOURS = 8


@dataclass(frozen=True)
class ResourceRef:
    """What a permission is being checked against.

    `None` means "no particular resource" — listing datasets, reading the audit log — and
    is satisfied only by a workspace-wide assignment.
    """

    scope_type: ScopeType
    scope_id: UUID


class PermissionDeniedError(PlatformError):
    """403, with the distinction `06` §5.1 draws between two different refusals.

    `PERMISSION_DENIED` — the principal does not hold this permission anywhere.
    `SCOPE_DENIED` — it holds it, but not on this resource (FR-345): the motor actuary
    reaching for home pricing. Separating them is actionable, because the remedies differ:
    one needs a role, the other needs an assignment on this artifact.

    Neither says what the principal *does* hold. Listing that would turn every denied
    request into an enumeration of the authorisation model.
    """

    def __init__(
        self, permission: Permission, resource: ResourceRef | None, *, held_elsewhere: bool
    ) -> None:
        where = f" on {resource.scope_type.value}:{resource.scope_id}" if resource else ""
        if held_elsewhere:
            super().__init__(
                "SCOPE_DENIED",
                "Out of scope",
                403,
                f"You hold {permission.value} but not{where}. It must be assigned on this "
                "resource (FR-345).",
            )
        else:
            super().__init__(
                "PERMISSION_DENIED",
                "Not permitted",
                403,
                f"This action requires {permission.value}{where}.",
            )
        self.permission = permission
        self.resource = resource


async def seed_builtin_roles(session: AsyncSession, workspace_id: UUID) -> list[RoleRow]:
    """Create the `00` §1.4 roles for a workspace if they are absent (FR-344).

    Idempotent, and a copy rather than a reference: changing the shipped defaults must not
    silently change what an existing workspace's approvers can do, because that is a
    permission change with no audit event and no one to attribute it to.
    """
    existing = {
        row.slug
        for row in (
            await session.execute(
                select(RoleRow).where(RoleRow.workspace_id == workspace_id)
            )
        ).scalars()
    }
    created: list[RoleRow] = []
    for slug, permissions in BUILTIN_ROLES.items():
        if slug in existing:
            continue
        row = RoleRow(
            workspace_id=workspace_id,
            slug=slug,
            description=f"Built-in {slug.replace('_', ' ')} role (00 §1.4).",
            permissions=sorted(p.value for p in permissions),
            builtin=True,
        )
        session.add(row)
        created.append(row)
    await session.flush()
    return created


async def effective_permissions(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    principal: Principal,
    resource: ResourceRef | None = None,
    credential_permissions: frozenset[str] = frozenset(),
) -> frozenset[Permission]:
    """Every permission the principal holds here, right now.

    Used by the API to tell the frontend what to show (FR-343's second sentence). The
    frontend hides what a user cannot do; this is what it hides *by*, and it is the same
    computation the enforcement uses — a second implementation would let the UI offer a
    control the backend then refuses.

    **`credential_permissions` is the set the presented credential actually authenticated
    with** (RL-924). A Service Account's grants live on its own record, not in a role —
    `score:execute` and `score:batch` are held by no builtin role, deliberately (FR-347) —
    so a computation that reads only role assignments can never see them, and until this
    parameter existed `Caller.permissions` was populated and consulted by nothing.

    **Passed, never looked up.** A principal-id lookup would return what the account row says
    *now*; this returns what the credential in hand authenticated with. Today they are equal
    (`auth/service.py:230` copies the row straight through), but by coincidence of the current
    implementation rather than by construction — and the day a credential carries a subset of
    its account's grants, a re-derivation would silently enforce the larger set.

    Defaulting to empty keeps every existing caller unchanged: only the paths holding a
    `Caller` pass anything, so nothing that authenticates a user gains a permission.
    """
    if principal.id is None:
        return frozenset()

    now = datetime.now(UTC)
    rows = (
        await session.execute(
            select(RoleAssignmentRow, RoleRow)
            .join(RoleRow, RoleRow.id == RoleAssignmentRow.role_id)
            .where(
                RoleAssignmentRow.workspace_id == workspace_id,
                RoleAssignmentRow.principal_id == principal.id,
                RoleAssignmentRow.revoked_at.is_(None),
            )
        )
    ).all()

    granted: set[Permission] = set()
    for assignment, role in rows:
        if assignment.expires_at is not None and assignment.expires_at <= now:
            continue  # an expired grant is not a grant (FR-349)
        if not _covers(assignment, resource):
            continue
        granted |= {Permission(p) for p in role.permissions}

    # A credential's own grants are workspace-wide: a Service Account is scoped by
    # environment and workspace, never to one dataset, and `ALLOWED_PERMISSIONS`
    # (`api/service_accounts.py`) admits only `score:execute` and `score:batch`, neither of
    # which is resource-scoped. If a resource-scoped permission is ever added there, this
    # union has to learn `_covers`' question — RL-924 names that as its override.
    granted |= {Permission(p) for p in credential_permissions}
    return frozenset(granted)


def _covers(assignment: RoleAssignmentRow, resource: ResourceRef | None) -> bool:
    """Does this assignment's scope reach the resource being acted on (FR-345)?"""
    if assignment.scope_type == ScopeType.WORKSPACE.value:
        return True
    if resource is None:
        # A scoped assignment cannot satisfy a question about no particular resource:
        # "list every dataset" is not answered by "you may edit this one dataset".
        return False
    return (
        assignment.scope_type == resource.scope_type.value
        and assignment.scope_id == resource.scope_id
    )


async def holds_anywhere(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    principal: Principal,
    permission: Permission,
) -> bool:
    """Does the principal hold this permission under **any** scope?

    Only used to choose between `PERMISSION_DENIED` and `SCOPE_DENIED`. Distinct from
    `effective_permissions(resource=None)`, which deliberately answers a narrower question:
    a scoped assignment does not satisfy a question about no particular resource, so asking
    it "anywhere?" returns nothing and every scoped refusal reads as if the principal never
    held the permission at all.
    """
    if principal.id is None:
        return False

    now = datetime.now(UTC)
    rows = (
        await session.execute(
            select(RoleAssignmentRow, RoleRow)
            .join(RoleRow, RoleRow.id == RoleAssignmentRow.role_id)
            .where(
                RoleAssignmentRow.workspace_id == workspace_id,
                RoleAssignmentRow.principal_id == principal.id,
                RoleAssignmentRow.revoked_at.is_(None),
            )
        )
    ).all()
    return any(
        permission.value in role.permissions
        and (assignment.expires_at is None or assignment.expires_at > now)
        for assignment, role in rows
    )


async def has_permission(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    principal: Principal,
    permission: Permission,
    resource: ResourceRef | None = None,
    credential_permissions: frozenset[str] = frozenset(),
) -> bool:
    return permission in await effective_permissions(
        session,
        workspace_id=workspace_id,
        principal=principal,
        resource=resource,
        credential_permissions=credential_permissions,
    )


async def require_permission(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    principal: Principal,
    permission: Permission,
    resource: ResourceRef | None = None,
    credential_permissions: frozenset[str] = frozenset(),
) -> None:
    """Raise `PermissionDeniedError` unless the principal holds it here (FR-343)."""
    if not await has_permission(
        session,
        workspace_id=workspace_id,
        principal=principal,
        permission=permission,
        resource=resource,
        credential_permissions=credential_permissions,
    ):
        _log.info(
            "permission denied",
            extra={
                "permission": permission.value,
                "principal_kind": principal.kind.value,
                "scope": resource.scope_type.value if resource else "workspace",
            },
        )
        # Distinguish "you never had this" from "not here" — the remedies differ.
        held_elsewhere = resource is not None and await holds_anywhere(
            session, workspace_id=workspace_id, principal=principal, permission=permission
        )
        raise PermissionDeniedError(permission, resource, held_elsewhere=held_elsewhere)


async def grant_role(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    granter: Principal,
    principal_kind: str,
    principal_id: UUID,
    role_slug: str,
    scope_type: ScopeType = ScopeType.WORKSPACE,
    scope_id: UUID | None = None,
) -> RoleAssignmentRow:
    """Assign a role, refusing an escalation the granter could not perform (FR-348).

    The granter must hold `admin:manage_roles` **and** every permission the role confers.
    Without the second check an administrator could mint an Approver role and assign it to
    themselves, which is separation of duties defeated in two API calls.
    """
    await require_permission(
        session,
        workspace_id=workspace_id,
        principal=granter,
        permission=Permission.ADMIN_MANAGE_ROLES,
    )

    role = (
        await session.execute(
            select(RoleRow).where(
                RoleRow.workspace_id == workspace_id, RoleRow.slug == role_slug
            )
        )
    ).scalar_one_or_none()
    if role is None:
        raise PlatformError(
            "NOT_FOUND", "Role not found", 404, f"No role {role_slug!r} in this workspace."
        )

    conferred = {Permission(p) for p in role.permissions}
    held = await effective_permissions(
        session, workspace_id=workspace_id, principal=granter
    )
    escalation = conferred - held
    if escalation:
        raise PlatformError(
            "PERMISSION_DENIED",
            "Cannot grant a permission you do not hold",
            403,
            f"Granting {role_slug!r} would confer {sorted(p.value for p in escalation)}, "
            "which you do not hold (FR-348).",
        )

    assignment = RoleAssignmentRow(
        workspace_id=workspace_id,
        principal_kind=principal_kind,
        principal_id=principal_id,
        role_id=role.id,
        scope_type=scope_type.value,
        scope_id=scope_id,
        granted_by=granter.id,
    )
    session.add(assignment)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=granter,
        source=JobSource.API,
        action="role_assignment.granted",
        entity_ref=f"role:{role_slug}@1",
        after={
            "principal_id": str(principal_id),
            "role": role_slug,
            "scope_type": scope_type.value,
            "scope_id": str(scope_id) if scope_id else None,
        },
    )
    return assignment


async def grant_break_glass(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    granter: Principal,
    principal_id: UUID,
    role_slug: str,
    reason: str,
    hours: int = 1,
) -> RoleAssignmentRow:
    """Emergency elevation: time-boxed, reason-required, audited (FR-349).

    Deliberately **not** subject to the no-self-elevation rule of `grant_role` — the point
    of break-glass is to exceed what the granter normally holds. What replaces that
    protection is the expiry, the mandatory reason, the audit event flagged as break-glass,
    and the fact that it cannot be quiet.
    """
    if not reason.strip():
        raise PlatformError(
            "BREAK_GLASS_REASON_REQUIRED",
            "Break-glass requires a reason",
            422,
            "FR-349: emergency elevation is reason-required. An unexplained grant is a "
            "permission change wearing an emergency label.",
        )
    if not 0 < hours <= MAX_BREAK_GLASS_HOURS:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Break-glass window is too long",
            422,
            f"Maximum {MAX_BREAK_GLASS_HOURS} hours. A longer grant is a role change with "
            "a shorter paper trail.",
        )

    await require_permission(
        session,
        workspace_id=workspace_id,
        principal=granter,
        permission=Permission.ADMIN_BREAK_GLASS,
    )

    role = (
        await session.execute(
            select(RoleRow).where(
                RoleRow.workspace_id == workspace_id, RoleRow.slug == role_slug
            )
        )
    ).scalar_one_or_none()
    if role is None:
        raise PlatformError(
            "NOT_FOUND", "Role not found", 404, f"No role {role_slug!r} in this workspace."
        )

    expires_at = datetime.now(UTC) + timedelta(hours=hours)
    assignment = RoleAssignmentRow(
        workspace_id=workspace_id,
        principal_kind="user",
        principal_id=principal_id,
        role_id=role.id,
        scope_type=ScopeType.WORKSPACE.value,
        granted_by=granter.id,
        expires_at=expires_at,
        reason=reason,
        break_glass=True,
    )
    session.add(assignment)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=granter,
        source=JobSource.API,
        action="break_glass.granted",
        entity_ref=f"role:{role_slug}@1",
        justification=reason,
        after={
            "principal_id": str(principal_id),
            "role": role_slug,
            "expires_at": expires_at.isoformat(),
            "break_glass": True,
        },
    )
    _log.warning(
        "break-glass elevation granted",
        extra={"role": role_slug, "expires_at": expires_at.isoformat()},
    )
    return assignment
