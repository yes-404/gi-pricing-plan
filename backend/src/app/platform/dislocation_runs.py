"""Dislocation Runs: the persisted `DislocationRun` and its lookup (03 §4.6, FR-263, FR-265).

`persist_run` is the single writer of `dislocation_runs`: every scalar copy on the row,
including `movers_blob_sha256`, is read off the same validated `DislocationRun` it stores,
so the JSONB and the columns cannot diverge. A run holds no quote input (its movers blob
carries `dislocation_frame`'s own columns only, RL-1504 item 5), but `fetch_run`'s callers
hold `rating:read` all the same.
"""

from __future__ import annotations

from typing import Final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DislocationRunRow
from app.errors import PlatformError
from model_schema.dislocation import DislocationRun

__all__ = ["MOVERS_BLOB_PREFIX", "fetch_run", "movers_digest", "persist_run"]

#: How `DislocationRun.largest_movers_blob` writes a digest (03 §4.6's example).
MOVERS_BLOB_PREFIX: Final = "blob:sha256:"


def movers_digest(run: DislocationRun) -> str:
    """The movers blob's sha256 hex digest, parsed from `run.largest_movers_blob`."""
    ref = run.largest_movers_blob
    if ref is None or not ref.startswith(MOVERS_BLOB_PREFIX):
        raise ValueError(
            f"a persisted Dislocation Run names its movers blob as {MOVERS_BLOB_PREFIX}<sha256>"
        )
    return ref.removeprefix(MOVERS_BLOB_PREFIX)


async def persist_run(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    run: DislocationRun,
    baseline_bundle_hash: str,
    candidate_bundle_hash: str,
    actor_id: UUID,
) -> DislocationRunRow:
    if run.job_id is None:
        raise ValueError("a persisted Dislocation Run carries the id of the Job that made it")
    row = DislocationRunRow(
        workspace_id=workspace_id,
        run=run.model_dump(mode="json", by_alias=True),
        baseline_ref=str(run.baseline_ref),
        candidate_ref=str(run.candidate_ref),
        baseline_bundle_hash=baseline_bundle_hash,
        candidate_bundle_hash=candidate_bundle_hash,
        portfolio_dataset_version_id=run.portfolio_dataset_version_id,
        movers_blob_sha256=movers_digest(run),
        job_id=run.job_id,
        created_by=actor_id,
    )
    session.add(row)
    await session.flush()
    return row


async def fetch_run(
    session: AsyncSession, *, workspace_id: UUID, run_id: UUID
) -> DislocationRunRow:
    """The run, or 404 `NOT_FOUND` for an unknown id and another workspace's alike."""
    row = (
        await session.execute(
            select(DislocationRunRow).where(
                DislocationRunRow.workspace_id == workspace_id,
                DislocationRunRow.id == run_id,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND", "Dislocation run not found", 404, f"No dislocation run {run_id}."
        )
    return row
