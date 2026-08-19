"""FR-MODEL-96 — the GLM approximation of a GBM, persisted as a Model.

The artifact used to carry the table inline, which made it the only thing that could ever
rate on the approximation — and a `TransparencyArtifact` has no status, so FR-OVR-14's pin
could never resolve to one (`03` FR-RATE-60). These tests are about the Model that fixes
that: it exists, it is fitted, its diagnostics are against the booster's predictions rather
than against observed claims, and rebuilding the artifact does not fit it a second time.
"""

from __future__ import annotations

from uuid import UUID

import pytest
from backend.tests.test_model_jobs import _actuary
from backend.tests.test_model_jobs_gbm import _fitted_gbm

from app.db.session import Database
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import transparency as transparency_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    MODEL_SPEC_ADAPTER,
    SURROGATE_RESPONSE_COLUMN,
    JobKind,
    JobStatus,
    ModelStatus,
    Principal,
    TransparencyArtifact,
)

register_data_handlers()
register_model_handlers()


async def _transparency_job(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    model_id: UUID,
    actor: Principal,
) -> TransparencyArtifact:
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.MODEL_TRANSPARENCY,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id), "sample": 2_000},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        return await transparency_service.load_transparency(
            session, workspace_id=workspace_id, model_id=model_id
        )


@pytest.mark.req("FR-MODEL-96")
async def test_the_artifact_names_a_fitted_model_that_holds_the_table(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED
    actor = await _actuary(database, workspace_id)

    artifact = await _transparency_job(database, blob_store, workspace_id, model_id, actor)

    assert artifact.glm_approximation is not None
    surrogate_id = artifact.glm_approximation.approximating_model_id
    assert surrogate_id is not None
    # The table moved; it did not get copied.
    assert artifact.glm_approximation.coefficients == ()

    async with database.session() as session:
        surrogate = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=surrogate_id
        )
    assert surrogate.status == ModelStatus.FITTED.value
    assert surrogate.diagnostics_id is not None
    spec = MODEL_SPEC_ADAPTER.validate_python(surrogate.spec)
    assert spec.approximates_model_id == model_id
    assert spec.response_column == SURROGATE_RESPONSE_COLUMN
    assert surrogate.fit_result is not None
    assert surrogate.fit_result["coefficients"]


@pytest.mark.req("FR-MODEL-102")
async def test_the_surrogate_carries_no_covariance_blob(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """An interval from a surrogate's coefficients describes the surrogate, and would be
    read as the GBM's uncertainty — which FR-MODEL-77 refuses by name."""
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    artifact = await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    assert artifact.glm_approximation is not None
    surrogate_id = artifact.glm_approximation.approximating_model_id
    assert surrogate_id is not None

    async with database.session() as session:
        surrogate = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=surrogate_id
        )
    assert surrogate.fit_result is not None
    assert surrogate.fit_result["covariance_blob"] is None


@pytest.mark.req("FR-MODEL-96")
async def test_rebuilding_the_artifact_reuses_the_surrogate_rather_than_refitting_it(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """FR-MODEL-66: the specification is the same, so the model is the same one.

    Without this the second build raises `MODEL_IMMUTABLE` against a model it just found,
    and the Job fails on its own success.
    """
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)

    first = await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    second = await _transparency_job(database, blob_store, workspace_id, model_id, actor)

    assert second.id != first.id, "each build appends an artifact (FR-MODEL-33)"
    assert first.glm_approximation is not None
    assert second.glm_approximation is not None
    assert (second.glm_approximation.approximating_model_id
            == first.glm_approximation.approximating_model_id)


@pytest.mark.req("FR-MODEL-96")
async def test_the_surrogates_diagnostics_measure_it_against_the_booster(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """FR-MODEL-96(iii). The A/E is the surrogate against the source model's predictions —
    so it is close to 1 by construction on a well-fitting approximation, and the *spec* is
    what says which target that is (FR-MODEL-102)."""
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    artifact = await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    assert artifact.glm_approximation is not None
    surrogate_id = artifact.glm_approximation.approximating_model_id
    assert surrogate_id is not None

    async with database.session() as session:
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=surrogate_id
        )
    assert diagnostics.universal.train.rows > 0
    assert diagnostics.universal.holdout.rows > 0
    # The two partitions are two populations. Without this nothing distinguishes the
    # holdout from a second pass over train, and FR-MODEL-54's obligation would be met by
    # a handler that reported the train frame twice — which is exactly what the Step 8
    # enforcement check found nothing else here refuses.
    assert diagnostics.universal.holdout.rows != diagnostics.universal.train.rows
    assert diagnostics.glm is not None
    assert 0.5 < diagnostics.universal.train.ae_overall < 1.5
