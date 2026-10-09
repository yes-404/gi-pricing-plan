"""FD-1458 (PL-1464): a Rating Version pinning a fitted GLM compiles and scores, end to end.

The resolver loads the GLM's Factors, Bandings and Groupings the way `/predict` does; compile
carries them in the Bundle; `POST /api/v1/score` returns the value `predict_rows` returns for
the same row (FR-222, FR-193, FR-239, NFR-491).

**Authored ahead of a database run** (the small-test rule bars Postgres): every test here needs
`GIP_TEST_DATABASE_URL`, and its red-by-cause is owed to the first gate-slot window (LG-9449).
"""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

import pytest
from backend.tests.approved_rows import mark_approved
from backend.tests.test_backtests import _fitted_model
from backend.tests.test_prediction import _fitted_residual_pair
from backend.tests.test_rating_version_compile import (
    _insert_version,
    _read_blob,
    _run_compile_job,
)
from backend.tests.test_score import admin_headers, client, scoring_headers  # noqa: F401
from fastapi.testclient import TestClient

from app.db.models import ModelRow
from app.platform import prediction as prediction_service
from app.worker.rating_handlers import register_rating_handlers
from model_schema import JobStatus
from pricing_core.rating.compile import Bundle

SCORE_URL = "/api/v1/score"
ROW = {"area": "urban", "exposure_years": 1.0}


def _algorithm(model_ref: str, feature_map: dict[str, str]) -> dict[str, Any]:
    """Inputs -> `model_call` -> an `output` that rounds once, at the output (FR-226)."""
    return {
        "slug": "glm-score",
        "version": 1,
        "input_contract": [
            {"name": "area", "type": "enum", "domain": ["urban", "rural"], "nullable": False},
            {"name": "exposure_years", "type": "decimal", "nullable": False},
        ],
        "outputs": [{"name": "risk_out", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_area", "type": "input", "label": "Area", "input_name": "area",
             "on_missing": "error", "produces": "area"},
            {"step_id": "s_exp", "type": "input", "label": "Exposure",
             "input_name": "exposure_years", "on_missing": "error",
             "produces": "exposure_years"},
            {"step_id": "s_risk", "type": "model_call", "label": "Risk", "model_ref": model_ref,
             "mode": "exact", "feature_map": feature_map, "result_type": "decimal",
             "consumes": ["area", "exposure_years"], "produces": ["risk"]},
            {"step_id": "s_out", "type": "output", "label": "Risk", "output_name": "risk_out",
             "rounding": {"mode": "half_even", "dp": 9}, "consumes": ["risk"]},
        ],
        "sub_graphs": [],
    }


async def _approve(database: Any, model_id: UUID) -> str:
    async with database.unit_of_work() as session:
        row = await session.get(ModelRow, model_id)
        assert row is not None
        await mark_approved(session, row)
        return f"model:{row.model_family_slug}@{row.version}"


def _compile(
    http: TestClient, headers: dict[str, str], database: Any, blob_store: Any,
    principal: Any, workspace_id: UUID, model_ref: str, feature_map: dict[str, str],
) -> tuple[Bundle, str]:
    """Save the algorithm, pin the model, compile through the real Job; return the Bundle."""
    register_rating_handlers()
    created = http.post(
        "/api/v1/rating-algorithms", json=_algorithm(model_ref, feature_map), headers=headers
    )
    assert created.status_code == 201, created.text
    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database, workspace_id, principal.id, algorithm_ref="rating_algorithm:glm-score@1",
            pins={"rate_tables": [], "models": [model_ref], "reference_tables": [],
                  "custom_objectives": []},
            slug="glm-rv",
        )
    )
    job = _run_compile_job(http, headers, database, blob_store, row.id)
    assert job.status is JobStatus.SUCCEEDED, job.error
    blob = _read_blob(database, blob_store, job.result["ref"])
    return Bundle.model_validate_json(blob), "rating_version:glm-rv@1"


