"""The Phase 1b rating version — creation, approval, and the approvals fan-out (W7-3).

`FR-440`: the demo seeds a minimal rating version pinning an approved Model. The
lifecycle mirrors the model's — `create_rating_version` (draft), `submit_for_review`
(`draft → review`), and the approver's decision carrying to the artifact through
`apply_approval_decision`. The approvals resolver must resolve a `rating_version`
reference (FR-386) and refuse one that does not exist.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_rating_version_compile import _empty_pins, _minimal_algorithm
from sqlalchemy import select

from app.db.models import (
    ApprovalDecisionRow,
    ApprovalRequestRow,
    AuditEventRow,
    BlobRow,
    RatingVersionRow,
    RegressionSuiteRow,
    RegressionSuiteVersionRow,
    RoleAssignmentRow,
    RoleRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import dislocation_runs as dislocation_service
from app.platform import rating_algorithms as algorithm_service
from app.platform import rating_versions as rating_service
from app.platform import rbac
from app.platform import regression_runs as run_service
from app.platform import regression_suites as suite_service
from app.platform.blobs import BlobStore
from model_schema import (
    ActorKind,
    ArtifactRef,
    BlobRef,
    DecisionKind,
    Principal,
    RatingVersionStatus,
    RegressionRun,
    RegressionSuiteContent,
    ScopeType,
    new_uuid7,
    suite_content_hash,
)
from model_schema.dislocation import DislocationRun
from pricing_core.rating.compile import Bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle


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


@pytest.mark.req("FR-440")
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

    gate = await _gate(database, workspace_id)
    await gate.adopt(rating_id)  # DP-S3-1 forward: a golden quote and a passing run (T6b)
    async with database.unit_of_work() as session:
        _, request = await rating_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actuary,
            rating_version_id=rating_id, change_summary="demo rating version",
            blob_store=gate.blob_store, load_compiled=gate.load,
        )
        request_id = request.id
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        assert RatingVersionStatus(row.status) is RatingVersionStatus.REVIEW

    # Two approvers, because `06` §4.2's default policy asks two for a Rating Version. This
    # test used to approve on one, and passed only because the hook approved on any
    # decision (the approval status bypass, 2026-09-28).
    second = await _principal(database, workspace_id, "approver")
    for who, then in ((approver, RatingVersionStatus.REVIEW), (second, None)):
        async with database.unit_of_work() as session:
            request = await approval_service.decide(
                session,
                evidence_authors=rating_service.golden_quote_delta_authors,
                workspace_id=workspace_id, request_id=request_id,
                approver=who, decision=DecisionKind.APPROVE, comment="approved",
            )
            await rating_service.apply_approval_decision(
                session, workspace_id=workspace_id, actor=who, request=request
            )
        if then is not None:
            async with database.session() as session:
                row = await rating_service.load_rating_version(
                    session, workspace_id=workspace_id, rating_version_id=rating_id
                )
                assert RatingVersionStatus(row.status) is then  # one approval of two
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        assert RatingVersionStatus(row.status) is RatingVersionStatus.APPROVED
        assert row.approval_request_id == request_id


@pytest.mark.req("FR-440")
async def test_a_rating_version_reference_resolves_in_the_approvals_fanout(
    database: Database, workspace_id
) -> None:
    """`_resolve_the_artifact` accepts a real rating_version reference (FR-386) once it is
    in review, and refuses it while it is a draft (`06` FR-351, since 2026-09-28)."""
    from app.api.approvals import _resolve_rating_version

    analyst = await _principal(database, workspace_id, "analyst")
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    rating_id = await _draft(
        database, workspace_id, analyst,
        ArtifactRef(type="model", slug="fremtpl2-glm", version=1),
    )
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)
        with pytest.raises(PlatformError) as refused:
            await _resolve_rating_version(session, workspace_id=workspace_id, artifact_ref=ref)
        assert refused.value.code == "APPROVAL_SUBJECT_NOT_IN_REVIEW"

    gate = await _gate(database, workspace_id)
    await gate.adopt(rating_id)  # DP-S3-1 forward: a golden quote and a passing run (T6b)
    async with database.unit_of_work() as session:
        await rating_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actuary,
            rating_version_id=rating_id, change_summary="into review",
            blob_store=gate.blob_store, load_compiled=gate.load,
        )
    async with database.session() as session:
        assert await _resolve_rating_version(
            session, workspace_id=workspace_id, artifact_ref=ref
        )


@pytest.mark.req("FR-440")
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
    """The by-id read refuses an id that does not exist (FR-440, the 404 route)."""
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


def _read_headers(principal: Principal, workspace_id: UUID) -> dict[str, str]:
    from app.api.deps import DEV_PRINCIPAL_HEADER

    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


async def _draft_with_algorithm(
    database: Database, workspace_id: UUID, actor: Principal, version: int
) -> UUID:
    """A `fremtpl2-demo@1` whose algorithm is `fremtpl2-demo@<version>` (the numbers differ)."""
    async with database.unit_of_work() as session:
        row = await rating_service.create_rating_version(
            session, workspace_id=workspace_id, actor=actor,
            slug="fremtpl2-demo", dataset_version_id=new_uuid7(),
            model_ref=ArtifactRef(type="model", slug="fremtpl2-glm", version=1),
            algorithm_ref=ArtifactRef(
                type="rating_algorithm", slug="fremtpl2-demo", version=version
            ),
        )
        return row.id


@pytest.mark.req("FR-1531")
async def test_a_rating_version_reads_by_its_own_slug_at_version(
    api_client, workspace_id, principal, grant, database
) -> None:
    await grant("analyst")
    headers = _read_headers(principal, workspace_id)
    rating_id = await _draft_with_algorithm(database, workspace_id, principal, 5)

    by_pair = api_client.get("/api/v1/rating-versions/fremtpl2-demo@1", headers=headers)
    assert by_pair.status_code == 200, by_pair.text
    assert by_pair.json()["id"] == str(rating_id)

    by_id = api_client.get(f"/api/v1/rating-versions/{rating_id}", headers=headers)
    assert by_id.status_code == 200, by_id.text

    by_algorithm_number = api_client.get("/api/v1/rating-versions/fremtpl2-demo@5", headers=headers)
    assert by_algorithm_number.status_code == 404, by_algorithm_number.text
    assert by_algorithm_number.json()["code"] == "NOT_FOUND"
    assert by_algorithm_number.json()["detail"] == (
        "No rating version rating_version:fremtpl2-demo@5."
    )


@pytest.mark.req("FR-1531")
async def test_another_workspaces_rating_version_pair_is_not_found(
    api_client, workspace_id, principal, grant, database
) -> None:
    await grant("analyst")
    other = new_uuid7()
    owner = await _principal(database, other, "analyst")
    await _draft(database, other, owner, ArtifactRef(type="model", slug="fremtpl2-glm", version=1))
    response = api_client.get(
        "/api/v1/rating-versions/fremtpl2-demo@1", headers=_read_headers(principal, workspace_id)
    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND"
    assert response.json()["detail"] == "No rating version rating_version:fremtpl2-demo@1."


@pytest.mark.req("FR-1531")
async def test_the_rating_version_pair_read_needs_rating_read(
    api_client, workspace_id, principal, membership
) -> None:
    await membership()
    response = api_client.get(
        "/api/v1/rating-versions/fremtpl2-demo@1", headers=_read_headers(principal, workspace_id)
    )
    assert response.status_code == 403, response.text


@pytest.mark.req("FR-1531")
def test_the_rating_version_read_publishes_rating_version(app) -> None:
    operation = app.openapi()["paths"]["/api/v1/rating-versions/{slug}@{version}"]["get"]
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema == {"$ref": "#/components/schemas/RatingVersion"}


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


def _submittable_over_http(
    database: Database, workspace_id: UUID, principal: Principal, rating_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Make a draft made over HTTP submittable (DP-S3-1 forward, T6b): a golden quote, a
    passing run, a compiled bundle, and the route's bundle loader pointed at it."""
    import asyncio

    from app.api import score as score_api

    async def prepare() -> _Gate:
        gate = await _gate(database, workspace_id)
        await gate.adopt(UUID(rating_id))
        return gate

    gate = asyncio.get_event_loop().run_until_complete(prepare())

    async def fetch(*_args: Any, ref: ArtifactRef, **_kwargs: Any) -> CompiledBundle:
        return await gate.load(ref)

    monkeypatch.setattr(score_api, "_fetch_bundle", fetch)



