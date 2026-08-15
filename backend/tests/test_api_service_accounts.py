"""Service Account management endpoints (FR-PLAT-3, FR-PLAT-6)."""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import DEV_PRINCIPAL_HEADER, DEV_WORKSPACE_HEADER
from app.config import Environment, Settings
from app.db.models import AuditEventRow
from app.db.session import Database
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
    await grant("admin")
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        DEV_WORKSPACE_HEADER: str(workspace_id),
    }


@pytest.fixture
def unprivileged_headers(workspace_id, principal) -> dict[str, str]:
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        DEV_WORKSPACE_HEADER: str(workspace_id),
    }


def _create(client: TestClient, headers: dict[str, str], **overrides: object):
    body = {
        "slug": "quote-engine-prod",
        "environments": ["prod"],
        "permissions": ["score:execute"],
    }
    body.update(overrides)
    return client.post("/api/v1/service-accounts", json=body, headers=headers)


@pytest.mark.req("FR-PLAT-3")
def test_creation_returns_the_key_exactly_once(client: TestClient, headers) -> None:
    response = _create(client, headers)
    assert response.status_code == 201
    body = response.json()

    key = body["key"]
    assert key.startswith("gip_prod_")
    assert "cannot be retrieved" in body["warning"]

    # Every other representation carries the prefix only — nothing stores the secret, so
    # there is nothing to show again even if the API wanted to.
    prefix = body["account"]["keys"][0]["prefix"]
    assert prefix in key
    assert key not in str(body["account"])


@pytest.mark.req("FR-PLAT-3")
def test_a_permission_outside_the_scoring_set_is_refused(client: TestClient, headers) -> None:
    """Negative: a key that could fit a model would be a standing actuarial credential."""
    response = _create(client, headers, permissions=["model:fit"])
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-PLAT-3")
def test_a_duplicate_slug_is_refused(client: TestClient, headers) -> None:
    assert _create(client, headers).status_code == 201
    assert _create(client, headers).status_code == 409


@pytest.mark.req("FR-PLAT-3")
def test_rotation_issues_a_new_key_and_gives_the_old_one_a_deadline(
    client: TestClient, headers
) -> None:
    """The old key keeps working for the overlap. A rotation that breaks production
    instantly is one nobody performs, and an unrotated key is the failure to prevent."""
    created = _create(client, headers).json()
    account_id = created["account"]["id"]
    original_prefix = created["account"]["keys"][0]["prefix"]
    original_expiry = created["account"]["keys"][0]["expires_at"]

    rotated = client.post(
        f"/api/v1/service-accounts/{account_id}/rotate", headers=headers
    ).json()

    assert rotated["key"] != created["key"]
    prefixes = {k["prefix"] for k in rotated["account"]["keys"]}
    assert original_prefix in prefixes
    assert len(prefixes) == 2

    old = next(k for k in rotated["account"]["keys"] if k["prefix"] == original_prefix)
    assert old["expires_at"] < original_expiry
    assert old["revoked_at"] is None


@pytest.mark.req("FR-PLAT-3")
async def test_a_revoked_key_stops_authenticating(
    client: TestClient, database: Database, headers
) -> None:
    from app.auth.service import authenticate_api_key
    from app.errors import PlatformError

    created = _create(client, headers).json()
    account_id = created["account"]["id"]
    prefix = created["account"]["keys"][0]["prefix"]

    async with database.unit_of_work() as session:
        identity = await authenticate_api_key(session, created["key"])
    assert identity.principal.display == "quote-engine-prod"

    response = client.delete(
        f"/api/v1/service-accounts/{account_id}/keys/{prefix}", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["keys"][0]["revoked_at"] is not None

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await authenticate_api_key(session, created["key"])
    assert exc.value.code == "API_KEY_INVALID"


@pytest.mark.req("FR-PLAT-6")
async def test_key_lifecycle_is_audited_by_prefix_never_by_value(
    client: TestClient, database: Database, headers, workspace_id
) -> None:
    created = _create(client, headers).json()
    account_id = created["account"]["id"]
    prefix = created["account"]["keys"][0]["prefix"]
    from app.auth.api_keys import parse_key

    parsed = parse_key(created["key"])
    assert parsed is not None
    secret = parsed.secret

    client.post(f"/api/v1/service-accounts/{account_id}/rotate", headers=headers)
    client.delete(f"/api/v1/service-accounts/{account_id}/keys/{prefix}", headers=headers)

    async with database.session() as session:
        events = (
            await session.execute(
                select(AuditEventRow)
                .where(AuditEventRow.workspace_id == workspace_id)
                .order_by(AuditEventRow.sequence)
            )
        ).scalars().all()

    assert [e.action for e in events] == [
        "service_account.created",
        "service_account.key_rotated",
        "service_account.key_revoked",
    ]
    for event in events:
        rendered = f"{event.before}{event.after}"
        assert secret not in rendered
        assert created["key"] not in rendered
    assert events[0].after["key_prefix"] == prefix


@pytest.mark.req("FR-OVR-13")
async def test_another_workspaces_account_is_404_not_403(
    client: TestClient, headers, database, principal
) -> None:
    """Tenancy non-disclosure, tested where it still bites.

    The caller is an admin in the second workspace too, so it is *authorised* there and the
    404 is about the account belonging to someone else — not about the caller being
    refused. Without the second grant this returns 403 and asserts nothing about scoping.
    """
    from sqlalchemy import select

    from app.db.models import RoleAssignmentRow, RoleRow
    from app.platform import rbac
    from model_schema import ScopeType, new_uuid7

    created = _create(client, headers).json()

    other_workspace = new_uuid7()
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, other_workspace)
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == other_workspace, RoleRow.slug == "admin"
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=other_workspace,
                principal_kind="user",
                principal_id=principal.id,
                role_id=role.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )

    other_headers = dict(headers)
    other_headers[DEV_WORKSPACE_HEADER] = str(other_workspace)
    response = client.post(
        f"/api/v1/service-accounts/{created['account']['id']}/rotate", headers=other_headers
    )
    assert response.status_code == 404


@pytest.mark.req("FR-PLAT-1")
def test_service_account_routes_require_authentication() -> None:
    settings = Settings(environment=Environment.LOCAL, version="test")
    with TestClient(create_app(settings), raise_server_exceptions=False) as client:
        response = client.post("/api/v1/service-accounts", json={})
        assert response.status_code == 401
        assert response.json()["code"] == "UNAUTHENTICATED"


@pytest.mark.req("FR-GOV-2")
def test_creating_a_service_account_needs_the_admin_permission(
    client: TestClient, unprivileged_headers
) -> None:
    """Negative: a service account is a standing credential; minting one is an admin act."""
    response = client.post(
        "/api/v1/service-accounts",
        json={"slug": "sneaky", "environments": ["prod"], "permissions": ["score:execute"]},
        headers=unprivileged_headers,
    )
    assert response.status_code == 403
