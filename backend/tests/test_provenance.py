"""Every one of the ten read routes answers with a composed `provenance` (FR-2159, FR-6).

Decided on #1506: #1519 (b), a read-side `Provenance` composed by the API and never
persisted; #1868 (a), the shape's own `entity_type` and UUID `entity_id` plus `subject_refs`
in the `refs` form, never empty where a governed parent exists, in a stated order for
`ModelComparison` (`summary.model_refs` order), `DislocationRun` (baseline, then candidate) and
`RegressionRun` (suite, then rating version); the object omits `computed_at`; the persisted
classes, their stored rows and every stored hash are untouched.

For each of the ten shapes, one artifact is stored through the platform's own writer where
one exists (`store_report`, `store_profile`, `record_comparison`, `record_backtest`,
`persist_run` twice, `record_certificate` twice, `record_transparency`), with a known Job id,
and read back through its route. The test then checks:

* `provenance.produced_by_job_id` equals the `job_id` **read back from the stored row**
  (the column, and the stored JSON where the shape keeps it there), not the seed's variable;
* `entity_type` and `entity_id` name the artifact the route was asked for;
* `subject_refs` is non-empty, every entry is a canonical `{type}:{slug}@{version}` string,
  and it names the governed parent; for the three ordered shapes it is exactly the stated
  sequence;
* the artifact row and its seeded parents' rows, every column (stored JSON and stored hashes
  included), are identical before and after the read, and no stored JSON gained a
  `provenance` key.

**Rows are inserted rather than produced by Jobs**, for `test_api_backtests`' reason: these
routes read and compose; how a Job produced the row is each artifact's own test file's
concern. `Diagnostics` has no writer outside the fit, so its row is inserted directly
(`_fitted_model_with_diagnostics`), with a payload built through `model-schema`.

Red before slice 2: every response lacks the `provenance` key, and the published OpenAPI
document has no `Provenance` component.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from backend.tests.test_api_backtests import _run, _seed_model_and_version
from backend.tests.test_api_datasets import _headers
from backend.tests.test_contracts import OPENAPI, _load
from backend.tests.test_custom_metrics_api import _create as _create_metric
from backend.tests.test_custom_objectives import _objective
from backend.tests.test_data_jobs import CLEAN, _ingest, _seed_dataset_and_rules
from backend.tests.test_dislocation_runs import _persist as _persist_dislocation_run
from backend.tests.test_dislocation_runs import _run as _dislocation_run
from backend.tests.test_model_jobs import _actuary
from backend.tests.test_regression_runs import _persist as _persist_regression_run
from backend.tests.test_regression_runs import _rating_version
from backend.tests.test_regression_runs import _run as _regression_run
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select

from app.db.models import (
    BacktestRow,
    CustomMetricRow,
    CustomObjectiveRow,
    DatasetVersionRow,
    DiagnosticsRow,
    DislocationRunRow,
    MetricCertificateRow,
    ModelComparisonRow,
    ModelRow,
    ObjectiveCertificateRow,
    ProfileRow,
    RatingVersionRow,
    RegressionRunRow,
    TransparencyArtifactRow,
    ValidationReportRow,
)
from app.db.session import Database
from app.platform import backtests as backtest_service
from app.platform import comparison as comparison_service
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import metrics as metric_service
from app.platform import objectives as objective_service
from app.platform import profiles as profile_service
from app.platform import provenance as provenance_service
from app.platform import transparency as transparency_service
from app.platform import validation as validation_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.tasks import execute_job
from model_schema import (
    METRIC_CERTIFICATE_CHECKS,
    OBJECTIVE_CERTIFICATE_CHECKS,
    ArtifactRef,
    BacktestSummary,
    CertificateCheck,
    CertificateOutcome,
    CertificateResult,
    CheckStatus,
    ComparisonSummary,
    ComplexityDiagnostic,
    Diagnostics,
    EbmShapeFunctions,
    GlmSpec,
    JobKind,
    JobStatus,
    ModelStatus,
    OffsetSpec,
    PartitionDiagnostics,
    Principal,
    Profile,
    RegressionRun,
    RuleOutcome,
    RuleResult,
    SamplingSpec,
    Severity,
    SplitRef,
    TransparencyArtifact,
    UniversalDiagnostics,
    ValidationLayer,
    ValidationReport,
    Weighting,
    new_uuid7,
)

# -- The caller ----------------------------------------------------------------------------


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    return api_client


@pytest_asyncio.fixture
async def reader(workspace_id, principal, grant) -> dict[str, str]:
    """`auditor` for every read permission the ten routes need (`dataset:read`, `model:read`,
    `rating:read`); `analyst` because two writers the seeds call (`create_objective`, the
    custom-metric create route) require `model:fit` of the actor."""
    await grant("analyst")
    await grant("auditor")
    return _headers(principal.id, workspace_id)


@dataclass(frozen=True)
class _Context:
    workspace_id: UUID
    actor: Principal
    client: TestClient
    headers: dict[str, str]


@dataclass(frozen=True)
class Seeded:
    """One stored artifact and what its read must say about it."""

    url: str
    entity_type: str
    entity_id: UUID
    #: Exactly the refs `subject_refs` holds (FR-2159: one for a shape with a single governed
    #: parent). With `ordered`, also in this order.
    parents: tuple[str, ...]
    ordered: bool
    #: The artifact's own row first, then the seeded parents' rows, by ORM class and id.
    rows: tuple[tuple[type, UUID], ...]


_JSON_COLUMNS = ("body", "payload", "run")


def _snapshot(rows: tuple[tuple[type, UUID], ...]) -> list[dict[str, Any]]:
    """Every column of every row, read on a fresh engine, so nothing is a cached object."""

    async def read(database: Database) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        async with database.session() as session:
            for cls, row_id in rows:
                row = await session.get(cls, row_id)
                assert row is not None, f"seeded {cls.__name__} {row_id} is not stored"
                out.append({attr.key: getattr(row, attr.key) for attr in inspect(cls).column_attrs})
        return out

    return _run(read)


def _stored_job_ids(artifact_row: dict[str, Any]) -> set[str]:
    """The job id as the artifact row stores it: the `job_id` column where the table has one,
    and the `job_id` key of the stored JSON where the shape keeps it there (`RegressionRun`'s
    only home for it is `regression_runs.run`)."""
    found: set[str] = set()
    if "job_id" in artifact_row and artifact_row["job_id"] is not None:
        found.add(str(artifact_row["job_id"]))
    for column in _JSON_COLUMNS:
        stored = artifact_row.get(column)
        if isinstance(stored, dict) and stored.get("job_id") is not None:
            found.add(str(stored["job_id"]))
    return found


# -- The ten seeds -------------------------------------------------------------------------


def _dataset_version(ctx: _Context) -> tuple[DatasetVersionRow, str]:
    """A real Dataset and its first Version, and the version's canonical ref."""

    async def make(database: Database) -> tuple[DatasetVersionRow, str]:
        async with database.unit_of_work() as session:
            dataset = await dataset_service.create_dataset(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                slug=f"ds-{new_uuid7().hex[-8:]}",
            )
            version = await dataset_service.new_version(
                session, workspace_id=ctx.workspace_id, actor=ctx.actor, dataset_id=dataset.id
            )
            return version, f"dataset_version:{dataset.slug}@{version.version}"

    return _run(make)


