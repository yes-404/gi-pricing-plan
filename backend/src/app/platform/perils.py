"""Composing, reconciling and submitting a Peril Structure (`02` §3.9, §5.1).

`pricing-core` owns the arithmetic; this owns the rules that make a structure mean
something. There are three, and each is answered **before** a Job exists:

* **every referenced model resolves, and every one of them is scoreable.** A structure
  citing a `draft` model is a composition that cannot be priced, and discovering that from
  a failed job twenty seconds later is a worse answer to the same question —
  `request_comparison` set that precedent and the reason;
* **the composition freezes once it has been reconciled.** The number measured *this* set
  of models; a later edit leaves it attached to a composition that never produced it. The
  service refuses, and a trigger refuses the raw `UPDATE` the service cannot see;
* **`review` is reachable only from `reconciled`.** FR-MODEL-60 makes the reconciliation
  the evidence FR-MODEL-61's approval reads, so the lifecycle has no edge that skips it.

Permissions are the Model's — `model:read`, `model:fit`, `model:submit`. `02` declares no
permission of its own for this artifact, and inventing one here would be governance the
specification has not agreed to; a structure is a composition of models, and the role that
may fit them is the role that may compose them. Recorded in `02` §5.1 with this slice.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ApprovalRequestRow, ModelRow, PerilStructureRow
from app.errors import PlatformError
from app.platform import approvals, audit, rbac
from model_schema import (
    SCOREABLE_MODEL_STATUSES,
    VALID_PERIL_STRUCTURE_TRANSITIONS,
    ArtifactRef,
    JobSource,
    LargeLossKind,
    ModelStatus,
    PerilComponent,
    PerilStructure,
    PerilStructureStatus,
    Permission,
    Principal,
    Reconciliation,
    new_uuid7,
)

__all__ = [
    "create_structure",
    "list_peril_structures",
    "load_structure",
    "reconcile_payload",
    "record_reconciliation",
    "request_reconciliation",
    "resolve_artifact_ref",
    "submit_for_review",
    "to_structure",
]


def to_structure(row: PerilStructureRow) -> PerilStructure:
    """The stored composition, re-validated on the way out.

    Re-validated rather than trusted: the row is JSONB, and every invariant the contract
    enforces — a `frequency_severity` peril with both its models, a peril not both modelled
    and excluded — is one a direct `UPDATE` could have broken.
    """
    return PerilStructure.model_validate(
        {
            "id": str(row.id),
            "slug": row.slug,
            "version": row.version,
            "perils": row.perils,
            "excluded_perils": row.excluded_perils,
            "reconciliation": row.reconciliation,
            "status": row.status,
            "created_at": row.created_at.isoformat(),
        }
    )


async def create_structure(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    perils: list[PerilComponent],
    excluded_perils: list[dict[str, Any]],
) -> PerilStructureRow:
    """Create the next version of a Peril Structure, as a `draft` (FR-MODEL-58).

    Versioning is by slug: a structure is edited by superseding it, never in place, which is
    what makes FR-MODEL-61's pinned reference resolvable for as long as any Rating Version
    holds it.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_FIT,
    )
    await _resolve_models(session, workspace_id=workspace_id, perils=perils)

    latest = await session.scalar(
        select(PerilStructureRow.version)
        .where(
            PerilStructureRow.workspace_id == workspace_id,
            PerilStructureRow.slug == slug,
        )
        .order_by(PerilStructureRow.version.desc())
        .limit(1)
    )
    version = (latest or 0) + 1

    row = PerilStructureRow(
        id=new_uuid7(),
        workspace_id=workspace_id,
        slug=slug,
        version=version,
        status=PerilStructureStatus.DRAFT.value,
        perils=[p.model_dump(mode="json") for p in perils],
        excluded_perils=excluded_perils,
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="peril_structure.created",
        entity_ref=f"peril_structure:{slug}@{version}",
        after={
            "status": PerilStructureStatus.DRAFT.value,
            "perils": [p.peril for p in perils],
            "excluded_perils": [e["peril"] for e in excluded_perils],
        },
    )
    return row


