"""Prometheus metrics (`07` §5.1, FR-443)."""

from __future__ import annotations

import re
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from redis.exceptions import ConnectionError as RedisConnectionError

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.main import create_app
from app.observability.metrics import (
    REGISTRY,
    observe_cache_lookup,
    render,
    reset_cache_lookups,
    track_cache,
)
from app.platform.bundle_slot import BundleSlot
from app.platform.diff_cache import DiffCache
from model_schema import new_uuid7
from model_schema.rating import RateTableDiff


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_blob_bucket, test_database_url

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        # Shadows conftest's `api_settings`, so it inherits no bucket — set defensively,
        # not because this file reads a blob today (`conftest_db.test_blob_bucket`).
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest.mark.req("FR-443")
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


@pytest.mark.req("FR-407")
async def test_the_route_label_is_the_template_not_the_path(
    client: TestClient, principal, workspace_id, membership
) -> None:
    """The one property that decides whether this endpoint is safe to run.

    Labelling by resolved path creates a Prometheus time series per job id, and an instance
    that has seen a million jobs holds a million series for one counter. The failure is
    silent — the counter keeps working while the monitoring system runs out of memory — so
    it has to be asserted rather than reviewed.

    The caller holds a membership but no role (W6b-11), so each request is refused at the
    permission check — and the refusal still records against the route template, which is
    exactly the property this test pins.
    """
    await membership()
    headers = {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
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


@pytest.mark.req("FR-407")
def test_an_unmatched_path_cannot_grow_the_cardinality(client: TestClient) -> None:
    """A 404 on an undefined path has no route template. Recording the path would let
    anyone probing random URLs add a time series per probe."""
    for n in range(4):
        client.get(f"/no/such/endpoint/{n}")

    body = client.get("/metrics").text
    assert 'route="<unmatched>"' in body
    assert "/no/such/endpoint/0" not in body


@pytest.mark.req("FR-407")
def test_status_is_recorded_as_a_class_not_a_code(client: TestClient) -> None:
    """The alert anyone writes is "the error rate rose". Forty-seven status labels per
    route make that a sum over a guess about which codes count."""
    client.get("/api/v1/jobs")  # 401, no identity
    body = client.get("/metrics").text
    assert 'status="4xx"' in body
    assert 'status="401"' not in body


@pytest.mark.req("FR-443")
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


@pytest.mark.req("FR-443")
def test_the_registry_is_not_the_process_global_one() -> None:
    """Two apps in one test session would otherwise share counters and each see the
    other's traffic — the same reason `create_app` takes its settings."""
    from prometheus_client import REGISTRY as PROCESS_GLOBAL

    assert REGISTRY is not PROCESS_GLOBAL


# --------------------------------------------------------------------------------------
# The cache hit-rate family (FR-443, `07` §5.1, #1505 slice 3)
# --------------------------------------------------------------------------------------

_FAMILY = "gip_cache_lookups_total"


def _samples(cache: str) -> dict[str, float]:
    """The `result -> count` samples the scrape carries for one cache."""
    found: dict[str, float] = {}
    for line in render().decode().splitlines():
        match = re.fullmatch(rf'{_FAMILY}\{{cache="{cache}",result="(\w+)"\}} ([0-9.e+]+)', line)
        if match:
            found[match.group(1)] = float(match.group(2))
    return found


class _DictClient:
    """The slice of the Redis client `DiffCache` uses, over a dict."""

    def __init__(self) -> None:
        self.data: dict[str, bytes] = {}
        self.fail = False

    async def get(self, key: str) -> bytes | None:
        if self.fail:
            raise RedisConnectionError("down")
        return self.data.get(key)

    async def set(self, key: str, value: bytes) -> None:
        self.data[key] = value


@pytest.fixture
def clean_cache_family() -> Iterator[None]:
    reset_cache_lookups()
    yield
    reset_cache_lookups()


@pytest.mark.req("FR-443")
async def test_a_diff_cache_hit_and_miss_appear_on_the_scrape(clean_cache_family: None) -> None:
    """One miss then one hit through `DiffCache`; the family carries both results."""
    cache = DiffCache(_DictClient())
    key = cache.key("a", "b", "d", None, None)

    assert await cache.get(key) is None  # miss
    await cache.set(key, RateTableDiff(changed_cells=0))
    assert await cache.get(key) is not None  # hit

    assert "# TYPE gip_cache_lookups_total counter" in render().decode()
    assert _samples("diff_cache") == {"miss": 1.0, "hit": 1.0}


@pytest.mark.req("FR-443")
async def test_a_redis_failure_is_an_error_not_a_miss(clean_cache_family: None) -> None:
    client = _DictClient()
    client.fail = True

    assert await DiffCache(client).get("k") is None

    assert _samples("diff_cache") == {"error": 1.0}


@pytest.mark.req("FR-443")
def test_a_cache_nobody_has_read_is_absent_not_zero(clean_cache_family: None) -> None:
    """The 2026-08-15 rule: a label set gets its first sample on first use."""
    DiffCache(_DictClient())  # constructing one is not a read
    track_cache("bundle_slot", lambda: (0, 0))  # a slot with no reads has no sample

    assert "gip_cache_lookups" not in render().decode()
    assert _samples("diff_cache") == {}
    assert _samples("bundle_slot") == {}


@pytest.mark.req("FR-443")
def test_a_bundle_slot_is_read_at_scrape_time(clean_cache_family: None) -> None:
    slot = BundleSlot(capacity=1)
    track_cache("bundle_slot", lambda: (slot.hits, slot.misses))
    assert slot.get("h") is None
    assert slot.get("h") is None  # a score-path miss is two lookups

    assert _samples("bundle_slot") == {"miss": 2.0}


@pytest.mark.req("FR-443")
def test_the_cache_labels_are_a_closed_set(clean_cache_family: None) -> None:
    """The label set is bounded: an unknown cache or result is refused, never exposed."""
    with pytest.raises(ValueError, match="closed set"):
        observe_cache_lookup("oidc_keys", "hit")
    with pytest.raises(ValueError, match="closed set"):
        observe_cache_lookup("diff_cache", "weird")


@pytest.mark.req("FR-443")
def test_only_the_redis_backed_cache_may_report_an_error(clean_cache_family: None) -> None:
    """`error` is `diff_cache`'s alone. The slot is in-process and cannot fail a lookup, and a
    refusal here keeps the message literal: no argument is echoed."""
    with pytest.raises(ValueError, match="closed set") as refused:
        observe_cache_lookup("bundle_slot", "error")
    assert str(refused.value) == "cache lookup label outside the closed set"
    observe_cache_lookup("diff_cache", "error")
    assert _samples("diff_cache") == {"error": 1.0}


@pytest.mark.req("FR-443")
def test_the_apps_own_bundle_slot_is_on_the_scrape(clean_cache_family: None) -> None:
    """Route level: `create_app` registers its slot, so `GET /metrics` carries the counts of
    `app.state.bundle_slot` (07 §4.6, §5.1). DB-free: the app is not entered, so no lifespan
    runs and nothing connects; the settings name no test database."""
    from backend.tests.test_bundle_slot import _compiled, _ref

    app = create_app(Settings(environment=Environment.LOCAL, version="test"))
    slot = app.state.bundle_slot
    assert slot.get("absent") is None  # a miss
    slot.put(_ref(1), _compiled("held"))
    assert slot.get("held") is not None  # a hit

    body = TestClient(app).get("/metrics").text

    assert 'gip_cache_lookups_total{cache="bundle_slot",result="hit"} 1.0' in body
    assert 'gip_cache_lookups_total{cache="bundle_slot",result="miss"} 1.0' in body
