"""The collection routes of `api/models.py`: what they list, and what they refuse.

Two defects the W5 audit found, both of which are only visible from the edge.

**A filter the handler does not declare is dropped, not refused.** `02` §5.1 published
`GET /api/v1/factors?dataset={slug}` while the code took `?dataset_id={uuid}`, and FastAPI
ignores a query parameter no handler declares — so a caller copying the page received
`200` and *every factor in the workspace*, with nothing to say the filter had not been
applied. An unfiltered list is the one wrong answer a caller cannot tell from a right one:
a 404 is visible, a 422 is visible, and a superset of what was asked for looks exactly like
the answer. `test_an_unrecognised_factor_filter_is_refused_rather_than_ignored` is that
defect, written before the fix and observed failing as `status=200 rows=2` across two
datasets.

**Models published no list route.** Factors, bandings and groupings each did; `02` §5.1
declared none for models, so the endpoint audit read 40 of 40 — true, and measuring the
specification against itself. `00` §5.2 illustrates the platform's pagination convention
with `GET /api/v1/models?limit=50&cursor=…&status=approved`, an endpoint that did not
exist, and `test_api_model_lifecycle._slug_of` read the `models` table directly because
there was no route to ask.

Rows are inserted rather than fitted. These routes read, page and filter; they do not care
how a row was produced, and a real GLM fit per test would buy nothing this file asserts.
The lifecycle tests own the fitted path.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import pytest
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.models import ModelRow
from app.db.session import Database
from model_schema import GlmSpec, ModelStatus, OffsetSpec, new_uuid7


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    return _headers(principal.id, workspace_id)


def _spec(family: str, dataset_version_id: UUID) -> dict[str, object]:
    """A valid `GlmSpec` as JSON — `to_model` re-validates it, so `{}` will not do."""
    spec = GlmSpec(
        model_family_slug=family,
        dataset_version_id=dataset_version_id,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
    )
    dumped: dict[str, object] = spec.model_dump(mode="json")
    return dumped


def _seed(workspace_id: UUID, families: list[tuple[str, ModelStatus]]) -> list[UUID]:
    """Insert one model per `(family, status)` pair, oldest first, on a loop of our own.

    `TestClient` is blocking, so an async fixture cannot be requested from the synchronous
    tests below — `test_api_model_lifecycle` reaches for the same construction and records
    why.
    """
    from backend.tests.conftest_db import test_database_url

    async def _insert(database: Database) -> list[UUID]:
        ids: list[UUID] = []
        async with database.unit_of_work() as session:
            for family, model_status in families:
                row = ModelRow(
                    workspace_id=workspace_id,
                    model_family_slug=family,
                    version=1,
                    status=model_status.value,
                    dataset_version_id=new_uuid7(),
                    spec=_spec(family, new_uuid7()),
                    spec_hash=f"v3:sha256:{new_uuid7().hex}{new_uuid7().hex}",
                )
                session.add(row)
                await session.flush()
                ids.append(row.id)
        return ids

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            return loop.run_until_complete(_insert(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()


def _factor(api_client: TestClient, actuary: dict[str, str], dataset_id: str) -> None:
    created = api_client.post(
        "/api/v1/factors",
        json={
            "slug": f"driver-age-{new_uuid7().hex[-6:]}",
            "dataset_id": dataset_id,
            "source_columns": ["driver_age"],
        },
        headers=actuary,
    )
    assert created.status_code == 201, created.text


# -- the silent filter ---------------------------------------------------------------------


@pytest.mark.req("FR-PLAT-47")
def test_an_unrecognised_factor_filter_is_refused_rather_than_ignored(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """**Negative.** `?dataset=` is not a filter this route has, and must not read as none.

    Before the query model this returned `200` with both datasets' factors — verified, not
    assumed: the probe that became this test reported `status=200 rows=2 a_in=True
    b_in=True`. The `422` is what makes the difference between "no such filter" and "no
    matching rows" visible to the caller.
    """
    dataset_a, dataset_b = str(new_uuid7()), str(new_uuid7())
    _factor(api_client, actuary, dataset_a)
    _factor(api_client, actuary, dataset_b)

    refused = api_client.get(
        "/api/v1/factors", params={"dataset": "motor-gb"}, headers=actuary
    )
    assert refused.status_code == 422, refused.text
    problem = refused.json()
    assert problem["code"] == "VALIDATION_FAILED"
    assert any("dataset" in error["field"] for error in problem.get("errors", [])), problem


@pytest.mark.req("FR-MODEL-2")
def test_the_declared_filter_still_narrows_the_factor_list(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """The positive control the negative test needs: `?dataset_id=` is honoured.

    Without it, "the filter is refused" would be satisfied by a route that refuses
    everything.
    """
    dataset_a, dataset_b = str(new_uuid7()), str(new_uuid7())
    _factor(api_client, actuary, dataset_a)
    _factor(api_client, actuary, dataset_b)

    listed = api_client.get(
        "/api/v1/factors", params={"dataset_id": dataset_a}, headers=actuary
    )
    assert listed.status_code == 200, listed.text
    datasets = {row["dataset_id"] for row in listed.json()}
    assert datasets == {dataset_a}, "the filter narrowed to exactly the dataset asked for"


@pytest.mark.req("FR-PLAT-47")
@pytest.mark.parametrize("collection", ["bandings", "groupings"])
def test_the_sibling_list_routes_refuse_an_unrecognised_filter_too(
    api_client: TestClient, actuary: dict[str, str], collection: str
) -> None:
    """The same defect, and it is fixed in one place rather than in one route.

    Leaving the two siblings silently permissive would make the strictness a property of
    whichever route someone happened to audit.
    """
    refused = api_client.get(
        f"/api/v1/{collection}", params={"dataset": "motor-gb"}, headers=actuary
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "VALIDATION_FAILED"


# -- GET /models -------------------------------------------------------------------------


@pytest.mark.req("FR-PLAT-47")
def test_models_are_listable_and_the_page_declares_its_shape(
    api_client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """`00` §5.2's envelope: `items`, `next_cursor`, `total_estimate`."""
    family = f"motor-ad-{new_uuid7().hex[-6:]}"
    _seed(workspace_id, [(family, ModelStatus.DRAFT)])

    listed = api_client.get("/api/v1/models", headers=actuary)
    assert listed.status_code == 200, listed.text
    body = listed.json()
    assert set(body) == {"items", "next_cursor", "total_estimate"}
    assert body["total_estimate"] >= 1
    assert any(row["model_family_slug"] == family for row in body["items"])
    listed_row = next(row for row in body["items"] if row["model_family_slug"] == family)
    assert listed_row["status"] == "draft"
    # FR-MODEL-67's flag is a per-row read of the dataset version and is not computed on
    # the list path; `GET /models/{slug}` is where it is answered.
    assert listed_row["flags"] == []


