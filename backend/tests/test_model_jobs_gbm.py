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

from app.db.models import BlobRow, CustomMetricRow, CustomObjectiveRow, ModelRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import metrics as metric_service
from app.platform import model_specs as spec_service
from app.platform import modelling as model_service
from app.platform import objectives as objective_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.handlers import handler_for
from app.worker.model_handlers import register_model_handlers
from app.worker.progress import JobProgress
from app.worker.tasks import execute_job
from model_schema import (
    TEMPLATE_APPLICABILITY,
    CertificateCheck,
    CertificateOutcome,
    CertificateResult,
    CheckStatus,
    EarlyStopping,
    GbmFunctionRef,
    GbmSpec,
    HessianStrategy,
    JobKind,
    JobStatus,
    MetricDirection,
    ModelStatus,
    ObjectiveBackend,
    ObjectiveTemplate,
    OffsetSpec,
    Principal,
    ResponseKind,
    SamplingSpec,
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


#: A grid dense enough to satisfy `CertificateResult`'s shape and small enough that its
#: values are never read — both `_certified_metric` and `_certified_objective` below
#: bypass the real sampling the way `test_custom_metrics.py`'s `_certified` does, so what
#: is under test is the worker's ref-resolution wiring (FR-MODEL-106/107), not the
#: certification maths `test_custom_metrics.py`/`test_custom_objectives.py` already cover.
_CERTIFY_GRID = SamplingSpec(
    n_points=1_000, y_range=(0.0, 20.0), f_range=(-5.0, 4.0), w_range=(0.01, 10.0), seed=7
)


async def _certified_metric(
    database: Database, workspace_id, actor: Principal, **over: object
) -> CustomMetricRow:
    """One Custom Metric, `certified` by recording a passing certificate directly.

    `TEMPLATE_APPLICABILITY[POISSON]` as-is, not a narrower applicability built by hand:
    `CustomMetric`'s own validator refuses one wider than its template's
    (`Applicability.is_within`), and the template's own applicability is always exactly
    as wide as itself — matching `packages/pricing-core/tests/test_gbm.py`'s `_metric`.
    """
    async with database.unit_of_work() as session:
        row = await metric_service.create(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=over.get("slug") or f"metric-{new_uuid7().hex[-6:]}",  # type: ignore[arg-type]
            template=ObjectiveTemplate.POISSON,
            params={},
            applicability=TEMPLATE_APPLICABILITY[ObjectiveTemplate.POISSON],
            direction=MetricDirection.LOWER_IS_BETTER,
            description=None,
        )
    passed = CertificateResult(
        overall=CertificateOutcome.CERTIFIED,
        sampling=_CERTIFY_GRID,
        checks=(
            CertificateCheck(name="finiteness", status=CheckStatus.PASS, detail="finite"),
        ),
        library_versions={"numpy": "2.0.0"},
    )
    async with database.unit_of_work() as session:
        certified, _certificate = await metric_service.record_certificate(
            session, workspace_id=workspace_id, actor=actor, metric_id=row.id, result=passed
        )
    return certified


async def _certified_objective(
    database: Database, blob_store: BlobStore, workspace_id, actor: Principal, **over: object
) -> CustomObjectiveRow:
    """One Custom Objective, certified through the **real Job** — `test_custom_objectives
    .py`'s `_certified`, kept local rather than imported: that module imports `_gbm_spec`
    from this one, and importing `_certified` back would make the two files load each
    other before either finished defining what the other needs.
    """
    async with database.unit_of_work() as session:
        row = await objective_service.create_objective(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=over.get("slug") or f"obj-{new_uuid7().hex[-6:]}",  # type: ignore[arg-type]
            template=ObjectiveTemplate.POISSON,
            params={},
            # Threaded rather than hardcoded `None`: the applicability branches of spec
            # validation can only be reached by an objective narrower than its template,
            # and a helper that always builds the template's own applicability is why
            # those two branches had no test.
            applicability=over.get("applicability"),  # type: ignore[arg-type]
            hessian_strategy=HessianStrategy.CLIP_TO_MIN,
            hessian_min=1e-6,
            description=None,
        )
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.OBJECTIVE_CERTIFY,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "objective_id": str(row.id),
                "sampling": _CERTIFY_GRID.model_dump(mode="json"),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        certified = await session.get(CustomObjectiveRow, row.id)
        assert certified is not None
        return certified


@pytest.mark.req("FR-MODEL-106")
async def test_a_certified_custom_metric_is_resolved_and_reaches_the_fit(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The worker seam `pricing-core` cannot cross (ADR-0001): `metric_service.resolve_ref`
    turns the ref the spec names into the artifact `fit_gbm` needs, inside the same
    session the objective resolution already uses. The resolved metric showing up in the
    stored diagnostics' curve is the evidence the wiring reached the fit, not that the
    entry was silently dropped."""
    actor = await _actuary(database, workspace_id)
    metric = await _certified_metric(database, workspace_id, actor)
    ref = f"custom_metric:{metric.slug}@{metric.version}"

    model_id, status = await _fitted_gbm(
        database, blob_store, workspace_id,
        response=ResponseKind.CLAIM_COUNT,
        eval_metrics=(GbmFunctionRef(kind="custom", ref=ref),),
    )
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )
    assert diagnostics.gbm is not None
    assert ref in {point.metric for point in diagnostics.gbm.eval_curve}


@pytest.mark.req("FR-MODEL-106")
async def test_a_custom_eval_metric_that_was_not_supplied_fails_the_job(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """ADR-0001 at the worker seam: a ref `eval_metrics` names with no Custom Metric row
    behind it is the caller's bug, and `_resolve_metrics` refuses it by name
    (`METRIC_REF_UNRESOLVED`) — the same shape as the unsupplied-objective case, now for
    a metric.

    Goes through the handler directly rather than `execute_job`, which maps every handler
    exception to `JOB_HANDLER_FAILED`: the code under test is what `PlatformError.code`
    carries out of the handler, not what the runner does with it once it has it.
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
            spec=_gbm_spec(
                version_id, (area,), split_ref=split,
                response=ResponseKind.CLAIM_COUNT,
                eval_metrics=(GbmFunctionRef(kind="custom", ref="custom_metric:absent@1"),),
            ),
        )
        model_id = row.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor, workspace_id=workspace_id,
        )

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
    assert caught.value.code == "METRIC_REF_UNRESOLVED"


