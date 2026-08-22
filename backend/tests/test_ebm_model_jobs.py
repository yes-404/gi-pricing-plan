"""`model.fit` for an EBM spec, through the same Job the GLM spine uses (`02` §3.5).

The point of this file is the *seam*, not the maths — `packages/pricing-core/tests/
test_ebm.py` proves the fit. What is proven here is everything the platform adds around it:

* one Job kind and one handler fit all three arms of `02` §4.4's union;
* an EBM's fit result IS the model — the exported tables (ADR-0003) — so the fit
  stores no booster and no covariance blob, and the JSONB row alone rescoring it;
* the diagnostics artifact carries no `glm` or `gbm` block and a populated
  `universal` block, which is what makes `Diagnostics.glm`/`gbm` measurements
  rather than declared fields (FR-MODEL-52);
* the monotone-constraint refusal arrives as the named
  `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` through the same handler mapping the GBM
  arm uses (FR-MODEL-23);
* a pair interaction fits through the job and exports its 2-D grid term.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import pytest
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _split,
    _validated_version,
)
from sqlalchemy import func, select

from app.db.models import AuditEventRow, BlobRow, ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.handlers import handler_for
from app.worker.model_handlers import register_model_handlers
from app.worker.progress import JobProgress
from app.worker.tasks import execute_job
from model_schema import (
    FIT_RESULT_ADAPTER,
    MODEL_SPEC_ADAPTER,
    EbmFitResult,
    EbmSpec,
    JobKind,
    JobStatus,
    ModelStatus,
    OffsetSpec,
    new_uuid7,
)

register_data_handlers()
register_model_handlers()


def _ebm_spec(version_id: UUID, factor_ids: tuple[UUID, ...], **over: object) -> EbmSpec:
    base: dict[str, object] = {
        "model_type": "ebm",
        "model_family_slug": f"ebm-{new_uuid7().hex[-6:]}",
        "dataset_version_id": version_id,
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="none"),
        "factors": factor_ids,
        "objective": "rmse",
    }
    base.update(over)
    return EbmSpec(**base)  # type: ignore[arg-type]


async def _fitted_ebm(
    database: Database, blob_store: BlobStore, workspace_id, **over: object
) -> tuple[UUID, JobStatus]:
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
            spec=_ebm_spec(version_id, (area,), split_ref=split, **over),
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

    return model_id, await execute_job(database, job.id, blob_store)


@pytest.mark.req("FR-MODEL-37")
async def test_an_ebm_fits_through_the_same_job_as_a_glm(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """One Job kind, one handler, a third arm of the union.

    The EBM's fit result is the exported tables themselves (ADR-0003): the row's
    `fit_result` validates as an `EbmFitResult` and the spec round-trips as an
    `EbmSpec`, through the same adapters `to_model` applies. R8: the `model.fitted`
    audit event carries the EBM arm's payload — `best_iteration`, `features`,
    `terms`, `intercept` — and no `booster` key, because there is no blob to hash.
    """
    model_id, status = await _fitted_ebm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        row = await session.get(ModelRow, model_id)
        assert row is not None
        fit = FIT_RESULT_ADAPTER.validate_python(row.fit_result)
        spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
        model = model_service.to_model(row)
        events = (
            await session.execute(
                select(AuditEventRow)
                .where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "model.fitted",
                )
                .order_by(AuditEventRow.sequence)
            )
        ).scalars().all()

    assert model.status is ModelStatus.FITTED
    assert isinstance(fit, EbmFitResult)
    assert fit.feature_order == ("area",)
    assert isinstance(spec, EbmSpec)
    assert spec.model_type == "ebm"

    assert len(events) == 1
    after = events[0].after or {}
    assert {"best_iteration", "features", "terms", "intercept"} <= set(after)
    assert "booster" not in after
    assert after["model_type"] == "ebm"


@pytest.mark.req("FR-MODEL-49")
@pytest.mark.req("FR-MODEL-52")
async def test_an_ebm_records_universal_diagnostics_and_no_glm_or_gbm_block(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`02` §4.8 makes diagnostics the condition of `fitted`, and an EBM's are its own.

    `glm is None` and `gbm is None` are asserted rather than assumed: a shared
    diagnostics artifact that quietly carried an empty block would render as a model
    with coefficients or trees it does not have. The `universal` block is the same
    code every arm runs (FR-MODEL-50), and the complexity count is the real bins
    across the exported tables.
    """
    model_id, status = await _fitted_ebm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))
        assert model.diagnostics_id is not None
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )

    assert diagnostics.glm is None
    assert diagnostics.gbm is None
    # FR-MODEL-54: both partitions, always.
    assert diagnostics.universal.train.ae_overall > 0
    assert diagnostics.universal.holdout.ae_overall > 0
    assert diagnostics.complexity.parameter_count >= 1


