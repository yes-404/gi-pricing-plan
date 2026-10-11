"""FD-1420 over HTTP: a `lookup` step reads the row in force as at its declared date.

The three scoring paths — `/score`, `/score/compare` and the batch Job — each price a quote
whose `effective_date` falls in a later window of a key with two effective-dated rows. Before
the fix every path returned the superseded row's rate (PL-1447; FR-221, `01` FR-69).
`packages/pricing-core/tests/test_rating_lookup_as_at.py` is the pricing-core half and its
`ROWS`, `_algo` and literals are mirrored here, not shared across the package boundary.
"""

from __future__ import annotations

import io
import json
from datetime import date
from typing import Any
from uuid import UUID, uuid4

import polars as pl
import pytest
from backend.tests.test_rating_version_compile import _headers, _insert_version
from fastapi.testclient import TestClient

from app.db.models import BlobRow, DatasetVersionRow, JobRow
from app.db.session import Database
from app.platform.blobs import BlobStore, to_ref
from app.worker.rating_handlers import register_rating_handlers
from app.worker.scoring_handlers import register_scoring_handlers
from app.worker.tasks import execute_job
from model_schema import JobStatus, Principal

SCORE_URL = "/api/v1/score"
COMPARE_URL = "/api/v1/score/compare"
BATCH_URL = "/api/v1/score/batch"
SCORED_REF = "rating_version:minimal-rv@1"
SUPERSEDED = "the superseded row's rate returned"

#: Two windows for one key: OLD until 2026-01-01 (exclusive), NEW from it, open-ended.
ROWS = [
    {"key": "SW1A", "payload": {"area_loading": "1.30"},
     "effective_from": "2020-01-01", "effective_to": "2026-01-01"},
    {"key": "SW1A", "payload": {"area_loading": "1.80"},
     "effective_from": "2026-01-01", "effective_to": None},
]