@pytest.mark.req("FR-MODEL-107")
async def test_early_stopping_on_a_custom_metric_reaches_fitted_through_the_job(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """The refusal FR-MODEL-45 was deferred behind, retired end to end: a spec pairing a
    Custom Objective with early stopping on a Custom Metric it declares now fits through
    the same Job every other GBM does, rather than hitting the unconditional
    `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` every such spec used to."""
    actor = await _actuary(database, workspace_id)
    objective = await _certified_objective(database, blob_store, workspace_id, actor)
    objective_ref = f"custom_objective:{objective.slug}@{objective.version}"
    metric = await _certified_metric(database, workspace_id, actor)
    metric_ref = f"custom_metric:{metric.slug}@{metric.version}"

    model_id, status = await _fitted_gbm(
        database, blob_store, workspace_id,
        objective=GbmFunctionRef(kind="custom", ref=objective_ref),
        response=ResponseKind.CLAIM_COUNT,
        eval_metrics=(GbmFunctionRef(kind="custom", ref=metric_ref),),
        early_stopping=EarlyStopping(on="holdout", metric=metric_ref, rounds=5),
    )
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        model = model_service.to_model(await session.get(ModelRow, model_id))
        diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=model_id
        )
    assert model.status is ModelStatus.FITTED
    assert diagnostics.gbm is not None
    assert metric_ref in {point.metric for point in diagnostics.gbm.eval_curve}


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
async def test_a_custom_objective_whose_ref_resolves_to_nothing_is_refused(
    database: Database, blob_store: BlobStore, workspace_id, settings
) -> None:
    """**This test replaced one that refused every Custom Objective.**

    It asserted the spec was unfittable because "FR-MODEL-38 has not been built at all",
    which was true when it was written and is not now: the artifact type, the routes, the
    certify and approval paths and the whole fit path all ship. `02` §5.1 authorised that
    placeholder conditionally — "a Custom Objective **while FR-MODEL-38 is unbuilt**" —
    and the condition has expired.

    What survives is the narrow case the old assertion happened to exercise: this ref
    resolves to no objective in the workspace. It is a **problem, not a 404**, the same
    treatment an unresolvable offset model gets, because a spec that merely cannot be
    fitted is not a bad request.
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
                version_id, (area,), response=ResponseKind.CLAIM_COUNT,
                objective=GbmFunctionRef(
                    kind="custom", ref="custom_objective:capped-gamma@2"
                ),
            ),
        )

    assert validation.ok is False
    problem = next(
        p for p in validation.problems if p.kind is SpecProblemKind.OBJECTIVE_UNSUPPORTED
    )
    assert problem.subject == "custom_objective:capped-gamma@2"


@pytest.mark.req("FR-MODEL-44")
async def test_a_certified_custom_objective_is_accepted_before_a_job_exists(
    database: Database, blob_store: BlobStore, workspace_id, settings
) -> None:
    """The permission the placeholder was hiding, and the point of retiring it.

    A `certified` objective is fittable — `FITTABLE_OBJECTIVE_STATUSES` is
    `{certified, review, approved}`, and its own comment distinguishes that from R4's
    `approved`-alone rule for a *model* reaching approval. So this spec validates, and the
    builder that composes it is no longer offering something its own validator refuses.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    objective = await _certified_objective(database, blob_store, workspace_id, actor)

    async with database.unit_of_work() as session:
        validation = await spec_service.validate_spec(
            session, settings, workspace_id=workspace_id, actor=actor,
            spec=_gbm_spec(
                version_id, (area,), response=ResponseKind.CLAIM_COUNT,
                objective=GbmFunctionRef(
                    kind="custom",
                    ref=f"custom_objective:{objective.slug}@{objective.version}",
                ),
            ),
        )

    # Scoped to the objective. The fixture spec declares no split, so `validation.ok` is
    # legitimately False for a reason this test is not about — asserting `ok is True` here
    # would couple it to the fixture's split and hide what it is checking.
    assert not [
        p for p in validation.problems if p.kind is SpecProblemKind.OBJECTIVE_UNSUPPORTED
    ]


