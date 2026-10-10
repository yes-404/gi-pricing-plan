"""Rate table routes (03 §5.1, slices W10-2/W10-3C): seeding, cell diffs, bulk
operations, and the export/import preview.

`POST /rate-tables/{slug}/seed-from-model` (FR-230),
`GET /rate-tables/{slug}@{version}/diff?against=` (FR-231),
`POST /rate-tables/{slug}@{version}/bulk-operation` (FR-233), and the CSV/XLSX
export and import preview (FR-235). Models are inserted rather than fitted —
these routes care that the model row carries an approved status and a fit result with
relativities, not how the fit happened, and a real GLM fit per test would buy nothing
this file asserts.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

import pytest
from backend.tests.approved_rows import add_approved
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient
from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import (
    FactorRow,
    ModelRow,
    RateTableRow,
    RateTableVersionRow,
)
from app.db.session import Database
from model_schema import GlmSpec, ModelStatus, OffsetSpec, new_uuid7
from model_schema.modelling import Factor, FactorType


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    """A caller with `RATING_WRITE` and `RATING_READ` (the `analyst` role)."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    return _headers(principal.id, workspace_id)


@pytest.fixture
def auditor_headers(workspace_id, grant) -> dict[str, str]:
    """A caller with `RATING_READ` but not `RATING_WRITE` (the `auditor` role)."""
    other = uuid4()
    asyncio.get_event_loop().run_until_complete(grant("auditor", principal_id=other))
    return _headers(other, workspace_id)


@pytest.fixture
def admin_headers(workspace_id, grant) -> dict[str, str]:
    """A caller with `ADMIN_MANAGE_SETTINGS` — the workspace threshold is a setting
    (FR-232), so the parquet-path tests set it through the API like an operator."""
    other = uuid4()
    asyncio.get_event_loop().run_until_complete(grant("admin", principal_id=other))
    return _headers(other, workspace_id)


def _glm_spec(family: str, dataset_version_id: UUID) -> dict[str, object]:
    """A valid `GlmSpec` as JSON — `to_model` re-validates it, so `{}` will not do."""
    spec = GlmSpec(
        model_family_slug=family,
        dataset_version_id=dataset_version_id,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
    )
    return spec.model_dump(mode="json")


def _fit_result(relativities: dict[str, list[float]]) -> dict[str, object]:
    """A `GlmFitResult` as JSON: one entry per factor, one per level."""
    return {
        "model_type": "glm",
        "converged": True,
        "iterations": 8,
        "fit_seconds": 1.0,
        "relativities": {
            factor: [
                {"level": level, "relativity": relativity, "estimate": 0.5}
                for level, relativity in levels
            ]
            for factor, levels in relativities.items()
        },
    }


def _run_with_database(work: Callable[[AsyncSession], Awaitable[None]]) -> None:
    """Run `work(session)` in one unit of work on a loop of our own (`TestClient` is
    blocking, so an async fixture cannot be requested from the synchronous tests below)."""
    from backend.tests.conftest_db import test_database_url

    async def _run(database: Database) -> None:
        async with database.unit_of_work() as session:
            await work(session)
            await session.flush()

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            loop.run_until_complete(_run(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()


def _insert_rows(rows: list[object]) -> None:
    """Insert rows (an approved row goes through `add_approved`)."""

    async def _insert(session: AsyncSession) -> None:
        for row in rows:
            if getattr(row, "status", None) == "approved":
                await add_approved(session, row)
            else:
                session.add(row)

    _run_with_database(_insert)


def _run_job(job_id: str) -> None:
    """Run a submitted Job to its end on a loop of our own, as the worker would (R1: a diff of a
    version pair is a Job the first time, and a read of its stored artifact after)."""
    from backend.tests.conftest_db import test_blob_bucket, test_database_url

    from app.platform.blobs import BlobStore
    from app.worker.rate_table_handlers import register_rate_table_handlers
    from app.worker.tasks import execute_job
    from model_schema import JobStatus

    register_rate_table_handlers()

    async def _run() -> None:
        database = Database(Settings(database_url=test_database_url()))
        try:
            store = BlobStore(Settings(blob_bucket=test_blob_bucket()))
            assert await execute_job(database, UUID(job_id), store) is JobStatus.SUCCEEDED
        finally:
            await database.dispose()

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_run())
    finally:
        loop.close()


def _diff_ready(api_client, url, params, headers):  # type: ignore[no-untyped-def]
    """The diff's answer: a 202 runs its Job to the end, then asks again; anything else is
    returned as it came (a 404 or 403 precedes any Job)."""
    response = api_client.get(url, params=params, headers=headers)
    if response.status_code == 202:
        _run_job(response.json()["id"])
        response = api_client.get(url, params=params, headers=headers)
    return response


async def _ensure_factor(
    session: AsyncSession, workspace_id: UUID, slug: str, version: int
) -> UUID:
    """The Factor row `slug@version` of the workspace, created once and then reused."""
    existing = await session.scalar(
        select(FactorRow).where(
            FactorRow.workspace_id == workspace_id,
            FactorRow.slug == slug,
            FactorRow.version == version,
        )
    )
    if existing is not None:
        return existing.id
    factor = Factor(
        id=new_uuid7(),
        slug=slug,
        dataset_id=new_uuid7(),
        version=version,
        type=FactorType.IDENTITY,
        source_columns=(slug,),
    )
    row = FactorRow(
        workspace_id=workspace_id,
        dataset_id=factor.dataset_id,
        slug=slug,
        version=version,
        body=factor.model_dump(mode="json", exclude={"id", "version", "dataset_id"}),
    )
    session.add(row)
    await session.flush()
    return row.id


def _seed_approved_model(
    workspace_id: UUID,
    family: str,
    relativities: dict[str, list[tuple[str, float]]],
    *,
    factor_versions: dict[str, int] | None = None,
) -> None:
    """An approved ModelRow whose fit carries the given relativities, and whose spec pins
    one Factor row per relativity entry (FR-230, `RL-1361` section D). `factor_versions`
    names the Factor version a model pins (default 1)."""

    async def _insert(session: AsyncSession) -> None:
        pinned = [
            await _ensure_factor(session, workspace_id, slug, (factor_versions or {}).get(slug, 1))
            for slug in relativities
        ]
        spec = _glm_spec(family, new_uuid7())
        spec["factors"] = [str(factor_id) for factor_id in pinned]
        await add_approved(
            session,
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug=family,
                version=1,
                status=ModelStatus.APPROVED.value,
                dataset_version_id=new_uuid7(),
                spec=spec,
                spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
                fit_result=_fit_result(relativities),
                diagnostics_id=uuid4(),
            ),
        )

    _run_with_database(_insert)


_LEVELS: dict[str, list[tuple[str, float]]] = {
    "driver_age_band": [
        ("17-20", 1.92),
        ("21-24", 1.41),
        ("25-29", 1.12),
    ]
}


def _seed_body(
    family: str,
    change_note: str = "Seeded for the W10-2 tests",
    factor: str = "driver_age_band",
) -> dict[str, object]:
    return {"model_ref": f"model:{family}@1", "factor": factor, "change_note": change_note}


def _table_slug() -> str:
    return f"motor-driver-age-{uuid4().hex[:8]}"


