"""FR-137 — the GLM approximation of a GBM, persisted as a Model.

The artifact used to carry the table inline, which made it the only thing that could ever
rate on the approximation — and a `TransparencyArtifact` has no status, so FR-20's pin
could never resolve to one (`03` FR-223). These tests are about the Model that fixes
that: it exists, it is fitted, its diagnostics are against the booster's predictions rather
than against observed claims, and rebuilding the artifact does not fit it a second time.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID

import pytest
from backend.tests.test_model_jobs import _actuary, _dataset, _validated_version
from backend.tests.test_model_jobs_gbm import _fitted_gbm
from backend.tests.test_prediction import _fitted_glm
from sqlalchemy import func, select

import pricing_core.modelling as pricing_modelling
from app.db.models import AuditEventRow, ModelRow, TransparencyArtifactRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import transparency as transparency_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.handlers import handler_for
from app.worker.model_handlers import register_model_handlers
from app.worker.progress import JobProgress
from app.worker.tasks import execute_job
from model_schema import (
    FIT_RESULT_ADAPTER,
    MODEL_SPEC_ADAPTER,
    SURROGATE_RESPONSE_COLUMN,
    ApproximatedModel,
    GbmSpec,
    JobKind,
    JobStatus,
    ModelStatus,
    Principal,
    TransparencyArtifact,
    TransparencyKind,
    new_uuid7,
)
from pricing_core.modelling import approximation_spec

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


async def _transparency_refusal(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    model_id: UUID,
    actor: Principal,
) -> PlatformError:
    """The refusal `_transparency` raises, caught where the runner would swallow its code.

    `execute_job` turns any handler exception into a `JOB_HANDLER_FAILED` job error, so a
    test that goes through it can see the message and never the code — and `00` §5.3 makes
    the *code* the contract. This runs the handler exactly as the runner does,
    `asyncio.to_thread(handler, parameters, progress)` against a real queued Job, and reads
    the code off the `PlatformError` itself.
    """
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.MODEL_TRANSPARENCY,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id), "sample": 2_000},
            actor,
            workspace_id=workspace_id,
        )
    handler = handler_for(JobKind.MODEL_TRANSPARENCY)
    assert handler is not None
    progress = JobProgress(
        job.id, database, asyncio.get_running_loop(), blob_store=blob_store
    )
    with pytest.raises(PlatformError) as caught:
        await asyncio.to_thread(
            handler,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id), "sample": 2_000, "job_id": str(job.id)},
            progress,
        )
    return caught.value


async def _fitted_gbm_without_a_split(
    database: Database, blob_store: BlobStore, workspace_id: UUID, actor: Principal
) -> UUID:
    """A fitted GBM whose spec declares no split — a state `model.fit` cannot produce.

    The fit handler refuses `split_ref is None` with the same code this Job does, so the
    state has to be built deliberately. It is built through the two platform services the
    fit handler itself calls — `reserve_model` and `record_fit` — and **not** by writing a
    `ModelRow` directly, so every invariant those two enforce still had to hold for this
    row: the dataset version is still `validated`, the factors still resolve, the model
    still reaches `fitted` carrying both a fit result and diagnostics. Only the one
    condition under test is absent.

    The numbers are a real fit's, borrowed from a GBM that does have a split. Nothing here
    reads them; what is under test is the refusal that happens before they are ever loaded.
    """
    source_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        source = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=source_id
        )
        spec = MODEL_SPEC_ADAPTER.validate_python(source.spec)
        result = FIT_RESULT_ADAPTER.validate_python(source.fit_result)
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=source_id
        )
    assert isinstance(spec, GbmSpec)

    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=actor,
            spec=spec.model_copy(
                update={
                    "split_ref": None,
                    "model_family_slug": f"nosplit-{new_uuid7().hex[-6:]}",
                }
            ),
        )
        assert should_fit is True
        model_id = row.id
        await model_service.record_fit(
            session,
            workspace_id=workspace_id,
            actor=actor,
            model_id=model_id,
            fit_result=result,
            diagnostics=diagnostics.model_copy(
                update={"id": new_uuid7(), "model_id": model_id}
            ),
        )
    return model_id


@pytest.mark.req("FR-137")
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
        source_row = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=model_id
        )
        surrogate = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=surrogate_id
        )
    assert surrogate.status == ModelStatus.FITTED.value
    assert surrogate.diagnostics_id is not None
    spec = MODEL_SPEC_ADAPTER.validate_python(surrogate.spec)
    assert spec.approximates_model_id == model_id
    # FR-169: the companion names the same model in the register a human reads.
    assert spec.approximates_model is not None
    assert spec.approximates_model.model_slug == source_row.model_family_slug
    assert spec.approximates_model.model_version == source_row.version
    assert spec.response_column == SURROGATE_RESPONSE_COLUMN
    assert surrogate.fit_result is not None
    assert surrogate.fit_result["coefficients"]


@pytest.mark.req("FR-141")
async def test_the_surrogate_carries_no_covariance_blob(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """An interval from a surrogate's coefficients describes the surrogate, and would be
    read as the GBM's uncertainty — which FR-198 refuses by name."""
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


