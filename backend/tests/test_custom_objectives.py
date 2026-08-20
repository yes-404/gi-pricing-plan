"""Custom Objectives, from authoring to approval and into a fit (`02` FR-MODEL-38..47, 75).

`packages/pricing-core/tests/test_objectives.py` owns the derivatives and §4.7's checks.
This owns the six things only the platform can be wrong about:

* **the definition cannot be edited after it exists** — at the privilege and trigger layers,
  not only in the service. A certificate certifies the parameters it was run against, and an
  objective whose `params` can move is one whose certificate means nothing;
* **a failed certificate leaves the objective in `draft` and clears `certificate_id`**, so
  the status never rests on evidence that has since been contradicted;
* **submission is refused without a certificate**, which is `06` R4 for this artifact type;
* **the approval decision reaches the objective** in the deciding transaction;
* **`expression` is refused by name**, with the flag off and with it on (FR-MODEL-75);
* **a model actually fits under one**, which is the whole point — and the worker resolving
  the ref is the seam `pricing-core` cannot test, because resolving a reference is exactly
  what ADR-0001 forbids it to do.

The certificate is run over a **small grid** (`n_points=300`). §4.7's checks are analytic
comparisons at each sampled point; the sampling density decides how long the Job takes and
not what it concludes, and the default 2 000 points makes this file three times slower for
nothing.
"""

from __future__ import annotations

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_contracts import OPENAPI, _load
from backend.tests.test_model_jobs import (
    _actuary,
    _dataset,
    _factor,
    _split,
    _validated_version,
)
from backend.tests.test_model_jobs_gbm import _gbm_spec
from backend.tests.test_model_lifecycle import _principal_with
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.db.models import CustomObjectiveRow, ModelRow, ObjectiveCertificateRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import objectives as service
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ArtifactRef,
    CertificateOutcome,
    CheckStatus,
    DecisionKind,
    GbmFunctionRef,
    HessianStrategy,
    JobKind,
    JobStatus,
    ModelStatus,
    ObjectiveStatus,
    ObjectiveTemplate,
    Principal,
    ResponseKind,
    SamplingSpec,
    new_uuid7,
)

register_data_handlers()
register_model_handlers()

#: A grid dense enough for §4.7's checks and small enough to run in a suite — see the
#: module docstring. `f_range` spans `log(y_range)`, which is what `default_sampling`
#: derives and what stops `minimum_at_truth` warning about the grid instead of the maths.
COUNT_GRID = SamplingSpec(
    n_points=1_000, y_range=(0.0, 20.0), f_range=(-5.0, 4.0), w_range=(0.01, 10.0), seed=7
)


async def _objective(
    database: Database,
    workspace_id,
    actor: Principal,
    *,
    slug: str | None = None,
    template: ObjectiveTemplate = ObjectiveTemplate.POISSON,
    params: dict[str, float] | None = None,
    **over: object,
) -> CustomObjectiveRow:
    async with database.unit_of_work() as session:
        return await service.create_objective(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=slug or f"obj-{new_uuid7().hex[-6:]}",
            template=template,
            params=params or {},
            applicability=over.get("applicability"),  # type: ignore[arg-type]
            hessian_strategy=HessianStrategy(
                over.get("hessian_strategy", HessianStrategy.CLIP_TO_MIN)
            ),
            hessian_min=float(over.get("hessian_min", 1e-6)),  # type: ignore[arg-type]
            description=over.get("description"),  # type: ignore[arg-type]
        )


async def _certified(
    database: Database, blob_store, workspace_id, actor: Principal, **over: object
) -> CustomObjectiveRow:
    """One objective, certified through the **real Job** rather than by calling the maths."""
    row = await _objective(database, workspace_id, actor, **over)
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.OBJECTIVE_CERTIFY,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "objective_id": str(row.id),
                "sampling": COUNT_GRID.model_dump(mode="json"),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        return (await session.get(CustomObjectiveRow, row.id))  # type: ignore[return-value]