async def request_reconciliation(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    structure_id: UUID,
    tolerance: Decimal,
) -> PerilStructureRow:
    """Validate a reconciliation request and return the structure (FR-MODEL-60).

    Gated on `model:fit` rather than `model:read`: this queues a compute Job that scores
    every peril's models over the holdout.

    `separate_model` is refused **here**, not in the worker. `pricing-core` refuses it too —
    it must, because it is reachable from a notebook — but a caller who is told now gets a
    409 naming the peril rather than a job that fails after loading the dataset.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_FIT,
    )
    row = await _get_or_404(session, workspace_id=workspace_id, structure_id=structure_id)

    if tolerance <= 0:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Tolerance must be positive",
            422,
            "FR-MODEL-60 reconciles within a *declared* tolerance. A tolerance of zero "
            "passes only an exact match, which no fitted model produces.",
        )

    structure = to_structure(row)
    if row.reconciliation is not None and row.status not in {
        PerilStructureStatus.DRAFT.value,
        PerilStructureStatus.RECONCILED.value,
    }:
        raise PlatformError(
            "PERIL_STRUCTURE_RECONCILIATION_FAILED",
            "This structure cannot be reconciled again",
            409,
            f"{row.slug}@{row.version} is {row.status}. Reconciling an artifact that is "
            "under review or approved would change the evidence the decision was made "
            "against; create the next version instead.",
        )

    for peril in structure.perils:
        if peril.large_loss.kind is LargeLossKind.SEPARATE_MODEL:
            raise PlatformError(
                "LOSS_TREATMENT_UNIMPLEMENTED",
                "This large-loss treatment cannot be reconciled yet",
                409,
                f"Peril {peril.peril} declares a 'separate_model' treatment, which needs "
                "the excess-layer model's own predictions. FR-MODEL-59 declares all four "
                "treatments and this slice computes three; reconciling it as though it "
                "were 'none' would under-state the premium by exactly the excess layer.",
            )

    resolved = await _resolve_models(
        session, workspace_id=workspace_id, perils=list(structure.perils)
    )
    _refuse_unshared_holdout(list(resolved.values()))
    return row


def reconcile_payload(
    row: PerilStructureRow,
    *,
    tolerance: Decimal,
    observed_column: str,
    exposure_column: str,
) -> dict[str, Any]:
    """The Job's parameters. Ids and names only — the worker resolves them itself.

    `tolerance` crosses as a string: a Job's parameters are JSON, and a `Decimal` that goes
    through a float loses the exactness FR-OVR-7 exists to keep.
    """
    return {
        "structure_id": str(row.id),
        "tolerance": str(tolerance),
        "observed_column": observed_column,
        "exposure_column": exposure_column,
    }


async def record_reconciliation(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    structure_id: UUID,
    reconciliation: Reconciliation,
    job_id: UUID | None = None,
) -> PerilStructureRow:
    """Persist the reconciliation and move `draft → reconciled` (FR-MODEL-60).

    A `fail` verdict is recorded, not refused. FR-MODEL-60 asks for the reconciliation to be
    *persisted*; a failing one is the finding, and discarding it would leave an actuary
    re-running the same job to see the same number. What a `fail` blocks is `review`, which
    is `submit_for_review`'s answer rather than this one's.
    """
    row = await _get_or_404(session, workspace_id=workspace_id, structure_id=structure_id)
    before = row.status

    row.reconciliation = reconciliation.model_dump(mode="json")
    row.job_id = job_id
    if row.status == PerilStructureStatus.DRAFT.value:
        row.status = PerilStructureStatus.RECONCILED.value
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.SYSTEM if job_id else JobSource.API,
        action="peril_structure.reconciled",
        entity_ref=f"peril_structure:{row.slug}@{row.version}",
        before={"status": before},
        after={
            "status": row.status,
            "ratio": str(reconciliation.ratio),
            "tolerance": str(reconciliation.tolerance),
            "reconciliation_status": reconciliation.status.value,
        },
    )
    return row


async def submit_for_review(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    structure_id: UUID,
    change_summary: str,
) -> tuple[PerilStructureRow, ApprovalRequestRow]:
    """`reconciled → review` and the approval request it exists to create (FR-MODEL-61).

    The approval machine is entirely generic (`06` FR-GOV-9): it takes an `ArtifactRef`, and
    `peril_structure` has been a valid artifact type since Phase 0. What was missing was the
    **policy entry** — without one, `approvals.submit` refuses with "no approval policy for
    this artifact type", which is a correct refusal of a structure nobody could ever approve.
    `DEFAULT_POLICY` gained the entry with this slice, naming `reconciliation` as its
    evidence.

    A structure whose reconciliation **failed** is refused. FR-MODEL-60 makes reconciling
    within the declared tolerance part of the coherence check, and the tolerance is the
    submitter's own number — a structure that misses it has failed a test it set itself.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.MODEL_SUBMIT,
    )
    row = await _get_or_404(session, workspace_id=workspace_id, structure_id=structure_id)
    current = PerilStructureStatus(row.status)
    if PerilStructureStatus.REVIEW not in VALID_PERIL_STRUCTURE_TRANSITIONS[current]:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Invalid peril structure lifecycle transition",
            409,
            f"{row.slug}@{row.version} is {row.status}; FR-MODEL-61 reaches `review` from "
            "`reconciled` only. The reconciliation is the evidence the approval reads.",
        )

    structure = to_structure(row)
    assert structure.reconciliation is not None  # the transition guarantees it
    if structure.reconciliation.status.value != "pass":
        raise PlatformError(
            "EVIDENCE_INCOMPLETE",
            "Required evidence is missing",
            422,
            f"{row.slug}@{row.version} reconciles at a ratio of "
            f"{structure.reconciliation.ratio} against a declared tolerance of "
            f"{structure.reconciliation.tolerance}. FR-MODEL-60 makes reconciling within "
            "the declared tolerance part of the coherence check, and the tolerance is the "
            "submitter's own number.",
        )

    request = await approvals.submit(
        session,
        workspace_id=workspace_id,
        submitter=actor,
        artifact_ref=ArtifactRef(
            type="peril_structure", slug=row.slug, version=row.version
        ),
        change_summary=change_summary,
    )
    row.status = PerilStructureStatus.REVIEW.value
    row.approval_request_id = request.id
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="peril_structure.submitted",
        entity_ref=f"peril_structure:{row.slug}@{row.version}",
        before={"status": PerilStructureStatus.RECONCILED.value},
        after={
            "status": PerilStructureStatus.REVIEW.value,
            "approval_request_id": str(request.id),
        },
        justification=change_summary,
    )
    return row, request