@pytest.mark.req("FR-230")
def test_seed_creates_version_one_with_cells(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["slug"] == slug
    assert body["version"] == 1
    assert body["rateable"] is True
    assert body["storage"] == "rows"
    assert [key["name"] for key in body["keys"]] == ["driver_age_band"]
    assert body["value"]["name"] == "relativity"
    assert body["change_note"] == "Seeded for the W10-2 tests"
    assert body["seeded_from"]["model_ref"] == f"model:{family}@1"
    assert [row["driver_age_band"] for row in body["rows"]] == [
        "17-20",
        "21-24",
        "25-29",
    ]
    assert [row["relativity"] for row in body["rows"]] == ["1.92", "1.41", "1.12"]


@pytest.mark.req("FR-230")
@pytest.mark.req("FR-231")
def test_seed_appends_the_next_version_and_diff_vs_previous(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()

    first = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert first.status_code == 201, first.text
    assert first.json()["version"] == 1

    softened = {"driver_age_band": [("17-20", 1.84), ("21-24", 1.41), ("25-29", 1.12)]}
    family_v2 = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family_v2, softened)
    second = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family_v2, change_note="Softened 17-20"),
        headers=actuary,
    )
    assert second.status_code == 201, second.text
    assert second.json()["version"] == 2

    diff = _diff_ready(

        api_client, f"/api/v1/rate-tables/{slug}@2/diff", {"against": "previous"}, actuary

    )
    assert diff.status_code == 200, diff.text
    body = diff.json()
    assert body["changed_cells"] == 1
    assert body["max_abs_change_pct"].startswith("4.166")
    assert body["exposure_weighted_mean_change_pct"] is None


@pytest.mark.req("FR-231")
def test_diff_vs_seed_compares_against_the_origin_not_the_previous_version(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """With three versions, `against=seed` answers v3-vs-v1 where
    `against=previous` answers v3-vs-v2.

    Versions 2 and 3 are **derived** (bulk operations), not re-seeds: under RL-1375 DP-1
    (a2) a re-seed starts its own seed origin, so only a derived version diffs back to v1.
    """
    slug = _table_slug()
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    created = _seed(api_client, actuary, slug, family, "driver_age_band")
    assert created.status_code == 201, created.text
    # v1 = 1.92 / 1.41 / 1.12 -> v2 = 1.84 / 1.41 / 1.20 -> v3 = 1.84 / 1.50 / 1.20
    for number, parameters in (
        (1, {"floor": "1.20", "cap": "1.84"}),
        (2, {"floor": "1.20", "cap": "1.50"}),
    ):
        derived = api_client.post(
            f"/api/v1/rate-tables/{slug}@{number}/bulk-operation",
            json=_bulk_body("floor_and_cap", parameters),
            headers=actuary,
        )
        assert derived.status_code == 201, derived.text

    vs_previous = _diff_ready(

        api_client, f"/api/v1/rate-tables/{slug}@3/diff", {"against": "previous"}, actuary

    )
    assert vs_previous.status_code == 200, vs_previous.text
    assert vs_previous.json()["changed_cells"] == 1  # 1.84 -> 1.50

    vs_seed = _diff_ready(

        api_client, f"/api/v1/rate-tables/{slug}@3/diff", {"against": "seed"}, actuary

    )
    assert vs_seed.status_code == 200, vs_seed.text
    assert vs_seed.json()["changed_cells"] == 2  # 17-20 and 25-29, from the origin


@pytest.mark.req("FR-231")
def test_diff_against_an_explicit_version(
    api_client: TestClient, workspace_id, actuary
) -> None:
    slug = _table_slug()
    softened = {"driver_age_band": [("17-20", 1.84), ("21-24", 1.41), ("25-29", 1.12)]}
    for family, relativities in (
        (f"mf-{uuid4().hex[:8]}", _LEVELS),
        (f"mf-{uuid4().hex[:8]}", softened),
    ):
        _seed_approved_model(workspace_id, family, relativities)
        created = api_client.post(
            f"/api/v1/rate-tables/{slug}/seed-from-model",
            json=_seed_body(family),
            headers=actuary,
        )
        assert created.status_code == 201, created.text

    diff = _diff_ready(

        api_client, f"/api/v1/rate-tables/{slug}@2/diff", {"against": "1"}, actuary

    )
    assert diff.status_code == 200, diff.text
    assert diff.json()["changed_cells"] == 1


@pytest.mark.req("FR-230")
def test_seed_refuses_a_non_approved_model(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _insert_rows(
        [
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug=family,
                version=1,
                status=ModelStatus.FITTED.value,
                dataset_version_id=new_uuid7(),
                spec=_glm_spec(family, new_uuid7()),
                spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
                fit_result=_fit_result(_LEVELS),
                diagnostics_id=uuid4(),
            )
        ]
    )

    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "PIN_NOT_APPROVED"


@pytest.mark.req("FR-230")
def test_seed_refuses_a_missing_model(
    api_client: TestClient, workspace_id, actuary
) -> None:
    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json=_seed_body(f"missing-{uuid4().hex[:8]}"),
        headers=actuary,
    )
    assert response.status_code == 404, response.text


@pytest.mark.req("FR-229")
@pytest.mark.req("FR-230")
def test_seed_refuses_a_bad_body(api_client: TestClient, workspace_id, actuary) -> None:
    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json={"model_ref": "not-a-ref", "change_note": "x"},
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"

    missing_note = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json={"model_ref": "model:whatever@1"},
        headers=actuary,
    )
    assert missing_note.status_code == 422, missing_note.text

    wrong_type = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json={"model_ref": "rating_algorithm:whatever@1", "change_note": "x"},
        headers=actuary,
    )
    assert wrong_type.status_code == 422, wrong_type.text


