"""`model.fit` end to end, on a dataset that reached `validated` through the real path.

`02` §1.3's hard rules are what these prove, in the order a caller meets them:

* **R1** — a version that is not `validated` cannot be fitted on, refused before a Job
  exists rather than inside one.
* **R2** — a fitted Model is immutable; a second fit of the same model is refused.
* **FR-MODEL-66** — the same specification does not fit twice; the existing model is
  returned instead.

The fit itself runs through `execute_job`, so what is exercised is the handler a worker
would run and not a service call underneath it.
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from backend.tests.test_data_jobs import (
    _ingest,
    _seed_dataset_and_rules,
    _validate,
)
from sqlalchemy import select

from app.db.models import ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import rbac
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ActorKind,
    Factor,
    FactorType,
    GlmSpec,
    JobKind,
    JobStatus,
    ModelStatus,
    OffsetSpec,
    Principal,
    ScopeType,
    new_uuid7,
)

# Both, and in this order: the model spine is fitted on a version this test ingests and
# validates through the `dataset.*` handlers, so a module that registered only its own
# would fail on the setup rather than the subject.
register_data_handlers()
register_model_handlers()

#: A tiny Poisson book. Small enough to fit in a test, structured enough that the fit has
#: a right answer: urban rows carry roughly twice the frequency of rural ones.
#: `claim_amount_minor` is carried because the shared ingest helper's recipe casts it —
#: the seed's own shape, and a book without it is not a book this platform ingests.
BOOK = b"policy_id,exposure_years,area,claim_count,claim_amount_minor\n" + b"".join(
    f"P{i},1.0,{'urban' if i % 2 else 'rural'},{2 if i % 2 else 1},"
    f"{200000 if i % 2 else 100000}\n".encode()
    for i in range(1, 401)
)


async def _actuary(database: Database, workspace_id) -> Principal:
    from app.db.models import RoleAssignmentRow, RoleRow

    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        for slug in ("analyst", "pricing_actuary"):
            role = (
                await session.execute(
                    select(RoleRow).where(
                        RoleRow.workspace_id == workspace_id, RoleRow.slug == slug
                    )
                )
            ).scalar_one()
            session.add(
                RoleAssignmentRow(
                    workspace_id=workspace_id, principal_kind="user", principal_id=user.id,
                    role_id=role.id, scope_type=ScopeType.WORKSPACE.value,
                )
            )
    return user


async def _dataset(database: Database, blob_store, workspace_id, actor: Principal) -> UUID:
    """A dataset **with a rule set**: `01` FR-DATA-16 refuses to validate without one, and
    a version that cannot be validated cannot be fitted on (`02` R1)."""
    return await _seed_dataset_and_rules(database, blob_store, workspace_id, actor)


async def _factor(database: Database, workspace_id, actor, dataset_id, slug, column) -> UUID:
    async with database.unit_of_work() as session:
        row = await model_service.create_factor(
            session,
            workspace_id=workspace_id,
            actor=actor,
            factor=Factor(
                id=uuid4(), slug=slug, dataset_id=dataset_id, version=1,
                type=FactorType.IDENTITY, source_columns=(column,),
            ),
        )
        return row.id


def _spec(version_id: UUID, factor_ids: tuple[UUID, ...], **over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": f"freq-{new_uuid7().hex[-6:]}",
        "dataset_version_id": version_id,
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "factors": factor_ids,
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


async def _validated_version(database, blob_store, workspace_id, actor, dataset_id) -> UUID:
    """Ingest and validate, then promote — the only route to `validated` (`01` §1.3)."""
    version_id = await _ingest(database, blob_store, workspace_id, actor, dataset_id, BOOK)
    report_id = await _validate(database, blob_store, workspace_id, actor, version_id)
    from app.platform import validation as validation_service

    async with database.unit_of_work() as session:
        await validation_service.promote_using_report(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, report_id=report_id,
        )
    return version_id


@pytest.mark.req("FR-MODEL-18")
async def test_a_model_fits_through_the_job_and_stores_its_coefficients(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The spine: validated data in, coefficients out, through the handler a worker runs.

    The urban rows carry twice the claims of the rural ones on equal exposure, so the
    fitted relativity must be near 2 — a fit that ignored the factor, the offset or the
    base level would not land there.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")

    async with database.unit_of_work() as session:
        row, created = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,)),
        )
        assert created is True
        model_id = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor,
            workspace_id=workspace_id,
        )

    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))

    assert model.status is ModelStatus.FITTED
    assert model.fit_result is not None
    urban = next(c for c in model.fit_result.coefficients if c.term == "area[urban]")
    assert urban.relativity == pytest.approx(2.0, rel=0.1)
    # R5: the estimate arrives with its uncertainty or it does not arrive.
    assert urban.std_error > 0
    assert urban.ci_95[0] < urban.estimate < urban.ci_95[1]
    # FR-MODEL-21: the relativity table names its base level.
    base = next(level for level in model.fit_result.relativities["area"] if level.is_base)
    assert base.level == "rural"
    assert base.relativity == 1.0


@pytest.mark.req("FR-MODEL-18")
async def test_an_unvalidated_version_cannot_be_fitted_on(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`02` R1, and it is `01` §1.3's gate — refused **before** a Job exists.

    Checked in the request rather than the worker so the caller learns it from a 409
    instead of from a job that fails twenty seconds later.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    draft_version = await _ingest(
        database, blob_store, workspace_id, actor, dataset_id, BOOK
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")

    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor,
                spec=_spec(draft_version, (area,)),
            )
    assert refused.value.code == "DATASET_NOT_VALIDATED"

    async with database.session() as session:
        assert (
            await session.execute(select(ModelRow).where(ModelRow.workspace_id == workspace_id))
        ).scalars().all() == []


@pytest.mark.req("FR-MODEL-18")
async def test_the_same_specification_does_not_fit_twice(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-66: the existing model is returned rather than a second one created.

    Not an error — the caller asked for a model with this specification and it exists.
    Fitting again would burn a worker to produce the same numbers under a new id, and
    leave two versions nobody can choose between.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    spec = _spec(version_id, (area,))

    async with database.unit_of_work() as session:
        first, created_first = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )
    async with database.unit_of_work() as session:
        second, created_second = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )

    assert created_first is True
    assert created_second is False
    assert first.id == second.id

    # ...and a spec differing anywhere at all is a different model.
    async with database.unit_of_work() as session:
        other, created_other = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), seed=7),
        )
    assert created_other is True
    assert other.id != first.id


@pytest.mark.req("FR-MODEL-18")
async def test_a_fitted_model_cannot_be_refitted(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`02` R2: immutable once fitted. A refit is a new version, never new coefficients.

    Without this the rule would hold only for callers who remembered it — and a Rating
    Version's reference to a model version would stop meaning anything fixed.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=_spec(version_id, (area,))
        )
        model_id = row.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        fitted = model_service.to_model(await session.get(ModelRow, model_id))
    assert fitted.fit_result is not None

    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await model_service.record_fit(
                session, workspace_id=workspace_id, actor=actor,
                model_id=model_id, fit_result=fitted.fit_result,
            )
    assert refused.value.code == "MODEL_IMMUTABLE"
