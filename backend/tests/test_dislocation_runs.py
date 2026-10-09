"""The Dislocation Run as a backend artifact (03 §5.1, FR-263, FR-265, FR-266; PL-1501).

The `dislocation.run` Job handler, its persisted row (`dislocation_runs`, one writer,
`persist_run`), the routes and the generated contract. Tests are written before their code
(PL-1501 §"Tasks"); each section below is one task's.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from backend.tests.blob_fixtures import blob_row, digest, job_result_owner
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.db.models import DislocationRunRow
from app.db.session import Database
from app.errors import RATING_ERROR_CODES, PlatformError
from app.main import create_app
from app.platform import dislocation_runs as service
from app.platform.rating_versions import WorkspaceResolver
from app.worker.dislocation_handlers import PreloadedResolver, _Recorder
from model_schema import ArtifactRef, new_uuid7
from model_schema.dislocation import DislocationRun
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


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_blob_bucket, test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=test_blob_bucket(),
    )


@pytest.fixture
def client(api_settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def reader_headers(workspace_id: UUID, principal: Any, grant: Any) -> dict[str, str]:
    """A `dataset:read` holder in `workspace_id` (the blob route's only permission)."""
    await grant("analyst")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


def _blob_get(client: TestClient, headers: dict[str, str], sha256: str) -> Any:
    return client.get(f"/api/v1/blobs/{sha256}", headers=headers, follow_redirects=False)


@pytest.mark.req("NFR-499")
async def test_the_generic_blob_route_refuses_a_movers_blob(
    client: TestClient, database: Database, workspace_id: UUID, reader_headers: dict[str, str]
) -> None:
    """RL-1504 item 5: the movers digest is referenced by the run row only, so
    `GET /api/v1/blobs/{sha256}` answers it as an unknown digest (404 `NOT_FOUND`)."""
    sha256 = digest()
    await blob_row(database, sha256, "application/vnd.apache.parquet")
    await _persist(database, workspace_id, _run(movers=sha256))
    response = _blob_get(client, reader_headers, sha256)
    assert response.status_code == 404, response.text
    body = response.json()
    assert (body["code"], body["title"], body["detail"]) == (
        "NOT_FOUND", "Blob not found", f"No blob with digest {sha256}.",
    )


@pytest.mark.req("NFR-499")
async def test_the_movers_digest_would_download_if_a_job_blob_result_named_it(
    client: TestClient, database: Database, workspace_id: UUID, reader_headers: dict[str, str]
) -> None:
    """The positive control for the test above: the 404 is the deny working, not a route that
    cannot serve this digest. Record it as a Job's `JobResult(kind="blob")` (the broken
    input PL-1501 Task 2 Step 4 names) and the route redirects."""
    sha256 = digest()
    await blob_row(database, sha256, "application/vnd.apache.parquet")
    await _persist(database, workspace_id, _run(movers=sha256))
    await job_result_owner(database, workspace_id, sha256)
    assert _blob_get(client, reader_headers, sha256).status_code == 307


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
