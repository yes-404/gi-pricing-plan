"""The Dislocation Run as a backend artifact (03 §5.1, FR-263, FR-265, FR-266; PL-1501).

The `dislocation.run` Job handler, its persisted row (`dislocation_runs`, one writer,
`persist_run`), the routes and the generated contract. Tests are written before their code
(PL-1501 §"Tasks"); each section below is one task's.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID, uuid4

import polars as pl
import pytest
import pytest_asyncio
from backend.tests.blob_fixtures import blob_row, digest, job_result_owner
from backend.tests.test_rating_version_compile import (
    _empty_pins,
    _headers,
    _insert_version,
)
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.models import (
    BlobRow,
    DatasetVersionRow,
    DislocationRunRow,
    JobRow,
    RatingVersionRow,
    RoleAssignmentRow,
    RoleRow,
    WorkspaceMemberRow,
)
from app.db.session import Database
from app.errors import RATING_ERROR_CODES, PlatformError
from app.platform import dislocation_runs as service
from app.platform import jobs
from app.platform.blobs import BlobStore, to_ref
from app.platform.rating_versions import WorkspaceResolver
from app.worker import dislocation_handlers
from app.worker.celery_app import build_celery
from app.worker.dislocation_handlers import (
    DISLOCATION_SINGLE_JOB_MAX_HOURS,
    MOVERS_COLUMNS,
    PreloadedResolver,
    _Recorder,
    register_dislocation_handlers,
)
from app.worker.rating_handlers import register_rating_handlers
from app.worker.tasks import execute_job
from model_schema import ArtifactRef, JobKind, JobStatus, ScopeType, new_uuid7
from model_schema.dislocation import DislocationRun
from pricing_core.rating.analysis import AttributionError
from pricing_core.rating.compile import ResolvedArtifact

_BASELINE = "rating_version:motor-gb@26"
_CANDIDATE = "rating_version:motor-gb@27"
_BASELINE_HASH = "sha256:" + "a" * 64
_CANDIDATE_HASH = "sha256:" + "b" * 64


def _run(*, movers: str | None = None, job_id: UUID | None = None) -> DislocationRun:
    """A valid, empty-portfolio Dislocation Run naming a movers blob."""
    return DislocationRun.model_validate({
        "baseline_ref": _BASELINE,
        "candidate_ref": _CANDIDATE,
        "portfolio_dataset_version_id": str(new_uuid7()),
        "job_id": str(job_id or new_uuid7()),
        "policy_count": 0,
        "exposure_years": "0",
        "totals": {"baseline_premium_minor": 0, "candidate_premium_minor": 0,
                   "change_pct": None},
        "outcomes": {"quoted_both": 0, "quoted_to_declined": 0, "declined_to_quoted": 0,
                     "declined_both": 0, "error": 0, "zero_baseline": 0,
                     "negative_baseline": 0},
        "distribution": [{"band": "all", "policies": 0, "exposure_share": None,
                          "mean_change_pct": None}],
        "largest_movers_blob": "blob:sha256:" + (movers or digest()),
        "errors": [],
    })


async def _persist(database: Database, workspace_id: UUID, run: DislocationRun) -> UUID:
    async with database.unit_of_work() as session:
        row = await service.persist_run(
            session, workspace_id=workspace_id, run=run,
            baseline_bundle_hash=_BASELINE_HASH, candidate_bundle_hash=_CANDIDATE_HASH,
            actor_id=new_uuid7(),
        )
        return row.id


# ---- Task 1: the error code --------------------------------------------------------


@pytest.mark.req("FR-1397")
def test_the_reconciliation_failure_code_is_registered() -> None:
    assert "ATTRIBUTION_RECONCILIATION_FAILED" in RATING_ERROR_CODES


# ---- Task 2: the persisted row, its single writer, the movers deny -----------------


@pytest.mark.req("FR-265")
@pytest.mark.req("NFR-499")
async def test_the_scalar_movers_digest_equals_the_runs_movers_blob(
    database: Database, workspace_id: UUID
) -> None:
    run = _run()
    run_id = await _persist(database, workspace_id, run)
    async with database.session() as session:
        row = (await session.execute(
            select(DislocationRunRow).where(DislocationRunRow.id == run_id)
        )).scalar_one()
    assert "blob:sha256:" + row.movers_blob_sha256 == run.largest_movers_blob
    assert row.run["largest_movers_blob"] == run.largest_movers_blob
    assert (row.baseline_ref, row.candidate_ref) == (_BASELINE, _CANDIDATE)
    assert (row.baseline_bundle_hash, row.candidate_bundle_hash) == (
        _BASELINE_HASH, _CANDIDATE_HASH,
    )
    assert row.job_id == run.job_id
    assert row.portfolio_dataset_version_id == run.portfolio_dataset_version_id
    assert DislocationRun.model_validate(row.run) == run


@pytest.mark.req("FR-265")
async def test_fetch_is_scoped_to_the_workspace(
    database: Database, workspace_id: UUID
) -> None:
    run_id = await _persist(database, workspace_id, _run())
    async with database.session() as session:
        row = await service.fetch_run(session, workspace_id=workspace_id, run_id=run_id)
        assert row.id == run_id
        for other_workspace, other_id in ((new_uuid7(), run_id), (workspace_id, new_uuid7())):
            with pytest.raises(PlatformError) as caught:
                await service.fetch_run(
                    session, workspace_id=other_workspace, run_id=other_id
                )
            assert (caught.value.code, caught.value.status_code) == ("NOT_FOUND", 404)


@pytest.mark.req("FR-265")
async def test_a_run_without_a_movers_blob_or_a_job_id_is_not_persisted(
    database: Database, workspace_id: UUID
) -> None:
    for broken, why in (
        (_run().model_copy(update={"largest_movers_blob": None}), "movers blob"),
        (_run().model_copy(update={"job_id": None}), "Job"),
    ):
        with pytest.raises(ValueError, match=why):
            await _persist(database, workspace_id, broken)


@pytest_asyncio.fixture
async def reader_headers(workspace_id: UUID, principal: Any, grant: Any) -> dict[str, str]:
    """A `dataset:read` holder in `workspace_id` (the blob route's only permission)."""
    await grant("analyst")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


def _blob_get(client: TestClient, headers: dict[str, str], sha256: str) -> Any:
    return client.get(f"/api/v1/blobs/{sha256}", headers=headers, follow_redirects=False)


@pytest.mark.req("NFR-499")
async def test_the_generic_blob_route_refuses_a_movers_blob(
    api_client: TestClient, database: Database, workspace_id: UUID, reader_headers: dict[str, str]
) -> None:
    """RL-1504 item 5: the movers digest is referenced by the run row only, so
    `GET /api/v1/blobs/{sha256}` answers it as an unknown digest (404 `NOT_FOUND`)."""
    sha256 = digest()
    await blob_row(database, sha256, "application/vnd.apache.parquet")
    await _persist(database, workspace_id, _run(movers=sha256))
    response = _blob_get(api_client, reader_headers, sha256)
    assert response.status_code == 404, response.text
    body = response.json()
    assert (body["code"], body["title"], body["detail"]) == (
        "NOT_FOUND", "Blob not found", f"No blob with digest {sha256}.",
    )


@pytest.mark.req("NFR-499")
async def test_the_movers_digest_would_download_if_a_job_blob_result_named_it(
    api_client: TestClient, database: Database, workspace_id: UUID, reader_headers: dict[str, str]
) -> None:
    """The positive control for the test above: the 404 is the deny working, not a route that
    cannot serve this digest. Record it as a Job's `JobResult(kind="blob")` (the broken
    input PL-1501 Task 2 Step 4 names) and the route redirects."""
    sha256 = digest()
    await blob_row(database, sha256, "application/vnd.apache.parquet")
    await _persist(database, workspace_id, _run(movers=sha256))
    await job_result_owner(database, workspace_id, sha256)
    assert _blob_get(api_client, reader_headers, sha256).status_code == 307


# ---- Task 3: the workspace resolver, moved (DP-S4-4) --------------------------------


class _Fixed:
    """A resolver serving a fixed map, counting its calls."""

    def __init__(self, artifacts: dict[ArtifactRef, ResolvedArtifact]) -> None:
        self.artifacts, self.calls = artifacts, 0

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        self.calls += 1
        return self.artifacts[ref]


@pytest.mark.req("FR-1398")
async def test_the_preloaded_resolver_serves_exactly_what_both_versions_resolved() -> None:
    """A subset resolves what a real compile resolved, with no I/O; a ref neither version
    resolved raises the `NOT_FOUND:` form `compile_bundle`'s callers read as a code."""
    algorithm = ArtifactRef.model_validate("rating_algorithm:motor-gb@3")
    table = ArtifactRef.model_validate("rate_table:motor-age@2")
    unpinned = ArtifactRef.model_validate("rate_table:motor-other@1")
    base = _Fixed({
        algorithm: ResolvedArtifact(status="no_maturity_concept", payload={"a": 1}),
        table: ResolvedArtifact(status="no_maturity_concept", payload={"t": 2}),
    })
    recorder = _Recorder(base)
    for ref in (algorithm, table):
        await recorder.resolve(ref)
    preloaded = PreloadedResolver(recorder.seen)
    calls = base.calls
    assert await preloaded.resolve(algorithm) == base.artifacts[algorithm]
    assert await preloaded.resolve(table) == base.artifacts[table]
    assert base.calls == calls  # no I/O once preloaded
    with pytest.raises(ValueError, match=r"^NOT_FOUND: .*motor-other@1"):
        await preloaded.resolve(unpinned)


@pytest.mark.req("FR-1398")
def test_the_compile_resolver_is_a_module_level_class_with_the_nested_ones_arguments() -> None:
    """The lift (Task 3): `compile_rating_version` no longer nests its resolver, and the
    class takes the three closure variables the nested one read."""
    import inspect

    assert list(inspect.signature(WorkspaceResolver).parameters) == [
        "session", "workspace_id", "blob_store",
    ]
    assert inspect.iscoroutinefunction(WorkspaceResolver.resolve)


# ---- Task 4: the `dislocation.run` handler -------------------------------------------
#
# The handler is driven through `execute_job` (a Job row, a registered handler), over two
# genuinely compiled Rating Versions whose algorithms differ in three independent branches,
# so the derived changes are c1, c2, c3 (sorted by step id) and K = 3 with no grouping.


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_rating_handlers()
    register_dislocation_handlers()


def _algorithm(a: str, b: str, c: str, version: int = 1) -> dict[str, Any]:
    """Three independent expression branches summed: editing a branch is one derived change."""
    def branch(step_id: str, expr: str, produces: str) -> dict[str, Any]:
        return {"step_id": step_id, "type": "expression", "label": step_id, "expr": expr,
                "result_type": "money_minor", "consumes": ["premium_in"], "produces": produces}

    return {
        "slug": "dislocation-fixture",
        "version": version,
        "input_contract": [{"name": "premium_in", "type": "int", "nullable": False}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": "premium_in",
             "on_missing": "error", "produces": "premium_in"},
            branch("s_a", a, "va"), branch("s_b", b, "vb"), branch("s_c", c, "vc"),
            {"step_id": "s_sum", "type": "expression", "label": "Sum", "expr": "va + vb + vc",
             "result_type": "money_minor", "consumes": ["va", "vb", "vc"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


_BASE_BRANCHES = ("premium_in * 2", "premium_in + 10", "premium_in + 7")
_CAND_BRANCHES = ("premium_in * 3", "premium_in + 20", "premium_in + 9")


def _portfolio(n: int = 12) -> pl.DataFrame:
    """`03` §4.8's frame for the fixture (one input) plus a non-frame column, `channel`."""
    return pl.DataFrame({
        "quote_id": [f"Q{i:03d}" for i in range(n)],
        "exposure_years": [1.0] * n,
        "premium_in": [100 + 10 * i for i in range(n)],
        "channel": ["direct" if i % 2 == 0 else "broker" for i in range(n)],
    })


@dataclass(frozen=True)
class _World:
    workspace_id: UUID
    principal: Any
    headers: dict[str, str]
    portfolio_id: UUID
    baseline: ArtifactRef
    candidate: ArtifactRef

    def spec(self, **overrides: Any) -> dict[str, Any]:
        spec: dict[str, Any] = {
            "baseline_ref": str(self.baseline),
            "candidate_ref": str(self.candidate),
            "portfolio_dataset_version_id": str(self.portfolio_id),
            "purpose": "renewal",
            "as_at": date(2026, 9, 1).isoformat(),
            "band_edges_pct": ["-50", "50"],
            "mover_threshold_pct": "1",
        }
        return spec | overrides


async def _compile(
    api_client: TestClient, headers: dict[str, str], database: Database,
    blob_store: BlobStore, row: RatingVersionRow,
) -> None:
    response = api_client.post(f"/api/v1/rating-versions/{row.id}/compile", headers=headers)
    assert response.status_code == 202, response.text
    status = await execute_job(database, UUID(response.json()["id"]), blob_store)
    assert status is JobStatus.SUCCEEDED, status


@pytest_asyncio.fixture
async def world(
    api_client: TestClient, database: Database, blob_store: BlobStore, workspace_id: UUID,
    principal: Any, grant: Any,
) -> _World:
    await grant("analyst")
    headers = _headers(principal, workspace_id)
    refs = []
    for branches in (_BASE_BRANCHES, _CAND_BRANCHES):
        created = api_client.post(
            "/api/v1/rating-algorithms",
            json=_algorithm(*branches, version=len(refs) + 1), headers=headers,
        )
        assert created.status_code in (200, 201), created.text
        row = await _insert_version(
            database, workspace_id, principal.id,
            algorithm_ref=f"rating_algorithm:dislocation-fixture@{created.json()['version']}",
            pins=_empty_pins(), slug=f"dislocation-rv-{len(refs)}", version=1,
        )
        await _compile(api_client, headers, database, blob_store, row)
        refs.append(ArtifactRef(type="rating_version", slug=row.slug, version=1))
    buffer = io.BytesIO()
    frame = _portfolio()
    frame.write_parquet(buffer, compression="zstd")
    async with database.unit_of_work() as session:
        blob = await blob_store.put(session, buffer.getvalue(), "application/vnd.apache.parquet")
        version = DatasetVersionRow(
            slug="dislocation-portfolio", workspace_id=workspace_id, dataset_id=uuid4(),
            version=1, status="validated", validation_report_id=new_uuid7(),
            created_by=principal.id, currency="GBP",
            tables=[{"name": "portfolio", "row_count": frame.height,
                     "blob": {"sha256": blob.sha256}}],
        )
        session.add(version)
        await session.flush()
        portfolio_id = version.id
    return _World(workspace_id, principal, headers, portfolio_id, refs[0], refs[1])


async def _run_job(
    database: Database, blob_store: BlobStore, world: _World, spec: dict[str, Any]
) -> tuple[UUID, JobRow]:
    """Submit a `dislocation.run` Job as the route will and drive it to a terminal state."""
    parameters = {
        "workspace_id": str(world.workspace_id),
        "actor": world.principal.model_dump(mode="json"),
        "spec": spec,
    }
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.DISLOCATION_RUN, parameters, world.principal,
            workspace_id=world.workspace_id,
        )
    await execute_job(database, job.id, blob_store)
    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row is not None
    return job.id, row


async def _runs(database: Database, workspace_id: UUID) -> list[DislocationRunRow]:
    async with database.session() as session:
        return list((await session.execute(
            select(DislocationRunRow).where(DislocationRunRow.workspace_id == workspace_id)
        )).scalars())


async def _blob(database: Database, blob_store: BlobStore, sha256: str) -> bytes:
    async with database.session() as session:
        row = await session.get(BlobRow, sha256)
        assert row is not None
        return await blob_store.read(to_ref(row))


@pytest.mark.req("FR-263")
@pytest.mark.req("FR-265")
@pytest.mark.req("FR-266")
async def test_a_dislocation_run_persists_with_its_job_id_and_movers_blob(
    database: Database, blob_store: BlobStore, world: _World
) -> None:
    job_id, job = await _run_job(database, blob_store, world, world.spec())
    assert job.status is JobStatus.SUCCEEDED, job.error
    rows = await _runs(database, world.workspace_id)
    assert len(rows) == 1
    row = rows[0]
    run = DislocationRun.model_validate(row.run)
    assert run.job_id == job_id == row.job_id
    assert row.movers_blob_sha256 == run.largest_movers_blob.removeprefix("blob:sha256:")
    assert job.result == {"kind": "artifact", "ref": f"dislocation_run:{row.id}"}
    assert run.attribution is not None
    assert len(run.derived_changes or []) == 3


@pytest.mark.req("NFR-499")
async def test_the_stored_movers_hold_no_portfolio_column(
    database: Database, blob_store: BlobStore, world: _World
) -> None:
    """RL-1504 item 5: the stored blob's columns are exactly `dislocation_frame`'s own, though
    the portfolio carries `channel` and `premium_in`."""
    await _run_job(database, blob_store, world, world.spec())
    (row,) = await _runs(database, world.workspace_id)
    movers = pl.read_parquet(io.BytesIO(await _blob(database, blob_store, row.movers_blob_sha256)))
    assert tuple(movers.columns) == MOVERS_COLUMNS
    assert movers.height > 0  # a threshold of 1% moves every policy of this fixture


@pytest.mark.req("FR-1398")
async def test_dislocation_subset_bundles_never_become_rating_versions(
    database: Database, blob_store: BlobStore, world: _World
) -> None:
    async def versions() -> int:
        async with database.session() as session:
            return (await session.execute(
                select(func.count()).select_from(RatingVersionRow)
                .where(RatingVersionRow.workspace_id == world.workspace_id)
            )).scalar_one()

    before = await versions()
    _, job = await _run_job(database, blob_store, world, world.spec())
    assert job.status is JobStatus.SUCCEEDED, job.error
    (row,) = await _runs(database, world.workspace_id)
    summary = DislocationRun.model_validate(row.run).attribution_summary
    assert summary is not None
    assert summary.subset_bundle_count == 2**3
    assert len(summary.subset_bundle_hashes) == 2**3
    assert await versions() == before


@pytest.mark.req("FR-1397")
async def test_a_run_that_does_not_reconcile_fails_with_attribution_reconciliation_failed(
    api_client: TestClient, database: Database, blob_store: BlobStore, world: _World,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def refuse(*_: Any, **__: Any) -> Any:
        # the text `attribute` raises when a compared policy has no premium under a subset
        # bundle (`pricing_core.rating.analysis`): it names the policy's quote id
        raise AttributionError(
            "ATTRIBUTION_RECONCILIATION_FAILED",
            "policy Q000 is quoted in the baseline and the candidate but has no premium "
            "under the subset bundle for changes [c1]",
        )

    monkeypatch.setattr(dislocation_handlers, "attribute", refuse)
    job_id, job = await _run_job(database, blob_store, world, world.spec())
    assert job.status is JobStatus.FAILED
    assert job.error is not None
    assert job.error["code"] == "ATTRIBUTION_RECONCILIATION_FAILED"
    # NFR-499 (02:47:13): the stored error and the API body carry no quote id
    assert "Q000" not in str(job.error)
    served = api_client.get(f"/api/v1/jobs/{job_id}", headers=world.headers)
    assert served.status_code == 200, served.text
    assert "Q000" not in served.text
    assert await _runs(database, world.workspace_id) == []


@pytest.mark.req("NFR-495")
async def test_two_runs_of_the_same_spec_are_byte_identical(
    database: Database, blob_store: BlobStore, world: _World
) -> None:
    for _ in range(2):
        _, job = await _run_job(database, blob_store, world, world.spec())
        assert job.status is JobStatus.SUCCEEDED, job.error
    first, second = await _runs(database, world.workspace_id)

    def without_job(row: DislocationRunRow) -> dict[str, Any]:
        return {k: v for k, v in row.run.items() if k != "job_id"}

    assert without_job(first) == without_job(second)
    assert first.movers_blob_sha256 == second.movers_blob_sha256
    assert first.job_id != second.job_id


@pytest.mark.req("FR-263")
def test_the_celery_visibility_timeout_exceeds_the_single_job_bound() -> None:
    """RL-1504 item 2: red at origin/main, where the key is absent (Celery's one-hour default
    would redeliver a running 4-hour Job to a second worker)."""
    from app.config import Settings

    options = build_celery(Settings()).conf.broker_transport_options
    assert options["visibility_timeout"] > DISLOCATION_SINGLE_JOB_MAX_HOURS * 3600


@pytest.mark.req("FR-263")
async def test_a_second_delivery_for_a_running_dislocation_job_does_nothing(
    database: Database, blob_store: BlobStore, world: _World
) -> None:
    parameters = {
        "workspace_id": str(world.workspace_id),
        "actor": world.principal.model_dump(mode="json"),
        "spec": world.spec(),
    }
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.DISLOCATION_RUN, parameters, world.principal,
            workspace_id=world.workspace_id,
        )
        (await session.get(JobRow, job.id)).status = JobStatus.RUNNING  # type: ignore[union-attr]
    assert await execute_job(database, job.id, blob_store) is JobStatus.RUNNING
    assert await _runs(database, world.workspace_id) == []
    async with database.session() as session:
        row = await session.get(JobRow, job.id)
    assert row is not None
    assert (row.status, row.result) == (JobStatus.RUNNING, None)



# ---- Task 5: the routes --------------------------------------------------------------


def _headers_of(user_id: UUID, workspace_id: UUID) -> dict[str, str]:
    """`_headers` for a bare user id (a caller with no `Principal` object)."""
    return {DEV_PRINCIPAL_HEADER: str(user_id), "Workspace-Id": str(workspace_id)}


async def _caller_with(
    database: Database, workspace_id: UUID, permissions: list[str]
) -> dict[str, str]:
    """Headers for a member holding exactly `permissions` (a stored custom role: no built-in
    role is narrow enough for the refusals below)."""
    caller = uuid4()
    async with database.unit_of_work() as session:
        role = RoleRow(
            workspace_id=workspace_id, slug=f"narrow-{uuid4().hex[:6]}",
            description=", ".join(permissions), permissions=permissions, builtin=False,
        )
        session.add(role)
        await session.flush()
        session.add(RoleAssignmentRow(
            workspace_id=workspace_id, principal_kind="user", principal_id=caller,
            role_id=role.id, scope_type=ScopeType.WORKSPACE.value,
        ))
        session.add(WorkspaceMemberRow(user_id=caller, workspace_id=workspace_id))
    return _headers_of(caller, workspace_id)


async def _dislocation_jobs(database: Database, workspace_id: UUID) -> int:
    async with database.session() as session:
        return (await session.execute(
            select(func.count()).select_from(JobRow).where(
                JobRow.workspace_id == workspace_id, JobRow.kind == JobKind.DISLOCATION_RUN
            )
        )).scalar_one()


@pytest.mark.req("FR-263")
async def test_post_answers_202_with_a_job_and_the_job_persists_the_run(
    api_client: TestClient, database: Database, blob_store: BlobStore, world: _World
) -> None:
    response = api_client.post("/api/v1/dislocation-runs", json=world.spec(), headers=world.headers)
    assert response.status_code == 202, response.text
    job = response.json()
    assert response.headers["Location"] == f"/api/v1/jobs/{job['id']}"
    assert await execute_job(database, UUID(job["id"]), blob_store) is JobStatus.SUCCEEDED
    (row,) = await _runs(database, world.workspace_id)
    fetched = api_client.get(f"/api/v1/dislocation-runs/{row.id}", headers=world.headers)
    assert fetched.status_code == 200, fetched.text
    assert DislocationRun.model_validate(fetched.json()) == DislocationRun.model_validate(row.run)


@pytest.mark.req("FR-1399")
async def test_post_refuses_groups_that_do_not_partition_the_derived_changes(
    api_client: TestClient, database: Database, world: _World
) -> None:
    spec = world.spec(change_groups=[{"name": "g1", "changes": ["c1", "c3"]}])  # c2 left out
    response = api_client.post("/api/v1/dislocation-runs", json=spec, headers=world.headers)
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["code"] == "VALIDATION_FAILED"
    assert "c2" in body["detail"]
    assert await _dislocation_jobs(database, world.workspace_id) == 0


@pytest.mark.req("FR-263")
async def test_post_needs_rating_compile_and_dataset_read(
    api_client: TestClient, database: Database, world: _World, grant: Any
) -> None:
    """DP-S4-2 (b): `rating:compile` (the analyst's, WF-699 D6's actor) and `dataset:read` on
    the portfolio. An auditor cannot start a run; a compile-only caller is refused too."""
    actuary = uuid4()
    await grant("pricing_actuary", principal_id=actuary)
    auditor = uuid4()
    await grant("auditor", principal_id=auditor)
    compile_only = await _caller_with(database, world.workspace_id, ["rating:compile"])
    outcomes = {}
    for name, headers in (
        ("actuary", _headers_of(actuary, world.workspace_id)),
        ("auditor", _headers_of(auditor, world.workspace_id)),
        ("compile_only", compile_only),
    ):
        response = api_client.post("/api/v1/dislocation-runs", json=world.spec(), headers=headers)
        outcomes[name] = (response.status_code, response.json().get("code"))
    assert outcomes == {
        "actuary": (202, None),
        "auditor": (403, "PERMISSION_DENIED"),
        "compile_only": (403, "PERMISSION_DENIED"),
    }


@pytest.mark.req("FR-265")
async def test_get_needs_rating_read_and_scopes_to_the_workspace(
    api_client: TestClient, database: Database, blob_store: BlobStore, world: _World
) -> None:
    await _run_job(database, blob_store, world, world.spec())
    (row,) = await _runs(database, world.workspace_id)
    url = f"/api/v1/dislocation-runs/{row.id}"
    no_rating = await _caller_with(database, world.workspace_id, ["dataset:read"])
    refused = api_client.get(url, headers=no_rating)
    assert (refused.status_code, refused.json()["code"]) == (403, "PERMISSION_DENIED")
    unknown = api_client.get(f"/api/v1/dislocation-runs/{new_uuid7()}", headers=world.headers)
    assert (unknown.status_code, unknown.json()["code"]) == (404, "NOT_FOUND")
    elsewhere = await _persist(database, new_uuid7(), _run())  # another workspace's run
    cross = api_client.get(f"/api/v1/dislocation-runs/{elsewhere}", headers=world.headers)
    assert (cross.status_code, cross.json()["code"]) == (404, "NOT_FOUND")


@pytest.mark.req("FR-263")
async def test_the_estimate_is_returned_before_any_job(
    api_client: TestClient, database: Database, world: _World
) -> None:
    from pricing_core.rating.analysis import estimate_attribution_ratings

    response = api_client.post(
        "/api/v1/dislocation-runs/estimate", json=world.spec(), headers=world.headers
    )
    assert response.status_code == 200, response.text
    body = response.json()
    expected = estimate_attribution_ratings(3, 12, grouped=False)
    assert (body["derived_changes"], body["policies"]) == (3, 12)
    assert body["estimated_ratings"] == expected
    rate = service.DISLOCATION_RATINGS_PER_WORKER_HOUR
    assert body["estimated_worker_hours"] == expected / rate
    assert body["method"] == "shapley"
    assert await _dislocation_jobs(database, world.workspace_id) == 0


@pytest.mark.req("FR-263")
async def test_a_run_estimated_over_the_single_job_bound_is_refused_before_any_job(
    api_client: TestClient, database: Database, world: _World, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RL-1504 item 1. The fixture's 96 ratings cannot exceed the real 4-hour bound, so the
    bound is lowered to zero; the refusal and the estimate are the production code paths."""
    monkeypatch.setattr(service, "DISLOCATION_SINGLE_JOB_MAX_HOURS", 0)
    response = api_client.post("/api/v1/dislocation-runs", json=world.spec(), headers=world.headers)
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["code"] == "VALIDATION_FAILED"
    for named in ("K = 3", "12 policies", "96 ratings"):
        assert named in body["detail"], body["detail"]
    assert await _dislocation_jobs(database, world.workspace_id) == 0
    estimate = api_client.post(
        "/api/v1/dislocation-runs/estimate", json=world.spec(), headers=world.headers
    )
    assert estimate.status_code == 200, estimate.text
    assert estimate.json()["estimated_ratings"] == 96


@pytest.mark.req("FR-263")
@pytest.mark.req("NFR-499")
async def test_movers_route_joins_the_portfolio_columns_at_read(
    api_client: TestClient, database: Database, blob_store: BlobStore, world: _World
) -> None:
    await _run_job(database, blob_store, world, world.spec())
    (row,) = await _runs(database, world.workspace_id)
    url = f"/api/v1/dislocation-runs/{row.id}/movers"
    response = api_client.get(url, headers=world.headers)
    assert response.status_code == 200, response.text
    served = response.json()
    stored = pl.read_parquet(io.BytesIO(await _blob(database, blob_store, row.movers_blob_sha256)))
    portfolio = _portfolio()
    assert [r["quote_id"] for r in served] == stored["quote_id"].to_list()  # §4.6's mover order
    assert served, "a threshold of 1% moves every policy of this fixture"
    for r in served:
        source = portfolio.filter(pl.col("quote_id") == r["quote_id"]).row(0, named=True)
        assert (r["premium_in"], r["channel"]) == (source["premium_in"], source["channel"])
        assert set(r) == {*MOVERS_COLUMNS, "exposure_years", "premium_in", "channel"}
    # `dataset:read` is a separate permission from `rating:read` (RL-1504 item 5).
    rating_only = await _caller_with(database, world.workspace_id, ["rating:read"])
    refused = api_client.get(url, headers=rating_only)
    assert (refused.status_code, refused.json()["code"]) == (403, "PERMISSION_DENIED")
