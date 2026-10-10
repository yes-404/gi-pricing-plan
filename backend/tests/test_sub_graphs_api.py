"""Sub-graph routes (WK-1250 Slice 1, 03 §5.1): codes, permissions, scoping, immutability.

Covers FR-217 (a stored, versioned fragment), FR-227 (output-port types at create), FR-212
(the graph rules, with the code each refusal returns), `00` FR-4 and FR-16, `06` FR-343.
"""

from __future__ import annotations

import copy
from typing import Any
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.models import RoleAssignmentRow, RoleRow, SubGraphVersionRow
from app.db.session import Database
from app.platform import sub_graphs as service
from model_schema import Principal, ScopeType, new_uuid7

pytestmark = [pytest.mark.req("FR-217"), pytest.mark.usefixtures("database")]


def body() -> dict[str, Any]:
    return {
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "relativity", "required": True}],
        "steps": [
            {"step_id": "s_ncd", "type": "table", "label": "NCD ladder",
             "rate_table_ref": "rate_table:ncd@2", "key_expr": ["ncd_years"],
             "consumes": "ncd_years", "produces": "ncd_factor"}
        ],
        "change_note": "first",
    }


def create(slug: str = "ncd-ladder", **changes: Any) -> dict[str, Any]:
    return {"slug": slug, **body(), **changes}


def _headers(principal: Principal, workspace_id: UUID) -> dict[str, str]:
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


@pytest.fixture
async def headers(grant, principal: Principal, workspace_id: UUID) -> dict[str, str]:
    await grant("analyst")
    return _headers(principal, workspace_id)


def _expression(result_type: str, produces: str = "ncd_factor") -> dict[str, Any]:
    return {"step_id": "s_x", "type": "expression", "label": "x", "expr": "ncd_years",
            "result_type": result_type, "consumes": "ncd_years", "produces": produces}


# --- acceptance 4a: the code the client sees, per refusal -------------------------------------


def test_a_cyclic_fragment_is_refused_rating_graph_cyclic(api_client: TestClient, headers) -> None:
    bad = create()
    bad["steps"] = [
        {**_expression("int", "a"), "step_id": "a", "consumes": "b"},
        {**_expression("int", "b"), "step_id": "b", "consumes": "a"},
        {**_expression("int", "ncd_factor"), "step_id": "c", "consumes": "a"},
    ]
    response = api_client.post("/api/v1/sub-graphs", json=bad, headers=headers)
    assert (response.status_code, response.json()["code"]) == (422, "RATING_GRAPH_CYCLIC")


def test_an_unresolved_consume_is_refused_rating_graph_unresolved_ref(
    api_client: TestClient, headers
) -> None:
    bad = create()
    bad["steps"][0]["consumes"] = ["ncd_years", "ghost"]
    response = api_client.post("/api/v1/sub-graphs", json=bad, headers=headers)
    assert (response.status_code, response.json()["code"]) == (422, "RATING_GRAPH_UNRESOLVED_REF")


def test_an_unproduced_output_port_is_refused_rating_graph_unresolved_ref(
    api_client: TestClient, headers
) -> None:
    bad = create()
    bad["outputs"].append({"name": "ghost", "type": "int", "required": False})
    response = api_client.post("/api/v1/sub-graphs", json=bad, headers=headers)
    assert (response.status_code, response.json()["code"]) == (422, "RATING_GRAPH_UNRESOLVED_REF")


def test_an_output_port_type_mismatch_is_refused_rating_type_mismatch(
    api_client: TestClient, headers
) -> None:
    bad = create()
    bad["outputs"][0]["type"] = "money_minor"
    bad["steps"] = [_expression("string")]
    response = api_client.post("/api/v1/sub-graphs", json=bad, headers=headers)
    assert (response.status_code, response.json()["code"]) == (422, "RATING_TYPE_MISMATCH")


