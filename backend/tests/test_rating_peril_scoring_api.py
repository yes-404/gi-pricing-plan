"""A-3 (PL-1465, SL-1466): a Peril Structure `model_call` over HTTP.

Two things: the save-time `feature_map` check reaches a `peril_structure_ref` step on both save
paths, against the UNION of the component models (item 16, `RL-1459` DP-A3-7 (a)), and a Rating
Version pinning an approved structure compiles and scores (item 11, FR-188, FR-191).

**Authored ahead of a database run** (the small-test rule bars Postgres): every test here needs
`GIP_TEST_DATABASE_URL`, and its red-by-cause is owed to the first gate-slot window (LG-1592).
The fixtures are A-1's and A-2's own (`test_peril_structure_approval.py`,
`test_rating_glm_model_call.py`), imported rather than rebuilt.
"""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID, uuid4

import pytest
from backend.tests.test_peril_structure_approval import (
    _approver,
    _decide,
    _in_review,
    _model_id,
    _set_model_status,
)
from backend.tests.test_peril_structures import _book, _burning_cost_peril, _structure
from backend.tests.test_rating_algorithms import _headers, valid_algorithm
from backend.tests.test_rating_glm_model_call import (
    ROW,
    SCORE_URL,
)
from backend.tests.test_rating_glm_model_call import (
    _algorithm as _glm_algorithm,
)
from backend.tests.test_rating_version_compile import (
    _insert_version,
    _read_blob,
    _run_compile_job,
)
from backend.tests.test_score import admin_headers, client, scoring_headers  # noqa: F401
from fastapi.testclient import TestClient

import app.platform.rating_algorithms as algorithms_module
from app.platform import prediction as prediction_service
from app.worker.rating_handlers import register_rating_handlers
from model_schema import JobStatus, ModelStatus
from pricing_core.rating.compile import Bundle

_LOOP = asyncio.get_event_loop


async def _structure_over_a_burning_cost_model(
    database: Any, blob_store: Any, workspace_id: UUID
) -> tuple[str, str, UUID, UUID]:
    """A one-peril structure in `review` over an approved burning-cost model: its ref, the
    component's ref, the component's model id and the approval request that holds it."""
    actor, version_id, area, split = await _book(database, blob_store, workspace_id)
    peril = await _burning_cost_peril(
        database, blob_store, workspace_id, actor, version_id, area, split
    )
    component = str(peril.burning_cost_model)
    model_id = await _model_id(database, component)
    await _set_model_status(database, model_id, ModelStatus.APPROVED)
    slug = f"ps-{uuid4().hex[-6:]}"
    _, request_id = await _in_review(database, blob_store, workspace_id, actor, [peril], slug)
    return f"peril_structure:{slug}@1", component, model_id, request_id


def _peril_algorithm(structure_ref: str, feature_map: dict[str, str]) -> dict[str, Any]:
    """`valid_algorithm` with its `model_call` re-pointed at a structure under `feature_map`."""
    body = valid_algorithm()
    for step in body["steps"]:
        if step["type"] == "model_call":
            step.pop("model_ref", None)
            step["peril_structure_ref"] = structure_ref
            step["feature_map"] = feature_map
    return body


async def _accepted(database: Any, workspace_id: UUID, structure_ref: str) -> set[str]:
    """What the union of the structure's components accepts: the control's source of truth."""
    from model_schema import ArtifactRef

    async with database.session() as session:
        accepted = await algorithms_module._accepted_by_a_component(
            session, workspace_id, ArtifactRef.model_validate(structure_ref)
        )
    assert accepted, "the fixture's component accepts at least its own Factor slug"
    return accepted


