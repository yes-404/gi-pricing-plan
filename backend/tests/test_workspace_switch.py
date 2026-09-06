"""The switcher's endpoints: the unscoped membership list, and the audited switch.

FR-396's fourth obligation and the ruling that shapes it (PR #237): the list must be
readable before a selection exists, and the switch is an explicit, audited act.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Settings
from app.db.models import AuditEventRow, WorkspaceMemberRow
from app.db.session import Database
from app.main import create_app
from app.platform import workspaces
from model_schema import new_uuid7

pytestmark = pytest.mark.req("FR-396")


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def headers(principal) -> dict[str, str]:
    """Dev identity for the fixture principal, with no workspace pin.

    The switch endpoints authenticate through `require_identity`, which reads only
    `x-dev-principal-id`; the workspace is a selection these routes must work before
    (`FR-396`'s second amendment, PR #237).
    """
    return {DEV_PRINCIPAL_HEADER: str(principal.id)}


async def _add_membership(
    database: Database, user_id, workspace_id, *, name: str
) -> None:
    """Create the workspace and make the principal a member of it (FR-395's FK).

    The slug is the one `ensure_workspace` derives from the fresh per-test workspace id
    (`workspaces.py:37-41`). A fixed slug would collide: the suite's isolation is per-test
    ids, nothing is cleaned between tests (`conftest_db.py:9-15`), and `uq_workspaces_slug`
    is global — the next test's workspace would be the duplicate.
    """
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id, name=name)
        session.add(WorkspaceMemberRow(user_id=user_id, workspace_id=workspace_id))


async def test_the_list_is_readable_without_a_selection(
    client: TestClient, database: Database, principal, headers
) -> None:
    """A first selection starts from this list: unscoped, and each entry named.

    A multi-membership principal with **no** `Workspace-Id` header must still reach the
    list it would choose from — `require_caller` refuses exactly this state, and the
    ruling's unscoped route exists to answer it.
    """
    first, second = new_uuid7(), new_uuid7()
    await _add_membership(database, principal.id, first, name="Alpha")
    await _add_membership(database, principal.id, second, name="Beta")

    response = client.get("/api/v1/me/workspaces", headers=headers)

    assert response.status_code == 200, response.text
    memberships = response.json()
    # Each entry carries exactly the three named fields, ordered by workspace name — the
    # same ORDER BY the existing `/me` query uses (`me.py:118-132`).
    assert [m["name"] for m in memberships] == ["Alpha", "Beta"]
    assert set(memberships[0]) == {"workspace_id", "slug", "name"}
    by_id = {m["workspace_id"]: m for m in memberships}
    assert by_id[str(first)]["slug"] == f"ws-{first.hex}"
    assert by_id[str(second)]["slug"] == f"ws-{second.hex}"


async def test_a_service_account_sees_an_empty_list(
    client: TestClient, database: Database, principal, headers, workspace_id, grant
) -> None:
    """A Service Account's workspace comes from the account, never a membership row.

    Its list is empty rather than an error (`me.py:114-117`): an SA has nothing to choose
    between, and `FR-397` says it never sends the header.
    """
    # The creation request travels as a scoped dev caller. The dev path resolves the
    # `Workspace-Id` header against the memberships (W6b-11 Task 8 landed); the header
    # names the membership `grant` seeds for the fixture workspace — the only pin the
    # path still honours. A second, direct `_add_membership` for the same pair would
    # violate `uq_workspace_members_user_workspace` (`models.py`).
    await grant("admin")
    created = client.post(
        "/api/v1/service-accounts",
        json={
            "slug": "quote-engine-prod",
            "environments": ["prod"],
            "permissions": ["score:execute"],
        },
        headers={**headers, "Workspace-Id": str(workspace_id)},
    ).json()

    response = client.get(
        "/api/v1/me/workspaces",
        headers={"Authorization": f"ApiKey {created['key']}"},
    )

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_no_credential_is_unauthenticated(client: TestClient) -> None:
    """The list is authenticated; anonymous reaches nothing (FR-342)."""
    response = client.get("/api/v1/me/workspaces")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


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


async def test_a_switch_is_recorded_in_both_chains(
    client: TestClient, database: Database, principal, headers
) -> None:
    """`06` FR-372 chains per workspace, so one event answers only half the question.

    An auditor reconstructing "who was acting where, and when did they stop" reads the
    chain of the workspace they are auditing; the workspace left must record its own side.
    """
    first, second = new_uuid7(), new_uuid7()
    await _add_membership(database, principal.id, first, name="Alpha")
    await _add_membership(database, principal.id, second, name="Beta")

    response = client.post(
        "/api/v1/me/workspace",
        json={"workspace_id": str(second)},
        headers={**headers, "Workspace-Id": str(first)},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        "workspace_id": str(second),
        "slug": f"ws-{second.hex}",
        "name": "Beta",
    }
    assert await _switch_events(database, first) == ["workspace.left"]
    assert await _switch_events(database, second) == ["workspace.entered"]


async def test_the_first_selection_writes_one_event(
    client: TestClient, database: Database, principal, headers
) -> None:
    """No chain to leave. `FR-396` says one event, not a synthetic departure."""
    first = new_uuid7()
    await _add_membership(database, principal.id, first, name="Alpha")

    response = client.post(
        "/api/v1/me/workspace", json={"workspace_id": str(first)}, headers=headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["slug"] == f"ws-{first.hex}"
    assert await _switch_events(database, first) == ["workspace.entered"]


async def test_a_switch_to_a_non_membership_is_denied(
    client: TestClient, database: Database, principal, headers
) -> None:
    """The choice is checked against the memberships, never taken on trust (FR-397)."""
    member, outsider = new_uuid7(), new_uuid7()
    await _add_membership(database, principal.id, member, name="Alpha")

    response = client.post(
        "/api/v1/me/workspace",
        json={"workspace_id": str(outsider)},
        headers=headers,
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "WORKSPACE_SCOPE_DENIED"
    assert await _switch_events(database, member) == []

    # The same refusal for the header's value: a well-formed left that is not a membership.
    response = client.post(
        "/api/v1/me/workspace",
        json={"workspace_id": str(member)},
        headers={**headers, "Workspace-Id": str(outsider)},
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "WORKSPACE_SCOPE_DENIED"
    assert await _switch_events(database, member) == []


async def test_a_malformed_header_is_a_platform_refusal_not_a_422(
    client: TestClient, database: Database, principal, headers
) -> None:
    """The header parses as str then UUID, so the refusal stays in the error catalogue."""
    member = new_uuid7()
    await _add_membership(database, principal.id, member, name="Alpha")

    response = client.post(
        "/api/v1/me/workspace",
        json={"workspace_id": str(member)},
        headers={**headers, "Workspace-Id": "not-a-uuid"},
    )

    assert response.status_code == 403, response.text
    assert response.json()["code"] == "WORKSPACE_SCOPE_DENIED"


async def test_reselecting_the_current_workspace_writes_one_event(
    client: TestClient, database: Database, principal, headers
) -> None:
    """`record_switch` skips the departure when `left == entered` — no self-left."""
    first = new_uuid7()
    await _add_membership(database, principal.id, first, name="Alpha")

    response = client.post(
        "/api/v1/me/workspace",
        json={"workspace_id": str(first)},
        headers={**headers, "Workspace-Id": str(first)},
    )

    assert response.status_code == 200, response.text
    assert await _switch_events(database, first) == ["workspace.entered"]


def test_the_header_is_published_on_the_switch_operation(client: TestClient) -> None:
    """Declared on the route, so the generated client carries it (FR-397)."""
    document = client.get("/openapi.json").json()
    operation = document["paths"]["/api/v1/me/workspace"]["post"]
    params = {p["name"]: p for p in operation.get("parameters", [])}
    assert "Workspace-Id" in params
    assert params["Workspace-Id"].get("required") is not True