def test_submit_rating_version_over_http(
    api_client, workspace_id, principal, grant, database, monkeypatch
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
    _submittable_over_http(database, workspace_id, principal, rating_id, monkeypatch)

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


@pytest.mark.req("FR-257")
@pytest.mark.req("FR-242")
def test_submit_writes_the_change_summary_on_the_version(
    api_client, workspace_id, principal, grant, database, monkeypatch
) -> None:
    """PL-1500 Task 7 (DP-E1-6 (a)): the version carries the summary it was submitted with.
    The submit answers with it, and a later GET of the version reads the same text. Red first:
    the submit response's `change_summary` is `None`, because nothing wrote the field."""
    import asyncio

    from app.api.deps import DEV_PRINCIPAL_HEADER

    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    headers = {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}
    created = api_client.post(
        "/api/v1/rating-versions",
        json={
            "slug": "fremtpl2-summary",
            "dataset_version_id": str(new_uuid7()),
            "model_ref": ArtifactRef(type="model", slug="fremtpl2-glm", version=1).model_dump(),
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    rating_id = created.json()["id"]
    _submittable_over_http(database, workspace_id, principal, rating_id, monkeypatch)

    summary = "Moved the young-driver relativity; see the structural diff."
    submitted = api_client.post(
        f"/api/v1/rating-versions/{rating_id}/submit",
        json={"change_summary": summary},
        headers=headers,
    )
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["change_summary"] == summary
    read = api_client.get(f"/api/v1/rating-versions/{rating_id}", headers=headers)
    assert read.status_code == 200, read.text
    assert read.json()["change_summary"] == summary


def test_a_blank_change_summary_cannot_submit_a_rating_version(
    api_client, workspace_id, principal, grant, database, monkeypatch
) -> None:
    """FR-257 limb 3 — the change summary, which the requirement delegates to FR-242.

    FR-257 (`03` §5, line 173) names **four** conditions a Rating Version must meet before
    `approved`: a passing Regression Suite, a Dislocation Run against the live version, *"a
    change summary (FR-242)"*, and a GIPP check where the insurer has enabled it. This
    marker evidences the third only. The other three are WK-672's and WK-673's and are recorded in
    register row F44, so `req-coverage.py` reporting FR-257 covered from here says nothing
    about them — the close audit takes FR-257's verdict from F44, never the coverage table.

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
    _submittable_over_http(database, workspace_id, principal, rating_id, monkeypatch)

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
    # `PlatformError(code, title, status, detail)` — the FR-352 sentence is the *detail*,
    # and asserting on it pins this raise site rather than merely the code, which four other
    # guards in `platform/approvals.py` also use.
    assert "FR-352" in problem["detail"], problem

    # The version is still submittable: the guard refused the submission, it did not consume it.
    ok = api_client.post(
        f"/api/v1/rating-versions/{rating_id}/submit",
        json={"change_summary": "widened the NCD ladder above 5 years"},
        headers=headers,
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["status"] == "review"


@pytest.mark.req("FR-450")
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


# -- the decision hook reads the real states (`06` FR-351; the approval status bypass) --


async def _two_approvers(database: Database, workspace_id: UUID) -> tuple[Principal, Principal]:
    """The default policy asks two distinct approvers for a Rating Version (`06` §4.2)."""
    return (
        await _principal(database, workspace_id, "approver"),
        await _principal(database, workspace_id, "approver"),
    )


async def _status_of(database: Database, workspace_id: UUID, rating_id: UUID) -> str:
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        return row.status


@pytest.mark.req("FR-351")
async def test_the_hook_refuses_a_rating_version_that_never_entered_review(
    database: Database, workspace_id
) -> None:
    """Negative: a request that reaches the hook for a **draft** version moves nothing.

    The request is made at service level, past the route's own refusal, because the hook is
    the second guard and has to hold on its own (defence in depth).
    """
    analyst = await _principal(database, workspace_id, "analyst")
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    first, second = await _two_approvers(database, workspace_id)
    rating_id = await _draft(
        database, workspace_id, analyst, ArtifactRef(type="model", slug="m-one", version=1)
    )
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)
    async with database.unit_of_work() as session:
        request = await approval_service.submit(
            session, workspace_id=workspace_id, submitter=actuary, artifact_ref=ref,
            change_summary="never submitted through the module",
        )
        request_id = request.id
    for approver in (first, second):
        async with database.unit_of_work() as session:
            request = await approval_service.decide(
                session,
                evidence_authors=rating_service.golden_quote_delta_authors,
                workspace_id=workspace_id, request_id=request_id,
                approver=approver, decision=DecisionKind.APPROVE,
            )

    async with database.unit_of_work() as session:
        request = await approval_service._load(session, workspace_id, request_id)
        with pytest.raises(PlatformError) as refused:
            await rating_service.apply_approval_decision(
                session, workspace_id=workspace_id, actor=second, request=request
            )
    assert refused.value.code == "APPROVAL_SUBJECT_NOT_IN_REVIEW"
    assert refused.value.status_code == 409
    assert await _status_of(database, workspace_id, rating_id) == "draft"


@pytest.mark.req("FR-351")
@pytest.mark.req("FR-354")
async def test_one_of_two_approvals_leaves_the_rating_version_in_review(
    database: Database, workspace_id
) -> None:
    """The hook moves the version only when the **request** is decided, not on every
    decision: one approval of two leaves the request, and so the version, in review."""
    analyst = await _principal(database, workspace_id, "analyst")
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    first, _ = await _two_approvers(database, workspace_id)
    rating_id = await _draft(
        database, workspace_id, analyst, ArtifactRef(type="model", slug="m-two", version=1)
    )
    gate = await _gate(database, workspace_id)
    await gate.adopt(rating_id)  # DP-S3-1 forward: a golden quote and a passing run (T6b)
    async with database.unit_of_work() as session:
        _, request = await rating_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actuary,
            rating_version_id=rating_id, change_summary="two approvals needed",
            blob_store=gate.blob_store, load_compiled=gate.load,
        )
        request_id = request.id
    async with database.unit_of_work() as session:
        request = await approval_service.decide(
            session,
            evidence_authors=rating_service.golden_quote_delta_authors,
            workspace_id=workspace_id, request_id=request_id,
            approver=first, decision=DecisionKind.APPROVE,
        )
        await rating_service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=first, request=request
        )
    assert await _status_of(database, workspace_id, rating_id) == "review"


@pytest.mark.req("FR-355")
async def test_a_rejected_rating_version_returns_to_draft_with_a_true_audit_before(
    database: Database, workspace_id
) -> None:
    """`06` FR-355: a rejection returns the artifact to draft. And the Audit Event's
    `before` is the row's real state, read from it, never a literal."""
    analyst = await _principal(database, workspace_id, "analyst")
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    first, _ = await _two_approvers(database, workspace_id)
    rating_id = await _draft(
        database, workspace_id, analyst, ArtifactRef(type="model", slug="m-three", version=1)
    )
    gate = await _gate(database, workspace_id)
    await gate.adopt(rating_id)  # DP-S3-1 forward: a golden quote and a passing run (T6b)
    async with database.unit_of_work() as session:
        row, request = await rating_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actuary,
            rating_version_id=rating_id, change_summary="to be rejected",
            blob_store=gate.blob_store, load_compiled=gate.load,
        )
        request_id, ref = request.id, f"rating_version:{row.slug}@{row.version}"
    async with database.unit_of_work() as session:
        request = await approval_service.decide(
            session,
            evidence_authors=rating_service.golden_quote_delta_authors,
            workspace_id=workspace_id, request_id=request_id,
            approver=first, decision=DecisionKind.REJECT, comment="Not yet.",
        )
        await rating_service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=first, request=request
        )
    assert await _status_of(database, workspace_id, rating_id) == "draft"
    async with database.session() as session:
        moves = (
            await session.execute(
                select(AuditEventRow.before, AuditEventRow.after).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.entity_ref == ref,
                    AuditEventRow.action.like("rating_version.%"),
                    AuditEventRow.action != "rating_version.created",
                )
            )
        ).all()
    assert [(b["status"], a["status"]) for b, a in moves] == [("review", "draft")]


