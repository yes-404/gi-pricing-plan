"""NFR-498: rate table versions, bulk operations, manual edits and algorithm edits emit Audit
Events with before/after state, in the write's transaction (06 R2, FR-368). FD-1513's fix,
red first (PL-1516 with its deltas, PL-1627, RL-1515, RL-1625).

"The state" of a rate table version is its stored wire form without inline `rows`, plus the
cells' canonical content hash under `cells_digest` (RL-1515 DP-2). "The content" of an
algorithm or a sub-graph version is its stored content.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import pytest
from backend.tests.test_api_rate_tables import _LEVELS, _table_slug
from backend.tests.test_rate_tables_service import _seed_approved_model, _set_threshold
from backend.tests.test_rating_algorithms import valid_algorithm
from backend.tests.test_sub_graphs_service import content as sub_graph_content
from sqlalchemy import select

from app.config import Settings
from app.db.models import AuditEventRow, SubGraphVersionRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit, sub_graphs
from app.platform import rate_tables as svc
from app.platform import rating_algorithms as algorithms
from app.platform.blobs import BlobStore
from app.platform.diff_cache import version_content_hash
from model_schema import ArtifactRef, Principal
from model_schema.rating import RateTableCell, RateTableManualEdit, RateTableVersion

pytestmark = pytest.mark.req("NFR-498")

SEEDED = "rate_table_version.seeded"
IMPORTED = "rate_table_version.imported"
BULK = "rate_table_version.bulk_operation"
EDITED = "rate_table_version.edited"
ALGORITHM = "rating_algorithm.created"
SUB_GRAPH = "sub_graph.created"

_CSV = b"driver_age_band,relativity\n17-20,1.9200\n21-24,1.4500\n25-29,1.1200\n"


async def _cells(version: RateTableVersion, blob_store: BlobStore) -> list[dict[str, str]]:
    """The version's cells wherever storage keeps them: inline rows, or the parquet blob."""
    if version.rows is not None:
        return [dict(row.root) for row in version.rows]
    assert version.cells is not None
    return svc._cells_from_parquet(await blob_store.read(version.cells))


async def _state(version: RateTableVersion, blob_store: BlobStore) -> dict[str, Any]:
    return version.model_dump(mode="json", exclude={"rows"}) | {
        "cells_digest": version_content_hash(await _cells(version, blob_store))
    }


async def _events(database: Database, workspace_id: UUID, action: str) -> list[AuditEventRow]:
    async with database.session() as session:
        return list(
            (
                await session.scalars(
                    select(AuditEventRow)
                    .where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == action,
                    )
                    .order_by(AuditEventRow.sequence)
                )
            ).all()
        )


async def _seed(
    database: Database,
    workspace_id: UUID,
    principal: Principal,
    blob_store: BlobStore,
    slug: str,
    family: str,
) -> RateTableVersion:
    return await svc.seed_from_model(
        database,
        workspace_id,
        principal,
        Settings(),
        blob_store,
        slug=slug,
        model_ref=ArtifactRef(type="model", slug=family, version=1),
        factor="driver_age_band",
        change_note="NFR-498",
    )


async def _bulk(
    database: Database,
    workspace_id: UUID,
    principal: Principal,
    blob_store: BlobStore,
    slug: str,
    version: int,
    percentage: str = "0.10",
) -> RateTableVersion:
    return await svc.bulk_operation(
        database,
        workspace_id,
        principal,
        Settings(),
        blob_store,
        slug=slug,
        version=version,
        kind="uplift_table",
        parameters={"percentage": percentage},
    )


