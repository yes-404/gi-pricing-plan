"""FD-1671 / SL-2118, condition (f): the create_app() + database reading of the score routes'
Decimal parse (FR-273), completing `test_score_decimal_input_http.py`'s stubbed one.

One real app, one genuinely compiled Rating Version with a `decimal` input, a Service Account
caller: a 15-digit factor prices as before, a 20-digit one is a 422 problem naming the input, and a
sampled quote's stored Quote Context keeps the factor a JSON **number** (a `Decimal` dumped in
pydantic's JSON mode is a string, which the off-path re-score would refuse as not numeric).

DB-backed: the gate's DB window runs it; a seat without a database does not."""

# ruff: noqa: F811  (fixtures imported from test_score are re-named as parameters, as pytest wants)
from __future__ import annotations

import asyncio
from typing import Any

import pytest
from backend.tests.test_rating_version_compile import (
    _empty_pins,
    _insert_version,
    _minimal_algorithm,
    _run_compile_job,
)
from backend.tests.test_score import (  # noqa: F401  (fixtures, imported the way sibling files do)
    SCORE_URL,
    SCORED_REF,
    _quote,
    _rows_for,
    _run,
    _set_trace_sample_rate,
    admin_headers,
    client,
    scoring_headers,
)
from fastapi.testclient import TestClient

from app.worker.rating_handlers import register_rating_handlers
from model_schema import JobStatus


def _decimal_algorithm() -> dict[str, Any]:
    """`_minimal_algorithm` plus a `decimal` input `factor`: payable = premium_in * factor."""
    algorithm = _minimal_algorithm()
    algorithm["input_contract"].append({"name": "factor", "type": "decimal", "nullable": False})
    algorithm["steps"].insert(
        1,
        {
            "step_id": "s_in_f",
            "type": "input",
            "label": "Factor",
            "input_name": "factor",
            "on_missing": "error",
            "produces": "factor",
        },
    )
    expr = next(s for s in algorithm["steps"] if s["step_id"] == "s_expr")
    expr["expr"] = "premium_in * factor"
    expr["consumes"] = ["premium_in", "factor"]
    return algorithm


@pytest.fixture
def compiled_decimal_version(
    client: TestClient,
    admin_headers: dict[str, str],
    database: Any,
    blob_store: Any,
    principal: Any,
    workspace_id: Any,
) -> Any:
    """`rating_version:minimal-rv@1` over `_decimal_algorithm()`."""
    register_rating_handlers()
    created = client.post(
        "/api/v1/rating-algorithms", json=_decimal_algorithm(), headers=admin_headers
    )
    assert created.status_code in (200, 201), created.text
    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins=_empty_pins(),
        )
    )
    job = _run_compile_job(client, admin_headers, database, blob_store, row.id)
    assert job.status is JobStatus.SUCCEEDED, job.error
    return row


def _post_factor(client: TestClient, headers: dict[str, str], factor_text: str) -> Any:
    """`premium_in` 50000 and a factor written as a JSON number, character for character."""
    body = (
        '{"purpose":"new_business","quoted_at":"2026-08-30T09:00:00Z","effective_date":"2026-09-01",'
        f'"inputs":{{"premium_in":50000,"factor":{factor_text}}},'
        f'"options":{{"rating_version_ref":"{SCORED_REF}"}}}}'
    )
    return client.post(
        SCORE_URL, content=body, headers={**headers, "content-type": "application/json"}
    )


@pytest.mark.req("FR-239")
def test_a_15_digit_factor_prices_as_before_through_the_real_app(
    client: TestClient, scoring_headers: dict[str, str], compiled_decimal_version: Any
) -> None:
    response = _post_factor(client, scoring_headers, "0.824690000000000")
    assert response.status_code == 200, response.text
    assert response.json()["outputs"]["payable_premium_minor"] == 41234


@pytest.mark.req("FR-273")
@pytest.mark.parametrize("text", ["0.82469000000000000002", "0.82468999999999999998"])
def test_a_20_digit_factor_is_a_422_problem_naming_the_input_through_the_real_app(
    client: TestClient, scoring_headers: dict[str, str], compiled_decimal_version: Any, text: str
) -> None:
    response = _post_factor(client, scoring_headers, text)
    assert response.status_code == 422, response.text
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "INPUT_CONTRACT_VIOLATION"
    assert "'factor'" in response.json()["detail"]
    assert text not in response.text  # NFR-499


@pytest.mark.req("FR-259")
def test_a_sampled_quotes_stored_context_keeps_the_factor_a_json_number(
    client: TestClient,
    scoring_headers: dict[str, str],
    compiled_decimal_version: Any,
    database: Any,
    workspace_id: Any,
) -> None:
    _run(_set_trace_sample_rate(database, workspace_id, 1.0))
    response = _post_factor(client, scoring_headers, "0.75")
    assert response.status_code == 200, response.text
    rows = _run(_rows_for(database, workspace_id))
    assert len(rows) == 1
    stored = rows[0].pending_quote_context
    assert stored is not None
    assert stored["inputs"]["factor"] == 0.75
    assert isinstance(stored["inputs"]["factor"], float)
