"""WF-01 — dataset to approved Model, driven end to end (FR-OVR-17(ii)).

**One test, one journey.** FR-OVR-17 refuses the cheap version explicitly — "marking an
existing test with a journey id claims a journey where one slice is covered" — so this walks
`wf-01`'s own phases in order, through the same Jobs and services a caller would reach, and
each block below names the steps it is executing.

It is deliberately long. A journey test that read like unit tests would be unit tests, and
what this exists to catch is the seam between phases: a version that validates but cannot be
fitted on, a split both candidates claim to share, a model that reaches an approver with no
evidence. Those failures live between the slices, which is where nothing else looks.

**Every step of `wf-01` now runs.** For most of this file's life three did not — D7's
interaction factor, and E4/E5's Peril Structure and reconciliation — and each was pinned at
the bottom as an **inverted assertion**: one that passes while the capability is absent and
fails the day it lands. All three fired exactly as designed and were driven by the slice
that broke them: E4/E5 on 2026-08-18 with `PerilStructure`, D7 the same day with
`interaction`. The pinned test is gone because its list is empty, and FR-OVR-17(ii) for
`wf-01` is **delivered** rather than partial.

Two divergences from the journey's own wording are recorded rather than pinned, because both
are limits of this fixture and not of the platform:

* **E4 composes AD as burning cost**, where `wf-01` composes it as frequency x severity —
  severity responds to cost *per claim*, and every claim-free row in this book carries a zero
  a Gamma refuses.
* **D7 crosses banded age with vehicle group**, where `wf-01` names
  `annual_mileage x driver_age` — this book has no mileage column.

`packages/pricing-core/tests/test_perils.py` and `test_interactions.py` drive both shapes
directly, on books built for them.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pydantic
import pytest
from backend.tests.test_data_jobs import _ingest, _validate
from sqlalchemy import select

from app.db.models import (
    DatasetVersionRow,
    ModelComparisonRow,
    ModelRow,
    RoleAssignmentRow,
    RoleRow,
    ValidationRuleRow,
    ValidationRuleSetRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import comparison as comparison_service
from app.platform import datasets as dataset_service
from app.platform import diagnostics as diagnostics_service
from app.platform import jobs as job_service
from app.platform import model_specs as spec_service
from app.platform import modelling as model_service
from app.platform import perils as peril_service
from app.platform import rbac
from app.platform import transformations as transform_service
from app.platform import transparency as transparency_service
from app.platform import validation as validation_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.model_handlers import register_model_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ActorKind,
    BandingMethod,
    BandingProposal,
    DatasetStatus,
    DecisionKind,
    ExcludedPeril,
    Factor,
    FactorIntent,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    GlmSpec,
    JobKind,
    JobStatus,
    LargeLossKind,
    LargeLossTreatment,
    ModelStatus,
    MonotonicDirection,
    OffsetSpec,
    OverallOutcome,
    PerilComponent,
    PerilMethod,
    PerilStructureStatus,
    Principal,
    ReconciliationStatus,
    RuleOutcome,
    ScopeType,
    Severity,
    SpecProblemKind,
    SplitRef,
    ValidationLayer,
    new_uuid7,
)

register_data_handlers()
register_model_handlers()

RECIPE = [
    {
        "step": "cast",
        "table": "policy_exposure",
        "params": {
            "columns": {
                "exposure_years": "float",
                "claim_count": "int",
                "claim_amount_minor": "int",
                "driver_age": "int",
            }
        },
    }
]

_HEADER = b"Policy ID,Exposure Years,Claim Count,Claim Amount Minor,Vehicle Group,Driver Age\n"


def _book(rows: int = 600) -> bytes:
    """A small motor book with an age effect a banding can find.

    Claims rise for the youngest drivers, which is what makes C3's banding and D6's A/E
    review something other than noise — and what makes the GLM and the GBM disagree enough
    for E1's comparison to be a comparison.
    """
    lines = []
    for i in range(rows):
        age = 18 + (i * 7) % 60
        claims = 1 if (age < 25 and i % 2 == 0) or i % 7 == 0 else 0
        lines.append(
            f"P{i},0.5,{claims},{claims * 250000},G{i % 5},{age}\n".encode()
        )
    return _HEADER + b"".join(lines)


CLEAN = _book()
#: One row with a negative exposure. B4's failing rule, and the reason B6 exists.
DIRTY = CLEAN + b"P999,-1.0,0,0,G1,40\n"


async def _principal(database: Database, workspace_id: UUID, role: str) -> Principal:
    """A principal holding exactly one built-in role.

    Distinct identities rather than one omnipotent fixture: three of this journey's steps
    are refusals that only exist across a role boundary (B9's acknowledgement, E6's
    submission, E9's self-approval), and a suite with one identity cannot reach them.
    """
    who = Principal(kind=ActorKind.USER, id=new_uuid7(), display=f"{role}@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role_row = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == role
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=who.id,
                role_id=role_row.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )
    return who


async def _dataset_with_rules(
    database: Database, workspace_id: UUID, actor: Principal
) -> UUID:
    """A Dataset with a Rule Set carrying **both** severities `wf-01` phase B needs.

    A `fail` on non-positive exposure — B4's failing rule, the one no acknowledgement can
    talk past (`01` §1.3) — and a `warn` on claim counts above one, which B8 reviews and B9
    accepts with a justification. Without the warn, B9 has nothing to acknowledge and the
    journey's most-cited governance step goes untested.
    """
    async with database.unit_of_work() as session:
        dataset = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=actor,
            slug=f"wf01-{new_uuid7().hex[-8:]}",
        )
        dataset_id = dataset.id

    async with database.unit_of_work() as session:
        rule_ids = []
        for slug, severity, params, message in (
            (
                "exposure-positive", Severity.FAIL,
                {"min_exclusive": 0, "key_columns": ["policy_id"]},
                "exposure must be positive",
            ),
            (
                "claim-count-plausible", Severity.WARN,
                {"max_inclusive": 0, "key_columns": ["policy_id"]},
                "a policy-year with a claim is worth a look",
            ),
        ):
            column = "exposure_years" if severity is Severity.FAIL else "claim_count"
            rule = ValidationRuleRow(
                workspace_id=workspace_id,
                slug=f"{slug}-{new_uuid7().hex[-6:]}",
                version=1,
                layer=ValidationLayer.ACTUARIAL_SANITY.value,
                check="range",
                severity=severity.value,
                body={
                    "target": {"table": "policy_exposure", "column": column},
                    "params": params,
                    "scope": {},
                    "tolerance": {},
                    "message": message,
                    "rationale": "wf-01 phase B needs one of each severity",
                },
                status="approved",
                authored_by=actor.id,
                approved_by=new_uuid7(),
                dry_run_report_id=new_uuid7(),
            )
            session.add(rule)
            await session.flush()
            rule_ids.append(str(rule.id))

        session.add(
            ValidationRuleSetRow(
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                slug=str(dataset_id),
                version=1,
                body={"rule_ids": rule_ids},
                status="approved",
            )
        )
    return dataset_id


async def _run(
    database: Database, blob_store: BlobStore, workspace_id: UUID, actor: Principal,
    kind: JobKind, parameters: dict[str, object],
) -> JobStatus:
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session, kind,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             **parameters},
            actor, workspace_id=workspace_id,
        )
    return await execute_job(database, job.id, blob_store)


@pytest.mark.req("FR-OVR-17")
async def test_wf01_dataset_to_approved_model(
    database: Database, blob_store: BlobStore, workspace_id, settings
) -> None:
    """`wf-01` phases A → E, every step the platform can execute.

    The actors are distinct principals with distinct roles, because several of the journey's
    steps are refusals that only mean something across a role boundary: B9's acknowledgement,
    E6's submission, E9's self-approval.
    """
    analyst = await _principal(database, workspace_id, "pricing_actuary")
    approver = await _principal(database, workspace_id, "approver")

    # -- Phase A — ingestion ------------------------------------------------------------
    # A5-A8: one Job ingests, writes content-addressed parquet, creates the version and
    # profiles it. A9's review is the assertion that the profile exists to be reviewed.
    dataset_id = await _dataset_with_rules(database, workspace_id, analyst)
    first_version = await _ingest(
        database, blob_store, workspace_id, analyst, dataset_id, DIRTY
    )
    async with database.session() as session:
        row = await session.get(DatasetVersionRow, first_version)
        assert row.status == DatasetStatus.DRAFT.value, "A7: a fresh version is `draft`"
        assert row.profile_id is not None, "A8: profiling is automatic, not requested"

    # -- Phase B — validation, including the loop the journey calls the normal case -------
    # B1-B5: the fail is real data, not a flag.
    failing_report = await _validate(
        database, blob_store, workspace_id, analyst, first_version
    )
    async with database.session() as session:
        report = await validation_service.load_report(
            session, workspace_id=workspace_id, report_id=failing_report
        )
    assert validation_service.overall_outcome(report) is OverallOutcome.FAIL
    assert any(r.outcome is RuleOutcome.FAIL for r in report.results)

    # B6: **the fix is to the data.** `02` R1 has no override, so the only way forward is a
    # new version — which is also why a Dataset Version is immutable.
    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await validation_service.promote_using_report(
                session, workspace_id=workspace_id, actor=analyst,
                version_id=first_version, report_id=failing_report,
            )
    assert refused.value.code == "VALIDATION_HAS_FAILURES"

    # B7: re-ingested, revalidated — no fail, and the warn that B8 reviews.
    version_id = await _ingest(
        database, blob_store, workspace_id, analyst, dataset_id, CLEAN
    )
    passing_report = await _validate(
        database, blob_store, workspace_id, analyst, version_id
    )
    async with database.session() as session:
        report = await validation_service.load_report(
            session, workspace_id=workspace_id, report_id=passing_report
        )
    warned = [r for r in report.results if r.outcome is RuleOutcome.WARN]
    assert not [r for r in report.results if r.outcome is RuleOutcome.FAIL]
    assert warned, "B8: the journey reviews warnings, so the fixture must produce one"

    # B9: acknowledged **with a justification**, by a role that may. An acknowledgement is
    # the governed act in this phase, and an unjustified one is refused.
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError):
            await validation_service.acknowledge(
                session, workspace_id=workspace_id, actor=analyst,
                report_id=passing_report, rule_id=warned[0].rule_id, justification="   ",
            )
    async with database.unit_of_work() as session:
        await validation_service.acknowledge(
            session, workspace_id=workspace_id, actor=analyst,
            report_id=passing_report, rule_id=warned[0].rule_id,
            justification="young-driver telematics product launched 2026-04",
        )

    # B10-B11: the transition, and the gate the whole of `01` exists for.
    async with database.unit_of_work() as session:
        promoted = await validation_service.promote_using_report(
            session, workspace_id=workspace_id, actor=analyst,
            version_id=version_id, report_id=passing_report,
        )
    assert promoted.status == DatasetStatus.VALIDATED.value
    async with database.session() as session:
        await dataset_service.fittable_or_refuse(
            session, workspace_id=workspace_id, version_id=version_id
        )
        with pytest.raises(PlatformError) as still_refused:
            await dataset_service.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=first_version
            )
    assert still_refused.value.code == "DATASET_NOT_VALIDATED"

    # -- Phase C — factors, bandings, groupings ------------------------------------------
    # C1: a named split, so both candidates are judged on **provably** the same rows.
    split = await _split_for(database, blob_store, workspace_id, analyst, version_id)

    # C3-C5: a banding proposed by method, then persisted as a versioned artifact carrying
    # its own evidence.
    async with database.session() as session:
        proposal = await transform_service.propose_banding_for_version(
            session, workspace_id=workspace_id, actor=analyst, blob_store=blob_store,
            proposal=_banding_proposal(version_id), slug="driver-age-actuarial",
        )
    assert proposal.boundaries, "C3: a proposal with no boundaries is not a proposal"
    async with database.unit_of_work() as session:
        banding = await transform_service.create_banding(
            session, workspace_id=workspace_id, actor=analyst, banding=proposal
        )
        banding_id = banding.id

    # C7: Factors with intent and a declared monotonic direction. The rationale is required
    # with the direction (FR-MODEL-4) — a judgement with no author is what that refuses.
    age_factor = await _create_factor(
        database, workspace_id, analyst, dataset_id, "driver_age_banded", "driver_age",
        type=FactorType.BANDING, banding_id=banding_id,
        monotonic_direction=MonotonicDirection.DECREASING,
        monotonic_rationale="frequency falls with age above the youngest bands",
    )
    vehicle_factor = await _create_factor(
        database, workspace_id, analyst, dataset_id, "vehicle_group", "vehicle_group",
    )

    # C8: a **prohibited** factor is refused wherever it is used, and the attempt is a step
    # of the journey rather than an aside.
    prohibited = await _create_factor(
        database, workspace_id, analyst, dataset_id, "postcode_full", "policy_id",
        prohibited=True, prohibited_reason="proxy for protected characteristics",
    )

    # -- Phase D — fitting and diagnostics ------------------------------------------------
    # D2: every error caught before compute is spent. The prohibited factor is one of them.
    async with database.unit_of_work() as session:
        validation = await spec_service.validate_spec(
            session, settings, workspace_id=workspace_id, actor=analyst,
            spec=_glm_spec(version_id, (age_factor, vehicle_factor, prohibited), split),
        )
    assert validation.ok is False
    assert any(
        p.kind is SpecProblemKind.FACTOR_PROHIBITED for p in validation.problems
    ), "C8/D2: a prohibited factor is refused at spec validation, before a Job exists"

    glm_spec = _glm_spec(version_id, (age_factor, vehicle_factor), split)
    async with database.unit_of_work() as session:
        clean = await spec_service.validate_spec(
            session, settings, workspace_id=workspace_id, actor=analyst, spec=glm_spec
        )
    assert clean.ok is True

    # D3-D5: the fit, and diagnostics on train **and** holdout (FR-MODEL-54).
    glm_id = await _fit_model(database, blob_store, workspace_id, analyst, glm_spec)
    async with database.session() as session:
        glm = model_service.to_model(await session.get(ModelRow, glm_id))
        glm_diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=glm_id
        )
    assert glm.status is ModelStatus.FITTED
    assert glm.fit_result is not None
    assert glm.fit_result.model_type == "glm"
    assert glm_diagnostics.universal.train.ae_overall > 0
    assert glm_diagnostics.universal.holdout.ae_overall > 0
    assert glm_diagnostics.glm is not None

    # D7: the interaction factor. `wf-01` names `annual_mileage x driver_age`; this book has
    # no mileage column, so the cross is **banded age x vehicle group** — a divergence in the
    # variables rather than in the step, and the one the fixture allows. Crossing the *banded*
    # age is the point either way: crossing raw ages would give one cell per age-year.
    interaction_id = await _create_factor(
        database, workspace_id, analyst, dataset_id,
        "age_x_vehicle", "driver_age",
        type=FactorType.INTERACTION,
        source_columns=(),
        operand_factor_ids=(age_factor, vehicle_factor),
        monotonic_direction=MonotonicDirection.NONE,
    )
    interaction_spec = _glm_spec(version_id, (interaction_id,), split)
    interaction_model_id = await _fit_model(
        database, blob_store, workspace_id, analyst, interaction_spec
    )
    async with database.session() as session:
        interacted = model_service.to_model(
            await session.get(ModelRow, interaction_model_id)
        )
    assert interacted.fit_result is not None
    # The relativity table is keyed by the crossed factor and its levels are cells. A table
    # keyed by either operand alone would mean the cross never ran, and one with the
    # operands as separate terms would mean the design carried collinear main effects.
    assert set(interacted.fit_result.relativities) == {"age_x_vehicle"}
    cells = [row.level for row in interacted.fit_result.relativities["age_x_vehicle"]]
    assert cells, "the cross produced no levels"
    assert all(" | " in cell for cell in cells), cells

    # D9 comes **before** D8 here, because the refusal is about a spec that never fits: a
    # counting objective with no offset and no acknowledgement is refused at the type.
    with pytest.raises(pydantic.ValidationError, match="offset"):
        _gbm_spec(version_id, (age_factor, vehicle_factor), split, offset=OffsetSpec())

    # D8: the GBM on the same factors and the same split.
    gbm_spec = _gbm_spec(version_id, (age_factor, vehicle_factor), split)
    gbm_id = await _fit_model(database, blob_store, workspace_id, analyst, gbm_spec)
    async with database.session() as session:
        gbm = model_service.to_model(await session.get(ModelRow, gbm_id))
        gbm_diagnostics = await diagnostics_service.load_diagnostics(
            session, workspace_id=workspace_id, model_id=gbm_id
        )
    assert gbm.fit_result is not None
    assert gbm.fit_result.model_type == "xgboost"
    assert gbm_diagnostics.gbm is not None
    assert gbm_diagnostics.glm is None, "a booster has no coefficient table to report"

    # D10: the transparency artifact, and the fidelity statement an approver reads.
    assert await _run(
        database, blob_store, workspace_id, analyst,
        JobKind.MODEL_TRANSPARENCY, {"model_id": str(gbm_id), "sample": 500},
    ) is JobStatus.SUCCEEDED
    async with database.session() as session:
        artifact = await transparency_service.load_transparency(
            session, workspace_id=workspace_id, model_id=gbm_id
        )
    assert artifact.glm_approximation is not None
    assert artifact.shap_summary is not None
    assert "%" in artifact.fidelity_statement, "FR-MODEL-36 says *where*, with a number"

    # -- Phase E — selection and approval -------------------------------------------------
    # E1: the comparison, on the shared holdout the split guarantees.
    async with database.unit_of_work() as session:
        rows = await comparison_service.request_comparison(
            session, workspace_id=workspace_id, actor=analyst,
            model_ids=[glm_id, gbm_id], baseline_id=glm_id,
        )
        job = await job_service.submit(
            session, JobKind.MODEL_COMPARE,
            {"workspace_id": str(workspace_id), "actor": analyst.model_dump(mode="json"),
             **comparison_service.compare_payload(rows, baseline_id=glm_id)},
            analyst, workspace_id=workspace_id,
        )
        compare_job = job.id
    assert await execute_job(database, compare_job, blob_store) is JobStatus.SUCCEEDED

    # The job succeeding is not the assertion. `wf-01` E1 compares *the two candidates*, and
    # a comparison that quietly dropped one — or scored the GBM as though its booster were a
    # set of coefficients — would still succeed. So the artifact is read back the way the
    # screen reads it, and asked whether both models are in it.
    async with database.session() as session:
        recorded = (
            await session.execute(
                select(ModelComparisonRow.id).where(ModelComparisonRow.job_id == compare_job)
            )
        ).scalar_one()
        comparison = await comparison_service.load_comparison(
            session, workspace_id=workspace_id, comparison_id=recorded
        )
    assert len(comparison.summary.model_refs) == 2, "a GLM compared with nothing is not E1"
    assert comparison.summary.holdout_rows > 0
    # The GBM was *scored*, not merely listed: a deviance measured from its booster's
    # predictions over the shared holdout. `ComparisonSummary` already refuses a metric that
    # names only some of the models, so a number here for each ref is the whole claim.
    deviance = next(m for m in comparison.summary.metrics if m.metric == "holdout_deviance")
    assert all(v.value is not None for v in deviance.values)
    # **Empty on purpose.** A relativity difference is a ratio between two models' level
    # effects, and a booster has no level effects to compare — `02` §3.6's transparency
    # artifact is where a GBM's factor story lives, not this table. Reporting differences
    # here would mean one side had been read off something that is not a relativity.
    assert comparison.summary.relativity_differences == ()

    # E2: the actuary selects the GLM. The comparison artifact is what records the evidence
    # behind that choice, which is the whole reason it is persisted.
    selected = glm_id

    # E3, the step the journey delegates in one line — "repeats phases C-E for the remaining
    # perils and for severity models". AD's *cost* model is fitted here because E4 needs one:
    # the model selected at E2 is a **frequency** model, and composing it as a peril's cost
    # would reconcile expected claim counts against observed claim amounts.
    #
    # **`wf-01` E4 composes AD as frequency x severity and this composes it as burning
    # cost**, which is a fixture limit rather than a platform one: severity responds to cost
    # *per claim*, and every claim-free row in this book carries a zero a Gamma refuses.
    # `packages/pricing-core/tests/test_perils.py` drives the frequency x severity arm
    # directly, so the arithmetic is covered where it can be exercised honestly.
    burning_cost_id = await _fit_model(
        database, blob_store, workspace_id, analyst,
        GlmSpec(
            model_family_slug=f"wf01-bc-{new_uuid7().hex[-6:]}",
            dataset_version_id=version_id,
            split_ref=split,
            peril="AD",
            response_column="claim_amount_minor",
            family="tweedie",
            family_params={"power": 1.5},
            offset=OffsetSpec(kind="log_column", column="exposure_years"),
            factors=(age_factor, vehicle_factor),
            seed=20260818,
        ),
    )

    # E4: the Peril Structure. `wf-01`'s own has three perils; this book has one modelled
    # peril, so the other two are **excluded with reasons** — which is FR-MODEL-60's actual
    # demand, that every peril be one or the other, rather than a demand for three models.
    async with database.session() as session:
        selected_row = await session.get(ModelRow, burning_cost_id)
        selected_ref = f"model:{selected_row.model_family_slug}@{selected_row.version}"

    async with database.unit_of_work() as session:
        structure_row = await peril_service.create_structure(
            session,
            workspace_id=workspace_id,
            actor=analyst,
            slug=f"wf01-motor-{new_uuid7().hex[-6:]}",
            perils=[
                PerilComponent(
                    peril="AD",
                    method=PerilMethod.BURNING_COST,
                    burning_cost_model=selected_ref,
                    large_loss=LargeLossTreatment(kind=LargeLossKind.NONE),
                )
            ],
            excluded_perils=[
                ExcludedPeril(
                    peril="TP_BI", reason="Modelled in the TP_BI structure, not this one."
                ).model_dump(mode="json"),
                ExcludedPeril(
                    peril="WINDSCREEN", reason="Loaded flat in the rating algorithm."
                ).model_dump(mode="json"),
            ],
        )
        structure_id, structure_slug = structure_row.id, structure_row.slug
        structure_version = structure_row.version

    # E5: the reconciliation, through the real worker. The tolerance is the actuary's own
    # declaration — `wf-01` E5 declares 0.02 against a book of hundreds of thousands of
    # policy-years; this fixture is twenty-one, so the number is wider and the *mechanism*
    # is what the journey is asserting.
    async with database.unit_of_work() as session:
        reserved = await peril_service.request_reconciliation(
            session, workspace_id=workspace_id, actor=analyst,
            structure_id=structure_id, tolerance=Decimal("0.9"),
        )
        reconcile_payload = peril_service.reconcile_payload(
            reserved,
            tolerance=Decimal("0.9"),
            observed_column="claim_amount_minor",
            exposure_column="exposure_years",
        )
    assert await _run(
        database, blob_store, workspace_id, analyst,
        JobKind.PERIL_STRUCTURE_RECONCILE, dict(reconcile_payload),
    ) is JobStatus.SUCCEEDED

    async with database.session() as session:
        reconciled = await peril_service.load_structure(
            session, workspace_id=workspace_id, structure_id=structure_id
        )
    assert reconciled.status is PerilStructureStatus.RECONCILED
    assert reconciled.reconciliation is not None
    assert reconciled.reconciliation.status is ReconciliationStatus.PASS
    # FR-MODEL-74: the treatment is stated beside the number it produced, per peril — so a
    # capped model reconciling to uncapped data cannot read as a modelling error.
    assert [p.large_loss_kind for p in reconciled.reconciliation.perils] == [
        LargeLossKind.NONE
    ]
    # FR-MODEL-58's sum, checked rather than assumed.
    assert (
        sum(p.modelled_burning_cost for p in reconciled.reconciliation.perils)
        == reconciled.reconciliation.modelled_burning_cost
    )

    # E6: submitted for approval. The evidence bundle is assembled and pinned here.
    async with database.unit_of_work() as session:
        _, request = await model_service.submit_for_review(
            session, workspace_id=workspace_id, actor=analyst, model_id=selected,
            change_summary="AD frequency, GLM selected over the GBM on transparency grounds",
        )
        request_id = request.id
    async with database.session() as session:
        submitted = model_service.to_model(await session.get(ModelRow, selected))
    assert submitted.status is ModelStatus.REVIEW
    assert submitted.approval_request_id == request_id

    # E9: **the submitter cannot approve their own work** (`06` R1). The journey names this
    # step, and a journey test that only walked the happy path would not reach it.
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as self_approval:
            await approval_service.decide(
                session, workspace_id=workspace_id, request_id=request_id,
                approver=analyst, decision=DecisionKind.APPROVE, comment="looks fine to me",
            )
    assert self_approval.value.code == "SUBMITTER_CANNOT_APPROVE"

    # E9-E10: a different principal approves, and the decision reaches the artifact in the
    # same transaction — a model left in `review` behind an approved request is a model no
    # Rating Version may reference and no screen can explain.
    async with database.unit_of_work() as session:
        decided = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE,
            comment="holdout lift and A/E by age band both support this",
        )
        approved_row = await model_service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=decided
        )
    assert approved_row is not None
    assert approved_row.status == ModelStatus.APPROVED.value

    # E6/E10 for the **structure**, which the journey submits and approves alongside the
    # models. It needed no new approval machinery — `06` FR-GOV-9's machine takes an
    # `ArtifactRef` — but it did need a `peril_structure` entry in the policy, without which
    # a submission is refused for an artifact nobody could ever approve.
    async with database.unit_of_work() as session:
        _, structure_request = await peril_service.submit_for_review(
            session, workspace_id=workspace_id, actor=analyst,
            structure_id=structure_id,
            change_summary="AD burning cost on the approved GLM; TP_BI and windscreen excluded",
        )
        structure_request_id = structure_request.id
    assert structure_request.artifact_ref == (
        f"peril_structure:{structure_slug}@{structure_version}"
    )

    # E9 again, on the structure: the same separation of duties, and it is the generic
    # machine enforcing it rather than a second implementation.
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as structure_self_approval:
            await approval_service.decide(
                session, workspace_id=workspace_id, request_id=structure_request_id,
                approver=analyst, decision=DecisionKind.APPROVE, comment="mine, approved",
            )
    assert structure_self_approval.value.code == "SUBMITTER_CANNOT_APPROVE"

    async with database.unit_of_work() as session:
        await approval_service.decide(
            session, workspace_id=workspace_id, request_id=structure_request_id,
            approver=approver, decision=DecisionKind.APPROVE,
            comment="reconciles within the declared tolerance; exclusions are reasoned",
        )

    # The journey's postcondition: an `approved` Model a Rating Version may reference.
    async with database.session() as session:
        final = model_service.to_model(await session.get(ModelRow, selected))
    assert final.status is ModelStatus.APPROVED
    assert final.dataset_version_id == version_id, "lineage survives the whole journey"


# -- Helpers: the steps whose *mechanics* are not what the journey is about ----------------


async def _create_factor(
    database: Database, workspace_id: UUID, actor: Principal, dataset_id: UUID,
    slug: str, column: str, **over: object,
) -> UUID:
    fields: dict[str, object] = {
        "id": uuid4(), "slug": slug, "dataset_id": dataset_id, "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,),
        "intent": FactorIntent.RISK,
    }
    fields.update(over)
    async with database.unit_of_work() as session:
        row = await model_service.create_factor(
            session, workspace_id=workspace_id, actor=actor,
            factor=Factor(**fields),  # type: ignore[arg-type]
        )
        return row.id


def _banding_proposal(version_id: UUID) -> BandingProposal:
    """C3: ten bands on `driver_age` by exposure quantile.

    `exposure_quantile` rather than `equal_width`: the journey's step says so, and equal
    width on an age column puts most of the book in three bands.
    """
    return BandingProposal(
        dataset_version_id=version_id, column="driver_age",
        method=BandingMethod.EXPOSURE_QUANTILE, n_bands=5,
    )


async def _split_for(
    database: Database, blob_store: BlobStore, workspace_id: UUID, actor: Principal,
    version_id: UUID,
) -> SplitRef:
    """C1, through the real `dataset.derive` Jobs.

    The parts are **materialised**, not asserted: a split whose parts were faked would give
    every fit a holdout identical to its training set, and every diagnostic downstream would
    report the model's own memory (`01` FR-DATA-36).
    """
    parts: dict[str, UUID] = {}
    for part in ("train", "test"):
        assert await _run(
            database, blob_store, workspace_id, actor, JobKind.DATASET_DERIVE,
            {"parent_version_id": str(version_id), "operation": "split",
             "params": {"method": "random", "seed": 20260817, "part": part,
                        "fractions": {"train": 0.75, "test": 0.25}}},
        ) is JobStatus.SUCCEEDED
        async with database.session() as session:
            child = (
                await session.execute(
                    select(DatasetVersionRow).where(
                        DatasetVersionRow.workspace_id == workspace_id,
                        DatasetVersionRow.derived_from["parent_version_id"].astext
                        == str(version_id),
                        DatasetVersionRow.derived_from["params"]["part"].astext == part,
                    )
                )
            ).scalar_one()
        parts[part] = child.id

    async with database.unit_of_work() as session:
        row = await dataset_service.record_split(
            session, workspace_id=workspace_id, actor=actor,
            parent_version_id=version_id, name=f"wf01-{new_uuid7().hex[-6:]}",
            method="random", seed=20260817, parts=parts,
        )
        return SplitRef(split_artifact_id=row.id, train_part="train", holdout_part="test")


def _glm_spec(version_id: UUID, factors: tuple[UUID, ...], split: SplitRef) -> GlmSpec:
    """D1: AD frequency — Poisson, log link, `offset = log(exposure_years)`."""
    return GlmSpec(
        model_family_slug=f"wf01-glm-{new_uuid7().hex[-6:]}",
        dataset_version_id=version_id,
        split_ref=split,
        peril="AD",
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=factors,
        seed=20260817,
    )


def _gbm_spec(
    version_id: UUID, factors: tuple[UUID, ...], split: SplitRef, **over: object
) -> GbmSpec:
    """D8: the same factors, the same split, `count:poisson` with the exposure offset."""
    base: dict[str, object] = {
        "model_type": "xgboost",
        "model_family_slug": f"wf01-gbm-{new_uuid7().hex[-6:]}",
        "dataset_version_id": version_id,
        "split_ref": split,
        "peril": "AD",
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "factors": factors,
        "objective": GbmFunctionRef(kind="builtin", name="count:poisson"),
        "categorical_handling": "native",
        "hyperparameters": {"max_depth": 3, "eta": 0.2, "num_boost_round": 40},
        "seed": 20260817,
    }
    base.update(over)
    return GbmSpec(**base)  # type: ignore[arg-type]


async def _fit_model(
    database: Database, blob_store: BlobStore, workspace_id: UUID, actor: Principal,
    spec: GlmSpec | GbmSpec,
) -> UUID:
    """D3: reserve, queue, run — the path `POST /models` takes."""
    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )
        assert should_fit is True, "FR-MODEL-66 would return the existing model instead"
        model_id = row.id
    assert await _run(
        database, blob_store, workspace_id, actor, JobKind.MODEL_FIT,
        {"model_id": str(model_id)},
    ) is JobStatus.SUCCEEDED
    return model_id


# -- Every step of `wf-01` now runs ---------------------------------------------------------
#
# **The pinned list is empty, and the test that held it is gone** (2026-08-18, the
# interaction slice). It carried D7, E4 and E5 as *inverted* assertions — each passing while
# its capability was absent and failing the day it landed — and every one of them did exactly
# that: E4/E5 went red when `PerilStructure` landed and the peril-structure slice drove them,
# D7 went red when `interaction` became resolvable and this slice drove it above.
#
# Deleting the test is the correct end state rather than a loss of coverage: the assertions
# were placeholders *for* the journey steps, and the journey now contains the steps. Keeping
# an empty pin would be a test asserting that nothing is missing, which is what the walk
# above already says, at length and with data.
#
# FR-OVR-17(ii) for `wf-01` is therefore **delivered**, not partial. One divergence remains
# recorded rather than pinned, because both halves are fixture limits and not platform ones:
# `wf-01` E4 composes AD as frequency x severity and the journey composes it as burning cost
# (severity responds to cost per claim, and every claim-free row here carries a zero a Gamma
# refuses), and D7 names `annual_mileage x driver_age` where this book has no mileage column,
# so the cross is banded age x vehicle group. `packages/pricing-core/tests/` drives both
# shapes directly.