async def _table(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> tuple[str, RateTableVersion]:
    """A fresh approved model and its first seeded table."""
    family, slug = f"mf-{uuid4().hex[:8]}", _table_slug()
    await _seed_approved_model(database, workspace_id, family, _LEVELS)
    return slug, await _seed(database, workspace_id, principal, blob_store, slug, family)


@pytest.mark.req("FR-368")
async def test_a_seed_records_its_version_with_before_and_after(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> None:
    family, slug = f"mf-{uuid4().hex[:8]}", _table_slug()
    await _seed_approved_model(database, workspace_id, family, _LEVELS)
    first = await _seed(database, workspace_id, principal, blob_store, slug, family)
    second = await _seed(database, workspace_id, principal, blob_store, slug, family)

    events = await _events(database, workspace_id, SEEDED)
    assert [e.entity_ref for e in events] == [f"rate_table:{slug}@1", f"rate_table:{slug}@2"]
    assert events[0].before is None
    assert events[0].after == await _state(first, blob_store)
    assert events[0].after["cells_digest"] == version_content_hash(
        [dict(row.root) for row in first.rows or []]
    )
    assert events[0].actor["id"] == str(principal.id)
    assert events[1].before == await _state(first, blob_store)
    assert events[1].before == events[0].after  # one immutable version, one state
    assert events[1].after == await _state(second, blob_store)


@pytest.mark.req("FR-368")
async def test_an_import_records_the_baseline_as_before(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> None:
    slug, first = await _table(database, workspace_id, principal, blob_store)
    imported = await svc.import_confirmed(
        database,
        workspace_id,
        principal,
        Settings(),
        blob_store,
        slug=slug,
        version=1,
        filename="nfr498.csv",
        content=_CSV,
    )

    [event] = await _events(database, workspace_id, IMPORTED)
    assert event.entity_ref == f"rate_table:{slug}@2"
    assert event.before == await _state(first, blob_store)
    assert event.after == await _state(imported, blob_store)
    assert event.after["created_by_import"] is not None
    assert event.actor["id"] == str(principal.id)


@pytest.mark.req("FR-368")
async def test_a_bulk_operation_records_the_baseline_and_the_derived_version(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> None:
    slug, first = await _table(database, workspace_id, principal, blob_store)
    derived = await _bulk(database, workspace_id, principal, blob_store, slug, 1)

    [event] = await _events(database, workspace_id, BULK)
    assert event.entity_ref == f"rate_table:{slug}@2"
    assert event.before == await _state(first, blob_store)
    assert event.after == await _state(derived, blob_store)
    assert event.after["created_by_operation"] is not None


@pytest.mark.req("FR-368")
async def test_a_bulk_operation_on_a_bulk_made_baseline_records_that_versions_own_state(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> None:
    """PL-1516 D3's red: a baseline made by an operation keeps `created_by_operation` in
    `before`, so the chain holds one state per immutable version."""
    slug, _ = await _table(database, workspace_id, principal, blob_store)
    await _bulk(database, workspace_id, principal, blob_store, slug, 1)
    await _bulk(database, workspace_id, principal, blob_store, slug, 2)

    events = await _events(database, workspace_id, BULK)
    assert [e.entity_ref for e in events] == [f"rate_table:{slug}@2", f"rate_table:{slug}@3"]
    assert events[1].before == events[0].after
    assert events[1].before["created_by_operation"] is not None


@pytest.mark.req("FR-368")
@pytest.mark.req("FR-229")
async def test_a_confirmed_manual_edit_records_the_base_version_as_before(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> None:
    """RL-1625: a confirmed manual edit records `rate_table_version.edited`."""
    slug, first = await _table(database, workspace_id, principal, blob_store)
    edited = await svc.manual_edit_confirmed(
        database,
        workspace_id,
        principal,
        Settings(),
        blob_store,
        slug=slug,
        body=RateTableManualEdit(
            base_version=1,
            change_note="band 21-24 +5%",
            confirm=True,
            edits=[RateTableCell({"driver_age_band": "21-24", "relativity": "1.4500"})],
        ),
    )

    [event] = await _events(database, workspace_id, EDITED)
    assert event.entity_ref == f"rate_table:{slug}@2"
    assert event.before == await _state(first, blob_store)
    assert event.after == await _state(edited, blob_store)
    assert event.after["created_by_edit"]["edited_cells"] == 1
    assert event.actor["id"] == str(principal.id)


@pytest.mark.req("FR-368")
async def test_a_parquet_version_records_its_blob_ref_digest_and_no_rows(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> None:
    await _set_threshold(database, workspace_id, 1)
    slug, first = await _table(database, workspace_id, principal, blob_store)
    assert first.storage == "parquet"
    derived = await _bulk(database, workspace_id, principal, blob_store, slug, 1)
    await _bulk(database, workspace_id, principal, blob_store, slug, 2)

    events = await _events(database, workspace_id, BULK)
    [one, two] = events
    assert one.after["storage"] == "parquet"
    assert one.after["cells"] is not None
    assert "rows" not in one.after
    assert one.after["cells_digest"] == version_content_hash(await _cells(derived, blob_store))
    assert one.after == await _state(derived, blob_store)
    assert one.before == await _state(first, blob_store)
    assert two.before == one.after
    assert two.before["storage"] == "parquet"


@pytest.mark.req("FR-368")
async def test_an_algorithm_save_records_the_previous_version_as_before(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    first = valid_algorithm()
    second = valid_algorithm() | {"version": 2}
    await algorithms.create_algorithm(database, workspace_id, principal, first)
    await algorithms.create_algorithm(database, workspace_id, principal, second)

    events = await _events(database, workspace_id, ALGORITHM)
    assert [e.entity_ref for e in events] == [
        "rating_algorithm:motor-gb@1",
        "rating_algorithm:motor-gb@2",
    ]
    assert [e.before for e in events] == [None, first]
    assert [e.after for e in events] == [first, second]
    assert events[0].actor["id"] == str(principal.id)


async def test_a_refused_write_records_nothing(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> None:
    """Control: a refused write leaves no event of its action (passes at the base too)."""
    await algorithms.create_algorithm(database, workspace_id, principal, valid_algorithm())
    saved = len(await _events(database, workspace_id, ALGORITHM))
    with pytest.raises(PlatformError) as conflict:
        await algorithms.create_algorithm(database, workspace_id, principal, valid_algorithm())
    assert conflict.value.status_code == 409
    assert len(await _events(database, workspace_id, ALGORITHM)) == saved

    slug, _ = await _table(database, workspace_id, principal, blob_store)
    with pytest.raises(PlatformError) as refused:
        await _bulk(database, workspace_id, principal, blob_store, slug, 1, percentage="x")
    assert refused.value.status_code == 422
    assert await _events(database, workspace_id, BULK) == []


async def _sub_graph_rows(database: Database, workspace_id: UUID) -> list[SubGraphVersionRow]:
    async with database.session() as session:
        return list(
            (
                await session.scalars(
                    select(SubGraphVersionRow)
                    .where(SubGraphVersionRow.workspace_id == workspace_id)
                    .order_by(SubGraphVersionRow.version)
                )
            ).all()
        )


@pytest.mark.req("FR-368")
async def test_a_sub_graph_version_one_records_its_full_content_as_after(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    """RL-1515 DP-5 (a), 7a: `after` is the stored content, steps included; version 1 has
    no `before`."""
    await sub_graphs.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **sub_graph_content()}
    )

    [row] = await _sub_graph_rows(database, workspace_id)
    [event] = await _events(database, workspace_id, SUB_GRAPH)
    assert event.entity_ref == "sub_graph:ncd-ladder@1"
    assert event.before is None
    assert event.after == row.content
    assert "steps" in event.after


@pytest.mark.req("FR-368")
async def test_a_sub_graph_version_two_records_version_one_as_before(
    database: Database, workspace_id: UUID, principal: Principal
) -> None:
    """RL-1515 DP-5 (a), 7b: version N carries version N-1's stored content as `before`."""
    await sub_graphs.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **sub_graph_content()}
    )
    await sub_graphs.create_version(
        database, workspace_id, principal, "ncd-ladder", sub_graph_content(change_note="second")
    )

    rows = await _sub_graph_rows(database, workspace_id)
    events = await _events(database, workspace_id, SUB_GRAPH)
    assert [e.entity_ref for e in events] == ["sub_graph:ncd-ladder@1", "sub_graph:ncd-ladder@2"]
    assert events[1].before == rows[0].content
    assert events[1].after == rows[1].content


@pytest.mark.req("FR-372")
async def test_the_chain_verifies_after_every_class(
    database: Database, workspace_id: UUID, principal: Principal, blob_store: BlobStore
) -> None:
    slug, _ = await _table(database, workspace_id, principal, blob_store)  # seeded
    await svc.import_confirmed(
        database, workspace_id, principal, Settings(), blob_store,
        slug=slug, version=1, filename="nfr498.csv", content=_CSV,
    )  # imported
    await _bulk(database, workspace_id, principal, blob_store, slug, 2)  # bulk_operation
    await svc.manual_edit_confirmed(
        database, workspace_id, principal, Settings(), blob_store,
        slug=slug,
        body=RateTableManualEdit(
            base_version=3,
            change_note="edit",
            confirm=True,
            edits=[RateTableCell({"driver_age_band": "21-24", "relativity": "1.4500"})],
        ),
    )  # edited
    await algorithms.create_algorithm(database, workspace_id, principal, valid_algorithm())
    await sub_graphs.create_sub_graph(
        database, workspace_id, principal, {"slug": "ncd-ladder", **sub_graph_content()}
    )

    async with database.unit_of_work() as session:
        assert await audit.verify_chain(session, workspace_id) == 6
