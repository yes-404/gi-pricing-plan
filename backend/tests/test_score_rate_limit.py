"""The scoring rate limit (`07` FR-452, FR-430, `03` NFR-499, register F48; `RL-1347` cases 1-9).

Real Redis throughout (CI's Redis 7, the local compose Redis): a single-process test proves
nothing about a shared counter, so cases 1 and 2 use two applications over one Redis, with the
clock fixed so a run cannot straddle a second boundary.

**What "admitted" means here.** These tests never price a quote. A request that passes the
limiter reaches `POST /score`'s handler and is refused there for a reason that has nothing to
do with the limit (`NO_LIVE_RATING_VERSION`, 409, since no Deployment exists); a request the
limiter refuses is 429 and never reaches the handler. So `status != 429` is the limiter's
"admitted", and it keeps the tests independent of a compiled Rating Version.
"""

from __future__ import annotations

import asyncio
import logging
import os
import statistics
import time
from collections.abc import Iterator
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Settings
from app.db.models import EnvironmentSettingRow
from app.db.session import Database
from app.main import create_app
from app.observability import metrics
from app.platform import rate_limit
from app.platform import settings as svc
from app.platform.rate_limit import RateLimiter, build_redis_client
from model_schema import ActorKind, Principal

SCORE_URL = "/api/v1/score"
DEFAULT_KEY = "scoring.default_client_rate_limit_rps"
FIXED_SECOND = 1_800_000_000.0
QUOTE = {
    "purpose": "new_business",
    "quoted_at": "2026-08-30T09:00:00Z",
    "effective_date": "2026-09-01",
    "inputs": {"premium_in": 1000},
    "options": {"rating_version_ref": None},
}


