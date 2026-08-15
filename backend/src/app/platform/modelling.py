"""Factors and Models: the governance around a fit (`02` §3.1, §3.4, §1.3).

`pricing-core` owns the maths; this owns the rules that make a fitted model mean something.
Three of them, each stated by `02` §1.3 and none of which a caller can route around:

* **R1 — fitting requires a `validated` Dataset Version.** The check is `01`'s own
  `fittable_or_refuse`, called here rather than reimplemented, so there is one place that
  answers "may I fit on this?".
* **R2 — a Model is immutable once fitted.** A refit allocates the next version with
  `parent_model_id` set. Nothing here updates a `fit_result`.
* **FR-MODEL-66 — the same specification does not fit twice.** `spec_hash` is unique per
  workspace, so a resubmitted spec returns the model that already exists.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FactorRow, ModelRow
from app.errors import PlatformError
from app.platform import audit, datasets, rbac
from model_schema import (
    Factor,
    GlmFitResult,
    GlmSpec,
    JobSource,
    Model,
    ModelStatus,
    Permission,
    Principal,
)

__all__ = [
    "create_factor",
    "list_factors",
    "load_factors",
    "load_model",
    "record_fit",
    "reserve_model",
    "spec_hash",
    "to_factor",
    "to_model",
]


def spec_hash(spec: GlmSpec) -> str:
    """A stable digest of the specification (FR-MODEL-66).

    Over the model's JSON with sorted keys, so two specs that differ only in field order
    are one spec — and two that differ anywhere at all, including a loss treatment or a
    seed, are two. `02` §4.4 is explicit that a cap belongs *inside* the spec for exactly
    this reason: two models differing only in their cap must not collide.
    """
    payload = json.dumps(spec.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}"


def to_factor(row: FactorRow) -> Factor:
    return Factor.model_validate({**row.body, "id": row.id, "version": row.version,
                                  "dataset_id": row.dataset_id})


def to_model(row: ModelRow) -> Model:
    return Model(
        id=row.id,
        model_family_slug=row.model_family_slug,
        version=row.version,
        status=ModelStatus(row.status),
        spec=GlmSpec.model_validate(row.spec),
        spec_hash=row.spec_hash,
        fit_result=GlmFitResult.model_validate(row.fit_result) if row.fit_result else None,
        dataset_version_id=row.dataset_version_id,
        parent_model_id=row.parent_model_id,
        change_reason=row.change_reason,
    )


async def create_factor(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    factor: Factor,
) -> FactorRow:
    """Author a Factor, or allocate the next version of an existing slug (FR-MODEL-7).

    Versioned rather than edited, for the reason a Model Spec pins a factor *version*: an
    edited factor would silently change what every model fitted on it was fitted on.
    """
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )

    version = 1 + (
        await session.execute(
            select(func.coalesce(func.max(FactorRow.version), 0)).where(
                FactorRow.workspace_id == workspace_id, FactorRow.slug == factor.slug
            )
        )
    ).scalar_one()

    body = factor.model_dump(mode="json", exclude={"id", "version", "dataset_id"})
    row = FactorRow(
        workspace_id=workspace_id,
        dataset_id=factor.dataset_id,
        slug=factor.slug,
        version=version,
        body=body,
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="factor.created",
        entity_ref=f"factor:{factor.slug}@{version}",
        after={"slug": factor.slug, "version": version, "type": factor.type.value,
               "intent": factor.intent.value, "prohibited": factor.prohibited},
    )
    return row


async def list_factors(
    session: AsyncSession, *, workspace_id: UUID, dataset_id: UUID | None = None
) -> list[FactorRow]:
    conditions = [FactorRow.workspace_id == workspace_id]
    if dataset_id is not None:
        conditions.append(FactorRow.dataset_id == dataset_id)
    return list(
        (
            await session.execute(
                select(FactorRow).where(*conditions).order_by(
                    FactorRow.slug, FactorRow.version.desc()
                )
            )
        ).scalars()
    )


async def load_factors(
    session: AsyncSession, *, workspace_id: UUID, factor_ids: list[UUID]
) -> list[Factor]:
    """The factors a spec pins, in the order it pins them.

    Order is the spec's, not the database's: the design matrix's column order follows it,
    and a fit whose columns reordered between runs would produce a different `spec_hash`
    for the same model.
    """
    rows = (
        await session.execute(
            select(FactorRow).where(
                FactorRow.workspace_id == workspace_id, FactorRow.id.in_(factor_ids)
            )
        )
    ).scalars().all()
    by_id = {row.id: row for row in rows}
    missing = [str(fid) for fid in factor_ids if fid not in by_id]
    if missing:
        raise PlatformError(
            "NOT_FOUND",
            "The spec names factors that do not exist",
            404,
            f"Unknown factor id(s): {', '.join(missing)}.",
        )
    return [to_factor(by_id[fid]) for fid in factor_ids]


async def reserve_model(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    spec: GlmSpec,
    change_reason: str | None = None,
) -> tuple[ModelRow, bool]:
    """Allocate the model row a fit will populate, or return the one that exists.

    Returns `(row, should_fit)` — **not** `(row, created)`. The two came apart when a
    failed fit was found to poison its `spec_hash` slot for ever: the row exists, so
    nothing new is created, and a Job must still be queued because the row has no numbers.
    Callers want to know whether to queue, which is the question this answers.

    **R1 is checked here**, before a Job is queued: refusing after the queue hop would mean
    a worker discovers the dataset is not validated and the caller learns it from a failed
    job instead of a `409`. It is checked *again* in the handler, because the version can
    lose its standing while the Job sits in the queue.
    """
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )
    dataset_version = await datasets.fittable_or_refuse(
        session, workspace_id=workspace_id, version_id=spec.dataset_version_id
    )
    await _refuse_unusable_factors(
        session, workspace_id=workspace_id, spec=spec, dataset_id=dataset_version.dataset_id
    )

    digest = spec_hash(spec)
    existing = (
        await session.execute(
            select(ModelRow).where(
                ModelRow.workspace_id == workspace_id, ModelRow.spec_hash == digest
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        # FR-MODEL-66. Not an error: the caller asked for a model with this specification
        # and that model exists. Fitting it again would burn a worker to produce the same
        # numbers under a new id, and leave two versions nobody can choose between.
        #
        # **Unless it never got any numbers.** A fit that failed — an unreachable blob, a
        # rank-deficient design, a worker that died — used to leave the row behind and
        # every resubmission was told "your model exists" for a model that could never
        # have coefficients. An unfitted reservation is returned as *not* created, so the
        # caller queues another Job against the same row.
        return existing, existing.fit_result is None

    version = 1 + (
        await session.execute(
            select(func.coalesce(func.max(ModelRow.version), 0)).where(
                ModelRow.workspace_id == workspace_id,
                ModelRow.model_family_slug == spec.model_family_slug,
            )
        )
    ).scalar_one()

    parent = (
        await session.execute(
            select(ModelRow.id)
            .where(
                ModelRow.workspace_id == workspace_id,
                ModelRow.model_family_slug == spec.model_family_slug,
                ModelRow.version == version - 1,
            )
        )
    ).scalar_one_or_none()

    row = ModelRow(
        workspace_id=workspace_id,
        model_family_slug=spec.model_family_slug,
        version=version,
        status=ModelStatus.DRAFT.value,
        dataset_version_id=spec.dataset_version_id,
        spec=spec.model_dump(mode="json"),
        spec_hash=digest,
        parent_model_id=parent,
        change_reason=change_reason,
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="model.reserved",
        entity_ref=f"model:{spec.model_family_slug}@{version}",
        after={"version": version, "spec_hash": digest,
               "dataset_version_id": str(spec.dataset_version_id),
               "parent_model_id": str(parent) if parent else None},
    )
    return row, True


async def _refuse_unusable_factors(
    session: AsyncSession, *, workspace_id: UUID, spec: GlmSpec, dataset_id: UUID
) -> None:
    """FR-MODEL-5 and FR-MODEL-2, at the attempt rather than in the worker.

    Both were enforced inside `pricing-core` at fit time, which is after a model row, a
    version number, a `spec_hash` slot, an audit event and a queued Job already exist. A
    prohibited factor is meant to be *refused*, and a refusal that arrives as a failed job
    is a record of the attempt succeeding.

    `FACTOR_PROHIBITED` is raised here — it was a registered code that nothing raised, in
    the same commit whose registry says it holds only codes something can raise.
    """
    if not spec.factors:
        return

    factors = await load_factors(session, workspace_id=workspace_id, factor_ids=list(spec.factors))

    prohibited = [f for f in factors if f.prohibited]
    if prohibited:
        detail = ", ".join(f"{f.slug} ({f.prohibited_reason})" for f in prohibited)
        raise PlatformError(
            "FACTOR_PROHIBITED",
            "The spec names a prohibited factor",
            409,
            f"{detail}. FR-MODEL-5: a prohibited Factor cannot be added to any Model Spec. "
            "Lifting a prohibition is a change to the Factor, not to the model that wanted "
            "it.",
        )

    # FR-MODEL-2: a Factor is defined against a **Dataset**. A factor from another dataset
    # fits whenever the column names happen to coincide — which in this domain is the norm
    # rather than the exception, and the resulting model cites a factor that was never
    # about this data.
    foreign = [f for f in factors if f.dataset_id != dataset_id]
    if foreign:
        detail = ", ".join(f"{f.slug} (dataset {f.dataset_id})" for f in foreign)
        raise PlatformError(
            "FACTOR_RESOLUTION_FAILED",
            "The spec names factors defined against a different dataset",
            409,
            f"{detail} against dataset {dataset_id}. FR-MODEL-2 defines a Factor against a "
            "Dataset; matching column names elsewhere do not make it the same variable.",
        )


async def record_fit(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    model_id: UUID,
    fit_result: GlmFitResult,
    job_id: UUID | None = None,
) -> ModelRow:
    """Write the numbers a fit produced, once (R2).

    Refuses a model that already carries a `fit_result`: R2 makes a Model immutable once
    fitted, and "refit" means a new version, not new coefficients on the old one. Without
    this the rule would hold only for callers who remembered it.
    """
    # `FOR UPDATE`, not a plain read. This is a check-then-act, and two Jobs naming one
    # model — nothing forbids submitting two — both read `fit_result IS NULL` and both
    # wrote, the second silently overwriting a fitted model's coefficients. R2 held only
    # for callers who arrived one at a time.
    row = (
        await session.execute(
            select(ModelRow).where(ModelRow.id == model_id).with_for_update()
        )
    ).scalar_one_or_none()
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError("NOT_FOUND", "Model not found", 404, f"No model {model_id}.")
    if row.fit_result is not None:
        raise PlatformError(
            "MODEL_IMMUTABLE",
            "This model is already fitted",
            409,
            f"{row.model_family_slug}@{row.version} carries a fit result. `02` R2: a Model "
            "is immutable once fitted — refitting produces a new version with "
            "`parent_model_id` set, never new coefficients on an existing one.",
        )

    row.fit_result = fit_result.model_dump(mode="json")
    row.status = ModelStatus.FITTED.value
    row.job_id = job_id
    await session.flush()

    intercept = fit_result.intercept
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.SYSTEM if job_id else JobSource.API,
        action="model.fitted",
        entity_ref=f"model:{row.model_family_slug}@{row.version}",
        after={
            "converged": fit_result.converged,
            "rows": fit_result.rows,
            "terms": len(fit_result.coefficients),
            "intercept": intercept.estimate if intercept else None,
        },
    )
    return row


async def load_model(
    session: AsyncSession, *, workspace_id: UUID, slug: str, version: int | None = None
) -> ModelRow:
    """A model by family slug and version, latest if no version is given."""
    query = select(ModelRow).where(
        ModelRow.workspace_id == workspace_id, ModelRow.model_family_slug == slug
    )
    query = (
        query.where(ModelRow.version == version)
        if version is not None
        else query.order_by(ModelRow.version.desc()).limit(1)
    )
    row = (await session.execute(query)).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Model not found",
            404,
            f"No model {slug!r}" + (f" version {version}." if version else "."),
        )
    return row


def fit_payload(row: ModelRow) -> dict[str, Any]:
    """What the `model.fit` Job carries: the model to fill in, and nothing else."""
    return {"model_id": str(row.id), "workspace_id": str(row.workspace_id)}
