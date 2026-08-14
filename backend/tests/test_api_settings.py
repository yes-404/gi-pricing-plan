"""The settings endpoints (`07` §5.1, FR-PLAT-43..46)."""

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


@pytest.mark.req("FR-PLAT-43")
def test_reads_show_the_source_not_only_the_value(client: TestClient, headers) -> None:
    """FR-PLAT-43: the effective value *and its source* are inspectable."""
    body = client.get("/api/v1/settings", headers=headers).json()
    psi = next(s for s in body if s["key"] == "validation.psi_warn_threshold")
    assert psi["effective_value"] == 0.10
    assert psi["resolved_from"] == "default"
    assert [c["source"] for c in psi["candidates"]] == ["env", "workspace", "default"]
    assert psi["constraints"] == {"min": 0.0, "max": 1.0}


@pytest.mark.req("FR-PLAT-45")
def test_updating_a_setting_changes_the_effective_value(
    client: TestClient, headers
) -> None:
    response = client.put(
        "/api/v1/settings",
        json={"values": {"validation.psi_warn_threshold": 0.2}},
        headers=headers,
    )
    assert response.status_code == 200
    psi = next(
        s for s in response.json() if s["key"] == "validation.psi_warn_threshold"
    )
    assert psi["effective_value"] == 0.2
    assert psi["resolved_from"] == "workspace"


@pytest.mark.req("FR-PLAT-44")
def test_an_invalid_value_is_refused_with_a_typed_problem(
    client: TestClient, headers
) -> None:
    response = client.put(
        "/api/v1/settings",
        json={"values": {"validation.psi_warn_threshold": 5}},
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "SETTING_INVALID"


@pytest.mark.req("FR-PLAT-44")
def test_an_unknown_setting_is_a_404(client: TestClient, headers) -> None:
    response = client.put(
        "/api/v1/settings", json={"values": {"nope.nope": 1}}, headers=headers
    )
    assert response.status_code == 404


@pytest.mark.req("FR-PLAT-46")
def test_flags_are_reported_as_flags(client: TestClient, headers) -> None:
    body = client.get("/api/v1/settings", headers=headers).json()
    flags = {s["key"]: s for s in body if s["feature_flag"]}
    assert "features.expression_objectives_enabled" in flags
    assert all(f["effective_value"] is False for f in flags.values())


@pytest.mark.req("FR-PLAT-1")
def test_settings_require_authentication() -> None:
    settings = Settings(environment=Environment.LOCAL, version="test")
    with TestClient(create_app(settings), raise_server_exceptions=False) as client:
        assert client.get("/api/v1/settings").status_code == 401


@pytest.mark.req("FR-OVR-13")
async def test_settings_are_scoped_to_the_callers_workspace(
    client: TestClient, headers, workspace_id, principal, database
) -> None:
    """Negative: an override in one workspace must not leak into another.

    The caller is granted `admin` in *both* workspaces, so the assertion is about data
    isolation rather than about being refused — without the second grant the request is
    denied at the permission layer and the test would pass without testing anything.
    """
    from sqlalchemy import select

    from app.db.models import RoleAssignmentRow, RoleRow
    from app.platform import rbac
    from model_schema import ScopeType, new_uuid7

    client.put(
        "/api/v1/settings",
        json={"values": {"validation.psi_warn_threshold": 0.4}},
        headers=headers,
    )

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

    other = dict(headers)
    other[DEV_WORKSPACE_HEADER] = str(other_workspace)
    body = client.get("/api/v1/settings", headers=other).json()
    psi = next(s for s in body if s["key"] == "validation.psi_warn_threshold")
    assert psi["effective_value"] == 0.10
    assert psi["resolved_from"] == "default"


@pytest.mark.req("FR-GOV-2")
def test_reading_settings_needs_a_role(client: TestClient, unprivileged_headers) -> None:
    assert client.get("/api/v1/settings", headers=unprivileged_headers).status_code == 403


@pytest.mark.req("FR-GOV-5")
async def test_an_auditor_can_read_settings_but_not_change_them(
    client: TestClient, workspace_id, grant
) -> None:
    """FR-GOV-5: read everything, write nothing — including here."""
    from model_schema import new_uuid7

    auditor = new_uuid7()
    await grant("auditor", principal_id=auditor)
    headers = {
        DEV_PRINCIPAL_HEADER: str(auditor),
        DEV_WORKSPACE_HEADER: str(workspace_id),
    }
    assert client.get("/api/v1/settings", headers=headers).status_code == 200
    response = client.put(
        "/api/v1/settings",
        json={"values": {"validation.psi_warn_threshold": 0.2}},
        headers=headers,
    )
    assert response.status_code == 403
