"""Dislocation Runs: the persisted `DislocationRun` and its lookup (03 §4.6, FR-263, FR-265).

`persist_run` is the single writer of `dislocation_runs`: every scalar copy on the row,
including `movers_blob_sha256`, is read off the same validated `DislocationRun` it stores,
so the JSONB and the columns cannot diverge. A run holds no quote input (its movers blob
carries `dislocation_frame`'s own columns only, RL-1504 item 5), but `fetch_run`'s callers
hold `rating:read` all the same.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BlobRow, DatasetVersionRow, DislocationRunRow
from app.errors import PlatformError
from app.platform.blobs import BlobStore, to_ref
from app.platform.datasets import read_version
from app.platform.rating_versions import WorkspaceResolver, resolve_rating_version_ref, to_schema
from model_schema.dislocation import (
    BundleDelta,
    ChangeGroup,
    DislocationEstimate,
    DislocationRun,
    DislocationSpec,
)
from pricing_core.rating.analysis import (
    AttributionError,
    derive_changes,
    estimate_attribution_ratings,
)
from pricing_core.safe_error import safe_error_text

__all__ = [
    "DISLOCATION_RATINGS_PER_WORKER_HOUR",
    "DISLOCATION_SINGLE_JOB_MAX_HOURS",
    "MOVERS_BLOB_PREFIX",
    "candidate_run_keys",
    "check_partition",
    "estimate_for_spec",
    "estimate_run",
    "fetch_run",
    "latest_run_for",
    "movers_digest",
    "persist_run",
    "portfolio_table",
    "read_stored_blob",
    "refuse_over_single_job_bound",
]

#: Ratings one worker performs in an hour: NFR-493's measured throughput, the CR-927 closure
#: record's NFR table (`docs/closures/CR-00927-work-item-record-wk-671-scoring.md`, line 355,
#: "5,093,947 risks/hour/worker"; `RL-1504` "Details"). Replaced by Slice 3's measured
#: dislocation-path rate (`RL-1264` item 1) when its ledger records one.
DISLOCATION_RATINGS_PER_WORKER_HOUR: Final = 5_093_947

#: A run estimated above this many hours on one worker is refused before any Job: one
#: `dislocation.run` Job, not a fan-out, is the ruled shape (`RL-1504` item 1, DP-S4-1). The
#: Celery `visibility_timeout` exceeds it (`celery_app.build_celery`).
DISLOCATION_SINGLE_JOB_MAX_HOURS: Final = 4

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


async def latest_run_for(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    candidate_ref: str,
    candidate_bundle_hash: str,
    baseline_ref: str,
) -> DislocationRunRow | None:
    """The latest run naming this candidate at this bundle hash against this baseline.

    FR-257 limb (2)'s lookup (`06` FR-364; PL-1500 Task 3): the `ix_dislocation_runs_candidate`
    index serves it. "Latest" is by `created_at`, then `id` (a UUIDv7, so time-ordered) for a tie.
    """
    return (
        await session.execute(
            select(DislocationRunRow)
            .where(
                DislocationRunRow.workspace_id == workspace_id,
                DislocationRunRow.candidate_ref == candidate_ref,
                DislocationRunRow.candidate_bundle_hash == candidate_bundle_hash,
                DislocationRunRow.baseline_ref == baseline_ref,
            )
            .order_by(DislocationRunRow.created_at.desc(), DislocationRunRow.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()


async def candidate_run_keys(
    session: AsyncSession, *, workspace_id: UUID, candidate_ref: str
) -> list[tuple[str, str]]:
    """`(candidate_bundle_hash, baseline_ref)` of every run naming this candidate: what the
    limb (2) gate reads to say *why* `latest_run_for` found none (stale hash or other baseline)."""
    rows = await session.execute(
        select(DislocationRunRow.candidate_bundle_hash, DislocationRunRow.baseline_ref).where(
            DislocationRunRow.workspace_id == workspace_id,
            DislocationRunRow.candidate_ref == candidate_ref,
        )
    )
    return [(bundle_hash, baseline_ref) for bundle_hash, baseline_ref in rows.all()]


def portfolio_table(version: DatasetVersionRow) -> dict[str, Any]:
    """The portfolio's table: the first not starting with `_` (`_rejected` is the quarantine)."""
    entry = next((t for t in version.tables if not t["name"].startswith("_")), None)
    if entry is None:
        raise PlatformError(
            "NOT_FOUND", "Portfolio table not found", 404,
            f"Dataset Version {version.id} has no table to rate.",
        )
    return dict(entry)


async def read_stored_blob(
    session: AsyncSession, blob_store: BlobStore, sha256: str, what: str
) -> bytes:
    """A blob's bytes by digest, or 404 `NOT_FOUND` naming what was expected."""
    row = await session.get(BlobRow, sha256)
    if row is None:
        raise PlatformError(
            "NOT_FOUND", f"{what} blob is missing", 404,
            f"{what} names blob {sha256}, which is not in the store.",
        )
    return await blob_store.read(to_ref(row))


