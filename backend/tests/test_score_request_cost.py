"""NFR-489's timing-free regression guard: what one warm `/score` request costs the database.

RL-1685 (PL-1454 DP-1) fixes the counted unit and both bounds. The unit is **one warm,
quoted request with `rating.trace_sample_rate` pinned at 0** (the setup of
`test_score.py`'s `test_a_quoted_outcome_at_rate_zero_persists_no_trace`): one request-scoped
read session serves every read, so the request takes at most `MAX_CHECKOUTS` pool checkouts,
and at most `MAX_STATEMENTS` SQL statements, which is the 10 the record counted with the
per-request `UPDATE api_keys` (DP-1 (b)) removed.

Counting checkouts and statements is deterministic. No wall-clock value is read, so the guard
cannot flake on a loaded machine, which a latency assertion on the shared VM does.
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from backend.tests.test_score import (  # noqa: F401  (fixtures, imported the way sibling files do)
    SCORE_URL,
    SCORED_REF,
    _quote,
    _rows_for,
    _set_trace_sample_rate,
    admin_headers,
    client,
    compiled_version,
    scoring_headers,
)
from fastapi.testclient import TestClient
from sqlalchemy import event, select, text, update

from app.api import score as score_module
from app.db.models import ApiKeyRow, ServiceAccountRow

pytestmark = pytest.mark.req("NFR-489")

#: RL-1685 Ruled 1 (a): one read session, so one checkout for a warm, quoted, unsampled request.
MAX_CHECKOUTS = 1
#: RL-1685 Ruled 1, Task 2's bounds: the record's 10 statements with the `UPDATE` removed.
MAX_STATEMENTS = 9


@pytest.fixture
def one_warm_request(
    client: TestClient,  # noqa: F811
    scoring_headers: dict[str, str],  # noqa: F811
    compiled_version: Any,  # noqa: F811
    database: Any,
    workspace_id: Any,
) -> Iterator[dict[str, int]]:
    """Counts of the second of two identical requests: the first warms the bundle slot.

    The sampling rate is pinned at 0 first, as the ruling's unit requires, and the counters
    are attached after the warm-up so only the measured request is counted.
    """
    asyncio.get_event_loop().run_until_complete(_set_trace_sample_rate(database, workspace_id, 0.0))
    body = _quote({"rating_version_ref": SCORED_REF})
    warm = client.post(SCORE_URL, json=body, headers=scoring_headers)
    assert warm.status_code == 200, warm.text

    engine = client.app.state.database.engine.sync_engine  # type: ignore[attr-defined]
    seen = {"checkouts": 0, "statements": 0}

    def _checkout(*_args: Any, **_kwargs: Any) -> None:
        seen["checkouts"] += 1

    def _statement(*_args: Any, **_kwargs: Any) -> None:
        seen["statements"] += 1

    event.listen(engine, "checkout", _checkout)
    event.listen(engine, "before_cursor_execute", _statement)
    try:
        measured = client.post(SCORE_URL, json=body, headers=scoring_headers)
        assert measured.status_code == 200, measured.text
        yield seen
    finally:
        event.remove(engine, "checkout", _checkout)
        event.remove(engine, "before_cursor_execute", _statement)


def test_a_warm_score_request_takes_one_pool_checkout(one_warm_request: dict[str, int]) -> None:
    assert one_warm_request["checkouts"] <= MAX_CHECKOUTS, one_warm_request


def test_a_warm_score_request_issues_at_most_nine_statements(
    one_warm_request: dict[str, int],
) -> None:
    assert one_warm_request["statements"] <= MAX_STATEMENTS, one_warm_request


# --- DP-1 (b): `last_used_at` is written only when it is None or older than 60 seconds ------


def _update_api_keys_during_one_request(
    client: TestClient,  # noqa: F811
    headers: dict[str, str],
) -> int:
    """The number of `UPDATE api_keys` statements one `/score` request issues, by text."""
    engine = client.app.state.database.engine.sync_engine  # type: ignore[attr-defined]
    texts: list[str] = []

    def _statement(_conn: Any, _cursor: Any, statement: str, *_rest: Any) -> None:
        texts.append(statement)

    event.listen(engine, "before_cursor_execute", _statement)
    try:
        response = client.post(
            SCORE_URL, json=_quote({"rating_version_ref": SCORED_REF}), headers=headers
        )
        assert response.status_code == 200, response.text
    finally:
        event.remove(engine, "before_cursor_execute", _statement)
    return sum(1 for t in texts if t.lstrip().upper().startswith("UPDATE API_KEYS"))


def _keys_of(workspace_id: Any) -> Any:
    """This test's keys: the database is shared across tests, so `api_keys` holds others."""
    return ApiKeyRow.service_account_id.in_(
        select(ServiceAccountRow.id).where(ServiceAccountRow.workspace_id == workspace_id)
    )