@pytest.mark.req("FR-MODEL-44")
async def test_a_draft_custom_objective_is_refused_before_a_job_exists(
    database: Database, blob_store: BlobStore, workspace_id, settings
) -> None:
    """A `draft` objective has no certificate, so FR-MODEL-42 is unsatisfied.

    Written because a §13 mutation deleting the status gate broke **nothing**: every other
    test here uses `_certified_objective`, so the gate was never exercised on a status it
    must refuse. `FITTABLE_OBJECTIVE_STATUSES` is `{certified, review, approved}` and
    `draft` is outside it — the one case the helper cannot produce.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")

    # `create_objective` makes a `draft` (FR-MODEL-38, 46) — deliberately not certified.
    async with database.unit_of_work() as session:
        draft = await objective_service.create_objective(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=f"draft-{new_uuid7().hex[-6:]}",
            template=ObjectiveTemplate.POISSON,
            params={},
            applicability=None,
            hessian_strategy=HessianStrategy.CLIP_TO_MIN,
            hessian_min=1e-6,
            description=None,
        )
        draft_ref = f"custom_objective:{draft.slug}@{draft.version}"

    async with database.unit_of_work() as session:
        validation = await spec_service.validate_spec(
            session, settings, workspace_id=workspace_id, actor=actor,
            spec=_gbm_spec(
                version_id, (area,), response=ResponseKind.CLAIM_COUNT,
                objective=GbmFunctionRef(kind="custom", ref=draft_ref),
            ),
        )

    assert validation.ok is False
    problem = next(
        p for p in validation.problems if p.kind is SpecProblemKind.OBJECTIVE_UNSUPPORTED
    )
    assert "draft" in problem.message


@pytest.mark.req("FR-MODEL-44")
async def test_a_custom_objective_inapplicable_to_the_response_is_refused(
    database: Database, blob_store: BlobStore, workspace_id, settings
) -> None:
    """FR-MODEL-44's applicability half, on the response axis.

    The objective is Poisson-templated, so its applicability admits `claim_count` alone;
    the spec models `claim_severity`. `fit_gbm` raises `OBJECTIVE_NOT_APPLICABLE` for this
    and the validator now says it before a Job exists.

    This and the backend case below were the two branches with **no** test — the two that
    need an objective with *narrow* applicability, which no other test here builds. Found
    in review after the status-gate hole, which is the same shape one branch over.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    objective = await _certified_objective(database, blob_store, workspace_id, actor)

    async with database.unit_of_work() as session:
        validation = await spec_service.validate_spec(
            session, settings, workspace_id=workspace_id, actor=actor,
            spec=_gbm_spec(
                version_id, (area,), response=ResponseKind.CLAIM_SEVERITY,
                objective=GbmFunctionRef(
                    kind="custom",
                    ref=f"custom_objective:{objective.slug}@{objective.version}",
                ),
            ),
        )

    assert validation.ok is False
    problem = next(
        p for p in validation.problems if p.kind is SpecProblemKind.OBJECTIVE_UNSUPPORTED
    )
    assert "claim_count" in problem.message
    assert "models claim_severity" in problem.message


