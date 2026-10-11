"""The approval API (`06` §5.1) — the state machine over HTTP."""

from __future__ import annotations

import pytest
import pytest_asyncio
from backend.tests.dry_run_reports import stored_dry_run_report
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
    RatingVersionRow,
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
    Severity,
    ValidationLayer,
    new_uuid7,
)

MODEL_SLUG = "motor-ad-frequency"
MODEL = f"model:{MODEL_SLUG}@7"

#: Who created the fixture model: nobody who submits or decides in these tests.
MODEL_AUTHOR = new_uuid7()

#: Every artifact type a module in this build can resolve a reference for (FR-386).
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
    from backend.tests.conftest_db import test_blob_bucket, test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        # Shadows conftest's `api_settings`, so it inherits no bucket — without this the
        # app it builds runs on the production default while every fixture store uses the
        # test bucket. **Set defensively, not because this file reads a blob today**: the
        # line must not read as conditional on that, because the day someone adds a blob
        # path here the 404 they get would have its cause two files away.
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


#: Every approvable type: `RESOLVABLE` plus `rating_version`, whose resolver
#: (`api/approvals.py::_resolve_rating_version`) arrived after that tuple was written.
APPROVABLE = (*RESOLVABLE, "rating_version")

#: The action each type's creation path records, restated here from the create paths
#: themselves (`modelling.reserve`'s `model.reserved`, and `<type>.created` for the rest)
#: rather than imported from the check, so a wrong entry in the check's table fails a test.
CREATION_ACTION = {
    "model": "model.reserved",
    "custom_objective": "custom_objective.created",
    "custom_metric": "custom_metric.created",
    "peril_structure": "peril_structure.created",
    "validation_rule": "validation_rule.created",
    "dataset_version": "dataset_version.created",
    "rating_version": "rating_version.created",
    # Added 2026-10-04 (WK-674 Slice 2, `RL-1401`): the eighth type. A Deployment Request is
    # created only by `platform.deployments`, so the generic parametrised tests over
    # `APPROVABLE` do not reach it; `tests/test_deployments.py` does.
    "deployment": "deployment_request.created",
}


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


async def _record_creation(session, workspace_id, artifact_type: str, ref: str, author) -> None:
    """Record `ref`'s creation Audit Event, as the owning module's create path does."""
    from app.platform import audit
    from model_schema import ActorKind, JobSource, Principal

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=Principal(kind=ActorKind.USER, id=author, display="author@insurer.example"),
        source=JobSource.API,
        action=CREATION_ACTION[artifact_type],
        entity_ref=ref,
    )


