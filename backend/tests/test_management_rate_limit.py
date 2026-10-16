"""FR-452's management-API rate limit (`RL-1687`, WK-674 Slice 4, `PL-1690` E4.1).

Real Redis throughout, the clock pinned (as `test_score_rate_limit.py`). A request that passes the
limit is anything but `429`; the routes used are `GET /api/v1/jobs` (a permission, `job:read`) and
`GET /api/v1/me` (authenticated, no permission), the two shapes of dependency that count.

Each test is red on the break it exists for, named in its docstring.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Settings
from app.db.models import WorkspaceSettingRow
from app.db.session import Database
from app.main import create_app
from app.platform import rate_limit, workspaces
from app.platform import settings as svc

LIMIT_KEY = "platform.default_management_rate_limit_rps"
JOBS_URL = "/api/v1/jobs"
ME_URL = "/api/v1/me"
FIXED_SECOND = 1_800_000_000.0
QUOTE = {
    "purpose": "new_business",
    "quoted_at": "2026-08-30T09:00:00Z",
    "effective_date": "2026-09-01",
    "inputs": {"premium_in": 1000},
    "options": {"rating_version_ref": None},
}


@pytest.fixture
def client(api_settings: Settings, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(rate_limit, "_KEY_TTL_SECONDS", 3600)
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as test_client:
        test_client.app.state.rate_limiter.clock = lambda: FIXED_SECOND  # type: ignore[attr-defined]
        yield test_client


@pytest_asyncio.fixture
async def admin_headers(workspace_id: UUID, principal: Any, grant: Any) -> dict[str, str]:
    await grant("admin")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def set_limit(database: Database, workspace_id: UUID) -> Any:
    """Set the management Setting for the workspace; removed afterwards."""

    async def _set(value: int) -> None:
        async with database.unit_of_work() as session:
            await workspaces.ensure_workspace(session, workspace_id=workspace_id)
            await svc.set_workspace_setting(session, workspace_id, LIMIT_KEY, value)

    yield _set
    async with database.unit_of_work() as session:
        await session.execute(
            delete(WorkspaceSettingRow).where(WorkspaceSettingRow.workspace_id == workspace_id)
        )


def _account(
    client: TestClient,
    headers: dict[str, str],
    *,
    permissions: tuple[str, ...],
    rate_limit_rps: int | None = None,
    slug: str = "managed-client",
) -> dict[str, str]:
    """Create a Service Account in `uat`; return its API-key headers."""
    body: dict[str, Any] = {
        "slug": slug,
        "environments": ["uat"],
        "permissions": list(permissions),
    }
    if rate_limit_rps is not None:
        body["rate_limit_rps"] = rate_limit_rps
    created = client.post("/api/v1/service-accounts", json=body, headers=headers)
    assert created.status_code == 201, created.text
    key = created.json()["keys"][0]
    return {"X-API-Key": key["key"], "Workspace-Id": headers["Workspace-Id"]}


@pytest.mark.req("FR-452")
async def test_management_rate_limit_counts_and_refuses(
    client: TestClient, admin_headers: dict[str, str], set_limit: Any
) -> None:
    """Limit 2: the third management read inside one window is `429 RATE_LIMITED` with
    `Retry-After: 1`. Red: no limit applied, the third read answers 200."""
    await set_limit(2)

    first = [client.get(JOBS_URL, headers=admin_headers).status_code for _ in range(2)]
    assert 429 not in first
    refused = client.get(JOBS_URL, headers=admin_headers)
    assert refused.status_code == 429
    assert refused.headers["Retry-After"] == "1"
    assert refused.json()["code"] == "RATE_LIMITED"
    # One counter for the whole management API: a different route spends the same budget, and
    # a route that declares no permission is counted too.
    assert client.get(ME_URL, headers=admin_headers).status_code == 429


@pytest.mark.req("FR-452")
async def test_management_rate_limit_is_separate_from_scoring(
    client: TestClient, admin_headers: dict[str, str], set_limit: Any
) -> None:
    """With the management limit exhausted, `POST /score` by the same Principal, under its own
    limit, is admitted. Red: one shared counter."""
    headers = _account(
        client, admin_headers, permissions=("score:execute", "job:read"), rate_limit_rps=5
    )
    await set_limit(1)

    assert client.get(JOBS_URL, headers=headers).status_code != 429
    assert client.get(JOBS_URL, headers=headers).status_code == 429
    # Admitted by the limiter: it reaches the handler and is refused there for a reason that has
    # nothing to do with the limit (no live Rating Version).
    assert client.post("/api/v1/score", json=QUOTE, headers=headers).status_code != 429


@pytest.mark.req("FR-452")
async def test_management_rate_limit_ignores_the_accounts_scoring_rate(
    client: TestClient, admin_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """(3a): an account with `rate_limit_rps` = 1 and the Setting unset makes three management
    calls in one window: all admitted, and Redis is not called. Red: the account's rate applied
    to the management counter."""
    headers = _account(client, admin_headers, permissions=("job:read",), rate_limit_rps=1)
    calls: list[str] = []
    limiter = client.app.state.rate_limiter  # type: ignore[attr-defined]
    real_admit = limiter.admit

    async def admit(route: str, *args: Any, **kwargs: Any) -> bool:
        calls.append(route)
        return bool(await real_admit(route, *args, **kwargs))

    monkeypatch.setattr(limiter, "admit", admit)

    statuses = [client.get(JOBS_URL, headers=headers).status_code for _ in range(3)]
    assert 429 not in statuses
    assert calls == []


@pytest.mark.req("FR-452")
async def test_management_rate_limit_never_counts_an_unauthenticated_or_refused_request(
    client: TestClient, admin_headers: dict[str, str], set_limit: Any
) -> None:
    """No Principal, no count: `GET /auth/config` past the limit is never refused, and a `403`
    leaves the count unchanged. Red: counted before authentication or before the permission
    check, so the second `403` becomes `429`."""
    headers = _account(client, admin_headers, permissions=("score:execute",))
    await set_limit(1)

    assert [client.get("/api/v1/auth/config").status_code for _ in range(4)] == [200] * 4
    # `job:read` is not held: every call is a 403, never a counted 429.
    assert [client.get(JOBS_URL, headers=headers).status_code for _ in range(3)] == [403] * 3
    # The count is still untouched: the principal's first permitted read is admitted.
    assert client.get(ME_URL, headers=headers).status_code != 429


def _spy_management_count(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Record each time the limiter is asked to admit a management request (the counter)."""
    calls: list[str] = []
    limiter = client.app.state.rate_limiter  # type: ignore[attr-defined]
    real_admit = limiter.admit

    async def admit(route: str, *args: Any, **kwargs: Any) -> bool:
        calls.append(route)
        return bool(await real_admit(route, *args, **kwargs))

    monkeypatch.setattr(limiter, "admit", admit)
    return calls


