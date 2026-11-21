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

import ast
import asyncio
import hashlib
import json
import logging
import pathlib
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any
from unittest.mock import create_autospec
from uuid import UUID, uuid4

import pytest
from backend.tests.approved_rows import add_approved
from backend.tests.conftest_db import edit_held_row_as_owner
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
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import score as score_api
from app.api.deps import DEV_PRINCIPAL_HEADER
from app.api.score import _fetch_bundle, hydrate_for_switch
from app.db.models import RatingVersionRow
from app.db.session import Database
from app.errors import PlatformError
from app.main import create_app
from app.platform import bundle_hydration
from app.platform.bundle_hydration import load_stored_bundle, revalidate, verify_bundle
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


_OTHER = "sha256:" + "1" * 64
#: Every hash `verify_bundle` compares, and for each a plant that changes that one thing and
#: nothing else (the other recorded hashes all stay the clean bundle's own): the hash recorded on
#: the version's row, the bundle's own stored `content_hash`, the Deployment's recorded hash, and
#: the hash recomputed from the bundle's three hashed inputs (`bundle_hash(graph, pins,
#: purpose_graphs)`), changed one input at a time. The value is the limb the log line and the
#: audit event name: the hashes that differ from the recomputed one. A changed input moves the
#: recomputed hash, so the three stored hashes are the ones left disagreeing with it.
_PLANTS: dict[str, tuple[Any, str]] = {
    "recorded_differs": (lambda b: (b, {"recorded": _OTHER}), "recorded"),
    "recorded_absent": (lambda b: (b, {"recorded": None}), "recorded"),
    "own_hash_differs": (
        lambda b: (b.model_copy(update={"content_hash": _OTHER}), {}),
        "bundle",
    ),
    "deployment_differs": (lambda b: (b, {"deployment": _OTHER}), "deployment"),
    "graph_differs": (
        lambda b: (
            b.model_copy(update={"graph": b.graph.model_copy(update={"slug": "other"})}),
            {},
        ),
        "recorded, bundle, deployment",
    ),
    "pins_differ": (
        lambda b: (
            b.model_copy(
                update={"pins": b.pins.model_copy(update={"models": ["model:motor-freq-glm@2"]})}
            ),
            {},
        ),
        "recorded, bundle, deployment",
    ),
    "purpose_graphs_differ": (lambda b: (_changed_content(b), {}), "recorded, bundle, deployment"),
}


