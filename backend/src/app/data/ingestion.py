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
from model_schema import DatasetKind, JobSource, Permission, Principal
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
) -> IngestionOutcome:
    """Ingest an uploaded file as a new Dataset Version (FR-DATA-2..8, FR-DATA-40)."""
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

    frame = frame.rename(mapping.rename_map())
    rows_read = frame.height

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
