"""The identity-only dependency records and hides a failed authentication (FR-392).

PL-1739 / SL-1740, audit findings B2 and B3 (LG 8089). `GET /api/v1/me/workspaces` is served
by `require_identity` (`api/deps.py`), which has no request session and so records a failure
through `_record_failure_in_own_unit`, a path `test_auth_failure_audit.py` (which drives
`require_caller` through `/api/v1/environments`) never reaches. Every test goes through the
HTTP harness.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

import pytest
from backend.tests.test_auth_failure_audit import (
    _all_events,
    _count,
    _failure_rows,
    _key,
)
from fastapi.testclient import TestClient

from app.auth.api_keys import generate_key, parse_key
from app.auth.oidc import TokenRejectedError
from app.auth.service import AuthFailureReason
from app.config import Settings
from app.db.session import Database
from app.main import create_app

pytestmark = pytest.mark.req("FR-392")

IDENTITY_ROUTE = "/api/v1/me/workspaces"
CALLER_ROUTE = "/api/v1/environments"
# The detail `AuthenticationFailed` fixes for every reason (`auth/service.py`).
FIXED_DETAIL = "The credential presented was not accepted. Quote the trace id when reporting it."


@pytest.fixture
def client(api_settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


class _RejectingVerifier:
    """A verifier that rejects every token with the given reason text."""

    issuer = "https://issuer.test/"

    def __init__(self, reason: str) -> None:
        self._reason = reason

    def verify(self, token: str) -> None:
        raise TokenRejectedError(self._reason)


def _get(client: TestClient, route: str, authorization: str):
    return client.get(route, headers={"Authorization": authorization})


# -- B2: the identity-only dependency, both failure branches --------------------------------


def test_b2_a_rejected_bearer_on_the_identity_route_is_401_counted_and_writes_no_row(
    client: TestClient,
) -> None:
    before = _count("bearer_rejected")

    response = _get(client, IDENTITY_ROUTE, "Bearer garbage.token.value")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "UNAUTHENTICATED"
    assert body["detail"] == FIXED_DETAIL
    assert _count("bearer_rejected") - before == 1


async def test_b2_a_rejected_bearer_on_the_identity_route_leaves_the_audit_log_untouched(
    client: TestClient, database: Database
) -> None:
    """A rejected token resolves to no workspace, so there is no chain to write a row into."""
    events_before = await _all_events(database)

    assert _get(client, IDENTITY_ROUTE, "Bearer garbage.token.value").status_code == 401

    assert await _all_events(database) == events_before


async def test_b2_a_revoked_key_on_the_identity_route_is_401_and_leaves_one_audit_row(
    client: TestClient, database: Database, workspace_id
) -> None:
    token, _, _ = await _key(database, workspace_id, revoked=True)
    before = _count("key_revoked")

    response = _get(client, IDENTITY_ROUTE, f"ApiKey {token}")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "API_KEY_INVALID"
    assert body["detail"] == FIXED_DETAIL
    assert _count("key_revoked") - before == 1
    rows = await _failure_rows(database, workspace_id)
    assert len(rows) == 1
    assert rows[0].after == {"reason": "key revoked"}
    assert rows[0].trace_id == response.headers["x-trace-id"]


async def test_b2_a_valid_key_on_the_identity_route_writes_no_failure_row(
    client: TestClient, database: Database, workspace_id
) -> None:
    token, _, _ = await _key(database, workspace_id)

    response = _get(client, IDENTITY_ROUTE, f"ApiKey {token}")

    assert response.status_code == 200, response.text
    assert await _failure_rows(database, workspace_id) == []


# -- B3: no reason leaves the process in a 401 -----------------------------------------------


async def _presented(
    reason: AuthFailureReason, client: TestClient, database: Database, workspace_id
) -> str:
    """The `Authorization` header value that fails authentication with `reason`."""
    match reason:
        case AuthFailureReason.MALFORMED_KEY:
            return "ApiKey not-a-key"
        case AuthFailureReason.INVALID_KEY:
            return f"ApiKey {generate_key('prod').value}"
        case AuthFailureReason.ACCOUNT_ARCHIVED:
            return f"ApiKey {(await _key(database, workspace_id, archived=True))[0]}"
        case AuthFailureReason.KEY_REVOKED:
            return f"ApiKey {(await _key(database, workspace_id, revoked=True))[0]}"
        case AuthFailureReason.KEY_EXPIRED:
            return f"ApiKey {(await _key(database, workspace_id, expired=True))[0]}"
        case AuthFailureReason.ENVIRONMENT_NOT_GRANTED:
            token = (await _key(database, workspace_id, environments=["uat"]))[0]
            assert parse_key(token) is not None
            return "ApiKey " + token.replace("gip_uat_", "gip_prod_", 1)
        case AuthFailureReason.BEARER_EXPIRED:
            client.app.state.oidc_verifier = _RejectingVerifier("Signature has expired. Expired")
            return "Bearer expired-token"
        case AuthFailureReason.BEARER_REJECTED:
            return "Bearer garbage.token.value"


@pytest.mark.parametrize("route", [CALLER_ROUTE, IDENTITY_ROUTE])
@pytest.mark.parametrize("reason", list(AuthFailureReason), ids=lambda r: r.value)
async def test_b3_a_401_names_no_failure_reason_in_its_body_or_headers(
    client: TestClient,
    database: Database,
    workspace_id,
    reason: AuthFailureReason,
    route: str,
) -> None:
    """The reason is a metric label and an audit detail, never an answer to the caller.

    A reason in the response would tell an attacker which key exists or which check to fix.
    """
    authorization = await _presented(reason, client, database, workspace_id)
    before = _count(reason.value)

    response = _get(client, route, authorization)

    assert response.status_code in (401, 403)
    # The case that reached its reason: the counter moved, so the reason really was this one.
    assert _count(reason.value) - before == 1
    headers = " ".join(f"{k}: {v}" for k, v in response.headers.items())
    exposed = f"{response.text} {headers}"
    # A whole token, not a substring: the response `code` `API_KEY_EXPIRED` legitimately ends
    # in the member name `KEY_EXPIRED`, and that code is not the reason.
    for needle in (reason.value, reason.name):
        assert not re.search(rf"(?<![A-Za-z0-9_]){needle}(?![A-Za-z0-9_])", exposed, re.I), needle