@pytest.mark.req("FR-240")
async def test_each_compared_hash_has_its_own_plant_and_the_caller_sees_one_refusal(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """For each hash `verify_bundle` compares (`_PLANTS`), a plant that changes that one thing is
    refused, and the limb that refused is read from the log line and the audit event: the plant
    determines the limb, so a compare that stopped being made fails ITS plant, not another's.

    The caller sees ONE refusal for all of them: the same code, status, title and detail (no
    detail of which compare failed, so no oracle); the limb is in the log and the audit only, and
    neither carries content. Database-free: the refusal's audit write is replaced."""
    audited: list[dict[str, Any]] = []

    async def record(session: object, **kwargs: Any) -> None:
        audited.append(kwargs["after"])

    monkeypatch.setattr(bundle_hydration.audit, "record", record)
    ref = ArtifactRef.parse("rating_version:hash-check@1")
    clean = _clean()
    seen: dict[str, tuple[Any, ...]] = {}
    for case, (plant, limb) in _PLANTS.items():
        bundle, changed = plant(clean)
        hashes = {"recorded": clean.content_hash, "deployment": clean.content_hash, **changed}
        audited.clear()
        caplog.clear()
        with (
            caplog.at_level(logging.ERROR, logger=bundle_hydration.__name__),
            pytest.raises(PlatformError) as refused,
        ):
            await verify_bundle(
                bundle,
                slot=BundleSlot(),
                database=_NoDatabase(),  # type: ignore[arg-type]
                workspace_id=uuid4(),
                ref=ref,
                **hashes,
            )
        err = refused.value
        seen[case] = (err.code, err.status_code, err.title, err.detail)
        assert (err.code, err.status_code) == (CODE, 500), case
        assert [getattr(r, "disagreeing", None) for r in caplog.records] == [limb], case
        assert [a["refusal"] for a in audited] == [f"hash mismatch ({limb})"], case
        assert "graph" not in json.dumps(audited), case  # hashes, never content
    assert len(set(seen.values())) == 1, seen
    assert set(seen) == set(_PLANTS)


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
    """A committed edit of a held `rating_versions` row that bypasses its content guard only: a
    restored or hand-edited database (the one seam, `edit_held_row_as_owner`)."""
    await edit_held_row_as_owner("rating_versions", "rating_versions_content_guard", sql, **params)


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


_NAME = "load_stored_" + "bundle"
_LOAD_SITES = (
    "app/api/score.py",
    "app/platform/bundle_hydration.py",
    "app/worker/rating_handlers.py",
    "app/worker/dislocation_handlers.py",
)


def _row_derived(expr: ast.expr) -> bool:
    """`expr` is the row's digest read and nothing more: `<receiver>.get("blob_sha256")` or
    `<receiver>["blob_sha256"]`, the receiver holding no call. A helper, an `or`/`if` fallback, a
    hash function or any other expression is refused, whatever it also names."""
    if isinstance(expr, ast.Call):
        reads = (
            isinstance(expr.func, ast.Attribute)
            and expr.func.attr == "get"
            and len(expr.args) == 1
            and not expr.keywords
            and isinstance(expr.args[0], ast.Constant)
            and expr.args[0].value == "blob_sha256"
        )
        receiver = expr.func.value if isinstance(expr.func, ast.Attribute) else expr
    elif isinstance(expr, ast.Subscript):
        reads = isinstance(expr.slice, ast.Constant) and expr.slice.value == "blob_sha256"
        receiver = expr.value
    else:
        return False
    return reads and not any(isinstance(n, ast.Call) for n in ast.walk(receiver))


def _digests_not_from_the_row(source: str) -> list[str]:
    """One entry per `load_stored_bundle(...)` call in `source` whose `payload_sha256` is not the
    row's `bundle -> blob_sha256`: absent, a name with no assignment in the module or with ANY
    binding that is not row-derived (`_row_derived`: a plain or annotated assignment is read; a
    tuple unpack, an augmented assignment, a walrus, a loop or `with` target, an `except ... as`
    or a parameter is refused unread), or an expression that is not. A digest computed from the
    payload just read would pass the loader's compare and hold it to nothing. It sees calls by
    the name `load_stored_bundle`; a call through another name is `_name_misuse`'s to refuse.
    """
    tree = ast.parse(source)
    parents = {id(c): n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}

    def bindings(scope: ast.AST, name: str) -> list[ast.expr]:
        """Every binding of `name` in `scope`, as the value it is given. A plain or annotated
        assignment gives its value, which is then read; any other binding (a tuple or list
        unpack, an augmented assignment, a walrus, a `for`/`with`/comprehension target, an
        `except ... as`, a parameter) gives a placeholder that is not row-derived, so it is
        refused: the census does not try to follow what such a binding holds."""
        opaque = ast.Constant(value=None)

        def names(target: ast.AST) -> bool:
            return any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(target))

        def plain(target: ast.AST) -> bool:
            return isinstance(target, ast.Name) and target.id == name

        found: list[ast.expr] = []
        for n in ast.walk(scope):
            if isinstance(n, ast.Assign):
                found += [n.value if plain(t) else opaque for t in n.targets if names(t)]
            elif isinstance(n, ast.AnnAssign) and names(n.target):
                found.append(n.value if n.value is not None and plain(n.target) else opaque)
            elif (
                (isinstance(n, ast.AugAssign | ast.NamedExpr) and names(n.target))
                or (isinstance(n, ast.For | ast.AsyncFor | ast.comprehension) and names(n.target))
                or (isinstance(n, ast.withitem) and n.optional_vars and names(n.optional_vars))
                or (isinstance(n, ast.ExceptHandler) and n.name == name)
                or (isinstance(n, ast.arg) and n.arg == name)
            ):
                found.append(opaque)
        return found

    def assignments(call: ast.AST, name: str) -> list[ast.expr]:
        """The bindings of `name` in the innermost enclosing function that binds it (a nested
        function reads its outer function's variable)."""
        scope: ast.AST | None = parents.get(id(call))
        while scope is not None:
            if isinstance(scope, ast.FunctionDef | ast.AsyncFunctionDef):
                values = bindings(scope, name)
                if values:
                    return values
            scope = parents.get(id(scope))
        return []

    problems = []
    for node in ast.walk(tree):
        callee = (
            getattr(node.func, "id", getattr(node.func, "attr", None))
            if isinstance(node, ast.Call)
            else None
        )
        if callee != "load_stored_bundle":
            continue
        assert isinstance(node, ast.Call)
        digest = next((k.value for k in node.keywords if k.arg == "payload_sha256"), None)
        if digest is None:
            problems.append(f"line {node.lineno}: no payload_sha256")
        elif isinstance(digest, ast.Name):
            values = assignments(node, digest.id)
            if not values or not all(_row_derived(v) for v in values):
                problems.append(f"line {node.lineno}: {digest.id} is not the row's digest")
        elif not _row_derived(digest):
            problems.append(f"line {node.lineno}: payload_sha256 is not the row's digest")
    return problems


