"""The data API over HTTP (`01` §5.1).

The service tests already prove the rules. What these prove is that the rules are still
enforced *when reached through a route* — that a permission is checked, a cross-tenant id
is indistinguishable from a missing one, and the gate cannot be walked round by posting
the transition a caller wants.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api.deps import DEV_PRINCIPAL_HEADER, DEV_WORKSPACE_HEADER
from app.config import Environment, Settings
from app.main import create_app
from model_schema import new_uuid7


@pytest.fixture
def api_settings() -> Settings:
    from backend.tests.conftest_db import test_database_url

    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
    )


@pytest.fixture
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


def _headers(principal_id, workspace_id) -> dict[str, str]:
    return {
        DEV_PRINCIPAL_HEADER: str(principal_id),
        DEV_WORKSPACE_HEADER: str(workspace_id),
    }


@pytest_asyncio.fixture
async def analyst(workspace_id, principal, grant) -> dict[str, str]:
    await grant("analyst")
    return _headers(principal.id, workspace_id)


@pytest_asyncio.fixture
async def actuary(workspace_id, principal, grant) -> dict[str, str]:
    await grant("pricing_actuary")
    return _headers(principal.id, workspace_id)


def _slug() -> str:
    return f"ds-{new_uuid7().hex[-8:]}"


@pytest.mark.req("FR-DATA-1")
def test_a_source_never_returns_its_credentials(
    client: TestClient, analyst: dict[str, str]
) -> None:
    """FR-DATA-1 and `07` FR-PLAT-25: a Source holds a *reference* to a platform secret.

    The response shape has nowhere to put a credential, so there is no redaction step that
    could be forgotten — which is the only kind of redaction worth relying on.
    """
    body = {
        "slug": f"src-{new_uuid7().hex[-8:]}",
        "kind": "object_store",
        "config": {"bucket": "policies"},
        "credentials_secret_ref": "secret://minio/policies",
    }
    response = client.post("/api/v1/sources", json=body, headers=analyst)
    assert response.status_code == 201, response.text

    payload = response.json()
    assert payload["has_credentials"] is True
    assert "secret://minio/policies" not in response.text
    assert "credentials_secret_ref" not in payload

    listing = client.get("/api/v1/sources", headers=analyst)
    assert "secret://minio/policies" not in listing.text


@pytest.mark.req("FR-DATA-1")
def test_creating_a_dataset_requires_a_permission(
    client: TestClient, workspace_id, principal
) -> None:
    """Development identity carries no permissions. A route that answered anyway would
    make every other test in this file meaningless."""
    response = client.post(
        "/api/v1/datasets",
        json={"slug": _slug()},
        headers=_headers(principal.id, workspace_id),
    )
    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-DATA-5")
def test_a_dataset_round_trips_with_its_data_dictionary(
    client: TestClient, analyst: dict[str, str]
) -> None:
    slug = _slug()
    created = client.post(
        "/api/v1/datasets",
        json={
            "slug": slug,
            "name": "Motor GB — quote & bind",
            "line_of_business": "motor",
            "territory": "GB",
            "currency": "GBP",
            "default_record_grain": "policy_exposure",
            "data_dictionary": {
                "policy_id": {
                    "description": "Pseudonymous policy key",
                    "semantic_type": "identifier",
                    "pii_class": "pseudonymous_key",
                },
                "date_of_birth": {"description": "DOB", "pii_class": "direct_identifier"},
            },
        },
        headers=analyst,
    )
    assert created.status_code == 201, created.text

    fetched = client.get(f"/api/v1/datasets/{slug}", headers=analyst)
    assert fetched.status_code == 200
    payload = fetched.json()
    assert payload["data_dictionary"]["policy_id"]["pii_class"] == "pseudonymous_key"
    assert payload["currency"] == "GBP"
    assert payload["latest_version"] is None


@pytest.mark.req("NFR-DATA-8")
def test_replacing_the_dictionary_is_audited_with_before_and_after(
    client: TestClient, analyst: dict[str, str], database, workspace_id
) -> None:
    """NFR-DATA-8. The dictionary decides which columns may be modelled at all, so "who
    removed the special-category marking, and when?" has to be answerable."""
    slug = _slug()
    client.post(
        "/api/v1/datasets",
        json={
            "slug": slug,
            "data_dictionary": {"ethnicity": {"pii_class": "special_category"}},
        },
        headers=analyst,
    )
    replaced = client.put(
        f"/api/v1/datasets/{slug}/dictionary",
        json={"data_dictionary": {"ethnicity": {"pii_class": "none"}}},
        headers=analyst,
    )
    assert replaced.status_code == 200, replaced.text
    assert replaced.json()["data_dictionary"]["ethnicity"]["pii_class"] == "none"

    # Read from the table rather than `GET /audit`: that route requires `audit:read`,
    # which an analyst does not hold, and the claim under test is about what was written.
    import asyncio

    from sqlalchemy import select

    from app.db.models import AuditEventRow

    async def event():
        async with database.session() as session:
            return (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == "dataset.dictionary_updated",
                    )
                )
            ).scalar_one()

    entry = asyncio.get_event_loop().run_until_complete(event())
    assert entry.before["data_dictionary"]["ethnicity"]["pii_class"] == "special_category"
    assert entry.after["data_dictionary"]["ethnicity"]["pii_class"] == "none"


