"""FR-57: the reference-pin seam — pinned, None, and pinned-but-unprofiled.

The read sits at `backend/src/app/worker/data_handlers.py:249`: a rule set may pin a
`reference_dataset_version_id`, and the distributional rules compare against that version's
profile. The requirement is "never inferred" — no test set the field until this one — so
this covers all three paths: the pinned profile resolves and the rule runs; `None` skips
the distributional rules; a pinned version with no profile falls back to `None` and skips
rather than failing the run (FR-54's preference, not a hard requirement).
"""

from __future__ import annotations

from uuid import UUID

import pytest
from sqlalchemy import select

from app.db.models import DatasetVersionRow, RoleAssignmentRow, RoleRow, ValidationRuleRow
from app.db.session import Database
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import rbac
from app.platform import validation as validation_service
from app.platform import validation_rules as rule_service
from app.platform.blobs import BlobStore
from app.worker.data_handlers import register_data_handlers
from app.worker.tasks import execute_job
from model_schema import (
    ActorKind,
    JobKind,
    JobStatus,
    Principal,
    RuleOutcome,
    ScopeType,
    Severity,
    ValidationLayer,
    new_uuid7,
)

register_data_handlers()

_HEADER = b"Policy ID,Exposure Years,Claim Count,Claim Amount Minor,Vehicle Group,Driver Age\n"
_BOOK = _HEADER + b"P1,0.5,0,0,G1,30\nP2,0.5,1,250000,G2,40\nP3,1.0,0,0,G1,25\n"


async def _actor(database: Database, workspace_id: UUID, role: str) -> Principal:
    who = Principal(kind=ActorKind.USER, id=new_uuid7(), display=f"{role}@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role_row = (
            await session.execute(
                select(RoleRow).where(RoleRow.workspace_id == workspace_id, RoleRow.slug == role)
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=who.id,
                role_id=role_row.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )
    return who


async def _dataset(database: Database, workspace_id: UUID, actor: Principal) -> UUID:
    async with database.unit_of_work() as session:
        row = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=actor,
            slug=f"refpin-{new_uuid7().hex[-8:]}",
        )
        return row.id


async def _ingest(
    database: Database, blob_store: BlobStore, workspace_id: UUID, actor: Principal,
    dataset_id: UUID,
) -> UUID:
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, _BOOK, "text/csv")
        job = await job_service.submit(
            session, JobKind.DATASET_INGEST,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "dataset_id": str(dataset_id),
                "blob": ref.sha256,
                "filename": "book.csv",
                "recipe": [
                    {
                        "step": "cast",
                        "table": "policy_exposure",
                        "params": {
                            "columns": {
                                "exposure_years": "float",
                                "claim_count": "int",
                            }
                        },
                    }
                ],
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    async with database.session() as session:
        row = (
            await session.execute(
                select(DatasetVersionRow)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc())
            )
        ).scalars().first()
    assert row is not None
    return row.id


async def _validate(
    database: Database, blob_store: BlobStore, workspace_id: UUID, actor: Principal,
    version_id: UUID,
) -> None:
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session, JobKind.DATASET_VALIDATE,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "dataset_version_id": str(version_id)},
            actor, workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED


async def _psi_rule(database: Database, workspace_id: UUID, actor: Principal) -> tuple[UUID, str]:
    async with database.unit_of_work() as session:
        slug = f"psi-{new_uuid7().hex[-6:]}"
        rule = ValidationRuleRow(
            workspace_id=workspace_id, slug=slug, version=1,
            layer=ValidationLayer.DISTRIBUTIONAL.value, check="psi_column",
            severity=Severity.WARN.value,
            body={"target": {"table": "policy_exposure", "column": "vehicle_group"},
                  "params": {"warn_above": 0.10, "fail_above": 0.25},
                  "message": "", "rationale": ""},
            status="approved", authored_by=actor.id, approved_by=new_uuid7(),
            dry_run_report_id=new_uuid7(),
        )
        session.add(rule)
        await session.flush()
        return rule.id, slug


async def _set_reference(
    database: Database, workspace_id: UUID, actor: Principal, dataset_id: UUID,
    rule_id: UUID, reference_id: UUID | None,
) -> None:
    async with database.unit_of_work() as session:
        await rule_service.replace_rule_set(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            slug=str(dataset_id),
            members=[rule_service.RuleSetMember(rule_id=rule_id)],
            reference_dataset_version_id=reference_id,
        )


async def _psi_outcome(
    database: Database, workspace_id: UUID, version_id: UUID, rule_slug: str,
) -> RuleOutcome:
    from model_schema import ValidationReport

    async with database.session() as session:
        reports = await validation_service.reports_for_version(
            session, workspace_id=workspace_id, version_id=version_id
        )
    report = ValidationReport.model_validate(reports[0].body)
    return next(r.outcome for r in report.results if r.rule_slug == rule_slug)


@pytest.mark.req("FR-57")
async def test_the_reference_pin_seam_three_paths(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Pinned runs, None skips, pinned-but-unprofiled skips without failing.

    The three paths are the requirement's own predicate: the reference is *preferred*, not
    required (`01` FR-54), so a pinned version without a profile must skip the
    distributional rules rather than fail the run.
    """
    actor = await _actor(database, workspace_id, "analyst")
    dataset_id = await _dataset(database, workspace_id, actor)
    # The rule set must exist before the reference is validated — a version with no rule
    # set cannot be validated at all.
    rule_id, psi_slug = await _psi_rule(database, workspace_id, actor)
    await _set_reference(database, workspace_id, actor, dataset_id, rule_id, None)

    reference_id = await _ingest(database, blob_store, workspace_id, actor, dataset_id)
    await _validate(database, blob_store, workspace_id, actor, reference_id)
    target_id = await _ingest(database, blob_store, workspace_id, actor, dataset_id)
    # An ingested version is *always* profiled (FR-60/61 runs profiling in the
    # ingestion Job), so the pinned-but-unprofiled reference must be a draft version that
    # was never ingested at all.
    async with database.unit_of_work() as session:
        draft = await dataset_service.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
        )
    unprofiled_id = draft.id

    # 1. Pinned: the reference has a profile, so the distributional rule runs.
    await _set_reference(database, workspace_id, actor, dataset_id, rule_id, reference_id)
    await _validate(database, blob_store, workspace_id, actor, target_id)
    outcome = await _psi_outcome(database, workspace_id, target_id, psi_slug)
    assert outcome is not RuleOutcome.SKIPPED

    # 2. None: no reference, the distributional rule is skipped.
    await _set_reference(database, workspace_id, actor, dataset_id, rule_id, None)
    await _validate(database, blob_store, workspace_id, actor, target_id)
    outcome = await _psi_outcome(database, workspace_id, target_id, psi_slug)
    assert outcome is RuleOutcome.SKIPPED

    # 3. Pinned-but-unprofiled: the pinned version was never validated, so it has no
    #    profile; the run still succeeds and the rule is skipped, not failed.
    await _set_reference(database, workspace_id, actor, dataset_id, rule_id, unprofiled_id)
    await _validate(database, blob_store, workspace_id, actor, target_id)
    outcome = await _psi_outcome(database, workspace_id, target_id, psi_slug)
    assert outcome is RuleOutcome.SKIPPED
