"""FD 8233: the tenant-binding tests' Redis database index must not collide with a gate's.

DB-free: it calls the `redis_url` fixture's function and asserts on the string it returns.
Gates use Redis dbs 1-4 and run-small and seats use 11-13, so an unset `GIP_REDIS_URL`
must draw from 5-10; a set one is honoured.
"""

from __future__ import annotations

from urllib.parse import urlparse

import pytest
from backend.tests.test_tenant_binding import redis_url

_DRAW = redis_url._get_wrapped_function()
_RESERVED = {1, 2, 3, 4, 11, 12, 13}


def _db(url: str) -> int:
    return int(urlparse(url).path.lstrip("/"))


@pytest.mark.req("FR-436")
def test_set_gip_redis_url_db_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIP_REDIS_URL", "redis://localhost:6379/7")
    assert _db(_DRAW()) == 7


@pytest.mark.req("FR-436")
def test_unset_gip_redis_url_draws_outside_reserved_dbs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GIP_REDIS_URL", raising=False)
    dbs = {_db(_DRAW()) for _ in range(300)}
    assert not dbs & _RESERVED
    assert dbs <= set(range(5, 11))
