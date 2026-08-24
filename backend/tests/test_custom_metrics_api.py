"""Custom Metrics over HTTP (`02` FR-MODEL-108).

Parallel to `test_custom_objectives.py`'s one HTTP test, but this is the file that owns the
Custom Metric endpoints — the service and the database-layer invariants
(`test_custom_metrics_table.py`) are proved elsewhere. This proves the surface a caller
actually reaches: create answers 201 with a draft, the artifact is readable back, the
certificate 404s by name before certification, an uncertified metric cannot be submitted,
a metric with no declared direction is refused at creation, and re-creating a slug takes
the next version.

Follows `test_api_datasets.py`'s client fixture and auth headers exactly: plain sync tests
over the DB-backed `api_client`, dev-auth headers from a granted role, not the async
`client`/`pytest.mark.anyio` pattern a from-scratch draft of this file might reach for —
`asyncio_mode = "auto"` (root `pyproject.toml`) is what lets `pytest_asyncio.fixture` async
fixtures resolve transparently inside these sync tests.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from backend.tests.test_api_datasets import _headers
from backend.tests.test_contracts import OPENAPI, _load
from backend.tests.test_model_jobs_gbm import _gbm_spec
from fastapi.testclient import TestClient

from app.config import Settings
from app.db.models import CustomMetricRow, ModelRow
from app.db.session import Database
from model_schema import GbmFunctionRef, MetricStatus, new_uuid7

_BODY = {
    "slug": "capped-gamma-nll",
    "template": "capped_gamma",
    "params": {"cap": 250000},
    "applicability": {
        "responses": ["claim_severity"],
        "backends": ["xgboost"],
        "offset_required": False,
        "y_domain": {"min_exclusive": 0.0},
    },
    "direction": "lower_is_better",
}


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    """The shared DB-backed client, under the name this module's tests already use."""
    return api_client


@pytest_asyncio.fixture
async def actuary(workspace_id, principal, grant) -> dict[str, str]:
    await grant("pricing_actuary")
    return _headers(principal.id, workspace_id)


@pytest.fixture
def stranger(workspace_id) -> dict[str, str]:
    """Authenticated into this workspace, holding nothing.

    The list route's refusal has to be the permission answering rather than an empty page
    that happens to look the same, so the principal must be real and hold nothing at all.
    """
    return _headers(new_uuid7(), workspace_id)


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
    return f"metric-{new_uuid7().hex[-10:]}"


def _create(
    client: TestClient, headers: dict[str, str], **overrides: Any
) -> dict[str, Any]:
    """One `draft` template metric, through the route that makes them.

    A fresh slug per call rather than `_BODY`'s fixed one: the list tests need two metrics
    in one workspace at once, and `create` versions a repeated slug instead of adding a row.
    """
    body: dict[str, Any] = {**_BODY, "slug": _slug(), **overrides}
    response = client.post("/api/v1/custom-metrics", json=body, headers=headers)
    assert response.status_code == 201, response.text
    return dict(response.json())


def _advance(metric_id: UUID, *, status: MetricStatus) -> None:
    """Move the lifecycle columns, and only those.

    `status IN ('draft','deprecated') OR certificate_id IS NOT NULL` is a CHECK, so a
    certificate id travels with the status — which is the invariant, not a fixture detail.
    """

    async def _update(database: Database) -> None:
        async with database.unit_of_work() as session:
            row = await session.get(CustomMetricRow, metric_id)
            assert row is not None
            row.certificate_id = new_uuid7()
            row.status = status.value

    _run(_update)


