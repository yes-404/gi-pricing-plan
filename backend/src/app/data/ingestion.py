"""Ingestion: file to Dataset Version (`01` §3.1, FR-DATA-2..8, FR-DATA-40).

The orchestration around `pricing_core.data.ingest`'s pure functions. This module owns the
I/O and the bookkeeping; the decisions — how a name normalises, what the schema looks like,
which rows are unusable — are made by functions that run without a platform.

Two properties carry the requirements:

* **A run is idempotent on `(idempotency_key, source_fingerprint)`** (FR-DATA-8). The
  fingerprint is part of the identity, not a detail recorded beside it: the same key with
  *changed* source data is a different ingestion, and returning the old version for it
  would quietly serve stale data to a caller who believes they refreshed it.
* **Ingestion never mutates an existing version** (FR-DATA-2). Every run either produces a
  new version or produces none. There is no path that edits `@11`.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

import polars as pl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.formats import read_tabular
from app.db.models import DatasetVersionRow, IngestionRunRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit, datasets, rbac
from app.platform.blobs import BlobStore
from model_schema import BlobRef, DatasetKind, JobSource, Permission, Principal
from pricing_core.data.ingest import (
    ColumnNameCollisionError,
    infer_schema,
    normalise_columns,
    partition_rejects,
)

__all__ = ["IngestionOutcome", "ingest_upload", "library_versions"]

_log = get_logger("app.data.ingestion")

PARQUET_MEDIA_TYPE = "application/vnd.apache.parquet"

#: Rows of the quarantine kept inline on the run record (FR-DATA-6 asks for "a sample").
#: The full quarantine is a table on the version; this is what a failure screen shows
#: without loading a blob.
REJECT_SAMPLE_ROWS = 5


def library_versions() -> dict[str, str]:
    """Which builds produced this version (FR-DATA-6, `01` §4.2).

    Recorded per version because a dtype inference or a parquet encoding can change between
    releases, and "why does the same file give different totals?" is otherwise unanswerable
    a year later.
    """
    import polars

    # Extended as the data stack grows — duckdb with profiling, pandera with validation.
    # Recorded per version rather than per deployment: an old version must say which build
    # produced it, not which build happens to be installed now.
    return {"polars": polars.__version__}


class IngestionOutcome:
    """What a run produced."""

    __slots__ = ("reused", "run", "schema", "version")

    def __init__(
        self,
        version: DatasetVersionRow,
        run: IngestionRunRow,
        schema: Any,
        *,
        reused: bool = False,
    ) -> None:
        self.version = version
        self.run = run
        self.schema = schema
        self.reused = reused


def _fingerprint(data: bytes) -> str:
    """`file_sha256` (FR-DATA-6). Content, not filename: the same bytes uploaded twice
    under different names are the same extraction."""
    return hashlib.sha256(data).hexdigest()


async def ingest_upload(
    session: AsyncSession,
    blob_store: BlobStore,
    *,
    workspace_id: UUID,
    actor: Principal,
    dataset_id: UUID,
    data: bytes,
    filename: str,
    table_name: str = "policy_exposure",
    required_non_null: list[str] | None = None,
    idempotency_key: str | None = None,
    source_id: UUID | None = None,
    sheet: str | None = None,
    recipe: Sequence[Mapping[str, Any]] | None = None,
) -> IngestionOutcome:
    """Ingest an uploaded file as a new Dataset Version (FR-DATA-2..8, FR-DATA-40).

    The Preparation Recipe is applied **during** ingestion (FR-DATA-9) and stored with the
    version (FR-DATA-14). Applying it afterwards would mean the parquet on the version is
    not what the version's totals, profile and validation report describe.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.DATASET_WRITE,
    )

    started = time.perf_counter()
    fingerprint = _fingerprint(data)

    if idempotency_key is not None:
        existing = await _find_run(
            session,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if existing is not None and existing.dataset_version_id is not None:
            # FR-DATA-8: same key, unchanged source — return the original rather than
            # creating another version of identical data.
            version = await session.get(DatasetVersionRow, existing.dataset_version_id)
            if version is not None:
                return IngestionOutcome(version, existing, None, reused=True)

    frame = read_tabular(data, filename, sheet=sheet)

    try:
        mapping = normalise_columns(list(frame.columns))
    except ColumnNameCollisionError as exc:
        raise PlatformError(
            "COLUMN_NAME_COLLISION",
            "Two columns normalise to the same name",
            422,
            str(exc),
        ) from exc

    frame = frame.rename(mapping.rename_map)
    rows_read = frame.height

    # Before the reject partition: a recipe that parses a date or fills a null changes
    # which rows are rejectable, and running it afterwards would quarantine rows the
    # recipe exists to rescue.
    if recipe:
        from pricing_core.data.prepare import RecipeError, apply_recipe

        try:
            frame = apply_recipe({table_name: frame}, list(recipe)).tables[table_name]
        except RecipeError as exc:
            raise PlatformError(
                "VALIDATION_FAILED",
                "The preparation recipe could not be applied",
                422,
                f"{exc} No version was created — a partially prepared version is one "
                "whose parquet does not match what its recipe says was done (FR-DATA-14).",
            ) from exc

    partition = partition_rejects(frame, required_non_null=required_non_null)
    schema = infer_schema(partition.clean)

    version = await datasets.new_version(
        session,
        workspace_id=workspace_id,
        actor=actor,
        dataset_id=dataset_id,
        kind=DatasetKind.INGESTED,
        source_id=source_id,
    )

    tables: list[dict[str, Any]] = [
        await _store_table(
            blob_store, session, partition.clean, name=table_name, schema=schema,
            source_names=mapping.source_names,
        )
    ]
    if partition.rejected.height:
        # FR-DATA-7: the quarantine is a table on the version, not a log line.
        tables.append(
            await _store_table(
                blob_store, session, partition.rejected, name="_rejected", schema=None,
                source_names={},
            )
        )

    version.tables = tables
    version.source_fingerprint = {"kind": "file_sha256", "value": fingerprint}
    # FR-DATA-14: stored with the version and replayable. The steps themselves, not an id
    # pointing at a mutable recipe row — a recipe edited later would rewrite the history of
    # every version that cites it.
    version.derived_from = (
        {**(version.derived_from or {}), "recipe": list(recipe)} if recipe else version.derived_from
    )
    version.library_versions = library_versions()

    run = IngestionRunRow(
        workspace_id=workspace_id,
        dataset_id=dataset_id,
        dataset_version_id=version.id,
        source_id=source_id,
        status="succeeded",
        idempotency_key=idempotency_key,
        source_fingerprint=fingerprint,
        rows_read=rows_read,
        rows_written=partition.clean.height,
        rows_rejected=partition.rejected.height,
        reject_sample=_reject_sample(partition.rejected),
        bytes_read=len(data),
        duration_ms=int((time.perf_counter() - started) * 1000),
        library_versions=library_versions(),
    )
    session.add(run)
    version.ingestion_run_id = run.id
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="dataset_version.ingested",
        entity_ref=f"dataset_version:{dataset_id}@{version.version}",
        after={
            "rows_read": rows_read,
            "rows_written": partition.clean.height,
            "rows_rejected": partition.rejected.height,
            "source_fingerprint": fingerprint,
        },
    )
    return IngestionOutcome(version, run, schema)


