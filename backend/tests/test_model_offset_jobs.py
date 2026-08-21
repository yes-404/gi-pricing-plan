"""FR-MODEL-24 end to end: a base GLM fit, then a residual fit offset against it — and
the named refusals. The Job is the gate: resolution happens at fit time, on the worker.

The seeding helpers are `test_model_jobs.py`'s: a version reaches `validated` through
the real ingestion/validation jobs, the split is derived through the real derive jobs,
and the fit under test runs through `execute_job` — what is exercised is the handler a
worker would run and not a service call underneath it.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import numpy as np
import pytest
from backend.tests.test_data_jobs import _validate
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _split,
    _validated_version,
)
from sqlalchemy import select

from app.db.models import DatasetVersionRow, ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.handlers import handler_for
from app.worker.model_handlers import register_model_handlers
from app.worker.progress import JobProgress
from app.worker.tasks import execute_job
from model_schema import (
    GlmSpec,
    JobKind,
    JobStatus,
    ModelStatus,
    OffsetSpec,
    SplitRef,
    new_uuid7,
)

# Both, and in this order — the model spine is fitted on versions this test ingests and
# validates through the `dataset.*` handlers, so a module that registered only its own
# would fail on the setup rather than the subject.
register_data_handlers()
register_model_handlers()

#: `read_tabular` reads every column as a string (FR-DATA-4 — inference is the confirmed
#: schema's job, not the reader's), so the residual book's two new columns need their own
#: casts: `resid_flag` must be a float for the IDENTITY factor to be continuous, and
#: `claim_count2` must be a count for the Poisson response.
_RESIDUAL_CAST_RECIPE = [
    {
        "step": "cast",
        "table": "policy_exposure",
        "params": {
            "columns": {
                "exposure_years": "float",
                "claim_count": "int",
                "claim_amount_minor": "int",
                "resid_flag": "float",
                "claim_count2": "int",
            }
        },
    }
]


def _residual_book(n: int = 4_000, seed: int = 20260821) -> bytes:
    """v2 of the book: v1's columns plus a residual signal and its own response.

    `claim_count2 ~ Poisson(exp(eta_base + 0.2·resid_flag))`, with
    `eta_base = log(exposure) - 2.0 + 0.5·[area == urban]` — the same truth the base
    model is fitted to, so the residual fit on top of the base model's linear predictor
    must recover the `resid_flag` effect on its own.
    """
    rng = np.random.default_rng(seed)
    exposure = rng.uniform(0.25, 1.0, n)
    urban = rng.integers(0, 2, n)
    z = rng.integers(0, 2, n)
    eta_base = np.log(exposure) - 2.0 + 0.5 * urban
    base_counts = rng.poisson(np.exp(eta_base))
    resid_counts = rng.poisson(np.exp(eta_base + 0.2 * z))
    header = (
        b"policy_id,exposure_years,area,resid_flag,claim_count,claim_count2,"
        b"claim_amount_minor\n"
    )
    return header + b"".join(
        f"P{i},{e:.6f},{'urban' if u else 'rural'},{float(z)},{base},{resid},100000\n"
        .encode()
        for i, (e, u, z, base, resid) in enumerate(
            zip(exposure, urban, z, base_counts, resid_counts, strict=True), start=1
        )
    )


def _residual_spec(
    version_id,
    resid_factor_id,
    split: SplitRef,
    *,
    ref: str,
    link: str = "log",
    model_family_slug: str | None = None,
) -> GlmSpec:
    """The residual model: v2's response, offset from the referenced fitted model."""
    return GlmSpec(
        model_family_slug=model_family_slug or f"resid-{new_uuid7().hex[-6:]}",
        dataset_version_id=version_id,
        response_column="claim_count2",
        offset=OffsetSpec(kind="model", offset_model_ref=ref),
        factors=[resid_factor_id],
        split_ref=split,
        family="poisson",
        link=link,
        seed=0,
    )


async def _residual_ingest(
    database: Database, blob_store: BlobStore, workspace_id, actor,
    dataset_id,
) -> UUID:
    """`test_data_jobs._ingest` with the residual book's cast recipe: without the casts
    `resid_flag` stays a String column and the factor is categorical — which is a
    different model than the slice specifies."""
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, _residual_book(), "text/csv")
        job = await job_service.submit(
            session,
            JobKind.DATASET_INGEST,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "dataset_id": str(dataset_id),
                "blob": ref.sha256,
                "filename": "exposure.csv",
                "recipe": _RESIDUAL_CAST_RECIPE,
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        row = (
            await session.execute(
                select(DatasetVersionRow)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc())
                .limit(1)
            )
        ).scalar_one()
        return row.id


async def _residual_version(
    database: Database, blob_store: BlobStore, workspace_id, actor, dataset_id,
) -> UUID:
    """`test_model_jobs._validated_version` for the residual book: ingest through the
    real Job with the residual cast recipe, validate, promote."""
    version_id = await _residual_ingest(
        database, blob_store, workspace_id, actor, dataset_id
    )
    report_id = await _validate(database, blob_store, workspace_id, actor, version_id)
    from app.platform import validation as validation_service

    async with database.unit_of_work() as session:
        await validation_service.promote_using_report(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, report_id=report_id,
        )
    return version_id


async def _residual_row(
    database: Database,
    blob_store: BlobStore,
    workspace_id,
    actor,
    spec: GlmSpec,
) -> tuple[object, object]:
    """Reserve the residual model and queue its fit; returns (model_id, job)."""
    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec,
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
    return model_id, job


