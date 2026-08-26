"""The Peril Structure library list over HTTP (`02` §5.1, FR-MODEL-127).

`test_peril_structures.py` owns the composition, the refusals, the reconciliation Job and
the approval — everything the artifact does. This file owns the fifth route, the collection
`GET` FR-MODEL-127 added on 2026-08-23: who may call it, what comes back, the workspace
boundary, and the one field it deliberately does **not** carry.

**The structures here are composed over a directly-seeded fitted Model rather than a real
fit.** `create_structure` calls `_resolve_models`, which asks three questions of each
reference — does it resolve in this workspace, is its status scoreable, does it carry a
`fit_result` — and nothing about the coefficients. `test_peril_structures.py` runs the fit
for real because it reconciles against it; nothing here does, and a fit per test would cost
minutes to prove a list route paginates.

Follows `test_custom_metrics_api.py`'s fixtures exactly: plain sync tests over the DB-backed
`api_client`, dev-auth headers from a granted role.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from backend.tests.test_api_datasets import _headers
from backend.tests.test_model_jobs_gbm import _gbm_spec
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.models import ModelRow, PerilStructureRow
from app.db.session import Database
from model_schema import PerilStructureStatus, new_uuid7


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    """The shared DB-backed client, under the name this module's tests use."""
    return api_client


@pytest_asyncio.fixture
async def actuary(workspace_id, principal, grant) -> dict[str, str]:
    """`model:fit` and `model:read` — enough to compose a structure and to list them."""
    await grant("pricing_actuary")
    return _headers(principal.id, workspace_id)


@pytest_asyncio.fixture
async def stranger(workspace_id, database) -> dict[str, str]:
    """Authenticated into this workspace, holding nothing.

    The list route's refusal has to be the permission answering rather than an empty page
    that happens to look the same, so the principal must be real and hold nothing at all.
    The membership (W6b-11) lets the identity resolve: without it the refusal would come
    from the membership check with `UNAUTHENTICATED`, and the route's own permission
    declaration would go untested.
    """
    from app.db.models import WorkspaceMemberRow
    from app.platform import workspaces

    stranger_id = new_uuid7()
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        session.add(WorkspaceMemberRow(user_id=stranger_id, workspace_id=workspace_id))
    return _headers(stranger_id, workspace_id)


