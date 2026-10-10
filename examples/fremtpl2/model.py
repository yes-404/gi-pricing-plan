"""The freMTPL2 demo models: factors, a GLM and a GBM, through the real Job path (W7-1).

The WK-666 seed ends with a validated freMTPL2 version. This module extends it: it derives a
named split, authors a small factor set, builds a GLM spec and a GBM spec, and runs both
through `reserve_model` → `model.fit` → `execute_job` — the exact path `POST /models` takes
in production. The two models are the subjects of W7-2's comparison and approval, W7-3's
rating version, and the Phase 1b exit demo (OD3, OD4).
"""

from __future__ import annotations

from typing import Any, Final
from uuid import UUID

from sqlalchemy import select

from app.db.models import BlobRow, DatasetVersionRow, ModelRow, RegressionRunRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import comparison as comparison_service
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import rating_algorithms as algorithm_service
from app.platform import rating_versions as rating_versions_service
from app.platform import regression_suites as suite_service
from app.platform.blobs import BlobStore, to_ref
from app.worker.model_handlers import register_model_handlers
from app.worker.rating_handlers import register_rating_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ArtifactRef,
    DecisionKind,
    EarlyStopping,
    Factor,
    FactorIntent,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    GlmSpec,
    JobKind,
    JobStatus,
    MonotonicDirection,
    OffsetSpec,
    Pins,
    Principal,
    QuoteContext,
    RegressionSuiteContent,
    SplitRef,
    new_uuid7,
)
from pricing_core.rating.compile import Bundle
from pricing_core.rating.properties import payable_minor
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_one

#: The demo factor set (OD4's "reduced factor set"): three continuous, four categorical.
#: Each names a column the WK-666 dictionary declares. The continuous columns carry the
#: largest exposure mass; the categorical ones are the ones the freMTPL2 literature fits.
CONTINUOUS_FACTORS: tuple[tuple[str, str], ...] = (
    ("driv_age", "driv_age"),
    ("veh_age", "veh_age"),
    ("veh_power", "veh_power"),
)
CATEGORICAL_FACTORS: tuple[tuple[str, str], ...] = (
    ("veh_brand", "veh_brand"),
    ("veh_gas", "veh_gas"),
    ("area", "area"),
    ("region", "region"),
)
FACTOR_SET: tuple[str, ...] = (
    *(column for _, column in CONTINUOUS_FACTORS),
    *(column for _, column in CATEGORICAL_FACTORS),
)

SPLIT_SEED: Final = 20260827
FIT_SEED: Final = 20260827


async def _run_job(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    actor: Principal,
    kind: JobKind,
    parameters: dict[str, Any],
) -> JobStatus:
    """Submit and run one Job synchronously — the seed's `ingest` pattern."""
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session, kind,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             **parameters},
            actor, workspace_id=workspace_id,
        )
    return await execute_job(database, job.id, blob_store)


async def _split_for(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    actor: Principal,
    version_id: UUID,
) -> SplitRef:
    """Derive train/test parts and record the split (FR-76), the WK-666 pattern.

    The parts are materialised through real `dataset.derive` Jobs — a split whose parts
    were faked would give every fit a holdout identical to its training set.
    """
    parts: dict[str, UUID] = {}
    for part in ("train", "test"):
        status = await _run_job(
            database, blob_store, workspace_id, actor, JobKind.DATASET_DERIVE,
            {"parent_version_id": str(version_id), "operation": "split",
             "params": {"method": "random", "seed": SPLIT_SEED, "part": part,
                        "fractions": {"train": 0.75, "test": 0.25}}},
        )
        if status is not JobStatus.SUCCEEDED:
            raise SystemExit(f"split derive {part}: job {status.value}")
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
            parent_version_id=version_id, name=f"demo-{new_uuid7().hex[-6:]}",
            method="random", seed=SPLIT_SEED, parts=parts,
        )
        return SplitRef(split_artifact_id=row.id, train_part="train", holdout_part="test")


async def _create_factor(
    database: Database,
    workspace_id: UUID,
    actor: Principal,
    dataset_id: UUID,
    slug: str,
    column: str,
) -> UUID:
    """Author one factor through the platform service (FR-96)."""
    async with database.unit_of_work() as session:
        row = await model_service.create_factor(
            session, workspace_id=workspace_id, actor=actor,
            factor=Factor(
                id=new_uuid7(),
                slug=slug,
                dataset_id=dataset_id,
                version=1,
                type=FactorType.IDENTITY,
                source_columns=(column,),
                intent=FactorIntent.RISK,
                monotonic_direction=MonotonicDirection.NONE,
            ),
        )
        return row.id