@pytest.mark.req("FR-222", "FR-188")
async def test_a_peril_feature_map_naming_nothing_a_component_accepts_is_refused_at_save(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """Item 16: a value no component accepts answers 422 `MODEL_CALL_FEATURE_MAP_INVALID`,
    the detail names the step, the value and the structure, and no row is written. The
    control, a value some component accepts, saves 201. Red first: after A-2 the same map
    saves 201 (R4 skipped the step)."""
    await grant("analyst")
    structure_ref, *_ = await _structure_over_a_burning_cost_model(
        database, blob_store, workspace_id
    )
    headers = _headers(principal, workspace_id)
    accepted = sorted(await _accepted(database, workspace_id, structure_ref))

    refused = api_client.post(
        "/api/v1/rating-algorithms",
        json=_peril_algorithm(structure_ref, {"driver_age": "not_a_feature_anywhere"}),
        headers=headers,
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "MODEL_CALL_FEATURE_MAP_INVALID"
    detail = refused.json()["detail"]
    for named in ("s_rp", "not_a_feature_anywhere", structure_ref):
        assert named in detail
    absent = api_client.get("/api/v1/rating-algorithms/motor-gb@1", headers=headers)
    assert absent.status_code == 404

    saved = api_client.post(
        "/api/v1/rating-algorithms",
        json=_peril_algorithm(structure_ref, {"driver_age": accepted[0]}),
        headers=headers,
    )
    assert saved.status_code == 201, saved.text


@pytest.mark.req("FR-222")
async def test_the_sub_graph_save_path_checks_a_peril_feature_map_too(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """Item 16, second save path: one function, called from both (A-2 item 18). The sub-graph
    body is the one `test_sub_graphs_api.py` posts for A-2's refusal, re-pointed at a
    structure."""
    from backend.tests.test_sub_graphs_api import _model_call_body

    await grant("analyst")
    structure_ref, *_ = await _structure_over_a_burning_cost_model(
        database, blob_store, workspace_id
    )
    body = _model_call_body("model:placeholder@1", {"area": "not_a_feature"})
    step = body["steps"][0]
    step.pop("model_ref")
    step["peril_structure_ref"] = structure_ref
    refused = api_client.post(
        "/api/v1/sub-graphs",
        json={"slug": "risk-call", **body},
        headers=_headers(principal, workspace_id),
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "MODEL_CALL_FEATURE_MAP_INVALID"


@pytest.mark.req("FR-188", "FR-191", "FR-240")
def test_a_rating_version_pinning_an_approved_peril_structure_compiles_and_scores(
    client: TestClient,  # noqa: F811
    admin_headers: dict[str, str],  # noqa: F811
    scoring_headers: dict[str, str],  # noqa: F811
    database: Any, blob_store: Any, principal: Any, workspace_id: UUID, grant: Any,
) -> None:
    """Item 11: a structure approved through A-1's path, a Rating Version pinning it, a compile
    Job `succeeded` and `POST /api/v1/score` returning the burning-cost model's own prediction
    (a one-peril structure with no large-loss treatment is that prediction). Red before this
    slice by cause: the score answers the `MODEL_CALL_FAILED` path, never a value."""
    register_rating_handlers()
    loop = _LOOP()
    structure_ref, _, model_id, request_id = loop.run_until_complete(
        _structure_over_a_burning_cost_model(database, blob_store, workspace_id)
    )
    approver = loop.run_until_complete(_approver(grant, workspace_id))
    assert _decide(client, request_id, approver).status_code == 200

    # The component is a log-exposure GLM: its offset column travels in the `feature_map` too
    # (`PL-1464` DP-2 (b)), or the scorer reports `MODEL_OFFSET_MISSING`.
    body = _glm_algorithm(
        "model:placeholder@1", {"area": "area", "exposure_years": "exposure_years"}
    )
    for step in body["steps"]:
        if step["type"] == "model_call":
            step.pop("model_ref")
            step["peril_structure_ref"] = structure_ref
    created = client.post("/api/v1/rating-algorithms", json=body, headers=admin_headers)
    assert created.status_code == 201, created.text
    row = loop.run_until_complete(
        _insert_version(
            database, workspace_id, principal.id, algorithm_ref="rating_algorithm:glm-score@1",
            pins={"rate_tables": [], "models": [structure_ref], "reference_tables": [],
                  "custom_objectives": []},
            slug="peril-rv",
        )
    )
    job = _run_compile_job(client, admin_headers, database, blob_store, row.id)
    assert job.status is JobStatus.SUCCEEDED, job.error
    bundle = Bundle.model_validate_json(_read_blob(database, blob_store, job.result["ref"]))
    assert structure_ref in bundle.resolved_payloads

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
            "options": {"rating_version_ref": "rating_version:peril-rv@1"},
        },
        headers=scoring_headers,
    )
    assert response.status_code == 200, response.text
    assert float(response.json()["outputs"]["risk_out"]) == pytest.approx(expected, rel=1e-9)


@pytest.mark.req("FR-188", "NFR-499")
def test_a_stored_structure_that_no_longer_validates_fails_the_compile_job_input_free(
    client: TestClient,  # noqa: F811
    admin_headers: dict[str, str],  # noqa: F811
    database: Any, blob_store: Any, principal: Any, workspace_id: UUID,
) -> None:
    """Row 3 (b'), backend level: a pinned structure whose stored row a direct `UPDATE` broke
    fails the compile Job as `BUNDLE_COMPILE_FAILED` (FD 9952 row 1), and the stored error
    carries no value from the row.

    `to_structure` re-validates the row on the way out (the resolver's boundary, before
    `compile_bundle` sees a payload), so `compile.py`'s own wrap is reached by a `pricing-core`
    caller with its own resolver (`test_rating_peril_scoring.py`); this test pins the Job path.
    """
    from sqlalchemy import update

    from app.db.models import PerilStructureRow

    register_rating_handlers()
    loop = _LOOP()
    async def _draft_structure() -> str:
        # A `draft` structure has no reconciliation, so the composition is still editable
        # (a reconciled one is frozen by trigger, 02 FR-MODEL-60).
        actor, version_id, area, split = await _book(database, blob_store, workspace_id)
        peril = await _burning_cost_peril(
            database, blob_store, workspace_id, actor, version_id, area, split
        )
        structure = await _structure(database, workspace_id, actor, [peril])
        return f"peril_structure:{structure.slug}@{structure.version}"

    structure_ref = loop.run_until_complete(_draft_structure())
    body = _glm_algorithm(
        "model:placeholder@1", {"area": "area", "exposure_years": "exposure_years"}
    )
    for step in body["steps"]:
        if step["type"] == "model_call":
            step.pop("model_ref")
            step["peril_structure_ref"] = structure_ref
    assert client.post(
        "/api/v1/rating-algorithms", json=body, headers=admin_headers
    ).status_code == 201
    sentinel = "SENTINEL-5e2b"

    async def _break() -> None:
        slug, version = structure_ref.split(":", 1)[1].rsplit("@", 1)
        async with database.unit_of_work() as session:
            await session.execute(
                update(PerilStructureRow)
                .where(PerilStructureRow.slug == slug, PerilStructureRow.version == int(version))
                .values(perils=[{"peril": sentinel, "method": "no_such_method"}])
            )

    loop.run_until_complete(_break())
    row = loop.run_until_complete(
        _insert_version(
            database, workspace_id, principal.id, algorithm_ref="rating_algorithm:glm-score@1",
            pins={"rate_tables": [], "models": [structure_ref], "reference_tables": [],
                  "custom_objectives": []},
            slug="peril-broken-rv",
        )
    )
    job = _run_compile_job(client, admin_headers, database, blob_store, row.id)
    assert job.status is JobStatus.FAILED
    assert job.error["code"] == "BUNDLE_COMPILE_FAILED"
    assert sentinel not in str(job.error)
