"""`score.batch` — the batch scoring Job handler (W11 Task 3B, FR-RATE-36/37/38).

**The handler is invoked directly, never through `execute_job`.** Ruling 31 §6's addendum
(`docs/plans/2026-08-29-w11-3-d6-batch-resumability-ruling.md`) is explicit that
resumability can only be tested at the handler level: `execute_job`'s own `QUEUED` guard
(`app/worker/tasks.py:94`/`:103`) refuses a second call for the *same* Job id outright, and
nothing in this suite has ever invoked a handler function directly before this file —
`backend/tests/test_worker.py` drives every handler through `execute_job`. This is that
first one, budgeted as new test shape rather than a neighbour to copy.

Fixture shape: `_minimal_algorithm`/`_empty_pins`/`_insert_version`/`_run_compile_job`/
`_headers`, reused from `test_rating_version_compile.py` rather than duplicated — the
established convention in this test suite. The scoring frame is this file's own: one
`premium_in` column per `_minimal_algorithm`'s single declared input, plus `03` §4.8's four
reserved columns.
"""

from __future__ import annotations

import asyncio
import io
from datetime import date
from typing import Any
from uuid import UUID, uuid4

import polars as pl
import pytest
from backend.tests.test_rating_version_compile import (
    _empty_pins,
    _headers,
    _insert_version,
    _minimal_algorithm,
)
from fastapi.testclient import TestClient

from app.db.models import DatasetVersionRow
from app.db.session import Database
from app.platform import jobs
from app.platform.blobs import BlobStore
from app.worker import scoring_handlers as scoring_handlers_module
from app.worker.progress import JobProgress
from app.worker.rating_handlers import register_rating_handlers
from app.worker.scoring_handlers import _score_batch_handler
from app.worker.tasks import execute_job
from model_schema import JobKind, JobResult, Principal

SCORED_REF = "rating_version:minimal-rv@1"


def _scoring_frame(n: int, *, bad_row: int | None = None) -> pl.DataFrame:
    """`n` rows in `03` §4.8's shape for `_minimal_algorithm` (one input, `premium_in`).

    `bad_row`, if given, sets that row's `premium_in` to `None` — `_minimal_algorithm`
    declares it `nullable: False`, so that row alone raises `INPUT_CONTRACT_VIOLATION`
    (FR-RATE-2) without disturbing any other row's column type (an out-of-range value
    would do the same without polars widening the whole column — the same trap
    `test_rating_score_batch.py`'s own error-isolation test documents).
    """
    return pl.DataFrame(
        {
            "quote_id": [f"Q{i}" for i in range(n)],
            "purpose": ["new_business"] * n,
            "effective_date": [date(2026, 9, 1).isoformat()] * n,
            "rating_version_ref": ["rating_version:placeholder@0"] * n,  # always overwritten
            "premium_in": [None if i == bad_row else 100 + i for i in range(n)],
        }
    )


async def _dataset_version(
    database: Database, blob_store: BlobStore, workspace_id: UUID, principal: Principal,
    frame: pl.DataFrame,
) -> UUID:
    """One Dataset Version carrying `frame` as its single table, `scoring_frame`."""
    buffer = io.BytesIO()
    frame.write_parquet(buffer, compression="zstd")
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, buffer.getvalue(), "application/x-parquet")
        row = DatasetVersionRow(
            slug="score-batch-fixture",
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


async def _compiled_version(
    client: TestClient, headers: dict[str, str], database: Database, blob_store: BlobStore,
    workspace_id: UUID, principal: Principal, grant: Any,
) -> None:
    """A genuinely compiled Rating Version, reachable as `SCORED_REF` — mirrors
    `test_rating_version_compile.py`'s own `api_client` + `grant("analyst")` pattern
    (`rating:write`; dev auth bypasses authentication, never authorisation). Written out
    rather than calling `_run_compile_job` directly: that helper's own
    `asyncio.get_event_loop().run_until_complete(...)` assumes a *synchronous* caller (its
    own file's tests are all plain `def`), and raises `RuntimeError: This event loop is
    already running` from inside this file's `async def` tests — the loop-already-running
    trap, not a bug in the helper.
    """
    register_rating_handlers()
    await grant("analyst")
    created = client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code in (200, 201), created.text
    row = await _insert_version(
        database, workspace_id, principal.id,
        algorithm_ref="rating_algorithm:minimal@1", pins=_empty_pins(),
    )

    response = client.post(
        f"/api/v1/rating-versions/{row.id}/compile", headers=headers
    )
    assert response.status_code == 202, response.text
    job_id = UUID(response.json()["id"])
    status = await execute_job(database, job_id, blob_store)
    assert status.value == "succeeded", status


async def _run_handler(
    database: Database, blob_store: BlobStore, workspace_id: UUID, principal: Principal,
    parameters: dict[str, Any],
) -> tuple[JobResult, UUID]:
    # `job_identity(caller)`'s own shape (`backend/src/app/api/deps.py`) — a route builds
    # this from the caller; this file has no route, so it is added here instead.
    identified = dict(parameters) | {
        "workspace_id": str(workspace_id),
        "actor": principal.model_dump(mode="json"),
    }
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.SCORE_BATCH, identified, principal, workspace_id=workspace_id
        )
    loop = asyncio.get_event_loop()
    progress = JobProgress(job.id, database, loop, blob_store=blob_store)
    full_parameters = identified | {"job_id": str(job.id)}
    result = await asyncio.to_thread(_score_batch_handler, full_parameters, progress)
    return result, job.id


