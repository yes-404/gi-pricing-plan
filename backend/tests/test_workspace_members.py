"""FR-PLAT-58: a realm login resolves into the seeded workspace, as that principal."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.auth.oidc import TokenClaims
from app.auth.service import authenticate_bearer
from app.db.models import WorkspaceMemberRow
from app.db.session import Database
from app.platform import workspaces
from model_schema import new_uuid7

ISSUER = "http://localhost:8080/realms/gi-pricing"


class StubVerifier:
    """Returns fixed claims.

    Copied from `test_workspace_selection.py` rather than imported, for the reason that
    module gives: a test module is not an import target for another one.
    """

    def __init__(self, claims: TokenClaims) -> None:
        self._claims = claims

    @property
    def issuer(self) -> str:
        return ISSUER

    def verify(self, token: str) -> TokenClaims:
        return self._claims


def _claims(subject: str) -> TokenClaims:
    """Copy this from `test_workspace_selection.py:39` verbatim.

    It takes a subject and nothing else -- the email and name it carries are fixed in that
    definition. Whatever `TokenClaims` currently requires is a fact about `app/auth/oidc.py`,
    so copy rather than reconstruct.
    """
    return TokenClaims(
        subject=subject, email="a.actuary@insurer.example", name="A Actuary", groups=(), raw={}
    )


@pytest.mark.req("FR-PLAT-58")
async def test_a_realm_login_resolves_to_the_seeded_principal(database: Database) -> None:
    """The seeded user's id IS the principal id, not a fresh one.

    Membership alone is not enough. `authenticate_bearer` returns `UserRow.id` as the
    principal, and the seed's role assignments are written against the principal it minted
    -- so a defaulted id authenticates successfully, joins the workspace, and is authorised
    for nothing. That failure surfaces three layers from its cause, which is why this is
    asserted through `authenticate_bearer` rather than by reading the row back.
    """
    workspace_id, principal_id = new_uuid7(), new_uuid7()
    subject = f"sub-{new_uuid7().hex[-12:]}"

    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(
            session, workspace_id=workspace_id, name="freMTPL2 demo"
        )
        await workspaces.ensure_member(
            session,
            workspace_id=workspace_id,
            user_id=principal_id,
            issuer=ISSUER,
            subject=subject,
            email="analyst@example.fr",
        )

    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(
            session, StubVerifier(_claims(subject)), "t"
        )

    assert identity.principal.id == principal_id
    assert workspace_id in identity.workspaces


@pytest.mark.req("FR-PLAT-58")
async def test_ensuring_a_member_twice_does_not_raise(database: Database) -> None:
    """The seed is re-run against an existing database more often than not.

    `workspace_members` carries `uq_workspace_members_user_workspace`
    (`db/models.py:489`), so a second blind insert raises rather than being ignored. `users`
    carries `uq_users_issuer_subject` for the same reason.
    """
    workspace_id, principal_id = new_uuid7(), new_uuid7()
    subject = f"sub-{new_uuid7().hex[-12:]}"

    for _ in range(2):
        async with database.unit_of_work() as session:
            await workspaces.ensure_workspace(session, workspace_id=workspace_id)
            await workspaces.ensure_member(
                session,
                workspace_id=workspace_id,
                user_id=principal_id,
                issuer=ISSUER,
                subject=subject,
            )

    async with database.unit_of_work() as session:
        rows = (
            await session.execute(
                select(WorkspaceMemberRow).where(
                    WorkspaceMemberRow.user_id == principal_id
                )
            )
        ).scalars().all()
    assert len(rows) == 1
