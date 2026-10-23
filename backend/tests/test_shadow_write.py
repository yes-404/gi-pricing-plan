"""The shadow configuration write, `PUT /api/v1/environments/{env}/shadow`
(`03` §4.13, FR-271, FR-272; WK-674 Slice 6, `RL-1834` D2 items 2 and 3).

Every test starts from a fresh workspace and fresh Rating Version slugs; Environments are
deployment-wide, so none is changed.
"""

# Fixtures are imported from the sibling modules that define them, as the other test files do,
# so a test parameter redefines the imported name (F811).
# ruff: noqa: F811

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import pytest
from backend.tests.test_deployments import (  # noqa: F401
    Seat,
    api_settings,
    approved_version,
    client,
    seat,
)
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import AuditEventRow, RatingVersionRow, ShadowConfigRow
from app.db.session import Database
from model_schema import new_uuid7

_ACTION = "deployment.shadow_configured"
_HASH = "sha256:" + "a" * 64


def put_shadow(client: TestClient, seat: Seat, env: str, ref: str, fraction: float = 0.25):
    return client.put(
        f"/api/v1/environments/{env}/shadow",
        json={"candidate_rating_version_ref": ref, "fraction": fraction},
        headers=seat.headers,
    )


async def _rows(database: Database, workspace_id: UUID) -> list[ShadowConfigRow]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(ShadowConfigRow)
                    .where(ShadowConfigRow.workspace_id == workspace_id)
                    .order_by(ShadowConfigRow.written_at, ShadowConfigRow.id)
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


async def _draft_version(database: Database, workspace_id: UUID) -> str:
    slug = f"draft-{uuid4().hex[:8]}"
    async with database.unit_of_work() as session:
        session.add(
            RatingVersionRow(
                workspace_id=workspace_id,
                slug=slug,
                version=1,
                status="draft",
                dataset_version_id=uuid4(),
                model_ref="model:motor-ad-frequency@7",
                created_by=new_uuid7(),
                bundle={"content_hash": _HASH},
            )
        )
    return f"rating_version:{slug}@1"


@pytest.mark.req("FR-271", "FR-272")
@pytest.mark.asyncio
async def test_a_compiled_candidate_is_configured_and_audited(
    client: TestClient, database, workspace_id, seat
) -> None:
    """The positive control. The candidate is approved but deployed nowhere (FR-271 is the
    pre-deployment net): 200 `ShadowConfig`, the bundle hash recorded, one row, one event."""
    admin = await seat("admin")
    ref = await approved_version(database, workspace_id, new_uuid7())
    put = put_shadow(client, admin, "prod", ref, 0.25)
    assert put.status_code == 200, put.text
    body = put.json()
    assert body["environment"] == "prod"
    assert body["candidate_rating_version_ref"] == ref
    assert body["candidate_bundle_hash"] == _HASH
    assert body["fraction"] == 0.25
    assert body["written_by"] == str(admin.id)
    (row,) = await _rows(database, workspace_id)
    assert row.candidate_bundle_hash == _HASH
    (event,) = await _events(database, workspace_id)
    assert event.entity_ref == "environment:prod"
    assert event.before is None
    assert event.after["candidate_rating_version_ref"] == ref


@pytest.mark.req("FR-271", "FR-272")
@pytest.mark.asyncio
async def test_a_second_write_appends_and_records_the_first_as_before(
    client: TestClient, database, workspace_id, seat
) -> None:
    admin = await seat("admin")
    ref = await approved_version(database, workspace_id, new_uuid7())
    assert put_shadow(client, admin, "prod", ref, 0.1).status_code == 200
    assert put_shadow(client, admin, "prod", ref, 1.0).status_code == 200
    assert len(await _rows(database, workspace_id)) == 2
    _, latest = await _events(database, workspace_id)
    assert latest.before["fraction"] == 0.1
    assert latest.after["fraction"] == 1.0