async def _create_artifact(
    database: Database,
    workspace_id,
    artifact_type: str,
    slug: str,
    version: int,
    status: str = "review",
) -> None:
    """One row of `artifact_type` at `slug@version`, so a reference to it resolves.

    Written straight to the table rather than through each owning module's create path.
    FR-386 asks whether the version exists; `06` FR-351, enforced on the generic route since
    2026-09-28 (the approval status bypass), asks that it be **in review**. So a row is
    written in its type's review state by default, with whatever a CHECK requires of a
    status past `draft`; `status="draft"` is the negative case. `dataset_version` has no
    review state: its reviewable state is `validated` (FR-351's 2026-09-28 clause), which
    the default `status="review"` stands for here.
    """
    async with database.unit_of_work() as session:
        if artifact_type == "model":
            session.add(
                model := ModelRow(
                    workspace_id=workspace_id,
                    model_family_slug=slug,
                    version=version,
                    status=ModelStatus.DRAFT.value,
                    dataset_version_id=new_uuid7(),
                    spec={},
                    spec_hash=f"v2:sha256:{new_uuid7().hex}",
                )
            )
            if status != "draft":
                # `record_fit`'s order, the only shape `models_fit_immutable` admits.
                await session.flush()
                diagnostics = DiagnosticsRow(
                    workspace_id=workspace_id, model_id=model.id, payload={}
                )
                session.add(diagnostics)
                await session.flush()
                model.fit_result = {}
                model.diagnostics_id = diagnostics.id
                model.status = status
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
                    status=status,
                    certificate_id=None if status == "draft" else new_uuid7(),
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
                    status=status,
                    certificate_id=None if status == "draft" else new_uuid7(),
                )
            )
        elif artifact_type == "peril_structure":
            session.add(
                PerilStructureRow(
                    workspace_id=workspace_id,
                    slug=slug,
                    version=version,
                    status=status,
                    perils=[],
                    excluded_perils=[],
                    reconciliation=None if status == "draft" else {"status": "pass"},
                )
            )
        elif artifact_type == "validation_rule":
            rule = ValidationRuleRow(
                workspace_id=workspace_id,
                slug=slug,
                version=version,
                layer=ValidationLayer.STRUCTURAL.value,
                check="range",
                severity=Severity.FAIL.value,
                body={},
                authored_by=new_uuid7(),
                status=status,
            )
            session.add(rule)
            if status != "draft":
                # A rule past `draft` has a dry run that executed (PL-1408, DP-3): the
                # approval reads the stored report, so a bare id is "cannot be read".
                await stored_dry_run_report(session, workspace_id=workspace_id, rule=rule)
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
                    status="validated" if status == "review" else status,
                    validation_report_id=new_uuid7() if status == "review" else None,
                    kind=DatasetKind.INGESTED.value,
                    # OQ-568 (c): a version names its own provenance (the row's
                    # envelope columns are non-null since 2057e7372a9a).
                    slug=slug,
                    created_by=new_uuid7(),
                    currency="GBP",
                )
            )
        elif artifact_type == "rating_version":
            session.add(
                RatingVersionRow(
                    workspace_id=workspace_id,
                    slug=slug,
                    version=version,
                    status=status,
                    dataset_version_id=new_uuid7(),
                    model_ref=MODEL,
                    created_by=new_uuid7(),
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
    reach FR-386's check at all — and
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

    Autouse and unconditional since FR-386: submission now resolves the reference it is
    asked to pin, so `model:motor-ad-frequency@7` naming nothing would make every test in
    this module a `404`. The module was written against a route that accepted any
    well-formed string, which is the defect FR-386 records.

    `review`, not `draft`, and on a `validated` dataset version with diagnostics — because
    a resolved reference is one `_carry_to_the_artifact` then follows through. A `draft`
    model would refuse `draft → approved` (FR-202) and a model on an unvalidated
    version would refuse as `ARTIFACT_FLAGGED` (FR-205), and the approval tests would
    then be measuring the model lifecycle rather than the approval one. That the two are now
    joined at all is the change: before FR-386 these requests pinned nothing, so the
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
            # OQ-568 (c): the envelope columns are non-null since 2057e7372a9a.
            slug=MODEL_SLUG,
            created_by=new_uuid7(),
            currency="GBP",
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
            # The creation event `modelling.reserve` records: its actor is the version's
            # author (`06` FR-353 as amended 2026-09-28), and without it every decision on
            # this model fails closed as APPROVAL_AUTHOR_UNRESOLVED.
            await _record_creation(
                session, workspace_id, "model", f"model:{MODEL_SLUG}@{number}", MODEL_AUTHOR
            )


@pytest.mark.req("FR-351")
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


@pytest.mark.req("FR-353")
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


@pytest.mark.req("FR-351")
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


@pytest.mark.req("FR-351")
def test_a_decision_without_the_decision_flag_is_refused_by_the_database(
    client: TestClient, submitter_headers, approver_headers, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Broken input** for the positive control above: with `approval_decision()` made a
    no-op, the same approval reaches the database without the flag and `approval_guard()`
    refuses it, named, rather than the request becoming `approved`."""
    from contextlib import asynccontextmanager

    from app.platform import approvals as approvals_service

    @asynccontextmanager
    async def no_flag(session):  # type: ignore[no-untyped-def]
        yield

    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": MODEL, "change_summary": "Refit."},
        headers=submitter_headers,
    ).json()
    monkeypatch.setattr(approvals_service, "approval_decision", no_flag)

    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/decide",
        json={"decision": "approve"},
        headers=approver_headers,
    )
    assert response.status_code == 500
    assert response.json()["code"] == "APPROVAL_OUTSIDE_DECISION_PATH"
    monkeypatch.undo()
    url = f"/api/v1/approval-requests/{created['id']}"
    still = client.get(url, headers=approver_headers).json()
    assert still["status"] == "review"


@pytest.mark.req("FR-343")
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


async def _a_deployed_rating_version_request(
    client: TestClient, database: Database, workspace_id, submitter_headers
) -> dict:
    """A request for a Rating Version that has a Deployment, planted as a real row."""
    from backend.tests.test_score import plant_deployment

    await _create_artifact(database, workspace_id, "rating_version", "rv-deployed", 1)
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": "rating_version:rv-deployed@1", "change_summary": "Ship."},
        headers=submitter_headers,
    )
    assert created.status_code == 201, created.text
    await plant_deployment(database, workspace_id, "dev", "rating_version:rv-deployed@1")
    return created.json()


@pytest.mark.req("FR-357")
async def test_withdrawing_after_deployment_is_refused(
    client: TestClient, database: Database, workspace_id, submitter_headers, approver_headers
) -> None:
    """The server derives liveness from the Deployment rows (RL-880; `PL-1392` Task 6): the body
    says nothing about it, and a Rating Version with a Deployment is refused."""
    created = await _a_deployed_rating_version_request(
        client, database, workspace_id, submitter_headers
    )
    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/withdraw",
        json={"reason": "changed my mind"},
        headers=approver_headers,
    )
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "WITHDRAW_AFTER_DEPLOY_FORBIDDEN"
    still = client.get(f"/api/v1/approval-requests/{created['id']}", headers=approver_headers)
    assert still.json()["status"] == "review"


@pytest.mark.req("FR-357")
async def test_a_client_can_no_longer_assert_that_the_artifact_is_not_live(
    client: TestClient, database: Database, workspace_id, submitter_headers, approver_headers
) -> None:
    """The field is gone and the body keeps `extra="forbid"` (`PL-1392` C11): a client still
    sending `artifact_is_live: false` is refused 422 naming the field, and nothing withdraws."""
    created = await _a_deployed_rating_version_request(
        client, database, workspace_id, submitter_headers
    )
    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/withdraw",
        json={"reason": "changed my mind", "artifact_is_live": False},
        headers=approver_headers,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"
    assert "artifact_is_live" in response.text
    still = client.get(f"/api/v1/approval-requests/{created['id']}", headers=approver_headers)
    assert still.json()["status"] == "review"


@pytest.mark.req("FR-357")
async def test_a_rating_version_with_no_deployment_can_still_be_withdrawn(
    client: TestClient, database: Database, workspace_id, submitter_headers, approver_headers
) -> None:
    """Positive control: the same request with no Deployment withdraws, so the refusal above is
    the Deployment's and not a route that refuses every withdrawal of a Rating Version."""
    await _create_artifact(database, workspace_id, "rating_version", "rv-undeployed", 1)
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": "rating_version:rv-undeployed@1", "change_summary": "Ship."},
        headers=submitter_headers,
    ).json()
    response = client.post(
        f"/api/v1/approval-requests/{created['id']}/withdraw",
        json={"reason": "changed my mind"},
        headers=approver_headers,
    )
    assert response.status_code == 200, response.text


@pytest.mark.req("FR-351")
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


@pytest.mark.req("FR-351")
def test_requests_are_listable_and_filterable(
    client: TestClient, submitter_headers, approver_headers
) -> None:
    """Listing and filtering, which the inbox will need.

    Deliberately **not** marked FR-358: that requirement is about evidence rendered
    inline — diffs, diagnostics, dislocation, GIPP — and none of those artifacts exist
    before WK-660 and WK-661. A marker here would claim the requirement in the traceability record
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


@pytest.mark.req("FR-354")
def test_the_default_policy_is_the_documented_one(
    client: TestClient, submitter_headers
) -> None:
    """`06` §4.2: a rating version needs two approvers, a model one."""
    body = client.get("/api/v1/approval-policy", headers=submitter_headers).json()
    required = {p["artifact_type"]: p["approvers_required"] for p in body["policies"]}
    assert required["rating_version"] == 2
    assert required["model"] == 1
    assert body["submitter_may_approve"] is False


@pytest.mark.req("FR-354")
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


@pytest.mark.req("FR-353")
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


@pytest.mark.req("FR-16")
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


# -- resolution at submission (FR-386) --------------------------------------------------


@pytest.mark.req("FR-386")
def test_a_reference_to_a_version_that_was_never_created_is_refused(
    client: TestClient, submitter_headers
) -> None:
    """The defect FR-386 records, as a test.

    `motor-ad-frequency` exists at 7, 8 and 9; `@99` does not. Before this the request was
    created anyway, and it could then be *approved* — the owning module cannot move an
    artifact that does not exist, so the decision moved nothing and there was nothing for a
    reader to reconcile it against. FR-356 makes an approval pinned to an exact version;
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


@pytest.mark.req("FR-386")
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


@pytest.mark.req("FR-386")
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


@pytest.mark.req("FR-386")
def test_an_artifact_type_no_module_can_resolve_fails_closed(
    client: TestClient, submitter_headers
) -> None:
    """Negative: `rating_version` has a policy entry (`06` §4.2) and no module — `03` is
    unbuilt — so nothing here can say whether the version exists.

    **Decided, not accidental.** `07`'s `JOB_HANDLER_NOT_REGISTERED` settles what a platform
    deployable before every kind has an implementation owes the caller: say the capability
    is absent, rather than accept the work and leave nothing to explain the silence.
    Accepting the submission would recreate FR-386's own defect one level up — a request
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


@pytest.mark.req("FR-260")
def test_a_regression_suite_reference_cannot_be_put_through_approval(
    client: TestClient, submitter_headers
) -> None:
    """Negative (WK-672 Slice 2, PL-1189; the lead's ruling on the `regression_suite`
    artifact type). `regression_suite` joined `ARTIFACT_TYPES` so a Rating Version's
    evidence can pin a suite version by reference (`03` §4.3). It is a reference only: the
    suite is not approvable (DP-S2-1 (A)), so a request naming one is refused and nothing
    is created.

    The refusal is the earliest one the route has: no workspace approval policy names the
    type, so it never reaches artifact resolution (and so never
    `ARTIFACT_TYPE_NOT_RESOLVABLE`, which is the refusal for a type that *has* a policy
    entry and no module). And the type has no creation action, so #861's author check
    could not resolve an Author for it either.
    """
    from app.platform import approvals

    assert "regression_suite" not in approvals.CREATION_ACTIONS
    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": "regression_suite:motor-gb-core@1", "change_summary": "x"},
        headers=submitter_headers,
    )
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["code"] == "VALIDATION_FAILED"
    assert body["title"] == "No approval policy for this artifact type"


@pytest.mark.req("FR-386")
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


# -- the author may not approve (FR-353 as amended 2026-09-28) -------------------------

async def _create_authored(
    database: Database, workspace_id, artifact_type: str, slug: str, version: int, author
) -> str:
    """`_create_artifact`, plus the creation Audit Event a real create path records.

    The event is what names the author (`06` FR-353 as amended): its actor is the person
    the approval check compares against.
    """
    await _create_artifact(database, workspace_id, artifact_type, slug, version)
    ref = f"{artifact_type}:{slug}@{version}"
    async with database.unit_of_work() as session:
        await _record_creation(session, workspace_id, artifact_type, ref, author)
    return ref


@pytest.mark.req("FR-353")
@pytest.mark.parametrize("decision", ["approve", "reject", "request_changes"])
@pytest.mark.parametrize("artifact_type", APPROVABLE)
async def test_the_author_cannot_decide_on_a_version_someone_else_submitted(
    client: TestClient, database: Database, workspace_id, grant, submitter_headers,
    artifact_type: str, decision: str,
) -> None:
    """FR-353 as amended: neither the submitter nor the author may decide on a version.

    The author holds the approver role and is not the submitter, so neither the route's
    permission check nor R1's submitter check can be what refuses — only the author check
    can. Every approvable type, and every decision: a rejection is a decision too.
    """
    await _allow_the_type(client, workspace_id, grant, database, artifact_type)
    author = new_uuid7()
    await grant("approver", principal_id=author)
    slug = f"{artifact_type.replace('_', '-')}-authored"
    ref = await _create_authored(database, workspace_id, artifact_type, slug, 1, author)

    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": ref, "change_summary": "Authored elsewhere."},
        headers=submitter_headers,
    )
    assert created.status_code == 201, created.text

    response = client.post(
        f"/api/v1/approval-requests/{created.json()['id']}/decide",
        json={"decision": decision, "comment": "Reviewed."},
        headers=_headers(author, workspace_id),
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "AUTHOR_CANNOT_APPROVE"


@pytest.mark.req("FR-353")
@pytest.mark.parametrize("artifact_type", APPROVABLE)
async def test_a_version_with_no_creation_event_cannot_be_approved(
    client: TestClient, database: Database, workspace_id, grant, submitter_headers,
    approver_headers, artifact_type: str,
) -> None:
    """Fail closed: with no creation Audit Event there is no author to compare against, and
    an approval that cannot be checked is refused rather than allowed."""
    await _allow_the_type(client, workspace_id, grant, database, artifact_type)
    slug = f"{artifact_type.replace('_', '-')}-unevented"
    await _create_artifact(database, workspace_id, artifact_type, slug, 1)

    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": f"{artifact_type}:{slug}@1", "change_summary": "x"},
        headers=submitter_headers,
    )
    assert created.status_code == 201, created.text

    response = client.post(
        f"/api/v1/approval-requests/{created.json()['id']}/decide",
        json={"decision": "approve"},
        headers=approver_headers,
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "APPROVAL_AUTHOR_UNRESOLVED"


@pytest.mark.req("FR-353")
def test_the_check_knows_the_creation_action_of_every_approvable_type() -> None:
    """The check's table and the create paths' actions are one mapping, over all eight
    (`deployment` is `APPROVABLE`'s eighth in the policy, not its generic-route tests')."""
    from app.platform import approvals

    assert dict(approvals.CREATION_ACTIONS) == CREATION_ACTION
    assert set(CREATION_ACTION) == set(APPROVABLE) | {"deployment"}


# -- only a version in review can be put to a decision (`06` FR-351) --------------------

#: Each approvable type's reviewable state (`06` FR-351, clause of 2026-09-28): `review`,
#: except `dataset_version`, whose lifecycle has none and is reviewable once `validated`.
REVIEWABLE_STATE = {t: "validated" if t == "dataset_version" else "review" for t in APPROVABLE}


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("artifact_type", APPROVABLE)
async def test_a_version_not_in_review_cannot_be_put_to_a_decision(
    client: TestClient, database: Database, workspace_id, grant, submitter_headers,
    artifact_type: str,
) -> None:
    """Negative: the generic route refuses a **draft** version, naming its state.

    Without this, a version that never passed its module's own submission — and so none of
    the gates that submission enforces — could be approved through `POST /approval-requests`.
    """
    await _allow_the_type(client, workspace_id, grant, database, artifact_type)
    slug = f"{artifact_type.replace('_', '-')}-draft"
    await _create_artifact(database, workspace_id, artifact_type, slug, 1, status="draft")

    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": f"{artifact_type}:{slug}@1", "change_summary": "x"},
        headers=submitter_headers,
    )
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "APPROVAL_SUBJECT_NOT_IN_REVIEW"
    assert "'draft'" in response.json()["detail"]


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    ("status", "accepted"), [("draft", False), ("failed", False), ("validated", True)]
)
async def test_a_dataset_version_is_reviewable_only_once_validated(
    client: TestClient, database: Database, workspace_id, grant, submitter_headers,
    status: str, accepted: bool,
) -> None:
    """`dataset_version` has no `review` state; its reviewable state is `validated`.

    Approving one records a governance sign-off and moves nothing: there is no decision hook
    for a dataset version, so its row keeps its status whatever is decided.
    """
    await _allow_the_type(client, workspace_id, grant, database, "dataset_version")
    slug = f"ds-{status}"
    await _create_artifact(
        database, workspace_id, "dataset_version", slug, 1,
        status="review" if status == "validated" else status,
    )
    response = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": f"dataset_version:{slug}@1", "change_summary": "x"},
        headers=submitter_headers,
    )
    if accepted:
        assert response.status_code == 201, response.text
    else:
        assert response.status_code == 409, response.text
        assert response.json()["code"] == "APPROVAL_SUBJECT_NOT_IN_REVIEW"
        assert f"'{status}'" in response.json()["detail"]


# -- what a decision does to the version, per type (`06` FR-351, FR-355) ------------------

#: The version's status after each outcome, from its reviewable state. A type with no
#: decision hook does not move at all: that is asserted, not a transition invented for it.
_OUTCOMES = ("approve", "first_of_two", "reject", "request_changes")


def _moves(approved: str, open_: str, returned: str) -> dict[str, str]:
    return dict(zip(_OUTCOMES, (approved, open_, returned, returned), strict=True))


_AFTER = {
    "model": _moves("approved", "review", "fitted"),
    "custom_objective": _moves("approved", "review", "certified"),
    "custom_metric": _moves("approved", "review", "certified"),
    "rating_version": _moves("approved", "review", "draft"),
    # FR-191, FR-355 (FD-1456): a structure's non-approval returns it to `reconciled` (never
    # `draft`: the reconciliation stays on the row, `VALID_PERIL_STRUCTURE_TRANSITIONS`).
    "peril_structure": _moves("approved", "review", "reconciled"),
    # FR-355: the pre-submission state of a rule is `draft` (`01` §4.5 step 1).
    "validation_rule": _moves("approved", "review", "draft"),
    "dataset_version": dict.fromkeys(_OUTCOMES, "validated"),
}

#: The action each hooked type's decision records on the version.
_MOVE_ACTION = {
    "model": lambda to: f"model.{to}",
    "custom_objective": lambda to: f"custom_objective.{to}",
    "custom_metric": lambda to: f"custom_metric.{to}",
    "rating_version": lambda to: (
        "rating_version.approved" if to == "approved" else "rating_version.returned_to_draft"
    ),
    "validation_rule": lambda to: f"validation_rule.{to}",
    "peril_structure": lambda to: f"peril_structure.{to}",
}


async def _require_two_approvals(
    client: TestClient, workspace_id, grant, database, artifact_type: str
) -> None:
    """Make `artifact_type` need two approvers, so a first approval is distinguishable."""
    await _allow_the_type(client, workspace_id, grant, database, artifact_type)
    admin = new_uuid7()
    await grant("admin", principal_id=admin)
    policy = client.get("/api/v1/approval-policy", headers=_headers(admin, workspace_id)).json()
    for entry in policy["policies"]:
        if entry["artifact_type"] == artifact_type:
            entry["approvers_required"] = 2
    response = client.put(
        "/api/v1/approval-policy", json=policy, headers=_headers(admin, workspace_id)
    )
    assert response.status_code == 200, response.text


async def _version_status(
    database: Database, workspace_id, artifact_type: str, slug: str, version: int
) -> str:
    from sqlalchemy import select

    table = {
        "model": (ModelRow, ModelRow.model_family_slug),
        "custom_objective": (CustomObjectiveRow, CustomObjectiveRow.slug),
        "custom_metric": (CustomMetricRow, CustomMetricRow.slug),
        "peril_structure": (PerilStructureRow, PerilStructureRow.slug),
        "validation_rule": (ValidationRuleRow, ValidationRuleRow.slug),
        "rating_version": (RatingVersionRow, RatingVersionRow.slug),
        "dataset_version": (DatasetVersionRow, DatasetVersionRow.slug),
    }[artifact_type]
    row, slug_column = table
    async with database.session() as session:
        return (
            await session.execute(
                select(row.status).where(
                    row.workspace_id == workspace_id, slug_column == slug, row.version == version
                )
            )
        ).scalar_one()


async def _decision_moves(database: Database, workspace_id, artifact_type: str, ref: str) -> list:
    """Every event on the version from its own module except its creation and submission."""
    from sqlalchemy import select

    from app.db.models import AuditEventRow

    async with database.session() as session:
        rows = (
            await session.execute(
                select(AuditEventRow.action, AuditEventRow.before, AuditEventRow.after)
                .where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.entity_ref == ref,
                    AuditEventRow.action.like(f"{artifact_type}.%"),
                    AuditEventRow.action.not_in(
                        (CREATION_ACTION[artifact_type], f"{artifact_type}.submitted")
                    ),
                )
                .order_by(AuditEventRow.at)
            )
        ).all()
    return [(a, (b or {}).get("status"), (af or {}).get("status")) for a, b, af in rows]


@pytest.mark.req("FR-351")
@pytest.mark.req("FR-355")
@pytest.mark.parametrize("outcome", _OUTCOMES)
@pytest.mark.parametrize("artifact_type", APPROVABLE)
async def test_a_decision_moves_the_version_as_fr_355_says_and_records_it_truly(
    client: TestClient, database: Database, workspace_id, grant, submitter_headers,
    artifact_type: str, outcome: str,
) -> None:
    """Table-driven over every approvable type and every outcome of a two-approver policy.

    The version's status follows FR-355's mapping for its type; a type with no decision hook
    does not move. Where it moves, the one Audit Event its module writes names the move, and
    its `before` is the state the version was really in.
    """
    await _require_two_approvals(client, workspace_id, grant, database, artifact_type)
    if artifact_type == "model":
        # The autouse model: `review`, on a validated dataset version with diagnostics, so an
        # approval is not refused for the model's own reasons (FR-205, FR-202).
        slug, version, ref = MODEL_SLUG, 7, MODEL
    else:
        slug, version = f"{artifact_type.replace('_', '-')}-table", 1
        ref = await _create_authored(
            database, workspace_id, artifact_type, slug, version, new_uuid7()
        )
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": ref, "change_summary": "Table case."},
        headers=submitter_headers,
    )
    assert created.status_code == 201, created.text
    request_id = created.json()["id"]

    first, second = new_uuid7(), new_uuid7()
    for who in (first, second):
        await grant("approver", principal_id=who)
    decisions = {
        "approve": [(first, "approve"), (second, "approve")],
        "first_of_two": [(first, "approve")],
        "reject": [(first, "reject")],
        "request_changes": [(first, "request_changes")],
    }[outcome]
    for who, decision in decisions:
        response = client.post(
            f"/api/v1/approval-requests/{request_id}/decide",
            json={"decision": decision, "comment": "Reviewed."},
            headers=_headers(who, workspace_id),
        )
        assert response.status_code == 200, response.text

    expected = _AFTER[artifact_type][outcome]
    assert await _version_status(database, workspace_id, artifact_type, slug, version) == expected
    moves = await _decision_moves(database, workspace_id, artifact_type, ref)
    if expected == REVIEWABLE_STATE[artifact_type]:
        assert moves == []
    else:
        assert moves == [
            (_MOVE_ACTION[artifact_type](expected), REVIEWABLE_STATE[artifact_type], expected)
        ]
