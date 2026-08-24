"""Custom Objectives — authoring, certification, submission and blast radius.

`02` §3.7 (FR-MODEL-38, 42, 44, 46, 47, 75), §4.5 the catalogue, §4.7 the certificate.

Three things about this service are worth reading before using it.

* **The artifact is validated by its contract before the row exists.** `create_objective`
  builds a `CustomObjective` and lets its validators refuse — the template's own parameter
  ranges, an applicability wider than §4.5's, a kind Phase 1 does not ship. A row that
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
from typing import Any, NoReturn
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
    CustomObjective,
    HessianStrategy,
    JobSource,
    ObjectiveCertificate,
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

__all__ = [
    "apply_approval_decision",
    "certifiable_or_refuse",
    "create_objective",
    "default_sampling",
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


def to_objective(row: CustomObjectiveRow) -> CustomObjective:
    """The stored artifact, re-validated on the way out.

    Re-validated rather than trusted, for `to_structure`'s reason: the definition columns
    are JSONB behind a trigger, and every invariant the contract enforces — the template's
    parameters, an applicability inside §4.5's — is one a `SET session_replication_role`
    could have walked past.
    """
    return CustomObjective.model_validate(
        {
            "id": str(row.id),
            "slug": row.slug,
            "version": row.version,
            "kind": row.kind,
            "template": row.template,
            "params": row.params,
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
    template: ObjectiveTemplate,
    params: dict[str, float],
    applicability: Applicability | None,
    hessian_strategy: HessianStrategy,
    hessian_min: float,
    description: str | None,
) -> CustomObjectiveRow:
    """Create the next version of a Custom Objective, as a `draft` (FR-MODEL-38, 46).

    Versioning is by slug, exactly as a Peril Structure's is: FR-MODEL-46 makes editing an
    objective a new version requiring fresh certification, and a Model fitted last month
    must still resolve `custom_objective:<slug>@<version>` to the loss it was fitted under.

    `applicability` defaults to the **template's own** rather than to something permissive.
    §4.5 states where each template's derivatives are valid, an author may narrow that and
    may not widen it, and a default of "everything" would invert the direction the contract
    allows movement in.
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
            "template": template.value,
            "params": params,
            "applicability": (
                applicability.model_dump(mode="json") if applicability is not None else None
            ),
            "hessian_strategy": hessian_strategy.value,
            "hessian_min": hessian_min,
            "description": description,
        },
        template=template,
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
        },
    )
    return row


async def refuse_expression_kind(
    session: AsyncSession, *, settings: Settings, workspace_id: UUID
) -> NoReturn:
    """FR-MODEL-75: `expression` objectives are Phase 2, and the flag is how it is said.

    Two refusals, and the second is the one that matters. With the flag **off** — its
    default, and its value for the whole of Phase 1 — this is the feature gate `07`
    FR-PLAT-45/46 describes. With the flag **on**, it still refuses, because turning a flag
    on cannot build the symbolic derivation, the second compilation target and the review
    path that an expression objective needs; accepting one then would persist an artifact
    nothing can evaluate and no certificate can describe.

    Better here than at the contract alone: `CustomObjective` refuses the kind too, but its
    message is about a shape, and a caller who asked for a Phase 2 capability deserves to be
    told that is what happened.
    """
    from app.platform import settings as settings_service

    resolution = await settings_service.resolve(
        session, settings, workspace_id, "features.expression_objectives_enabled"
    )
    enabled = bool(resolution.effective_value)

    detail = (
        "`02` FR-MODEL-75 and OQ-MODEL-1 (decided 2026-08-15): Phase 1 ships `template` "
        "objectives only. §4.6's grammar is specified and its parser is built, but the "
        "symbolic derivation of gradient and hessian, the vectorised compilation target "
        "and the review path for a user-authored loss are not — so an expression objective "
        "would be an artifact nothing could certify or fit."
    )
    if enabled:
        detail += (
            " `features.expression_objectives_enabled` is on in this workspace, and it "
            "gates a capability that does not exist yet rather than one being withheld."
        )
    raise PlatformError(
        "OBJECTIVE_KIND_NOT_ENABLED",
        "Expression objectives are not available",
        409,
        detail,
    )


async def load_objective(
    session: AsyncSession, *, workspace_id: UUID, objective_id: UUID
) -> CustomObjective:
    """One objective by id."""
    return to_objective(
        await _get_or_404(session, workspace_id=workspace_id, objective_id=objective_id)
    )


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
            "/api/v1/custom-objectives/{id}/certify produces one (FR-MODEL-42).",
        )
    return to_certificate(row)


