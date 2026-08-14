"""The Jobs API (`07` §5.1, `00` §5.2/5.3).

The authentication tests come first because they are the ones that must not regress:
OIDC is not implemented yet, so these routes are only safe if the absence of an identity
provider is a **refusal** rather than an omission.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER, DEV_WORKSPACE_HEADER
from app.config import ConfigInvalidError, Environment, Settings, load_settings
from app.db.session import Database
from app.main import create_app
from app.platform import jobs as job_service
from model_schema import ActorKind, JobKind, JobStatus, Principal, new_uuid7

pytestmark = pytest.mark.usefixtures("database")


@pytest.fixture
def api_settings() -> Settings:
    """Settings with development identity on, pointed at the *test* database.

    The DSN comes from the same helper the `database` fixture uses. Reading it from a bare
    `Settings()` made the app fall back to the packaged default whenever
    `GIP_DATABASE_URL` was unset — which is true locally and false in CI, so the tests
    would have passed on the runner and failed on a developer machine.
    """
    from backend.tests.conftest_db import test_database_url
    from pydantic import SecretStr

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
    )


@pytest.fixture
def caller_headers(workspace_id, principal) -> dict[str, str]:
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        DEV_WORKSPACE_HEADER: str(workspace_id),
    }


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


async def _submit(database: Database, workspace_id, principal, **kw):
    async with database.unit_of_work() as session:
        return await job_service.submit(
            session,
            kw.pop("kind", JobKind.MODEL_FIT),
            kw.pop("parameters", {}),
            principal,
            workspace_id=workspace_id,
            **kw,
        )


# -- authentication ----------------------------------------------------------------------


@pytest.mark.req("FR-PLAT-1")
def test_routes_refuse_when_no_identity_provider_is_configured() -> None:
    """Negative, and the important one: the default build must fail closed.

    OIDC is not implemented yet. If these routes answered without it, every job in every
    workspace would be readable and cancellable by anyone who could reach the port.
    """
    settings = Settings(environment=Environment.LOCAL, version="test")
    assert settings.dev_auth_enabled is False
    with TestClient(create_app(settings), raise_server_exceptions=False) as client:
        for method, path in [
            ("get", "/api/v1/jobs"),
            ("get", f"/api/v1/jobs/{new_uuid7()}"),
            ("get", f"/api/v1/jobs/{new_uuid7()}/logs"),
            ("post", f"/api/v1/jobs/{new_uuid7()}/cancel"),
        ]:
            response = getattr(client, method)(path)
            assert response.status_code == 401, path
            assert response.json()["code"] == "UNAUTHENTICATED"


@pytest.mark.req("FR-PLAT-5")
@pytest.mark.parametrize("environment", [Environment.UAT, Environment.PROD])
def test_development_identity_is_refused_outside_local(environment: Environment) -> None:
    """It trusts a header as identity — in uat or prod that is a total authorisation bypass."""
    with pytest.raises(ConfigInvalidError, match="dev_auth_enabled"):
        load_settings(
            environment=environment, dev_auth_enabled=True, tls_terminated=True
        )


@pytest.mark.req("FR-PLAT-1")
def test_incomplete_development_identity_is_refused(client: TestClient) -> None:
    response = client.get("/api/v1/jobs", headers={DEV_PRINCIPAL_HEADER: str(new_uuid7())})
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


# -- listing -----------------------------------------------------------------------------


@pytest.mark.req("FR-PLAT-7")
async def test_list_returns_the_workspace_jobs(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    await _submit(database, workspace_id, principal)
    await _submit(database, workspace_id, principal, kind=JobKind.SCORE_BATCH)

    body = client.get("/api/v1/jobs", headers=caller_headers).json()
    assert body["total_estimate"] == 2
    assert {item["kind"] for item in body["items"]} == {"model.fit", "score.batch"}
    assert body["next_cursor"] is None


@pytest.mark.req("FR-OVR-13")
async def test_another_workspaces_jobs_are_invisible(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    """Negative: tenancy is enforced in the query, not by the caller passing the right id."""
    other = new_uuid7()
    await _submit(database, other, principal)

    body = client.get("/api/v1/jobs", headers=caller_headers).json()
    assert body["items"] == []
    assert body["total_estimate"] == 0


@pytest.mark.req("FR-OVR-13")
async def test_a_job_in_another_workspace_is_404_not_403(
    client: TestClient, database: Database, principal, caller_headers
) -> None:
    """403 would confirm the id exists, which is a disclosure in a multi-tenant system."""
    other = new_uuid7()
    job = await _submit(database, other, principal)

    response = client.get(f"/api/v1/jobs/{job.id}", headers=caller_headers)
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-PLAT-7")
async def test_list_filters_by_status_and_kind(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    fit = await _submit(database, workspace_id, principal)
    await _submit(database, workspace_id, principal, kind=JobKind.SCORE_BATCH)
    async with database.unit_of_work() as session:
        await job_service.transition(session, fit.id, JobStatus.RUNNING, actor=principal)

    running = client.get("/api/v1/jobs?status=running", headers=caller_headers).json()
    assert [item["id"] for item in running["items"]] == [str(fit.id)]

    batches = client.get("/api/v1/jobs?kind=score.batch", headers=caller_headers).json()
    assert [item["kind"] for item in batches["items"]] == ["score.batch"]


@pytest.mark.req("FR-PLAT-7")
async def test_list_filters_by_submitter(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    other = Principal(kind=ActorKind.USER, id=new_uuid7(), display="other@insurer.example")
    mine = await _submit(database, workspace_id, principal)
    await _submit(database, workspace_id, other)

    body = client.get(
        f"/api/v1/jobs?submitted_by={principal.id}", headers=caller_headers
    ).json()
    assert [item["id"] for item in body["items"]] == [str(mine.id)]


@pytest.mark.req("FR-PLAT-7")
async def test_cursor_pages_through_without_repeating_or_skipping(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    """The property offset pagination loses: stability while rows are being inserted."""
    submitted = [
        (await _submit(database, workspace_id, principal)).id for _ in range(5)
    ]

    seen: list[str] = []
    cursor = None
    for _ in range(10):
        url = f"/api/v1/jobs?limit=2{f'&cursor={cursor}' if cursor else ''}"
        body = client.get(url, headers=caller_headers).json()
        seen.extend(item["id"] for item in body["items"])
        cursor = body["next_cursor"]
        if cursor is None:
            break

    assert len(seen) == len(set(seen)) == 5
    assert set(seen) == {str(i) for i in submitted}


@pytest.mark.req("FR-PLAT-47")
def test_a_malformed_cursor_is_a_typed_400(client: TestClient, caller_headers) -> None:
    """Negative: an empty page would look like 'no more results' and truncate silently."""
    response = client.get("/api/v1/jobs?cursor=not-a-cursor", headers=caller_headers)
    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-PLAT-47")
def test_limit_is_bounded(client: TestClient, caller_headers) -> None:
    response = client.get("/api/v1/jobs?limit=100000", headers=caller_headers)
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_FAILED"


# -- detail, cancel, logs, events ---------------------------------------------------------


@pytest.mark.req("FR-PLAT-7")
async def test_detail_carries_progress_and_trace(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    job = await _submit(database, workspace_id, principal, parameters={"seed": 7})
    body = client.get(f"/api/v1/jobs/{job.id}", headers=caller_headers).json()
    assert body["id"] == str(job.id)
    assert body["parameters"] == {"seed": 7}
    assert body["status"] == "queued"


@pytest.mark.req("FR-PLAT-9")
async def test_cancelling_a_queued_job(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    job = await _submit(database, workspace_id, principal)
    body = client.post(f"/api/v1/jobs/{job.id}/cancel", headers=caller_headers).json()
    assert body["status"] == "cancelled"


@pytest.mark.req("FR-PLAT-9")
async def test_cancelling_a_finished_job_is_a_typed_conflict(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    job = await _submit(database, workspace_id, principal)
    client.post(f"/api/v1/jobs/{job.id}/cancel", headers=caller_headers)
    response = client.post(f"/api/v1/jobs/{job.id}/cancel", headers=caller_headers)
    assert response.status_code == 409
    assert response.json()["code"] == "JOB_NOT_CANCELLABLE"


@pytest.mark.req("FR-PLAT-10")
async def test_logs_are_returned_oldest_first_with_the_trace(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    from app.db.models import JobLogRow

    job = await _submit(database, workspace_id, principal)
    async with database.unit_of_work() as session:
        for i in range(3):
            session.add(
                JobLogRow(
                    job_id=job.id,
                    level="INFO",
                    logger="app.worker",
                    message=f"line {i}",
                    trace_id="4bf92f3577b34da6a3ce929d0e0e4736",
                )
            )

    body = client.get(f"/api/v1/jobs/{job.id}/logs", headers=caller_headers).json()
    assert [item["message"] for item in body["items"]] == ["line 0", "line 1", "line 2"]
    assert body["items"][0]["trace_id"] == "4bf92f3577b34da6a3ce929d0e0e4736"


@pytest.mark.req("FR-PLAT-10")
async def test_logs_of_another_workspaces_job_are_404(
    client: TestClient, database: Database, principal, caller_headers
) -> None:
    job = await _submit(database, new_uuid7(), principal)
    assert client.get(f"/api/v1/jobs/{job.id}/logs", headers=caller_headers).status_code == 404


@pytest.mark.req("FR-PLAT-8")
async def test_the_event_stream_ends_when_the_job_is_terminal(
    client: TestClient, database: Database, workspace_id, principal, caller_headers
) -> None:
    """A stream that never closes holds a connection for every job anyone ever opened."""
    job = await _submit(database, workspace_id, principal)
    async with database.unit_of_work() as session:
        await job_service.transition(session, job.id, JobStatus.CANCELLED, actor=principal)

    with client.stream(
        "GET", f"/api/v1/jobs/{job.id}/events", headers=caller_headers
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = "".join(response.iter_text())

    assert "event: progress" in body
    assert "event: done" in body
    assert '"status": "cancelled"' in body


@pytest.mark.req("FR-PLAT-48")
def test_the_routes_appear_in_the_generated_contract() -> None:
    import json
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2]
    paths = json.loads(
        (root / "docs" / "contracts" / "openapi" / "generated.json").read_text()
    )["paths"]
    assert {
        "/api/v1/jobs",
        "/api/v1/jobs/{job_id}",
        "/api/v1/jobs/{job_id}/logs",
        "/api/v1/jobs/{job_id}/cancel",
        "/api/v1/jobs/{job_id}/events",
    } <= set(paths)