@pytest.mark.req("FR-MODEL-44")
async def test_a_custom_objective_inapplicable_to_the_backend_is_refused(
    database: Database, blob_store: BlobStore, workspace_id, settings
) -> None:
    """FR-MODEL-44's applicability half, on the backend axis.

    An objective narrowed to LightGBM against an XGBoost spec. The narrowing is legal —
    `Applicability.is_within` refuses an author who *widened* the template's, not one who
    narrowed it — and it is the only way to reach this branch, which is why no other test
    here does.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    lightgbm_only = TEMPLATE_APPLICABILITY[ObjectiveTemplate.POISSON].model_copy(
        update={"backends": frozenset({ObjectiveBackend.LIGHTGBM})}
    )
    objective = await _certified_objective(
        database, blob_store, workspace_id, actor, applicability=lightgbm_only
    )

    async with database.unit_of_work() as session:
        validation = await spec_service.validate_spec(
            session, settings, workspace_id=workspace_id, actor=actor,
            spec=_gbm_spec(
                version_id, (area,), response=ResponseKind.CLAIM_COUNT,
                objective=GbmFunctionRef(
                    kind="custom",
                    ref=f"custom_objective:{objective.slug}@{objective.version}",
                ),
            ),
        )

    assert validation.ok is False
    problem = next(
        p for p in validation.problems if p.kind is SpecProblemKind.OBJECTIVE_UNSUPPORTED
    )
    assert "fits with xgboost" in problem.message


@pytest.mark.req("FR-MODEL-44")
async def test_a_custom_objective_with_no_declared_response_is_refused(
    database: Database, blob_store: BlobStore, workspace_id, settings
) -> None:
    """A builtin objective names its own family; a custom one does not.

    `fit_gbm` raises `OBJECTIVE_RESPONSE_UNDECLARED` for this, and the validator now says
    the same thing before a Job exists. Without `response` there is nothing to check
    applicability against and nothing for the diagnostics deviance to read.
    """
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id
    )
    area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
    objective = await _certified_objective(database, blob_store, workspace_id, actor)

    async with database.unit_of_work() as session:
        validation = await spec_service.validate_spec(
            session, settings, workspace_id=workspace_id, actor=actor,
            spec=_gbm_spec(
                version_id, (area,),
                objective=GbmFunctionRef(
                    kind="custom",
                    ref=f"custom_objective:{objective.slug}@{objective.version}",
                ),
            ),
        )

    assert validation.ok is False
    problem = next(
        p for p in validation.problems if p.kind is SpecProblemKind.OBJECTIVE_UNSUPPORTED
    )
    assert "declares no `response`" in problem.message


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


# --------------------------------------------------------------------------------------
# `02` §3.6 — the transparency artifact
# --------------------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-33")
async def test_a_transparency_artifact_is_built_and_read_back(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-33 end to end, through the Job that builds it and the route that reads it.

    Both halves matter. A `POST` whose artifact nothing can fetch is complete to the
    endpoint audit and useless to a caller — the omission FR-MODEL-84 was appended to close.
    """
    from app.platform import transparency as transparency_service

    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED

    actor = await _actuary(database, workspace_id)
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
        artifact = await transparency_service.load_transparency(
            session, workspace_id=workspace_id, model_id=model_id
        )

    assert artifact.model_id == model_id
    assert artifact.glm_approximation is not None
    assert artifact.shap_summary is not None
    assert artifact.shap_summary.sample_rows <= 2_000
    # FR-MODEL-36: prose that says where, not a score that says how much.
    assert "%" in artifact.fidelity_statement