async def _find_run(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    dataset_id: UUID,
    idempotency_key: str,
    fingerprint: str,
) -> IngestionRunRow | None:
    return (
        await session.execute(
            select(IngestionRunRow).where(
                IngestionRunRow.workspace_id == workspace_id,
                IngestionRunRow.dataset_id == dataset_id,
                IngestionRunRow.idempotency_key == idempotency_key,
                IngestionRunRow.source_fingerprint == fingerprint,
            )
        )
    ).scalar_one_or_none()


async def _store_table(
    blob_store: BlobStore,
    session: AsyncSession,
    frame: pl.DataFrame,
    *,
    name: str,
    schema: Any,
    source_names: dict[str, str],
) -> dict[str, Any]:
    """Write one table as parquet and describe it for `01` §4.2's `tables` list."""
    import io

    buffer = io.BytesIO()
    frame.write_parquet(buffer, compression="zstd")
    ref = await blob_store.put(session, buffer.getvalue(), PARQUET_MEDIA_TYPE)

    return {
        "name": name,
        "record_grain": name,
        "primary_key": list(schema.candidate_keys) if schema else [],
        "row_count": frame.height,
        "blob": ref.model_dump(mode="json", by_alias=True),
        "arrow_schema": {c: str(t) for c, t in zip(frame.columns, frame.dtypes, strict=True)},
        "source_names": source_names,
    }


