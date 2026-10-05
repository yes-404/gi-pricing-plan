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
from backend.tests.test_data_jobs import CLEAN, _ingest
from backend.tests.test_validation_rule_approval import _dataset_with_set
from sqlalchemy import func, select

from app.db.models import (
    AuditEventRow,
    DatasetVersionRow,
    JobRow,
    ValidationReportRow,
    ValidationRuleRow,
)
from app.db.session import Database
from app.platform import audit
from app.platform import jobs as job_service
from app.platform.approvals import approval_decision
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.tasks import execute_job
from model_schema import (
    JobKind,
    JobStatus,
    Principal,
    Severity,
    ValidationLayer,
    new_uuid7,
)

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


@pytest.mark.req("FR-50")
async def test_a_rule_reset_by_dp6_does_not_execute_in_its_sets_next_run(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    principal: Principal,
    grant,
) -> None:
    """FD-1414, RL-1407 DP-6: the reset takes a rule out of its set's next run.

    Held by the handler's call to `rule_set_to_run` rather than `rule_set_for`: the read
    shows a member in `review`, only the run refuses it.
    """
    register_data_handlers()
    await grant("analyst")
    rule = _rule(workspace_id, f"a-{new_uuid7().hex[-8:]}")
    rule.layer = ValidationLayer.ACTUARIAL_SANITY.value
    rule.check = "range"
    rule.body = {
        **rule.body,
        "target": {"table": "policy_exposure", "column": "exposure_years"},
        "params": {"min_inclusive": 0, "key_columns": ["policy_id"]},
    }
    async with database.unit_of_work() as session:
        async with approval_decision(session):
            session.add(rule)
            await session.flush()
        rule_id = rule.id
    slug, dataset_id = await _dataset_with_set(database, workspace_id, principal, [rule_id])
    version = await _ingest(database, blob_store, workspace_id, principal, dataset_id, CLEAN)

    async def _state() -> tuple[str, int]:
        async with database.session() as session:
            row = await session.get(DatasetVersionRow, version)
            assert row is not None
            reports = (
                await session.execute(
                    select(func.count())
                    .select_from(ValidationReportRow)
                    .where(ValidationReportRow.dataset_version_id == version)
                )
            ).scalar_one()
            return row.status, reports

    before = await _state()
    await _load().reset(database)
    assert (await _row(database, workspace_id, rule.slug)).status == "review"

    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.DATASET_VALIDATE,
            {
                "workspace_id": str(workspace_id),
                "actor": principal.model_dump(mode="json"),
                "dataset_version_id": str(version),
            },
            principal,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is not JobStatus.SUCCEEDED
    async with database.session() as session:
        stored = await session.get(JobRow, job.id)
    assert stored is not None
    assert stored.error is not None
    assert stored.error["code"] == "RULE_NOT_APPROVED"
    # RL-1407 (#1070 @24ea2130), the maintainer's condition 1, rendered for rule A.
    assert stored.error["message"] == (
        f"Not approved: {rule_id} ({rule.slug}@1, review). A rule set runs only approved "
        "rules (`01` FR-50). The way back, for each rule: attach a new dry run "
        "(POST /api/v1/validation-rules/{id}/dry-run), then submit an approval request "
        "(POST /api/v1/validation-rules/{id}/submit for a draft rule, "
        "POST /api/v1/approval-requests for a rule in review), and have an approver "
        f"decide it. Or replace the rule set without it (PUT /api/v1/datasets/{slug}/rule-set)."
    )
    assert await _state() == before
