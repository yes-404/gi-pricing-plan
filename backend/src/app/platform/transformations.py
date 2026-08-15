"""Bandings and Groupings: the governance around a factor transformation (`02` §3.2, §3.3).

`pricing-core` proposes the boundaries and the mapping; this decides who may, against
which version, and what the act leaves behind. Three rules carry the weight:

* **FR-MODEL-12 / FR-MODEL-16** — both artifacts are **versioned, never edited**, and
  creation is audited. A Model pins the version it was fitted with, so an edited banding
  would silently change what every model fitted on it was fitted on. Allocating the next
  version is the only write this module performs.
* **`02` R1** — a proposal is derived against a *validated* Dataset Version, through `01`'s
  own `fittable_or_refuse`. Proposing bands from data the platform has refused to fit on
  would produce evidence (FR-MODEL-10) for a fit that cannot happen.
* **FR-MODEL-9 / FR-MODEL-14** — the platform *proposes*; the actuary edits; what is stored
  is what was accepted. So proposing writes nothing at all, and `create_*` takes whatever
  the caller sends back.

**Proposing reads the version's parquet in the request.** `02` §5.1 declares both propose
endpoints as ordinary calls rather than `202`-plus-Job, and it is right to: the factor
workbench is interactive, and only the columns the proposal names are read.
"""

from __future__ import annotations

import io
from uuid import UUID

import polars as pl
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BandingRow, BlobRow, GroupingRow
from app.errors import PlatformError
from app.platform import audit, datasets, rbac
from app.platform.blobs import BlobStore, to_ref
from model_schema import (
    Banding,
    BandingEvaluation,
    BandingProposal,
    Grouping,
    GroupingEvaluation,
    GroupingProposal,
    JobSource,
    Permission,
    Principal,
)
from pricing_core.modelling import (
    ModellingError,
    band_statistics,
    grouping_evidence,
    propose_banding,
    propose_grouping,
)

__all__ = [
    "create_banding",
    "create_grouping",
    "evaluate_banding_for_version",
    "evaluate_grouping_for_version",
    "list_bandings",
    "list_groupings",
    "load_bandings",
    "load_groupings",
    "propose_banding_for_version",
    "propose_grouping_for_version",
    "to_banding",
    "to_grouping",
]


def to_banding(row: BandingRow) -> Banding:
    return Banding.model_validate(
        {**row.body, "id": row.id, "version": row.version, "dataset_id": row.dataset_id}
    )


def to_grouping(row: GroupingRow) -> Grouping:
    return Grouping.model_validate(
        {**row.body, "id": row.id, "version": row.version, "dataset_id": row.dataset_id}
    )


async def propose_banding_for_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    blob_store: BlobStore,
    proposal: BandingProposal,
    slug: str,
) -> Banding:
    """Derive boundaries and their evidence, and persist nothing (FR-MODEL-9)."""
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )
    version = await datasets.fittable_or_refuse(
        session, workspace_id=workspace_id, version_id=proposal.dataset_version_id
    )
    frame = await _read_columns(
        session,
        blob_store,
        version,
        columns=(
            proposal.column,
            proposal.exposure_column,
            proposal.claim_count_column,
            proposal.claim_amount_column,
        ),
    )
    try:
        return propose_banding(frame, proposal, dataset_id=version.dataset_id, slug=slug)
    except ModellingError as exc:
        raise _refuse(exc, "The banding could not be proposed") from exc


async def propose_grouping_for_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    blob_store: BlobStore,
    proposal: GroupingProposal,
    slug: str,
) -> Grouping:
    """Derive a mapping and its evidence, and persist nothing (FR-MODEL-14)."""
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )
    version = await datasets.fittable_or_refuse(
        session, workspace_id=workspace_id, version_id=proposal.dataset_version_id
    )
    frame = await _read_columns(
        session,
        blob_store,
        version,
        columns=(
            proposal.column,
            proposal.exposure_column,
            proposal.claim_count_column,
            proposal.claim_amount_column,
        ),
    )
    try:
        return propose_grouping(frame, proposal, dataset_id=version.dataset_id, slug=slug)
    except ModellingError as exc:
        raise _refuse(exc, "The grouping could not be proposed") from exc


