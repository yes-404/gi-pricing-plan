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


def test_the_rating_version_routes_read_over_http(
    api_client, workspace_id, principal, grant, database
) -> None:
    """`GET /rating-versions` and `GET /rating-versions/{id}` read what the seed writes.

    The by-id route is the plan's one read; the list route is the exit demo's discovery
    seam (W7-5). Both answer a `rating:read` caller with the seeded artifact.
    """
    import asyncio

    from app.api.deps import DEV_PRINCIPAL_HEADER

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }
    model_ref = ArtifactRef(type="model", slug="fremtpl2-glm", version=1)
    rating_id = asyncio.get_event_loop().run_until_complete(
        _draft(database, workspace_id, principal, model_ref)
    )

    listed = api_client.get("/api/v1/rating-versions", headers=headers)
    assert listed.status_code == 200, listed.text
    assert [item["id"] for item in listed.json()] == [str(rating_id)]

    detail = api_client.get(f"/api/v1/rating-versions/{rating_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    assert detail.json()["slug"] == "fremtpl2-demo"
    assert detail.json()["status"] == "draft"
    assert detail.json()["model_ref"] == "model:fremtpl2-glm@1"


def test_an_unknown_rating_version_id_is_a_404_over_http(
    api_client, workspace_id, principal, grant
) -> None:
    """The by-id read refuses an id that does not exist (FR-PLAT-67, the 404 route)."""
    import asyncio

    from app.api.deps import DEV_PRINCIPAL_HEADER

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }
    response = api_client.get(
        f"/api/v1/rating-versions/{new_uuid7()}", headers=headers
    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND"
