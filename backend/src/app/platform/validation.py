"""Validation reports, acknowledgements and the promotion they gate (`01` §3.3, §4.6).

`datasets.promote_to_validated` owns the *rule* — zero fails, zero errors, every warning
acknowledged — and takes the verdict as arguments, because reading the report belongs
here. This module is the other half: it stores reports, records acknowledgements, and
computes the two numbers promotion turns on.

**Reports are stored whole and never rewritten.** A report is the evidence that a version
was or was not fit to model on, so a report the platform reshapes on read — because a
field was added, or an enum gained a member — is not evidence of what was decided. The
summary columns beside the body are indexes and nothing else.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AcknowledgementRow, DatasetVersionRow, ValidationReportRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit, datasets, rbac
from app.platform.rbac import ResourceRef
from model_schema import (
    Acknowledgement,
    JobSource,
    OverallOutcome,
    Permission,
    Principal,
    RuleOutcome,
    ScopeType,
    ValidationReport,
)

__all__ = [
    "acknowledge",
    "acknowledgements_for",
    "load_report",
    "load_report_view",
    "promote_using_report",
    "reports_for_version",
    "store_report",
    "unacknowledged_warnings",
]

_log = get_logger("app.validation")


def _counts(report: ValidationReport) -> dict[str, int]:
    counts = {outcome.value: 0 for outcome in RuleOutcome}
    for result in report.results:
        counts[result.outcome.value] += 1
    return counts


def overall_outcome(report: ValidationReport) -> OverallOutcome:
    """A report's verdict (`01` §4.6), from the rule results alone.

    **One line, because there must be one implementation.** This function and
    `ValidationReport.overall` were two statements of §4.6's invariant, and they disagreed:
    this one followed the 2026-08-14 amendment and the property did not, so the row said
    `pass_with_warnings` while the handler — which reads the property through
    `permits_validation` — drove the version to `failed`. Any dataset version with a single
    warning was then unpromotable for ever. Found by `WF-698`'s journey test, 2026-08-17.

    Kept as a function rather than deleted: it is the name three call sites and two tests
    already use, and a re-export costs nothing while a rename touches files this change has
    no business in.
    """
    return report.overall


async def store_report(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    report: ValidationReport,
    job_id: UUID | None = None,
) -> ValidationReportRow:
    """Persist one run's report against its version (FR-42, FR-49)."""
    version = await session.get(DatasetVersionRow, report.dataset_version_id)
    if version is None or version.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "Dataset version not found",
            404,
            f"No version {report.dataset_version_id} in this workspace.",
        )

    counts = _counts(report)
    outcome = overall_outcome(report)
    row = ValidationReportRow(
        id=report.id,
        workspace_id=workspace_id,
        dataset_version_id=report.dataset_version_id,
        rule_set_id=report.rule_set_id,
        rule_set_version=report.rule_set_version,
        job_id=job_id or report.job_id,
        overall=outcome.value,
        rule_count=len(report.results),
        fail_count=counts[RuleOutcome.FAIL.value],
        warn_count=counts[RuleOutcome.WARN.value],
        error_count=counts[RuleOutcome.ERROR.value],
        # `mode="json"` because the body is read back through `model_validate_json` and
        # compared byte-for-byte by NFR-469. A body stored with Python datetimes and
        # UUIDs round-trips through JSONB into strings anyway — doing it here means the
        # bytes that were compared are the bytes that were stored.
        body=report.model_dump(mode="json"),
        started_at=report.started_at,
        finished_at=report.finished_at,
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="validation_report.created",
        entity_ref=f"validation_report:{report.id}",
        after={
            "dataset_version_id": str(report.dataset_version_id),
            "rule_set_version": report.rule_set_version,
            "overall": outcome.value,
            "fail": counts[RuleOutcome.FAIL.value],
            "warn": counts[RuleOutcome.WARN.value],
            "error": counts[RuleOutcome.ERROR.value],
        },
        job_id=job_id,
    )
    _log.info(
        "validation report stored",
        extra={"report_id": str(report.id), "overall": outcome.value},
    )
    return row


