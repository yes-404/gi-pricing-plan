"""WK-2113 S3, conditions (1) and (2): a STORED bundle that prices on a `control` operand is
re-validated at every entry that reads it, and refused (FR-88, FR-240; aud-intent2 cell B1).

DB-backed: needs the database and the blob store, so it runs only in a window the lead grants.
**WRITTEN, NOT RUN** (the preparing seat had no DB). Each entry point is one test, named for the
function in aud-intent2's path table:

* approval chain   : `platform/deployments.py::submit_request` (`POST .../deployment-requests`)
* deploy           : `platform/deployments.py::deploy`        (`POST .../deployments`)
* rollback         : `platform/deployments.py::rollback`      (`POST .../deployments/rollback`)
* switch PREPARE   : `api/score.py::hydrate_for_switch`

Each asserts the RFC 9457 problem with the named code and the version, hash and operand in its
detail, never a 500, no Deployment row written, and **exactly one** audit event for the refused
load naming version, hash and operand (ruling "2026-11-13 19:58:03 GMT", condition (2)).

The refusal status, the audit action and its `after` keys are named constants below (rulings
2026-11-13 21:17:39 and 21:23:21: 409, `rating_version.load_refused`, re-validation at submit,
deploy, rollback and switch PREPARE, the decision itself not reading the bundle).

The offending bundle is `fixtures/stored_bundles/offender.bundle.json`: a real compiled bundle
whose GLM carries the risk interaction `region_x_yoa` over the `control` Factor `yoa`, built by
turning S1's compile guard off for the construction only (see the README, `gen/make_fixtures.py`).
Its `content_hash` equals the clean fixture's: the hash covers the pins, not the carried Factor
payloads, so **a hash cannot tell a re-validated bundle from an unchecked one**.
"""

from __future__ import annotations

import pathlib
from typing import Any
from uuid import UUID, uuid4

import pytest
from backend.tests import test_deployments as _deployments
from backend.tests.approved_rows import add_approved
from fastapi.testclient import TestClient
from sqlalchemy import select, update

from app.db.models import AuditEventRow, DeploymentRow, RatingVersionRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform.bundle_slot import BundleSlot
from app.platform.deployment_switch import SwitchMessage
from model_schema import new_uuid7

api_settings = _deployments.api_settings
client = _deployments.client
seat = _deployments.seat
deploy = _deployments.deploy
request_into = _deployments.request_into

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "stored_bundles"

CODE = "CONTROL_FACTOR_IN_RATEABLE_PATH"
#: DP-2 (ruling 2026-11-13 21:17:39): the stored artifact conflicts with the current rules, 409.
REFUSAL_STATUS = 409
#: The audit action for a refused load (`03` §4.3); its `after` keys are `bundle_hash`, `refusal`.
REFUSAL_ACTION = "rating_version.load_refused"
OPERAND = "yoa"
INTERACTION = "region_x_yoa"


async def stored_version(
    database: Database,
    blob_store: Any,
    workspace_id: UUID,
    fixture: str,
    *,
    author: UUID | None = None,
) -> tuple[str, str]:
    """An `approved` Rating Version whose bundle is the fixture's bytes in the blob store.

    Returns (`rating_version:<slug>@1`, `content_hash`). `row.bundle` carries exactly the two
    keys `_fetch_bundle` reads: `content_hash` and `blob_sha256`.
    """
    import json

    payload = (FIXTURES / fixture).read_bytes()
    content_hash = json.loads(payload)["content_hash"]
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, payload, "application/json")
        slug = f"rv-{uuid4().hex[:8]}"
        await add_approved(
            session,
            RatingVersionRow(
                workspace_id=workspace_id,
                slug=slug,
                version=1,
                status="approved",
                dataset_version_id=uuid4(),
                model_ref="model:motor-ad-frequency@7",
                created_by=author or new_uuid7(),
                bundle={"content_hash": content_hash, "blob_sha256": ref.sha256},
            ),
        )
    return f"rating_version:{slug}@1", content_hash


async def refusal_events(database: Database, workspace_id: UUID) -> list[AuditEventRow]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == REFUSAL_ACTION,
                    )
                )
            )
            .scalars()
            .all()
        )


def assert_problem(response: Any, ref: str, content_hash: str) -> None:
    """An RFC 9457 problem with the named code, never a 500, naming version, hash, operand."""
    assert response.status_code != 500, response.text
    assert response.status_code == REFUSAL_STATUS, response.text
    body = response.json()
    assert body["code"] == CODE
    assert ref in body["detail"]
    assert OPERAND in body["detail"]
    assert content_hash.removeprefix("sha256:") in body["detail"]


