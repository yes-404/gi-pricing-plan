"""A validation failure's text reaching a caller or a log carries no submitted value (NFR-499).

FD-1589 / #1712 rows 2, 3, 7, 9 and 10 (rows 4, 5 and 6 are S7b's): each sink used to render
`str(exc)` (or `f"{exc}"`) of a Pydantic `ValidationError` or a library error, and that text
prints every failing `input_value`.
Each now goes through `pricing_core.safe_error.safe_error_detail` (or fixed text, or `from None`).
Every test plants a sentinel where the sink can see it and asserts the sentinel is absent, with a
control that the text a caller needs is still there. Row 3's plain `ValueError` is a planted
reach, not a live one: the record says its reach is not demonstrated.
"""

from __future__ import annotations

import asyncio
import logging
import traceback
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from backend.tests.conftest_db import seed_as_owner
from backend.tests.test_prediction import _fitted_glm
from backend.tests.test_rating_version_compile import _empty_pins, _headers, _minimal_algorithm
from pydantic import ValidationError
from sqlalchemy import func, select

from app.config import ConfigInvalidError, load_settings
from app.db.models import (
    CustomMetricRow,
    CustomObjectiveRow,
    RatingAlgorithmRow,
    SubGraphVersionRow,
)
from app.errors import PlatformError
from app.platform import metrics as metrics_service
from app.platform import objectives as objectives_service
from app.platform import prediction as prediction_service
from app.platform import rate_tables as rate_tables_service
from app.platform.rating_algorithms import graph_validation_error
from model_schema import RatingAlgorithm
from model_schema.sub_graphs import SubGraphCreate

_SENTINEL = "SENTINEL-submitted-value-4f8a21"


@pytest.mark.req("NFR-499")
async def test_a_bulk_operation_parameter_refusal_carries_no_submitted_value(monkeypatch) -> None:
    """Row 2: `bulk_operation`'s `except ValidationError` clause."""

    class _Session:
        async def scalar(self, _statement):
            return SimpleNamespace(id=uuid4())

    class _Database:
        @asynccontextmanager
        async def unit_of_work(self):
            yield _Session()

    async def _load_version(*_args):
        return SimpleNamespace()

    async def _to_version(*_args):
        return None

    monkeypatch.setattr(rate_tables_service, "_load_version", _load_version)
    monkeypatch.setattr(rate_tables_service, "_to_version", _to_version)

    with pytest.raises(PlatformError) as refused:
        await rate_tables_service.bulk_operation(
            _Database(), uuid4(), SimpleNamespace(id=uuid4()), None, None,
            slug="t", version=1, kind="uplift_table", parameters={"percentage": _SENTINEL},
        )
    assert refused.value.status_code == 422
    assert refused.value.code == "VALIDATION_FAILED"
    assert "percentage" in (refused.value.detail or ""), "control: the field is still named"
    assert _SENTINEL not in (refused.value.detail or "")


@pytest.mark.req("NFR-499")
def test_a_library_value_error_in_a_bulk_operation_carries_no_value() -> None:
    """Row 3, a PLANTED reach: the fallback of `_map_operation_error` for a plain `ValueError`
    whose text repeats a value. A coded refusal keeps its detail (control)."""
    fallback = rate_tables_service._map_operation_error(ValueError(f"cannot read {_SENTINEL}"))
    assert fallback.code == "VALIDATION_FAILED"
    assert _SENTINEL not in (fallback.detail or "")

    coded = rate_tables_service._map_operation_error(
        ValueError("INCOMPLETE_KEY_DOMAIN: key a is missing")
    )
    assert coded.code == "RATE_TABLE_INCOMPLETE"
    assert coded.detail == "key a is missing"


