"""FD-1488: a test session on a database behind the head stops once, by name.

DB-free: `migration_problem` is a pure function over three sets of revisions. A database
*ahead* of the checkout (a revision the scripts do not know) is DP-H2: it passes.
"""

from __future__ import annotations

import pytest
from backend.tests.conftest_db import migration_problem

pytestmark = pytest.mark.req("NFR-499")


def test_a_database_at_the_head_passes() -> None:
    assert migration_problem({"b"}, {"b"}, {"a", "b"}) is None


def test_a_database_one_revision_behind_is_refused_by_name() -> None:
    message = migration_problem({"a"}, {"b"}, {"a", "b"})
    assert message is not None
    assert "'a'" in message
    assert "'b'" in message
    assert "uv run alembic upgrade head" in message


def test_a_revision_the_scripts_do_not_know_passes() -> None:
    # The database is ahead of this checkout: DP-H2 (a), a warning, not a stop.
    assert migration_problem({"z"}, {"b"}, {"a", "b"}) is None


def test_two_heads_with_one_applied_is_refused() -> None:
    message = migration_problem({"b1"}, {"b1", "b2"}, {"a", "b1", "b2"})
    assert message is not None
    assert "uv run alembic upgrade head" in message


def test_the_script_directory_is_read_once_across_two_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.tests import conftest_db

    reads: list[object] = []
    real = conftest_db.ScriptDirectory.from_config

    def counting(config: object) -> object:
        reads.append(config)
        return real(config)  # type: ignore[arg-type]

    monkeypatch.setattr(conftest_db.ScriptDirectory, "from_config", counting)
    conftest_db._script_revisions.cache_clear()
    try:
        first = conftest_db._script_revisions()
        second = conftest_db._script_revisions()
    finally:
        conftest_db._script_revisions.cache_clear()
    assert first == second
    assert len(reads) == 1
    heads, known = first
    assert heads
    assert heads <= known


def test_a_database_behind_the_head_stops_the_session_by_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.tests import conftest_db

    monkeypatch.setattr(
        conftest_db, "_script_revisions", lambda: (frozenset({"b"}), frozenset({"a", "b"}))
    )
    with pytest.raises(pytest.exit.Exception) as stopped:
        conftest_db._check_migrations_once({"a"})
    assert "uv run alembic upgrade head" in str(stopped.value)
    with pytest.warns(UserWarning, match="ahead of this checkout"):
        conftest_db._check_migrations_once({"z"})
