"""The switcher's endpoints: the unscoped membership list, and the audited switch.

FR-PLAT-63's fourth obligation and the ruling that shapes it (PR #237): the list must be
readable before a selection exists, and the switch is an explicit, audited act.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER, DEV_WORKSPACE_HEADER
from app.config import Settings
from app.db.models import WorkspaceMemberRow
from app.db.session import Database
from app.main import create_app
from app.platform import workspaces
from model_schema import new_uuid7

pytestmark = pytest.mark.req("FR-PLAT-63")


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def headers(principal) -> dict[str, str]:
    """Dev identity for the fixture principal, with no workspace pin.

    The switch endpoints authenticate through `require_identity`, which reads only
    `x-dev-principal-id`; the workspace is a selection these routes must work before
    (`FR-PLAT-63`'s second amendment, PR #237).
    """
    return {DEV_PRINCIPAL_HEADER: str(principal.id)}


async def _add_membership(
    database: Database, user_id, workspace_id, *, name: str, slug: str
) -> None:
    """Create the workspace and make the principal a member of it (FR-PLAT-62's FK)."""
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(
            session, workspace_id=workspace_id, name=name, slug=slug
        )
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
    await _add_membership(database, principal.id, first, name="Alpha", slug="ws-alpha")
    await _add_membership(database, principal.id, second, name="Beta", slug="ws-beta")

    response = client.get("/api/v1/me/workspaces", headers=headers)

    assert response.status_code == 200, response.text
    memberships = response.json()
    # Each entry carries exactly the three named fields, ordered by workspace name — the
    # same ORDER BY the existing `/me` query uses (`me.py:118-132`).
    assert [m["name"] for m in memberships] == ["Alpha", "Beta"]
    assert set(memberships[0]) == {"workspace_id", "slug", "name"}
    by_id = {m["workspace_id"]: m for m in memberships}
    assert by_id[str(first)]["slug"] == "ws-alpha"
    assert by_id[str(second)]["slug"] == "ws-beta"


async def test_a_service_account_sees_an_empty_list(
    client: TestClient, database: Database, principal, headers, workspace_id, grant
) -> None:
    """A Service Account's workspace comes from the account, never a membership row.

    Its list is empty rather than an error (`me.py:114-117`): an SA has nothing to choose
    between, and `FR-PLAT-65` says it never sends the header.
    """
    await grant("admin")
    # The creation request travels as a scoped dev caller: the pin is still required by
    # `_development_caller` today, and the Workspace-Id header is what the dev path will
    # resolve against once the pin goes (W6b-11 Task 8) — both name a membership.
    await _add_membership(
        database, principal.id, workspace_id, name="The Workspace", slug="ws-the-workspace"
    )
    created = client.post(
        "/api/v1/service-accounts",
        json={
            "slug": "quote-engine-prod",
            "environments": ["prod"],
            "permissions": ["score:execute"],
        },
        headers={
            **headers,
            DEV_WORKSPACE_HEADER: str(workspace_id),
            "Workspace-Id": str(workspace_id),
        },
    ).json()

    response = client.get(
        "/api/v1/me/workspaces",
        headers={"Authorization": f"ApiKey {created['key']}"},
    )

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_no_credential_is_unauthenticated(client: TestClient) -> None:
    """The list is authenticated; anonymous reaches nothing (FR-GOV-1)."""
    response = client.get("/api/v1/me/workspaces")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"
