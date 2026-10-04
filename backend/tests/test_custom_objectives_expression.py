"""The `expression` Custom Objective through the platform (`02` §4.6, FR-144, FR-150, WK-690 S3).

Task 2 of `PL-1382` owns the storage tests (`-k storage`): the table stores the `expression`
arm, keeps its definition immutable, and lets `derived` be written exactly once, from NULL,
while the objective is a `draft`. Later tasks of the slice append their own sections here.

The rows are inserted with SQL, not through the ORM row: the constraint and the trigger are
the layer under test, and a test that reached them through the application's own writer
would pass whenever the writer and the model agreed with each other.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.db.models import CustomObjectiveRow
from app.db.session import Database
from model_schema import new_uuid7

_APPLICABILITY = {
    "responses": ["burning_cost"],
    "backends": ["xgboost"],
    "offset_required": False,
    "y_domain": {"min_inclusive": 0.0, "max_inclusive": None},
}
_PARAMETERS = [{"name": "w_under", "type": "float", "default": 2.0, "min": 1.0, "max": 10.0}]
_DERIVED = {
    "gradient": "2*w*(exp(f) - y)*exp(f)",
    "hessian": "2*w*(2*exp(f) - y)*exp(f)",
    "derivation_tool": "sympy",
    "derivation_version": "1.14.0",
    "derived_at": "2026-08-14T11:02:00+00:00",
}

_INSERT = text(
    "INSERT INTO custom_objectives (id, workspace_id, slug, version, status, kind, template, "
    "params, applicability, hessian_strategy, hessian_min, certificate_id, "
    "bound_symbols, parameters, loss, derived) "
    "VALUES (:id, :workspace_id, :slug, 1, :status, :kind, :template, '{}'::jsonb, "
    "CAST(:applicability AS jsonb), 'clip_to_min', 1e-6, :certificate_id, "
    "CAST(:bound_symbols AS jsonb), CAST(:parameters AS jsonb), :loss, CAST(:derived AS jsonb))"
)


async def _insert(database: Database, workspace_id: Any, **over: Any) -> Any:
    """Insert a row, an `expression` draft unless `over` says otherwise; return its id."""
    values: dict[str, Any] = {
        "id": new_uuid7(),
        "workspace_id": workspace_id,
        "slug": f"expr-{new_uuid7().hex[-8:]}",
        "status": "draft",
        "kind": "expression",
        "template": None,
        "certificate_id": None,
        "bound_symbols": json.dumps(["y", "f", "w"]),
        "parameters": json.dumps(_PARAMETERS),
        "loss": "w * (y - exp(f)) ** 2",
        "derived": None,
    }
    values.update(over)
    values["applicability"] = json.dumps(_APPLICABILITY)
    async with database.unit_of_work() as session:
        await session.execute(_INSERT, values)
    return values["id"]


async def _refused(database: Database, sql: str, **params: Any) -> str:
    """Run `sql` expecting the database to refuse it; return the refusal's text."""
    with pytest.raises((IntegrityError, DBAPIError)) as refused:
        async with database.unit_of_work() as session:
            await session.execute(text(sql), params)
    return str(refused.value)


@pytest.mark.req("FR-144")
async def test_storage_an_expression_row_inserts_and_round_trips(
    database: Database, workspace_id
) -> None:
    row_id = await _insert(database, workspace_id, derived=json.dumps(_DERIVED))
    async with database.unit_of_work() as session:
        row = await session.get(CustomObjectiveRow, row_id)
    assert row is not None
    assert row.kind == "expression"
    assert row.template is None
    assert row.loss == "w * (y - exp(f)) ** 2"
    assert row.bound_symbols == ["y", "f", "w"]
    assert row.parameters == _PARAMETERS
    assert row.derived == _DERIVED


@pytest.mark.req("FR-144")
async def test_storage_a_template_row_without_a_template_is_still_refused(
    database: Database, workspace_id
) -> None:
    with pytest.raises(IntegrityError) as refused:
        await _insert(
            database,
            workspace_id,
            kind="template",
            template=None,
            bound_symbols=None,
            parameters=None,
            loss=None,
        )
    assert "custom_objective_fields_follow_kind" in str(refused.value)


@pytest.mark.req("FR-144")
@pytest.mark.parametrize(
    "over",
    [
        {"kind": "template", "template": "poisson"},  # a template carrying a loss
        {"template": "poisson"},  # an expression naming a template
        {"loss": None},  # an expression with no loss
    ],
    ids=["template-with-loss", "expression-with-template", "expression-without-loss"],
)
async def test_storage_a_row_mixing_the_two_arms_is_refused(
    database: Database, workspace_id, over: dict[str, Any]
) -> None:
    with pytest.raises(IntegrityError) as refused:
        await _insert(database, workspace_id, **over)
    assert "custom_objective_fields_follow_kind" in str(refused.value)