def _name_misuse(source: str) -> list[str]:
    """Every use of the name `load_stored_bundle` in `source` that is not a plain call of it, a
    plain `import` of it or its definition: an `import ... as` alias, a reference that is not the
    callee (`functools.partial(load_stored_bundle, ...)`, an assignment, an argument), and the
    name as a string (`getattr(module, "load_stored_bundle")`), `__all__` excepted. Each would
    let a call escape `_digests_not_from_the_row`, which finds calls by the name."""
    tree = ast.parse(source)
    parents = {id(c): n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
    problems = []
    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)
        if isinstance(node, ast.alias) and node.name.rpartition(".")[2] == _NAME and node.asname:
            problems.append(f"line {line}: imported as {node.asname}")
        elif isinstance(node, ast.Name | ast.Attribute) and (
            getattr(node, "id", getattr(node, "attr", None)) == _NAME
        ):
            parent = parents.get(id(node))
            if not (isinstance(parent, ast.Call) and parent.func is node):
                problems.append(f"line {line}: {_NAME} used as a value, not called")
        elif isinstance(node, ast.Constant) and node.value == _NAME:
            parent = parents.get(id(node))
            while parent is not None and not isinstance(parent, ast.Assign):
                parent = parents.get(id(parent))
            in_all = isinstance(parent, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "__all__" for t in parent.targets
            )
            if not in_all:
                problems.append(f"line {line}: {_NAME} as a string")
    return problems


def _files_calling_the_loader(sources: dict[str, str]) -> list[str]:
    """The paths in `sources` whose source calls `load_stored_bundle` (by name or attribute)."""
    return [
        path
        for path, source in sorted(sources.items())
        if _NAME in source
        and any(
            isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) == _NAME
            for n in ast.walk(ast.parse(source))
        )
    ]


