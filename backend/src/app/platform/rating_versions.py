"""The Phase 1b rating version (OD1, W7-3) — draft, submit, approve, read.

`FR-PLAT-67`: the demo seed creates and approves a minimal rating version that pins an
approved Model. The full `03` surface stays Phase 2. The lifecycle mirrors the model's:
`create_rating_version` (draft), `submit_for_review` (`draft → review`, creating the
approval request through the same governance `approvals.submit` the model uses), and the
approver's decision reaches the row through `apply_approval_decision`, the seam
`api/approvals.py::_carry_to_the_artifact` drives for every artifact type.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ApprovalRequestRow, RatingVersionRow
from app.errors import PlatformError
from app.platform import approvals, audit, rbac
from model_schema import (
    ArtifactRef,
    JobSource,
    Permission,
    Principal,
    RatingVersion,
    RatingVersionStatus,
)

__all__ = [
    "apply_approval_decision",
    "create_rating_version",
    "load_rating_version",
    "submit_for_review",
    "to_schema",
]


def to_schema(row: RatingVersionRow) -> RatingVersion:
    """The row as the `03` §4.3 Phase 1b subset (`FR-PLAT-67`)."""
    return RatingVersion(
        id=row.id,
        workspace_id=row.workspace_id,
        slug=row.slug,
        version=row.version,
        status=RatingVersionStatus(row.status),
        dataset_version_id=row.dataset_version_id,
        model_ref=ArtifactRef.model_validate(row.model_ref),
        created_at=row.created_at,
        created_by=row.created_by,
        updated_at=row.updated_at,
    )


async def load_rating_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rating_version_id: UUID,
) -> RatingVersionRow:
    """The row, scoped to the workspace so a cross-workspace id reads as 404."""
    row = await session.get(RatingVersionRow, rating_version_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Rating version not found", 404, f"No rating version {rating_version_id}."
        )
    return row


async def create_rating_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    dataset_version_id: UUID,
    model_ref: ArtifactRef,
) -> RatingVersionRow:
    """Create a draft rating version pinned to the approved model (`FR-PLAT-67`)."""
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.RATING_WRITE,
    )
    next_version = 1 + (
        await session.execute(
            select(func.coalesce(func.max(RatingVersionRow.version), 0)).where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == slug,
            )
        )
    ).scalar_one()
    row = RatingVersionRow(
        workspace_id=workspace_id,
        slug=slug,
        version=next_version,
        status=RatingVersionStatus.DRAFT.value,
        dataset_version_id=dataset_version_id,
        model_ref=str(model_ref),
        created_by=actor.id,
    )
    session.add(row)
    await session.flush()
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="rating_version.created",
        entity_ref=f"rating_version:{slug}@{next_version}",
        before={},
        after={"status": RatingVersionStatus.DRAFT.value, "model_ref": str(model_ref)},
    )
    return row


async def submit_for_review(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    rating_version_id: UUID,
    change_summary: str,
) -> tuple[RatingVersionRow, ApprovalRequestRow]:
    """`draft → review`, creating the approval request through governance."""
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.RATING_SUBMIT,
    )
    row = await load_rating_version(
        session, workspace_id=workspace_id, rating_version_id=rating_version_id
    )
    if RatingVersionStatus(row.status) is not RatingVersionStatus.DRAFT:
        raise PlatformError(
            "VALIDATION_FAILED",
            "A rating version must be draft to submit",
            409,
            f"Rating version {row.slug}@{row.version} is {row.status}, not draft.",
        )
    request = await approvals.submit(
        session,
        workspace_id=workspace_id,
        submitter=actor,
        artifact_ref=ArtifactRef(type="rating_version", slug=row.slug, version=row.version),
        change_summary=change_summary,
    )
    row.status = RatingVersionStatus.REVIEW.value
    row.approval_request_id = request.id
    await session.flush()
    return row, request


async def apply_approval_decision(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    request: ApprovalRequestRow,
) -> RatingVersionRow | None:
    """Carry a governance decision into the artifact (W7-3, FR-PLAT-67).

    Returns `None` when the request is about something other than a Rating Version, so the
    caller can drive every artifact type through one call per module. Called in the same
    transaction as the decision, exactly as the model's sibling.
    """
    if request.artifact_type != "rating_version":
        return None

    ref = ArtifactRef.model_validate(request.artifact_ref)
    row = (
        await session.execute(
            select(RatingVersionRow)
            .where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == ref.slug,
                RatingVersionRow.version == ref.version,
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if row is None:
        return None

    row.status = RatingVersionStatus.APPROVED.value
    row.updated_at = func.now()
    await session.flush()
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="rating_version.approved",
        entity_ref=f"rating_version:{ref.slug}@{ref.version}",
        before={"status": RatingVersionStatus.REVIEW.value},
        after={"status": RatingVersionStatus.APPROVED.value},
    )
    return row
