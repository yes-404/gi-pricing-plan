"""Rate table platform service (03 §3.3, slice W10-3C): bulk operations, the parquet
write path, and the seed-lineage guard.

The four bulk operations (FR-RATE-18, 04 §4.4), the storage-threshold decision at
version-creation time (FR-RATE-62, DP2), and the save-time seed-lineage equality proof
(FR-RATE-19, 03 §4.2, DP4). Models are inserted rather than fitted, exactly as the
W10-2 API tests do — the service cares that the model row is approved with relativities,
not how the fit happened.
"""

from __future__ import annotations

import io
from decimal import Decimal
from uuid import uuid4

import polars as pl
import pytest
from backend.tests.test_api_rate_tables import (
    _LEVELS,
    _fit_result,
    _glm_spec,
    _table_slug,
)
from sqlalchemy import select

from app.config import Settings
from app.db.models import ModelRow, RateTableRow, RateTableVersionRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import rate_tables as svc
from app.platform import settings as settings_svc
from app.platform import workspaces
from app.platform.blobs import BlobStore
from model_schema import ModelStatus, new_uuid7
from model_schema.rating import RateTableVersion, SeededFrom
from model_schema.refs import ArtifactRef, BlobRef

THRESHOLD = "rate_tables.cell_threshold"


async def _set_threshold(database: Database, workspace_id, value: int) -> None:
    """`workspace_settings` carries an FK to `workspaces`; a bare fixture id needs the
    workspace row first (the `test_settings` convention)."""
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await settings_svc.set_workspace_setting(session, workspace_id, THRESHOLD, value)


async def _seed_approved_model(
    database: Database, workspace_id, family: str, relativities: dict[str, object]
) -> None:
    """An approved ModelRow whose fit carries the given relativities, inserted on the
    `database` fixture — the API test file's version spins its own event loop, which
    cannot run inside an async test."""
    from uuid import uuid4

    async with database.unit_of_work() as session:
        session.add(
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug=family,
                version=1,
                status=ModelStatus.APPROVED.value,
                dataset_version_id=new_uuid7(),
                spec=_glm_spec(family, new_uuid7()),
                spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
                fit_result=_fit_result(relativities),
                diagnostics_id=uuid4(),
            )
        )
        await session.flush()


async def _seed(
    database: Database, workspace_id, principal, family: str, slug: str, blob_store: BlobStore
) -> RateTableVersion:
    await _seed_approved_model(database, workspace_id, family, _LEVELS)
    return await svc.seed_from_model(
        database,
        workspace_id,
        principal.id,
        Settings(),
        blob_store,
        slug=slug,
        model_ref=ArtifactRef(type="model", slug=family, version=1),
        change_note="Seeded for the W10-3C service tests",
    )


async def _version_row(
    database: Database, workspace_id, slug: str, version: int
) -> RateTableVersionRow:
    async with database.session() as session:
        table_row = await session.scalar(
            select(RateTableRow).where(
                RateTableRow.workspace_id == workspace_id,
                RateTableRow.slug == slug,
            )
        )
        assert table_row is not None
        row = await session.scalar(
            select(RateTableVersionRow).where(
                RateTableVersionRow.rate_table_id == table_row.id,
                RateTableVersionRow.version_number == version,
            )
        )
        assert row is not None
        return row