def _app_client(api_settings: Settings, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    # The clock is pinned, so the window key never changes; the key's real-time expiry must
    # not run out under it, or a stall of more than 2 s resets the counter (FD 8049).
    monkeypatch.setattr(rate_limit, "_KEY_TTL_SECONDS", 3600)
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as client:
        client.app.state.rate_limiter.clock = lambda: FIXED_SECOND  # type: ignore[attr-defined]
        yield client


@pytest.fixture
def client(api_settings: Settings, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    yield from _app_client(api_settings, monkeypatch)


@pytest.fixture
def second_client(api_settings: Settings, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """A second replica: its own application, the same database and the same Redis."""
    yield from _app_client(api_settings, monkeypatch)


@pytest_asyncio.fixture
async def admin_headers(workspace_id: UUID, principal: Any, grant: Any) -> dict[str, str]:
    await grant("admin")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def clean_environment_settings(database: Database) -> Any:
    yield
    async with database.unit_of_work() as session:
        await session.execute(delete(EnvironmentSettingRow))


def _account(
    client: TestClient,
    headers: dict[str, str],
    *,
    environments: list[str],
    rate_limit_rps: int | None = None,
    permissions: tuple[str, ...] = ("score:execute",),
    slug: str = "limited-client",
) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    """Create a Service Account; return the API-key headers by Environment, and the account."""
    body: dict[str, Any] = {
        "slug": slug,
        "environments": environments,
        "permissions": list(permissions),
    }
    if rate_limit_rps is not None:
        body["rate_limit_rps"] = rate_limit_rps
    created = client.post("/api/v1/service-accounts", json=body, headers=headers)
    assert created.status_code == 201, created.text
    payload = created.json()
    by_environment = {
        k["environment"]: {
            "X-API-Key": k["key"],
            "Workspace-Id": headers["Workspace-Id"],
        }
        for k in payload["keys"]
    }
    return by_environment, payload["account"]


def _score(client: TestClient, headers: dict[str, str]) -> int:
    return client.post(SCORE_URL, json=QUOTE, headers=headers).status_code


@pytest.mark.req("FR-452")
def test_the_counter_is_shared_across_replicas_and_the_refusal_carries_retry_after(
    client: TestClient, second_client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Cases 1 and 2. Red on broken input: a per-process counter admits 6, not 3."""
    keys, _ = _account(client, admin_headers, environments=["uat"], rate_limit_rps=3)
    headers = keys["uat"]

    first = [_score(client, headers), _score(second_client, headers), _score(client, headers)]
    assert 429 not in first

    refused = second_client.post(SCORE_URL, json=QUOTE, headers=headers)
    assert refused.status_code == 429
    assert refused.headers["Retry-After"] == "1"
    problem = refused.json()
    assert problem["code"] == "RATE_LIMITED"
    assert "premium_in" not in refused.text
    assert _score(client, headers) == 429


@pytest.mark.req("FR-430")
def test_the_limit_is_independent_per_environment(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Case 3: with `dev` at its limit a `uat` request is admitted."""
    keys, _ = _account(client, admin_headers, environments=["dev", "uat"], rate_limit_rps=1)

    assert _score(client, keys["dev"]) != 429
    assert _score(client, keys["dev"]) == 429
    assert _score(client, keys["uat"]) != 429


@pytest.mark.req("FR-452")
async def test_the_environment_default_limits_only_its_environment(
    client: TestClient,
    admin_headers: dict[str, str],
    database: Database,
    workspace_id: UUID,
    clean_environment_settings: Any,
) -> None:
    """Case 4: no account rate; the default set for `uat` only."""
    keys, _ = _account(client, admin_headers, environments=["dev", "uat"])
    async with database.unit_of_work() as session:
        await svc.set_environment_setting(session, "uat", DEFAULT_KEY, 2, None)

    assert 429 not in [_score(client, keys["uat"]) for _ in range(2)]
    assert _score(client, keys["uat"]) == 429
    assert all(_score(client, keys["dev"]) != 429 for _ in range(5))

    # The same key set at workspace level limits both Environments.
    from app.platform import workspaces

    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await svc.set_workspace_setting(session, workspace_id, DEFAULT_KEY, 1)
        await session.execute(delete(EnvironmentSettingRow))
    fresh, _ = _account(
        client, admin_headers, environments=["dev", "uat"], slug="second-client"
    )
    for environment in ("dev", "uat"):
        assert _score(client, fresh[environment]) != 429
        assert _score(client, fresh[environment]) == 429


@pytest.mark.req("FR-452")
async def test_the_accounts_own_rate_wins_over_the_environment_default(
    client: TestClient,
    admin_headers: dict[str, str],
    database: Database,
    clean_environment_settings: Any,
) -> None:
    """Case 5: account 5, `uat` default 2 — requests 3, 4 and 5 are admitted, the 6th is not."""
    keys, _ = _account(client, admin_headers, environments=["uat"], rate_limit_rps=5)
    async with database.unit_of_work() as session:
        await svc.set_environment_setting(session, "uat", DEFAULT_KEY, 2, None)

    results = [_score(client, keys["uat"]) for _ in range(6)]
    assert 429 not in results[:5]
    assert results[5] == 429


class _NeverCalled:
    def __getattr__(self, name: str) -> Any:
        raise AssertionError(f"Redis was called ({name}) although no limit applies")


@pytest.mark.req("FR-452")
def test_with_no_limit_the_request_is_admitted_and_redis_is_never_called(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Case 6."""
    keys, _ = _account(client, admin_headers, environments=["uat"])
    client.app.state.rate_limiter._client = _NeverCalled()  # type: ignore[attr-defined]

    assert 429 not in [_score(client, keys["uat"]) for _ in range(20)]


def _unenforced(environment: str) -> float:
    return (
        metrics.REGISTRY.get_sample_value(
            "gip_rate_limit_unenforced_total", {"environment": environment}
        )
        or 0.0
    )


@pytest.mark.req("FR-452")
def test_a_redis_outage_admits_counts_and_logs_each_request(
    client: TestClient, admin_headers: dict[str, str], caplog: pytest.LogCaptureFixture
) -> None:
    """Case 7. The Redis URL points at a closed port."""
    keys, _ = _account(client, admin_headers, environments=["uat"], rate_limit_rps=1)
    client.app.state.rate_limiter = RateLimiter(  # type: ignore[attr-defined]
        build_redis_client("redis://127.0.0.1:1/0"), clock=lambda: FIXED_SECOND
    )
    before = _unenforced("uat")

    with caplog.at_level(logging.WARNING, logger="app.platform.rate_limit"):
        results = [_score(client, keys["uat"]) for _ in range(4)]

    assert 429 not in results
    assert _unenforced("uat") - before == 4
    warnings = [r for r in caplog.records if r.name == "app.platform.rate_limit"]
    assert len(warnings) == 4
    for record in warnings:
        assert "premium_in" not in record.getMessage()
        assert "ConnectionError" in record.getMessage()


@pytest.mark.req("FR-452")
def test_without_the_fail_open_guard_an_outage_is_a_500(
    client: TestClient,
    admin_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Case 7's red on broken input: the guard is disabled and the request fails."""

    class _NothingError(Exception):
        pass

    monkeypatch.setattr(rate_limit, "RedisError", _NothingError)
    keys, _ = _account(client, admin_headers, environments=["uat"], rate_limit_rps=1)
    client.app.state.rate_limiter = RateLimiter(  # type: ignore[attr-defined]
        build_redis_client("redis://127.0.0.1:1/0"), clock=lambda: FIXED_SECOND
    )

    assert _score(client, keys["uat"]) == 500


@pytest.mark.req("FR-452")
async def test_a_request_refused_at_authentication_or_authorisation_is_not_counted(
    client: TestClient, admin_headers: dict[str, str], database: Database
) -> None:
    """Case 8: 401 and 403 leave the count unchanged."""
    keys, account = _account(
        client,
        admin_headers,
        environments=["uat"],
        rate_limit_rps=1,
        permissions=("score:batch",),
    )
    key = RateLimiter.key("score", "uat", "service_account", UUID(account["id"]), int(FIXED_SECOND))
    redis = build_redis_client(client.app.state.settings.redis_url.get_secret_value())  # type: ignore[attr-defined]
    try:
        forbidden = client.post(SCORE_URL, json=QUOTE, headers=keys["uat"])
        assert forbidden.status_code == 403
        unauthenticated = client.post(
            SCORE_URL,
            json=QUOTE,
            headers={"X-API-Key": "gip_uat_nope_nope", "Workspace-Id": keys["uat"]["Workspace-Id"]},
        )
        assert unauthenticated.status_code == 401
        assert await redis.get(key) is None
    finally:
        await redis.aclose()


_EXPIRY_PRINCIPAL = Principal(kind=ActorKind.SERVICE_ACCOUNT, id=UUID(int=8051), display="expiry")


@pytest.mark.req("FR-452")
async def test_an_admitted_request_leaves_a_key_with_a_bounded_expiry(
    api_settings: Settings,
) -> None:
    """FD 8049: the counter key must expire, or old windows never leave Redis.

    Red on broken input: with `pipe.expire` removed `PTTL` is -1.
    """
    redis = build_redis_client(api_settings.redis_url.get_secret_value())
    limiter = RateLimiter(redis, clock=lambda: FIXED_SECOND)
    key = RateLimiter.key(
        "expiry-pttl", "uat", "service_account", _EXPIRY_PRINCIPAL.id, int(FIXED_SECOND)
    )
    try:
        await redis.delete(key)
        assert await limiter.admit("expiry-pttl", "uat", _EXPIRY_PRINCIPAL, 1)
        pttl = await redis.pttl(key)
        assert 0 < pttl <= rate_limit._KEY_TTL_SECONDS * 1000
    finally:
        await redis.delete(key)
        await redis.aclose()


@pytest.mark.req("FR-452")
async def test_an_expired_key_is_gone_and_the_next_admit_counts_one(
    api_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FD 8049: with a 1 s expiry the key disappears, and the counter restarts at 1.

    A bounded `EXISTS` poll (deadline 3 s), never a fixed sleep. Red on broken input: with
    `pipe.expire` removed the key never goes and the second admit counts 2.
    """
    monkeypatch.setattr(rate_limit, "_KEY_TTL_SECONDS", 1)
    redis = build_redis_client(api_settings.redis_url.get_secret_value())
    limiter = RateLimiter(redis, clock=lambda: FIXED_SECOND)
    key = RateLimiter.key(
        "expiry-gone", "uat", "service_account", _EXPIRY_PRINCIPAL.id, int(FIXED_SECOND)
    )
    try:
        await redis.delete(key)
        assert await limiter.admit("expiry-gone", "uat", _EXPIRY_PRINCIPAL, 1)
        deadline = time.monotonic() + 3.0
        while await redis.exists(key) and time.monotonic() < deadline:
            await asyncio.sleep(0.05)
        assert not await redis.exists(key), "the key outlived its 1 s expiry by more than 3 s"
        assert await limiter.admit("expiry-gone", "uat", _EXPIRY_PRINCIPAL, 1)
        assert await redis.get(key) == b"1"
    finally:
        await redis.delete(key)
        await redis.aclose()


@pytest.mark.req("FR-452")
def test_the_429_is_declared_in_the_score_operation_of_the_openapi_document(
    client: TestClient,
) -> None:
    operation = client.get("/openapi.json").json()["paths"]["/api/v1/score"]["post"]
    assert "429" in operation["responses"]


@pytest.mark.req("FR-452")
@pytest.mark.skipif(
    os.environ.get("GIP_MEASURE_RATE_LIMIT") != "1",
    reason="Case 9 is a measurement, run in a gate slot with GIP_MEASURE_RATE_LIMIT=1",
)
async def test_case_9_measures_the_limiters_own_cost(
    api_settings: Settings, capsys: pytest.CaptureFixture[str]
) -> None:
    """Measured and quoted, not gated (RL-1347 case 9): p50 and p99 over 10,000 calls."""
    limiter = RateLimiter(build_redis_client(api_settings.redis_url.get_secret_value()))
    principal = Principal(kind=ActorKind.SERVICE_ACCOUNT, id=UUID(int=9), display="measure")
    samples: list[float] = []
    try:
        for _ in range(10_000):
            started = time.perf_counter()
            await limiter.admit("measure", "uat", principal, 10**9)
            samples.append((time.perf_counter() - started) * 1000)
    finally:
        await limiter._client.aclose()
    ordered = sorted(samples)
    p50 = statistics.median(ordered)
    p99 = ordered[int(len(ordered) * 0.99) - 1]
    with capsys.disabled():
        print(f"\nRATE_LIMIT_CASE_9 calls=10000 p50_ms={p50:.3f} p99_ms={p99:.3f}")
