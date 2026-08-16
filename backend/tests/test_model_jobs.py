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

from app.db.models import DatasetVersionRow, ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets as dataset_service
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import rbac
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ActorKind,
    DatasetStatus,
    Factor,
    FactorType,
    GlmSpec,
    JobKind,
    JobStatus,
    ModelStatus,
    OffsetSpec,
    Principal,
    ScopeType,
    SplitRef,
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
#:
#: **Rural carries three quarters of the exposure**, so it is unambiguously the base level
#: (`02` §4.1's `largest_exposure`). An even split left the base decided by a tie-break and
#: the expected term name unknowable — which is a bad fixture rather than a bad rule.
BOOK = b"policy_id,exposure_years,area,claim_count,claim_amount_minor\n" + b"".join(
    f"P{i},1.0,{'urban' if i % 4 == 0 else 'rural'},{2 if i % 4 == 0 else 1},"
    f"{200000 if i % 4 == 0 else 100000}\n".encode()
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


async def _split(
    database: Database, blob_store: BlobStore, workspace_id, actor, parent_version_id: UUID
) -> SplitRef:
    """Derive train and test parts through the real Jobs, then record the split.

    Through `dataset.derive` rather than by inserting rows, because materialising the parts
    is what that handler now does — a split whose parts were faked would give every fit a
    holdout identical to its training set, which is the defect this slice exists to remove.
    """
    parts: dict[str, UUID] = {}
    for part in ("train", "test"):
        async with database.unit_of_work() as session:
            job = await job_service.submit(
                session,
                JobKind.DATASET_DERIVE,
                {
                    "workspace_id": str(workspace_id),
                    "actor": {"kind": actor.kind.value, "id": str(actor.id),
                              "display": actor.display},
                    "parent_version_id": str(parent_version_id),
                    "operation": "split",
                    "params": {"method": "random", "seed": 20260816, "part": part,
                               "fractions": {"train": 0.75, "test": 0.25}},
                },
                actor,
                workspace_id=workspace_id,
            )
        assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
        async with database.session() as session:
            child = (
                await session.execute(
                    select(DatasetVersionRow).where(
                        DatasetVersionRow.workspace_id == workspace_id,
                        DatasetVersionRow.derived_from["parent_version_id"].astext
                        == str(parent_version_id),
                        DatasetVersionRow.derived_from["params"]["part"].astext == part,
                    )
                )
            ).scalar_one()
        parts[part] = child.id

    async with database.unit_of_work() as session:
        row = await dataset_service.record_split(
            session,
            workspace_id=workspace_id,
            actor=actor,
            parent_version_id=parent_version_id,
            name=f"holdout-{new_uuid7().hex[-6:]}",
            method="random",
            seed=20260816,
            parts=parts,
        )
        return SplitRef(split_artifact_id=row.id, train_part="train", holdout_part="test")


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
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split),
        )
        assert should_fit is True
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


@pytest.mark.req("FR-MODEL-66")
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
    split = await _split(database, blob_store, workspace_id, actor, version_id)
    spec = _spec(version_id, (area,), split_ref=split)

    async with database.unit_of_work() as session:
        first, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )
        first_id = first.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(first_id)},
            actor, workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.unit_of_work() as session:
        second, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )
        assert second.id == first_id, "one specification, one model row"
        assert should_fit is False, "it is already fitted; there is nothing to queue"

    # ...and a spec differing anywhere at all is a different model.
    async with database.unit_of_work() as session:
        other, other_should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), seed=7, split_ref=split),
        )
    assert other_should_fit is True
    assert other.id != first_id


@pytest.mark.req("FR-MODEL-65")
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
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split)
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

    # The diagnostics the first fit recorded, replayed. Re-using them rather than building
    # an empty set keeps the refusal about R2 — a second `record_fit` that failed for want
    # of a valid argument would pass this test without exercising the rule.
    async with database.session() as session:
        evidence = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )

    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await model_service.record_fit(
                session, workspace_id=workspace_id, actor=actor,
                model_id=model_id, fit_result=fitted.fit_result, diagnostics=evidence,
            )
    assert refused.value.code == "MODEL_IMMUTABLE"


# -- What three independent audits found the first version could not catch ----------------


