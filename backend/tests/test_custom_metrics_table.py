"""FR-MODEL-103 — the custom_metrics table and its immutability guarantee.

Parallel to `test_custom_objectives.py`'s database-layer coverage: this proves the two
invariants only the platform can be wrong about — the definition cannot be edited once the
row exists, and the lifecycle columns stay mutable so a metric can actually be certified.
`packages/pricing-core/tests/test_metrics.py` owns the arithmetic.
"""

from __future__ import annotations

import uuid
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError

from app.db.models import CustomMetricRow
from app.db.session import Database

pytestmark = pytest.mark.anyio

_APPLICABILITY = {
    "responses": ["claim_severity"],
    "backends": ["xgboost"],
    "offset_required": False,
    "y_domain": {"min": 0.0},
}


def _row(workspace_id: UUID, **kw: object) -> CustomMetricRow:
    fields: dict[str, object] = {
        "id": uuid.uuid4(),
        "workspace_id": workspace_id,
        "slug": "capped-gamma-nll",
        "version": 1,
        "kind": "template",
        "template": "capped_gamma",
        "params": {"cap": 250000.0},
        "applicability": _APPLICABILITY,
        "direction": "lower_is_better",
        "status": "draft",
    }
    fields.update(kw)
    return CustomMetricRow(**fields)  # type: ignore[arg-type]


@pytest.mark.req("FR-MODEL-103")
async def test_a_metric_row_round_trips(database: Database, workspace_id: UUID) -> None:
    row = _row(workspace_id)
    async with database.unit_of_work() as session:
        session.add(row)
        await session.flush()
        row_id = row.id

    async with database.session() as session:
        fetched = await session.get(CustomMetricRow, row_id)
    assert fetched is not None
    assert fetched.params == {"cap": 250000.0}
    assert fetched.direction == "lower_is_better"


@pytest.mark.req("FR-MODEL-103")
async def test_the_definition_cannot_be_edited(database: Database, workspace_id: UUID) -> None:
    """A Model fitted under version 1 must keep meaning version 1's arithmetic."""
    row = _row(workspace_id, slug="poisson-nll", template="poisson", params={})
    async with database.unit_of_work() as session:
        session.add(row)
        await session.flush()
        row_id = row.id

    with pytest.raises(DBAPIError) as refused:
        async with database.unit_of_work() as session:
            await session.execute(
                sa.update(CustomMetricRow)
                .where(CustomMetricRow.id == row_id)
                .values(params={"cap": 1.0})
            )
    assert "immutable" in str(refused.value)

    async with database.session() as session:
        unchanged = await session.get(CustomMetricRow, row_id)
    assert unchanged is not None
    assert unchanged.params == {}


@pytest.mark.req("FR-MODEL-45")
async def test_the_lifecycle_columns_stay_mutable(database: Database, workspace_id: UUID) -> None:
    """The trigger must not freeze the status, or nothing could ever be certified."""
    row = _row(workspace_id, slug="gamma-nll", template="gamma", params={})
    certificate_id = uuid.uuid4()
    async with database.unit_of_work() as session:
        session.add(row)
        await session.flush()
        row_id = row.id

    async with database.unit_of_work() as session:
        await session.execute(
            sa.update(CustomMetricRow)
            .where(CustomMetricRow.id == row_id)
            .values(status="certified", certificate_id=certificate_id)
        )

    async with database.session() as session:
        updated = await session.get(CustomMetricRow, row_id)
    assert updated is not None
    assert updated.status == "certified"
    assert updated.certificate_id == certificate_id


@pytest.mark.req("FR-MODEL-103")
async def test_a_slug_and_version_pair_is_unique(database: Database, workspace_id: UUID) -> None:
    async with database.unit_of_work() as session:
        session.add(_row(workspace_id, slug="duplicate"))

    with pytest.raises(DBAPIError):
        async with database.unit_of_work() as session:
            session.add(_row(workspace_id, slug="duplicate"))