def _copy_into(workspace_id: UUID, metric: dict[str, Any]) -> UUID:
    """The same declaration, under another workspace.

    A direct insert because `grant` is workspace-scoped: no principal this test can build
    holds `model:fit` in a second workspace, so the row cannot be made through the route.
    The declaration is copied off a real response rather than hand-written — `applicability`
    is a `model-schema` shape and nothing here may define a second copy of it.
    """

    async def _insert(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = CustomMetricRow(
                id=new_uuid7(),
                workspace_id=workspace_id,
                slug=metric["slug"],
                version=metric["version"],
                status=MetricStatus.DRAFT.value,
                kind=metric["kind"],
                template=metric["template"],
                params=metric["params"],
                applicability=metric["applicability"],
                direction=metric["direction"],
            )
            session.add(row)
            await session.flush()
            return row.id

    return _run(_insert)


def _seed_model_referencing(
    workspace_id: UUID, *metrics: dict[str, Any], status: str = "draft"
) -> UUID:
    """One Model whose Spec names these metric versions — what `usage_count` counts.

    Varargs, unlike `test_custom_objectives_api`'s single-artifact helper, because that is
    exactly the difference between the two aggregates: `GbmSpec.objective` is one
    `GbmFunctionRef` and `eval_metrics` is a tuple of them, so a model can name several
    metrics and must count once against each.

    A direct insert because fitting a model is a Job and the aggregate reads the `spec`
    column rather than the fit. The spec is built through `model-schema`'s `GbmSpec`
    (`CLAUDE.md` §2), so the refs seeded here are the refs a real fit would write. `status`
    is a parameter because the count must not depend on it: `usage` filters on nothing but
    the workspace, so neither may this.
    """
    spec = _gbm_spec(
        new_uuid7(),
        (new_uuid7(),),
        eval_metrics=tuple(
            GbmFunctionRef(
                kind="custom", ref=f"custom_metric:{metric['slug']}@{metric['version']}"
            )
            for metric in metrics
        ),
    ).model_dump(mode="json")
    beyond_draft = status not in ("draft", "archived")

    async def _insert(database: Database) -> UUID:
        async with database.unit_of_work() as session:
            row = ModelRow(
                workspace_id=workspace_id,
                model_family_slug=str(spec["model_family_slug"]),
                version=1,
                status=status,
                dataset_version_id=UUID(str(spec["dataset_version_id"])),
                spec=spec,
                spec_hash=f"v3:sha256:{new_uuid7().hex}{new_uuid7().hex}",
                fit_result={"fitted": True} if beyond_draft else None,
                diagnostics_id=new_uuid7() if beyond_draft else None,
            )
            session.add(row)
            await session.flush()
            return row.id

    return _run(_insert)


@pytest.mark.req("FR-MODEL-45")
def test_create_returns_201_and_a_draft(
    client: TestClient, actuary: dict[str, str]
) -> None:
    response = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["version"] == 1
    assert body["certificate_id"] is None


@pytest.mark.req("FR-MODEL-108")
def test_the_created_metric_is_readable(
    client: TestClient, actuary: dict[str, str]
) -> None:
    created = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    response = client.get(f"/api/v1/custom-metrics/{created['id']}", headers=actuary)
    assert response.status_code == 200
    assert response.json()["slug"] == "capped-gamma-nll"


@pytest.mark.req("FR-MODEL-108")
def test_the_certificate_404s_before_certification_and_names_the_metric(
    client: TestClient, actuary: dict[str, str]
) -> None:
    created = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    response = client.get(
        f"/api/v1/custom-metrics/{created['id']}/certificate", headers=actuary
    )
    assert response.status_code == 404
    assert created["id"] in response.text


@pytest.mark.req("FR-MODEL-105")
def test_an_uncertified_metric_cannot_be_submitted(
    client: TestClient, actuary: dict[str, str]
) -> None:
    """The negative half of the lifecycle: `draft -> review` is not an edge.

    The 409's `code` is `VALIDATION_FAILED` — the same code
    `submit_custom_objective` raises for a bad transition (`objectives.submit_for_review`),
    asserted here rather than left implicit so a second code meaning the same thing is
    never introduced by mistake.
    """
    created = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    response = client.post(
        f"/api/v1/custom-metrics/{created['id']}/submit", headers=actuary
    )
    assert response.status_code == 409
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-MODEL-104")
def test_a_metric_without_a_direction_is_refused(
    client: TestClient, actuary: dict[str, str]
) -> None:
    body = {k: v for k, v in _BODY.items() if k != "direction"}
    response = client.post("/api/v1/custom-metrics", json=body, headers=actuary)
    assert response.status_code == 422


@pytest.mark.req("FR-MODEL-103")
def test_a_metric_missing_a_parameter_with_no_default_is_refused(
    client: TestClient, actuary: dict[str, str]
) -> None:
    """`capped_gamma` with no `cap` answered **201** until 2026-08-20.

    `CustomMetric._the_parameters_are_the_templates_own` had copied only the unknown-key
    half of `CustomObjective`'s validator, so the one input this endpoint cannot store —
    a template that cannot be evaluated at all — was the one it accepted. Certification
    then died on a bare `KeyError` inside the Job, naming no parameter. The 422 comes for
    free once the contract refuses: `_validated` turns any `ValueError` from the artifact
    into `VALIDATION_FAILED` with the contract's own message.
    """
    body = {**_BODY, "params": {}}
    response = client.post("/api/v1/custom-metrics", json=body, headers=actuary)
    assert response.status_code == 422
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED"
    assert "'cap'" in problem["detail"]


@pytest.mark.req("FR-MODEL-103")
def test_creating_the_same_slug_twice_makes_a_second_version(
    client: TestClient, actuary: dict[str, str]
) -> None:
    first = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    second = client.post("/api/v1/custom-metrics", json=_BODY, headers=actuary).json()
    assert (first["version"], second["version"]) == (1, 2)


# -- The library list ------------------------------------------------------------------------


@pytest.mark.req("FR-MODEL-127")
def test_the_library_lists_the_workspace_metrics(
    client: TestClient, actuary: dict[str, str]
) -> None:
    """The screen `02` §5.3 specifies had no endpoint to draw from until this route."""
    first, second = _create(client, actuary), _create(client, actuary)
    response = client.get("/api/v1/custom-metrics", headers=actuary)
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["items"]}
    assert {first["id"], second["id"]} <= ids


