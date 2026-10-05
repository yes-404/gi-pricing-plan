"""Writing `approved` rows in a test the way the decision path leaves them.

`approval_guard()` (WK-674 Slice 2a) refuses an `approved` row with no evidence. A fixture
that needs one therefore writes the evidence **first**: for the six evidence-only tables a
decided `approval_requests` row for the row's ref, under `approval_decision()` (the flag is
what `approval_requests` itself accepts), **flushed explicitly** as `approvals.decide` does at
its flush, and only then the artifact row. The flush is explicit so the order never depends
on the ORM's table sort. For a rule set, or `approval_requests` itself, the flag
suffices and there is no evidence to write (`RL-1301` A.4.2).

This module creates the evidence; it never names the flag or the trigger DDL.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalRequestRow,
    CustomMetricRow,
    CustomObjectiveRow,
    ModelRow,
    PerilStructureRow,
    RatingVersionRow,
    ValidationRuleRow,
    ValidationRuleSetRow,
)
from app.platform.approvals import approval_decision
from model_schema import ArtifactRef, new_uuid7

__all__ = ["add_approved", "decided_request", "mark_approved"]

#: class -> (artifact type, slug attribute). `ModelRow`'s slug is `model_family_slug`.
_EVIDENCE: dict[type[Any], tuple[str, str]] = {
    ModelRow: ("model", "model_family_slug"),
    CustomMetricRow: ("custom_metric", "slug"),
    CustomObjectiveRow: ("custom_objective", "slug"),
    PerilStructureRow: ("peril_structure", "slug"),
    RatingVersionRow: ("rating_version", "slug"),
    ValidationRuleRow: ("validation_rule", "slug"),
}
_FLAG_ONLY = (ValidationRuleSetRow, ApprovalRequestRow)


async def decided_request(
    session: AsyncSession, *, workspace_id: UUID, artifact_type: str, slug: str, version: int
) -> ApprovalRequestRow:
    """An `approved` request for `type:slug@version`, flushed before the caller writes on."""
    request = ApprovalRequestRow(
        workspace_id=workspace_id,
        artifact_ref=str(ArtifactRef(type=artifact_type, slug=slug, version=version)),
        artifact_type=artifact_type,
        submitted_by=new_uuid7(),
        change_summary="test fixture: the decision the artifact rests on",
        status="approved",
        approvers_required=1,
    )
    async with approval_decision(session):
        session.add(request)
        await session.flush()
    return request


async def _write_evidence(session: AsyncSession, row: Any) -> None:
    artifact_type, slug_attr = _EVIDENCE[type(row)]
    await decided_request(
        session,
        workspace_id=row.workspace_id,
        artifact_type=artifact_type,
        slug=getattr(row, slug_attr),
        version=row.version if row.version is not None else 1,
    )


async def add_approved(session: AsyncSession, row: Any) -> Any:
    """Add a new row whose status is `approved`, with its evidence written and flushed first."""
    if type(row) in _EVIDENCE:
        await _write_evidence(session, row)
        session.add(row)
        await session.flush()
    else:
        assert isinstance(row, _FLAG_ONLY), type(row)
        async with approval_decision(session):
            session.add(row)
            await session.flush()
    return row


async def mark_approved(session: AsyncSession, row: Any) -> Any:
    """Move an existing row to `approved`, with its evidence written and flushed first."""
    if type(row) in _EVIDENCE:
        await _write_evidence(session, row)
        row.status = "approved"
        await session.flush()
    else:
        assert isinstance(row, _FLAG_ONLY), type(row)
        async with approval_decision(session):
            row.status = "approved"
            await session.flush()
    return row
