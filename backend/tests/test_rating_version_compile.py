"""Rating Version compile endpoint (slice W9-3, FR-RATE-24/25; W11 Task 1.2).

A pinned version compiles to a self-contained Bundle with a reproducible hash; an
unpinned version and a broken guard are refused with named errors. Compilation is a
`rating.compile` Job since Task 1.2 (Ruling 2) — the route answers 202 rather than
computing synchronously — and every resolver branch (rate tables, reference tables,
custom objectives, models) must resolve real content, embedded inline per Ruling 7, for
the Job to succeed rather than fail with `NOT_FOUND` / `PIN_NOT_APPROVED`.
"""

from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

import pytest
from backend.tests.test_api_reference import _table as _seed_reference_table
from backend.tests.test_custom_objectives_api import _advance, _create
from backend.tests.test_model_jobs_gbm import _fitted_gbm
from backend.tests.test_rate_tables_service import _seed as _seed_rate_table
from backend.tests.test_rate_tables_service import _table_slug as _rate_table_slug

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.models import BlobRow, JobRow, ModelRow, RatingVersionRow
from app.db.session import Database
from app.platform.blobs import BlobStore, to_ref
from app.platform.rating_versions import compile_rating_version
from app.worker.rating_handlers import register_rating_handlers
from app.worker.tasks import execute_job
from model_schema import JobStatus, ModelStatus, ObjectiveStatus
from pricing_core.rating.compile import Bundle


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_rating_handlers()