async def evaluate_banding_for_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    blob_store: BlobStore,
    evaluation: BandingEvaluation,
) -> Banding:
    """Recompute FR-MODEL-10's statistics for boundaries the actuary edited (FR-MODEL-83).

    `/propose` derives boundaries from a **method** and cannot accept one, so without this
    "the proposal is always editable" means editable but unmeasurable — and an actuary who
    moves a boundary has to fit a model to find out what it did.

    Persists nothing, and does not renumber or re-slug: what comes back is the banding that
    went in, with `band_stats` and `derived_on_dataset_version_id` filled from this version.
    """
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )
    version = await datasets.fittable_or_refuse(
        session, workspace_id=workspace_id, version_id=evaluation.dataset_version_id
    )
    banding = evaluation.banding
    frame = await _read_columns(
        session,
        blob_store,
        version,
        columns=(
            banding.column,
            evaluation.exposure_column,
            evaluation.claim_count_column,
            evaluation.claim_amount_column,
        ),
    )
    try:
        stats = band_statistics(
            frame,
            banding,
            exposure_column=evaluation.exposure_column,
            claim_count_column=evaluation.claim_count_column,
            claim_amount_column=evaluation.claim_amount_column,
        )
    except ModellingError as exc:
        raise _refuse(exc, "The banding could not be evaluated") from exc
    return banding.model_copy(
        update={
            "band_stats": stats,
            "derived_on_dataset_version_id": evaluation.dataset_version_id,
        }
    )


async def evaluate_grouping_for_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    blob_store: BlobStore,
    evaluation: GroupingEvaluation,
) -> Grouping:
    """Recompute FR-MODEL-15's evidence for a mapping the actuary edited (FR-MODEL-83).

    This is the half §5.3 names explicitly: merging levels shows the deviance/df trade-off
    *before* the grouping is saved. The p-value is the whole answer to "could these levels
    be the same?", and computing it only on save is computing it after the decision.
    """
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )
    version = await datasets.fittable_or_refuse(
        session, workspace_id=workspace_id, version_id=evaluation.dataset_version_id
    )
    grouping = evaluation.grouping
    frame = await _read_columns(
        session,
        blob_store,
        version,
        columns=(
            grouping.column,
            evaluation.exposure_column,
            evaluation.claim_count_column,
            evaluation.claim_amount_column,
        ),
    )
    try:
        evidence = grouping_evidence(
            frame,
            dict(grouping.mapping),
            column=grouping.column,
            exposure_column=evaluation.exposure_column,
            claim_count_column=evaluation.claim_count_column,
            claim_amount_column=evaluation.claim_amount_column,
        )
    except ModellingError as exc:
        raise _refuse(exc, "The grouping could not be evaluated") from exc
    return grouping.model_copy(
        update={
            "evidence": evidence,
            "derived_on_dataset_version_id": evaluation.dataset_version_id,
        }
    )


async def create_banding(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    banding: Banding,
) -> BandingRow:
    """Persist a Banding, or allocate the next version of an existing slug (FR-MODEL-12).

    Versioned rather than edited, for the reason a Model Spec pins a version: re-cutting a
    boundary in place would silently change what every model fitted on it was fitted on.
    """
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )
    version = 1 + (
        await session.execute(
            select(func.coalesce(func.max(BandingRow.version), 0)).where(
                BandingRow.workspace_id == workspace_id, BandingRow.slug == banding.slug
            )
        )
    ).scalar_one()

    row = BandingRow(
        workspace_id=workspace_id,
        dataset_id=banding.dataset_id,
        slug=banding.slug,
        version=version,
        column_name=banding.column,
        body=banding.model_dump(mode="json", exclude={"id", "version", "dataset_id"}),
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="banding.created",
        entity_ref=f"banding:{banding.slug}@{version}",
        after={
            "slug": banding.slug,
            "version": version,
            "column": banding.column,
            "method": banding.method.value,
            "bands": len(banding.labels),
            "derived_on_dataset_version_id": (
                str(banding.derived_on_dataset_version_id)
                if banding.derived_on_dataset_version_id
                else None
            ),
        },
    )
    return row


async def create_grouping(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    grouping: Grouping,
) -> GroupingRow:
    """Persist a Grouping, or allocate the next version of an existing slug (FR-MODEL-16).

    FR-MODEL-16 makes creation an audited event in its own right: grouping is a modelling
    decision, and the generated model document lists every one with its method.
    """
    await rbac.require_permission(
        session, workspace_id=workspace_id, principal=actor, permission=Permission.MODEL_FIT
    )
    version = 1 + (
        await session.execute(
            select(func.coalesce(func.max(GroupingRow.version), 0)).where(
                GroupingRow.workspace_id == workspace_id, GroupingRow.slug == grouping.slug
            )
        )
    ).scalar_one()

    row = GroupingRow(
        workspace_id=workspace_id,
        dataset_id=grouping.dataset_id,
        slug=grouping.slug,
        version=version,
        column_name=grouping.column,
        parent_grouping_id=grouping.parent_grouping_id,
        body=grouping.model_dump(mode="json", exclude={"id", "version", "dataset_id"}),
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="grouping.created",
        entity_ref=f"grouping:{grouping.slug}@{version}",
        after={
            "slug": grouping.slug,
            "version": version,
            "column": grouping.column,
            "method": grouping.method.value,
            "source_levels": len(grouping.mapping),
            "target_levels": len(grouping.target_levels),
            "unseen_level_behaviour": grouping.unseen_level_behaviour.value,
        },
    )
    return row