@pytest.mark.req("FR-240")
@pytest.mark.parametrize("site", _LOAD_SITES)
def test_census_each_load_site_passes_the_rows_digest_and_never_one_it_computed(
    site: str,
) -> None:
    """Every `load_stored_bundle` call's `payload_sha256` is the row's `bundle -> blob_sha256`
    (a self-computed digest would always equal the bytes' and hold them to nothing). Each site
    is shown red when its own argument is replaced with `sha256(payload)`; the census counts the
    calls, so a site that stopped calling the loader does not read as clean here."""
    source = (_SRC / site).read_text()
    calls = [
        n
        for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) == _NAME
    ]
    assert len(calls) == 1, (site, len(calls))
    assert _digests_not_from_the_row(source) == [], site
    planted = re.sub(
        r"payload_sha256=\w+,", "payload_sha256=hashlib.sha256(payload).hexdigest(),", source
    )
    assert planted != source, site
    assert _digests_not_from_the_row(planted) != [], site


@pytest.mark.req("FR-240")
def test_census_a_rebound_digest_name_is_refused() -> None:
    """The name passed is held to EVERY assignment of it in its function: one row-derived
    assignment does not excuse a second that hashes the payload."""
    source = (
        "async def f(row, payload):\n"
        "    blob_sha256 = row.bundle.get('blob_sha256')\n"
        "    blob_sha256 = hashlib.sha256(payload).hexdigest()\n"
        "    return await load_stored_bundle(payload, payload_sha256=blob_sha256)\n"
    )
    assert _digests_not_from_the_row(source) != []
    assert (
        _digests_not_from_the_row(source.replace("    blob_sha256 = hashlib", "    zz = hashlib"))
        == []
    )


_HASH = "hashlib.sha256(payload).hexdigest()"
_ROW = "row.bundle.get('blob_sha256')"
_LOAD_CALL = "    return await load_stored_bundle(payload, payload_sha256=d)\n"
_FN = "async def f(row, payload):\n"

#: Each form the fresh-reader addendum found to slip past a callee-name, `Assign`-only census.
_UNDETECTED = {
    "annassign_second_binding": f"{_FN}    d = {_ROW}\n    d: str = {_HASH}\n{_LOAD_CALL}",
    "tuple_unpack_second_binding": f"{_FN}    d = {_ROW}\n    d, _ = {_HASH}, 1\n{_LOAD_CALL}",
    "augmented_second_binding": f"{_FN}    d = {_ROW}\n    d += 'x'\n{_LOAD_CALL}",
    "walrus_second_binding": f"{_FN}    d = {_ROW}\n    (d := {_HASH})\n{_LOAD_CALL}",
    "for_target_second_binding": (
        f"{_FN}    d = {_ROW}\n    for d in [{_HASH}]:\n        pass\n{_LOAD_CALL}"
    ),
    "helper_with_the_constant": f"{_FN}    d = _sha(payload, 'blob_sha256')\n{_LOAD_CALL}",
    "helper_after_or": f"{_FN}    d = {_ROW} or _sha(payload)\n{_LOAD_CALL}",
}


@pytest.mark.req("FR-240")
@pytest.mark.parametrize("source", list(_UNDETECTED.values()), ids=list(_UNDETECTED))
def test_census_a_second_binding_or_a_helper_that_hashes_is_refused(source: str) -> None:
    """A binding of the digest name that is not a plain, row-derived assignment is refused
    unread; and a helper handed the constant `blob_sha256`, or a fallback after the read, is not
    the row's read (`_row_derived`: the row's `.get("blob_sha256")` and nothing more)."""
    assert _digests_not_from_the_row(source) != []


_ALIASES = {
    "import_as": f"from x import load_stored_bundle as lsb\n{_FN}    return await lsb(payload)\n",
    "partial": f"{_FN}    g = partial(load_stored_bundle, payload_sha256={_ROW})\n    return g()\n",
    "functools_partial": f"{_FN}    return functools.partial(mod.load_stored_bundle)\n",
    "getattr_by_name": f"{_FN}    return await getattr(mod, 'load_stored_bundle')(payload)\n",
    "assigned_to_a_name": f"{_FN}    g = load_stored_bundle\n    return await g(payload)\n",
    "passed_as_an_argument": f"{_FN}    return await run(load_stored_bundle, payload)\n",
}


