"""`00` FR-15: time is stored as UTC `timestamptz`, and business-effective dating is half-open
`[from, to)` (#1727, the P3-C limb). Both tests are DB-free.

The storage half walks `Base.metadata`: every `DateTime` column must be `timezone=True`. The
dating half drives `routing.select_range`, the one place a quote's effective date meets a
Rating Version's `[effective_from, effective_to)` range, through a stand-in session that serves
the stored rule and its pinned Deployment the way the function reads them.
"""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
import sqlalchemy as sa

import app.db.models  # noqa: F401  (registers every table on the metadata)
from app.db.base import Base
from app.platform.routing import select_range


def _naive_datetime_columns(metadata: sa.MetaData) -> list[str]:
    return sorted(
        f"{table.name}.{column.name}"
        for table in metadata.tables.values()
        for column in table.columns
        if isinstance(column.type, sa.DateTime) and not column.type.timezone
    )


@pytest.mark.req("FR-15")
def test_every_datetime_column_is_timezone_aware() -> None:
    assert Base.metadata.tables, "the metadata is empty: the models were not imported"
    assert _naive_datetime_columns(Base.metadata) == []


@pytest.mark.req("FR-15")
def test_the_column_check_sees_a_naive_datetime_column() -> None:
    """The check is not vacuous: a planted naive column is named."""
    metadata = sa.MetaData()
    sa.Table(
        "planted", metadata, sa.Column("at", sa.DateTime(timezone=False)),
        sa.Column("ok", sa.DateTime(timezone=True)),
    )
    assert _naive_datetime_columns(metadata) == ["planted.at"]


FROM, TO = date(2026, 1, 1), date(2027, 1, 1)
REF = "rating_version:motor-gb@1"


class _Result:
    def __init__(self, value: Any) -> None:
        self._value = value

    def scalar_one_or_none(self) -> Any:
        return self._value


class _Session:
    """Serves the current rule, then the pinned Deployment id, in the order `select_range` reads."""

    def __init__(self) -> None:
        self.deployment = uuid4()
        rule = SimpleNamespace(ranges=[{
            "rating_version_ref": REF, "effective_from": FROM.isoformat(),
            "effective_to": TO.isoformat(), "deployment_id": str(self.deployment),
        }])
        self._answers = [rule]

    async def execute(self, statement: Any) -> _Result:
        if self._answers:
            return _Result(self._answers.pop(0))
        return _Result(self.deployment)


async def _select(effective_date: date) -> Any:
    session = _Session()
    chosen = await select_range(
        session, workspace_id=uuid4(), environment="prod",  # type: ignore[arg-type]
        effective_date=effective_date,
    )
    return chosen, session.deployment


@pytest.mark.req("FR-15")
async def test_a_range_is_selected_at_its_effective_from() -> None:
    chosen, deployment = await _select(FROM)
    assert chosen is not None
    assert (str(chosen[0]), chosen[1]) == (REF, deployment)


@pytest.mark.req("FR-15")
async def test_a_range_is_not_selected_at_its_effective_to() -> None:
    """`[from, to)`: the instant equal to `effective_to` belongs to the next range, not this one."""
    chosen, _ = await _select(TO)
    assert chosen is None


@pytest.mark.req("FR-15")
async def test_a_range_holds_the_day_before_its_end_and_not_the_day_before_its_start() -> None:
    inside, _ = await _select(date(2026, 12, 31))
    before, _ = await _select(date(2025, 12, 31))
    assert inside is not None
    assert before is None