@pytest.mark.req("FR-MODEL-33")
async def test_a_glm_is_refused_a_transparency_artifact(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-33 applies to **non-GLM** models, and the refusal is the interesting half.

    A GLM approximating itself would report perfect fidelity — an artifact that satisfies
    R3 and carries no information, which is worse than none because it reads as evidence.
    """
    from backend.tests.test_model_jobs import _spec as _glm_spec

    from app.platform import transparency as transparency_service

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
            spec=_glm_spec(version_id, (area,), split_ref=split),
        )
        model_id = row.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor, workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refusal:
            await transparency_service.fitted_gbm_or_refuse(
                session, workspace_id=workspace_id, model_id=model_id
            )
    assert refusal.value.code == "MODEL_ALREADY_TRANSPARENT"
    assert refusal.value.status_code == 409


@pytest.mark.req("FR-MODEL-84")
async def test_a_model_with_no_artifact_reports_that_rather_than_an_empty_one(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """404, naming the model and the route that would build one.

    An empty artifact would satisfy R3's presence check while explaining nothing — the same
    state `TransparencyArtifact` refuses at the type.
    """
    from app.platform import transparency as transparency_service

    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED

    async with database.session() as session:
        with pytest.raises(PlatformError) as missing:
            await transparency_service.load_transparency(
                session, workspace_id=workspace_id, model_id=model_id
            )
    assert missing.value.code == "NOT_FOUND"
    # The refusal names the route that would fix it: a 404 that only says "not found"
    # makes the caller guess whether the model, the artifact or the workspace is wrong.
    assert "POST /api/v1/models/{id}/transparency" in str(missing.value)


@pytest.mark.req("FR-MODEL-33")
async def test_a_second_artifact_appends_rather_than_replacing(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-MODEL-33 allows several, and FR-MODEL-36 makes each one evidence.

    A re-sampled SHAP summary is a second artifact, not a correction of the first: an
    approval that cited the earlier one must still resolve to what the approver read. The
    table has no unique constraint on `model_id` for exactly this reason, and the read path
    takes the latest.
    """
    from app.platform import transparency as transparency_service

    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED
    actor = await _actuary(database, workspace_id)

    ids = []
    for sample in (1_000, 2_000):
        async with database.unit_of_work() as session:
            job = await job_service.submit(
                session, JobKind.MODEL_TRANSPARENCY,
                {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
                 "model_id": str(model_id), "sample": sample},
                actor, workspace_id=workspace_id,
            )
        assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
        async with database.session() as session:
            ids.append(
                (
                    await transparency_service.load_transparency(
                        session, workspace_id=workspace_id, model_id=model_id
                    )
                ).id
            )

    assert ids[0] != ids[1], "the second build replaced the first instead of appending"


@pytest.mark.req("FR-MODEL-89")
async def test_a_gbm_cannot_reach_review_until_an_artifact_names_it(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """`02` §4.8 R3, enforced in the direction the link actually runs (FR-MODEL-89).

    R3 used to read `⟹ transparency_artifact_id set`, and could not be enforced: the
    artifact carries `model_id` and nothing writes a column back onto the model, so the
    invariant was a field-set claim about a field nobody populates — the same shape as
    `status ≥ fitted ⟹ diagnostics_id`, which is the failure OQ-MODEL-8 was written around.

    Both halves are asserted, because the refusal alone would pass against a build that
    refuses every GBM submission. FR-MODEL-64 puts the gate at `review` rather than at
    `approved`: an approver's attention should not be spent on a model that was never
    eligible.
    """
    model_id, status = await _fitted_gbm(database, blob_store, workspace_id)
    assert status is JobStatus.SUCCEEDED
    actor = await _actuary(database, workspace_id)

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await model_service.submit_for_review(
                session, workspace_id=workspace_id, actor=actor, model_id=model_id,
                change_summary="submitted with no transparency artifact",
            )
    assert refused.value.code == "EVIDENCE_INCOMPLETE"
    assert "transparency artifact names it" in (refused.value.detail or "")

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

    async with database.unit_of_work() as session:
        row, _ = await model_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor, model_id=model_id,
            change_summary="submitted with the artifact the invariant asks for",
        )
    assert ModelStatus(row.status) is ModelStatus.REVIEW
