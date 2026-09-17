"""The backtest routes over HTTP (`02` FR-187, FR-94).

**FR-187, not FR-144.** The plan this file was written from named FR-144 as
"backtest results"; it is nothing of the kind — FR-144 is the **symbolic derivation of
gradient and hessian from an `expression` objective's loss**, a Phase 2 capability gated off
by FR-150 and correctly implemented by nothing. Marking these tests with it would have
put a traceability claim on a requirement no line of this repository satisfies, which is
precisely the "a marker is a claim, not a proof" failure `CLAUDE.md` §13 warns about.
FR-187 is the backtest requirement and is what `test_backtests.py` already carries.

`test_backtests.py` covers the platform layer. This file covers the two routes: who may
call them, what they return, and the workspace boundary — none of which the platform tests
can see, because they never build a request.

The only route evidence that existed before this file was
`test_backtests.py::test_both_backtest_routes_are_in_the_published_contract`, which asserts
the two paths appear in the OpenAPI document. That is a test of `generate-contracts.py`: a
route returning 500 on every call would have kept it green.

**Rows are inserted rather than fitted.** These routes queue, look up and scope; they do not
care how a model was produced, and a real GLM fit per test would measure the fit.
`test_backtests.py` owns the fitted path.

**Every test seeds its own model and its own target version.** `uq_backtests_model_version`
(`db/models.py`) has no workspace column, so the same `(model_id, dataset_version_id)` pair
cannot be backtested twice even in two different workspaces — the one place this suite's
fresh-workspace isolation does not hold. A shared module-level fixture seeding one pair would
make the second test in the file fail with an `IntegrityError` that reads like a defect in
the route. Recorded as a finding in `02` §4.12; not fixed here, because narrowing the
constraint is a migration and a governance question.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from uuid import UUID

import pytest
import pytest_asyncio
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.models import BacktestRow, DatasetVersionRow, DiagnosticsRow, ModelRow
from app.db.session import Database
from model_schema import (
    BacktestSummary,
    GlmSpec,
    ModelStatus,
    OffsetSpec,
    PartitionDiagnostics,
    Weighting,
    new_uuid7,
)


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    """The shared DB-backed client, under the name this module's tests already use."""
    return api_client


@pytest_asyncio.fixture
async def actuary(workspace_id, principal, grant) -> dict[str, str]:
    """`model:fit` **and** `model:read` — the principal that may start a backtest."""
    await grant("analyst")
    return _headers(principal.id, workspace_id)


@pytest_asyncio.fixture
async def reader(workspace_id, grant) -> dict[str, str]:
    """`model:read` and **not** `model:fit`.

    A separate principal rather than a second grant on the one above, so the permit and the
    refusal below distinguish the two permissions instead of proving that some header works.
    `auditor` is `READ_PERMISSIONS`; `analyst` is the read role that also holds `model:fit`.
    """
    reader_id = new_uuid7()
    await grant("auditor", principal_id=reader_id)
    return _headers(reader_id, workspace_id)


@pytest_asyncio.fixture
async def stranger(workspace_id, database) -> dict[str, str]:
    """Authenticated into this workspace, holding nothing.

    The membership (W6b-11) lets the identity resolve, so the refusal these tests expect
    comes from the role check rather than the membership check.
    """
    from app.db.models import WorkspaceMemberRow
    from app.platform import workspaces

    stranger_id = new_uuid7()
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        session.add(WorkspaceMemberRow(user_id=stranger_id, workspace_id=workspace_id))
    return _headers(stranger_id, workspace_id)


def _summary(*, model_ref: str, version_ref: str, fitted_on_ref: str) -> BacktestSummary:
    return BacktestSummary(
        model_ref=model_ref,
        dataset_version_ref=version_ref,
        fitted_on_ref=fitted_on_ref,
        partition=PartitionDiagnostics(
            weighting=Weighting.EXPOSURE,
            rows=400,
            ae_overall=1.07,
            gini=0.31,
            gini_normalised=0.42,
        ),
    )


