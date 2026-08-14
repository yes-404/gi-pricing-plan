"""The settings endpoints (`07` §5.1, FR-PLAT-43..46)."""

from __future__ import annotations

import pytest
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


@pytest.fixture
def headers(workspace_id, principal) -> dict[str, str]:
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
def test_settings_are_scoped_to_the_callers_workspace(
    client: TestClient, headers
) -> None:
    """Negative: an override in one workspace must not leak into another."""
    from model_schema import new_uuid7

    client.put(
        "/api/v1/settings",
        json={"values": {"validation.psi_warn_threshold": 0.4}},
        headers=headers,
    )
    other = dict(headers)
    other[DEV_WORKSPACE_HEADER] = str(new_uuid7())
    body = client.get("/api/v1/settings", headers=other).json()
    psi = next(s for s in body if s["key"] == "validation.psi_warn_threshold")
    assert psi["effective_value"] == 0.10
    assert psi["resolved_from"] == "default"
