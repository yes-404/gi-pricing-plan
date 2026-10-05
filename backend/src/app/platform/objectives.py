"""Custom Objectives — authoring, certification, submission and blast radius.

`02` §3.7 (FR-142, FR-144, FR-146, FR-150, FR-163), §4.5 the catalogue, §4.7 the certificate.

Three things about this service are worth reading before using it.

* **The artifact is validated by its contract before the row exists.** `create_objective`
  builds a `CustomObjective` and lets its validators refuse — the template's own parameter
  ranges, an applicability wider than §4.5's, an `expression` objective's missing loss. A row that
  reached the table without passing them would be an objective that fails at fit time, in
  a worker, with a message about NumPy.

* **Certification is a Job.** §4.7's checks end in a smoke fit, which trains a booster; a
  synchronous endpoint would hold a request open across it. What the API answers
  synchronously is everything that can be answered without computing — the permission, the
  status, and whether re-certifying would overwrite the evidence a decision already rests
  on.

* **Permissions are the Model's** — `model:read`, `model:fit`, `model:submit`. `06` §4.1's
  role example names `custom_objective:author` and `custom_objective:submit`, and that
  example also names six other permissions the built `Permission` enum does not have: it
  predates the consolidation where every modelling input write is `model:fit`. Inventing
  two permissions here to match a superseded example would be governance nobody agreed to,
  and would leave every existing role unable to author an objective. Recorded in `06` §4.1
  with this slice, with the date and which side was wrong.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import (
    ApprovalRequestRow,
    CustomObjectiveRow,
    ModelRow,
    ObjectiveCertificateRow,
)
from app.errors import PlatformError
from app.platform import approvals, audit, rbac
from model_schema import (
    TEMPLATE_APPLICABILITY,
    VALID_OBJECTIVE_TRANSITIONS,
    Applicability,
    ApprovalStatus,
    ArtifactRef,
    CertificateOutcome,
    CertificateResult,
    CheckStatus,
    CustomObjective,
    DerivedBlock,
    FieldError,
    HessianStrategy,
    JobSource,
    ObjectiveCertificate,
    ObjectiveKind,
    ObjectiveParameter,
    ObjectiveStatus,
    ObjectiveTemplate,
    ObjectiveUsage,
    ObjectiveUsageModel,
    Permission,
    Principal,
    ResponseKind,
    SamplingSpec,
    new_uuid7,
)
from pricing_core.data.expressions import ExpressionError, GrammarProfile, parse_expression
from pricing_core.modelling.expression_objective import derive

__all__ = [
    "apply_approval_decision",
    "certifiable_or_refuse",
    "create_objective",
    "default_sampling",
    "derive_objective",
    "list_objectives",
    "load_certificate",
    "load_objective",
    "record_certificate",
    "refuse_expression_kind",
    "resolve_ref",
    "submit_for_review",
    "to_certificate",
    "to_objective",
    "usage",
    "usage_counts",
]

#: The seed every certification uses unless the caller names another. Fixed rather than
#: drawn: two certifications of the same objective at different library versions are only
#: comparable if they sampled the same grid, and §4.7 makes the grid part of the evidence.
DEFAULT_SEED = 20260818

#: The responses whose `y` is a probability, and the ones whose `y` is a count. Everything
#: else this module sees is money in minor units, which is three orders of magnitude wider —
#: see `default_sampling`.
_PROBABILITY_RESPONSES = frozenset({ResponseKind.CONVERSION, ResponseKind.RETENTION})
_COUNT_RESPONSES = frozenset({ResponseKind.CLAIM_COUNT})


def to_objective(
    row: CustomObjectiveRow, *, usage_count: int | None = None
) -> CustomObjective:
    """The stored artifact, re-validated on the way out.

    Re-validated rather than trusted, for `to_structure`'s reason: the definition columns
    are JSONB behind a trigger, and every invariant the contract enforces — the template's
    parameters, an applicability inside §4.5's — is one a `SET session_replication_role`
    could have walked past.

    `usage_count` is a keyword the way `datasets.to_schema` takes `latest_version`: a
    per-request aggregate the *caller* computed once for a whole page, passed in rather
    than queried here, because a query here would be one round trip per row — the N+1
    FR-167 names as part of its requirement. Defaulted to `None`, so every route
    that does not count says *not asked* rather than *nothing uses this*.
    """
    return CustomObjective.model_validate(
        {
            "usage_count": usage_count,
            "id": str(row.id),
            "slug": row.slug,
            "version": row.version,
            "kind": row.kind,
            "template": row.template,
            "params": row.params,
            "bound_symbols": row.bound_symbols,
            "parameters": row.parameters,
            "loss": row.loss,
            "derived": row.derived,
            "applicability": row.applicability,
            "hessian_strategy": row.hessian_strategy,
            "hessian_min": row.hessian_min,
            "status": row.status,
            "description": row.description,
            "certificate_id": str(row.certificate_id) if row.certificate_id else None,
            "approval_request_id": (
                str(row.approval_request_id) if row.approval_request_id else None
            ),
        }
    )


def to_certificate(row: ObjectiveCertificateRow) -> ObjectiveCertificate:
    """The stored certificate, re-validated — including `overall` against its own checks."""
    return ObjectiveCertificate.model_validate(
        {
            "id": str(row.id),
            "custom_objective_id": str(row.custom_objective_id),
            "objective_version": row.objective_version,
            "certified_at": row.certified_at.isoformat(),
            "job_id": str(row.job_id) if row.job_id else None,
            "result": row.payload,
        }
    )


async def create_objective(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    template: ObjectiveTemplate | None,
    params: dict[str, float],
    applicability: Applicability | None,
    hessian_strategy: HessianStrategy,
    hessian_min: float,
    description: str | None,
    kind: ObjectiveKind = ObjectiveKind.TEMPLATE,
    bound_symbols: Sequence[str] | None = None,
    parameters: Sequence[ObjectiveParameter] | None = None,
    loss: str | None = None,
) -> CustomObjectiveRow:
    """Create the next version of a Custom Objective, as a `draft` (FR-MODEL-38, 46).

    Versioning is by slug, exactly as a Peril Structure's is: FR-163 makes editing an
    objective a new version requiring fresh certification, and a Model fitted last month
    must still resolve `custom_objective:<slug>@<version>` to the loss it was fitted under.

    `applicability` defaults to the **template's own** rather than to something permissive.
    §4.5 states where each template's derivatives are valid, an author may narrow that and
    may not widen it, and a default of "everything" would invert the direction the contract
    allows movement in.

    An `expression` objective has no template to default from, so its `applicability` is
    required, and its `loss` is parsed in the `objective` profile after the contract has
    accepted the shape: a grammar error is `OBJECTIVE_GRAMMAR_VIOLATION` with its position
    (FR-145), stored as `derived = NULL` until `derive_objective` runs.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_FIT,
    )
    latest = await session.scalar(
        select(CustomObjectiveRow.version)
        .where(
            CustomObjectiveRow.workspace_id == workspace_id,
            CustomObjectiveRow.slug == slug,
        )
        .order_by(CustomObjectiveRow.version.desc())
        .limit(1)
    )
    version = (latest or 0) + 1

    # The contract refuses first, so a rejected objective never reaches the table and the
    # message names the parameter rather than a constraint.
    objective = _validated(
        {
            "id": str(new_uuid7()),
            "slug": slug,
            "version": version,
            "kind": kind.value,
            "template": template.value if template is not None else None,
            "params": params,
            "bound_symbols": list(bound_symbols) if bound_symbols is not None else None,
            "parameters": (
                [p.model_dump(mode="json") for p in parameters] if parameters is not None else None
            ),
            "loss": loss,
            "applicability": (
                applicability.model_dump(mode="json") if applicability is not None else None
            ),
            "hessian_strategy": hessian_strategy.value,
            "hessian_min": hessian_min,
            "description": description,
        },
        template=template,
    )
    if objective.loss is not None:
        _require_the_grammar(
            objective.loss,
            symbols=frozenset(objective.bound_symbols or ())
            | frozenset(p.name for p in objective.parameters or ()),
        )
    row = CustomObjectiveRow(
        id=objective.id,
        workspace_id=workspace_id,
        slug=objective.slug,
        version=objective.version,
        status=ObjectiveStatus.DRAFT.value,
        kind=objective.kind.value,
        template=objective.template.value if objective.template else None,
        params=dict(objective.params),
        bound_symbols=list(objective.bound_symbols) if objective.bound_symbols else None,
        parameters=(
            [p.model_dump(mode="json") for p in objective.parameters]
            if objective.parameters is not None
            else None
        ),
        loss=objective.loss,
        applicability=objective.applicability.model_dump(mode="json"),
        hessian_strategy=objective.hessian_strategy.value,
        hessian_min=objective.hessian_min,
        description=objective.description,
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError:  # pragma: no cover — a concurrent create of the same slug
        raise PlatformError(
            "VALIDATION_FAILED",
            "That objective version already exists",
            409,
            f"{slug}@{version} was created by another request. Retry to take the next "
            "version.",
        ) from None

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="custom_objective.created",
        entity_ref=f"custom_objective:{row.slug}@{row.version}",
        after={
            "status": row.status,
            "template": row.template,
            "params": row.params,
            "hessian_strategy": row.hessian_strategy,
            **({"kind": row.kind, "loss": row.loss} if row.loss is not None else {}),
        },
    )
    return row


