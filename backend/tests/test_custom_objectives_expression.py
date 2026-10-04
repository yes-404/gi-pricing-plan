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