@pytest.mark.req("FR-234")
def test_seed_validation_failure_is_named(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """A model whose relativities repeat a level is refused with the named code —
    the plan's DUPLICATE_KEY maps onto 03 §5.2's RATE_TABLE_KEY_DUPLICATE."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(
        workspace_id, family, {"driver_age_band": [("17-20", 1.92), ("17-20", 1.50)]}
    )

    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "RATE_TABLE_KEY_DUPLICATE"


@pytest.mark.req("FR-231")
def test_diff_404s_for_unknown_table_and_version(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()
    created = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert created.status_code == 201, created.text

    missing_table = api_client.get(
        f"/api/v1/rate-tables/{_table_slug()}@1/diff",
        params={"against": "previous"},
        headers=actuary,
    )
    assert missing_table.status_code == 404, missing_table.text
    assert missing_table.json()["code"] == "RATE_TABLE_MISS"

    missing_version = _diff_ready(

        api_client, f"/api/v1/rate-tables/{slug}@9/diff", {"against": "previous"}, actuary

    )
    assert missing_version.status_code == 404, missing_version.text

    no_previous = _diff_ready(

        api_client, f"/api/v1/rate-tables/{slug}@1/diff", {"against": "previous"}, actuary

    )
    assert no_previous.status_code == 404, no_previous.text


@pytest.mark.req("FR-231")
def test_diff_rejects_an_unknown_baseline(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()
    created = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert created.status_code == 201, created.text

    response = _diff_ready(

        api_client, f"/api/v1/rate-tables/{slug}@1/diff", {"against": "banana"}, actuary

    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-231")
def test_diff_seed_without_a_seed_origin_404s(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """`against=seed` resolves the baseline from the `seeded_from` trail; a version
    carrying no trail (direct inserts — the only creation path in this slice always
    pins a seed origin) answers 404 RATE_TABLE_MISS."""
    slug = _table_slug()
    table_row = RateTableRow(
        workspace_id=workspace_id,
        slug=slug,
        current_version=1,
        created_by=uuid4(),
    )
    _insert_rows([table_row])
    _insert_rows(
        [
            RateTableVersionRow(
                workspace_id=workspace_id,
                rate_table_id=table_row.id,
                version_number=1,
                storage="rows",
                definition={
                    "slug": slug,
                    "version": 1,
                    "rateable": True,
                    "storage": "rows",
                    "keys": [
                        {
                            "name": "driver_age_band",
                            "type": "string",
                            "banding_ref": None,
                        }
                    ],
                    "value": {
                        "name": "relativity",
                        "type": "relativity",
                        "unit": "factor",
                        "min": None,
                        "max": None,
                    },
                    "default_row": None,
                },
                change_note="unseeded probe",
                created_by=uuid4(),
            ),
        ]
    )

    response = _diff_ready(

        api_client, f"/api/v1/rate-tables/{slug}@1/diff", {"against": "seed"}, actuary

    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "RATE_TABLE_MISS"


@pytest.mark.req("FR-232")
def test_a_diff_touching_a_parquet_version_answers_202_with_a_job(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """03 §5.1: where either version is `storage: parquet` the diff answers 202 with a
    Job on the compute queue (FR-232) — the same artifact the row-backed 200
    returns, only latency and status differ (FR-231)."""
    slug = _table_slug()
    definition = {
        "slug": slug,
        "version": 1,
        "rateable": True,
        "storage": "rows",
        "keys": [
            {
                "name": "driver_age_band",
                "type": "string",
                "banding_ref": None,
            }
        ],
        "value": {
            "name": "relativity",
            "type": "relativity",
            "unit": "factor",
            "min": None,
            "max": None,
        },
        "default_row": None,
    }
    _insert_rows(
        [
            RateTableRow(
                workspace_id=workspace_id,
                slug=slug,
                current_version=2,
                created_by=uuid4(),
            )
        ]
    )

    async def _add_parquet_version(database: Database) -> None:
        async with database.unit_of_work() as session:
            table_row = (
                await session.execute(
                    select(RateTableRow).where(
                        RateTableRow.workspace_id == workspace_id,
                        RateTableRow.slug == slug,
                    )
                )
            ).scalar_one()
            session.add(
                RateTableVersionRow(
                    workspace_id=workspace_id,
                    rate_table_id=table_row.id,
                    version_number=1,
                    storage="rows",
                    definition=definition,
                    change_note="rows baseline",
                    created_by=uuid4(),
                )
            )
            session.add(
                RateTableVersionRow(
                    workspace_id=workspace_id,
                    rate_table_id=table_row.id,
                    version_number=2,
                    storage="parquet",
                    definition={**definition, "version": 2, "storage": "parquet"},
                    change_note="parquet probe",
                    created_by=uuid4(),
                )
            )
            await session.flush()

    from backend.tests.conftest_db import test_database_url

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            loop.run_until_complete(_add_parquet_version(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()

    response = api_client.get(
        f"/api/v1/rate-tables/{slug}@2/diff", params={"against": "previous"}, headers=actuary
    )
    assert response.status_code == 202, response.text
    job = response.json()
    assert job["kind"] == "rate_table.diff_cells"
    assert job["queue"] == "compute"
    assert job["status"] == "queued"
    assert job["parameters"]["slug"] == slug
    assert job["parameters"]["version"] == 2
    assert job["parameters"]["against"] == "previous"
    assert response.headers["location"] == f"/api/v1/jobs/{job['id']}"


@pytest.mark.req("FR-450")
def test_routes_are_permission_gated(
    api_client: TestClient, workspace_id, principal, auditor_headers, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()

    anon_seed = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
    )
    assert anon_seed.status_code == 401, anon_seed.text

    read_only_seed = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=auditor_headers,
    )
    assert read_only_seed.status_code == 403, read_only_seed.text

    created = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert created.status_code == 201, created.text

    anon_diff = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/diff",
        params={"against": "previous"},
    )
    assert anon_diff.status_code == 401, anon_diff.text

    # Version 1 has no `previous` (that diff is a 404, asserted in the 404s test); the seed
    # origin is version 1 itself, so this answers 200 with zero changes (after its Job).
    read_only_diff = _diff_ready(
        api_client, f"/api/v1/rate-tables/{slug}@1/diff", {"against": "seed"}, auditor_headers
    )
    assert read_only_diff.status_code == 200, read_only_diff.text

    anon_operation = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/bulk-operation",
        json=_bulk_body("uplift_table", {"percentage": "0.10"}),
    )
    assert anon_operation.status_code == 401, anon_operation.text

    read_only_operation = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/bulk-operation",
        json=_bulk_body("uplift_table", {"percentage": "0.10"}),
        headers=auditor_headers,
    )
    assert read_only_operation.status_code == 403, read_only_operation.text

    anon_export = api_client.get(f"/api/v1/rate-tables/{slug}@1/export/csv")
    assert anon_export.status_code == 401, anon_export.text

    read_only_export = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/csv",
        headers=auditor_headers,
    )
    assert read_only_export.status_code == 200, read_only_export.text

    anon_import = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": ("import.csv", b"driver_age_band,relativity\n17-20,1.92\n", "text/csv")},
    )
    assert anon_import.status_code == 401, anon_import.text

    read_only_import = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": ("import.csv", b"driver_age_band,relativity\n17-20,1.92\n", "text/csv")},
        headers=auditor_headers,
    )
    assert read_only_import.status_code == 403, read_only_import.text


def _bulk_body(kind: str, parameters: dict[str, object]) -> dict[str, object]:
    return {"kind": kind, "parameters": parameters}


@pytest.mark.req("FR-233")
def test_bulk_operation_creates_a_new_version_with_the_operation_record(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()
    seeded = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert seeded.status_code == 201, seeded.text

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/bulk-operation",
        json=_bulk_body("uplift_table", {"percentage": "0.10"}),
        headers=actuary,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["version"] == 2
    assert body["storage"] == "rows"
    assert [row["relativity"] for row in body["rows"]] == ["2.112", "1.551", "1.232"]
    operation = body["created_by_operation"]
    assert operation["kind"] == "uplift_table"
    assert operation["parameters"] == {"percentage": "0.10"}
    assert operation["applied_to"] == f"rate_table:{slug}@1"
    assert operation["result"] == {
        "changed_cells": 3,
        "new_version": f"rate_table:{slug}@2",
    }
    assert body["created_by_import"] is None
    assert body["seeded_from"]["model_ref"] == f"model:{family}@1"


@pytest.mark.req("FR-233")
def test_bulk_operation_refuses_an_unknown_kind(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()
    seeded = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert seeded.status_code == 201, seeded.text

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/bulk-operation",
        json=_bulk_body("lift_everything", {}),
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-233")
def test_bulk_operation_refuses_floor_above_cap(
    api_client: TestClient, workspace_id, actuary
) -> None:
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()
    seeded = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert seeded.status_code == 201, seeded.text

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/bulk-operation",
        json=_bulk_body("floor_and_cap", {"floor": "2.0", "cap": "1.0"}),
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "FLOOR_ABOVE_CAP"


@pytest.mark.req("FR-233")
def test_bulk_operation_on_a_missing_version_is_refused(
    api_client: TestClient, workspace_id, actuary
) -> None:
    slug = _table_slug()
    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/bulk-operation",
        json=_bulk_body("uplift_table", {"percentage": "0.10"}),
        headers=actuary,
    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "RATE_TABLE_MISS"


def _set_threshold(
    api_client: TestClient, admin_headers: dict[str, str], value: int
) -> None:
    """The workspace cell-count threshold through the settings API (FR-232)."""
    response = api_client.put(
        "/api/v1/settings",
        json={"values": {"rate_tables.cell_threshold": value}},
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text


def _seeded_table(
    api_client: TestClient, workspace_id, actuary
) -> tuple[str, str]:
    """Seed a table and return (slug, family) — the W10-3C test shorthand."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _LEVELS)
    slug = _table_slug()
    seeded = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert seeded.status_code == 201, seeded.text
    return slug, family


@pytest.mark.req("FR-235")
def test_export_csv_returns_the_seeded_cells(
    api_client: TestClient, workspace_id, actuary
) -> None:
    slug, _ = _seeded_table(api_client, workspace_id, actuary)

    response = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/csv",
        headers=actuary,
    )

    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/csv")
    assert response.content == (
        b"driver_age_band,relativity\n"
        b"17-20,1.92\n"
        b"21-24,1.41\n"
        b"25-29,1.12\n"
    )