async def _stale_draft_request(database: Database, workspace_id: UUID, slug: str):
    """A request opened on a version that never left `draft` — what the generic route could
    make before the approval status bypass was fixed. Made at service level, past the route."""
    analyst = await _principal(database, workspace_id, "analyst")
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    rating_id = await _draft(
        database, workspace_id, analyst, ArtifactRef(type="model", slug=slug, version=1)
    )
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)
    async with database.unit_of_work() as session:
        request = await approval_service.submit(
            session, workspace_id=workspace_id, submitter=actuary, artifact_ref=ref,
            change_summary="opened before the fix",
        )
        return rating_id, request.id, actuary


@pytest.mark.req("FR-355")
@pytest.mark.parametrize("close", ["reject", "withdraw"])
async def test_a_stale_request_on_a_draft_rating_version_can_still_be_closed(
    database: Database, workspace_id, close: str
) -> None:
    """A pre-fix request on a version still in `draft` must stay closable: rejecting or
    withdrawing it returns the version to where it already is, so the hook moves nothing
    rather than refusing — and the version can then be submitted properly."""
    rating_id, request_id, actuary = await _stale_draft_request(
        database, workspace_id, f"m-stale-{close}"
    )
    approver = await _principal(database, workspace_id, "approver")
    async with database.unit_of_work() as session:
        if close == "reject":
            request = await approval_service.decide(
                session,
                evidence_authors=rating_service.golden_quote_delta_authors,
                workspace_id=workspace_id, request_id=request_id,
                approver=approver, decision=DecisionKind.REJECT, comment="Stale.",
            )
        else:
            request = await approval_service.withdraw(
                session, workspace_id=workspace_id, request_id=request_id,
                actor=approver, reason="Stale.",
            )
        await rating_service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=request
        )
    assert await _status_of(database, workspace_id, rating_id) == "draft"

    gate = await _gate(database, workspace_id)
    await gate.adopt(rating_id)  # DP-S3-1 forward: a golden quote and a passing run (T6b)
    async with database.unit_of_work() as session:
        row, _ = await rating_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actuary,
            rating_version_id=rating_id, change_summary="submitted properly",
            blob_store=gate.blob_store, load_compiled=gate.load,
        )
    assert row.status == "review"


# ---------------------------------------------------------------------------
# FR-260: the golden-quote gate at submit, the pin and the delta (PL-1189 Task 5).
#
# Fixture: `test_rating_version_compile.py`'s `_minimal_algorithm` (payable premium =
# `premium_in * 2`), saved as `minimal@1`, and as `minimal@2` with `+ 1` where a test needs
# a second bundle that prices differently. Versions are compiled in-process with
# `compile_rating_version`, and `load_compiled` hydrates the returned `Bundle`.
# ---------------------------------------------------------------------------

_SUITE = "minimal-core"
_RUN_T0 = datetime(2026, 9, 28, 9, 0, 0, tzinfo=UTC)


def _algorithm(version: int, *, plus: int = 0) -> dict[str, Any]:
    body = copy.deepcopy(_minimal_algorithm())
    body["version"] = version
    if plus:
        body["steps"][1]["expr"] = f"premium_in * 2 + {plus}"
    return body


def _quote(
    name: str = "base-quote", *, premium_in: int = 100, expected: int = 200,
    tolerance: int = 0, note: str | None = None, quoted_at: str = "2026-09-28T09:00:00Z",
) -> dict[str, Any]:
    return {
        "name": name,
        "context": {
            "purpose": "new_business", "quoted_at": quoted_at,
            "effective_date": "2026-09-01", "inputs": {"premium_in": premium_in},
        },
        "expected": {"payable_premium_minor": expected, "outcome": "quoted"},
        "tolerance": {"money_minor": tolerance},
        "note": note,
    }


def _suite(*quotes: dict[str, Any], algorithm_slug: str = "minimal") -> RegressionSuiteContent:
    return RegressionSuiteContent.model_validate(
        {
            "algorithm_slug": algorithm_slug,
            "golden_quotes": list(quotes),
            "properties": [],
            "generation": {"cases": 10, "seed": 1, "strategy": "input_contract_sampling"},
        }
    )


class AccountingBlobStore(BlobStore):
    """A `BlobStore` whose `put` keeps the accounting row and the bytes in memory.

    The submit tests need a store that accepts a blob and counts it, not MinIO: the structural
    diff is stored at submission (PL-1500 Task 2), and `read` here returns what `put` was given.
    """

    def __init__(self) -> None:  # no S3 client: only `put` and `read` are used
        self.objects: dict[str, bytes] = {}

    async def put(self, session: Any, content: Any, media_type: str) -> BlobRef:
        body = content if isinstance(content, bytes) else b"".join(content)
        digest = hashlib.sha256(body).hexdigest()
        if await session.get(BlobRow, digest) is None:
            session.add(
                BlobRow(sha256=digest, bytes_=len(body), media_type=media_type, ref_count=0)
            )
            await session.flush()
        self.objects[digest] = body
        return BlobRef(sha256=digest, bytes=len(body), media_type=media_type)

    async def read(self, ref: BlobRef) -> bytes:
        return self.objects[ref.sha256]