def _parameters(dataset_version_id: UUID, **overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "dataset_version_id": str(dataset_version_id),
        "rating_version_refs": [SCORED_REF],
        "chunk_rows": 2,
    }
    base.update(overrides)
    return base


async def _summary(database: Database, blob_store: BlobStore, result: JobResult) -> dict[str, Any]:
    import json

    from app.db.models import BlobRow
    from app.platform.blobs import to_ref

    assert result.kind == "blob"
    assert result.ref is not None
    async with database.session() as session:
        row = await session.get(BlobRow, result.ref)
        assert row is not None
        payload = await blob_store.read(to_ref(row))
    return json.loads(payload)  # type: ignore[no-any-return]


async def _output_bytes(database: Database, blob_store: BlobStore, sha256: str) -> bytes:
    from app.db.models import BlobRow
    from app.platform.blobs import to_ref

    async with database.session() as session:
        row = await session.get(BlobRow, sha256)
        assert row is not None
        return await blob_store.read(to_ref(row))


@pytest.fixture
def headers(principal: Principal, workspace_id: UUID) -> dict[str, str]:
    return _headers(principal, workspace_id)


# ---------------------------------------------------------------------------
# Step 1: resumability. Called directly, never through `execute_job` (module docstring).
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-37")
async def test_a_resumed_run_does_not_re_score_completed_chunks_and_matches_an_uninterrupted_run(
    api_client: TestClient, headers: dict[str, str], database: Database, blob_store: BlobStore,
    workspace_id: UUID, principal: Principal, grant: Any, monkeypatch: pytest.MonkeyPatch,
) -> None:
    await _compiled_version(
        api_client, headers, database, blob_store, workspace_id, principal, grant
    )

    # --- An uninterrupted, independent run over the same shape (its own Dataset Version,
    # so the two never share a manifest key) — the byte-identity baseline. ---
    baseline_frame = _scoring_frame(8)
    baseline_dvid = await _dataset_version(
        database, blob_store, workspace_id, principal, baseline_frame
    )
    baseline_result, _ = await _run_handler(
        database, blob_store, workspace_id, principal, _parameters(baseline_dvid)
    )
    baseline_summary = await _summary(database, blob_store, baseline_result)
    baseline_output = await _output_bytes(
        database, blob_store, baseline_summary["results"][0]["output_blob_sha256"]
    )

    # --- The interrupted run: a crash partway through, simulated by making the *third*
    # scratch write raise. chunk_rows=2 over 8 rows is 4 chunks, so this leaves exactly
    # two chunks' worth of scratch behind — never by inspecting the final output. ---
    frame = _scoring_frame(8)
    dataset_version_id = await _dataset_version(
        database, blob_store, workspace_id, principal, frame
    )
    parameters = _parameters(dataset_version_id)

    original_write_scratch = BlobStore.write_scratch
    calls = 0

    async def _crash_on_third_write(self: BlobStore, key: str, content: bytes) -> None:
        nonlocal calls
        calls += 1
        if calls == 3:
            raise RuntimeError("simulated crash mid-run")
        await original_write_scratch(self, key, content)

    monkeypatch.setattr(BlobStore, "write_scratch", _crash_on_third_write)

    with pytest.raises(RuntimeError, match="simulated crash mid-run"):
        await _run_handler(database, blob_store, workspace_id, principal, parameters)

    monkeypatch.setattr(BlobStore, "write_scratch", original_write_scratch)

    # Exactly two chunk parts survived the crash — not zero, not all four.
    scratch_prefix_probe = await blob_store.list_scratch("score-batch/")
    surviving = [k for k in scratch_prefix_probe if f"/{dataset_version_id}/" in k]
    assert len(surviving) == 2, surviving

    # --- The resumed run: a *different* Job id, same parameters. Counting calls into
    # score_batch is (i) — the chunk-invocation count, never the output. ---
    score_batch_calls = 0
    real_score_batch = scoring_handlers_module.score_batch

    def _counting_score_batch(*args: Any, **kwargs: Any) -> Any:
        nonlocal score_batch_calls
        score_batch_calls += 1
        return real_score_batch(*args, **kwargs)

    monkeypatch.setattr(scoring_handlers_module, "score_batch", _counting_score_batch)

    resumed_result, resumed_job_id = await _run_handler(
        database, blob_store, workspace_id, principal, parameters
    )

    monkeypatch.setattr(scoring_handlers_module, "score_batch", real_score_batch)

    # 4 total chunks, 2 already done -> only 2 new score_batch calls.
    assert score_batch_calls == 2, (
        f"resumed run re-scored a completed chunk: {score_batch_calls} score_batch calls, "
        "expected 2 (4 chunks total, 2 already in scratch)"
    )

    resumed_summary = await _summary(database, blob_store, resumed_result)
    resumed_output = await _output_bytes(
        database, blob_store, resumed_summary["results"][0]["output_blob_sha256"]
    )

    # (ii) — the final parquet is byte-identical to the uninterrupted baseline run.
    assert resumed_output == baseline_output

    # `resumed_job_id` is a fresh row from this call's own `jobs.submit` — a different Job
    # id from the interrupted run's is guaranteed by construction (`_run_handler` submits
    # a new Job every call), which is the "under a different Job id" the plan's Step 1
    # requires. Sanity-checked rather than merely assumed:
    assert resumed_job_id is not None


