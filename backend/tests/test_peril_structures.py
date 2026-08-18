"""Peril structures, from the request to the approval (`02` FR-MODEL-58..61, 74, §5.1).

`packages/pricing-core/tests/test_perils.py` owns the arithmetic. This owns the four things
only the platform can be wrong about:

* **the refusals happen before a Job is queued** — an unfitted model, a `separate_model`
  treatment nothing computes yet, perils modelled on different holdouts. `request_comparison`
  set the precedent and the reason;
* **a reconciled composition cannot be edited**, at the privilege layer rather than only in
  the service. The reconciliation measured *that* set of models;
* **all four routes are in the published contract** — including the two `02` §5.1 did not
  declare, which is the gap the endpoint audit is structurally unable to see;
* **the whole path runs**: compose, reconcile through the real Job, submit for approval.

The fixture book is 21 exposure-years, so the passing reconciliation declares a **wide**
tolerance. The failing one is produced by a doubled restoration loading rather than by a
punitive tolerance — the fit reconciles to the penny here, so a near-zero tolerance still
passed. What is under test is the machinery: that the ratio is computed on a *restored*
basis and that the verdict follows the declared number.
"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_contracts import OPENAPI, _load
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _spec,
    _split,
    _validated_version,
)
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.models import PerilStructureRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import perils as service
from app.worker.tasks import execute_job
from model_schema import (
    ExcludedPeril,
    JobKind,
    JobStatus,
    LargeLossKind,
    LargeLossTreatment,
    PerilComponent,
    PerilMethod,
    PerilStructureStatus,
    Principal,
)

EVIDENCE = {"sha256": "c" * 64, "bytes": 1_024, "media_type": "application/json"}


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    return _headers(principal.id, workspace_id)


async def _fitted_model(
    database: Database, blob_store, workspace_id, actor, version_id, factor_id, split, **over
) -> tuple[UUID, str, int]:
    """One model fitted through the real Job, and the ref a peril would cite."""
    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_spec(version_id, (factor_id,), split_ref=split, **over),
        )
        model_id, slug, version = row.id, row.model_family_slug, row.version
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "model_id": str(model_id),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    return model_id, slug, version


async def _book(
    database: Database, blob_store, workspace_id
) -> tuple[Principal, UUID, UUID, object]:
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)
    return actor, version_id, area, split


async def _burning_cost_peril(
    database, blob_store, workspace_id, actor, version_id, area, split
) -> PerilComponent:
    """One `burning_cost` peril over the seeded book's incurred cost column."""
    _, slug, version = await _fitted_model(
        database,
        blob_store,
        workspace_id,
        actor,
        version_id,
        area,
        split,
        response_column="claim_amount_minor",
        family="tweedie",
        family_params={"power": 1.5},
    )
    return PerilComponent(
        peril="WINDSCREEN",
        method=PerilMethod.BURNING_COST,
        burning_cost_model=f"model:{slug}@{version}",
        large_loss=LargeLossTreatment(kind=LargeLossKind.NONE),
    )


async def _structure(
    database, workspace_id, actor, perils, excluded=()
) -> PerilStructureRow:
    async with database.unit_of_work() as session:
        return await service.create_structure(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=f"motor-gb-{uuid4().hex[-6:]}",
            perils=list(perils),
            excluded_perils=[e.model_dump(mode="json") for e in excluded],
        )


# -- the refusals, before a Job exists -----------------------------------------------------


