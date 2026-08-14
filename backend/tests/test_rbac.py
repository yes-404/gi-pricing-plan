"""Roles, scopes and enforcement (`06` §3.1, FR-GOV-1..8)."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.db.models import AuditEventRow, RoleAssignmentRow, RoleRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import rbac
from app.platform.rbac import PermissionDeniedError, ResourceRef
from model_schema import (
    BUILTIN_ROLES,
    READ_PERMISSIONS,
    ActorKind,
    Permission,
    Principal,
    ScopeType,
    new_uuid7,
)


def _user() -> Principal:
    return Principal(kind=ActorKind.USER, id=new_uuid7(), display="u@insurer.example")


async def _assign(
    database: Database,
    workspace_id,
    principal: Principal,
    role_slug: str,
    *,
    scope_type: ScopeType = ScopeType.WORKSPACE,
    scope_id=None,
) -> None:
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == role_slug
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=principal.id,
                role_id=role.id,
                scope_type=scope_type.value,
                scope_id=scope_id,
            )
        )


# -- the role catalogue ---------------------------------------------------------------


@pytest.mark.req("FR-GOV-3")
def test_the_platform_ships_the_roles_the_overview_names() -> None:
    """`00` §1.4 names six actors; FR-GOV-3 says the platform ships them."""
    assert set(BUILTIN_ROLES) == {
        "analyst",
        "pricing_actuary",
        "approver",
        "deployer",
        "auditor",
        "admin",
    }


@pytest.mark.req("FR-GOV-5")
def test_the_auditor_reads_everything_and_writes_nothing() -> None:
    """FR-GOV-5, asserted as a set identity rather than a list.

    Derived from READ_PERMISSIONS so a read permission added later reaches the Auditor
    automatically — the failure otherwise being an artifact type an auditor cannot see,
    which is the one thing the role exists to prevent.
    """
    auditor = BUILTIN_ROLES["auditor"]
    assert auditor == READ_PERMISSIONS
    assert all(p in READ_PERMISSIONS for p in auditor)
    for write in (
        Permission.DATASET_WRITE,
        Permission.MODEL_FIT,
        Permission.APPROVAL_DECIDE,
        Permission.ADMIN_MANAGE_ROLES,
    ):
        assert write not in auditor


@pytest.mark.req("FR-GOV-11")
def test_an_administrator_cannot_approve() -> None:
    """Negative: an admin who could approve could grant itself the right and use it."""
    assert Permission.APPROVAL_DECIDE not in BUILTIN_ROLES["admin"]
    assert Permission.DEPLOYMENT_PROMOTE not in BUILTIN_ROLES["admin"]


@pytest.mark.req("FR-GOV-6")
def test_no_builtin_role_grants_a_service_account_permission_to_a_human() -> None:
    """FR-GOV-6 scopes Service Accounts to scoring; the converse also holds — scoring is
    not something a human role needs, and granting it would blur the audit trail."""
    for slug, permissions in BUILTIN_ROLES.items():
        assert Permission.SCORE_EXECUTE not in permissions, slug
        assert Permission.SCORE_BATCH not in permissions, slug


# -- enforcement -----------------------------------------------------------------------


@pytest.mark.req("FR-GOV-2")
async def test_a_principal_with_no_assignment_holds_nothing(
    database: Database, workspace_id
) -> None:
    """Deny by default: there is no branch that allows because nothing matched."""
    async with database.session() as session:
        held = await rbac.effective_permissions(
            session, workspace_id=workspace_id, principal=_user()
        )
    assert held == frozenset()


@pytest.mark.req("FR-GOV-2")
async def test_a_workspace_assignment_confers_the_roles_permissions(
    database: Database, workspace_id
) -> None:
    user = _user()
    await _assign(database, workspace_id, user, "analyst")
    async with database.session() as session:
        held = await rbac.effective_permissions(
            session, workspace_id=workspace_id, principal=user
        )
    assert Permission.MODEL_FIT in held
    assert Permission.APPROVAL_DECIDE not in held


@pytest.mark.req("FR-GOV-4")
async def test_a_scoped_assignment_does_not_reach_another_resource(
    database: Database, workspace_id
) -> None:
    """"so a motor actuary cannot approve home pricing without an explicit assignment"."""
    user = _user()
    motor, home = new_uuid7(), new_uuid7()
    await _assign(
        database,
        workspace_id,
        user,
        "approver",
        scope_type=ScopeType.RATING_ALGORITHM,
        scope_id=motor,
    )

    async with database.session() as session:
        on_motor = await rbac.has_permission(
            session,
            workspace_id=workspace_id,
            principal=user,
            permission=Permission.APPROVAL_DECIDE,
            resource=ResourceRef(ScopeType.RATING_ALGORITHM, motor),
        )
        on_home = await rbac.has_permission(
            session,
            workspace_id=workspace_id,
            principal=user,
            permission=Permission.APPROVAL_DECIDE,
            resource=ResourceRef(ScopeType.RATING_ALGORITHM, home),
        )
    assert on_motor is True
    assert on_home is False


@pytest.mark.req("FR-GOV-4")
async def test_a_scoped_assignment_does_not_answer_an_unscoped_question(
    database: Database, workspace_id
) -> None:
    """Negative: "you may edit this one dataset" does not mean "you may list them all"."""
    user = _user()
    await _assign(
        database,
        workspace_id,
        user,
        "analyst",
        scope_type=ScopeType.DATASET,
        scope_id=new_uuid7(),
    )
    async with database.session() as session:
        held = await rbac.has_permission(
            session,
            workspace_id=workspace_id,
            principal=user,
            permission=Permission.DATASET_READ,
        )
    assert held is False


@pytest.mark.req("FR-GOV-2")
async def test_scope_denied_is_distinguished_from_permission_denied(
    database: Database, workspace_id
) -> None:
    """`06` §5.1 separates the codes because the remedies differ."""
    user = _user()
    motor = new_uuid7()
    await _assign(
        database, workspace_id, user, "approver",
        scope_type=ScopeType.RATING_ALGORITHM, scope_id=motor,
    )

    async with database.session() as session:
        with pytest.raises(PermissionDeniedError) as scoped:
            await rbac.require_permission(
                session,
                workspace_id=workspace_id,
                principal=user,
                permission=Permission.APPROVAL_DECIDE,
                resource=ResourceRef(ScopeType.RATING_ALGORITHM, new_uuid7()),
            )
        with pytest.raises(PermissionDeniedError) as absent:
            await rbac.require_permission(
                session,
                workspace_id=workspace_id,
                principal=user,
                permission=Permission.ADMIN_MANAGE_ROLES,
                resource=ResourceRef(ScopeType.RATING_ALGORITHM, motor),
            )
    assert scoped.value.code == "SCOPE_DENIED"
    assert absent.value.code == "PERMISSION_DENIED"


@pytest.mark.req("FR-GOV-2")
async def test_a_denial_does_not_enumerate_what_the_principal_holds(
    database: Database, workspace_id
) -> None:
    """Negative: listing held permissions turns every 403 into a map of the model."""
    user = _user()
    await _assign(database, workspace_id, user, "analyst")
    async with database.session() as session:
        with pytest.raises(PermissionDeniedError) as exc:
            await rbac.require_permission(
                session,
                workspace_id=workspace_id,
                principal=user,
                permission=Permission.APPROVAL_DECIDE,
            )
    detail = exc.value.detail or ""
    assert Permission.MODEL_FIT.value not in detail
    assert Permission.DATASET_WRITE.value not in detail


# -- granting --------------------------------------------------------------------------


@pytest.mark.req("FR-GOV-7")
async def test_granting_requires_the_manage_roles_permission(
    database: Database, workspace_id
) -> None:
    granter, target = _user(), _user()
    await _assign(database, workspace_id, granter, "analyst")
    async with database.unit_of_work() as session:
        with pytest.raises(PermissionDeniedError):
            await rbac.grant_role(
                session,
                workspace_id=workspace_id,
                granter=granter,
                principal_kind="user",
                principal_id=target.id,
                role_slug="analyst",
            )


@pytest.mark.req("FR-GOV-7")
async def test_a_user_cannot_grant_a_permission_they_do_not_hold(
    database: Database, workspace_id
) -> None:
    """The escalation FR-GOV-7 forbids: an admin minting an Approver and using it."""
    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await rbac.grant_role(
                session,
                workspace_id=workspace_id,
                granter=admin,
                principal_kind="user",
                principal_id=target.id,
                role_slug="approver",
            )
    assert exc.value.code == "PERMISSION_DENIED"
    assert "approval:decide" in (exc.value.detail or "")


@pytest.mark.req("FR-GOV-7")
async def test_a_grant_within_what_the_granter_holds_succeeds_and_is_audited(
    database: Database, workspace_id
) -> None:
    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")
    await _assign(database, workspace_id, admin, "approver")

    async with database.unit_of_work() as session:
        await rbac.grant_role(
            session,
            workspace_id=workspace_id,
            granter=admin,
            principal_kind="user",
            principal_id=target.id,
            role_slug="approver",
        )

    async with database.session() as session:
        held = await rbac.effective_permissions(
            session, workspace_id=workspace_id, principal=Principal(
                kind=ActorKind.USER, id=target.id, display="t"
            )
        )
        actions = [
            e.action
            for e in (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id
                    )
                )
            ).scalars()
        ]
    assert Permission.APPROVAL_DECIDE in held
    assert "role_assignment.granted" in actions


# -- break-glass -----------------------------------------------------------------------


@pytest.mark.req("FR-GOV-8")
async def test_break_glass_is_time_boxed_and_expires(
    database: Database, workspace_id
) -> None:
    from datetime import UTC, datetime, timedelta

    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")

    async with database.unit_of_work() as session:
        assignment = await rbac.grant_break_glass(
            session,
            workspace_id=workspace_id,
            granter=admin,
            principal_id=target.id,
            role_slug="approver",
            reason="Production rating version blocked at 02:00; incident INC-4471.",
            hours=1,
        )
    assert assignment.break_glass is True
    assert assignment.expires_at is not None

    target_principal = Principal(kind=ActorKind.USER, id=target.id, display="t")
    async with database.session() as session:
        held = await rbac.effective_permissions(
            session, workspace_id=workspace_id, principal=target_principal
        )
    assert Permission.APPROVAL_DECIDE in held

    # Expire it and confirm the grant stops conferring anything.
    async with database.unit_of_work() as session:
        row = await session.get(RoleAssignmentRow, assignment.id)
        row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    async with database.session() as session:
        held = await rbac.effective_permissions(
            session, workspace_id=workspace_id, principal=target_principal
        )
    assert Permission.APPROVAL_DECIDE not in held


@pytest.mark.req("FR-GOV-8")
async def test_break_glass_requires_a_reason(database: Database, workspace_id) -> None:
    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await rbac.grant_break_glass(
                session,
                workspace_id=workspace_id,
                granter=admin,
                principal_id=target.id,
                role_slug="approver",
                reason="   ",
            )
    assert exc.value.code == "BREAK_GLASS_REASON_REQUIRED"


@pytest.mark.req("FR-GOV-8")
async def test_break_glass_cannot_be_open_ended(database: Database, workspace_id) -> None:
    """Negative: a grant measured in days is a role change with a shorter paper trail."""
    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError, match="Maximum"):
            await rbac.grant_break_glass(
                session,
                workspace_id=workspace_id,
                granter=admin,
                principal_id=target.id,
                role_slug="approver",
                reason="indefinite access please",
                hours=rbac.MAX_BREAK_GLASS_HOURS + 1,
            )


@pytest.mark.req("FR-GOV-8")
async def test_break_glass_is_audited_and_flagged(
    database: Database, workspace_id
) -> None:
    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")
    reason = "Incident INC-4471: approver unavailable, rating fix blocked."

    async with database.unit_of_work() as session:
        await rbac.grant_break_glass(
            session,
            workspace_id=workspace_id,
            granter=admin,
            principal_id=target.id,
            role_slug="approver",
            reason=reason,
        )

    async with database.session() as session:
        event = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "break_glass.granted",
                )
            )
        ).scalar_one()
    assert event.justification == reason
    assert event.after["break_glass"] is True


@pytest.mark.req("FR-GOV-3")
async def test_seeding_roles_is_idempotent(database: Database, workspace_id) -> None:
    async with database.unit_of_work() as session:
        first = await rbac.seed_builtin_roles(session, workspace_id)
    async with database.unit_of_work() as session:
        second = await rbac.seed_builtin_roles(session, workspace_id)
    assert len(first) == len(BUILTIN_ROLES)
    assert second == []