@pytest.mark.req("FR-MODEL-127")
def test_the_slug_filter_is_an_exact_match(
    client: TestClient, actuary: dict[str, str]
) -> None:
    """**Exact**, not a prefix.

    FR-MODEL-127 makes this filter the thing that resolves §5.3's `slug@version` addresses
    against UUID-only detail routes. A prefix match would resolve `capped-gamma` to
    `capped-gamma` and `capped-gamma-tail` alike, which is a wrong artifact rather than a
    wide result.
    """
    target = _create(client, actuary)
    _create(client, actuary, slug=f"{target['slug']}-tail")
    response = client.get(f"/api/v1/custom-metrics?slug={target['slug']}", headers=actuary)
    assert response.status_code == 200, response.text
    assert [row["id"] for row in response.json()["items"]] == [target["id"]]


@pytest.mark.req("FR-MODEL-127")
def test_the_status_filter_selects_one_lifecycle_state(
    client: TestClient, actuary: dict[str, str]
) -> None:
    draft = _create(client, actuary)
    moved = _create(client, actuary)
    _advance(UUID(moved["id"]), status=MetricStatus.REVIEW)
    response = client.get("/api/v1/custom-metrics?status=review", headers=actuary)
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["items"]}
    assert moved["id"] in ids
    assert draft["id"] not in ids


