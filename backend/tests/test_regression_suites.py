"""The Regression Suite store (03 §4.7, §5.1; FR-260, FR-368, NFR-499; PL-1189 Task 4).

Versioned, access-controlled and creation-audited. One suite per Rating Algorithm is the
database's rule: the two race tests hold both writers at a barrier past every read, so
only a constraint can refuse the second (audit finding F6, re-audit N3).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Environment, Settings
from app.db.models import AuditEventRow, RegressionSuiteRow
from app.db.session import Database
from app.errors import PlatformError
from app.main import create_app
from app.platform import regression_suites as service
from model_schema import Principal, RegressionSuiteContent, new_uuid7

#: A value that appears only inside a golden quote's context — never in any audit
#: payload or log line (NFR-499).
_SECRET_POSTCODE = "ZZ9 9ZZ"


def _content(algorithm_slug: str = "motor-gb", premium: int = 112_480) -> dict[str, Any]:
    return {
        "algorithm_slug": algorithm_slug,
        "golden_quotes": [
            {
                "name": "young-driver-london",
                "context": {
                    "purpose": "new_business",
                    "quoted_at": "2026-09-28T09:00:00Z",
                    "effective_date": "2026-10-01",
                    "inputs": {"driver_age": 19, "postcode": _SECRET_POSTCODE},
                },
                "expected": {"payable_premium_minor": premium, "outcome": "quoted"},
                "tolerance": {"money_minor": 0},
            }
        ],
        "properties": [{"name": "premium-positive", "check": {"kind": "premium_positive"}}],
        "generation": {"cases": 100, "seed": 7, "strategy": "input_contract_sampling"},
    }


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
def client(api_settings: Settings) -> TestClient:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


def _headers(principal_id: UUID, workspace_id: UUID) -> dict[str, str]:
    return {DEV_PRINCIPAL_HEADER: str(principal_id), "Workspace-Id": str(workspace_id)}


@pytest_asyncio.fixture
async def analyst(workspace_id: UUID, principal: Principal, grant) -> Principal:
    await grant("analyst")
    return principal


async def _create(
    database: Database, workspace_id: UUID, actor: Principal, slug: str, **content: Any
):
    async with database.unit_of_work() as session:
        _, row = await service.create_suite_version(
            session, workspace_id=workspace_id, actor=actor, slug=slug,
            content=RegressionSuiteContent.model_validate(_content(**content)),
            change_note="golden quotes",
        )
        return row.version


# --- access control -------------------------------------------------------------------


@pytest.mark.req("FR-260")
async def test_a_principal_without_rating_write_is_refused_creation(
    client: TestClient, workspace_id: UUID, grant
) -> None:
    reader = new_uuid7()
    await grant("approver", principal_id=reader)  # rating:read, no rating:write
    response = client.post(
        "/api/v1/regression-suites/motor-gb-core/versions",
        json=_content() | {"change_note": "x"},
        headers=_headers(reader, workspace_id),
    )
    assert response.status_code == 403, response.text


@pytest.mark.req("FR-260")
@pytest.mark.req("NFR-499")
async def test_a_principal_without_rating_read_is_refused_the_read(
    client: TestClient, workspace_id: UUID, analyst: Principal, membership
) -> None:
    created = client.post(
        "/api/v1/regression-suites/motor-gb-core/versions",
        json=_content() | {"change_note": "first"},
        headers=_headers(analyst.id, workspace_id),
    )
    assert created.status_code == 201, created.text
    assert created.json()["version"] == 1

    read = client.get(
        "/api/v1/regression-suites/motor-gb-core@1", headers=_headers(analyst.id, workspace_id)
    )
    assert read.status_code == 200, read.text
    assert read.json()["golden_quotes"][0]["context"]["inputs"]["postcode"] == _SECRET_POSTCODE
    assert read.json()["content_hash"] == created.json()["content_hash"]

    outsider = new_uuid7()
    await membership(principal_id=outsider)  # a member with no role at all
    refused = client.get(
        "/api/v1/regression-suites/motor-gb-core@1", headers=_headers(outsider, workspace_id)
    )
    assert refused.status_code == 403, refused.text
    assert _SECRET_POSTCODE not in refused.text


# --- the creation event ---------------------------------------------------------------


@pytest.mark.req("FR-368")
@pytest.mark.req("NFR-499")
async def test_every_version_has_one_creation_event_and_no_context_is_logged(
    client: TestClient, database: Database, workspace_id: UUID, analyst: Principal,
    caplog: pytest.LogCaptureFixture, capfd: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Both versions are created through the route, so the request middleware, the service
    and the audit write all run while logging is captured (audit finding G3: the earlier
    service-level form passed because nothing logged at all). A sentinel on the route's own
    logger must be captured first, and the route's request records after it, so the
    no-context assert cannot pass on an empty capture; the JSON handler's stdout is read
    through `capfd` as well. Proved non-vacuous by a positive
    control recorded in the slice ledger: a temporary log line carrying the content turns
    this test red.
    """
    # An in-process alembic run earlier in the session (`backend/migrations/env.py`'s
    # `fileConfig`, whose `disable_existing_loggers` defaults to true) disables every logger
    # that already exists, and a disabled logger drops its records before any handler sees
    # them — so in full-suite order this test captured nothing (#867's CI). Re-enable them
    # for this test only, then prove the capture works on the route's own logger before
    # asserting anything about what was logged.
    for candidate in list(logging.root.manager.loggerDict.values()):
        if isinstance(candidate, logging.Logger) and candidate.disabled:
            monkeypatch.setattr(candidate, "disabled", False)
    caplog.set_level(logging.DEBUG)
    sentinel = f"nfr-499-capture-sentinel-{new_uuid7()}"
    logging.getLogger("app.request").info(sentinel)
    assert sentinel in caplog.text, "the capture does not see app.request's records"
    for premium in (112_480, 112_900):
        response = client.post(
            "/api/v1/regression-suites/motor-gb-core/versions",
            json=_content(premium=premium) | {"change_note": "golden quotes"},
            headers=_headers(analyst.id, workspace_id),
        )
        assert response.status_code == 201, response.text
    captured = capfd.readouterr()

    async with database.session() as session:
        events = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == service.CREATED_ACTION,
                ).order_by(AuditEventRow.entity_ref)
            )
        ).scalars().all()
    assert [e.entity_ref for e in events] == [
        "regression_suite:motor-gb-core@1", "regression_suite:motor-gb-core@2",
    ]
    for event in events:
        assert UUID(str(event.actor["id"])) == analyst.id
        assert event.after is not None
        assert event.after["golden_quote_names"] == ["young-driver-london"]
        assert _SECRET_POSTCODE not in repr(event.before) + repr(event.after)
        assert "context" not in event.after
    route_records = [
        r for r in caplog.records if r.name == "app.request" and sentinel not in r.getMessage()
    ]
    assert route_records, "the route's own request records were not captured"
    assert _SECRET_POSTCODE not in caplog.text
    assert _SECRET_POSTCODE not in captured.out + captured.err


