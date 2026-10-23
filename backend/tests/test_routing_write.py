"""The date-routing rule write, `PUT /api/v1/environments/{env}/routing`
(`03` §4.13, FR-270, FR-272; WK-674 Slice 6, `RL-1834` D1 items 1 to 4).

Every test starts from a fresh workspace and fresh Rating Version slugs. The Environments are
deployment-wide, so a test never changes one; the rule rows are scoped by the fresh workspace.
Selection at scoring time is `test_routing.py`'s; this file holds the write.
"""

# Fixtures are imported from the sibling modules that define them, as the other test files do,
# so a test parameter redefines the imported name (F811).
# ruff: noqa: F811

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_deployments import (  # noqa: F401
    Seat,
    api_settings,
    approved_version,
    client,
    deploy,
    seat,
)
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.db.models import AuditEventRow, RoutingRuleRow
from app.db.session import Database
from model_schema import new_uuid7

_ACTION = "deployment.routing_changed"


def _range(ref: str, start: str, end: str | None = None) -> dict[str, Any]:
    return {"rating_version_ref": ref, "effective_from": start, "effective_to": end}


def put_routing(client: TestClient, seat: Seat, env: str, ranges: list[dict[str, Any]]):
    return client.put(
        f"/api/v1/environments/{env}/routing", json={"ranges": ranges}, headers=seat.headers
    )


async def _rows(database: Database, workspace_id: UUID) -> list[RoutingRuleRow]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(RoutingRuleRow)
                    .where(RoutingRuleRow.workspace_id == workspace_id)
                    .order_by(RoutingRuleRow.written_at, RoutingRuleRow.id)
                )
            ).scalars()
        )


async def _events(database: Database, workspace_id: UUID) -> list[AuditEventRow]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(AuditEventRow)
                    .where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == _ACTION,
                    )
                    .order_by(AuditEventRow.id)
                )
            ).scalars()
        )


async def _deployed(client: TestClient, database, workspace_id, deployer: Seat, env="dev") -> str:
    ref = await approved_version(database, workspace_id, new_uuid7())
    assert deploy(client, deployer, env, ref).status_code == 201
    return ref


@pytest.mark.req("FR-270", "FR-272")
@pytest.mark.asyncio
async def test_a_rule_naming_a_deployed_version_is_written_and_audited(
    client: TestClient, database, workspace_id, seat
) -> None:
    """The positive control: 200 `RoutingRule`, each range pinned to the Deployment of its
    version, one row, and one `deployment.routing_changed` event whose `before` is null."""
    deployer = await seat("deployer")
    ref = await _deployed(client, database, workspace_id, deployer)
    put = put_routing(client, deployer, "dev", [_range(ref, "2026-01-01", "2026-07-01")])
    assert put.status_code == 200, put.text
    body = put.json()
    assert body["environment"] == "dev"
    assert body["written_by"] == str(deployer.id)
    (stored,) = body["ranges"]
    assert stored["rating_version_ref"] == ref
    assert stored["effective_from"] == "2026-01-01"
    assert stored["effective_to"] == "2026-07-01"
    rows = await _rows(database, workspace_id)
    assert len(rows) == 1
    assert rows[0].ranges[0]["deployment_id"] == stored["deployment_id"]
    (event,) = await _events(database, workspace_id)
    assert event.entity_ref == "environment:dev"
    assert event.before is None
    assert event.after["ranges"][0]["deployment_id"] == stored["deployment_id"]


@pytest.mark.req("FR-270", "FR-272")
@pytest.mark.asyncio
async def test_a_second_write_appends_and_records_the_previous_rule_as_before(
    client: TestClient, database, workspace_id, seat
) -> None:
    deployer = await seat("deployer")
    ref = await _deployed(client, database, workspace_id, deployer)
    first = put_routing(client, deployer, "dev", [_range(ref, "2026-01-01", "2026-07-01")])
    second = put_routing(client, deployer, "dev", [_range(ref, "2026-07-01")])
    assert first.status_code == second.status_code == 200
    assert len(await _rows(database, workspace_id)) == 2
    _, latest = await _events(database, workspace_id)
    assert latest.before["ranges"] == first.json()["ranges"]
    assert latest.after["ranges"][0]["effective_to"] is None


@pytest.mark.req("FR-270")
@pytest.mark.asyncio
async def test_an_empty_range_list_clears_the_rule(
    client: TestClient, database, workspace_id, seat
) -> None:
    deployer = await seat("deployer")
    ref = await _deployed(client, database, workspace_id, deployer)
    assert put_routing(client, deployer, "dev", [_range(ref, "2026-01-01")]).status_code == 200
    cleared = put_routing(client, deployer, "dev", [])
    assert cleared.status_code == 200
    assert cleared.json()["ranges"] == []
    assert (await _rows(database, workspace_id))[-1].ranges == []


@pytest.mark.req("FR-270")
@pytest.mark.asyncio
async def test_adjacent_half_open_ranges_do_not_overlap(
    client: TestClient, database, workspace_id, seat
) -> None:
    """`[a, b)` then `[b, c)` share no date, so the rule is accepted."""
    deployer = await seat("deployer")
    ref = await _deployed(client, database, workspace_id, deployer)
    put = put_routing(
        client,
        deployer,
        "dev",
        [_range(ref, "2026-01-01", "2026-07-01"), _range(ref, "2026-07-01", "2027-01-01")],
    )
    assert put.status_code == 200, put.text