async def record_dislocation_run(
    database: Database,
    workspace_id: UUID,
    *,
    candidate_ref: str,
    candidate_hash: str,
    baseline_ref: str,
    actor_id: UUID,
    quantiles: dict[str, str | None] | None = None,
    baseline_hash: str | None = None,
) -> UUID:
    """Persist a Dislocation Run naming `candidate_ref` at `candidate_hash` against
    `baseline_ref` (FR-257 limb (2)'s evidence), through the one writer `persist_run`.

    The run is empty-portfolio and valid; the limb (2) gate reads only its refs and hashes.
    `quantiles` is FR-224's observed figure (PL-1500 Task 4), left out of a limb (2) run."""
    body: dict[str, Any] = {
        "baseline_ref": baseline_ref,
        "candidate_ref": candidate_ref,
        "portfolio_dataset_version_id": str(new_uuid7()),
        "job_id": str(new_uuid7()),
        "policy_count": 0,
        "exposure_years": "0",
        "totals": {"baseline_premium_minor": 0, "candidate_premium_minor": 0, "change_pct": None},
        "outcomes": {
            "quoted_both": 0, "quoted_to_declined": 0, "declined_to_quoted": 0,
            "declined_both": 0, "error": 0, "zero_baseline": 0, "negative_baseline": 0,
        },
        "distribution": [
            {"band": "all", "policies": 0, "exposure_share": None, "mean_change_pct": None}
        ],
        "largest_movers_blob": "blob:sha256:" + "d" * 64,
        "errors": [],
    }
    if quantiles is not None:
        body["abs_change_pct_quantiles"] = quantiles
    run = DislocationRun.model_validate(body)
    async with database.unit_of_work() as session:
        row = await dislocation_service.persist_run(
            session, workspace_id=workspace_id, run=run,
            baseline_bundle_hash=baseline_hash or candidate_hash,
            candidate_bundle_hash=candidate_hash,
            actor_id=actor_id,
        )
        return row.id


class _Gate:
    """One workspace's golden-quote world: principals, algorithms, versions, suites."""

    def __init__(self, database: Database, workspace_id: UUID) -> None:
        self.database = database
        self.workspace_id = workspace_id
        self.bundles: dict[str, Bundle] = {}
        self.next_version = 1
        self.blob_store = AccountingBlobStore()

    async def setup(self) -> _Gate:
        self.analyst = await _principal(self.database, self.workspace_id, "analyst")
        self.actuary = await _principal(self.database, self.workspace_id, "pricing_actuary")
        self.approvers = [
            await _principal(self.database, self.workspace_id, "approver") for _ in range(2)
        ]
        await algorithm_service.create_algorithm(
            self.database, self.workspace_id, self.analyst.id, _algorithm(1)
        )
        await algorithm_service.create_algorithm(
            self.database, self.workspace_id, self.analyst.id, _algorithm(2, plus=1)
        )
        return self

    async def author(self, role: str = "analyst") -> Principal:
        return await _principal(self.database, self.workspace_id, role)

    async def suite(self, actor: Principal, content: RegressionSuiteContent) -> int:
        async with self.database.unit_of_work() as session:
            _, row = await suite_service.create_suite_version(
                session, workspace_id=self.workspace_id, actor=actor, slug=_SUITE,
                content=content, change_note="edit",
            )
            return row.version

    async def version(
        self, *, algorithm: str = "rating_algorithm:minimal@1", slug: str = "minimal-rv",
        compile_it: bool = True,
    ) -> UUID:
        number = self.next_version
        self.next_version += 1
        async with self.database.unit_of_work() as session:
            row = RatingVersionRow(
                workspace_id=self.workspace_id, slug=slug, version=number, status="draft",
                dataset_version_id=new_uuid7(), model_ref="model:motor-ad-frequency@7",
                created_by=self.analyst.id, algorithm_ref=algorithm, pins=_empty_pins(),
            )
            session.add(row)
            await session.flush()
            await audit_record_created(session, self.workspace_id, self.analyst, slug, number)
            rating_id = row.id
        if compile_it:
            async with self.database.unit_of_work() as session:
                bundle = await rating_service.compile_rating_version(
                    session, workspace_id=self.workspace_id, rating_version_id=rating_id,
                    blob_store=None,  # type: ignore[arg-type]
                )
            self.bundles[f"rating_version:{slug}@{number}"] = bundle
        return rating_id

    async def load(self, ref: ArtifactRef) -> CompiledBundle:
        return load_bundle(self.bundles[str(ref)])

    async def record_run(
        self, rating_id: UUID, overall: str = "pass", *, minutes: int = 0,
        suite_hash: str | None = None, bundle_hash: str | None = None,
    ) -> UUID:
        """Persist a Regression Run for this version's bundle and its algorithm's current
        suite (the pair FR-257 limb (1) reads), unless a hash is overridden for a test."""
        row = await self.row(rating_id)
        async with self.database.session() as session:
            found = await suite_service.current_suite_for_algorithm(
                session, workspace_id=self.workspace_id,
                algorithm_slug=await self._algorithm_slug(rating_id),
            )
        assert found is not None, "record_run needs a suite for the version's algorithm"
        failing = overall == "fail"
        run = RegressionRun.model_validate({
            "suite_ref": f"regression_suite:{found[0].slug}@{found[1].version}",
            "suite_content_hash": suite_hash or found[1].content_hash,
            "rating_version_ref": f"rating_version:{row.slug}@{row.version}",
            "bundle_hash": bundle_hash or row.bundle["content_hash"],  # type: ignore[index]
            "started_at": (_RUN_T0 + timedelta(minutes=minutes)).isoformat(),
            "finished_at": (_RUN_T0 + timedelta(minutes=minutes, seconds=3)).isoformat(),
            "overall": overall,
            "generation": {"seed": 1, "cases": 10, "hypothesis_version": "6.165.7"},
            "cases_blob": {"sha256": "c" * 64, "bytes": 2, "media_type": "application/json"},
            "golden_results": [],
            "property_results": [
                {"name": "p", "status": "fail", "cases_run": 10, "counterexample": {"x": 1},
                 "counterexample_minimal": True, "shrink": "completed",
                 "error_code": "PROPERTY_ASSERTION_FAILED"}
                if failing else {"name": "p", "status": "pass", "cases_run": 10}
            ],
        })
        async with self.database.unit_of_work() as session:
            saved = await run_service.persist_run(
                session, workspace_id=self.workspace_id, rating_version_id=rating_id,
                run=run, actor_id=self.analyst.id,
            )
            return saved.id

    async def _algorithm_slug(self, rating_id: UUID) -> str:
        row = await self.row(rating_id)
        return row.algorithm_ref.split(":")[1].split("@")[0]  # type: ignore[union-attr]

    async def ensure_suite(self, rating_id: UUID) -> None:
        """Author one golden-quote suite for the version's algorithm if it has none — the
        shared fixture DP-S3-1 (forward) requires of every version that must reach `review`.
        The quote is `_quote()`'s, which every fixture algorithm here prices exactly."""
        algorithm = await self._algorithm_slug(rating_id)
        async with self.database.session() as session:
            if await suite_service.current_suite_for_algorithm(
                session, workspace_id=self.workspace_id, algorithm_slug=algorithm
            ) is not None:
                return
        async with self.database.unit_of_work() as session:
            await suite_service.create_suite_version(
                session, workspace_id=self.workspace_id, actor=self.analyst,
                slug=f"{algorithm}-core", content=_suite(_quote(), algorithm_slug=algorithm),
                change_note="fixture golden quote",
            )

    async def adopt(self, rating_id: UUID) -> None:
        """Make an existing draft (made by `create_rating_version`, with no algorithm and no
        bundle) submittable: point it at `minimal@1`, compile it, give the algorithm a golden
        quote and record a passing run. For tests older than DP-S3-1 (T6b)."""
        async with self.database.unit_of_work() as session:
            row = await rating_service.load_rating_version(
                session, workspace_id=self.workspace_id, rating_version_id=rating_id
            )
            row.algorithm_ref = "rating_algorithm:minimal@1"
            row.pins = _empty_pins()
            key = f"rating_version:{row.slug}@{row.version}"
        async with self.database.unit_of_work() as session:
            self.bundles[key] = await rating_service.compile_rating_version(
                session, workspace_id=self.workspace_id, rating_version_id=rating_id,
                blob_store=None,  # type: ignore[arg-type]
            )
        await self.ensure_suite(rating_id)
        await self.record_run(rating_id, "pass")

    async def ensure_dislocation_run(self, rating_id: UUID) -> UUID | None:
        """Record the Dislocation Run FR-257 limb (2) needs, if the version has a baseline:
        the shared fixture that gives every existing submit test its new evidence (PL-1500
        Acceptance 10). A first version has no baseline and needs none. The run names the
        version's current bundle hash and the baseline the gate itself will pick."""
        row = await self.row(rating_id)
        if row.bundle is None:
            return None
        async with self.database.session() as session:
            policy = await approval_service.policy_for(session, self.workspace_id)
            baseline, _reason = await rating_service._dislocation_baseline(
                session, workspace_id=self.workspace_id, row=row, policy=policy
            )
        if baseline is None:
            return None
        return await record_dislocation_run(
            self.database, self.workspace_id,
            candidate_ref=f"rating_version:{row.slug}@{row.version}",
            candidate_hash=str(row.bundle["content_hash"]), baseline_ref=str(baseline),
            actor_id=self.analyst.id,
        )

    async def submit(
        self, rating_id: UUID, loader: Any = None, *, run: str | None = "pass",
        provision: bool = True, dislocation: bool = True,
    ) -> ApprovalRequestRow:
        """Submit. By default the version's algorithm is given a golden-quote suite if it has
        none, and a passing Regression Run is recorded first (FR-257 limb (1), DP-S3-1 forward):
        every golden-quote test that must reach `review` goes through this one fixture (T6b).
        `provision=False` authors no suite; `run=None` records no run; `dislocation=False`
        records no Dislocation Run (FR-257 limb (2), PL-1500 Task 3)."""
        if provision:
            await self.ensure_suite(rating_id)
        row = await self.row(rating_id)
        async with self.database.session() as session:
            has_suite = await suite_service.current_suite_for_algorithm(
                session, workspace_id=self.workspace_id,
                algorithm_slug=await self._algorithm_slug(rating_id),
            ) is not None
        if run is not None and has_suite and row.bundle is not None:
            await self.record_run(rating_id, run)
        if dislocation:
            await self.ensure_dislocation_run(rating_id)
        async with self.database.unit_of_work() as session:
            _, request = await rating_service.submit_for_review(
                session, workspace_id=self.workspace_id, actor=self.actuary,
                rating_version_id=rating_id, change_summary="golden",
                blob_store=self.blob_store, load_compiled=loader or self.load,
            )
            return request

    async def approve(self, request_id: UUID, approvers: list[Principal] | None = None) -> None:
        for who in approvers or self.approvers:
            async with self.database.unit_of_work() as session:
                request = await approval_service.decide(
                    session, workspace_id=self.workspace_id, request_id=request_id,
                    approver=who, decision=DecisionKind.APPROVE, comment="ok",
                    evidence_authors=rating_service.golden_quote_delta_authors,
                )
                await rating_service.apply_approval_decision(
                    session, workspace_id=self.workspace_id, actor=who, request=request
                )

    async def row(self, rating_id: UUID) -> RatingVersionRow:
        async with self.database.session() as session:
            return await rating_service.load_rating_version(
                session, workspace_id=self.workspace_id, rating_version_id=rating_id
            )

    async def evidence(self, rating_id: UUID) -> dict[str, Any]:
        return (await self.row(rating_id)).evidence["golden_quotes"]  # type: ignore[index]


