"""The lifecycle over HTTP: the routes, the ETag, and `wf-01` E6 → E10 (`02` §5.1).

The service tests own the transitions. This file owns the three things only the edge can be
wrong about:

* **the published contract** — `02` §5.1 declared `POST /models/{id}/submit` in Phase 0 and
  nothing served it. The endpoint audit compares the spec's table against the *published*
  contract, so an endpoint missing from both is invisible to it, which is how `01`'s
  reference lifecycle survived a workstream closure;
* **`If-Match`** — `00` §5.4's optimistic concurrency, deferred by W2 and then by W4 and
  reassigned here. `CONFLICT_STALE_WRITE` was absent from the error registry until now;
* **the seam** — the `decide` route carrying its decision into the model. The service
  function exists either way; whether the *route* calls it is a different claim, and the
  one `wf-01` E10 actually makes.

The model is fitted through the real path — ingestion, validation, a split, a GLM — because
a lifecycle test on a model that never had numbers is a test of the transition table, which
is already covered elsewhere.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_contracts import OPENAPI, _load
from backend.tests.test_diagnostics import _fit
from backend.tests.test_model_lifecycle import _grant_role
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.session import Database
from app.platform.blobs import BlobStore
from model_schema import ActorKind, Principal, new_uuid7


def _fitted(workspace_id: UUID) -> tuple[Principal, UUID, str, Principal]:
    """A fitted model, its family slug, its author and an approver — on this test's own loop.

    Every other HTTP test in the suite is synchronous, and `TestClient` is a blocking
    client, so the async fixtures cannot be requested here. Driving the real fit path from a
    loop created for the purpose is the honest alternative: the alternative that needs no
    loop is a model row inserted by hand, and then the test proves the routes work on a
    shape the fit path never produces.
    """
    from backend.tests.conftest_db import test_database_url

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        store = BlobStore(Settings(blob_bucket="gip-test-blobs"))
        try:
            loop.run_until_complete(store.ensure_bucket())
        except Exception as exc:  # pragma: no cover - infrastructure, not behaviour
            pytest.skip(f"MinIO not reachable: {type(exc).__name__}")
        try:
            actor, model_id = loop.run_until_complete(_fit(database, store, workspace_id))
            approver = Principal(
                kind=ActorKind.USER, id=new_uuid7(), display="approver@insurer.example"
            )
            loop.run_until_complete(
                _grant_role(database, workspace_id, approver.id, "approver")
            )
            slug = loop.run_until_complete(_slug_of(database, model_id))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()
    return actor, model_id, slug, approver


async def _slug_of(database: Database, model_id: UUID) -> str:
    """The family slug behind an id.

    Read from the database rather than over the API because there was **no** `GET /models`
    list route — `02` §5.1 declared none, and inventing one for a test's convenience would
    have added an endpoint to the surface with no requirement behind it.

    **`GET /models` exists from 2026-08-22** (W5, the audit-remediation slice): the gap was
    a defect in §5.1 rather than a decision, and this docstring is the record of where it
    was noticed. The direct read stays, because the setup for a lifecycle test should not
    depend on a second route being correct — `test_api_models` owns the list route.
    """
    from sqlalchemy import select

    from app.db.models import ModelRow

    async with database.session() as session:
        return (
            await session.execute(
                select(ModelRow.model_family_slug).where(ModelRow.id == model_id)
            )
        ).scalar_one()


# -- The published contract ---------------------------------------------------------------


@pytest.mark.req("FR-MODEL-64")
def test_the_lifecycle_routes_are_published() -> None:
    """Declared in `02` §5.1 since Phase 0, served by nothing until this slice."""
    paths = _load(OPENAPI)["paths"]
    assert "/api/v1/models/{model_id}/submit" in paths
    assert "post" in paths["/api/v1/models/{model_id}/submit"]
    assert "/api/v1/models/{model_id}/archive" in paths
    assert "post" in paths["/api/v1/models/{model_id}/archive"]


@pytest.mark.req("FR-PLAT-47")
def test_the_lifecycle_routes_declare_if_match_and_the_stale_write_conflict() -> None:
    """`00` §5.4 is part of the contract a client generates from, not a runtime detail. A
    required header absent from the published spec is a 409 nobody's client expects."""
    submit = _load(OPENAPI)["paths"]["/api/v1/models/{model_id}/submit"]["post"]
    headers = [p["name"] for p in submit.get("parameters", []) if p.get("in") == "header"]
    assert "If-Match" in headers
    assert "409" in submit["responses"]


