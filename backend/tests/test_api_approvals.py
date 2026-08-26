"""The approval API (`06` §5.1) — the state machine over HTTP."""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.db.models import (
    CustomMetricRow,
    CustomObjectiveRow,
    DatasetRow,
    DatasetVersionRow,
    DiagnosticsRow,
    ModelRow,
    PerilStructureRow,
    ValidationRuleRow,
)
from app.db.session import Database
from app.main import create_app
from model_schema import (
    TEMPLATE_APPLICABILITY,
    DatasetKind,
    DatasetStatus,
    MetricDirection,
    ModelStatus,
    ObjectiveTemplate,
    PerilStructureStatus,
    Severity,
    ValidationLayer,
    new_uuid7,
)

MODEL_SLUG = "motor-ad-frequency"
MODEL = f"model:{MODEL_SLUG}@7"

#: Every artifact type a module in this build can resolve a reference for (FR-GOV-36).
#: `rating_version` is deliberately absent — it has a policy entry and no module, and
#: `test_an_artifact_type_no_module_can_resolve_fails_closed` is what says so.
RESOLVABLE = (
    "model",
    "custom_objective",
    "custom_metric",
    "peril_structure",
    "validation_rule",
    "dataset_version",
)


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


def _headers(principal_id, workspace_id) -> dict[str, str]:
    """Headers for a caller granted in `workspace_id` (W6b-11).

    `Workspace-Id` names a membership — `grant` seeds one — so the selection is checked
    and accepted. The old `x-dev-workspace-id` pin, which bypassed the membership check,
    is gone.
    """
    return {
        DEV_PRINCIPAL_HEADER: str(principal_id),
        "Workspace-Id": str(workspace_id),
    }


@pytest_asyncio.fixture
async def submitter_headers(workspace_id, principal, grant) -> dict[str, str]:
    await grant("analyst")
    return _headers(principal.id, workspace_id)


@pytest_asyncio.fixture
async def approver_headers(workspace_id, grant) -> dict[str, str]:
    approver = new_uuid7()
    await grant("approver", principal_id=approver)
    return _headers(approver, workspace_id)


#: The shipped template's own declaration, not a hand-written one. `objectives.resolve_ref`
#: and `metrics.resolve_ref` both re-validate the row through the contract on the way out,
#: so a stub `{}` here is refused by `Applicability` before the route can answer at all.
_APPLICABILITY = TEMPLATE_APPLICABILITY[ObjectiveTemplate.POISSON].model_dump(mode="json")


async def _create_artifact(
    database: Database, workspace_id, artifact_type: str, slug: str, version: int
) -> None:
    """One row of `artifact_type` at `slug@version`, so a reference to it resolves.

    Written straight to the table rather than through each owning module's create path.
    That is the point of the fixture: FR-GOV-36 asks only whether the version **exists**,
    and every row here is left `draft` — status is the owning module's own submit path's
    question, and `POST /approval-requests` is reached without it.
    """
    async with database.unit_of_work() as session:
        if artifact_type == "model":
            session.add(
                ModelRow(
                    workspace_id=workspace_id,
                    model_family_slug=slug,
                    version=version,
                    status=ModelStatus.DRAFT.value,
                    dataset_version_id=new_uuid7(),
                    spec={},
                    spec_hash=f"v2:sha256:{new_uuid7().hex}",
                )
            )
        elif artifact_type == "custom_objective":
            session.add(
                CustomObjectiveRow(
                    workspace_id=workspace_id,
                    slug=slug,
                    version=version,
                    kind="template",
                    template=ObjectiveTemplate.POISSON.value,
                    params={},
                    applicability=_APPLICABILITY,
                )
            )
        elif artifact_type == "custom_metric":
            session.add(
                CustomMetricRow(
                    workspace_id=workspace_id,
                    slug=slug,
                    version=version,
                    kind="template",
                    template=ObjectiveTemplate.POISSON.value,
                    params={},
                    applicability=_APPLICABILITY,
                    direction=MetricDirection.LOWER_IS_BETTER.value,
                )
            )
        elif artifact_type == "peril_structure":
            session.add(
                PerilStructureRow(
                    workspace_id=workspace_id,
                    slug=slug,
                    version=version,
                    status=PerilStructureStatus.DRAFT.value,
                    perils=[],
                    excluded_perils=[],
                )
            )
        elif artifact_type == "validation_rule":
            session.add(
                ValidationRuleRow(
                    workspace_id=workspace_id,
                    slug=slug,
                    version=version,
                    layer=ValidationLayer.STRUCTURAL.value,
                    check="range",
                    severity=Severity.FAIL.value,
                    body={},
                    authored_by=new_uuid7(),
                )
            )
        elif artifact_type == "dataset_version":
            # The only one that takes two rows: the slug in the reference is the
            # **dataset's** and the version is the snapshot's, which is why
            # `datasets.resolve_artifact_ref` is the only one of the six that joins.
            dataset = DatasetRow(
                workspace_id=workspace_id, slug=slug, name=slug, owner_id=new_uuid7()
            )
            session.add(dataset)
            await session.flush()
            session.add(
                DatasetVersionRow(
                    workspace_id=workspace_id,
                    dataset_id=dataset.id,
                    version=version,
                    status=DatasetStatus.DRAFT.value,
                    kind=DatasetKind.INGESTED.value,
                )
            )
        else:  # pragma: no cover - a new member of RESOLVABLE with no factory
            raise AssertionError(f"no factory for {artifact_type!r}")


