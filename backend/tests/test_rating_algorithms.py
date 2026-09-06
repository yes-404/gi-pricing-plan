"""Rating Algorithm API — save-time validation before persist (slice W9-2).

`POST /rating-algorithms` refuses an invalid graph and a broken boundary guard with the
named error; `GET /rating-algorithms/{slug}@{version}/diff` returns the structural diff
(FR-219).
"""

from __future__ import annotations

import asyncio

import pytest

from app.api.deps import DEV_PRINCIPAL_HEADER


def valid_algorithm() -> dict:
    """A consistent seven-step graph whose expressions compile against the engine."""
    return {
        "slug": "motor-gb",
        "version": 1,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
            {"name": "effective_date", "type": "date", "nullable": False},
            {"name": "channel", "type": "enum", "domain": ["direct", "broker"], "nullable": False},
        ],
        "outputs": [
            {"name": "payable_premium_minor", "type": "money_minor", "required": True},
        ],
        "steps": [
            {"step_id": "s_in_age", "type": "input", "label": "Driver age",
             "input_name": "driver_age", "on_missing": "error", "produces": "driver_age"},
            {"step_id": "s_in_eff", "type": "input", "label": "Effective date",
             "input_name": "effective_date", "on_missing": "error", "produces": "effective_date"},
            {"step_id": "s_in_channel", "type": "input", "label": "Channel",
             "input_name": "channel", "on_missing": "error", "produces": "channel"},
            {"step_id": "s_area", "type": "lookup", "label": "Area",
             "reference_table_ref": "reference_table:ons-postcode-directory@7",
             "key_expr": ["channel"], "as_at": "effective_date", "on_miss": "error",
             "consumes": ["channel", "effective_date"], "produces": "rating_area"},
            {"step_id": "s_rp", "type": "model_call", "label": "Risk premium",
             "model_ref": "model:motor-ad-frequency@7", "mode": "exact",
             "feature_map": {"driver_age": "driver_age", "rating_area": "rating_area"},
             "consumes": ["driver_age", "rating_area"],
             "produces": ["risk_premium_minor", "peril_risk_premium"]},
            {"step_id": "s_expense", "type": "table", "label": "Expense",
             "rate_table_ref": "rate_table:motor-expense@3", "key_expr": ["channel"],
             "on_miss": "default", "consumes": ["channel"], "produces": "expense_factor"},
            {"step_id": "s_office", "type": "expression", "label": "Office premium",
             "expr": "risk_premium_minor * expense_factor", "result_type": "money_minor",
             "consumes": ["risk_premium_minor", "expense_factor"],
             "produces": "office_premium_minor"},
            {"step_id": "s_minprem", "type": "constraint", "label": "Min premium",
             "condition": "office_premium_minor >= 100", "on_violation": "clamp",
             "clamp_bounds": {"min": "100"}, "reason_code": "MIN_PREMIUM_APPLIED",
             "consumes": ["office_premium_minor"], "produces": "office_premium_minor"},
            {"step_id": "s_out", "type": "output", "label": "Payable premium",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["office_premium_minor"]},
        ],
        "sub_graphs": [],
    }


def _headers(principal, workspace_id) -> dict[str, str]:
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }


@pytest.mark.req("FR-212")
def test_a_valid_algorithm_saves(api_client, workspace_id, principal, grant) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    response = api_client.post(
        "/api/v1/rating-algorithms",
        json=valid_algorithm(),
        headers=_headers(principal, workspace_id),
    )
    assert response.status_code == 201, response.text
    assert response.json()["slug"] == "motor-gb"
    assert response.json()["version"] == 1


@pytest.mark.req("FR-212")
def test_a_cyclic_algorithm_is_refused_at_save_time(
    api_client, workspace_id, principal, grant
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    body = valid_algorithm()
    body["steps"][6]["consumes"] = ["risk_premium_minor", "expense_factor", "cycle_val"]
    body["steps"][7] = {
        "step_id": "s_minprem", "type": "constraint", "label": "Cycle",
        "condition": "true", "on_violation": "clamp", "reason_code": "CYCLE",
        "consumes": ["office_premium_minor"], "produces": "cycle_val",
    }
    response = api_client.post(
        "/api/v1/rating-algorithms", json=body, headers=_headers(principal, workspace_id)
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "RATING_GRAPH_CYCLIC"


@pytest.mark.req("FR-274")
def test_an_unguarded_division_is_refused_at_save_time(
    api_client, workspace_id, principal, grant
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    body = valid_algorithm()
    for step in body["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor / expense_factor"
    response = api_client.post(
        "/api/v1/rating-algorithms", json=body, headers=_headers(principal, workspace_id)
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "EXPRESSION_UNGUARDED_DIVISION"


@pytest.mark.req("FR-219")
def test_the_diff_route_names_the_changes(
    api_client, workspace_id, principal, grant
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    first = api_client.post(
        "/api/v1/rating-algorithms",
        json=valid_algorithm(),
        headers=_headers(principal, workspace_id),
    )
    assert first.status_code == 201, first.text

    body = valid_algorithm()
    body["version"] = 2
    for step in body["steps"]:
        if step["step_id"] == "s_expense":
            step["rate_table_ref"] = "rate_table:motor-expense@4"
    second = api_client.post(
        "/api/v1/rating-algorithms", json=body, headers=_headers(principal, workspace_id)
    )
    assert second.status_code == 201, second.text

    diff = api_client.get(
        "/api/v1/rating-algorithms/motor-gb@2/diff",
        params={"against": 1},
        headers=_headers(principal, workspace_id),
    )
    assert diff.status_code == 200, diff.text
    repoints = diff.json()["repointed_tables"]
    assert len(repoints) == 1
    assert repoints[0]["step_id"] == "s_expense"
    assert repoints[0]["after"] == "rate_table:motor-expense@4"