@pytest.mark.req("FR-240")
@pytest.mark.parametrize("source", list(_ALIASES.values()), ids=list(_ALIASES))
def test_census_an_alias_or_an_indirect_use_of_the_loader_is_refused(source: str) -> None:
    assert _name_misuse(source) != []


@pytest.mark.req("FR-240")
def test_census_a_plain_import_call_and_all_entry_are_not_misuse() -> None:
    source = (
        "from app.platform.bundle_hydration import load_stored_bundle\n"
        "__all__ = ['load_stored_bundle']\n"
        "async def f(row, payload):\n"
        "    return await load_stored_bundle(payload)\n"
        "async def g(row, payload):\n"
        "    return await mod.load_stored_bundle(payload)\n"
    )
    assert _name_misuse(source) == []


def _every_src_file() -> dict[str, str]:
    return {str(p.relative_to(_SRC)): p.read_text() for p in sorted(_SRC.rglob("*.py"))}


@pytest.mark.req("FR-240")
def test_census_every_file_under_src_that_calls_the_loader_is_a_listed_site_and_clean() -> None:
    """The census reads every `.py` file under `backend/src`, not four named ones: a fifth file
    that calls `load_stored_bundle` is found here and must be listed in `_LOAD_SITES` (where the
    per-site test also plants its red); every file is held to `_name_misuse`, and every calling
    file to `_digests_not_from_the_row`."""
    sources = _every_src_file()
    found = _files_calling_the_loader(sources)
    assert found == sorted(_LOAD_SITES), found
    assert {p: _name_misuse(s) for p, s in sources.items() if _name_misuse(s)} == {}
    assert {p: _digests_not_from_the_row(sources[p]) for p in found} == {key: [] for key in found}


@pytest.mark.req("FR-240")
def test_census_a_fifth_file_that_calls_the_loader_is_found() -> None:
    fifth = {"app/x.py": f"{_FN}{_LOAD_CALL}", "app/y.py": "def f(): pass\n"}
    assert _files_calling_the_loader(fifth) == ["app/x.py"]
    assert _files_calling_the_loader({**_every_src_file(), **fifth}) == sorted(
        [*_LOAD_SITES, "app/x.py"]
    )


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


class _NoDatabase:
    """A store with no database behind it: the refusal's audit write is replaced below."""

    @asynccontextmanager
    async def unit_of_work(self) -> AsyncIterator[None]:
        yield None


