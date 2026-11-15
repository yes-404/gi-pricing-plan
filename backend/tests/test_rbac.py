"""Roles, scopes and enforcement (`06` §3.1, FR-342, FR-343, FR-344, FR-345, FR-346, FR-347, FR-348,
FR-349)."""

from __future__ import annotations

import pytest
from backend.tests.conftest_db import seed_as_owner
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEventRow, RoleAssignmentRow, RoleRow, ServiceAccountRow
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
    async def seed(session: AsyncSession) -> None:
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

    await seed_as_owner(seed)


# -- the role catalogue ---------------------------------------------------------------


@pytest.mark.req("FR-344")
def test_the_platform_ships_the_roles_the_overview_names() -> None:
    """`00` §1.4 names six actors; FR-344 says the platform ships them."""
    assert set(BUILTIN_ROLES) == {
        "analyst",
        "pricing_actuary",
        "approver",
        "deployer",
        "auditor",
        "admin",
    }


@pytest.mark.req("FR-346")
def test_the_auditor_reads_everything_and_writes_nothing() -> None:
    """FR-346, asserted as a set identity rather than a list.

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


@pytest.mark.req("FR-353")
def test_an_administrator_cannot_approve() -> None:
    """Negative: an admin who could approve could grant itself the right and use it."""
    assert Permission.APPROVAL_DECIDE not in BUILTIN_ROLES["admin"]
    assert Permission.DEPLOYMENT_PROMOTE not in BUILTIN_ROLES["admin"]


@pytest.mark.req("FR-347")
def test_no_builtin_role_grants_a_service_account_permission_to_a_human() -> None:
    """FR-347 scopes Service Accounts to scoring; the converse also holds — scoring is
    not something a human role needs, and granting it would blur the audit trail."""
    for slug, permissions in BUILTIN_ROLES.items():
        assert Permission.SCORE_EXECUTE not in permissions, slug
        assert Permission.SCORE_BATCH not in permissions, slug


# -- enforcement -----------------------------------------------------------------------


@pytest.mark.req("FR-343")
async def test_a_principal_with_no_assignment_holds_nothing(
    database: Database, workspace_id
) -> None:
    """Deny by default: there is no branch that allows because nothing matched."""
    async with database.session() as session:
        held = await rbac.effective_permissions(
            session, workspace_id=workspace_id, principal=_user()
        )
    assert held == frozenset()


@pytest.mark.req("FR-343")
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


@pytest.mark.req("FR-345")
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


@pytest.mark.req("FR-345")
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


@pytest.mark.req("FR-343")
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


@pytest.mark.req("FR-343")
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


@pytest.mark.req("FR-348")
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


async def _seed_service_account(workspace_id, created_by) -> ServiceAccountRow:
    account = ServiceAccountRow(
        workspace_id=workspace_id,
        slug=f"sa-{new_uuid7().hex[:12]}",
        environments=["dev"],
        permissions=[],
        created_by=created_by,
    )

    async def seed(session: AsyncSession) -> None:
        session.add(account)

    await seed_as_owner(seed)
    return account


async def _grant_refused(
    database: Database,
    workspace_id,
    granter,
    *,
    kind: str,
    principal_id,
    role_slug: str = "analyst",
) -> PlatformError:
    """Attempt the grant as the application role, assert it was refused, and that nothing
    was written or audited."""
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await rbac.grant_role(
                session,
                workspace_id=workspace_id,
                granter=granter,
                principal_kind=kind,
                principal_id=principal_id,
                role_slug=role_slug,
            )
    async with database.session() as session:
        rows = (
            await session.execute(
                select(RoleAssignmentRow).where(
                    RoleAssignmentRow.principal_id == principal_id,
                    RoleAssignmentRow.granted_by.is_not(None),
                )
            )
        ).scalars().all()
        events = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "role_assignment.granted",
                )
            )
        ).scalars().all()
    assert rows == []
    assert events == []
    assert exc.value.code == "PERMISSION_DENIED"
    return exc.value


@pytest.mark.req("FR-348")
@pytest.mark.parametrize("kind", ["user", "service_account"])
async def test_a_principal_cannot_grant_a_role_to_itself(
    database: Database, workspace_id, kind: str
) -> None:
    """R1 / R1b: refused even when the granter already holds every permission the role
    confers, and whatever `principal_kind` is passed (assignments resolve by id alone)."""
    admin = _user()
    await _assign(database, workspace_id, admin, "admin")
    await _assign(database, workspace_id, admin, "analyst")
    refusal = await _grant_refused(
        database, workspace_id, admin, kind=kind, principal_id=admin.id
    )
    assert refusal.title == "Cannot grant a role to yourself"


@pytest.mark.req("FR-348")
async def test_a_self_grant_of_an_unknown_role_is_refused_not_missing(
    database: Database, workspace_id
) -> None:
    """The self-grant check runs before the role lookup: 403, never 404."""
    admin = _user()
    await _assign(database, workspace_id, admin, "admin")
    refusal = await _grant_refused(
        database,
        workspace_id,
        admin,
        kind="user",
        principal_id=admin.id,
        role_slug="no-such-role",
    )
    assert refusal.status_code == 403
    assert refusal.title == "Cannot grant a role to yourself"


@pytest.mark.req("FR-348")
@pytest.mark.parametrize("kind", ["service_account", "user"])
async def test_a_principal_cannot_grant_a_role_to_a_service_account_it_owns(
    database: Database, workspace_id, kind: str
) -> None:
    """R2 / R2b: refused whatever `principal_kind` is passed."""
    admin = _user()
    await _assign(database, workspace_id, admin, "admin")
    await _assign(database, workspace_id, admin, "analyst")
    account = await _seed_service_account(workspace_id, admin.id)
    refusal = await _grant_refused(
        database, workspace_id, admin, kind=kind, principal_id=account.id
    )
    assert refusal.title == "Cannot grant a role to a service account you own"


@pytest.mark.req("FR-348")
async def test_grant_role_itself_reads_the_owner_of_the_account(
    database: Database, owner_database: Database, workspace_id
) -> None:
    """The refusal comes from `grant_role` reading `created_by`, not from a helper or a
    fixture: the same account, the same granter, refused while the granter is the recorded
    owner and granted once the recorded owner is someone else."""
    admin, other = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")
    account = await _seed_service_account(workspace_id, admin.id)
    refusal = await _grant_refused(
        database, workspace_id, admin, kind="service_account", principal_id=account.id
    )
    assert refusal.title == "Cannot grant a role to a service account you own"

    async def hand_over(session: AsyncSession) -> None:
        await session.execute(
            update(ServiceAccountRow)
            .where(ServiceAccountRow.id == account.id)
            .values(created_by=other.id)
        )

    await seed_as_owner(hand_over)
    async with owner_database.unit_of_work() as session:
        assignment = await rbac.grant_role(
            session,
            workspace_id=workspace_id,
            granter=admin,
            principal_kind="service_account",
            principal_id=account.id,
            role_slug="analyst",
        )
    assert assignment.principal_id == account.id


@pytest.mark.req("FR-348")
async def test_the_owner_lookup_is_scoped_to_the_granters_workspace(
    database: Database, owner_database: Database, workspace_id
) -> None:
    """An account of ANOTHER workspace that the granter created is not found by the owner
    lookup (`rbac.py` filters by workspace), so the ownership refusal does not fire."""
    admin = _user()
    await _assign(database, workspace_id, admin, "admin")
    foreign = await _seed_service_account(new_uuid7(), admin.id)
    async with owner_database.unit_of_work() as session:
        assignment = await rbac.grant_role(
            session,
            workspace_id=workspace_id,
            granter=admin,
            principal_kind="service_account",
            principal_id=foreign.id,
            role_slug="analyst",
        )
    assert assignment.workspace_id == workspace_id


@pytest.mark.req("FR-348")
async def test_a_service_account_with_an_unknown_owner_is_refused(
    database: Database, workspace_id
) -> None:
    """Deny by default: `created_by` NULL is an owner nobody can rule out."""
    admin = _user()
    await _assign(database, workspace_id, admin, "admin")
    # Holds analyst too, so the withdrawn escalation rule cannot be what refuses.
    await _assign(database, workspace_id, admin, "analyst")
    account = await _seed_service_account(workspace_id, None)
    refusal = await _grant_refused(
        database, workspace_id, admin, kind="service_account", principal_id=account.id
    )
    assert refusal.title == "Cannot grant a role to a service account with no recorded owner"
    assert "not recorded" in (refusal.detail or "")
    assert "you own" not in refusal.title


@pytest.mark.req("FR-347")
@pytest.mark.parametrize("owner", ["granter", "another", "unknown"])
@pytest.mark.parametrize("role_slug", ["approver", "deployer"])
async def test_a_service_account_is_never_granted_an_approval_or_deployment_role(
    database: Database, workspace_id, owner: str, role_slug: str
) -> None:
    """FR-347 by rule, for an owned, a colleague's and an unowned account alike: the grant
    is refused before any insert and before the audit record, and the refusal names FR-347
    (so it is not one of the ownership refusals, which an account owned by another
    principal would not meet)."""
    admin, other = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")
    created_by = {"granter": admin.id, "another": other.id, "unknown": None}[owner]
    account = await _seed_service_account(workspace_id, created_by)
    refusal = await _grant_refused(
        database,
        workspace_id,
        admin,
        kind="service_account",
        principal_id=account.id,
        role_slug=role_slug,
    )
    assert refusal.title == "Cannot grant this role to a service account"
    assert "FR-347" in (refusal.detail or "")


@pytest.mark.req("FR-348")
async def test_a_grant_conferring_permissions_the_granter_lacks_succeeds(
    database: Database, owner_database: Database, workspace_id
) -> None:
    """G1: the withdrawn "permission subset" rule (#1843, option (A))."""
    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")

    async with owner_database.unit_of_work() as session:
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
            session,
            workspace_id=workspace_id,
            principal=Principal(kind=ActorKind.USER, id=target.id, display="t"),
        )
        events = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "role_assignment.granted",
                )
            )
        ).scalars().all()
    assert Permission.APPROVAL_DECIDE in held
    assert len(events) == 1


