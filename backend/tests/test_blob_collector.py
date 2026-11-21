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
import hashlib
import threading
from datetime import UTC, datetime, timedelta

import pytest
from backend.tests.conftest_db import seed_as_owner
from botocore.exceptions import ClientError, EndpointConnectionError
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEventRow, BlobRow, BlobUploadRow, ScoringTraceRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit, blobs, traces
from app.platform.blobs import BlobStore, blob_key
from model_schema import BlobRef, JobSource, Principal, Trace, TraceStep, new_uuid7


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


async def _aged_unreferenced_blob(
    database: Database, blob_store: BlobStore, content: bytes | None = None
) -> str:
    """A stored blob at `ref_count` 0 that no owner names and the grace period has passed."""
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, content or _unique(b"collector"), "text/plain")
    async with database.unit_of_work() as session:
        assert await blobs.release(session, ref.sha256) == 0
    await _backdate(ref.sha256)
    return ref.sha256


async def _delete_row_as_owner(digest: str) -> None:
    """The collector's row delete (step 1) as test setup: the login role has no DELETE on blobs."""

    async def _delete(session: AsyncSession) -> None:
        await session.execute(text("DELETE FROM blobs WHERE sha256 = :d"), {"d": digest})

    await seed_as_owner(_delete)


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
        database, actor=principal, workspace_id=workspace_id, dry_run=False
    )

    assert digest in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, digest) is None
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_a_retain_that_commits_while_the_delete_waits_keeps_the_blob(
    database: Database,
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
                database, actor=principal, workspace_id=workspace_id, dry_run=False
            )
        )
        # The collector and the probe are both the login role: it sees its own sessions' waits.
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
        database, actor=principal, workspace_id=workspace_id, dry_run=False
    )

    assert digest not in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, digest) is not None
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_an_owner_row_that_commits_while_the_delete_waits_keeps_the_blob(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
) -> None:
    """#1893 review, point 1: the review's own reproduction. A blob sits at count 0. A `put` of the
    same bytes holds the row lock (its `retain` has run, uncommitted). The collector waits behind
    it. An owner row naming the digest then commits, WITHOUT taking a reference (the undercount
    case the owner check exists for). The `put` rolls back. The one-statement form removed the row
    and the object, because its `NOT EXISTS` used the statement's starting snapshot and so missed
    the owner row; the two-statement form takes a fresh snapshot after the lock wait and keeps
    it."""
    content = _unique(b"owner-during-wait")
    digest = await _aged_unreferenced_blob(database, blob_store, content)
    holding, release = asyncio.Event(), asyncio.Event()

    class _RollBackError(Exception):
        pass

    async def _put_then_roll_back() -> None:
        try:
            async with database.unit_of_work() as session:
                await blob_store.put(session, content, "text/plain")  # retain: the row lock
                holding.set()
                await release.wait()
                raise _RollBackError
        except _RollBackError:
            pass

    async def _owner_row_without_a_reference() -> None:
        # The login role may INSERT a trace row (it is what `write_trace` does): no owner needed.
        async with database.unit_of_work() as session:
            session.add(
                ScoringTraceRow(
                    workspace_id=new_uuid7(),
                    quote_id=f"quote-{new_uuid7()}",
                    rating_version_ref="rating_version:motor-gb@3",
                    bundle_hash="sha256:" + "0" * 64,
                    sample_reason="rate",
                    blob_sha256=digest,
                    status="complete",
                )
            )

    put_task = asyncio.create_task(_put_then_roll_back())
    await asyncio.wait_for(holding.wait(), timeout=30)
    collector = asyncio.create_task(
        blob_store.collect_garbage(
            database, actor=principal, workspace_id=workspace_id, dry_run=False
        )
    )
    await _wait_for_a_blocked_backend(database)  # the collector waits on the put's row lock
    await _owner_row_without_a_reference()  # committed while it waits
    release.set()
    await put_task
    report = await collector

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
async def test_a_put_that_commits_between_the_row_commit_and_the_object_step_keeps_the_object(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Red-first 1. The collector commits its row delete; a `put` of the same bytes then commits
    (a new row, the object written again); only then does the object step run. It must re-read,
    find the row, KEEP the object and report the digest as re-put. A collector that trusted its
    earlier selection deletes the object and leaves a row with no bytes."""
    content = _unique(b"between")
    digest = await _aged_unreferenced_blob(database, blob_store, content)
    row_committed, put_done = asyncio.Event(), asyncio.Event()
    original = blob_store._delete_object_if_unreferenced

    async def _after_a_put(db: Database, d: str) -> bool:
        if d == digest:
            row_committed.set()
            await put_done.wait()
        return await original(db, d)

    monkeypatch.setattr(blob_store, "_delete_object_if_unreferenced", _after_a_put)
    collector = asyncio.create_task(
        blob_store.collect_garbage(
            database, actor=principal, workspace_id=workspace_id, dry_run=False
        )
    )
    await asyncio.wait_for(row_committed.wait(), timeout=30)
    async with database.unit_of_work() as session:
        await blob_store.put(session, content, "text/plain")  # row is gone: inserts, re-uploads
    put_done.set()
    report = await collector

    assert digest in report.deleted
    assert digest in report.re_put
    async with database.session() as session:
        row = await session.get(BlobRow, digest)
    assert row is not None
    assert row.ref_count == 1
    assert await _object_exists(blob_store, digest)  # the row has bytes


@pytest.mark.req("FR-420")
async def test_a_put_that_starts_during_the_object_step_waits_then_writes_the_object(
    database: Database,
    blob_store: BlobStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Red-first 2. The object delete is held open inside the object step's unit of work (it holds
    the exclusive lock); a `put` of the same bytes starts, is seen waiting on a lock, and only
    after the delete finishes uploads the object and inserts the row. Without the lock the put's
    upload lands first and the delete then removes it.

    Runs as the login role throughout: the row DELETE (the collector's step 1, which needs the
    owner) is set up by `seed_as_owner`, and the object step needs no DELETE privilege."""
    content = _unique(b"during")
    digest = await _aged_unreferenced_blob(database, blob_store, content)
    await _delete_row_as_owner(digest)
    entered, release = threading.Event(), threading.Event()
    real_delete = blob_store._client.delete_object

    def _held_delete(**kwargs: object) -> object:
        entered.set()
        assert release.wait(timeout=30)
        return real_delete(**kwargs)

    monkeypatch.setattr(blob_store._client, "delete_object", _held_delete)
    collector = asyncio.create_task(blob_store._delete_object_if_unreferenced(database, digest))
    assert await asyncio.to_thread(entered.wait, 30)

    async def _put() -> None:
        async with database.unit_of_work() as session:
            await blob_store.put(session, content, "text/plain")

    put_task = asyncio.create_task(_put())
    await _wait_for_a_blocked_backend(database)
    assert not put_task.done()
    release.set()
    await asyncio.gather(collector, put_task)

    async with database.session() as session:
        assert await session.get(BlobRow, digest) is not None
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_a_null_owner_digest_does_not_stop_the_collector_taking_an_unowned_blob(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
) -> None:
    """Red-first for `NOT EXISTS`, against the real function. An owner place that yields a NULL
    digest is a real row: a Blob Upload not yet promoted has `sha256` NULL, and `blob_uploads` is
    an owner place. The red (the function's `DELETE` written with `NOT IN`): `x NOT IN (..., NULL)`
    is never true, so the `DELETE` matches nothing and collection halts silently, with no error,
    for as long as any owner place holds a NULL. With `NOT EXISTS` an unowned blob is still
    taken."""
    digest = await _aged_unreferenced_blob(database, blob_store)
    async with database.unit_of_work() as session:
        session.add(
            BlobUploadRow(
                id=new_uuid7(),
                workspace_id=workspace_id,
                principal_id=principal.id,
                staging_key=f"staging/{new_uuid7()}",
                s3_upload_id=None,
                part_count=1,
                media_type="text/plain",
                complete_by=datetime.now(UTC) + timedelta(hours=1),
            )
        )  # sha256 stays NULL: the NULL owner digest

    report = await blob_store.collect_garbage(
        database, actor=principal, workspace_id=workspace_id, dry_run=False
    )

    assert digest in report.deleted


@pytest.mark.req("FR-420")
async def test_a_put_whose_retain_finds_the_row_deleted_falls_through_and_stores_the_blob(
    database: Database,
    blob_store: BlobStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Audit D1. A `put` reads an existing row at count 0; the row is then deleted and committed
    (the collector's DELETE, which takes no digest lock); only then does the put's `retain` run,
    and its UPDATE finds no row. The put must fall through to the new-object path under the lock
    it holds, not fail with `BLOB_NOT_FOUND`: it stores the blob. The interleaving is forced by
    holding the first `retain` call. The row delete is the collector's step 1 done by
    `seed_as_owner` (it needs the owner), so the test itself runs as the login role; the
    collector's own re-read of the row afterwards is the between-commit test's subject."""
    content = _unique(b"retain-gone")
    digest = await _aged_unreferenced_blob(database, blob_store, content)
    read_done, release_put = asyncio.Event(), asyncio.Event()
    original_retain = blobs.retain
    calls = 0

    async def _retain_after_the_delete(session: AsyncSession, sha256: str) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            read_done.set()  # the put has read the row
            await release_put.wait()  # ... and now waits until the row delete has committed
        return await original_retain(session, sha256)

    monkeypatch.setattr(blobs, "retain", _retain_after_the_delete)

    async def _put() -> BlobRef:
        async with database.unit_of_work() as session:
            return await blob_store.put(session, content, "text/plain")

    put_task = asyncio.create_task(_put())
    await asyncio.wait_for(read_done.wait(), timeout=30)
    await _delete_row_as_owner(digest)  # committed while the put holds its read
    release_put.set()
    ref = await put_task

    assert ref.sha256 == digest
    async with database.session() as session:
        row = await session.get(BlobRow, digest)
    assert row is not None
    assert row.ref_count == 1
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_promote_upload_falls_through_when_the_row_is_deleted_before_its_retain(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#1893 review, point 3 (and audit D4): the review's own interleaving. A blob row already
    exists at count 0, so `promote_upload`'s insert does nothing; the collector's DELETE commits
    (done here by `seed_as_owner`); only then does `promote_upload`'s `retain` run and find no
    row. It must insert again and retain, as `put` does, not fail with `BLOB_NOT_FOUND`. The
    interleaving is forced by holding the first `retain`. Runs as the login role."""
    content = _unique(b"promote-gone")
    digest = await _aged_unreferenced_blob(database, blob_store, content)
    staging_key = f"staging/{new_uuid7()}"
    await asyncio.to_thread(
        blob_store._client.put_object, Bucket=blob_store._bucket, Key=staging_key, Body=content
    )
    upload_id = new_uuid7()
    async with database.unit_of_work() as session:
        session.add(
            BlobUploadRow(
                id=upload_id,
                workspace_id=workspace_id,
                principal_id=principal.id,
                staging_key=staging_key,
                s3_upload_id=None,
                part_count=1,
                media_type="text/plain",
                complete_by=datetime.now(UTC) + timedelta(hours=1),
            )
        )
    read_done, release_promote = asyncio.Event(), asyncio.Event()
    original_retain = blobs.retain
    calls = 0

    async def _retain_after_the_delete(session: AsyncSession, sha256: str) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            read_done.set()
            await release_promote.wait()
        return await original_retain(session, sha256)

    monkeypatch.setattr(blobs, "retain", _retain_after_the_delete)
    promote = asyncio.create_task(blob_store.promote_upload(database, upload_id))
    await asyncio.wait_for(read_done.wait(), timeout=30)
    # The collector's DELETE, committed between promote_upload's insert and its retain.
    await _delete_row_as_owner(digest)
    release_promote.set()
    ref = await promote

    assert ref.sha256 == digest
    async with database.session() as session:
        row = await session.get(BlobRow, digest)
        upload = await session.get(BlobUploadRow, upload_id)
    assert row is not None
    assert row.ref_count == 1
    assert upload is not None
    assert upload.sha256 == digest
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_promote_upload_copies_again_when_the_collector_took_the_object_after_its_first_phase(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Audit D4: the first phase of `promote_upload` saw a stored row and skipped its copy; then
    a whole collector run (row delete and the real object step) completes before the final unit
    of work takes its digest lock. The final unit finds no row and no object, and must copy the
    object back, or the promoted blob names bytes that do not exist. The pause is placed on the
    final unit's first `_lock_digest` call; the collector uses the exclusive form and is not held.
    Red: remove the `_object_exists` recheck in the final unit and the object is missing."""
    content = _unique(b"promote-collected")
    digest = await _aged_unreferenced_blob(database, blob_store, content)
    staging_key = f"staging/{new_uuid7()}"
    await asyncio.to_thread(
        blob_store._client.put_object, Bucket=blob_store._bucket, Key=staging_key, Body=content
    )
    upload_id = new_uuid7()
    async with database.unit_of_work() as session:
        session.add(
            BlobUploadRow(
                id=upload_id,
                workspace_id=workspace_id,
                principal_id=principal.id,
                staging_key=staging_key,
                s3_upload_id=None,
                part_count=1,
                media_type="text/plain",
                complete_by=datetime.now(UTC) + timedelta(hours=1),
            )
        )
    at_final_unit, release_promote = asyncio.Event(), asyncio.Event()
    original_lock = blobs._lock_digest
    paused = False

    async def _lock_after_the_collector(session: AsyncSession, sha256: str, **kwargs) -> None:
        nonlocal paused
        if kwargs.get("shared") and not paused:
            paused = True
            at_final_unit.set()
            await release_promote.wait()
        await original_lock(session, sha256, **kwargs)

    monkeypatch.setattr(blobs, "_lock_digest", _lock_after_the_collector)
    promote = asyncio.create_task(blob_store.promote_upload(database, upload_id))
    await asyncio.wait_for(at_final_unit.wait(), timeout=30)

    report = await blob_store.collect_garbage(
        database, actor=principal, workspace_id=workspace_id, dry_run=False
    )
    assert digest in report.deleted
    assert not await _object_exists(blob_store, digest)

    release_promote.set()
    ref = await promote

    assert ref.sha256 == digest
    assert await _object_exists(blob_store, digest)
    async with database.session() as session:
        row = await session.get(BlobRow, digest)
    assert row is not None
    assert row.ref_count == 1


@pytest.mark.req("FR-420")
async def test_a_storage_error_that_is_not_a_client_error_leaves_an_orphan_and_keeps_the_report(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Audit D5. An unreachable storage endpoint raises a `BotoCoreError`, not a `ClientError`.
    It must not abort the run after the rows were deleted and the audit event committed: the
    object stays as an orphan (the sweep is slice 3b's), the report is returned, and no row
    dangles."""
    digest = await _aged_unreferenced_blob(database, blob_store)

    def _unreachable(**_: object) -> None:
        raise EndpointConnectionError(endpoint_url="http://127.0.0.1:1")

    monkeypatch.setattr(blob_store._client, "delete_object", _unreachable)
    report = await blob_store.collect_garbage(
        database, actor=principal, workspace_id=workspace_id, dry_run=False
    )

    assert digest in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, digest) is None
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_a_caller_holding_the_audit_lock_gets_a_coded_error_not_a_hang(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#1855 (v): the caller breaks the contract. Its open transaction has recorded an audit event
    for the workspace, so it holds the workspace's audit lock, idle on the client side; the
    collector's own unit of work needs that lock for its audit event. PostgreSQL does not call
    that a deadlock, so without a bound the call never returns: the test's `wait_for` ends it and
    fails the test (the red against 3a). With the lock timeout the collector rolls back and raises
    `BLOB_GC_LOCK_TIMEOUT`."""
    monkeypatch.setattr(blobs, "_GC_LOCK_TIMEOUT_MS", 1000)
    async with database.unit_of_work() as session:
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=principal,
            source=JobSource.SYSTEM,
            action="probe.audit_lock_held",
            entity_ref="probe:audit-lock@1",
            after={"probe": True},
        )
        with pytest.raises(PlatformError) as raised:
            await asyncio.wait_for(
                blob_store.collect_garbage(
                    database, actor=principal, workspace_id=workspace_id, dry_run=True
                ),
                timeout=30,
            )
    assert raised.value.code == "BLOB_GC_LOCK_TIMEOUT"
    assert raised.value.status_code == 503


@pytest.mark.req("FR-420")
async def test_the_digest_lock_taken_shared_in_opposite_orders_does_not_deadlock(
    database: Database,
) -> None:
    """Writers take the digest lock SHARED, so two transactions that lock {A, B} and {B, A} both
    proceed; with the exclusive form PostgreSQL aborts one with a deadlock. This tests the lock
    mode alone. It does NOT claim that two `put`s of the same digests in opposite orders cannot
    deadlock: the `blobs` row each one inserts or updates is itself locked until commit, and that
    deadlock exists with or without the advisory lock (measured at this slice's window)."""
    a, b = hashlib.sha256(_unique(b"lock-a")).hexdigest(), hashlib.sha256(
        _unique(b"lock-b")
    ).hexdigest()
    barrier = asyncio.Barrier(2)

    async def _lock_both(first: str, second: str) -> None:
        async with database.unit_of_work() as session:
            await blobs._lock_digest(session, first, shared=True)
            await barrier.wait()  # each now holds its first digest's lock
            await blobs._lock_digest(session, second, shared=True)

    await asyncio.wait_for(asyncio.gather(_lock_both(a, b), _lock_both(b, a)), timeout=30)


@pytest.mark.req("FR-420")
async def test_two_first_time_puts_of_the_same_bytes_both_take_a_reference(
    database: Database, blob_store: BlobStore
) -> None:
    """Writers do not exclude each other, so the second insert meets the first at the unique
    index: it must retain, not fail."""
    content = _unique(b"first-time-twice")
    barrier = asyncio.Barrier(2)

    async def _put() -> None:
        async with database.unit_of_work() as session:
            await barrier.wait()
            await blob_store.put(session, content, "text/plain")

    await asyncio.wait_for(asyncio.gather(_put(), _put()), timeout=30)

    async with database.session() as session:
        row = await session.get(BlobRow, hashlib.sha256(content).hexdigest())
    assert row is not None
    assert row.ref_count == 2


@pytest.mark.req("FR-420")
async def test_a_dry_run_deletes_nothing_and_is_audited(
    database: Database, blob_store: BlobStore, workspace_id, principal: Principal
) -> None:
    digest = await _aged_unreferenced_blob(database, blob_store)

    report = await blob_store.collect_garbage(
        database, actor=principal, workspace_id=workspace_id, dry_run=True
    )

    assert report.dry_run
    assert report.deleted == ()
    assert report.considered >= 1
    async with database.session() as session:
        assert await session.get(BlobRow, digest) is not None
        events = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "blob.garbage_collection_previewed",
                )
            )
        ).scalars().all()
        deletions = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "blob.garbage_collected",
                )
            )
        ).scalars().all()
    assert events
    # #1895: a preview is not counted as a deletion.
    assert deletions == []
    assert await _object_exists(blob_store, digest)


@pytest.mark.req("FR-420")
async def test_a_non_dry_run_deletes_row_and_object_and_audits_the_deleted_digests(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    principal: Principal,
) -> None:
    digest = await _aged_unreferenced_blob(database, blob_store)

    report = await blob_store.collect_garbage(
        database, actor=principal, workspace_id=workspace_id, dry_run=False
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
