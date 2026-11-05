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