# -- authoring -----------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-38")
async def test_a_new_objective_is_a_draft_and_versions_from_one(
    database: Database, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    first = await _objective(database, workspace_id, actor, slug="motor-freq")
    second = await _objective(database, workspace_id, actor, slug="motor-freq")

    assert (first.version, first.status) == (1, ObjectiveStatus.DRAFT.value)
    assert (second.version, second.status) == (2, ObjectiveStatus.DRAFT.value)
    assert first.certificate_id is None


@pytest.mark.req("FR-MODEL-39")
async def test_a_parameter_outside_the_templates_range_is_refused_before_the_row_exists(
    database: Database, workspace_id
) -> None:
    """§4.5 gives `tweedie.p` the open interval (1, 2). A `p` of 2 is a Gamma, and a stored
    objective whose parameters the contract would reject is one nothing can load."""
    actor = await _actuary(database, workspace_id)
    with pytest.raises(PlatformError) as refused:
        await _objective(
            database, workspace_id, actor,
            template=ObjectiveTemplate.TWEEDIE, params={"p": 2.0},
        )
    assert refused.value.status_code == 422

    async with database.session() as session:
        stored = (
            await session.execute(
                select(CustomObjectiveRow).where(
                    CustomObjectiveRow.workspace_id == workspace_id
                )
            )
        ).scalars().all()
    assert stored == []


@pytest.mark.req("FR-MODEL-75")
async def test_an_expression_objective_is_refused_by_name_whether_the_flag_is_on_or_off(
    database: Database, workspace_id, api_settings
) -> None:
    """The flag being **on** must still refuse (FR-MODEL-75).

    A feature flag that admitted the kind would persist an artifact nothing can certify or
    fit — the derivation, the compilation target and the review path are not built, and no
    setting builds them. The message differs; the answer does not.
    """
    from app.platform import settings as settings_service

    async with database.session() as session:
        with pytest.raises(PlatformError) as off:
            await service.refuse_expression_kind(
                session, settings=api_settings, workspace_id=workspace_id
            )
    assert off.value.code == "OBJECTIVE_KIND_NOT_ENABLED"
    assert off.value.status_code == 409

    async with database.unit_of_work() as session:
        await settings_service.set_workspace_setting(
            session, workspace_id, "features.expression_objectives_enabled", True
        )
    async with database.session() as session:
        with pytest.raises(PlatformError) as on:
            await service.refuse_expression_kind(
                session, settings=api_settings, workspace_id=workspace_id
            )
    assert on.value.code == "OBJECTIVE_KIND_NOT_ENABLED"
    assert on.value.status_code == 409
    assert (on.value.detail or "") != (off.value.detail or "")


# -- the definition cannot move ------------------------------------------------------------


@pytest.mark.req("FR-MODEL-41")
async def test_the_definition_cannot_be_rewritten_while_the_lifecycle_can(
    database: Database, workspace_id
) -> None:
    """The certificate certifies the parameters it ran against.

    An `UPDATE custom_objectives SET params = ...` would leave a `certified` objective whose
    evidence describes a different function — the `validation_reports` incident, in the one
    place where the consequence is a mispriced book rather than a misreported dataset.
    """
    actor = await _actuary(database, workspace_id)
    row = await _objective(database, workspace_id, actor, template=ObjectiveTemplate.TWEEDIE,
                           params={"p": 1.5})

    with pytest.raises(DBAPIError) as refused:
        async with database.unit_of_work() as session:
            await session.execute(
                text("UPDATE custom_objectives SET params = '{\"p\": 1.9}'::jsonb "
                     "WHERE id = :id"),
                {"id": row.id},
            )
    assert "immutable" in str(refused.value).lower()

    # The lifecycle columns move, because that is what a lifecycle is.
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE custom_objectives SET status = 'deprecated' WHERE id = :id"),
            {"id": row.id},
        )


@pytest.mark.req("FR-MODEL-47")
async def test_an_objective_cannot_be_deleted_or_truncated(
    database: Database, workspace_id
) -> None:
    """FR-MODEL-47 asks what was fitted under an objective. A deleted row answers nothing —
    and the models that cite it by ref would keep citing a slug that resolves to nobody."""
    actor = await _actuary(database, workspace_id)
    row = await _objective(database, workspace_id, actor)

    with pytest.raises(DBAPIError):
        async with database.unit_of_work() as session:
            await session.execute(
                text("DELETE FROM custom_objectives WHERE id = :id"), {"id": row.id}
            )
    with pytest.raises(DBAPIError):
        async with database.unit_of_work() as session:
            await session.execute(text("TRUNCATE custom_objectives"))


