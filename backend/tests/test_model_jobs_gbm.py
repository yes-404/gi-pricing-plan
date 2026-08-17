"""`model.fit` for a GBM spec, through the same Job the GLM spine uses (`02` §3.5).

The point of this file is the *seam*, not the maths — `packages/pricing-core/tests/
test_gbm.py` proves the fit. What is proven here is everything the platform adds around it:

* one Job kind and one handler fit either arm of `02` §4.4's union;
* the booster is stored as a blob **in the transaction that writes the model row**, so a
  committed model never references an object nobody wrote;
* the diagnostics artifact carries the `gbm` block and no `glm` block, which is what makes
  `Diagnostics.gbm` a measurement rather than a declared field (FR-MODEL-52);
* `POST /model-specs/validate` refuses an unfittable objective **before** a Job exists
  (FR-MODEL-44), which is the half of that requirement nothing built until now.
"""

from __future__ import annotations

from uuid import UUID

import pytest
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _split,
    _validated_version,
)

from app.db.models import BlobRow, ModelRow
from app.db.session import Database
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import model_specs as spec_service
from app.platform import modelling as model_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    EarlyStopping,
    GbmFunctionRef,
    GbmSpec,
    JobKind,
    JobStatus,
    ModelStatus,
    OffsetSpec,
    SpecProblemKind,
    new_uuid7,
)

register_data_handlers()
register_model_handlers()


def _gbm_spec(version_id: UUID, factor_ids: tuple[UUID, ...], **over: object) -> GbmSpec:
    base: dict[str, object] = {
        "model_type": "xgboost",
        "model_family_slug": f"gbm-{new_uuid7().hex[-6:]}",
        "dataset_version_id": version_id,
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "factors": factor_ids,
        "objective": GbmFunctionRef(kind="builtin", name="count:poisson"),
        "categorical_handling": "native",
        "hyperparameters": {"max_depth": 3, "eta": 0.2, "num_boost_round": 30},
    }
    base.update(over)
    return GbmSpec(**base)  # type: ignore[arg-type]


async def _fitted_gbm(
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
            spec=_gbm_spec(version_id, (area,), split_ref=split, **over),
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


@pytest.mark.req("FR-MODEL-25")
async def test_a_gbm_fits_through_the_same_job_as_a_glm(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """One Job kind, one handler, either arm of the union.

    A second `model.gbm_fit` kind would have been the easy move and the wrong one: every
    caller, every status screen and every audit query would then have had to know which of
    two names to look for, and `02` §5.1 declares one `POST /models`.
    """
    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))

    assert model.status is ModelStatus.FITTED
    assert model.fit_result is not None
    assert model.fit_result.model_type == "xgboost"
    assert model.spec.model_type == "xgboost"
    assert model.fit_result.feature_order == ("area",)


@pytest.mark.req("FR-MODEL-31")
async def test_the_booster_is_stored_under_the_digest_the_fit_computed(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-31: content-addressed, and **written in the model's own transaction**.

    `pricing-core` computes the reference and cannot store the payload (ADR-0001), so the
    one failure this has to exclude is a committed model whose `booster_blob` points at an
    object nobody wrote. Reading the bytes back through the store is what proves it.
    """
    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))
        assert model.fit_result is not None
        ref = model.fit_result.booster_blob
        assert await session.get(BlobRow, ref.sha256) is not None

    payload = await blob_store.read(ref)
    assert len(payload) == ref.bytes_
    # The backend's own format, readable as itself — ADR-0003's refusal of a pickle is not
    # a convention here, it is what the bytes are.
    assert payload.lstrip().startswith(b"{")


@pytest.mark.req("FR-MODEL-52")
async def test_a_gbm_records_gbm_diagnostics_and_no_glm_block(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`02` §4.8 makes diagnostics the condition of `fitted`, so a GBM that reached
    `fitted` has them — and they are the GBM's own.

    `glm is None` is asserted rather than assumed: a shared diagnostics artifact that
    quietly carried an empty GLM block would render as a model with no coefficients rather
    than as a model that has none.
    """
    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))
        assert model.diagnostics_id is not None
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )

    assert diagnostics.glm is None
    assert diagnostics.gbm is not None
    assert diagnostics.gbm.tree_count == 30
    assert diagnostics.gbm.importances
    assert diagnostics.gbm.permutation_importances
    # FR-MODEL-54: both partitions, always.
    assert diagnostics.universal.train.ae_overall > 0
    assert diagnostics.universal.holdout.ae_overall > 0


@pytest.mark.req("FR-MODEL-44")
async def test_an_unsupported_objective_is_a_spec_problem_not_a_failed_job(
    database: Database, blob_store: BlobStore, workspace_id, settings
) -> None:
    """FR-MODEL-44's *objective applicability* half, which nothing built until this slice.

    `wf-01` D2: the caller learns before any compute is spent. The alternative is a 202, a
    queued Job, and a failure three minutes later saying the same thing — which is also
    what `02` §5.3's live validation would render on every keystroke.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")

    async with database.unit_of_work() as session:
        validation = await spec_service.validate_spec(
            session, settings, workspace_id=workspace_id, actor=actor,
            spec=_gbm_spec(
                version_id, (area,),
                objective=GbmFunctionRef(kind="builtin", name="rank:pairwise"),
            ),
        )

    assert validation.ok is False
    problem = next(
        p for p in validation.problems if p.kind is SpecProblemKind.OBJECTIVE_UNSUPPORTED
    )
    assert problem.subject == "rank:pairwise"


@pytest.mark.req("FR-MODEL-44")
async def test_a_custom_objective_is_refused_before_a_job_exists(
    database: Database, blob_store: BlobStore, workspace_id, settings
) -> None:
    """`02` R4 makes an unapproved Custom Objective unusable, and FR-MODEL-38 has not been
    built at all — so the spec is unfittable for two reasons and says so once."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")

    async with database.unit_of_work() as session:
        validation = await spec_service.validate_spec(
            session, settings, workspace_id=workspace_id, actor=actor,
            spec=_gbm_spec(
                version_id, (area,),
                objective=GbmFunctionRef(
                    kind="custom", ref="custom_objective:capped-gamma@2"
                ),
            ),
        )

    assert validation.ok is False
    assert any(
        p.kind is SpecProblemKind.OBJECTIVE_UNSUPPORTED for p in validation.problems
    )


@pytest.mark.req("FR-MODEL-30")
async def test_early_stopping_uses_the_split_the_spec_declares(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-30 end to end: the worker passes the holdout frame it derived from
    `split_ref`, so the stopping metric is read off rows the model was not fitted on.

    Without the holdout argument `fit_gbm` refuses, so a green result here is the evidence
    that the platform supplied it rather than that the requirement was skipped.
    """
    model_id, status = await _fitted_gbm(
        database, blob_store, workspace_id,
        early_stopping=EarlyStopping(on="holdout", metric="poisson-nloglik", rounds=5),
    )
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )

    # The curve is a **diagnostic** (FR-MODEL-52), not part of the fit artifact, and it
    # carries both partitions (FR-MODEL-54).
    assert diagnostics.gbm is not None
    assert diagnostics.gbm.eval_curve
    assert all(p.holdout is not None for p in diagnostics.gbm.eval_curve)
    assert all(p.train is not None for p in diagnostics.gbm.eval_curve)
