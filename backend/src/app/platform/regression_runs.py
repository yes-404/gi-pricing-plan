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

from sqlalchemy import DateTime, Uuid, func, literal, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.pagination import COUNT_CAP, Page, decode_cursor, encode_cursor
from app.db.models import RegressionRunRow
from app.errors import PlatformError
from model_schema import RegressionRun, RegressionRunSummary

__all__ = ["fetch_run", "latest_run", "list_runs", "persist_run"]


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


async def list_runs(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rating_version_id: UUID,
    cursor: str | None,
    limit: int,
) -> Page[RegressionRunSummary]:
    """One page of a Rating Version's runs, newest first (`finished_at` desc, `id` desc).

    `id` (a UUIDv7) is the tie-break and the cursor's key. The cursor run is loaded under the
    same workspace and version filters as the list, so an id from another version or workspace
    is a 400 exactly like an id that names no run at all (FR-1531 posture; 03 §5.1).
    """
    scope = (
        RegressionRunRow.workspace_id == workspace_id,
        RegressionRunRow.rating_version_id == rating_version_id,
    )
    query = select(RegressionRunRow).where(*scope)
    after = decode_cursor(cursor)
    if after is not None:
        anchor = (
            await session.execute(
                select(RegressionRunRow).where(*scope, RegressionRunRow.id == after)
            )
        ).scalar_one_or_none()
        if anchor is None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Unknown cursor",
                400,
                "The cursor is not a Regression Run of this Rating Version. Omit it to start "
                "from the newest.",
            )
        query = query.where(
            tuple_(RegressionRunRow.finished_at, RegressionRunRow.id)
            < tuple_(
                literal(anchor.finished_at, DateTime(timezone=True)),
                literal(anchor.id, Uuid()),
            )
        )
    rows = (
        await session.scalars(
            query.order_by(RegressionRunRow.finished_at.desc(), RegressionRunRow.id.desc()).limit(
                limit + 1
            )
        )
    ).all()
    total = await session.scalar(
        select(func.count()).select_from(
            select(RegressionRunRow.id).where(*scope).limit(COUNT_CAP).subquery()
        )
    )
    page = rows[:limit]
    return Page[RegressionRunSummary](
        items=[
            RegressionRunSummary.model_validate(
                {
                    "id": row.id,
                    **{
                        key: row.run.get(key)
                        for key in (
                            "job_id",
                            "overall",
                            "bundle_hash",
                            "suite_ref",
                            "suite_content_hash",
                            "started_at",
                            "finished_at",
                        )
                    },
                }
            )
            for row in page
        ],
        next_cursor=encode_cursor(page[-1].id) if len(rows) > limit else None,
        total_estimate=total or 0,
    )