# -- `If-Match` ---------------------------------------------------------------------------


@pytest.mark.req("FR-PLAT-47")
def test_a_submission_without_if_match_is_refused(
    api_client: TestClient, workspace_id
) -> None:
    """Required, not optional. `00` §5.4 says mutating requests on versioned entities
    *require* `If-Match`; a header the server accepts the absence of is a convention rather
    than a precondition, and a client that never learned to send it never finds out."""
    actor, model_id, _slug, _ = _fitted(workspace_id)
    refused = api_client.post(
        f"/api/v1/models/{model_id}/submit",
        json={"change_summary": "ready"},
        headers=_headers(actor.id, workspace_id),
    )
    assert refused.status_code == 409, refused.text
    assert refused.json()["code"] == "CONFLICT_STALE_WRITE"


@pytest.mark.req("FR-PLAT-47")
def test_a_stale_if_match_is_refused_and_the_current_one_is_accepted(
    api_client: TestClient, workspace_id
) -> None:
    """The ETag is over the status, so the value a caller read before someone else acted is
    the value that must fail. What it guards is the caller's *view* — models are immutable
    (`02` R2), so this is not a lost update to a field; it is the difference between "your
    transition is invalid" and "what you read is stale", and only the second is actionable."""
    actor, model_id, slug, _ = _fitted(workspace_id)
    headers = _headers(actor.id, workspace_id)

    stale = api_client.post(
        f"/api/v1/models/{model_id}/submit",
        json={"change_summary": "ready"},
        headers={**headers, "If-Match": 'W/"model:nothing-like-it"'},
    )
    assert stale.status_code == 409, stale.text
    assert stale.json()["code"] == "CONFLICT_STALE_WRITE"

    etag = api_client.get(f"/api/v1/models/{slug}", headers=headers).headers["etag"]
    accepted = api_client.post(
        f"/api/v1/models/{model_id}/submit",
        json={"change_summary": "ready"},
        headers={**headers, "If-Match": etag},
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["status"] == "review"



@pytest.mark.req("FR-PLAT-47")
def test_the_model_etag_changes_when_the_status_does(
    api_client: TestClient, workspace_id
) -> None:
    """An ETag that did not move on a transition would validate a stale view for ever."""
    actor, model_id, slug, _ = _fitted(workspace_id)
    headers = _headers(actor.id, workspace_id)

    before = api_client.get(f"/api/v1/models/{slug}", headers=headers).headers["etag"]
    api_client.post(
        f"/api/v1/models/{model_id}/submit",
        json={"change_summary": "ready"},
        headers={**headers, "If-Match": before},
    )
    after = api_client.get(f"/api/v1/models/{slug}", headers=headers).headers["etag"]
    assert before != after


# -- The seam: E6 → E10 over HTTP ---------------------------------------------------------


@pytest.mark.req("FR-MODEL-64")
def test_the_journeys_approval_arm_runs_end_to_end(
    api_client: TestClient, workspace_id
) -> None:
    """`wf-01` E6 → E10, over the routes an actuary and an approver actually use.

    Before this slice the arm stopped at E6: the route did not exist, and even with the
    service function in place an approved *request* left the model in `review` unless the
    route carried the decision across. That is the claim this test makes and the service
    tests cannot.
    """
    actor, model_id, slug, approver = _fitted(workspace_id)
    author = _headers(actor.id, workspace_id)
    reviewer = _headers(approver.id, workspace_id)

    etag = api_client.get(f"/api/v1/models/{slug}", headers=author).headers["etag"]
    submitted = api_client.post(
        f"/api/v1/models/{model_id}/submit",
        json={"change_summary": "first AD frequency model, urban relativity 1.98"},
        headers={**author, "If-Match": etag},
    )
    assert submitted.status_code == 200, submitted.text
    request_id = submitted.json()["approval_request_id"]
    assert request_id is not None

    # E8: the approver finds it in the queue.
    queue = api_client.get(
        "/api/v1/approval-requests", headers=reviewer, params={"status": "review"}
    )
    assert queue.status_code == 200, queue.text
    assert any(item["id"] == request_id for item in queue.json()["items"])

    # E9, and its negative: the submitter cannot approve their own work.
    mine = api_client.post(
        f"/api/v1/approval-requests/{request_id}/decide",
        json={"decision": "approve", "comment": "mine, and fine"},
        headers=author,
    )
    assert mine.status_code in (403, 404), mine.text

    decided = api_client.post(
        f"/api/v1/approval-requests/{request_id}/decide",
        json={"decision": "approve", "comment": "lift and A/E both hold on the holdout"},
        headers=reviewer,
    )
    assert decided.status_code == 200, decided.text
    assert decided.json()["status"] == "approved"

    # E10: and the artifact moved, which is the whole point of the arm.
    after = api_client.get(f"/api/v1/models/{slug}", headers=author)
    assert after.status_code == 200, after.text
    assert after.json()["status"] == "approved"


@pytest.mark.req("FR-GOV-13")
def test_requesting_changes_returns_the_model_to_fitted_over_the_api(
    api_client: TestClient, workspace_id
) -> None:
    """The amendment to `06` FR-GOV-13, at the edge: a model returned from review is
    `fitted` and resubmittable, not `draft` and apparently unfitted."""
    actor, model_id, slug, approver = _fitted(workspace_id)
    author = _headers(actor.id, workspace_id)
    reviewer = _headers(approver.id, workspace_id)

    etag = api_client.get(f"/api/v1/models/{slug}", headers=author).headers["etag"]
    submitted = api_client.post(
        f"/api/v1/models/{model_id}/submit",
        json={"change_summary": "ready"},
        headers={**author, "If-Match": etag},
    )
    request_id = submitted.json()["approval_request_id"]

    api_client.post(
        f"/api/v1/approval-requests/{request_id}/decide",
        json={"decision": "request_changes", "comment": "reband driver age first"},
        headers=reviewer,
    )
    after = api_client.get(f"/api/v1/models/{slug}", headers=author).json()
    assert after["status"] == "fitted"
    assert after["fit_result"] is not None


@pytest.mark.req("FR-MODEL-64")
def test_submitting_requires_the_submit_permission(
    api_client: TestClient, workspace_id
) -> None:
    """`model:submit` is held by `pricing_actuary` and not by `analyst`. An analyst may fit
    and explore; putting a model in front of an approver starts a governed process."""
    _actor, model_id, _slug, _ = _fitted(workspace_id)
    outsider = Principal(
        kind=ActorKind.USER, id=new_uuid7(), display="analyst@insurer.example"
    )
    loop = asyncio.new_event_loop()
    try:
        from backend.tests.conftest_db import test_database_url

        database = Database(Settings(database_url=test_database_url()))
        try:
            loop.run_until_complete(
                _grant_role(database, workspace_id, outsider.id, "analyst")
            )
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()

    refused = api_client.post(
        f"/api/v1/models/{model_id}/submit",
        json={"change_summary": "ready"},
        headers={**_headers(outsider.id, workspace_id), "If-Match": 'W/"anything"'},
    )
    assert refused.status_code == 403, refused.text