@pytest.mark.req("FR-138")
@pytest.mark.req("FR-137")
async def test_rebuilding_the_artifact_reuses_the_surrogate_rather_than_refitting_it(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """FR-204: the specification is the same, so the model is the same one.

    Without this the second build raises `MODEL_IMMUTABLE` against a model it just found,
    and the Job fails on its own success.
    """
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)

    first = await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    second = await _transparency_job(database, blob_store, workspace_id, model_id, actor)

    assert second.id != first.id, "each build appends an artifact (FR-132)"
    assert first.glm_approximation is not None
    assert second.glm_approximation is not None
    assert (second.glm_approximation.approximating_model_id
            == first.glm_approximation.approximating_model_id)


@pytest.mark.req("FR-137")
async def test_the_surrogates_diagnostics_measure_it_against_the_booster(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """FR-137(iii). The A/E is the surrogate against the source model's predictions —
    so it is close to 1 by construction on a well-fitting approximation, and the *spec* is
    what says which target that is (FR-141)."""
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    artifact = await _transparency_job(database, blob_store, workspace_id, model_id, actor)
    assert artifact.glm_approximation is not None
    surrogate_id = artifact.glm_approximation.approximating_model_id
    assert surrogate_id is not None

    async with database.session() as session:
        surrogate = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=surrogate_id
        )
        gbm = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )
    assert surrogate.universal.train.rows > 0
    assert surrogate.universal.holdout.rows > 0
    # **The surrogate's holdout is the source model's holdout.** Both are computed over the
    # partitions of the one split the two specs share, so this pins the semantics rather
    # than a number: without it a handler that passed the train frame as both partitions
    # would satisfy FR-183 by reporting the same population twice, and nothing here
    # would say so. Compared against the GBM's own diagnostics and not against a row count
    # of its own, because a count only differs by the accident of a split that does not
    # divide evenly — a 50/50 fixture would turn that into a false red.
    assert surrogate.universal.holdout.rows == gbm.universal.holdout.rows
    assert surrogate.universal.train.rows == gbm.universal.train.rows
    assert surrogate.glm is not None
    assert 0.5 < surrogate.universal.train.ae_overall < 1.5


