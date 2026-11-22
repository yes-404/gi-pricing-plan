"""`evidence_blob` is checked at write (#1902; `02` FR-127, FR-189).

A model spec or peril structure citing an `evidence_blob` that is absent, or that the
caller's workspace cannot read, is refused with one coded 422 — one code, so a caller cannot
probe for a digest that exists in another workspace. The rule is `blob_readable_by`, used
as it is. DB-backed: Postgres only, through `blob_fixtures`.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import pytest
from backend.tests.blob_fixtures import digest, job_blob
from backend.tests.test_api_datasets import _headers
from backend.tests.test_api_models import _spec
from backend.tests.test_model_jobs import _spec as _fitted_spec
from backend.tests.test_peril_structures import (
    _book,
    _burning_cost_peril,
    _structure,
    evidence_in,
)
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.session import Database
from app.errors import MODELLING_ERROR_CODES, PlatformError
from model_schema import LargeLossKind, LargeLossTreatment, new_uuid7

CODE = "EVIDENCE_BLOB_UNREADABLE"
ROUTES = ("/api/v1/models", "/api/v1/model-specs/validate")


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    return _headers(principal.id, workspace_id)


def _ref(sha256: str) -> dict[str, object]:
    return {"sha256": sha256, "bytes": 1_024, "media_type": "application/json"}


def _owned_blob(workspace_id: UUID, sha256: str | None = None) -> str:
    """A blob owned by a job in `workspace_id`; on a loop of our own (`TestClient` blocks)."""
    from backend.tests.conftest_db import test_database_url

    sha256 = sha256 or digest()

    async def _seed(database: Database) -> None:
        await job_blob(database, workspace_id, sha256)

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            loop.run_until_complete(_seed(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()
    return sha256


def _body(sha256: str) -> dict[str, object]:
    spec = _spec("motor-gb", new_uuid7())
    spec["loss_treatment"] = {
        "kind": "capped",
        "cap_minor": 2_500_000,
        "restoration_loading": 1.2,
        "evidence_blob": _ref(sha256),
    }
    return {"spec": spec, "change_reason": "evidence check"}


def _post(client: TestClient, route: str, body: dict[str, object], headers: dict[str, str]):
    payload = body if route.endswith("/models") else {"spec": body["spec"]}
    return client.post(route, json=payload, headers=headers)


def test_the_code_is_a_registered_modelling_code() -> None:
    assert CODE in MODELLING_ERROR_CODES


@pytest.mark.req("FR-127")
@pytest.mark.parametrize("route", ROUTES)
def test_an_absent_evidence_blob_is_refused(
    api_client: TestClient, actuary: dict[str, str], route: str
) -> None:
    refused = _post(api_client, route, _body(digest()), actuary)
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == CODE


@pytest.mark.req("FR-127")
@pytest.mark.parametrize("route", ROUTES)
def test_an_evidence_blob_owned_in_another_workspace_is_refused_with_the_same_code(
    api_client: TestClient, actuary: dict[str, str], route: str
) -> None:
    sha256 = _owned_blob(new_uuid7())  # a job in some other workspace
    refused = _post(api_client, route, _body(sha256), actuary)
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == CODE


@pytest.mark.req("FR-127")
@pytest.mark.parametrize("route", ROUTES)
def test_the_absent_and_the_other_workspace_refusals_are_identical(
    api_client: TestClient, actuary: dict[str, str], route: str
) -> None:
    """The no-oracle claim, held by a test: one digest, first owned nowhere, then owned by a
    job in another workspace. Status, code, title and detail must not differ, or a caller
    could tell the two apart."""
    sha256 = digest()
    absent = _post(api_client, route, _body(sha256), actuary)
    _owned_blob(new_uuid7(), sha256)  # now owned by a job in some other workspace
    elsewhere = _post(api_client, route, _body(sha256), actuary)
    assert absent.status_code == 422, absent.text
    assert elsewhere.status_code == absent.status_code
    for field in ("code", "title", "detail"):
        assert elsewhere.json()[field] == absent.json()[field], field


@pytest.mark.req("FR-127")
@pytest.mark.parametrize(
    ("route", "success"), [("/api/v1/models", 202), ("/api/v1/model-specs/validate", 200)]
)
async def test_a_readable_evidence_blob_passes_the_check(
    api_client: TestClient, database, blob_store, workspace_id, route: str, success: int
) -> None:
    """The control: a blob owned by a job in the caller's workspace, on a spec whose dataset
    version is validated, so the route runs to its own success status (a new fit is a 202
    Job, a validation a 200)."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    spec = _fitted_spec(version_id, (area,), split_ref=split).model_dump(mode="json")
    spec["loss_treatment"] = {
        "kind": "capped",
        "cap_minor": 2_500_000,
        "restoration_loading": 1.2,
        "evidence_blob": await evidence_in(database, workspace_id),
    }
    response = _post(
        api_client,
        route,
        {"spec": spec, "change_reason": "evidence check"},
        _headers(actor.id, workspace_id),
    )
    assert response.status_code == success, response.text


# -- the peril structure, through the service ---------------------------------------------


def _capped(peril, sha256: str):
    return peril.model_copy(
        update={
            "large_loss": LargeLossTreatment(
                kind=LargeLossKind.CAPPED,
                cap_minor=2_500_000,
                restoration_loading=2,
                evidence_blob=_ref(sha256),
            )
        }
    )


@pytest.mark.req("FR-189")
@pytest.mark.parametrize("owner", ["absent", "other_workspace"])
async def test_a_structure_citing_an_unreadable_evidence_blob_is_refused(
    database, blob_store, workspace_id, owner: str
) -> None:
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    sha256 = digest()
    if owner == "other_workspace":
        await job_blob(database, new_uuid7(), sha256)
    with pytest.raises(PlatformError) as refused:
        await _structure(database, workspace_id, actor, [_capped(peril, sha256)])
    assert refused.value.code == CODE
    assert refused.value.status_code == 422


@pytest.mark.req("FR-189")
async def test_a_structure_citing_a_readable_evidence_blob_is_created(
    database, blob_store, workspace_id
) -> None:
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    sha256 = digest()
    await job_blob(database, workspace_id, sha256)
    row = await _structure(database, workspace_id, actor, [_capped(peril, sha256)])
    assert row.version == 1


# -- the peril structure, through its own route (POST /peril-structures) -------------------


def _post_structure(client: TestClient, actor, workspace_id, peril):
    return client.post(
        "/api/v1/peril-structures",
        json={
            "slug": f"motor-gb-{new_uuid7().hex[-6:]}",
            "perils": [peril.model_dump(mode="json")],
        },
        headers=_headers(actor.id, workspace_id),
    )


@pytest.mark.req("FR-189")
@pytest.mark.parametrize("owner", ["absent", "other_workspace"])
async def test_the_peril_structure_route_refuses_an_unreadable_evidence_blob(
    api_client: TestClient, database, blob_store, workspace_id, owner: str
) -> None:
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    sha256 = digest()
    if owner == "other_workspace":
        await job_blob(database, new_uuid7(), sha256)
    refused = _post_structure(api_client, actor, workspace_id, _capped(peril, sha256))
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == CODE


@pytest.mark.req("FR-189")
async def test_the_peril_structure_route_creates_with_a_readable_evidence_blob(
    api_client: TestClient, database, blob_store, workspace_id
) -> None:
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    sha256 = digest()
    await job_blob(database, workspace_id, sha256)
    created = _post_structure(api_client, actor, workspace_id, _capped(peril, sha256))
    assert created.status_code == 201, created.text