@pytest.mark.req("FR-MODEL-38")
async def test_a_slug_and_version_cannot_be_used_twice(
    database: Database, workspace_id
) -> None:
    """The unique index, not the read-then-write. Two concurrent authors both read `1`."""
    actor = await _actuary(database, workspace_id)
    row = await _objective(database, workspace_id, actor, slug="collision")
    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            session.add(
                CustomObjectiveRow(
                    id=new_uuid7(), workspace_id=workspace_id, slug=row.slug, version=1,
                    status="draft", kind="template", template="poisson", params={},
                    applicability=row.applicability, hessian_strategy="clip_to_min",
                    hessian_min=1e-6,
                )
            )


@pytest.mark.req("FR-MODEL-42")
async def test_the_application_role_cannot_rewrite_or_delete_a_certificate(
    database: Database,
) -> None:
    """Layer 1. The triggers would refuse anyway, and a later migration granting `UPDATE`
    back would leave every other test in this file green while the first layer was gone."""
    async with database.session() as session:
        granted = {
            row[0]
            for row in (
                await session.execute(
                    text(
                        "SELECT privilege_type FROM information_schema.table_privileges "
                        "WHERE grantee = 'gip_app' AND table_name = 'objective_certificates'"
                    )
                )
            ).all()
        }
    assert granted == {"SELECT", "INSERT"}


# -- certification -------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-42")
async def test_certifying_records_the_certificate_and_moves_the_objective(
    database: Database, blob_store, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    row = await _certified(database, blob_store, workspace_id, actor)

    assert row.status == ObjectiveStatus.CERTIFIED.value
    assert row.certificate_id is not None

    async with database.session() as session:
        certificate = await service.load_certificate(
            session, workspace_id=workspace_id, objective_id=row.id
        )
    # `certified_with_findings`, not `certified`: over a grid spanning y ∈ [0, 20] the
    # gradient of a Poisson loss covers ~7 orders of magnitude and §4.7's
    # `scale_behaviour` check warns. That a finding does not block is the point —
    # FR-MODEL-43 carries it to the approver instead (`02` §4.7).
    assert certificate.result.overall is CertificateOutcome.CERTIFIED_WITH_FINDINGS
    assert {check.status for check in certificate.result.checks} == {
        CheckStatus.PASS,
        CheckStatus.WARN,
    }
    assert certificate.result.sampling == COUNT_GRID
    assert {check.name for check in certificate.result.checks} >= {
        "analytic_vs_numeric_gradient",
        "analytic_vs_numeric_hessian",
        "convexity",
        "smoke_fit",
    }


@pytest.mark.req("FR-MODEL-42")
async def test_a_never_certified_objective_has_no_certificate_to_read(
    database: Database, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    row = await _objective(database, workspace_id, actor)
    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await service.load_certificate(
                session, workspace_id=workspace_id, objective_id=row.id
            )
    assert refused.value.status_code == 404


@pytest.mark.req("FR-MODEL-42")
async def test_a_failed_certificate_is_recorded_and_clears_the_passing_one(
    database: Database, blob_store, workspace_id
) -> None:
    """A re-certification that fails must not leave the objective `certified`.

    Recorded rather than discarded: the finding *is* the answer the run was asked for.
    Cleared rather than kept: an objective still pointing at the previous passing
    certificate would be claiming a status that rests on evidence since contradicted.
    """
    from model_schema import CertificateCheck, CertificateResult

    actor = await _actuary(database, workspace_id)
    row = await _certified(database, blob_store, workspace_id, actor)
    passing = row.certificate_id

    failed = CertificateResult(
        overall=CertificateOutcome.FAILED,
        sampling=COUNT_GRID,
        checks=(
            CertificateCheck(
                name="hessian_matches_numeric",
                status=CheckStatus.FAILED,
                detail="max relative error 4.1e-01 at y=3, f=2.0",
            ),
        ),
        library_versions={"numpy": "2.0.0"},
    )
    async with database.unit_of_work() as session:
        moved, certificate = await service.record_certificate(
            session, workspace_id=workspace_id, actor=actor,
            objective_id=row.id, result=failed,
        )
        assert moved.status == ObjectiveStatus.DRAFT.value
        assert moved.certificate_id is None
        assert certificate.id != passing

    # The superseded certificate is still there: it is the record of what was believed.
    async with database.session() as session:
        stored = (
            await session.execute(
                select(ObjectiveCertificateRow).where(
                    ObjectiveCertificateRow.custom_objective_id == row.id
                )
            )
        ).scalars().all()
    assert len(stored) == 2


@pytest.mark.req("FR-MODEL-42")
async def test_re_certifying_under_review_is_refused(
    database: Database, blob_store, workspace_id
) -> None:
    """Under review the certificate is what an approver is reading. A run that came back
    `failed` would move the evidence beneath a live decision."""
    actor = await _actuary(database, workspace_id)
    row = await _certified(database, blob_store, workspace_id, actor)
    async with database.unit_of_work() as session:
        await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor,
            objective_id=row.id, change_summary="ready",
        )
    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await service.certifiable_or_refuse(
                session, workspace_id=workspace_id, actor=actor, objective_id=row.id
            )
    assert refused.value.status_code == 409


# -- approval ------------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-46")
async def test_submission_without_a_certificate_is_refused(
    database: Database, workspace_id
) -> None:
    """`06` R4 for this artifact type. The policy names `objective_certificate`; a policy
    requirement nothing verifies is a tightening that does nothing."""
    actor = await _actuary(database, workspace_id)
    row = await _objective(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as refused:
            await service.submit_for_review(
                session, workspace_id=workspace_id, actor=actor,
                objective_id=row.id, change_summary="please",
            )
    assert refused.value.status_code == 409  # `draft → review` is not a transition at all


@pytest.mark.req("FR-MODEL-46")
async def test_the_approval_decision_reaches_the_objective(
    database: Database, blob_store, workspace_id
) -> None:
    actor = await _actuary(database, workspace_id)
    row = await _certified(database, blob_store, workspace_id, actor)
    async with database.unit_of_work() as session:
        moved, request = await service.submit_for_review(
            session, workspace_id=workspace_id, actor=actor,
            objective_id=row.id, change_summary="certified, ready for review",
        )
        assert moved.status == ObjectiveStatus.REVIEW.value
        request_id = request.id

    approver = await _principal_with(database, workspace_id, "approver")
    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, approver=approver,
            request_id=request_id,
            decision=DecisionKind.APPROVE,
            comment="derivatives check out",
        )
        applied = await service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )
    assert applied is not None
    assert applied.status == ObjectiveStatus.APPROVED.value


