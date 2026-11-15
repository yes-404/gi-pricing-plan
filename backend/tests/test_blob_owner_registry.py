"""FR-420's precondition, part 2: every place an artifact references a blob is a registered
owner, and the backfill raises each owned blob's reference count to the number of owners.

`BLOB_OWNERS` is the one declared list (`app.platform.blobs`). The census below derives, from
the table metadata, every column that carries a blob digest and fails when one is not in the
list, so a new owner cannot be added without its backfill. The last test is the proof the slice
rests on: after the backfill, the collector (dry run, grace 0) selects no blob that any row in
the database still mentions.
"""

from __future__ import annotations

import re

import pytest
from backend.tests.blob_fixtures import job_result_owner
from sqlalchemy import func, select, text

from app.db.models import Base, BlobRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import blobs
from app.platform.blobs import BLOB_OWNERS, BlobStore
from model_schema import new_uuid7

# A column that holds a blob's digest, by the name this schema gives every such column.
_DIGEST_COLUMN = re.compile(r"(^|_)(sha256|blob)(_|$)")

#: `table.column` -> why a digest-named column is not an owner. Empty or reasoned, never silent.
NOT_OWNERS: dict[str, str] = {
    "blobs.sha256": "the blob row's own primary key",
}


@pytest.mark.req("FR-420")
def test_every_digest_column_is_a_registered_owner() -> None:
    registered = " ".join(owner.digests for owner in BLOB_OWNERS)
    unregistered = [
        f"{table.name}.{column.name}"
        for table in Base.metadata.sorted_tables
        for column in table.columns
        if _DIGEST_COLUMN.search(column.name)
        and f"{table.name}.{column.name}" not in NOT_OWNERS
        and not re.search(
            rf"FROM {table.name}\b.*\b{column.name}\b|\b{column.name}\b.* FROM {table.name}\b",
            registered,
        )
    ]
    assert unregistered == []


@pytest.mark.req("FR-420")
def test_the_census_would_see_an_unregistered_owner() -> None:
    """Positive control: the digest-column pattern matches the owners we know of."""
    names = {
        f"{table.name}.{column.name}"
        for table in Base.metadata.sorted_tables
        for column in table.columns
        if _DIGEST_COLUMN.search(column.name)
    }
    assert {"scoring_traces.blob_sha256", "regression_runs.cases_blob_sha256"} <= names


async def _blob(database: Database, blob_store: BlobStore, label: bytes) -> str:
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, label + b" " + str(new_uuid7()).encode(), "text/plain")
        # The legacy state this backfill repairs: a blob an owner references at count 0.
        await blobs.release(session, ref.sha256)
    return ref.sha256


async def _count(database: Database, sha256: str) -> int:
    async with database.session() as session:
        row = await session.get(BlobRow, sha256)
        assert row is not None
        await session.refresh(row)
        return row.ref_count