@pytest.mark.req("FR-137")
async def test_a_model_with_no_split_is_refused_before_a_frame_is_read(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """The surrogate is a Model, so it needs the evidence every Model needs.

    FR-137 gives the approximation a status, and `02` §4.8 makes diagnostics the
    condition of `fitted`; FR-183 makes a diagnostic reported without its holdout
    counterpart a defect. A source model with no split has no holdout to report, so there
    is no surrogate this Job could legitimately produce — and it says so instead of failing
    later inside `_split_frames`.
    """
    actor = await _actuary(database, workspace_id)
    model_id = await _fitted_gbm_without_a_split(database, blob_store, workspace_id, actor)

    refusal = await _transparency_refusal(
        database, blob_store, workspace_id, model_id, actor
    )

    assert refusal.code == "MODEL_SPLIT_REQUIRED"
    assert refusal.status_code == 422
    assert refusal.detail is not None
    assert "FR-183" in refusal.detail


@pytest.mark.req("FR-137")
async def test_a_surrogate_slug_the_column_cannot_hold_is_refused_by_name(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """`models.model_family_slug` is a `String(64)` and the surrogate's is seven longer.

    Without the guard this is an `asyncpg` `DataError` naming a column, raised after the
    approximation has been fitted and the SHAP pass has run — a Job that spends its whole
    budget to report a database detail. The refusal names the analyst's slug and the length
    it produces, which is the only form of this message anyone can act on.
    """
    # 58 is the shortest slug that crosses: 58 + len("-approx") == 65, one past the column.
    slug = "g" * 58
    assert len(f"{slug}-approx") == 65
    model_id, status = await _fitted_gbm(
        database, blob_store, workspace_id, model_family_slug=slug
    )
    assert status is JobStatus.SUCCEEDED, "the source model itself still fits — 58 <= 64"
    actor = await _actuary(database, workspace_id)

    refusal = await _transparency_refusal(
        database, blob_store, workspace_id, model_id, actor
    )

    assert refusal.code == "VALIDATION_FAILED"
    assert refusal.status_code == 422
    assert refusal.detail is not None
    assert slug in refusal.detail, "the message names the slug the analyst chose"
    assert "65 characters" in refusal.detail, "and the length that crosses the boundary"


# -- FR-137: a pre-branch stored artifact still reads --------------------------------


@pytest.mark.req("FR-137")
def test_a_legacy_stored_artifact_still_reads() -> None:
    """The read-path half of the compatibility guarantee `test_glm_approximation.py`
    proves at the type.

    That module proves a legacy `GlmApproximation` still *validates*; it never calls the
    function the read path actually calls. `to_artifact`
    (`backend/src/app/platform/transparency.py`) re-validates the stored JSON on every
    read, and every fixture in this file goes through `model.transparency`, which no
    longer writes the legacy shape — so nothing here had ever exercised `to_artifact`
    against a row written before 2026-08-19: `glm_approximation` carrying its coefficients
    and relativities inline, `approximating_model_id` absent. A test proving only that a
    *new* artifact round-trips cannot protect a guarantee about *old* ones — the row below
    is built by hand for exactly that reason, in the shape a pre-branch row is actually in.
    """
    row = TransparencyArtifactRow(
        id=new_uuid7(),
        workspace_id=new_uuid7(),
        model_id=new_uuid7(),
        created_at=datetime.now(UTC),
        job_id=None,
        payload={
            "glm_approximation": {
                "target": "gbm_prediction",
                "family": "gamma",
                "link": "log",
                "r_squared": 0.94,
                "deviance_explained": 0.9,
                "coefficients": [
                    {
                        "term": "intercept", "estimate": -2.4, "std_error": 0.01,
                        "z": -199.8, "p_value": 0.0, "ci_95": [-2.44, -2.39],
                    },
                ],
                "relativities": {
                    "region": [
                        {"level": "north", "relativity": 1.0, "is_base": True},
                    ],
                },
                "worst_regions": [],
            },
            "shap_summary": None,
            "fidelity_statement": "The approximation explains 94% of deviance.",
            "monotonicity_verified": None,
        },
    )

    artifact = transparency_service.to_artifact(row)

    assert artifact.glm_approximation is not None
    assert artifact.glm_approximation.approximating_model_id is None
    assert artifact.glm_approximation.coefficients
    assert artifact.kinds == (TransparencyKind.GLM_APPROXIMATION,)


# -- FR-137: a hand-written surrogate spec is refused --------------------------------


@pytest.mark.req("FR-137")
async def test_a_surrogate_of_a_model_that_does_not_exist_is_a_404(
    database, blob_store, workspace_id
) -> None:
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    async with database.session() as session:
        source_row = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=model_id
        )
        source = MODEL_SPEC_ADAPTER.validate_python(source_row.spec)
    spec = approximation_spec(
        source,
        source_model_id=new_uuid7(),
        source_model_slug=source_row.model_family_slug,
        source_model_version=source_row.version,
    )

    with pytest.raises(PlatformError) as caught:
        async with database.unit_of_work() as session:
            await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor, spec=spec
            )
    assert caught.value.status_code == 404
    assert caught.value.code == "NOT_FOUND"


