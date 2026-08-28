"""Rate table platform service (03 §3.3, slices W10-2/W10-3C): seeding, cell diffs,
bulk operations, and the parquet write path.

Thin over the pure operations in `pricing_core.rate_tables.operations`: load the
model artifact, run the operation, persist rows (or a parquet blob above the
workspace's cell-count threshold, FR-RATE-62). Named failures from pricing-core are
mapped onto the module's API error codes (03 §5.2): the four validation codes become
`RATE_TABLE_INCOMPLETE` / `RATE_TABLE_KEY_DUPLICATE`, the approval gate stays
`PIN_NOT_APPROVED`, and the bulk-operation/import refusals keep their own names.
"""

from __future__ import annotations

import io
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Literal, cast
from uuid import UUID

import polars as pl
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import Settings
from app.db.models import (
    RateTableCellRow,
    RateTableRow,
    RateTableVersionRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import settings as settings_svc
from app.platform.blobs import BlobStore
from app.platform.diff_cache import DiffCache, version_content_hash
from app.platform.modelling import load_model, to_model
from model_schema.rating import (
    FloorAndCapParameters,
    ImportPreview,
    RateTable,
    RateTableDiff,
    RateTableKey,
    RateTableStorageMode,
    RateTableVersion,
    RebaseToLevelParameters,
    SeededFrom,
    UpliftByFilterParameters,
    UpliftTableParameters,
)
from model_schema.refs import ArtifactRef, BlobRef
from pricing_core.rate_tables.operations import (
    decide_storage_mode,
    diff_vs_previous,
    diff_vs_seed,
    export_to_csv,
    export_to_xlsx,
    floor_and_cap,
    import_from_csv,
    import_from_xlsx,
    rebase_to_level,
    uplift_by_filter,
    uplift_table,
)
from pricing_core.rate_tables.operations import (
    import_confirmed as import_confirmed_op,
)
from pricing_core.rate_tables.operations import (
    seed_from_model as seed_from_model_op,
)

#: The plan's four named validation codes → 03 §5.2 module codes (RATE_TABLE_INCOMPLETE,
#: RATE_TABLE_KEY_DUPLICATE). NULL_VALUE and OUT_OF_BOUNDS are completeness failures.
_VALIDATION_CODES = {
    "INCOMPLETE_KEY_DOMAIN": "RATE_TABLE_INCOMPLETE",
    "NULL_VALUE": "RATE_TABLE_INCOMPLETE",
    "OUT_OF_BOUNDS": "RATE_TABLE_INCOMPLETE",
    "DUPLICATE_KEY": "RATE_TABLE_KEY_DUPLICATE",
}

DiffAgainst = Literal["previous", "seed"]


def _map_operation_error(exc: ValueError) -> PlatformError:
    """A pricing-core operation failure → the module's API error code (03 §5.2)."""
    code, _, detail = str(exc).partition(": ")
    if code in _VALIDATION_CODES:
        return PlatformError(
            _VALIDATION_CODES[code], code.replace("_", " ").title(), 422, detail
        )
    if code.isupper() and "_" in code and code != "VALIDATION_FAILED":
        return PlatformError(code, code.replace("_", " ").title(), 422, detail)
    return PlatformError("VALIDATION_FAILED", "Validation Failed", 422, str(exc))


async def seed_from_model(
    database: Database,
    workspace_id: UUID,
    created_by: UUID,
    settings: Settings,
    blob_store: BlobStore,
    *,
    slug: str,
    model_ref: ArtifactRef,
    change_note: str,
    rateable: bool = True,
) -> RateTableVersion:
    """Seed a new rate table version from an approved model (FR-RATE-16, spec §5.1).

    The seed is the origin of a lineage: it creates the table (version 1) or appends
    the next version of an existing table, pins `seeded_from` so "how far from the
    technical rate?" is answerable (FR-RATE-16), and its storage is decided against
    the workspace threshold like every new version (FR-RATE-62, DP2).
    """
    async with database.unit_of_work() as session:
        model_row = await load_model(
            session,
            workspace_id=workspace_id,
            slug=model_ref.slug,
            version=model_ref.version,
        )
        model = to_model(model_row)
        try:
            result = seed_from_model_op(
                model,
                table_slug=slug,
                change_note=change_note,
                seeded_at=datetime.now(UTC),
                rateable=rateable,
            )
        except ValueError as exc:
            raise _map_operation_error(exc) from exc

        table_row = await session.scalar(
            select(RateTableRow).where(
                RateTableRow.workspace_id == workspace_id,
                RateTableRow.slug == slug,
            )
        )
        if table_row is None:
            table_row = RateTableRow(
                workspace_id=workspace_id,
                slug=slug,
                current_version=0,
                created_by=created_by,
            )
            session.add(table_row)
            await session.flush()
            version_number = 1
        else:
            version_number = table_row.current_version + 1

        derived = RateTableVersion(
            slug=result.table.slug,
            version=version_number,
            rateable=result.table.rateable,
            storage=RateTableStorageMode.ROWS,
            keys=result.table.keys,
            value=result.table.value,
            default_row=result.table.default_row,
            rows=_wire_rows(result.cells),
            change_note=change_note,
            seeded_from=result.seeded_from,
        )
        threshold = await _resolve_threshold(session, settings, workspace_id)
        return await _persist_new_version(
            session,
            table_row=table_row,
            derived=derived,
            version_number=version_number,
            created_by=created_by,
            threshold=threshold,
            blob_store=blob_store,
        )


def _cells_for_rows(
    cells: Sequence[dict[str, str]], keys: list[Any], value_name: str
) -> list[tuple[list[str], str]]:
    """Rows → (key tuple as JSON array, value as decimal string), in key order."""
    key_names = [key.name for key in keys]
    return [([row[name] for name in key_names], row[value_name]) for row in cells]


def _wire_rows(cells: Sequence[dict[str, str]]) -> list[dict[str, str | int]]:
    """Cells → the wire form's row type (§4.2): every value is a decimal string."""
    return cast(list[dict[str, str | int]], list(cells))


async def _load_table(
    session: Any, workspace_id: UUID, slug: str
) -> RateTableRow:
    table_row = cast(
        RateTableRow | None,
        await session.scalar(
            select(RateTableRow).where(
                RateTableRow.workspace_id == workspace_id,
                RateTableRow.slug == slug,
            )
        ),
    )
    if table_row is None:
        raise PlatformError(
            "RATE_TABLE_MISS", "Rate table not found", 404, f"{slug} not found."
        )
    return table_row


async def diff_needs_job(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    against: str | int,
) -> bool:
    """Whether the diff must answer 202 with a Job (03 §5.1, FR-RATE-62).

    Either version `storage: parquet` routes the request to a `rate_table.diff` Job;
    a rows-only pair stays on the synchronous 200 path. Raises the same refusals as
    `diff` (a missing table or version, a baseless baseline) so the two forms cannot
    disagree about what exists. Versions are immutable, so a later resolution inside
    the worker arrives at the same baseline and the same cells.
    """
    async with database.unit_of_work() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        baseline_number = await _resolve_baseline(
            session, table_row.id, version, against
        )
        baseline_row = await _load_version(
            session, table_row.id, baseline_number, slug
        )
        return (
            version_row.storage == "parquet" or baseline_row.storage == "parquet"
        )


async def diff(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    against: str | int,
    *,
    blob_store: BlobStore,
    cache: DiffCache | None = None,
    portfolio_dataset_version_id: UUID | None = None,
) -> RateTableDiff:
    """Cell-level diff of one version against a baseline (FR-RATE-17, spec §5.1).

    `against` names the baseline: `previous` (the prior version), `seed` (the version
    that seeded the table — the technical-rate origin, FR-RATE-16), or an explicit
    version number. Diffed on read (DP3: compute on read, nothing materialised at
    version creation). Exposure weights are supplied by the caller at fetch time
    (DP1); this slice passes none — the portfolio-dataset join is not yet built.

    One compute path for both storages (FR-RATE-62): a `parquet` version's cells are
    materialised from its blob the way every bounded table transform does; storage
    decides whether the API answers 200 or 202 with a Job (`diff_needs_job`), never
    what the artifact contains.

    With `cache` (DP3 (b)) the read path is compute-on-read: a miss computes and
    stores, a hit serves the stored artifact. The key covers both versions' content
    hashes and the portfolio identity, never a wall-clock date — an immutable pair
    can only ever name one entry (`diff_cache`).
    """
    async with database.unit_of_work() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        baseline_number = await _resolve_baseline(
            session, table_row.id, version, against
        )
        baseline_row = await _load_version(
            session, table_row.id, baseline_number, slug
        )

        table = RateTable.model_validate(version_row.definition)
        current_cells = await _load_cells_of(
            session, version_row, table, blob_store
        )
        baseline_cells = await _load_cells_of(
            session, baseline_row, table, blob_store
        )
        key: str | None = None
        if cache is not None:
            key = cache.key(
                version_content_hash(current_cells),
                version_content_hash(baseline_cells),
                portfolio_dataset_version_id,
            )
            cached = await cache.get(key)
            if cached is not None:
                return cached
        if against == "seed":
            diff = diff_vs_seed(baseline_cells, current_cells, table.keys, table.value)
        else:
            diff = diff_vs_previous(baseline_cells, current_cells, table.keys, table.value)
        if key is not None:
            assert cache is not None
            await cache.set(key, diff)
        return diff


async def export_csv(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    blob_store: BlobStore,
) -> bytes:
    """The version's cells as CSV, decimal strings only (FR-RATE-20).

    Reads parquet-stored versions inline from their blob — a bounded table transform
    (03 §3.3, W10-3D), the same materialisation `_to_version` does for operations.
    """
    async with database.unit_of_work() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        table = await _to_version(session, version_row, blob_store)
        return export_to_csv(table)


async def export_xlsx(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    blob_store: BlobStore,
) -> bytes:
    """The version's cells as XLSX, every cell written as text (FR-RATE-20)."""
    async with database.unit_of_work() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        table = await _to_version(session, version_row, blob_store)
        return export_to_xlsx(table)


async def import_preview(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    blob_store: BlobStore,
    *,
    filename: str,
    content: bytes,
) -> ImportPreview:
    """The would-be version as a diff against the addressed one (FR-RATE-20, 03 §5.1).

    Strict round-trip preview only: nothing is created. The file's extension routes
    CSV vs XLSX (the core dispatches the same way); the verdict's canonical filename
    is the upload's name as received (DP5).
    """
    async with database.unit_of_work() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        table = await _to_version(session, version_row, blob_store)
        try:
            if filename.endswith(".csv"):
                return import_from_csv(table, content, filename=filename)
            return import_from_xlsx(table, content, filename=filename)
        except ValueError as exc:
            raise _map_operation_error(exc) from exc


async def import_confirmed(
    database: Database,
    workspace_id: UUID,
    created_by: UUID,
    settings: Settings,
    blob_store: BlobStore,
    *,
    slug: str,
    version: int,
    filename: str,
    content: bytes,
) -> RateTableVersion:
    """Create the version the preview showed (FR-RATE-20, 03 §5.1, DP6).

    The upload is parsed again through the same strict pipeline the preview ran —
    the created version cannot diverge from the preview (same bytes, same immutable
    baseline). The verdict is recorded on the version as `created_by_import` (DP5),
    the seed anchor is inherited from the baseline (DP4, FR-RATE-19), and the
    storage decision follows the workspace threshold like any other version (DP2).
    """
    async with database.unit_of_work() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        table = await _to_version(session, version_row, blob_store)
        try:
            result = import_confirmed_op(table, content, filename=filename)
        except ValueError as exc:
            raise _map_operation_error(exc) from exc
        derived = RateTableVersion(
            slug=slug,
            version=version + 1,
            rateable=True,
            storage=RateTableStorageMode.ROWS,
            keys=table.keys,
            value=table.value,
            default_row=table.default_row,
            rows=_wire_rows(result.cells),
            change_note=f"import: {filename}",
            seeded_from=table.seeded_from,
            created_by_import=result.created_by_import,
        )
        _guard_seed_lineage(derived, version_row)
        threshold = await _resolve_threshold(session, settings, workspace_id)
        return await _persist_new_version(
            session,
            table_row=table_row,
            derived=derived,
            version_number=version + 1,
            created_by=created_by,
            threshold=threshold,
            blob_store=blob_store,
        )


async def _resolve_baseline(
    session: Any, rate_table_id: UUID, version: int, against: str | int
) -> int:
    if isinstance(against, int):
        return against
    if against == "previous":
        if version <= 1:
            raise PlatformError(
                "RATE_TABLE_MISS",
                "No previous version",
                404,
                f"version {version} has no previous version to diff against.",
            )
        return version - 1
    if against == "seed":
        seed_number = cast(
            int | None,
            await session.scalar(
                select(RateTableVersionRow.version_number)
                .where(
                    RateTableVersionRow.rate_table_id == rate_table_id,
                    RateTableVersionRow.seeded_from.is_not(None),
                )
                .order_by(RateTableVersionRow.version_number)
                .limit(1)
            ),
        )
        if seed_number is None:
            raise PlatformError(
                "RATE_TABLE_MISS",
                "No seed origin",
                404,
                "rate table has no seeded version to diff against.",
            )
        return seed_number
    raise PlatformError(
        "VALIDATION_FAILED",
        "Invalid diff baseline",
        422,
        f"against={against!r}: expected 'previous', 'seed' or a version number.",
    )


async def _load_version(
    session: Any, rate_table_id: UUID, version_number: int, slug: str
) -> RateTableVersionRow:
    row = cast(
        RateTableVersionRow | None,
        await session.scalar(
            select(RateTableVersionRow).where(
                RateTableVersionRow.rate_table_id == rate_table_id,
                RateTableVersionRow.version_number == version_number,
            )
        ),
    )
    if row is None:
        raise PlatformError(
            "RATE_TABLE_MISS",
            "Rate table version not found",
            404,
            f"{slug}@{version_number} not found.",
        )
    return row


async def _load_cells(
    session: Any, version_id: UUID, table: RateTable
) -> list[dict[str, str]]:
    rows = (
        await session.execute(
            select(RateTableCellRow.key, RateTableCellRow.value).where(
                RateTableCellRow.version_id == version_id
            )
        )
    ).all()
    key_names = [key.name for key in table.keys]
    return [
        {name: key_value for name, key_value in zip(key_names, row[0], strict=True)}
        | {table.value.name: row[1]}
        for row in rows
    ]


async def _resolve_threshold(
    session: Any, settings: Settings, workspace_id: UUID
) -> int:
    """The workspace's cell-count threshold, read when a version is written (DP2)."""
    resolution = await settings_svc.resolve(
        session, settings, workspace_id, "rate_tables.cell_threshold"
    )
    return cast(int, resolution.effective_value)


def _cells_to_parquet(
    cells: Sequence[dict[str, str]], keys: Sequence[RateTableKey], value_name: str
) -> bytes:
    """Cells → parquet bytes (FR-RATE-62). Every column is UTF-8: keys and values are
    level names and decimal strings, and a numeric inference would silently re-type
    them — the strict round-trip FR-RATE-20's verdict is about."""
    columns: dict[str, list[str]] = {
        key.name: [row[key.name] for row in cells] for key in keys
    }
    columns[value_name] = [row[value_name] for row in cells]
    frame = pl.DataFrame(columns, schema={name: pl.Utf8 for name in columns})
    buffer = io.BytesIO()
    frame.write_parquet(buffer)
    return buffer.getvalue()


def _cells_from_parquet(content: bytes) -> list[dict[str, str]]:
    frame = pl.read_parquet(io.BytesIO(content))
    return cast(list[dict[str, str]], frame.to_dicts())


async def _load_cells_of(
    session: Any,
    version_row: RateTableVersionRow,
    table: RateTable,
    blob_store: BlobStore,
) -> list[dict[str, str]]:
    """The version's cells, wherever storage keeps them (FR-RATE-62)."""
    if version_row.storage == "parquet":
        ref = BlobRef.model_validate(version_row.cells)
        return _cells_from_parquet(await blob_store.read(ref))
    return await _load_cells(session, version_row.id, table)


async def _to_version(
    session: Any, version_row: RateTableVersionRow, blob_store: BlobStore
) -> RateTableVersion:
    """The version as a transformation input, cells materialised inline.

    Parquet-stored versions are read from their blob here — a bounded table
    transform, unlike the Job-worthy diff (W10-3D). The returned model always
    presents `rows`: pricing-core's operations refuse blobs by design
    (PARQUET_CELLS_UNAVAILABLE), and the persistence path re-decides storage
    against the threshold (DP2), so the in-memory claim is never stored.
    """
    table = RateTable.model_validate(version_row.definition)
    cells = await _load_cells_of(session, version_row, table, blob_store)
    return RateTableVersion(
        slug=table.slug,
        version=table.version,
        rateable=table.rateable,
        storage=RateTableStorageMode.ROWS,
        keys=table.keys,
        value=table.value,
        default_row=table.default_row,
        rows=_wire_rows(cells),
        change_note=version_row.change_note,
        seeded_from=(
            SeededFrom.model_validate(version_row.seeded_from)
            if version_row.seeded_from is not None
            else None
        ),
    )


def _guard_seed_lineage(
    derived: RateTableVersion, baseline: RateTableVersionRow
) -> None:
    """Save-time equality proof (03 §4.2, FR-RATE-19, DP4): a derived version's seed
    anchor must equal its resolved baseline's — never invented, dropped or swapped.

    pricing-core builds the derived version from the same baseline, so through the
    API this fires on internal construction corruption rather than request input;
    the broken-input test states the invariant it protects.
    """
    derived_anchor = (
        derived.seeded_from.model_dump(mode="json")
        if derived.seeded_from is not None
        else None
    )
    if derived_anchor != baseline.seeded_from:
        raise PlatformError(
            "RATE_TABLE_SEED_MISMATCH",
            "Seed lineage mismatch",
            422,
            f"derived version {derived.slug}@{derived.version} carries seeded_from "
            f"{derived_anchor!r} but its baseline @{baseline.version_number} carries "
            f"{baseline.seeded_from!r}; a derived version may not invent or drop the "
            "seed anchor (03 §4.2).",
        )


async def _persist_new_version(
    session: Any,
    *,
    table_row: RateTableRow,
    derived: RateTableVersion,
    version_number: int,
    created_by: UUID,
    threshold: int,
    blob_store: BlobStore,
) -> RateTableVersion:
    """Write the derived version, deciding its storage against the resolved threshold.

    DP2: the threshold is read at version-creation time only; storage is decided here
    from the cell count and frozen with the version (FR-RATE-62). At or below the
    threshold the cells keep the `rate_table_cells` rows; above it they are written
    to a content-addressed parquet blob addressed by `cells`. Returns the version in
    its §4.2 wire form.
    """
    cells = cast(list[dict[str, str]], derived.rows)
    storage_mode = decide_storage_mode(len(cells), threshold)
    definition = RateTable(
        slug=derived.slug,
        version=version_number,
        rateable=derived.rateable,
        storage=RateTableStorageMode(storage_mode),
        keys=derived.keys,
        value=derived.value,
        default_row=derived.default_row,
    ).model_dump()
    version_row = RateTableVersionRow(
        workspace_id=table_row.workspace_id,
        rate_table_id=table_row.id,
        version_number=version_number,
        storage=storage_mode,
        definition=definition,
        change_note=derived.change_note,
        seeded_from=(
            derived.seeded_from.model_dump(mode="json")
            if derived.seeded_from is not None
            else None
        ),
        created_by=created_by,
        created_by_operation=(
            derived.created_by_operation.model_dump(mode="json")
            if derived.created_by_operation is not None
            else None
        ),
        created_by_import=(
            derived.created_by_import.model_dump(mode="json")
            if derived.created_by_import is not None
            else None
        ),
    )
    session.add(version_row)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Rate table version already exists",
            409,
            f"{derived.slug}@{version_number} already exists in this workspace.",
        ) from exc
    table_row.current_version = version_number
    blob_ref: BlobRef | None = None
    if storage_mode == "rows":
        session.add_all(
            RateTableCellRow(version_id=version_row.id, key=key, value=value)
            for key, value in _cells_for_rows(
                cells, derived.keys, derived.value.name
            )
        )
    else:
        blob_ref = await blob_store.put(
            session,
            _cells_to_parquet(cells, derived.keys, derived.value.name),
            "application/parquet",
        )
        version_row.cells = blob_ref.model_dump(mode="json")
    await session.flush()
    return RateTableVersion(
        slug=derived.slug,
        version=version_number,
        rateable=derived.rateable,
        storage=RateTableStorageMode(storage_mode),
        keys=derived.keys,
        value=derived.value,
        default_row=derived.default_row,
        rows=_wire_rows(cells) if storage_mode == "rows" else None,
        cells=blob_ref,
        change_note=derived.change_note,
        seeded_from=derived.seeded_from,
        created_by_operation=derived.created_by_operation,
        created_by_import=derived.created_by_import,
    )