@pytest.mark.req("FR-MODEL-46")
async def test_a_decision_about_another_artifact_type_leaves_the_objective_alone(
    database: Database, workspace_id
) -> None:
    """`_carry_to_the_artifact` calls every module. Each must return `None` for a request
    that is not its own, or adding an artifact type becomes a change in the approvals route."""
    from app.db.models import ApprovalRequestRow

    actor = await _actuary(database, workspace_id)
    request = ApprovalRequestRow(
        id=new_uuid7(), workspace_id=workspace_id, artifact_type="model",
        artifact_ref=str(ArtifactRef(type="model", slug="anything", version=1)),
        status="approved",
        submitted_by=actor.id,
        change_summary="not an objective",
        approvers_required=1,
    )
    async with database.session() as session:
        assert (
            await service.apply_approval_decision(
                session, workspace_id=workspace_id, actor=actor, request=request
            )
            is None
        )


# -- fitting under one, and the blast radius -----------------------------------------------


@pytest.mark.req("FR-MODEL-43")
async def test_a_gbm_fits_under_a_custom_objective_and_shows_up_in_its_usage(
    database: Database, blob_store, workspace_id
) -> None:
    """The seam `pricing-core` cannot test.

    `fit_gbm` refuses a `custom` objective that arrives without its artifact — resolving the
    ref is the platform's job (ADR-0001), and until the worker did it every custom objective
    was a spec nothing could fit. FR-MODEL-47's usage query is the same ref, read backwards.
    """
    actor = await _actuary(database, workspace_id)
    objective = await _certified(database, blob_store, workspace_id, actor)
    ref = f"custom_objective:{objective.slug}@{objective.version}"

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
                objective=GbmFunctionRef(kind="custom", ref=ref),
                response=ResponseKind.CLAIM_COUNT,
            ),
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
        model = model_service.to_model(await session.get(ModelRow, model_id))
        usage = await service.usage(
            session, workspace_id=workspace_id, actor=actor, objective_id=objective.id
        )
    assert model.status is ModelStatus.FITTED
    assert [(m.model_family_slug, m.version) for m in usage.models] == [
        (model.spec.model_family_slug, model.version)
    ]
    assert usage.rating_versions == ()
    assert usage.deployments == ()