@pytest.mark.req("FR-DATA-2")
def test_starting_an_ingestion_returns_202_and_a_job(
    client: TestClient, analyst: dict[str, str]
) -> None:
    """`00` §5.1 R1: a long operation returns 202 with the Job and a `Location`.

    No version is created here. A version that existed before its data did is a version
    something could be fitted on.
    """
    slug = _slug()
    client.post("/api/v1/datasets", json={"slug": slug}, headers=analyst)
    response = client.post(
        f"/api/v1/datasets/{slug}/versions",
        json={"blob": "a" * 64, "filename": "exposure.csv", "recipe": []},
        headers=analyst,
    )
    assert response.status_code == 202, response.text
    assert response.headers["Location"] == f"/api/v1/jobs/{response.json()['id']}"
    assert response.json()["kind"] == "dataset.ingest"
    assert response.json()["status"] == "queued"

    versions = client.get(f"/api/v1/datasets/{slug}", headers=analyst)
    assert versions.json()["latest_version"] is None


@pytest.mark.req("FR-DATA-17")
def test_a_version_cannot_be_validated_without_naming_its_report(
    client: TestClient, actuary: dict[str, str], workspace_id, principal, database
) -> None:
    """`01` §1.3 over HTTP: the caller says *which* report, never whether it passed."""
    import asyncio

    from app.platform import datasets as service

    async def make_version():
        async with database.unit_of_work() as session:
            dataset = await service.create_dataset(
                session, workspace_id=workspace_id, actor=principal, slug=_slug()
            )
            version = await service.new_version(
                session, workspace_id=workspace_id, actor=principal, dataset_id=dataset.id
            )
            return version.id

    version_id = asyncio.get_event_loop().run_until_complete(make_version())
    response = client.post(
        f"/api/v1/dataset-versions/{version_id}/transition",
        json={"to": "validated"},
        headers=actuary,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_HAS_FAILURES"


@pytest.mark.req("FR-OVR-13")
def test_a_version_in_another_workspace_is_a_404(
    client: TestClient, analyst: dict[str, str]
) -> None:
    """A 403 would confirm the id exists, which is a disclosure in a multi-tenant system
    even when the body says nothing else."""
    response = client.get(
        f"/api/v1/dataset-versions/{new_uuid7()}/profile", headers=analyst
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-DATA-4")
def test_previewing_a_source_creates_nothing(
    client: TestClient, analyst: dict[str, str]
) -> None:
    """FR-DATA-4: the point of a preview is that it is free to be wrong.

    A preview that left a trace would make "just have a look at this file" an audited act,
    and people would stop looking.
    """
    source = client.post(
        "/api/v1/sources",
        json={"slug": f"src-{new_uuid7().hex[-8:]}", "kind": "upload"},
        headers=analyst,
    ).json()

    csv = b"Policy ID,Exposure Years\nP1,1.0\nP2,0.5\n"
    response = client.post(
        f"/api/v1/sources/{source['id']}/preview",
        files={"file": ("exposure.csv", csv, "text/csv")},
        headers=analyst,
    )
    assert response.status_code == 200, response.text
    payload = response.json()

    # The normalised names, and what they were before — a silent rename is the one thing
    # more confusing than a rejected file.
    assert payload["source_names"]["policy_id"] == "Policy ID"
    assert payload["row_count_in_sample"] == 2
    assert [column["name"] for column in payload["columns"]] == [
        "policy_id",
        "exposure_years",
    ]

    datasets = client.get("/api/v1/datasets", headers=analyst).json()
    assert all(d["slug"] != "exposure" for d in datasets["items"])


@pytest.mark.req("FR-DATA-31")
def test_reference_lookup_is_effective_dated_and_half_open(
    client: TestClient, workspace_id, principal, grant
) -> None:
    """FR-DATA-31. The interval is `[from, to)`, so a row ending on a date does not cover
    it — which is exactly what lets consecutive versions abut without overlapping."""
    import asyncio

    asyncio.get_event_loop().run_until_complete(grant("admin"))
    headers = _headers(principal.id, workspace_id)
    slug = f"ref-{new_uuid7().hex[-8:]}"

    assert (
        client.post(
            "/api/v1/reference-tables",
            json={"slug": slug, "key_columns": ["area"], "payload_columns": ["factor"]},
            headers=headers,
        ).status_code
        == 201
    )
    loaded = client.post(
        f"/api/v1/reference-tables/{slug}/versions",
        json={
            "rows": [
                {
                    "key": "AB",
                    "payload": {"factor": 1.1},
                    "effective_from": "2024-01-01",
                    "effective_to": "2025-01-01",
                },
                {"key": "AB", "payload": {"factor": 1.2}, "effective_from": "2025-01-01"},
            ]
        },
        headers=headers,
    )
    assert loaded.status_code == 201, loaded.text
    client.post(
        f"/api/v1/reference-tables/{slug}/versions/1/publish", headers=headers
    )

    def factor(as_at: str) -> float:
        response = client.get(
            f"/api/v1/reference-tables/{slug}/lookup",
            params={"key": "AB", "as_at": as_at},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        return response.json()["payload"]["factor"]

    assert factor("2024-06-01") == 1.1
    # The boundary: 2025-01-01 belongs to the *second* row, not the first.
    assert factor("2025-01-01") == 1.2

    missing = client.get(
        f"/api/v1/reference-tables/{slug}/lookup",
        params={"key": "AB", "as_at": "2023-01-01"},
        headers=headers,
    )
    assert missing.status_code == 404


@pytest.mark.req("FR-DATA-31")
def test_overlapping_reference_intervals_are_refused(
    client: TestClient, workspace_id, principal, grant
) -> None:
    """Two rows covering one date give a lookup two answers, and which one a quote gets
    would depend on row order — a rating difference nobody could reproduce."""
    import asyncio

    asyncio.get_event_loop().run_until_complete(grant("admin"))
    headers = _headers(principal.id, workspace_id)
    slug = f"ref-{new_uuid7().hex[-8:]}"
    client.post(
        "/api/v1/reference-tables",
        json={"slug": slug, "key_columns": ["area"]},
        headers=headers,
    )

    response = client.post(
        f"/api/v1/reference-tables/{slug}/versions",
        json={
            "rows": [
                {
                    "key": "AB",
                    "effective_from": "2024-01-01",
                    "effective_to": "2025-06-01",
                },
                {"key": "AB", "effective_from": "2025-01-01"},
            ]
        },
        headers=headers,
    )
    assert response.status_code == 409
    assert response.json()["code"] == "REFERENCE_INTERVAL_OVERLAP"


@pytest.mark.req("NFR-DATA-7")
def test_the_report_summary_stays_under_its_budget_at_500_rules(
    client: TestClient, actuary: dict[str, str], database, workspace_id, principal
) -> None:
    """NFR-DATA-7: the summary for a report of up to 500 rules returns in < 500 ms.

    Measured against the list endpoint because that is the one with a budget: it returns
    counts and verdicts read from indexed columns, never the bodies. Deserialising fifty
    500-rule reports to render a list of dates is the difference between meeting this and
    missing it, which is why the summary and the artifact are different endpoints.

    The assertion is deliberately loose — five times the budget — because a shared runner's timing
    is noise. It is a *regression* guard: it catches the day someone makes the list load
    bodies, which costs an order of magnitude, not a few milliseconds.
    """
    import asyncio
    import time
    from datetime import UTC, datetime, timedelta
    from uuid import uuid4

    from app.platform import datasets as dataset_service
    from app.platform import validation as validation_service
    from model_schema import RuleOutcome, Severity, ValidationLayer, ValidationReport
    from model_schema.validation import RuleResult

    async def seed() -> tuple[str, int]:
        async with database.unit_of_work() as session:
            dataset = await dataset_service.create_dataset(
                session, workspace_id=workspace_id, actor=principal, slug=_slug()
            )
            version = await dataset_service.new_version(
                session, workspace_id=workspace_id, actor=principal, dataset_id=dataset.id
            )
            version_id = version.id
        started = datetime.now(UTC)
        results = tuple(
            RuleResult(
                rule_id=uuid4(),
                rule_slug=f"rule-{index:03d}",
                rule_version=1,
                layer=ValidationLayer.STRUCTURAL,
                severity=Severity.WARN,
                outcome=RuleOutcome.WARN if index % 50 == 0 else RuleOutcome.PASS,
                detail="x" * 200,
                offending_sample=tuple(f"P{n}" for n in range(20)),
            )
            for index in range(500)
        )
        async with database.unit_of_work() as session:
            await validation_service.store_report(
                session,
                workspace_id=workspace_id,
                actor=principal,
                report=ValidationReport(
                    id=uuid4(),
                    dataset_version_id=version_id,
                    rule_set_id=uuid4(),
                    rule_set_version=1,
                    started_at=started,
                    finished_at=started + timedelta(seconds=1),
                    results=results,
                ),
            )
        return str(version_id), len(results)

    version_id, rule_count = asyncio.get_event_loop().run_until_complete(seed())

    client.get(f"/api/v1/dataset-versions/{version_id}/validation-reports", headers=actuary)
    start = time.perf_counter()
    response = client.get(
        f"/api/v1/dataset-versions/{version_id}/validation-reports", headers=actuary
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200, response.text
    summary = response.json()[0]
    assert summary["rule_count"] == rule_count
    assert summary["warn_count"] == 10
    assert summary["unacknowledged_warnings"] == 10
    # The summary carries no rule results at all — that is what makes it a summary.
    assert "results" not in summary
    assert elapsed_ms < 2_500, f"summary took {elapsed_ms:.0f} ms against a 500 ms budget"
    print(f"\n  NFR-DATA-7: {elapsed_ms:.0f} ms for {rule_count} rules (budget 500 ms)")


@pytest.mark.req("NFR-DATA-9")
def test_the_sql_check_is_refused_while_its_workspace_flag_is_off(
    client: TestClient, workspace_id, principal, grant
) -> None:
    """OQ-DATA-3: gated by `features.sql_validation_check_enabled`, defaulting to off.

    Checked when the rule is *authored*, not only when it runs. A draft `sql` rule sitting
    in a workspace with the flag off is a rule waiting for someone to turn the flag on for
    an unrelated reason.
    """
    import asyncio

    # Both roles: a `sql` rule needs `admin:manage_settings` and a declarative one needs
    # `dataset:write`, and this test compares the two paths for one caller.
    asyncio.get_event_loop().run_until_complete(grant("admin"))
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal.id, workspace_id)

    refused = client.post(
        "/api/v1/validation-rules",
        json={
            "slug": f"sql-{new_uuid7().hex[-8:]}",
            "layer": "actuarial_sanity",
            "check": "sql",
            "severity": "fail",
            "params": {"query": "SELECT count(*) FROM exposure"},
        },
        headers=headers,
    )
    assert refused.status_code == 409, refused.text
    assert "sql_validation_check_enabled" in refused.json()["detail"]

    # A declarative rule is unaffected — the gate is on the escape hatch, not on authoring.
    allowed = client.post(
        "/api/v1/validation-rules",
        json={
            "slug": f"rng-{new_uuid7().hex[-8:]}",
            "layer": "structural",
            "check": "not_null",
            "severity": "fail",
            "target": {"table": "exposure", "column": "policy_id"},
            "params": {"columns": ["policy_id"], "key_columns": ["policy_id"]},
        },
        headers=headers,
    )
    assert allowed.status_code == 201, allowed.text
    assert allowed.json()["status"] == "draft"


@pytest.mark.req("FR-PLAT-12")
def test_a_repeated_submission_with_one_idempotency_key_starts_one_job(
    client: TestClient, analyst: dict[str, str]
) -> None:
    """`00` §5.4: every POST that creates a Job or artifact accepts `Idempotency-Key`, and
    a repeat returns the original result.

    A **header**, not a query parameter — a retry is generated by an HTTP client that knows
    nothing about this endpoint's query string, and a key in the URL is also a key in every
    access log.
    """
    slug = _slug()
    client.post("/api/v1/datasets", json={"slug": slug}, headers=analyst)
    body = {"blob": "b" * 64, "filename": "exposure.csv", "recipe": []}
    key = {"Idempotency-Key": f"retry-{new_uuid7()}"}

    first = client.post(f"/api/v1/datasets/{slug}/versions", json=body,
                        headers={**analyst, **key})
    second = client.post(f"/api/v1/datasets/{slug}/versions", json=body,
                         headers={**analyst, **key})
    assert first.status_code == second.status_code == 202
    assert first.json()["id"] == second.json()["id"], "the retry started a second job"

    without = client.post(f"/api/v1/datasets/{slug}/versions", json=body, headers=analyst)
    assert without.json()["id"] != first.json()["id"]