@pytest.mark.req("FR-222")
@pytest.mark.req("FR-239")
def test_a_rating_version_pinning_a_fitted_glm_compiles_and_scores(
    client: TestClient,  # noqa: F811
    admin_headers: dict[str, str],  # noqa: F811
    scoring_headers: dict[str, str],  # noqa: F811
    database: Any, blob_store: Any, principal: Any, workspace_id: UUID,
) -> None:
    """A GLM fitted through the real Job and approved, pinned by a `model_call`, compiled
    through `_run_compile_job`: the Bundle carries its Factors, and `/score` returns the value
    `/predict` returns for the same row (item 5). Red first: `/score` answers
    `MODEL_CALL_FAILED`."""
    loop = asyncio.get_event_loop()
    _, model_id, *_ = loop.run_until_complete(_fitted_model(database, blob_store, workspace_id))
    model_ref = loop.run_until_complete(_approve(database, model_id))
    bundle, version_ref = _compile(
        client, admin_headers, database, blob_store, principal, workspace_id, model_ref,
        {"area": "area", "exposure_years": "exposure_years"},
    )
    assert any(key.startswith("factor:area@") for key in bundle.resolved_payloads)

    async def _expected() -> float:
        async with database.session() as session:
            prediction = await prediction_service.predict_rows(
                session, workspace_id=workspace_id, actor=principal, model_id=model_id,
                rows=[ROW], blob_store=blob_store,
            )
        return float(prediction.rows[0].expected)

    expected = loop.run_until_complete(_expected())
    response = client.post(
        SCORE_URL,
        json={
            "purpose": "new_business", "quoted_at": "2026-10-10T09:00:00Z",
            "effective_date": "2026-10-11", "inputs": ROW,
            "options": {"rating_version_ref": version_ref},
        },
        headers=scoring_headers,
    )
    assert response.status_code == 200, response.text
    assert float(response.json()["outputs"]["risk_out"]) == pytest.approx(expected, rel=1e-9)


@pytest.mark.req("FR-116")
def test_a_model_offset_glm_scores_with_its_source_model(
    client: TestClient, admin_headers: dict[str, str], scoring_headers: dict[str, str],  # noqa: F811
    database: Any, blob_store: Any, principal: Any, workspace_id: UUID,
) -> None:
    """DP-3 (a), item 6: the residual GLM's offset is the base model's linear predictor; the
    base model's fit and inputs travel in the Bundle under its own ref, and the value equals
    `/predict`'s for the residual model."""
    loop = asyncio.get_event_loop()
    pair = loop.run_until_complete(_fitted_residual_pair(database, blob_store, workspace_id))
    loop.run_until_complete(_approve(database, pair.base_id))
    residual_ref = loop.run_until_complete(_approve(database, pair.residual_id))
    row = {"area": "urban", "exposure_years": 1.0, "resid_flag": 1.0}
    algorithm = _algorithm(
        residual_ref,
        {"area": "area", "exposure_years": "exposure_years", "resid_flag": "resid_flag"},
    )
    algorithm["input_contract"].append(
        {"name": "resid_flag", "type": "decimal", "nullable": False}
    )
    algorithm["steps"].insert(
        2,
        {"step_id": "s_flag", "type": "input", "label": "Flag", "input_name": "resid_flag",
         "on_missing": "error", "produces": "resid_flag"},
    )
    algorithm["steps"][3]["consumes"] = ["area", "exposure_years", "resid_flag"]
    register_rating_handlers()
    assert client.post(
        "/api/v1/rating-algorithms", json=algorithm, headers=admin_headers
    ).status_code == 201
    version = loop.run_until_complete(
        _insert_version(
            database, workspace_id, principal.id, algorithm_ref="rating_algorithm:glm-score@1",
            pins={"rate_tables": [], "models": [residual_ref], "reference_tables": [],
                  "custom_objectives": []},
            slug="glm-rv",
        )
    )
    job = _run_compile_job(client, admin_headers, database, blob_store, version.id)
    assert job.status is JobStatus.SUCCEEDED, job.error
    bundle = Bundle.model_validate_json(_read_blob(database, blob_store, job.result["ref"]))
    assert pair.ref in bundle.resolved_payloads  # the source model, under its own ref

    async def _expected() -> float:
        async with database.session() as session:
            prediction = await prediction_service.predict_rows(
                session, workspace_id=workspace_id, actor=pair.actor,
                model_id=pair.residual_id, rows=[row], blob_store=blob_store,
            )
        return float(prediction.rows[0].expected)

    expected = loop.run_until_complete(_expected())
    response = client.post(
        SCORE_URL,
        json={
            "purpose": "new_business", "quoted_at": "2026-10-10T09:00:00Z",
            "effective_date": "2026-10-11", "inputs": row,
            "options": {"rating_version_ref": "rating_version:glm-rv@1"},
        },
        headers=scoring_headers,
    )
    assert response.status_code == 200, response.text
    assert float(response.json()["outputs"]["risk_out"]) == pytest.approx(expected, rel=1e-9)