@pytest.mark.req("FR-348")
async def test_a_grant_to_a_service_account_owned_by_another_principal_succeeds(
    database: Database, owner_database: Database, workspace_id
) -> None:
    """G2: the refusal is keyed on ownership, not on the principal being a service account."""
    admin, other_admin = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")
    account = await _seed_service_account(workspace_id, other_admin.id)

    async with owner_database.unit_of_work() as session:
        assignment = await rbac.grant_role(
            session,
            workspace_id=workspace_id,
            granter=admin,
            principal_kind="service_account",
            principal_id=account.id,
            role_slug="analyst",
        )
    assert assignment.principal_id == account.id


@pytest.mark.req("FR-348")
async def test_a_grant_within_what_the_granter_holds_succeeds_and_is_audited(
    database: Database, owner_database: Database, workspace_id
) -> None:
    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")
    await _assign(database, workspace_id, admin, "approver")

    # `grant_role` has no application caller: it runs as the owner. The reads below stay on
    # the application's login role.
    async with owner_database.unit_of_work() as session:
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


@pytest.mark.req("FR-349")
async def test_break_glass_is_time_boxed_and_expires(
    database: Database, owner_database: Database, workspace_id
) -> None:
    from datetime import UTC, datetime, timedelta

    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")

    # `grant_break_glass` has no application caller: it runs as the owner (and so does the
    # test's own expiry edit below); the permission reads stay on the login role.
    async with owner_database.unit_of_work() as session:
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
    async with owner_database.unit_of_work() as session:
        row = await session.get(RoleAssignmentRow, assignment.id)
        row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    async with database.session() as session:
        held = await rbac.effective_permissions(
            session, workspace_id=workspace_id, principal=target_principal
        )
    assert Permission.APPROVAL_DECIDE not in held


