"""A Peril Structure reaches `approved` only through the approval workflow (FD-1456, PL-1461).

Four things this module holds, none of which `test_peril_structures.py` can see because it
stops at `review`:

* **the decision moves the structure** — approval supersedes an earlier approved version
  (DP-2 (a)), and a structure over a component model that is not `ModelStatus.APPROVED` is
  refused at approval, with the decision rolled back (DP-1 (a), RL-1457);
* **the component check uses `ModelStatus`'s own approved set**, never compile's cross-type
  `_APPROVED_OR_BETTER`, whose `live` and `retired` are not model statuses;
* **the compile resolver resolves a Peril Structure pin** and maturity refuses one that is
  not `approved` (FR-237, FR-20) — FD-1456's positive test, replacing PL-1429's tripwire.

The fixtures are the real path (a fitted model, the reconcile Job, `submit_for_review`, the
HTTP decide), so the approval request is real and `approval_guard()` sees a genuine decision.
"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from backend.tests.approved_rows import mark_approved
from backend.tests.test_api_approvals import _headers as _approver_headers
from backend.tests.test_peril_structures import (
    _book,
    _burning_cost_peril,
)
from backend.tests.test_rating_version_compile import (
    _empty_pins,
    _read_blob,
    _run_compile_job,
)
from backend.tests.test_rating_version_create_pins import _algorithm, _body
from sqlalchemy import select

from app.db.models import (
    ApprovalDecisionRow,
    ApprovalRequestRow,
    AuditEventRow,
    ModelRow,
    PerilStructureRow,
)
from app.db.session import Database
from app.platform import jobs as job_service
from app.platform import perils as service
from app.worker.tasks import execute_job
from model_schema import (
    JobKind,
    JobStatus,
    LargeLossTreatment,
    ModelStatus,
    Principal,
    new_uuid7,
)
from pricing_core.rating.compile import Bundle

_LOOP = asyncio.get_event_loop

_APPROVED_COMPONENT = ModelStatus.APPROVED


@pytest.fixture(autouse=True)
def _handlers() -> None:
    from app.worker.rating_handlers import register_rating_handlers

    register_rating_handlers()


async def _model_id(database: Database, ref: str) -> UUID:
    """The `ModelRow.id` behind a `model:<slug>@<version>` ref."""
    slug, _, version = ref.removeprefix("model:").rpartition("@")
    async with database.session() as session:
        return (
            await session.execute(
                select(ModelRow.id).where(
                    ModelRow.model_family_slug == slug, ModelRow.version == int(version)
                )
            )
        ).scalar_one()


async def _set_model_status(database: Database, model_id: UUID, status: ModelStatus) -> None:
    """Put a component model in `status`; `approved` goes through the guard's evidence."""
    async with database.unit_of_work() as session:
        row = await session.get(ModelRow, model_id)
        assert row is not None
        if status is ModelStatus.APPROVED:
            await mark_approved(session, row)
        else:
            row.status = status.value
            await session.flush()


