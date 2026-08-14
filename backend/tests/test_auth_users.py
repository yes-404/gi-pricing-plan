"""User provisioning from identity-provider claims (FR-PLAT-4)."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.auth.oidc import TokenClaims

# NOTE: subjects use the *tail* of a UUIDv7 hex, never the head. The leading bits are the
# millisecond timestamp, so `hex[:8]` collides for anything created in the same
# millisecond — which made two of these tests share a user and inherit its memberships.
from app.auth.service import authenticate_bearer
from app.db.models import UserRow, WorkspaceMemberRow
from app.db.session import Database
from app.errors import PlatformError
from model_schema import ActorKind, new_uuid7

ISSUER = "https://idp.test.example/realms/gip"


class StubVerifier:
    """Returns fixed claims. Token verification itself is covered in test_auth_oidc."""

    def __init__(self, claims: TokenClaims) -> None:
        self._claims = claims

    @property
    def issuer(self) -> str:
        return ISSUER

    def verify(self, token: str) -> TokenClaims:
        return self._claims


def _claims(subject: str, email: str | None = "a.actuary@insurer.example") -> TokenClaims:
    return TokenClaims(
        subject=subject, email=email, name="A Actuary", groups=("pricing",), raw={}
    )


@pytest.mark.req("FR-PLAT-4")
async def test_a_user_is_created_on_first_login(database: Database) -> None:
    subject = f"user-{new_uuid7().hex[-12:]}"
    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, StubVerifier(_claims(subject)), "t")

    assert identity.principal.kind is ActorKind.USER

    async with database.session() as session:
        user = (
            await session.execute(select(UserRow).where(UserRow.subject == subject))
        ).scalar_one()
    assert user.issuer == ISSUER
    assert user.email == "a.actuary@insurer.example"
    assert user.last_login_at is not None


@pytest.mark.req("FR-PLAT-4")
async def test_a_second_login_updates_rather_than_duplicates(database: Database) -> None:
    """Keyed on (issuer, subject), never email — an email change must not orphan history."""
    subject = f"user-{new_uuid7().hex[-12:]}"
    async with database.unit_of_work() as session:
        first = await authenticate_bearer(session, StubVerifier(_claims(subject)), "t")
    async with database.unit_of_work() as session:
        second = await authenticate_bearer(
            session, StubVerifier(_claims(subject, "new.name@insurer.example")), "t"
        )

    assert first.principal.id == second.principal.id

    async with database.session() as session:
        users = (
            await session.execute(select(UserRow).where(UserRow.subject == subject))
        ).scalars().all()
    assert len(users) == 1
    assert users[0].email == "new.name@insurer.example"


@pytest.mark.req("FR-PLAT-4")
async def test_a_user_with_no_membership_reaches_no_workspace(database: Database) -> None:
    """FR-PLAT-4: no mapped access means *no* access, not default access.

    A real, authenticated, known user who may act nowhere is the correct state until
    governance grants them something (W3).
    """
    subject = f"user-{new_uuid7().hex[-12:]}"
    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, StubVerifier(_claims(subject)), "t")
    assert identity.workspaces == frozenset()

    from app.api.deps import _single_workspace

    with pytest.raises(PlatformError) as exc:
        _single_workspace(identity)
    assert exc.value.status_code == 403
    assert "never the default" in (exc.value.detail or "")


@pytest.mark.req("FR-PLAT-4")
async def test_membership_grants_exactly_one_workspace(
    database: Database, workspace_id
) -> None:
    subject = f"user-{new_uuid7().hex[-12:]}"
    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, StubVerifier(_claims(subject)), "t")
        session.add(
            WorkspaceMemberRow(user_id=identity.principal.id, workspace_id=workspace_id)
        )

    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, StubVerifier(_claims(subject)), "t")

    from app.api.deps import _single_workspace

    caller = _single_workspace(identity)
    assert caller.workspace_id == workspace_id


@pytest.mark.req("FR-PLAT-4")
async def test_membership_of_several_workspaces_requires_a_choice(
    database: Database,
) -> None:
    """Negative: the platform must not pick a tenant on the caller's behalf."""
    subject = f"user-{new_uuid7().hex[-12:]}"
    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, StubVerifier(_claims(subject)), "t")
        for _ in range(2):
            session.add(
                WorkspaceMemberRow(user_id=identity.principal.id, workspace_id=new_uuid7())
            )

    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, StubVerifier(_claims(subject)), "t")

    from app.api.deps import _single_workspace

    with pytest.raises(PlatformError) as exc:
        _single_workspace(identity)
    assert exc.value.status_code == 403


@pytest.mark.req("FR-PLAT-1")
def test_the_user_table_has_no_password_column() -> None:
    """FR-PLAT-1: the platform stores no user passwords, and cannot start to."""
    columns = {c.name for c in UserRow.__table__.columns}
    assert not any(
        term in name for name in columns for term in ("password", "secret", "hash")
    ), columns