@pytest.mark.req("FR-MODEL-58")
async def test_a_structure_citing_an_unfitted_model_is_refused(
    database, blob_store, workspace_id
) -> None:
    """A `draft` model has no coefficients, so the composition cannot be priced at all."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )
        reserved_slug, reserved_version = row.model_family_slug, row.version

    peril = PerilComponent(
        peril="AD",
        method=PerilMethod.BURNING_COST,
        burning_cost_model=f"model:{reserved_slug}@{reserved_version}",
        large_loss=LargeLossTreatment(kind=LargeLossKind.NONE),
    )
    with pytest.raises(PlatformError) as refused:
        await _structure(database, workspace_id, actor, [peril])
    assert refused.value.code == "MODEL_NOT_FITTED"


@pytest.mark.req("FR-MODEL-58")
async def test_a_structure_citing_a_model_that_does_not_resolve_is_refused(
    database, blob_store, workspace_id
) -> None:
    actor, _version_id, _area, _split = await _book(database, blob_store, workspace_id)
    peril = PerilComponent(
        peril="AD",
        method=PerilMethod.BURNING_COST,
        burning_cost_model="model:no-such-family@3",
        large_loss=LargeLossTreatment(kind=LargeLossKind.NONE),
    )
    with pytest.raises(PlatformError) as refused:
        await _structure(database, workspace_id, actor, [peril])
    assert refused.value.code == "NOT_FOUND"
    assert "no-such-family@3" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-59")
async def test_separate_model_is_refused_before_a_job_exists(
    database, blob_store, workspace_id
) -> None:
    """FR-MODEL-59 declares four treatments and this slice computes three. The caller is
    told now, naming the peril, rather than by a job that fails after loading the dataset."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    excess = peril.model_copy(
        update={
            "large_loss": LargeLossTreatment(
                kind=LargeLossKind.SEPARATE_MODEL,
                excess_model=peril.burning_cost_model,
                attachment_minor=100_000_000,
                evidence_blob=EVIDENCE,
            )
        }
    )
    row = await _structure(database, workspace_id, actor, [excess])
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_reconciliation(
                session,
                workspace_id=workspace_id,
                actor=actor,
                structure_id=row.id,
                tolerance=Decimal("0.02"),
            )
    assert refused.value.code == "LOSS_TREATMENT_UNIMPLEMENTED"
    assert "WINDSCREEN" in (refused.value.detail or "")


@pytest.mark.req("FR-MODEL-60")
async def test_a_zero_tolerance_is_refused(database, blob_store, workspace_id) -> None:
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    row = await _structure(database, workspace_id, actor, [peril])
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_reconciliation(
                session,
                workspace_id=workspace_id,
                actor=actor,
                structure_id=row.id,
                tolerance=Decimal("0"),
            )
    assert refused.value.code == "VALIDATION_FAILED"


@pytest.mark.req("FR-MODEL-60")
async def test_perils_on_different_holdouts_are_refused_and_both_are_named(
    database, blob_store, workspace_id
) -> None:
    """FR-MODEL-60 sums across perils and compares the total to one observed figure; perils
    scored on different holdouts sum over different books."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    here = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )

    other_dataset = await _dataset(database, blob_store, workspace_id, actor)
    other_version = await _validated_version(
        database, blob_store, workspace_id, actor, other_dataset
    )
    other_area = await _factor(
        database, workspace_id, actor, other_dataset, "area", "area"
    )
    other_split = await _split(
        database, blob_store, workspace_id, actor, other_version
    )
    _, slug, version = await _fitted_model(
        database,
        blob_store,
        workspace_id,
        actor,
        other_version,
        other_area,
        other_split,
        response_column="claim_amount_minor",
        family="tweedie",
        family_params={"power": 1.5},
    )
    elsewhere = PerilComponent(
        peril="TP_BI",
        method=PerilMethod.BURNING_COST,
        burning_cost_model=f"model:{slug}@{version}",
        large_loss=LargeLossTreatment(kind=LargeLossKind.NONE),
    )

    row = await _structure(database, workspace_id, actor, [here, elsewhere])
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.request_reconciliation(
                session,
                workspace_id=workspace_id,
                actor=actor,
                structure_id=row.id,
                tolerance=Decimal("0.02"),
            )
    assert refused.value.code == "PERIL_STRUCTURE_RECONCILIATION_FAILED"
    detail = refused.value.detail or ""
    assert str(split.split_artifact_id) in detail
    assert str(other_split.split_artifact_id) in detail


# -- the lifecycle -------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-58")
async def test_versioning_is_by_slug(database, blob_store, workspace_id) -> None:
    """A structure is edited by superseding it, which is what keeps FR-MODEL-61's pinned
    reference resolvable for as long as any Rating Version holds it."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    slug = f"motor-gb-{uuid4().hex[-6:]}"
    versions = []
    for _ in range(2):
        async with database.unit_of_work() as session:
            row = await service.create_structure(
                session,
                workspace_id=workspace_id,
                actor=actor,
                slug=slug,
                perils=[peril],
                excluded_perils=[],
            )
            versions.append(row.version)
    assert versions == [1, 2]