def test_a_cycle_wins_over_a_type_mismatch(api_client: TestClient, headers) -> None:
    bad = create()
    bad["outputs"][0]["type"] = "money_minor"
    bad["steps"] = [
        {**_expression("string", "a"), "step_id": "a", "consumes": "b"},
        {**_expression("string", "b"), "step_id": "b", "consumes": "a"},
        {**_expression("string", "ncd_factor"), "step_id": "c", "consumes": "a"},
    ]
    response = api_client.post("/api/v1/sub-graphs", json=bad, headers=headers)
    assert response.json()["code"] == "RATING_GRAPH_CYCLIC"


def _shape_refusals() -> list[tuple[str, dict[str, Any]]]:
    dup = create()
    dup["steps"].append(copy.deepcopy(dup["steps"][0]))
    chain = create()
    chain["steps"].append({**_expression("int", "ncd_years"), "step_id": "s_redo", "consumes": []})
    orphan = create()
    orphan["steps"].append(
        {**_expression("int", "unused"), "step_id": "s_orphan", "consumes": []}
    )
    extra = create(sub_graphs=[])
    port_step = create()
    port_step["steps"].append(
        {"step_id": "s_out", "type": "output", "label": "o", "output_name": "ncd_factor",
         "rounding": {"mode": "half_even", "dp": 0}, "consumes": "ncd_factor"}
    )
    blank = create(change_note="")
    missing = create()
    del missing["outputs"]
    return [
        ("duplicate step_id", dup), ("broken chain", chain), ("orphan", orphan),
        ("sub_graphs field", extra), ("output step", port_step), ("empty change note", blank),
        ("missing field", missing),
    ]


@pytest.mark.parametrize(("cause", "bad"), _shape_refusals(), ids=[c for c, _ in _shape_refusals()])
def test_a_shape_refusal_is_validation_failed(
    api_client: TestClient, headers, cause: str, bad: dict[str, Any]
) -> None:
    response = api_client.post("/api/v1/sub-graphs", json=bad, headers=headers)
    assert (response.status_code, response.json()["code"]) == (422, "VALIDATION_FAILED"), cause


def test_an_unknown_field_named_cycle_note_is_validation_failed(
    api_client: TestClient, headers
) -> None:
    response = api_client.post(
        "/api/v1/sub-graphs", json=create(cycle_note="not a cycle"), headers=headers
    )
    assert (response.status_code, response.json()["code"]) == (422, "VALIDATION_FAILED")


def test_a_non_object_body_is_validation_failed(api_client: TestClient, headers) -> None:
    response = api_client.post("/api/v1/sub-graphs", json=[1, 2], headers=headers)
    assert (response.status_code, response.json()["code"]) == (422, "VALIDATION_FAILED")


# --- acceptance 5: the two create routes and immutability -------------------------------------


def test_create_then_revise_then_read_and_list(api_client: TestClient, headers) -> None:
    first = api_client.post("/api/v1/sub-graphs", json=create(), headers=headers)
    assert first.status_code == 201, first.text
    assert (first.json()["slug"], first.json()["version"]) == ("ncd-ladder", 1)
    second = api_client.post(
        "/api/v1/sub-graphs/ncd-ladder/versions", json={**body(), "change_note": "two"},
        headers=headers,
    )
    assert second.status_code == 201, second.text
    assert second.json()["version"] == 2
    read = api_client.get("/api/v1/sub-graphs/ncd-ladder@2", headers=headers)
    assert read.status_code == 200
    assert read.json()["change_note"] == "two"
    listed = api_client.get("/api/v1/sub-graphs/ncd-ladder/versions?limit=1", headers=headers)
    assert [i["version"] for i in listed.json()["items"]] == [1]
    assert listed.json()["next_cursor"] is not None
    rest = api_client.get(
        f"/api/v1/sub-graphs/ncd-ladder/versions?limit=1&cursor={listed.json()['next_cursor']}",
        headers=headers,
    )
    assert [i["version"] for i in rest.json()["items"]] == [2]


async def test_create_on_an_existing_slug_is_409(
    api_client: TestClient, headers, database: Database, workspace_id: UUID
) -> None:
    api_client.post("/api/v1/sub-graphs", json=create(), headers=headers)
    async with database.session() as session:
        before = (await session.scalars(select(SubGraphVersionRow.content).where(
            SubGraphVersionRow.workspace_id == workspace_id))).all()
    response = api_client.post(
        "/api/v1/sub-graphs", json=create(change_note="other"), headers=headers
    )
    assert (response.status_code, response.json()["code"]) == (409, "VALIDATION_FAILED")
    async with database.session() as session:
        after = (await session.scalars(select(SubGraphVersionRow.content).where(
            SubGraphVersionRow.workspace_id == workspace_id))).all()
    assert list(after) == list(before)


