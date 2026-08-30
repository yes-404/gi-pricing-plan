"""The freMTPL2 demo models: factors, a GLM and a GBM, through the real Job path (W7-1).

The W7a seed ends with a validated freMTPL2 version. This module extends it: it derives a
named split, authors a small factor set, builds a GLM spec and a GBM spec, and runs both
through `reserve_model` → `model.fit` → `execute_job` — the exact path `POST /models` takes
in production. The two models are the subjects of W7-2's comparison and approval, W7-3's
rating version, and the Phase 1b exit demo (OD3, OD4).
"""

from __future__ import annotations

from typing import Any, Final
from uuid import UUID

from sqlalchemy import select

from app.db.models import DatasetVersionRow, ModelRow
from app.db.session import Database
from app.platform import approvals as approval_service
from app.platform import comparison as comparison_service
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import rating_versions as rating_versions_service
from app.platform.blobs import BlobStore
from app.worker.model_handlers import register_model_handlers
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
    Principal,
    SplitRef,
    new_uuid7,
)

#: The demo factor set (OD4's "reduced factor set"): three continuous, four categorical.
#: Each names a column the W7a dictionary declares. The continuous columns carry the
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
    """Derive train/test parts and record the split (FR-DATA-36), the W7a pattern.

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
    """Author one factor through the platform service (FR-MODEL-7)."""
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
            raise SystemExit(f"{label}: FR-MODEL-66 returned an existing model")
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


async def create_approved_rating_version(
    database: Database,
    workspace_id: UUID,
    analyst: Principal,
    actuary: Principal,
    approver: Principal,
    dataset_version_id: UUID,
    model_id: UUID,
) -> UUID:
    """W7-3: create, submit and approve the demo rating version (FR-PLAT-67).

    The rating version pins the approved GLM as `model:{slug}@{version}`, so the exit
    demo's rating version is addressable and its approval is auditable. The service `decide`
    moves the request; `apply_approval_decision` carries to the artifact, exactly as the
    model approval does.
    """
    async with database.session() as session:
        model_row = await session.get(ModelRow, model_id)
        assert model_row is not None
        model_ref = ArtifactRef(
            type="model", slug=model_row.model_family_slug, version=model_row.version
        )

    async with database.unit_of_work() as session:
        row = await rating_versions_service.create_rating_version(
            session, workspace_id=workspace_id, actor=analyst,
            slug="fremtpl2-demo", dataset_version_id=dataset_version_id, model_ref=model_ref,
        )
        rating_id = row.id

    async with database.unit_of_work() as session:
        _, request = await rating_versions_service.submit_for_review(
            session, workspace_id=workspace_id, actor=actuary,
            rating_version_id=rating_id,
            change_summary="Phase 1b demo rating version pinning the approved GLM",
        )
        request_id = request.id

    async with database.unit_of_work() as session:
        request = await approval_service.decide(
            session, workspace_id=workspace_id, request_id=request_id,
            approver=approver, decision=DecisionKind.APPROVE,
            comment="Demo rating version approved for the Phase 1b exit",
        )
        await rating_versions_service.apply_approval_decision(
            session, workspace_id=workspace_id, actor=approver, request=request
        )
    print(f"  rating version approved: {rating_id}")
    return rating_id