async def audit_record_created(
    session: Any, workspace_id: UUID, actor: Principal, slug: str, version: int
) -> None:
    """The version's creation event, as `create_rating_version` writes it: #861's author
    check reads it, and a version without one could never be decided."""
    from app.platform import audit
    from model_schema import JobSource

    await audit.record(
        session, workspace_id=workspace_id, actor=actor, source=JobSource.API,
        action="rating_version.created", entity_ref=f"rating_version:{slug}@{version}",
        before={}, after={"status": "draft"},
    )


async def _gate(database: Database, workspace_id: UUID) -> _Gate:
    return await _Gate(database, workspace_id).setup()


async def _requests_for(database: Database, workspace_id: UUID) -> int:
    async with database.session() as session:
        return len(
            (
                await session.execute(
                    select(ApprovalRequestRow).where(
                        ApprovalRequestRow.workspace_id == workspace_id
                    )
                )
            ).scalars().all()
        )


# --- acceptance item 6: the gate --------------------------------------------------------


@pytest.mark.req("FR-260")
async def test_golden_mismatch_refuses_submission_and_leaves_the_version_draft(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote(expected=201)))
    rating_id = await gate.version()

    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id)
    assert refused.value.code == "GOLDEN_QUOTE_MISMATCH"
    assert refused.value.status_code == 409
    row = await gate.row(rating_id)
    assert row.status == "draft"
    assert (row.evidence or {}).get("golden_quotes") is None
    assert await _requests_for(database, workspace_id) == 0


@pytest.mark.req("FR-260")
async def test_golden_match_moves_to_review_and_pins_suite_and_bundle(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    content = _suite(_quote())
    await gate.suite(gate.analyst, content)
    rating_id = await gate.version()
    await gate.submit(rating_id)

    row = await gate.row(rating_id)
    assert row.status == "review"
    pinned = row.evidence["golden_quotes"]  # type: ignore[index]
    assert pinned["status"] == "checked"
    assert pinned["suite_ref"] == f"regression_suite:{_SUITE}@1"
    assert pinned["suite_content_hash"] == suite_content_hash(content)
    compiled = gate.bundles[f"rating_version:minimal-rv@{row.version}"]
    assert pinned["bundle_hash"] == compiled.content_hash
    assert pinned["bundle_hash"] == row.bundle["content_hash"]  # type: ignore[index]
    assert [r["status"] for r in pinned["results"]] == ["pass"]


@pytest.mark.req("FR-260")
async def test_golden_a_loaded_bundle_that_is_not_this_versions_is_refused(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rating_id = await gate.version()
    other = await gate.version(algorithm="rating_algorithm:minimal@2", slug="other-rv")
    other_bundle = gate.bundles[f"rating_version:other-rv@{(await gate.row(other)).version}"]

    async def wrong(_ref: ArtifactRef) -> CompiledBundle:
        return load_bundle(other_bundle)

    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id, loader=wrong)
    assert refused.value.code == "BUNDLE_COMPILE_FAILED"
    assert refused.value.status_code == 409
    row = await gate.row(rating_id)
    assert row.status == "draft"
    assert (row.evidence or {}).get("golden_quotes") is None


@pytest.mark.req("FR-260")
async def test_golden_a_suite_with_no_compiled_bundle_is_refused(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rating_id = await gate.version(compile_it=False)
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id)
    assert refused.value.code == "BUNDLE_COMPILE_FAILED"
    assert (await gate.row(rating_id)).status == "draft"


@pytest.mark.req("FR-260")
@pytest.mark.req("FR-257")
async def test_golden_no_suite_is_refused_as_incomplete_evidence(
    database: Database, workspace_id
) -> None:
    """DP-S3-1 (PL-1205 Task 6), FR-257 limb (1) only: a passing Regression Suite has at
    least one golden quote. **Changed from S2's expectation**, which was that a version with
    no suite reached `review` carrying `golden_quotes = {status: not_checked, reason:
    no_suite_for_algorithm}`; it now raises `EVIDENCE_INCOMPLETE` and nothing is written."""
    gate = await _gate(database, workspace_id)
    rating_id = await gate.version()
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id, provision=False)
    assert refused.value.code == "EVIDENCE_INCOMPLETE"
    assert "at least one golden quote" in (refused.value.detail or "")
    row = await gate.row(rating_id)
    assert row.status == "draft"
    assert (row.evidence or {}).get("golden_quotes") is None
    assert await _requests_for(database, workspace_id) == 0


