"""The freMTPL2 demo models: factors, a GLM and a GBM, through the real Job path (W7-1).

The WK-666 seed ends with a validated freMTPL2 version. This module extends it: it derives a
named split, authors a small factor set, builds a GLM spec and a GBM spec, and runs both
through `reserve_model` → `model.fit` → `execute_job` — the exact path `POST /models` takes
in production. The two models are the subjects of W7-2's comparison and approval, W7-3's
rating version, and the Phase 1b exit demo (OD3, OD4).
"""

from __future__ import annotations

import io
import math
from dataclasses import dataclass
from decimal import Decimal
from itertools import pairwise
from typing import Any, Final
from uuid import UUID

from algorithm import (
    BASE_LABEL,
    FREMTPL2_ALGORITHM_SLUG,
    base_premium_minor,
    build_fremtpl2_algorithm,
    glm_premium_minor,
)
from sqlalchemy import select

from app.db.models import BlobRow, DatasetVersionRow, ModelRow, RegressionRunRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import approvals as approval_service
from app.platform import comparison as comparison_service
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import rate_tables as rate_table_service
from app.platform import rating_algorithms as algorithm_service
from app.platform import rating_versions as rating_versions_service
from app.platform import regression_suites as suite_service
from app.platform import transformations as transform_service
from app.platform.blobs import BlobStore, to_ref
from app.platform.dislocation_runs import portfolio_table, read_stored_blob
from app.worker.model_handlers import register_model_handlers
from app.worker.rating_handlers import register_rating_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ArtifactRef,
    Banding,
    BandingMethod,
    BandingProposal,
    DecisionKind,
    EarlyStopping,
    Factor,
    FactorIntent,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    GlmFitResult,
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
from pricing_core.rating.runtime import CompiledBundle, load_bundle

#: The demo factor set (OD4's "reduced factor set"), seven categorical-rated Factors. The three
#: continuous columns are **banded** (PL-1525 DP-a1 (a)): a banding is the rateable form (RL-1361:
#: a continuous factor has no relativity table), and each Factor's slug differs from its column,
#: because the algorithm's band step produces the Factor from the raw column and a value name has
#: one producer. Each is `(factor slug, column)`; the column is one the WK-666 dictionary declares.
CONTINUOUS_FACTORS: tuple[tuple[str, str], ...] = (
    ("driv_age_band", "driv_age"),
    ("veh_age_band", "veh_age"),
    ("veh_power_band", "veh_power"),
)
CATEGORICAL_FACTORS: tuple[tuple[str, str], ...] = (
    ("veh_brand", "veh_brand"),
    ("veh_gas", "veh_gas"),
    ("area", "area"),
    ("region", "region"),
)
#: The Factor slugs, in the order the model is fitted and the tables are seeded.
FACTOR_SET: tuple[str, ...] = tuple(
    slug for slug, _ in (*CONTINUOUS_FACTORS, *CATEGORICAL_FACTORS)
)