def _algorithm(table_ref: str) -> dict[str, Any]:
    return {
        "slug": "score-fixture", "version": 1,
        "input_contract": [
            {"name": "base_minor", "type": "int", "nullable": False},
            {"name": "postcode", "type": "string", "nullable": False},
        ],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in_base", "type": "input", "label": "Base", "input_name": "base_minor",
             "on_missing": "error", "produces": "base_minor"},
            {"step_id": "s_in_pc", "type": "input", "label": "Postcode", "input_name": "postcode",
             "on_missing": "error", "produces": "postcode"},
            {"step_id": "s_area", "type": "lookup", "label": "Area loading",
             "reference_table_ref": table_ref, "key_expr": ["postcode"],
             "as_at": "effective_date", "on_miss": "error", "consumes": ["postcode"],
             "produces": "area_loading"},
            {"step_id": "s_expr", "type": "expression", "label": "Apply",
             "expr": "base_minor * number(area_loading)", "result_type": "money_minor",
             "consumes": ["base_minor", "area_loading"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


def _create_reference_table(
    client: TestClient, headers: dict[str, str], rows: list[dict[str, Any]]
) -> tuple[str, Any]:
    """Mirrors `test_api_reference.py::_table`: create, load a version, publish it."""
    slug = f"area-{uuid4().hex[-6:]}"
    assert client.post(
        "/api/v1/reference-tables",
        json={"slug": slug, "key_columns": ["postcode"], "payload_columns": ["area_loading"]},
        headers=headers,
    ).status_code == 201
    loaded = client.post(
        f"/api/v1/reference-tables/{slug}/versions",
        json={"source_note": "2026 refresh", "rows": rows},
        headers=headers,
    )
    return slug, loaded


@pytest.fixture
async def headers(principal: Principal, workspace_id: UUID, grant: Any) -> dict[str, str]:
    """A user who may build the fixtures (`admin` creates Service Accounts, `analyst` holds
    `rating:write` and `rating:read`) and who may not score (`score:*` is granted by no
    builtin role, FR-347)."""
    await grant("admin")
    await grant("analyst")
    return _headers(principal, workspace_id)


def _service_account(
    client: TestClient, headers: dict[str, str], workspace_id: UUID, permission: str
) -> dict[str, str]:
    created = client.post(
        "/api/v1/service-accounts",
        json={
            "slug": f"as-at-{permission.replace(':', '-')}",
            "environments": ["uat"],
            "permissions": [permission],
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    return {"X-API-Key": created.json()["key"], "Workspace-Id": str(workspace_id)}


@pytest.fixture
def scoring_headers(
    api_client: TestClient, headers: dict[str, str], workspace_id: UUID
) -> dict[str, str]:
    return _service_account(api_client, headers, workspace_id, "score:execute")


@pytest.fixture
def batch_headers(
    api_client: TestClient, headers: dict[str, str], workspace_id: UUID
) -> dict[str, str]:
    return _service_account(api_client, headers, workspace_id, "score:batch")


@pytest.fixture
async def compiled_version(
    api_client: TestClient,
    headers: dict[str, str],
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    principal: Principal,
) -> None:
    """A genuinely compiled Rating Version at `SCORED_REF`, pinning a published reference
    table that holds `ROWS`. Written out as `test_scoring_handlers.py::_compiled_version`
    does: the compile Job is driven with `execute_job` from this async fixture."""
    register_rating_handlers()
    slug, loaded = _create_reference_table(api_client, headers, ROWS)
    assert loaded.status_code == 201, loaded.text
    assert api_client.post(
        f"/api/v1/reference-tables/{slug}/versions/1/publish", headers=headers
    ).status_code == 200
    table_ref = f"reference_table:{slug}@1"
    created = api_client.post(
        "/api/v1/rating-algorithms", json=_algorithm(table_ref), headers=headers
    )
    assert created.status_code in (200, 201), created.text
    row = await _insert_version(
        database, workspace_id, principal.id,
        algorithm_ref="rating_algorithm:score-fixture@1",
        pins={
            "rate_tables": [], "models": [], "reference_tables": [table_ref],
            "custom_objectives": [],
        },
    )
    response = api_client.post(f"/api/v1/rating-versions/{row.id}/compile", headers=headers)
    assert response.status_code == 202, response.text
    status = await execute_job(database, UUID(response.json()["id"]), blob_store)
    assert status is JobStatus.SUCCEEDED, status


def _context(effective_date: str) -> dict[str, Any]:
    """A `QuoteContext` body without `options`: `/score/compare` names its two versions itself."""
    return {
        "purpose": "new_business",
        "quoted_at": "2026-08-30T09:00:00Z",
        "effective_date": effective_date,
        "inputs": {"base_minor": 100_000, "postcode": "SW1A"},
    }


def _scored(effective_date: str) -> dict[str, Any]:
    return {**_context(effective_date), "options": {"rating_version_ref": SCORED_REF}}


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-69")
def test_score_prices_on_the_row_in_force(
    api_client: TestClient, scoring_headers: dict[str, str], compiled_version: None
) -> None:
    response = api_client.post(SCORE_URL, json=_scored("2026-06-01"), headers=scoring_headers)

    assert response.status_code == 200, response.text
    assert response.json()["outputs"]["payable_premium_minor"] == 180_000, SUPERSEDED


@pytest.mark.req("FR-221")
def test_score_compare_prices_both_sides_on_the_row_in_force(
    api_client: TestClient, headers: dict[str, str], compiled_version: None
) -> None:
    body = {"context": _context("2026-06-01"), "base": SCORED_REF, "comparison": SCORED_REF}
    response = api_client.post(COMPARE_URL, json=body, headers=headers)

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["base"]["outputs"]["payable_premium_minor"] == 180_000, SUPERSEDED
    assert result["comparison"]["outputs"]["payable_premium_minor"] == 180_000, SUPERSEDED


async def _scoring_dataset(
    database: Database, blob_store: BlobStore, workspace_id: UUID, principal: Principal
) -> UUID:
    """A Dataset Version carrying a `scoring_frame` (`03` §4.8's shape) of two quotes, one in
    each window; `test_scoring_handlers.py::_dataset_version` is the neighbour."""
    frame = pl.DataFrame({
        "quote_id": ["Q0", "Q1"],
        "purpose": ["new_business", "new_business"],
        "effective_date": [date(2025, 6, 1).isoformat(), date(2026, 6, 1).isoformat()],
        "rating_version_ref": ["rating_version:placeholder@0"] * 2,  # always overwritten
        "base_minor": [100_000, 100_000],
        "postcode": ["SW1A", "SW1A"],
    })
    buffer = io.BytesIO()
    frame.write_parquet(buffer, compression="zstd")
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, buffer.getvalue(), "application/x-parquet")
        row = DatasetVersionRow(
            slug="score-as-at-fixture",
            workspace_id=workspace_id,
            dataset_id=uuid4(),
            version=1,
            status="draft",
            created_by=principal.id,
            currency="GBP",
            tables=[{"name": "scoring_frame", "blob": {"sha256": ref.sha256}}],
        )
        session.add(row)
        await session.flush()
        return row.id


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-253")
async def test_score_batch_job_prices_on_the_row_in_force(
    api_client: TestClient,
    batch_headers: dict[str, str],
    compiled_version: None,
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    principal: Principal,
) -> None:
    register_scoring_handlers()
    dataset_version_id = await _scoring_dataset(database, blob_store, workspace_id, principal)
    response = api_client.post(
        BATCH_URL,
        json={
            "dataset_version_id": str(dataset_version_id),
            "rating_version_refs": [SCORED_REF],
            "chunk_rows": 2,
        },
        headers=batch_headers,
    )
    assert response.status_code == 202, response.text
    job_id = UUID(response.json()["id"])
    assert await execute_job(database, job_id, blob_store) is JobStatus.SUCCEEDED

    async with database.session() as session:
        job_row = await session.get(JobRow, job_id)
        assert job_row is not None
        assert job_row.result is not None
        summary_row = await session.get(BlobRow, job_row.result["ref"])
        assert summary_row is not None
        summary = json.loads(await blob_store.read(to_ref(summary_row)))
        output_row = await session.get(BlobRow, summary["results"][0]["output_blob_sha256"])
        assert output_row is not None
        output = pl.read_parquet(io.BytesIO(await blob_store.read(to_ref(output_row))))

    ordered = output.sort("quote_id")
    prices = [json.loads(v)["payable_premium_minor"] for v in ordered["outputs_json"]]
    assert prices == [130_000, 180_000], SUPERSEDED


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-213")
@pytest.mark.parametrize(
    ("raw", "status", "price"),
    [
        pytest.param("2026-06-01", 200, 180_000, id="plain-date"),
        # `QuoteContext.effective_date` is a pydantic `date`: a datetime with an offset parses
        # to its LOCAL date (DP-3 (a) pins this), so it lands in the 2026-01-01 window.
        pytest.param("2026-01-01T00:00:00+01:00", 200, 180_000, id="offset-midnight-local-date"),
        pytest.param("2026-01-01T00:30:00+01:00", 422, None, id="offset-not-midnight-refused"),
        pytest.param("2026-13-01", 422, None, id="impossible-month-refused"),
    ],
)
def test_effective_date_parsing_is_pinned(
    api_client: TestClient,
    scoring_headers: dict[str, str],
    compiled_version: None,
    raw: str,
    status: int,
    price: int | None,
) -> None:
    response = api_client.post(SCORE_URL, json=_scored(raw), headers=scoring_headers)

    assert response.status_code == status, response.text
    if price is None:
        assert response.json()["code"] == "VALIDATION_FAILED"
    else:
        assert response.json()["outputs"]["payable_premium_minor"] == price, SUPERSEDED


@pytest.mark.req("FR-221")
@pytest.mark.req("FR-69")
def test_overlapping_windows_are_refused_at_table_save_with_their_code(
    api_client: TestClient, headers: dict[str, str]
) -> None:
    overlapping = [{**ROWS[0], "effective_to": "2026-02-01"}, ROWS[1]]
    _, loaded = _create_reference_table(api_client, headers, overlapping)

    assert loaded.status_code == 409, loaded.text
    assert loaded.json()["code"] == "REFERENCE_INTERVAL_OVERLAP"