async def _fit(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    actor: Principal,
    spec: GlmSpec | GbmSpec,
    label: str,
) -> UUID:
    """Reserve, queue, run — the path `POST /models` takes."""
    async with database.unit_of_work() as session:
        row, should_fit = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )
        if not should_fit:
            raise SystemExit(f"{label}: FR-204 returned an existing model")
        model_id = row.id
    status = await _run_job(
        database, blob_store, workspace_id, actor, JobKind.MODEL_FIT,
        {"model_id": str(model_id)},
    )
    if status is not JobStatus.SUCCEEDED:
        raise SystemExit(f"{label}: model.fit {status.value} — see job")
    return model_id


async def fit_demo_models(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    analyst: Principal,
    dataset_id: UUID,
    version_id: UUID,
) -> dict[str, UUID]:
    """Create the demo factors and fit the GLM and the GBM.

    Returns `{"glm": model_id, "gbm": model_id}` for W7-2's comparison.
    """
    register_model_handlers()

    split = await _split_for(database, blob_store, workspace_id, analyst, version_id)
    print(f"  split {split.split_artifact_id} (train/test)")

    factor_ids: dict[str, UUID] = {}
    for slug, column in (*CONTINUOUS_FACTORS, *CATEGORICAL_FACTORS):
        factor_ids[slug] = await _create_factor(
            database, workspace_id, analyst, dataset_id, slug, column
        )
    factors = tuple(factor_ids[slug] for slug in FACTOR_SET)
    print(f"  {len(factors)} factors on {dataset_id}")

    glm_spec = GlmSpec(
        model_family_slug=f"fremtpl2-glm-{new_uuid7().hex[-6:]}",
        dataset_version_id=version_id,
        split_ref=split,
        peril="AD",
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=factors,
        seed=FIT_SEED,
    )
    glm_id = await _fit(database, blob_store, workspace_id, analyst, glm_spec, "GLM")
    print(f"  GLM fitted: {glm_id}")

    gbm_spec = GbmSpec(
        model_type="xgboost",
        model_family_slug=f"fremtpl2-gbm-{new_uuid7().hex[-6:]}",
        dataset_version_id=version_id,
        split_ref=split,
        peril="AD",
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=factors,
        objective=GbmFunctionRef(kind="builtin", name="count:poisson"),
        categorical_handling="native",
        monotone_constraints="derived_from_factors",
        early_stopping=EarlyStopping(on="holdout", metric="poisson-nloglik", rounds=10),
        hyperparameters={"max_depth": 4, "eta": 0.1, "num_boost_round": 60},
        seed=FIT_SEED,
    )
    gbm_id = await _fit(database, blob_store, workspace_id, analyst, gbm_spec, "GBM")
    print(f"  GBM fitted: {gbm_id}")

    return {"glm": glm_id, "gbm": gbm_id}


async def compare_and_approve(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    actuary: Principal,
    approver: Principal,
    glm_id: UUID,
    gbm_id: UUID,
) -> UUID:
    """W7-2: run the comparison, submit the GLM as the actuary, approve it as the approver.

    Returns the approved model id. The GLM is the selected model — the comparison records
    the evidence behind the choice (OD3: compare, select one, approve it).
    """
    async with database.unit_of_work() as session:
        rows = await comparison_service.request_comparison(
            session, workspace_id=workspace_id, actor=actuary,
            model_ids=[glm_id, gbm_id], baseline_id=glm_id,
        )
        job = await job_service.submit(
            session, JobKind.MODEL_COMPARE,
            {
                "workspace_id": str(workspace_id),
                "actor": actuary.model_dump(mode="json"),
                **comparison_service.compare_payload(rows, baseline_id=glm_id),
            },
            actuary, workspace_id=workspace_id,
        )
        compare_job = job.id
    status = await execute_job(database, compare_job, blob_store)
    if status is not JobStatus.SUCCEEDED:
        raise SystemExit(f"model.compare {status.value} — see job")
    print(f"  comparison ran: {compare_job}")

    async with database.unit_of_work() as session:
        _, request = await model_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actuary, model_id=glm_id,
            change_summary="AD frequency, GLM selected over the GBM on transparency grounds",
        )
        request_id = request.id
    print(f"  GLM submitted for review: {request_id}")

    async with database.unit_of_work() as session:
        request = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE,
            comment="GLM approved for the demo rating version",
        )
        # The service `decide` moves the *request*; the API route's
        # `_carry_to_the_artifact` moves the artifact. The seed drives the services, so it
        # carries here — the model reaches `approved`, which is the gate W7-3's rating
        # version pins on.
        await model_service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=request
        )
    print(f"  GLM approved: {glm_id}")
    return glm_id


