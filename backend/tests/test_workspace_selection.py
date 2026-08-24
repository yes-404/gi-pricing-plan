"""FR-PLAT-63 and FR-PLAT-65: choosing a workspace, and the platform verifying the choice."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import _select_workspace
from app.auth.oidc import TokenClaims
from app.auth.service import AuthenticatedIdentity, authenticate_bearer
from app.db.models import AuditEventRow, WorkspaceMemberRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import workspace_switch, workspaces
from model_schema import new_uuid7

ISSUER = "https://idp.test.example/realms/gip"


class StubVerifier:
    """Returns fixed claims.

    Copied from `test_auth_users.py` rather than imported: neither it nor `_claims` is part
    of that module's surface, and a test module is not an import target for another one.
    """

    def __init__(self, claims: TokenClaims) -> None:
        self._claims = claims

    @property
    def issuer(self) -> str:
        return ISSUER

    def verify(self, token: str) -> TokenClaims:
        return self._claims


def _claims(subject: str) -> TokenClaims:
    return TokenClaims(
        subject=subject, email="a.actuary@insurer.example", name="A Actuary", groups=(), raw={}
    )


async def _memberships(database: Database, count: int) -> tuple[AuthenticatedIdentity, list]:
    """Authenticate a fresh user, give it `count` memberships, and re-authenticate.

    The second authentication is the point: `identity.workspaces` is read at authentication
    time, so a membership added after it would not appear and every assertion below would be
    made against an empty set.

    Subjects use the *tail* of a UUIDv7 hex, never the head — the leading bits are the
    millisecond timestamp, so `hex[:8]` collides within a millisecond and two tests would
    share a user and inherit its memberships (`test_auth_users.py` records the same trap).
    """
    subject = f"user-{new_uuid7().hex[-12:]}"
    ids = []
    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, StubVerifier(_claims(subject)), "t")
        for _ in range(count):
            workspace_id = new_uuid7()
            # A membership names a workspace that exists (FR-PLAT-62's foreign key).
            await workspaces.ensure_workspace(session, workspace_id=workspace_id)
            session.add(
                WorkspaceMemberRow(user_id=identity.principal.id, workspace_id=workspace_id)
            )
            ids.append(workspace_id)

    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, StubVerifier(_claims(subject)), "t")
    return identity, ids


@pytest.mark.req("FR-PLAT-65")
async def test_a_selection_among_memberships_is_honoured(database: Database) -> None:
    """A choice among facts the platform already holds is not a claim (FR-PLAT-65)."""
    identity, (first, second) = await _memberships(database, 2)
    assert _select_workspace(identity, second).workspace_id == second
    assert _select_workspace(identity, first).workspace_id == first


@pytest.mark.req("FR-PLAT-65")
async def test_a_selection_outside_the_memberships_is_denied(database: Database) -> None:
    """**Negative.** The header is checked, never trusted — this is the whole requirement.

    A caller who is a genuine member of two workspaces names a third. If this passed, the
    header would be a claim rather than a choice, which is the invariant `deps.py` has
    carried since W2 and which FR-PLAT-65 answers rather than overrides.
    """
    identity, _ = await _memberships(database, 2)
    with pytest.raises(PlatformError) as exc:
        _select_workspace(identity, new_uuid7())
    assert exc.value.code == "WORKSPACE_SCOPE_DENIED"
    assert exc.value.status_code == 403


@pytest.mark.req("FR-PLAT-63")
async def test_several_memberships_and_no_selection_is_refused(database: Database) -> None:
    """Refusing is the permanent rule; the header only gives a way to satisfy it."""
    identity, _ = await _memberships(database, 2)
    with pytest.raises(PlatformError) as exc:
        _select_workspace(identity, None)
    assert exc.value.code == "WORKSPACE_SELECTION_REQUIRED"
    assert exc.value.status_code == 403


@pytest.mark.req("FR-PLAT-63")
async def test_a_single_membership_needs_no_selection(database: Database) -> None:
    """A Service Account has exactly one by construction and never sends the header."""
    identity, (only,) = await _memberships(database, 1)
    assert _select_workspace(identity, None).workspace_id == only


@pytest.mark.req("FR-PLAT-65")
def test_the_header_is_published_on_an_operation(api_client: TestClient) -> None:
    """Declared on the dependency, and therefore on every operation that depends on it.

    Asserted rather than assumed: the whole reason for declaring it instead of reading the
    raw request is that a generated client should carry it, and nothing else in the suite
    would notice if FastAPI stopped hoisting it.
    """
    document = api_client.get("/openapi.json").json()
    names = [p["name"] for p in document["paths"]["/api/v1/me"]["get"].get("parameters", [])]
    assert "Workspace-Id" in names


async def _switch_events(database: Database, workspace_id) -> list[str]:
    """Every `workspace.*` action recorded in one workspace's chain, in sequence order."""
    async with database.session() as session:
        rows = (
            (
                await session.execute(
                    select(AuditEventRow)
                    .where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action.like("workspace.%"),
                    )
                    .order_by(AuditEventRow.sequence)
                )
            )
            .scalars()
            .all()
        )
    return [row.action for row in rows]


@pytest.mark.req("FR-PLAT-63")
async def test_a_switch_is_recorded_in_both_chains(database: Database) -> None:
    """`06` FR-GOV-24 chains per workspace, so one event answers only half the question.

    An auditor reconstructing "who was acting where, and when did they stop" reads the chain
    of the workspace they are auditing. A single event in the workspace entered is invisible
    from the workspace left — which is the one the auditor is usually looking at.
    """
    identity, (first, second) = await _memberships(database, 2)
    async with database.unit_of_work() as session:
        await workspace_switch.record_switch(
            session, principal=identity.principal, left=first, entered=second
        )

    assert await _switch_events(database, first) == ["workspace.left"]
    assert await _switch_events(database, second) == ["workspace.entered"], (
        "each chain records its own side of the move, not a copy of the same event"
    )


@pytest.mark.req("FR-PLAT-63")
async def test_the_first_selection_after_login_writes_one_event(database: Database) -> None:
    """No chain to leave. The requirement says one event, not a synthetic departure."""
    identity, (first, second) = await _memberships(database, 2)
    async with database.unit_of_work() as session:
        await workspace_switch.record_switch(
            session, principal=identity.principal, left=None, entered=second
        )

    assert await _switch_events(database, second) == ["workspace.entered"]
    assert await _switch_events(database, first) == [], (
        "a first selection has no chain to leave, and inventing a departure event would "
        "put a fact in the audit chain that did not happen"
    )