def _run[T](work: Callable[[Database], Awaitable[T]]) -> T:
    """Run one coroutine on a loop of our own, disposing the engine it opened.

    `TestClient` is blocking, so an async fixture cannot be requested from the synchronous
    tests below — `test_custom_objectives_api._run` is the same construction and records
    why. **`dispose()` is mandatory**: an engine left open exhausts the pool across a file.
    """
    from backend.tests.conftest_db import test_database_url

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            return loop.run_until_complete(work(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()


def _slug() -> str:
    return f"motor-{new_uuid7().hex[-10:]}"


def _seed_fitted_model(workspace_id: UUID) -> str:
    """One `fitted` Model a peril can cite, without running a fit.

    `_resolve_models` refuses a reference that resolves to nothing (`NOT_FOUND`) and one
    whose model is not scoreable or carries no `fit_result` (`MODEL_NOT_FITTED`), and asks
    nothing else — so a row with a real `GbmSpec`, `status='fitted'` and a `fit_result` is
    exactly what it needs. The spec is built through `model-schema` (`CLAUDE.md` §2) rather
    than hand-written.

    Returns the `model:<slug>@1` reference the peril carries.
    """
    spec = _gbm_spec(new_uuid7(), (new_uuid7(),)).model_dump(mode="json")

    async def _insert(database: Database) -> str:
        async with database.unit_of_work() as session:
            row = ModelRow(
                workspace_id=workspace_id,
                model_family_slug=str(spec["model_family_slug"]),
                version=1,
                status="fitted",
                dataset_version_id=UUID(str(spec["dataset_version_id"])),
                spec=spec,
                spec_hash=f"v3:sha256:{new_uuid7().hex}{new_uuid7().hex}",
                fit_result={"fitted": True},
                diagnostics_id=new_uuid7(),
            )
            session.add(row)
            await session.flush()
            return f"model:{row.model_family_slug}@{row.version}"

    return _run(_insert)


def _create(
    client: TestClient, headers: dict[str, str], model_ref: str, **overrides: Any
) -> dict[str, Any]:
    """One `draft` structure, through the route that makes them."""
    body: dict[str, Any] = {
        "slug": _slug(),
        "perils": [
            {
                "peril": "AD",
                "method": "burning_cost",
                "burning_cost_model": model_ref,
                "large_loss": {"kind": "none"},
            }
        ],
        **overrides,
    }
    response = client.post("/api/v1/peril-structures", json=body, headers=headers)
    assert response.status_code == 201, response.text
    return dict(response.json())


def _advance(structure_id: UUID, *, status: PerilStructureStatus) -> None:
    """Move the lifecycle column, and only that.

    `archived` rather than `reconciled` or `review`: `reconciled_peril_structure_has_a_
    reconciliation` is a CHECK and `PerilStructure._coherent` the same rule at the contract,
    so any state past `draft` but for `archived` would need a fabricated reconciliation —
    evidence invented to exercise a filter, which is the wrong thing to teach the next
    reader about this table.
    """

    async def _update(database: Database) -> None:
        async with database.unit_of_work() as session:
            row = await session.get(PerilStructureRow, structure_id)
            assert row is not None
            row.status = status.value

    _run(_update)


def _copy_into(workspace_id: UUID, structure: dict[str, Any]) -> UUID:
    """The same composition, under another workspace.

    A direct insert because `grant` is workspace-scoped: no principal this test can build
    holds `model:fit` in a second workspace, so the row cannot be made through the route.
    The composition is copied off a real response rather than hand-written — `perils` is a
    `model-schema` shape and nothing here may define a second copy of it.
    """

    async def _insert(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = PerilStructureRow(
                id=new_uuid7(),
                workspace_id=workspace_id,
                slug=structure["slug"],
                version=structure["version"],
                status=PerilStructureStatus.DRAFT.value,
                perils=structure["perils"],
                excluded_perils=structure["excluded_perils"],
            )
            session.add(row)
            await session.flush()
            return row.id

    return _run(_insert)


# -- The library list ------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-127")
def test_the_library_lists_the_workspace_structures(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """The screen `02` §5.3 specifies had no endpoint to draw from until this route."""
    model_ref = _seed_fitted_model(workspace_id)
    first = _create(client, actuary, model_ref)
    second = _create(client, actuary, model_ref)
    response = client.get("/api/v1/peril-structures", headers=actuary)
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["items"]}
    assert {first["id"], second["id"]} <= ids


@pytest.mark.req("FR-MODEL-127")
def test_the_slug_filter_is_an_exact_match(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """**Exact**, not a prefix.

    FR-MODEL-127 makes this filter the thing that resolves §5.3's `slug@version` addresses
    against UUID-only detail routes. A prefix match would resolve `motor-gb` to `motor-gb`
    and `motor-gb-fleet` alike, which is a wrong artifact rather than a wide result — and
    FR-MODEL-61 makes this the artifact a Rating Version pins by name.
    """
    model_ref = _seed_fitted_model(workspace_id)
    target = _create(client, actuary, model_ref)
    _create(client, actuary, model_ref, slug=f"{target['slug']}-fleet")
    response = client.get(
        f"/api/v1/peril-structures?slug={target['slug']}", headers=actuary
    )
    assert response.status_code == 200, response.text
    assert [row["id"] for row in response.json()["items"]] == [target["id"]]


@pytest.mark.req("FR-MODEL-127")
def test_the_status_filter_selects_one_lifecycle_state(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    model_ref = _seed_fitted_model(workspace_id)
    draft = _create(client, actuary, model_ref)
    moved = _create(client, actuary, model_ref)
    _advance(UUID(moved["id"]), status=PerilStructureStatus.ARCHIVED)
    response = client.get("/api/v1/peril-structures?status=archived", headers=actuary)
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["items"]}
    assert moved["id"] in ids
    assert draft["id"] not in ids


@pytest.mark.req("FR-MODEL-127")
def test_the_row_carries_no_usage_count(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """§5.1:1712 asks for pagination and two filters and no count, unlike its two siblings.

    Asserted rather than left implicit: the difference between the three rows is an open
    question W32-8 raises against FR-MODEL-127's unqualified prose, and a row that silently
    grew a count would answer it by accident.
    """
    model_ref = _seed_fitted_model(workspace_id)
    created = _create(client, actuary, model_ref)
    response = client.get("/api/v1/peril-structures", headers=actuary)
    assert response.status_code == 200, response.text
    rows = {row["id"]: row for row in response.json()["items"]}
    assert "usage_count" not in rows[created["id"]]


@pytest.mark.req("FR-MODEL-127")
def test_the_library_stops_at_the_workspace_boundary(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """**Negative.** A list route is the easiest place to leak a whole workspace at once."""
    model_ref = _seed_fitted_model(workspace_id)
    mine = _create(client, actuary, model_ref)
    elsewhere = _copy_into(new_uuid7(), mine)
    response = client.get("/api/v1/peril-structures", headers=actuary)
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["items"]}
    assert mine["id"] in ids
    assert str(elsewhere) not in ids


@pytest.mark.req("FR-MODEL-127")
def test_listing_without_model_read_is_refused(
    client: TestClient,
    actuary: dict[str, str],
    stranger: dict[str, str],
    workspace_id: UUID,
) -> None:
    """**Negative.** The refusal idiom, on the list route.

    `stranger` is authenticated into this workspace and holds nothing, so the 403 is the
    permission answering rather than an empty page that happens to look the same.
    """
    _create(client, actuary, _seed_fitted_model(workspace_id))
    response = client.get("/api/v1/peril-structures", headers=stranger)
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-MODEL-127")
def test_the_page_is_cursor_paginated(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """Two pages, no overlap, and the cursor is opaque — the `GET /models` contract."""
    model_ref = _seed_fitted_model(workspace_id)
    for _ in range(3):
        _create(client, actuary, model_ref)
    first = client.get("/api/v1/peril-structures?limit=2", headers=actuary)
    assert first.status_code == 200, first.text
    page_one = first.json()
    assert len(page_one["items"]) == 2
    assert page_one["next_cursor"]
    second = client.get(
        f"/api/v1/peril-structures?limit=2&cursor={page_one['next_cursor']}",
        headers=actuary,
    )
    assert second.status_code == 200, second.text
    assert not (
        {row["id"] for row in page_one["items"]}
        & {row["id"] for row in second.json()["items"]}
    )