@pytest.mark.req("FR-257")
async def test_a_suite_with_no_golden_quote_is_refused(
    database: Database, workspace_id
) -> None:
    """DP-S3-1, limb (1) only: a suite holding properties but zero golden quotes."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite())
    rating_id = await gate.version()
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id)
    assert refused.value.code == "EVIDENCE_INCOMPLETE"
    assert (await gate.row(rating_id)).status == "draft"


@pytest.mark.req("FR-257")
async def test_no_regression_run_refuses_submission(database: Database, workspace_id) -> None:
    """Limb (1) only: a passing Regression Suite; limbs (2)-(4) are not tested here."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rating_id = await gate.version()
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id, run=None)
    assert refused.value.code == "EVIDENCE_INCOMPLETE"
    assert "no Regression Run" in (refused.value.detail or "")
    assert (await gate.row(rating_id)).status == "draft"


@pytest.mark.req("FR-257")
async def test_a_failing_run_refuses_submission(database: Database, workspace_id) -> None:
    """Limb (1) only: a passing Regression Suite; limbs (2)-(4) are not tested here."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rating_id = await gate.version()
    await gate.record_run(rating_id, "fail")
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id, run=None)
    assert refused.value.code == "EVIDENCE_INCOMPLETE"
    assert "failed" in (refused.value.detail or "")


@pytest.mark.req("FR-257")
async def test_a_run_on_a_stale_bundle_hash_refuses_submission(
    database: Database, workspace_id
) -> None:
    """Limb (1) only: a passing Regression Suite; limbs (2)-(4) are not tested here."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rating_id = await gate.version()
    await gate.record_run(rating_id, "pass", bundle_hash="sha256:" + "9" * 64)
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id, run=None)
    assert refused.value.code == "EVIDENCE_INCOMPLETE"


@pytest.mark.req("FR-257")
async def test_a_run_on_another_suite_version_refuses_submission(
    database: Database, workspace_id
) -> None:
    """DP-S3-2, limb (1) only: the run's suite hash must equal the suite the gate pins, so
    a suite edited after the run is not approved on the stale run."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rating_id = await gate.version()
    await gate.record_run(rating_id, "pass")
    await gate.suite(gate.analyst, _suite(_quote(note="edited after the run")))
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id, run=None)
    assert refused.value.code == "EVIDENCE_INCOMPLETE"


@pytest.mark.req("FR-257")
async def test_an_earlier_pass_does_not_count_once_a_later_run_failed(
    database: Database, workspace_id
) -> None:
    """Audit A1, limb (1) only: pass, then a later fail on the same pair, is refused; a still
    later pass is accepted."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rating_id = await gate.version()
    await gate.record_run(rating_id, "pass", minutes=0)
    await gate.record_run(rating_id, "fail", minutes=5)
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id, run=None)
    assert refused.value.code == "EVIDENCE_INCOMPLETE"
    await gate.record_run(rating_id, "pass", minutes=10)
    await gate.submit(rating_id, run=None)
    assert (await gate.row(rating_id)).status == "review"


