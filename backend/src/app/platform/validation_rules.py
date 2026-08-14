"""Custom validation rules and rule sets, and their governance (`01` §4.5, FR-DATA-21/22).

A rule is what a report's verdict *means*. So the governance here is not ceremony: a rule
edited after the fact silently rewrites the meaning of every report that cites it, and a
rule approved by its own author is a rule nobody independent has read.

Four things this module enforces, each of which `01` §4.5 states and none of which a
caller can route around:

* Authoring produces `draft`, never `approved` (step 1).
* Approval requires a **dry run** — the rule must have executed against a real version
  (step 2). An approver reading a rule's JSON cannot tell whether it selects three rows
  or three million.
* The approver is never the author (step 3), enforced by a table constraint as well.
* An `approved` rule is immutable; an edit is a **new version** needing its own approval
  (step 4).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ValidationRuleRow, ValidationRuleSetRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit, rbac
from model_schema import (
    JobSource,
    Permission,
    Principal,
    RuleSetEntry,
    ScopeType,
    Severity,
    ValidationLayer,
    ValidationRule,
    ValidationRuleSet,
)

__all__ = [
    "approve_rule",
    "attach_dry_run",
    "create_rule",
    "load_rule",
    "replace_rule_set",
    "rule_set_for",
    "submit_for_review",
    "to_schema",
]

_log = get_logger("app.validation_rules")

DRAFT, REVIEW, APPROVED = "draft", "review", "approved"

#: `01` §4.5: the `sql` check is authored by an Admin only and gated by a workspace flag.
#: Named here rather than inline so the two places that care — authoring and rule-set
#: assembly — cannot drift apart on which check is the dangerous one.
SQL_CHECK = "sql"


def to_schema(row: ValidationRuleRow) -> ValidationRule:
    return ValidationRule.model_validate(
        {
            **row.body,
            "id": row.id,
            "slug": row.slug,
            "version": row.version,
            "layer": row.layer,
            "check": row.check,
            "severity": row.severity,
            "status": row.status,
        }
    )


async def create_rule(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    layer: ValidationLayer,
    check: str,
    severity: Severity,
    target: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    message: str = "",
    rationale: str = "",
    settings: Any = None,
) -> ValidationRuleRow:
    """Author a rule into `draft` (FR-DATA-21 step 1).

    Editing an approved rule is not an update — it allocates the next version, leaving the
    approved one exactly as the reports that cite it described.
    """
    if check == SQL_CHECK:
        await _refuse_sql_unless_enabled(session, workspace_id=workspace_id, settings=settings)
        # OQ-DATA-3, decided 2026-08-14: Admin-authored, **instead of** the Analyst or
        # Actuary who authors every other rule (`01` §4.5 step 5) — not in addition to
        # them. Requiring both would leave no built-in role able to author one, which
        # makes a decided capability unreachable rather than restricted.
        await rbac.require_permission(
            session,
            workspace_id=workspace_id,
            principal=actor,
            permission=Permission.ADMIN_MANAGE_SETTINGS,
        )
    else:
        await rbac.require_permission(
            session,
            workspace_id=workspace_id,
            principal=actor,
            permission=Permission.DATASET_WRITE,
        )

    version = 1 + (
        await session.execute(
            select(func.coalesce(func.max(ValidationRuleRow.version), 0)).where(
                ValidationRuleRow.workspace_id == workspace_id,
                ValidationRuleRow.slug == slug,
            )
        )
    ).scalar_one()

    row = ValidationRuleRow(
        workspace_id=workspace_id,
        slug=slug,
        version=version,
        layer=layer.value,
        check=check,
        severity=severity.value,
        body={
            "target": target or {},
            "params": params or {},
            "scope": {},
            "tolerance": {},
            "message": message,
            "rationale": rationale,
        },
        status=DRAFT,
        authored_by=actor.id,
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise PlatformError(
            "VALIDATION_FAILED",
            "That rule version already exists",
            409,
            f"Rule {slug!r} version {version} exists. Rule versions are allocated, never "
            "chosen.",
        ) from exc

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="validation_rule.created",
        entity_ref=f"validation_rule:{slug}@{version}",
        after={"slug": slug, "version": version, "check": check, "status": DRAFT},
    )
    return row


async def _refuse_sql_unless_enabled(
    session: AsyncSession, *, workspace_id: UUID, settings: Any
) -> None:
    """`features.sql_validation_check_enabled`, which defaults to off (OQ-DATA-3).

    A workspace that never needs the escape hatch never carries its risk. Checked when the
    rule is *authored* rather than only when it runs: a draft `sql` rule sitting in a
    workspace that has the flag off is a rule waiting for someone to turn the flag on for
    an unrelated reason.
    """
    from app.platform import settings as settings_service

    if settings is None:  # pragma: no cover — the API always supplies them
        return
    resolution = await settings_service.resolve(
        session, settings, workspace_id, "features.sql_validation_check_enabled"
    )
    if not resolution.effective_value:
        raise PlatformError(
            "VALIDATION_FAILED",
            "The sql validation check is disabled in this workspace",
            409,
            "`01` §4.5 gates the sql escape hatch behind "
            "`features.sql_validation_check_enabled`, which defaults to off (OQ-DATA-3). "
            "The declarative checks cover the great majority of real rules; this one is "
            "deliberately expensive to reach for.",
        )


async def load_rule(
    session: AsyncSession, *, workspace_id: UUID, rule_id: UUID
) -> ValidationRuleRow:
    row = await session.get(ValidationRuleRow, rule_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Validation rule not found", 404, f"No rule {rule_id}."
        )
    return row


async def attach_dry_run(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rule_id: UUID,
    report_id: UUID,
) -> ValidationRuleRow:
    """Record that this rule executed against a real version (FR-DATA-21 step 2)."""
    row = await load_rule(session, workspace_id=workspace_id, rule_id=rule_id)
    row.dry_run_report_id = report_id
    await session.flush()
    return row


async def submit_for_review(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, rule_id: UUID
) -> ValidationRuleRow:
    """`draft` → `review`, and only with a dry run attached (FR-DATA-21 steps 2 and 3)."""
    row = await load_rule(session, workspace_id=workspace_id, rule_id=rule_id)
    if row.status != DRAFT:
        raise PlatformError(
            "RULE_NOT_APPROVED",
            f"Only a draft rule can be submitted; this one is {row.status!r}",
            409,
            "An approved rule is immutable (`01` §4.5 step 4) — an edit creates a new "
            "version, which is submitted on its own.",
        )
    if row.dry_run_report_id is None:
        raise PlatformError(
            "RULE_NOT_APPROVED",
            "A rule must be dry-run before it can be submitted",
            409,
            "FR-DATA-21 step 2 attaches the dry-run result to the approval request. "
            "Without it the approver is reading JSON and guessing what it selects.",
        )

    row.status = REVIEW
    await session.flush()
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="validation_rule.submitted",
        entity_ref=f"validation_rule:{row.slug}@{row.version}",
        before={"status": DRAFT},
        after={"status": REVIEW, "dry_run_report_id": str(row.dry_run_report_id)},
    )
    return row


async def approve_rule(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, rule_id: UUID
) -> ValidationRuleRow:
    """`review` → `approved`, by someone other than the author (FR-DATA-21 step 3)."""
    row = await load_rule(session, workspace_id=workspace_id, rule_id=rule_id)
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.APPROVAL_DECIDE,
    )
    if row.status != REVIEW:
        raise PlatformError(
            "RULE_NOT_APPROVED",
            f"Only a rule in review can be approved; this one is {row.status!r}",
            409,
            "`01` §4.5 step 3.",
        )
    if row.authored_by == actor.id:
        raise PlatformError(
            "SUBMITTER_CANNOT_APPROVE",
            "A rule cannot be approved by its author",
            409,
            "`01` §4.5 step 3 and FR-GOV-11. A rule decides whether data may be modelled "
            "on; one person deciding both what it says and that it is right is not a "
            "review.",
        )

    row.status = APPROVED
    row.approved_by = actor.id
    await session.flush()
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="validation_rule.approved",
        entity_ref=f"validation_rule:{row.slug}@{row.version}",
        before={"status": REVIEW},
        after={"status": APPROVED, "approved_by": str(actor.id)},
    )
    return row


async def rule_set_for(
    session: AsyncSession, *, workspace_id: UUID, dataset_id: UUID, slug: str
) -> ValidationRuleSet:
    """The dataset's current rule set (FR-DATA-22)."""
    row = (
        await session.execute(
            select(ValidationRuleSetRow)
            .where(
                ValidationRuleSetRow.workspace_id == workspace_id,
                ValidationRuleSetRow.dataset_id == dataset_id,
            )
            .order_by(ValidationRuleSetRow.version.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "This dataset has no rule set",
            404,
            f"Dataset {slug!r} has no Validation Rule Set. One must be defined before the "
            "version can be validated (FR-DATA-16).",
        )
    return await _to_rule_set(session, row, workspace_id=workspace_id)


async def _to_rule_set(
    session: AsyncSession, row: ValidationRuleSetRow, *, workspace_id: UUID
) -> ValidationRuleSet:
    """Resolve the stored rule ids into the rules they name.

    The set stores ids rather than copies. A copy would let the set and the rule disagree
    about a rule's severity, and the report cites both.
    """
    rule_ids = [UUID(value) for value in row.body.get("rule_ids", [])]
    rules = (
        await session.execute(
            select(ValidationRuleRow).where(
                ValidationRuleRow.workspace_id == workspace_id,
                ValidationRuleRow.id.in_(rule_ids),
            )
        )
    ).scalars().all()
    by_id = {rule.id: rule for rule in rules}
    entries = tuple(
        RuleSetEntry(rule=to_schema(by_id[rule_id])) for rule_id in rule_ids if rule_id in by_id
    )
    return ValidationRuleSet(
        id=row.id,
        slug=row.slug,
        version=row.version,
        dataset_id=row.dataset_id,
        entries=entries,
        reference_dataset_version_id=row.reference_dataset_version_id,
        status=row.status,
    )


async def replace_rule_set(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    dataset_id: UUID,
    slug: str,
    rule_ids: list[UUID],
    reference_dataset_version_id: UUID | None = None,
) -> ValidationRuleSet:
    """Create the next rule-set version (FR-DATA-22).

    Never an in-place edit. A Validation Report records the exact `rule_set_version` it
    ran; mutating a set would change what every past report was a report *of*, and "it
    passed" would stop meaning "it passed these rules".
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.DATASET_WRITE,
        resource=rbac.ResourceRef(scope_type=ScopeType.DATASET, scope_id=dataset_id),
    )

    rules = (
        await session.execute(
            select(ValidationRuleRow).where(
                ValidationRuleRow.workspace_id == workspace_id,
                ValidationRuleRow.id.in_(rule_ids),
            )
        )
    ).scalars().all()
    found = {rule.id for rule in rules}
    missing = [str(rule_id) for rule_id in rule_ids if rule_id not in found]
    if missing:
        raise PlatformError(
            "NOT_FOUND",
            "The rule set names rules that do not exist",
            404,
            f"Unknown rule id(s): {', '.join(missing)}.",
        )

    unapproved = sorted(f"{rule.slug}@{rule.version}" for rule in rules if rule.status != APPROVED)
    if unapproved:
        raise PlatformError(
            "RULE_NOT_APPROVED",
            "Every rule in a rule set must be approved",
            409,
            f"Not approved: {', '.join(unapproved)}. A rule set is what a version is "
            "validated against, so a draft rule in one would gate modelling on something "
            "nobody reviewed (FR-DATA-21).",
        )

    version = 1 + (
        await session.execute(
            select(func.coalesce(func.max(ValidationRuleSetRow.version), 0)).where(
                ValidationRuleSetRow.workspace_id == workspace_id,
                ValidationRuleSetRow.slug == slug,
            )
        )
    ).scalar_one()

    row = ValidationRuleSetRow(
        workspace_id=workspace_id,
        dataset_id=dataset_id,
        slug=slug,
        version=version,
        body={"rule_ids": [str(rule_id) for rule_id in rule_ids]},
        reference_dataset_version_id=reference_dataset_version_id,
        status=APPROVED,
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="validation_rule_set.replaced",
        entity_ref=f"validation_rule_set:{slug}@{version}",
        after={"version": version, "rule_ids": [str(r) for r in rule_ids]},
    )
    return await _to_rule_set(session, row, workspace_id=workspace_id)
