"""`disable_trigger` refuses the database `GIP_TEST_PROTECTED_DATABASE` names, and only that one.

Database-free: the stand-in executor returns the database name the way the helper reads it and
records the statements it is given. CI sets no variable, so the unset case is the CI shape.
"""

from __future__ import annotations

from typing import Any

import pytest
from backend.tests.conftest_db import disable_trigger

_PAIR = ("rating_versions", "rating_versions_content_guard")
_ENV = "GIP_TEST_PROTECTED_DATABASE"


class _Result:
    def __init__(self, value: str) -> None:
        self._value = value

    def scalar_one(self) -> str:
        return self._value


class _Executor:
    def __init__(self, database: str) -> None:
        self._database = database
        self.statements: list[str] = []

    async def execute(self, statement: Any) -> _Result:
        self.statements.append(str(statement))
        return _Result(self._database)


async def test_a_database_named_by_the_variable_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_ENV, "tmpl")
    executor = _Executor("tmpl")
    with pytest.raises(AssertionError, match="never edit the template database"):
        await disable_trigger(executor, *_PAIR)
    assert not any("DISABLE TRIGGER" in s for s in executor.statements)


async def test_another_database_proceeds_when_the_variable_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(_ENV, "tmpl")
    executor = _Executor("worker_db")
    await disable_trigger(executor, *_PAIR)
    assert any("DISABLE TRIGGER" in s for s in executor.statements)


async def test_every_database_proceeds_when_the_variable_is_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(_ENV, raising=False)
    executor = _Executor("gipricing")
    await disable_trigger(executor, *_PAIR)
    assert any("DISABLE TRIGGER" in s for s in executor.statements)
