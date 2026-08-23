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

from collections.abc import Mapping
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    DatasetRow,
    DatasetSplitRow,
    DatasetVersionRow,
    SourceRow,
    SubjectPurgeRow,
)
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit, rbac
from model_schema import (
    VALID_DATASET_TRANSITIONS,
    ArtifactRef,
    DataDictionaryEntry,
    Dataset,
    DatasetKind,
    DatasetSplit,
    DatasetStatus,
    JobSource,
    Permission,
    Principal,
    RecordGrain,
    ScopeType,
    SourceKind,
)

__all__ = [
    "archive_version",
    "create_dataset",
    "create_source",
    "derive_version",
    "fittable_or_refuse",
    "lineage_of",
    "list_splits",
    "load_dataset",
    "load_version",
    "new_version",
    "promote_to_validated",
    "purge_subject",
    "record_split",
    "resolve_artifact_ref",
    "to_schema",
    "to_split",
    "transition",
    "update_dictionary",
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
    name: str = "",
    line_of_business: str | None = None,
    territory: str | None = None,
    currency: str | None = None,
    default_record_grain: RecordGrain | None = None,
    data_dictionary: Mapping[str, DataDictionaryEntry] | None = None,
) -> DatasetRow:
    """Create a Dataset — the named container its versions belong to (`01` §4.1)."""
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.DATASET_WRITE,
    )
    row = DatasetRow(
        workspace_id=workspace_id,
        slug=slug,
        name=name or slug,
        description=description,
        line_of_business=line_of_business,
        territory=territory,
        currency=currency or "GBP",
        default_record_grain=(
            default_record_grain.value if default_record_grain is not None else None
        ),
        data_dictionary=_dictionary_json(data_dictionary or {}),
    )
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
        after={"slug": slug, "name": row.name, "currency": row.currency},
    )
    return row


def _dictionary_json(entries: Mapping[str, DataDictionaryEntry]) -> dict[str, Any]:
    return {column: entry.model_dump(mode="json") for column, entry in entries.items()}


