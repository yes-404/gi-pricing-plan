"""Regression Runs: the persisted `RegressionRun` and its lookup (03 §4.9, FR-260, FR-261).

`persist_run` is the single writer of `regression_runs`: the row's scalar copies —
including `cases_blob_sha256`, which the generic blob route's deny matches — are read off the
same validated `RegressionRun` it stores, so the JSONB and the columns cannot diverge. A
run's `counterexample` is a quote-input fragment (NFR-499): callers of `fetch_run` hold
`rating:read`, and no log line carries a context.

`latest_run` is what FR-257 limb (1) reads: the latest run of one Rating Version for one
exact (`bundle_hash`, `suite_content_hash`) pair — ordered by `finished_at`, then `id` — so
an earlier pass never stands once a later run on the same pair has failed (audit A1).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RegressionRunRow
from model_schema import RegressionRun

__all__ = ["fetch_run", "latest_run", "persist_run"]


async def persist_run(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rating_version_id: UUID,
    run: RegressionRun,
    actor_id: UUID,
) -> RegressionRunRow:
    row = RegressionRunRow(
        workspace_id=workspace_id,
        rating_version_id=rating_version_id,
        run=run.model_dump(mode="json", by_alias=True),
        bundle_hash=run.bundle_hash,
        suite_content_hash=run.suite_content_hash,
        overall=run.overall,
        cases_blob_sha256=run.cases_blob.sha256,
        finished_at=run.finished_at,
        created_by=actor_id,
    )
    session.add(row)
    await session.flush()
    return row


async def fetch_run(
    session: AsyncSession, *, workspace_id: UUID, run_id: UUID
) -> RegressionRunRow | None:
    return (
        await session.execute(
            select(RegressionRunRow).where(
                RegressionRunRow.workspace_id == workspace_id, RegressionRunRow.id == run_id
            )
        )
    ).scalar_one_or_none()


async def latest_run(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rating_version_id: UUID,
    bundle_hash: str,
    suite_content_hash: str,
) -> RegressionRunRow | None:
    """The latest run for exactly this (bundle, suite) pair of this Rating Version."""
    return (
        await session.execute(
            select(RegressionRunRow)
            .where(
                RegressionRunRow.workspace_id == workspace_id,
                RegressionRunRow.rating_version_id == rating_version_id,
                RegressionRunRow.bundle_hash == bundle_hash,
                RegressionRunRow.suite_content_hash == suite_content_hash,
            )
            .order_by(RegressionRunRow.finished_at.desc(), RegressionRunRow.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
