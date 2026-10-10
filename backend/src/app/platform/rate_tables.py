"""Rate table platform service (03 §3.3, slices W10-2/W10-3C): seeding, cell diffs,
bulk operations, and the parquet write path.

Thin over the pure operations in `pricing_core.rate_tables.operations`: load the
model artifact, run the operation, persist rows (or a parquet blob above the
workspace's cell-count threshold, FR-232). Named failures from pricing-core are
mapped onto the module's API error codes (03 §5.2): the four validation codes become
`RATE_TABLE_INCOMPLETE` / `RATE_TABLE_KEY_DUPLICATE`, the approval gate stays
`PIN_NOT_APPROVED`, and the bulk-operation/import refusals keep their own names.
"""

from __future__ import annotations

import io
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, cast
from uuid import UUID

import polars as pl
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.pagination import COUNT_CAP, MAX_LIMIT, Page, decode_int_cursor, encode_cursor
from app.config import Settings
from app.db.models import (
    BlobRow,
    DatasetVersionRow,
    JobRow,
    RateTableCellRow,
    RateTableRow,
    RateTableVersionRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets, transformations
from app.platform import jobs as job_service
from app.platform import settings as settings_svc
from app.platform.blobs import BlobStore, to_ref
from app.platform.diff_cache import DiffCache, cells_key, definition_hash, version_content_hash
from app.platform.modelling import (
    load_factor_by_ref,
    load_factors,
    load_model,
    to_model,
)
from model_schema import Banding, DatasetStatus, Factor, Grouping, JobKind, JobStatus
from model_schema.jobs import Job
from model_schema.rating import (
    FloorAndCapParameters,
    ImportPreview,
    RateTable,
    RateTableCell,
    RateTableDiff,
    RateTableDiffCell,
    RateTableKey,
    RateTableStorageMode,
    RateTableVersion,
    RebaseToLevelParameters,
    SeededFrom,
    UpliftByFilterParameters,
    UpliftTableParameters,
)
from model_schema.refs import ArtifactRef, BlobRef
from pricing_core.modelling import FactorResolutionError
from pricing_core.rate_tables.operations import (
    check_model_approved,
    decide_storage_mode,
    diff_cells,
    diff_summary,
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
from pricing_core.rate_tables.weights import (
    PortfolioWeights,
    WeightJoinError,
    exposure_weights,
)
from pricing_core.rating.analysis import PortfolioFrameError, read_portfolio

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
    factor: str,
    change_note: str,
    rateable: bool = True,
) -> RateTableVersion:
    """Seed one Factor of an approved model into a rate table version (FR-230, `RL-1361`).

    One seed holds one Factor: the table has one key, bound by `factor_ref` to the Factor
    version the model pins. The seed is the origin of a lineage: it creates the table
    (version 1) or appends the next version of an existing one, pins `seeded_from` so "how
    far from the technical rate?" is answerable (FR-230), and its storage is decided against
    the workspace threshold like every new version (FR-232, DP2). A re-seed records its own
    source model and starts a new seed origin (`RL-1375` DP-1).

    **Refusal order.** Approval comes before the Factors are loaded (`RL-1376`), so a
    non-approved model gives `PIN_NOT_APPROVED` whatever its Factor ids resolve to; an id
    that resolves nowhere is then a 404 (`load_factors`), never an empty list.
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
            check_model_approved(model)
        except ValueError as exc:
            raise _map_operation_error(exc) from exc
        factors = await load_factors(
            session, workspace_id=workspace_id, factor_ids=list(model.spec.factors)
        )
        try:
            result = seed_from_model_op(
                model,
                factor=factor,
                factors=factors,
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
            await _check_reseed_lineage(session, table_row, slug=slug, factor=factor)
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


async def _check_reseed_lineage(
    session: Any, table_row: RateTableRow, *, slug: str, factor: str
) -> None:
    """`RL-1375` DP-2: a seed into an existing table needs one key naming this Factor.

    Accepted only when the current version has exactly one key and that key either carries
    a `factor_ref` naming `factor`'s slug (at any version) or carries neither `factor_ref`
    nor `banding_ref` and is named `factor` (every key seeded before `factor_ref` existed).
    Anything else is a 422 `VALIDATION_FAILED` naming the table and its keys.
    """
    current = await _load_version(session, table_row.id, table_row.current_version, slug)
    keys: list[dict[str, Any]] = list(current.definition.get("keys", []))
    names = [str(key.get("name")) for key in keys]
    if len(keys) == 1 and _key_takes_the_seed(keys[0], factor):
        return
    raise PlatformError(
        "VALIDATION_FAILED",
        "Request validation failed",
        422,
        f"rate table {slug!r} cannot take a seed of Factor {factor!r}: its current version "
        f"@{table_row.current_version} has key(s) {names}; a seed into an existing table "
        "needs exactly one key that is bound to that Factor or is an unbound key named "
        "after it. Seed a new table slug instead.",
    )


def _key_takes_the_seed(key: dict[str, Any], factor: str) -> bool:
    factor_ref = key.get("factor_ref")
    if factor_ref is not None:
        try:
            return ArtifactRef.model_validate(factor_ref).slug == factor
        except ValueError:
            return False
    return key.get("banding_ref") is None and key.get("name") == factor


def _cells_for_rows(
    cells: Sequence[dict[str, str]], keys: list[Any], value_name: str
) -> list[tuple[list[str], str]]:
    """Rows → (key tuple as JSON array, value as decimal string), in key order."""
    key_names = [key.name for key in keys]
    return [([row[name] for name in key_names], row[value_name]) for row in cells]


def _wire_rows(cells: Sequence[dict[str, str]]) -> list[RateTableCell]:
    """Cells → the wire form's row type (§4.2): every value is a decimal string."""
    return [RateTableCell(row) for row in cells]


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


async def check_portfolio(
    session: Any, *, workspace_id: UUID, version_id: UUID
) -> DatasetVersionRow:
    """May this caller's workspace weight a diff by that portfolio? (`RL-1361` item 7.)

    The version's scope first: another workspace's version, and a version that does not
    exist, answer the same `404`, so the existence of a foreign id is not disclosed. Then its
    status: only a `validated` version is a portfolio (`01` §1.3), `409`
    `DATASET_NOT_VALIDATED` for a `draft` or `archived` one. Neither check takes a row lock.
    """
    row = await datasets.read_version(session, workspace_id=workspace_id, version_id=version_id)
    if DatasetStatus(row.status) is not DatasetStatus.VALIDATED:
        raise PlatformError(
            "DATASET_NOT_VALIDATED",
            "Dataset version is not validated",
            409,
            f"The portfolio has status {row.status!r}; a rate-table diff weighted by a "
            "portfolio requires 'validated' (03 FR-231). There is no override.",
        )
    return row


async def _portfolio_frame(
    session: Any, blob_store: BlobStore, version_row: DatasetVersionRow
) -> pl.LazyFrame:
    """The portfolio's table, checked against §4.8's frame (DP-D: `tables[0]`, as fitting does)."""
    if not version_row.tables:
        raise PlatformError(
            "VALIDATION_FAILED", "The portfolio has no table", 422,
            f"Dataset version {version_row.id} holds no table.",
        )
    entry = version_row.tables[0]
    blob = await session.get(BlobRow, entry["blob"]["sha256"])
    if blob is None:
        raise PlatformError(
            "NOT_FOUND", "A table's blob is missing", 404,
            f"Version {version_row.id} names a blob that is not in the store.",
        )
    frame = pl.read_parquet(io.BytesIO(await blob_store.read(to_ref(blob)))).lazy()
    return read_portfolio(frame)


async def _key_artifacts(
    session: Any, workspace_id: UUID, keys: Sequence[RateTableKey]
) -> tuple[dict[str, list[Factor]], dict[UUID, Banding], dict[UUID, Grouping]]:
    """Everything the keys pin, loaded by ref: each Factor with its operands, each Banding,
    and the Bandings and Groupings those Factors pin by id. A ref that resolves to nothing is
    a `404` naming the key and the ref."""
    factors: dict[str, list[Factor]] = {}
    bandings: dict[UUID, Banding] = {}
    for key in keys:
        try:
            if key.factor_ref is not None:
                factors[str(key.factor_ref)] = await load_factor_by_ref(
                    session, workspace_id=workspace_id, ref=key.factor_ref
                )
            elif key.banding_ref is not None:
                banding = await transformations.load_banding_by_ref(
                    session, workspace_id=workspace_id, ref=key.banding_ref
                )
                bandings[banding.id] = banding
        except PlatformError as exc:
            if exc.code != "NOT_FOUND":
                raise
            raise PlatformError(
                "NOT_FOUND", exc.title, 404, f"Key {key.name!r}: {exc.detail}"
            ) from exc
    pinned = [factor for chain in factors.values() for factor in chain]
    banding_ids = list(
        dict.fromkeys(
            f.banding_id for f in pinned if f.banding_id and f.banding_id not in bandings
        )
    )
    grouping_ids = list(dict.fromkeys(f.grouping_id for f in pinned if f.grouping_id))
    bandings.update(
        await transformations.load_bandings(session, workspace_id=workspace_id, ids=banding_ids)
    )
    groupings = await transformations.load_groupings(
        session, workspace_id=workspace_id, ids=grouping_ids
    )
    return factors, bandings, groupings


async def _portfolio_weights(
    session: Any,
    blob_store: BlobStore,
    *,
    workspace_id: UUID,
    version_id: UUID,
    table: RateTable,
    current_cells: Sequence[dict[str, str]],
) -> PortfolioWeights:
    """Σ exposure per cell of the current version, or the `422` that refuses the portfolio.

    One path for the 200 diff, the cells route and both Jobs, so the aggregate mean and the
    per-cell weights come from one map (`RL-1418`). The pure join raises `WeightJoinError`
    (and `FactorResolutionError`, re-wrapped), the frame check `PortfolioFrameError`: each is
    `VALIDATION_FAILED` on the wire (`03` §5.1, the diff row).
    """
    version_row = await check_portfolio(session, workspace_id=workspace_id, version_id=version_id)
    factors, bandings, groupings = await _key_artifacts(session, workspace_id, table.keys)
    try:
        frame = await _portfolio_frame(session, blob_store, version_row)
        return exposure_weights(
            frame, table.keys, current_cells,
            factors=factors, bandings=bandings, groupings=groupings,
        )
    except (PortfolioFrameError, WeightJoinError, FactorResolutionError) as exc:
        raise PlatformError(
            "VALIDATION_FAILED", "The portfolio cannot weight this rate table", 422, str(exc)
        ) from exc


async def diff_needs_job(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    against: str | int,
    *,
    portfolio_dataset_version_id: UUID | None = None,
) -> bool:
    """Whether the diff must answer 202 with a Job (03 §5.1, FR-232).

    Either version `storage: parquet` routes the request to a `rate_table.diff` Job;
    a rows-only pair stays on the synchronous 200 path. Raises the same refusals as
    `diff` (a missing table or version, a baseless baseline) so the two forms cannot
    disagree about what exists. Versions are immutable, so a later resolution inside
    the worker arrives at the same baseline and the same cells.

    A named portfolio is checked here too (`check_portfolio`), so a refused portfolio is
    answered before any Job exists (`RL-1361` item 8).
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
        if portfolio_dataset_version_id is not None:
            await check_portfolio(
                session, workspace_id=workspace_id, version_id=portfolio_dataset_version_id
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
    """Cell-level diff of one version against a baseline (FR-231, spec §5.1).

    `against` names the baseline: `previous` (the prior version), `seed` (the version
    that seeded the table — the technical-rate origin, FR-230), or an explicit
    version number. Diffed on read (DP3: compute on read, nothing materialised at
    version creation). With `portfolio_dataset_version_id` the cells are weighted by that
    `validated` portfolio's exposure (`exposure_weights`) and the two coverage figures are
    set; without it the diff says so by leaving them `None` (FR-231, `RL-1361`).

    The portfolio is checked first (scope, then status, `check_portfolio`), before any cell
    is read and before the cache is consulted, so a cached entry can never answer for a
    portfolio the caller may not name.

    One compute path for both storages (FR-232): a `parquet` version's cells are
    materialised from its blob the way every bounded table transform does; storage
    decides whether the API answers 200 or 202 with a Job (`diff_needs_job`), never
    what the artifact contains.

    With `cache` (DP3 (b)) the read path is compute-on-read: a miss computes and
    stores, a hit serves the stored artifact. The key covers both versions' content
    hashes, the current definition and the portfolio identity within its workspace, never
    a wall-clock date — an immutable pair can only ever name one entry (`diff_cache`).
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
        if portfolio_dataset_version_id is not None:
            await check_portfolio(
                session, workspace_id=workspace_id, version_id=portfolio_dataset_version_id
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
                definition_hash(table),
                portfolio_dataset_version_id,
                workspace_id,
            )
            cached = await cache.get(key)
            if cached is not None:
                return cached
        weighted: PortfolioWeights | None = None
        if portfolio_dataset_version_id is not None:
            weighted = await _portfolio_weights(
                session, blob_store, workspace_id=workspace_id,
                version_id=portfolio_dataset_version_id, table=table,
                current_cells=current_cells,
            )
        weights = weighted.weights if weighted is not None else None
        if against == "seed":
            diff = diff_vs_seed(
                baseline_cells, current_cells, table.keys, table.value, weights=weights
            )
        else:
            diff = diff_vs_previous(
                baseline_cells, current_cells, table.keys, table.value, weights=weights
            )
        if weighted is not None:
            diff = diff.model_copy(
                update={
                    "portfolio_exposure": weighted.portfolio_exposure,
                    "matched_exposure": weighted.matched_exposure,
                }
            )
        if key is not None:
            assert cache is not None
            await cache.set(key, diff)
        return diff


#: Cells per chunk blob of a stored cells artifact. At least the route's `MAX_LIMIT`, so a page of
#: any legal limit touches at most two chunks (the cells-page latency NFR, R1): a page costs
#: O(page), never O(table).
CELLS_CHUNK = 1000
assert CELLS_CHUNK >= MAX_LIMIT


@dataclass(frozen=True, slots=True)
class DiffCellsPage:
    """One page of a diff's changed cells, and where the next one starts (`None` on the last)."""

    items: list[RateTableDiffCell]
    total_estimate: int
    next_cursor: str | None


@dataclass(frozen=True, slots=True)
class DiffCellsJobNeeded:
    """No stored artifact for this query. `in_flight` is the queued or running
    `rate_table.diff_cells` Job for the same key, if any: the route answers 202 with THAT Job
    rather than starting a second. Otherwise it submits one carrying `key`, which names the
    artifact the Job writes (a failed Job is not cached: the next request starts a new one)."""

    key: str
    in_flight: Job | None = None


async def _all_cells(
    session: Any,
    blob_store: BlobStore,
    *,
    workspace_id: UUID,
    version_row: RateTableVersionRow,
    baseline_row: RateTableVersionRow,
    table: RateTable,
    portfolio_dataset_version_id: UUID | None,
) -> tuple[list[RateTableDiffCell], PortfolioWeights | None]:
    """Every changed cell, in `03` §4.2's order, weighted by the portfolio when one is named,
    and the portfolio's coverage.

    The weights come from `_portfolio_weights`, the map the summary uses, so the cells and the
    aggregate mean cannot disagree (`RL-1418`).
    """
    current_cells = await _load_cells_of(session, version_row, table, blob_store)
    baseline_cells = await _load_cells_of(session, baseline_row, table, blob_store)
    weighted: PortfolioWeights | None = None
    if portfolio_dataset_version_id is not None:
        weighted = await _portfolio_weights(
            session, blob_store, workspace_id=workspace_id,
            version_id=portfolio_dataset_version_id, table=table, current_cells=current_cells,
        )
    cells = diff_cells(
        baseline_cells, current_cells, table.keys, table.value,
        weights=weighted.weights if weighted is not None else None,
    )
    return cells, weighted


async def _find_artifact(
    session: Any, blob_store: BlobStore, *, workspace_id: UUID, key: str
) -> tuple[dict[str, Any] | None, Job | None]:
    """The manifest a succeeded `rate_table.diff_cells` Job stored for exactly this key, else the
    Job in flight for it. A Job whose manifest blob is gone does not count: the query is built
    again, never answered from another query's artifact."""
    rows = await session.execute(
        select(JobRow)
        .where(
            JobRow.workspace_id == workspace_id,
            JobRow.kind == JobKind.RATE_TABLE_DIFF_CELLS,
            JobRow.parameters["key"].astext == key,
        )
        .order_by(JobRow.queued_at.desc())
    )
    in_flight: Job | None = None
    for job in rows.scalars():
        if job.status in (JobStatus.QUEUED, JobStatus.RUNNING):
            in_flight = in_flight or job_service.to_schema(job)
        elif job.status is JobStatus.SUCCEEDED:
            ref = (job.result or {}).get("ref")
            blob = await session.get(BlobRow, ref) if ref else None
            if blob is None:
                continue
            try:
                manifest: dict[str, Any] = json.loads(await blob_store.read(to_ref(blob)))
            except PlatformError:
                continue
            return manifest, None
    return None, in_flight


def _bad_cursor() -> PlatformError:
    return PlatformError(
        "VALIDATION_FAILED",
        "Malformed cursor",
        400,
        "The cursor is not one this API issued. Omit it to start from the beginning.",
    )


async def _read_cells(
    session: Any, blob_store: BlobStore, manifest: dict[str, Any], start: int, stop: int
) -> list[RateTableDiffCell] | None:
    """Cells `start` to `stop` of the artifact, reading only the chunks they lie in. `None` if
    a chunk is gone, which makes the artifact absent."""
    size: int = manifest["chunk_size"]
    items: list[RateTableDiffCell] = []
    for index in range(start // size, (stop - 1) // size + 1):
        blob = await session.get(BlobRow, manifest["chunks"][index])
        if blob is None:
            return None
        try:
            lines = (await blob_store.read(to_ref(blob))).splitlines()
        except PlatformError:
            return None
        low = max(start - index * size, 0)
        high = min(stop - index * size, len(lines))
        items.extend(RateTableDiffCell.model_validate_json(line) for line in lines[low:high])
    return items


async def _cells_key_for(
    session: Any,
    workspace_id: UUID,
    slug: str,
    version: int,
    against: str | int,
    portfolio_dataset_version_id: UUID | None,
) -> tuple[str, RateTableVersionRow]:
    """Resolve the versions and check the portfolio, before any Job, and name the query's
    artifact by identity (`cells_key`): nothing is read from a cell. Also returns the
    current version's row, for `_refuse_dangling_refs`."""
    table_row = await _load_table(session, workspace_id, slug)
    version_row = await _load_version(session, table_row.id, version, slug)
    baseline_number = await _resolve_baseline(session, table_row.id, version, against)
    await _load_version(session, table_row.id, baseline_number, slug)  # a 404 if it is gone
    if portfolio_dataset_version_id is not None:
        await check_portfolio(
            session, workspace_id=workspace_id, version_id=portfolio_dataset_version_id
        )
    key = cells_key(
        slug, version_row.version_number, baseline_number, portfolio_dataset_version_id
    )
    return key, version_row


async def _refuse_dangling_refs(
    session: Any, workspace_id: UUID, version_row: RateTableVersionRow, portfolio: UUID | None
) -> None:
    """A `factor_ref` or `banding_ref` that resolves to nothing is a `404` naming the key and the
    ref, synchronously and before any Job, on both routes and both storages (the maintainer's
    ruling; `RL-1361`'s "the Job fails with NOT_FOUND" for a parquet pair is superseded). Only a
    portfolio-weighted query reads the refs; a query that finds its artifact never reaches this."""
    if portfolio is None:
        return
    table = RateTable.model_validate(version_row.definition)
    await _key_artifacts(session, workspace_id, table.keys)


async def diff_cells_page(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    against: str | int,
    *,
    blob_store: BlobStore,
    portfolio_dataset_version_id: UUID | None = None,
    limit: int,
    cursor: str | None = None,
) -> DiffCellsPage | DiffCellsJobNeeded:
    """One cursor page of the diff's changed cells (FR-231, `RL-1418` T1 as amended).

    The `against` resolution and the portfolio checks (scope, then status) run first, before
    any Job. Every pair, whatever its storage, is answered from the artifact a
    `rate_table.diff_cells` Job stored for this exact query, found by version identity without
    loading a cell, or this reports that the Job is needed. So the first request for a
    (versions, portfolio) key is a 202 and a later page reads the manifest and the one or two
    chunks it lies in (R1, `07` §1.3: an operation that can exceed 2 s returns 202 with a Job).
    """
    async with database.unit_of_work() as session:
        key, version_row = await _cells_key_for(
            session, workspace_id, slug, version, against, portfolio_dataset_version_id
        )
        manifest, in_flight = await _find_artifact(
            session, blob_store, workspace_id=workspace_id, key=key
        )
        if manifest is None:
            if in_flight is None:
                await _refuse_dangling_refs(
                    session, workspace_id, version_row, portfolio_dataset_version_id
                )
            return DiffCellsJobNeeded(key=key, in_flight=in_flight)
        total: int = manifest["total"]
        start = decode_int_cursor(cursor) if cursor is not None else 0
        assert start is not None
        if cursor is not None and not 0 < start < total:
            raise _bad_cursor()
        stop = min(start + limit, total)
        items = await _read_cells(session, blob_store, manifest, start, stop) if total else []
        if items is None:
            return DiffCellsJobNeeded(key=key)
        return DiffCellsPage(
            items=items,
            total_estimate=min(total, COUNT_CAP),
            next_cursor=encode_cursor(stop) if stop < total else None,
        )


async def diff_from_artifact(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    against: str | int,
    *,
    blob_store: BlobStore,
    portfolio_dataset_version_id: UUID | None = None,
) -> RateTableDiff | DiffCellsJobNeeded:
    """The diff summary (FR-231), read from the manifest of the same artifact the cells route
    serves: the first request for a key is the Job (rows pairs too), later ones are 200 with
    the summary and the coverage figures the artifact carries and no cell read (R1)."""
    async with database.unit_of_work() as session:
        key, version_row = await _cells_key_for(
            session, workspace_id, slug, version, against, portfolio_dataset_version_id
        )
        manifest, in_flight = await _find_artifact(
            session, blob_store, workspace_id=workspace_id, key=key
        )
        if manifest is None:
            if in_flight is None:
                await _refuse_dangling_refs(
                    session, workspace_id, version_row, portfolio_dataset_version_id
                )
            return DiffCellsJobNeeded(key=key, in_flight=in_flight)
        return RateTableDiff.model_validate(manifest["summary"])


async def build_cells_artifact(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    against: str | int,
    *,
    blob_store: BlobStore,
    portfolio_dataset_version_id: UUID | None = None,
) -> str:
    """Compute every changed cell and store the artifact; returns the manifest's sha256 (FR-232).

    The cells are written in order as chunk blobs of `CELLS_CHUNK` cells, one JSON object per
    line, and a small manifest names them and carries the diff's summary and coverage figures.
    The checks run again under the Job's workspace, because the portfolio can lose its standing
    between submit and run (`RL-1361` item 8).
    """
    async with database.unit_of_work() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        baseline_number = await _resolve_baseline(session, table_row.id, version, against)
        baseline_row = await _load_version(session, table_row.id, baseline_number, slug)
        if portfolio_dataset_version_id is not None:
            await check_portfolio(
                session, workspace_id=workspace_id, version_id=portfolio_dataset_version_id
            )
        table = RateTable.model_validate(version_row.definition)
        cells, weighted = await _all_cells(
            session, blob_store, workspace_id=workspace_id, version_row=version_row,
            baseline_row=baseline_row, table=table,
            portfolio_dataset_version_id=portfolio_dataset_version_id,
        )
        summary = diff_summary(cells)
        if weighted is not None:
            summary = summary.model_copy(
                update={
                    "portfolio_exposure": weighted.portfolio_exposure,
                    "matched_exposure": weighted.matched_exposure,
                }
            )
        chunks: list[str] = []
        for start in range(0, len(cells), CELLS_CHUNK):
            payload = b"".join(
                cell.model_dump_json().encode() + b"\n" for cell in cells[start:start + CELLS_CHUNK]
            )
            chunks.append((await blob_store.put(session, payload, "application/x-ndjson")).sha256)
        manifest = {
            "chunk_size": CELLS_CHUNK,
            "total": len(cells),
            "chunks": chunks,
            "summary": json.loads(summary.model_dump_json()),
        }
        ref = await blob_store.put(session, json.dumps(manifest).encode(), "application/json")
        return ref.sha256


async def export_csv(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    blob_store: BlobStore,
) -> bytes:
    """The version's cells as CSV, decimal strings only (FR-235).

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
    """The version's cells as XLSX, every cell written as text (FR-235)."""
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
    """The would-be version as a diff against the addressed one (FR-235, 03 §5.1).

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
    """Create the version the preview showed (FR-235, 03 §5.1, DP6).

    The upload is parsed again through the same strict pipeline the preview ran —
    the created version cannot diverge from the preview (same bytes, same immutable
    baseline). The verdict is recorded on the version as `created_by_import` (DP5),
    the seed anchor is inherited from the baseline (DP4, FR-234), and the
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
        # `RL-1375` DP-1 (a2): version N's seed origin is the lowest-numbered version of the
        # same table whose `seeded_from` equals N's, the whole stored value (`model_ref` and
        # `seeded_at`), so a re-seed starts its own origin and two seeds of one model stay
        # distinct. A version with no `seeded_from` has no origin.
        anchor = await session.scalar(
            select(RateTableVersionRow.seeded_from).where(
                RateTableVersionRow.rate_table_id == rate_table_id,
                RateTableVersionRow.version_number == version,
            )
        )
        seed_number = None
        if anchor is not None:
            seed_number = cast(
                int | None,
                await session.scalar(
                    select(RateTableVersionRow.version_number)
                    .where(
                        RateTableVersionRow.rate_table_id == rate_table_id,
                        RateTableVersionRow.seeded_from == anchor,
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
    """Cells → parquet bytes (FR-232). Every column is UTF-8: keys and values are
    level names and decimal strings, and a numeric inference would silently re-type
    them — the strict round-trip FR-235's verdict is about."""
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
    """The version's cells, wherever storage keeps them (FR-232)."""
    if version_row.storage == "parquet":
        ref = BlobRef.model_validate(version_row.cells)
        return _cells_from_parquet(await blob_store.read(ref))
    return await _load_cells(session, version_row.id, table)


async def read_definition(
    database: Database, workspace_id: UUID, slug: str, version: int
) -> RateTable:
    """FR 9940: one version's definition — keys, value, storage, flag, default row — never
    its cells. The stored `definition` is exactly a `RateTable`."""
    async with database.session() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        return RateTable.model_validate(version_row.definition)


def _cells_in_key_order(
    cells: Sequence[dict[str, str]], key_names: Sequence[str]
) -> list[dict[str, str]]:
    """RL-1475 item 2: code-point order per key column in declared order, compared as
    strings, for both storages. The one place cells are sorted; never a SQL `ORDER BY`,
    whose collation could differ from the parquet path's."""
    return sorted(cells, key=lambda row: tuple(row[name] for name in key_names))


async def cells_page(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    blob_store: BlobStore,
    *,
    cursor: str | None,
    limit: int,
) -> Page[RateTableCell]:
    """FR 9940: one page of an immutable version's cells, never a Job (FR-232).

    The cells of the version are loaded per page, then sorted and sliced. For a rows-stored
    version that is at most the version's cell count, which is at most the workspace
    threshold (FR-232); a parquet version reads its blob once per page.
    """
    async with database.session() as session:
        table_row = await _load_table(session, workspace_id, slug)
        version_row = await _load_version(session, table_row.id, version, slug)
        table = RateTable.model_validate(version_row.definition)
        cells = await _load_cells_of(session, version_row, table, blob_store)
    ordered = _cells_in_key_order(cells, [key.name for key in table.keys])
    total = len(ordered)
    start = decode_int_cursor(cursor) or 0
    if cursor is not None and not 0 < start < total:
        raise _bad_cursor()
    stop = min(start + limit, total)
    return Page[RateTableCell](
        items=_wire_rows(ordered[start:stop]),
        next_cursor=encode_cursor(stop) if stop < total else None,
        total_estimate=min(total, COUNT_CAP),
    )


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
    """Save-time equality proof (03 §4.2, FR-234, DP4): a derived version's seed
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
    from the cell count and frozen with the version (FR-232). At or below the
    threshold the cells keep the `rate_table_cells` rows; above it they are written
    to a content-addressed parquet blob addressed by `cells`. Returns the version in
    its §4.2 wire form.
    """
    assert derived.rows is not None  # `_persist_new_version`'s input is a rows-form version
    cells = [dict(row.root) for row in derived.rows]
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
    """Apply a bulk operation and persist the new version (FR-233, 03 §5.1).

    The operation addresses a specific version (`{slug}@{version}`): the baseline is
    loaded from the addressed version, its seed lineage is proven equal at save time
    (FR-234, 03 §4.2, DP4), and the new version's storage is decided against the
    workspace threshold (FR-232, DP2).
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
