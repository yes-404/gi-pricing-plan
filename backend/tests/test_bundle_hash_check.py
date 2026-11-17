"""The loader compares the bundle it loads with the hashes recorded for it (`03` FR-240, FR-267,
clauses of 2026-11-16; ADR-2157).

One comparison (`bundle_hydration.verify_bundle`), used at every load site. Each site has a test
that goes red when that site's call alone is removed: the scoring fetch (`_fetch_bundle`),
re-validation (`revalidate`, at submit, deploy and rollback) and the switch's PREPARE
(`hydrate_for_switch`); and the live reference threads the Deployment's hash to the fetch.
The route-level case is a quote whose stored bundle is replaced under it: the database refuses
the replacement, and with that hold removed the loader refuses the bundle.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
from typing import Any
from uuid import UUID, uuid4

import pytest
from backend.tests.approved_rows import add_approved
from backend.tests.conftest_db import seed_as_owner
from backend.tests.test_rating_version_compile import (
    _insert_version,
    _minimal_algorithm,
    _row_bundle,
    _run_compile_job,
    _set_status,
)
from backend.tests.test_regression_runs import run_world  # noqa: F401
from backend.tests.test_score import SCORE_URL, _quote, admin_headers, client  # noqa: F401
from backend.tests.test_stored_bundle_revalidation import (
    FIXTURES,
    REFUSAL_ACTION,
    refusal_events,
)
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.api.score import _fetch_bundle, hydrate_for_switch
from app.db.models import RatingVersionRow
from app.db.session import Database
from app.errors import PlatformError
from app.main import create_app
from app.platform.bundle_hydration import revalidate, verify_bundle
from app.platform.bundle_slot import BundleSlot
from app.platform.deployment_switch import SwitchMessage
from app.worker.rating_handlers import register_rating_handlers
from model_schema import ActorKind, ArtifactRef, Principal, new_uuid7
from pricing_core.rating.compile import Bundle

CODE = "BUNDLE_HASH_MISMATCH"
_ACTOR = Principal(kind=ActorKind.USER, id=new_uuid7(), display="actor")


def _clean() -> Bundle:
    return Bundle.model_validate_json((FIXTURES / "clean.bundle.json").read_bytes())


async def _stored(
    database: Database, blob_store: Any, workspace_id: UUID, *, recorded: str | None
) -> ArtifactRef:
    """An approved version whose blob is the clean fixture and whose row records `recorded`."""
    payload = (FIXTURES / "clean.bundle.json").read_bytes()
    async with database.unit_of_work() as session:
        stored = await blob_store.put(session, payload, "application/json")
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
                created_by=new_uuid7(),
                bundle={
                    **({"content_hash": recorded} if recorded is not None else {}),
                    "bytes": len(payload),
                    "compiled_at": "2026-11-13T00:00:00+00:00",
                    "blob_sha256": stored.sha256,
                },
            ),
        )
    return ArtifactRef.parse(f"rating_version:{slug}@1")


async def _verify(database: Database, workspace_id: UUID, bundle: Bundle, **hashes: Any) -> None:
    await verify_bundle(
        bundle,
        slot=BundleSlot(),
        database=database,
        workspace_id=workspace_id,
        ref=ArtifactRef.parse("rating_version:hash-check@1"),
        **hashes,
    )


@pytest.mark.req("FR-240")
async def test_a_bundle_that_agrees_with_every_recorded_hash_loads(
    database: Database, workspace_id: UUID
) -> None:
    bundle = _clean()
    await _verify(database, workspace_id, bundle, recorded=bundle.content_hash)
    await _verify(
        database,
        workspace_id,
        bundle,
        recorded=bundle.content_hash,
        deployment=bundle.content_hash,
    )
    assert await refusal_events(database, workspace_id) == []


def _changed_content(bundle: Bundle) -> Bundle:
    """Content changed under the stored hash: the recomputation no longer equals it."""
    return bundle.model_copy(update={"purpose_graphs": {"x": bundle.graph}})


@pytest.mark.req("FR-240")
@pytest.mark.parametrize(
    "case",
    [
        "recorded_differs",
        "recorded_absent",
        "own_hash_differs",
        "content_differs",
        "deployment_differs",
    ],
)
async def test_a_bundle_that_disagrees_with_any_hash_is_refused_as_an_integrity_error(
    database: Database, workspace_id: UUID, case: str
) -> None:
    bundle = _clean()
    other = "sha256:" + "1" * 64
    kwargs: dict[str, Any] = {"recorded": bundle.content_hash}
    if case == "recorded_differs":
        kwargs["recorded"] = other
    elif case == "recorded_absent":
        kwargs["recorded"] = None
    elif case == "own_hash_differs":
        bundle = bundle.model_copy(update={"content_hash": other})
    elif case == "content_differs":
        bundle = _changed_content(bundle)
    else:
        kwargs["deployment"] = other
    with pytest.raises(PlatformError) as refused:
        await _verify(database, workspace_id, bundle, **kwargs)
    assert (refused.value.code, refused.value.status_code) == (CODE, 500)
    events = await refusal_events(database, workspace_id)
    assert len(events) == 1
    after = events[0].after or {}
    assert "hash mismatch" in str(after.get("refusal"))
    assert "graph" not in json.dumps(after)  # the event names hashes, never content


@pytest.mark.req("FR-240")
async def test_the_scoring_fetch_refuses_a_bundle_its_row_does_not_record(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    ref = await _stored(database, blob_store, workspace_id, recorded="sha256:" + "2" * 64)
    with pytest.raises(PlatformError) as refused:
        await _fetch_bundle(
            database,
            blob_store,
            BundleSlot(),
            database=database,
            workspace_id=workspace_id,
            ref=ref,
        )
    assert refused.value.code == CODE


@pytest.mark.req("FR-240")
async def test_the_scoring_fetch_refuses_a_bundle_the_deployment_does_not_record(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    ref = await _stored(database, blob_store, workspace_id, recorded=_clean().content_hash)
    with pytest.raises(PlatformError) as refused:
        await _fetch_bundle(
            database,
            blob_store,
            BundleSlot(),
            database=database,
            workspace_id=workspace_id,
            ref=ref,
            deployment_hash="sha256:" + "3" * 64,
        )
    assert refused.value.code == CODE


@pytest.mark.req("FR-267")
async def test_revalidation_refuses_a_bundle_its_row_does_not_record(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    ref = await _stored(database, blob_store, workspace_id, recorded="sha256:" + "4" * 64)
    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await revalidate(
                session,
                database=database,
                blob_store=blob_store,
                slot=BundleSlot(),
                workspace_id=workspace_id,
                ref=ref,
                actor=_ACTOR,
            )
    assert refused.value.code == CODE
    (event,) = await refusal_events(database, workspace_id)
    assert event.actor.get("id") == str(_ACTOR.id)  # a governance act: the acting principal


@pytest.mark.req("FR-268")
async def test_switch_prepare_refuses_a_bundle_the_deployment_does_not_record(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    ref = await _stored(database, blob_store, workspace_id, recorded=_clean().content_hash)
    message = SwitchMessage(
        switch_id=str(new_uuid7()),
        phase="prepare",
        workspace_id=workspace_id,
        environment="dev",
        deployment_id=new_uuid7(),
        rating_version_ref=str(ref),
        bundle_hash="sha256:" + "5" * 64,
    )
    with pytest.raises(PlatformError) as refused:
        await hydrate_for_switch(database, blob_store, BundleSlot(), message)
    assert (refused.value.code, refused.value.status_code) == (CODE, 500)
    assert [e.action for e in await refusal_events(database, workspace_id)] == [REFUSAL_ACTION]


# ---------------------------------------------------------------------------------------
# A stored bundle replaced under an approved, deployed version
# ---------------------------------------------------------------------------------------


def run(coro: Any) -> Any:
    """The compile test helpers drive the loop themselves, so this test is a plain function."""
    return asyncio.get_event_loop().run_until_complete(coro)


async def _replacement_refused(database: Database, digest: str, version_id: UUID) -> str | None:
    """The SQLSTATE of the application's attempt to point a version at another bundle's blob."""
    async with database.engine.connect() as conn:
        tx = await conn.begin()
        who = (await conn.execute(text("SELECT current_user"))).scalar_one()
        assert who == "gip_app_login", who
        try:
            await conn.execute(
                text(
                    "UPDATE rating_versions SET bundle = jsonb_set(bundle, '{blob_sha256}', "
                    "to_jsonb(CAST(:d AS text))) WHERE id = :id"
                ),
                {"d": digest, "id": version_id},
            )
        except DBAPIError as exc:
            return getattr(exc.orig, "sqlstate", None)
        finally:
            await tx.rollback()
    return None


async def _replace_as_owner(sql: str, **params: Any) -> None:
    """A committed edit that bypasses the triggers: a restored or hand-edited database."""

    async def edit(session: Any) -> None:
        await session.execute(text("SET LOCAL session_replication_role = replica"))
        await session.execute(text(sql), params)

    await seed_as_owner(edit)


def _quote_through(api_settings: Any, headers: dict[str, str]) -> tuple[int, Any]:
    """A fresh application: a new process's load from the rows."""
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as fresh:
        resp = fresh.post(SCORE_URL, json=_quote({"rating_version_ref": None}), headers=headers)
    return resp.status_code, resp.json()


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-44")
def test_a_replaced_bundle_is_held_by_the_database_and_refused_by_the_loader(
    client: TestClient,  # noqa: F811
    admin_headers: dict[str, str],  # noqa: F811
    database: Database,
    blob_store: Any,
    principal: Principal,
    workspace_id: UUID,
    grant: Any,
    api_settings: Any,
) -> None:
    """Two versions of one algorithm shape that price differently. The first is deployed.

    Hold 1, the database: the application's connection cannot move the first version's bundle
    to the second's, and a fresh application still quotes what it quoted.
    Hold 2, the loader: with the database's hold removed (an owner edit that skips triggers),
    a fresh application refuses the replaced bundle, both when only the blob key moved (the
    row's recorded hash disagrees) and when the whole bundle moved (the Deployment's hash does).
    A process that already holds the bundle keeps serving it until it loads again.
    """
    register_rating_handlers()
    alg_a, alg_b = _minimal_algorithm(), _minimal_algorithm()
    alg_b["slug"] = "minimal3"
    alg_b["steps"][1]["expr"] = "premium_in * 3"
    for alg in (alg_a, alg_b):
        created = client.post("/api/v1/rating-algorithms", json=alg, headers=admin_headers)
        assert created.status_code in (200, 201), created.text
    pins = {"rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": []}
    v1 = run(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            "rating_algorithm:minimal@1",
            pins,
            slug="minimal-rv",
            version=1,
        )
    )
    v2 = run(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            "rating_algorithm:minimal3@1",
            pins,
            slug="minimal-rv-b",
            version=1,
        )
    )
    for v in (v1, v2):
        job = _run_compile_job(client, admin_headers, database, blob_store, v.id)
        assert getattr(job.status, "value", job.status) == "succeeded", job.error
        _set_status(database, v.id, "approved")
    b1, b2 = _row_bundle(database, v1.id), _row_bundle(database, v2.id)
    assert b1 is not None
    assert b2 is not None
    assert b1["blob_sha256"] != b2["blob_sha256"]

    deployer = new_uuid7()
    run(grant("deployer", principal_id=deployer))
    run(grant("approver", principal_id=deployer))
    deployed = client.post(
        "/api/v1/environments/dev/deployments",
        json={
            "rating_version_ref": "rating_version:minimal-rv@1",
            "reason": "stored bundle replaced",
        },
        headers={DEV_PRINCIPAL_HEADER: str(deployer), "Workspace-Id": str(workspace_id)},
    )
    assert deployed.status_code == 201, deployed.text
    account = client.post(
        "/api/v1/service-accounts",
        json={"slug": "quoter", "environments": ["dev"], "permissions": ["score:execute"]},
        headers=admin_headers,
    )
    assert account.status_code == 201, account.text
    key = {"X-API-Key": account.json()["key"], "Workspace-Id": str(workspace_id)}
    status, body = _quote_through(api_settings, key)
    assert status == 200
    live = body["outputs"]
    assert live

    # Hold 1: the database.
    assert run(_replacement_refused(database, b2["blob_sha256"], v1.id)) == "42501"
    status, body = _quote_through(api_settings, key)
    assert (status, body.get("outputs")) == (200, live)

    # Hold 2: the loader, with the database's hold removed.
    only_the_key = (
        "UPDATE rating_versions SET bundle = jsonb_set(bundle, '{blob_sha256}', "
        "to_jsonb(CAST(:d AS text))) WHERE id = :id"
    )
    restore = "UPDATE rating_versions SET bundle = CAST(:b AS jsonb) WHERE id = :id"
    try:
        run(_replace_as_owner(only_the_key, d=b2["blob_sha256"], id=v1.id))
        warm = client.post(SCORE_URL, json=_quote({}), headers=key)
        assert warm.json().get("outputs") == live, "a process holding the bundle keeps it"
        status, body = _quote_through(api_settings, key)
        assert (status, body.get("code")) == (500, CODE)
        run(_replace_as_owner(restore, b=json.dumps(b1), id=v1.id))
        run(
            _replace_as_owner(
                "UPDATE rating_versions SET bundle = (SELECT bundle FROM rating_versions "
                "WHERE id = :o) WHERE id = :id",
                o=v2.id,
                id=v1.id,
            )
        )
        status, body = _quote_through(api_settings, key)
        assert (status, body.get("code")) == (500, CODE)
    finally:
        run(_replace_as_owner(restore, b=json.dumps(b1), id=v1.id))
    status, body = _quote_through(api_settings, key)
    assert (status, body.get("outputs")) == (200, live)