def _reject_sample(rejected: pl.DataFrame) -> list[dict[str, Any]]:
    """A few quarantined rows with their reason (FR-DATA-6).

    Values are stringified: a sample is for a human reading a failure screen, and preserving
    dtypes in a JSONB column buys nothing while risking a value JSON cannot represent.
    """
    if rejected.height == 0:
        return []
    sample = rejected.head(REJECT_SAMPLE_ROWS)
    return [
        {key: (None if value is None else str(value)) for key, value in row.items()}
        for row in sample.iter_rows(named=True)
    ]


async def correct_schema(
    session: AsyncSession,
    blob_store: BlobStore,
    *,
    workspace_id: UUID,
    actor: Principal,
    version_id: UUID,
    table: str,
    columns: dict[str, str],
) -> DatasetVersionRow:
    """Recast columns of a `draft` version's table (FR-DATA-4).

    Inference is a guess, and the guess this platform makes most often is reading a
    zero-padded policy id as an integer. Correcting it has to recast the **data**, not
    only the recorded dtype: a version whose `arrow_schema` says `String` over a parquet
    file holding `Int64` is a version that validates against one schema and fits against
    another.

    `draft` only, checked by the caller. Once a version is validated its schema is part of
    what was checked, and editing it would silently change what an approved report was
    about.
    """
    import io

    from pricing_core.data.prepare import RecipeError, apply_recipe

    version = await session.get(DatasetVersionRow, version_id, with_for_update=True)
    if version is None or version.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Dataset version not found", 404, f"No version {version_id}."
        )
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.DATASET_WRITE,
    )

    tables = [dict(entry) for entry in version.tables]
    target = next((entry for entry in tables if entry["name"] == table), None)
    if target is None:
        present = ", ".join(sorted(entry["name"] for entry in tables)) or "none"
        raise PlatformError(
            "NOT_FOUND",
            f"This version has no table named {table!r}",
            404,
            f"Tables present: {present}.",
        )

    missing = sorted(set(columns) - set(target["arrow_schema"]))
    if missing:
        raise PlatformError(
            "SCHEMA_INFERENCE_CONFLICT",
            "Correction names columns the table does not have",
            422,
            f"Unknown column(s): {', '.join(missing)}. Correction renames nothing — it "
            "recasts existing columns, so every name must already be present.",
        )

    payload = await blob_store.read(BlobRef.model_validate(target["blob"]))
    frame = pl.read_parquet(io.BytesIO(payload))
    try:
        recast = apply_recipe(
            {table: frame}, [{"step": "cast", "table": table, "params": {"columns": columns}}]
        ).tables[table]
    except RecipeError as exc:
        raise PlatformError(
            "SCHEMA_INFERENCE_CONFLICT",
            "The correction is not a supported cast",
            422,
            str(exc),
        ) from exc

    # A cast that silently nulls the column is worse than a refused one: the version stays
    # draft, looks corrected, and loses the data. `strict=False` is what makes the cast
    # survivable at all, so the check has to be here rather than in Polars.
    for column in columns:
        added_nulls = recast[column].null_count() - frame[column].null_count()
        if added_nulls:
            raise PlatformError(
                "SCHEMA_INFERENCE_CONFLICT",
                f"Casting {column!r} to {columns[column]!r} would discard values",
                422,
                f"{added_nulls} of {frame.height} values do not survive the cast and would "
                "become null. The column holds something other than what the correction "
                "claims — inspect the rejected rows before correcting the schema.",
            )

    buffer = io.BytesIO()
    recast.write_parquet(buffer, compression="zstd")
    ref = await blob_store.put(session, buffer.getvalue(), PARQUET_MEDIA_TYPE)

    before = dict(target["arrow_schema"])
    target["blob"] = ref.model_dump(mode="json", by_alias=True)
    target["arrow_schema"] = {
        name: str(dtype) for name, dtype in zip(recast.columns, recast.dtypes, strict=True)
    }
    # Reassigned rather than mutated in place: SQLAlchemy does not track mutation inside a
    # JSONB list, so an in-place edit commits nothing and reports success.
    version.tables = tables
    await session.flush()

    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="dataset_version.schema_corrected",
        entity_ref=f"dataset_version:{version_id}",
        before={"table": table, "arrow_schema": before},
        after={"table": table, "arrow_schema": target["arrow_schema"]},
    )
    return version
