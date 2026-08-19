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
from sqlalchemy import text
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


@pytest.mark.req("FR-MODEL-108")
async def test_a_metric_cannot_be_deleted_or_truncated(
    database: Database, workspace_id: UUID
) -> None:
    """FR-MODEL-108 asks which models early-stopped under a metric. A deleted row answers
    nothing — and every GbmSpec.eval_metrics ref citing it by slug would keep citing a name
    that resolves to nobody."""
    row = _row(workspace_id, slug="deletable-check", template="gamma", params={})
    async with database.unit_of_work() as session:
        session.add(row)
        await session.flush()
        row_id = row.id

    with pytest.raises(DBAPIError) as refused:
        async with database.unit_of_work() as session:
            await session.execute(
                text("DELETE FROM custom_metrics WHERE id = :id"), {"id": row_id}
            )
    assert "cannot be deleted" in str(refused.value)

    with pytest.raises(DBAPIError):
        async with database.unit_of_work() as session:
            await session.execute(text("TRUNCATE custom_metrics"))

    async with database.session() as session:
        still_there = await session.get(CustomMetricRow, row_id)
    assert still_there is not None


@pytest.mark.req("FR-MODEL-103")
async def test_an_expression_metric_is_refused_in_phase_1(
    database: Database, workspace_id: UUID
) -> None:
    """FR-MODEL-103/FR-MODEL-75: Phase 1 admits no `expression` metric — a row with
    `kind = 'expression'` would carry no loss at all."""
    with pytest.raises(DBAPIError) as refused:
        async with database.unit_of_work() as session:
            session.add(_row(workspace_id, slug="not-a-template", kind="expression"))
    assert "custom_metric_is_a_template_in_phase_1" in str(refused.value)


@pytest.mark.req("FR-MODEL-105")
async def test_a_status_past_draft_needs_a_certificate(
    database: Database, workspace_id: UUID
) -> None:
    """FR-MODEL-105, mirroring `CustomMetric._a_status_past_draft_rests_on_a_certificate`
    as corrected in `30b6388`: `certified` needs a certificate, but `deprecated` — reachable
    directly from `draft` — does not, because a metric abandoned before certification was
    withdrawn, not certified."""
    with pytest.raises(DBAPIError) as refused:
        async with database.unit_of_work() as session:
            session.add(
                _row(workspace_id, slug="no-certificate", status="certified", template="gamma")
            )
    assert "certified_metric_has_a_certificate" in str(refused.value)

    # `deprecated` is the exemption `30b6388` added: no certificate required to withdraw a
    # metric straight out of `draft`.
    row = _row(workspace_id, slug="withdrawn-early", status="deprecated", template="gamma")
    async with database.unit_of_work() as session:
        session.add(row)
        await session.flush()
        row_id = row.id

    async with database.session() as session:
        fetched = await session.get(CustomMetricRow, row_id)
    assert fetched is not None
    assert fetched.status == "deprecated"
    assert fetched.certificate_id is None
