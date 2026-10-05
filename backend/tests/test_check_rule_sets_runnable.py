"""`scripts/check-rule-sets-runnable.py`: the demo's pre-flight over a workspace's rule sets.

RL-1407 condition 2, PL-1408 Task 7 Step 3a (Acceptance 26). A workspace whose rule sets
hold a member that is not `approved` is refused with the run-time refusal's text, a
workspace with no rule set is refused as half-seeded, and a runnable one prints the count.
"""

from __future__ import annotations

import importlib.util
import io
import pathlib
from typing import Any
from uuid import UUID

import pytest
from backend.tests.approved_rows import add_approved
from sqlalchemy import select

from app.db.models import RoleAssignmentRow, RoleRow, ValidationRuleRow
from app.db.session import Database
from app.platform import datasets, rbac
from app.platform import validation_rules as rule_service
from model_schema import ActorKind, Principal, ScopeType, Severity, ValidationLayer, new_uuid7

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-rule-sets-runnable.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("gi_check_rule_sets", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def _analyst(database: Database, workspace_id: UUID) -> Principal:
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display="analyst@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == "analyst"
                )
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


async def _dataset_with_rule_set(
    database: Database, workspace_id: UUID, *, with_rule_set: bool = True
) -> tuple[str, UUID]:
    """A dataset, and (unless refused) a rule set of one approved rule; returns slug, rule id."""
    actor = await _analyst(database, workspace_id)
    slug = f"ds-{new_uuid7().hex[-8:]}"
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=slug
        )
        dataset_id = dataset.id
        rule = ValidationRuleRow(
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
            status="approved",
            authored_by=actor.id,
            approved_by=new_uuid7(),
            dry_run_report_id=new_uuid7(),
        )
        await add_approved(session, rule)
        rule_id = rule.id
        if with_rule_set:
            await rule_service.replace_rule_set(
                session,
                workspace_id=workspace_id,
                actor=actor,
                dataset_id=dataset_id,
                slug=str(dataset_id),
                members=[rule_service.RuleSetMember(rule_id=rule_id)],
            )
    return slug, rule_id


async def _run(database: Database, workspace_id: UUID) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    code = await _load().check(database, workspace_id, out=out, err=err)
    return code, out.getvalue(), err.getvalue()


@pytest.mark.req("FR-50")
async def test_a_workspace_whose_rule_sets_run_prints_the_count_and_exits_0(
    database: Database, workspace_id: UUID
) -> None:
    await _dataset_with_rule_set(database, workspace_id)

    code, out, err = await _run(database, workspace_id)

    assert (code, out, err) == (0, "rule sets runnable: 1\n", "")


@pytest.mark.req("FR-50")
async def test_a_member_in_review_is_refused_with_the_run_time_text(
    database: Database, workspace_id: UUID
) -> None:
    slug, rule_id = await _dataset_with_rule_set(database, workspace_id)
    async with database.unit_of_work() as session:
        rule = await session.get(ValidationRuleRow, rule_id)
        assert rule is not None
        rule.status = "review"
        rule.approved_by = None

    code, out, err = await _run(database, workspace_id)

    assert code == 1
    assert out == ""
    assert f"Not approved: {rule_id} ({rule.slug}@1, review)." in err
    assert f"PUT /api/v1/datasets/{slug}/rule-set" in err


@pytest.mark.req("FR-50")
async def test_a_workspace_with_no_rule_set_is_refused_as_half_seeded(
    database: Database, workspace_id: UUID
) -> None:
    await _dataset_with_rule_set(database, workspace_id, with_rule_set=False)

    code, out, err = await _run(database, workspace_id)

    assert code == 1
    assert out == ""
    assert err == (
        f"Workspace {workspace_id} has no rule set: the seed did not finish. Re-run the seed.\n"
    )
