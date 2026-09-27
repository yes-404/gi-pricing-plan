"""The diagnostics artifact, and the invariant it makes meetable (`02` §4.8, FR-170).

The spine enforced `fitted ⟹ fit_result` and left `status ≥ fitted ⟹ diagnostics_id`
unstated, because diagnostics did not exist to point at. These prove the second half now
holds at each of the three layers that can be reached independently: the type, the
database, and the fit path.
"""

from __future__ import annotations

from uuid import uuid4

import pydantic
import pytest
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _spec,
    _split,
    _validated_version,
)
from sqlalchemy import text

from app.db.models import ModelRow
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.worker.tasks import execute_job
from model_schema import (
    GlmFitResult,
    GlmSpec,
    JobKind,
    JobStatus,
    Model,
    ModelStatus,
    OffsetSpec,
    PartitionDiagnostics,
    UniversalDiagnostics,
    Weighting,
)


def _partition(weighting: Weighting = Weighting.EXPOSURE) -> PartitionDiagnostics:
    return PartitionDiagnostics(
        weighting=weighting, rows=100, ae_overall=1.0, gini=0.2, gini_normalised=0.3
    )


# -- The type -----------------------------------------------------------------------------


@pytest.mark.req("FR-183")
def test_a_diagnostic_cannot_be_built_without_its_holdout() -> None:
    """FR-183 calls a one-sided diagnostic a defect. The cheapest way to honour that
    is to make the defective shape unrepresentable — so this is a `TypeError`-class failure
    at construction, not a check somebody has to remember downstream."""
    with pytest.raises(pydantic.ValidationError):
        UniversalDiagnostics(train=_partition())  # type: ignore[call-arg]


@pytest.mark.req("FR-184")
def test_train_and_holdout_must_share_a_weighting_scheme() -> None:
    """Negative: an exposure-weighted train A/E beside an unweighted holdout A/E are two
    different quantities, and side by side is exactly where a reader assumes they are
    comparable."""
    with pytest.raises(pydantic.ValidationError, match="weighting"):
        UniversalDiagnostics(
            train=_partition(Weighting.EXPOSURE), holdout=_partition(Weighting.COUNT)
        )


@pytest.mark.req("FR-170")
def test_a_model_beyond_draft_without_diagnostics_is_refused_at_the_type() -> None:
    """`02` §4.8's invariant. A model at `review` with no diagnostics is an approval
    request with no evidence in it."""
    spec = GlmSpec(
        model_family_slug="f",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
    )
    fit = GlmFitResult(converged=True, iterations=3, fit_seconds=0.1, dispersion=1.0)
    common = dict(
        id=uuid4(), model_family_slug="f", version=1, spec=spec,
        spec_hash="v2:sha256:x", fit_result=fit, dataset_version_id=uuid4(),
    )

    with pytest.raises(pydantic.ValidationError, match="no diagnostics"):
        Model(status=ModelStatus.FITTED, **common)  # type: ignore[arg-type]

    # And the positive, so the test cannot pass by refusing everything.
    assert Model(status=ModelStatus.FITTED, diagnostics_id=uuid4(), **common).status is (  # type: ignore[arg-type]
        ModelStatus.FITTED
    )
    assert Model(status=ModelStatus.DRAFT, **{**common, "fit_result": None}).status is (  # type: ignore[arg-type]
        ModelStatus.DRAFT
    )


# -- The database -------------------------------------------------------------------------


@pytest.mark.req("FR-170")
async def test_the_database_refuses_a_fitted_model_with_no_diagnostics(
    database, workspace_id
) -> None:
    """The layer that survives a direct `UPDATE`. The type can be bypassed by anything
    writing SQL; the CHECK cannot."""
    async with database.unit_of_work() as session:
        with pytest.raises(Exception, match="fitted_model_has_diagnostics"):
            await session.execute(
                text(
                    "INSERT INTO models (id, workspace_id, model_family_slug, version, "
                    "status, dataset_version_id, spec, spec_hash, fit_result) VALUES "
                    "(gen_random_uuid(), :ws, 'direct', 1, 'fitted', gen_random_uuid(), "
                    "'{}'::jsonb, 'v2:sha256:direct', '{}'::jsonb)"
                ),
                {"ws": workspace_id},
            )


@pytest.mark.req("FR-43")
async def test_diagnostics_cannot_be_rewritten(database, workspace_id) -> None:
    """Artifact discipline: computed once at fit time and read thereafter (FR-170).
    A diagnostics row that could be updated would let the evidence behind an approval
    change after the approval."""
    async with database.session() as session:
        granted = (
            await session.execute(
                text(
                    "SELECT privilege_type FROM information_schema.table_privileges "
                    "WHERE table_name = 'diagnostics' AND grantee = 'gip_app'"
                )
            )
        ).scalars().all()
    assert "INSERT" in granted
    assert "SELECT" in granted
    assert "UPDATE" not in granted
    assert "DELETE" not in granted


# -- The fit path -------------------------------------------------------------------------


async def _fit(database, blob_store, workspace_id):
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
            spec=_spec(version_id, (area,), split_ref=split),
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
    return actor, model_id


@pytest.mark.req("FR-170")
async def test_a_fit_produces_and_stores_its_diagnostics(
    database, blob_store, workspace_id
) -> None:
    """FR-170: **every** fit produces a persisted Diagnostics artifact — not an
    optional extra a caller may request afterwards."""
    _, model_id = await _fit(database, blob_store, workspace_id)

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))
        stored = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )

    assert model.status is ModelStatus.FITTED
    assert model.diagnostics_id == stored.id
    assert stored.universal.train.rows > 0
    assert stored.universal.holdout.rows > 0
    # The fixture book is deterministic — urban rows always carry two claims on unit
    # exposure, rural always one — so a correct fit reproduces it exactly and the
    # deviance is 0 rather than merely small. Asserting `> 0` would fail on a *better*
    # fit, which is the wrong way round for a quality metric.
    assert stored.glm is not None
    assert stored.glm.deviance == pytest.approx(0.0, abs=1e-9)
    assert stored.glm.null_deviance > stored.glm.deviance
    assert stored.complexity.factor_count == 1


@pytest.mark.req("FR-183")
async def test_the_holdout_is_not_the_training_set(
    database, blob_store, workspace_id
) -> None:
    """The defect that made this slice necessary. `dataset.derive` used to hand a derived
    version its parent's blob, so a "holdout" contained every training row and the model's
    performance on it was its memory.

    Asserting the row counts differ is what a fake split could not satisfy."""
    _, model_id = await _fit(database, blob_store, workspace_id)

    async with database.session() as session:
        stored = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )

    train, holdout = stored.universal.train.rows, stored.universal.holdout.rows
    assert holdout < train, "the holdout is the smaller part of a 75/25 split"
    assert train + holdout == 400, "the parts partition the book, losing and sharing nothing"


@pytest.mark.req("FR-183")
async def test_a_spec_with_no_split_cannot_be_fitted(
    database, blob_store, workspace_id
) -> None:
    """Negative: without a split there is no holdout, so there are no diagnostics, so the
    model cannot reach `fitted`. Refused before the fit rather than after three minutes of
    compute that cannot be recorded."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")

    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (area,)),
        )
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(row.id)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED

    async with database.session() as session:
        stored = await session.get(ModelRow, row.id)
        assert stored is not None
        assert stored.status == ModelStatus.DRAFT.value
        assert stored.diagnostics_id is None