@pytest.mark.req("FR-235")
def test_export_xlsx_parses_to_the_seeded_cells(
    api_client: TestClient, workspace_id, actuary
) -> None:
    slug, _ = _seeded_table(api_client, workspace_id, actuary)

    response = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/xlsx",
        headers=actuary,
    )

    assert response.status_code == 200, response.text
    workbook = load_workbook(io.BytesIO(response.content), read_only=True)
    sheet = workbook.active
    assert [row for row in sheet.iter_rows(values_only=True)] == [
        ("driver_age_band", "relativity"),
        ("17-20", "1.92"),
        ("21-24", "1.41"),
        ("25-29", "1.12"),
    ]


@pytest.mark.req("FR-235")
def test_import_previews_a_modified_export(
    api_client: TestClient, workspace_id, actuary
) -> None:
    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    exported = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/csv",
        headers=actuary,
    )
    assert exported.status_code == 200, exported.text
    modified = exported.content.replace(b"21-24,1.41", b"21-24,1.4500")

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": ("import.csv", modified, "text/csv")},
        headers=actuary,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["diff"]["changed_cells"] == 1
    verdict = body["created_by_import"]
    assert verdict["filename"] == "import.csv"
    assert verdict["content_sha256"] == hashlib.sha256(modified).hexdigest()
    assert verdict["round_trip"] == "passed"
    assert verdict["applied_to"] == f"rate_table:{slug}@1"


@pytest.mark.req("FR-235")
def test_import_preview_creates_nothing(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """DP6: without `confirm` the request is a strict preview — no version is made."""
    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    exported = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/csv",
        headers=actuary,
    )
    assert exported.status_code == 200, exported.text

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": ("import.csv", exported.content, "text/csv")},
        headers=actuary,
    )
    assert response.status_code == 200, response.text

    missing = _diff_ready(

        api_client, f"/api/v1/rate-tables/{slug}@2/diff", {"against": "previous"}, actuary

    )
    assert missing.status_code == 404
    assert missing.json()["code"] == "RATE_TABLE_MISS"


@pytest.mark.req("FR-235")
def test_import_confirm_creates_the_version(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """DP6: `confirm: true` re-parses the same upload and creates the version."""
    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    exported = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/csv",
        headers=actuary,
    )
    assert exported.status_code == 200, exported.text
    modified = exported.content.replace(b"21-24,1.41", b"21-24,1.4500")

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": ("import.csv", modified, "text/csv")},
        data={"confirm": "true"},
        headers=actuary,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["version"] == 2
    assert body["created_by_operation"] is None
    verdict = body["created_by_import"]
    assert verdict is not None
    assert verdict["filename"] == "import.csv"
    assert verdict["content_sha256"] == hashlib.sha256(modified).hexdigest()
    assert verdict["round_trip"] == "passed"
    assert verdict["applied_to"] == f"rate_table:{slug}@1"

    exported_v2 = api_client.get(
        f"/api/v1/rate-tables/{slug}@2/export/csv",
        headers=actuary,
    )
    assert exported_v2.status_code == 200, exported_v2.text
    assert b"21-24,1.4500" in exported_v2.content


@pytest.mark.req("FR-235")
def test_import_confirm_cannot_override_the_verdict(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """DP6: confirmation reruns the strict round-trip — a verdict violation on the
    preview stays a refusal on the confirm, and nothing is created."""
    slug, _ = _seeded_table(api_client, workspace_id, actuary)

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": ("import.csv", b"vehicle_age_band,relativity\n17-20,1.92\n", "text/csv")},
        data={"confirm": "true"},
        headers=actuary,
    )

    assert response.status_code == 422, response.text
    assert response.json()["code"] == "IMPORT_KEY_MISMATCH"
    missing = _diff_ready(
        api_client, f"/api/v1/rate-tables/{slug}@2/diff", {"against": "previous"}, actuary
    )
    assert missing.status_code == 404
    assert missing.json()["code"] == "RATE_TABLE_MISS"


@pytest.mark.req("FR-232")
@pytest.mark.req("FR-235")
def test_import_confirm_on_a_parquet_baseline_spills(
    api_client: TestClient, workspace_id, actuary, admin_headers
) -> None:
    """DP2: the confirmed version obeys the workspace threshold like any other."""
    _set_threshold(api_client, admin_headers, 2)
    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    exported = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/csv",
        headers=actuary,
    )
    assert exported.status_code == 200, exported.text

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": ("import.csv", exported.content, "text/csv")},
        data={"confirm": "true"},
        headers=actuary,
    )

    assert response.status_code == 201, response.text
    assert response.json()["storage"] == "parquet"
    assert response.json()["rows"] is None
    assert response.json()["cells"]["media_type"] == "application/parquet"


@pytest.mark.req("FR-235")
def test_import_refuses_an_oversized_filename(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """DP5: the verdict's filename is bounded — it is a record, never a path."""
    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    exported = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/csv",
        headers=actuary,
    )
    assert exported.status_code == 200, exported.text

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": (f"{'a' * 256}.csv", exported.content, "text/csv")},
        headers=actuary,
    )

    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-235")
def test_import_refuses_a_wrong_header(
    api_client: TestClient, workspace_id, actuary
) -> None:
    slug, _ = _seeded_table(api_client, workspace_id, actuary)

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": ("import.csv", b"vehicle_age_band,relativity\n17-20,1.92\n", "text/csv")},
        headers=actuary,
    )

    assert response.status_code == 422, response.text
    assert response.json()["code"] == "IMPORT_KEY_MISMATCH"


@pytest.mark.req("FR-232")
@pytest.mark.req("FR-235")
def test_export_reads_a_parquet_version_inline(
    api_client: TestClient, workspace_id, actuary, admin_headers
) -> None:
    """Above the threshold the version lives as a parquet blob; export materialises
    the cells from it — the Job-worthy read is the diff (W10-3D), not an export."""
    _set_threshold(api_client, admin_headers, 2)
    slug, _ = _seeded_table(api_client, workspace_id, actuary)

    response = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/csv",
        headers=actuary,
    )

    assert response.status_code == 200, response.text
    assert response.content == (
        b"driver_age_band,relativity\n"
        b"17-20,1.92\n"
        b"21-24,1.41\n"
        b"25-29,1.12\n"
    )


@pytest.mark.req("FR-232")
@pytest.mark.req("FR-235")
def test_import_diffs_against_a_parquet_baseline(
    api_client: TestClient, workspace_id, actuary, admin_headers
) -> None:
    _set_threshold(api_client, admin_headers, 2)
    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    exported = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/export/csv",
        headers=actuary,
    )
    assert exported.status_code == 200, exported.text
    modified = exported.content.replace(b"21-24,1.41", b"21-24,1.4500")

    response = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/import",
        files={"file": ("import.csv", modified, "text/csv")},
        headers=actuary,
    )

    assert response.status_code == 200, response.text
    assert response.json()["diff"]["changed_cells"] == 1