@pytest.mark.req("FR-MODEL-18")
async def test_a_version_that_loses_its_standing_before_the_job_runs_is_refused(
    database: Database, blob_store, workspace_id
) -> None:
    """`02` R1, at the moment of the fit rather than the moment of the request.

    Checking it at reservation answers "may this be queued?". `validated → validating →
    failed` are both legal transitions and the analyst who fits can also validate, so a
    version can lose its standing while the Job sits in the queue. Without the second
    check a model reached `fitted` on a `failed` dataset version — proven by an audit,
    not by this suite.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split)
        )
        model_id = row.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor, workspace_id=workspace_id,
        )

    # The version fails a re-validation between the queue and the worker.
    async with database.unit_of_work() as session:
        await dataset_service.transition(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, to_status=DatasetStatus.VALIDATING,
        )
    async with database.unit_of_work() as session:
        await dataset_service.conclude_failed_validation(
            session, workspace_id=workspace_id, actor=actor, version_id=version_id
        )

    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))
    assert model.fit_result is None, "a model must not be fitted on a version that failed"
    assert model.status is ModelStatus.DRAFT


@pytest.mark.req("FR-MODEL-5")
async def test_a_prohibited_factor_is_refused_at_the_attempt(
    database: Database, blob_store, workspace_id
) -> None:
    """FR-MODEL-5, with its own error code, before anything is queued.

    It was enforced inside `pricing-core` at fit time — after a model row, a version
    number, a `spec_hash` slot, an audit event saying `model.reserved` and a queued Job all
    existed. A refusal that arrives as a failed job is a record of the attempt succeeding.
    `FACTOR_PROHIBITED` was a registered code that nothing raised.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )

    async with database.unit_of_work() as session:
        row = await model_service.create_factor(
            session, workspace_id=workspace_id, actor=actor,
            factor=Factor(
                id=uuid4(), slug="postcode", dataset_id=dataset_id, version=1,
                type=FactorType.IDENTITY, source_columns=("area",),
                prohibited=True,
                prohibited_reason="Proxy for a protected characteristic; board decision.",
            ),
        )
        prohibited_id = row.id

    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor,
                spec=_spec(version_id, (prohibited_id,)),
            )
    assert refused.value.code == "FACTOR_PROHIBITED"

    async with database.session() as session:
        rows = (
            await session.execute(select(ModelRow).where(ModelRow.workspace_id == workspace_id))
        ).scalars().all()
    assert rows == [], "no model row, no version number, no spec_hash slot"


@pytest.mark.req("FR-MODEL-2")
async def test_a_factor_from_another_dataset_is_refused(
    database: Database, blob_store, workspace_id
) -> None:
    """FR-MODEL-2 defines a Factor against a **Dataset**.

    Nothing compared the factor's dataset to the version being fitted, so a factor declared
    on dataset A fitted a version of dataset B whenever the column names coincided — which
    in this domain is the norm rather than the exception.
    """
    actor = await _actuary(database, workspace_id)
    ours = await _dataset(database, blob_store, workspace_id, actor)
    theirs = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(database, blob_store, workspace_id, actor, ours)
    foreign = await _factor(database, workspace_id, actor, theirs, "area", "area")

    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor,
                spec=_spec(version_id, (foreign,)),
            )
    assert refused.value.code == "FACTOR_RESOLUTION_FAILED"


@pytest.mark.req("FR-MODEL-66")
async def test_a_reservation_whose_fit_failed_can_be_retried(
    database: Database, blob_store, workspace_id
) -> None:
    """FR-MODEL-66 deduplicates *fitted* models, not reservations.

    A fit that failed — an unreachable blob, a worker that died — left the row behind, and
    every resubmission of the identical spec was told "your model exists" for a model that
    had no numbers and could never get any. The `spec_hash` slot was poisoned for good.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)
    spec = _spec(version_id, (area,), split_ref=split)

    async with database.unit_of_work() as session:
        first, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )
        assert should_fit is True
        first_id = first.id

    # No fit happens. The same spec comes back.
    async with database.unit_of_work() as session:
        again, should_fit_again = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )
    assert again.id == first_id, "still one row — FR-MODEL-66 holds"
    assert should_fit_again is True, "and it still needs a Job, because it has no numbers"


@pytest.mark.req("FR-MODEL-65")
async def test_a_fitted_model_cannot_be_rewritten_in_the_database(
    database: Database, blob_store, workspace_id
) -> None:
    """`02` R2 below the application, where `01`'s artifacts already live.

    An audit rewrote a stored coefficient to zero with a raw `UPDATE`, and deleted a fitted
    model outright — one migration after three other artifact tables were given exactly
    this protection.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,), split_ref=split)
        )
        model_id = row.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor, workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    from sqlalchemy import text
    from sqlalchemy.exc import DBAPIError

    with pytest.raises(DBAPIError) as rewritten:
        async with database.unit_of_work() as session:
            await session.execute(
                text("UPDATE models SET fit_result = '{}'::jsonb WHERE id = :id"),
                {"id": model_id},
            )
    assert "immutable" in str(rewritten.value)

    with pytest.raises(DBAPIError) as deleted:
        async with database.unit_of_work() as session:
            await session.execute(text("DELETE FROM models WHERE id = :id"), {"id": model_id})
    assert "cannot be deleted" in str(deleted.value)

    # ...and the lifecycle stays writable: a fitted model can still change status.
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE models SET status = 'review' WHERE id = :id"), {"id": model_id}
        )