#: The label every demo-fixture artifact carries (DP-S3-8): the algorithm's slug and step
#: labels, the suite's slug, the golden quote's name and the change note. It is not priced
#: from the approved GLM — the real freMTPL2 algorithm is G2's, owned by the lead.
DEMO_FIXTURE: Final = "demo-fixture"
DEMO_ALGORITHM_SLUG: Final = f"{DEMO_FIXTURE}-motor"
DEMO_SUITE_SLUG: Final = f"{DEMO_FIXTURE}-suite"
DEMO_QUOTE_NAME: Final = f"{DEMO_FIXTURE}-quote"
DEMO_PREMIUM_IN: Final = 100

def _demo_algorithm() -> dict[str, Any]:
    """The demo fixture's algorithm: `payable = premium_in * 2`. **Not priced from the GLM**
    (DP-S3-8): it exists so the demo's rating version can carry executed regression evidence
    (FR-257 limb (1)); the real algorithm around the approved freMTPL2 models is G2's."""
    return {
        "slug": DEMO_ALGORITHM_SLUG,
        "version": 1,
        "input_contract": [{"name": "premium_in", "type": "int", "nullable": False,
                            "min": 0, "max": 1_000_000}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "Demo fixture input",
             "input_name": "premium_in", "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_expr", "type": "expression", "label": "Demo fixture: doubles the input",
             "expr": "premium_in * 2", "result_type": "money_minor",
             "consumes": ["premium_in"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Demo fixture payable premium",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


async def _load_compiled(
    database: Database, blob_store: BlobStore, workspace_id: UUID, rating_id: UUID
) -> CompiledBundle:
    """The compiled bundle the compile Job stored, as the submit gate's loader reads it."""
    async with database.session() as session:
        row = await rating_versions_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        blob_row = await session.get(BlobRow, (row.bundle or {})["blob_sha256"])
        if blob_row is None:
            raise RuntimeError("the compile Job stored no bundle")
        payload = await blob_store.read(to_ref(blob_row))
    return load_bundle(Bundle.model_validate_json(payload))


async def save_demo_algorithm(
    database: Database, workspace_id: UUID, analyst: Principal
) -> ArtifactRef:
    """Save the demo-fixture algorithm through the service; a re-seed's 409 is tolerated."""
    if analyst.id is None:
        raise RuntimeError("the demo analyst has no id")
    try:
        await algorithm_service.create_algorithm(
            database, workspace_id, analyst.id, _demo_algorithm()
        )
    except PlatformError as exc:  # a re-seed: the algorithm is already saved
        if exc.status_code != 409:
            raise
    return ArtifactRef(type="rating_algorithm", slug=DEMO_ALGORITHM_SLUG, version=1)


async def author_demo_rating_evidence(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    analyst: Principal,
    rating_id: UUID,
) -> UUID:
    """Give a draft rating version its executed FR-257 limb (1) evidence (DP-S3-8, T6b).

    **Every piece is produced by the real path, none inserted**: the version arrives with its
    algorithm (saved through the service, `save_demo_algorithm`) and pins declared at create;
    it is compiled by the `rating.compile` Job; the
    golden quote's expected premium is computed by `score_one` on that compiled bundle at
    seed time; and the regression runs through the `rating.regression` Job, whose handler
    calls `run_regression` and persists the run. No `RegressionRun` row and no pass verdict
    is written here. Returns the regression Job's run id.
    """
    register_rating_handlers()
    async with database.session() as session:
        row = await rating_versions_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)

    compiled_status = await _run_job(
        database, blob_store, workspace_id, analyst, JobKind.RATING_COMPILE,
        {"rating_version_id": str(rating_id)},
    )
    if compiled_status is not JobStatus.SUCCEEDED:
        raise RuntimeError(f"demo compile Job {compiled_status}")
    bundle = await _load_compiled(database, blob_store, workspace_id, rating_id)

    context = QuoteContext.model_validate({
        "purpose": "new_business", "quoted_at": "2026-09-28T09:00:00",
        "effective_date": "2026-10-01", "inputs": {"premium_in": DEMO_PREMIUM_IN},
        "options": {"rating_version_ref": str(ref)},
    })
    expected = payable_minor(await score_one(bundle, context))
    if expected is None:
        raise RuntimeError("the demo golden quote was not quoted")
    suite = RegressionSuiteContent.model_validate({
        "algorithm_slug": DEMO_ALGORITHM_SLUG,
        "golden_quotes": [{
            "name": DEMO_QUOTE_NAME,
            "context": context.model_dump(mode="json", exclude={"options"}),
            "expected": {"payable_premium_minor": expected, "outcome": "quoted"},
            "tolerance": {"money_minor": 0},
            "note": "demo fixture: not priced from the GLM",
        }],
        "properties": [
            {"name": "no-null-output", "check": {"kind": "no_null_output"}},
            {"name": "premium-bounded", "check": {"kind": "premium_bounded", "lower_minor": 0}},
        ],
        "generation": {"cases": 25, "seed": SPLIT_SEED, "strategy": "input_contract_sampling"},
    })
    async with database.unit_of_work() as session:
        await suite_service.create_suite_version(
            session, workspace_id=workspace_id, actor=analyst, slug=DEMO_SUITE_SLUG,
            content=suite, change_note="demo fixture: not priced from the GLM",
        )

    run_status = await _run_job(
        database, blob_store, workspace_id, analyst, JobKind.RATING_REGRESSION,
        {"rating_version_id": str(rating_id)},
    )
    if run_status is not JobStatus.SUCCEEDED:
        raise RuntimeError(f"demo regression Job {run_status}")
    async with database.session() as session:
        latest = (await session.execute(
            select(RegressionRunRow).where(RegressionRunRow.rating_version_id == rating_id)
            .order_by(RegressionRunRow.finished_at.desc()).limit(1)
        )).scalar_one()
    return latest.id


async def submit_and_approve_demo(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    actuary: Principal,
    approver: Principal,
    second_approver: Principal,
    rating_id: UUID,
) -> None:
    """Submit the demo rating version through the real gate and approve it with two approvers.

    The gate re-scores the golden quote, pins the suite and reads the executed run
    (FR-257 limb (1)); `06` §4.2's default policy asks two approvers for a rating version.
    The store is the submission's (FR-219's structural diff is kept as a blob). The seeded
    version is the algorithm's first with nothing live, so limb (2) needs no Dislocation Run
    and the evidence records `no_baseline`; a later version would need one (`03` FR-257).
    """
    async def load_compiled(_ref: ArtifactRef) -> CompiledBundle:
        return await _load_compiled(database, blob_store, workspace_id, rating_id)

    async with database.unit_of_work() as session:
        _, request = await rating_versions_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actuary,
            rating_version_id=rating_id,
            change_summary="Phase 1b demo rating version pinning the approved GLM",
            blob_store=blob_store, load_compiled=load_compiled,
        )
        request_id = request.id

    for who in (approver, second_approver):
        async with database.unit_of_work() as session:
            request = await approval_service.decide(
                session, workspace_id=workspace_id, request_id=request_id,
                approver=who, decision=DecisionKind.APPROVE,
                comment="Demo rating version approved for the Phase 1b exit",
                evidence_authors=rating_versions_service.golden_quote_delta_authors,
            )
            await rating_versions_service.apply_approval_decision(
                session, workspace_id=workspace_id, actor=who, request=request
            )


async def create_approved_rating_version(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    analyst: Principal,
    actuary: Principal,
    approver: Principal,
    second_approver: Principal,
    dataset_version_id: UUID,
    model_id: UUID,
) -> UUID:
    """W7-3: create, submit and approve the demo rating version (FR-440).

    The rating version pins the approved GLM as `model:{slug}@{version}`, so the exit
    demo's rating version is addressable and its approval is auditable. Since WK-672 Slice 3
    it also carries **executed** regression evidence (`author_demo_rating_evidence`): a
    submission needs a passing Regression Suite with a golden quote (FR-257 limb (1)), and
    two approvers decide it (`06` §4.2's default policy).
    """
    async with database.session() as session:
        model_row = await session.get(ModelRow, model_id)
        if model_row is None:
            raise RuntimeError(f"the approved model {model_id} does not exist")
        model_ref = ArtifactRef(
            type="model", slug=model_row.model_family_slug, version=model_row.version
        )

    algorithm_ref = await save_demo_algorithm(database, workspace_id, analyst)
    async with database.unit_of_work() as session:
        row = await rating_versions_service.create_rating_version(
            session, workspace_id=workspace_id, actor=analyst,
            slug="fremtpl2-demo", dataset_version_id=dataset_version_id, model_ref=model_ref,
            algorithm_ref=algorithm_ref, pins=Pins(),
        )
        rating_id = row.id

    run_id = await author_demo_rating_evidence(
        database, blob_store, workspace_id, analyst, rating_id
    )

    await submit_and_approve_demo(
        database, blob_store, workspace_id, actuary, approver, second_approver, rating_id
    )
    print(f"  rating version approved: {rating_id} (regression run {run_id}, demo fixture)")
    return rating_id
