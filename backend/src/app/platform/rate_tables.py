"""Rate table platform service (03 §3.3, slice W10-2): seeding and cell diffs.

Thin over the pure operations in `pricing_core.rate_tables.operations`: load the
model artifact, run the operation, persist rows. Named failures from pricing-core are
mapped onto the module's API error codes (03 §5.2): the four validation codes become
`RATE_TABLE_INCOMPLETE` / `RATE_TABLE_KEY_DUPLICATE`, the approval gate stays
`PIN_NOT_APPROVED`.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Literal, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    RateTableCellRow,
    RateTableRow,
    RateTableVersionRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform.modelling import load_model, to_model
from model_schema.rating import (
    RateTable,
    RateTableDiff,
)
from model_schema.refs import ArtifactRef
from pricing_core.rate_tables.operations import (
    diff_vs_previous,
    diff_vs_seed,
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
    *,
    slug: str,
    model_ref: ArtifactRef,
    change_note: str,
    rateable: bool = True,
) -> dict[str, Any]:
    """Seed a new rate table version from an approved model (FR-RATE-16, spec §5.1).

    The seed is the only version-creation path in this slice: it creates the table
    (version 1) or appends the next version of an existing table, and pins
    `seeded_from` so "how far from the technical rate?" is answerable (FR-RATE-16).
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
                current_version=1,
                created_by=created_by,
            )
            session.add(table_row)
            await session.flush()
            version_number = 1
        else:
            version_number = table_row.current_version + 1

        definition = result.table.model_dump()
        definition["version"] = version_number
        version_row = RateTableVersionRow(
            workspace_id=workspace_id,
            rate_table_id=table_row.id,
            version_number=version_number,
            storage=result.table.storage,
            definition=definition,
            change_note=change_note,
            seeded_from=result.seeded_from.model_dump(mode="json"),
            created_by=created_by,
        )
        session.add(version_row)
        try:
            await session.flush()
        except IntegrityError as exc:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Rate table version already exists",
                409,
                f"{slug}@{version_number} already exists in this workspace.",
            ) from exc
        table_row.current_version = version_number
        session.add_all(
            RateTableCellRow(version_id=version_row.id, key=key, value=value)
            for key, value in _cells_for_rows(
                result.cells, result.table.keys, result.table.value.name
            )
        )
        await session.flush()

        return {
            **definition,
            "rows": list(result.cells),
            "seeded_from": result.seeded_from.model_dump(mode="json"),
            "change_note": change_note,
        }


def _cells_for_rows(
    cells: Sequence[dict[str, str]], keys: list[Any], value_name: str
) -> list[tuple[list[str], str]]:
    """Rows → (key tuple as JSON array, value as decimal string), in key order."""
    key_names = [key.name for key in keys]
    return [([row[name] for name in key_names], row[value_name]) for row in cells]


async def diff(
    database: Database,
    workspace_id: UUID,
    slug: str,
    version: int,
    against: str | int,
) -> RateTableDiff:
    """Cell-level diff of one version against a baseline (FR-RATE-17, spec §5.1).

    `against` names the baseline: `previous` (the prior version), `seed` (the version
    that seeded the table — the technical-rate origin, FR-RATE-16), or an explicit
    version number. Diffed on read (DP3: compute on read, nothing materialised at
    version creation). Exposure weights are supplied by the caller at fetch time
    (DP1); this slice passes none — the portfolio-dataset join is not yet built.
    Answers 200 for `rows`-stored versions; a `parquet` version is refused with
    `RATE_TABLE_PARQUET_UNBUILT` — nothing can yet write parquet storage, so the
    202-with-Job form (FR-RATE-62) lands in W10-3 with the storage itself.
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

        version_row = await _load_version(session, table_row.id, version, slug)
        # The parquet refusal fires before the baseline resolves: version 1 against
        # `previous` would otherwise 404 as baseless before the storage check runs.
        _refuse_parquet(version_row, slug, version)
        baseline_number = await _resolve_baseline(
            session, table_row.id, version, against
        )
        baseline_row = await _load_version(
            session, table_row.id, baseline_number, slug
        )
        _refuse_parquet(baseline_row, slug, baseline_number)

        table = RateTable.model_validate(version_row.definition)
        current_cells = await _load_cells(session, version_row.id, table)
        baseline_cells = await _load_cells(session, baseline_row.id, table)
        if against == "seed":
            diff = diff_vs_seed(baseline_cells, current_cells, table.keys, table.value)
        else:
            diff = diff_vs_previous(baseline_cells, current_cells, table.keys, table.value)
        return diff


def _refuse_parquet(version_row: RateTableVersionRow, slug: str, number: int) -> None:
    """Refuse a diff touching a parquet-stored version (03 §5.1, RATE_TABLE_PARQUET_UNBUILT)."""
    if version_row.storage == "parquet":
        raise PlatformError(
            "RATE_TABLE_PARQUET_UNBUILT",
            "Parquet-backed diff is not built yet",
            501,
            f"{slug}@{number} is stored as parquet, whose diff answers 202 with a "
            "Job (FR-RATE-62) — deferred to W10-3 with the parquet storage itself, "
            "and refused here rather than fabricating a diff.",
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
