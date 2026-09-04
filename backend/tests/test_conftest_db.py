"""Tests for `backend/tests/conftest_db.py`'s own database-URL resolution — W37-6's
per-worktree-database enforcement (`.claude/skills/dev-commands/SKILL.md`'s gate block,
`.claude/skills/python-test/SKILL.md`'s "mutually destructive" section).

`conftest_db.py` is not itself collected as a test module (pytest only collects
`test_*.py`/`*_test.py` files), so its functions get no coverage unless exercised
directly here. No `@pytest.mark.req` marker: this is test-infrastructure correctness,
not evidence for a numbered platform requirement — the same reasoning
`tests/test_doc_id.py`'s own module docstring gives for `doc-id.py`.
"""

from __future__ import annotations

import pathlib
import socket
import sys
import types

import pytest
from backend.tests import conftest_db


@pytest.fixture(autouse=True)
def _clean_slate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test starts uncached and unoverridden: `_per_worktree_test_database_url` is
    `lru_cache`d, and `GIP_TEST_DATABASE_URL` must not leak between tests or from the
    real session this suite is itself running under (which always has it set, per
    `dev-commands`'s gate block).
    """
    conftest_db._per_worktree_test_database_url.cache_clear()
    monkeypatch.delenv("GIP_TEST_DATABASE_URL", raising=False)
    yield
    conftest_db._per_worktree_test_database_url.cache_clear()


def test_database_url_returns_an_explicit_override_without_checking_anything(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GIP_TEST_DATABASE_URL", "postgresql+asyncpg://x:y@z/explicit")

    def _must_not_be_called(name: str) -> bool:
        raise AssertionError("an explicit override must never reach the existence check")

    monkeypatch.setattr(conftest_db, "_worktree_database_exists", _must_not_be_called)
    assert conftest_db.test_database_url() == "postgresql+asyncpg://x:y@z/explicit"


def test_worktree_database_name_is_derived_from_this_checkouts_own_directory() -> None:
    expected = f"gipricing_{pathlib.Path(conftest_db.__file__).resolve().parents[2].name}"
    assert conftest_db._worktree_database_name() == expected


def test_database_url_refuses_when_the_per_worktree_database_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Red-then-green's red half: no override, and the database genuinely absent."""
    monkeypatch.setattr(conftest_db, "_worktree_database_exists", lambda name: False)
    with pytest.raises(RuntimeError) as excinfo:
        conftest_db.test_database_url()
    message = str(excinfo.value)
    assert "does not exist" in message
    assert "createdb" in message
    assert "gipricing" in message.lower()


def test_database_url_derives_the_per_worktree_url_when_the_database_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The green half: no override, database present — returns the derived DSN, never
    the shared `gipricing` one this same input used to fall back to.
    """
    name = conftest_db._worktree_database_name()
    monkeypatch.setattr(conftest_db, "_worktree_database_exists", lambda n: n == name)
    url = conftest_db.test_database_url()
    assert url == f"postgresql+asyncpg://gipricing:gipricing@localhost:5432/{name}"
    assert url != conftest_db.DEFAULT_TEST_DSN


def test_database_url_never_silently_falls_back_to_the_shared_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The precise regression this change closes: before W37-6, an unset override with
    the per-worktree database absent silently resolved to `DEFAULT_TEST_DSN` (the shared
    `gipricing` database) — a return, not a raise. It must raise instead, every time.
    """
    monkeypatch.setattr(conftest_db, "_worktree_database_exists", lambda name: False)
    with pytest.raises(RuntimeError):
        conftest_db.test_database_url()


def test_worktree_database_exists_is_true_when_postgres_is_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The refusal's own precondition, isolated: an absent compose stack must read as
    "not this check's problem" (`True`, deferring to `database()`'s own skip), never as
    a false "your per-worktree database is missing" refusal.
    """

    async def _refused(**kwargs: object) -> None:
        raise ConnectionRefusedError("no server listening")

    fake_asyncpg = types.SimpleNamespace(connect=_refused)
    monkeypatch.setitem(sys.modules, "asyncpg", fake_asyncpg)

    assert conftest_db._worktree_database_exists("gipricing_does-not-matter") is True


def test_worktree_database_exists_reads_a_real_row_when_postgres_answers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The other branch, still isolated from the network: Postgres answers and the
    query genuinely finds (or does not find) a row — proven against a fake connection
    object rather than a real one, so this test needs no live Postgres itself.
    """

    class _FakeConnection:
        def __init__(self, present: set[str]) -> None:
            self._present = present

        async def fetchrow(self, _query: str, name: str) -> object | None:
            return object() if name in self._present else None

        async def close(self) -> None:
            return None

    async def _connect_present(**kwargs: object) -> _FakeConnection:
        return _FakeConnection({"gipricing_real"})

    monkeypatch.setitem(
        sys.modules, "asyncpg", types.SimpleNamespace(connect=_connect_present)
    )
    assert conftest_db._worktree_database_exists("gipricing_real") is True
    assert conftest_db._worktree_database_exists("gipricing_not-real") is False


def _postgres_reachable() -> bool:
    try:
        with socket.create_connection(("localhost", 5432), timeout=2):
            return True
    except OSError:
        return False


def test_worktree_database_exists_against_the_real_postgres_instance() -> None:
    """An end-to-end proof against the real database this suite itself runs against, not
    only the mocked unit tests above. `postgres` (the maintenance database) always
    exists when Postgres is up; a name no `createdb` has ever produced does not.
    """
    if not _postgres_reachable():
        pytest.skip("Postgres is not reachable in this environment")
    assert conftest_db._worktree_database_exists("postgres") is True
    assert (
        conftest_db._worktree_database_exists(
            "gipricing_this-database-was-never-created-zzz"
        )
        is False
    )