@pytest.mark.req("FR-163")
@pytest.mark.parametrize(
    "assignment",
    [
        "loss = 'y + f'",
        "parameters = '[]'::jsonb",
        "bound_symbols = '[\"y\"]'::jsonb",
    ],
    ids=["loss", "parameters", "bound_symbols"],
)
async def test_storage_an_expression_definition_cannot_be_rewritten(
    database: Database, workspace_id, assignment: str
) -> None:
    row_id = await _insert(database, workspace_id)
    message = await _refused(
        database, f"UPDATE custom_objectives SET {assignment} WHERE id = :id", id=row_id
    )
    assert "custom_objectives_definition_immutable" in message or "immutable" in message


@pytest.mark.req("FR-163")
async def test_storage_derived_is_written_once_from_null_while_draft(
    database: Database, workspace_id
) -> None:
    row_id = await _insert(database, workspace_id)
    derived = json.dumps(_DERIVED)
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE custom_objectives SET derived = CAST(:d AS jsonb) WHERE id = :id"),
            {"d": derived, "id": row_id},
        )
    message = await _refused(
        database,
        "UPDATE custom_objectives SET derived = '{}'::jsonb WHERE id = :id",
        id=row_id,
    )
    assert "derived" in message
    message = await _refused(
        database, "UPDATE custom_objectives SET derived = NULL WHERE id = :id", id=row_id
    )
    assert "derived" in message


@pytest.mark.req("FR-163")
async def test_storage_derived_cannot_be_first_written_after_the_draft(
    database: Database, workspace_id
) -> None:
    """A trigger that allowed NULL to a value would allow it after approval too."""
    row_id = await _insert(database, workspace_id, status="certified", certificate_id=new_uuid7())
    message = await _refused(
        database,
        "UPDATE custom_objectives SET derived = '{}'::jsonb WHERE id = :id",
        id=row_id,
    )
    assert "derived" in message


@pytest.mark.req("FR-163")
async def test_storage_the_lifecycle_of_an_expression_row_still_moves(
    database: Database, workspace_id
) -> None:
    row_id = await _insert(database, workspace_id)
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE custom_objectives SET status = 'deprecated' WHERE id = :id"),
            {"id": row_id},
        )


# -- Task 4: the flag made liftable; create and derive; the grammar refusal ----------------------
#
# `-k flag`, `-k derive` and `-k grammar`. The set-true cases are the red-first ones: at the
# base the refusal is unconditional, so the *unset* case passes there for the wrong reason.

_FLAG = "features.expression_objectives_enabled"
_LOSS = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
_EXAMPLE_PARAMETERS = [
    {"name": "w_under", "type": "float", "default": 2.0, "min": 1.0, "max": 10.0},
    {"name": "w_over", "type": "float", "default": 1.0, "min": 0.1, "max": 10.0},
]


def _expression_body(**over: Any) -> dict[str, Any]:
    """`02` §4.6's example as a create request: no `derived`, which the platform generates."""
    body: dict[str, Any] = {
        "slug": f"expr-{new_uuid7().hex[-8:]}",
        "kind": "expression",
        "bound_symbols": ["y", "f", "w"],
        "parameters": _EXAMPLE_PARAMETERS,
        "loss": _LOSS,
        "applicability": {
            "responses": ["burning_cost", "claim_severity"],
            "backends": ["xgboost", "lightgbm"],
            "offset_required": False,
            "y_domain": {"min_inclusive": 0},
        },
    }
    body.update(over)
    return body


async def _set_flag(database: Database, workspace_id: Any, value: bool) -> None:
    from app.platform import settings as settings_service
    from app.platform import workspaces

    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await settings_service.set_workspace_setting(session, workspace_id, _FLAG, value)


@pytest.fixture
async def author(database: Database, workspace_id: Any) -> dict[str, str]:
    """`model:fit` and `custom_objective:author`: the two permissions create and derive need."""
    from backend.tests.test_custom_objectives import _principal_holding

    return await _principal_holding(
        database, workspace_id, {"custom_objective:author", "model:fit", "model:read"}
    )


@pytest.mark.req("FR-150")
async def test_flag_unset_refuses_create_and_derive_by_name(api_client: Any, author: Any) -> None:
    """An unset key resolves to the definition's default, `False` (FR-150)."""
    created = api_client.post("/api/v1/custom-objectives", json=_expression_body(), headers=author)
    derived = api_client.post(
        f"/api/v1/custom-objectives/{new_uuid7()}/derive", json={}, headers=author
    )
    for response in (created, derived):
        assert response.status_code == 409, response.text
        assert response.json()["code"] == "OBJECTIVE_KIND_NOT_ENABLED"