# --- WK-1178 SL-1377 (PL-1376, RL-1361, RL-1375, RL-1383, FD-1357): one seeded table per Factor --

_TWO_FACTORS: dict[str, list[tuple[str, float]]] = {
    "driver_age_band": [("17-20", 1.92), ("21-24", 1.41), ("25-29", 1.12)],
    "region": [("north", 1.30), ("south", 0.90)],
}


def _seed(
    api_client: TestClient, actuary, slug: str, family: str, factor: str, note: str = "seed"
):  # type: ignore[no-untyped-def]
    return api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family, change_note=note, factor=factor),
        headers=actuary,
    )


def _insert_table(
    workspace_id: UUID, slug: str, keys: list[dict[str, object]]
) -> None:
    """A one-version table inserted directly (no seed origin), with the given key
    declarations: the shapes RL-1375 DP-2 must refuse or accept."""
    table_row = RateTableRow(
        workspace_id=workspace_id, slug=slug, current_version=1, created_by=uuid4()
    )
    _insert_rows([table_row])
    _insert_rows(
        [
            RateTableVersionRow(
                workspace_id=workspace_id,
                rate_table_id=table_row.id,
                version_number=1,
                storage="rows",
                definition={
                    "slug": slug,
                    "version": 1,
                    "rateable": True,
                    "storage": "rows",
                    "keys": keys,
                    "value": {
                        "name": "relativity",
                        "type": "relativity",
                        "unit": "factor",
                        "min": None,
                        "max": None,
                    },
                    "default_row": None,
                },
                change_note="direct insert",
                created_by=uuid4(),
            )
        ]
    )