@pytest.mark.req("FR-MODEL-23")
@pytest.mark.req("FR-MODEL-37")
async def test_an_ebm_with_a_bad_monotone_constraint_fails_the_job_with_the_named_code(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The refusal FR-MODEL-28 demands arrives named, not as a silently-zeroed term.

    `area` is an identity categorical, so a monotone constraint on it has no order
    to hold against — `fit_ebm`'s pre-check refuses it as
    `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` before the estimator exists (`interpret`
    0.7.8 would silently zero the term). `execute_job` maps every handler exception
    to `JOB_HANDLER_FAILED`, so the code is read the way `test_model_jobs_gbm.py`
    reads `METRIC_REF_UNRESOLVED`: the handler run exactly as the runner runs it,
    against a real queued Job, and the code read off the `PlatformError` itself.
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
            spec=_ebm_spec(
                version_id, (area,), split_ref=split, monotone_constraints={"area": 1},
            ),
        )
        model_id = row.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor, workspace_id=workspace_id,
        )

    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED

    handler = handler_for(JobKind.MODEL_FIT)
    assert handler is not None
    progress = JobProgress(
        job.id, database, asyncio.get_running_loop(), blob_store=blob_store
    )
    with pytest.raises(PlatformError) as caught:
        await asyncio.to_thread(
            handler,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            progress,
        )
    assert caught.value.code == "EBM_MONOTONE_CONSTRAINT_INCOMPLETE"


@pytest.mark.req("FR-MODEL-37")
async def test_the_ebm_fit_job_stores_no_blob(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """An EBM has no booster and no covariance — the JSONB row is the whole model.

    `store()` writes a blob only for the arms that produce bytes, so the fit must
    leave the blob store exactly as it found it. The count is taken after the setup
    and after the fit, because MinIO content addressing is stateful: an absence
    assertion has to compare this run's own before/after, not a fixed total.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.session() as session:
        before = (
            await session.execute(select(func.count()).select_from(BlobRow))
        ).scalar_one()

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_ebm_spec(version_id, (area,), split_ref=split),
        )
        model_id = row.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor, workspace_id=workspace_id,
        )

    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        after = (
            await session.execute(select(func.count()).select_from(BlobRow))
        ).scalar_one()
    assert after == before


@pytest.mark.req("FR-MODEL-37")
async def test_an_ebm_with_interactions_fits_through_the_job(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`interactions=1` on two factors exports its pair term through the same Job.

    The interaction grid is part of the JSONB fit result (FR-MODEL-37), so a pair
    interaction is a second fit through the same job rather than a different
    artifact. `max_bins=64` keeps the grid small; the pair term is the one whose
    `term_features` has length 2. The setup is inlined because `_fitted_ebm` fits
    one factor — a pair needs both factors created against this dataset (FR-MODEL-2).
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    amount = await _factor(
        database, workspace_id, actor, dataset_id, "claim_amount_minor",
        "claim_amount_minor",
    )
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_ebm_spec(
                version_id, (area, amount), split_ref=split,
                interactions=1, max_bins=64,
            ),
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
    assert model.fit_result is not None
    assert isinstance(model.fit_result, EbmFitResult)
    pair_terms = [t for t in model.fit_result.terms if len(t.term_features) == 2]
    assert len(pair_terms) == 1