# ---------------------------------------------------------------------------
# The estimate, the partition check and the guard (FR-1399, RL-1264 item 3, RL-1504 items 1, 4).
# Run by `POST /dislocation-runs` and `POST /dislocation-runs/estimate` through one code path.
# ---------------------------------------------------------------------------

#: Above this many change groups Shapley gives way to the order-dependent method (03 §5.2).
_MAX_SHAPLEY_GROUPS: Final = 6


def check_partition(deltas: Sequence[BundleDelta], groups: Sequence[ChangeGroup] | None) -> None:
    """FR-1399: the change groups partition the derived changes exactly, else 422
    `VALIDATION_FAILED` naming each change left out, placed twice or not derived.

    The same rule `attribute` applies (its text, so a route refusal and a Job refusal read
    alike), asked here so a bad grouping costs no Job.
    """
    if groups is None:
        return
    derived = {d.id for d in deltas}
    seen: dict[str, int] = {}
    for group in groups:
        for change_id in group.changes:
            seen[change_id] = seen.get(change_id, 0) + 1
    left_out = [d.id for d in deltas if d.id not in seen]
    twice = sorted(c for c, n in seen.items() if n > 1)
    unknown = sorted(c for c in seen if c not in derived)
    if not (left_out or twice or unknown):
        return
    parts = []
    if left_out:
        parts.append("left out: " + ", ".join(left_out))
    if twice:
        parts.append("placed twice: " + ", ".join(twice))
    if unknown:
        parts.append("not derived changes: " + ", ".join(unknown))
    raise PlatformError(
        "VALIDATION_FAILED",
        "Change groups do not partition the derived changes",
        422,
        "change groups must partition the derived changes exactly (" + "; ".join(parts) + ")",
    )


def estimate_run(
    deltas: Sequence[BundleDelta], spec: DislocationSpec, policies: int
) -> DislocationEstimate:
    """The rating count and single-worker hours of a run with `deltas` over `policies` policies."""
    grouped = spec.change_groups is not None
    k = len(spec.change_groups) if spec.change_groups is not None else len(deltas)
    ratings = estimate_attribution_ratings(k, policies, grouped=grouped)
    return DislocationEstimate(
        derived_changes=len(deltas),
        policies=policies,
        estimated_ratings=ratings,
        estimated_worker_hours=ratings / DISLOCATION_RATINGS_PER_WORKER_HOUR,
        method="shapley" if k <= _MAX_SHAPLEY_GROUPS else "order_dependent",
    )


def refuse_over_single_job_bound(estimate: DislocationEstimate, *, groups: int | None) -> None:
    """RL-1504 item 1: a run estimated above `DISLOCATION_SINGLE_JOB_MAX_HOURS` on one worker
    is refused with 422 `VALIDATION_FAILED` naming K, the policy count and the estimate."""
    bound = DISLOCATION_SINGLE_JOB_MAX_HOURS * DISLOCATION_RATINGS_PER_WORKER_HOUR
    if estimate.estimated_ratings <= bound:
        return
    k = groups if groups is not None else estimate.derived_changes
    raise PlatformError(
        "VALIDATION_FAILED",
        "Dislocation run is too large for one Job",
        422,
        f"K = {k} changes over {estimate.policies} policies is {estimate.estimated_ratings} "
        f"ratings, an estimated {estimate.estimated_worker_hours:.1f} hours on one worker; "
        f"the bound is {DISLOCATION_SINGLE_JOB_MAX_HOURS} hours. Group the changes, or use a "
        "smaller portfolio.",
    )


async def estimate_for_spec(
    session: AsyncSession, *, workspace_id: UUID, spec: DislocationSpec, blob_store: BlobStore
) -> DislocationEstimate:
    """Resolve both versions and the portfolio, derive the changes, check the partition and
    estimate. Writes nothing; the caller decides whether to apply the guard and submit."""
    versions = []
    for ref in (spec.baseline_ref, spec.candidate_ref):
        if ref.type != "rating_version":
            raise PlatformError(
                "VALIDATION_FAILED", "Not a rating version reference", 422,
                f"{ref} is not a rating_version reference.",
            )
        versions.append(
            to_schema(
                await resolve_rating_version_ref(session, workspace_id=workspace_id, ref=ref)
            )
        )
    portfolio = await read_version(
        session, workspace_id=workspace_id, version_id=spec.portfolio_dataset_version_id
    )
    table = portfolio_table(portfolio)
    try:
        deltas = await derive_changes(
            versions[0], versions[1], WorkspaceResolver(session, workspace_id, blob_store)
        )
    except AttributionError as exc:
        raise PlatformError(
            exc.code, exc.code.replace("_", " ").title(), 422, safe_error_text(exc)
        ) from exc
    check_partition(deltas, spec.change_groups)
    return estimate_run(deltas, spec, int(table["row_count"]))