def test_versions_on_an_unknown_slug_is_not_found(api_client: TestClient, headers) -> None:
    response = api_client.post("/api/v1/sub-graphs/nope/versions", json=body(), headers=headers)
    assert (response.status_code, response.json()["code"]) == (404, "NOT_FOUND")


def test_get_of_an_unknown_version_is_not_found(api_client: TestClient, headers) -> None:
    api_client.post("/api/v1/sub-graphs", json=create(), headers=headers)
    response = api_client.get("/api/v1/sub-graphs/ncd-ladder@7", headers=headers)
    assert (response.status_code, response.json()["code"]) == (404, "NOT_FOUND")


async def test_a_lost_numbering_race_is_409(
    api_client: TestClient, headers, monkeypatch: pytest.MonkeyPatch
) -> None:
    api_client.post("/api/v1/sub-graphs", json=create(), headers=headers)
    real = service._latest_version

    async def stale(session: Any, workspace: UUID, slug: str) -> int | None:
        seen = await real(session, workspace, slug)
        # The rival takes the number inside the service's own transaction (the test client
        # runs the app on another event loop, so a second connection is not available here).
        session.add(SubGraphVersionRow(
            workspace_id=workspace, slug=slug, version=(seen or 0) + 1,
            content={}, change_note="rival", created_by=new_uuid7(),
        ))
        await session.flush()
        return seen

    monkeypatch.setattr(service, "_latest_version", stale)
    response = api_client.post(
        "/api/v1/sub-graphs/ncd-ladder/versions", json=body(), headers=headers
    )
    assert (response.status_code, response.json()["code"]) == (409, "VALIDATION_FAILED")


def test_no_route_updates_or_deletes_a_sub_graph(api_client: TestClient) -> None:
    paths = api_client.app.openapi()["paths"]
    methods = {
        (method.upper(), path)
        for path, item in paths.items()
        if path.startswith("/api/v1/sub-graphs")
        for method in item
    }
    assert {m for m, _ in methods} == {"GET", "POST"}
    assert len(methods) == 4


# --- acceptance 8 and 9: permission and workspace scoping -------------------------------------


_ROUTES = [
    ("POST", "/api/v1/sub-graphs"),
    ("POST", "/api/v1/sub-graphs/ncd-ladder/versions"),
    ("GET", "/api/v1/sub-graphs/ncd-ladder@1"),
    ("GET", "/api/v1/sub-graphs/ncd-ladder/versions"),
]


@pytest.mark.req("FR-343")
@pytest.mark.parametrize(("method", "path"), _ROUTES)
async def test_a_caller_without_the_role_is_forbidden(
    api_client: TestClient, membership, workspace_id: UUID, method: str, path: str
) -> None:
    caller = new_uuid7()
    await membership(principal_id=caller)
    response = api_client.request(
        method, path, json=create(),
        headers={DEV_PRINCIPAL_HEADER: str(caller), "Workspace-Id": str(workspace_id)},
    )
    assert response.status_code == 403


@pytest.mark.req("FR-343")
@pytest.mark.parametrize(("method", "path"), _ROUTES)
async def test_a_caller_scoped_to_one_rating_algorithm_is_forbidden(
    api_client: TestClient, grant, database: Database, membership, workspace_id: UUID,
    method: str, path: str,
) -> None:
    await grant("analyst", principal_id=new_uuid7())  # seeds the roles
    caller = new_uuid7()
    await membership(principal_id=caller)
    async with database.unit_of_work() as session:
        role = (await session.execute(
            select(RoleRow).where(RoleRow.workspace_id == workspace_id, RoleRow.slug == "analyst")
        )).scalar_one()
        session.add(RoleAssignmentRow(
            workspace_id=workspace_id, principal_kind="user", principal_id=caller,
            role_id=role.id, scope_type=ScopeType.RATING_ALGORITHM.value, scope_id=new_uuid7(),
        ))
    response = api_client.request(
        method, path, json=create(),
        headers={DEV_PRINCIPAL_HEADER: str(caller), "Workspace-Id": str(workspace_id)},
    )
    assert response.status_code == 403