@pytest.mark.req("FR-150")
async def test_flag_false_refuses_create_and_derive_by_name(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    await _set_flag(database, workspace_id, False)
    created = api_client.post("/api/v1/custom-objectives", json=_expression_body(), headers=author)
    derived = api_client.post(
        f"/api/v1/custom-objectives/{new_uuid7()}/derive", json={}, headers=author
    )
    for response in (created, derived):
        assert response.status_code == 409, response.text
        assert response.json()["code"] == "OBJECTIVE_KIND_NOT_ENABLED"


@pytest.mark.req("FR-150")
async def test_flag_true_accepts_create_as_an_underived_draft(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    await _set_flag(database, workspace_id, True)
    response = api_client.post("/api/v1/custom-objectives", json=_expression_body(), headers=author)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["kind"] == "expression"
    assert body["status"] == "draft"
    assert body["template"] is None
    assert body["loss"] == _LOSS
    assert body["bound_symbols"] == ["y", "f", "w"]
    assert [p["name"] for p in body["parameters"]] == ["w_under", "w_over"]
    assert body["derived"] is None


async def _created(api_client: Any, author: Any, database: Database, workspace_id: Any) -> dict:
    await _set_flag(database, workspace_id, True)
    response = api_client.post("/api/v1/custom-objectives", json=_expression_body(), headers=author)
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.req("FR-144")
async def test_derive_stores_what_pricing_core_derives_stamped_and_audited(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select

    from app.db.models import AuditEventRow
    from pricing_core.modelling.expression_objective import derive

    created = await _created(api_client, author, database, workspace_id)
    before = datetime.now(UTC)
    response = api_client.post(
        f"/api/v1/custom-objectives/{created['id']}/derive", json={}, headers=author
    )
    assert response.status_code == 200, response.text
    stored = response.json()["derived"]
    expected = derive(_LOSS, parameters=["w_under", "w_over"])
    assert stored["gradient"] == expected.gradient
    assert stored["hessian"] == expected.hessian
    assert stored["derivation_tool"] == "sympy"
    assert stored["derivation_version"] == expected.derivation_version
    stamped = datetime.fromisoformat(stored["derived_at"])
    assert before - timedelta(seconds=1) <= stamped <= datetime.now(UTC) + timedelta(seconds=1)

    async with database.session() as session:
        events = (
            await session.scalars(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "custom_objective.derived",
                )
            )
        ).all()
    assert len(events) == 1
    assert events[0].entity_ref == f"custom_objective:{created['slug']}@1"
    assert events[0].before["derived"] is None
    assert events[0].after["derived"]["gradient"] == expected.gradient


@pytest.mark.req("NFR-484")
async def test_derive_stores_the_installed_sympy_version(
    api_client: Any, author: Any, database: Database, workspace_id: Any, monkeypatch: Any
) -> None:
    """`RL-1289`'s rule carried to storage: the version is read when derive runs."""
    import sympy

    created = await _created(api_client, author, database, workspace_id)
    monkeypatch.setattr(sympy, "__version__", "9.9.9")
    response = api_client.post(
        f"/api/v1/custom-objectives/{created['id']}/derive", json={}, headers=author
    )
    assert response.status_code == 200, response.text
    assert response.json()["derived"]["derivation_version"] == "9.9.9"


@pytest.mark.req("FR-144")
async def test_derive_refuses_a_template_objective_and_a_second_derivation(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    await _set_flag(database, workspace_id, True)
    template = api_client.post(
        "/api/v1/custom-objectives",
        json={"slug": "tmpl-for-derive", "template": "poisson"},
        headers=author,
    )
    assert template.status_code == 201, template.text
    refused = api_client.post(
        f"/api/v1/custom-objectives/{template.json()['id']}/derive", json={}, headers=author
    )
    assert refused.status_code == 409, refused.text
    assert refused.json()["code"] == "VALIDATION_FAILED"

    expression = api_client.post(
        "/api/v1/custom-objectives", json=_expression_body(), headers=author
    ).json()
    url = f"/api/v1/custom-objectives/{expression['id']}/derive"
    assert api_client.post(url, json={}, headers=author).status_code == 200
    again = api_client.post(url, json={}, headers=author)
    assert again.status_code == 409, again.text
    assert again.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-145")
async def test_grammar_violation_is_422_with_the_position_in_errors(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    from pricing_core.data.expressions import ExpressionError, GrammarProfile, parse_expression

    await _set_flag(database, workspace_id, True)
    loss = "w * numpy.where(y, f, w)"
    with pytest.raises(ExpressionError) as parsed:
        parse_expression(loss, GrammarProfile.OBJECTIVE, symbols=frozenset({"y", "f", "w"}))
    line, column = parsed.value.lineno, parsed.value.col_offset + 1

    response = api_client.post(
        "/api/v1/custom-objectives",
        json=_expression_body(loss=loss, parameters=[]),
        headers=author,
    )
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["code"] == "OBJECTIVE_GRAMMAR_VIOLATION"
    assert "position" not in body
    assert body["errors"][0]["field"] == "loss"
    assert body["errors"][0]["code"] == "OBJECTIVE_GRAMMAR_VIOLATION"
    assert body["errors"][0]["message"].startswith(f"line {line}, column {column}:")


@pytest.mark.req("FR-145")
async def test_grammar_violation_covers_text_that_does_not_parse(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    await _set_flag(database, workspace_id, True)
    response = api_client.post(
        "/api/v1/custom-objectives",
        json=_expression_body(loss="w * (y - ", parameters=[]),
        headers=author,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "OBJECTIVE_GRAMMAR_VIOLATION"
    assert response.json()["errors"][0]["message"].startswith("line 1, column ")


@pytest.mark.req("FR-153")
async def test_an_expression_objective_without_applicability_is_refused_422(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    """RL-1410 R3: an `expression` has no template to default `applicability` from."""
    await _set_flag(database, workspace_id, True)
    body = _expression_body()
    del body["applicability"]
    response = api_client.post("/api/v1/custom-objectives", json=body, headers=author)
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"
    listed = api_client.get(f"/api/v1/custom-objectives?slug={body['slug']}", headers=author)
    assert listed.status_code == 200, listed.text
    assert [row for row in listed.json()["items"] if row["slug"] == body["slug"]] == []


@pytest.mark.req("FR-145")
async def test_grammar_violation_is_not_raised_for_a_valid_loss(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    """The control: the same route and caller, a loss inside the grammar, is 201."""
    created = await _created(api_client, author, database, workspace_id)
    assert created["loss"] == _LOSS


# -- certification (Task 5, `-k certify`) ---------------------------------------------------


async def _derived(api_client: Any, author: Any, database: Database, workspace_id: Any) -> dict:
    created = await _created(api_client, author, database, workspace_id)
    response = api_client.post(
        f"/api/v1/custom-objectives/{created['id']}/derive", json={}, headers=author
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.req("FR-146")
async def test_certify_refuses_an_underived_expression_before_a_job_exists(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    """`RL-1362` DP-S3-3 (2): 409 `VALIDATION_FAILED` naming `/derive`, and no job row."""
    from sqlalchemy import func, select

    from app.db.models import JobRow

    created = await _created(api_client, author, database, workspace_id)
    response = api_client.post(
        f"/api/v1/custom-objectives/{created['id']}/certify", json={}, headers=author
    )
    assert response.status_code == 409, response.text
    body = response.json()
    assert body["code"] == "VALIDATION_FAILED"
    assert "POST /api/v1/custom-objectives/{id}/derive" in body["detail"]
    async with database.session() as session:
        queued = await session.scalar(
            select(func.count())
            .select_from(JobRow)
            .where(JobRow.workspace_id == workspace_id, JobRow.kind == "objective.certify")
        )
    assert queued == 0


@pytest.mark.req("FR-146")
async def test_certify_runs_a_derived_expression_as_the_existing_job(
    api_client: Any, author: Any, database: Database, workspace_id: Any, blob_store: Any
) -> None:
    """Acceptance 7: 202, then a certificate over the symbolic battery."""
    from uuid import UUID

    from app.platform import objectives as service
    from app.worker.model_handlers import register_model_handlers
    from app.worker.tasks import execute_job
    from model_schema import (
        OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC,
        CertificateOutcome,
        CheckStatus,
        JobStatus,
    )

    register_model_handlers()
    derived = await _derived(api_client, author, database, workspace_id)
    response = api_client.post(
        f"/api/v1/custom-objectives/{derived['id']}/certify", json={}, headers=author
    )
    assert response.status_code == 202, response.text
    job_id = UUID(response.json()["id"])
    assert await execute_job(database, job_id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        certificate = await service.load_certificate(
            session, workspace_id=workspace_id, objective_id=UUID(derived["id"])
        )
    result = certificate.result
    assert tuple(check.name for check in result.checks) == OBJECTIVE_CERTIFICATE_CHECKS_SYMBOLIC
    assert result.overall is CertificateOutcome.CERTIFIED_WITH_FINDINGS
    convexity = next(check for check in result.checks if check.name == "convexity")
    assert convexity.status is CheckStatus.VIOLATED
    assert result.library_versions["sympy"]