@pytest.mark.req("FR-230")
def test_a_two_factor_model_seeds_one_table_per_factor(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """The FD-1357 red: a two-factor model used to answer 500 (`KeyError`)."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _TWO_FACTORS)
    age_slug, region_slug = _table_slug(), _table_slug()

    age = _seed(api_client, actuary, age_slug, family, "driver_age_band")
    region = _seed(api_client, actuary, region_slug, family, "region")

    assert age.status_code == 201, age.text
    assert region.status_code == 201, region.text
    assert [key["name"] for key in age.json()["keys"]] == ["driver_age_band"]
    assert {row["driver_age_band"] for row in age.json()["rows"]} == {"17-20", "21-24", "25-29"}
    assert [key["name"] for key in region.json()["keys"]] == ["region"]
    assert {row["region"] for row in region.json()["rows"]} == {"north", "south"}
    assert age.json()["keys"][0]["factor_ref"] == "factor:driver_age_band@1"
    assert region.json()["keys"][0]["factor_ref"] == "factor:region@1"


@pytest.mark.req("FR-230")
def test_a_factor_that_names_no_relativity_entry_is_a_422(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """3(a) and 3(b): a continuous factor has no relativity entry, so it is this refusal."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _TWO_FACTORS)
    ok = _seed(api_client, actuary, _table_slug(), family, "region")  # positive control
    assert ok.status_code == 201, ok.text
    for factor in ("driver_age", "vehicle_age"):
        response = _seed(api_client, actuary, _table_slug(), family, factor)
        assert response.status_code == 422, response.text
        assert response.json()["code"] == "VALIDATION_FAILED"
        assert factor in response.text


@pytest.mark.req("FR-230")
def test_a_model_factor_id_that_resolves_nowhere_is_a_404(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """3(f): `load_factors` raises, and the seed never falls back to an empty list."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, {"region": _TWO_FACTORS["region"]})
    ok = _seed(api_client, actuary, _table_slug(), family, "region")  # positive control
    assert ok.status_code == 201, ok.text

    dangling = f"mf-{uuid4().hex[:8]}"
    _insert_rows(
        [
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug=dangling,
                version=1,
                status=ModelStatus.APPROVED.value,
                dataset_version_id=new_uuid7(),
                spec={**_glm_spec(dangling, new_uuid7()), "factors": [str(uuid4())]},
                spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
                fit_result=_fit_result({"region": _TWO_FACTORS["region"]}),
                diagnostics_id=uuid4(),
            )
        ]
    )
    response = _seed(api_client, actuary, _table_slug(), dangling, "region")
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-230")
def test_approval_is_checked_before_the_factors_are_loaded(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """The refusal order (PL-1376 Task 3): a non-approved model whose spec pins an id that
    resolves nowhere is 422 `PIN_NOT_APPROVED`, not 404."""
    family = f"mf-{uuid4().hex[:8]}"
    _insert_rows(
        [
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug=family,
                version=1,
                status=ModelStatus.FITTED.value,
                dataset_version_id=new_uuid7(),
                spec={**_glm_spec(family, new_uuid7()), "factors": [str(uuid4())]},
                spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
                fit_result=_fit_result(_LEVELS),
                diagnostics_id=uuid4(),
            )
        ]
    )
    response = _seed(api_client, actuary, _table_slug(), family, "driver_age_band")
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "PIN_NOT_APPROVED"


@pytest.mark.req("FR-230")
@pytest.mark.parametrize(
    "keys",
    [
        # a one-key table bound by `factor_ref` to another Factor's slug
        [{"name": "region", "type": "string", "factor_ref": "factor:region@1"}],
        # a one-key unbound table with another name
        [{"name": "region", "type": "string", "banding_ref": None}],
        # a one-key table bound by `banding_ref`
        [
            {
                "name": "driver_age_band",
                "type": "string",
                "banding_ref": "banding:driver-age-actuarial-v2@2",
            }
        ],
        # a two-key table, unbound
        [
            {"name": "driver_age_band", "type": "string", "banding_ref": None},
            {"name": "region", "type": "string", "banding_ref": None},
        ],
    ],
    ids=["bound-to-other-factor", "unbound-other-name", "banding-ref", "two-keys"],
)
def test_a_seed_into_a_table_the_rule_refuses_is_a_422_naming_it(
    api_client: TestClient, workspace_id, actuary, keys: list[dict[str, object]]
) -> None:
    """RL-1375 DP-2: a seed of `driver_age_band` into an existing table is accepted only
    for one key bound to that Factor or an unbound one named after it."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _TWO_FACTORS)
    slug = _table_slug()
    _insert_table(workspace_id, slug, keys)

    response = _seed(api_client, actuary, slug, family, "driver_age_band")

    assert response.status_code == 422, response.text
    body = response.json()
    assert body["code"] == "VALIDATION_FAILED"
    assert slug in body["detail"]
    assert all(key["name"] in body["detail"] for key in keys)


@pytest.mark.req("FR-230")
@pytest.mark.parametrize(
    "key",
    [
        {"name": "driver_age_band", "type": "string", "banding_ref": None},
        {"name": "driver_age_band", "type": "string", "factor_ref": "factor:driver_age_band@7"},
    ],
    ids=["unbound-same-name", "bound-to-same-slug"],
)
def test_a_seed_into_a_table_the_rule_accepts_binds_the_key(
    api_client: TestClient, workspace_id, actuary, key: dict[str, object]
) -> None:
    """RL-1375 DP-2 (e'): the new version's one key carries `factor_ref` to the pinned
    Factor version (here 1), in both accepted shapes."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _TWO_FACTORS)
    slug = _table_slug()
    _insert_table(workspace_id, slug, [key])

    response = _seed(api_client, actuary, slug, family, "driver_age_band")

    assert response.status_code == 201, response.text
    assert response.json()["version"] == 2
    assert [k["name"] for k in response.json()["keys"]] == ["driver_age_band"]
    assert response.json()["keys"][0]["factor_ref"] == "factor:driver_age_band@1"


@pytest.mark.req("FR-230")
def test_a_reseed_with_a_newer_version_of_the_same_factor_is_accepted(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """RL-1361 section A; and RL-1383's Acceptance 19 (an underscore slug re-seeds): model
    v2 pins version 2 of the Factor that v1 pinned at version 1."""
    slug = _table_slug()
    first, second = f"mf-{uuid4().hex[:8]}", f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, first, _TWO_FACTORS)
    _seed_approved_model(workspace_id, second, _TWO_FACTORS, factor_versions={"driver_age_band": 2})

    one = _seed(api_client, actuary, slug, first, "driver_age_band")
    assert one.status_code == 201, one.text
    assert one.json()["keys"][0]["factor_ref"] == "factor:driver_age_band@1"
    exported = api_client.get(f"/api/v1/rate-tables/{slug}@1/export/csv", headers=actuary)
    assert exported.status_code == 200, exported.text  # re-reads the stored definition

    two = _seed(api_client, actuary, slug, second, "driver_age_band")
    assert two.status_code == 201, two.text
    assert two.json()["version"] == 2
    assert two.json()["keys"][0]["factor_ref"] == "factor:driver_age_band@2"


@pytest.mark.req("FR-230")
def test_a_factor_outside_the_factor_slug_grammar_is_a_422_naming_the_slug(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """RL-1383 Ruled item 3 (Acceptance 19): `Region` is a slug `Factor` accepts today
    (FD-1384) and a reference cannot hold; the seed refuses it by name, never a 500."""
    family = f"mf-{uuid4().hex[:8]}"
    ok_family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, ok_family, {"veh_brand": [("a", 1.1), ("b", 0.9)]})
    ok = _seed(api_client, actuary, _table_slug(), ok_family, "veh_brand")  # positive control
    assert ok.status_code == 201, ok.text
    assert ok.json()["keys"][0]["factor_ref"] == "factor:veh_brand@1"

    _seed_approved_model(workspace_id, family, {"Region": [("n", 1.1), ("s", 0.9)]})
    response = _seed(api_client, actuary, _table_slug(), family, "Region")
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"
    assert "Region" in response.json()["detail"]


@pytest.mark.req("FR-230")
@pytest.mark.req("FR-451")
def test_the_seed_route_publishes_a_typed_request_and_201(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """Acceptance 6 and 7: both shapes are generated `model-schema` components."""
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    document = json.loads((root / "docs/contracts/openapi/generated.json").read_text())
    operation = document["paths"]["/api/v1/rate-tables/{slug}/seed-from-model"]["post"]
    request_schema = operation["requestBody"]["content"]["application/json"]["schema"]
    assert request_schema == {"$ref": "#/components/schemas/SeedFromModelRequest"}
    created = operation["responses"]["201"]["content"]["application/json"]["schema"]
    assert created == {"$ref": "#/components/schemas/RateTableVersion"}
    generated = root / "docs/contracts/schemas/generated"
    assert (generated / "seed-from-model-request.schema.json").is_file()
    assert (generated / "rate-table-version.schema.json").is_file()

    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _TWO_FACTORS)
    ok = _seed(api_client, actuary, _table_slug(), family, "region")  # positive control
    assert ok.status_code == 201, ok.text
    no_factor = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json={"model_ref": f"model:{family}@1", "change_note": "seed"},
        headers=actuary,
    )
    assert no_factor.status_code == 422, no_factor.text
    assert no_factor.json()["code"] == "VALIDATION_FAILED"
    assert any("factor" in str(error) for error in no_factor.json()["errors"])


@pytest.mark.req("FR-230")
@pytest.mark.req("FR-229")
@pytest.mark.parametrize(
    "patch",
    [
        {"change_note": "   "},
        {"model_ref": "rating_algorithm:motor-rating@1"},
        {"factor": ""},
        {"rateable": True},
    ],
    ids=["blank-note", "non-model-ref", "empty-factor", "unknown-field"],
)
def test_the_seed_request_refusals_are_422_with_a_field_error(
    api_client: TestClient, workspace_id, actuary, patch: dict[str, object]
) -> None:
    """6b: each of the request's own refusals is 422 `VALIDATION_FAILED`."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _TWO_FACTORS)
    body = {"model_ref": f"model:{family}@1", "factor": "region", "change_note": "seed"}
    ok = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model", json=body, headers=actuary
    )
    assert ok.status_code == 201, ok.text  # positive control
    response = api_client.post(
        f"/api/v1/rate-tables/{_table_slug()}/seed-from-model",
        json={**body, **patch},
        headers=actuary,
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"
    assert response.json()["errors"]


@pytest.mark.req("FR-230")
@pytest.mark.req("FR-231")
def test_against_seed_resolves_to_the_versions_own_seed_origin(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """RL-1375 DP-1 (a2): seed v1 (model A), derive v2, re-seed v3 (model B), derive v4.
    `against=seed` on `@4` is v3 and on `@2` is v1; v3's `seeded_from` names model B."""
    slug = _table_slug()
    model_a, model_b = f"mf-{uuid4().hex[:8]}", f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, model_a, _LEVELS)
    softened = {"driver_age_band": [("17-20", 1.84), ("21-24", 1.41), ("25-29", 1.12)]}
    _seed_approved_model(workspace_id, model_b, softened)

    assert _seed(api_client, actuary, slug, model_a, "driver_age_band").status_code == 201
    derive_2 = api_client.post(
        f"/api/v1/rate-tables/{slug}@1/bulk-operation",
        json=_bulk_body("floor_and_cap", {"floor": "1.20", "cap": "1.84"}),
        headers=actuary,
    )
    assert derive_2.status_code == 201, derive_2.text
    reseed = _seed(api_client, actuary, slug, model_b, "driver_age_band")
    assert reseed.status_code == 201, reseed.text
    assert reseed.json()["version"] == 3
    assert reseed.json()["seeded_from"]["model_ref"] == f"model:{model_b}@1"
    derive_4 = api_client.post(
        f"/api/v1/rate-tables/{slug}@3/bulk-operation",
        json=_bulk_body("floor_and_cap", {"floor": "1.20", "cap": "1.50"}),
        headers=actuary,
    )
    assert derive_4.status_code == 201, derive_4.text
    assert derive_4.json()["version"] == 4

    # `@4` against its seed origin (v3, 1.84/1.41/1.12) differs in 17-20 and 25-29 only;
    # against the first seed (v1) every cell it left alone would also differ from v1's.
    vs_origin = _diff_ready(
        api_client, f"/api/v1/rate-tables/{slug}@4/diff", {"against": "seed"}, actuary
    )
    assert vs_origin.status_code == 200, vs_origin.text
    vs_v3 = _diff_ready(
        api_client, f"/api/v1/rate-tables/{slug}@4/diff", {"against": "3"}, actuary
    )
    assert vs_origin.json()["changed_cells"] == vs_v3.json()["changed_cells"]
    vs_v1 = _diff_ready(
        api_client, f"/api/v1/rate-tables/{slug}@4/diff", {"against": "1"}, actuary
    )
    assert vs_origin.json() != vs_v1.json()
    on_v2 = _diff_ready(
        api_client, f"/api/v1/rate-tables/{slug}@2/diff", {"against": "seed"}, actuary
    )
    on_v2_vs_v1 = _diff_ready(
        api_client, f"/api/v1/rate-tables/{slug}@2/diff", {"against": "1"}, actuary
    )
    assert on_v2.status_code == 200, on_v2.text
    assert on_v2.json()["changed_cells"] == on_v2_vs_v1.json()["changed_cells"]


# -- the definition and cell-page reads (FR 9940, FR-232; RL-1475 items 2 and 3) -------------

_MIXED_LEVELS: dict[str, list[tuple[str, float]]] = {
    "driver_age_band": [("B", 1.0), ("a", 1.1), ("10", 1.2), ("9", 1.3)]
}
#: Code-point order, per key column, compared as strings (RL-1475 item 2): `"10"` before `"9"`,
#: and `"B"` before `"a"`. Written out so no sort in the test can agree with a wrong one.
_EXPECTED_ORDER = ["10", "9", "B", "a"]


def _seed_mixed_table(api_client: TestClient, workspace_id, actuary) -> str:
    """Seed the mixed-level table as version 1 and return its slug."""
    family = f"mf-{uuid4().hex[:8]}"
    _seed_approved_model(workspace_id, family, _MIXED_LEVELS)
    slug = _table_slug()
    seeded = api_client.post(
        f"/api/v1/rate-tables/{slug}/seed-from-model",
        json=_seed_body(family),
        headers=actuary,
    )
    assert seeded.status_code == 201, seeded.text
    return slug


def _all_pages(
    api_client: TestClient, slug: str, headers: dict[str, str], limit: int
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    cursor: str | None = None
    while True:
        params: dict[str, object] = {"limit": limit} | ({"cursor": cursor} if cursor else {})
        response = api_client.get(
            f"/api/v1/rate-tables/{slug}@1/cells", params=params, headers=headers
        )
        assert response.status_code == 200, response.text
        items += response.json()["items"]
        cursor = response.json()["next_cursor"]
        if cursor is None:
            return items


def _job_count() -> int:
    from sqlalchemy import func

    from app.db.models import JobRow

    counted: list[int] = []

    async def _count(session: AsyncSession) -> None:
        counted.append(await session.scalar(select(func.count()).select_from(JobRow)) or 0)

    _run_with_database(_count)
    return counted[0]


@pytest.mark.req("FR-9940")
def test_definition_read_carries_no_cells(
    api_client: TestClient, workspace_id, actuary
) -> None:
    from model_schema.rating import RateTable

    slug = _seed_mixed_table(api_client, workspace_id, actuary)

    response = api_client.get(f"/api/v1/rate-tables/{slug}@1", headers=actuary)

    assert response.status_code == 200, response.text
    body = response.json()
    assert "rows" not in body
    assert "cells" not in body
    assert RateTable.model_validate(body).slug == slug


@pytest.mark.req("FR-232")
def test_cell_pages_agree_across_storages_in_key_order(
    api_client: TestClient, workspace_id, actuary, admin_headers
) -> None:
    jobs_before = _job_count()
    rows_slug = _seed_mixed_table(api_client, workspace_id, actuary)
    _set_threshold(api_client, admin_headers, 2)  # the next version spills to parquet
    parquet_slug = _seed_mixed_table(api_client, workspace_id, actuary)
    definition = api_client.get(f"/api/v1/rate-tables/{parquet_slug}@1", headers=actuary).json()
    assert definition["storage"] == "parquet"

    rows_order = [row["driver_age_band"] for row in _all_pages(api_client, rows_slug, actuary, 2)]
    parquet_order = [
        row["driver_age_band"] for row in _all_pages(api_client, parquet_slug, actuary, 2)
    ]

    assert rows_order == parquet_order == _EXPECTED_ORDER
    assert _job_count() == jobs_before


@pytest.mark.req("FR-232")
def test_cell_paging_concatenates_and_refuses_a_bad_cursor_or_limit(
    api_client: TestClient, workspace_id, actuary
) -> None:
    slug = _seed_mixed_table(api_client, workspace_id, actuary)

    one_by_one = _all_pages(api_client, slug, actuary, 1)
    whole = _all_pages(api_client, slug, actuary, 200)
    assert one_by_one == whole
    assert len({row["driver_age_band"] for row in whole}) == len(whole) == 4

    bad_cursor = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/cells", params={"cursor": "not-a-cursor"}, headers=actuary
    )
    assert bad_cursor.status_code == 400, bad_cursor.text
    assert bad_cursor.json()["code"] == "VALIDATION_FAILED"
    too_many = api_client.get(
        f"/api/v1/rate-tables/{slug}@1/cells", params={"limit": 201}, headers=actuary
    )
    assert too_many.status_code == 422, too_many.text


@pytest.mark.req("FR-9940")
def test_rate_table_isolation_another_workspace_answers_404(
    api_client: TestClient, workspace_id, actuary
) -> None:
    from app.platform import workspaces

    foreign = uuid4()
    slug = _table_slug()

    async def _insert(session: AsyncSession) -> None:
        await workspaces.ensure_workspace(session, workspace_id=foreign)

    _run_with_database(_insert)
    _insert_table(foreign, slug, [{"name": "driver_age_band", "type": "string"}])

    for path in (f"/api/v1/rate-tables/{slug}@1", f"/api/v1/rate-tables/{slug}@1/cells"):
        response = api_client.get(path, headers=actuary)
        assert response.status_code == 404, response.text
        assert response.json()["code"] == "RATE_TABLE_MISS"


@pytest.mark.req("FR-232")
def test_cells_bound_a_rows_page_loads_at_most_the_threshold(
    api_client: TestClient, workspace_id, actuary, admin_headers, monkeypatch
) -> None:
    """FR-232's bound under test: a rows-stored page loads the version's cells (at most its
    count, which is at most the workspace threshold, 250 000 by default); a parquet version
    reads its blob once per page."""
    from app.platform import rate_tables as service
    from app.platform.blobs import BlobStore

    loaded: list[int] = []
    real_load = service._load_cells

    async def _counting_load(session, version_id, table):  # type: ignore[no-untyped-def]
        cells = await real_load(session, version_id, table)
        loaded.append(len(cells))
        return cells

    monkeypatch.setattr(service, "_load_cells", _counting_load)
    rows_slug = _seed_mixed_table(api_client, workspace_id, actuary)
    loaded.clear()
    _all_pages(api_client, rows_slug, actuary, 2)  # two pages
    assert loaded == [4, 4]
    assert max(loaded) <= 250_000

    reads: list[int] = []
    real_read = BlobStore.read

    async def _counting_read(self, ref):  # type: ignore[no-untyped-def]
        reads.append(1)
        return await real_read(self, ref)

    monkeypatch.setattr(BlobStore, "read", _counting_read)
    _set_threshold(api_client, admin_headers, 2)
    parquet_slug = _seed_mixed_table(api_client, workspace_id, actuary)
    reads.clear()
    _all_pages(api_client, parquet_slug, actuary, 2)  # two pages
    assert len(reads) == 2


# -- the manual-edit route (FR-229, FR-234, F-W10-3; RL-1555 items 1 to 3) --------------------


def _edit_body(slug: str, **changes: object) -> dict[str, object]:
    body: dict[str, object] = {
        "base_version": 1,
        "change_note": "area band 21-24 +5%",
        "edits": [{"driver_age_band": "21-24", "relativity": "1.4500"}],
    }
    return body | changes


def _post_edit(api_client: TestClient, slug: str, headers: dict[str, str], **changes: object):  # type: ignore[no-untyped-def]
    return api_client.post(
        f"/api/v1/rate-tables/{slug}/versions", json=_edit_body(slug, **changes), headers=headers
    )


def _version_count(slug: str) -> int:
    counted: list[int] = []

    async def _count(session: AsyncSession) -> None:
        from sqlalchemy import func

        counted.append(
            await session.scalar(
                select(func.count())
                .select_from(RateTableVersionRow)
                .join(RateTableRow, RateTableRow.id == RateTableVersionRow.rate_table_id)
                .where(RateTableRow.slug == slug)
            )
            or 0
        )

    _run_with_database(_count)
    return counted[0]


def _stored_created_by_edit(slug: str, version: int) -> dict[str, object] | None:
    """The `created_by_edit` column of the stored row, read back from the database."""
    found: list[dict[str, object] | None] = []

    async def _read(session: AsyncSession) -> None:
        found.append(
            await session.scalar(
                select(RateTableVersionRow.created_by_edit)
                .join(RateTableRow, RateTableRow.id == RateTableVersionRow.rate_table_id)
                .where(RateTableRow.slug == slug, RateTableVersionRow.version_number == version)
            )
        )

    _run_with_database(_read)
    return found[0]


@pytest.mark.req("FR-229")
def test_manual_edit_preview_creates_nothing_and_is_a_bare_diff(
    api_client: TestClient, workspace_id, actuary
) -> None:
    from model_schema.rating import RateTableDiff

    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    before = _version_count(slug)

    response = _post_edit(api_client, slug, actuary)

    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == set(RateTableDiff.model_fields)  # bare: no `diff` or verdict wrapper
    assert RateTableDiff.model_validate(body).changed_cells == 1
    assert _version_count(slug) == before


@pytest.mark.req("FR-229")
def test_manual_edit_confirm_creates_the_next_version_with_its_record(
    api_client: TestClient, workspace_id, actuary
) -> None:
    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    submitted = {"applied_to": f"rate_table:{slug}@1", "edited_cells": 1}

    created = _post_edit(api_client, slug, actuary, confirm=True)

    assert created.status_code == 201, created.text
    body = created.json()
    assert body["version"] == 2
    assert body["change_note"] == "area band 21-24 +5%"
    assert body["created_by_edit"] == submitted
    # The record is stored, not only returned: read it back from the row (RL-1555 item 2).
    assert _stored_created_by_edit(slug, 2) == submitted
    assert _stored_created_by_edit(slug, 1) is None  # a seeded version carries none
    cells = _all_pages_of(api_client, slug, 2, actuary)
    assert {row["driver_age_band"]: row["relativity"] for row in cells} == {
        "17-20": "1.92",
        "21-24": "1.4500",
        "25-29": "1.12",
    }
    # A second confirm against the same, now stale, base is the existing 409.
    again = _post_edit(api_client, slug, actuary, confirm=True)
    assert again.status_code == 409, again.text
    assert again.json()["code"] == "VALIDATION_FAILED"


def _all_pages_of(
    api_client: TestClient, slug: str, version: int, headers: dict[str, str]
) -> list[dict[str, str]]:
    response = api_client.get(
        f"/api/v1/rate-tables/{slug}@{version}/cells", params={"limit": 200}, headers=headers
    )
    assert response.status_code == 200, response.text
    return response.json()["items"]


@pytest.mark.req("FR-229")
def test_a_manual_edit_diffs_against_its_base_by_exactly_the_edited_cells(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """RL-1555 item 2 and the maintainer's 04:12:41 condition: the stored version differs from
    its base by exactly the edited cells, their count is `edited_cells`, and each old → new
    pair is what was submitted."""
    from decimal import Decimal

    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    edits = [
        {"driver_age_band": "17-20", "relativity": "2.0000"},
        {"driver_age_band": "25-29", "relativity": "1.0000"},
    ]
    created = _post_edit(api_client, slug, actuary, confirm=True, edits=edits)
    assert created.status_code == 201, created.text

    diff = _diff_ready(
        api_client,
        f"/api/v1/rate-tables/{slug}@2/diff/cells",
        {"against": "1"},
        actuary,
    )

    assert diff.status_code == 200, diff.text
    changed = diff.json()["items"]
    assert len(changed) == created.json()["created_by_edit"]["edited_cells"] == 2
    old = {row["driver_age_band"]: Decimal(row["relativity"]) for row in _all_pages_of(
        api_client, slug, 1, actuary
    )}
    assert {
        item["key"]["driver_age_band"]: (
            Decimal(item["baseline_value"]),
            Decimal(item["current_value"]),
        )
        for item in changed
    } == {
        edit["driver_age_band"]: (old[edit["driver_age_band"]], Decimal(edit["relativity"]))
        for edit in edits
    }
    assert {item["change"] for item in changed} == {"changed"}


@pytest.mark.req("FR-234")
@pytest.mark.parametrize(
    ("changes", "status", "field_errors"),
    [
        ({"change_note": ""}, 422, None),
        ({"change_note": "   "}, 422, None),
        ({"edits": []}, 422, None),
        ({"unknown_field": 1}, 422, None),
        ({"edits": [{"driver_age_band": "21-24", "relativity": 1.45}]}, 422, None),
        (
            {"edits": [{"driver_age_band": "99-99", "relativity": "1.0"}]},
            422,
            [("edits.0.relativity", "UNKNOWN_KEY")],
        ),
        (
            {"edits": [{"driver_age_band": "21-24", "relativity": "1.0"}] * 2},
            422,
            [("edits.1.relativity", "DUPLICATE_KEY")],
        ),
        (
            {"edits": [{"driver_age_band": "21-24", "relativity": "1.0"}, {"relativity": "1"}]},
            422,
            [("edits.1.relativity", "EDIT_COLUMNS")],
        ),
    ],
)
def test_manual_edit_refusals(
    api_client: TestClient, workspace_id, actuary, changes, status, field_errors
) -> None:
    """One case per refusal; an unknown key is a 422 with a field error, never a 500."""
    slug, _ = _seeded_table(api_client, workspace_id, actuary)

    response = _post_edit(api_client, slug, actuary, **changes)

    assert response.status_code == status, response.text
    if field_errors is not None:
        assert [(e["field"], e["code"]) for e in response.json()["errors"]] == field_errors
        assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-234")
def test_manual_edit_out_of_bounds_values_each_name_their_edit(
    api_client: TestClient, workspace_id, actuary
) -> None:
    """Two non-decimal (out-of-bounds) values answer two field errors, `edits.0.<value>` and
    `edits.1.<value>`, both `OUT_OF_BOUNDS`, under the problem code `RATE_TABLE_INCOMPLETE`
    (RL-1555 item 3)."""
    # A seeded value column declares no bounds, so the shared check's other OUT_OF_BOUNDS
    # arm is used: a value that is not a decimal at all.
    slug, _ = _seeded_table(api_client, workspace_id, actuary)
    not_a_decimal = "not-a-number"

    response = _post_edit(
        api_client,
        slug,
        actuary,
        edits=[
            {"driver_age_band": "17-20", "relativity": not_a_decimal},
            {"driver_age_band": "21-24", "relativity": not_a_decimal},
        ],
    )

    assert response.status_code == 422, response.text
    assert response.json()["code"] == "RATE_TABLE_INCOMPLETE"
    assert [(e["field"], e["code"]) for e in response.json()["errors"]] == [
        ("edits.0.relativity", "OUT_OF_BOUNDS"),
        ("edits.1.relativity", "OUT_OF_BOUNDS"),
    ]


@pytest.mark.req("FR-229")
def test_rate_table_isolation_on_the_manual_edit_route(
    api_client: TestClient, workspace_id, actuary
) -> None:
    from app.platform import workspaces

    foreign = uuid4()
    slug = _table_slug()

    async def _insert(session: AsyncSession) -> None:
        await workspaces.ensure_workspace(session, workspace_id=foreign)

    _run_with_database(_insert)
    _insert_table(foreign, slug, [{"name": "driver_age_band", "type": "string"}])

    response = _post_edit(api_client, slug, actuary)

    assert response.status_code == 404, response.text
    assert response.json()["code"] == "RATE_TABLE_MISS"
