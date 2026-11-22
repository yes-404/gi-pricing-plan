"""Liveness must not depend on dependencies; readiness must (FR-444)."""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from app.api import health
from app.api.health import ComponentStatus, register_probe
from app.config import Settings
from app.main import create_app


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
    assert body == {
        "service": "gi-pricing-api",
        "version": "test",
        "commit": "local",
        "environment": "local",
    }


@pytest.mark.req("FR-444")
def test_version_carries_the_build_commit(settings: Settings) -> None:
    """#1819 (decision 2026-11-21, answer 4 (ii)): `/version` carries the commit, read from
    `Settings.build`, and reads no database."""
    sha = "0123456789abcdef0123456789abcdef01234567"
    app = create_app(settings.model_copy(update={"build": sha}))
    body = TestClient(app).get("/version").json()
    assert body["commit"] == sha
    assert set(body) == {"service", "version", "commit", "environment"}


@pytest.mark.req("FR-444")
def test_health_shapes_live_in_model_schema() -> None:
    """Answer 7: the component shapes are `model_schema.system_status`'s, names unchanged,
    and `api.health` imports them rather than declaring a second copy (CLAUDE.md §4)."""
    from model_schema import system_status

    assert health.ComponentStatus is system_status.ComponentStatus
    assert health.ComponentHealth is system_status.ComponentHealth


@pytest.mark.req("FR-444")
def test_redis_down_is_reported_but_does_not_change_the_verdict(client: TestClient) -> None:
    """FR-444 as amended 2026-11-21 (answer 4 (i), option b): Redis is a component, not a
    gate. Negative: if it gated, a Redis outage would take every replica out of service."""

    async def up() -> None:
        return None

    async def down() -> str:
        return "unreachable: ConnectionError"

    register_probe("database", up)
    register_probe("blobs", up)
    register_probe("redis", down)
    response = client.get("/readyz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == ComponentStatus.UP
    components = {c["name"]: c["status"] for c in body["components"]}
    assert components == {"blobs": "up", "database": "up", "redis": "down"}


@pytest.mark.req("FR-444")
def test_a_gating_component_down_still_fails_readiness_beside_redis_up(client: TestClient) -> None:
    async def up() -> None:
        return None

    async def down() -> str:
        return "unreachable"

    register_probe("database", down)
    register_probe("redis", up)
    assert client.get("/readyz").status_code == 503


@pytest.mark.req("FR-444")
def test_the_redis_probe_reports_the_type_only() -> None:
    """R3: a Redis error message can carry the URL, and so a password. Only the exception
    type is reported."""

    class Broken:
        async def ping(self) -> bool:
            raise ConnectionError("redis://:hunter2@host:6379")

    class Fine:
        async def ping(self) -> bool:
            return True

    assert asyncio.run(health.redis_probe(Fine())()) is None
    reason = asyncio.run(health.redis_probe(Broken())())
    assert reason == "unreachable: ConnectionError"