#: The bands' method and count (PL-1525 Acceptance 11 (a)): 5 exposure-blind quantile bands.
BANDING_METHOD: Final = BandingMethod.QUANTILE
BAND_COUNT: Final = 5

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
    banding_id: UUID | None = None,
) -> UUID:
    """Author one factor through the platform service (FR-96); a banded one pins its Banding."""
    async with database.unit_of_work() as session:
        row = await model_service.create_factor(
            session, workspace_id=workspace_id, actor=actor,
            factor=Factor(
                id=new_uuid7(),
                slug=slug,
                dataset_id=dataset_id,
                version=1,
                type=FactorType.IDENTITY if banding_id is None else FactorType.BANDING,
                source_columns=(column,),
                banding_id=banding_id,
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


@dataclass(frozen=True)
class DemoBanding:
    """A saved Banding: its row id (what a Factor pins) and the artifact as proposed."""

    id: UUID
    banding: Banding


async def create_demo_bandings(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    analyst: Principal,
    version_id: UUID,
) -> dict[str, DemoBanding]:
    """One Banding per continuous column, proposed on the validated dataset version and saved
    through the service (FR-97, FR-98, FR-101). Returns them by Factor slug.

    The edges are an output of the proposal on the seeded data, so they are printed here and
    recorded in the slice ledger (PL-1525 Acceptance 11 (a)); nobody typed them.
    """
    bandings: dict[str, DemoBanding] = {}
    for slug, column in CONTINUOUS_FACTORS:
        async with database.session() as session:
            proposed = await transform_service.propose_banding_for_version(
                session, workspace_id=workspace_id, actor=analyst, blob_store=blob_store,
                proposal=BandingProposal(
                    dataset_version_id=version_id, column=column, method=BANDING_METHOD,
                    n_bands=BAND_COUNT,
                ),
                slug=f"fremtpl2-{column.replace('_', '-')}-banding",
            )
        async with database.unit_of_work() as session:
            row = await transform_service.create_banding(
                session, workspace_id=workspace_id, actor=analyst, banding=proposed
            )
            banding_id = row.id
        bandings[slug] = DemoBanding(banding_id, proposed)
        print(f"  banding {proposed.slug}@{proposed.version} ({banding_id}): {column} "
              f"{BANDING_METHOD.value} x{BAND_COUNT} on {version_id}, "
              f"boundaries {list(proposed.boundaries)}, labels {list(proposed.labels)}")
    return bandings


async def fit_demo_models(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    analyst: Principal,
    dataset_id: UUID,
    version_id: UUID,
    bandings: dict[str, DemoBanding],
) -> dict[str, UUID]:
    """Create the demo factors and fit the GLM and the GBM.

    Returns `{"glm": model_id, "gbm": model_id}` for W7-2's comparison.
    """
    register_model_handlers()

    split = await _split_for(database, blob_store, workspace_id, analyst, version_id)
    print(f"  split {split.split_artifact_id} (train/test)")

    factor_ids: dict[str, UUID] = {}
    for slug, column in (*CONTINUOUS_FACTORS, *CATEGORICAL_FACTORS):
        banding = bandings.get(slug)
        factor_ids[slug] = await _create_factor(
            database, workspace_id, analyst, dataset_id, slug, column,
            None if banding is None else banding.id,
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


DEMO_SUITE_SLUG: Final = "fremtpl2-rate-suite"
DEMO_RATING_SLUG: Final = "fremtpl2-demo"
DEMO_CHANGE_NOTE: Final = (
    "priced from the approved freMTPL2 GLM through its seeded rate tables; the base premium is "
    f"{BASE_LABEL}"
)


def table_slug(factor: str) -> str:
    """A Factor's seeded Rate Table slug. The slug grammar has no `_` (`refs.py:_SLUG`), a
    Factor slug may (`_FACTOR_SLUG`), so `driv_age_band` seeds `fremtpl2-driv-age-band`."""
    return f"fremtpl2-{factor.replace('_', '-')}"


async def load_approved_glm(
    database: Database, workspace_id: UUID, model_id: UUID
) -> tuple[ArtifactRef, GlmFitResult]:
    """The approved GLM's ref and fit result."""
    async with database.session() as session:
        row = await session.get(ModelRow, model_id)
        if row is None:
            raise RuntimeError(f"the approved model {model_id} does not exist")
        model = model_service.to_model(row)
    fit = model.fit_result
    if not isinstance(fit, GlmFitResult):
        raise RuntimeError(f"the approved model {model_id} carries no GLM fit result")
    return ArtifactRef(type="model", slug=row.model_family_slug, version=row.version), fit


async def seed_demo_rate_tables(
    database: Database,
    settings: Any,
    blob_store: BlobStore,
    workspace_id: UUID,
    analyst: Principal,
    model_id: UUID,
) -> dict[str, ArtifactRef]:
    """One Rate Table per Factor of the approved GLM, seeded with `seed_from_model` (FR-230).

    Returns the refs by Factor slug, in `FACTOR_SET` order. A Factor the model has no
    relativities for stops the seed: the algorithm below prices on every one.
    """
    if analyst.id is None:
        raise RuntimeError("the demo analyst has no id")
    model_ref, fit = await load_approved_glm(database, workspace_id, model_id)
    absent = [factor for factor in FACTOR_SET if factor not in fit.relativities]
    if absent:
        raise RuntimeError(f"the approved GLM has no relativities for {absent}")
    tables: dict[str, ArtifactRef] = {}
    for factor in FACTOR_SET:
        version = await rate_table_service.seed_from_model(
            database, workspace_id, analyst.id, settings, blob_store,
            slug=table_slug(factor), model_ref=model_ref, factor=factor,
            change_note=f"seeded from the approved freMTPL2 GLM, factor {factor}",
        )
        tables[factor] = ArtifactRef(type="rate_table", slug=version.slug, version=version.version)
    print(f"  {len(tables)} rate tables seeded from {model_ref}: "
          + ", ".join(str(ref) for ref in tables.values()))
    return tables


async def demo_base_premium(
    database: Database, blob_store: BlobStore, workspace_id: UUID, model_id: UUID, version_id: UUID
) -> int:
    """DP-a2: `exp(intercept)` of the approved GLM times the mean claim cost of the seed's
    dataset version (Σ claim_amount_minor ÷ Σ claim_count), whole minor units. **A
    simplification** (frequency GLM x mean severity; no severity model)."""
    import polars as pl

    _, fit = await load_approved_glm(database, workspace_id, model_id)
    intercept = next(c.estimate for c in fit.coefficients if c.term == "intercept")
    async with database.session() as session:
        version = await dataset_service.read_version(
            session, workspace_id=workspace_id, version_id=version_id
        )
        raw = await read_stored_blob(
            session, blob_store, portfolio_table(version)["blob"]["sha256"], "The seed's table"
        )
    frame = pl.read_parquet(io.BytesIO(raw)).select("claim_amount_minor", "claim_count")
    totals = frame.select(
        pl.col("claim_amount_minor").cast(pl.Int64).sum().alias("amount"),
        pl.col("claim_count").cast(pl.Int64).sum().alias("claims"),
    ).row(0, named=True)
    mean_claim = Decimal(totals["amount"]) / Decimal(totals["claims"])
    base = base_premium_minor(Decimal(str(intercept)), mean_claim)
    print(f"  base premium {base} minor units = exp({intercept}) x mean claim cost "
          f"{mean_claim:.2f} ({totals['amount']} / {totals['claims']} claims on {version_id}); "
          f"{BASE_LABEL}")
    return base


@dataclass(frozen=True)
class GoldenCase:
    """A golden quote: its inputs, the Factor levels they fall on, and the premium the GLM gives
    them, computed from the coefficients and never from the scored bundle."""

    name: str
    inputs: dict[str, Any]
    expected_minor: int


def demo_golden_cases(
    fit: GlmFitResult, bandings: dict[str, DemoBanding], base_minor: int
) -> list[GoldenCase]:
    """Three quotes: every Factor at its base level; at its first non-base level; at its last
    level. A banded Factor's raw value is the lower edge of the band it is on, so the cases sit
    on band edges (PL-1525 Acceptance 3)."""
    import polars as pl

    from pricing_core.modelling.bandings import apply_banding

    picks = {
        "base-levels": lambda levels: next(r for r in levels if r.is_base),
        "first-non-base-levels": lambda levels: next(r for r in levels if not r.is_base),
        "last-levels": lambda levels: levels[-1],
    }
    cases = []
    for name, pick in picks.items():
        inputs: dict[str, Any] = {"bonus_malus": 100}
        levels_by_factor: dict[str, str] = {}
        for factor in FACTOR_SET:
            level = pick(fit.relativities[factor]).level
            levels_by_factor[factor] = level
            demo = bandings.get(factor)
            if demo is None:
                inputs[factor] = level
            else:
                value = math.ceil(demo.banding.boundaries[demo.banding.labels.index(level)])
                labelled = apply_banding(pl.Series("v", [value]), demo.banding)[0]
                if labelled != level:
                    raise RuntimeError(
                        f"{factor}: the edge value {value} falls in band {labelled!r}, "
                        f"not {level!r}"
                    )
                inputs[demo.banding.column] = value
        expected = glm_premium_minor(
            fit.coefficients, fit.relativities, base_minor, levels_by_factor
        )
        cases.append(GoldenCase(name, inputs, expected))
    return cases


def monotone_property(
    fit: GlmFitResult, bandings: dict[str, DemoBanding]
) -> dict[str, Any] | None:
    """One `monotone` property on a banded Factor whose fitted relativities rise or fall with
    its bands (FR-261); `None` when none does. The Factor and its relativities are printed, for
    the ledger."""
    for factor, demo in bandings.items():
        by_level = {r.level: r.relativity for r in fit.relativities[factor]}
        series = [by_level[label] for label in demo.banding.labels]
        if any(value is None for value in series):
            continue
        direction = (
            "increasing" if all(a <= b for a, b in pairwise(series))
            else "decreasing" if all(a >= b for a, b in pairwise(series))
            else None
        )
        if direction is not None:
            print(f"  monotone property: {demo.banding.column} {direction}; "
                  f"relativities by band {dict(zip(demo.banding.labels, series, strict=True))}")
            return {"name": f"premium-monotone-in-{demo.banding.column}",
                    "check": {"kind": "monotone", "input": demo.banding.column,
                              "direction": direction}}
    return None


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
    database: Database, workspace_id: UUID, analyst: Principal,
    tables: dict[str, ArtifactRef], bandings: dict[str, DemoBanding],
    domains: dict[str, list[str]], base_minor: int,
) -> ArtifactRef:
    """Save the freMTPL2 algorithm through the service; a re-seed's 409 is tolerated."""
    if analyst.id is None:
        raise RuntimeError("the demo analyst has no id")
    payload = build_fremtpl2_algorithm(
        tables=tables, bandings={slug: d.banding for slug, d in bandings.items()},
        base_minor=base_minor, domains=domains,
    )
    try:
        await algorithm_service.create_algorithm(database, workspace_id, analyst.id, payload)
    except PlatformError as exc:  # a re-seed: the algorithm is already saved
        if exc.status_code != 409:
            raise
    return ArtifactRef(type="rating_algorithm", slug=FREMTPL2_ALGORITHM_SLUG, version=1)


async def author_demo_rating_evidence(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    analyst: Principal,
    rating_id: UUID,
    cases: list[GoldenCase],
    monotone: dict[str, Any] | None,
) -> UUID:
    """Give a draft rating version its executed FR-257 limb (1) evidence (DP-S3-8, T6b).

    **Every piece is produced by the real path, none inserted**: the version arrives with its
    algorithm and pins declared at create; it is compiled by the `rating.compile` Job; the
    golden quotes' expected premiums are the GLM's (`cases`, computed from the fitted
    coefficients, **not** from the compiled bundle: a golden quote whose expectation was
    `score_one` on the bundle under test could not fail); and the regression runs through the
    `rating.regression` Job, whose handler calls `run_regression` and persists the run. No
    `RegressionRun` row and no pass verdict is written here. Returns the regression run's id.
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

    golden = []
    for case in cases:
        context = QuoteContext.model_validate({
            "purpose": "new_business", "quoted_at": "2026-09-28T09:00:00",
            "effective_date": "2026-10-01", "inputs": case.inputs,
            "options": {"rating_version_ref": str(ref)},
        })
        golden.append({
            "name": f"{FREMTPL2_ALGORITHM_SLUG}-{case.name}",
            "context": context.model_dump(mode="json", exclude={"options"}),
            "expected": {"payable_premium_minor": case.expected_minor, "outcome": "quoted"},
            "tolerance": {"money_minor": 0},
            "note": f"the approved GLM's premium for {case.name}, computed from its coefficients",
        })
    properties = [
        {"name": "no-null-output", "check": {"kind": "no_null_output"}},
        {"name": "premium-bounded", "check": {"kind": "premium_bounded", "lower_minor": 0}},
    ]
    if monotone is not None:
        properties.append(monotone)
    suite = RegressionSuiteContent.model_validate({
        "algorithm_slug": FREMTPL2_ALGORITHM_SLUG,
        "golden_quotes": golden,
        "properties": properties,
        "generation": {"cases": 25, "seed": SPLIT_SEED, "strategy": "input_contract_sampling"},
    })
    async with database.unit_of_work() as session:
        await suite_service.create_suite_version(
            session, workspace_id=workspace_id, actor=analyst, slug=DEMO_SUITE_SLUG,
            content=suite, change_note=DEMO_CHANGE_NOTE,
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
    tables: dict[str, ArtifactRef],
    bandings: dict[str, DemoBanding],
    base_minor: int,
) -> UUID:
    """W7-3: create, submit and approve the demo rating version (FR-440).

    The rating version is priced from the approved GLM: it pins the freMTPL2 algorithm, the
    approved model as `model:{slug}@{version}`, and every seeded Rate Table at its seeded
    version (FR-237), so the exit demo's rating version is addressable and its approval is
    auditable. It carries **executed** regression evidence (`author_demo_rating_evidence`)
    whose golden quotes are the GLM's own premiums, and two approvers decide it (`06` §4.2).
    """
    model_ref, fit = await load_approved_glm(database, workspace_id, model_id)
    domains = {
        factor: [r.level for r in fit.relativities[factor]]
        for factor, _ in CATEGORICAL_FACTORS
    }
    algorithm_ref = await save_demo_algorithm(
        database, workspace_id, analyst, tables, bandings, domains, base_minor
    )
    async with database.unit_of_work() as session:
        row = await rating_versions_service.create_rating_version(
            session, workspace_id=workspace_id, actor=analyst,
            slug=DEMO_RATING_SLUG, dataset_version_id=dataset_version_id, model_ref=model_ref,
            algorithm_ref=algorithm_ref,
            pins=Pins(rate_tables=list(tables.values()), models=[model_ref]),
        )
        rating_id = row.id

    run_id = await author_demo_rating_evidence(
        database, blob_store, workspace_id, analyst, rating_id,
        demo_golden_cases(fit, bandings, base_minor), monotone_property(fit, bandings),
    )

    await submit_and_approve_demo(
        database, blob_store, workspace_id, actuary, approver, second_approver, rating_id
    )
    print(f"  rating version approved: {rating_id} (regression run {run_id}, priced from the "
          f"approved GLM; the base premium is {BASE_LABEL})")
    return rating_id
