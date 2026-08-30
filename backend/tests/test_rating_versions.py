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


def test_create_rating_version_over_http(
    api_client, workspace_id, principal, grant, database
) -> None:
    """POST /api/v1/rating-versions creates a draft rating version over HTTP."""
    import asyncio

    from app.api.deps import DEV_PRINCIPAL_HEADER

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }
    model_ref = ArtifactRef(type="model", slug="fremtpl2-glm", version=1)
    dataset_version_id = new_uuid7()
    body = {
        "slug": "fremtpl2-demo",
        "dataset_version_id": str(dataset_version_id),
        "model_ref": model_ref.model_dump(),
    }

    response = api_client.post("/api/v1/rating-versions", json=body, headers=headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["slug"] == "fremtpl2-demo"
    assert data["status"] == "draft"
    assert data["model_ref"] == "model:fremtpl2-glm@1"
    assert data["dataset_version_id"] == str(dataset_version_id)


def test_submit_rating_version_over_http(
    api_client, workspace_id, principal, grant, database
) -> None:
    """POST /api/v1/rating-versions/{id}/submit moves to review over HTTP."""
    import asyncio

    from app.api.deps import DEV_PRINCIPAL_HEADER

    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))

    # Create a draft rating version
    headers = {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }
    model_ref = ArtifactRef(type="model", slug="fremtpl2-glm", version=1)
    dataset_version_id = new_uuid7()
    create_body = {
        "slug": "fremtpl2-demo",
        "dataset_version_id": str(dataset_version_id),
        "model_ref": model_ref.model_dump(),
    }
    create_response = api_client.post("/api/v1/rating-versions", json=create_body, headers=headers)
    assert create_response.status_code == 201, create_response.text
    rating_id = create_response.json()["id"]

    # Submit for review
    submit_body = {"change_summary": "demo rating version"}
    submit_response = api_client.post(
        f"/api/v1/rating-versions/{rating_id}/submit",
        json=submit_body,
        headers=headers,
    )
    assert submit_response.status_code == 200, submit_response.text
    data = submit_response.json()
    assert data["status"] == "review"
    assert data["id"] == rating_id


@pytest.mark.req("FR-RATE-40")
def test_a_blank_change_summary_cannot_submit_a_rating_version(
    api_client, workspace_id, principal, grant, database
) -> None:
    """FR-RATE-40 limb 3 — the change summary, which the requirement delegates to FR-RATE-27.

    FR-RATE-40 (`03` §5, line 173) names **four** conditions a Rating Version must meet before
    `approved`: a passing Regression Suite, a Dislocation Run against the live version, *"a
    change summary (FR-RATE-27)"*, and a GIPP check where the insurer has enabled it. This
    marker evidences the third only. The other three are W12's and W13's and are recorded in
    register row F44, so `req-coverage.py` reporting FR-RATE-40 covered from here says nothing
    about them — the close audit takes FR-RATE-40's verdict from F44, never the coverage table.

    **The summary is `"   "` rather than `""` on purpose, and the code is asserted as well as
    the status.** `RatingVersionSubmit` (`api/models.py:276`) declares `change_summary: str`
    with no `min_length` — unlike `SubmitApproval` in `api/approvals.py`, which has
    `Field(min_length=1)` — so on *this* route both `""` and `"   "` clear Pydantic and reach
    `approvals.submit`'s guard. Asserting the code pins which guard refused: were anyone to add
    `min_length` to the model, a status-only assertion would silently start testing Pydantic's
    422 instead of the platform's, and go on passing while the thing it was written to prove
    stopped being exercised.
    """
    import asyncio

    from app.api.deps import DEV_PRINCIPAL_HEADER

    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    headers = {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }
    create_response = api_client.post(
        "/api/v1/rating-versions",
        json={
            "slug": "fremtpl2-demo",
            "dataset_version_id": str(new_uuid7()),
            "model_ref": ArtifactRef(type="model", slug="fremtpl2-glm", version=1).model_dump(),
        },
        headers=headers,
    )
    assert create_response.status_code == 201, create_response.text
    rating_id = create_response.json()["id"]

    # `submit_for_review` refuses a non-draft version with 409 *before* reaching the change
    # summary, so the version must be draft for this test to be testing what it says.
    assert create_response.json()["status"] == "draft"

    response = api_client.post(
        f"/api/v1/rating-versions/{rating_id}/submit",
        json={"change_summary": "   "},
        headers=headers,
    )

    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED", problem
    assert problem["title"] == "A change summary is required", problem
    # `PlatformError(code, title, status, detail)` — the FR-GOV-10 sentence is the *detail*,
    # and asserting on it pins this raise site rather than merely the code, which four other
    # guards in `platform/approvals.py` also use.
    assert "FR-GOV-10" in problem["detail"], problem

    # The version is still submittable: the guard refused the submission, it did not consume it.
    ok = api_client.post(
        f"/api/v1/rating-versions/{rating_id}/submit",
        json={"change_summary": "widened the NCD ladder above 5 years"},
        headers=headers,
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["status"] == "review"


@pytest.mark.req("FR-PLAT-47")
def test_the_submit_route_documents_the_422_it_returns(app) -> None:
    """A client cannot handle a status the contract does not mention.

    `test_contracts.py`'s `test_every_operation_documents_the_problems_it_returns` asserts that
    401 is documented and that *something* beyond 200/201 is — which this route satisfied on
    409 alone, so its missing 422 survived that check. `api/responses.py`'s `problems`
    docstring names the class: *"Any route taking a path or query parameter can return 422 …
    seven routes omitted it and published FastAPI's `HTTPValidationError` instead, which is a
    second error shape a client would have to branch on."* This route is the eighth, and it
    returns 422 for two independent reasons — a non-UUID `rating_version_id`, and the blank
    change summary the test above proves.
    """
    responses = app.openapi()["paths"]["/api/v1/rating-versions/{rating_version_id}/submit"][
        "post"
    ]["responses"]

    assert "422" in responses, sorted(responses)
    # Ours, not FastAPI's `HTTPValidationError` — the second shape is the actual defect.
    assert "application/problem+json" in responses["422"]["content"], responses["422"]