@pytest.mark.req("FR-271")
@pytest.mark.asyncio
async def test_a_draft_candidate_is_refused(
    client: TestClient, database, workspace_id, seat
) -> None:
    """A `draft` bundle can still be recompiled, so its results would attach to no fixed
    bundle (`RL-1834` D2 item 3)."""
    admin = await seat("admin")
    ref = await _draft_version(database, workspace_id)
    refused = put_shadow(client, admin, "prod", ref)
    assert refused.status_code == 422
    assert refused.json()["code"] == "VALIDATION_FAILED"
    assert await _rows(database, workspace_id) == []
    assert await _events(database, workspace_id) == []


@pytest.mark.req("FR-271")
@pytest.mark.asyncio
async def test_an_uncompiled_candidate_is_refused(
    client: TestClient, database, workspace_id, seat
) -> None:
    admin = await seat("admin")
    ref = await approved_version(database, workspace_id, new_uuid7(), compiled=False)
    refused = put_shadow(client, admin, "prod", ref)
    assert refused.status_code == 409
    assert refused.json()["code"] == "BUNDLE_COMPILE_FAILED"
    assert await _rows(database, workspace_id) == []


@pytest.mark.req("FR-271")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ref",
    ["rating_version:no-such-version@1", "model:motor-ad-frequency@7"],
    ids=["unknown", "type"],
)
async def test_a_candidate_that_is_not_a_rating_version_of_this_workspace_is_refused(
    client: TestClient, workspace_id, database, seat, ref: str
) -> None:
    admin = await seat("admin")
    refused = put_shadow(client, admin, "prod", ref)
    assert refused.status_code == 422
    assert refused.json()["code"] == "VALIDATION_FAILED"
    assert await _rows(database, workspace_id) == []


@pytest.mark.req("FR-271")
@pytest.mark.asyncio
@pytest.mark.parametrize("fraction", [0, -0.1, 1.5])
async def test_a_fraction_outside_the_unit_interval_is_refused(
    client: TestClient, database, workspace_id, seat, fraction: float
) -> None:
    admin = await seat("admin")
    ref = await approved_version(database, workspace_id, new_uuid7())
    refused = put_shadow(client, admin, "prod", ref, fraction)
    assert refused.status_code == 422
    assert await _rows(database, workspace_id) == []


@pytest.mark.req("FR-271", "FR-449")
@pytest.mark.asyncio
async def test_a_deployer_without_admin_manage_settings_is_refused(
    client: TestClient, database, workspace_id, seat
) -> None:
    """`deployment:promote` does not configure shadow scoring: it is `admin:manage_settings`."""
    deployer = await seat("deployer")
    ref = await approved_version(database, workspace_id, new_uuid7())
    refused = put_shadow(client, deployer, "prod", ref)
    assert refused.status_code == 403
    assert await _rows(database, workspace_id) == []
    assert await _events(database, workspace_id) == []


@pytest.mark.req("FR-271")
@pytest.mark.asyncio
async def test_an_unknown_environment_is_404(client: TestClient, seat) -> None:
    admin = await seat("admin")
    assert (
        put_shadow(client, admin, "no-such-env", "rating_version:no-such-version@1").status_code
        == 404
    )


@pytest.mark.req("FR-272", "NFR-498")
@pytest.mark.asyncio
async def test_a_shadow_change_cannot_commit_without_its_audit_event(
    client: TestClient, database, workspace_id, seat, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Violation: a shadow change commits without its Audit Event. Deliberately broken input:
    the audit write raises and the configuration row rolls back with it."""
    from app.platform import audit

    admin = await seat("admin")
    ref = await approved_version(database, workspace_id, new_uuid7())

    async def broken(*_a: Any, **_k: Any) -> None:
        raise RuntimeError("audit store down")

    monkeypatch.setattr(audit, "record", broken)
    assert put_shadow(client, admin, "prod", ref).status_code == 500
    assert await _rows(database, workspace_id) == []