async def _refusal_code(
    database: Database, blob_store: BlobStore, workspace_id, actor, model_id, job_id
) -> str:
    """The code of the refusal the fit handler raises.

    `execute_job` maps every handler exception to `JOB_HANDLER_FAILED` — the code under
    test is what `PlatformError.code` carries out of the handler, so it is read the way
    `test_model_jobs_gbm.py` reads `METRIC_REF_UNRESOLVED`: the handler run exactly as
    the runner runs it, against a real queued Job, and the code read off the
    `PlatformError` itself.
    """
    handler = handler_for(JobKind.MODEL_FIT)
    assert handler is not None
    progress = JobProgress(
        job_id, database, asyncio.get_running_loop(), blob_store=blob_store
    )
    with pytest.raises(PlatformError) as caught:
        await asyncio.to_thread(
            handler,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id), "job_id": str(job_id)},
            progress,
        )
    return caught.value.code


@pytest.mark.req("FR-MODEL-24")
async def test_a_residual_fit_offsets_against_the_referenced_model(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The spine of the slice: base fit first, residual fit on top of its linear
    predictor, the pinned ref recorded on the result, and the residual signal recovered
    as the `resid_flag` coefficient."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        base, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_base_spec(version_id, area, split),
        )
        assert should_fit is True
        base_id = base.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(base_id)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    # v2 of the book: the residual signal and the response that lives on top of the
    # base truth.
    dataset2_id = await _dataset(database, blob_store, workspace_id, actor)
    v2_id = await _residual_version(database, blob_store, workspace_id, actor, dataset2_id)
    resid_flag = await _factor(
        database, workspace_id, actor, dataset2_id, "resid_flag", "resid_flag"
    )
    split2 = await _split(database, blob_store, workspace_id, actor, v2_id)

    async with database.session() as session:
        base_row = await session.get(ModelRow, base_id)
    assert base_row is not None
    ref = f"model:{base_row.model_family_slug}@{base_row.version}"

    residual_id, job = await _residual_row(
        database, blob_store, workspace_id, actor,
        _residual_spec(v2_id, resid_flag, split2, ref=ref),
    )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, residual_id))
    assert model.status is ModelStatus.FITTED
    assert model.fit_result is not None
    assert model.fit_result.offset_model_ref == ref
    resid = next(c for c in model.fit_result.coefficients if c.term == "resid_flag")
    assert resid.estimate == pytest.approx(0.2, rel=0.1)


def _base_spec(version_id, area, split: SplitRef) -> GlmSpec:
    """The base GLM `test_model_jobs.py`'s spine fits: Poisson, log link, exposure
    offset, factor `area`."""
    from backend.tests.test_model_jobs import _spec

    return _spec(version_id, (area,), split_ref=split)


@pytest.mark.req("FR-MODEL-24")
async def test_a_ref_naming_no_model_fails_the_job(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`model:ghost@1` resolves to nothing: the fit job fails named, `NOT_FOUND`."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _residual_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    resid_flag = await _factor(
        database, workspace_id, actor, dataset_id, "resid_flag", "resid_flag"
    )
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    model_id, job = await _residual_row(
        database, blob_store, workspace_id, actor,
        _residual_spec(version_id, resid_flag, split, ref="model:ghost@1"),
    )
    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED

    code = await _refusal_code(database, blob_store, workspace_id, actor, model_id, job.id)
    assert code == "NOT_FOUND"


@pytest.mark.req("FR-MODEL-24")
async def test_a_ref_naming_an_unfitted_model_fails_the_job(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """A reserved-but-never-fitted model has no linear predictor to offset against:
    refused by name (`MODEL_OFFSET_REF_INVALID`), not fitted as though no offset were
    declared."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _residual_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    resid_flag = await _factor(
        database, workspace_id, actor, dataset_id, "resid_flag", "resid_flag"
    )
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    # A second model in its own family, reserved and never fitted.
    async with database.unit_of_work() as session:
        unfitted, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_base_spec(version_id, resid_flag, split),
        )
        unfitted_ref = f"model:{unfitted.model_family_slug}@{unfitted.version}"

    model_id, job = await _residual_row(
        database, blob_store, workspace_id, actor,
        _residual_spec(version_id, resid_flag, split, ref=unfitted_ref),
    )
    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED

    code = await _refusal_code(database, blob_store, workspace_id, actor, model_id, job.id)
    assert code == "MODEL_OFFSET_REF_INVALID"


@pytest.mark.req("FR-MODEL-24")
async def test_a_link_mismatch_fails_the_job(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The offset would be a number from another scale: the referenced model's link must
    equal the new spec's, refused by name (`MODEL_OFFSET_REF_INVALID`)."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    split = await _split(database, blob_store, workspace_id, actor, version_id)

    async with database.unit_of_work() as session:
        base, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_base_spec(version_id, area, split),
        )
        assert should_fit is True
        base_id = base.id
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(base_id)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        base_row = await session.get(ModelRow, base_id)
    assert base_row is not None
    ref = f"model:{base_row.model_family_slug}@{base_row.version}"

    dataset2_id = await _dataset(database, blob_store, workspace_id, actor)
    v2_id = await _residual_version(database, blob_store, workspace_id, actor, dataset2_id)
    resid_flag = await _factor(
        database, workspace_id, actor, dataset2_id, "resid_flag", "resid_flag"
    )
    split2 = await _split(database, blob_store, workspace_id, actor, v2_id)

    model_id, job = await _residual_row(
        database, blob_store, workspace_id, actor,
        _residual_spec(v2_id, resid_flag, split2, ref=ref, link="identity"),
    )
    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED

    code = await _refusal_code(database, blob_store, workspace_id, actor, model_id, job.id)
    assert code == "MODEL_OFFSET_REF_INVALID"