def _run[T](work: Callable[[Database], Awaitable[T]]) -> T:
    """Run one coroutine on a loop of our own, disposing the engine it opened.

    `TestClient` is blocking, so an async fixture cannot be requested from the synchronous
    tests below — `test_api_models._seed` reaches for the same construction and records why.
    **`dispose()` is mandatory**: an engine left open exhausts the pool across a file.
    """
    from backend.tests.conftest_db import test_database_url

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            return loop.run_until_complete(work(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()


def _seed_model_and_version(workspace_id: UUID) -> tuple[UUID, UUID]:
    """A `fitted` model and a *different* `validated` version, both minted fresh.

    Fresh on every call for `uq_backtests_model_version`'s reason — see the module
    docstring. The versions declare no `arrow_schema`, which is the documented
    "let the Job find out from the parquet" path through `refuse_missing_columns`; what is
    under test here is the route, not the column check `test_backtests.py` already owns.
    """

    async def _insert(database: Database) -> tuple[UUID, UUID]:
        dataset_id = new_uuid7()
        async with database.unit_of_work() as session:
            fitted_on = DatasetVersionRow(
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                version=1,
                status="validated",
                validation_report_id=new_uuid7(),
                tables=[],
                # OQ-568 (c): the envelope columns are non-null since 2057e7372a9a.
                # No DatasetRow exists here (the route under test never joins one), so
                # the slug is a placeholder the constraint only needs to be non-null.
                slug="motor-gb",
                created_by=new_uuid7(),
                currency="GBP",
            )
            later = DatasetVersionRow(
                workspace_id=workspace_id,
                dataset_id=dataset_id,
                version=2,
                status="validated",
                validation_report_id=new_uuid7(),
                tables=[],
                slug="motor-gb",
                created_by=new_uuid7(),
                currency="GBP",
            )
            session.add_all([fitted_on, later])
            await session.flush()

            family = f"motor-{new_uuid7().hex[-8:]}"
            spec = GlmSpec(
                model_family_slug=family,
                dataset_version_id=fitted_on.id,
                response_column="claim_count",
                offset=OffsetSpec(kind="log_column", column="exposure_years"),
            )
            model = ModelRow(
                workspace_id=workspace_id,
                model_family_slug=family,
                version=1,
                status=ModelStatus.FITTED.value,
                dataset_version_id=fitted_on.id,
                spec=spec.model_dump(mode="json"),
                spec_hash=f"v3:sha256:{new_uuid7().hex}{new_uuid7().hex}",
                fit_result={"converged": True},
                diagnostics_id=new_uuid7(),
            )
            session.add(model)
            await session.flush()
            session.add(
                DiagnosticsRow(
                    id=model.diagnostics_id,
                    workspace_id=workspace_id,
                    model_id=model.id,
                    payload={"seeded": True},
                )
            )
            return model.id, later.id

    return _run(_insert)


def _seed_backtest(workspace_id: UUID) -> tuple[UUID, BacktestSummary]:
    """One stored backtest under `workspace_id`, and the summary it carries."""
    model_id, version_id = _seed_model_and_version(workspace_id)
    summary = _summary(
        model_ref=f"model:seeded@{version_id.hex[-4:]}",
        version_ref=f"dataset_version:later@{version_id.hex[-4:]}",
        fitted_on_ref=f"dataset_version:earlier@{version_id.hex[-4:]}",
    )

    async def _insert(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = BacktestRow(
                id=new_uuid7(),
                workspace_id=workspace_id,
                model_id=model_id,
                dataset_version_id=version_id,
                computed_at=datetime.now(UTC),
                payload=summary.model_dump(mode="json"),
            )
            session.add(row)
            await session.flush()
            return row.id

    return _run(_insert), summary


# -- The permits ---------------------------------------------------------------------------


@pytest.mark.req("FR-187")
def test_requesting_a_backtest_returns_202_and_points_at_the_result(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """202 and a `Location`, not the artifact.

    The route enqueues a Job; a caller that expected a `Backtest` body would read the Job
    and conclude the backtest was empty rather than pending.
    """
    model_id, version_id = _seed_model_and_version(workspace_id)
    response = client.post(
        f"/api/v1/models/{model_id}/backtest",
        json={"dataset_version_id": str(version_id)},
        headers=actuary,
    )
    assert response.status_code == 202, response.text
    assert response.headers["Location"] == f"/api/v1/jobs/{response.json()['id']}"
    assert response.json()["kind"] == "model.backtest"


@pytest.mark.req("FR-187")
def test_a_completed_backtest_reads_back_with_its_summary(
    client: TestClient, reader: dict[str, str], workspace_id: UUID
) -> None:
    """The stored artifact, whole, through the route that returns it.

    Asserts a field deep enough inside `summary` that a route returning a differently
    shaped artifact — a `Diagnostics`, or the Job — fails here rather than passing on the
    status code.

    Read by the **`auditor`**, which holds `model:read` and not `model:fit`. Reading it as
    the `analyst` would prove only that *some* authorised header works: the analyst holds
    both permissions, so a route re-gated on `model:fit` would keep this green while every
    read-only principal lost the artifact. Found by mutation on 2026-08-23 (W32-6) —
    swapping `ReadModels` for `FitModels` on the route left the whole file passing.
    """
    backtest_id, summary = _seed_backtest(workspace_id)
    response = client.get(f"/api/v1/models/backtests/{backtest_id}", headers=reader)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["id"] == str(backtest_id)
    assert body["summary"]["dataset_version_ref"] == summary.dataset_version_ref
    assert body["summary"]["fitted_on_ref"] == summary.fitted_on_ref
    assert body["summary"]["partition"]["ae_overall"] == 1.07
    assert body["summary"]["partition"]["weighting"] == "exposure"


# -- The refusals --------------------------------------------------------------------------


@pytest.mark.req("FR-94")
def test_a_backtest_in_another_workspace_is_not_found(
    client: TestClient, actuary: dict[str, str]
) -> None:
    """The highest-value test in this file.

    `load_backtest` folds `workspace_id` into its predicate, so a stranger gets 404 rather
    than 403 — the id must not be confirmed to exist. Nothing proved this before, and a
    refactor that moved the workspace check into a separate `if` would leak existence
    through a 403 while every platform test stayed green.

    The caller here is a **fully authorised principal of another workspace**. One holding no
    role would observe the RBAC refusal instead and prove nothing about scoping.
    """
    backtest_id, _ = _seed_backtest(new_uuid7())
    response = client.get(f"/api/v1/models/backtests/{backtest_id}", headers=actuary)
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-94")
def test_the_refusal_names_the_backtest_that_was_asked_for(
    client: TestClient, actuary: dict[str, str]
) -> None:
    """FR-94's "naming it" clause, which `load_backtest` implements as
    `f"No backtest {backtest_id} in this workspace."` — an operator holding an id from
    another environment needs to see *which* id was refused.

    Asserted on `detail`, the human-readable half of problem+json, because that is where
    the id lands; `code` is `NOT_FOUND` for every missing artifact and cannot carry it.
    """
    missing = new_uuid7()
    response = client.get(f"/api/v1/models/backtests/{missing}", headers=actuary)
    assert response.status_code == 404, response.text
    assert str(missing) in response.json()["detail"]


@pytest.mark.req("FR-94")
def test_reading_a_backtest_without_model_read_is_refused(
    client: TestClient, stranger: dict[str, str], workspace_id: UUID
) -> None:
    """**Negative.** The read route is gated, and the id it is given exists — so the 403 is
    the permission's answer and not a 404 wearing one."""
    backtest_id, _ = _seed_backtest(workspace_id)
    response = client.get(f"/api/v1/models/backtests/{backtest_id}", headers=stranger)
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-187")
def test_requesting_a_backtest_without_model_fit_is_refused(
    client: TestClient, reader: dict[str, str], workspace_id: UUID
) -> None:
    """`model:read` is not enough to *start* one.

    The permit above uses `analyst`, which holds both permissions; this caller is an
    `auditor`, which reads and cannot fit. The pair therefore distinguishes the two
    permissions rather than testing that some header works — and the request body is the
    same valid one, so the refusal cannot be the 422 a malformed request would earn.
    """
    model_id, version_id = _seed_model_and_version(workspace_id)
    response = client.post(
        f"/api/v1/models/{model_id}/backtest",
        json={"dataset_version_id": str(version_id)},
        headers=reader,
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"