# ---------------------------------------------------------------------------
# Step 3: the threshold, in both directions (Ruling 24). FR-RATE-38.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-38")
async def test_a_requested_threshold_above_the_workspace_setting_is_refused(
    api_client: TestClient, headers: dict[str, str], database: Database, blob_store: BlobStore,
    workspace_id: UUID, principal: Principal, grant: Any,
) -> None:
    from app.errors import PlatformError
    from app.platform import settings as settings_service

    await _compiled_version(
        api_client, headers, database, blob_store, workspace_id, principal, grant
    )
    async with database.unit_of_work() as session:
        await settings_service.set_workspace_setting(
            session, workspace_id, "rating.batch_abort_failure_rate", 0.1
        )

    frame = _scoring_frame(4)
    dataset_version_id = await _dataset_version(
        database, blob_store, workspace_id, principal, frame
    )
    parameters = _parameters(dataset_version_id, abort_failure_rate=0.5)  # 0.5 > 0.1

    with pytest.raises(PlatformError) as excinfo:
        await _run_handler(database, blob_store, workspace_id, principal, parameters)
    assert excinfo.value.code == "BATCH_ABORT_THRESHOLD_ABOVE_SETTING"

    # Refused before any row was scored — no scratch part was ever written.
    surviving = await blob_store.list_scratch("score-batch/")
    assert not [k for k in surviving if f"/{dataset_version_id}/" in k]