# --- one suite per algorithm, by the database -----------------------------------------


@pytest.mark.req("FR-260")
async def test_a_second_suite_for_an_algorithm_is_refused(
    database: Database, workspace_id: UUID, analyst: Principal
) -> None:
    await _create(database, workspace_id, analyst, "motor-gb-core")
    with pytest.raises(PlatformError) as refused:
        await _create(database, workspace_id, analyst, "motor-gb-other")
    assert refused.value.status_code == 409


@pytest.mark.req("FR-260")
async def test_a_suite_cannot_change_algorithm_across_versions(
    database: Database, workspace_id: UUID, analyst: Principal
) -> None:
    await _create(database, workspace_id, analyst, "motor-gb-core")
    with pytest.raises(PlatformError) as refused:
        await _create(database, workspace_id, analyst, "motor-gb-core", algorithm_slug="home-gb")
    assert refused.value.status_code == 409


async def _race(
    database: Database, workspace_id: UUID, actor: Principal, slugs: tuple[str, str]
) -> list[int | PlatformError]:
    results: list[int | PlatformError] = []

    async def one(slug: str) -> None:
        try:
            results.append(await _create(database, workspace_id, actor, slug))
        except PlatformError as exc:
            results.append(exc)

    await asyncio.gather(*(one(slug) for slug in slugs))
    return results


