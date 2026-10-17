"""No route holds a pool connection it no longer needs (NFR-489, RL-1685 PL-1454 DP-1 (a)).

Counted as `pool.checkedout()` at the moment a handler (or a later write) starts, so the
assertion is deterministic and reads no clock. Each case names the audit finding it guards.
"""

from __future__ import annotations

from typing import Any

import pytest
from backend.tests.test_score import (  # noqa: F401  (fixtures, imported the way sibling files do)
    SCORE_URL,
    SCORED_REF,
    _quote,
    _rows_for,
    _run,
    _scored,
    admin_headers,
    client,
    scoring_headers,
    served,
)
from fastapi.testclient import TestClient

from app.api import me as me_module
from app.api import score as score_module
from app.platform import traces as traces_service

pytestmark = pytest.mark.req("NFR-489")


def _checked_out(running: TestClient) -> int:
    pool = running.app.state.database.engine.sync_engine.pool  # type: ignore[attr-defined]
    return int(pool.checkedout())


def test_an_api_key_request_to_a_require_caller_route_holds_no_connection_in_the_handler(
    client: TestClient,  # noqa: F811
    scoring_headers: dict[str, str],  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """F1: `require_caller` authenticates an API key on the request session and used to leave
    that session's connection checked out for the whole request. `/me` depends on it directly,
    as do four other modules; it reads through its own session, so it held two."""
    # The first use of a key stamps `last_used_at` and commits, which releases the connection;
    # the measured request is the second, where nothing is dirty (RL-1685 DP-1 (b)).
    assert client.get("/api/v1/me", headers=scoring_headers).status_code == 200
    held: list[int] = []
    original = me_module.rbac.effective_permissions

    async def _spy(*args: Any, **kwargs: Any) -> Any:
        held.append(_checked_out(client))
        return await original(*args, **kwargs)

    monkeypatch.setattr(me_module.rbac, "effective_permissions", _spy)
    response = client.get("/api/v1/me", headers=scoring_headers)
    assert response.status_code == 200, response.text
    assert held == [0], f"connections held when the handler began its own reads: {held}"


@pytest.mark.req("FR-259")
def test_the_sampled_trace_write_starts_with_the_read_session_released(
    client: TestClient,  # noqa: F811
    scoring_headers: dict[str, str],  # noqa: F811
    served: Any,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
    database: Any,
    workspace_id: Any,
) -> None:
    """F2: the sampling-rate read ran on the request session and the write opened a second
    connection while the first was still held; two held at once is what a pool of one cannot
    survive. A decline is sampled at 100 %, so no rate is set."""
    declined = _scored(outcome="declined", decline_reasons=["driver_age below minimum"])

    async def _score_one(*_args: Any, **_kwargs: Any) -> Any:
        return declined

    held: list[int] = []
    original = traces_service.write_pending_trace

    async def _spy(*args: Any, **kwargs: Any) -> Any:
        held.append(_checked_out(client))
        return await original(*args, **kwargs)

    monkeypatch.setattr(score_module, "score_one", _score_one)
    monkeypatch.setattr(traces_service, "write_pending_trace", _spy)
    response = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": SCORED_REF}), headers=scoring_headers
    )
    assert response.status_code == 200, response.text
    assert held == [0], f"connections held when the sampled write began: {held}"
    assert len(_run(_rows_for(database, workspace_id))) == 1  # the write still happened
