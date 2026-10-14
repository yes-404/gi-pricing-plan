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
from typing import Any

import pytest
from backend.tests.test_score import (  # noqa: F401  (fixtures, imported the way sibling files do)
    SCORE_URL,
    SCORED_REF,
    _quote,
    _set_trace_sample_rate,
    admin_headers,
    client,
    compiled_version,
    scoring_headers,
)
from fastapi.testclient import TestClient
from sqlalchemy import event

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