async def load_report(
    session: AsyncSession, *, workspace_id: UUID, report_id: UUID
) -> ValidationReport:
    """Read a stored report back as the artifact it was (FR-49)."""
    row = await session.get(ValidationReportRow, report_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Validation report not found", 404, f"No report {report_id}."
        )
    return ValidationReport.model_validate(row.body)


async def acknowledgements_for(
    session: AsyncSession, *, workspace_id: UUID, report_id: UUID
) -> dict[UUID, Acknowledgement]:
    """The acknowledgements recorded against a report, by rule id (FR-47)."""
    result = await session.execute(
        select(AcknowledgementRow).where(
            AcknowledgementRow.workspace_id == workspace_id,
            AcknowledgementRow.report_id == report_id,
        )
    )
    return {
        row.rule_id: Acknowledgement(
            user_id=row.user_id, at=row.acknowledged_at, justification=row.justification
        )
        for row in result.scalars()
    }


async def load_report_view(
    session: AsyncSession, *, workspace_id: UUID, report_id: UUID
) -> ValidationReport:
    """The report **as presented**, with its acknowledgements merged in.

    Distinct from `load_report`, which returns the stored artifact verbatim and must keep
    doing so — NFR-469 compares bodies byte for byte, and an accessor that folded in
    rows written afterwards would make an immutable artifact appear to change.

    The merge belongs at the read edge because an acknowledgement is a fact *about* a
    report rather than inside it (`01` §4.6, amended). Without it the API can say how many
    warnings are outstanding but not **which** — and "warnings needing acknowledgement" is
    a band `01` §5.3 requires the validation view to render above the fold. With one
    warning a client could infer it; with three it cannot.
    """
    report = await load_report(session, workspace_id=workspace_id, report_id=report_id)
    acknowledged = await acknowledgements_for(
        session, workspace_id=workspace_id, report_id=report_id
    )
    if not acknowledged:
        return report
    return report.model_copy(
        update={
            "results": tuple(
                result.model_copy(update={"acknowledgement": acknowledged[result.rule_id]})
                if result.rule_id in acknowledged
                else result
                for result in report.results
            )
        }
    )


async def reports_for_version(
    session: AsyncSession, *, workspace_id: UUID, version_id: UUID
) -> list[ValidationReportRow]:
    """Report history, newest first (`01` §5.1).

    Summary rows, not bodies: a version validated fifty times should not load fifty full
    reports to render a list of dates and verdicts (NFR-471).
    """
    result = await session.execute(
        select(ValidationReportRow)
        .where(
            ValidationReportRow.workspace_id == workspace_id,
            ValidationReportRow.dataset_version_id == version_id,
        )
        .order_by(ValidationReportRow.created_at.desc(), ValidationReportRow.id.desc())
    )
    return list(result.scalars().all())