@pytest.mark.req("FR-420")
async def test_the_backfill_raises_a_referenced_blob_to_its_owner_count(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Two jobs name the same blob as their result: count 2. Breaker: drop the owner."""
    sha = await _blob(database, blob_store, b"two job results")
    assert await _count(database, sha) == 0
    for _ in range(2):
        await job_result_owner(database, workspace_id, sha)

    async with database.unit_of_work() as session:
        moved = await blobs.backfill_ref_counts(session)
    assert moved >= 1
    assert await _count(database, sha) == 2


@pytest.mark.req("FR-420")
async def test_the_backfill_never_lowers_a_count_and_is_idempotent(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    sha = await _blob(database, blob_store, b"held more than owned")
    async with database.unit_of_work() as session:
        await blobs.retain(session, sha)
        await blobs.retain(session, sha)
        await blobs.retain(session, sha)
    await job_result_owner(database, workspace_id, sha)

    async with database.unit_of_work() as session:
        await blobs.backfill_ref_counts(session)
    assert await _count(database, sha) == 3

    async with database.unit_of_work() as session:
        assert await blobs.backfill_ref_counts(session) == 0


@pytest.mark.req("FR-420")
async def test_after_the_backfill_the_collector_selects_nothing_any_row_mentions(
    database: Database, blob_store: BlobStore, workspace_id, principal
) -> None:
    """The slice's proof. Every blob the collector would take at grace 0 is mentioned in no
    other table: a digest found anywhere in a row is a reference the registry missed.

    Runs as the application's login role throughout, because the collector does: its read of
    `blobs` and its audit append are inside `gip_app`'s grants (`b7e4c2a91d36`), so an owner
    connection here would prove less than the application's own path.

    Run on the seeded demo copy as well as the test database (the DB window does both).
    """
    async with database.unit_of_work() as session:
        await blobs.backfill_ref_counts(session)
    async with database.unit_of_work() as session:
        report = await blob_store.collect_garbage(
            session, actor=principal, workspace_id=workspace_id, dry_run=True, grace_days=0
        )
    assert report.dry_run is True
    assert report.deleted == ()  # a dry run deletes nothing

    async with database.session() as session:
        # The collector's own selector (`ref_count = 0` and older than the cutoff), with the
        # digests a dry run does not list. Its count is the report's `considered`.
        selected = list(
            (
                await session.execute(
                    select(BlobRow.sha256).where(
                        BlobRow.ref_count == 0, BlobRow.created_at < func.now()
                    )
                )
            ).scalars()
        )
        assert len(selected) == report.considered
        tables = [
            row[0]
            for row in (
                await session.execute(
                    text(
                        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
                        "AND tablename NOT IN ('blobs', 'audit_events')"
                    )
                )
            ).all()
        ]
        mentioned = [
            f"{sha[:12]} in {table}"
            for sha in selected
            for table in tables
            if (
                await session.execute(
                    text(f'SELECT 1 FROM "{table}" AS t WHERE t::text LIKE :pat LIMIT 1'),
                    {"pat": f"%{sha}%"},
                )
            ).first()
        ]
    assert mentioned == []


@pytest.mark.req("FR-420")
async def test_a_release_that_would_reach_zero_while_an_owner_names_the_blob_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The second line of defence (#1504 D1). `put` took the one reference; a job result names
    the blob; releasing it to 0 would make the collector's selector take a blob the job reads.

    The refusal is an internal 500-class error, and the caller's transaction rolls back with the
    decrement, so the count is still 1. Breaker: drop the owner check in `blobs.release` -> the
    release commits at 0 and the blob is collectable.
    """
    async with database.unit_of_work() as session:
        ref = await blob_store.put(
            session, b"owned blob " + str(new_uuid7()).encode(), "text/plain"
        )
    await job_result_owner(database, workspace_id, ref.sha256)

    with pytest.raises(PlatformError) as caught:
        async with database.unit_of_work() as session:
            await blobs.release(session, ref.sha256)
    assert caught.value.code == "BLOB_REFERENCE_INVARIANT_BREACHED"
    assert caught.value.status_code == 500
    assert await _count(database, ref.sha256) == 1


@pytest.mark.req("FR-420")
async def test_a_release_of_an_unowned_blob_still_reaches_zero(
    database: Database, blob_store: BlobStore
) -> None:
    """Positive control for the guard: with no owner row the same release is allowed."""
    sha = await _blob(database, blob_store, b"unowned")  # put, then release to 0
    assert await _count(database, sha) == 0
    async with database.session() as session:
        assert await blobs.owner_count(session, sha) == 0


@pytest.mark.req("FR-420")
async def test_owner_count_counts_each_owner_place(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    sha = await _blob(database, blob_store, b"two owners")
    for _ in range(2):
        await job_result_owner(database, workspace_id, sha)
    async with database.session() as session:
        assert await blobs.owner_count(session, sha) == 2
        assert await blobs.owner_count(session, "0" * 64) == 0


@pytest.mark.req("FR-420")
async def test_a_digest_at_an_unregistered_jsonb_path_is_not_an_owner_the_registry_sees(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """N1's limit, proven red on a planted row: a digest stored at a JSONB path no `BLOB_OWNERS`
    entry names (here `jobs.parameters.blob`, the ingest input) is invisible to `owner_count`, so
    neither the backfill nor the release guard protects it. The column-name census above cannot
    see a JSONB path either: a new path becomes an owner only by adding its entry to
    `BLOB_OWNERS`, which is a review step, not a check."""
    from datetime import UTC, datetime

    from app.db.models import JobRow
    from model_schema import JobKind, JobQueue, JobSource, JobStatus

    sha = await _blob(database, blob_store, b"unregistered path")
    async with database.unit_of_work() as session:
        session.add(
            JobRow(
                workspace_id=workspace_id,
                kind=JobKind.RATE_TABLE_DIFF,
                status=JobStatus.SUCCEEDED,
                queue=JobQueue.DEFAULT,
                source=JobSource.API,
                submitted_by={"kind": "user", "id": str(new_uuid7())},
                parameters={"blob": sha},
                finished_at=datetime.now(UTC),
            )
        )
    async with database.session() as session:
        assert await blobs.owner_count(session, sha) == 0
