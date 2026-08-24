"""Ingestion end to end (`01` §3.1, FR-DATA-2..8, FR-DATA-40).

Against a real database and a real blob store: parquet round-trips and content-addressed
storage are the behaviours under test, and neither survives a double.
"""

from __future__ import annotations

import gzip
import io

import polars as pl
import pytest
from sqlalchemy import select

from app.data.ingestion import ingest_upload
from app.db.models import IngestionRunRow, RoleAssignmentRow, RoleRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets, rbac
from app.platform.blobs import BlobStore
from model_schema import (
    ActorKind,
    DataDictionaryEntry,
    DatasetStatus,
    PiiClass,
    Principal,
    ScopeType,
    new_uuid7,
)

CSV = b"Policy ID,Exposure Start,Exposure Years\nP1,2026-01-01,1.0\nP2,2026-02-01,0.5\n"


async def _analyst(database: Database, workspace_id) -> Principal:
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == "analyst"
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=user.id,
                role_id=role.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )
    return user


async def _dataset(database: Database, workspace_id, actor):
    async with database.unit_of_work() as session:
        row = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        return row.id


@pytest.mark.req("FR-DATA-3")
async def test_a_csv_upload_becomes_a_draft_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        outcome = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=CSV, filename="exposure.csv",
        )
        version_id = outcome.version.id
        assert outcome.version.status == DatasetStatus.DRAFT
        assert outcome.version.version == 1
        assert outcome.run.rows_read == 2
        assert outcome.run.rows_written == 2

    async with database.session() as session:
        from app.db.models import DatasetVersionRow

        row = await session.get(DatasetVersionRow, version_id)
    assert [t["name"] for t in row.tables] == ["policy_exposure"]
    assert row.tables[0]["row_count"] == 2


@pytest.mark.req("FR-DATA-5")
async def test_column_names_are_normalised_and_the_source_names_kept(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        outcome = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=CSV, filename="exposure.csv",
        )
        table = outcome.version.tables[0]

    assert set(table["arrow_schema"]) == {"policy_id", "exposure_start", "exposure_years"}
    assert table["source_names"]["policy_id"] == "Policy ID"


@pytest.mark.req("FR-DATA-5")
async def test_a_column_collision_fails_the_ingestion(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Negative: a silent rename would lose a column and nobody would know."""
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    colliding = b"Policy ID,policy id\nP1,P1\n"

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await ingest_upload(
                session, blob_store,
                workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
                data=colliding, filename="dup.csv",
            )
    assert exc.value.code == "COLUMN_NAME_COLLISION"


@pytest.mark.req("FR-DATA-7")
async def test_unusable_rows_are_quarantined_with_the_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-DATA-7: rejected to a quarantine table stored with the version, not dropped."""
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    data = b"Policy ID,Exposure Start\nP1,2026-01-01\nP2,\nP3,2026-03-01\n"

    async with database.unit_of_work() as session:
        outcome = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=data, filename="exposure.csv",
            required_non_null=["exposure_start"],
        )
        tables = {t["name"]: t for t in outcome.version.tables}
        run = outcome.run

    assert "_rejected" in tables
    assert tables["_rejected"]["row_count"] == 1
    assert run.rows_read == 3
    assert run.rows_written == 2
    assert run.rows_rejected == 1
    assert run.reject_sample[0]["_reject_reason"] == "exposure_start is null"


@pytest.mark.req("FR-DATA-6")
async def test_the_run_records_what_the_requirement_lists(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        outcome = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=CSV, filename="exposure.csv",
        )
        run = outcome.run

    assert run.bytes_read == len(CSV)
    assert run.duration_ms >= 0
    assert run.source_fingerprint is not None
    assert len(run.source_fingerprint) == 64
    assert "polars" in run.library_versions
    assert outcome.version.library_versions["polars"]


@pytest.mark.req("FR-DATA-8")
async def test_the_same_key_and_unchanged_source_returns_the_original_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        first = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=CSV, filename="exposure.csv", idempotency_key="load-2026H1",
        )
        first_id = first.version.id
    async with database.unit_of_work() as session:
        second = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=CSV, filename="exposure.csv", idempotency_key="load-2026H1",
        )
    assert second.reused is True
    assert second.version.id == first_id


@pytest.mark.req("FR-DATA-8")
async def test_the_same_key_with_changed_data_creates_a_new_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """Negative, and the reason the fingerprint is part of the identity.

    Returning the old version for changed source data would quietly serve stale data to a
    caller who believes they refreshed it.
    """
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    changed = CSV + b"P3,2026-03-01,0.25\n"

    async with database.unit_of_work() as session:
        first = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=CSV, filename="exposure.csv", idempotency_key="nightly",
        )
        first_id = first.version.id
    async with database.unit_of_work() as session:
        second = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=changed, filename="exposure.csv", idempotency_key="nightly",
        )
    assert second.reused is False
    assert second.version.id != first_id
    assert second.version.version == 2


