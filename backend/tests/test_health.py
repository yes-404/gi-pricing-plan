"""Liveness must not depend on dependencies; readiness must (FR-444)."""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from app.api.health import ComponentStatus, register_probe


@pytest.mark.req("FR-444")
def test_healthz_is_up_with_no_probes(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == ComponentStatus.UP


@pytest.mark.req("FR-444")
def test_healthz_ignores_a_failing_dependency(client: TestClient) -> None:
    """Negative: wiring dependencies into liveness turns a database blip into a restart
    storm, because the orchestrator kills every replica at once."""

    async def down() -> str:
        return "connection refused"

    register_probe("database", down)
    assert client.get("/healthz").status_code == 200


@pytest.mark.req("FR-444")
def test_readyz_reports_each_component(client: TestClient) -> None:
    async def up() -> None:
        return None

    register_probe("database", up)
    register_probe("redis", up)
    body = client.get("/readyz").json()
    assert body["status"] == ComponentStatus.UP
    assert [c["name"] for c in body["components"]] == ["database", "redis"]


@pytest.mark.req("FR-444")
def test_readyz_is_503_when_a_component_is_down(client: TestClient) -> None:
    async def up() -> None:
        return None

    async def down() -> str:
        return "connection refused"

    register_probe("redis", up)
    register_probe("blobs", down)
    response = client.get("/readyz")
    assert response.status_code == 503
    components = {c["name"]: c for c in response.json()["components"]}
    assert components["blobs"]["status"] == ComponentStatus.DOWN
    assert components["blobs"]["detail"] == "connection refused"
    assert components["redis"]["status"] == ComponentStatus.UP


@pytest.mark.req("FR-444")
def test_a_hung_probe_does_not_hang_readiness(client: TestClient) -> None:
    """An unanswered readiness check looks like a hung process and gets the wrong remedy."""

    async def hangs() -> None:
        await asyncio.sleep(30)

    register_probe("database", hangs)
    response = client.get("/readyz")
    assert response.status_code == 503
    assert "did not respond" in response.json()["components"][0]["detail"]


@pytest.mark.req("FR-444")
def test_a_raising_probe_is_a_down_component_not_a_500(client: TestClient) -> None:
    async def raises() -> None:
        raise ConnectionError("boom")

    register_probe("database", raises)
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["components"][0]["detail"] == "probe failed: ConnectionError"


@pytest.mark.req("FR-444")
def test_version_reports_service_and_environment(client: TestClient) -> None:
    body = client.get("/version").json()
    assert body == {"service": "gi-pricing-api", "version": "test", "environment": "local"}