async def _allow_the_type(
    client: TestClient, workspace_id, grant, database, artifact_type: str
) -> None:
    """Give `artifact_type` a policy entry where `06` §4.2's defaults have none.

    Not a workaround. `submit` refuses an unpolicied type *before* it resolves anything, on
    purpose, so a workspace that has never said how a dataset version gets approved does not
    reach FR-GOV-36's check at all — and
    `test_the_missing_policy_is_answered_before_the_missing_artifact` is what pins that
    order. Reaching the check means saying so first.

    The policy reader is a member but holds no role (W6b-11): approval-policy needs only
    authentication, so without membership the read would be refused with `UNAUTHENTICATED`
    before the handler ran.
    """
    from app.db.models import WorkspaceMemberRow
    from app.platform import workspaces

    reader = new_uuid7()
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        session.add(WorkspaceMemberRow(user_id=reader, workspace_id=workspace_id))
    policy = client.get(
        "/api/v1/approval-policy", headers=_headers(reader, workspace_id)
    ).json()
    if any(entry["artifact_type"] == artifact_type for entry in policy["policies"]):
        return
    admin = new_uuid7()
    await grant("admin", principal_id=admin)
    policy["policies"].append(
        {
            "artifact_type": artifact_type,
            "approvers_required": 1,
            "approver_roles": ["approver"],
            "evidence": [],
        }
    )
    response = client.put(
        "/api/v1/approval-policy", json=policy, headers=_headers(admin, workspace_id)
    )
    assert response.status_code == 200, response.text


@pytest_asyncio.fixture(autouse=True)
async def the_model_every_test_here_pins(database: Database, workspace_id) -> None:
    """`MODEL` and the two versions beside it, as rows a decision can actually move.

    Autouse and unconditional since FR-GOV-36: submission now resolves the reference it is
    asked to pin, so `model:motor-ad-frequency@7` naming nothing would make every test in
    this module a `404`. The module was written against a route that accepted any
    well-formed string, which is the defect FR-GOV-36 records.

    `review`, not `draft`, and on a `validated` dataset version with diagnostics — because
    a resolved reference is one `_carry_to_the_artifact` then follows through. A `draft`
    model would refuse `draft → approved` (FR-MODEL-64) and a model on an unvalidated
    version would refuse as `ARTIFACT_FLAGGED` (FR-MODEL-67), and the approval tests would
    then be measuring the model lifecycle rather than the approval one. That the two are now
    joined at all is the change: before FR-GOV-36 these requests pinned nothing, so the
    decision moved nothing and no state on the other side had to be coherent.
    """
    async with database.unit_of_work() as session:
        dataset = DatasetRow(
            workspace_id=workspace_id, slug=MODEL_SLUG, name=MODEL_SLUG, owner_id=new_uuid7()
        )
        session.add(dataset)
        await session.flush()
        version = DatasetVersionRow(
            workspace_id=workspace_id,
            dataset_id=dataset.id,
            version=1,
            status=DatasetStatus.VALIDATED.value,
            kind=DatasetKind.INGESTED.value,
            validation_report_id=new_uuid7(),
        )
        session.add(version)
        await session.flush()
        for number in (7, 8, 9):
            model = ModelRow(
                workspace_id=workspace_id,
                model_family_slug=MODEL_SLUG,
                version=number,
                status=ModelStatus.DRAFT.value,
                dataset_version_id=version.id,
                spec={},
                spec_hash=f"v2:sha256:{new_uuid7().hex}",
            )
            session.add(model)
            await session.flush()
            diagnostics = DiagnosticsRow(
                workspace_id=workspace_id, model_id=model.id, payload={}
            )
            session.add(diagnostics)
            await session.flush()
            # `record_fit`'s order: the numbers, the pointer and the status in one UPDATE,
            # which is the only shape `models_fit_immutable` admits.
            model.fit_result = {}
            model.diagnostics_id = diagnostics.id
            model.status = ModelStatus.REVIEW.value
            await session.flush()