def _require_the_grammar(loss: str, *, symbols: frozenset[str]) -> None:
    """FR-145: `loss` parses in the `objective` profile, or 422 with the position in `errors[0]`.

    RL-1362 DP-S3-3: one `FieldError` on `loss`, its message beginning `line <L>, column <C>:`
    with `ExpressionError.lineno` and `col_offset` (1-based column). No problem extension:
    `ProblemDetail` is `extra="forbid"`. A text that does not parse as Python at all is the
    same refusal, positioned by `SyntaxError`, whose `offset` is already 1-based.
    """
    try:
        parse_expression(loss, GrammarProfile.OBJECTIVE, symbols=symbols)
    except ExpressionError as exc:
        line, column = exc.lineno, None if exc.col_offset is None else exc.col_offset + 1
        reason = str(exc)
    except SyntaxError as exc:
        line, column, reason = exc.lineno, exc.offset, exc.msg
    else:
        return
    message = reason if line is None else f"line {line}, column {column}: {reason}"
    raise PlatformError(
        "OBJECTIVE_GRAMMAR_VIOLATION",
        "The loss is outside the objective grammar",
        422,
        "`02` §4.6's `objective` profile refused the loss (FR-145).",
        errors=(FieldError(field="loss", code="OBJECTIVE_GRAMMAR_VIOLATION", message=message),),
    )