@pytest.mark.req("FR-MODEL-61")
async def test_a_draft_cannot_be_submitted(database, blob_store, workspace_id) -> None:
    """FR-MODEL-61 reaches `review` from `reconciled` only: the reconciliation is the
    evidence the approval reads, so the lifecycle has no edge that skips it."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    row = await _structure(database, workspace_id, actor, [peril])
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session,
                workspace_id=workspace_id,
                actor=actor,
                structure_id=row.id,
                change_summary="first cut",
            )
    assert refused.value.status_code == 409


@pytest.mark.req("FR-MODEL-60")
async def test_a_reconciled_composition_cannot_be_rewritten(
    database, blob_store, workspace_id
) -> None:
    """At the privilege layer, not only in the service: the reconciliation measured *this*
    set of models, and a later edit leaves the number attached to a composition that never
    produced it."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    row = await _structure(database, workspace_id, actor, [peril])
    structure_id = row.id

    async with database.unit_of_work() as session:
        await session.execute(
            text(
                "UPDATE peril_structures SET reconciliation = '{}'::jsonb, "
                "status = 'reconciled' WHERE id = :id"
            ),
            {"id": structure_id},
        )

    with pytest.raises(Exception) as blocked:  # noqa: PT011 - the driver's error type
        async with database.unit_of_work() as session:
            await session.execute(
                text("UPDATE peril_structures SET perils = '[]'::jsonb WHERE id = :id"),
                {"id": structure_id},
            )
    assert "immutable" in str(blocked.value).lower()


@pytest.mark.req("FR-MODEL-60")
async def test_a_reconciled_structure_cannot_be_deleted(
    database, blob_store, workspace_id
) -> None:
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    row = await _structure(database, workspace_id, actor, [peril])
    structure_id = row.id
    async with database.unit_of_work() as session:
        await session.execute(
            text(
                "UPDATE peril_structures SET reconciliation = '{}'::jsonb, "
                "status = 'reconciled' WHERE id = :id"
            ),
            {"id": structure_id},
        )
    with pytest.raises(Exception) as blocked:  # noqa: PT011 - the driver's error type
        async with database.unit_of_work() as session:
            await session.execute(
                text("DELETE FROM peril_structures WHERE id = :id"), {"id": structure_id}
            )
    assert "cannot be deleted" in str(blocked.value).lower()