async def load_structure(
    session: AsyncSession, *, workspace_id: UUID, structure_id: UUID
) -> PerilStructure:
    """FR-MODEL-90 — the read `02` §5.1 declared a create and a reconcile without."""
    return to_structure(
        await _get_or_404(session, workspace_id=workspace_id, structure_id=structure_id)
    )


async def list_peril_structures(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    limit: int,
    count_cap: int,
    status: PerilStructureStatus | None = None,
    slug: str | None = None,
    after: UUID | None = None,
) -> tuple[Sequence[PerilStructureRow], int]:
    """One page of the workspace's peril structures, newest first (FR-MODEL-127).

    `metrics.list_metrics` and `objectives.list_objectives` are the same fifteen lines over
    their own tables, and the three are deliberately **not** factored into a shared generic:
    the tables carry different status enums and the abstraction that unified them would be
    harder to read than all three.

    **This one returns no usage count, and its two siblings do.** `02` §5.1 asks the metric
    and objective rows for a blast radius and asks nothing of this row, and the reason is
    that there is no query to write: a Model Spec references an objective and a metric by
    `custom_objective:`/`custom_metric:` ref, and nothing in Phase 1b references a peril
    structure at all — FR-MODEL-61's Rating Version, which will, is Phase 2. A count here
    would be a column of zeroes that reads as "nothing uses this" when the truth is "nothing
    can yet". Raised as an open question with this slice rather than answered by building
    one.

    `ix_peril_structures_slug_status` covers `(workspace_id, slug, status)`, so both filters
    are index-served and no migration accompanies this route. `slug` is an **equality** for
    `list_metrics`'s reason: a prefix match resolves `motor-gb` to `motor-gb-fleet` too,
    which is a wrong artifact rather than a wide result.

    Ids are UUIDv7 and therefore time-ordered, so one column is both the sort and the
    cursor; `limit + 1` rows are fetched and the caller drops the extra one. No RBAC check —
    every caller arrives through `requires(MODEL_READ)`. `limit` and `count_cap` are
    parameters because `DEFAULT_LIMIT` and `COUNT_CAP` live in `app.api.pagination` and no
    module under `app/platform/` imports from `app/api/`.
    """
    conditions = [PerilStructureRow.workspace_id == workspace_id]
    if status is not None:
        conditions.append(PerilStructureRow.status == status.value)
    if slug is not None:
        conditions.append(PerilStructureRow.slug == slug)

    query = (
        select(PerilStructureRow)
        .where(*conditions)
        .order_by(PerilStructureRow.id.desc())
        .limit(limit + 1)
    )
    if after is not None:
        query = query.where(PerilStructureRow.id < after)

    rows = (await session.execute(query)).scalars().all()
    total = (
        await session.execute(
            select(func.count()).select_from(
                select(PerilStructureRow.id).where(*conditions).limit(count_cap).subquery()
            )
        )
    ).scalar_one()
    return rows, int(total)


