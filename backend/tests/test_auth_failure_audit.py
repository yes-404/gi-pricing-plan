"""A failed authentication is recorded and its record survives the refusal (FR-392).

PL-1739 / SL-1740 (FD-1727). Every test goes through the HTTP harness, so the 401 escapes
the request exactly as in production; none calls `authenticate_api_key` inside a unit of
work that would swallow the raise and commit. The API-key row is written on the request's own
session after it rolls back (DP-1 (b), ruled 2026-10-17 14:41:18); the bearer path keeps a
separate unit (DP-1 (i)) but a rejected token resolves to no workspace, so it writes no row.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_keys import generate_key, parse_key
from app.config import Settings
from app.db.models import ApiKeyRow, AuditEventRow, ServiceAccountRow
from app.db.session import Database
from app.main import create_app
from app.observability.metrics import REGISTRY
from model_schema import new_uuid7

pytestmark = pytest.mark.req("FR-392")

ROUTE = "/api/v1/environments"
METRIC = "gip_auth_failures_total"
EIGHT_REASONS = {
    "malformed_key",
    "invalid_key",
    "account_archived",
    "key_revoked",
    "key_expired",
    "environment_not_granted",
    "bearer_expired",
    "bearer_rejected",
}


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


async def _key(
    database: Database,
    workspace_id: UUID,
    *,
    revoked: bool = False,
    expired: bool = False,
    archived: bool = False,
    environments: list[str] | None = None,
) -> tuple[str, str, ServiceAccountRow]:
    """A Service Account with one key; returns (full token, secret, account).

    The account holds `settings:read`, the permission `GET /api/v1/environments` requires
    (`api/environments.py:36`). With only `score:execute` a valid key authenticates and is
    then refused `403` by the route, so R4's valid-key control could never reach `200`.
    """
    envs = environments or ["prod"]
    async with database.unit_of_work() as session:
        account = ServiceAccountRow(
            workspace_id=workspace_id,
            slug=f"acct-{new_uuid7().hex[-12:]}",
            environments=envs,
            permissions=["settings:read"],
            archived_at=datetime.now(UTC) if archived else None,
        )
        session.add(account)
        await session.flush()
        generated = generate_key(envs[0])
        session.add(
            ApiKeyRow(
                service_account_id=account.id,
                prefix=generated.prefix,
                secret_hash=generated.secret_hash,
                environment=generated.environment,
                expires_at=datetime.now(UTC) + timedelta(days=-1 if expired else 365),
                revoked_at=datetime.now(UTC) if revoked else None,
            )
        )
        await session.flush()
        parsed = parse_key(generated.value)
        assert parsed is not None
        return generated.value, parsed.secret, account


def _get(client: TestClient, token: str, scheme: str = "ApiKey"):
    return client.get(ROUTE, headers={"Authorization": f"{scheme} {token}"})


def _count(reason: str) -> float:
    return REGISTRY.get_sample_value(METRIC, {"reason": reason}) or 0.0


async def _failure_rows(database: Database, workspace_id: UUID) -> list[AuditEventRow]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == "principal.auth_failed",
                    )
                )
            ).scalars()
        )


async def _all_events(database: Database) -> int:
    async with database.session() as session:
        return (await session.execute(select(func.count()).select_from(AuditEventRow))).scalar_one()


# -- R1 to R3: the row survives the 401 ----------------------------------------------------


async def test_r1_a_revoked_key_leaves_one_audit_row(
    client: TestClient, database: Database, workspace_id
) -> None:
    token, _, _ = await _key(database, workspace_id, revoked=True)

    response = _get(client, token)

    assert response.status_code == 401
    rows = await _failure_rows(database, workspace_id)
    assert len(rows) == 1
    assert rows[0].after == {"reason": "key revoked"}
    assert rows[0].trace_id == response.headers["x-trace-id"]


async def test_r2_an_expired_key_leaves_one_audit_row(
    client: TestClient, database: Database, workspace_id
) -> None:
    token, _, _ = await _key(database, workspace_id, expired=True)

    response = _get(client, token)

    assert response.status_code == 401
    assert response.json()["code"] == "API_KEY_EXPIRED"
    rows = await _failure_rows(database, workspace_id)
    assert len(rows) == 1
    assert rows[0].after == {"reason": "key expired"}


async def test_r3_an_archived_account_leaves_one_audit_row(
    client: TestClient, database: Database, workspace_id
) -> None:
    token, _, _ = await _key(database, workspace_id, archived=True)

    assert _get(client, token).status_code == 401
    rows = await _failure_rows(database, workspace_id)
    assert len(rows) == 1
    assert rows[0].after == {"reason": "service account archived"}


async def test_r3_an_environment_not_granted_leaves_one_audit_row(
    client: TestClient, database: Database, workspace_id
) -> None:
    token, _, _ = await _key(database, workspace_id, environments=["uat"])
    forged = token.replace("gip_uat_", "gip_prod_", 1)
    assert forged != token

    assert _get(client, forged).status_code in (401, 403)
    rows = await _failure_rows(database, workspace_id)
    assert len(rows) == 1
    assert rows[0].after == {"reason": "environment not granted"}


# -- R4: the guard -------------------------------------------------------------------------


async def test_r4_a_valid_key_writes_no_failure_row(
    client: TestClient, database: Database, workspace_id
) -> None:
    token, _, _ = await _key(database, workspace_id)

    response = _get(client, token)

    assert response.status_code == 200, response.text
    assert await _failure_rows(database, workspace_id) == []


# -- R5, R6: every failure is counted ------------------------------------------------------


async def test_r5_workspace_less_failures_are_counted_and_not_audited(
    client: TestClient, database: Database, workspace_id
) -> None:
    token, _, _ = await _key(database, workspace_id)
    parsed = parse_key(token)
    assert parsed is not None
    wrong_secret = f"gip_{parsed.environment}_{parsed.prefix}_" + "x" * 64
    cases = [
        ("malformed_key", "not-a-key"),
        ("invalid_key", generate_key("prod").value),
        ("invalid_key", wrong_secret),
    ]
    for reason, presented in cases:
        events_before, count_before = await _all_events(database), _count(reason)

        assert _get(client, presented).status_code == 401

        assert _count(reason) - count_before == 1
        assert await _all_events(database) == events_before


async def test_r6_keyed_failures_are_counted_too(
    client: TestClient, database: Database, workspace_id
) -> None:
    revoked, _, _ = await _key(database, workspace_id, revoked=True)
    expired, _, _ = await _key(database, workspace_id, expired=True)
    for reason, token in (("key_revoked", revoked), ("key_expired", expired)):
        before = _count(reason)

        assert _get(client, token).status_code == 401

        assert _count(reason) - before == 1


# -- R7: the bearer path -------------------------------------------------------------------


def test_r7_a_rejected_bearer_token_is_counted_and_logged_at_warning(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    before = _count("bearer_rejected")
    with caplog.at_level(logging.DEBUG, logger="app.auth"):
        response = _get(client, "garbage.token.value", scheme="Bearer")

    assert response.status_code == 401
    assert _count("bearer_rejected") - before == 1
    lines = [r for r in caplog.records if r.name == "app.auth" and "reason" in r.__dict__]
    assert lines
    assert all(r.levelno == logging.WARNING for r in lines)
    assert all("action" in r.__dict__ for r in lines)


# -- R8: a lost failure row is a 5xx, and still counted ------------------------------------


async def test_r8_a_failing_failure_audit_is_a_5xx_and_still_counted(
    client: TestClient, database: Database, workspace_id, monkeypatch: pytest.MonkeyPatch
) -> None:
    token, _, _ = await _key(database, workspace_id, revoked=True)

    async def boom(*args, **kwargs):
        raise RuntimeError("audit store down")

    monkeypatch.setattr("app.platform.audit.record", boom)
    before = _count("key_revoked")

    response = _get(client, token)

    assert _count("key_revoked") - before == 1
    assert response.status_code >= 500


async def test_r8_a_failing_commit_of_the_failure_row_is_a_5xx_and_leaves_no_row(
    client: TestClient, database: Database, workspace_id, monkeypatch: pytest.MonkeyPatch
) -> None:
    """DP-2 F1 for the request-session commit: a lost commit is never swallowed into a 401."""
    token, _, _ = await _key(database, workspace_id, revoked=True)

    async def boom(self: AsyncSession) -> None:
        raise RuntimeError("commit failed")

    monkeypatch.setattr(AsyncSession, "commit", boom)

    response = _get(client, token)

    assert response.status_code >= 500
    monkeypatch.undo()
    assert await _failure_rows(database, workspace_id) == []


async def test_r8_a_failing_audit_write_on_the_bearer_path_cannot_arise(
    client: TestClient, database: Database
) -> None:
    """A rejected token resolves to no workspace, so the bearer path writes no row at all."""
    before = await _all_events(database)

    assert _get(client, "garbage.token.value", scheme="Bearer").status_code == 401

    assert await _all_events(database) == before


async def test_r11_a_failed_api_key_request_never_holds_two_pool_connections(
    client: TestClient, database: Database, workspace_id
) -> None:
    """SL-1455's one-connection rule (`deps.py` `require_caller` docstring), on the failure path.

    The checkout counting pattern of `test_score_request_cost.py`, with check-in as well: the
    rollback returns the connection before the audit write takes one, so the two are
    sequential and at most one is ever held.
    """
    token, _, _ = await _key(database, workspace_id, revoked=True)
    engine = client.app.state.database.engine.sync_engine  # type: ignore[attr-defined]
    seen = {"held": 0, "max_held": 0, "checkouts": 0}

    def _checkout(*_args: object, **_kwargs: object) -> None:
        seen["checkouts"] += 1
        seen["held"] += 1
        seen["max_held"] = max(seen["max_held"], seen["held"])

    def _checkin(*_args: object, **_kwargs: object) -> None:
        seen["held"] -= 1

    event.listen(engine, "checkout", _checkout)
    event.listen(engine, "checkin", _checkin)
    try:
        response = _get(client, token)
    finally:
        event.remove(engine, "checkout", _checkout)
        event.remove(engine, "checkin", _checkin)

    assert response.status_code == 401
    assert seen["max_held"] == 1, seen
    # R11 (a): the rollback returns the connection, the audit write takes exactly one more.
    # The success path total of 1 is held by `test_score_request_cost.py` (MAX_CHECKOUTS) on
    # /score; `GET /environments` takes three (its handler opens its own sessions).
    assert seen["checkouts"] == 2, seen
    assert len(await _failure_rows(database, workspace_id)) == 1


# -- R9: no secret in any failure row, and the rows exist ----------------------------------


@pytest.mark.req("NFR-532")
@pytest.mark.req("FR-375")
async def test_r9_no_failure_event_contains_a_key_secret(
    client: TestClient, database: Database, workspace_id
) -> None:
    keys = [
        await _key(database, workspace_id, revoked=True),
        await _key(database, workspace_id, expired=True),
        await _key(database, workspace_id, archived=True),
        await _key(database, workspace_id, environments=["uat"]),
    ]
    presented = [k[0] for k in keys]
    presented[3] = presented[3].replace("gip_uat_", "gip_prod_", 1)
    for token in presented:
        assert _get(client, token).status_code in (401, 403)

    rows = await _failure_rows(database, workspace_id)
    assert len(rows) == 4
    for row in rows:
        text = " ".join(str(v) for v in (row.before, row.after, row.entity_ref, row.action))
        for token, secret, _ in keys:
            assert secret not in text
            assert token not in text


# -- R10: the closed label set -------------------------------------------------------------


async def test_r10_the_label_set_is_closed_and_carries_no_key_material(
    client: TestClient,
    database: Database,
    workspace_id,
    caplog: pytest.LogCaptureFixture,
) -> None:
    keys = [
        await _key(database, workspace_id, revoked=True),
        await _key(database, workspace_id, expired=True),
        await _key(database, workspace_id, archived=True),
    ]
    with caplog.at_level(logging.DEBUG, logger="app.auth"):
        for token, _, _ in keys:
            _get(client, token)
        _get(client, "not-a-key")
        _get(client, generate_key("prod").value)
        _get(client, "garbage.token.value", scheme="Bearer")

    samples = [s for family in REGISTRY.collect() for s in family.samples if s.name == METRIC]
    assert samples
    for sample in samples:
        assert set(sample.labels) == {"reason"}
        assert sample.labels["reason"] in EIGHT_REASONS
    values = " ".join(v for s in samples for v in s.labels.values())
    logged = " ".join(
        r.getMessage() + str(r.__dict__) for r in caplog.records if r.name == "app.auth"
    )
    for token, secret, account in keys:
        parsed = parse_key(token)
        assert parsed is not None
        for needle in (secret, token, parsed.prefix, str(account.id), account.slug):
            assert needle not in values
            assert needle not in logged

    from app.auth.service import AuthenticationFailed, AuthFailureReason, record_auth_failure

    assert {r.value for r in AuthFailureReason} == EIGHT_REASONS
    before = {s.labels["reason"]: s.value for s in samples}
    async with database.session() as session:
        with pytest.raises(ValueError, match="not a valid AuthFailureReason"):
            await record_auth_failure(
                session,
                AuthenticationFailed("API_KEY_INVALID", "raw detail"),  # type: ignore[arg-type]
            )
    after = {
        s.labels["reason"]: s.value
        for family in REGISTRY.collect()
        for s in family.samples
        if s.name == METRIC
    }
    assert after == before
