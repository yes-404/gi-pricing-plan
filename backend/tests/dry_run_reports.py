"""A stored dry-run report with a chosen outcome, for fixtures that need one.

`_require_executed_dry_run` reads the attached report, so the old fixture idiom
`row.dry_run_report_id = new_uuid7()` now reads as "a report that cannot be read" and is
refused (PL-1408, DP-3). The real dry-run job is used where the outcome's cause matters
(`test_validation_rule_approval.py`); this is for the rest.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ValidationReportRow, ValidationRuleRow
from model_schema import (
    RuleOutcome,
    RuleResult,
    Severity,
    ValidationLayer,
    ValidationReport,
    new_uuid7,
)

__all__ = ["stored_dry_run_report"]


async def stored_dry_run_report(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rule: ValidationRuleRow,
    outcome: RuleOutcome = RuleOutcome.PASS,
) -> UUID:
    """Insert one report for a one-rule run of `rule` and attach it; return its id."""
    await session.flush()  # `rule.id` is assigned on flush
    now = datetime.now(UTC)
    report = ValidationReport(
        id=new_uuid7(),
        dataset_version_id=new_uuid7(),
        rule_set_id=rule.id,
        rule_set_version=rule.version,
        started_at=now,
        finished_at=now,
        results=(
            RuleResult(
                rule_id=rule.id,
                rule_slug=rule.slug,
                rule_version=rule.version,
                layer=ValidationLayer(rule.layer),
                severity=Severity(rule.severity),
                outcome=outcome,
            ),
        ),
    )
    counts = report.counts
    session.add(
        ValidationReportRow(
            id=report.id,
            workspace_id=workspace_id,
            dataset_version_id=report.dataset_version_id,
            rule_set_id=report.rule_set_id,
            rule_set_version=report.rule_set_version,
            overall=report.overall.value,
            rule_count=len(report.results),
            fail_count=counts[RuleOutcome.FAIL.value],
            warn_count=counts[RuleOutcome.WARN.value],
            error_count=counts[RuleOutcome.ERROR.value],
            body=report.model_dump(mode="json"),
            started_at=now,
            finished_at=now,
        )
    )
    await session.flush()
    rule.dry_run_report_id = report.id
    await session.flush()
    return report.id