@pytest.mark.req("FR-PLAT-47")
def test_the_model_list_filters_by_family_and_by_status(
    api_client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    wanted = f"motor-ad-{new_uuid7().hex[-6:]}"
    other = f"motor-tp-{new_uuid7().hex[-6:]}"
    _seed(workspace_id, [(wanted, ModelStatus.DRAFT), (other, ModelStatus.ARCHIVED)])

    by_family = api_client.get(
        "/api/v1/models", params={"family": wanted}, headers=actuary
    ).json()
    assert [row["model_family_slug"] for row in by_family["items"]] == [wanted]

    by_status = api_client.get(
        "/api/v1/models", params={"status": "archived"}, headers=actuary
    ).json()
    assert [row["model_family_slug"] for row in by_status["items"]] == [other]

    neither = api_client.get(
        "/api/v1/models",
        params={"family": wanted, "status": "archived"},
        headers=actuary,
    ).json()
    assert neither["items"] == [], "both filters apply, not whichever was read last"


@pytest.mark.req("FR-PLAT-47")
def test_the_model_list_pages_by_cursor_without_repeating_or_dropping_a_row(
    api_client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """Three rows over pages of two: every id once, and the last page says it is the last."""
    families = [f"peril-{i}-{new_uuid7().hex[-6:]}" for i in range(3)]
    seeded = set(_seed(workspace_id, [(f, ModelStatus.DRAFT) for f in families]))

    seen: list[str] = []
    cursor: str | None = None
    for _ in range(5):  # bounded: a cursor that never terminates is the bug, not a hang
        params: dict[str, object] = {"limit": 2}
        if cursor is not None:
            params["cursor"] = cursor
        page = api_client.get("/api/v1/models", params=params, headers=actuary).json()
        assert len(page["items"]) <= 2
        seen.extend(row["id"] for row in page["items"])
        cursor = page["next_cursor"]
        if cursor is None:
            break
    else:  # pragma: no cover - only reached if the cursor never terminates
        raise AssertionError("the cursor did not terminate")

    assert len(seen) == len(set(seen)), "a row appeared on two pages"
    assert seeded <= {UUID(model_id) for model_id in seen}


@pytest.mark.req("FR-PLAT-47")
def test_the_model_list_is_scoped_to_the_callers_workspace(
    api_client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """**Negative.** Another workspace's models are not listed, at any filter.

    A list route is the cheapest possible cross-workspace leak: one unscoped `select` and
    every model in the deployment is readable by anyone with `model:read`.
    """
    stranger = new_uuid7()
    family = f"other-ws-{new_uuid7().hex[-6:]}"
    _seed(stranger, [(family, ModelStatus.DRAFT)])
    _seed(workspace_id, [(f"mine-{new_uuid7().hex[-6:]}", ModelStatus.DRAFT)])

    body = api_client.get("/api/v1/models", headers=actuary).json()
    assert all(row["model_family_slug"] != family for row in body["items"])
    assert api_client.get(
        "/api/v1/models", params={"family": family}, headers=actuary
    ).json()["items"] == []


@pytest.mark.req("FR-PLAT-47")
def test_an_unrecognised_model_filter_is_refused_rather_than_ignored(
    api_client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """**Negative.** `?dataset_version_id=` is not a filter this route has — yet."""
    _seed(workspace_id, [(f"motor-{new_uuid7().hex[-6:]}", ModelStatus.DRAFT)])

    refused = api_client.get(
        "/api/v1/models",
        params={"dataset_version_id": str(new_uuid7())},
        headers=actuary,
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-PLAT-47")
def test_the_model_list_bounds_its_limit_and_types_its_cursor(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """**Negative**, twice: an unbounded page and an empty page are both silent failures.

    A malformed cursor answered with an empty page reads as "no more results" and truncates
    a caller's iteration without a word — `test_api_jobs` records the same refusal.
    """
    over = api_client.get("/api/v1/models", params={"limit": 100_000}, headers=actuary)
    assert over.status_code == 422
    assert over.json()["code"] == "VALIDATION_FAILED"

    bad_cursor = api_client.get(
        "/api/v1/models", params={"cursor": "not-a-cursor"}, headers=actuary
    )
    assert bad_cursor.status_code == 400
    assert bad_cursor.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-PLAT-47")
def test_listing_models_requires_the_read_permission(api_client: TestClient) -> None:
    """**Negative.** Development identity carries no roles; the route is not open."""
    anonymous = api_client.get("/api/v1/models")
    assert anonymous.status_code in (401, 403), anonymous.text


@pytest.mark.req("FR-DATA-56")
def test_a_privileged_caller_cannot_fit_on_a_non_validated_version(
    api_client, workspace_id, actuary, database, principal
) -> None:
    """FR-DATA-56 over HTTP: a `model:fit` caller gets `DATASET_NOT_VALIDATED`, no override.

    The service-level proof exists (`test_model_jobs.py`). This proves the route's own
    permission check and the gate fire together: the caller *holds* `model:fit` (the
    analyst role), so the 409 must name the version's status — never a missing permission,
    and never an override the day one is added (the test fails if the route starts
    accepting a non-validated version).
    """
    import asyncio

    from app.platform import datasets as dataset_service

    async def _seed() -> tuple[str, str]:
        async with database.unit_of_work() as session:
            row = await dataset_service.create_dataset(
                session, workspace_id=workspace_id, actor=principal, slug="fit-gate"
            )
            version = await dataset_service.new_version(
                session, workspace_id=workspace_id, actor=principal, dataset_id=row.id
            )
            return str(row.id), str(version.id)

    _, version_id = asyncio.get_event_loop().run_until_complete(_seed())
    response = api_client.post(
        "/api/v1/models", json={"spec": _spec("fit-gate-glm", version_id)}, headers=actuary
    )
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "DATASET_NOT_VALIDATED"