@pytest.mark.req("FR-349")
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


@pytest.mark.req("FR-349")
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


@pytest.mark.req("FR-349")
async def test_break_glass_is_audited_and_flagged(
    database: Database, owner_database: Database, workspace_id
) -> None:
    admin, target = _user(), _user()
    await _assign(database, workspace_id, admin, "admin")
    reason = "Incident INC-4471: approver unavailable, rating fix blocked."

    # `grant_break_glass` has no application caller: it runs as the owner; the audit read
    # below stays on the login role.
    async with owner_database.unit_of_work() as session:
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


@pytest.mark.req("FR-344")
@pytest.mark.production_seed
async def test_seeding_roles_is_idempotent(owner_database: Database, workspace_id) -> None:
    # `seed_builtin_roles` has no application caller: the whole test runs as the owner.
    async with owner_database.unit_of_work() as session:
        first = await rbac.seed_builtin_roles(session, workspace_id)
    async with owner_database.unit_of_work() as session:
        second = await rbac.seed_builtin_roles(session, workspace_id)
    assert len(first) == len(BUILTIN_ROLES)
    assert second == []


@pytest.mark.req("FR-347")
async def test_a_credentials_own_permissions_are_enforced(
    database: Database, workspace_id, principal
) -> None:
    """RL-924: a permission no role can carry is still enforceable.

    `score:execute` is held by no builtin role, deliberately (FR-347, asserted above), so
    before this the only enforcement path could never satisfy it and `Caller.permissions`
    was populated and read by nothing.
    """
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        assert not await rbac.has_permission(
            session,
            workspace_id=workspace_id,
            principal=principal,
            permission=Permission.SCORE_EXECUTE,
        )
        assert await rbac.has_permission(
            session,
            workspace_id=workspace_id,
            principal=principal,
            permission=Permission.SCORE_EXECUTE,
            credential_permissions=frozenset({"score:execute"}),
        )


