"""FR-420 — the collector's delete-after-commit form and its re-check (#1504 slice 3a, #1855).

Against real PostgreSQL and real MinIO. The collector has no caller yet (see
`test_blob_collector_has_no_premature_caller.py`); these cases pin the form it must have before
one is added: rows deleted by one re-checking statement, the audit row in the same transaction,
objects deleted only after that commit and under the digest lock.

Interleavings are ordered by reading `pg_stat_activity` for a blocked backend, never by sleeping
a fixed time. Run them in a window where no other session is waiting on a lock in this database.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from backend.tests.conftest_db import seed_as_owner
from botocore.exceptions import ClientError
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEventRow, BlobRow
from app.db.session import Database
from app.platform import blobs, traces
from app.platform.blobs import BlobStore, blob_key
from model_schema import BlobRef, Principal, Trace, TraceStep, new_uuid7


def _unique(label: bytes) -> bytes:
    return label + b" " + str(new_uuid7()).encode()


async def _backdate(digest: str, *, days: int = 60) -> None:
    async def _update(session: AsyncSession) -> None:
        await session.execute(
            update(BlobRow)
            .where(BlobRow.sha256 == digest)
            .values(created_at=datetime.now(UTC) - timedelta(days=days))
        )

    await seed_as_owner(_update)


async def _aged_unreferenced_blob(database: Database, blob_store: BlobStore) -> str:
    """A stored blob at `ref_count` 0 that no owner names and the grace period has passed."""
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, _unique(b"collector"), "text/plain")
    async with database.unit_of_work() as session:
        assert await blobs.release(session, ref.sha256) == 0
    await _backdate(ref.sha256)
    return ref.sha256


async def _object_exists(blob_store: BlobStore, digest: str) -> bool:
    return await asyncio.to_thread(blob_store._object_exists, blob_key(digest))


async def _wait_for_a_blocked_backend(database: Database) -> None:
    """Return once some other backend of this database waits on a lock."""
    for _ in range(200):
        async with database.session() as session:
            blocked = (
                await session.execute(
                    text(
                        "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() "
                        "AND pid <> pg_backend_pid() AND wait_event_type = 'Lock'"
                    )
                )
            ).scalar_one()
        if blocked:
            return
        await asyncio.sleep(0.05)
    raise AssertionError("no backend became blocked on a lock within 10 s")


@pytest.mark.req("FR-420")
async def test_a_failed_object_delete_after_the_commit_leaves_an_orphan_never_a_dangling_row(
    database: Database,
    owner_database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R1. The row delete commits first. If the object delete then fails, the row is gone and the
    object remains: an orphan, which costs bytes. The old order (object, then row, in the caller's
    transaction) could roll the row back and leave a row with no object."""
    digest = await _aged_unreferenced_blob(database, blob_store)

    def _boom(**_: object) -> None:
        raise ClientError({"Error": {"Code": "500", "Message": "boom"}}, "DeleteObject")

    monkeypatch.setattr(blob_store._client, "delete_object", _boom)
    report = await blob_store.collect_garbage(
        owner_database, actor=principal, workspace_id=workspace_id, dry_run=False
    )

    assert digest in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, digest) is None
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_a_retain_that_commits_while_the_delete_waits_keeps_the_blob(
    database: Database,
    owner_database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
) -> None:
    """R2. A de-duplicating `put` takes a reference (row lock held, uncommitted); the collector's
    DELETE waits on that lock; the put commits; the DELETE re-checks `ref_count` and skips."""
    digest = await _aged_unreferenced_blob(database, blob_store)
    async with database.session() as session:
        row = await session.get(BlobRow, digest)
        assert row is not None
    # Same bytes again: read them back so the put hashes to the same digest.
    ref = BlobRef(sha256=digest, bytes=row.bytes_, media_type=row.media_type)
    content = b"".join([chunk async for chunk in blob_store.open(ref)])

    async with database.unit_of_work() as session:
        await blob_store.put(session, content, row.media_type)  # ref_count 1, uncommitted
        collector = asyncio.create_task(
            blob_store.collect_garbage(
                owner_database, actor=principal, workspace_id=workspace_id, dry_run=False
            )
        )
        await _wait_for_a_blocked_backend(database)
        assert not collector.done()
    report = await collector

    assert digest not in report.deleted
    async with database.session() as session:
        kept = await session.get(BlobRow, digest)
    assert kept is not None
    assert kept.ref_count == 1
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_a_blob_an_owner_row_names_is_not_collected_even_at_ref_count_zero(
    database: Database,
    owner_database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
) -> None:
    """R3. A leaked undercount (an owner exists, the count says 0) must not be collectable: the
    DELETE re-checks `BLOB_OWNERS` itself."""
    trace = Trace(
        rating_version_ref="rating_version:motor-gb@3",
        bundle_hash=f"sha256:{new_uuid7().hex.ljust(64, '0')[:64]}",
        quote_id=f"quote-{new_uuid7()}",
        ladder_reconciled=True,
        steps=[
            TraceStep(
                step_id="s1",
                type="lookup",
                label="Rating area",
                consumed={"postcode_outcode": "SW1A"},
                produced={"rating_area": "A3"},
                elapsed_us=1,
            )
        ],
    )
    async with database.unit_of_work() as session:
        row = await traces.write_trace(
            session, blob_store, trace, workspace_id=workspace_id, sample_reason="rate"
        )
        digest = row.blob_sha256
    assert digest is not None
    async with database.unit_of_work() as session:
        await session.execute(update(BlobRow).where(BlobRow.sha256 == digest).values(ref_count=0))
    await _backdate(digest)

    report = await blob_store.collect_garbage(
        owner_database, actor=principal, workspace_id=workspace_id, dry_run=False
    )

    assert digest not in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, digest) is not None
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_the_object_step_skips_a_digest_a_concurrent_put_is_re_storing(
    database: Database, blob_store: BlobStore, workspace_id, principal: Principal
) -> None:
    """The re-put race (§2.1a). The row is gone (object kept, as after a failed object delete).
    A `put` of the same bytes misses the row, writes the row and has not committed; the
    collector's object step must wait on the digest lock, then see the row and keep the object.
    Without the lock it deletes the object and the commit leaves a row with no bytes."""
    content = _unique(b"reput")
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, content, "text/plain")
    async with database.unit_of_work() as session:
        await blobs.release(session, ref.sha256)
    # Row gone, object left behind: the state after step 2 committed and step 3 has not run.
    async def _drop_row(session: AsyncSession) -> None:
        await session.execute(text("DELETE FROM blobs WHERE sha256 = :d"), {"d": ref.sha256})

    await seed_as_owner(_drop_row)

    async with database.unit_of_work() as session:
        await blob_store.put(session, content, "text/plain")  # misses, inserts, uncommitted
        step3 = asyncio.create_task(
            blob_store._delete_object_if_unreferenced(database, ref.sha256)
        )
        await _wait_for_a_blocked_backend(database)
        assert not step3.done()
    await step3

    async with database.session() as session:
        assert await session.get(BlobRow, ref.sha256) is not None
    assert await _object_exists(blob_store, ref.sha256)


@pytest.mark.req("FR-420")
async def test_a_dry_run_deletes_nothing_and_is_audited(
    database: Database, blob_store: BlobStore, workspace_id, principal: Principal
) -> None:
    digest = await _aged_unreferenced_blob(database, blob_store)

    report = await blob_store.collect_garbage(
        database, actor=principal, workspace_id=workspace_id, dry_run=True
    )

    assert report.dry_run and report.deleted == ()
    assert report.considered >= 1
    async with database.session() as session:
        assert await session.get(BlobRow, digest) is not None
        events = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "blob.garbage_collected",
                )
            )
        ).scalars().all()
    assert events
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_a_non_dry_run_deletes_row_and_object_and_audits_the_deleted_digests(
    database: Database,
    owner_database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
) -> None:
    digest = await _aged_unreferenced_blob(database, blob_store)

    report = await blob_store.collect_garbage(
        owner_database, actor=principal, workspace_id=workspace_id, dry_run=False
    )

    assert digest in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, digest) is None
        events = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "blob.garbage_collected",
                )
            )
        ).scalars().all()
    assert any(digest in (e.after or {}).get("deleted", []) for e in events)
    assert not await _object_exists(blob_store, digest)