async def _reconciled(
    database: Database, blob_store, workspace_id, actor: Principal, perils, slug: str
) -> PerilStructureRow:
    """`create_structure` then the real reconcile Job: the structure ends `reconciled`."""
    async with database.unit_of_work() as session:
        row = await service.create_structure(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=slug,
            perils=list(perils),
            excluded_perils=[],
        )
        structure_id = row.id
    async with database.unit_of_work() as session:
        reserved = await service.request_reconciliation(
            session,
            workspace_id=workspace_id,
            actor=actor,
            structure_id=structure_id,
            tolerance=Decimal("0.9"),
        )
        job = await job_service.submit(
            session,
            JobKind.PERIL_STRUCTURE_RECONCILE,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                **service.reconcile_payload(
                    reserved,
                    tolerance=Decimal("0.9"),
                    observed_column="claim_amount_minor",
                    exposure_column="exposure_years",
                ),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        refreshed = await session.get(PerilStructureRow, structure_id)
    assert refreshed is not None
    assert refreshed.status == "reconciled"
    return refreshed


async def _in_review(
    database: Database, blob_store, workspace_id, actor: Principal, perils, slug: str
) -> tuple[PerilStructureRow, UUID]:
    """A structure in `review`, and the id of the approval request that holds it there."""
    reconciled = await _reconciled(database, blob_store, workspace_id, actor, perils, slug)
    async with database.unit_of_work() as session:
        row, request = await service.submit_for_review(
            session,
            workspace_id=workspace_id,
            actor=actor,
            structure_id=reconciled.id,
            change_summary="FD-1456 fixture",
        )
        assert row.status == "review"
        return row, request.id


async def _approver(grant, workspace_id) -> dict[str, str]:
    who = new_uuid7()
    await grant("approver", principal_id=who)
    return _approver_headers(who, workspace_id)


def _decide(client, request_id: UUID, headers: dict[str, str], decision: str = "approve"):
    return client.post(
        f"/api/v1/approval-requests/{request_id}/decide",
        json={"decision": decision, "comment": "Reviewed."},
        headers=headers,
    )


async def _status(database: Database, structure_id: UUID) -> str:
    async with database.session() as session:
        row = await session.get(PerilStructureRow, structure_id)
    assert row is not None
    return row.status


async def _peril_events(database: Database, ref: str) -> list[tuple[str, str | None, str | None]]:
    async with database.session() as session:
        rows = (
            await session.execute(
                select(AuditEventRow.action, AuditEventRow.before, AuditEventRow.after)
                .where(
                    AuditEventRow.entity_ref == ref,
                    AuditEventRow.action.like("peril_structure.%"),
                )
                .order_by(AuditEventRow.at)
            )
        ).all()
    return [(a, (b or {}).get("status"), (af or {}).get("status")) for a, b, af in rows]


# -- DP-2 (a): an earlier approved version is superseded -------------------------------------


@pytest.mark.req("FR-191")
async def test_approving_a_peril_structure_supersedes_the_earlier_approved_version(
    api_client, database, blob_store, workspace_id, grant
) -> None:
    """`ps@1` approved through the workflow, then `ps@2`: `ps@1` reads `superseded`."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    await _set_model_status(
        database, await _model_id(database, str(peril.burning_cost_model)), ModelStatus.APPROVED
    )
    slug = f"ps-{uuid4().hex[-6:]}"
    headers = await _approver(grant, workspace_id)

    first, first_request = await _in_review(
        database, blob_store, workspace_id, actor, [peril], slug
    )
    assert _decide(api_client, first_request, headers).status_code == 200
    assert await _status(database, first.id) == "approved"

    second, second_request = await _in_review(
        database, blob_store, workspace_id, actor, [peril], slug
    )
    assert (first.version, second.version) == (1, 2)
    assert _decide(api_client, second_request, headers).status_code == 200

    assert await _status(database, second.id) == "approved"
    assert await _status(database, first.id) == "superseded"
    decided = [
        event
        for event in await _peril_events(database, f"peril_structure:{slug}@1")
        if event[0] in {"peril_structure.approved", "peril_structure.superseded"}
    ]
    assert decided == [
        ("peril_structure.approved", "review", "approved"),
        ("peril_structure.superseded", "approved", "superseded"),
    ]


# -- DP-1 (a): per-peril model approvals are enforced at approval ---------------------------


@pytest.mark.req("FR-363")
@pytest.mark.req("FR-191")
async def test_a_peril_structure_with_an_unapproved_component_is_refused_at_approve(
    api_client, database, blob_store, workspace_id, grant
) -> None:
    """A `fitted` component model: `422 EVIDENCE_INCOMPLETE` naming it; nothing moves."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    component = str(peril.burning_cost_model)
    structure, request_id = await _in_review(
        database, blob_store, workspace_id, actor, [peril], f"ps-{uuid4().hex[-6:]}"
    )

    refused = _decide(api_client, request_id, await _approver(grant, workspace_id))

    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "EVIDENCE_INCOMPLETE"
    assert component in refused.text
    assert await _status(database, structure.id) == "review"
    async with database.session() as session:
        request = await session.get(ApprovalRequestRow, request_id)
        decisions = (
            await session.execute(
                select(ApprovalDecisionRow).where(ApprovalDecisionRow.request_id == request_id)
            )
        ).all()
    assert request is not None
    assert request.status == "review"
    assert decisions == [], "the decision must roll back with the carry"


@pytest.mark.req("FR-363")
async def test_a_peril_structure_whose_components_are_all_approved_is_approved(
    api_client, database, blob_store, workspace_id, grant
) -> None:
    """The control for the refusal above: the same path, the component approved."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    await _set_model_status(
        database, await _model_id(database, str(peril.burning_cost_model)), ModelStatus.APPROVED
    )
    structure, request_id = await _in_review(
        database, blob_store, workspace_id, actor, [peril], f"ps-{uuid4().hex[-6:]}"
    )

    assert _decide(api_client, request_id, await _approver(grant, workspace_id)).status_code == 200
    assert await _status(database, structure.id) == "approved"


@pytest.mark.req("FR-363")
@pytest.mark.parametrize("component_status", list(ModelStatus), ids=lambda s: s.value)
async def test_the_component_check_accepts_only_model_status_approved(
    api_client, database, blob_store, workspace_id, grant, component_status: ModelStatus
) -> None:
    """Every `ModelStatus` member: only `APPROVED` passes, `superseded` included (RL-1457 item 1).

    The component is fitted (so the structure can be composed), then moved to the status under
    test before the decision.
    """
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    component = str(peril.burning_cost_model)
    structure, request_id = await _in_review(
        database, blob_store, workspace_id, actor, [peril], f"ps-{uuid4().hex[-6:]}"
    )
    await _set_model_status(database, await _model_id(database, component), component_status)

    response = _decide(api_client, request_id, await _approver(grant, workspace_id))

    if component_status is _APPROVED_COMPONENT:
        assert response.status_code == 200, response.text
        assert await _status(database, structure.id) == "approved"
    else:
        assert response.status_code == 422, response.text
        assert response.json()["code"] == "EVIDENCE_INCOMPLETE"
        assert component in response.text
        assert await _status(database, structure.id) == "review"


def test_the_component_check_accepted_set_is_inside_the_enum() -> None:
    """`live` and `retired` are compile's cross-type statuses; they are not model statuses.

    Red against the plan's first list (`{"approved", "live", "retired"}`): a check that
    accepted either would accept a status no `ModelStatus` member has.
    """
    from app.platform.perils import APPROVED_COMPONENT_STATUSES

    assert frozenset({ModelStatus.APPROVED}) == APPROVED_COMPONENT_STATUSES
    assert {s.value for s in APPROVED_COMPONENT_STATUSES} <= {s.value for s in ModelStatus}
    assert not {"live", "retired"} & {s.value for s in APPROVED_COMPONENT_STATUSES}


@pytest.mark.req("FR-363")
async def test_a_separate_model_excess_model_is_checked_at_approve(
    api_client, database, blob_store, workspace_id, grant
) -> None:
    """The large-loss `excess_model` is a component too (`_model_refs` does not list it).

    A `separate_model` structure cannot be reconciled yet (it is refused before a Job), so
    the row is placed in `review` directly, under a real approval request.
    """
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    await _set_model_status(
        database, await _model_id(database, str(peril.burning_cost_model)), ModelStatus.APPROVED
    )
    # The excess model is a second fitted model, left unapproved.
    excess_peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    excess_ref = str(excess_peril.burning_cost_model)
    separate = peril.model_copy(
        update={
            "large_loss": LargeLossTreatment.model_validate(
                {
                    "kind": "separate_model",
                    "excess_model": excess_ref,
                    "attachment_minor": 100_000_000,
                    "evidence_blob": {
                        "sha256": "c" * 64,
                        "bytes": 1_024,
                        "media_type": "application/json",
                    },
                }
            )
        }
    )
    slug = f"ps-{uuid4().hex[-6:]}"
    async with database.unit_of_work() as session:
        # Created through the service so the structure has its creation Audit Event (FR-353
        # refuses an approval whose author cannot be established); then placed in `review`.
        row = await service.create_structure(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=slug,
            perils=[separate],
            excluded_perils=[],
        )
        row.status = "review"
        row.reconciliation = {"status": "pass"}
        await session.flush()
        structure_id = row.id
    created = api_client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": f"peril_structure:{slug}@1", "change_summary": "excess"},
        headers=_approver_headers(actor.id, workspace_id),
    )
    assert created.status_code == 201, created.text
    request_id = UUID(created.json()["id"])
    headers = await _approver(grant, workspace_id)

    refused = _decide(api_client, request_id, headers)
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "EVIDENCE_INCOMPLETE"
    assert excess_ref in refused.text
    assert await _status(database, structure_id) == "review"

    await _set_model_status(database, await _model_id(database, excess_ref), ModelStatus.APPROVED)
    assert _decide(api_client, request_id, headers).status_code == 200
    assert await _status(database, structure_id) == "approved"


# -- FR-237, FR-20: the compile resolver ------------------------------------------------------


def _pin_and_compile(api_client, headers, database, blob_store, ref: str, slug: str):
    algorithm_ref = _algorithm(api_client, headers)
    created = api_client.post(
        "/api/v1/rating-versions",
        json=_body(slug, algorithm_ref=algorithm_ref, pins={**_empty_pins(), "models": [ref]}),
        headers=headers,
    )
    assert created.status_code == 201, created.text
    version_id = UUID(created.json()["id"])
    return version_id, _run_compile_job(api_client, headers, database, blob_store, version_id)


@pytest.mark.req("FR-237")
@pytest.mark.req("FR-20")
@pytest.mark.parametrize("state", ["reconciled", "review"])
def test_an_unapproved_peril_structure_pin_is_refused_at_compile(
    api_client, database, blob_store, workspace_id, principal, grant, state: str
) -> None:
    """FD-1456's positive test: a structure that is not `approved` fails `PIN_NOT_APPROVED`."""
    from backend.tests.test_rating_version_compile import _headers

    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    async def _build() -> str:
        actor, version_id, area, split = await _book(database, blob_store, workspace_id)
        peril = await _burning_cost_peril(
            database, blob_store, workspace_id, actor, version_id, area, split
        )
        slug = f"ps-{uuid4().hex[-6:]}"
        if state == "reconciled":
            await _reconciled(database, blob_store, workspace_id, actor, [peril], slug)
        else:
            await _in_review(database, blob_store, workspace_id, actor, [peril], slug)
        return f"peril_structure:{slug}@1"

    ref = _LOOP().run_until_complete(_build())
    _, job = _pin_and_compile(api_client, headers, database, blob_store, ref, f"rv-{state}")

    assert job.status is JobStatus.FAILED
    assert job.error["code"] == "PIN_NOT_APPROVED", job.error
    assert ref in job.error["message"]


@pytest.mark.req("FR-237")
@pytest.mark.req("FR-20")
def test_an_approved_peril_structure_pin_compiles_and_the_bundle_carries_its_payload(
    api_client, database, blob_store, workspace_id, principal, grant
) -> None:
    """The same structure approved through the workflow recompiles to `succeeded`."""
    from backend.tests.test_rating_version_compile import _headers

    _LOOP().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    async def _build() -> tuple[str, UUID]:
        actor, version_id, area, split = await _book(database, blob_store, workspace_id)
        peril = await _burning_cost_peril(
            database, blob_store, workspace_id, actor, version_id, area, split
        )
        await _set_model_status(
            database,
            await _model_id(database, str(peril.burning_cost_model)),
            ModelStatus.APPROVED,
        )
        slug = f"ps-{uuid4().hex[-6:]}"
        _, request_id = await _in_review(database, blob_store, workspace_id, actor, [peril], slug)
        return f"peril_structure:{slug}@1", request_id

    ref, request_id = _LOOP().run_until_complete(_build())
    version_id, first = _pin_and_compile(api_client, headers, database, blob_store, ref, "rv-ok")
    assert first.status is JobStatus.FAILED
    assert first.error["code"] == "PIN_NOT_APPROVED"

    approver = _LOOP().run_until_complete(_approver(grant, workspace_id))
    assert _decide(api_client, request_id, approver).status_code == 200

    second = _run_compile_job(api_client, headers, database, blob_store, version_id)
    assert second.status is JobStatus.SUCCEEDED, second.error
    bundle = Bundle.model_validate_json(_read_blob(database, blob_store, second.result["ref"]))
    assert bundle.resolved_payloads[ref]["status"] == "approved"
