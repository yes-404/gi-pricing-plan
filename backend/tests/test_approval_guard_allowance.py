"""The allowance sites write `approved` through the flag, and only while they enter it.

WK-674 Slice 2a, PL-1303 Acceptance 7; RL-1301 A.4.5. Each site is run for real
(`validation_rules.seed_builtin_rules`, `replace_rule_set`); with its entry
removed — `approval_decision()` made a no-op — the same write is refused by the database.
`examples/fremtpl2/seed.py` imports the name directly and is held by the static literal in
`test_approval_guard_static.py`.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

from app.db.models import RoleAssignmentRow, RoleRow, ValidationRuleRow
from app.db.session import Database
from app.platform import approvals, datasets, rbac
from app.platform import validation_rules as rule_service
from model_schema import ActorKind, Principal, ScopeType, Severity, ValidationLayer, new_uuid7

GUARD_SQLSTATE = "GP001"


async def _principal_with_role(database: Database, workspace_id: Any, slug: str) -> Principal:
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display=f"{slug}@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role = (
            await session.execute(
                select(RoleRow).where(RoleRow.workspace_id == workspace_id, RoleRow.slug == slug)
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=user.id,
                role_id=role.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )
    return user


def _rule(workspace_id: Any, author: Any, *, status: str, **extra: Any) -> ValidationRuleRow:
    return ValidationRuleRow(
        workspace_id=workspace_id,
        slug=f"r-{new_uuid7().hex[-6:]}",
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
        status=status,
        authored_by=author,
        **extra,
    )


@asynccontextmanager
async def _no_flag(session: Any) -> Any:
    yield


async def _outcome(work: Any) -> str | None:
    """`None` when the write succeeded, else the SQLSTATE that refused it."""
    try:
        await work()
    except DBAPIError as exc:
        return str(getattr(exc.orig, "sqlstate", None))
    return None


@pytest.fixture(params=[True, False], ids=["entered", "entry-removed"])
def entered(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Returns `arm()`: call it after the setup that itself needs the flag."""

    def arm() -> bool:
        if not request.param:
            monkeypatch.setattr(approvals, "approval_decision", _no_flag)
        return bool(request.param)

    return arm


def _expect(outcome: str | None, entered: bool, site: str) -> None:
    if entered:
        assert outcome is None, f"{site}: the sanctioned site was refused ({outcome})"
    else:
        assert outcome == GUARD_SQLSTATE, f"{site}: with its entry removed it must be refused"


@pytest.mark.req("FR-351")
async def test_seed_builtin_rules_writes_approved_only_through_its_entry(
    database: Database, workspace_id: Any, entered: Any
) -> None:
    author = new_uuid7()
    is_entered = entered()

    async def work() -> None:
        async with database.unit_of_work() as session:
            created = await rule_service.seed_builtin_rules(
                session, workspace_id, authored_by=author
            )
            assert created

    _expect(await _outcome(work), is_entered, "seed_builtin_rules")


@pytest.mark.req("FR-351")
async def test_replace_rule_set_writes_approved_only_through_its_entry(
    database: Database, workspace_id: Any, entered: Any
) -> None:
    actor = await _principal_with_role(database, workspace_id, "analyst")
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        dataset_id = dataset.id
        async with approvals.approval_decision(session):
            rule = _rule(
                workspace_id,
                actor.id,
                status="approved",
                approved_by=new_uuid7(),
                dry_run_report_id=new_uuid7(),
            )
            session.add(rule)
            await session.flush()
        rule_id = rule.id
    is_entered = entered()

    async def work() -> None:
        async with database.unit_of_work() as session:
            await rule_service.replace_rule_set(
                session,
                workspace_id=workspace_id,
                actor=actor,
                dataset_id=dataset_id,
                slug=str(dataset_id),
                members=[rule_service.RuleSetMember(rule_id=rule_id)],
            )

    _expect(await _outcome(work), is_entered, "replace_rule_set")
