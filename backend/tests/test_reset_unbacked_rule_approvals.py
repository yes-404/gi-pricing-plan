"""`scripts/reset-unbacked-rule-approvals.py` resets an approval nothing backs, audited.

FD-1356 follow-on 2, RL-1407 DP-6 (b), PL-1408 Task 7 Step 3 (Acceptance 13). The script
returns every non-built-in `approved` rule that has no `approved` approval request to
`review`, writing one `validation_rule.approval_reset` Audit Event per row through
`audit.record`, and leaves a built-in or a rule with an approved request alone.

The test database is shared by every test, so a count over the whole database is not the
test's to assert: each assertion names the rows and workspaces this test created.
"""

from __future__ import annotations

import importlib.util
import pathlib
from typing import Any
from uuid import UUID

import pytest
from backend.tests.approved_rows import decided_request
from sqlalchemy import select

from app.db.models import AuditEventRow, ValidationRuleRow
from app.db.session import Database
from app.platform import audit
from app.platform.approvals import approval_decision
from model_schema import Severity, ValidationLayer, new_uuid7

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "reset-unbacked-rule-approvals.py"
ACTION = "validation_rule.approval_reset"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("gi_reset_unbacked", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rule(workspace_id: UUID, slug: str, *, builtin: bool = False) -> ValidationRuleRow:
    return ValidationRuleRow(
        workspace_id=workspace_id,
        slug=slug,
        version=1,
        layer=ValidationLayer.STRUCTURAL.value,
        check="not_null",
        severity=Severity.FAIL.value,
        body={
            "target": {"table": "t", "column": "a"},
            "params": {"columns": ["a"]},
            "scope": {},
            "tolerance": {},
            "message": "",
            "rationale": "",
        },
        status="approved",
        authored_by=new_uuid7(),
        approved_by=None if builtin else new_uuid7(),
        dry_run_report_id=None if builtin else new_uuid7(),
        builtin=builtin,
        catalogue_id="VR-STR-1" if builtin else None,
    )


async def _row(database: Database, workspace_id: UUID, slug: str) -> ValidationRuleRow:
    async with database.session() as session:
        return (
            await session.execute(
                select(ValidationRuleRow).where(
                    ValidationRuleRow.workspace_id == workspace_id, ValidationRuleRow.slug == slug
                )
            )
        ).scalar_one()


async def _events(database: Database, workspace_id: UUID) -> list[AuditEventRow]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(AuditEventRow)
                    .where(
                        AuditEventRow.workspace_id == workspace_id, AuditEventRow.action == ACTION
                    )
                    .order_by(AuditEventRow.sequence)
                )
            ).scalars()
        )


@pytest.fixture
async def population(database: Database) -> dict[str, tuple[UUID, str]]:
    """A and C in one workspace with B; D in a second, as the ruling's Acceptance sets out.

    A: approved, non-built-in, no request. B: approved built-in. C: approved with an
    approved request. D: another A, in the second workspace.
    """
    ws1, ws2 = new_uuid7(), new_uuid7()
    suffix = new_uuid7().hex[-8:]
    names = {key: f"{key}-{suffix}" for key in "abcd"}
    async with database.unit_of_work() as session:
        async with approval_decision(session):
            session.add(_rule(ws1, names["a"]))
            session.add(_rule(ws1, names["b"], builtin=True))
            session.add(_rule(ws2, names["d"]))
            await session.flush()
        await decided_request(
            session, workspace_id=ws1, artifact_type="validation_rule", slug=names["c"], version=1
        )
        async with approval_decision(session):
            session.add(_rule(ws1, names["c"]))
            await session.flush()
    return {
        "a": (ws1, names["a"]),
        "b": (ws1, names["b"]),
        "c": (ws1, names["c"]),
        "d": (ws2, names["d"]),
    }


@pytest.mark.req("FR-351")
async def test_the_reset_returns_an_unbacked_approval_to_review_with_one_event_each(
    database: Database, population: dict[str, tuple[UUID, str]]
) -> None:
    script = _load()
    result = await script.reset(database)

    for key in "ad":
        workspace_id, slug = population[key]
        row = await _row(database, workspace_id, slug)
        assert (row.status, row.approved_by) == ("review", None), key
        events = await _events(database, workspace_id)
        mine = [e for e in events if e.entity_ref == f"validation_rule:{slug}@1"]
        assert len(mine) == 1, key
        assert mine[0].before is not None
        assert mine[0].before["status"] == "approved"
        assert mine[0].after == {"status": "review", "approved_by": None}
        assert mine[0].actor["display"] == "fd-1356-reset"
        assert mine[0].actor["kind"] == "system"
        assert mine[0].source == "system"
        assert mine[0].justification == (
            "FD-1356 follow-on 2: approved outside the approval workflow; no approved "
            "approval request backs this approval (RL-1407 DP-6)."
        )
    assert result[population["a"][0]] >= 1
    assert result[population["d"][0]] >= 1


@pytest.mark.req("FR-351")
async def test_the_reset_leaves_a_built_in_and_a_backed_approval_alone(
    database: Database, population: dict[str, tuple[UUID, str]]
) -> None:
    await _load().reset(database)

    for key in "bc":
        workspace_id, slug = population[key]
        row = await _row(database, workspace_id, slug)
        assert row.status == "approved", f"{key} was reset"
        assert not [e for e in await _events(database, workspace_id) if slug in e.entity_ref], key


@pytest.mark.req("FR-351")
async def test_the_chain_of_every_workspace_written_still_verifies(
    database: Database, population: dict[str, tuple[UUID, str]]
) -> None:
    await _load().reset(database)

    for key in "ad":
        async with database.session() as session:
            assert await audit.verify_chain(session, population[key][0]) >= 1


@pytest.mark.req("FR-351")
async def test_a_second_run_resets_none_of_these_and_writes_no_event(
    database: Database, population: dict[str, tuple[UUID, str]]
) -> None:
    script = _load()
    await script.reset(database)
    before = {k: len(await _events(database, population[k][0])) for k in "ad"}

    second = await script.reset(database)

    assert population["a"][0] not in second
    assert population["d"][0] not in second
    assert {k: len(await _events(database, population[k][0])) for k in "ad"} == before