@pytest.mark.req("FR-GOV-9")
def test_submitting_returns_a_request_in_review(
    client: TestClient, submitter_headers
) -> None:
    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit on 2026H1."},
        headers=submitter_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "review"
    assert body["artifact_ref"] == MODEL
    assert body["approvers_required"] == 1


@pytest.mark.req("FR-GOV-11")
async def test_the_submitter_cannot_approve_even_holding_the_approver_role(
    client: TestClient, workspace_id, principal, grant, submitter_headers
) -> None:
    """R1 end to end, and the grant is what makes it a test of R1.

    Without also granting the submitter `approver`, the route's permission dependency
    refuses first and the response says PERMISSION_DENIED — which would pass while proving
    nothing about separation of duties.
    """
    await grant("approver")

    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()

    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/decide",
        json={"decision": "approve"},
        headers=submitter_headers,
    )
    assert response.status_code == 403
    assert response.json()["code"] == "SUBMITTER_CANNOT_APPROVE"


@pytest.mark.req("FR-GOV-9")
def test_an_approver_approves(
    client: TestClient, submitter_headers, approver_headers
) -> None:
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()

    body = client.post(
        f"/api/v1/approval-requests/{created['id']}/decide",
        json={"decision": "approve", "comment": "Diagnostics clean."},
        headers=approver_headers,
    ).json()
    assert body["status"] == "approved"
    assert body["approvers_recorded"] == 1
    assert body["decisions"][0]["comment"] == "Diagnostics clean."


@pytest.mark.req("FR-GOV-2")
async def test_deciding_requires_the_permission(
    client: TestClient, submitter_headers, workspace_id, membership
) -> None:
    """Negative: an analyst may submit but not decide.

    The decider holds a membership but no role (W6b-11), so the refusal must come from
    the role check — asserted by code, not just by status.
    """
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()
    other = new_uuid7()
    await membership(principal_id=other)
    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/decide",
        json={"decision": "approve"},
        headers={
            DEV_PRINCIPAL_HEADER: str(other),
            "Workspace-Id": str(workspace_id),
        },
    )
    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-GOV-15")
def test_withdrawing_after_deployment_is_refused(
    client: TestClient, submitter_headers, approver_headers
) -> None:
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()
    client.post(
        f"/api/v1/approval-requests/{created['id']}/decide",
        json={"decision": "approve"},
        headers=approver_headers,
    )
    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/withdraw",
        json={"reason": "changed my mind", "artifact_is_live": True},
        headers=approver_headers,
    )
    assert response.status_code == 409
    assert response.json()["code"] == "WITHDRAW_AFTER_DEPLOY_FORBIDDEN"


@pytest.mark.req("FR-GOV-9")
def test_a_malformed_artifact_reference_is_refused(
    client: TestClient, submitter_headers
) -> None:
    """ID-3: the reference is the pin. A malformed one pins nothing."""
    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": "model:motor-ad-frequency", "change_summary": "x"},
        headers=submitter_headers,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-GOV-9")
