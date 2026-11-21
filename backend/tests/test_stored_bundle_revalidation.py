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
from model_schema import ArtifactRef, new_uuid7

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
    return await stored_version_bytes(
        database, blob_store, workspace_id, (FIXTURES / fixture).read_bytes(), author=author
    )


async def stored_version_bytes(
    database: Database,
    blob_store: Any,
    workspace_id: UUID,
    payload: bytes,
    *,
    author: UUID | None = None,
    algorithm_ref: str | None = None,
    pins: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """`stored_version` for a bundle's bytes built in the test (#1943). `algorithm_ref` and
    `pins` are the row's, for a test that needs `revalidate` to read them."""
    import json

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
                algorithm_ref=algorithm_ref,
                pins=pins,
                created_by=author or new_uuid7(),
                bundle={
                    "content_hash": content_hash,
                    "bytes": len(payload),
                    "compiled_at": "2026-11-13T00:00:00+00:00",
                    "blob_sha256": ref.sha256,
                },
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


@pytest.mark.req("FR-88")
@pytest.mark.req("FR-240")
@pytest.mark.req("NFR-498")
@pytest.mark.asyncio
async def test_a_governance_refusal_is_audited_every_time_as_the_acting_principal(
    client: TestClient, database: Database, blob_store: Any, workspace_id: UUID, seat: Any
) -> None:
    """Amendment 3 (b), in ONE worker (one slot): a refused deploy, then a refused score of the same
    hash, write TWO events; a second refused deploy writes a THIRD; a repeated score writes none.
    The DP-1 memo de-duplicates scoring-path load refusals only; a deploy is a governance act by a
    named principal and is never de-duplicated."""
    from app.api.score import _compiled_for
    from model_schema import ActorKind, Principal

    deployer = await seat("deployer")
    ref_str, content_hash = await stored_version(
        database, blob_store, workspace_id, "offender.bundle.json"
    )
    ref = ArtifactRef.parse(ref_str)
    slot = client.app.state.bundle_slot  # type: ignore[attr-defined]
    requester = Principal(kind=ActorKind.USER, id=new_uuid7(), display="scorer")

    async def score() -> None:
        with pytest.raises(PlatformError):
            await _compiled_for(
                database,
                blob_store,
                slot,
                database=database,
                workspace_id=workspace_id,
                ref=ref,
                requester=requester,
            )

    assert_problem(deploy(client, deployer, "dev", ref_str), ref_str, content_hash)
    assert len(await refusal_events(database, workspace_id)) == 1
    await score()
    assert len(await refusal_events(database, workspace_id)) == 2
    assert_problem(deploy(client, deployer, "dev", ref_str), ref_str, content_hash)
    assert len(await refusal_events(database, workspace_id)) == 3
    await score()
    events = await refusal_events(database, workspace_id)
    assert len(events) == 3, "a repeated score writes no further event"
    by_actor = sorted(str(e.actor.get("id")) for e in events)
    assert by_actor.count(str(deployer.id)) == 2  # both deploys, the acting principal
    scored = [e for e in events if e.actor.get("kind") == "system"]
    assert len(scored) == 1
    assert (scored[0].after or {}).get("requested_by") == str(requester.id)


def _offset_source_absent_bytes() -> bytes:
    """The clean bundle, its GLM's model offset naming a source the bundle does not carry."""
    import json

    raw = json.loads((FIXTURES / "clean.bundle.json").read_text())
    spec = raw["resolved_payloads"]["model:motor-freq-glm@1"]["spec"]
    spec["offset"] = {"kind": "model", "offset_model_ref": "model:motor-source@1"}
    return json.dumps(raw).encode()


def _assert_unpinned_problem(response: Any, ref: str, content_hash: str) -> None:
    assert response.status_code == REFUSAL_STATUS, response.text
    body = response.json()
    assert body["code"] == "RATING_VERSION_UNPINNED"
    assert ref in body["detail"]
    assert "model:motor-source@1" in body["detail"]
    assert content_hash.removeprefix("sha256:") in body["detail"]


@pytest.mark.req("FR-116")
@pytest.mark.req("FR-240")
@pytest.mark.asyncio
@pytest.mark.parametrize("act", ["submit", "deploy", "rollback"])
async def test_submit_deploy_and_rollback_refuse_a_bundle_missing_its_offset_source_by_name(
    act: str,
    client: TestClient,
    database: Database,
    blob_store: Any,
    workspace_id: UUID,
    seat: Any,
) -> None:
    """#1943 D3: a stored Bundle whose model offset names a source it does not carry is refused
    at submit, deploy and rollback with `RATING_VERSION_UNPINNED` (409, audited once, no
    Deployment written); it was an unnamed 500. Rollback reuses an earlier Deployment, so its
    version is deployed while clean and its stored bundle is then swapped, as in
    `test_a_rollback_to_a_stored_control_operand_bundle_is_refused`."""
    deployer = await seat("deployer")
    ref, content_hash = await stored_version_bytes(
        database, blob_store, workspace_id, _offset_source_absent_bytes()
    )
    written = 0
    if act == "rollback":
        first, _ = await stored_version(database, blob_store, workspace_id, "clean.bundle.json")
        second, _ = await stored_version(database, blob_store, workspace_id, "clean.bundle.json")
        assert deploy(client, deployer, "dev", first).status_code == 201
        assert deploy(client, deployer, "dev", second).status_code == 201
        written = await deployments_written(database, workspace_id)
        async with database.unit_of_work() as session:
            stored = (
                await session.execute(
                    select(RatingVersionRow.bundle).where(
                        RatingVersionRow.workspace_id == workspace_id,
                        RatingVersionRow.slug == ref.split(":")[1].split("@")[0],
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
        ref = first
    if act == "submit":
        refused = request_into(client, deployer, "prod", ref)
    elif act == "deploy":
        refused = deploy(client, deployer, "dev", ref)
    else:
        refused = client.post(
            "/api/v1/environments/dev/deployments/rollback",
            json={"rating_version_ref": ref, "reason": "regression"},
            headers=deployer.headers,
        )
    _assert_unpinned_problem(refused, ref, content_hash)
    assert await deployments_written(database, workspace_id) == written
    events = await refusal_events(database, workspace_id)
    assert [e.entity_ref for e in events] == [ref]


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-237")
@pytest.mark.req("FR-240")
@pytest.mark.asyncio
async def test_deploy_refuses_a_version_mounting_a_sub_graph_its_pins_do_not_carry_by_name(
    client: TestClient, database: Database, blob_store: Any, workspace_id: UUID, seat: Any
) -> None:
    """#1943: `revalidate`'s second half (`check_rateable_intent`) refuses a version, with pins,
    whose algorithm mounts a sub-graph those pins do not carry at that version
    (`RATING_VERSION_UNPINNED`). It answered 500 (the code was not a load-guard code); it is now a
    409 with one `rating_version.load_refused` event and no Deployment. The stored Bundle is the
    clean fixture, so the first half passes and the refusal is the second half's."""
    from backend.tests.test_rating_version_compile import (
        _empty_pins,
        _mounting_algorithm,
        _ncd_sub_graph,
    )

    deployer = await seat("deployer", "analyst")
    made = client.post("/api/v1/sub-graphs", json=_ncd_sub_graph(), headers=deployer.headers)
    assert made.status_code == 201, made.text
    algorithm = client.post(
        "/api/v1/rating-algorithms", json=_mounting_algorithm(), headers=deployer.headers
    )
    assert algorithm.status_code == 201, algorithm.text
    ref, content_hash = await stored_version_bytes(
        database,
        blob_store,
        workspace_id,
        (FIXTURES / "clean.bundle.json").read_bytes(),
        algorithm_ref="rating_algorithm:mounting@1",
        pins=_empty_pins(),
    )
    refused = deploy(client, deployer, "dev", ref)
    assert refused.status_code == REFUSAL_STATUS, refused.text
    body = refused.json()
    assert body["code"] == "RATING_VERSION_UNPINNED"
    assert ref in body["detail"]
    assert "sub_graph:ncd-ladder@1" in body["detail"]
    assert content_hash.removeprefix("sha256:") in body["detail"]
    assert await deployments_written(database, workspace_id) == 0
    events = await refusal_events(database, workspace_id)
    assert [e.entity_ref for e in events] == [ref]


async def _pin_a_model_whose_source_has_an_offset(
    client: TestClient,
    database: Database,
    blob_store: Any,
    workspace_id: UUID,
    deployer: Any,
    slug: str,
) -> None:
    """Give the stored version `slug` an algorithm and a pin for a model C that is offset from B,
    which is offset from A. The fit refuses C (#1943 D4), so C is the hand-written row of
    `test_rating_version_compile.py`: written past the fit. The Bundle the version stores is
    untouched (the clean fixture), so it loads and prices: the pinned model is never called."""
    from backend.tests.approved_rows import mark_approved
    from backend.tests.test_model_offset_jobs import _residual_spec
    from backend.tests.test_prediction import _fitted_residual_pair
    from backend.tests.test_rating_version_compile import _empty_pins, _minimal_algorithm

    from app.db.models import ModelRow
    from app.platform import modelling as model_service

    made = client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=deployer.headers
    )
    assert made.status_code == 201, made.text
    pair = await _fitted_residual_pair(database, blob_store, workspace_id)
    async with database.unit_of_work() as session:
        b_row = await session.get(ModelRow, pair.residual_id)
        assert b_row is not None
        b_ref = f"model:{b_row.model_family_slug}@{b_row.version}"
        c_row, _ = await model_service.reserve_model(
            session,
            workspace_id=workspace_id,
            actor=pair.actor,
            spec=_residual_spec(pair.v2_id, pair.resid_flag_id, pair.split2, ref=b_ref),
        )
        c_row.fit_result = b_row.fit_result
        c_row.diagnostics_id = b_row.diagnostics_id
        c_row.status = "fitted"
        await session.flush()
        await mark_approved(session, c_row)
        c_ref = f"model:{c_row.model_family_slug}@{c_row.version}"
        pins = {**_empty_pins(), "models": [c_ref]}
        await session.execute(
            update(RatingVersionRow)
            .where(RatingVersionRow.workspace_id == workspace_id, RatingVersionRow.slug == slug)
            .values(algorithm_ref="rating_algorithm:minimal@1", pins=pins)
        )


@pytest.mark.req("FR-116")
@pytest.mark.req("FR-243")
@pytest.mark.asyncio
@pytest.mark.parametrize("act", ["submit", "deploy", "rollback"])
async def test_a_version_pinning_a_two_level_offset_model_is_refused_with_one_event(
    act: str,
    client: TestClient,
    database: Database,
    blob_store: Any,
    workspace_id: UUID,
    seat: Any,
) -> None:
    """#1943 point 1: a stored version that pins, and never calls, a model whose offset source has
    an offset of its own still prices (its Bundle is the clean fixture), but submit, deploy and
    rollback refuse it, `MODEL_OFFSET_REF_INVALID` (409) with exactly one
    `rating_version.load_refused` event and no Deployment, like every other revalidation refusal."""
    deployer = await seat("deployer", "analyst")
    ref, _ = await stored_version(database, blob_store, workspace_id, "clean.bundle.json")
    if act == "rollback":
        second, _ = await stored_version(database, blob_store, workspace_id, "clean.bundle.json")
        assert deploy(client, deployer, "dev", ref).status_code == 201
        assert deploy(client, deployer, "dev", second).status_code == 201
    await _pin_a_model_whose_source_has_an_offset(
        client, database, blob_store, workspace_id, deployer, ref.split(":")[1].split("@")[0]
    )
    before = await deployments_written(database, workspace_id)
    if act == "submit":
        refused = request_into(client, deployer, "prod", ref)
    elif act == "deploy":
        refused = deploy(client, deployer, "dev", ref)
    else:
        refused = client.post(
            "/api/v1/environments/dev/deployments/rollback",
            json={"rating_version_ref": ref, "reason": "regression"},
            headers=deployer.headers,
        )
    assert refused.status_code == REFUSAL_STATUS, refused.text
    assert refused.json()["code"] == "MODEL_OFFSET_REF_INVALID"
    assert await deployments_written(database, workspace_id) == before
    events = await refusal_events(database, workspace_id)
    assert [e.entity_ref for e in events] == [ref]
    assert "MODEL_OFFSET_REF_INVALID" in str((events[0].after or {}).get("refusal"))