@pytest.mark.req("FR-257")
async def test_a_passing_run_is_recorded_and_golden_evidence_is_untouched(
    database: Database, workspace_id, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Limb (1) only: a passing Regression Suite; limbs (2)-(4) are not tested here. The run
    id is the one key written beside `golden_quotes`, which is byte-identical before and
    after the write (`PL-1205` acceptance item 10): the pinned value is snapshotted as the
    golden-quote gate returned it, at the last step before `submit` writes `evidence`."""
    gate = await _gate(database, workspace_id)
    content = _suite(_quote())
    await gate.suite(gate.analyst, content)
    rating_id = await gate.version()
    run_id = await gate.record_run(rating_id, "pass")
    real_run_gate = rating_service._regression_run_gate
    before: list[str] = []

    async def snapshotting(*args: Any, **kwargs: Any) -> UUID:
        before.append(json.dumps(kwargs["golden_quotes"], sort_keys=True))
        return await real_run_gate(*args, **kwargs)

    monkeypatch.setattr(rating_service, "_regression_run_gate", snapshotting)
    await gate.submit(rating_id, run=None)
    assert len(before) == 1  # the seam was reached, so the snapshot below is not vacuous
    row = await gate.row(rating_id)
    assert row.status == "review"
    evidence = row.evidence or {}
    assert evidence["regression_suite_run_id"] == str(run_id)
    assert set(evidence) == {"golden_quotes", "regression_suite_run_id"}
    pinned = evidence["golden_quotes"]
    assert json.dumps(pinned, sort_keys=True) == before[0]
    assert pinned["status"] == "checked"
    assert pinned["suite_content_hash"] == suite_content_hash(content)
    assert set(pinned) == {
        "status", "suite_ref", "suite_content_hash", "bundle_hash", "results", "delta",
    }


# --- acceptance item 7: the pin holds ---------------------------------------------------


@pytest.mark.req("FR-260")
async def test_golden_a_later_suite_version_does_not_change_what_was_pinned(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rating_id = await gate.version()
    await gate.submit(rating_id)
    before = await gate.evidence(rating_id)
    await gate.suite(gate.analyst, _suite(_quote(tolerance=9)))
    after = await gate.evidence(rating_id)
    assert after["suite_content_hash"] == before["suite_content_hash"]
    assert after["suite_ref"] == f"regression_suite:{_SUITE}@1"


# --- acceptance item 8: the delta -------------------------------------------------------


async def _approved_baseline(gate: _Gate, content: RegressionSuiteContent) -> UUID:
    await gate.suite(gate.analyst, content)
    rv1 = await gate.version()
    request = await gate.submit(rv1)
    await gate.approve(request.id)
    assert (await gate.row(rv1)).status == "approved"
    return rv1


@pytest.mark.req("FR-260")
async def test_golden_delta_lists_a_changed_expected_value_with_its_author(
    database: Database, workspace_id
) -> None:
    """The deputy's DP-S2-1 condition: B changes an expected value in v2; RV2's delta
    shows it, with B as the author read from v2's creation event."""
    gate = await _gate(database, workspace_id)
    rv1 = await _approved_baseline(gate, _suite(_quote()))
    b = await gate.author()
    await gate.suite(b, _suite(_quote(expected=201)))
    rv2 = await gate.version(algorithm="rating_algorithm:minimal@2")
    await gate.submit(rv2)

    delta = (await gate.evidence(rv2))["delta"]
    rv1_row = await gate.row(rv1)
    assert delta["baseline_rating_version_ref"] == f"rating_version:minimal-rv@{rv1_row.version}"
    assert delta["baseline_suite_ref"] == f"regression_suite:{_SUITE}@1"
    (change,) = delta["changes"]
    assert change["name"] == "base-quote"
    assert change["change"] == "changed"
    assert change["changed_fields"] == ["expected"]
    assert change["before"] == {"payable_premium_minor": 200, "outcome": "quoted"}
    assert change["after"] == {"payable_premium_minor": 201, "outcome": "quoted"}
    assert change["steps"] == [
        {"version": 2, "changed_fields": ["expected"], "author": str(b.id)}
    ]


@pytest.mark.req("FR-260")
async def test_golden_delta_lists_a_tolerance_only_widening_with_its_author(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    b = await gate.author()
    await gate.suite(b, _suite(_quote(tolerance=5)))
    rv2 = await gate.version()
    await gate.submit(rv2)

    (change,) = (await gate.evidence(rv2))["delta"]["changes"]
    assert change["change"] == "changed"
    assert change["changed_fields"] == ["tolerance"]
    assert change["before_tolerance"] == {"money_minor": 0}
    assert change["after_tolerance"] == {"money_minor": 5}
    assert change["steps"] == [
        {"version": 2, "changed_fields": ["tolerance"], "author": str(b.id)}
    ]


@pytest.mark.req("FR-260")
async def test_golden_delta_lists_added_and_removed_quotes(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote("old-quote")))
    await gate.suite(gate.analyst, _suite(_quote("new-quote", premium_in=50, expected=100)))
    rv2 = await gate.version()
    await gate.submit(rv2)
    changes = {c["name"]: c for c in (await gate.evidence(rv2))["delta"]["changes"]}
    assert changes["new-quote"]["change"] == "added"
    assert changes["new-quote"]["steps"][0]["changed_fields"] == ["added"]
    assert changes["old-quote"]["change"] == "removed"
    assert changes["old-quote"]["steps"][0]["changed_fields"] == ["removed"]


@pytest.mark.req("FR-260")
@pytest.mark.req("NFR-499")
async def test_golden_delta_records_a_context_change_by_hash_only(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    await gate.suite(gate.analyst, _suite(_quote(quoted_at="2026-09-29T09:00:00Z")))
    rv2 = await gate.version()
    await gate.submit(rv2)
    (change,) = (await gate.evidence(rv2))["delta"]["changes"]
    assert change["changed_fields"] == ["context"]
    assert change["before_context_hash"] != change["after_context_hash"]
    assert change["before_context_hash"].startswith("sha256:")
    assert "premium_in" not in repr(await gate.evidence(rv2))


@pytest.mark.req("FR-260")
async def test_golden_delta_with_no_approved_baseline_lists_every_quote_as_added(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote("a-quote"), _quote("b-quote")))
    rv = await gate.version()
    await gate.submit(rv)
    delta = (await gate.evidence(rv))["delta"]
    assert delta["baseline_rating_version_ref"] is None
    assert delta["baseline_suite_ref"] is None
    assert delta["baseline_suite_content_hash"] is None
    assert sorted((c["name"], c["change"]) for c in delta["changes"]) == [
        ("a-quote", "added"), ("b-quote", "added"),
    ]
    assert all(c["steps"][0]["author"] == str(gate.analyst.id) for c in delta["changes"])


@pytest.mark.req("FR-260")
async def test_golden_delta_baseline_is_the_later_approved_version(
    database: Database, workspace_id
) -> None:
    """RV_a pins suite v1 and RV_b suite v2; RV_b is approved first, RV_a second. The
    baseline is RV_a (approved later), not RV_b (the higher version)."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_a = await gate.version()
    req_a = await gate.submit(rv_a)
    await gate.suite(gate.analyst, _suite(_quote(tolerance=1)))
    rv_b = await gate.version()
    req_b = await gate.submit(rv_b)
    await gate.approve(req_b.id)
    await gate.approve(req_a.id)
    await gate.suite(gate.analyst, _suite(_quote(tolerance=2)))
    rv_c = await gate.version()
    await gate.submit(rv_c)
    delta = (await gate.evidence(rv_c))["delta"]
    assert delta["baseline_rating_version_ref"] == (
        f"rating_version:minimal-rv@{(await gate.row(rv_a)).version}"
    )
    assert delta["baseline_suite_ref"] == f"regression_suite:{_SUITE}@1"
    (change,) = delta["changes"]
    assert [s["version"] for s in change["steps"]] == [2, 3]


@pytest.mark.req("FR-260")
async def test_golden_delta_ignores_an_approved_version_of_another_algorithm(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    other = _algorithm(1)
    other["slug"] = "other-algo"
    await algorithm_service.create_algorithm(database, workspace_id, gate.analyst.id, other)
    rv_other = await gate.version(algorithm="rating_algorithm:other-algo@1", slug="other-rv")
    await gate.approve((await gate.submit(rv_other)).id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rv = await gate.version()
    await gate.submit(rv)
    assert (await gate.evidence(rv))["delta"]["baseline_rating_version_ref"] is None


@pytest.mark.req("FR-260")
async def test_golden_delta_a_later_cosmetic_edit_does_not_mask_a_substantive_one(
    database: Database, workspace_id
) -> None:
    """Audit finding F3: X widens a tolerance in v2, Y edits only the note in v3. One step,
    X's; Y appears nowhere."""
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    x, y = await gate.author(), await gate.author()
    await gate.suite(x, _suite(_quote(tolerance=3)))
    await gate.suite(y, _suite(_quote(tolerance=3, note="typo fixed")))
    rv2 = await gate.version()
    await gate.submit(rv2)
    (change,) = (await gate.evidence(rv2))["delta"]["changes"]
    assert change["steps"] == [
        {"version": 2, "changed_fields": ["tolerance"], "author": str(x.id)}
    ]
    assert str(y.id) not in repr(await gate.evidence(rv2))


@pytest.mark.req("FR-260")
async def test_golden_delta_two_substantive_edits_give_two_authored_steps(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    x, y = await gate.author(), await gate.author()
    await gate.suite(x, _suite(_quote(tolerance=3)))
    await gate.suite(y, _suite(_quote(expected=202, tolerance=3)))
    rv2 = await gate.version()
    await gate.submit(rv2)
    (change,) = (await gate.evidence(rv2))["delta"]["changes"]
    assert change["changed_fields"] == ["expected", "tolerance"]
    assert change["steps"] == [
        {"version": 2, "changed_fields": ["tolerance"], "author": str(x.id)},
        {"version": 3, "changed_fields": ["expected"], "author": str(y.id)},
    ]


@pytest.mark.req("FR-260")
@pytest.mark.req("FR-353")
async def test_golden_a_suite_version_with_no_creation_event_refuses_submit(
    database: Database, workspace_id
) -> None:
    """The author is read from the creation Audit Event, never `created_by`; a version
    written without one (here: straight into the table) is refused, fail-closed."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    content = _suite(_quote(tolerance=4))
    async with database.unit_of_work() as session:
        suite = (
            await session.execute(
                select(RegressionSuiteRow).where(RegressionSuiteRow.workspace_id == workspace_id)
            )
        ).scalar_one()
        session.add(
            RegressionSuiteVersionRow(
                suite_id=suite.id, version=2,
                content=content.model_dump(mode="json"),
                content_hash=suite_content_hash(content), change_note="no event",
                created_by=gate.analyst.id,
            )
        )
    rv = await gate.version()
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rv)
    assert refused.value.code == "APPROVAL_AUTHOR_UNRESOLVED"
    assert refused.value.status_code == 403
    assert (await gate.row(rv)).status == "draft"


# --- acceptance item 8a: the gate cannot be skipped, and the delta's author cannot approve


@pytest.mark.req("FR-260")
async def test_golden_bypass_a_draft_cannot_be_put_to_approval_directly(
    database: Database, workspace_id
) -> None:
    """#864's refusal, on a draft whose suite mismatches: the generic route's resolver
    refuses it (`APPROVAL_SUBJECT_NOT_IN_REVIEW`), so it never reaches `approved` without
    `evidence.golden_quotes`."""
    from app.api.approvals import _resolve_rating_version

    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote(expected=999)))
    rv = await gate.version()
    row = await gate.row(rv)
    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await _resolve_rating_version(
                session, workspace_id=workspace_id,
                artifact_ref=ArtifactRef(type="rating_version", slug=row.slug, version=row.version),
            )
    assert refused.value.code == "APPROVAL_SUBJECT_NOT_IN_REVIEW"
    row = await gate.row(rv)
    assert row.status == "draft"
    assert (row.evidence or {}).get("golden_quotes") is None


async def _decision_rows(database: Database, request_id: UUID) -> int:
    async with database.session() as session:
        return len(
            (
                await session.execute(
                    select(ApprovalDecisionRow).where(ApprovalDecisionRow.request_id == request_id)
                )
            ).scalars().all()
        )


@pytest.mark.req("FR-260")
@pytest.mark.req("FR-353")
async def test_golden_evidence_author_cannot_approve(database: Database, workspace_id) -> None:
    """DP-S2-6: C authors suite v2's change and holds `approval:decide`; C is neither the
    submitter nor the version's author, and is still refused, with no decision row."""
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    c = await gate.author()
    await _grant_role(database, workspace_id, c, "approver")
    await gate.suite(c, _suite(_quote(tolerance=2)))
    rv2 = await gate.version()
    request = await gate.submit(rv2)

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await approval_service.decide(
                session, workspace_id=workspace_id, request_id=request.id,
                approver=c, decision=DecisionKind.APPROVE, comment="mine",
                evidence_authors=rating_service.golden_quote_delta_authors,
            )
    assert refused.value.code == "APPROVAL_BY_EVIDENCE_AUTHOR"
    assert refused.value.status_code == 403
    assert await _decision_rows(database, request.id) == 0

    # A principal who authored no change in the delta is not refused by this rule.
    await gate.approve(request.id)
    assert (await gate.row(rv2)).status == "approved"


@pytest.mark.req("FR-260")
async def test_golden_evidence_author_decide_without_a_resolver_is_a_type_error(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    rv = await gate.version()
    request = await gate.submit(rv)
    async with database.unit_of_work() as session:
        with pytest.raises(TypeError, match="requires evidence_authors"):
            await approval_service.decide(
                session, workspace_id=workspace_id, request_id=request.id,
                approver=gate.approvers[0], decision=DecisionKind.APPROVE, comment="x",
            )
    assert await _decision_rows(database, request.id) == 0


@pytest.mark.req("FR-260")
async def test_golden_evidence_author_set_is_empty_without_golden_quotes(
    database: Database, workspace_id
) -> None:
    """Re-audit N2: a version in review with no `evidence.golden_quotes` at all (one that
    was in review when the gate shipped) gives an empty author set and is not refused."""
    gate = await _gate(database, workspace_id)
    rv = await gate.version()
    request = await gate.submit(rv)
    async with database.unit_of_work() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rv
        )
        row.evidence = None
        ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)
    async with database.session() as session:
        assert await rating_service.golden_quote_delta_authors(
            session, workspace_id=workspace_id, artifact_ref=ref
        ) == set()
    await gate.approve(request.id)
    assert (await gate.row(rv)).status == "approved"


async def _grant_role(
    database: Database, workspace_id: UUID, who: Principal, role: str
) -> None:
    async with database.unit_of_work() as session:
        role_row = (
            await session.execute(
                select(RoleRow).where(RoleRow.workspace_id == workspace_id, RoleRow.slug == role)
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id, principal_kind="user", principal_id=who.id,
                role_id=role_row.id, scope_type=ScopeType.WORKSPACE.value,
            )
        )


# --- route level: the loader refuses rather than degrades, and the approver sees the delta


@pytest.fixture
def golden_client() -> Any:
    from backend.tests.conftest_db import test_blob_bucket, test_database_url
    from fastapi.testclient import TestClient
    from pydantic import SecretStr

    from app.config import Environment, Settings
    from app.main import create_app

    settings = Settings(
        environment=Environment.LOCAL, version="test", dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()), blob_bucket=test_blob_bucket(),
    )
    with TestClient(create_app(settings), raise_server_exceptions=False) as client:
        yield client