async def acknowledge(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    report_id: UUID,
    rule_id: UUID,
    justification: str,
) -> AcknowledgementRow:
    """Accept one `warn`, with a reason, audited (FR-46, FR-47).

    Three refusals, and each exists because the alternative makes the gate decorative:
    only a `warn` can be acknowledged, only by a principal holding the permission, and
    only once per `(report, rule)`.
    """
    if not justification.strip():
        raise PlatformError(
            "VALIDATION_FAILED",
            "An acknowledgement requires a justification",
            422,
            "FR-46: the justification is the audit record. An acknowledgement "
            "without one is an unexplained decision to model on data that raised a "
            "warning.",
        )

    row = await session.get(ValidationReportRow, report_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Validation report not found", 404, f"No report {report_id}."
        )

    version = await session.get(DatasetVersionRow, row.dataset_version_id)
    permitted = await rbac.has_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.DATASET_ACKNOWLEDGE_WARNING,
        resource=(
            ResourceRef(scope_type=ScopeType.DATASET, scope_id=version.dataset_id)
            if version is not None
            else None
        ),
    )
    if not permitted:
        # `01` §5.1 owns a code for exactly this, so raise it rather than the generic
        # denial: the caller needs to know it is the *role* that is wrong, not the scope.
        # An analyst reading "permission denied" goes looking for a grant; reading this,
        # they go and find an actuary, which is what FR-46 intends them to do.
        raise PlatformError(
            "ACKNOWLEDGE_FORBIDDEN_ROLE",
            "Acknowledging a validation warning requires the Pricing Actuary role",
            403,
            "FR-46 places this judgement with an actuary. Modelling on warned data "
            "is an actuarial decision, and the acknowledgement is its record.",
        )

    report = ValidationReport.model_validate(row.body)
    target = next((r for r in report.results if r.rule_id == rule_id), None)
    if target is None:
        raise PlatformError(
            "NOT_FOUND",
            "Rule not found in this report",
            404,
            f"Report {report_id} has no result for rule {rule_id}.",
        )
    if target.outcome is not RuleOutcome.WARN:
        raise PlatformError(
            "VALIDATION_FAILED",
            f"Only a warning can be acknowledged; this rule is {target.outcome.value!r}",
            409,
            "`01` §1.3: a `fail` is not acknowledgeable — there is no override. An "
            "`error` means the rule did not run, which is a reason to fix the rule.",
        )

    acknowledgement = AcknowledgementRow(
        workspace_id=workspace_id,
        dataset_version_id=row.dataset_version_id,
        report_id=report_id,
        rule_id=rule_id,
        user_id=actor.id,
        justification=justification.strip(),
        acknowledged_at=datetime.now(UTC),
    )
    session.add(acknowledgement)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise PlatformError(
            "ACKNOWLEDGEMENT_ALREADY_RECORDED",
            "This warning is already acknowledged",
            409,
            f"Rule {rule_id} on report {report_id} already carries an acknowledgement "
            "(FR-47 scopes one to a report and rule).",
        ) from exc

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="validation_warning.acknowledged",
        entity_ref=f"validation_report:{report_id}",
        before={"rule_id": str(rule_id), "acknowledged": False},
        after={"rule_id": str(rule_id), "acknowledged": True, "rule_slug": target.rule_slug},
        justification=justification.strip(),
    )
    return acknowledgement


async def unacknowledged_warnings(
    session: AsyncSession, *, workspace_id: UUID, report_id: UUID
) -> int:
    """How many `warn` results still lack an acknowledgement (FR-46)."""
    row = await session.get(ValidationReportRow, report_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Validation report not found", 404, f"No report {report_id}."
        )
    acknowledged = await session.execute(
        select(func.count()).select_from(AcknowledgementRow).where(
            AcknowledgementRow.report_id == report_id
        )
    )
    return max(row.warn_count - int(acknowledged.scalar_one()), 0)


async def promote_using_report(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    version_id: UUID,
    report_id: UUID,
) -> DatasetVersionRow:
    """Promote a version using its stored report (`01` §1.3, FR-46).

    The glue that was missing: `promote_to_validated` takes the verdict as arguments so
    that the rule and the storage stay separable, and this is the one place that supplies
    them from the database rather than from a caller's belief about them.
    """
    row = await session.get(ValidationReportRow, report_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Validation report not found", 404, f"No report {report_id}."
        )
    if row.dataset_version_id != version_id:
        raise PlatformError(
            "VALIDATION_FAILED",
            "That report belongs to a different dataset version",
            409,
            f"Report {report_id} validates version {row.dataset_version_id}, not "
            f"{version_id}. Promoting on another version's report would validate data "
            "nobody checked.",
        )

    outstanding = await unacknowledged_warnings(
        session, workspace_id=workspace_id, report_id=report_id
    )
    return await datasets.promote_to_validated(
        session,
        workspace_id=workspace_id,
        actor=actor,
        version_id=version_id,
        report_id=report_id,
        report_passed=OverallOutcome(row.overall)
        in {OverallOutcome.PASS, OverallOutcome.PASS_WITH_WARNINGS},
        unacknowledged_warnings=outstanding,
    )




