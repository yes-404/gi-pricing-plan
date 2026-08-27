"""The Phase 1b rating version — creation, approval, and the approvals fan-out (W7-3).

`FR-PLAT-67`: the demo seeds a minimal rating version pinning an approved Model. The
lifecycle mirrors the model's — `create_rating_version` (draft), `submit_for_review`
(`draft → review`), and the approver's decision carrying to the artifact through
`apply_approval_decision`. The approvals resolver must resolve a `rating_version`
reference (FR-GOV-36) and refuse one that does not exist.
"""

from __future__ import annotations

from uuid import UUID

import pytest
from sqlalchemy import select

from app.db.models import RoleAssignmentRow, RoleRow
from app.db.session import Database
from app.platform import approvals as approval_service
from app.platform import rating_versions as rating_service
from app.platform import rbac
from model_schema import (
    ActorKind,
    ArtifactRef,
    DecisionKind,
    Principal,
    RatingVersionStatus,
    ScopeType,
    new_uuid7,
)


async def _principal(database: Database, workspace_id: UUID, role: str) -> Principal:
    who = Principal(kind=ActorKind.USER, id=new_uuid7(), display=f"{role}@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role_row = (
            await session.execute(
                select(RoleRow).where(RoleRow.workspace_id == workspace_id, RoleRow.slug == role)
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=who.id,
                role_id=role_row.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )
    return who


async def _draft(
    database: Database, workspace_id: UUID, analyst: Principal, model_ref: ArtifactRef
) -> UUID:
    async with database.unit_of_work() as session:
        row = await rating_service.create_rating_version(
            session, workspace_id=workspace_id, actor=analyst,
            slug="fremtpl2-demo", dataset_version_id=new_uuid7(), model_ref=model_ref,
        )
        return row.id


@pytest.mark.req("FR-PLAT-67")
async def test_create_submit_approve_a_rating_version(
    database: Database, workspace_id
) -> None:
    """The full Phase 1b lifecycle: draft → review → approved, pinning the model."""
    analyst = await _principal(database, workspace_id, "analyst")
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    approver = await _principal(database, workspace_id, "approver")
    model_ref = ArtifactRef(type="model", slug="fremtpl2-glm", version=1)

    rating_id = await _draft(database, workspace_id, analyst, model_ref)
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        assert RatingVersionStatus(row.status) is RatingVersionStatus.DRAFT
        assert row.model_ref == str(model_ref)

    async with database.unit_of_work() as session:
        _, request = await rating_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actuary,
            rating_version_id=rating_id, change_summary="demo rating version",
        )
        request_id = request.id
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        assert RatingVersionStatus(row.status) is RatingVersionStatus.REVIEW

    async with database.unit_of_work() as session:
        request = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE, comment="approved",
        )
        await rating_service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=request
        )
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        assert RatingVersionStatus(row.status) is RatingVersionStatus.APPROVED
        assert row.approval_request_id == request_id


@pytest.mark.req("FR-PLAT-67")
async def test_a_rating_version_reference_resolves_in_the_approvals_fanout(
    database: Database, workspace_id
) -> None:
    """`_resolve_the_artifact` accepts a real rating_version reference (FR-GOV-36)."""
    from app.api.approvals import _resolve_rating_version

    analyst = await _principal(database, workspace_id, "analyst")
    rating_id = await _draft(
        database, workspace_id, analyst,
        ArtifactRef(type="model", slug="fremtpl2-glm", version=1),
    )
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)
        assert await _resolve_rating_version(
            session, workspace_id=workspace_id, artifact_ref=ref
        )


@pytest.mark.req("FR-PLAT-67")
async def test_an_unknown_rating_version_reference_is_refused(
    database: Database, workspace_id
) -> None:
    """A submission naming a rating version that does not exist resolves to nothing."""
    from app.api.approvals import _resolve_rating_version

    ref = ArtifactRef(type="rating_version", slug="no-such", version=1)
    async with database.session() as session:
        resolved = await _resolve_rating_version(
            session, workspace_id=workspace_id, artifact_ref=ref
        )
    assert resolved is False
