"""`GET /api/v1/me` (FR-GOV-1, FR-GOV-2)."""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER, DEV_WORKSPACE_HEADER
from app.config import Environment, Settings
from app.main import create_app


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def headers(workspace_id, principal, grant) -> dict[str, str]:
    await grant("pricing_actuary")
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        DEV_WORKSPACE_HEADER: str(workspace_id),
    }


@pytest.mark.req("FR-GOV-2")
def test_me_reports_the_permissions_the_frontend_should_render_by(
    client: TestClient, headers
) -> None:
    """The same computation enforcement uses — a second one would let the UI offer a
    control the backend refuses."""
    body = client.get("/api/v1/me", headers=headers).json()
    assert body["principal_kind"] == "user"
    assert "model:fit" in body["permissions"]
    assert "approval:decide" not in body["permissions"]
    assert [r["role"] for r in body["roles"]] == ["pricing_actuary"]


@pytest.mark.req("FR-GOV-1")
def test_me_requires_a_principal(client: TestClient) -> None:
    """FR-GOV-1: anonymous access exists only for health checks and the OpenAPI document."""
    assert client.get("/api/v1/me").status_code == 401


@pytest.mark.req("FR-GOV-1")
def test_health_and_openapi_are_the_only_anonymous_surfaces(client: TestClient) -> None:
    """Negative: anything else answering anonymously is an unauthenticated read."""
    for path in ("/healthz", "/readyz", "/version", "/openapi.json"):
        assert client.get(path).status_code in {200, 503}, path
    for path in ("/api/v1/me", "/api/v1/jobs", "/api/v1/settings"):
        assert client.get(path).status_code == 401, path


@pytest.mark.req("FR-GOV-2")
def test_a_principal_with_no_role_reports_no_permissions(
    client: TestClient, workspace_id, principal
) -> None:
    """Authentication is not authorisation; `/me` must say so rather than 403."""
    body = client.get(
        "/api/v1/me",
        headers={
            DEV_PRINCIPAL_HEADER: str(principal.id),
            DEV_WORKSPACE_HEADER: str(workspace_id),
        },
    ).json()
    assert body["permissions"] == []
    assert body["roles"] == []


@pytest.mark.req("FR-GOV-8")
async def test_break_glass_is_visible_on_me(
    client: TestClient, database, workspace_id, principal, grant
) -> None:
    """FR-GOV-8: prominently flagged. A user must be able to see they are elevated."""
    from app.platform import rbac
    from model_schema import ActorKind, Principal, new_uuid7

    admin = Principal(kind=ActorKind.USER, id=new_uuid7(), display="admin")
    await grant("admin", principal_id=admin.id)
    async with database.unit_of_work() as session:
        await rbac.grant_break_glass(
            session,
            workspace_id=workspace_id,
            granter=admin,
            principal_id=principal.id,
            role_slug="approver",
            reason="INC-4471",
        )

    body = client.get(
        "/api/v1/me",
        headers={
            DEV_PRINCIPAL_HEADER: str(principal.id),
            DEV_WORKSPACE_HEADER: str(workspace_id),
        },
    ).json()
    elevated = [r for r in body["roles"] if r["break_glass"]]
    assert len(elevated) == 1
    assert elevated[0]["role"] == "approver"
    assert elevated[0]["expires_at"] is not None


@pytest.mark.req("FR-PLAT-63")
async def test_me_lists_every_membership_with_its_name(
    client: TestClient, database, workspace_id, principal, grant
) -> None:
    """A switcher cannot offer a choice the identity endpoint does not describe.

    Two memberships, and the response must name both — not only the one the caller is
    acting in, which is what `workspace_id` already says.
    """
    from app.db.models import WorkspaceMemberRow
    from app.platform import workspaces
    from model_schema import new_uuid7

    other = new_uuid7()
    async with database.unit_of_work() as session:
        # Named *before* `grant`, deliberately. `grant` calls `ensure_workspace` with no
        # name, and `ensure_workspace` returns an existing row untouched — so naming
        # afterwards would silently do nothing and this assertion would read
        # "Workspace xxxxxxxx". Creating both named up front also exercises that
        # idempotency: `grant`'s later call must find these rows and leave them alone.
        await workspaces.ensure_workspace(session, workspace_id=workspace_id, name="Motor")
        await workspaces.ensure_workspace(session, workspace_id=other, name="Household")
        # Both memberships are written here. `grant` assigns a *role*, which is a different
        # fact from membership and does not imply one — a caller can hold a role assignment
        # in a workspace it has no `workspace_members` row for, which is exactly why this
        # endpoint reads memberships rather than inferring them from roles.
        session.add(WorkspaceMemberRow(user_id=principal.id, workspace_id=workspace_id))
        session.add(WorkspaceMemberRow(user_id=principal.id, workspace_id=other))

    await grant("pricing_actuary")

    response = client.get(
        "/api/v1/me",
        headers={
            DEV_PRINCIPAL_HEADER: str(principal.id),
            DEV_WORKSPACE_HEADER: str(workspace_id),
        },
    )
    assert response.status_code == 200, response.text
    named = {w["workspace_id"]: w["name"] for w in response.json()["workspaces"]}
    assert named == {str(workspace_id): "Motor", str(other): "Household"}