def _minimal_algorithm() -> dict:
    """A minimal graph with no external artifact refs — input, expression, output."""
    return {
        "slug": "minimal",
        "version": 1,
        "input_contract": [
            {"name": "premium_in", "type": "int", "nullable": False},
        ],
        "outputs": [
            {"name": "payable_premium_minor", "type": "money_minor", "required": True},
        ],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In",
             "input_name": "premium_in", "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_expr", "type": "expression", "label": "Apply",
             "expr": "premium_in * 2", "result_type": "money_minor",
             "consumes": ["premium_in"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


def _headers(principal, workspace_id) -> dict[str, str]:
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }


def _empty_pins() -> dict:
    return {"rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": []}


async def _insert_version(
    database, workspace_id, created_by, algorithm_ref: str | None, pins: dict
) -> RatingVersionRow:
    row = RatingVersionRow(
        workspace_id=workspace_id,
        slug="minimal-rv",
        version=1,
        status="draft",
        dataset_version_id=uuid4(),
        model_ref="model:motor-ad-frequency@7",
        created_by=created_by,
        algorithm_ref=algorithm_ref,
        pins=pins,
    )
    async with database.unit_of_work() as session:
        session.add(row)
        await session.flush()
        return row


def _run_compile_job(
    api_client, headers: dict[str, str], database: Database, blob_store: BlobStore,
    rating_version_id: UUID,
) -> JobRow:
    """POST the compile route, drive the returned Job synchronously (no live worker in
    tests — the `test_worker_rate_tables` convention), and return the finished `JobRow`."""
    response = api_client.post(
        f"/api/v1/rating-versions/{rating_version_id}/compile", headers=headers
    )
    assert response.status_code == 202, response.text
    job_body = response.json()
    assert response.headers["Location"] == f"/api/v1/jobs/{job_body['id']}"
    job_id = UUID(job_body["id"])

    async def _run() -> JobRow:
        job_status = await execute_job(database, job_id, blob_store)
        async with database.session() as session:
            row = await session.get(JobRow, job_id)
        assert row is not None
        assert row.status is job_status
        return row

    return asyncio.get_event_loop().run_until_complete(_run())


def _read_blob(database: Database, blob_store: BlobStore, sha256: str) -> bytes:
    async def _run() -> bytes:
        async with database.session() as session:
            row = await session.get(BlobRow, sha256)
        assert row is not None
        return await blob_store.read(to_ref(row))

    return asyncio.get_event_loop().run_until_complete(_run())


@pytest.mark.req("FR-RATE-24")
def test_a_pinned_version_compiles_over_http(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms",
        json=_minimal_algorithm(),
        headers=headers,
    )
    assert created.status_code == 201, created.text

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins=_empty_pins(),
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    assert job_row.result["kind"] == "blob"
    payload = _read_blob(database, blob_store, job_row.result["ref"])
    bundle = Bundle.model_validate_json(payload)
    assert bundle.content_hash.startswith("sha256:")
    assert bundle.graph.nodes


@pytest.mark.req("FR-RATE-22")
def test_an_unpinned_version_is_refused_over_http(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database, workspace_id, principal.id, algorithm_ref=None, pins=_empty_pins()
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "RATING_VERSION_UNPINNED"


@pytest.mark.req("FR-RATE-25")
def test_a_version_pinning_a_rate_table_compiles(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """A Rating Version pinning a real W10 rate table resolves and compiles.

    Before Task 1.2, `_Resolver`'s catch-all refuses every `rate_table` ref with
    `NOT_FOUND` and the detail `"has no backend table yet (Phase 2)"` — verified against
    unmodified `rating_versions.py` before this task's resolver branch was added.
    """
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    family = f"mf-{uuid4().hex[:8]}"
    slug = _rate_table_slug()
    seeded = asyncio.get_event_loop().run_until_complete(
        _seed_rate_table(database, workspace_id, principal, family, slug, blob_store)
    )

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [f"rate_table:{seeded.slug}@{seeded.version}"],
                "models": [],
                "reference_tables": [],
                "custom_objectives": [],
            },
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    payload = _read_blob(database, blob_store, job_row.result["ref"])
    bundle = Bundle.model_validate_json(payload)
    ref_key = f"rate_table:{seeded.slug}@{seeded.version}"
    assert ref_key in bundle.resolved_payloads
    assert bundle.resolved_payloads[ref_key]["rows"], "the rate table's rows were dropped"


@pytest.mark.req("FR-RATE-25")
def test_a_version_pinning_a_published_reference_table_compiles(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """A Rating Version pinning a *published* reference table version resolves.

    FR-DATA-30's own lifecycle (`draft`/`published`) is not `compile_bundle`'s generic
    `approved`/`live`/`retired` maturity vocabulary; the resolver bridges "published" to
    "approved" so a real, published reference table can compile at all.
    """
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("admin"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    slug = _seed_reference_table(api_client, headers, publish=True)

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [],
                "models": [],
                "reference_tables": [f"reference_table:{slug}@1"],
                "custom_objectives": [],
            },
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    payload = _read_blob(database, blob_store, job_row.result["ref"])
    bundle = Bundle.model_validate_json(payload)
    ref_key = f"reference_table:{slug}@1"
    assert ref_key in bundle.resolved_payloads
    assert bundle.resolved_payloads[ref_key]["rows"], "the reference table's rows were dropped"


@pytest.mark.req("FR-OVR-14")
def test_a_version_pinning_an_unpublished_reference_table_is_refused(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """A `draft` reference table version is still refused — the bridge must not fake
    maturity for a version that was never published."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("admin"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    slug = _seed_reference_table(api_client, headers, publish=False)

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [],
                "models": [],
                "reference_tables": [f"reference_table:{slug}@1"],
                "custom_objectives": [],
            },
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "PIN_NOT_APPROVED"


@pytest.mark.req("FR-RATE-25")
def test_a_version_pinning_an_approved_custom_objective_compiles(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    objective = _create(api_client, headers)
    _advance(UUID(objective["id"]), status=ObjectiveStatus.APPROVED)

    objective_ref = f"custom_objective:{objective['slug']}@{objective['version']}"
    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [],
                "models": [],
                "reference_tables": [],
                "custom_objectives": [objective_ref],
            },
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    payload = _read_blob(database, blob_store, job_row.result["ref"])
    bundle = Bundle.model_validate_json(payload)
    assert objective_ref in bundle.resolved_payloads


@pytest.mark.req("FR-RATE-24")
def test_the_compiled_bundle_survives_persistence(
    workspace_id, principal, grant, database, blob_store, api_client
) -> None:
    """Compile, fetch the Bundle back from the blob store, and confirm nothing was
    dropped — including a GBM's booster, which must be the content itself (Ruling 7),
    never a blob reference `load_bundle` (Task 1.3) could not fetch without I/O."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    async def _seed_gbm() -> str:
        model_id, fit_status = await _fitted_gbm(database, blob_store, workspace_id)
        assert fit_status is JobStatus.SUCCEEDED
        async with database.unit_of_work() as session:
            model_row = await session.get(ModelRow, model_id)
            assert model_row is not None
            model_row.status = ModelStatus.APPROVED.value
            slug, version = model_row.model_family_slug, model_row.version
        return f"model:{slug}@{version}"

    model_ref = asyncio.get_event_loop().run_until_complete(_seed_gbm())

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [],
                "models": [model_ref],
                "reference_tables": [],
                "custom_objectives": [],
            },
        )
    )

    async def _in_process_bundle() -> Bundle:
        async with database.unit_of_work() as session:
            return await compile_rating_version(
                session, workspace_id=workspace_id, rating_version_id=row.id,
                blob_store=blob_store,
            )

    in_process_bundle = asyncio.get_event_loop().run_until_complete(_in_process_bundle())

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    assert job_row.result["kind"] == "blob"

    payload = _read_blob(database, blob_store, job_row.result["ref"])
    restored = Bundle.model_validate_json(payload)
    assert restored.graph.nodes, "the persisted Bundle has an empty graph"
    assert restored.resolved_payloads, "the persisted Bundle has no resolved payloads"
    assert restored.content_hash == in_process_bundle.content_hash

    fit_result = restored.resolved_payloads[model_ref]["fit_result"]
    assert fit_result["model_type"] in ("xgboost", "lightgbm")
    assert "booster_content" in fit_result, "the booster is missing from the payload"
    # The proof Ruling 7 asks for: real serialised booster content, not a blob sha256.
    assert len(fit_result["booster_content"]) > 100
    assert fit_result["booster_content"] != fit_result["booster_blob"]["sha256"]