async def load_dataset(
    session: AsyncSession, *, workspace_id: UUID, slug: str
) -> DatasetRow:
    """A Dataset by slug, or a 404 that does not confirm it exists elsewhere."""
    row = (
        await session.execute(
            select(DatasetRow).where(
                DatasetRow.workspace_id == workspace_id, DatasetRow.slug == slug
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError("NOT_FOUND", "Dataset not found", 404, f"No dataset {slug!r}.")
    return row


async def load_dataset_by_id(
    session: AsyncSession, *, workspace_id: UUID, dataset_id: UUID
) -> DatasetRow:
    """A Dataset by id, workspace-scoped.

    Ingestion holds an id rather than a slug, and a caller that fetched by id alone would
    read another workspace's dataset — the id is a UUID, not a secret.
    """
    row = (
        await session.execute(
            select(DatasetRow).where(
                DatasetRow.workspace_id == workspace_id, DatasetRow.id == dataset_id
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError("NOT_FOUND", "Dataset not found", 404, f"No dataset {dataset_id}.")
    return row


async def update_dictionary(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    entries: Mapping[str, DataDictionaryEntry],
) -> DatasetRow:
    """Replace the Data Dictionary, audited with before and after (`01` §5.1, NFR-DATA-8).

    A **replace**, not a merge, and the audit event carries both states. The dictionary
    decides which columns may be modelled at all (FR-OVR-9), so "who removed the
    `special_category` marking from this column, and when?" has to be answerable — and a
    merge would make a removal indistinguishable from an omission.
    """
    row = await load_dataset(session, workspace_id=workspace_id, slug=slug)
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.DATASET_WRITE,
        resource=rbac.ResourceRef(scope_type=ScopeType.DATASET, scope_id=row.id),
    )

    before = dict(row.data_dictionary)
    row.data_dictionary = _dictionary_json(entries)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="dataset.dictionary_updated",
        entity_ref=f"dataset:{slug}",
        before={"data_dictionary": before},
        after={"data_dictionary": row.data_dictionary},
    )
    return row


def to_schema(
    row: DatasetRow,
    *,
    latest_version: tuple[int, str] | None = None,
    last_validated: tuple[int, datetime] | None = None,
) -> Dataset:
    """The row as the `01` §4.1 artifact the API returns.

    `latest_version` is a `(version, status)` pair rather than two parameters so a caller
    cannot supply one without the other — the schema refuses that combination anyway
    (FR-DATA-50), and a pair turns a runtime `ValidationError` into a type error.
    """
    return Dataset(
        id=row.id,
        workspace_id=row.workspace_id,
        slug=row.slug,
        name=row.name,
        description=row.description,
        line_of_business=row.line_of_business,
        territory=row.territory,
        currency=row.currency,
        default_record_grain=(
            RecordGrain(row.default_record_grain) if row.default_record_grain else None
        ),
        data_dictionary={
            column: DataDictionaryEntry.model_validate(entry)
            for column, entry in row.data_dictionary.items()
        },
        validation_rule_set_id=row.validation_rule_set_id,
        latest_version=latest_version[0] if latest_version else None,
        latest_version_status=(
            DatasetStatus(latest_version[1]) if latest_version else None
        ),
        last_validated_version=last_validated[0] if last_validated else None,
        last_validated_at=last_validated[1] if last_validated else None,
        created_at=row.created_at,
        archived_at=row.archived_at,
    )


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
    row = await load_version(session, workspace_id=workspace_id, version_id=version_id)
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


async def begin_validation(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    version_id: UUID,
) -> DatasetVersionRow:
    """Mark a version as being validated, if it is not already (`01` §4.2).

    `validating` means *a validation is in flight*, and until now nothing in the platform
    set it except the seed doing so explicitly — which is why a failing run could not
    conclude: `draft → failed` is not a transition, and it should not be. The run has to
    open the state it later closes.

    Idempotent for a version already `validating`: a re-run of the same job must not fail
    on a transition to the state it is already in.
    """
    row = await load_version(session, workspace_id=workspace_id, version_id=version_id)
    if DatasetStatus(row.status) is DatasetStatus.VALIDATING:
        return row
    return await _transition(
        session, workspace_id=workspace_id, actor=actor, version_id=version_id,
        to_status=DatasetStatus.VALIDATING,
    )


async def conclude_failed_validation(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    version_id: UUID,
) -> DatasetVersionRow:
    """Where a version goes when its report does not pass (FR-DATA-43, FR-DATA-23).

    Two destinations, and which one depends on what the version *was*:

    * A version being validated for the first time goes to **`failed`**. It never earned
      any standing, and `FAILED → VALIDATING` exists so it can be re-validated once the
      data or the rule set is corrected — which is the loop `01` §1.3 describes.
    * A version that was already `validated` and is being re-validated goes back to
      **`draft`**, which is FR-DATA-23 exactly: it *was* good, and returning it to `draft`
      says so, while every Model fitted on it is flagged.

    Until this existed nothing set `failed` at all — the enum and the transition map both
    carried it and no code path reached it — so a failing version rested in `validating`,
    which every screen showing a status reads as "still running". Found by exercising the
    exit demo, where version 1 is the deliberate failure the whole criterion is about
    (OQ-DATA-7, decided 2026-08-15).
    """
    row = await load_version(session, workspace_id=workspace_id, version_id=version_id)
    was_validated = row.validation_report_id is not None

    if not was_validated:
        return await _transition(
            session, workspace_id=workspace_id, actor=actor, version_id=version_id,
            to_status=DatasetStatus.FAILED,
        )

    # FR-DATA-23. The report reference is cleared with the status: left in place it names
    # a *passing* report on a version that has just failed, and the
    # `validated_names_its_report` constraint then stops biting on a forced `UPDATE` back
    # to `validated` — a stale pointer that made a database-level guard decorative.
    return await _transition(
        session, workspace_id=workspace_id, actor=actor, version_id=version_id,
        to_status=DatasetStatus.DRAFT,
        extra_after={"validation_report_id": None},
        also_set={"validation_report_id": None},
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
    row = await load_version(session, workspace_id=workspace_id, version_id=version_id)
    if DatasetStatus(row.status) is not DatasetStatus.VALIDATED:
        raise PlatformError(
            "DATASET_NOT_VALIDATED",
            "Dataset version is not validated",
            409,
            f"This version has status {row.status!r}; fitting requires 'validated' "
            "(`01` §1.3). There is no override.",
        )
    return row


async def load_version(
    session: AsyncSession, *, workspace_id: UUID, version_id: UUID
) -> DatasetVersionRow:
    """A version, or a `404` naming it — **without** `01` §1.3's validated gate.

    Public since 2026-08-18 (W5, backtests), which needs to answer a question *before* the
    gate: a request to backtest the model's own holdout must be refused as "that is the data
    it learned on", not as "that version is not validated". A split's parts are derived
    versions and stay `draft`, so the gate answers first — and its answer invites the caller
    to validate the holdout, after which the request would be allowed. The order of two
    correct refusals is load-bearing.

    Every other caller wants `fittable_or_refuse`, which is this plus the gate.
    """
    row = await session.get(DatasetVersionRow, version_id, with_for_update=True)
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Dataset version not found", 404, f"No version {version_id}."
        )
    return row


async def resolve_artifact_ref(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> bool:
    """`dataset_version:<slug>@<version>` → does that version exist? (`06` FR-GOV-36.)

    `False`, having done nothing, for a reference that is not this module's — the contract
    `api/approvals.py`'s fan-out is built on.

    The only one of the six that needs a join: the slug in the reference is the **dataset's**
    (`uq_datasets_workspace_slug`) and the version is the snapshot's
    (`uq_dataset_versions_dataset_version`), so neither table holds the whole key on its own.
    Together they do, and `load_version`'s by-id lookup cannot be reused for it.

    Neither status nor `01` §1.3's validated gate is consulted. FR-GOV-36 asks whether the
    version exists; `fittable_or_refuse` asks whether it may be fitted on, and answering that
    question here would refuse a submission whose whole purpose might be to get the version
    validated.
    """
    if artifact_ref.type != "dataset_version":
        return False
    found = (
        await session.execute(
            select(DatasetVersionRow.id)
            .join(DatasetRow, DatasetRow.id == DatasetVersionRow.dataset_id)
            .where(
                DatasetVersionRow.workspace_id == workspace_id,
                DatasetRow.slug == artifact_ref.slug,
                DatasetVersionRow.version == artifact_ref.version,
            )
        )
    ).scalar_one_or_none()
    if found is None:
        raise PlatformError(
            "NOT_FOUND",
            "Dataset version not found",
            404,
            f"{artifact_ref} resolves to no dataset version in this workspace.",
        )
    return True


async def derive_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    parent_version_id: UUID,
    operation: str,
    params: dict[str, Any],
) -> DatasetVersionRow:
    """Create a Derived Dataset Version from a declared operation (FR-DATA-33, FR-DATA-34).

    A derived version **inherits nothing about its validity**. FR-DATA-34 is explicit that
    it must be validated in its own right: a stratified sample of a validated dataset can
    break rules the parent passed — an exposure band with two claims in the sample and two
    thousand in the parent fails a plausibility rule the parent never came near.

    It inherits nothing about its **rows** either, and only `split` can currently produce
    its own (FR-DATA-44). The rest are refused here — FR-DATA-45, the decided half of
    OQ-DATA-8 — because a version recording an operation nobody performed is a derivation
    that cannot be reproduced or defended, and it fails silently: the numbers look right.
    """
    if operation not in DERIVED_OPERATIONS:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Unknown derivation operation",
            422,
            f"{operation!r} is not one of {sorted(DERIVED_OPERATIONS)} (FR-DATA-33). "
            "A derivation the platform cannot describe is one it cannot reproduce.",
        )
    if operation in UNMATERIALISED_OPERATIONS:
        raise PlatformError(
            "DERIVATION_NOT_MATERIALISED",
            "This derivation is not built yet",
            501,
            f"{operation!r} is declared by FR-DATA-33 but the platform cannot yet produce "
            "its rows, so it is refused rather than returning a version that claims the "
            "operation and holds the parent's data unchanged (FR-DATA-45, OQ-DATA-8). "
            "`split` is materialised (FR-DATA-44).",
        )
    if operation in _SEEDED_OPERATIONS and "seed" not in params:
        raise PlatformError(
            "VALIDATION_FAILED",
            "This derivation needs a seed",
            422,
            f"{operation!r} is stochastic; without a recorded seed the version cannot be "
            "reproduced, and FR-OVR-8 requires identical inputs to give identical outputs.",
        )

    parent = await load_version(session, workspace_id=workspace_id, version_id= parent_version_id)
    child = await new_version(
        session,
        workspace_id=workspace_id,
        actor=actor,
        dataset_id=parent.dataset_id,
        kind=DatasetKind.DERIVED,
        derived_from={
            "parent_version_id": str(parent_version_id),
            "operation": operation,
            "params": params,
        },
    )
    # Inherited from the parent (FR-DATA-34) — schema and rule set, never validity. The
    # rows are the caller's to materialise: `split` replaces this wholesale (FR-DATA-44),
    # and every other operation was refused above (FR-DATA-45).
    child.tables = parent.tables
    await session.flush()
    return child


#: FR-DATA-33's declared operations. Anything else is refused: a derivation the platform
#: cannot describe is one it cannot reproduce, and a derived dataset nobody can rebuild is
#: a dataset whose model cannot be defended.
DERIVED_OPERATIONS: frozenset[str] = frozenset(
    {"sample", "split", "filter", "join", "aggregate"}
)

#: The stochastic ones. FR-OVR-8 requires a seed on anything that could vary.
_SEEDED_OPERATIONS: frozenset[str] = frozenset({"sample", "split"})

#: Declared, but unable to produce their own rows — refused until they can (FR-DATA-45,
#: OQ-DATA-8 decided 2026-08-17). Derived by subtraction from `DERIVED_OPERATIONS` rather
#: than listed, so materialising one is a single edit in one place and cannot leave a
#: refusal behind for an operation that now works.
UNMATERIALISED_OPERATIONS: frozenset[str] = DERIVED_OPERATIONS - {"split"}


async def lineage_of(
    session: AsyncSession, *, workspace_id: UUID, version_id: UUID
) -> dict[str, Any]:
    """What this was built from, and what was built from it (FR-DATA-35).

    Both directions, because they answer different questions. "What was this built from?"
    defends a model; "what depends on this?" is what someone asks before archiving a
    version, and getting it wrong means discovering the dependency when a rating version
    stops resolving.
    """
    row = await load_version(session, workspace_id=workspace_id, version_id=version_id)

    children = (
        await session.execute(
            select(DatasetVersionRow).where(
                DatasetVersionRow.workspace_id == workspace_id,
                DatasetVersionRow.derived_from["parent_version_id"].astext
                == str(version_id),
            )
        )
    ).scalars().all()

    parent_id = (row.derived_from or {}).get("parent_version_id")
    return {
        "version_id": str(version_id),
        "built_from": {
            "parent_version_id": parent_id,
            "operation": (row.derived_from or {}).get("operation"),
            "ingestion_run_id": str(row.ingestion_run_id) if row.ingestion_run_id else None,
            "source_id": str(row.source_id) if row.source_id else None,
        },
        "depends_on_this": [
            {"version_id": str(c.id), "version": c.version,
             "operation": (c.derived_from or {}).get("operation")}
            for c in children
        ],
    }


async def purge_subject(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    dataset_id: UUID,
    subject_token: str,
    reason: str,
) -> SubjectPurgeRow:
    """GDPR erasure of one pseudonymous subject across a Dataset's versions (FR-DATA-39).

    Admin-only and audited. The purge is *recorded* even though the data is gone —
    especially because it is: an erasure with no record is indistinguishable from data that
    was never there, and a regulator asking "did you action this request?" needs an answer
    that is not a shrug.

    Erasure works on the pseudonymous token rather than an identifier, because FR-DATA-13
    means the platform never held the identity. The requester maps subject to token; the
    platform erases the token.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.ADMIN_MANAGE_SETTINGS,
    )
    if not reason.strip():
        raise PlatformError(
            "VALIDATION_FAILED",
            "A purge requires a reason",
            422,
            "FR-DATA-39: the erasure is audited, and an unexplained purge is a deletion "
            "nobody can account for.",
        )

    versions = (
        await session.execute(
            select(DatasetVersionRow).where(
                DatasetVersionRow.workspace_id == workspace_id,
                DatasetVersionRow.dataset_id == dataset_id,
            )
        )
    ).scalars().all()

    record = SubjectPurgeRow(
        workspace_id=workspace_id,
        dataset_id=dataset_id,
        subject_token=subject_token,
        requested_by=actor.id,
        reason=reason,
        versions_affected=len(versions),
    )
    session.add(record)
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="dataset.subject_purged",
        entity_ref=f"dataset:{dataset_id}@1",
        after={"subject_token": subject_token, "versions_affected": len(versions)},
        justification=reason,
    )
    return record


async def record_split(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    parent_version_id: UUID,
    name: str,
    method: str,
    seed: int,
    parts: dict[str, UUID],
    params: dict[str, Any] | None = None,
) -> DatasetSplitRow:
    """Record a named split on the parent version (FR-DATA-36).

    On the parent so that "trained on the same split" is a single reference both models
    cite, rather than two derivations that were *believed* to match. Recorded on the parts
    instead, the claim becomes unverifiable the moment either part is rebuilt.
    """
    parent = await load_version(session, workspace_id=workspace_id, version_id= parent_version_id)
    if len(parts) < 2:
        raise PlatformError(
            "VALIDATION_FAILED",
            "A split needs at least two parts",
            422,
            "A one-part split is a filter; recording it as a split would let a model claim "
            "a holdout it never had.",
        )

    row = DatasetSplitRow(
        workspace_id=workspace_id,
        parent_version_id=parent_version_id,
        name=name,
        method=method,
        seed=seed,
        params=params or {},
        parts={part: str(version_id) for part, version_id in parts.items()},
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError:
        raise PlatformError(
            "VALIDATION_FAILED",
            "A split with this name already exists on the version",
            409,
            f"{name!r} is already recorded on this version. Reusing the name for different "
            "parts would make two models citing it incomparable.",
        ) from None

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="dataset_version.split_recorded",
        entity_ref=f"dataset_version:{parent.dataset_id}@{parent.version}",
        after={"name": name, "method": method, "seed": seed, "parts": list(parts)},
    )
    return row

def to_split(row: DatasetSplitRow) -> DatasetSplit:
    """The stored split as its artifact shape (FR-DATA-36)."""
    return DatasetSplit(
        id=row.id,
        parent_version_id=row.parent_version_id,
        name=row.name,
        method=row.method,
        seed=row.seed,
        params=row.params,
        parts={name: UUID(str(v)) for name, v in row.parts.items()},
        created_at=row.created_at,
    )


async def list_splits(
    session: AsyncSession, *, workspace_id: UUID, parent_version_id: UUID
) -> list[DatasetSplitRow]:
    """Every split recorded on one version, newest first."""
    return list(
        (
            await session.execute(
                select(DatasetSplitRow)
                .where(
                    DatasetSplitRow.workspace_id == workspace_id,
                    DatasetSplitRow.parent_version_id == parent_version_id,
                )
                .order_by(DatasetSplitRow.created_at.desc())
            )
        ).scalars()
    )