def _route_headers(who: Principal, workspace_id: UUID) -> dict[str, str]:
    from app.api.deps import DEV_PRINCIPAL_HEADER

    return {DEV_PRINCIPAL_HEADER: str(who.id), "Workspace-Id": str(workspace_id)}


async def _member(database: Database, workspace_id: UUID, who: Principal) -> None:
    from app.db.models import WorkspaceMemberRow
    from app.platform import workspaces

    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        session.add(WorkspaceMemberRow(user_id=who.id, workspace_id=workspace_id))


@pytest.mark.req("FR-260")
async def test_golden_route_refuses_rather_than_scoring_the_slots_last_known_good(
    database: Database, workspace_id, golden_client: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Audit finding F5: with metadata storage failing, submit refuses. `_compiled_for`
    would have served the slot's last-known-good bundle; the gate never calls it."""
    from app.api import score as score_api

    gate = await _gate(database, workspace_id)
    await _member(database, workspace_id, gate.actuary)
    await gate.suite(gate.analyst, _suite(_quote()))
    rv = await gate.version()
    good = gate.bundles[f"rating_version:minimal-rv@{(await gate.row(rv)).version}"]

    async def metadata_down(*_args: Any, **_kwargs: Any) -> CompiledBundle:
        from sqlalchemy.exc import OperationalError

        raise OperationalError("SELECT rating_versions", {}, Exception("metadata storage down"))

    async def last_known_good(*_args: Any, **_kwargs: Any) -> CompiledBundle:
        return load_bundle(good)

    monkeypatch.setattr(score_api, "_fetch_bundle", metadata_down)
    monkeypatch.setattr(score_api, "_compiled_for", last_known_good)
    response = golden_client.post(
        f"/api/v1/rating-versions/{rv}/submit", json={"change_summary": "golden"},
        headers=_route_headers(gate.actuary, workspace_id),
    )
    # Refused (the storage failure surfaces as the platform's 500), never a 200 scored
    # against the slot's bundle.
    assert response.status_code == 500, response.text
    assert response.json()["code"] == "INTERNAL_ERROR"
    row = await gate.row(rv)
    assert row.status == "draft"
    assert (row.evidence or {}).get("golden_quotes") is None


@pytest.mark.req("FR-260")
async def test_golden_delta_is_visible_to_an_approver_through_the_api(
    database: Database, workspace_id, golden_client: Any
) -> None:
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    b = await gate.author()
    await gate.suite(b, _suite(_quote(tolerance=5)))
    rv2 = await gate.version()
    await gate.submit(rv2)
    approver = gate.approvers[0]
    await _member(database, workspace_id, approver)

    response = golden_client.get(
        f"/api/v1/rating-versions/{rv2}", headers=_route_headers(approver, workspace_id)
    )
    assert response.status_code == 200, response.text
    (change,) = response.json()["evidence"]["golden_quotes"]["delta"]["changes"]
    assert change["steps"][0]["author"] == str(b.id)