def _validation_report(ctx: _Context) -> Seeded:
    version, version_ref = _dataset_version(ctx)
    job_id = new_uuid7()
    started = datetime.now(UTC)
    report = ValidationReport(
        id=uuid4(),
        dataset_version_id=version.id,
        rule_set_id=uuid4(),
        rule_set_version=1,
        job_id=job_id,
        started_at=started,
        finished_at=started + timedelta(seconds=1),
        results=(
            RuleResult(
                rule_id=uuid4(),
                rule_slug="severity-outlier",
                rule_version=1,
                layer=ValidationLayer.ACTUARIAL_SANITY,
                severity=Severity.WARN,
                outcome=RuleOutcome.WARN,
                detail="12 claims above the outlier threshold",
            ),
        ),
    )

    async def store(database: Database) -> None:
        async with database.unit_of_work() as session:
            await validation_service.store_report(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                report=report,
                job_id=job_id,
            )

    _run(store)
    return Seeded(
        url=f"/api/v1/validation-reports/{report.id}",
        entity_type="validation_report",
        entity_id=report.id,
        parents=(version_ref,),
        ordered=False,
        rows=((ValidationReportRow, report.id), (DatasetVersionRow, version.id)),
    )


def _profile(ctx: _Context) -> Seeded:
    version, version_ref = _dataset_version(ctx)
    job_id = new_uuid7()
    profile = Profile(
        id=new_uuid7(),
        dataset_version_id=version.id,
        computed_at=datetime.now(UTC),
        job_id=job_id,
        row_count=0,
    )

    async def store(database: Database) -> None:
        async with database.unit_of_work() as session:
            await profile_service.store_profile(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                profile=profile,
                job_id=job_id,
            )

    _run(store)
    return Seeded(
        url=f"/api/v1/dataset-versions/{version.id}/profile",
        entity_type="profile",
        entity_id=profile.id,
        parents=(version_ref,),
        ordered=False,
        rows=((ProfileRow, profile.id), (DatasetVersionRow, version.id)),
    )