@pytest.mark.req("FR-16")
async def test_another_workspaces_sub_graph_is_404_and_absent_from_its_list(
    api_client: TestClient, headers, database: Database, principal: Principal
) -> None:
    other = new_uuid7()
    await service.create_sub_graph(database, other, principal, create())
    assert api_client.get("/api/v1/sub-graphs/ncd-ladder@1", headers=headers).status_code == 404
    listing = api_client.get("/api/v1/sub-graphs/ncd-ladder/versions", headers=headers)
    assert listing.status_code == 404
    mine = api_client.post("/api/v1/sub-graphs", json=create(), headers=headers)
    assert mine.status_code == 201
    assert api_client.get("/api/v1/sub-graphs/ncd-ladder@1", headers=headers).status_code == 200


# -- FD-1458 (PL-1464) items 18 and 19: the same feature_map save check ---------------------
#
# **Authored ahead of a database run** (a fitted GLM is needed); red-by-cause owed (LG-1587).


def _model_call_body(model_ref: str, feature_map: dict[str, str]) -> dict[str, Any]:
    return {
        "inputs": [{"name": "area", "type": "string"}],
        "outputs": [{"name": "risk", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_risk", "type": "model_call", "label": "Risk", "model_ref": model_ref,
             "mode": "exact", "feature_map": feature_map, "consumes": "area",
             "produces": ["risk"]}
        ],
        "change_note": "first",
    }


async def test_a_sub_graph_whose_model_call_names_a_raw_column_is_refused(
    api_client: TestClient, headers, database, blob_store, workspace_id: UUID
) -> None:
    from backend.tests.test_rating_algorithms import (
        FACTOR_SLUG,
        SOURCE_COLUMN,
        fitted_glm_with_distinct_slug,
    )

    ref = await fitted_glm_with_distinct_slug(database, blob_store, workspace_id)
    refused = api_client.post(
        "/api/v1/sub-graphs",
        json={"slug": "risk-call", **_model_call_body(ref, {"area": SOURCE_COLUMN})},
        headers=headers,
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "MODEL_CALL_FEATURE_MAP_INVALID"
    for named in ("s_risk", ref):
        assert named in refused.json()["detail"]
    assert api_client.get("/api/v1/sub-graphs/risk-call@1", headers=headers).status_code == 404

    saved = api_client.post(
        "/api/v1/sub-graphs",
        json={"slug": "risk-call", **_model_call_body(ref, {"area": FACTOR_SLUG})},
        headers=headers,
    )
    assert saved.status_code == 201, saved.text


async def test_a_sub_graph_version_whose_model_call_names_a_raw_column_is_refused(
    api_client: TestClient, headers, database, blob_store, workspace_id: UUID
) -> None:
    from backend.tests.test_rating_algorithms import (
        FACTOR_SLUG,
        SOURCE_COLUMN,
        fitted_glm_with_distinct_slug,
    )

    ref = await fitted_glm_with_distinct_slug(database, blob_store, workspace_id)
    assert api_client.post(
        "/api/v1/sub-graphs",
        json={"slug": "risk-call", **_model_call_body(ref, {"area": FACTOR_SLUG})},
        headers=headers,
    ).status_code == 201
    refused = api_client.post(
        "/api/v1/sub-graphs/risk-call/versions",
        json=_model_call_body(ref, {"area": SOURCE_COLUMN}), headers=headers,
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "MODEL_CALL_FEATURE_MAP_INVALID"
    assert api_client.get("/api/v1/sub-graphs/risk-call@2", headers=headers).status_code == 404

    saved = api_client.post(
        "/api/v1/sub-graphs/risk-call/versions",
        json=_model_call_body(ref, {"area": FACTOR_SLUG}), headers=headers,
    )
    assert saved.status_code == 201, saved.text
    assert saved.json()["version"] == 2
