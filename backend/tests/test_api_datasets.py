"""The data API over HTTP (`01` §5.1).

The service tests already prove the rules. What these prove is that the rules are still
enforced *when reached through a route* — that a permission is checked, a cross-workspace id
is indistinguishable from a missing one, and the gate cannot be walked round by posting
the transition a caller wants.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.session import Database
from model_schema import new_uuid7


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    """The shared DB-backed client, under the name this module's tests already use."""
    return api_client


def _headers(principal_id, workspace_id) -> dict[str, str]:
    """Headers for a caller granted in `workspace_id` (W6b-11).

    `Workspace-Id` is the same header every caller path reads, and it names a membership
    — `grant` seeds one, so the selection is checked and accepted. The old
    `x-dev-workspace-id` pin, which bypassed the membership check entirely, is gone.
    """
    return {
        DEV_PRINCIPAL_HEADER: str(principal_id),
        "Workspace-Id": str(workspace_id),
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
async def test_creating_a_dataset_requires_a_permission(
    client: TestClient, workspace_id, principal, membership
) -> None:
    """Development identity carries no permissions. A route that answered anyway would
    make every other test in this file meaningless.

    The caller is a member but holds no role (W6b-11), so the refusal is the route's own
    permission check rather than the membership check's `UNAUTHENTICATED`.
    """
    await membership()
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
    """A 403 would confirm the id exists, which discloses another workspace's work
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


@pytest.mark.req("FR-DATA-2")
def test_the_version_timeline_is_newest_first_and_paginated(
    client: TestClient, analyst: dict[str, str], database, workspace_id, principal
) -> None:
    """`01` §5.3 renders a version timeline, and §5.1 offered no way to fetch one — only
    `latest_version` and per-version detail, so a client had to issue one request per
    version and could not show a status without fetching them all.

    Newest first, because a timeline is read from the top: a dataset refreshed monthly for
    ten years has a hundred and twenty versions.
    """
    import asyncio

    from app.platform import datasets as service

    slug = _slug()

    async def seed() -> None:
        async with database.unit_of_work() as session:
            dataset = await service.create_dataset(
                session, workspace_id=workspace_id, actor=principal, slug=slug
            )
            for _ in range(4):
                await service.new_version(
                    session, workspace_id=workspace_id, actor=principal,
                    dataset_id=dataset.id,
                )

    asyncio.get_event_loop().run_until_complete(seed())

    first = client.get(
        f"/api/v1/datasets/{slug}/versions", params={"limit": 3}, headers=analyst
    )
    assert first.status_code == 200, first.text
    page = first.json()
    assert [item["version"] for item in page["items"]] == [4, 3, 2]
    assert page["total_estimate"] == 4
    assert page["next_cursor"]

    second = client.get(
        f"/api/v1/datasets/{slug}/versions",
        params={"limit": 3, "cursor": page["next_cursor"]},
        headers=analyst,
    )
    assert [item["version"] for item in second.json()["items"]] == [1]
    assert second.json()["next_cursor"] is None


@pytest.mark.req("FR-DATA-21")
def test_a_rule_walks_draft_to_approved_and_never_by_its_author(
    client: TestClient, workspace_id, principal, grant, database
) -> None:
    """FR-DATA-21's chain, over HTTP: author → dry-run → submit → approve.

    §5.1 exposed no approve route, so a rule could be authored, dry-run and submitted and
    then sat in `review` with no way out — and since a Rule Set refuses any rule that is
    not `approved`, nothing authored through the API could ever be used. Found by walking
    the chain the rule-set editor needs.

    The separation is the control: `01` §4.5 step 3 says "approved by an Approver (never
    the author)", and it holds even when one person has both roles.
    """
    import asyncio

    from app.db.models import ValidationRuleRow

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("approver"))
    headers = _headers(principal.id, workspace_id)

    created = client.post(
        "/api/v1/validation-rules",
        json={
            "slug": f"rng-{new_uuid7().hex[-8:]}",
            "layer": "actuarial_sanity",
            "check": "range",
            "severity": "warn",
            "target": {"table": "policy_exposure", "column": "driv_age"},
            "params": {"min_inclusive": 18, "key_columns": ["policy_id"]},
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    rule_id = created.json()["id"]
    assert created.json()["status"] == "draft"

    # Step 2: no dry run, no submission. An approver reading JSON cannot tell whether a
    # rule selects three rows or three million.
    refused = client.post(f"/api/v1/validation-rules/{rule_id}/submit", headers=headers)
    assert refused.status_code == 409
    assert refused.json()["code"] == "RULE_NOT_APPROVED"

    async def attach_dry_run() -> None:
        async with database.unit_of_work() as session:
            row = await session.get(ValidationRuleRow, UUID(rule_id))
            row.dry_run_report_id = new_uuid7()

    asyncio.get_event_loop().run_until_complete(attach_dry_run())

    submitted = client.post(f"/api/v1/validation-rules/{rule_id}/submit", headers=headers)
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["status"] == "review"

    # Step 3: this principal authored it, and holds `approval:decide`. The role is not the
    # control — the separation is.
    self_approved = client.post(
        f"/api/v1/validation-rules/{rule_id}/approve", headers=headers
    )
    assert self_approved.status_code == 409
    assert self_approved.json()["code"] == "SUBMITTER_CANNOT_APPROVE"

    approver = new_uuid7()
    asyncio.get_event_loop().run_until_complete(
        grant("approver", principal_id=approver)
    )
    approved = client.post(
        f"/api/v1/validation-rules/{rule_id}/approve",
        headers=_headers(approver, workspace_id),
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"


def _approved_rule(client, headers, approver_headers, database, **over) -> str:
    """Walk a rule to `approved` — the only state a Rule Set will accept."""
    import asyncio

    from app.db.models import ValidationRuleRow

    body = {
        "slug": f"rng-{new_uuid7().hex[-8:]}",
        "layer": "actuarial_sanity",
        "check": "range",
        "severity": "warn",
        "target": {"table": "policy_exposure", "column": "driv_age"},
        "params": {"min_inclusive": 18, "key_columns": ["policy_id"]},
    }
    body.update(over)
    created = client.post("/api/v1/validation-rules", json=body, headers=headers)
    assert created.status_code == 201, created.text
    rule_id = created.json()["id"]

    async def attach() -> None:
        async with database.unit_of_work() as session:
            row = await session.get(ValidationRuleRow, UUID(rule_id))
            row.dry_run_report_id = new_uuid7()

    asyncio.get_event_loop().run_until_complete(attach())
    assert client.post(
        f"/api/v1/validation-rules/{rule_id}/submit", headers=headers
    ).status_code == 200
    assert client.post(
        f"/api/v1/validation-rules/{rule_id}/approve", headers=approver_headers
    ).status_code == 200
    return rule_id


@pytest.mark.req("FR-DATA-22")
def test_a_rule_set_entry_carries_its_enabled_flag_and_override(
    client: TestClient, workspace_id, principal, grant, database
) -> None:
    """`01` §4.3's entry fields, over HTTP.

    The replace body took a bare list of rule ids, so neither field could be expressed by
    any caller: a rule could be turned off nowhere but in the database, and the "may only
    raise" invariant guarded something unreachable. Found by building §5.3's rule-set
    editor against the API and having nothing to bind the enable/disable control to.
    """
    import asyncio

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal.id, workspace_id)
    approver = new_uuid7()
    asyncio.get_event_loop().run_until_complete(grant("approver", principal_id=approver))
    approver_headers = _headers(approver, workspace_id)

    slug = f"ds-{new_uuid7().hex[-8:]}"
    assert client.post(
        "/api/v1/datasets", json={"slug": slug, "name": "Entry fields"}, headers=headers
    ).status_code == 201

    kept = _approved_rule(client, headers, approver_headers, database)
    parked = _approved_rule(
        client, headers, approver_headers, database, layer="structural", check="not_null",
        params={"key_columns": ["policy_id"]},
    )

    put = client.put(
        f"/api/v1/datasets/{slug}/rule-set",
        json={
            "rules": [
                {"rule_id": kept, "severity_override": "fail"},
                {"rule_id": parked, "enabled": False},
            ]
        },
        headers=headers,
    )
    assert put.status_code == 200, put.text

    got = client.get(f"/api/v1/datasets/{slug}/rule-set", headers=headers).json()
    entries = {entry["rule"]["id"]: entry for entry in got["entries"]}
    assert entries[kept]["severity_override"] == "fail"
    assert entries[parked]["enabled"] is False
    # A disabled entry is still *in* the set — it is not a deletion — but it does not
    # cover its layer, so FR-DATA-16's warning names that layer.
    assert "structural" in got["empty_layers"]
    assert "actuarial_sanity" not in got["empty_layers"]


@pytest.mark.req("FR-DATA-22")
def test_an_override_may_raise_severity_but_never_lower_it(
    client: TestClient, workspace_id, principal, grant, database
) -> None:
    """`01` §4.3: `warn → fail` is a workspace tightening a shipped rule and needs no review.

    `fail → warn` is a workspace deciding a failure is acceptable — a change to the rule,
    which goes through the rule's own review (FR-DATA-21) where somebody sees it. Allowing
    it here would be a way to pass validation without changing anything a reviewer reads.
    """
    import asyncio

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal.id, workspace_id)
    approver = new_uuid7()
    asyncio.get_event_loop().run_until_complete(grant("approver", principal_id=approver))
    approver_headers = _headers(approver, workspace_id)

    slug = f"ds-{new_uuid7().hex[-8:]}"
    client.post("/api/v1/datasets", json={"slug": slug, "name": "Overrides"}, headers=headers)
    strict = _approved_rule(client, headers, approver_headers, database, severity="fail")

    lowered = client.put(
        f"/api/v1/datasets/{slug}/rule-set",
        json={"rules": [{"rule_id": strict, "severity_override": "warn"}]},
        headers=headers,
    )
    assert lowered.status_code == 409, lowered.text
    assert lowered.json()["code"] == "RULE_SEVERITY_DOWNGRADE_FORBIDDEN"

    # ...and the refusal is specific to the direction, not to overrides.
    lenient = _approved_rule(client, headers, approver_headers, database, severity="warn")
    raised = client.put(
        f"/api/v1/datasets/{slug}/rule-set",
        json={"rules": [{"rule_id": lenient, "severity_override": "fail"}]},
        headers=headers,
    )
    assert raised.status_code == 200, raised.text


@pytest.mark.req("FR-DATA-2")
def test_the_dataset_list_carries_each_dataset_s_latest_version(
    client: TestClient, workspace_id, principal, grant, database
) -> None:
    """`01` §5.3 names it as one of four columns the list must show.

    It rendered empty for every row: the list called `to_schema(row)` with no version while
    the detail route passed one, so a dataset with two versions read as having none. Found
    by driving the demo entrance — the dataset list is its first screen — and not by any
    test, because every test that cared about a version number asked the detail route.
    """
    import asyncio

    from app.platform import datasets as dataset_service

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal.id, workspace_id)

    async def _dataset(slug: str, versions: int) -> None:
        async with database.unit_of_work() as session:
            row = await dataset_service.create_dataset(
                session, workspace_id=workspace_id, actor=principal, slug=slug
            )
            for _ in range(versions):
                await dataset_service.new_version(
                    session, workspace_id=workspace_id, actor=principal, dataset_id=row.id
                )

    versioned, bare = f"ds-{new_uuid7().hex[-8:]}", f"ds-{new_uuid7().hex[-8:]}"
    asyncio.get_event_loop().run_until_complete(_dataset(versioned, 2))
    asyncio.get_event_loop().run_until_complete(_dataset(bare, 0))

    listed = {
        item["slug"]: item
        for item in client.get("/api/v1/datasets", headers=headers).json()["items"]
    }
    assert listed[versioned]["latest_version"] == 2, "the list must agree with the detail route"
    assert (
        client.get(f"/api/v1/datasets/{versioned}", headers=headers).json()["latest_version"]
        == 2
    )
    # A dataset with no versions reports null rather than 0 — "none yet" and "version zero"
    # are different claims, and only one of them is true.
    assert listed[bare]["latest_version"] is None


def _run(coro):
    """Drive one coroutine from a synchronous test.

    `asyncio.get_event_loop()` rather than a loop of our own: the `database` fixture's
    engine binds its connections to the loop `pytest-asyncio` created for it, and a second
    loop produces `got Future attached to a different loop` — which reads like a driver
    bug. `test_the_dataset_list_carries_each_dataset_s_latest_version` above reaches for
    the same construction.
    """
    return asyncio.get_event_loop().run_until_complete(coro)


async def _draft_dataset(
    database: Database, workspace_id: UUID, actor, slug: str, *, versions: int = 1
) -> UUID:
    from app.platform import datasets as dataset_service

    async with database.unit_of_work() as session:
        row = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=slug
        )
        for _ in range(versions):
            await dataset_service.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=row.id
            )
        return row.id


async def _validate_latest(
    database: Database,
    workspace_id: UUID,
    actor,
    dataset_id: UUID,
    *,
    finished_at: datetime,
) -> int:
    """Take the dataset's newest version through `validating → validated`, and say which.

    The report row is inserted directly rather than through `validation.store_report`:
    what `_last_validated` reads is `finished_at`, and building a whole `ValidationReport`
    to carry one timestamp would put the rule engine in the path of a list test.
    """
    from sqlalchemy import select

    from app.db.models import DatasetVersionRow, ValidationReportRow
    from app.platform import datasets as dataset_service
    from model_schema import DatasetStatus

    async with database.unit_of_work() as session:
        version = (
            await session.execute(
                select(DatasetVersionRow)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc())
                .limit(1)
            )
        ).scalar_one()
        version_id, version_number = version.id, version.version
        report = ValidationReportRow(
            id=new_uuid7(),
            workspace_id=workspace_id,
            dataset_version_id=version_id,
            rule_set_id=new_uuid7(),
            rule_set_version=1,
            overall="pass",
            rule_count=0,
            body={},
            started_at=finished_at,
            finished_at=finished_at,
        )
        session.add(report)
        await session.flush()
        await dataset_service.transition(
            session,
            workspace_id=workspace_id,
            actor=actor,
            version_id=version_id,
            to_status=DatasetStatus.VALIDATING,
        )
        await dataset_service.promote_to_validated(
            session,
            workspace_id=workspace_id,
            actor=actor,
            version_id=version_id,
            report_id=report.id,
            report_passed=True,
            unacknowledged_warnings=0,
        )
    return int(version_number)


@pytest.mark.req("FR-DATA-50")
def test_the_list_carries_the_latest_version_s_status(
    client: TestClient, workspace_id, principal, grant, database
) -> None:
    """The badge. Blank before this slice: `to_schema` had nowhere to put a status."""
    _run(grant("analyst"))
    headers = _headers(principal.id, workspace_id)
    slug = _slug()
    _run(_draft_dataset(database, workspace_id, principal, slug, versions=1))

    body = client.get("/api/v1/datasets", headers=headers).json()
    row = next(item for item in body["items"] if item["slug"] == slug)
    assert row["latest_version"] == 1
    assert row["latest_version_status"] == "draft"
    assert row["last_validated_at"] is None
    assert row["last_validated_version"] is None


@pytest.mark.req("FR-DATA-50")
def test_a_draft_above_a_validated_version_reports_both_and_says_which(
    client: TestClient, workspace_id, principal, grant, database
) -> None:
    """FR-DATA-50's worked example, and the only test that can catch the two fields being
    computed from the same version.

    Build v1, validate it, then create v2 and leave it `draft`. The badge must read
    `draft` for v2 while the date belongs to v1 — a list that computed both from
    `latest_version` would report no validation date at all and look entirely plausible.
    """
    from app.platform import datasets as dataset_service

    _run(grant("analyst"))
    headers = _headers(principal.id, workspace_id)
    slug = _slug()
    dataset_id = _run(_draft_dataset(database, workspace_id, principal, slug, versions=1))
    validated = _run(
        _validate_latest(
            database,
            workspace_id,
            principal,
            dataset_id,
            finished_at=datetime(2026, 8, 20, 9, 30, tzinfo=UTC),
        )
    )

    async def _second_version() -> None:
        async with database.unit_of_work() as session:
            await dataset_service.new_version(
                session, workspace_id=workspace_id, actor=principal, dataset_id=dataset_id
            )

    _run(_second_version())

    body = client.get("/api/v1/datasets", headers=headers).json()
    row = next(item for item in body["items"] if item["slug"] == slug)
    assert row["latest_version"] == 2
    assert row["latest_version_status"] == "draft"
    assert row["last_validated_version"] == validated == 1
    assert row["last_validated_at"] is not None
    assert row["last_validated_at"].startswith("2026-08-20T09:30")

    # The detail route must agree with the list — a detail page showing nothing where the
    # list shows a date would be its own defect.
    detail = client.get(f"/api/v1/datasets/{slug}", headers=headers).json()
    assert detail["latest_version_status"] == "draft"
    assert detail["last_validated_version"] == 1


@pytest.mark.req("FR-DATA-50")
def test_the_page_costs_the_same_number_of_statements_at_any_size(
    client: TestClient, workspace_id, principal, grant, database
) -> None:
    """FR-DATA-50 budgets "one further aggregate"; `_latest_versions`' own docstring
    records the 51-round-trip defect this guards against.

    Counted with a SQLAlchemy `before_cursor_execute` listener rather than asserted in
    prose, because an N+1 reintroduced by a later refactor is invisible to every other
    test in this file.
    """
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    _run(grant("analyst"))
    headers = _headers(principal.id, workspace_id)
    for _ in range(3):
        _run(_draft_dataset(database, workspace_id, principal, _slug(), versions=1))

    # Warm the pool and the app's lazily-built state, so what is counted below is the page
    # and not a first-request cost.
    client.get("/api/v1/datasets", headers=headers)

    statements: list[str] = []

    def _count(conn, cursor, statement, parameters, context, executemany) -> None:
        statements.append(statement)

    event.listen(Engine, "before_cursor_execute", _count)
    try:
        small = client.get("/api/v1/datasets?limit=3", headers=headers)
        at_three = len(statements)

        event.remove(Engine, "before_cursor_execute", _count)
        for _ in range(7):
            _run(_draft_dataset(database, workspace_id, principal, _slug(), versions=1))
        statements.clear()
        event.listen(Engine, "before_cursor_execute", _count)

        large = client.get("/api/v1/datasets?limit=10", headers=headers)
        at_ten = len(statements)
    finally:
        event.remove(Engine, "before_cursor_execute", _count)

    assert small.status_code == 200, small.text
    assert large.status_code == 200, large.text
    assert len(small.json()["items"]) == 3
    assert len(large.json()["items"]) == 10
    # Six, not five. FR-DATA-50's "one further aggregate" budgets the *page's* queries,
    # and four of these are it: the row query, the capped count, `_latest_versions` and
    # `_last_validated`. The fifth is `requires(DATASET_READ)`'s role-assignment lookup,
    # and the sixth is the `workspace_members` read in identity resolution (W6b-11): the
    # caller's workspace set comes from the database, never from a header. Both are
    # per-request authorisation costs every route in this file pays, independent of the
    # page and of this slice. Counted rather than filtered out, because a listener that
    # only counts the statements it expects cannot catch an N+1 in one it does not.
    assert at_three == at_ten == 6, (
        f"a page costs {at_three} statements at 3 rows and {at_ten} at 10; the budget is "
        "six — the memberships read, the permission check, the row query, the capped "
        f"count, the latest-version aggregate and the one further aggregate.\n{statements!r}"
    )


@pytest.mark.req("FR-DATA-51")
def test_a_created_dataset_is_owned_by_its_creator(
    client: TestClient, analyst: dict[str, str], principal
) -> None:
    slug = _slug()
    created = client.post("/api/v1/datasets", json={"slug": slug}, headers=analyst)
    assert created.status_code == 201, created.text
    assert created.json()["owner_id"] == str(principal.id)


@pytest.mark.req("FR-DATA-51")
async def test_the_system_principal_cannot_own_a_dataset(database, workspace_id) -> None:
    """`Principal.id` is null only for `system`, and FR-DATA-51 makes `owner_id` non-null.

    Asserted at the service rather than over HTTP: no route authenticates as `system`, and
    a nullable column would have swallowed this silently.
    """
    from app.errors import PlatformError
    from app.platform import datasets as dataset_service
    from model_schema import ActorKind, Principal

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await dataset_service.create_dataset(
                session,
                workspace_id=workspace_id,
                actor=Principal(kind=ActorKind.SYSTEM),
                slug=_slug(),
            )
    assert exc.value.code == "VALIDATION_FAILED"
    assert "owner" in exc.value.detail.lower()


def _owner_change(client: TestClient, dataset_id, headers, owner_id):
    return client.patch(
        f"/api/v1/datasets/{dataset_id}",
        json={"owner_id": str(owner_id)},
        headers=headers,
    )


@pytest.mark.req("FR-DATA-51")
def test_the_owner_can_hand_the_dataset_on(
    client: TestClient, analyst: dict[str, str], workspace_id
) -> None:
    successor = new_uuid7()
    created = client.post("/api/v1/datasets", json={"slug": _slug()}, headers=analyst)
    assert created.status_code == 201, created.text

    response = _owner_change(client, created.json()["id"], analyst, successor)
    assert response.status_code == 200, response.text
    assert response.json()["owner_id"] == str(successor)


@pytest.mark.req("FR-DATA-51")
def test_an_admin_can_reassign_a_dataset_they_do_not_own(
    client: TestClient, analyst: dict[str, str], workspace_id, grant
) -> None:
    """The second arm.

    Without this test the rule collapses to "the owner may", and an Admin unable to
    reassign a dataset whose owner has left is exactly the situation the Admin arm exists
    for. The admin here holds no `dataset:write` — `admin` is not a superset of `analyst`
    in `BUILTIN_ROLES` — so this also proves the two conditions are independent.
    """
    administrator, successor = new_uuid7(), new_uuid7()
    _run(grant("admin", principal_id=administrator))
    created = client.post("/api/v1/datasets", json={"slug": _slug()}, headers=analyst)
    assert created.status_code == 201, created.text

    response = _owner_change(
        client,
        created.json()["id"],
        _headers(administrator, workspace_id),
        successor,
    )
    assert response.status_code == 200, response.text
    assert response.json()["owner_id"] == str(successor)


@pytest.mark.req("FR-DATA-51")
def test_a_third_party_with_dataset_write_is_refused(
    client: TestClient, analyst: dict[str, str], workspace_id, grant
) -> None:
    """The load-bearing refusal.

    `dataset:write` is not enough — a writer who is neither Admin nor owner may edit the
    dictionary and may not reassign the dataset, and a route that checked only the
    permission would look correct in every other test in this file.
    """
    third_party = new_uuid7()
    _run(grant("analyst", principal_id=third_party))
    created = client.post("/api/v1/datasets", json={"slug": _slug()}, headers=analyst)
    assert created.status_code == 201, created.text

    # The same principal *can* edit the dictionary, which is what makes the refusal below
    # about ownership rather than about holding no permission at all.
    edited = client.put(
        f"/api/v1/datasets/{created.json()['slug']}/dictionary",
        json={"data_dictionary": {}},
        headers=_headers(third_party, workspace_id),
    )
    assert edited.status_code == 200, edited.text

    response = _owner_change(
        client, created.json()["id"], _headers(third_party, workspace_id), new_uuid7()
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-DATA-51")
def test_the_reassignment_is_audited_with_both_owners(
    client: TestClient, analyst: dict[str, str], database, workspace_id, principal
) -> None:
    """`06` R2 and FR-DATA-51's "audited as a metadata change".

    `before` must carry the outgoing owner: an audit event saying only who owns it now
    cannot answer who lost it, which is the question an ownership record exists for.
    """
    successor = new_uuid7()
    created = client.post("/api/v1/datasets", json={"slug": _slug()}, headers=analyst)
    assert created.status_code == 201, created.text
    assert _owner_change(client, created.json()["id"], analyst, successor).status_code == 200

    from sqlalchemy import select

    from app.db.models import AuditEventRow

    async def event():
        async with database.session() as session:
            return (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == "dataset.owner_changed",
                    )
                )
            ).scalar_one()

    entry = _run(event())
    assert entry.before["owner_id"] == str(principal.id)
    assert entry.after["owner_id"] == str(successor)
