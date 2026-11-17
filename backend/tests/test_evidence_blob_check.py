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
from backend.tests.test_peril_structures import (
    _book,
    _burning_cost_peril,
    _structure,
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


def _owned_blob(workspace_id: UUID) -> str:
    """A blob owned by a job in `workspace_id`; on a loop of our own (`TestClient` blocks)."""
    from backend.tests.conftest_db import test_database_url

    sha256 = digest()

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
def test_a_readable_evidence_blob_passes_the_check(
    api_client: TestClient, actuary: dict[str, str], workspace_id: UUID, route: str
) -> None:
    """The control: owned by a job in the caller's workspace. Whatever the route answers
    next (a dataset version that does not exist is a 404), it is not this refusal."""
    response = _post(api_client, route, _body(_owned_blob(workspace_id)), actuary)
    assert response.json().get("code") != CODE, response.text


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