def test_requests_are_listable_and_filterable(
    client: TestClient, submitter_headers, approver_headers
) -> None:
    """Listing and filtering, which the inbox will need.

    Deliberately **not** marked FR-GOV-16: that requirement is about evidence rendered
    inline — diffs, diagnostics, dislocation, GIPP — and none of those artifacts exist
    before W4 and W5. A marker here would claim the requirement in the traceability record
    while the closure record says it is deferred, and the two must not disagree.
    """
    for i in (7, 8, 9):
        client.post(
            "/api/v1/approval-requests",
            json={"artifact_ref": f"model:motor-ad-frequency@{i}", "change_summary": "x"},
            headers=submitter_headers,
        )
    body = client.get("/api/v1/approval-requests?status=review", headers=approver_headers).json()
    assert body["total_estimate"] == 3
    assert all(i["status"] == "review" for i in body["items"])


@pytest.mark.req("FR-GOV-12")
def test_the_default_policy_is_the_documented_one(
    client: TestClient, submitter_headers
) -> None:
    """`06` §4.2: a rating version needs two approvers, a model one."""
    body = client.get("/api/v1/approval-policy", headers=submitter_headers).json()
    required = {p["artifact_type"]: p["approvers_required"] for p in body["policies"]}
    assert required["rating_version"] == 2
    assert required["model"] == 1
    assert body["submitter_may_approve"] is False


@pytest.mark.req("FR-GOV-12")
async def test_replacing_the_policy_requires_admin(
    client: TestClient, workspace_id, grant, submitter_headers
) -> None:
    policy = client.get("/api/v1/approval-policy", headers=submitter_headers).json()
    denied = client.put("/api/v1/approval-policy", json=policy, headers=submitter_headers)
    assert denied.status_code == 403

    admin = new_uuid7()
    await grant("admin", principal_id=admin)
    allowed = client.put(
        "/api/v1/approval-policy",
        json=policy,
        headers=_headers(admin, workspace_id),
    )
    assert allowed.status_code == 200


