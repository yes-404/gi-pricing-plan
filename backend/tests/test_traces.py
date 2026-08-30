"""`03` §4.5 `Trace` persistence — the row-plus-blob write and the retention guard.

FR-RATE-41/42, `00` NFR-OVR-6, W11 Task 4A. Against real PostgreSQL and real MinIO, like
`test_blobs.py`: the retention guard and the GC-survival claim are both database
behaviours a double cannot exercise.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import update

from app.db.models import BlobRow, ScoringTraceRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import traces
from app.platform.blobs import BlobStore
from model_schema import Trace, TraceStep, new_uuid7


def _trace(*, quote_id: str, rating_version: str, bundle_hash: str) -> Trace:
    """A trace shaped like `03` §4.5's worked example, with distinguishing non-default
    values on every field the row projects — the divergence test needs that."""
    return Trace(
        rating_version_ref=rating_version,
        bundle_hash=bundle_hash,
        quote_id=quote_id,
        ladder_reconciled=True,
        steps=[
            TraceStep(
                step_id="s_area",
                type="lookup",
                label="Rating area from outcode",
                consumed={"postcode_outcode": "SW1A", "as_at": "2026-10-20"},
                produced={"rating_area": "A3"},
                matched={
                    "reference_table": "reference_table:ons-postcode-directory@7",
                    "key": {"postcode_outcode": "SW1A"},
                },
                elapsed_us=41,
            ),
            TraceStep(
                step_id="s_minprem",
                type="constraint",
                label="Minimum premium",
                consumed={"office_premium_minor": 26_400, "min_premium_minor": 28_000},
                produced={"office_premium_minor": 28_000},
                violation={"applied": "clamp", "reason_code": "MIN_PREMIUM_APPLIED"},
                elapsed_us=3,
            ),
        ],
    )


def _bundle_hash() -> str:
    return f"sha256:{new_uuid7().hex.ljust(64, '0')[:64]}"


async def _write(
    database: Database, blob_store: BlobStore, workspace_id, *, trace: Trace, sample_reason="rate"
) -> ScoringTraceRow:
    async with database.unit_of_work() as session:
        row = await traces.write_trace(
            session,
            blob_store,
            trace,
            workspace_id=workspace_id,
            sample_reason=sample_reason,
        )
        row_id = row.id
    async with database.session() as session:
        refetched = await session.get(ScoringTraceRow, row_id)
        assert refetched is not None
        return refetched


@pytest.mark.req("FR-RATE-41")
async def test_a_sampled_trace_round_trips(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Persist a `Trace`, read the row back, fetch its body: reconstructs the original."""
    original = _trace(
        quote_id="quote-abc123",
        rating_version="rating_version:motor-gb@27",
        bundle_hash=_bundle_hash(),
    )
    row = await _write(database, blob_store, workspace_id, trace=original)

    async with database.session() as session:
        reconstructed = await traces.read_trace(session, blob_store, row)

    assert reconstructed == original


