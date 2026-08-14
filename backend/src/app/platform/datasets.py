"""Dataset versions and the gate (`01` §1.3, §3.1, FR-DATA-2, FR-DATA-17, FR-DATA-40).

> A Model may only be fitted on a Dataset Version whose status is `validated`. There is no
> override, no "force fit", and no admin bypass.

This module is where that is true or not. Three things make it true:

* **Version allocation is serialised** (FR-DATA-2, ID-2). `version = max + 1` computed
  under a lock, with a unique constraint behind it — two concurrent ingestions must not
  both become `@12`, because a reference to `@12` has to mean one body of data for ever.
* **`validated` is reachable only through `promote`**, which reads the report and refuses
  unless it passed and every warning is acknowledged. There is no setter.
* **Every transition is audited in the caller's transaction** (`06` R2), so a version's
  status history is as trustworthy as the version itself.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DatasetRow, DatasetVersionRow, SourceRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit, rbac
from model_schema import (
    VALID_DATASET_TRANSITIONS,
    DatasetKind,
    DatasetStatus,
    JobSource,
    Permission,
    Principal,
    SourceKind,
)

__all__ = [
    "archive_version",
    "create_dataset",
    "create_source",
    "fittable_or_refuse",
    "new_version",
    "promote_to_validated",
    "transition",
]

_log = get_logger("app.datasets")

#: Namespace for the advisory lock that serialises version allocation, distinct from the
#: audit chain's so the two never contend.
_VERSION_LOCK_NAMESPACE = 0x4749_5044  # "GIPD"


async def create_source(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    kind: SourceKind,
    config: dict[str, Any] | None = None,
    credentials_secret_ref: str | None = None,
) -> SourceRow:
    """Register a Source (FR-DATA-1).

    `credentials_secret_ref` must be a `secret:<slug>` reference. A value here would be a
    credential in a table the API returns, which `07` R3 forbids — and the check is a
    database constraint as well, because "we always pass a reference" is a convention and
    conventions are what a hurried change breaks.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.DATASET_WRITE,
    )
    if credentials_secret_ref is not None and not credentials_secret_ref.startswith(
        "secret:"
    ):
        raise PlatformError(
            "VALIDATION_FAILED",
            "Credentials must be a secret reference",
            422,
            "`07` FR-PLAT-25: credentials are referenced as `secret:<slug>` and resolved "
            "at the point of use. A value here would be stored, returned and logged.",
        )

    row = SourceRow(
        workspace_id=workspace_id,
        slug=slug,
        kind=kind.value,
        config=config or {},
        credentials_secret_ref=credentials_secret_ref,
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError:
        raise PlatformError(
            "VALIDATION_FAILED", "Source already exists", 409, f"Source {slug!r} exists."
        ) from None

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="source.created",
        entity_ref=f"reference_table:{slug}@1",
        after={"slug": slug, "kind": kind.value, "credentials": credentials_secret_ref},
    )
    return row


async def create_dataset(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    description: str | None = None,
) -> DatasetRow:
    """Create a Dataset — the named container its versions belong to (`01` §4.1)."""
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.DATASET_WRITE,
    )
    row = DatasetRow(workspace_id=workspace_id, slug=slug, description=description)
    session.add(row)
    try:
        await session.flush()
    except IntegrityError:
        raise PlatformError(
            "VALIDATION_FAILED", "Dataset already exists", 409, f"Dataset {slug!r} exists."
        ) from None

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="dataset.created",
        entity_ref=f"dataset:{slug}@1",
        after={"slug": slug},
    )
    return row


async def new_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    dataset_id: UUID,
    kind: DatasetKind = DatasetKind.INGESTED,
    source_id: UUID | None = None,
    derived_from: dict[str, Any] | None = None,
) -> DatasetVersionRow:
    """Allocate the next version at `max + 1`, in `draft` (FR-DATA-2, ID-2).

    Serialised by an advisory lock per dataset. Without it two concurrent ingestions both
    read `max = 11` and both try `@12`; the unique constraint then fails one of them, which
    is safe but means a long ingestion is thrown away at the last moment. The lock makes
    the second wait and get `@13`.
    """
    dataset = await session.get(DatasetRow, dataset_id)
    if dataset is None or dataset.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Dataset not found", 404, f"No dataset {dataset_id}."
        )

    await session.execute(
        text("SELECT pg_advisory_xact_lock(:ns, :key)").bindparams(
            ns=_VERSION_LOCK_NAMESPACE, key=(dataset_id.int & 0x7FFF_FFFF) - 0x4000_0000
        )
    )
    highest = (
        await session.execute(
            select(func.max(DatasetVersionRow.version)).where(
                DatasetVersionRow.dataset_id == dataset_id
            )
        )
    ).scalar()

    row = DatasetVersionRow(
        workspace_id=workspace_id,
        dataset_id=dataset_id,
        version=(highest or 0) + 1,
        status=DatasetStatus.DRAFT.value,
        kind=kind.value,
        source_id=source_id,
        derived_from=derived_from,
    )
    session.add(row)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="dataset_version.created",
        entity_ref=f"dataset_version:{dataset.slug}@{row.version}",
        after={"version": row.version, "status": DatasetStatus.DRAFT.value, "kind": kind.value},
    )
    return row