@pytest.mark.req("FR-137")
async def test_a_surrogate_of_a_glm_is_refused(
    database, blob_store, workspace_id
) -> None:
    """FR-132 applies to non-GLM models: a GLM approximating a GLM reports 100 %
    fidelity, which looks like evidence and is not — the refusal `fitted_gbm_or_refuse`
    already makes at the endpoint, now made where a spec can arrive without one."""
    actor, model_id = await _fitted_glm(database, blob_store, workspace_id)
    async with database.session() as session:
        source_row = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=model_id
        )
        source = MODEL_SPEC_ADAPTER.validate_python(source_row.spec)
    spec = approximation_spec(
        source,
        source_model_id=model_id,
        source_model_slug=source_row.model_family_slug,
        source_model_version=source_row.version,
    )

    with pytest.raises(PlatformError) as caught:
        async with database.unit_of_work() as session:
            await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor, spec=spec
            )
    assert caught.value.code == "MODEL_APPROXIMATION_INVALID"
    assert caught.value.status_code == 409


@pytest.mark.req("FR-137")
async def test_a_surrogate_on_a_different_dataset_version_is_refused(
    database, blob_store, workspace_id
) -> None:
    """An approximation fitted over a different population describes a different model, and
    renders identically to a correct one."""
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    async with database.session() as session:
        source_row = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=model_id
        )
        source = MODEL_SPEC_ADAPTER.validate_python(source_row.spec)
    other_dataset = await _dataset(database, blob_store, workspace_id, actor)
    other_version = await _validated_version(
        database, blob_store, workspace_id, actor, other_dataset
    )
    spec = approximation_spec(
        source,
        source_model_id=model_id,
        source_model_slug=source_row.model_family_slug,
        source_model_version=source_row.version,
    ).model_copy(
        update={"dataset_version_id": other_version}
    )

    with pytest.raises(PlatformError) as caught:
        async with database.unit_of_work() as session:
            await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor, spec=spec
            )
    assert caught.value.code == "MODEL_APPROXIMATION_INVALID"
    assert caught.value.status_code == 409
    assert "dataset_version_id" in str(caught.value.detail)


@pytest.mark.req("FR-169")
async def test_a_surrogate_whose_companion_names_the_wrong_model_is_refused(
    database, blob_store, workspace_id
) -> None:
    """FR-169: the companion is compared like the other three fields.

    A companion naming a slug or version different from the pinned model is a relation
    failure — the surrogate says it approximates `motor-ad-frequency@7` while the id pins
    a different model — and the same refusal names it.
    """
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    async with database.session() as session:
        source_row = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=model_id
        )
        source = MODEL_SPEC_ADAPTER.validate_python(source_row.spec)
    spec = approximation_spec(
        source,
        source_model_id=model_id,
        source_model_slug=source_row.model_family_slug,
        source_model_version=source_row.version,
    ).model_copy(
        update={
            "approximates_model": ApproximatedModel(
                model_slug="a-family-this-model-is-not", model_version=3
            )
        }
    )

    with pytest.raises(PlatformError) as caught:
        async with database.unit_of_work() as session:
            await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor, spec=spec
            )
    assert caught.value.code == "MODEL_APPROXIMATION_INVALID"
    assert caught.value.status_code == 409
    assert "model_slug" in str(caught.value.detail)