@pytest.mark.req("FR-RATE-42")
async def test_row_and_body_are_written_from_one_serialisation(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The discriminating test: the row's three projected fields equal the values *inside
    the stored body* — a projection assembled separately from the body would pass the
    round-trip test above and fail this one (Ruling 23)."""
    original = _trace(
        quote_id="quote-divergence-check",
        rating_version="rating_version:motor-gb@41",
        bundle_hash=_bundle_hash(),
    )
    row = await _write(database, blob_store, workspace_id, trace=original)

    async with database.session() as session:
        body = await traces.read_trace(session, blob_store, row)

    assert row.quote_id == body.quote_id == original.quote_id
    assert (
        row.rating_version_ref
        == str(body.rating_version_ref)
        == str(original.rating_version_ref)
    )
    assert row.bundle_hash == body.bundle_hash == original.bundle_hash


@pytest.mark.req("FR-RATE-42")
async def test_batch_produced_trace_carries_no_environment(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A trace written on request for a batch Job (FR-RATE-41, Ruling 25) carries no
    `environment` — the signal `GET /api/v1/traces` (Task 4C) excludes it by."""
    original = _trace(
        quote_id="quote-batch",
        rating_version="rating_version:motor-gb@3",
        bundle_hash=_bundle_hash(),
    )
    async with database.unit_of_work() as session:
        row = await traces.write_trace(
            session,
            blob_store,
            original,
            workspace_id=workspace_id,
            sample_reason="rate",
        )
        row_id = row.id

    async with database.session() as session:
        refetched = await session.get(ScoringTraceRow, row_id)
        assert refetched is not None
        assert refetched.environment is None


@pytest.mark.req("NFR-OVR-6")
async def test_deleting_a_trace_inside_the_retention_floor_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Negative: NFR-OVR-6's >= 13-month floor refuses a delete of a fresh row."""
    row = await _write(
        database,
        blob_store,
        workspace_id,
        trace=_trace(
            quote_id="quote-young",
            rating_version="rating_version:motor-gb@5",
            bundle_hash=_bundle_hash(),
        ),
    )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await traces.delete_trace(session, row.id)
    assert exc.value.code == "TRACE_RETENTION_FLOOR"
    assert exc.value.status_code == 409

    async with database.session() as session:
        assert await session.get(ScoringTraceRow, row.id) is not None


@pytest.mark.req("NFR-OVR-6")
async def test_deleting_a_trace_outside_the_retention_floor_is_permitted(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The guard has an edge: a row older than the floor may be deleted."""
    row = await _write(
        database,
        blob_store,
        workspace_id,
        trace=_trace(
            quote_id="quote-old",
            rating_version="rating_version:motor-gb@6",
            bundle_hash=_bundle_hash(),
        ),
    )
    async with database.unit_of_work() as session:
        await session.execute(
            update(ScoringTraceRow)
            .where(ScoringTraceRow.id == row.id)
            .values(created_at=datetime.now(UTC) - timedelta(days=400))
        )

    async with database.unit_of_work() as session:
        await traces.delete_trace(session, row.id)

    async with database.session() as session:
        assert await session.get(ScoringTraceRow, row.id) is None
        # The blob reference was released on delete, not left dangling at ref_count > 0.
        blob_row = await session.get(BlobRow, row.blob_sha256)
        assert blob_row is not None
        assert blob_row.ref_count == 0


@pytest.mark.req("NFR-RATE-12")
async def test_a_referenced_trace_blob_survives_garbage_collection(
    database: Database, blob_store: BlobStore, workspace_id, principal
) -> None:
    """Ruling 23's claim, verified rather than assumed: `write_trace`'s `retain` keeps a
    trace's blob invisible to GC's `ref_count == 0` selector even once it is old."""
    row = await _write(
        database,
        blob_store,
        workspace_id,
        trace=_trace(
            quote_id="quote-gc-check",
            rating_version="rating_version:motor-gb@7",
            bundle_hash=_bundle_hash(),
        ),
    )
    async with database.unit_of_work() as session:
        await session.execute(
            update(BlobRow)
            .where(BlobRow.sha256 == row.blob_sha256)
            .values(created_at=datetime.now(UTC) - timedelta(days=60))
        )

    async with database.unit_of_work() as session:
        report = await blob_store.collect_garbage(
            session, actor=principal, workspace_id=workspace_id, dry_run=False
        )

    assert row.blob_sha256 not in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, row.blob_sha256) is not None


@pytest.mark.req("NFR-OVR-6")
async def test_deleting_an_unknown_trace_is_a_typed_error(database: Database) -> None:
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await traces.delete_trace(session, new_uuid7())
    assert exc.value.code == "NOT_FOUND"


@pytest.mark.req("FR-RATE-42")
async def test_write_requires_a_transaction(database: Database, blob_store: BlobStore) -> None:
    """Negative: mirrors `blobs.put`'s own guard — the row and the blob's accounting must
    commit together."""
    async with database.session() as session:
        with pytest.raises(RuntimeError, match="requires an open transaction"):
            await traces.write_trace(
                session,
                blob_store,
                _trace(
                    quote_id="quote-no-txn",
                    rating_version="rating_version:motor-gb@9",
                    bundle_hash=_bundle_hash(),
                ),
                workspace_id=new_uuid7(),
                sample_reason="rate",
            )
