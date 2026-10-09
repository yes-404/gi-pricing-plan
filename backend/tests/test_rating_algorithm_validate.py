"""`POST /rating-algorithms/validate` — FR-WKNEW (WK-675 S3; RL-1474 acceptance 1, 3, 5-10).

The route reports, located and without saving, the issues that saving the same body would
refuse on. Fixtures come from `test_rating_algorithms` by name; a new save-refusal fixture is
picked up here by adding it to `INVALID_SAVE_FIXTURES`.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import pytest
from backend.tests.test_rating_algorithms import (
    PRE_EDIT_VALID_ALGORITHM,
    _headers,
    valid_algorithm,
)
from sqlalchemy import func, select

from app.db.models import AuditEventRow, RatingAlgorithmRow
from model_schema import new_uuid7

VALIDATE = "/api/v1/rating-algorithms/validate"


def _cyclic() -> dict[str, Any]:
    body = valid_algorithm()
    body["steps"][6]["consumes"] = ["risk_premium_minor", "expense_factor", "cycle_val"]
    body["steps"][7] = {
        "step_id": "s_minprem", "type": "constraint", "label": "Cycle",
        "condition": "true", "on_violation": "clamp", "reason_code": "CYCLE",
        "consumes": ["office_premium_minor"], "produces": "cycle_val",
    }
    return body


def _unresolved() -> dict[str, Any]:
    body = valid_algorithm()
    body["steps"][6]["consumes"] = ["risk_premium_minor", "expense_factor", "commission_factor"]
    return body


def _duplicate_step_id() -> dict[str, Any]:
    body = valid_algorithm()
    body["steps"][1]["step_id"] = body["steps"][0]["step_id"]
    return body


def _output_without_step() -> dict[str, Any]:
    body = valid_algorithm()
    body["outputs"].append({"name": "extra_out", "type": "money_minor", "required": False})
    return body


def _unguarded_division() -> dict[str, Any]:
    body = valid_algorithm()
    for step in body["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor / expense_factor"
    return body


def _type_mismatch() -> dict[str, Any]:
    """The `test_rating_compile` fixture: a string input feeding a money output."""
    data = valid_algorithm()
    data["input_contract"].append({"name": "customer_name", "type": "string", "nullable": False})
    data["outputs"].append({"name": "name_out", "type": "money_minor", "required": False})
    data["steps"].append({
        "step_id": "s_in_name", "type": "input", "label": "Name",
        "input_name": "customer_name", "on_missing": "error", "produces": "customer_name",
    })
    data["steps"].append({
        "step_id": "s_name_out", "type": "output", "label": "Name out",
        "output_name": "name_out", "rounding": {"mode": "half_even", "dp": 0},
        "consumes": "customer_name",
    })
    return data


INVALID_SAVE_FIXTURES: dict[str, Callable[[], dict[str, Any]]] = {
    "cyclic": _cyclic,
    "unresolved": _unresolved,
    "duplicate_step_id": _duplicate_step_id,
    "output_without_step": _output_without_step,
    "unguarded_division": _unguarded_division,
    "type_mismatch": _type_mismatch,
    "pre_edit_valid": lambda: PRE_EDIT_VALID_ALGORITHM,
}


def _validate(api_client, workspace_id, principal, grant, body):
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    return api_client.post(VALIDATE, json=body, headers=_headers(principal, workspace_id))


@pytest.mark.req("FR-WKNEW")
def test_a_cycle_names_only_the_steps_on_it(api_client, workspace_id, principal, grant) -> None:
    body = _cyclic()
    # a step downstream of the cycle must not be named
    body["steps"].insert(8, {
        "step_id": "s_after", "type": "expression", "label": "After", "expr": "cycle_val",
        "result_type": "money_minor", "consumes": ["cycle_val"], "produces": "after_val",
    })
    response = _validate(api_client, workspace_id, principal, grant, body)
    assert response.status_code == 200, response.text
    cyclic = {
        i["step_id"] for i in response.json()["issues"] if i["code"] == "RATING_GRAPH_CYCLIC"
    }
    assert cyclic == {"s_office", "s_minprem"}


@pytest.mark.req("FR-WKNEW")
def test_an_unresolved_reference_is_located_on_the_consuming_step(
    api_client, workspace_id, principal, grant
) -> None:
    response = _validate(api_client, workspace_id, principal, grant, _unresolved())
    assert response.status_code == 200, response.text
    issues = response.json()["issues"]
    assert ("RATING_GRAPH_UNRESOLVED_REF", "s_office") in {
        (i["code"], i["step_id"]) for i in issues
    }


@pytest.mark.req("FR-WKNEW")
def test_a_type_mismatch_is_reported_on_its_step(
    api_client, workspace_id, principal, grant
) -> None:
    response = _validate(api_client, workspace_id, principal, grant, _type_mismatch())
    assert response.status_code == 200, response.text
    found = {(i["code"], i["step_id"]) for i in response.json()["issues"]}
    assert ("RATING_TYPE_MISMATCH", "s_name_out") in found


@pytest.mark.req("FR-WKNEW")
@pytest.mark.parametrize("name", sorted(INVALID_SAVE_FIXTURES))
def test_the_first_reported_issue_is_the_code_save_refuses_with(
    api_client, workspace_id, principal, grant, name
) -> None:
    body = INVALID_SAVE_FIXTURES[name]()
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    saved = api_client.post(
        "/api/v1/rating-algorithms", json=body, headers=_headers(principal, workspace_id)
    )
    report = api_client.post(VALIDATE, json=body, headers=_headers(principal, workspace_id))
    assert report.status_code == 200, report.text
    assert saved.status_code == 422, saved.text
    assert report.json()["issues"][0]["code"] == saved.json()["code"]


@pytest.mark.req("FR-WKNEW")
def test_a_valid_body_reports_nothing_and_then_saves(
    api_client, workspace_id, principal, grant
) -> None:
    response = _validate(api_client, workspace_id, principal, grant, valid_algorithm())
    assert response.status_code == 200, response.text
    assert response.json() == {"issues": []}
    saved = api_client.post(
        "/api/v1/rating-algorithms",
        json=valid_algorithm(),
        headers=_headers(principal, workspace_id),
    )
    assert saved.status_code == 201, saved.text


@pytest.mark.req("FR-WKNEW")
async def test_validate_persists_and_audits_nothing(
    api_client, workspace_id, principal, grant, database
) -> None:
    await grant("analyst")

    async def _counts() -> tuple[int, int]:
        async with database.unit_of_work() as session:
            rows = await session.scalar(select(func.count()).select_from(RatingAlgorithmRow))
            events = await session.scalar(select(func.count()).select_from(AuditEventRow))
            return int(rows or 0), int(events or 0)

    before = await _counts()
    response = api_client.post(
        VALIDATE, json=valid_algorithm(), headers=_headers(principal, workspace_id)
    )
    assert response.status_code == 200, response.text
    assert await _counts() == before


@pytest.mark.req("FR-WKNEW")
async def test_validate_needs_rating_write(api_client, workspace_id, grant) -> None:
    reader = new_uuid7()
    await grant("approver", principal_id=reader)  # rating:read, no rating:write
    response = api_client.post(
        VALIDATE, json=valid_algorithm(), headers=_headers(_Who(reader), workspace_id)
    )
    assert response.status_code == 403, response.text


class _Who:
    """`_headers` reads `.id` off its principal argument."""

    def __init__(self, id_) -> None:
        self.id = id_


@pytest.mark.req("FR-WKNEW")
def test_a_malformed_body_is_a_field_level_422(
    api_client, workspace_id, principal, grant
) -> None:
    body = valid_algorithm()
    del body["steps"][0]["input_name"]
    response = _validate(api_client, workspace_id, principal, grant, body)
    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED"
    fields = [err["field"] for err in problem["errors"]]
    assert fields
    assert all(field.startswith("steps.0") for field in fields), fields


@pytest.mark.req("FR-WKNEW")
def test_the_route_publishes_typed_bodies(app) -> None:
    operation = app.openapi()["paths"][VALIDATE]["post"]
    body = operation["requestBody"]["content"]["application/json"]["schema"]
    ok = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert body == {"$ref": "#/components/schemas/RatingAlgorithmDraft"}
    assert ok == {"$ref": "#/components/schemas/AlgorithmValidationReport"}
