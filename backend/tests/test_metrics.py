"""Prometheus metrics (`07` §5.1, FR-PLAT-40)."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.deps import DEV_PRINCIPAL_HEADER, DEV_WORKSPACE_HEADER
from app.config import Environment, Settings
from app.main import create_app
from app.observability.metrics import REGISTRY
from model_schema import new_uuid7


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_database_url

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


@pytest.mark.req("FR-PLAT-40")
def test_metrics_are_exposed_in_prometheus_format(client: TestClient) -> None:
    client.get("/healthz")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    body = response.text
    assert "# TYPE gip_http_requests_total counter" in body
    assert "# TYPE gip_http_request_duration_seconds histogram" in body
    assert "gip_blob_objects" in body
    assert "gip_job_queue_depth" in body


@pytest.mark.req("FR-PLAT-52")
def test_the_route_label_is_the_template_not_the_path(client: TestClient) -> None:
    """The one property that decides whether this endpoint is safe to run.

    Labelling by resolved path creates a Prometheus time series per job id, and an instance
    that has seen a million jobs holds a million series for one counter. The failure is
    silent — the counter keeps working while the monitoring system runs out of memory — so
    it has to be asserted rather than reviewed.
    """
    headers = {
        DEV_PRINCIPAL_HEADER: str(new_uuid7()),
        DEV_WORKSPACE_HEADER: str(new_uuid7()),
    }
    route = "/api/v1/jobs/{job_id}"

    def series_for(body: str) -> dict[str, float]:
        """Counter lines whose `route` label is exactly this template.

        Exactly, not by substring: `/api/v1/jobs/{job_id}/logs` contains it, and matching
        loosely would count three routes as one. And a *delta*, because the registry is
        process-wide and every other test file in the session writes to it — an absolute
        count here would pass alone and fail in a full run, which is the worst of both.
        """
        prefix = f'gip_http_requests_total{{method="GET",route="{route}",'
        return {
            line: float(line.rsplit(" ", 1)[1])
            for line in body.splitlines()
            if line.startswith(prefix)
        }

    before = series_for(client.get("/metrics").text)
    ids = [new_uuid7() for _ in range(5)]
    for job_id in ids:
        client.get(f"/api/v1/jobs/{job_id}", headers=headers)

    body = client.get("/metrics").text
    assert f'route="{route}"' in body
    for job_id in ids:
        assert str(job_id) not in body, "a UUID reached a metric label"

    # Five requests, five increments, and — the claim that matters — no `route` label
    # anywhere in the exposition contains an identifier. Asserted over every label value
    # rather than over a line count: other tests in the session hit the same route with a
    # different status class, so counting *series* is counting other people's traffic.
    assert sum(series_for(body).values()) - sum(before.values()) == 5

    labels = set(re.findall(r'route="([^"]*)"', body))
    uuid_like = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}")
    assert not [label for label in labels if uuid_like.search(label)], labels
    assert route in labels


@pytest.mark.req("FR-PLAT-52")
def test_an_unmatched_path_cannot_grow_the_cardinality(client: TestClient) -> None:
    """A 404 on an undefined path has no route template. Recording the path would let
    anyone probing random URLs add a time series per probe."""
    for n in range(4):
        client.get(f"/no/such/endpoint/{n}")

    body = client.get("/metrics").text
    assert 'route="<unmatched>"' in body
    assert "/no/such/endpoint/0" not in body


@pytest.mark.req("FR-PLAT-52")
def test_status_is_recorded_as_a_class_not_a_code(client: TestClient) -> None:
    """The alert anyone writes is "the error rate rose". Forty-seven status labels per
    route make that a sum over a guess about which codes count."""
    client.get("/api/v1/jobs")  # 401, no identity
    body = client.get("/metrics").text
    assert 'status="4xx"' in body
    assert 'status="401"' not in body


@pytest.mark.req("FR-PLAT-40")
async def test_queue_depth_clears_when_a_kind_drains(database, workspace_id) -> None:
    """A kind that drained to zero must stop reporting its last non-zero depth — the
    failure mode that makes a queue alert useless, because it never recovers."""
    from app.api.health import refresh_platform_gauges
    from app.observability.metrics import job_queue_depth
    from app.platform import jobs as job_service
    from model_schema import ActorKind, JobKind, JobStatus, Principal

    actor = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session, JobKind.DATASET_PROFILE, {}, actor, workspace_id=workspace_id
        )

    await refresh_platform_gauges(database)
    queued = job_queue_depth.labels(kind="dataset.profile", status="queued")._value.get()
    assert queued >= 1

    async with database.unit_of_work() as session:
        await job_service.transition(session, job.id, JobStatus.RUNNING, actor=actor)
        await job_service.transition(session, job.id, JobStatus.SUCCEEDED, actor=actor)

    await refresh_platform_gauges(database)
    after = job_queue_depth.labels(kind="dataset.profile", status="queued")._value.get()
    assert after == 0


@pytest.mark.req("FR-PLAT-40")
def test_the_registry_is_not_the_process_global_one() -> None:
    """Two apps in one test session would otherwise share counters and each see the
    other's traffic — the same reason `create_app` takes its settings."""
    from prometheus_client import REGISTRY as PROCESS_GLOBAL

    assert REGISTRY is not PROCESS_GLOBAL