async def derive_objective(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, objective_id: UUID
) -> CustomObjectiveRow:
    """Derive and store an `expression` draft's gradient and hessian (FR-144).

    The permissions are the route's (`model:fit` and `custom_objective:author`) and the flag
    is checked before this runs. Refused, 409 `VALIDATION_FAILED` (the module's lifecycle
    code), for a template, a non-`draft` objective, and one already derived: `derived` is
    written once from NULL (the definition trigger), so a second write would be refused by
    the database with a message about a trigger.
    """
    row = await _get_or_404(session, workspace_id=workspace_id, objective_id=objective_id)
    ref = f"{row.slug}@{row.version}"
    if row.kind != ObjectiveKind.EXPRESSION.value or row.loss is None:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Only an expression objective is derived",
            409,
            f"{ref} is a {row.kind} objective; a template's derivatives are analytic.",
        )
    if row.status != ObjectiveStatus.DRAFT.value or row.derived is not None:
        raise PlatformError(
            "VALIDATION_FAILED",
            "This objective cannot be derived in its current state",
            409,
            f"{ref} is {row.status} and "
            f"{'already derived' if row.derived is not None else 'not yet derived'}. "
            "Derivation is written once, on a draft; create the next version to change the loss.",
        )
    try:
        derived = derive(row.loss, parameters=[p["name"] for p in row.parameters or []])
    except ExpressionError as exc:
        raise PlatformError(
            "OBJECTIVE_GRAMMAR_VIOLATION",
            "The loss cannot be derived",
            422,
            str(exc),
            errors=(
                FieldError(field="loss", code="OBJECTIVE_GRAMMAR_VIOLATION", message=str(exc)),
            ),
        ) from exc
    block = DerivedBlock(
        gradient=derived.gradient,
        hessian=derived.hessian,
        derivation_tool="sympy",
        derivation_version=derived.derivation_version,
        derived_at=datetime.now(UTC),
    ).model_dump(mode="json")
    row.derived = block
    await session.flush()
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="custom_objective.derived",
        entity_ref=f"custom_objective:{row.slug}@{row.version}",
        before={"derived": None},
        after={"derived": block},
    )
    return row


async def refuse_expression_kind(
    session: AsyncSession, *, settings: Settings, workspace_id: UUID
) -> None:
    """FR-150: `expression` objectives are behind `features.expression_objectives_enabled`.

    Raises 409 `OBJECTIVE_KIND_NOT_ENABLED` unless the workspace's setting resolves to
    `True`; an unset key resolves to the definition's default, `False`. Better here than at
    the contract alone: `CustomObjective` accepts the kind, and a caller who asked for a
    capability the workspace has not enabled deserves to be told that is what happened.
    """
    from app.platform import settings as settings_service

    resolution = await settings_service.resolve(
        session, settings, workspace_id, "features.expression_objectives_enabled"
    )
    if resolution.effective_value is True:
        return
    raise PlatformError(
        "OBJECTIVE_KIND_NOT_ENABLED",
        "Expression objectives are not available",
        409,
        "`features.expression_objectives_enabled` is off in this workspace (FR-150): it "
        "is off unless set, and an `expression` objective is created and derived only "
        "while it is on.",
    )


