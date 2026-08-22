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

import dataclasses
import hashlib
import json
from collections.abc import Mapping
from typing import Any, Final
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalRequestRow,
    DatasetVersionRow,
    DiagnosticsRow,
    FactorRow,
    ModelRow,
    TransparencyArtifactRow,
)
from app.errors import PlatformError
from app.platform import approvals, audit, datasets, rbac, transformations
from model_schema import (
    FIT_RESULT_ADAPTER,
    MODEL_SPEC_ADAPTER,
    VALID_MODEL_TRANSITIONS,
    ApprovalStatus,
    ArtifactRef,
    Banding,
    DatasetStatus,
    Diagnostics,
    EbmFitResult,
    Factor,
    FactorType,
    FitResult,
    GbmFitResult,
    GbmSpec,
    GlmFitResult,
    GlmSpec,
    Grouping,
    JobSource,
    Model,
    ModelFlag,
    ModelSpec,
    ModelStatus,
    ObjectiveTemplate,
    Permission,
    Principal,
)
from pricing_core.modelling.factors import FactorResolutionError

__all__ = [
    "SPEC_HASH_VERSION",
    "OffsetModelSource",
    "apply_approval_decision",
    "archive",
    "create_factor",
    "flags_for",
    "list_factors",
    "load_factors",
    "load_interval_models",
    "load_model",
    "load_model_by_id",
    "record_fit",
    "reserve_model",
    "resolve_offset_model",
    "spec_hash",
    "spec_hash_is_current",
    "submit_for_review",
    "to_factor",
    "to_model",
]


#: The version of the `spec_hash` *algorithm*, carried inside the hashed payload and
#: printed at the front of every digest.
#:
#: **Bump this whenever any arm of `ModelSpec` gains, loses or renames a field.** Adding a
#: field changes the JSON the digest is taken over, so every stored digest silently stops
#: matching its own specification — a resubmitted spec then looks new, FR-MODEL-66's dedup
#: quietly ends, and the same model is fitted twice under two versions with nothing to say
#: why. OQ-MODEL-8 named this as the constraint to satisfy *before* the first new field
#: lands.
#:
#: The tag does not prevent the change; it makes it **legible**. A `v1:` digest in a
#: database this code no longer produces is a row that needs backfilling, and it can be
#: found with a `LIKE 'v1:%'`. An untagged digest cannot be found at all.
#: **v2, 2026-08-16** — `GlmSpec` gained `split_ref` with the diagnostics slice. Every `v1:`
#: digest in the database describes a spec this build would hash differently, so a `v1:`
#: model resubmitted today looks new. That is the documented cost of the field, paid
#: visibly: `spec_hash_is_current` reports the stale rows and `LIKE 'v1:%'` finds them.
#: **v3, 2026-08-17** — `02` §4.4's common block gained `loss_treatment` with the GBM
#: slice (FR-MODEL-73). It sits on the common block rather than on the GBM arm because
#: capping is a property of the *response*, and a field defined on one arm of a union is a
#: field that will be spelled differently on the other. The cost is the same as v2's and is
#: paid the same way: every `v2:` digest describes a spec this build hashes differently, so
#: a `v2:` model resubmitted today looks new. `spec_hash_is_current` reports them and
#: `LIKE 'v2:%'` finds them.
#: `interval_for` moved it `v3` to `v4` (2026-08-19, FR-MODEL-100): a bound's link to
#: the model it bounds is part of that model's identity, so it joins the payload.
#: `approximates_model_id` moved it `v4` to `v5` (2026-08-19, FR-MODEL-96): the model a
#: surrogate approximates is part of what that surrogate is, and two approximations of two
#: different GBMs over one population would otherwise share a digest — which FR-MODEL-66
#: answers by handing the second caller the first caller's model. Every `v4:` digest is
#: findable with `LIKE 'v4:%'` and reported stale by `spec_hash_is_current`.
#: `select_by`/`cv` moved it `v5` to `v6` (2026-08-21, FR-MODEL-20/53): how the fit is
#: selected — one alpha, or a CV scan of `cv.alphas` — is part of the fitted question,
#: and two specs differing there must not share a digest or FR-MODEL-66 answers the
#: second caller with the first caller's model. Every `v5:` digest is now stale and
#: findable with `LIKE 'v5:%'`.
#: `tweedie` moved it `v6` to `v7` (2026-08-21, FR-MODEL-22): a model whose power is
#: estimated over `tweedie.p_grid` is a different fitted question than one with a fixed
#: power — the grid is part of the question, and two specs differing there must not
#: share a digest or FR-MODEL-66 answers the second caller with the first caller's
#: model. Every `v6:` digest is now stale and findable with `LIKE 'v6:%'`.
#: `offset_model_ref` (renamed from the scaffold's `model_ref`, FR-MODEL-24) moved it
#: `v7` to `v8` (2026-08-21, the offset-from-another-model slice): the field joins the
#: canonicalised spec — the offset it names is part of what a fit means, and FR-MODEL-66's
#: dedup must not match a fit against another model's structure to one that has no offset.
#: **v9, 2026-08-21** — EbmSpec joined the union (FR-MODEL-37): model_type, objective,
#: interactions, max_bins, max_rounds, monotone_constraints. Every `v8:` digest is now
#: stale and must be findable with `LIKE 'v8:%'`.
#: **v10, 2026-08-22** — the first bump for an **interpretation** change rather than a
#: payload one (FR-MODEL-19). `weight` was already in the payload; what changed is that
#: `fit_gbm` began honouring it, having accepted and ignored it since the GBM slice. So a
#: `v9:` digest over a weighted GBM spec names a fit this build produces differently, and
#: FR-MODEL-66's dedup would answer the next caller with an unweighted fit for a weighted
#: spec. Every `v9:` digest is now stale and findable with `LIKE 'v9:%'`. The cost is the
#: documented one and is over-paid: an unweighted GLM's digest goes stale too, for a change
#: that cannot have affected it. A targeted invalidation has no mechanism here, and
#: inventing one is larger than the defect it would spare.
SPEC_HASH_VERSION: Final = 10


