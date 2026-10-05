"""Custom validation rules and rule sets, and their governance (`01` §4.5, FR-50/51).

A rule is what a report's verdict *means*. So the governance here is not ceremony: a rule
edited after the fact silently rewrites the meaning of every report that cites it, and a
rule approved by its own author is a rule nobody independent has read.

Four things this module enforces, each of which `01` §4.5 states and none of which a
caller can route around:

* Authoring produces `draft`, never `approved` (step 1).
* Approval requires a **dry run** — the rule must have executed against a real version
  (step 2). An approver reading a rule's JSON cannot tell whether it selects three rows
  or three million.
* The approver is never the author (step 3), enforced by a table constraint as well, and
  approval is a decision on an approval request: this module submits the request and
  carries the decision (`apply_approval_decision`), and writes `approved` nowhere else.
* An `approved` rule is immutable; an edit is a **new version** needing its own approval
  (step 4).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalRequestRow,
    DatasetRow,
    ValidationReportRow,
    ValidationRuleRow,
    ValidationRuleSetRow,
    ValidationRuleStatus,
)
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import approvals, audit, rbac
from model_schema import (
    BUILTIN_RULES,
    ApprovalStatus,
    ArtifactRef,
    JobSource,
    Permission,
    Principal,
    RuleSetEntry,
    ScopeType,
    Severity,
    ValidationLayer,
    ValidationRule,
    ValidationRuleSet,
    builtin_rule,
)

__all__ = [
    "RuleSetMember",
    "apply_approval_decision",
    "attach_dry_run",
    "create_rule",
    "load_rule",
    "open_request_for",
    "replace_rule_set",
    "resolve_artifact_ref",
    "rule_set_for",
    "rule_set_to_run",
    "seed_builtin_rules",
    "submit_for_review",
    "to_schema",
]

_log = get_logger("app.validation_rules")

DRAFT, REVIEW, APPROVED = (
    ValidationRuleStatus.DRAFT.value,
    ValidationRuleStatus.REVIEW.value,
    ValidationRuleStatus.APPROVED.value,
)

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
            "catalogue_id": row.catalogue_id,
        }
    )


async def seed_builtin_rules(
    session: AsyncSession, workspace_id: UUID, *, authored_by: UUID
) -> list[ValidationRuleRow]:
    """Create `01` §4.4's catalogue in a workspace if it is absent (FR-68).

    `rbac.seed_builtin_roles`' sibling, idempotent for the same reason: it runs on paths
    that may be retried, and `uq_validation_rule_version` turns a second run into an
    `IntegrityError` surfacing far from its cause.

    A copy rather than a reference, also for `seed_builtin_roles`' reason — changing the
    shipped catalogue must not silently change what an existing workspace's reports
    *meant*. §4.4's ids are stable, so a later slice can offer a workspace the newer text
    as a new version it approves; nothing rewrites the rule a report already cites.

    Seeded **`approved`, with no approver and no dry run**. `01` §4.5's step-2 and step-3
    obligations are about a rule this workspace wrote: a shipped rule was reviewed once,
    in the specification, and there is no in-workspace author for an approver to differ
    from. `approved_rule_dry_run_and_separate_approver`'s `builtin IS TRUE` arm names that
    exemption rather than leaving callers to fabricate a `dry_run_report_id` pointing at no
    report, which is what `examples/fremtpl2/seed.py` did before this slice.

    No audit event, matching `seed_builtin_roles`: seeding is not an actor's decision about
    this workspace's governance, it is the workspace arriving with the catalogue every
    workspace has. `validation_rule.created` records the decisions.

    Writes with `flush()`, never `commit()` — FR-370's rule that a platform write shares
    the caller's transaction.
    """
    existing = {
        catalogue_id
        for (catalogue_id,) in (
            await session.execute(
                select(ValidationRuleRow.catalogue_id).where(
                    ValidationRuleRow.workspace_id == workspace_id,
                    ValidationRuleRow.catalogue_id.is_not(None),
                )
            )
        ).all()
    }
    created: list[ValidationRuleRow] = []
    # ALLOWANCE (PL-1303 Acceptance 7, RL-1301 A.4.5): a legitimate seed writer. The shipped
    # catalogue arrives `approved` with no request to cite, so it enters the decision flag
    # around its own write; `approval_guard()` still refuses every other writer here.
    async with approvals.approval_decision(session):
        for catalogue_id, rule in BUILTIN_RULES.items():
            if catalogue_id in existing:
                continue
            row = ValidationRuleRow(
                workspace_id=workspace_id,
                slug=rule.slug,
                version=1,
                layer=rule.layer.value,
                check=rule.check,
                severity=rule.severity.value,
                body={
                    "target": {},
                    # FR-56: the catalogue carries a built-in's default thresholds, so the
                    # seeded row publishes them rather than leaving every threshold a literal in
                    # `pricing-core` that no caller can read. Copied, not aliased — the catalogue
                    # is a process-wide constant and this dict is about to be handed to the ORM.
                    "params": dict(rule.params),
                    "scope": {},
                    "tolerance": {},
                    "message": rule.summary,
                    "rationale": (
                        f"Built-in rule {catalogue_id} from `01` §4.4's catalogue, reviewed "
                        "there rather than in this workspace."
                    ),
                },
                status=APPROVED,
                authored_by=authored_by,
                builtin=True,
                catalogue_id=catalogue_id,
            )
            session.add(row)
            created.append(row)
        await session.flush()
    return created


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
    catalogue_id: str | None = None,
    message: str = "",
    rationale: str = "",
    settings: Any = None,
) -> ValidationRuleRow:
    """Author a rule into `draft` (FR-50 step 1).

    Editing an approved rule is not an update — it allocates the next version, leaving the
    approved one exactly as the reports that cite it described.
    """
    if check == SQL_CHECK:
        await _refuse_sql_unless_enabled(session, workspace_id=workspace_id, settings=settings)
        # OQ-559, decided 2026-08-14: Admin-authored, **instead of** the Analyst or
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

    if catalogue_id is not None:
        try:
            builtin_rule(catalogue_id)
        except ValueError as exc:
            raise PlatformError(
                "VALIDATION_FAILED",
                "That catalogue entry does not exist",
                422,
                str(exc),
            ) from exc

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
        catalogue_id=catalogue_id,
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
    """`features.sql_validation_check_enabled`, which defaults to off (OQ-559).

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
            "`features.sql_validation_check_enabled`, which defaults to off (OQ-559). "
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