@pytest.mark.req("FR-GOV-11")
async def test_a_policy_that_disables_separation_of_duties_is_refused(
    client: TestClient, workspace_id, grant
) -> None:
    """Negative: `06` R1 cannot be configured away, so the API must refuse to store it."""
    admin = new_uuid7()
    await grant("admin", principal_id=admin)
    response = client.put(
        "/api/v1/approval-policy",
        json={"policies": [], "submitter_may_approve": True},
        headers=_headers(admin, workspace_id),
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-OVR-13")
async def test_another_workspaces_request_is_404(
    client: TestClient, submitter_headers, principal, database
) -> None:
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()
    # The detail route needs only authentication, so the caller reaches the handler and
    # the 404 is about the workspace scope rather than about being refused a permission.
    # The submitter must *be* a member of the other workspace (W6b-11): the `Workspace-Id`
    # header is checked against the memberships the database holds, never trusted.
    from app.db.models import WorkspaceMemberRow
    from app.platform import workspaces

    other = new_uuid7()
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=other)
        session.add(WorkspaceMemberRow(user_id=principal.id, workspace_id=other))
    response = client.get(
        f"/api/v1/approval-requests/{created['id']}",
        headers=_headers(principal.id, other),
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


# -- resolution at submission (FR-GOV-36) --------------------------------------------------


@pytest.mark.req("FR-GOV-36")
def test_a_reference_to_a_version_that_was_never_created_is_refused(
    client: TestClient, submitter_headers
) -> None:
    """The defect FR-GOV-36 records, as a test.

    `motor-ad-frequency` exists at 7, 8 and 9; `@99` does not. Before this the request was
    created anyway, and it could then be *approved* — the owning module cannot move an
    artifact that does not exist, so the decision moved nothing and there was nothing for a
    reader to reconcile it against. FR-GOV-14 makes an approval pinned to an exact version;
    a pin to a version that was never created is a pin to nothing.
    """
    response = client.post(
        "/api/v1/approval-requests",
        json={
            "artifact_ref": f"model:{MODEL_SLUG}@99",
            "change_summary": "Refit on 2026H1.",
        },
        headers=submitter_headers,
    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-GOV-36")
@pytest.mark.parametrize("artifact_type", RESOLVABLE)
async def test_every_resolvable_type_refuses_a_version_that_does_not_exist(
    client: TestClient, workspace_id, grant, database, submitter_headers, artifact_type: str
) -> None:
    """Negative, once per artifact type a module in this build can look up.

    Parametrized rather than written six times because the requirement is about the *route*
    and not about any one module: a type that reaches `_resolve_the_artifact` and is not
    refused is a type whose entry in the fan-out is missing or wrong, and the failure names
    which one.
    """
    await _allow_the_type(client, workspace_id, grant, database, artifact_type)
    slug = f"{artifact_type.replace('_', '-')}-never-created"
    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": f"{artifact_type}:{slug}@3", "change_summary": "x"},
        headers=submitter_headers,
    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-GOV-36")
@pytest.mark.parametrize("artifact_type", RESOLVABLE)
async def test_every_resolvable_type_still_accepts_the_version_that_exists(
    client: TestClient,
    database: Database,
    workspace_id,
    grant,
    submitter_headers,
    artifact_type: str,
) -> None:
    """The positive control the negative test needs to mean anything.

    A resolver that refused everything would pass the six tests above and break the
    platform. This is the same six references, with the row present.
    """
    await _allow_the_type(client, workspace_id, grant, database, artifact_type)
    slug = f"{artifact_type.replace('_', '-')}-exists"
    await _create_artifact(database, workspace_id, artifact_type, slug, 3)
    ref = f"{artifact_type}:{slug}@3"
    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": ref, "change_summary": "x"},
        headers=submitter_headers,
    )
    assert response.status_code == 201, response.text
    assert response.json()["artifact_ref"] == ref
    assert response.json()["status"] == "review"


@pytest.mark.req("FR-GOV-36")
def test_an_artifact_type_no_module_can_resolve_fails_closed(
    client: TestClient, submitter_headers
) -> None:
    """Negative: `rating_version` has a policy entry (`06` §4.2) and no module — `03` is
    unbuilt — so nothing here can say whether the version exists.

    **Decided, not accidental.** `07`'s `JOB_HANDLER_NOT_REGISTERED` settles what a platform
    deployable before every kind has an implementation owes the caller: say the capability
    is absent, rather than accept the work and leave nothing to explain the silence.
    Accepting the submission would recreate FR-GOV-36's own defect one level up — a request
    that can be decided and moves nothing.

    **The code is `ARTIFACT_TYPE_NOT_RESOLVABLE`**, registered in `GOVERNANCE_ERROR_CODES`
    and declared in `06` §5.1's ownership block on 2026-08-22. It shipped for an hour on
    `VALIDATION_FAILED`, which was wrong in a way worth recording: that code tells the
    caller their input was bad when it was not — the reference is well formed, its type is
    in `ARTIFACT_TYPES`, and the policy admits it. What is absent is a module in this
    build, which is a fact about the deployment and not about the request.
    """
    response = client.post(
        "/api/v1/approval-requests",
        json={
            "artifact_ref": "rating_version:motor-gb-comprehensive@1",
            "change_summary": "First deployable bundle.",
        },
        headers=submitter_headers,
    )
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["title"] == "No module in this deployment can resolve this artifact type"
    assert body["code"] == "ARTIFACT_TYPE_NOT_RESOLVABLE"


@pytest.mark.req("FR-GOV-36")
def test_the_missing_policy_is_answered_before_the_missing_artifact(
    client: TestClient, submitter_headers
) -> None:
    """Order, not just outcome. `dataset_version` earns two correct refusals in a workspace
    on the default policy — no policy entry, and no such version — and the one the submitter
    can act on is the policy.

    Resolution therefore sits *after* the policy check in `approvals.submit`, not before it
    and not in the route ahead of the call. Answering "no such version" first would send the
    submitter off to create a version that still could not be approved.
    """
    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": "dataset_version:never-created@1", "change_summary": "x"},
        headers=submitter_headers,
    )
    assert response.status_code == 422, response.text
    assert response.json()["title"] == "No approval policy for this artifact type"