def spec_hash(spec: ModelSpec) -> str:
    """A stable digest of the specification (FR-MODEL-66).

    Over the model's JSON with sorted keys, so two specs that differ only in field order
    are one spec — and two that differ anywhere at all, including a loss treatment or a
    seed, are two. `02` §4.4 is explicit that a cap belongs *inside* the spec for exactly
    this reason: two models differing only in their cap must not collide.

    The algorithm version is **inside** the payload as well as in front of the digest, so
    two algorithm versions cannot produce the same hash even for an identical spec. A
    prefix alone would let a future reader strip it and compare across versions, which is
    exactly the comparison that is not meaningful.
    """
    payload = json.dumps(
        {"spec_hash_version": SPEC_HASH_VERSION, "spec": spec.model_dump(mode="json")},
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"v{SPEC_HASH_VERSION}:sha256:{hashlib.sha256(payload.encode()).hexdigest()}"


def spec_hash_is_current(digest: str) -> bool:
    """Whether `digest` was produced by the algorithm this build runs.

    A stored digest from an older algorithm is not wrong, it is **unmatchable** — the
    lookup in `reserve_model` will miss it and fit the model again. Answerable rather than
    silent is the whole reason the version is in the string.
    """
    return digest.startswith(f"v{SPEC_HASH_VERSION}:")


def to_factor(row: FactorRow) -> Factor:
    return Factor.model_validate({**row.body, "id": row.id, "version": row.version,
                                  "dataset_id": row.dataset_id})


def to_model(row: ModelRow, *, flags: tuple[ModelFlag, ...] = ()) -> Model:
    """The artifact as the contract declares it (`02` §4.8).

    `flags` is a parameter rather than a column because FR-MODEL-67's flag is computed from
    the dataset version's *current* status — see `flags_for`, which is async and therefore
    cannot be called from here. A caller that has not asked for them passes none, and the
    artifact then says `[]` truthfully for "not evaluated on this path" only because every
    path that gates on a flag evaluates it (`apply_approval_decision`).
    """
    return Model(
        id=row.id,
        model_family_slug=row.model_family_slug,
        version=row.version,
        status=ModelStatus(row.status),
        spec=MODEL_SPEC_ADAPTER.validate_python(row.spec),
        spec_hash=row.spec_hash,
        fit_result=FIT_RESULT_ADAPTER.validate_python(row.fit_result)
        if row.fit_result
        else None,
        diagnostics_id=row.diagnostics_id,
        dataset_version_id=row.dataset_version_id,
        parent_model_id=row.parent_model_id,
        change_reason=row.change_reason,
        flags=flags,
        approval_request_id=row.approval_request_id,
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
    """The factors a spec pins, in the order it pins them, **plus the operands they cross**.

    Order is the spec's, not the database's: the design matrix's column order follows it,
    and a fit whose columns reordered between runs would produce a different `spec_hash`
    for the same model.

    **Interaction operands are loaded transitively** (FR-MODEL-91, 2026-08-18). A spec pins
    an `interaction` Factor by id and says nothing about what it crosses, so without this
    every such fit failed in `pricing-core` with "crosses factor …, which was not supplied"
    — a refusal that is correct, arriving from the wrong layer, about something the caller
    never had a way to provide. `ModelSpec.factors` stays flat, which is what makes the
    spec readable; the platform resolves the tree.

    Operands are appended *after* the pinned factors rather than woven in, and that is safe
    precisely because an operand contributes no design column of its own — `resolve_factors`
    excludes it — so nothing about the column order changes.

    One level of expansion is enough. An operand that is itself an interaction is loaded
    here and refused at resolution, which is where the "declare a three-way as one factor"
    message belongs.
    """
    async def _load(ids: list[UUID], what: str) -> dict[UUID, FactorRow]:
        rows = (
            await session.execute(
                select(FactorRow).where(
                    FactorRow.workspace_id == workspace_id, FactorRow.id.in_(ids)
                )
            )
        ).scalars().all()
        by_id = {row.id: row for row in rows}
        missing = [str(fid) for fid in ids if fid not in by_id]
        if missing:
            raise PlatformError(
                "NOT_FOUND",
                f"The spec names {what} that do not exist",
                404,
                f"Unknown factor id(s): {', '.join(missing)}.",
            )
        return by_id

    pinned = [to_factor(row) for row in (await _load(factor_ids, "factors")).values()]
    by_id = {factor.id: factor for factor in pinned}
    ordered = [by_id[fid] for fid in factor_ids]

    operand_ids = [
        operand
        for factor in ordered
        if factor.type is FactorType.INTERACTION
        for operand in factor.operand_factor_ids
        if operand not in by_id
    ]
    if not operand_ids:
        return ordered

    deduped = list(dict.fromkeys(operand_ids))
    operands = await _load(deduped, "interaction operands")
    return ordered + [to_factor(operands[fid]) for fid in deduped]


async def reserve_model(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    spec: ModelSpec,
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
    # Before the factor check, deliberately. A bound naming the wrong dataset version also
    # fails factor resolution — the factors belong to the central model's dataset and not to
    # the one the bound named — so the factor error is a *symptom* of the pairing mistake.
    # Reported in the other order, the caller goes and re-checks factors that were never
    # wrong (FR-MODEL-78).
    await _refuse_mismatched_interval_model(
        session, workspace_id=workspace_id, spec=spec
    )
    # Before the factor check too, and for the same reason: a surrogate naming the wrong
    # source model usually also fails factor resolution, and the factor error would send
    # the caller to re-check factors that were never wrong (FR-MODEL-96).
    await _refuse_mismatched_approximation(
        session, workspace_id=workspace_id, spec=spec
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
    session: AsyncSession, *, workspace_id: UUID, spec: ModelSpec, dataset_id: UUID
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


async def load_interval_models(
    session: AsyncSession, *, workspace_id: UUID, central_model_id: UUID
) -> list[ModelRow]:
    """Every quantile bound fitted for `central_model_id`, lower first (FR-MODEL-78).

    **Ordered here rather than by the caller.** Two callers sorting the same list two ways
    is how a lower bound reaches the upper side of a response, and `PredictedRow`'s
    ordering validator would then raise three layers away from the cause.

    The predicate reads a field inside a JSON document, so `workspace_id` is filtered
    explicitly: unlike a foreign key, a JSONB path carries no tenancy of its own.

    `[]` is the ordinary answer — almost no model is bounded — and the prediction path
    reads it as FR-MODEL-77's `no_interval_models_fitted` rather than as a failure.
    """
    rows = (
        (
            await session.execute(
                select(ModelRow).where(
                    ModelRow.workspace_id == workspace_id,
                    ModelRow.spec["interval_for"]["model_id"].astext
                    == str(central_model_id),
                )
            )
        )
        .scalars()
        .all()
    )
    return sorted(rows, key=_bound_alpha)


def _bound_alpha(row: ModelRow) -> float:
    """The alpha a stored bound declares, for ordering. Raises if the row is not a bound."""
    spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
    if not isinstance(spec, GbmSpec) or spec.interval_for is None:
        raise PlatformError(
            "MODEL_INTERVAL_PAIR_INVALID",
            "A stored bound carries no interval_for",
            409,
            f"{row.model_family_slug}@{row.version} was found by the interval_for lookup "
            "and does not carry one. The JSONB predicate and the parsed spec disagree, "
            "which means the stored document is not the shape this code reads.",
        )
    return spec.interval_for.alpha


async def _refuse_mismatched_interval_model(
    session: AsyncSession, *, workspace_id: UUID, spec: ModelSpec
) -> None:
    """FR-MODEL-78's rules for what a bound must be, enforced before a Job exists.

    A bound that disagrees with its central model is an interval drawn around a different
    model. It fits without complaint, returns two ordered numbers, and nothing downstream
    can tell it from a correct one — which is why the refusal is here rather than left to a
    reviewer's judgement.

    **Set comparison on `factors`, not tuple comparison.** Two specs listing the same
    factors in a different order describe the same design matrix, and refusing that would
    reject a legitimate bound over a difference the fit cannot see.

    **The objective is checked too, and it is the rule most easily left out.** A bound whose
    objective is `count:poisson` passes every structural rule and estimates the *mean*; the
    pair would then be two mean estimates reported as an interval. FR-MODEL-78 says a bound
    is fitted with the `quantile` template at a declared alpha, and this is where that
    sentence becomes a refusal.
    """
    if not isinstance(spec, GbmSpec) or spec.interval_for is None:
        return

    from app.platform import objectives as objective_service

    central = await session.get(ModelRow, spec.interval_for.model_id)
    if central is None or central.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "The model this bound is for does not exist",
            404,
            f"interval_for names model {spec.interval_for.model_id}, which is not a model "
            "in this workspace.",
        )

    central_spec = MODEL_SPEC_ADAPTER.validate_python(central.spec)
    mismatches = [
        field
        for field, mine, theirs in (
            ("model_family_slug", spec.model_family_slug, central_spec.model_family_slug),
            ("dataset_version_id", spec.dataset_version_id, central_spec.dataset_version_id),
            ("split_ref", spec.split_ref, central_spec.split_ref),
            ("factors", set(spec.factors), set(central_spec.factors)),
        )
        if mine != theirs
    ]
    if mismatches:
        raise PlatformError(
            "MODEL_INTERVAL_PAIR_INVALID",
            "This bound does not match the model it bounds",
            409,
            f"interval_for names {central.model_family_slug}@{central.version}, but the "
            f"two specifications disagree on {', '.join(mismatches)} (FR-MODEL-78). An "
            "interval fitted on a different design is an interval around a different "
            "model, and renders identically to a correct one.",
        )

    await _refuse_a_bound_that_is_not_a_quantile_fit(
        session, workspace_id=workspace_id, spec=spec, service=objective_service
    )

    side = "lower" if spec.interval_for.alpha < 0.5 else "upper"
    for existing in await load_interval_models(
        session, workspace_id=workspace_id, central_model_id=central.id
    ):
        existing_alpha = _bound_alpha(existing)
        if (existing_alpha < 0.5) == (spec.interval_for.alpha < 0.5):
            raise PlatformError(
                "MODEL_INTERVAL_PAIR_INVALID",
                f"This model already has a {side} bound",
                409,
                f"{central.model_family_slug}@{central.version} already has a {side} bound "
                f"at alpha={existing_alpha} ({existing.model_family_slug}@"
                f"{existing.version}). FR-MODEL-100 allows one per side: the response "
                "carries a single `level`, and two bounds on one side leave nothing to say "
                "which pair produced it.",
            )


async def _refuse_mismatched_approximation(
    session: AsyncSession, *, workspace_id: UUID, spec: ModelSpec
) -> None:
    """FR-MODEL-96's rules for what a surrogate may approximate, before a Job exists.

    The type already refuses a spec that claims to be a surrogate while pointing at an
    observed response column (FR-MODEL-102). What the type cannot see is the *other* model:
    whether it exists, whether it has predictions to approximate, and whether it was fitted
    over the same population. An approximation of a model it does not describe fits without
    complaint and renders identically to a correct one.
    """
    if not isinstance(spec, GlmSpec) or spec.approximates_model_id is None:
        return

    source = await session.get(ModelRow, spec.approximates_model_id)
    if source is None or source.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "The model this approximates does not exist",
            404,
            f"approximates_model_id names model {spec.approximates_model_id}, which is "
            "not a model in this workspace.",
        )
    if source.fit_result is None:
        raise PlatformError(
            "MODEL_APPROXIMATION_INVALID",
            "The model this approximates has no fit to approximate",
            409,
            f"{source.model_family_slug}@{source.version} is at "
            f"{source.status!r} and has no predictions. FR-MODEL-34 fits the surrogate to "
            "the model's own predictions, and a model at `draft` has none.",
        )

    source_spec = MODEL_SPEC_ADAPTER.validate_python(source.spec)
    if source_spec.model_type == "glm":
        raise PlatformError(
            "MODEL_APPROXIMATION_INVALID",
            "A GLM needs no approximation",
            409,
            f"{source.model_family_slug}@{source.version} is a GLM. FR-MODEL-33 applies to "
            "non-GLM models: approximating a GLM with another GLM reports 100 % fidelity, "
            "which looks like evidence and is not.",
        )

    mismatches = [
        field
        for field, mine, theirs in (
            ("dataset_version_id", spec.dataset_version_id, source_spec.dataset_version_id),
            ("split_ref", spec.split_ref, source_spec.split_ref),
            ("factors", set(spec.factors), set(source_spec.factors)),
        )
        if mine != theirs
    ]
    if mismatches:
        raise PlatformError(
            "MODEL_APPROXIMATION_INVALID",
            "This approximation does not match the model it approximates",
            409,
            f"approximates_model_id names {source.model_family_slug}@{source.version}, but "
            f"the two specifications disagree on {', '.join(mismatches)} (FR-MODEL-96). An "
            "approximation fitted over a different population or design describes a "
            "different model, and renders identically to a correct one.",
        )


async def _refuse_a_bound_that_is_not_a_quantile_fit(
    session: AsyncSession, *, workspace_id: UUID, spec: GbmSpec, service: Any
) -> None:
    """The bound's loss must be the pinball loss, at the alpha the bound claims.

    Two alphas are declared because they mean two things — the loss the booster minimises,
    and the quantile the artifact says it estimates — and a bound whose loss seeks the 5th
    percentile while `interval_for` says the 25th is mislabelled at exactly the point a
    reader would check it.
    """
    assert spec.interval_for is not None
    declared = spec.interval_for.alpha
    if spec.objective.kind != "custom" or not spec.objective.ref:
        raise PlatformError(
            "MODEL_INTERVAL_PAIR_INVALID",
            "A bound must be fitted with the quantile template",
            409,
            f"objective {spec.objective.name!r} is a builtin, and FR-MODEL-78 fits each "
            "bound with the `quantile` template (§4.5) at a declared alpha. A builtin "
            "objective estimates the mean, so the pair would be two mean estimates "
            "reported as an interval.",
        )

    objective = await service.resolve_ref(
        session, workspace_id=workspace_id, ref=spec.objective.ref
    )
    if objective.template != ObjectiveTemplate.QUANTILE:
        raise PlatformError(
            "MODEL_INTERVAL_PAIR_INVALID",
            "A bound must be fitted with the quantile template",
            409,
            f"{spec.objective.ref} is the {objective.template.value!r} template, not "
            "`quantile` (FR-MODEL-78). Only the pinball loss estimates a quantile; every "
            "other template in §4.5 estimates a mean of some kind.",
        )
    objective_alpha = objective.params.get("alpha")
    if objective_alpha != declared:
        raise PlatformError(
            "MODEL_INTERVAL_PAIR_INVALID",
            "The bound and its objective disagree about which quantile this is",
            409,
            f"interval_for declares alpha={declared} and {spec.objective.ref} minimises "
            f"the pinball loss at alpha={objective_alpha}. The loss decides what the "
            "booster learns and the artifact decides what the pair claims; a bound where "
            "they differ is mislabelled where a reader would check it.",
        )


async def record_fit(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    model_id: UUID,
    fit_result: FitResult,
    diagnostics: Diagnostics,
    job_id: UUID | None = None,
) -> ModelRow:
    """Write the numbers a fit produced, once (R2), with the evidence for them.

    Refuses a model that already carries a `fit_result`: R2 makes a Model immutable once
    fitted, and "refit" means a new version, not new coefficients on the old one. Without
    this the rule would hold only for callers who remembered it.

    `diagnostics` is **required**, not optional. FR-MODEL-49 makes them a product of every
    fit and `02` §4.8 makes them a condition of `fitted`; an optional argument would make
    the invariant depend on each caller remembering to pass one, which is the shape of
    every invariant this repository has had to repair.
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

    # The diagnostics row is written **before** the status moves, in this transaction.
    # `02` §4.8 makes `diagnostics_id` a condition of `fitted`, and the database CHECK
    # enforces it — so a fit that recorded coefficients and then failed to record evidence
    # rolls back rather than leaving a model nothing may reference and nothing explains.
    diagnostics_row = DiagnosticsRow(
        workspace_id=workspace_id,
        model_id=model_id,
        job_id=job_id,
        payload=diagnostics.model_dump(
            mode="json", exclude={"id", "model_id", "computed_at", "job_id"}
        ),
    )
    session.add(diagnostics_row)
    await session.flush()

    row.fit_result = fit_result.model_dump(mode="json")
    row.diagnostics_id = diagnostics_row.id
    row.status = ModelStatus.FITTED.value
    row.job_id = job_id
    await session.flush()

    # The audit payload is per arm, because "what was fitted" is a different sentence for
    # a coefficient vector, a booster, and an EBM's exported tables. A shared subset — rows
    # and model type — would record the three events identically and leave a reader unable
    # to tell them apart.
    after: dict[str, object] = {"model_type": fit_result.model_type, "rows": fit_result.rows}
    if isinstance(fit_result, GlmFitResult):
        intercept = fit_result.intercept
        after |= {
            "converged": fit_result.converged,
            "terms": len(fit_result.coefficients),
            "intercept": intercept.estimate if intercept else None,
        }
    elif isinstance(fit_result, GbmFitResult):
        after |= {
            "booster": fit_result.booster_blob.sha256,
            "best_iteration": fit_result.best_iteration,
            "features": len(fit_result.feature_order),
        }
    else:
        # The EBM arm (2026-08-21, the W5 EBM slice): the fit IS the exported tables —
        # no blob to hash. The payload names what identifies the fit.
        assert isinstance(fit_result, EbmFitResult)
        after |= {
            "best_iteration": fit_result.best_iteration,
            "features": len(fit_result.feature_order),
            "terms": len(fit_result.terms),
            "intercept": fit_result.intercept,
        }
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.SYSTEM if job_id else JobSource.API,
        action="model.fitted",
        entity_ref=f"model:{row.model_family_slug}@{row.version}",
        after=after,
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


@dataclasses.dataclass(frozen=True)
class OffsetModelSource:
    """What an offset-from-another-model ref resolves to (FR-MODEL-24).

    The η array is deliberately not computed here: the linear predictor is pricing-core
    maths and belongs on the worker thread, not the event loop.
    """

    spec: GlmSpec
    fit: GlmFitResult
    factors: list[Factor]
    bandings: Mapping[UUID, Banding]
    groupings: Mapping[UUID, Grouping]


async def resolve_offset_model(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    ref: str,
    caller_link: str,
) -> OffsetModelSource:
    """Resolve `offset_model_ref` to the artifacts whose η is the offset (FR-MODEL-24).

    Every refusal is named: the ref must name a fitted GLM in this workspace whose link
    equals the new spec's — otherwise the fit would be offset by a number from another
    scale, the defect class FR-MODEL-71 refuses for `base_margin`.
    """
    parsed = ArtifactRef.model_validate(ref)
    if parsed.type != "model":
        raise PlatformError(
            "MODEL_OFFSET_REF_INVALID",
            "The model the offset names is not a model",
            409,
            f"{ref} names a {parsed.type}, and an offset must be another model (FR-MODEL-24).",
        )
    row = await load_model(
        session, workspace_id=workspace_id, slug=parsed.slug, version=parsed.version
    )
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "The model the offset names does not exist",
            404,
            f"{ref} resolves to no model in this workspace.",
        )
    if row.fit_result is None:
        raise PlatformError(
            "MODEL_OFFSET_REF_INVALID",
            "The model the offset names has no fit to offset against",
            409,
            f"{ref} is not fitted, and the offset is its linear predictor (FR-MODEL-24).",
        )
    ref_spec = MODEL_SPEC_ADAPTER.validate_python(row.spec)
    ref_fit = FIT_RESULT_ADAPTER.validate_python(row.fit_result)
    if not isinstance(ref_spec, GlmSpec) or not isinstance(ref_fit, GlmFitResult):
        raise PlatformError(
            "MODEL_OFFSET_REF_INVALID",
            "The model the offset names is not a GLM",
            409,
            f"{ref} is not a GLM, and the first offset-from-model slice is GLM-to-GLM "
            "(FR-MODEL-24, amended 2026-08-21).",
        )
    if ref_spec.link != caller_link:
        raise PlatformError(
            "MODEL_OFFSET_REF_INVALID",
            "The offset model's link is not the new spec's",
            409,
            f"{ref} was fitted with a {ref_spec.link} link and the new spec declares "
            f"{caller_link}; the offset would be a number from another scale (FR-MODEL-24).",
        )
    try:
        factors = await load_factors(
            session, workspace_id=workspace_id, factor_ids=list(ref_spec.factors)
        )
    except FactorResolutionError as exc:
        raise PlatformError(
            "FACTOR_RESOLUTION_FAILED",
            "The offset model's factors do not resolve",
            409,
            str(exc),
        ) from exc
    bandings = await transformations.load_bandings(
        session, workspace_id=workspace_id,
        ids=[f.banding_id for f in factors if f.banding_id],
    )
    groupings = await transformations.load_groupings(
        session, workspace_id=workspace_id,
        ids=[f.grouping_id for f in factors if f.grouping_id],
    )
    return OffsetModelSource(
        spec=ref_spec, fit=ref_fit, factors=factors, bandings=bandings, groupings=groupings
    )


def fit_payload(row: ModelRow) -> dict[str, Any]:
    """What the `model.fit` Job carries: the model to fill in, and nothing else."""
    return {"model_id": str(row.id), "workspace_id": str(row.workspace_id)}


# -- The lifecycle (FR-MODEL-64) -----------------------------------------------------------
#
# `06` FR-GOV-9 makes the approval machine uniform across artifact types and stops it at
# `approved`: "post-approval states belong to the owning module". This is that module for a
# Model, and the seam is deliberate in both directions.
#
# **Direction.** `MODEL` depends on `GOV` (DEP-1), so this file calls `approvals`. Nothing in
# `approvals` may call back here, which is why `apply_approval_decision` is driven by the
# caller that already holds both — the API route for `POST /approval-requests/{id}/decide` —
# rather than by a hook inside the approval machine. `withdraw`'s `artifact_is_live`
# argument is the same seam, decided the same way when W3 built it: governance owns the
# rule, the owning module owns the state.


async def flags_for(
    session: AsyncSession, *, workspace_id: UUID, row: ModelRow
) -> tuple[ModelFlag, ...]:
    """FR-MODEL-67's flags, **computed rather than stored**.

    A stored flag is a snapshot, and the thing this one describes moves: `01` FR-DATA-23
    makes validation re-runnable on an already-validated version, so a dataset that was
    good under an older rule set can go to `failed` long after a model was fitted on it.
    A column written at fit time would then say `[]` for exactly the model FR-MODEL-67
    exists to stop.

    The cost is a read per model, which is why it is not called on the list path.
    """
    version = await session.get(DatasetVersionRow, row.dataset_version_id)
    if version is None or DatasetStatus(version.status) is not DatasetStatus.VALIDATED:
        return (ModelFlag.DATASET_INVALIDATED,)
    return ()


def _require_transition(row: ModelRow, target: ModelStatus) -> ModelStatus:
    """Refuse an edge the lifecycle does not have, before anything is written.

    `VALIDATION_FAILED` at 409 follows `01`'s precedent for the same refusal
    (`datasets._transition`): the *request* was well formed, the artifact's state is what
    makes it impossible, and a caller branching on the code should not have to tell a
    malformed body from a stale view of a lifecycle.
    """
    current = ModelStatus(row.status)
    if target not in VALID_MODEL_TRANSITIONS[current]:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Invalid model lifecycle transition",
            409,
            f"{row.model_family_slug}@{row.version} is {current.value!r} and cannot move "
            f"to {target.value!r} (FR-MODEL-64).",
        )
    return current


async def load_model_by_id(
    session: AsyncSession, *, workspace_id: UUID, model_id: UUID, for_update: bool = False
) -> ModelRow:
    """A model by id, optionally locked.

    `for_update` is not a caller's convenience: every transition is a check-then-act on
    `status`, and the route that checks an `If-Match` precondition has to read the same row
    the transition will write. Two unlocked reads in one request is how a precondition
    passes against a state that has already moved.
    """
    query = select(ModelRow).where(ModelRow.id == model_id)
    if for_update:
        query = query.with_for_update()
    row = (await session.execute(query)).scalar_one_or_none()
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError("NOT_FOUND", "Model not found", 404, f"No model {model_id}.")
    return row


async def _for_update(session: AsyncSession, workspace_id: UUID, model_id: UUID) -> ModelRow:
    return await load_model_by_id(
        session, workspace_id=workspace_id, model_id=model_id, for_update=True
    )


async def submit_for_review(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    model_id: UUID,
    change_summary: str,
) -> tuple[ModelRow, ApprovalRequestRow]:
    """`fitted → review`, with the approval request it exists to create (`wf-01` E6/E7).

    Gated on `model:submit` — a permission that existed in `permissions.py` and gated
    nothing until now, held by `pricing_actuary` and not by `analyst`. Submitting is not
    fitting: it puts a model in front of an approver and starts a governed process, and the
    role that may explore a specification is not automatically the role that may do that.

    **The flag is not checked here.** A model whose dataset version has lost its standing
    can still be submitted; what it cannot do is reach `approved` (FR-MODEL-67). Refusing
    the submission would hide the flag from the approver, and `06` FR-GOV-17's whole design
    is that flags are visible *in the approval surface* rather than being an error the
    submitter alone ever sees.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_SUBMIT,
    )
    row = await _for_update(session, workspace_id, model_id)
    _require_transition(row, ModelStatus.REVIEW)
    await _require_evidence(session, workspace_id=workspace_id, row=row)

    # Governance allocates the request, enforces one-open-request-per-artifact, and audits
    # the submission. A second `submit` for the same model reaches its partial unique index
    # and comes back as a 409 — which is the right layer for that answer, because two open
    # reviews of one artifact is a governance rule, not a modelling one.
    request = await approvals.submit(
        session,
        workspace_id=workspace_id,
        submitter=actor,
        artifact_ref=ArtifactRef(
            type="model", slug=row.model_family_slug, version=row.version
        ),
        change_summary=change_summary,
    )

    row.status = ModelStatus.REVIEW.value
    row.approval_request_id = request.id
    await session.flush()

    # Recorded on the submission rather than left for the approver to discover: FR-GOV-17
    # puts the flag in the approval surface, and the audit trail is where "was it flagged
    # when it was submitted?" is answered after the dataset has moved on again.
    flags = await flags_for(session, workspace_id=workspace_id, row=row)
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="model.submitted",
        entity_ref=f"model:{row.model_family_slug}@{row.version}",
        before={"status": ModelStatus.FITTED.value},
        after={
            "status": ModelStatus.REVIEW.value,
            "approval_request_id": str(request.id),
            "flags": [f.value for f in flags],
        },
        justification=change_summary,
    )
    return row, request