def _partition() -> PartitionDiagnostics:
    return PartitionDiagnostics(
        weighting=Weighting.EXPOSURE, rows=400, ae_overall=1.0, gini=0.3, gini_normalised=0.4
    )


def _fitted_model_with_diagnostics(workspace_id: UUID, *, job_id: UUID) -> tuple[ModelRow, UUID]:
    """A `fitted` model and its stored `Diagnostics`, the payload built through `model-schema`.

    `_seed_model_and_version` (`test_api_backtests`) stores `{"seeded": True}` as the
    diagnostics payload, which `to_diagnostics` refuses, so `GET .../diagnostics` cannot read
    it; this is the same insert with a valid payload and a Job id. `diagnostics` is
    append-only (`test_diagnostics_cannot_be_rewritten`), so a valid row cannot be patched in.
    """

    async def insert(database: Database) -> tuple[ModelRow, UUID]:
        async with database.unit_of_work() as session:
            version = DatasetVersionRow(
                workspace_id=workspace_id,
                dataset_id=new_uuid7(),
                version=1,
                status="validated",
                validation_report_id=new_uuid7(),
                tables=[],
                slug="motor-gb",
                created_by=new_uuid7(),
                currency="GBP",
            )
            session.add(version)
            await session.flush()
            family = f"motor-{new_uuid7().hex[-8:]}"
            spec = GlmSpec(
                model_family_slug=family,
                dataset_version_id=version.id,
                response_column="claim_count",
                offset=OffsetSpec(kind="log_column", column="exposure_years"),
            )
            model = ModelRow(
                workspace_id=workspace_id,
                model_family_slug=family,
                version=1,
                status=ModelStatus.FITTED.value,
                dataset_version_id=version.id,
                spec=spec.model_dump(mode="json"),
                spec_hash=f"v3:sha256:{new_uuid7().hex}{new_uuid7().hex}",
                fit_result={"converged": True},
                diagnostics_id=new_uuid7(),
            )
            session.add(model)
            await session.flush()
            computed_at = datetime.now(UTC)
            diagnostics = Diagnostics(
                id=model.diagnostics_id,
                model_id=model.id,
                computed_at=computed_at,
                job_id=job_id,
                universal=UniversalDiagnostics(train=_partition(), holdout=_partition()),
                complexity=ComplexityDiagnostic(factor_count=0, parameter_count=1),
            )
            session.add(
                DiagnosticsRow(
                    id=model.diagnostics_id,
                    workspace_id=workspace_id,
                    model_id=model.id,
                    computed_at=computed_at,
                    job_id=job_id,
                    payload=diagnostics.model_dump(
                        mode="json", exclude={"id", "model_id", "computed_at", "job_id"}
                    ),
                )
            )
            return model, model.diagnostics_id

    return _run(insert)