async def resolve_artifact_ref(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> bool:
    """`peril_structure:<slug>@<version>` → does that version exist? (`06` FR-GOV-36.)

    `False`, having done nothing, for a reference that is not this module's — the contract
    `api/approvals.py`'s fan-out is built on, and the same guard `modelling`, `objectives`
    and `metrics` open `apply_approval_decision` with in the other direction.

    By slug and version rather than by id, unlike `load_structure`: a reference *is* a slug
    and a version (ID-3), and `uq_peril_structures_slug_version` makes the pair identify one
    row. Status is deliberately not consulted — FR-GOV-36 asks whether the artifact exists,
    and which statuses may be submitted is `submit_for_review`'s question, already answered
    for anything that reached this module's own path.
    """
    if artifact_ref.type != "peril_structure":
        return False
    row = (
        await session.execute(
            select(PerilStructureRow.id).where(
                PerilStructureRow.workspace_id == workspace_id,
                PerilStructureRow.slug == artifact_ref.slug,
                PerilStructureRow.version == artifact_ref.version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND",
            "Peril structure not found",
            404,
            f"{artifact_ref} resolves to no peril structure in this workspace.",
        )
    return True


# -- internals -----------------------------------------------------------------------------


async def _get_or_404(
    session: AsyncSession, *, workspace_id: UUID, structure_id: UUID
) -> PerilStructureRow:
    row = await session.get(PerilStructureRow, structure_id)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND",
            "Peril structure not found",
            404,
            f"No peril structure {structure_id} in this workspace.",
        )
    return row


async def _resolve_models(
    session: AsyncSession, *, workspace_id: UUID, perils: list[PerilComponent]
) -> dict[str, ModelRow]:
    """Every referenced model, or a refusal naming the first that does not resolve.

    FR-MODEL-58 pins references by version, so this looks each one up by
    `(model_family_slug, version)` — the pair `ArtifactRef` carries. A ref that resolves to
    nothing is a composition that cannot be priced, and it is cheaper to say so now.
    """
    resolved: dict[str, ModelRow] = {}
    for peril in perils:
        for ref in _model_refs(peril):
            key = str(ref)
            if key in resolved:
                continue
            row = (
                await session.execute(
                    select(ModelRow).where(
                        ModelRow.workspace_id == workspace_id,
                        ModelRow.model_family_slug == ref.slug,
                        ModelRow.version == ref.version,
                    )
                )
            ).scalar_one_or_none()
            if row is None:
                raise PlatformError(
                    "NOT_FOUND",
                    "Referenced model not found",
                    404,
                    f"Peril {peril.peril} references {key}, which resolves to no model in "
                    "this workspace.",
                )
            if ModelStatus(row.status) not in SCOREABLE_MODEL_STATUSES or row.fit_result is None:
                raise PlatformError(
                    "MODEL_NOT_FITTED",
                    "A referenced model has not been fitted",
                    409,
                    f"Peril {peril.peril} references {key}, which is {row.status} and "
                    "carries no coefficients. A structure citing an unfitted model is a "
                    "composition that cannot be priced.",
                )
            resolved[key] = row
    return resolved


def _refuse_unshared_holdout(rows: list[ModelRow]) -> None:
    """Every peril's models must reconcile on one holdout (FR-MODEL-60).

    The comparison's `_refuse_unshared_splits` makes the same demand for the same reason,
    and here it is stronger: FR-MODEL-60 sums modelled burning cost across perils and
    compares the total to one observed figure. Perils scored on different holdouts are a
    sum over different books, and the ratio would be a number about no population.

    It is also what makes the reconciliation's `dataset_version_id` and `part` derivable
    rather than a caller input — a caller who could name them could name a third holdout.
    """
    seen: dict[tuple[str, str, str], list[str]] = {}
    for row in rows:
        spec = row.spec or {}
        ref = spec.get("split_ref")
        label = f"{row.model_family_slug}@{row.version}"
        if not ref:
            raise PlatformError(
                "PERIL_STRUCTURE_RECONCILIATION_FAILED",
                "A referenced model cites no split",
                409,
                f"{label} declares no `split_ref`, so it has no named holdout to "
                "reconcile on (`01` FR-DATA-36).",
            )
        key = (
            str(spec.get("dataset_version_id")),
            str(ref["split_artifact_id"]),
            str(ref.get("holdout_part", "test")),
        )
        seen.setdefault(key, []).append(label)

    if len(seen) > 1:
        detail = "; ".join(
            f"{', '.join(labels)} on version {version} split {split} part {part!r}"
            for (version, split, part), labels in seen.items()
        )
        raise PlatformError(
            "PERIL_STRUCTURE_RECONCILIATION_FAILED",
            "The perils were not modelled on the same holdout",
            409,
            f"{detail}. FR-MODEL-60 sums modelled burning cost across perils and compares "
            "the total to one observed figure; perils scored on different holdouts sum "
            "over different books.",
        )


def _model_refs(peril: PerilComponent) -> list[ArtifactRef]:
    """The model references one peril carries, whichever method it uses."""
    return [
        ref
        for ref in (peril.frequency_model, peril.severity_model, peril.burning_cost_model)
        if ref is not None
    ]