@pytest.mark.req("FR-347")
async def test_enforcement_follows_the_credential_not_the_account_row(
    database: Database, workspace_id, principal
) -> None:
    """RL-924's acceptance limb 2, and the whole reason the set is **passed**.

    The account row here would say one thing and the presented credential another. What is
    enforced must be the credential's set, because that is what was actually authenticated
    with — not what the row happens to say at the moment of the check.

    **A re-derived implementation cannot be made to fail this test**, which is why the
    ruling refused one: a lookup by principal id has no way to disagree with the row, so
    the design's safety would rest on an invariant nothing could observe. Here the two
    disagree by construction, and enforcement demonstrably follows the credential.
    """
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)

        # The credential authenticated with `score:batch` only. `score:execute` must not be
        # granted, however wide the account behind it may be.
        assert not await rbac.has_permission(
            session,
            workspace_id=workspace_id,
            principal=principal,
            permission=Permission.SCORE_EXECUTE,
            credential_permissions=frozenset({"score:batch"}),
        )
        # And the converse: a credential carrying `score:execute` grants it, and grants
        # nothing else it did not carry.
        assert not await rbac.has_permission(
            session,
            workspace_id=workspace_id,
            principal=principal,
            permission=Permission.SCORE_BATCH,
            credential_permissions=frozenset({"score:execute"}),
        )


@pytest.mark.req("FR-367")
def test_no_builtin_role_holds_custom_objective_author() -> None:
    """FR-367: not default-granted. A permission every fitter holds would be vocabulary
    without a decision behind it, so an Admin grants it explicitly."""
    for slug, permissions in BUILTIN_ROLES.items():
        assert Permission.CUSTOM_OBJECTIVE_AUTHOR not in permissions, slug
