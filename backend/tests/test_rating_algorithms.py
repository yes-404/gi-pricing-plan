"""Rating Algorithm API — save-time validation before persist (slice W9-2).

`POST /rating-algorithms` refuses an invalid graph and a broken boundary guard with the
named error; `GET /rating-algorithms/{slug}@{version}/diff` returns the structural diff
(FR-219).
"""

from __future__ import annotations

import asyncio

import pytest

from app.api.deps import DEV_PRINCIPAL_HEADER

#: The pre-edit `valid_algorithm` body, verbatim (SL-1345, RL-1329 §2 step 5): its clamp is on the
#: source of the payable's rung, so the placement check refuses it with LADDER_CLAMP_UNPLACEABLE.
PRE_EDIT_VALID_ALGORITHM: dict = {
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


def valid_algorithm() -> dict:
    """A consistent twelve-step graph whose expressions compile against the engine."""
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
            # The clamped name is the source of the last rung before `constraints`
            # (`office_premium`), and the payable reads a later name: a placeable clamp.
            {"step_id": "s_out_office", "type": "output", "label": "Office premium",
             "output_name": "office_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["office_premium_minor"]},
            {"step_id": "s_payable", "type": "expression", "label": "Payable premium value",
             "expr": "office_premium_minor * 1", "result_type": "money_minor",
             "consumes": ["office_premium_minor"], "produces": "payable_value"},
            {"step_id": "s_out", "type": "output", "label": "Payable premium",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable_value"]},
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


@pytest.mark.req("FR-274")
def test_a_masked_division_in_a_condition_is_refused_at_save_time(
    api_client, workspace_id, principal, grant
) -> None:
    """FD-1317 D2: a `??` "guard" on a constraint's condition (WK-1178 code slice)."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    body = valid_algorithm()
    for step in body["steps"]:
        if step["step_id"] == "s_minprem":
            step["condition"] = "((office_premium_minor / expense_factor) ?? 0) >= 100"
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


# --- WK-1250 Slice 1: the shape-refusal -> code mapping, characterised before its extraction ---


def _post(api_client, workspace_id, principal, grant, body):
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    return api_client.post(
        "/api/v1/rating-algorithms", json=body, headers=_headers(principal, workspace_id)
    )


@pytest.mark.req("FR-212")
def test_an_undefined_value_is_refused_with_rating_graph_unresolved_ref(
    api_client, workspace_id, principal, grant
) -> None:
    body = valid_algorithm()
    body["steps"][6]["consumes"] = ["risk_premium_minor", "expense_factor", "commission_factor"]
    response = _post(api_client, workspace_id, principal, grant, body)
    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "RATING_GRAPH_UNRESOLVED_REF"
    assert problem["title"] == "Rating graph references an undefined value"
    assert problem["detail"] == "Every consumed value is produced by a step (FR-212)."


@pytest.mark.req("FR-212")
def test_another_shape_refusal_is_validation_failed(
    api_client, workspace_id, principal, grant
) -> None:
    body = valid_algorithm()
    body["steps"][1]["step_id"] = body["steps"][0]["step_id"]
    response = _post(api_client, workspace_id, principal, grant, body)
    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED"
    assert problem["title"] == "Rating algorithm is invalid"
    assert "every step_id is unique (FR-215)" in problem["detail"]


@pytest.mark.req("FR-212")
def test_an_unknown_field_named_cycle_note_is_validation_failed(
    api_client, workspace_id, principal, grant
) -> None:
    body = valid_algorithm()
    body["cycle_note"] = "not a graph cycle"
    response = _post(api_client, workspace_id, principal, grant, body)
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-214")
def test_a_declared_output_without_an_output_step_is_validation_failed(
    api_client, workspace_id, principal, grant
) -> None:
    body = valid_algorithm()
    body["outputs"].append({"name": "extra_out", "type": "money_minor", "required": False})
    response = _post(api_client, workspace_id, principal, grant, body)
    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED"
    assert problem["title"] == "Rating algorithm is invalid"
    assert "has no output step (FR-214)" in problem["detail"]


@pytest.mark.req("FR-240")
def test_the_pre_edit_valid_algorithm_is_refused_at_save_time(
    api_client, workspace_id, principal, grant
) -> None:
    """SL-1345: the old shape (a clamp on the payable's own source) stays refused, with the
    code that names it, so the fixture edit did not make the check pass by weakening it."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    response = api_client.post(
        "/api/v1/rating-algorithms",
        json=PRE_EDIT_VALID_ALGORITHM,
        headers=_headers(principal, workspace_id),
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "LADDER_CLAMP_UNPLACEABLE"


# --- WK-673 Slice 3 (SL-1387): the FR-219 diff route is typed, and keeps its keys ---


@pytest.mark.req("FR-219")
def test_algorithm_diff_route_is_typed_and_keeps_its_keys(
    api_client, workspace_id, principal, grant
) -> None:
    schema = api_client.app.openapi()
    ok = schema["paths"]["/api/v1/rating-algorithms/{slug}@{version}/diff"]["get"]["responses"][
        "200"
    ]["content"]["application/json"]["schema"]
    assert ok == {"$ref": "#/components/schemas/AlgorithmDiff"}

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    for version in (1, 2):
        body = valid_algorithm()
        body["version"] = version
        created = api_client.post(
            "/api/v1/rating-algorithms", json=body, headers=_headers(principal, workspace_id)
        )
        assert created.status_code == 201, created.text
    diff = api_client.get(
        "/api/v1/rating-algorithms/motor-gb@2/diff",
        params={"against": 1},
        headers=_headers(principal, workspace_id),
    )
    assert diff.status_code == 200, diff.text
    assert set(diff.json()) == {
        # the six keys that exist before SL-1387, pinned by literal
        "added_steps",
        "removed_steps",
        "changed_steps",
        "repointed_tables",
        "input_contract_changed",
        "outputs_changed",
        # the two it adds
        "input_contract_deltas",
        "output_deltas",
    }


@pytest.mark.req("FR-212")
def test_the_save_route_publishes_typed_bodies(app) -> None:
    operation = app.openapi()["paths"]["/api/v1/rating-algorithms"]["post"]
    body = operation["requestBody"]["content"]["application/json"]["schema"]
    created = operation["responses"]["201"]["content"]["application/json"]["schema"]
    assert body == {"$ref": "#/components/schemas/RatingAlgorithmDraft"}
    assert created == {"$ref": "#/components/schemas/RatingAlgorithmSaved"}


@pytest.mark.req("FR-212")
def test_the_typed_save_body_keeps_the_graph_codes(
    api_client, workspace_id, principal, grant
) -> None:
    """DP-S2-1 condition 2: the codes, never the status alone."""
    cyclic = valid_algorithm()
    cyclic["steps"][6]["consumes"] = ["risk_premium_minor", "expense_factor", "cycle_val"]
    cyclic["steps"][7] = {
        "step_id": "s_minprem", "type": "constraint", "label": "Cycle",
        "condition": "true", "on_violation": "clamp", "reason_code": "CYCLE",
        "consumes": ["office_premium_minor"], "produces": "cycle_val",
    }
    unresolved = valid_algorithm()
    unresolved["steps"][6]["consumes"] = [
        "risk_premium_minor", "expense_factor", "commission_factor",
    ]
    assert _post(api_client, workspace_id, principal, grant, cyclic).json()["code"] == (
        "RATING_GRAPH_CYCLIC"
    )
    assert _post(api_client, workspace_id, principal, grant, unresolved).json()["code"] == (
        "RATING_GRAPH_UNRESOLVED_REF"
    )


@pytest.mark.req("FR-212")
def test_the_save_answers_the_typed_201(api_client, workspace_id, principal, grant) -> None:
    response = _post(api_client, workspace_id, principal, grant, valid_algorithm())
    assert response.status_code == 201, response.text
    assert set(response.json()) == {"id", "slug", "version"}


# --- the algorithm read by slug@version (RL-1475 T1/T2; Acceptance 3) ------------------------


@pytest.mark.req("FR-1530")
async def test_a_saved_algorithm_reads_back_by_slug_at_version(
    api_client, workspace_id, principal, grant
) -> None:
    from model_schema import RatingAlgorithm

    await grant("analyst")
    saved = api_client.post(
        "/api/v1/rating-algorithms",
        json=valid_algorithm(),
        headers=_headers(principal, workspace_id),
    )
    assert saved.status_code == 201, saved.text
    read = api_client.get(
        "/api/v1/rating-algorithms/motor-gb@1", headers=_headers(principal, workspace_id)
    )
    assert read.status_code == 200, read.text
    assert RatingAlgorithm.model_validate(read.json()) == RatingAlgorithm.model_validate(
        valid_algorithm()
    )


@pytest.mark.req("FR-1530")
async def test_an_unknown_algorithm_version_is_not_found(
    api_client, workspace_id, principal, grant
) -> None:
    await grant("analyst")
    read = api_client.get(
        "/api/v1/rating-algorithms/motor-gb@99", headers=_headers(principal, workspace_id)
    )
    assert read.status_code == 404, read.text
    assert read.json()["code"] == "NOT_FOUND"
    # The handler's own refusal, not the router's: an unrouted path also answers NOT_FOUND.
    assert read.json()["detail"] == "No rating algorithm motor-gb@99 in this workspace."


@pytest.mark.req("FR-1530")
async def test_another_workspaces_algorithm_is_not_found(
    api_client, workspace_id, principal, grant, database
) -> None:
    from app.platform import rating_algorithms as service
    from model_schema import new_uuid7

    await grant("analyst")
    await service.create_algorithm(database, new_uuid7(), principal.id, valid_algorithm())
    read = api_client.get(
        "/api/v1/rating-algorithms/motor-gb@1", headers=_headers(principal, workspace_id)
    )
    assert read.status_code == 404, read.text
    assert read.json()["code"] == "NOT_FOUND"
    assert read.json()["detail"] == "No rating algorithm motor-gb@1 in this workspace."


@pytest.mark.req("FR-1530")
async def test_the_algorithm_read_needs_rating_read(
    api_client, workspace_id, principal, membership
) -> None:
    await membership()
    read = api_client.get(
        "/api/v1/rating-algorithms/motor-gb@1", headers=_headers(principal, workspace_id)
    )
    assert read.status_code == 403, read.text


@pytest.mark.req("FR-1530")
def test_the_algorithm_read_publishes_rating_algorithm(app) -> None:
    operation = app.openapi()["paths"]["/api/v1/rating-algorithms/{slug}@{version}"]["get"]
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema == {"$ref": "#/components/schemas/RatingAlgorithm"}


# -- FD-1458 (PL-1464): the feature_map save check ----------------------------------------
#
# **Authored ahead of a database run** (items 13, 16, 21 need a fitted GLM): their
# red-by-cause is owed to the first gate-slot window (LG-9449).

from pathlib import Path  # noqa: E402

from backend.tests.test_model_jobs import (  # noqa: E402
    _actuary,
    _dataset,
    _factor,
    _spec,
    _split,
    _validated_version,
)

import app.platform.rating_algorithms as algorithms_module  # noqa: E402
from app.db.models import ModelRow  # noqa: E402
from app.platform import jobs as job_service  # noqa: E402
from app.platform import modelling as model_service  # noqa: E402
from app.worker.tasks import execute_job  # noqa: E402
from model_schema import JobKind, JobStatus  # noqa: E402
from pricing_core.modelling import factors as pricing_core_factors  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
#: A Factor slug that is NOT its source column, so "the slug" and "the raw column" differ.
FACTOR_SLUG = "area_group"
SOURCE_COLUMN = "area"


async def fitted_glm_with_distinct_slug(database, blob_store, workspace_id) -> str:
    """A GLM fitted through the real Job whose one Factor's slug (`area_group`) differs from
    its source column (`area`); returns its `model:slug@version` ref."""
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(database, blob_store, workspace_id, actor, dataset_id)
    factor = await _factor(database, workspace_id, actor, dataset_id, FACTOR_SLUG, SOURCE_COLUMN)
    split = await _split(database, blob_store, workspace_id, actor, version_id)
    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor,
            spec=_spec(version_id, (factor,), split_ref=split),
        )
        model_id = row.id
        job = await job_service.submit(
            session, JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(model_id)},
            actor, workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        fitted = await session.get(ModelRow, model_id)
    assert fitted is not None
    return f"model:{fitted.model_family_slug}@{fitted.version}"


def glm_algorithm(model_ref: str, feature_map: dict) -> dict:
    """`valid_algorithm` with its `model_call` re-pointed at `model_ref` under `feature_map`."""
    body = valid_algorithm()
    for step in body["steps"]:
        if step["type"] == "model_call":
            step["model_ref"] = model_ref
            step["feature_map"] = feature_map
    return body


@pytest.mark.req("FR-222")
async def test_a_feature_map_naming_a_raw_column_is_refused_at_save(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """Item 13 (DP-2 (b), DP-5 (ii) (a)): a raw dataset column is refused with its code and
    nothing is written; the control, the Factor slug, saves."""
    await grant("analyst")
    ref = await fitted_glm_with_distinct_slug(database, blob_store, workspace_id)
    headers = _headers(principal, workspace_id)

    refused = api_client.post(
        "/api/v1/rating-algorithms",
        json=glm_algorithm(ref, {"driver_age": SOURCE_COLUMN}), headers=headers,
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "MODEL_CALL_FEATURE_MAP_INVALID"
    detail = refused.json()["detail"]
    for named in ("s_rp", SOURCE_COLUMN, ref):
        assert named in detail
    absent = api_client.get("/api/v1/rating-algorithms/motor-gb@1", headers=headers)
    assert absent.status_code == 404

    saved = api_client.post(
        "/api/v1/rating-algorithms",
        json=glm_algorithm(ref, {"driver_age": FACTOR_SLUG}), headers=headers,
    )
    assert saved.status_code == 201, saved.text


@pytest.mark.req("FR-227")
async def test_a_stored_model_call_without_result_type_reads_back_as_decimal(
    api_client, workspace_id, principal, grant
) -> None:
    """Item 16: an algorithm stored before the field (`valid_algorithm` declares none) reads
    back through the service with its `model_call` step `decimal`. No migration is written:
    the algorithm is its JSON payload and the default is the model's."""
    await grant("analyst")
    headers = _headers(principal, workspace_id)
    assert api_client.post(
        "/api/v1/rating-algorithms", json=valid_algorithm(), headers=headers
    ).status_code == 201
    read = api_client.get("/api/v1/rating-algorithms/motor-gb@1", headers=headers)
    assert read.status_code == 200, read.text
    call = next(s for s in read.json()["steps"] if s["type"] == "model_call")
    assert call["result_type"] == "decimal"


@pytest.mark.req("FR-222")
async def test_the_feature_map_save_check_calls_the_one_required_inputs_helper(
    monkeypatch, api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """Item 21: the save check imports `required_model_inputs` and calls it once, with the
    fitted GLM's Factor slugs in spec order."""
    assert (
        algorithms_module.required_model_inputs is pricing_core_factors.required_model_inputs
    )
    await grant("analyst")
    ref = await fitted_glm_with_distinct_slug(database, blob_store, workspace_id)
    calls: list[tuple[str, ...]] = []

    def spy(factors, feature_order):
        result = pricing_core_factors.required_model_inputs(factors, feature_order)
        calls.append(result)
        return result

    monkeypatch.setattr(algorithms_module, "required_model_inputs", spy)
    response = api_client.post(
        "/api/v1/rating-algorithms",
        json=glm_algorithm(ref, {"driver_age": FACTOR_SLUG}),
        headers=_headers(principal, workspace_id),
    )
    assert response.status_code == 201, response.text
    assert calls == [(FACTOR_SLUG,)]


@pytest.mark.req("FR-222")
def test_required_model_inputs_is_defined_once() -> None:
    roots = [*(REPO / "packages").glob("*/src"), REPO / "backend" / "src"]
    hits = sorted(
        path.relative_to(REPO).as_posix()
        for root in roots
        for path in root.rglob("*.py")
        if "def required_model_inputs(" in path.read_text(encoding="utf-8")
    )
    assert hits == ["packages/pricing-core/src/pricing_core/modelling/factors.py"]