# ---------------------------------------------------------------------------------------
# Every site that loads a stored bundle goes through the one function
# ---------------------------------------------------------------------------------------

_SRC = pathlib.Path(__file__).resolve().parents[1] / "src"
#: Built in two parts so this file does not match its own predicate.
_PARSE = "Bundle." + "model_validate_json("
_LOADER = "load_stored_" + "bundle("


@pytest.mark.req("FR-240")
def test_a_stored_bundle_is_parsed_in_one_place_only() -> None:
    """The census: `grep -rn 'Bundle.model_validate_json(' backend/src` has exactly one hit, in
    `platform/bundle_hydration.py`, inside `load_stored_bundle`. Any other parse would skip the
    comparison."""
    hits = [
        f"{path.relative_to(_SRC)}:{number}"
        for path in sorted(_SRC.rglob("*.py"))
        for number, line in enumerate(path.read_text().splitlines(), 1)
        if _PARSE in line
    ]
    assert len(hits) == 1, hits
    assert hits[0].startswith("app/platform/bundle_hydration.py:"), hits


@pytest.mark.req("FR-240")
@pytest.mark.parametrize(
    "site",
    [
        "app/api/score.py",
        "app/platform/bundle_hydration.py",
        "app/worker/rating_handlers.py",
        "app/worker/dislocation_handlers.py",
    ],
)
def test_each_load_site_calls_the_one_function(site: str) -> None:
    """The four files that load a stored bundle each call the loader; removing a site's call
    alone fails its row (the scoring fetch and the switch share `score.py`; re-validation is
    `bundle_hydration.revalidate`)."""
    source = (_SRC / site).read_text()
    assert _LOADER in source.replace("async def " + _LOADER, ""), site


