"""The Phase 1b rating version (OD1, W7-3) — draft, submit, approve, read.

`FR-PLAT-67`: the demo seed creates and approves a minimal rating version that pins an
approved Model. The full `03` surface stays Phase 2. The lifecycle mirrors the model's:
`create_rating_version` (draft), `submit_for_review` (`draft → review`, creating the
approval request through the same governance `approvals.submit` the model uses), and the
approver's decision reaches the row through `apply_approval_decision`, the seam
`api/approvals.py::_carry_to_the_artifact` drives for every artifact type.
"""

from __future__ import annotations

from typing import Any, Literal, cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ApprovalRequestRow, ModelRow, RatingAlgorithmRow, RatingVersionRow
from app.errors import PlatformError
from app.platform import approvals, audit, rbac
from model_schema import (
    ArtifactRef,
    BundleMetadata,
    JobSource,
    Permission,
    Pins,
    Principal,
    RatingVersion,
    RatingVersionEvidence,
    RatingVersionStatus,
)
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle

__all__ = [
    "apply_approval_decision",
    "compile_rating_version",
    "create_rating_version",
    "load_rating_version",
    "submit_for_review",
    "to_schema",
]


def to_schema(row: RatingVersionRow) -> RatingVersion:
    """The row as the `03` §4.3 RatingVersion — the Phase 1b subset plus the W9-3 fields.

    The §4.3 fields are nullable so Phase 1b rows (the demo seed) keep parsing; a W9-3
    version carries `algorithm_ref` and `pins` for compilation.
    """
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
        algorithm_ref=(
            ArtifactRef.model_validate(row.algorithm_ref) if row.algorithm_ref else None
        ),
        pins=Pins.model_validate(row.pins) if row.pins else None,
        model_reference_mode=cast(
            Literal["exact", "approximation"], row.model_reference_mode or "exact"
        ),
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        bundle=BundleMetadata.model_validate(row.bundle) if row.bundle else None,
        change_summary=row.change_summary,
        evidence=RatingVersionEvidence.model_validate(row.evidence) if row.evidence else None,
        approval_request_id=row.approval_request_id,
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


async def compile_rating_version(
    session: AsyncSession, workspace_id: UUID, rating_version_id: UUID
) -> dict[str, Any]:
    """Compile a pinned Rating Version to a Bundle and store its metadata (W9-3).

    Resolves the algorithm and the pins through the workspace's own tables. Rate tables,
    reference tables and custom objectives have no tables yet (Phase 2), so a version
    pinning one is refused with `NOT_FOUND` — a compile cannot embed what does not exist.
    """
    row = await load_rating_version(
        session, workspace_id=workspace_id, rating_version_id=rating_version_id
    )
    schema = to_schema(row)

    class _Resolver:
        async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
            if ref.type == "rating_algorithm":
                algo = await session.scalar(
                    select(RatingAlgorithmRow).where(
                        RatingAlgorithmRow.workspace_id == workspace_id,
                        RatingAlgorithmRow.slug == ref.slug,
                        RatingAlgorithmRow.version == ref.version,
                    )
                )
                if algo is None:
                    raise PlatformError("NOT_FOUND", "Rating algorithm not found", 404)
                return ResolvedArtifact(status="approved", payload=algo.content)
            if ref.type == "model":
                model = await session.scalar(
                    select(ModelRow).where(
                        ModelRow.workspace_id == workspace_id,
                        ModelRow.model_family_slug == ref.slug,
                        ModelRow.version == ref.version,
                    )
                )
                if model is None:
                    raise PlatformError("NOT_FOUND", "Model not found", 404)
                return ResolvedArtifact(
                    status=model.status, payload={"status": model.status}
                )
            raise PlatformError(
                "NOT_FOUND",
                "Pinned artifact cannot be resolved yet",
                404,
                f"{ref} has no backend table yet (Phase 2); a compile cannot embed it.",
            )

    try:
        bundle = await compile_bundle(schema, _Resolver())
    except ValueError as exc:
        text = str(exc)
        code, _, detail = text.partition(": ")
        if not (code.isupper() and "_" in code):
            code, detail = "BUNDLE_COMPILE_FAILED", text
        raise PlatformError(
            code, code.replace("_", " ").title(), 422, detail
        ) from exc
    row.bundle = {
        "content_hash": bundle.content_hash,
        "bytes": len(bundle.model_dump_json().encode()),
        "compiled_at": bundle.compiled_at.isoformat(),
    }
    return dict(row.bundle or {})