async def assert_one_event(
    database: Database, workspace_id: UUID, ref: str, content_hash: str
) -> None:
    events = await refusal_events(database, workspace_id)
    assert len(events) == 1, [e.action for e in events]
    event = events[0]
    assert event.entity_ref == ref
    after = event.after or {}
    assert after.get("bundle_hash") == content_hash
    assert OPERAND in str(after.get("refusal"))


async def deployments_written(database: Database, workspace_id: UUID) -> int:
    async with database.session() as session:
        return len(
            (
                await session.execute(
                    select(DeploymentRow.id).where(DeploymentRow.workspace_id == workspace_id)
                )
            ).all()
        )


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.asyncio
async def test_a_deployment_request_for_a_stored_control_operand_bundle_is_refused(
    client: TestClient, database: Database, blob_store: Any, workspace_id: UUID, seat: Any
) -> None:
    """Approval chain: `submit_request` reads the stored bundle through
    `_approved_compiled_version`.

    Ruling 21:23:21 (4): the check sits at submission, not at the decision; `deploy` re-validates
    again, which also covers a rules upgrade between the two.
    """
    deployer = await seat("deployer")
    ref, content_hash = await stored_version(
        database, blob_store, workspace_id, "offender.bundle.json"
    )
    refused = request_into(client, deployer, "prod", ref)
    assert_problem(refused, ref, content_hash)
    await assert_one_event(database, workspace_id, ref, content_hash)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.asyncio
async def test_a_deploy_of_a_stored_control_operand_bundle_is_refused_and_writes_nothing(
    client: TestClient, database: Database, blob_store: Any, workspace_id: UUID, seat: Any
) -> None:
    deployer = await seat("deployer")
    ref, content_hash = await stored_version(
        database, blob_store, workspace_id, "offender.bundle.json"
    )
    refused = deploy(client, deployer, "dev", ref)
    assert_problem(refused, ref, content_hash)
    assert await deployments_written(database, workspace_id) == 0
    await assert_one_event(database, workspace_id, ref, content_hash)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.asyncio
async def test_a_rollback_to_a_stored_control_operand_bundle_is_refused(
    client: TestClient, database: Database, blob_store: Any, workspace_id: UUID, seat: Any
) -> None:
    """Rollback reuses an earlier Deployment's `bundle_hash` and never recompiles (aud-intent2 B1).

    The earlier version is deployed while its stored bundle is clean, then its bundle is replaced
    in the row by the offending one: the state of a version approved and deployed before the fix
    (a fixture UPDATE; a real version cannot recompile, `RATING_VERSION_IMMUTABLE`).
    """
    deployer = await seat("deployer")
    first, _ = await stored_version(database, blob_store, workspace_id, "clean.bundle.json")
    second, _ = await stored_version(database, blob_store, workspace_id, "clean.bundle.json")
    assert deploy(client, deployer, "dev", first).status_code == 201
    assert deploy(client, deployer, "dev", second).status_code == 201
    offender_ref, content_hash = await stored_version(
        database, blob_store, workspace_id, "offender.bundle.json"
    )
    async with database.unit_of_work() as session:
        stored = (
            await session.execute(
                select(RatingVersionRow.bundle).where(
                    RatingVersionRow.workspace_id == workspace_id,
                    RatingVersionRow.slug == offender_ref.split(":")[1].split("@")[0],
                )
            )
        ).scalar_one()
        await session.execute(
            update(RatingVersionRow)
            .where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == first.split(":")[1].split("@")[0],
            )
            .values(bundle=stored)
        )
    before = await deployments_written(database, workspace_id)
    back = client.post(
        "/api/v1/environments/dev/deployments/rollback",
        json={"rating_version_ref": first, "reason": "regression"},
        headers=deployer.headers,
    )
    assert_problem(back, first, content_hash)
    assert await deployments_written(database, workspace_id) == before
    await assert_one_event(database, workspace_id, first, content_hash)


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("FR-268")
@pytest.mark.asyncio
async def test_switch_prepare_refuses_a_stored_control_operand_bundle_and_audits_once(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    """PREPARE hydrates the bundle a Deployment names; a refusal means the process does not
    acknowledge (`DEPLOY_SWITCH_INCOMPLETE` upstream), so no Deployment is written."""
    from app.api.score import hydrate_for_switch

    ref, content_hash = await stored_version(
        database, blob_store, workspace_id, "offender.bundle.json"
    )
    message = SwitchMessage(
        switch_id=str(new_uuid7()),
        phase="prepare",
        workspace_id=workspace_id,
        environment="dev",
        deployment_id=new_uuid7(),
        rating_version_ref=ref,
        bundle_hash=content_hash,
    )
    with pytest.raises(PlatformError) as refused:
        await hydrate_for_switch(database, blob_store, BundleSlot(), message)
    assert refused.value.code == CODE
    assert ref in str(refused.value.detail)
    assert OPERAND in str(refused.value.detail)
    await assert_one_event(database, workspace_id, ref, content_hash)