async def _require_evidence(
    session: AsyncSession, *, workspace_id: UUID, row: ModelRow
) -> None:
    """`06` R4 and FR-GOV-10: the policy's required evidence, enforced at submission.

    `EVIDENCE_INCOMPLETE` was a registered code nothing raised — the shape of gap this
    repository has had to repair twice, where a catalogue entry is indistinguishable from a
    working refusal.

    **Fails closed on an evidence kind it cannot check.** A workspace may edit the policy
    (FR-GOV-12), so it can name evidence this slice has no way to look for — model
    comparison is still declared and unbuilt. Treating an uncheckable requirement as
    satisfied would let a policy tightening silently do nothing, which is worse than a
    submission refused with the reason named.

    **The list it reads is the union of `06` §3.3's floor and the workspace policy**
    (FR-GOV-37, OQ-GOV-7 decided 2026-08-18). The two tables disagreed for a Model and this
    check could only read one of them; §3.3 is now the floor and §4.2 may only add to it, so
    a workspace cannot edit its way past `02` §4.8 R3.

    **`transparency` became checkable on 2026-08-17 and this function was still failing
    closed on it.** The artifact exists now, so the policy kind is answered by looking for
    one rather than by refusing — and FR-MODEL-89's R3 is enforced here whether or not any
    policy asks for it, because R3 is an invariant of the Model rather than a workspace's
    choice.
    """
    has_transparency = await _has_transparency_artifact(
        session, workspace_id=workspace_id, model_id=row.id
    )
    model_type = str(row.spec.get("model_type", "glm"))
    if model_type != "glm" and not has_transparency:
        # FR-MODEL-89 / `02` §4.8 R3, enforced at submission for the same reason
        # FR-MODEL-64 puts it at `review`: `approved` is unreachable without passing here,
        # and refusing at the approval step would waste an approver's attention on a model
        # that was never eligible. The check runs artifact→model, which is the direction
        # the link runs — `models` carries no column anything writes back.
        raise PlatformError(
            "EVIDENCE_INCOMPLETE",
            "Required evidence is missing",
            422,
            f"{row.model_family_slug}@{row.version} is a {model_type} model and no "
            "transparency artifact names it. `02` §4.8 R3 and FR-MODEL-89: a non-GLM model "
            "cannot be approved without one, and FR-MODEL-64 makes `review` the gate. "
            "POST /api/v1/models/{id}/transparency produces it.",
        )

    policy = await approvals.policy_for(session, workspace_id)

    #: What this slice can actually verify, and what answers each one. The two spellings of
    #: the transparency kind are both live on purpose: `06` §4.2 and `EVIDENCE_FLOOR` name
    #: it `transparency_artifact_if_non_glm`, and a workspace policy stored before
    #: 2026-08-18 may still say `transparency_artifact`. Refusing the older spelling as
    #: uncheckable would fail a submission closed on evidence the model has.
    transparency_satisfied = model_type == "glm" or has_transparency
    verifiable = {
        "diagnostics": row.diagnostics_id is not None,
        "transparency_artifact_if_non_glm": transparency_satisfied,
        "transparency_artifact": transparency_satisfied,
    }

    #: FR-GOV-37: the union of `06` §3.3's floor and the workspace's own entry, so a policy
    #: stored before the floor existed cannot sit below it.
    required = policy.effective_evidence("model")
    missing = [kind for kind in required if not verifiable.get(kind, False)]
    if missing:
        unknown = [kind for kind in missing if kind not in verifiable]
        detail = (
            f"{row.model_family_slug}@{row.version} is missing required evidence: "
            f"{', '.join(missing)}. `06` FR-GOV-19 defines it per artifact type and R4 "
            "makes it a condition of submission, not of approval."
        )
        if unknown:
            detail += (
                f" This build cannot verify {', '.join(unknown)} — the artifact does not "
                "exist yet — and treating an uncheckable requirement as met would make a "
                "policy tightening do nothing."
            )
        raise PlatformError("EVIDENCE_INCOMPLETE", "Required evidence is missing", 422, detail)