@pytest.mark.req("FR-MODEL-127")
def test_each_row_carries_its_usage_count(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """§5.1:1705's list row carries the count; an unreferenced metric reads zero.

    Zero on the list and **null** on `GET /{id}`: the list asked the question and the
    detail route did not, so the two absences are different facts and are reported
    differently.
    """
    used, unused = _create(client, actuary), _create(client, actuary)
    _seed_model_referencing(workspace_id, used)
    response = client.get("/api/v1/custom-metrics", headers=actuary)
    assert response.status_code == 200, response.text
    rows = {row["id"]: row for row in response.json()["items"]}
    assert rows[used["id"]]["usage_count"] == 1
    assert rows[unused["id"]]["usage_count"] == 0

    detail = client.get(f"/api/v1/custom-metrics/{used['id']}", headers=actuary)
    assert detail.status_code == 200, detail.text
    assert detail.json()["usage_count"] is None


@pytest.mark.req("FR-MODEL-127")
def test_a_model_naming_several_metrics_counts_against_each(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """`eval_metrics` is an array, unlike `GbmSpec.objective`, which is a single ref.

    Named precisely: only `GbmSpec.objective` is a single `GbmFunctionRef`, while
    `EbmSpec.objective` is `Literal["rmse", "mae"]` — a closed builtin set that can never
    name a custom artifact, so it contributes nothing to any usage count.

    One model naming three metrics is one use of each — not one use of the first, and not
    three uses of one. This is the case the lateral expansion exists for.
    """
    first, second, third = (_create(client, actuary) for _ in range(3))
    _seed_model_referencing(workspace_id, first, second, third)
    response = client.get("/api/v1/custom-metrics", headers=actuary)
    assert response.status_code == 200, response.text
    rows = {row["id"]: row for row in response.json()["items"]}
    assert [rows[metric["id"]]["usage_count"] for metric in (first, second, third)] == [
        1,
        1,
        1,
    ]


@pytest.mark.req("FR-MODEL-127")
def test_the_row_count_agrees_with_the_detail_blast_radius(
    client: TestClient, actuary: dict[str, str], workspace_id: UUID
) -> None:
    """The row and `GET /{id}/usage` answer the same question about the same artifact.

    FR-MODEL-127's count is the library's summary of FR-MODEL-108's blast radius. Were the
    aggregate to filter on model status where `usage` does not, the row would quietly
    disagree with the page an actuary opens from it — which is worse than either absent.
    """
    metric = _create(client, actuary)
    for row_status in ("draft", "fitted", "archived"):
        _seed_model_referencing(workspace_id, metric, status=row_status)

    listed = client.get(f"/api/v1/custom-metrics?slug={metric['slug']}", headers=actuary)
    assert listed.status_code == 200, listed.text
    detail = client.get(f"/api/v1/custom-metrics/{metric['id']}/usage", headers=actuary)
    assert detail.status_code == 200, detail.text
    assert listed.json()["items"][0]["usage_count"] == len(detail.json()["models"]) == 3


@pytest.mark.req("FR-MODEL-127")
def test_the_library_stops_at_the_workspace_boundary(
    client: TestClient, actuary: dict[str, str]
) -> None:
    """**Negative.** A list route is the easiest place to leak a whole workspace at once."""
    mine = _create(client, actuary)
    elsewhere = _copy_into(new_uuid7(), mine)
    response = client.get("/api/v1/custom-metrics", headers=actuary)
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["items"]}
    assert mine["id"] in ids
    assert str(elsewhere) not in ids


@pytest.mark.req("FR-MODEL-127")
def test_listing_without_model_read_is_refused(
    client: TestClient, actuary: dict[str, str], stranger: dict[str, str]
) -> None:
    """**Negative.** The refusal idiom, on the list route.

    `stranger` is authenticated into this workspace and holds nothing, so the 403 is the
    permission answering rather than an empty page that happens to look the same.
    """
    _create(client, actuary)
    response = client.get("/api/v1/custom-metrics", headers=stranger)
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-MODEL-127")
def test_the_page_is_cursor_paginated(
    client: TestClient, actuary: dict[str, str]
) -> None:
    """Two pages, no overlap, and the cursor is opaque — the `GET /models` contract."""
    for _ in range(3):
        _create(client, actuary)
    first = client.get("/api/v1/custom-metrics?limit=2", headers=actuary)
    assert first.status_code == 200, first.text
    page_one = first.json()
    assert len(page_one["items"]) == 2
    assert page_one["next_cursor"]
    second = client.get(
        f"/api/v1/custom-metrics?limit=2&cursor={page_one['next_cursor']}",
        headers=actuary,
    )
    assert second.status_code == 200, second.text
    assert not (
        {row["id"] for row in page_one["items"]}
        & {row["id"] for row in second.json()["items"]}
    )


# -- the published contract ----------------------------------------------------------------


@pytest.mark.req("FR-MODEL-127")
@pytest.mark.req("FR-MODEL-108")
def test_every_custom_metric_route_is_in_the_published_contract() -> None:
    """The sibling guard `test_custom_objectives.py` and `test_peril_structures.py` already
    carry. It is the one assertion that fails when a route ships but the contract is not
    regenerated — the drift `generate-contracts.py --check` catches in CI, proven here
    against the committed artifact so the failure names the route rather than the file.
    """
    paths = _load(OPENAPI)["paths"]
    for method, path in (
        ("post", "/api/v1/custom-metrics"),
        ("get", "/api/v1/custom-metrics"),
        ("get", "/api/v1/custom-metrics/{metric_id}"),
        ("post", "/api/v1/custom-metrics/{metric_id}/certify"),
        ("get", "/api/v1/custom-metrics/{metric_id}/certificate"),
        ("post", "/api/v1/custom-metrics/{metric_id}/submit"),
        ("get", "/api/v1/custom-metrics/{metric_id}/usage"),
    ):
        assert method in paths.get(path, {}), f"{method.upper()} {path} is unpublished"