@pytest.mark.req("FR-270")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "second",
    [("2026-06-30", "2026-12-31"), ("2026-03-01", "2026-04-01"), ("2026-06-01", None)],
    ids=["straddles-the-end", "inside", "open-ended"],
)
async def test_overlapping_ranges_are_refused_and_nothing_is_written(
    client: TestClient, database, workspace_id, seat, second: tuple[str, str | None]
) -> None:
    """Violation: overlapping ranges are stored. Red against a route without the overlap check."""
    deployer = await seat("deployer")
    ref = await _deployed(client, database, workspace_id, deployer)
    refused = put_routing(
        client,
        deployer,
        "dev",
        [_range(ref, "2026-01-01", "2026-07-01"), _range(ref, second[0], second[1])],
    )
    assert refused.status_code == 409
    assert refused.json()["code"] == "DEPLOY_DATE_RANGE_OVERLAP"
    assert await _rows(database, workspace_id) == []
    assert await _events(database, workspace_id) == []


@pytest.mark.req("FR-270")
@pytest.mark.asyncio
async def test_a_version_not_deployed_to_this_environment_is_refused(
    client: TestClient, database, workspace_id, seat
) -> None:
    """The write half of `RL-1834` D1 (b): a version deployed to `uat` only cannot be routed
    in `dev`. 409 `VALIDATION_FAILED`, no row, no event."""
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, new_uuid7())
    assert deploy(client, deployer, "dev", ref).status_code == 201
    assert deploy(client, deployer, "uat", ref).status_code == 201
    other = await approved_version(database, workspace_id, new_uuid7())
    refused = put_routing(client, deployer, "dev", [_range(other, "2026-01-01")])
    assert refused.status_code == 409
    assert refused.json()["code"] == "VALIDATION_FAILED"
    assert other in refused.json()["detail"]
    assert await _rows(database, workspace_id) == []
    assert await _events(database, workspace_id) == []


@pytest.mark.req("FR-270")
@pytest.mark.asyncio
@pytest.mark.parametrize("end", ["2026-01-01", "2025-12-31"], ids=["equal", "before"])
async def test_a_range_must_end_after_it_starts(
    client: TestClient, database, workspace_id, seat, end: str
) -> None:
    deployer = await seat("deployer")
    ref = await _deployed(client, database, workspace_id, deployer)
    refused = put_routing(client, deployer, "dev", [_range(ref, "2026-01-01", end)])
    assert refused.status_code == 422
    assert refused.json()["code"] == "VALIDATION_FAILED"
    assert await _rows(database, workspace_id) == []


@pytest.mark.req("FR-270")
@pytest.mark.asyncio
async def test_a_reference_that_is_not_a_rating_version_is_refused(
    client: TestClient, database, workspace_id, seat
) -> None:
    deployer = await seat("deployer")
    bad = _range("model:motor-ad-frequency@7", "2026-01-01")
    refused = put_routing(client, deployer, "dev", [bad])
    assert refused.status_code == 422
    assert refused.json()["code"] == "VALIDATION_FAILED"
    assert await _rows(database, workspace_id) == []


@pytest.mark.req("FR-270", "FR-345")
@pytest.mark.asyncio
async def test_a_principal_without_deployment_promote_is_refused(
    client: TestClient, database, workspace_id, seat
) -> None:
    deployer = await seat("deployer")
    ref = await _deployed(client, database, workspace_id, deployer)
    outsider = await seat()
    refused = put_routing(client, outsider, "dev", [_range(ref, "2026-01-01")])
    assert refused.status_code == 403
    assert await _rows(database, workspace_id) == []
    assert await _events(database, workspace_id) == []


@pytest.mark.req("FR-270")
@pytest.mark.asyncio
async def test_an_unknown_environment_is_404(client: TestClient, workspace_id, seat) -> None:
    deployer = await seat("deployer")
    assert put_routing(client, deployer, "no-such-env", []).status_code == 404


@pytest.mark.req("FR-272", "NFR-498")
@pytest.mark.asyncio
async def test_a_routing_change_cannot_commit_without_its_audit_event(
    client: TestClient, database, workspace_id, seat, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Violation: a routing change commits without its Audit Event. Deliberately broken input:
    the audit write raises, and the rule row must roll back with it (same transaction)."""
    from app.platform import routing

    deployer = await seat("deployer")
    ref = await _deployed(client, database, workspace_id, deployer)

    async def broken(*_a: object, **_k: object) -> None:
        raise RuntimeError("audit store down")

    monkeypatch.setattr(routing.audit, "record", broken)
    failed = put_routing(client, deployer, "dev", [_range(ref, "2026-01-01")])
    assert failed.status_code == 500
    async with database.session() as session:
        count = (
            await session.execute(
                select(func.count())
                .select_from(RoutingRuleRow)
                .where(RoutingRuleRow.workspace_id == workspace_id)
            )
        ).scalar_one()
    assert count == 0