@pytest.mark.req("FR-RATE-18")
async def test_bulk_uplift_records_the_operation_and_inherits_seed_lineage(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """The 04 §4.4 record rides the version: parameters, applied_to, result — and the
    seed anchor survives the derivation (03 §4.2, DP4)."""
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    seeded = await _seed(database, workspace_id, principal, family, slug, blob_store)
    baseline = seeded.seeded_from.model_dump(mode="json")

    wire = await svc.bulk_operation(
        database,
        workspace_id,
        principal.id,
        Settings(),
        blob_store,
        slug=slug,
        version=1,
        kind="uplift_table",
        parameters={"percentage": "0.10"},
    )

    assert wire.version == 2
    assert wire.storage == "rows"
    assert {row["driver_age_band"]: row["relativity"] for row in wire.rows or []} == {
        "17-20": "2.112",
        "21-24": "1.551",
        "25-29": "1.232",
    }
    operation = wire.created_by_operation
    assert operation is not None
    assert operation.kind == "uplift_table"
    assert operation.parameters.percentage == Decimal("0.10")
    assert operation.applied_to == ArtifactRef(
        type="rate_table", slug=slug, version=1
    )
    assert operation.result.changed_cells == 3
    assert operation.result.new_version == ArtifactRef(
        type="rate_table", slug=slug, version=2
    )
    assert wire.seeded_from is not None
    assert wire.seeded_from.model_dump(mode="json") == baseline

    version_row = await _version_row(database, workspace_id, slug, 2)
    assert version_row.storage == "rows"
    assert version_row.created_by_operation is not None
    assert version_row.created_by_operation["parameters"]["percentage"] == "0.10"
    assert version_row.created_by_operation["result"]["changed_cells"] == 3
    assert version_row.seeded_from == baseline


@pytest.mark.req("FR-RATE-62")
async def test_cells_spill_to_parquet_above_the_workspace_threshold(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """Above the workspace threshold the new version addresses a content-addressed
    parquet blob instead of rows, and the blob round-trips the exact cells."""
    await _set_threshold(database, workspace_id, 2)
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    await _seed(database, workspace_id, principal, family, slug, blob_store)

    wire = await svc.bulk_operation(
        database,
        workspace_id,
        principal.id,
        Settings(),
        blob_store,
        slug=slug,
        version=1,
        kind="uplift_table",
        parameters={"percentage": "0.10"},
    )

    assert wire.storage == "parquet"
    assert wire.rows is None
    assert wire.cells is not None
    assert wire.cells.media_type == "application/parquet"

    version_row = await _version_row(database, workspace_id, slug, 2)
    assert version_row.storage == "parquet"
    assert version_row.cells == wire.cells.model_dump(mode="json")

    content = await blob_store.read(BlobRef.model_validate(version_row.cells))
    frame = pl.read_parquet(io.BytesIO(content))
    cells = {
        row["driver_age_band"]: row["relativity"] for row in frame.to_dicts()
    }
    assert cells == {
        "17-20": "2.112",
        "21-24": "1.551",
        "25-29": "1.232",
    }


@pytest.mark.req("FR-RATE-62")
async def test_the_seed_obeys_the_threshold(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """DP2: the threshold applies to new versions — the seed itself decides."""
    await _set_threshold(database, workspace_id, 2)
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    seeded = await _seed(database, workspace_id, principal, family, slug, blob_store)

    assert seeded.storage == "parquet"
    version_row = await _version_row(database, workspace_id, slug, 1)
    assert version_row.storage == "parquet"
    assert version_row.cells is not None


@pytest.mark.req("FR-RATE-62")
async def test_a_parquet_baseline_feeds_a_bulk_operation(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """An operation on a parquet-stored version reads the blob inline — the Job-worthy
    read is the diff (W10-3D), not a bounded table transform."""
    await _set_threshold(database, workspace_id, 2)
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    await _seed(database, workspace_id, principal, family, slug, blob_store)
    await svc.bulk_operation(
        database,
        workspace_id,
        principal.id,
        Settings(),
        blob_store,
        slug=slug,
        version=1,
        kind="uplift_table",
        parameters={"percentage": "0.10"},
    )

    wire = await svc.bulk_operation(
        database,
        workspace_id,
        principal.id,
        Settings(),
        blob_store,
        slug=slug,
        version=2,
        kind="floor_and_cap",
        parameters={"floor": "1.0", "cap": "2.0"},
    )

    assert wire.version == 3
    assert wire.storage == "parquet"
    assert wire.created_by_operation is not None
    assert wire.created_by_operation.kind == "floor_and_cap"
    assert wire.created_by_operation.result.changed_cells == 1

    version_row = await _version_row(database, workspace_id, slug, 3)
    content = await blob_store.read(BlobRef.model_validate(version_row.cells))
    frame = pl.read_parquet(io.BytesIO(content))
    cells = {
        row["driver_age_band"]: row["relativity"] for row in frame.to_dicts()
    }
    assert cells == {"17-20": "2", "21-24": "1.551", "25-29": "1.232"}


@pytest.mark.req("FR-RATE-19")
async def test_the_seed_lineage_guard_refuses_a_divergent_derived_version(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """Save-time proof (03 §4.2): a derived version may not invent or drop the seed
    anchor. Through `bulk_operation` the core inherits the baseline's lineage by
    construction, so the guard is exercised on crafted input — the corruption it
    catches is internal, and the test states the invariant it protects."""
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    await _seed(database, workspace_id, principal, family, slug, blob_store)
    baseline_row = await _version_row(database, workspace_id, slug, 1)

    derived = RateTableVersion(
        slug=slug,
        version=2,
        rateable=True,
        storage="rows",
        keys=baseline_row.definition["keys"],
        value=baseline_row.definition["value"],
        rows=[
            {"driver_age_band": "17-20", "relativity": "2.112"},
            {"driver_age_band": "21-24", "relativity": "1.551"},
            {"driver_age_band": "25-29", "relativity": "1.232"},
        ],
        change_note="crafted",
        seeded_from=SeededFrom(
            model_ref=ArtifactRef(type="model", slug="some-other-model", version=9),
            seeded_at=baseline_row.seeded_from["seeded_at"],
        ),
    )

    with pytest.raises(PlatformError) as exc:
        svc._guard_seed_lineage(derived, baseline_row)
    assert exc.value.code == "RATE_TABLE_SEED_MISMATCH"
    assert exc.value.status_code == 422


@pytest.mark.req("FR-RATE-19")
async def test_the_seed_lineage_guard_accepts_the_baselines_anchor(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    await _seed(database, workspace_id, principal, family, slug, blob_store)
    baseline_row = await _version_row(database, workspace_id, slug, 1)

    derived = RateTableVersion(
        slug=slug,
        version=2,
        rateable=True,
        storage="rows",
        keys=baseline_row.definition["keys"],
        value=baseline_row.definition["value"],
        rows=[
            {"driver_age_band": "17-20", "relativity": "2.112"},
            {"driver_age_band": "21-24", "relativity": "1.551"},
            {"driver_age_band": "25-29", "relativity": "1.232"},
        ],
        change_note="crafted",
        seeded_from=SeededFrom.model_validate(baseline_row.seeded_from),
    )

    svc._guard_seed_lineage(derived, baseline_row)


@pytest.mark.req("FR-RATE-18")
async def test_floor_above_cap_is_a_named_refusal(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    await _seed(database, workspace_id, principal, family, slug, blob_store)

    with pytest.raises(PlatformError) as exc:
        await svc.bulk_operation(
            database,
            workspace_id,
            principal.id,
            Settings(),
            blob_store,
            slug=slug,
            version=1,
            kind="floor_and_cap",
            parameters={"floor": "2.0", "cap": "1.0"},
        )
    assert exc.value.code == "FLOOR_ABOVE_CAP"
    assert exc.value.status_code == 422


@pytest.mark.req("FR-RATE-18")
async def test_an_unknown_operation_kind_is_refused(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    await _seed(database, workspace_id, principal, family, slug, blob_store)

    with pytest.raises(PlatformError) as exc:
        await svc.bulk_operation(
            database,
            workspace_id,
            principal.id,
            Settings(),
            blob_store,
            slug=slug,
            version=1,
            kind="lift_everything",
            parameters={},
        )
    assert exc.value.code == "VALIDATION_FAILED"
    assert exc.value.status_code == 422


@pytest.mark.req("FR-RATE-18")
async def test_malformed_operation_parameters_are_refused(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    await _seed(database, workspace_id, principal, family, slug, blob_store)

    with pytest.raises(PlatformError) as exc:
        await svc.bulk_operation(
            database,
            workspace_id,
            principal.id,
            Settings(),
            blob_store,
            slug=slug,
            version=1,
            kind="uplift_table",
            parameters={"percentage": "not-a-percentage"},
        )
    assert exc.value.code == "VALIDATION_FAILED"
    assert exc.value.status_code == 422
