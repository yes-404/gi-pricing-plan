"""`f2b6d90a4c17`'s downgrade refuses, before altering, while an expression Banding exists.

A Banding cut over an `expression` Factor's formula has a NULL `column_name`; re-imposing
NOT NULL on such a table failed with a bare `NotNullViolation` and no reason (WK-690 S4,
audit F-C2, to-lead "2026-10-18 18:20:40 BST"). The migration must count those rows, name the
count (never a value) and stop before the `ALTER`; it must never delete or convert data (a
Banding is append-only, FR-101). These tests run the real `downgrade()` against a recording
`op`; `alembic downgrade -1` against a real database is the round-trip window in `LG-8062`.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

_MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "migrations"
    / "versions"
    / "f2b6d90a4c17_bandings_column_name_nullable.py"
)


def _load_migration() -> ModuleType:
    """The migration module. `versions/` is not importable by name."""
    spec = importlib.util.spec_from_file_location("_bandings_column_name_migration", _MIGRATION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Op:
    """A recording stand-in for `alembic.op`: the count the bind returns, and what was altered."""

    def __init__(self, null_rows: int) -> None:
        self.null_rows = null_rows
        self.statements: list[str] = []
        self.altered: list[dict[str, Any]] = []

    def get_bind(self) -> _Op:
        return self

    def execute(self, statement: Any) -> SimpleNamespace:
        self.statements.append(str(statement))
        return SimpleNamespace(scalar_one=lambda: self.null_rows)

    def alter_column(self, table: str, column: str, **kwargs: Any) -> None:
        self.altered.append({"table": table, "column": column, **kwargs})


def _downgrade_with(null_rows: int, monkeypatch: pytest.MonkeyPatch) -> _Op:
    migration = _load_migration()
    recorder = _Op(null_rows)
    monkeypatch.setattr(migration, "op", recorder)
    migration.downgrade()
    return recorder


def test_downgrade_refuses_naming_the_count_and_alters_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    migration = _load_migration()
    recorder = _Op(3)
    monkeypatch.setattr(migration, "op", recorder)

    with pytest.raises(RuntimeError) as refused:
        migration.downgrade()

    message = str(refused.value)
    assert message.startswith("cannot downgrade f2b6d90a4c17"), message
    assert "3 banding" in message, message
    assert "removed or re-cut" in message, message
    # Refused before altering, and the question asked was a count, not a read of any value.
    assert recorder.altered == []
    assert len(recorder.statements) == 1
    assert "count(" in recorder.statements[0].lower()
    assert "column_name is null" in recorder.statements[0].lower()


def test_downgrade_with_no_expression_banding_re_imposes_not_null(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = _downgrade_with(0, monkeypatch)

    assert recorder.altered == [
        {
            "table": "bandings",
            "column": "column_name",
            "existing_type": recorder.altered[0]["existing_type"],
            "nullable": False,
        }
    ]