async def _has_transparency_artifact(
    session: AsyncSession, *, workspace_id: UUID, model_id: UUID
) -> bool:
    """Whether any `TransparencyArtifact` names this model (FR-MODEL-89).

    The artifact carries `model_id` and the Model carries no back-reference that anything
    writes, so this is the only direction the question can be asked in. FR-MODEL-33 allows
    many artifacts per model; one is enough to satisfy R3.
    """
    found = await session.scalar(
        select(TransparencyArtifactRow.id)
        .where(
            TransparencyArtifactRow.workspace_id == workspace_id,
            TransparencyArtifactRow.model_id == model_id,
        )
        .limit(1)
    )
    return found is not None


async def apply_approval_decision(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    request: ApprovalRequestRow,
) -> ModelRow | None:
    """Carry a governance decision into the artifact (`wf-01` E10, FR-MODEL-64).

    Returns `None` when the request is about something other than a Model, so the caller
    can drive every artifact type through one call rather than branching per type.

    Called in the **same transaction** as the decision. A model left in `review` after its
    request reached `approved` is a model no Rating Version may reference and no screen can
    explain, and two transactions is all it takes to produce one.
    """
    if request.artifact_type != "model":
        return None

    ref = ArtifactRef.model_validate(request.artifact_ref)
    row = (
        await session.execute(
            select(ModelRow)
            .where(
                ModelRow.workspace_id == workspace_id,
                ModelRow.model_family_slug == ref.slug,
                ModelRow.version == ref.version,
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if row is None:
        # **The hole this used to describe is closed.** `06` FR-GOV-36 is built: `POST
        # /approval-requests` resolves the reference it is asked to pin before the row
        # exists (`api/approvals.py::_resolve_the_artifact`), so a request naming a model
        # that was never created is now refused with `NOT_FOUND` at submission rather than
        # accepted and decided here without effect.
        #
        # **Still tolerated, and the distinction is still load-bearing.** What reaches this
        # branch now is a request submitted *before* that check existed — every deployed
        # database holds some — and 404'ing it would make those requests permanently
        # undecidable. A dead row nobody can close is worse than a decision that moves
        # nothing, which is the whole reason the tolerance was written; closing the hole
        # upstream shrinks what falls through it, and does not change that judgement.
        # Nothing this platform produces adds to the residue: `submit_for_review` holds the
        # row it names, and a fitted model cannot be deleted (`02` R2, enforced by trigger).
        return None

    target = _target_status(ApprovalStatus(request.status))
    if target is None or ModelStatus(row.status) is target:
        # A partial approval: the request is still in `review` because the policy wants
        # another approver. Nothing about the artifact has changed yet.
        return row

    if target is ModelStatus.APPROVED:
        flags = await flags_for(session, workspace_id=workspace_id, row=row)
        if flags:
            # FR-MODEL-67 and `06` FR-GOV-17. The decision is recorded and the artifact does
            # not move; the transaction is rolled back by the caller, so neither happens.
            raise PlatformError(
                "ARTIFACT_FLAGGED",
                "This model carries a flag and cannot be approved",
                409,
                f"{request.artifact_ref} is flagged {[f.value for f in flags]}. "
                "FR-MODEL-67: a Model whose Dataset Version was invalidated cannot advance "
                "to `approved`. Re-validating the version, or refitting on one that holds, "
                "clears it — the flag is computed, not stored, so nothing needs unsetting.",
            )

    before = ModelStatus(row.status)
    _require_transition(row, target)
    row.status = target.value
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=f"model.{target.value}",
        entity_ref=str(ref),
        before={"status": before.value},
        after={"status": target.value, "approval_request_id": str(request.id)},
    )

    if target is ModelStatus.APPROVED:
        await _supersede_earlier_versions(
            session, workspace_id=workspace_id, actor=actor, approved=row
        )
    return row


def _target_status(request_status: ApprovalStatus) -> ModelStatus | None:
    """What a request's status means for the artifact behind it.

    `changes_requested`, `rejected` and `withdrawn` all return the model to **`fitted`**,
    not to `draft`. FR-GOV-13 says `draft`, and for most artifact types that is right; for a
    Model it is not, because `02` uses `draft` for *reserved, not yet fitted* and R2 makes
    the coefficients immutable. A model cannot un-fit. `06` FR-GOV-13 carries the amendment
    (2026-08-17) rather than this code carrying a silent divergence.
    """
    return {
        ApprovalStatus.APPROVED: ModelStatus.APPROVED,
        ApprovalStatus.CHANGES_REQUESTED: ModelStatus.FITTED,
        ApprovalStatus.REJECTED: ModelStatus.FITTED,
        ApprovalStatus.WITHDRAWN: ModelStatus.FITTED,
    }.get(request_status)


async def _supersede_earlier_versions(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, approved: ModelRow
) -> None:
    """`approved → superseded` for every earlier approved version of the family.

    Automatic rather than an operation someone performs, because the alternative is a family
    with two approved versions and nothing to say which one a Rating Version means. Only
    `approved` rows move: a version still at `fitted` is a candidate, not a predecessor, and
    superseding it would say it had once been in force.
    """
    earlier = (
        await session.execute(
            select(ModelRow)
            .where(
                ModelRow.workspace_id == workspace_id,
                ModelRow.model_family_slug == approved.model_family_slug,
                ModelRow.version < approved.version,
                ModelRow.status == ModelStatus.APPROVED.value,
            )
            .with_for_update()
        )
    ).scalars().all()

    for row in earlier:
        _require_transition(row, ModelStatus.SUPERSEDED)
        row.status = ModelStatus.SUPERSEDED.value
        await session.flush()
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=actor,
            source=JobSource.API,
            action="model.superseded",
            entity_ref=f"model:{row.model_family_slug}@{row.version}",
            before={"status": ModelStatus.APPROVED.value},
            after={
                "status": ModelStatus.SUPERSEDED.value,
                "superseded_by": f"model:{approved.model_family_slug}@{approved.version}",
            },
        )


async def archive(
    session: AsyncSession, *, workspace_id: UUID, actor: Principal, model_id: UUID
) -> ModelRow:
    """`draft | fitted | superseded → archived` — the lifecycle's only end state.

    An `approved` model cannot be archived directly: it is a Rating Version's referent, and
    the operation that removes one names its replacement (`_supersede_earlier_versions`).
    A model in `review` cannot either — withdraw the request first, so the approver's queue
    does not lose an item without a decision recorded against it.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_SUBMIT,
    )
    row = await _for_update(session, workspace_id, model_id)
    before = _require_transition(row, ModelStatus.ARCHIVED)
    row.status = ModelStatus.ARCHIVED.value
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="model.archived",
        entity_ref=f"model:{row.model_family_slug}@{row.version}",
        before={"status": before.value},
        after={"status": ModelStatus.ARCHIVED.value},
    )
    return row