@pytest.mark.req("FR-240")
async def test_the_dislocation_run_refuses_a_bundle_its_row_does_not_record(
    database: Database, blob_store: Any, workspace_id: UUID
) -> None:
    from types import SimpleNamespace

    from app.worker.dislocation_handlers import _compiled

    ref = await _stored(database, blob_store, workspace_id, recorded="sha256:" + "6" * 64)
    progress = SimpleNamespace(blob_store=blob_store, database=database)
    async with database.session() as session:
        row = await session.scalar(
            select(RatingVersionRow).where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == ref.slug,
            )
        )
        assert row is not None
        with pytest.raises(PlatformError) as refused:
            await _compiled(progress, session, workspace_id, row, ref)  # type: ignore[arg-type]
    assert refused.value.code == CODE


@pytest.mark.req("FR-240")
def test_the_regression_run_refuses_a_bundle_its_row_does_not_record(run_world: Any) -> None:  # noqa: F811
    """The job's own entry (`rating.regression`): a version whose row records another hash than
    its stored bundle's is refused, and the Job ends `failed` with the integrity code."""
    from backend.tests.conftest_db import edit_held_row_as_owner

    w = run_world
    w.make_suite(properties=[{"name": "no-null", "check": {"kind": "no_null_output"}}])
    run(
        edit_held_row_as_owner(
            "rating_versions",
            "rating_versions_content_guard",
            "UPDATE rating_versions SET bundle = jsonb_set(bundle, '{content_hash}', "
            "to_jsonb(CAST(:h AS text))) WHERE id = :id",
            h="sha256:" + "7" * 64,
            id=w.rv,
        )
    )
    job = w.run()
    assert getattr(job.status, "value", job.status) == "failed", job.status
    assert CODE in str(job.error), job.error