def _model_row(model_id: UUID) -> ModelRow:
    async def read(database: Database) -> ModelRow:
        async with database.session() as session:
            row = await session.get(ModelRow, model_id)
            assert row is not None
            return row

    return _run(read)


def _diagnostics(ctx: _Context) -> Seeded:
    model, diagnostics_id = _fitted_model_with_diagnostics(ctx.workspace_id, job_id=new_uuid7())
    return Seeded(
        url=f"/api/v1/models/{model.model_family_slug}/diagnostics?version={model.version}",
        entity_type="diagnostics",
        entity_id=diagnostics_id,
        parents=(f"model:{model.model_family_slug}@{model.version}",),
        ordered=False,
        rows=((DiagnosticsRow, diagnostics_id), (ModelRow, model.id)),
    )


def _model_comparison(ctx: _Context) -> Seeded:
    """Three models, the baseline in the middle: the order asserted is `summary.model_refs`',
    which a baseline-first composition would get wrong."""
    first, baseline, third = "model:motor-c@4", "model:motor-a@1", "model:motor-b@2"
    summary = ComparisonSummary(
        model_refs=(first, baseline, third),
        baseline_ref=baseline,
        split_ref=SplitRef(split_artifact_id=new_uuid7(), train_part="train", holdout_part="test"),
        holdout_rows=10,
    )
    job_id = new_uuid7()

    async def store(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = await comparison_service.record_comparison(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                summary=summary,
                job_id=job_id,
            )
            return row.id

    comparison_id = _run(store)
    return Seeded(
        url=f"/api/v1/models/comparisons/{comparison_id}",
        entity_type="model_comparison",
        entity_id=comparison_id,
        parents=(first, baseline, third),
        ordered=True,
        rows=((ModelComparisonRow, comparison_id),),
    )


def _backtest(ctx: _Context) -> Seeded:
    model_id, version_id = _seed_model_and_version(ctx.workspace_id)
    model = _model_row(model_id)
    model_ref = f"model:{model.model_family_slug}@{model.version}"
    # `_seed_model_and_version` names both versions `motor-gb`, at 1 (fitted on) and 2.
    version_ref, fitted_on_ref = "dataset_version:motor-gb@2", "dataset_version:motor-gb@1"
    summary = BacktestSummary(
        model_ref=model_ref,
        dataset_version_ref=version_ref,
        fitted_on_ref=fitted_on_ref,
        partition=_partition(),
    )
    job_id = new_uuid7()

    async def store(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = await backtest_service.record_backtest(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                model_id=model_id,
                dataset_version_id=version_id,
                summary=summary,
                job_id=job_id,
            )
            return row.id

    backtest_id = _run(store)
    return Seeded(
        url=f"/api/v1/models/backtests/{backtest_id}",
        entity_type="backtest",
        entity_id=backtest_id,
        # FR-2159 names the Model as a Backtest's single governed parent; the version it ran
        # against stays in `summary.dataset_version_ref`, beside the provenance.
        parents=(model_ref,),
        ordered=False,
        rows=((BacktestRow, backtest_id), (ModelRow, model_id)),
    )


def _regression_run_seed(ctx: _Context) -> Seeded:
    rating_version_id = _run(lambda database: _rating_version(database, ctx.workspace_id))
    suite_ref, rating_version_ref = "regression_suite:motor-gb-core@3", "rating_version:motor-gb@1"
    run = RegressionRun.model_validate(
        {
            **_regression_run().model_dump(mode="json", by_alias=True),
            "suite_ref": suite_ref,
            "rating_version_ref": rating_version_ref,
            "job_id": str(new_uuid7()),
        }
    )
    run_id = _run(
        lambda database: _persist_regression_run(database, ctx.workspace_id, rating_version_id, run)
    )
    return Seeded(
        url=f"/api/v1/rating-versions/{rating_version_id}/regression-runs/{run_id}",
        entity_type="regression_run",
        entity_id=run_id,
        parents=(suite_ref, rating_version_ref),
        ordered=True,
        rows=((RegressionRunRow, run_id), (RatingVersionRow, rating_version_id)),
    )


def _dislocation_run_seed(ctx: _Context) -> Seeded:
    run = _dislocation_run(job_id=new_uuid7())
    run_id = _run(lambda database: _persist_dislocation_run(database, ctx.workspace_id, run))
    return Seeded(
        url=f"/api/v1/dislocation-runs/{run_id}",
        entity_type="dislocation_run",
        entity_id=run_id,
        parents=(str(run.baseline_ref), str(run.candidate_ref)),
        ordered=True,
        rows=((DislocationRunRow, run_id),),
    )


def _certificate_result(names: tuple[str, ...]) -> CertificateResult:
    return CertificateResult(
        checks=tuple(
            CertificateCheck(name=name, status=CheckStatus.PASS, detail="seeded for the read")
            for name in names
        ),
        sampling=SamplingSpec(
            n_points=1_000, seed=7, y_range=(0.0, 20.0), f_range=(-5.0, 4.0), w_range=(0.01, 10.0)
        ),
        overall=CertificateOutcome.CERTIFIED,
    )


def _objective_certificate(ctx: _Context) -> Seeded:
    objective = _run(lambda database: _objective(database, ctx.workspace_id, ctx.actor))
    job_id = new_uuid7()

    async def store(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            _, certificate = await objective_service.record_certificate(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                objective_id=objective.id,
                result=_certificate_result(OBJECTIVE_CERTIFICATE_CHECKS),
                job_id=job_id,
            )
            return certificate.id

    certificate_id = _run(store)
    return Seeded(
        url=f"/api/v1/custom-objectives/{objective.id}/certificate",
        entity_type="objective_certificate",
        entity_id=certificate_id,
        parents=(f"custom_objective:{objective.slug}@{objective.version}",),
        ordered=False,
        rows=((ObjectiveCertificateRow, certificate_id), (CustomObjectiveRow, objective.id)),
    )


def _metric_certificate(ctx: _Context) -> Seeded:
    metric = _create_metric(ctx.client, ctx.headers)
    metric_id = UUID(metric["id"])
    job_id = new_uuid7()

    async def store(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            _, certificate = await metric_service.record_certificate(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                metric_id=metric_id,
                result=_certificate_result(METRIC_CERTIFICATE_CHECKS),
                job_id=job_id,
            )
            return certificate.id

    certificate_id = _run(store)
    return Seeded(
        url=f"/api/v1/custom-metrics/{metric_id}/certificate",
        entity_type="metric_certificate",
        entity_id=certificate_id,
        parents=(f"custom_metric:{metric['slug']}@{metric['version']}",),
        ordered=False,
        rows=((MetricCertificateRow, certificate_id), (CustomMetricRow, metric_id)),
    )


def _transparency_artifact(ctx: _Context) -> Seeded:
    model_id, _ = _seed_model_and_version(ctx.workspace_id)
    model = _model_row(model_id)
    artifact = TransparencyArtifact(
        id=new_uuid7(),
        model_id=model_id,
        created_at=datetime.now(UTC),
        fidelity_statement="the EBM's shape functions are the model, exported as tables",
        ebm_shape_functions=EbmShapeFunctions(terms_blob="{}"),
    )
    job_id = new_uuid7()

    async def store(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = await transparency_service.record_transparency(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                model_id=model_id,
                artifact=artifact,
                job_id=job_id,
            )
            return row.id

    artifact_id = _run(store)
    return Seeded(
        url=f"/api/v1/models/{model_id}/transparency",
        entity_type="transparency_artifact",
        entity_id=artifact_id,
        parents=(f"model:{model.model_family_slug}@{model.version}",),
        ordered=False,
        rows=((TransparencyArtifactRow, artifact_id), (ModelRow, model_id)),
    )


SEEDS: dict[str, Callable[[_Context], Seeded]] = {
    "validation_report": _validation_report,
    "profile": _profile,
    "diagnostics": _diagnostics,
    "model_comparison": _model_comparison,
    "backtest": _backtest,
    "regression_run": _regression_run_seed,
    "objective_certificate": _objective_certificate,
    "dislocation_run": _dislocation_run_seed,
    "metric_certificate": _metric_certificate,
    "transparency_artifact": _transparency_artifact,
}

ORDERED = ("model_comparison", "dislocation_run", "regression_run")


def _read(
    shape: str, client: TestClient, headers: dict[str, str], workspace_id: UUID, actor: Principal
) -> tuple[Seeded, dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Seed, snapshot, read through the route, snapshot again."""
    seeded = SEEDS[shape](_Context(workspace_id, actor, client, headers))
    before = _snapshot(seeded.rows)
    response = client.get(seeded.url, headers=headers)
    assert response.status_code == 200, response.text
    after = _snapshot(seeded.rows)
    return seeded, response.json(), before, after


# -- The tests -----------------------------------------------------------------------------


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
@pytest.mark.parametrize("shape", list(SEEDS))
def test_the_read_carries_provenance_composed_from_the_stored_row(
    shape: str,
    client: TestClient,
    reader: dict[str, str],
    workspace_id: UUID,
    principal: Principal,
) -> None:
    seeded, body, before, after = _read(shape, client, reader, workspace_id, principal)

    # Nothing the read touched was written: the artifact row and its parents' rows, every
    # column, stored JSON and stored hashes included. Checked first so that the red below
    # can only be the missing key.
    assert after == before
    for row in after:
        for column in _JSON_COLUMNS:
            stored = row.get(column)
            if isinstance(stored, dict):
                assert "provenance" not in stored, f"{shape}: provenance was persisted"

    stored_job_ids = _stored_job_ids(before[0])
    assert len(stored_job_ids) == 1, f"{shape}: the row stores {stored_job_ids!r}"
    (stored_job_id,) = stored_job_ids

    assert "provenance" in body, f"{shape}: the read carries no provenance"
    provenance = body["provenance"]
    assert provenance["produced_by_job_id"] == stored_job_id
    assert provenance["entity_type"] == seeded.entity_type
    assert provenance["entity_id"] == str(seeded.entity_id)
    assert "computed_at" not in provenance

    refs = provenance["subject_refs"]
    assert refs, f"{shape} has a governed parent, so subject_refs is never empty (#1868)"
    for ref in refs:
        assert str(ArtifactRef.parse(ref)) == ref, f"{shape}: {ref!r} is not in the refs form"
    for parent in seeded.parents:
        assert parent in refs, f"{shape}: {parent!r} is missing from {refs!r}"
    # FR-2159: one reference for each shape with a single governed parent, nothing beside it.
    assert sorted(refs) == sorted(seeded.parents), f"{shape}: {refs!r}"

    # The persisted shape is still all there: the read is the shape plus one key.
    assert body.get("job_id", stored_job_id) == stored_job_id


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
@pytest.mark.parametrize("shape", ORDERED)
def test_the_subject_refs_are_in_the_stated_order(
    shape: str,
    client: TestClient,
    reader: dict[str, str],
    workspace_id: UUID,
    principal: Principal,
) -> None:
    """#1868's condition: `ModelComparison` in `summary.model_refs` order (the seed puts the
    baseline second, so baseline-first fails), `DislocationRun` baseline then candidate,
    `RegressionRun` suite then rating version. Exactly these, nothing else between them."""
    seeded, body, _, _ = _read(shape, client, reader, workspace_id, principal)
    assert seeded.ordered
    assert "provenance" in body, f"{shape}: the read carries no provenance"
    assert body["provenance"]["subject_refs"] == list(seeded.parents)


# -- The published contract ----------------------------------------------------------------

ROUTES: dict[str, str] = {
    "validation_report": "/api/v1/validation-reports/{report_id}",
    "profile": "/api/v1/dataset-versions/{version_id}/profile",
    "diagnostics": "/api/v1/models/{slug}/diagnostics",
    "model_comparison": "/api/v1/models/comparisons/{comparison_id}",
    "backtest": "/api/v1/models/backtests/{backtest_id}",
    "regression_run": "/api/v1/rating-versions/{rating_version_id}/regression-runs/{run_id}",
    "objective_certificate": "/api/v1/custom-objectives/{objective_id}/certificate",
    "dislocation_run": "/api/v1/dislocation-runs/{run_id}",
    "metric_certificate": "/api/v1/custom-metrics/{metric_id}/certificate",
    "transparency_artifact": "/api/v1/models/{model_id}/transparency",
}


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
@pytest.mark.parametrize("shape", list(ROUTES))
def test_the_published_response_of_each_read_route_declares_provenance(shape: str) -> None:
    """The generated client (slice 3) reads `Provenance` from this document, so each 200 must
    reference a schema that carries `provenance`, and `Provenance` must be a component."""
    document = _load(OPENAPI)
    schemas = document["components"]["schemas"]
    assert "Provenance" in schemas, "the published document has no Provenance component"
    ok = document["paths"][ROUTES[shape]]["get"]["responses"]["200"]
    ref = ok["content"]["application/json"]["schema"]["$ref"]
    response_schema = schemas[ref.rsplit("/", 1)[-1]]
    assert response_schema["properties"]["provenance"] == {
        "$ref": "#/components/schemas/Provenance"
    }
    assert "provenance" in response_schema["required"]


# -- The Validation Report's Job (#1506 item 4) ----------------------------------------------


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
async def test_a_validation_job_records_itself_on_the_report_row_and_the_read_shows_it(
    database: Database, blob_store: BlobStore, workspace_id: UUID
) -> None:
    """`dataset.validate` passes its own Job's id when it stores the report.

    Before #1506 item 4 the worker called `store_report` without `job_id`, so every report a
    real Job wrote carried a null `validation_reports.job_id`, and its `provenance` would read
    "not recorded" for every real report.

    **On the row only** (the maintainer's condition): `test_validation_is_deterministic`
    compares two reports' bodies with `job_id` included (NFR-469), so the body stays without
    it and two runs on one Dataset Version still give equal bodies. The read takes the id
    from the row: the response's `job_id` and `provenance.produced_by_job_id` are both it.
    """
    register_data_handlers()
    actor = await _actuary(database, workspace_id)
    dataset_id = await _seed_dataset_and_rules(database, blob_store, workspace_id, actor)
    version_id = await _ingest(database, blob_store, workspace_id, actor, dataset_id, CLEAN)

    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.DATASET_VALIDATE,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "dataset_version_id": str(version_id),
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        row = (
            await session.execute(
                select(ValidationReportRow).where(
                    ValidationReportRow.workspace_id == workspace_id,
                    ValidationReportRow.dataset_version_id == version_id,
                )
            )
        ).scalar_one()
        assert row.job_id == job.id, "the report row does not record the Job that produced it"
        assert row.body.get("job_id") is None, "the Job id went into the body, not the row only"

        view = await validation_service.load_report_view(
            session, workspace_id=workspace_id, report_id=row.id
        )
        read = await provenance_service.validation_report_read(
            session, workspace_id=workspace_id, view=view
        )
    assert read.job_id == job.id
    assert read.provenance.produced_by_job_id == job.id


# -- A governed parent the refs form cannot name ---------------------------------------------

#: A model family slug outside the refs grammar. Nothing holds family slugs to it (#1506's
#: comment of 2026-11-19), so a stored model can carry one.
_OFF_GRAMMAR = "Motor_Freq"


def _rename_model(model_id: UUID) -> None:
    from sqlalchemy import update

    async def rename(database: Database) -> None:
        async with database.unit_of_work() as session:
            await session.execute(
                update(ModelRow)
                .where(ModelRow.id == model_id)
                .values(model_family_slug=_OFF_GRAMMAR)
            )

    _run(rename)


def _off_grammar_diagnostics(ctx: _Context) -> tuple[str, tuple[str, ...]]:
    model, _ = _fitted_model_with_diagnostics(ctx.workspace_id, job_id=new_uuid7())
    _rename_model(model.id)
    return f"/api/v1/models/{_OFF_GRAMMAR}/diagnostics?version={model.version}", ()


def _off_grammar_transparency(ctx: _Context) -> tuple[str, tuple[str, ...]]:
    seeded = _transparency_artifact(ctx)
    _rename_model(seeded.rows[1][1])
    return seeded.url, ()


def _off_grammar_backtest(ctx: _Context) -> tuple[str, tuple[str, ...]]:
    return _backtest_with_stored_ref(ctx, f"model:{_OFF_GRAMMAR}@1")


def _malformed_ref_backtest(ctx: _Context) -> tuple[str, tuple[str, ...]]:
    """A stored ref that cannot be read for a reason other than its slug: a version that is
    not an integer."""
    return _backtest_with_stored_ref(ctx, "model:motor-freq@v2")


def _backtest_with_stored_ref(ctx: _Context, model_ref: str) -> tuple[str, tuple[str, ...]]:
    model_id, version_id = _seed_model_and_version(ctx.workspace_id)
    summary = BacktestSummary(
        model_ref=model_ref,
        dataset_version_ref="dataset_version:motor-gb@2",
        fitted_on_ref="dataset_version:motor-gb@1",
        partition=_partition(),
    )

    async def store(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = await backtest_service.record_backtest(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                model_id=model_id,
                dataset_version_id=version_id,
                summary=summary,
                job_id=new_uuid7(),
            )
            return row.id

    return f"/api/v1/models/backtests/{_run(store)}", ()


def _off_grammar_comparison(ctx: _Context) -> tuple[str, tuple[str, ...]]:
    named, unnamed, baseline = "model:motor-c@4", f"model:{_OFF_GRAMMAR}@1", "model:motor-a@1"
    summary = ComparisonSummary(
        model_refs=(named, unnamed, baseline),
        baseline_ref=baseline,
        split_ref=SplitRef(split_artifact_id=new_uuid7(), train_part="train", holdout_part="test"),
        holdout_rows=10,
    )

    async def store(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = await comparison_service.record_comparison(
                session,
                workspace_id=ctx.workspace_id,
                actor=ctx.actor,
                summary=summary,
                job_id=new_uuid7(),
            )
            return row.id

    return f"/api/v1/models/comparisons/{_run(store)}", (named, baseline)


OFF_GRAMMAR_SEEDS: dict[str, Callable[[_Context], tuple[str, tuple[str, ...]]]] = {
    "diagnostics": _off_grammar_diagnostics,
    "transparency_artifact": _off_grammar_transparency,
    "backtest": _off_grammar_backtest,
    "model_comparison": _off_grammar_comparison,
    "backtest_malformed_stored_ref": _malformed_ref_backtest,
}


@pytest.mark.req("FR-2159")
@pytest.mark.parametrize("shape", list(OFF_GRAMMAR_SEEDS))
def test_a_parent_the_refs_form_cannot_name_is_counted_and_the_read_never_fails(
    shape: str,
    client: TestClient,
    reader: dict[str, str],
    workspace_id: UUID,
    principal: Principal,
) -> None:
    """A model whose family slug is outside the refs grammar: the read answers 200, as it does
    without provenance, and its provenance counts the parent it could not name rather than
    failing or leaving it out silently (`00` FR-2159's note of 2026-11-19, pending the
    maintainer's answer). The parents it can name are still listed, in their order."""
    url, named = OFF_GRAMMAR_SEEDS[shape](_Context(workspace_id, principal, client, reader))
    response = client.get(url, headers=reader)
    assert response.status_code == 200, response.text
    provenance = response.json()["provenance"]
    assert provenance["unnamed_subjects"] == 1, provenance
    assert tuple(provenance["subject_refs"]) == named, provenance


@pytest.mark.req("FR-2159")
def test_a_parent_named_in_full_leaves_the_unnamed_count_null(
    client: TestClient, reader: dict[str, str], workspace_id: UUID, principal: Principal
) -> None:
    seeded = _diagnostics(_Context(workspace_id, principal, client, reader))
    response = client.get(seeded.url, headers=reader)
    assert response.status_code == 200, response.text
    assert response.json()["provenance"].get("unnamed_subjects") is None
