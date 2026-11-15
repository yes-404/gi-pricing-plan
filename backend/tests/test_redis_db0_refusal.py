"""The backend suite refuses a Redis URL that could reach database 0 (#1806).

DB-free: calls `refuse_live_redis` directly. The hook that applies it is
`pytest_configure` in `conftest.py`, exercised by the planted runs in the fix's record.
"""

from __future__ import annotations

import pytest
from backend.tests.conftest import refuse_live_redis


@pytest.mark.parametrize(
    "url",
    [
        None,
        "",
        "   ",
        "redis://localhost:6379/0",
        "redis://localhost:6379",
        "redis://localhost:6379/",
        "redis://localhost:6379/?db=0",
        "redis://localhost:6379/abc",
    ],
)
def test_a_url_that_could_reach_database_0_is_refused(url: str | None) -> None:
    message = refuse_live_redis(url)
    assert message is not None
    assert "GIP_REDIS_URL=redis://localhost:6379/12" in message


@pytest.mark.parametrize(
    "url",
    [
        "redis://localhost:6379/1",
        "redis://localhost:6379/12",
        "rediss://redis.example:6380/3",
        "redis://localhost:6379/?db=2",
    ],
)
def test_a_scratch_database_is_allowed(url: str) -> None:
    assert refuse_live_redis(url) is None


def test_the_message_never_repeats_the_password() -> None:
    for url in ("redis://:secret@localhost:6379/0", "redis://:secret@localhost:6379/x"):
        message = refuse_live_redis(url)
        assert message is not None
        assert "secret" not in message