async def transition(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    version_id: UUID,
    to_status: DatasetStatus,
    justification: str | None = None,
) -> DatasetVersionRow:
    """Move a version along its lifecycle, refusing what `01` does not allow.

    **`validated` is not reachable here.** It is reachable only through
    `promote_to_validated`, which reads the report. A transition function that could set
    it would be the override `01` §1.3 says does not exist.
    """
    if to_status is DatasetStatus.VALIDATED:
        raise PlatformError(
            "DATASET_VERSION_IMMUTABLE",
            "validated is not a transition",
            409,
            "`01` §1.3: a version becomes validated only through a passing validation "
            "report with every warning acknowledged. Use promote_to_validated.",
        )
    return await _transition(
        session,
        workspace_id=workspace_id,
        actor=actor,
        version_id=version_id,
        to_status=to_status,
        justification=justification,
    )


async def _transition(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    version_id: UUID,
    to_status: DatasetStatus,
    justification: str | None = None,
    extra_after: dict[str, Any] | None = None,
    also_set: dict[str, Any] | None = None,
) -> DatasetVersionRow:
    row = await _load(session, workspace_id, version_id)
    current = DatasetStatus(row.status)

    if to_status not in VALID_DATASET_TRANSITIONS[current]:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Invalid dataset version transition",
            409,
            f"A version in {current.value!r} cannot move to {to_status.value!r} (`01` §4.2).",
        )

    # Set the accompanying fields *before* the status, in the same flush. The
    # `validated_names_its_report` constraint is checked per row, not per statement, so
    # writing the status first fails on a row that is only half updated — which is the
    # constraint doing its job and the caller getting the order wrong.
    for field, value in (also_set or {}).items():
        setattr(row, field, value)
    row.status = to_status.value
    await session.flush()

    dataset = await session.get(DatasetRow, row.dataset_id)
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=f"dataset_version.{to_status.value}",
        entity_ref=f"dataset_version:{dataset.slug if dataset else '?'}@{row.version}",
        before={"status": current.value},
        after={"status": to_status.value, **(extra_after or {})},
        justification=justification,
    )
    return row


async def promote_to_validated(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    version_id: UUID,
    report_id: UUID,
    report_passed: bool,
    unacknowledged_warnings: int,
) -> DatasetVersionRow:
    """The only way to `validated` (FR-DATA-17, `01` §1.3).

    `report_passed` and `unacknowledged_warnings` are passed in rather than read here
    because the report belongs to the validation slice; what this function owns is the
    *rule* — zero fails, zero errors, every warning acknowledged — and the refusal.

    The refusal is the point of the whole module. An actuary who believes a failing rule is
    wrong changes the rule, and that change is reviewed and audited.
    """
    if not report_passed:
        raise PlatformError(
            "VALIDATION_HAS_FAILURES",
            "The validation report did not pass",
            409,
            "`01` §1.3: there is no override, no force-fit and no admin bypass. If a "
            "failing rule is wrong, change the rule — the change is reviewed and audited.",
        )
    if unacknowledged_warnings:
        raise PlatformError(
            "WARN_NOT_ACKNOWLEDGED",
            "Warnings are not acknowledged",
            409,
            f"{unacknowledged_warnings} warning(s) require an explicit, audited "
            "acknowledgement by a Principal before this version can be validated "
            "(FR-DATA-17).",
        )

    return await _transition(
        session,
        workspace_id=workspace_id,
        actor=actor,
        version_id=version_id,
        to_status=DatasetStatus.VALIDATED,
        extra_after={"validation_report_id": str(report_id)},
        also_set={"validation_report_id": report_id},
    )


async def archive_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    version_id: UUID,
    reason: str,
) -> DatasetVersionRow:
    """Soft-delete only (ID-5): nothing is removed from the database."""
    if not reason.strip():
        raise PlatformError(
            "VALIDATION_FAILED", "Archiving requires a reason", 422, "ID-5 / FR-DATA-38."
        )
    return await _transition(
        session,
        workspace_id=workspace_id,
        actor=actor,
        version_id=version_id,
        to_status=DatasetStatus.ARCHIVED,
        justification=reason,
    )


async def fittable_or_refuse(
    session: AsyncSession, *, workspace_id: UUID, version_id: UUID
) -> DatasetVersionRow:
    """The check `02` calls before fitting anything (`01` §1.3).

    One function, so there is one place where "may I fit on this?" is answered and one
    place to read when someone asks how the gate works.
    """
    row = await _load(session, workspace_id, version_id)
    if DatasetStatus(row.status) is not DatasetStatus.VALIDATED:
        raise PlatformError(
            "DATASET_NOT_VALIDATED",
            "Dataset version is not validated",
            409,
            f"This version has status {row.status!r}; fitting requires 'validated' "
            "(`01` §1.3). There is no override.",
        )
    return row


async def _load(
    session: AsyncSession, workspace_id: UUID, version_id: UUID
) -> DatasetVersionRow:
    row = await session.get(DatasetVersionRow, version_id, with_for_update=True)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Dataset version not found", 404, f"No version {version_id}."
        )
    return row