async def _set_last_used(database: Any, workspace_id: Any, age: timedelta) -> None:
    async with database.unit_of_work() as session:
        await session.execute(
            update(ApiKeyRow)
            .where(_keys_of(workspace_id))
            .values(last_used_at=datetime.now(UTC) - age)
        )


async def _last_used(database: Any, workspace_id: Any) -> datetime | None:
    async with database.session() as session:
        return (
            await session.execute(select(ApiKeyRow.last_used_at).where(_keys_of(workspace_id)))
        ).scalar_one()


def test_last_used_at_is_not_written_on_every_request(
    client: TestClient,  # noqa: F811
    scoring_headers: dict[str, str],  # noqa: F811
    compiled_version: Any,  # noqa: F811
    database: Any,
    workspace_id: Any,
) -> None:
    """Two requests inside the interval: the second issues no `UPDATE api_keys`."""
    asyncio.get_event_loop().run_until_complete(_set_trace_sample_rate(database, workspace_id, 0.0))
    asyncio.get_event_loop().run_until_complete(
        _set_last_used(database, workspace_id, timedelta(seconds=30))
    )
    assert _update_api_keys_during_one_request(client, scoring_headers) == 0


def test_last_used_at_is_written_once_the_interval_has_passed(
    client: TestClient,  # noqa: F811
    scoring_headers: dict[str, str],  # noqa: F811
    compiled_version: Any,  # noqa: F811
    database: Any,
    workspace_id: Any,
) -> None:
    """Past the 60 s interval the write happens, exactly once, and advances the stamp.

    Green before the fix (the write is per request); it guards the other side of DP-1 (b),
    so a fix that stops writing `last_used_at` at all cannot pass.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_set_trace_sample_rate(database, workspace_id, 0.0))
    stale = timedelta(seconds=120)
    loop.run_until_complete(_set_last_used(database, workspace_id, stale))
    before = loop.run_until_complete(_last_used(database, workspace_id))
    assert before is not None
    assert _update_api_keys_during_one_request(client, scoring_headers) == 1
    after = loop.run_until_complete(_last_used(database, workspace_id))
    assert after is not None
    assert after > before + timedelta(seconds=60)


# --- RL-1685 Ruled 1 (a), binding condition: a failed sampling-rate read never fails a quote --


async def _poison_session(session: Any) -> None:
    """A real statement failure: it aborts the transaction, as on a shared session."""
    await session.execute(text("SELECT 1/0"))


@pytest.mark.req("FR-259")
@pytest.mark.parametrize("failure", ["raises", "aborts_the_transaction"])
def test_a_failed_sampling_rate_read_degrades_to_not_sampled(
    failure: str,
    client: TestClient,  # noqa: F811
    scoring_headers: dict[str, str],  # noqa: F811
    compiled_version: Any,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
    database: Any,
    workspace_id: Any,
) -> None:
    """The failure is injected at the sampling-rate read, wherever it lives.

    It is injected on `settings_service.resolve` for `rating.trace_sample_rate` only (the
    FR-452 limit read goes through the same function and must keep working), so the test
    follows the read to its new place once it moves onto the request-scoped session. The
    second parametrisation aborts the transaction, which on a session the request still
    uses would fail every later statement. Green before the fix: the read is already inside
    `_maybe_sample_trace`'s `try`; it guards the move.
    """
    real_resolve = score_module.settings_service.resolve
    seen = {"hit": 0}

    async def _resolve(session: Any, settings: Any, workspace: Any, key: str, *rest: Any) -> Any:
        if key == "rating.trace_sample_rate":
            seen["hit"] += 1
            if failure == "raises":
                raise RuntimeError("injected: the sampling-rate read failed")
            await _poison_session(session)
        return await real_resolve(session, settings, workspace, key, *rest)

    monkeypatch.setattr(score_module.settings_service, "resolve", _resolve)

    response = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": SCORED_REF}), headers=scoring_headers
    )

    assert seen["hit"] == 1, "the injected read was never reached; the test proves nothing"
    assert response.status_code == 200, response.text
    assert response.json()["outcome"] == "quoted"
    loop = asyncio.get_event_loop()
    assert loop.run_until_complete(_rows_for(database, workspace_id)) == []
