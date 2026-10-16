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


#: The two identity-level routes (`RL-1687` (2a), precised by the maintainer's (by delegation)
#: entry "2026-10-16 10:31:43 BST", DP-S4-ME (A)): a principal reaches them before it has a
#: workspace selection, so they are counted with `workspace_id=None` and the Setting resolves
#: without the workspace layer (environment variable, then Environment, then the default).
#: Each carries the request that is answered `200`.
_IDENTITY_ROUTES = [
    pytest.param("GET", "/api/v1/me/workspaces", lambda workspace_id: None, id="me-workspaces"),
    pytest.param(
        "POST",
        "/api/v1/me/workspace",
        lambda workspace_id: {"workspace_id": str(workspace_id)},
        id="me-workspace",
    ),
]
_ENV_LIMIT_VARIABLE = "GIP_SETTING_PLATFORM_DEFAULT_MANAGEMENT_RATE_LIMIT_RPS"


@pytest.mark.req("FR-452")
@pytest.mark.parametrize(("method", "url", "body"), _IDENTITY_ROUTES)
async def test_an_identity_route_is_counted_once(
    client: TestClient,
    workspace_id: UUID,
    admin_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    url: str,
    body: Any,
) -> None:
    """DP-S4-ME (A): `GET /me/workspaces` and `POST /me/workspace` move the management counter
    by exactly one. The limit comes from the environment-variable layer (a workspace override
    does not apply to these routes), so the counter is called with the default-or-env limit.
    Red: the route takes `IdentityDep` and is never counted, so the counter does not move (0)."""
    monkeypatch.setenv(_ENV_LIMIT_VARIABLE, "1000")
    calls = _spy_management_count(client, monkeypatch)
    identity_headers = {DEV_PRINCIPAL_HEADER: admin_headers[DEV_PRINCIPAL_HEADER]}

    before = len(calls)
    answered = client.request(method, url, json=body(workspace_id), headers=identity_headers)
    after = len(calls)

    assert answered.status_code == 200, answered.text
    assert after - before == 1


@pytest.mark.req("FR-452")
@pytest.mark.parametrize(("method", "url", "body"), _IDENTITY_ROUTES)
async def test_an_identity_route_ignores_a_workspace_override(
    client: TestClient,
    workspace_id: UUID,
    admin_headers: dict[str, str],
    set_limit: Any,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    url: str,
    body: Any,
) -> None:
    """DP-S4-ME (A): the workspace layer is skipped, so a workspace limit of 1 does not refuse
    the second call and the counter is not asked (the default is unset: no limit, no counter
    call). Red: the route resolves a workspace (a membership chosen for the principal) and the
    override of 1 turns the second call into `429`."""
    await set_limit(1)
    calls = _spy_management_count(client, monkeypatch)
    identity_headers = {DEV_PRINCIPAL_HEADER: admin_headers[DEV_PRINCIPAL_HEADER]}

    statuses = [
        client.request(method, url, json=body(workspace_id), headers=identity_headers).status_code
        for _ in range(3)
    ]

    assert statuses == [200, 200, 200]
    assert calls == []


@pytest.mark.req("FR-452")
@pytest.mark.parametrize(("method", "url", "body"), _IDENTITY_ROUTES)
async def test_an_identity_route_keeps_the_process_variable_layer(
    client: TestClient,
    workspace_id: UUID,
    admin_headers: dict[str, str],
    set_limit: Any,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    url: str,
    body: Any,
) -> None:
    """Only the workspace layer is skipped (the lead's message, pending the maintainer's
    confirmation): the process-variable layer (FR-446, `GIP_SETTING_<KEY>`) still applies, and
    it outranks a workspace value. Process variable 1 with a workspace override of 1000: the
    second call is `429`. Red: the whole resolve is skipped (no limit), or the workspace value
    is read, and the second call is `200`."""
    await set_limit(1000)
    monkeypatch.setenv(_ENV_LIMIT_VARIABLE, "1")
    identity_headers = {DEV_PRINCIPAL_HEADER: admin_headers[DEV_PRINCIPAL_HEADER]}

    first = client.request(method, url, json=body(workspace_id), headers=identity_headers)
    second = client.request(method, url, json=body(workspace_id), headers=identity_headers)

    assert first.status_code == 200, first.text
    assert second.status_code == 429, second.text


class _StubVerifier:
    """Fixed claims for a bearer caller (as `test_workspace_identity.py`'s stub)."""

    def __init__(self, subject: str) -> None:
        from app.auth.oidc import TokenClaims

        self._claims = TokenClaims(
            subject=subject, email="b.bearer@insurer.example", name="B Bearer", groups=(), raw={}
        )

    @property
    def issuer(self) -> str:
        return "https://idp.test.example/realms/gip"

    def verify(self, token: str) -> Any:
        return self._claims


@pytest.mark.req("FR-452")
@pytest.mark.parametrize(("method", "url", "body"), _IDENTITY_ROUTES)
async def test_an_identity_route_is_counted_once_for_a_bearer_caller(
    client: TestClient,
    database: Database,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    url: str,
    body: Any,
) -> None:
    """A BEARER caller (no Environment: `RL-1687` (2a) skips that layer for it) is counted once
    per identity route, the limit resolving process variable -> default (the maintainer's
    (by delegation) entries "2026-10-16 10:31:43 BST" and "10:36:38 BST", Q2). With the process
    variable at 1, the second call is `429`. Red: the route is never counted (0 calls, no 429)."""
    from app.auth.service import authenticate_bearer
    from app.db.models import WorkspaceMemberRow
    from model_schema import new_uuid7

    subject = f"bearer-{new_uuid7().hex[-12:]}"
    verifier = _StubVerifier(subject)
    member_of = new_uuid7()
    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, verifier, "t")
        await workspaces.ensure_workspace(session, workspace_id=member_of)
        session.add(WorkspaceMemberRow(user_id=identity.principal.id, workspace_id=member_of))
    client.app.state.oidc_verifier = verifier  # type: ignore[attr-defined]
    headers = {"Authorization": "Bearer t"}
    calls = _spy_management_count(client, monkeypatch)

    monkeypatch.setenv(_ENV_LIMIT_VARIABLE, "1000")
    before = len(calls)
    answered = client.request(method, url, json=body(member_of), headers=headers)
    assert answered.status_code == 200, answered.text
    assert len(calls) - before == 1

    monkeypatch.setenv(_ENV_LIMIT_VARIABLE, "1")
    refused = client.request(method, url, json=body(member_of), headers=headers)
    assert refused.status_code == 429, refused.text