@pytest.mark.req("FR-DATA-40")
async def test_each_version_is_a_complete_snapshot(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-DATA-40 / OQ-DATA-2: a version is complete and independently validatable, never
    a delta against its predecessor."""
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        first = await ingest_upload(
            session, blob_store, workspace_id=workspace_id, actor=actor,
            dataset_id=dataset_id, data=CSV, filename="a.csv",
        )
        first_ref = first.version.tables[0]["blob"]
    async with database.unit_of_work() as session:
        second = await ingest_upload(
            session, blob_store, workspace_id=workspace_id, actor=actor,
            dataset_id=dataset_id, data=CSV + b"P3,2026-03-01,0.25\n", filename="b.csv",
        )
        second_ref = second.version.tables[0]["blob"]
        assert second.version.tables[0]["row_count"] == 3

    # Each version's table holds every row it describes, not the delta.
    from model_schema import BlobRef

    body = await blob_store.read(BlobRef.model_validate(second_ref))
    frame = pl.read_parquet(io.BytesIO(body))
    assert frame.height == 3
    assert first_ref["sha256"] != second_ref["sha256"]


@pytest.mark.req("FR-DATA-3")
async def test_a_gzipped_upload_is_handled_transparently(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        outcome = await ingest_upload(
            session, blob_store, workspace_id=workspace_id, actor=actor,
            dataset_id=dataset_id, data=gzip.compress(CSV), filename="exposure.csv.gz",
        )
    assert outcome.run.rows_read == 2


@pytest.mark.req("FR-DATA-3")
async def test_a_parquet_upload_round_trips(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    buffer = io.BytesIO()
    pl.DataFrame({"policy_id": ["P1", "P2"], "exposure_years": [1.0, 0.5]}).write_parquet(
        buffer
    )
    async with database.unit_of_work() as session:
        outcome = await ingest_upload(
            session, blob_store, workspace_id=workspace_id, actor=actor,
            dataset_id=dataset_id, data=buffer.getvalue(), filename="exposure.parquet",
        )
    assert outcome.run.rows_written == 2


@pytest.mark.req("FR-DATA-3")
async def test_an_unsupported_file_type_is_refused(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await ingest_upload(
                session, blob_store, workspace_id=workspace_id, actor=actor,
                dataset_id=dataset_id, data=b"\\x00\\x01", filename="model.pkl",
            )
    assert exc.value.code == "SCHEMA_INFERENCE_CONFLICT"


@pytest.mark.req("FR-DATA-2")
async def test_ingestion_never_mutates_an_existing_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """FR-DATA-2: every run produces a new version or none. There is no path editing @11."""
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        first = await ingest_upload(
            session, blob_store, workspace_id=workspace_id, actor=actor,
            dataset_id=dataset_id, data=CSV, filename="a.csv",
        )
        first_id, first_tables = first.version.id, first.version.tables
    async with database.unit_of_work() as session:
        await ingest_upload(
            session, blob_store, workspace_id=workspace_id, actor=actor,
            dataset_id=dataset_id, data=CSV + b"P9,2026-09-01,0.1\n", filename="b.csv",
        )
    async with database.session() as session:
        from app.db.models import DatasetVersionRow

        unchanged = await session.get(DatasetVersionRow, first_id)
    assert unchanged.tables == first_tables
    assert unchanged.version == 1


@pytest.mark.req("FR-GOV-2")
async def test_ingestion_requires_the_write_permission(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    stranger = Principal(kind=ActorKind.USER, id=new_uuid7(), display="x")
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await ingest_upload(
                session, blob_store, workspace_id=workspace_id, actor=stranger,
                dataset_id=dataset_id, data=CSV, filename="a.csv",
            )
    assert exc.value.code == "PERMISSION_DENIED"


@pytest.mark.req("FR-DATA-6")
async def test_the_run_is_queryable_after_the_fact(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        await ingest_upload(
            session, blob_store, workspace_id=workspace_id, actor=actor,
            dataset_id=dataset_id, data=CSV, filename="a.csv",
        )
    async with database.session() as session:
        runs = (
            await session.execute(
                select(IngestionRunRow).where(IngestionRunRow.dataset_id == dataset_id)
            )
        ).scalars().all()
    assert len(runs) == 1
    assert runs[0].status == "succeeded"


# -- FR-DATA-41: a direct identifier is refused at ingestion ------------------------------

PII_CSV = (
    b"policy_id,customer_email,exposure_start,exposure_years\n"
    b"P1,alice@example.com,2026-01-01,1.0\n"
    b"P2,bob@example.com,2026-01-01,1.0\n"
)


async def _dataset_with_pii_dictionary(
    database: Database,
    workspace_id,
    actor,
    pii_class: PiiClass = PiiClass.DIRECT_IDENTIFIER,
):
    """A dataset whose dictionary classifies `customer_email` at `pii_class`.

    The class is a parameter because the rule under test is *which* classes are refused,
    not whether a classified column is refused. A caller passing a *permitted* class is
    the only input that distinguishes a `forbidden` derived from `pii_class` from one
    derived from dictionary membership — with no dictionary both are empty and the
    refusal returns at its empty-`forbidden` guard, so a test built that way cannot
    tell the two derivations apart.
    """
    async with database.unit_of_work() as session:
        row = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        await datasets.update_dictionary(
            session,
            workspace_id=workspace_id,
            actor=actor,
            slug=row.slug,
            entries={
                "customer_email": DataDictionaryEntry(
                    description="The policyholder's email address",
                    pii_class=pii_class,
                )
            },
        )
        return row.id


@pytest.mark.req("FR-DATA-41")
async def test_a_direct_identifier_column_is_refused_at_ingestion(
    database: Database, blob_store, workspace_id
) -> None:
    """FR-DATA-13's other half, which nothing enforced until now.

    `DIRECT_IDENTIFIER_PRESENT` was registered in the error catalogue and raised nowhere;
    `modelling_forbidden_columns` had no caller. A dataset carrying an email address
    ingested cleanly, and every FR-DATA-13 marker sat on `pseudonymise`.
    """
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset_with_pii_dictionary(database, workspace_id, actor)

    with pytest.raises(PlatformError) as refused:
        async with database.unit_of_work() as session:
            await ingest_upload(
                session, blob_store,
                workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
                data=PII_CSV, filename="exposure.csv",
            )
    assert refused.value.code == "DIRECT_IDENTIFIER_PRESENT"
    assert "customer_email" in refused.value.detail

    # Refused *before* the version: an identifier in object storage is a deletion problem,
    # not a refusal.
    async with database.session() as session:
        from app.db.models import DatasetVersionRow

        versions = (
            await session.execute(
                select(DatasetVersionRow).where(DatasetVersionRow.dataset_id == dataset_id)
            )
        ).scalars().all()
    assert versions == []


@pytest.mark.req("FR-DATA-41")
async def test_pseudonymising_the_column_lets_the_upload_through(
    database: Database, blob_store, workspace_id
) -> None:
    """The remedy FR-DATA-13 names, and the reason the check runs *after* the recipe.

    Checked before it, a pseudonymise step could never satisfy the rule it exists for.
    """
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset_with_pii_dictionary(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        outcome = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=PII_CSV, filename="exposure.csv",
            recipe=[
                {
                    "step": "pseudonymise",
                    "params": {"column": "customer_email", "key": "workspace-secret"},
                }
            ],
        )
    assert outcome.version.version == 1
    assert outcome.run.rows_written == 2


@pytest.mark.req("FR-DATA-41")
async def test_a_column_the_dictionary_does_not_forbid_is_not_refused(
    database: Database, blob_store, workspace_id
) -> None:
    """The negative of the rule: the refused set is a class, not the dictionary.

    `customer_email` is classified `quasi_identifier` — in the dictionary, and permitted.
    That is the only input that distinguishes a `forbidden` derived from `pii_class` from
    one derived from dictionary membership. **In unmutated code this test still returns at
    the empty-`forbidden` guard**, because `quasi_identifier` is outside
    `MODELLING_FORBIDDEN_PII` and `modelling_forbidden_columns` therefore yields nothing —
    so do not read it as covering the per-column filter, the pseudonymise carve-out or the
    error construction below that guard. What it covers is the *derivation*: a control
    built with no dictionary passes against a check refusing every classified column
    (verified 2026-08-24 by mutating `forbidden` to `set(dataset.data_dictionary)` — the
    whole module stayed green at 17 passed), and this one fails it. Keep the
    classification here.
    """
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset_with_pii_dictionary(
        database, workspace_id, actor, pii_class=PiiClass.QUASI_IDENTIFIER
    )

    async with database.unit_of_work() as session:
        outcome = await ingest_upload(
            session, blob_store,
            workspace_id=workspace_id, actor=actor, dataset_id=dataset_id,
            data=PII_CSV, filename="exposure.csv",
        )
    assert outcome.run.rows_written == 2