async def resolve_artifact_ref(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> bool:
    """`validation_rule:<slug>@<version>` → does that version exist? (`06` FR-386.)

    `False`, having done nothing, for a reference that is not this module's — the contract
    `api/approvals.py`'s fan-out is built on.

    By slug and version rather than by id, unlike `load_rule`: a reference *is* a slug and a
    version (ID-3), and `uq_validation_rule_version` makes the pair identify one row. This
    answers whether there is a rule in `review` whose dry run executed
    (`_require_executed_dry_run`); whether the approver is its author is the decide path's.
    """
    if artifact_ref.type != "validation_rule":
        return False
    row = (
        await session.execute(
            select(ValidationRuleRow).where(
                ValidationRuleRow.workspace_id == workspace_id,
                ValidationRuleRow.slug == artifact_ref.slug,
                ValidationRuleRow.version == artifact_ref.version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Validation rule not found",
            404,
            f"{artifact_ref} resolves to no validation rule in this workspace.",
        )
    approvals.require_in_review(artifact_ref, row.status)
    await _require_executed_dry_run(session, workspace_id=workspace_id, row=row)
    return True


async def _require_executed_dry_run(
    session: AsyncSession, *, workspace_id: UUID, row: ValidationRuleRow
) -> None:
    """The dry run executed: its report exists here and has no `error` (FR-363, `06:114`).

    `01` §4.5 step 2 says the rule "must execute successfully", and `01:470-473` says the
    mandatory dry run is what stops an `error` outcome reaching approval. A `fail` is a rule
    that ran and caught rows, so it passes. A report that cannot be read is refused, never
    assumed (the platform's fail-closed rule, as `APPROVAL_AUTHOR_UNRESOLVED`).
    """
    report = (
        None
        if row.dry_run_report_id is None
        else await session.get(ValidationReportRow, row.dry_run_report_id)
    )
    if report is None or report.workspace_id != workspace_id:
        raise PlatformError(
            "EVIDENCE_INCOMPLETE",
            "Required evidence is missing",
            422,
            f"validation_rule:{row.slug}@{row.version}: its dry-run report "
            f"{row.dry_run_report_id} cannot be read in this workspace. `06` FR-363.",
        )
    if report.error_count > 0:
        raise PlatformError(
            "EVIDENCE_INCOMPLETE",
            "Required evidence is missing",
            422,
            f"validation_rule:{row.slug}@{row.version}: its dry run did not execute "
            f"({report.error_count} `error` result(s)). `01` §4.5 step 2 requires a run "
            "that executed; a `fail` outcome would be accepted. `06` FR-363.",
        )


async def attach_dry_run(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rule_id: UUID,
    report_id: UUID,
) -> ValidationRuleRow:
    """Record that this rule executed against a real version (FR-50 step 2).

    Refused for an `approved` rule: its dry-run report is its approval evidence, and
    `01` §4.5 step 4 makes an approved rule immutable (FD-1415, RL-1407 (#1070 @24ea2130)).
    The worker stores the report and attaches it in one unit of work, so this refusal rolls
    the report back with it.
    """
    row = await load_rule(session, workspace_id=workspace_id, rule_id=rule_id)
    if row.status == APPROVED:
        raise PlatformError(
            "RULE_VERSION_IMMUTABLE",
            "An approved rule's dry run cannot be replaced",
            409,
            f"validation_rule:{row.slug}@{row.version} is approved. `01` §4.5 step 4: "
            "an approved rule is immutable, and its dry-run report is its approval "
            "evidence. Dry-run a new version instead.",
        )
    row.dry_run_report_id = report_id
    await session.flush()
    return row


async def submit_for_review(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    rule_id: UUID,
    change_summary: str,
) -> ValidationRuleRow:
    """`draft` → `review` and the approval request it exists to create (FR-50 steps 2, 3).

    Only with a dry run attached that executed. The request is filed here, as
    `objectives.submit_for_review` files its own, so that approval is a decision on a
    request (`apply_approval_decision`) and not a status this module writes by itself.
    """
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
            "FR-50 step 2 attaches the dry-run result to the approval request. "
            "Without it the approver is reading JSON and guessing what it selects.",
        )
    await _require_executed_dry_run(session, workspace_id=workspace_id, row=row)

    request = await approvals.submit(
        session,
        workspace_id=workspace_id,
        submitter=actor,
        artifact_ref=ArtifactRef(type="validation_rule", slug=row.slug, version=row.version),
        change_summary=change_summary,
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
        after={
            "status": REVIEW,
            "dry_run_report_id": str(row.dry_run_report_id),
            "approval_request_id": str(request.id),
        },
        justification=change_summary,
    )
    return row


#: What a request's status means for the rule behind it. `06` FR-355 returns the artifact
#: to its pre-submission state, which for a rule is `draft` (`01` §4.5 step 1).
_TARGET = {
    ApprovalStatus.APPROVED: APPROVED,
    ApprovalStatus.CHANGES_REQUESTED: DRAFT,
    ApprovalStatus.REJECTED: DRAFT,
    ApprovalStatus.WITHDRAWN: DRAFT,
}


async def apply_approval_decision(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    request: ApprovalRequestRow,
) -> ValidationRuleRow | None:
    """Carry a governance decision into the rule (FR-50 step 3, `06` FR-355).

    `None` for a request about anything else, so `_carry_to_the_artifact` drives every
    artifact type through one call. Same transaction as the decision: a rule left in
    `review` after its request reached `approved` is one no Rule Set may run and no screen
    can explain. The caller is already inside `approval_decision()`, so this does not
    enter it again.

    An approval re-checks the dry run (`_require_executed_dry_run`): the refusal rolls the
    decision back with it, so an approver is told the evidence is missing and finds nothing
    recorded against a rule that cannot run.
    """
    if request.artifact_type != "validation_rule":
        return None

    ref = ArtifactRef.model_validate(request.artifact_ref)
    row = (
        await session.execute(
            select(ValidationRuleRow)
            .where(
                ValidationRuleRow.workspace_id == workspace_id,
                ValidationRuleRow.slug == ref.slug,
                ValidationRuleRow.version == ref.version,
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if row is None:
        # Tolerated as a Model's is: `POST /approval-requests` accepts any well-formed
        # ref, and a request naming a rule that was never created must still be
        # decidable rather than sitting open for ever (`06` FR-386).
        return None

    target = _TARGET.get(ApprovalStatus(request.status))
    if target is None or row.status == target:
        # A partial approval: the policy wants another approver and nothing has moved.
        return row
    if row.status != REVIEW:
        raise PlatformError(
            "RULE_NOT_APPROVED",
            f"Only a rule in review can be decided; this one is {row.status!r}",
            409,
            f"{ref} is {row.status} and the decision would move it to {target}. "
            "`01` §4.5 steps 3 and 4.",
        )

    if target == APPROVED:
        await _require_executed_dry_run(session, workspace_id=workspace_id, row=row)
        row.approved_by = actor.id
    row.status = target
    await session.flush()

    after: dict[str, Any] = {"status": target, "approval_request_id": str(request.id)}
    if target == APPROVED:
        after["approved_by"] = str(actor.id)
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=f"validation_rule.{target}",
        entity_ref=str(ref),
        before={"status": REVIEW},
        after=after,
    )
    return row


async def open_request_for(
    session: AsyncSession, *, workspace_id: UUID, row: ValidationRuleRow
) -> UUID:
    """The id of the open approval request on this rule, for the approve route's client.

    A rule in `review` with no open request (a reset one, `PL-1408` Task 7) has no path
    through the approve route: it is refused, and the refusal names the way back.
    """
    request_id = (
        await session.execute(
            select(ApprovalRequestRow.id).where(
                ApprovalRequestRow.workspace_id == workspace_id,
                ApprovalRequestRow.artifact_ref
                == str(ArtifactRef(type="validation_rule", slug=row.slug, version=row.version)),
                ApprovalRequestRow.status == ApprovalStatus.REVIEW.value,
            )
            .order_by(ApprovalRequestRow.submitted_at)
            .limit(1)
        )
    ).scalar_one_or_none()
    if request_id is None:
        raise PlatformError(
            "RULE_NOT_APPROVED",
            "This rule has no open approval request",
            409,
            f"validation_rule:{row.slug}@{row.version} is in review with no open request "
            "to decide. File one with `POST /api/v1/approval-requests` naming it, then "
            "decide that request. `01` §4.5 step 3.",
        )
    return request_id


async def _latest_rule_set_row(
    session: AsyncSession, *, workspace_id: UUID, dataset_id: UUID, slug: str
) -> ValidationRuleSetRow:
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
            "version can be validated (FR-45).",
        )
    return row


async def rule_set_for(
    session: AsyncSession, *, workspace_id: UUID, dataset_id: UUID, slug: str
) -> ValidationRuleSet:
    """The dataset's current rule set, as stored (FR-51).

    A read: it shows a member in `review` so a user can see what to fix, and refuses only
    a member with no rule row. What a *run* may use is `rule_set_to_run`'s.
    """
    row = await _latest_rule_set_row(
        session, workspace_id=workspace_id, dataset_id=dataset_id, slug=slug
    )
    return await _to_rule_set(session, row, workspace_id=workspace_id, dataset_slug=slug)


async def rule_set_to_run(
    session: AsyncSession, *, workspace_id: UUID, dataset_id: UUID, slug: str
) -> ValidationRuleSet:
    """The dataset's current rule set, refused unless every member exists and is approved.

    Every member, enabled or not, as the set's write checks (FD-1414, RL-1407
    (#1070 @24ea2130)): a rule that is not `approved` must not execute (`01` FR-50), and
    skipping it would let a version validate without a check its set declares. Raised
    before the run, so a refused job writes nothing.
    """
    row = await _latest_rule_set_row(
        session, workspace_id=workspace_id, dataset_id=dataset_id, slug=slug
    )
    by_id = await _rules_by_id(
        session, workspace_id=workspace_id, rule_ids=[m.rule_id for m in _members(row)]
    )
    _require_runnable_members(
        [m.rule_id for m in _members(row)], by_id, dataset_slug=slug, approved=True
    )
    return await _to_rule_set(session, row, workspace_id=workspace_id, dataset_slug=slug)


async def _rules_by_id(
    session: AsyncSession, *, workspace_id: UUID, rule_ids: Sequence[UUID]
) -> dict[UUID, ValidationRuleRow]:
    rules = (
        await session.execute(
            select(ValidationRuleRow).where(
                ValidationRuleRow.workspace_id == workspace_id,
                ValidationRuleRow.id.in_(rule_ids),
            )
        )
    ).scalars().all()
    return {rule.id: rule for rule in rules}


def _require_runnable_members(
    rule_ids: Sequence[UUID],
    by_id: dict[UUID, ValidationRuleRow],
    *,
    dataset_slug: str,
    approved: bool,
) -> None:
    """One predicate for the set's write, the run and the read (FD-1414).

    A member with no rule row is `NOT_FOUND` everywhere; a member that is not `approved` is
    `RULE_NOT_APPROVED` where `approved` is asked for (the write and the run, not the
    read). The texts are the maintainer's condition 1 on RL-1407 (#1070 @24ea2130), verbatim:
    each names every offender and the way back.
    """
    missing = sorted({str(rule_id) for rule_id in rule_ids if rule_id not in by_id})
    if missing:
        raise PlatformError(
            "NOT_FOUND",
            "The rule set names rules that do not exist",
            404,
            f"Unknown rule id(s): {', '.join(missing)}. A rule set runs only rules that "
            "exist (`01` FR-50). The way back: replace the rule set without them "
            f"(PUT /api/v1/datasets/{dataset_slug}/rule-set).",
        )
    if not approved:
        return
    unapproved = sorted(
        (by_id[rule_id] for rule_id in set(rule_ids) if by_id[rule_id].status != APPROVED),
        key=lambda rule: (rule.slug, rule.version),
    )
    if unapproved:
        members = ", ".join(f"{r.id} ({r.slug}@{r.version}, {r.status})" for r in unapproved)
        raise PlatformError(
            "RULE_NOT_APPROVED",
            "Every rule in a rule set must be approved",
            409,
            f"Not approved: {members}. A rule set runs only approved rules (`01` FR-50). "
            "The way back, for each rule: attach a new dry run "
            "(POST /api/v1/validation-rules/{id}/dry-run), then submit an approval request "
            "(POST /api/v1/validation-rules/{id}/submit for a draft rule, "
            "POST /api/v1/approval-requests for a rule in review), and have an approver "
            "decide it. Or replace the rule set without it "
            f"(PUT /api/v1/datasets/{dataset_slug}/rule-set).",
        )


@dataclass(frozen=True, slots=True)
class RuleSetMember:
    """What a caller asks for: a rule id, and the two things a set may say about it.

    Distinct from `RuleSetEntry`, which carries the resolved rule. A caller has the id;
    only the service can turn it into a rule, and only after checking it is approved.
    """

    rule_id: UUID
    enabled: bool = True
    severity_override: Severity | None = None


def _members(row: ValidationRuleSetRow) -> list[RuleSetMember]:
    """Read the stored artifact.

    `01` §4.4 stores `rules` with the per-entry fields. Rows written before that shape
    existed carry a bare `rule_ids` list; they are read as all-enabled with no override,
    which is exactly what they meant.
    """
    stored = row.body.get("rules")
    if stored is None:
        return [RuleSetMember(rule_id=UUID(value)) for value in row.body.get("rule_ids", [])]
    return [
        RuleSetMember(
            rule_id=UUID(entry["rule_id"]),
            enabled=bool(entry.get("enabled", True)),
            severity_override=(
                Severity(entry["severity_override"]) if entry.get("severity_override") else None
            ),
        )
        for entry in stored
    ]


async def _to_rule_set(
    session: AsyncSession,
    row: ValidationRuleSetRow,
    *,
    workspace_id: UUID,
    dataset_slug: str,
) -> ValidationRuleSet:
    """Resolve the stored rule ids into the rules they name.

    The set stores ids rather than copies. A copy would let the set and the rule disagree
    about a rule's severity, and the report cites both. A member with no rule row is
    refused, not dropped: showing a smaller set than the one stored is a silent change to
    what a report will be a report of (FD-1414).
    """
    members = _members(row)
    by_id = await _rules_by_id(
        session, workspace_id=workspace_id, rule_ids=[m.rule_id for m in members]
    )
    _require_runnable_members(
        [m.rule_id for m in members], by_id, dataset_slug=dataset_slug, approved=False
    )
    entries = tuple(
        RuleSetEntry(
            rule=to_schema(by_id[member.rule_id]),
            enabled=member.enabled,
            severity_override=member.severity_override,
        )
        for member in members
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
    members: Sequence[RuleSetMember],
    reference_dataset_version_id: UUID | None = None,
) -> ValidationRuleSet:
    """Create the next rule-set version (FR-51).

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

    rule_ids = [member.rule_id for member in members]
    by_id = await _rules_by_id(session, workspace_id=workspace_id, rule_ids=rule_ids)
    _require_runnable_members(rule_ids, by_id, dataset_slug=slug, approved=True)

    # `01` §4.3: an override may only *raise*. `RuleSetEntry` enforces it too, but that
    # would surface here as a 500 — the caller asked for something the platform refuses,
    # which is a 409, and the refusal has to say why.
    lowered = sorted(
        by_id[m.rule_id].slug
        for m in members
        if m.severity_override is Severity.WARN
        and Severity(by_id[m.rule_id].severity) is Severity.FAIL
    )
    if lowered:
        raise PlatformError(
            "RULE_SEVERITY_DOWNGRADE_FORBIDDEN",
            "An override may only raise severity",
            409,
            f"Would lower fail to warn: {', '.join(lowered)}. Deciding a failure is "
            "acceptable is a change to the rule, and goes through the rule's own review "
            "(FR-50) where someone sees it.",
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
        body={
            "rules": [
                {
                    "rule_id": str(member.rule_id),
                    # Informational: a rule version is a row of its own, so the id already
                    # pins the version. Stored so the artifact reads as `01` §4.4 shows it
                    # and a reviewer sees which version without a second lookup.
                    "rule_version": by_id[member.rule_id].version,
                    "enabled": member.enabled,
                    "severity_override": (
                        member.severity_override.value if member.severity_override else None
                    ),
                }
                for member in members
            ]
        },
        reference_dataset_version_id=reference_dataset_version_id,
        status=APPROVED,
    )
    # ALLOWANCE (PL-1303 Acceptance 7): temporary, pending the WK-1178 triage of whether a
    # rule set is ungoverned (`06:64`); the table default is also `approved` (`models.py`).
    async with approvals.approval_decision(session):
        session.add(row)
        await session.flush()

    # `01` §4.1's `validation_rule_set_id`, which nothing set: the row carried
    # `dataset_id` and the dataset never pointed back, so §5.3's "rule set link" had
    # nothing to link to and a reader could not tell a dataset with rules from one without.
    dataset = await session.get(DatasetRow, dataset_id)
    if dataset is not None:
        dataset.validation_rule_set_id = row.id

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="validation_rule_set.replaced",
        entity_ref=f"validation_rule_set:{slug}@{version}",
        after={
            "version": version,
            "rule_ids": [str(r) for r in rule_ids],
            "disabled": [str(m.rule_id) for m in members if not m.enabled],
            "overridden": {
                str(m.rule_id): m.severity_override.value
                for m in members
                if m.severity_override is not None
            },
        },
    )
    return await _to_rule_set(session, row, workspace_id=workspace_id, dataset_slug=slug)