def _dispatch_operation(
    kind: str, parameters: dict[str, Any], table: RateTableVersion
) -> RateTableVersion:
    """Parse the 04 §4.4 parameters (decimal strings, never floats) and run the op."""
    match kind:
        case "uplift_table":
            uplift_params = UpliftTableParameters.model_validate(parameters)
            return uplift_table(table, percentage=uplift_params.percentage)
        case "uplift_by_filter":
            filter_params = UpliftByFilterParameters.model_validate(parameters)
            return uplift_by_filter(
                table, percentage=filter_params.percentage, filter=filter_params.filter
            )
        case "floor_and_cap":
            floor_params = FloorAndCapParameters.model_validate(parameters)
            return floor_and_cap(table, floor=floor_params.floor, cap=floor_params.cap)
        case "rebase_to_level":
            rebase_params = RebaseToLevelParameters.model_validate(parameters)
            return rebase_to_level(table, base_level=rebase_params.base_level)
        case _:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Unknown bulk operation kind",
                422,
                f"kind={kind!r}: expected one of uplift_table, uplift_by_filter, "
                "floor_and_cap, rebase_to_level (04 §4.4).",
            )


async def bulk_operation(
    database: Database,
    workspace_id: UUID,
    created_by: UUID,
    settings: Settings,
    blob_store: BlobStore,
    *,
    slug: str,
    version: int,
    kind: str,
    parameters: dict[str, Any],
) -> RateTableVersion:
    """Apply a bulk operation and persist the new version (FR-RATE-18, 03 §5.1).

    The operation addresses a specific version (`{slug}@{version}`): the baseline is
    loaded from the addressed version, its seed lineage is proven equal at save time
    (FR-RATE-19, 03 §4.2, DP4), and the new version's storage is decided against the
    workspace threshold (FR-RATE-62, DP2).
    """
    async with database.unit_of_work() as session:
        table_row = await session.scalar(
            select(RateTableRow).where(
                RateTableRow.workspace_id == workspace_id,
                RateTableRow.slug == slug,
            )
        )
        if table_row is None:
            raise PlatformError(
                "RATE_TABLE_MISS", "Rate table not found", 404, f"{slug} not found."
            )
        baseline_row = await _load_version(session, table_row.id, version, slug)
        baseline = await _to_version(session, baseline_row, blob_store)
        try:
            derived = _dispatch_operation(kind, parameters, baseline)
        except ValidationError as exc:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Invalid bulk operation parameters",
                422,
                str(exc),
            ) from exc
        except ValueError as exc:
            raise _map_operation_error(exc) from exc
        _guard_seed_lineage(derived, baseline_row)
        threshold = await _resolve_threshold(session, settings, workspace_id)
        return await _persist_new_version(
            session,
            table_row=table_row,
            derived=derived,
            version_number=baseline_row.version_number + 1,
            created_by=created_by,
            threshold=threshold,
            blob_store=blob_store,
        )