@pytest.mark.req("FR-MODEL-43")
async def test_a_draft_objective_cannot_be_fitted_with(
    database: Database, blob_store, workspace_id
) -> None:
    """A `draft` objective has no certificate, so FR-MODEL-42 has not been satisfied and its
    derivatives are unproven. The Job fails rather than producing a model nobody can defend."""
    actor = await _actuary(database, workspace_id)
    objective = await _objective(database, workspace_id, actor)
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
                objective=GbmFunctionRef(
                    kind="custom",
                    ref=f"custom_objective:{objective.slug}@{objective.version}",
                ),
                response=ResponseKind.CLAIM_COUNT,
            ),
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


# -- the published contract ----------------------------------------------------------------


@pytest.mark.req("FR-MODEL-95")
def test_every_custom_objective_route_is_in_the_published_contract() -> None:
    """Including the two `02` §5.1 did not declare — the gap the endpoint audit cannot see,
    because it compares the spec against the contract and an absent endpoint is in neither."""
    paths = _load(OPENAPI)["paths"]
    for method, path in (
        ("post", "/api/v1/custom-objectives"),
        ("get", "/api/v1/custom-objectives/{objective_id}"),
        ("post", "/api/v1/custom-objectives/{objective_id}/derive"),
        ("post", "/api/v1/custom-objectives/{objective_id}/certify"),
        ("get", "/api/v1/custom-objectives/{objective_id}/certificate"),
        ("post", "/api/v1/custom-objectives/{objective_id}/submit"),
        ("get", "/api/v1/custom-objectives/{objective_id}/usage"),
    ):
        assert method in paths.get(path, {}), f"{method.upper()} {path} is unpublished"


@pytest.mark.req("FR-MODEL-75")
def test_the_derive_route_refuses_rather_than_pretending_the_concept_is_unknown(
    api_client: TestClient, workspace_id, principal
) -> None:
    """A 404 would say "this platform has no such concept". The truth is "not until Phase 2",
    and FR-MODEL-75 names this endpoint as one of the two that must say so."""
    response = api_client.post(
        f"/api/v1/custom-objectives/{new_uuid7()}/derive",
        json={},
        headers=_headers(principal.id, workspace_id),
    )
    assert response.status_code in (403, 409)


@pytest.mark.req("FR-MODEL-38")
async def test_a_money_parameter_survives_the_route_as_an_integer(
    api_client: TestClient, workspace_id, principal, grant
) -> None:
    """Pre-existing defect, found while building the parallel Custom Metric endpoint
    (`custom_metrics.py`'s `CreateCustomMetric.params` needed the same fix).

    `CreateCustomObjective.params` was `dict[str, float]`, so a caller's `{"cap": 250000}`
    arrived at `TemplateParameter.check` as `250000.0` — and `check` **raises** for
    `kind == "money_minor"` and a non-`int` value (`CLAUDE.md` §7: money is integer minor
    units). `capped_gamma` and `spliced_severity` are the two of thirteen shipped templates
    carrying a money parameter, and neither could be created through this endpoint at all.

    This asserts the fixed route accepts `capped_gamma` with an integer `cap` and returns
    it unchanged — `int`, not `250000.0` — proving the value reached `CustomObjective`
    without being coerced first.
    """
    await grant("pricing_actuary")
    response = api_client.post(
        "/api/v1/custom-objectives",
        json={
            "slug": "capped-gamma-money-regression",
            "template": "capped_gamma",
            "params": {"cap": 250000},
            "applicability": {
                "responses": ["claim_severity"],
                "backends": ["xgboost"],
                "offset_required": False,
                "y_domain": {"min_exclusive": 0.0},
            },
        },
        headers=_headers(principal.id, workspace_id),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["params"]["cap"] == 250000
    assert isinstance(body["params"]["cap"], int)