# -- FR-141: the surrogate's slug is derived at reservation --------------------------


@pytest.mark.req("FR-141")
async def test_an_over_long_source_slug_is_refused_by_name_at_reservation(
    database, blob_store, workspace_id
) -> None:
    """OQ-604 (c) moved the length refusal into `reserve_model`.

    `models.model_family_slug` is a `String(64)` and the surrogate's is seven longer, so
    without the refusal here an over-long *source* slug would reach the column at the end
    of the compute as a driver `DataError` naming the column — the API path persisted a
    caller-supplied slug verbatim, so it never hit the guard the transparency Job carries.
    A short caller slug must not rescue the reservation: the refusal names the derived
    slug, which the caller does not choose.
    """
    # 58 is the shortest slug that crosses: 58 + len("-approx") == 65, one past the column.
    slug = "g" * 58
    assert len(f"{slug}-approx") == 65
    model_id, status = await _fitted_gbm(
        database, blob_store, workspace_id, model_family_slug=slug
    )
    assert status is JobStatus.SUCCEEDED, "the source model itself still fits — 58 <= 64"
    actor = await _actuary(database, workspace_id)
    async with database.session() as session:
        source_row = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=model_id
        )
        source = MODEL_SPEC_ADAPTER.validate_python(source_row.spec)
    spec = approximation_spec(
        source,
        source_model_id=model_id,
        source_model_slug=source_row.model_family_slug,
        source_model_version=source_row.version,
    ).model_copy(
        update={"model_family_slug": f"caller-chosen-{new_uuid7().hex[-6:]}"}
    )

    with pytest.raises(PlatformError) as caught:
        async with database.unit_of_work() as session:
            await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor, spec=spec
            )
    assert caught.value.code == "VALIDATION_FAILED"
    assert caught.value.status_code == 422
    assert caught.value.detail is not None
    assert slug in caught.value.detail, "the message names the source slug that overflows"
    assert "65 characters" in caught.value.detail, "and the length that crosses the boundary"


@pytest.mark.req("FR-141")
async def test_a_surrogate_reserved_with_a_mismatched_caller_slug_stores_the_derived_one(
    database, blob_store, workspace_id
) -> None:
    """OQ-604 (c): the derived slug is stored, not the caller's.

    FR-141 says the surrogate's `model_family_slug` is the source model's own family
    slug with `-approx` appended, and the API path used to persist a caller-supplied slug
    verbatim — so the sentence was true of only the surrogates the transparency Job built.
    The row, its version slot and its audit event now all name the derived slug, whatever
    the spec carried.
    """
    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED
    actor = await _actuary(database, workspace_id)
    async with database.session() as session:
        source_row = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=model_id
        )
        source = MODEL_SPEC_ADAPTER.validate_python(source_row.spec)
    assert isinstance(source, GbmSpec)
    caller_slug = f"caller-chosen-{new_uuid7().hex[-6:]}"
    spec = approximation_spec(
        source,
        source_model_id=model_id,
        source_model_slug=source_row.model_family_slug,
        source_model_version=source_row.version,
    ).model_copy(
        update={"model_family_slug": caller_slug}
    )

    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )
    assert should_fit is True
    derived = f"{source.model_family_slug}-approx"

    async with database.session() as session:
        stored = await session.get(ModelRow, row.id)
        reservations = (
            await session.execute(
                select(func.count())
                .select_from(AuditEventRow)
                .where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "model.reserved",
                    AuditEventRow.entity_ref == f"model:{derived}@1",
                )
            )
        ).scalar_one()
    assert stored is not None
    assert stored.model_family_slug == derived
    assert stored.model_family_slug != caller_slug, "the caller's slug is replaced, not kept"
    assert stored.version == 1
    assert reservations == 1, "the audit event names the derived slug too"