# -- the whole path ------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-60")
async def test_the_reconcile_job_runs_and_persists_its_verdict(
    database, blob_store, workspace_id
) -> None:
    """`wf-01` E5 end to end: compose, reconcile through the real Job, read the artifact.

    The tolerance is wide for the reason the module docstring gives — the machinery is what
    is under test, on a book of twenty-one exposure years.
    """
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    row = await _structure(
        database,
        workspace_id,
        actor,
        [peril],
        excluded=[ExcludedPeril(peril="COURTESY_CAR", reason="Loaded flat in rating.")],
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

    async with database.unit_of_work() as session:
        structure = await service.load_structure(
            session, workspace_id=workspace_id, structure_id=structure_id
        )
    assert structure.status is PerilStructureStatus.RECONCILED
    assert structure.reconciliation is not None
    assert structure.reconciliation.status.value == "pass"
    # FR-MODEL-74: the treatment is stated beside the number, per peril.
    assert [p.large_loss_kind for p in structure.reconciliation.perils] == [
        LargeLossKind.NONE
    ]
    # FR-MODEL-58: the total is the sum over perils, exactly.
    assert (
        sum(p.modelled_burning_cost_minor for p in structure.reconciliation.perils)
        == structure.reconciliation.modelled_burning_cost_minor
    )


@pytest.mark.req("FR-MODEL-61")
async def test_a_failing_reconciliation_is_recorded_and_blocks_review(
    database, blob_store, workspace_id
) -> None:
    """FR-MODEL-60 asks for the reconciliation to be *persisted*; a failing one is the
    finding. What it blocks is `review`, because the tolerance is the submitter's own
    number and a structure that misses it has failed a test it set itself.

    The failure is produced by a **doubled restoration loading**, not by a punitive
    tolerance: the fit reconciles to the penny on this book, so a near-zero tolerance still
    passed. That is a better test anyway — it drives FR-MODEL-74's restoration through the
    platform path and shows it moving the ratio, which a `none` treatment cannot.
    """
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    doubled = peril.model_copy(
        update={
            "large_loss": LargeLossTreatment(
                kind=LargeLossKind.CAPPED,
                cap_minor=2_500_000,
                restoration_loading=Decimal("2.0"),
                evidence_blob=EVIDENCE,
            )
        }
    )
    row = await _structure(database, workspace_id, actor, [doubled])
    structure_id = row.id

    async with database.unit_of_work() as session:
        reserved = await service.request_reconciliation(
            session,
            workspace_id=workspace_id,
            actor=actor,
            structure_id=structure_id,
            tolerance=Decimal("0.02"),
        )
        job = await job_service.submit(
            session,
            JobKind.PERIL_STRUCTURE_RECONCILE,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                **service.reconcile_payload(
                    reserved,
                    tolerance=Decimal("0.02"),
                    observed_column="claim_amount_minor",
                    exposure_column="exposure_years",
                ),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.unit_of_work() as session:
        structure = await service.load_structure(
            session, workspace_id=workspace_id, structure_id=structure_id
        )
        assert structure.reconciliation is not None
        assert structure.reconciliation.status.value == "fail"

        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session,
                workspace_id=workspace_id,
                actor=actor,
                structure_id=structure_id,
                change_summary="please approve",
            )
    assert refused.value.code == "EVIDENCE_INCOMPLETE"


@pytest.mark.req("FR-MODEL-61")
async def test_a_reconciled_structure_reaches_review_with_an_approval_request(
    database, blob_store, workspace_id
) -> None:
    """FR-MODEL-61's approvability, through the generic machine (`06` FR-GOV-9).

    It works only because `DEFAULT_POLICY` gained a `peril_structure` entry with this slice:
    without one, `approvals.submit` refuses with "no approval policy for this artifact
    type", which is a correct refusal of an artifact nobody could ever approve.
    """
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    row = await _structure(database, workspace_id, actor, [peril])
    structure_id, slug, version = row.id, row.slug, row.version

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

    async with database.unit_of_work() as session:
        updated, request = await service.submit_for_review(
            session,
            workspace_id=workspace_id,
            actor=actor,
            structure_id=structure_id,
            change_summary="first structure for the GB motor book",
        )
        assert updated.status == PerilStructureStatus.REVIEW.value
        assert request.artifact_ref == f"peril_structure:{slug}@{version}"
        assert updated.approval_request_id == request.id


# -- the contract --------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-90")
def test_all_four_routes_are_published() -> None:
    """`02` §5.1 declared the create and the reconcile. A create whose artifact nothing can
    fetch, and an approvable artifact with no way to submit it, are the omission FR-MODEL-84
    repaired for transparency — and one the endpoint audit cannot see, because it compares
    the spec against the contract and an endpoint missing from both is in neither.
    """
    paths = _load(OPENAPI)["paths"]
    assert "post" in paths["/api/v1/peril-structures"]
    assert "get" in paths["/api/v1/peril-structures/{structure_id}"]
    assert "post" in paths["/api/v1/peril-structures/{structure_id}/reconcile"]
    assert "post" in paths["/api/v1/peril-structures/{structure_id}/submit"]


@pytest.mark.req("FR-MODEL-90")
def test_reading_a_structure_that_does_not_exist_is_a_404(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    response = api_client.get(f"/api/v1/peril-structures/{uuid4()}", headers=actuary)
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
