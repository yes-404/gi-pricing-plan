"""WF-702 Route B — the expression objective, walked over HTTP (`PL-1268` Acceptance 7, SL-1275).

`docs/workflows/WF-00702-custom-objective-lifecycle.md` Route B: §4.6's example objective
(`asymmetric-burning-cost`) goes from create through derive, certify
(`certified_with_findings`, convexity `violated`) and submit, to `approved` by two non-author
Approvers, with the flag on; with the flag at its default in another workspace the create is
refused 409 `OBJECTIVE_KIND_NOT_ENABLED`. Run it with
`uv run pytest backend/tests/test_wf702_route_b.py -q`.

Each assertion is a code or a stored value the API returned, not "the call succeeded".

**What this file does not walk, by design of the slice** (`PL-1621` R5.3, owner FR-377's Work):
B4.4 (the Approver's question) and B4.5 (the Commentary Block resubmission) are *not started*.
**One step the workflow states is not built** and is recorded here rather than matched to:
B4.2 says a `violated` convexity check escalates to the two-approver rule. The platform has no
such escalation; `custom_objective`'s policy entry asks one approver by default. The file
therefore sets the workspace policy to two approvers, which is the workspace's own to set
(`06` §4.2), and the two decisions below are real ones.
"""

from __future__ import annotations

from uuid import UUID

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_custom_objectives import _principal_holding
from backend.tests.test_custom_objectives_expression import (
    _expression_body,
    _set_flag,
)
from backend.tests.test_model_lifecycle import _principal_with
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.session import Database
from model_schema import new_uuid7

OBJECTIVES = "/api/v1/custom-objectives"


async def _run_job(job_id: str) -> None:
    """Run a submitted Job to its end on the test's own loop, as the worker would."""
    from backend.tests.conftest_db import test_blob_bucket, test_database_url

    from app.platform.blobs import BlobStore
    from app.worker.model_handlers import register_model_handlers
    from app.worker.tasks import execute_job
    from model_schema import JobStatus

    register_model_handlers()
    database = Database(Settings(database_url=test_database_url()))
    try:
        store = BlobStore(Settings(blob_bucket=test_blob_bucket()))
        assert await execute_job(database, UUID(job_id), store) is JobStatus.SUCCEEDED
    finally:
        await database.dispose()


@pytest.mark.req("FR-163")
async def test_wf702_route_b_expression_objective_from_create_to_two_approvals(
    api_client: TestClient, database: Database, workspace_id: UUID
) -> None:
    await _set_flag(database, workspace_id, True)
    author = await _principal_holding(
        database,
        workspace_id,
        {"custom_objective:author", "model:fit", "model:read", "model:submit"},
    )
    first = _headers((await _principal_with(database, workspace_id, "approver")).id, workspace_id)
    second = _headers((await _principal_with(database, workspace_id, "approver")).id, workspace_id)

    # B1.4 / B1.5 — the editor's live parse: a bad attempt is a positioned `ok: false`, and
    # nothing is stored (the preview route, FR-8140).
    bad = api_client.post(
        f"{OBJECTIVES}/preview",
        json={"loss": "numpy.where(f < y, 1, 2)", "parameters": []},
        headers=author,
    )
    assert bad.status_code == 200, bad.text
    assert bad.json()["ok"] is False
    assert bad.json()["error"]["reason"] == "grammar"

    # B1.1-B1.3, B1.6 — create the loss only, with parameters and applicability.
    body = _expression_body(slug="asymmetric-burning-cost")
    created = api_client.post(OBJECTIVES, json=body, headers=author)
    assert created.status_code == 201, created.text
    objective = created.json()
    assert objective["status"] == "draft"
    assert objective["derived"] is None
    objective_id = objective["id"]

    # B2.1-B2.4 — derive: the platform writes the derivatives, with the tool and version.
    derived = api_client.post(f"{OBJECTIVES}/{objective_id}/derive", json={}, headers=author)
    assert derived.status_code == 200, derived.text
    block = derived.json()["derived"]
    assert block["derivation_tool"] == "sympy"
    assert block["gradient"]
    assert block["hessian"]
    assert block["derivation_version"]

    # B3 — certify: 202 and a Job; the worker runs it; the verdict is `certified_with_findings`
    # because convexity is `violated` (non-convex asymmetric loss), never `failed` (FR-152).
    certify = api_client.post(f"{OBJECTIVES}/{objective_id}/certify", json={}, headers=author)
    assert certify.status_code == 202, certify.text
    await _run_job(certify.json()["id"])
    certificate = api_client.get(f"{OBJECTIVES}/{objective_id}/certificate", headers=author)
    assert certificate.status_code == 200, certificate.text
    result = certificate.json()["result"]
    statuses = {check["name"]: check["status"] for check in result["checks"]}
    assert statuses["convexity"] == "violated"
    assert result["overall"] == "certified_with_findings"
    assert api_client.get(f"{OBJECTIVES}/{objective_id}", headers=author).json()["status"] == (
        "certified"
    )

    # B4.1 / B4.2 — submit with the certificate attached. The default policy asks one Approver
    # and the latest certificate's convexity is `violated`, so the request needs one more: two
    # (FR-152, FR-163).
    submitted = api_client.post(
        f"{OBJECTIVES}/{objective_id}/submit",
        json={"change_summary": "Asymmetric burning cost: under-pricing penalised twice."},
        headers=author,
    )
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["status"] == "review"
    request_id = submitted.json()["approval_request_id"]
    decide = f"/api/v1/approval-requests/{request_id}/decide"

    # B4.3 / B4.6 — two non-author Approvers; the first leaves it in review, the second approves.
    one = api_client.post(decide, json={"decision": "approve"}, headers=first)
    assert one.status_code == 200, one.text
    assert one.json()["status"] == "review"
    assert api_client.get(f"{OBJECTIVES}/{objective_id}", headers=author).json()["status"] == (
        "review"
    )
    two = api_client.post(decide, json={"decision": "approve"}, headers=second)
    assert two.status_code == 200, two.text
    assert two.json()["status"] == "approved"
    assert two.json()["approvers_recorded"] == 2
    final = api_client.get(f"{OBJECTIVES}/{objective_id}", headers=author).json()
    assert final["status"] == "approved"


@pytest.mark.req("FR-150")
async def test_wf702_route_b_with_the_flag_at_its_default_the_create_is_409(
    api_client: TestClient, database: Database
) -> None:
    """A second workspace that never set the flag: the same body is refused by name."""
    elsewhere = new_uuid7()
    author = await _principal_holding(
        database, elsewhere, {"custom_objective:author", "model:fit", "model:read"}
    )
    response = api_client.post(OBJECTIVES, json=_expression_body(), headers=author)
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "OBJECTIVE_KIND_NOT_ENABLED"
    preview = api_client.post(
        f"{OBJECTIVES}/preview", json={"loss": "w * (y - exp(f)) ** 2"}, headers=author
    )
    assert preview.status_code == 409, preview.text
    assert preview.json()["code"] == "OBJECTIVE_KIND_NOT_ENABLED"