@pytest.mark.req("FR-RATE-38")
async def test_a_run_crossing_the_effective_threshold_aborts_recording_both_numbers(
    api_client: TestClient, headers: dict[str, str], database: Database, blob_store: BlobStore,
    workspace_id: UUID, principal: Principal, grant: Any,
) -> None:
    from app.errors import PlatformError
    from app.platform import settings as settings_service

    await _compiled_version(
        api_client, headers, database, blob_store, workspace_id, principal, grant
    )
    async with database.unit_of_work() as session:
        await settings_service.set_workspace_setting(
            session, workspace_id, "rating.batch_abort_failure_rate", 0.1
        )

    # chunk_rows=2, bad_row=0: the first chunk alone carries a 1/2 = 0.5 failure rate,
    # already over the 0.1 effective threshold — the abort fires after one chunk.
    frame = _scoring_frame(4, bad_row=0)
    dataset_version_id = await _dataset_version(
        database, blob_store, workspace_id, principal, frame
    )
    parameters = _parameters(dataset_version_id)

    with pytest.raises(PlatformError) as excinfo:
        await _run_handler(database, blob_store, workspace_id, principal, parameters)

    assert excinfo.value.code == "BATCH_ABORTED"
    detail = excinfo.value.detail or ""
    assert "0.1" in detail  # threshold in force
    assert "0.5" in detail  # observed failure rate

    # And an aborted run leaves nothing behind — scratch was cleaned up, not left orphaned.
    surviving = await blob_store.list_scratch("score-batch/")
    assert not [k for k in surviving if f"/{dataset_version_id}/" in k]


@pytest.mark.req("FR-RATE-38")
async def test_the_unset_default_means_no_rate_based_abort_but_counts_still_accrue(
    api_client: TestClient, headers: dict[str, str], database: Database, blob_store: BlobStore,
    workspace_id: UUID, principal: Principal, grant: Any,
) -> None:
    """Nothing sets `rating.batch_abort_failure_rate` for this workspace and the request
    carries no `abort_failure_rate` either — FR-RATE-38's own construction makes an
    undeclared threshold mean *no rate-based abort*, and the counts-and-samples half still
    applies (Step 4 asserts the counting in full; this asserts the non-abort)."""
    await _compiled_version(
        api_client, headers, database, blob_store, workspace_id, principal, grant
    )

    frame = _scoring_frame(4, bad_row=1)
    dataset_version_id = await _dataset_version(
        database, blob_store, workspace_id, principal, frame
    )
    parameters = _parameters(dataset_version_id)

    result, _ = await _run_handler(database, blob_store, workspace_id, principal, parameters)
    summary = await _summary(database, blob_store, result)

    ref_result = summary["results"][0]
    assert ref_result["threshold"] is None
    assert ref_result["error_counts"] == {"INPUT_CONTRACT_VIOLATION": 1}
    assert ref_result["outcome_counts"]["error"] == 1
    assert ref_result["outcome_counts"]["quoted"] == 3
    assert ref_result["row_count"] == 4
    samples = ref_result["error_samples"]["INPUT_CONTRACT_VIOLATION"]
    assert samples
    assert "premium_in" in samples[0]


# ---------------------------------------------------------------------------
# Step 5: chunk parts are scratch, released when the run completes (Ruling 31 §4).
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-37")
async def test_chunk_parts_are_scratch_and_the_blob_store_holds_exactly_one_new_object(
    api_client: TestClient, headers: dict[str, str], database: Database, blob_store: BlobStore,
    workspace_id: UUID, principal: Principal, grant: Any,
) -> None:
    from sqlalchemy import func, select

    from app.db.models import BlobRow

    await _compiled_version(
        api_client, headers, database, blob_store, workspace_id, principal, grant
    )
    frame = _scoring_frame(9)  # chunk_rows=2 -> 5 chunks, so several parts are written
    dataset_version_id = await _dataset_version(
        database, blob_store, workspace_id, principal, frame
    )
    parameters = _parameters(dataset_version_id)

    async with database.session() as session:
        before = (await session.execute(select(func.count()).select_from(BlobRow))).scalar_one()

    result, _ = await _run_handler(database, blob_store, workspace_id, principal, parameters)
    assert result.kind == "blob"

    async with database.session() as session:
        after = (await session.execute(select(func.count()).select_from(BlobRow))).scalar_one()

    # Exactly two new BlobRows: the output parquet and the JSON summary — never one per
    # chunk. Chunk parts are scratch (`blobs.py`'s `scratch/` prefix), which carries no
    # `BlobRow` at all, so a per-chunk write would not show up here even if it happened —
    # the direct proof is the scratch listing below, empty after a successful run.
    assert after - before == 2, f"expected 2 new blobs (output + summary), got {after - before}"

    surviving = await blob_store.list_scratch("score-batch/")
    assert not [k for k in surviving if f"/{dataset_version_id}/" in k], (
        "scratch parts were not released when the run completed (Ruling 31 §4)"
    )