@pytest.mark.req("FR-260")
async def test_two_concurrent_suites_for_one_algorithm_give_one_201_and_one_409(
    database: Database, workspace_id: UUID, analyst: Principal,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Both writers pass the registry read before either inserts, so a check-then-insert
    would admit both; only `uq_regression_suites_algorithm` can refuse the second."""
    barrier = asyncio.Barrier(2)
    real_registry = service._registry

    async def registry_then_wait(*args: Any, **kwargs: Any):
        found = await real_registry(*args, **kwargs)
        await barrier.wait()
        return found

    monkeypatch.setattr(service, "_registry", registry_then_wait)
    results = await _race(database, workspace_id, analyst, ("motor-gb-a", "motor-gb-b"))

    assert sorted(type(r).__name__ for r in results) == ["PlatformError", "int"]
    refusal = next(r for r in results if isinstance(r, PlatformError))
    assert refusal.status_code == 409
    async with database.session() as session:
        rows = (
            await session.execute(
                select(RegressionSuiteRow).where(RegressionSuiteRow.workspace_id == workspace_id)
            )
        ).scalars().all()
    assert len(rows) == 1


@pytest.mark.req("FR-260")
async def test_two_concurrent_versions_of_one_suite_collide_as_409_not_500(
    database: Database, workspace_id: UUID, analyst: Principal,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await _create(database, workspace_id, analyst, "motor-gb-core")
    barrier = asyncio.Barrier(2)
    real_next = service._next_version

    async def next_then_wait(*args: Any, **kwargs: Any) -> int:
        number = await real_next(*args, **kwargs)
        await barrier.wait()
        return number

    monkeypatch.setattr(service, "_next_version", next_then_wait)
    results = await _race(database, workspace_id, analyst, ("motor-gb-core", "motor-gb-core"))

    assert sorted(type(r).__name__ for r in results) == ["PlatformError", "int"]
    assert 2 in results
    refusal = next(r for r in results if isinstance(r, PlatformError))
    assert refusal.status_code == 409


@pytest.mark.req("FR-260")
async def test_a_missing_version_reads_as_404(
    client: TestClient, workspace_id: UUID, analyst: Principal
) -> None:
    response = client.get(
        "/api/v1/regression-suites/never-made@1", headers=_headers(analyst.id, workspace_id)
    )
    assert response.status_code == 404, response.text



# --- a `monotone` bound is validated at declaration, never inside a Job (PL-1205, DP-S3-5) --


def _algorithm(input_field: dict[str, Any]) -> dict[str, Any]:
    return {
        "slug": "motor-gb", "version": 1,
        "input_contract": [{"name": "x", "nullable": False, **input_field}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": "x",
             "on_missing": "error", "produces": "x"},
            {"step_id": "s_expr", "type": "expression", "label": "Apply", "expr": "x * 2",
             "result_type": "money_minor", "consumes": ["x"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


@pytest.mark.req("FR-261")
@pytest.mark.parametrize(("field", "check"), [
    ({"type": "int"}, {"lower": "5"}),                                    # a lone bound, no range
    ({"type": "int", "min": 0, "max": 10}, {"lower": "20"}),              # outside the contract
    ({"type": "int", "min": 5, "max": 9}, {"lower": "3", "upper": "4"}),  # empty
    ({"type": "decimal", "min": "0.004", "max": "0.006"}, {}),            # no two-place value
    ({"type": "string"}, {}),                                             # not orderable
], ids=["lone-bound", "outside-contract", "empty", "no-two-place", "not-orderable"])
async def test_an_invalid_monotone_bound_is_a_422_at_declaration_and_no_job_exists(
    client: TestClient, database: Database, workspace_id: UUID, analyst: Principal,
    field: dict[str, Any], check: dict[str, Any],
) -> None:
    from app.db.models import JobRow
    from app.platform import rating_algorithms as algorithm_service

    await algorithm_service.create_algorithm(
        database, workspace_id, analyst.id, _algorithm(field)
    )
    body = _content(algorithm_slug="motor-gb") | {
        "change_note": "x",
        "properties": [{"name": "mono-x", "check": {
            "kind": "monotone", "input": "x", "direction": "increasing", **check}}],
    }
    response = client.post(
        "/api/v1/regression-suites/motor-gb-core/versions", json=body,
        headers=_headers(analyst.id, workspace_id),
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "REGRESSION_PROPERTY_INVALID"
    assert "mono-x" in response.json()["detail"]
    async with database.session() as session:
        jobs = select(JobRow).where(JobRow.workspace_id == workspace_id)
        assert not (await session.execute(jobs)).scalars().all()
        suites = select(RegressionSuiteRow).where(
            RegressionSuiteRow.workspace_id == workspace_id
        )
        assert not (await session.execute(suites)).scalars().all()


@pytest.mark.req("FR-261")
@pytest.mark.parametrize("check", [{"lower": "5"}, {"upper": "5"}], ids=["lone-lower", "lone-upper"])
async def test_a_lone_monotone_bound_is_accepted_when_the_contract_has_the_other_end(
    client: TestClient, database: Database, workspace_id: UUID, analyst: Principal,
    check: dict[str, Any],
) -> None:
    from app.platform import rating_algorithms as algorithm_service

    await algorithm_service.create_algorithm(
        database, workspace_id, analyst.id, _algorithm({"type": "int", "min": 0, "max": 10})
    )
    body = _content(algorithm_slug="motor-gb") | {
        "change_note": "x",
        "properties": [{"name": "mono-x", "check": {
            "kind": "monotone", "input": "x", "direction": "increasing", **check}}],
    }
    response = client.post(
        "/api/v1/regression-suites/motor-gb-core/versions", json=body,
        headers=_headers(analyst.id, workspace_id),
    )
    assert response.status_code == 201, response.text