async def resolve_ref(
    session: AsyncSession, *, workspace_id: UUID, ref: str
) -> CustomObjective:
    """`custom_objective:<slug>@<version>` → the artifact, for the fit path.

    This is the resolution ADR-0001 keeps out of `pricing-core`: `fit_gbm` takes the
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
    """Answer "may this be certified?" before a Job exists (FR-MODEL-42).

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
            "rests on (FR-MODEL-42), and re-running it under review or after approval "
            "would change the evidence a decision was made against. Withdraw the "
            "submission, or create the next version.",
        )
    return row


def default_sampling(objective: CustomObjective) -> SamplingSpec:
    """§4.7's grid, derived from what the objective says it applies to (FR-MODEL-44).

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
    """`certified → review` and the approval request it exists to create (FR-MODEL-46).

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
    if ObjectiveStatus.REVIEW not in VALID_OBJECTIVE_TRANSITIONS[current]:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Invalid custom objective lifecycle transition",
            409,
            f"{row.slug}@{row.version} is {row.status}; FR-MODEL-46 reaches `review` from "
            "`certified` only. FR-MODEL-42 makes the certificate the evidence the "
            "approval reads.",
        )
    await _require_evidence(session, workspace_id=workspace_id, row=row)

    request = await approvals.submit(
        session,
        workspace_id=workspace_id,
        submitter=actor,
        artifact_ref=ArtifactRef(
            type="custom_objective", slug=row.slug, version=row.version
        ),
        change_summary=change_summary,
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
    """Carry a governance decision into the objective (FR-MODEL-46, `06` FR-GOV-13).

    Returns `None` for a request about anything else, so `_carry_to_the_artifact` drives
    every artifact type through one call. Same transaction as the decision, for
    `apply_approval_decision`'s reason on a Model: an objective left in `review` after its
    request reached `approved` is one no model may be approved under and no screen can
    explain.

    `changes_requested` returns the objective to **`certified`**, not to `draft`. `06`
    FR-GOV-13 returns the artifact to its pre-submission state, and for a certified
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
        # still be decidable rather than sitting open for ever (`06` FR-GOV-36).
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
            "which FR-MODEL-46 does not allow.",
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
    """FR-MODEL-47's blast radius: everything fitted under this objective version.

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
    """Count the Model Specs referencing each of `refs`, in **one** query (FR-MODEL-127).

    The library row's count, not the detail route's blast radius: same question, page-sized
    answer. `usage` above answers it for one artifact and is deliberately not reused here —
    calling it per row is the N+1 FR-MODEL-127 names as part of the requirement, and it
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


def _validated(payload: dict[str, Any], *, template: ObjectiveTemplate) -> CustomObjective:
    """`CustomObjective` or a 422 that names what the template actually allows.

    The contract's validators carry the explanation — §4.5's parameter ranges, the
    applicability rule, FR-MODEL-75 — so the refusal quotes them rather than restating
    them differently.
    """
    if payload.get("applicability") is None:
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
    """`06` R4 and FR-GOV-10 for this artifact type, failing closed on what it cannot check.

    `_require_evidence` on a Model carries the reasoning; the shape is the same and the
    difference is only which kinds are verifiable here.
    """
    policy = await approvals.policy_for(session, workspace_id)

    verifiable = {"objective_certificate": row.certificate_id is not None}
    #: FR-GOV-37: `06` §3.3's floor unioned with the workspace entry, so an edited policy
    #: cannot drop the certificate that `02` FR-MODEL-42 makes the thing an approver reads.
    missing = [
        kind
        for kind in policy.effective_evidence("custom_objective")
        if not verifiable.get(kind, False)
    ]
    if missing:
        unknown = [kind for kind in missing if kind not in verifiable]
        detail = (
            f"{row.slug}@{row.version} is missing required evidence: {', '.join(missing)}. "
            "`06` FR-GOV-19 defines it per artifact type and R4 makes it a condition of "
            "submission. FR-MODEL-42: certification is what an approver reads."
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
    the same amendment `06` FR-GOV-13 already carries for a Model (2026-08-17) and for the
    same shape of reason: FR-GOV-13's `draft` is the pre-submission state, and for a
    certified objective that is `certified`. Sending it to `draft` would say the
    certificate had been withdrawn, which no review decision does.
    """
    return {
        ApprovalStatus.APPROVED: ObjectiveStatus.APPROVED,
        ApprovalStatus.CHANGES_REQUESTED: ObjectiveStatus.CERTIFIED,
        ApprovalStatus.REJECTED: ObjectiveStatus.CERTIFIED,
        ApprovalStatus.WITHDRAWN: ObjectiveStatus.CERTIFIED,
    }.get(request_status)
