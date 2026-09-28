"""The persisted Regression Run and its lookup (03 §4.9, FR-260, FR-261, FR-9301; PL-1205 T5).

`regression_runs` has one writer, `persist_run`; the scalar `cases_blob_sha256` the generic
blob route's deny matches is written from the same object as the JSONB, and a test holds
them equal. `latest_run` is the submit gate's lookup: the LATEST run for exactly one
(bundle, suite) pair, so an earlier pass never outlives a later failure (audit A1).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import select

from app.db.models import RatingVersionRow, RegressionRunRow
from app.db.session import Database
from app.platform import regression_runs as service
from model_schema import RegressionRun, new_uuid7

_T0 = datetime(2026, 9, 28, 9, 0, 0, tzinfo=UTC)


def _run(*, overall: str = "pass", bundle: str = "b", suite: str = "a",
         minutes: int = 0, blob: str = "c") -> RegressionRun:
    failing = overall == "fail"
    return RegressionRun.model_validate({
        "suite_ref": "regression_suite:motor-gb-core@3",
        "suite_content_hash": "sha256:" + suite * 64,
        "rating_version_ref": "rating_version:motor-gb@27",
        "bundle_hash": "sha256:" + bundle * 64,
        "started_at": (_T0 + timedelta(minutes=minutes)).isoformat(),
        "finished_at": (_T0 + timedelta(minutes=minutes, seconds=4)).isoformat(),
        "overall": overall,
        "generation": {"seed": 1, "cases": 10, "hypothesis_version": "6.165.7"},
        "cases_blob": {"sha256": blob * 64, "bytes": 10, "media_type": "application/json"},
        "golden_results": [],
        "property_results": [
            {"name": "p", "status": "fail", "cases_run": 10, "counterexample": {"x": 1},
             "counterexample_minimal": True, "shrink": "completed",
             "error_code": "PROPERTY_ASSERTION_FAILED"}
            if failing else {"name": "p", "status": "pass", "cases_run": 10}
        ],
    })


async def _rating_version(database: Database, workspace_id: UUID, slug: str = "motor-gb") -> UUID:
    async with database.unit_of_work() as session:
        row = RatingVersionRow(
            workspace_id=workspace_id, slug=slug, version=1, status="draft",
            dataset_version_id=new_uuid7(), model_ref="model:motor-ad-frequency@7",
            created_by=new_uuid7(), algorithm_ref=None,
            pins={"rate_tables": [], "models": [], "reference_tables": [],
                  "custom_objectives": []},
        )
        session.add(row)
        await session.flush()
        return row.id


async def _persist(database: Database, workspace_id: UUID, rv: UUID, run: RegressionRun) -> UUID:
    async with database.unit_of_work() as session:
        row = await service.persist_run(
            session, workspace_id=workspace_id, rating_version_id=rv, run=run,
            actor_id=new_uuid7(),
        )
        return row.id


async def _latest(database: Database, workspace_id: UUID, rv: UUID, **pair: str) -> Any:
    bundle = "sha256:" + pair.get("bundle", "b") * 64
    suite = "sha256:" + pair.get("suite", "a") * 64
    async with database.session() as session:
        row = await service.latest_run(
            session, workspace_id=workspace_id, rating_version_id=rv,
            bundle_hash=bundle, suite_content_hash=suite,
        )
        return None if row is None else (row.id, row.overall)


@pytest.mark.req("FR-261")
@pytest.mark.req("NFR-499")
async def test_the_scalar_blob_digest_equals_the_runs_cases_blob(
    database: Database, workspace_id: UUID
) -> None:
    rv = await _rating_version(database, workspace_id)
    run = _run(blob="d")
    run_id = await _persist(database, workspace_id, rv, run)
    async with database.session() as session:
        row = (await session.execute(
            select(RegressionRunRow).where(RegressionRunRow.id == run_id)
        )).scalar_one()
    assert row.cases_blob_sha256 == run.cases_blob.sha256 == row.run["cases_blob"]["sha256"]
    assert (row.bundle_hash, row.suite_content_hash, row.overall) == (
        run.bundle_hash, run.suite_content_hash, "pass",
    )
    assert RegressionRun.model_validate(row.run) == run


@pytest.mark.req("FR-257")
async def test_the_latest_run_of_a_pair_wins_and_a_later_failure_supersedes_a_pass(
    database: Database, workspace_id: UUID
) -> None:
    """Limb (1) only: a passing Regression Suite; limbs (2)-(4) are not tested here."""
    rv = await _rating_version(database, workspace_id)
    assert await _latest(database, workspace_id, rv) is None
    first = await _persist(database, workspace_id, rv, _run(overall="pass", minutes=0))
    assert await _latest(database, workspace_id, rv) == (first, "pass")
    second = await _persist(database, workspace_id, rv, _run(overall="fail", minutes=5))
    assert await _latest(database, workspace_id, rv) == (second, "fail")
    third = await _persist(database, workspace_id, rv, _run(overall="pass", minutes=10))
    assert await _latest(database, workspace_id, rv) == (third, "pass")


@pytest.mark.req("FR-257")
async def test_a_run_of_another_bundle_or_suite_or_version_is_not_this_pairs_run(
    database: Database, workspace_id: UUID
) -> None:
    rv = await _rating_version(database, workspace_id)
    other = await _rating_version(database, workspace_id, slug="home-gb")
    await _persist(database, workspace_id, rv, _run(bundle="e"))   # a stale bundle
    await _persist(database, workspace_id, rv, _run(suite="f"))    # a different suite
    await _persist(database, workspace_id, other, _run())          # another version's run
    assert await _latest(database, workspace_id, rv) is None
    assert await _latest(database, workspace_id, rv, bundle="e") is not None
    assert await _latest(database, workspace_id, other) is not None


@pytest.mark.req("FR-257")
async def test_the_lookup_is_scoped_to_the_workspace(
    database: Database, workspace_id: UUID
) -> None:
    rv = await _rating_version(database, workspace_id)
    await _persist(database, workspace_id, rv, _run())
    async with database.session() as session:
        assert await service.latest_run(
            session, workspace_id=new_uuid7(), rating_version_id=rv,
            bundle_hash="sha256:" + "b" * 64, suite_content_hash="sha256:" + "a" * 64,
        ) is None


# --- the route, the Job, the row and the blob (PL-1205 Task 5b; FR-260, FR-261, FR-9301) ------

import asyncio  # noqa: E402

from backend.tests.test_rating_version_compile import (  # noqa: E402
    _empty_pins,
    _headers,
    _insert_version,
    _minimal_algorithm,
    _run_compile_job,
)

from app.api.deps import DEV_PRINCIPAL_HEADER  # noqa: E402
from app.db.models import BlobRow, JobRow  # noqa: E402
from app.worker.rating_handlers import register_rating_handlers  # noqa: E402
from app.worker.tasks import execute_job  # noqa: E402
from model_schema import CasesLog, JobStatus  # noqa: E402

_SECRET = 7_654_321  # a quote-input value that must never appear in a log, error or audit line


def _suite_body(*, properties: list[dict[str, Any]], expected: int = 200) -> dict[str, Any]:
    return {
        "algorithm_slug": "minimal",
        "golden_quotes": [{
            "name": "known-quote",
            "context": {"purpose": "new_business", "quoted_at": "2026-09-28T09:00:00Z",
                        "effective_date": "2026-10-01", "inputs": {"premium_in": 100}},
            "expected": {"payable_premium_minor": expected, "outcome": "quoted"},
            "tolerance": {"money_minor": 0},
        }],
        "properties": properties,
        "generation": {"cases": 20, "seed": 3, "strategy": "input_contract_sampling"},
    }


def _post_run(client: Any, headers: dict[str, str], rv: UUID) -> Any:
    return client.post(f"/api/v1/rating-versions/{rv}/regression-runs", headers=headers)


def _drive(database: Database, blob_store: Any, job_id: UUID) -> JobRow:
    async def go() -> JobRow:
        await execute_job(database, job_id, blob_store)
        async with database.session() as session:
            row = await session.get(JobRow, job_id)
        assert row is not None
        return row

    return asyncio.get_event_loop().run_until_complete(go())


@pytest.fixture
def run_world(api_client, workspace_id, principal, grant, database, blob_store):
    """An analyst, a compiled `minimal@1` version, and a helper making suites and runs."""
    register_rating_handlers()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    assert api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    ).status_code == 201
    row = loop.run_until_complete(
        _insert_version(database, workspace_id, principal.id, "rating_algorithm:minimal@1",
                        _empty_pins())
    )
    compiled = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert compiled.status is JobStatus.SUCCEEDED, compiled.error

    def make_suite(**kw: Any) -> None:
        response = api_client.post(
            "/api/v1/regression-suites/minimal-core/versions",
            json=_suite_body(**kw) | {"change_note": "s"}, headers=headers,
        )
        assert response.status_code == 201, response.text

    def run() -> JobRow:
        accepted = _post_run(api_client, headers, row.id)
        assert accepted.status_code == 202, accepted.text
        return _drive(database, blob_store, UUID(accepted.json()["id"]))

    return type("World", (), {
        "headers": headers, "rv": row.id, "make_suite": staticmethod(make_suite),
        "run": staticmethod(run), "client": api_client, "database": database,
        "blob_store": blob_store, "workspace_id": workspace_id,
    })


def _the_run(database: Database, rv: UUID) -> RegressionRunRow:
    async def go() -> RegressionRunRow:
        async with database.session() as session:
            rows = (await session.execute(
                select(RegressionRunRow).where(RegressionRunRow.rating_version_id == rv)
            )).scalars().all()
        assert len(rows) == 1, rows
        return rows[0]

    return asyncio.get_event_loop().run_until_complete(go())


@pytest.mark.req("FR-261")
@pytest.mark.req("FR-260")
def test_a_regression_run_is_a_202_job_that_persists_the_run_and_its_case_blob(
    run_world,
) -> None:
    w = run_world
    w.make_suite(properties=[{"name": "no-null", "check": {"kind": "no_null_output"}}])
    job = w.run()
    assert job.status is JobStatus.SUCCEEDED, job.error
    assert job.result["kind"] == "artifact"
    row = _the_run(w.database, w.rv)
    assert row.overall == "pass"
    run = RegressionRun.model_validate(row.run)
    assert run.job_id == job.id
    assert run.bundle_hash == row.bundle_hash
    assert row.cases_blob_sha256 == run.cases_blob.sha256

    async def blob_bytes() -> bytes:
        from app.platform.blobs import to_ref

        async with w.database.session() as session:
            blob_row = await session.get(BlobRow, row.cases_blob_sha256)
        assert blob_row is not None
        return await w.blob_store.read(to_ref(blob_row))

    body = asyncio.get_event_loop().run_until_complete(blob_bytes())
    log = CasesLog.model_validate_json(body)
    assert len(log.cases) > 0
    from model_schema import cases_log_sha256

    assert cases_log_sha256(log) == row.cases_blob_sha256


@pytest.mark.req("FR-261")
def test_a_failing_property_ends_the_job_failed_and_the_run_still_persists(run_world) -> None:
    w = run_world
    # `payable = premium_in * 2` is negative for a negative input: the generator reaches it.
    w.make_suite(properties=[{"name": "positive", "check": {"kind": "premium_positive"}}])
    job = w.run()
    assert job.status is JobStatus.FAILED
    assert job.error["code"] == "PROPERTY_ASSERTION_FAILED"
    row = _the_run(w.database, w.rv)
    assert row.overall == "fail"
    (prop,) = RegressionRun.model_validate(row.run).property_results
    assert (prop.status, prop.shrink) == ("fail", "completed")


@pytest.mark.req("FR-260")
def test_a_golden_mismatch_ends_the_job_failed_with_its_own_code(run_world) -> None:
    w = run_world
    w.make_suite(properties=[{"name": "no-null", "check": {"kind": "no_null_output"}}],
                 expected=999)
    job = w.run()
    assert job.status is JobStatus.FAILED
    assert job.error["code"] == "GOLDEN_QUOTE_MISMATCH"
    assert _the_run(w.database, w.rv).overall == "fail"


@pytest.mark.req("FR-261")
def test_starting_a_run_needs_rating_compile(
    run_world, api_client, workspace_id, grant, database
) -> None:
    from model_schema import Principal, new_uuid7

    w = run_world
    reader = Principal(kind="user", id=new_uuid7(), display="reader")  # type: ignore[arg-type]
    asyncio.get_event_loop().run_until_complete(grant("approver", principal_id=reader.id))
    refused = api_client.post(
        f"/api/v1/rating-versions/{w.rv}/regression-runs",
        headers={DEV_PRINCIPAL_HEADER: str(reader.id), "Workspace-Id": str(workspace_id)},
    )
    assert refused.status_code == 403, refused.text


@pytest.mark.req("NFR-499")
@pytest.mark.req("FR-261")
def test_the_case_blob_and_the_run_row_are_refused_without_rating_read_or_across_workspaces(
    run_world, api_client, workspace_id, grant, database
) -> None:
    """DP-S3-4 (iii): the run row's JSONB counterexample and the case blob are read only
    through the run's own `rating:read` routes. The generic blob route refuses the blob to
    EVERY caller with the same 404 a missing blob gets (#868's deny tuple names the column)."""
    from model_schema import new_uuid7

    w = run_world
    w.make_suite(properties=[{"name": "positive", "check": {"kind": "premium_positive"}}])
    w.run()
    row = _the_run(w.database, w.rv)
    run_url = f"/api/v1/rating-versions/{w.rv}/regression-runs/{row.id}"

    # 1. a rating:read holder reads the run (with its counterexample) and the case log
    ok = api_client.get(run_url, headers=w.headers)
    assert ok.status_code == 200, ok.text
    assert ok.json()["property_results"][0]["counterexample"] is not None
    assert api_client.get(run_url + "/cases", headers=w.headers).status_code == 200

    # 2. the generic blob route: 404 for a dataset:read holder, identical to a missing blob.
    #    The digest is made otherwise ownable — a job in THIS workspace names it as its blob
    #    result, which the route's allow-list would serve — so only the deny tuple refuses it.
    async def own_it() -> None:
        from datetime import UTC, datetime

        from app.db.models import JobRow as _JobRow
        from model_schema import JobKind, JobQueue, JobSource

        async with database.unit_of_work() as session:
            session.add(_JobRow(
                workspace_id=workspace_id, kind=JobKind.RATE_TABLE_DIFF,
                status=JobStatus.SUCCEEDED, queue=JobQueue.DEFAULT, source=JobSource.API,
                submitted_by={"kind": "user", "id": str(new_uuid7())},
                result={"kind": "blob", "ref": row.cases_blob_sha256},
                finished_at=datetime.now(UTC),
            ))

    asyncio.get_event_loop().run_until_complete(own_it())
    blob_url = f"/api/v1/blobs/{row.cases_blob_sha256}"
    denied = api_client.get(blob_url, headers=w.headers, follow_redirects=False)
    missing = api_client.get(f"/api/v1/blobs/{'0' * 64}", headers=w.headers,
                             follow_redirects=False)
    assert denied.status_code == missing.status_code == 404
    assert denied.json()["code"] == missing.json()["code"]

    # 3. a member with no rating:read is refused both run routes
    outsider = new_uuid7()
    asyncio.get_event_loop().run_until_complete(grant("approver", principal_id=outsider))
    # `approver` holds rating:read; a principal with NO role at all does not
    nobody = new_uuid7()
    from app.db.models import WorkspaceMemberRow

    async def enrol() -> None:
        async with database.unit_of_work() as session:
            session.add(WorkspaceMemberRow(user_id=nobody, workspace_id=workspace_id))

    asyncio.get_event_loop().run_until_complete(enrol())
    weak = {DEV_PRINCIPAL_HEADER: str(nobody), "Workspace-Id": str(workspace_id)}
    assert api_client.get(run_url, headers=weak).status_code == 403
    assert api_client.get(run_url + "/cases", headers=weak).status_code == 403

    # 4. another workspace cannot see this run: uniform 404
    other = new_uuid7()
    other_headers = {DEV_PRINCIPAL_HEADER: str(nobody), "Workspace-Id": str(other)}
    assert api_client.get(run_url, headers=other_headers).status_code in (403, 404)


@pytest.mark.req("NFR-499")
def test_a_failed_run_puts_no_quote_input_in_the_job_error(run_world) -> None:
    w = run_world
    w.make_suite(properties=[{"name": "positive", "check": {"kind": "premium_positive"}}])
    job = w.run()
    text = repr(job.error) + repr(job.parameters)
    assert str(_SECRET) not in text
    assert "premium_in" not in repr(job.error)