@pytest.mark.req("FR-240")
@pytest.mark.parametrize("swapped_part", ["resolved_payloads", "algorithm_ref"])
async def test_a_stored_payload_is_held_to_the_digest_its_row_records(
    monkeypatch: pytest.MonkeyPatch, swapped_part: str
) -> None:
    """The payload bytes read are held to the sha256 the row records, before they are used.

    The digest is `bundle -> blob_sha256` on the version's row, which the content guard holds
    once the version is past draft (`test_rating_version_content_guard.py`). The content hash
    covers the graph and pins only; here the graph, the pins and the recorded content hash are
    all unchanged and one other part of the payload differs, so the digest alone refuses, as it
    does for a digest that differs from the bytes' (the bytes unchanged) and for none: the
    resolved payloads (rate table cells, coefficients, boosters), and the `algorithm_ref` the
    bundle carries, which travels in the payload bytes and by no other path.
    Database-free: the refusal's audit write is replaced.
    """
    audited: list[tuple[str, str]] = []

    async def record(session: object, **kwargs: Any) -> None:
        audited.append((kwargs["action"], kwargs["after"]["refusal"]))

    monkeypatch.setattr(bundle_hydration.audit, "record", record)
    original = (FIXTURES / "clean.bundle.json").read_bytes()
    stored = json.loads(original)
    if swapped_part == "resolved_payloads":
        first = next(iter(stored["resolved_payloads"]))
        stored["resolved_payloads"][first]["base_level_method"] = "a_different_method"
    else:
        stored["algorithm_ref"] = "rating_algorithm:another@1"
    swapped = json.dumps(stored).encode()
    assert swapped != original
    bundle = Bundle.model_validate_json(swapped)
    clean = _clean()
    assert (bundle.graph, bundle.pins, bundle.content_hash) == (
        clean.graph,
        clean.pins,
        clean.content_hash,
    )
    digest = hashlib.sha256(original).hexdigest()
    ref = ArtifactRef(type="rating_version", slug="payload-digest", version=1)

    async def load(payload: bytes, recorded_digest: str | None) -> Bundle:
        return await load_stored_bundle(
            payload,
            payload_sha256=recorded_digest,
            recorded=clean.content_hash,
            slot=BundleSlot(),
            database=_NoDatabase(),  # type: ignore[arg-type]
            workspace_id=uuid4(),
            ref=ref,
        )

    assert (await load(original, digest)).content_hash == clean.content_hash
    # the same bytes under the digest with its `sha256:` prefix: one value, not a mismatch
    assert (await load(original, "sha256:" + digest)).content_hash == clean.content_hash
    #: A plant for each way the digest compare can fail, each changing that one thing: the bytes
    #: (digest unchanged), the digest (bytes unchanged), and the digest absent.
    plants = (
        ("bytes", swapped, digest),
        ("digest", original, "f" * 64),
        ("digest absent", original, None),
    )
    for name, refused, recorded_digest in plants:
        with pytest.raises(PlatformError) as raised:
            await load(refused, recorded_digest)
        assert raised.value.code == CODE, name
    assert audited == [(REFUSAL_ACTION, "hash mismatch (payload digest)")] * len(plants)


class _BlobReadReachedError(Exception):
    """The fetch went on to read the blob."""


@pytest.mark.req("FR-240")
async def test_a_slot_hit_is_compared_with_the_row_and_not_with_the_deployment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Characterisation of the scoring fetch's slot-hit path (ADR-2157 decision 6: the hold is
    made at load; a process that holds a bundle keeps it until it loads again).

    What it compares: the content hash recorded on the version's row (read on this call) with the
    hash the slot holds the bundle under. What it does not compare: the Deployment's hash
    (`deployment_hash`), nor the stored bytes, which it does not read. A hit is served as held;
    a row whose recorded hash the slot does not hold goes on to read the blob, where
    `load_stored_bundle` compares every hash. The switch's PREPARE has its own explicit check
    (`hydrate_for_switch`). Database-free: the session and the row are stand-ins.
    """
    held = "sha256:" + "a" * 64
    row = SimpleNamespace(bundle={"content_hash": held, "blob_sha256": "b" * 64})

    async def resolve(session: object, **kwargs: Any) -> SimpleNamespace:
        return row

    monkeypatch.setattr(score_api.rating_versions_service, "resolve_rating_version_ref", resolve)
    session = create_autospec(AsyncSession, instance=True)
    session.get.side_effect = _BlobReadReachedError
    compiled = SimpleNamespace(content_hash=held)
    slot = BundleSlot()
    ref = ArtifactRef(type="rating_version", slug="slot-hit", version=1)
    slot.put(ref, compiled)  # type: ignore[arg-type]

    async def fetch(deployment_hash: str | None) -> Any:
        return await _fetch_bundle(
            session,
            None,  # type: ignore[arg-type]
            slot,
            database=None,  # type: ignore[arg-type]
            workspace_id=uuid4(),
            ref=ref,
            deployment_hash=deployment_hash,
        )

    assert await fetch(None) is compiled
    assert await fetch("sha256:" + "9" * 64) is compiled  # a Deployment hash it does not hold
    session.get.assert_not_called()  # no blob read on a hit

    row.bundle["content_hash"] = "sha256:" + "c" * 64  # the row now records a hash it does not hold
    with pytest.raises(_BlobReadReachedError):
        await fetch(None)