#: The three routes whose permission is decided inside the handler's service (`RL-1687` (1a):
#: "a 401 or a 403 is never counted"), each with the one permission that admits it and the
#: status a permitted call ends in (a ghost Rating Version is a 404 *after* the permission).
_IN_HANDLER_ROUTES = [
    pytest.param(
        "/api/v1/validation-rules",
        lambda: {
            "slug": "counted-rule",
            "layer": "structural",
            "check": "not_null",
            "severity": "fail",
            "target": {"table": "exposure", "column": "policy_id"},
            "params": {"columns": ["policy_id"], "key_columns": ["policy_id"]},
        },
        "dataset:write",
        201,
        id="validation-rules",
    ),
    pytest.param(
        "/api/v1/environments/uat/deployment-requests",
        lambda: {"rating_version_ref": "rating_version:ghost@1", "change_summary": "review"},
        "deployment:promote",
        404,
        id="deployment-requests",
    ),
    pytest.param(
        "/api/v1/environments/uat/deployments",
        lambda: {"rating_version_ref": "rating_version:ghost@1", "reason": "release"},
        "deployment:promote",
        404,
        id="deployments",
    ),
]


@pytest.mark.req("FR-452")
@pytest.mark.parametrize(("url", "body", "permission", "permitted_status"), _IN_HANDLER_ROUTES)
async def test_a_403_from_an_in_handler_permission_check_is_not_counted(
    client: TestClient,
    admin_headers: dict[str, str],
    set_limit: Any,
    monkeypatch: pytest.MonkeyPatch,
    url: str,
    body: Any,
    permission: str,
    permitted_status: int,
) -> None:
    """A caller without the route's permission gets `403` and the management counter is
    unchanged (read before and after). Red: `counted_caller` counts at the dependency, before
    the handler's own check, so the refused call moves the counter by one."""
    await set_limit(1000)
    headers = _account(client, admin_headers, permissions=("job:read",), slug="refused-client")
    calls = _spy_management_count(client, monkeypatch)

    before = len(calls)
    refused = client.post(url, json=body(), headers=headers)
    after = len(calls)

    assert refused.status_code == 403, refused.text
    assert after == before


@pytest.mark.req("FR-452")
@pytest.mark.parametrize(("url", "body", "permission", "permitted_status"), _IN_HANDLER_ROUTES)
async def test_a_permitted_call_to_an_in_handler_permission_route_is_counted_once(
    client: TestClient,
    admin_headers: dict[str, str],
    set_limit: Any,
    monkeypatch: pytest.MonkeyPatch,
    url: str,
    body: Any,
    permission: str,
    permitted_status: int,
) -> None:
    """Positive control for the test above: a caller holding the permission moves the counter
    by exactly one, whatever the handler then answers. Red: the move to count-after-the-check
    drops the count (0) or doubles it (2)."""
    await set_limit(1000)
    headers = _account(client, admin_headers, permissions=(permission,), slug="permitted-client")
    calls = _spy_management_count(client, monkeypatch)

    before = len(calls)
    answered = client.post(url, json=body(), headers=headers)
    after = len(calls)

    assert answered.status_code == permitted_status, answered.text
    assert after - before == 1