async def list_bandings(
    session: AsyncSession, *, workspace_id: UUID, dataset_id: UUID | None = None
) -> list[BandingRow]:
    query = select(BandingRow).where(BandingRow.workspace_id == workspace_id)
    if dataset_id is not None:
        query = query.where(BandingRow.dataset_id == dataset_id)
    query = query.order_by(BandingRow.slug, BandingRow.version.desc())
    return list((await session.execute(query)).scalars())


async def list_groupings(
    session: AsyncSession, *, workspace_id: UUID, dataset_id: UUID | None = None
) -> list[GroupingRow]:
    query = select(GroupingRow).where(GroupingRow.workspace_id == workspace_id)
    if dataset_id is not None:
        query = query.where(GroupingRow.dataset_id == dataset_id)
    query = query.order_by(GroupingRow.slug, GroupingRow.version.desc())
    return list((await session.execute(query)).scalars())


async def load_bandings(
    session: AsyncSession, *, workspace_id: UUID, ids: list[UUID]
) -> dict[UUID, Banding]:
    """The bandings a set of factors pins, keyed by id for `resolve_factors`.

    A missing one is a `404`, never an empty map: `resolve_factors` refuses a factor whose
    artifact was not supplied, and letting it get that far would report a resolution
    failure for what is really a dangling reference.
    """
    if not ids:
        return {}
    rows = list(
        (
            await session.execute(
                select(BandingRow).where(
                    BandingRow.workspace_id == workspace_id, BandingRow.id.in_(ids)
                )
            )
        ).scalars()
    )
    _refuse_missing({row.id for row in rows}, ids, kind="banding")
    return {row.id: to_banding(row) for row in rows}


async def load_groupings(
    session: AsyncSession, *, workspace_id: UUID, ids: list[UUID]
) -> dict[UUID, Grouping]:
    if not ids:
        return {}
    rows = list(
        (
            await session.execute(
                select(GroupingRow).where(
                    GroupingRow.workspace_id == workspace_id, GroupingRow.id.in_(ids)
                )
            )
        ).scalars()
    )
    _refuse_missing({row.id for row in rows}, ids, kind="grouping")
    return {row.id: to_grouping(row) for row in rows}


def _refuse_missing(found: set[UUID], wanted: list[UUID], *, kind: str) -> None:
    missing = [str(i) for i in wanted if i not in found]
    if missing:
        raise PlatformError(
            "NOT_FOUND",
            f"The spec names {kind}s that do not exist",
            404,
            f"Unknown {kind} id(s): {', '.join(missing)}.",
        )


async def _read_columns(
    session: AsyncSession,
    blob_store: BlobStore,
    version: object,
    *,
    columns: tuple[str, ...],
) -> pl.DataFrame:
    """The named columns of the version's table, and no others.

    Column-projected because a proposal needs four columns of a book that may hold sixty,
    and this runs inside a request. Absent columns are dropped rather than demanded here:
    `pricing-core` refuses with the requirement-shaped message, and duplicating that
    judgement would give one condition two error texts.
    """
    entry = version.tables[0]  # type: ignore[attr-defined]
    blob = await session.get(BlobRow, entry["blob"]["sha256"])
    if blob is None:
        raise PlatformError(
            "NOT_FOUND",
            "A table's blob is missing",
            404,
            f"Version {version.id} names a blob that is not in the store.",  # type: ignore[attr-defined]
        )
    payload = io.BytesIO(await blob_store.read(to_ref(blob)))
    available = set(pl.read_parquet_schema(payload))
    payload.seek(0)
    wanted = [c for c in dict.fromkeys(columns) if c in available]
    if not wanted:
        raise PlatformError(
            "FACTOR_RESOLUTION_FAILED",
            "The dataset version has none of the columns this proposal names",
            409,
            f"Wanted {list(columns)}; the version has {sorted(available)[:20]}.",
        )
    return pl.read_parquet(payload, columns=wanted)


def _refuse(exc: ModellingError, title: str) -> PlatformError:
    """Give a `pricing-core` failure its HTTP shape.

    The core names the failure and the platform renders it — the same seam the fit handler
    uses, so a proposal that fails and a fit that fails report the same code for the same
    cause rather than two codes a client has to learn separately.
    """
    return PlatformError(exc.code, title, 409, str(exc))