async def load_objective(
    session: AsyncSession, *, workspace_id: UUID, objective_id: UUID
) -> CustomObjective:
    """One objective by id."""
    return to_objective(
        await _get_or_404(session, workspace_id=workspace_id, objective_id=objective_id)
    )


async def list_objectives(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    limit: int,
    count_cap: int,
    status: ObjectiveStatus | None = None,
    slug: str | None = None,
    after: UUID | None = None,
) -> tuple[Sequence[CustomObjectiveRow], int]:
    """One page of the workspace's objectives, newest first (FR-167).

    Here rather than in the router, which is where `GET /models` keeps its query: none of
    the three artifact modules' routers imports SQLAlchemy at all, and a router that
    reached for it only here would leave the next person two patterns and no rule.

    `ix_custom_objectives_slug_status` covers `(workspace_id, slug, status)`, so both
    filters are index-served and no migration accompanies this route. `slug` is an
    **equality**: FR-167 makes this filter what resolves §5.3's `slug@version`
    addresses against UUID-only detail routes, and a prefix match would resolve
    `motor-ad` to `motor-ad-severity` as well — a wrong artifact, not a wide result.

    Ids are UUIDv7 and therefore time-ordered, so one column is both the sort and the
    cursor. `limit + 1` rows are fetched: the extra one answers "is there another page?"
    and the caller drops it.

    Returns the rows and the capped total; the router builds the `Page`. No RBAC check —
    unlike `usage`, which is reachable from a Job. Every caller of this arrives through
    `requires(MODEL_READ)`, and a second check on the same request would be a second
    round trip for an answer already given.

    `limit` and `count_cap` are parameters rather than imports because `DEFAULT_LIMIT` and
    `COUNT_CAP` live in `app.api.pagination`, and no module under `app/platform/` imports
    from `app/api/`. Reading them here would invert that direction to save two arguments.
    """
    conditions = [CustomObjectiveRow.workspace_id == workspace_id]
    if status is not None:
        conditions.append(CustomObjectiveRow.status == status.value)
    if slug is not None:
        conditions.append(CustomObjectiveRow.slug == slug)

    query = (
        select(CustomObjectiveRow)
        .where(*conditions)
        .order_by(CustomObjectiveRow.id.desc())
        .limit(limit + 1)
    )
    if after is not None:
        query = query.where(CustomObjectiveRow.id < after)

    rows = (await session.execute(query)).scalars().all()
    total = (
        await session.execute(
            select(func.count()).select_from(
                select(CustomObjectiveRow.id).where(*conditions).limit(count_cap).subquery()
            )
        )
    ).scalar_one()
    return rows, int(total)


