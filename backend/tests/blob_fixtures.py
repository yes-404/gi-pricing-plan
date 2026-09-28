"""Rows that make a blob owned, or a quote input, for the tests of the routes that scope by owner.

`blobs` has no workspace column, so who may read a digest comes from the rows that reference it
(`app.platform.blobs.blob_readable_by`): a Dataset Version's table or a Job's blob result in
the caller's workspace, and never a digest a quote-input store references. These build exactly
those rows, so a test says which owner it means instead of hand-writing the row's shape.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from app.db.models import BlobRow, DatasetRow, DatasetVersionRow, JobRow, ScoringTraceRow
from app.db.session import Database
from model_schema import (
    DatasetKind,
    DatasetStatus,
    JobKind,
    JobQueue,
    JobSource,
    JobStatus,
    new_uuid7,
)


def digest() -> str:
    return hashlib.sha256(new_uuid7().bytes).hexdigest()


async def blob_row(database: Database, sha256: str, media_type: str) -> None:
    async with database.unit_of_work() as session:
        session.add(BlobRow(sha256=sha256, bytes_=10, media_type=media_type))


async def dataset_blob(database: Database, workspace_id, sha256: str) -> None:
    """A blob row plus a dataset version in `workspace_id` whose parquet table is `sha256`."""
    await blob_row(database, sha256, "application/vnd.apache.parquet")
    async with database.unit_of_work() as session:
        slug = f"ds-{sha256[:8]}"
        dataset = DatasetRow(workspace_id=workspace_id, slug=slug, name=slug, owner_id=new_uuid7())
        session.add(dataset)
        await session.flush()
        session.add(
            DatasetVersionRow(
                workspace_id=workspace_id,
                dataset_id=dataset.id,
                version=1,
                status=DatasetStatus.DRAFT.value,
                kind=DatasetKind.INGESTED.value,
                slug=slug,
                created_by=new_uuid7(),
                currency="GBP",
                tables=[{"name": "policies", "blob": {"sha256": sha256}}],
            )
        )


async def job_result_owner(database: Database, workspace_id, sha256: str) -> None:
    """A job in `workspace_id` whose result is `JobResult(kind="blob")` naming `sha256` (`03`
    §5.2). Only the job row: the blob's own row is the caller's to create."""
    async with database.unit_of_work() as session:
        session.add(
            JobRow(
                workspace_id=workspace_id,
                kind=JobKind.RATE_TABLE_DIFF,
                status=JobStatus.SUCCEEDED,
                queue=JobQueue.DEFAULT,
                source=JobSource.API,
                submitted_by={"kind": "user", "id": str(new_uuid7())},
                result={"kind": "blob", "ref": sha256},
                finished_at=datetime.now(UTC),
            )
        )


async def job_blob(database: Database, workspace_id, sha256: str) -> None:
    """A blob row plus a job in `workspace_id` whose blob result names it."""
    await blob_row(database, sha256, "application/json")
    await job_result_owner(database, workspace_id, sha256)


async def trace_blob(database: Database, workspace_id, sha256: str) -> None:
    """A sampled scoring trace whose body — quote inputs — is `sha256`."""
    await blob_row(database, sha256, "application/json")
    async with database.unit_of_work() as session:
        session.add(
            ScoringTraceRow(
                workspace_id=workspace_id,
                rating_version_ref="rating_version:motor-gb@1",
                bundle_hash="sha256:" + "0" * 64,
                sample_reason="rate",
                blob_sha256=sha256,
            )
        )