@pytest.mark.req("FR-138")
async def test_a_rebuild_does_not_refit_the_surrogate_it_reuses(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FR-138: on `should_fit=False` the numbers are loaded, not recomputed.

    The rebuild test above proves the surrogate *Model row* is reused. It cannot see the
    cost, which is the whole point of the requirement: a full `glum` fit plus one type-III
    refit per factor (FR-172), paid for numbers the handler then discards. This
    counts the calls instead of trusting the ordering.

    Patched on `pricing_core.modelling` rather than on `app.worker.model_handlers`: the
    handler imports both names at call-site scope, so the module namespace it resolves
    them through is the source package's, not its own.
    """
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)
    first = await _transparency_job(database, blob_store, workspace_id, model_id, actor)

    calls: list[str] = []
    real_build = pricing_modelling.build_glm_approximation
    real_diagnostics = pricing_modelling.compute_diagnostics

    def _counted_build(*args: object, **kwargs: object):
        calls.append("build_glm_approximation")
        return real_build(*args, **kwargs)  # type: ignore[arg-type]

    def _counted_diagnostics(*args: object, **kwargs: object):
        calls.append("compute_diagnostics")
        return real_diagnostics(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(pricing_modelling, "build_glm_approximation", _counted_build)
    monkeypatch.setattr(pricing_modelling, "compute_diagnostics", _counted_diagnostics)

    second = await _transparency_job(database, blob_store, workspace_id, model_id, actor)

    assert second.id != first.id, "each build appends an artifact (FR-132)"
    assert calls == [], "a rebuild must not refit the surrogate it is about to reuse"
    assert second.glm_approximation is not None
    assert first.glm_approximation is not None
    assert (
        second.glm_approximation.approximating_model_id
        == first.glm_approximation.approximating_model_id
    )
    assert second.glm_approximation.r_squared == first.glm_approximation.r_squared
    assert (
        second.glm_approximation.deviance_explained
        == first.glm_approximation.deviance_explained
    )
    assert second.glm_approximation.worst_regions == first.glm_approximation.worst_regions


@pytest.mark.req("FR-138")
async def test_a_failed_build_leaves_no_reserved_surrogate_behind(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FR-138's branch asks `reserve_model` a second time, ahead of the compute, and
    that question has to cost nothing.

    Asked inside a transaction that committed, a build that then failed would leave a draft
    surrogate and a `model.reserved` event describing a model nothing ever fitted — the
    state `store()`'s single transaction exists to make unreachable, and the one way the
    cheaper rebuild path could be paid for with a governance defect. The probe reserves in
    a read session for that reason, and this is what says so.
    """
    model_id, _ = await _fitted_gbm(database, blob_store, workspace_id)
    actor = await _actuary(database, workspace_id)

    def _explode(*args: object, **kwargs: object) -> None:
        raise RuntimeError("the approximation failed after the reservation was probed")

    monkeypatch.setattr(pricing_modelling, "build_glm_approximation", _explode)

    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.MODEL_TRANSPARENCY,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id), "sample": 2_000},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.FAILED

    async with database.session() as session:
        source_row = await model_service.load_model_by_id(
            session, workspace_id=workspace_id, model_id=model_id
        )
        source = MODEL_SPEC_ADAPTER.validate_python(source_row.spec)
        slug = approximation_spec(
            source,
            source_model_id=model_id,
            source_model_slug=source_row.model_family_slug,
            source_model_version=source_row.version,
        ).model_family_slug
        surrogates = list(
            (
                await session.execute(
                    select(ModelRow.id).where(
                        ModelRow.workspace_id == workspace_id,
                        ModelRow.model_family_slug == slug,
                    )
                )
            ).scalars()
        )
        reservations = (
            await session.execute(
                select(func.count())
                .select_from(AuditEventRow)
                .where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "model.reserved",
                    AuditEventRow.entity_ref == f"model:{slug}@1",
                )
            )
        ).scalar_one()

    assert surrogates == [], "a failed build must leave no reserved surrogate behind"
    assert reservations == 0, "nor an audit event for a reservation that did not happen"