async def load_certificate(
    session: AsyncSession, *, workspace_id: UUID, objective_id: UUID
) -> ObjectiveCertificate:
    """The objective's latest certificate (§4.7), or a 404 if it has never been certified.

    The latest rather than the one `certificate_id` names, and they are the same row in
    every case but one: a re-certification that came back `failed` clears the pointer
    (`record_certificate`), and the finding is exactly what a reader is looking for then.
    """
    await _get_or_404(session, workspace_id=workspace_id, objective_id=objective_id)
    row = (
        await session.execute(
            select(ObjectiveCertificateRow)
            .where(
                ObjectiveCertificateRow.workspace_id == workspace_id,
                ObjectiveCertificateRow.custom_objective_id == objective_id,
            )
            .order_by(ObjectiveCertificateRow.certified_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "This objective has not been certified",
            404,
            f"No certificate for objective {objective_id}. POST "
            "/api/v1/custom-objectives/{id}/certify produces one (FR-146).",
        )
    return to_certificate(row)


async def resolve_ref(
    session: AsyncSession, *, workspace_id: UUID, ref: str
) -> CustomObjective:
    """`custom_objective:<slug>@<version>` → the artifact, for the fit path.

    This is the resolution ADR-703 keeps out of `pricing-core`: `fit_gbm` takes the
    objective it is to compile and refuses one whose ref does not match the spec's, but it
    cannot read the store the objective lives in.
    """
    parsed = ArtifactRef.model_validate(ref)
    row = (
        await session.execute(
            select(CustomObjectiveRow).where(
                CustomObjectiveRow.workspace_id == workspace_id,
                CustomObjectiveRow.slug == parsed.slug,
                CustomObjectiveRow.version == parsed.version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Custom objective not found",
            404,
            f"{ref} resolves to no custom objective in this workspace.",
        )
    return to_objective(row)


async def certifiable_or_refuse(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, objective_id: UUID
) -> CustomObjectiveRow:
    """Answer "may this be certified?" before a Job exists (FR-146).

    Gated on `model:fit` rather than `model:read`: this queues a compute Job that samples a
    grid and trains a smoke booster.

    Refused past `certified`. Re-certifying is a normal thing to do — after a library
    upgrade, or on a wider grid — but an objective in `review` or `approved` is one whose
    certificate an approver is reading or has already argued from, and a run that came back
    `failed` would move the evidence under a live decision. Withdraw the submission, or
    create the next version.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_FIT,
    )
    row = await _get_or_404(session, workspace_id=workspace_id, objective_id=objective_id)
    status = ObjectiveStatus(row.status)
    if status not in {ObjectiveStatus.DRAFT, ObjectiveStatus.CERTIFIED}:
        raise PlatformError(
            "VALIDATION_FAILED",
            "This objective cannot be certified in its current status",
            409,
            f"{row.slug}@{row.version} is {row.status}. Certification is what `certified` "
            "rests on (FR-146), and re-running it under review or after approval "
            "would change the evidence a decision was made against. Withdraw the "
            "submission, or create the next version.",
        )
    if row.kind == "expression" and row.derived is None:
        raise PlatformError(
            "VALIDATION_FAILED",
            "This expression objective has not been derived",
            409,
            f"{row.slug}@{row.version} has no derived gradient and hessian to certify. "
            "Run POST /api/v1/custom-objectives/{id}/derive first.",
        )
    return row


def default_sampling(objective: CustomObjective) -> SamplingSpec:
    """§4.7's grid, derived from what the objective says it applies to (FR-153).

    A single default grid would be wrong for most of the catalogue. `y` is a probability
    for `focal_binomial`, a small count for the Poisson family, and money in **minor
    units** for every severity template — spans of 1, 20 and 10⁶ respectively. Sampling a
    severity loss over `y ∈ [0, 1]` would certify it on a domain no claim occupies and
    report the convexity share of a region the fit never visits.

    `f_range` follows from `y_range` rather than being chosen: the templates are log-link,
    §4.7's `minimum_at_truth` looks for the `f` where the gradient vanishes and compares it
    to `log y`, and an `f` range that does not span `log(y_range)` finds no interior minimum
    for most of the sample and returns a `warn` about the grid rather than the objective.
    """
    responses = objective.applicability.responses
    if responses <= _PROBABILITY_RESPONSES:
        # The logistic margin, not the probability: ±6 covers p ∈ [0.0025, 0.9975].
        return SamplingSpec(
            n_points=_DEFAULT_POINTS,
            seed=DEFAULT_SEED,
            y_range=(0.0, 1.0),
            f_range=(-6.0, 6.0),
            w_range=_DEFAULT_WEIGHTS,
        )
    y_high = 20.0 if responses <= _COUNT_RESPONSES else 1_000_000.0
    return SamplingSpec(
        n_points=_DEFAULT_POINTS,
        seed=DEFAULT_SEED,
        y_range=(0.0, y_high),
        f_range=(-5.0, math.ceil(math.log(y_high)) + 1.0),
        w_range=_DEFAULT_WEIGHTS,
    )


async def record_certificate(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    objective_id: UUID,
    result: CertificateResult,
    job_id: UUID | None = None,
) -> tuple[CustomObjectiveRow, ObjectiveCertificateRow]:
    """Persist a certificate and move the objective's status (FR-MODEL-42, 46).

    A `failed` certificate is **recorded and leaves the objective in `draft`** — recorded
    because the finding is the answer the run was asked for, and `draft` because a status
    past it is a claim that the derivatives were proven and they were not.

    A re-certification that fails also **clears `certificate_id`**. Leaving it pointing at
    the passing certificate of a previous run would leave the objective saying its status
    rests on evidence that has since been contradicted; the superseded row stays in
    `objective_certificates`, which is where the history of what was believed when lives.
    """
    row = await _get_or_404(session, workspace_id=workspace_id, objective_id=objective_id)
    before = row.status

    certificate = ObjectiveCertificateRow(
        id=new_uuid7(),
        workspace_id=workspace_id,
        custom_objective_id=row.id,
        objective_version=row.version,
        job_id=job_id,
        payload=result.model_dump(mode="json"),
    )
    session.add(certificate)

    failed = result.overall is CertificateOutcome.FAILED
    row.status = (ObjectiveStatus.DRAFT if failed else ObjectiveStatus.CERTIFIED).value
    row.certificate_id = None if failed else certificate.id
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.SYSTEM if job_id else JobSource.API,
        action="custom_objective.certified",
        entity_ref=f"custom_objective:{row.slug}@{row.version}",
        before={"status": before},
        after={
            "status": row.status,
            "certificate_id": str(certificate.id),
            "overall": result.overall.value,
            "findings": [
                f"{check.name}={check.status.value}"
                for check in result.checks
                if check.status.value != "pass"
            ],
        },
    )
    return row, certificate


async def submit_for_review(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    objective_id: UUID,
    change_summary: str,
) -> tuple[CustomObjectiveRow, ApprovalRequestRow]:
    """`certified → review` and the approval request it exists to create (FR-163).

    The evidence check is `06` R4's, and it is enforced here for `_require_evidence`'s
    reason: the policy names `objective_certificate` for this artifact type, and a policy
    requirement nothing verifies is a tightening that does nothing.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_SUBMIT,
    )
    row = await _get_or_404(session, workspace_id=workspace_id, objective_id=objective_id)
    current = ObjectiveStatus(row.status)
    # RL-1362 DP-S3-3: the predicate is the status. `record_certificate` sets `draft` on a
    # failed certificate and `certified` on a passing one, so `draft` is exactly "no passing
    # certificate for this version". Every other invalid transition keeps VALIDATION_FAILED.
    if current is ObjectiveStatus.DRAFT:
        raise PlatformError(
            "OBJECTIVE_NOT_CERTIFIED",
            "This objective has no passing certificate",
            409,
            f"{row.slug}@{row.version} is a `draft`: certify it (POST "
            "/api/v1/custom-objectives/{id}/certify) before submitting it (FR-146, FR-163).",
        )
    if ObjectiveStatus.REVIEW not in VALID_OBJECTIVE_TRANSITIONS[current]:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Invalid custom objective lifecycle transition",
            409,
            f"{row.slug}@{row.version} is {row.status}; FR-163 reaches `review` from "
            "`certified` only. FR-146 makes the certificate the evidence the "
            "approval reads.",
        )
    await _require_evidence(session, workspace_id=workspace_id, row=row)
    # WK-690 S3 Delta 7 (g): `certificate_id` is a bare pointer (no foreign key), and
    # `_require_evidence` only checks it is set. A pointer to no certificate row is no
    # evidence, and would otherwise read below as "no `violated` finding". It must also be
    # this objective's own certificate, in this workspace: another objective's, or another
    # workspace's, is no evidence for this one (audit A7).
    pointed = await session.get(ObjectiveCertificateRow, row.certificate_id)
    if (
        pointed is None
        or pointed.workspace_id != workspace_id
        or pointed.custom_objective_id != row.id
    ):
        raise PlatformError(
            "VALIDATION_FAILED",
            "The objective's certificate does not exist",
            409,
            f"{row.slug}@{row.version} names certificate {row.certificate_id}, which has "
            "no certificate row: re-certify it (POST /api/v1/custom-objectives/{id}/certify) "
            "before submitting it (FR-146, FR-163).",
        )

    # FR-152 / RL-1362 DP-S3-4: a `violated` convexity check adds one Approver to the
    # policy's count, for both kinds, read from the latest certificate.
    # No certificate row, which only a hand-written row can lack, is no `violated` finding:
    # the rule is the ruling's literal predicate.
    latest = (
        await session.execute(
            select(ObjectiveCertificateRow)
            .where(
                ObjectiveCertificateRow.workspace_id == workspace_id,
                ObjectiveCertificateRow.custom_objective_id == objective_id,
            )
            .order_by(ObjectiveCertificateRow.certified_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    non_convex = latest is not None and any(
        check.name == "convexity" and check.status is CheckStatus.VIOLATED
        for check in to_certificate(latest).result.checks
    )
    request = await approvals.submit(
        session,
        workspace_id=workspace_id,
        submitter=actor,
        artifact_ref=ArtifactRef(
            type="custom_objective", slug=row.slug, version=row.version
        ),
        change_summary=change_summary,
        additional_approvers=1 if non_convex else 0,
    )
    row.status = ObjectiveStatus.REVIEW.value
    row.approval_request_id = request.id
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="custom_objective.submitted",
        entity_ref=f"custom_objective:{row.slug}@{row.version}",
        before={"status": ObjectiveStatus.CERTIFIED.value},
        after={
            "status": ObjectiveStatus.REVIEW.value,
            "approval_request_id": str(request.id),
        },
        justification=change_summary,
    )
    return row, request


async def apply_approval_decision(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    request: ApprovalRequestRow,
) -> CustomObjectiveRow | None:
    """Carry a governance decision into the objective (FR-163, `06` FR-355).

    Returns `None` for a request about anything else, so `_carry_to_the_artifact` drives
    every artifact type through one call. Same transaction as the decision, for
    `apply_approval_decision`'s reason on a Model: an objective left in `review` after its
    request reached `approved` is one no model may be approved under and no screen can
    explain.

    `changes_requested` returns the objective to **`certified`**, not to `draft`. `06`
    FR-355 returns the artifact to its pre-submission state, and for a certified
    objective that is `certified` — a review decision does not withdraw a certificate.
    """
    if request.artifact_type != "custom_objective":
        return None

    ref = ArtifactRef.model_validate(request.artifact_ref)
    row = (
        await session.execute(
            select(CustomObjectiveRow)
            .where(
                CustomObjectiveRow.workspace_id == workspace_id,
                CustomObjectiveRow.slug == ref.slug,
                CustomObjectiveRow.version == ref.version,
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if row is None:
        # Tolerated for the reason a Model's is: `POST /approval-requests` accepts any
        # well-formed ref, and a request naming an objective that was never created must
        # still be decidable rather than sitting open for ever (`06` FR-386).
        return None

    target = _target_status(ApprovalStatus(request.status))
    if target is None or ObjectiveStatus(row.status) is target:
        # A partial approval: the policy wants another approver and nothing has moved.
        return row

    before = ObjectiveStatus(row.status)
    if target not in VALID_OBJECTIVE_TRANSITIONS[before]:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Invalid custom objective lifecycle transition",
            409,
            f"{ref} is {before.value} and the decision would move it to {target.value}, "
            "which FR-163 does not allow.",
        )
    row.status = target.value
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=f"custom_objective.{target.value}",
        entity_ref=str(ref),
        before={"status": before.value},
        after={"status": target.value, "approval_request_id": str(request.id)},
    )
    return row


async def usage(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, objective_id: UUID
) -> ObjectiveUsage:
    """FR-164's blast radius: everything fitted under this objective version.

    Asked model→objective, which is the direction the reference runs: a Model Spec carries
    `custom_objective:<slug>@<version>` and the objective row carries no list anything
    writes back. A stored list would be the thing that goes stale exactly when it matters —
    a defect is found, and the answer to "what did we price with this?" must be derived
    from what the models actually say.

    Not paginated, deliberately: this is read when a defect is found, and a truncated blast
    radius is the one answer here worse than a slow one.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_READ,
    )
    row = await _get_or_404(session, workspace_id=workspace_id, objective_id=objective_id)
    ref = f"custom_objective:{row.slug}@{row.version}"

    models = (
        (
            await session.execute(
                select(ModelRow)
                .where(
                    ModelRow.workspace_id == workspace_id,
                    ModelRow.spec["objective"]["ref"].astext == ref,
                )
                .order_by(ModelRow.model_family_slug, ModelRow.version)
            )
        )
        .scalars()
        .all()
    )
    return ObjectiveUsage(
        custom_objective_id=row.id,
        slug=row.slug,
        version=row.version,
        status=ObjectiveStatus(row.status),
        models=tuple(
            ObjectiveUsageModel(
                model_id=model.id,
                model_family_slug=model.model_family_slug,
                version=model.version,
                status=model.status,
                dataset_version_id=UUID(str(model.spec["dataset_version_id"])),
            )
            for model in models
        ),
    )


async def usage_counts(
    session: AsyncSession, *, workspace_id: UUID, refs: Sequence[str]
) -> dict[str, int]:
    """Count the Model Specs referencing each of `refs`, in **one** query (FR-167).

    The library row's count, not the detail route's blast radius: same question, page-sized
    answer. `usage` above answers it for one artifact and is deliberately not reused here —
    calling it per row is the N+1 FR-167 names as part of the requirement, and it
    would be indistinguishable from this until a workspace held a few hundred artifacts.

    **It counts exactly what `usage` counts**, because a row and its own detail route
    disagreeing about one artifact is worse than either being absent:

    * scoped by `workspace_id` and nothing else, as `usage`'s query is;
    * **no status filter on the Model** — `usage` counts a `draft` and an `archived` model
      alongside a `fitted` one, so this does too. "Referencing" is a property of the spec,
      not of where the model got to.

    A ref no model references is **absent** from the result rather than zero: the caller
    supplies the zero, so a bug that drops a ref cannot present as a genuine zero.

    `spec` is one JSONB column and `objective.ref` is a top-level scalar inside it, so this
    is an equality on an extracted text value. There is no index on `models.spec` today; at
    Phase 1b's scale the sequential scan is well inside budget, and the note is here so the
    next person reads a decision rather than an oversight.

    An empty page asks the database nothing — the caller's first screen of an empty
    workspace should not cost a round trip.
    """
    if not refs:
        return {}
    ref_column = ModelRow.spec["objective"]["ref"].astext
    rows = await session.execute(
        select(ref_column, func.count())
        .where(ModelRow.workspace_id == workspace_id, ref_column.in_(list(refs)))
        .group_by(ref_column)
    )
    return {ref: count for ref, count in rows.all()}


# -- internals -----------------------------------------------------------------------------

#: §4.7's default grid size and weight span. 2 000 points is what `_derivative_checks`
#: needs to see the tail of a piecewise loss without making certification a minute's work;
#: weights span two orders because an exposure column in years and one in policy-months are
#: both normal.
_DEFAULT_POINTS = 2_000
_DEFAULT_WEIGHTS = (0.01, 10.0)


def _validated(payload: dict[str, Any], *, template: ObjectiveTemplate | None) -> CustomObjective:
    """`CustomObjective` or a 422 that names what the template actually allows.

    The contract's validators carry the explanation — §4.5's parameter ranges, the
    applicability rule, FR-150 — so the refusal quotes them rather than restating
    them differently.
    """
    if payload.get("applicability") is None:
        if template is None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "An expression objective states its applicability",
                422,
                "There is no template to default `applicability` from (§4.5), so an "
                "`expression` objective names the responses and backends it applies to.",
            )
        payload["applicability"] = TEMPLATE_APPLICABILITY[template].model_dump(mode="json")
    try:
        return CustomObjective.model_validate(payload)
    except ValueError as exc:
        raise PlatformError(
            "VALIDATION_FAILED",
            "This custom objective is not valid",
            422,
            f"{exc}",
        ) from exc


async def _get_or_404(
    session: AsyncSession, *, workspace_id: UUID, objective_id: UUID
) -> CustomObjectiveRow:
    row = await session.get(CustomObjectiveRow, objective_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "Custom objective not found",
            404,
            f"No custom objective {objective_id} in this workspace.",
        )
    return row


async def _require_evidence(
    session: AsyncSession, *, workspace_id: UUID, row: CustomObjectiveRow
) -> None:
    """`06` R4 and FR-352 for this artifact type, failing closed on what it cannot check.

    `_require_evidence` on a Model carries the reasoning; the shape is the same and the
    difference is only which kinds are verifiable here.
    """
    policy = await approvals.policy_for(session, workspace_id)

    verifiable = {"objective_certificate": row.certificate_id is not None}
    #: FR-364: `06` §3.3's floor unioned with the workspace entry, so an edited policy
    #: cannot drop the certificate that `02` FR-146 makes the thing an approver reads.
    missing = [
        kind
        for kind in policy.effective_evidence("custom_objective")
        if not verifiable.get(kind, False)
    ]
    if missing:
        unknown = [kind for kind in missing if kind not in verifiable]
        detail = (
            f"{row.slug}@{row.version} is missing required evidence: {', '.join(missing)}. "
            "`06` FR-363 defines it per artifact type and R4 makes it a condition of "
            "submission. FR-146: certification is what an approver reads."
        )
        if unknown:
            detail += (
                f" This build cannot verify {', '.join(unknown)} — treating an uncheckable "
                "requirement as met would make a policy tightening do nothing."
            )
        raise PlatformError("EVIDENCE_INCOMPLETE", "Required evidence is missing", 422, detail)


def _target_status(request_status: ApprovalStatus) -> ObjectiveStatus | None:
    """What a request's status means for the objective behind it.

    The three non-approvals return it to **`certified`** rather than to `draft`, which is
    the same amendment `06` FR-355 already carries for a Model (2026-08-17) and for the
    same shape of reason: FR-355's `draft` is the pre-submission state, and for a
    certified objective that is `certified`. Sending it to `draft` would say the
    certificate had been withdrawn, which no review decision does.
    """
    return {
        ApprovalStatus.APPROVED: ObjectiveStatus.APPROVED,
        ApprovalStatus.CHANGES_REQUESTED: ObjectiveStatus.CERTIFIED,
        ApprovalStatus.REJECTED: ObjectiveStatus.CERTIFIED,
        ApprovalStatus.WITHDRAWN: ObjectiveStatus.CERTIFIED,
    }.get(request_status)