@pytest.mark.req("NFR-499")
def test_a_stored_algorithm_that_no_longer_validates_leaks_no_value_at_version_create(
    api_client, workspace_id, principal, grant, database
) -> None:
    """Row 7: the second `except ValueError` clause of `create_rating_version`. The code is
    kept (Q2 (a)); the text is the allow-listed one."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    stored = _minimal_algorithm()
    stored["steps"][0]["type"] = _SENTINEL

    # A saved algorithm is an immutable artifact (no UPDATE, even for the owner), so the stale
    # row is INSERTed already invalid: what an older validator once accepted and the current one
    # refuses. The same direct write `test_rating_version_dislocation_gate` makes.
    async def _store() -> None:
        async with database.unit_of_work() as session:
            session.add(
                RatingAlgorithmRow(
                    workspace_id=workspace_id, slug="minimal", version=1,
                    content=stored, created_by=principal.id,
                )
            )

    loop.run_until_complete(_store())

    refused = api_client.post(
        "/api/v1/rating-versions",
        json={
            "slug": "stale-algorithm-rv",
            "dataset_version_id": str(uuid4()),
            "model_ref": "model:motor-ad-frequency@7",
            "algorithm_ref": "rating_algorithm:minimal@1",
            "pins": _empty_pins(),
        },
        headers=headers,
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "MODEL_REFERENCE_MODE_INCONSISTENT"
    assert _SENTINEL not in refused.text


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize(
    "setting", ["job_stall_seconds"], ids=["an invalid GIP_ setting"]
)
def test_a_refused_configuration_carries_no_value_in_its_traceback(setting: str) -> None:
    """Row 9: `load_settings` raises `from None`, so the chained `ValidationError`, which prints
    `input_value`, is not in any traceback. The per-field line is kept (control)."""
    with pytest.raises(ConfigInvalidError) as refused:
        load_settings(**{setting: _SENTINEL})
    rendered = "".join(traceback.format_exception(refused.value))
    assert f"GIP_{setting.upper()}" in rendered, "control: the variable is still named"
    assert _SENTINEL not in rendered


@pytest.mark.req("NFR-499")
async def test_a_body_that_is_not_a_table_carries_no_polars_text(
    database, blob_store, workspace_id
) -> None:
    """Row 10: `predict_rows`' detail is fixed text, with none of polars' own message."""
    actor, model_id = await _fitted_glm(database, blob_store, workspace_id)

    # The model and its factors resolve (FR-87); the body is the fault. A non-mapping first row
    # makes `pl.DataFrame` raise a `TypeError` whose text prints the next row's value.
    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await prediction_service.predict_rows(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                rows=["urban", {"area": _SENTINEL}],  # type: ignore[list-item]
                blob_store=blob_store,
            )
    assert refused.value.status_code == 422
    assert refused.value.code == "VALIDATION_FAILED"
    assert "same columns" in (refused.value.detail or ""), "control: the guidance is kept"
    assert _SENTINEL not in (refused.value.detail or "")


# -- #1712 rows 4, 5 and 6 (S7b) -------------------------------------------------------------
#
# Pydantic's `input_value` shows only the start and the end of a payload, so a sentinel in one
# place never proves another (the first version of these cases put one sentinel in the middle,
# then in the slug, and passed with each route fix reverted). Every caller-controlled string of a
# request body therefore gets its OWN sentinel, and a failure names the field that leaked and
# where. Each route also has a case whose payload is short enough that nothing is shortened.

_SLUG = "zqs-4f8a21"


def _name(field: str) -> str:
    """One distinct sentinel per field, valid as an identifier and as free text."""
    return f"zq_{field}_4f8a21"


def _stored(row: Any, slug: str) -> int:
    """Rows of `row` whose slug is `slug`, read as the owner: a refusal stores nothing."""

    async def count(session) -> int:
        return (
            await session.execute(select(func.count()).select_from(row).where(row.slug == slug))
        ).scalar_one()

    return asyncio.get_event_loop().run_until_complete(seed_as_owner(count))


def _leaks(text: str, log: str, sentinels: dict[str, str]) -> list[str]:
    found = []
    for field, value in sentinels.items():
        if value in text:
            found.append(f"{field} ({value!r}) is in the response body")
        if value in log:
            found.append(f"{field} ({value!r}) is in a log record")
    return found


def _assert_no_trace(response, caplog, row: Any, sentinels: dict[str, str]) -> None:
    """No sentinel in the response body, in any captured log record, or in a stored row. A
    failure prints which field leaked and where."""
    found = _leaks(response.text, caplog.text, sentinels)
    if row is not None and _stored(row, sentinels["slug"]):
        found.append("a row with the submitted slug is stored")
    assert not found, "leaked: " + "; ".join(found)


def _custom_artifact_body(route: str, template: str, params: dict) -> dict:
    body = {
        "slug": _SLUG,
        "template": template,
        "params": params,
        "description": _name("description"),
    }
    if route.endswith("custom-metrics"):
        body["direction"] = "lower_is_better"
    return body


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize("route", ["/api/v1/custom-metrics", "/api/v1/custom-objectives"])
@pytest.mark.parametrize(
    ("template", "params", "kept", "extra"),
    [
        # A malformed key is counted and not shown; the rule is still there.
        (
            "asymmetric_squared",
            {"ZQKEY<>4f8a21": 1.0},
            ["does not take a key", "not a parameter"],
            {"parameter key": "ZQKEY<>4f8a21"},
        ),
        # A value the caller sent is not echoed (a money parameter given as a float).
        (
            "capped_gamma",
            {"cap": 987654321.5},
            ["integer minor units"],
            {"parameter value": "987654321"},
        ),
        # A value distinct from the bound it broke is not echoed beyond the bound text.
        ("tweedie", {"p": 0.987654}, ["greater than '1.0'"], {"parameter value": "0.987654"}),
    ],
    ids=["malformed-key", "money-value", "bound-value"],
)
def test_a_custom_artifact_refusal_carries_no_submitted_value(
    api_client, workspace_id, principal, grant, caplog, route, template, params, kept, extra
) -> None:
    """Rows 5 and 6: `_validated` used to render the exception, and that text prints the key and
    the value the caller sent and the start and end of the payload it built (an id, the slug, ...,
    the description). Kept: the rule. The `kept` text is any ONE of the alternatives per route
    (the metric and the objective word the unknown-key rule alike)."""
    caplog.set_level(logging.DEBUG)
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    body = _custom_artifact_body(route, template, params)
    sentinels = {"slug": body["slug"], "description": body["description"], **extra}
    refused = api_client.post(route, json=body, headers=_headers(principal, workspace_id))
    assert refused.status_code == 422, refused.text
    row = CustomMetricRow if route.endswith("custom-metrics") else CustomObjectiveRow
    _assert_no_trace(refused, caplog, row, sentinels)
    detail = refused.json()["detail"]
    assert any(text in detail for text in kept), (detail, kept)


def _sentinel_algorithm(case: str) -> tuple[dict, dict[str, str]]:
    """A rating algorithm whose every caller-controlled string carries its own sentinel, with
    the one shape fault `case` names, and the sentinels by field."""
    n = {
        key: _name(key)
        for key in (
            "input", "produced", "output", "s_in", "s_expr", "s_out",
            "label_in", "label_expr", "label_out", "orphan_id", "orphan_label", "orphan_out",
            "unproduced_output",
        )
    }
    algorithm = {
        "slug": _SLUG,
        "version": 1,
        "input_contract": [{"name": n["input"], "type": "int", "nullable": False}],
        "outputs": [{"name": n["output"], "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": n["s_in"], "type": "input", "label": n["label_in"],
             "input_name": n["input"], "on_missing": "error", "produces": n["input"]},
            {"step_id": n["s_expr"], "type": "expression", "label": n["label_expr"],
             "expr": f"{n['input']} * 2", "result_type": "money_minor",
             "consumes": [n["input"]], "produces": n["produced"]},
            {"step_id": n["s_out"], "type": "output", "label": n["label_out"],
             "output_name": n["output"], "rounding": {"mode": "half_even", "dp": 0},
             "consumes": [n["produced"]]},
        ],
        "sub_graphs": [],
    }
    used = {"slug": _SLUG}
    if case == "orphan":
        algorithm["steps"].append(
            {"step_id": n["orphan_id"], "type": "expression", "label": n["orphan_label"],
             "expr": "1", "result_type": "int", "produces": n["orphan_out"]}
        )
    else:
        algorithm["outputs"].append(
            {"name": n["unproduced_output"], "type": "int", "required": False}
        )
    used |= {
        key: value
        for key, value in n.items()
        if value in str(algorithm) and (case == "orphan" or key != "orphan_id")
    }
    return algorithm, used


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize(
    ("case", "kept"),
    [("orphan", "unreachable from any input"), ("unproduced", "has no output step (FR-214)")],
)
def test_a_rating_graph_shape_refusal_carries_no_submitted_value(
    api_client, workspace_id, principal, grant, caplog, case, kept
) -> None:
    """Row 4: every caller-controlled string of the algorithm (slug, input and output names, step
    ids, labels, expressions' names, what a step produces) is the caller's own text. The 422
    states the rule; where it is, is the validate route's report (RL-1474)."""
    caplog.set_level(logging.DEBUG)
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    algorithm, sentinels = _sentinel_algorithm(case)
    refused = api_client.post(
        "/api/v1/rating-algorithms", json=algorithm, headers=_headers(principal, workspace_id)
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "VALIDATION_FAILED"
    _assert_no_trace(refused, caplog, RatingAlgorithmRow, sentinels)
    assert kept in refused.json()["detail"], "control: the rule is kept"


def _sentinel_sub_graph() -> tuple[dict, dict[str, str]]:
    n = {
        key: _name(key)
        for key in (
            "input", "output", "s_ncd", "label_ncd", "orphan_id", "orphan_label", "orphan_out",
            "change_note",
        )
    }
    payload = {
        "slug": _SLUG,
        "inputs": [{"name": n["input"], "type": "int"}],
        "outputs": [{"name": n["output"], "type": "relativity", "required": True}],
        "steps": [
            {"step_id": n["s_ncd"], "type": "table", "label": n["label_ncd"],
             "rate_table_ref": "rate_table:ncd@2", "key_expr": [n["input"]],
             "consumes": n["input"], "produces": n["output"]},
            {"step_id": n["orphan_id"], "type": "expression", "label": n["orphan_label"],
             "expr": "1", "result_type": "int", "produces": n["orphan_out"]},
        ],
        "change_note": n["change_note"],
    }
    return payload, {"slug": _SLUG, **n}


@pytest.mark.req("NFR-499")
def test_a_sub_graph_shape_refusal_carries_no_submitted_value(
    api_client, workspace_id, principal, grant, caplog
) -> None:
    """Row 4 through the sub-graph route: every caller-controlled string (slug, port names, step
    ids, labels, what a step produces, the change note) is absent from the 422, the log and the
    stored rows."""
    caplog.set_level(logging.DEBUG)
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    payload, sentinels = _sentinel_sub_graph()
    refused = api_client.post(
        "/api/v1/sub-graphs", json=payload, headers=_headers(principal, workspace_id)
    )
    assert refused.status_code == 422, refused.text
    _assert_no_trace(refused, caplog, SubGraphVersionRow, sentinels)
    assert "unreachable from any input port" in refused.json()["detail"], "control: rule kept"


# The short-payload cases: a payload so short that pydantic shortens nothing, so a reverted sink
# would print every submitted string. A request body cannot be that short (the request models
# need fields of their own), so these call the sinks the routes call, with the same kind of
# invalid payload; none needs a database.


@pytest.mark.req("NFR-499")
def test_a_short_custom_metric_payload_leaks_nothing_through_validated() -> None:
    payload = {"slug": _name("slug"), "applicability": {"responses": [_name("response")]}}
    with pytest.raises(PlatformError) as refused:
        metrics_service._validated(payload, template=metrics_service.ObjectiveTemplate.TWEEDIE)
    assert refused.value.status_code == 422
    for field, value in {"slug": _name("slug"), "response": _name("response")}.items():
        assert value not in (refused.value.detail or ""), f"{field} leaked in the 422 detail"
    assert (refused.value.detail or "").startswith("1 validation error") or "validation error" in (
        refused.value.detail or ""
    ), "control: the failure is still described"


@pytest.mark.req("NFR-499")
def test_a_short_custom_objective_payload_leaks_nothing_through_validated() -> None:
    payload = {"slug": _name("slug"), "applicability": {"responses": [_name("response")]}}
    with pytest.raises(PlatformError) as refused:
        objectives_service._validated(payload, template=None)
    assert refused.value.status_code == 422
    for field, value in {"slug": _name("slug"), "response": _name("response")}.items():
        assert value not in (refused.value.detail or ""), f"{field} leaked in the 422 detail"
    assert "validation error" in (refused.value.detail or ""), "control: still described"


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize(
    ("schema", "artifact"),
    [(RatingAlgorithm, "rating algorithm"), (SubGraphCreate, "sub-graph")],
    ids=["rating-algorithm", "sub-graph"],
)
def test_a_short_graph_payload_leaks_nothing_through_graph_validation_error(
    schema, artifact
) -> None:
    payload = {"slug": _name("slug"), "inputs": [_name("input")], "steps": _name("steps")}
    with pytest.raises(ValidationError) as caught:
        schema.model_validate(payload)
    refusal = graph_validation_error(caught.value, artifact=artifact)
    assert refusal.status_code == 422
    for field in ("slug", "input", "steps"):
        assert _name(field) not in (refusal.detail or ""), f"{field} leaked in the 422 detail"
    assert "validation error" in (refusal.detail or ""), "control: still described"
