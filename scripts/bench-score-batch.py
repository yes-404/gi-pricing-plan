#!/usr/bin/env python3
"""Measure NFR-493 — batch scoring throughput per worker (WK-671 Slice 3, Task 3D).

`docs/specs/03-rating-engine.md` §9: *"Batch scoring ≥ 1 M risks/hour per worker
(NFR-455), linear in workers."* This measures the **handler**
(`app.worker.scoring_handlers._score_batch_handler`), not the route: `POST
/api/v1/score/batch` (Task 3C) only submits a Job, and a route's own HTTP overhead is not
this component's cost — the same reason `bench-rating.py` measures `score_one` directly
and `bench-compiled-for.py` measures `_compiled_for` directly rather than through FastAPI.

**Fixture: no `model_call` step.** `_algorithm_payload` below is `bench-compiled-for.py`'s
own minimal shape (one `int` input, one expression step) — a single Rating Version pin,
no rate table, no GBM booster to train. This is a deliberate, disclosed simplification, not
an attempt to make the number pass: NFR-493's own budget is about the batch **pipeline**
(chunking, the manifest, scratch I/O, the final parquet write) at scale, and per-row
algorithm cost is NFR-489/490's budget, already measured separately in `bench-rating.py`
against a ~200-step motor structure. A reader who wants the two costs combined multiplies
this script's per-row overhead estimate by NFR-489's own per-row figure; this script does
not do that arithmetic for them, because it has not measured the with-GBM case itself.

Real Postgres and MinIO, exactly as production runs: the handler does real I/O (a
version-row read, a dataset-table blob read, one scratch write/read per chunk, one final
blob write), so a fixture with no I/O would not be measuring what NFR-493 asks about.

    docker compose -f deploy/docker-compose.yml up -d --wait
    GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing \
        uv run alembic upgrade head
    uv run python scripts/bench-score-batch.py [--rows N] [--chunk-rows N]

Not a CI gate, RL-872's governance carried over unchanged (`docs/rulings/RL-00872-dp3-
load-generation-tooling-for-the-sustained-200-rps-test.md`): a timing assertion on a shared runner fails for reasons that have
nothing to do with the code. This prints numbers for a dated research note; a human reads
them once against the budget, and a failing number is reported as failing, not tuned away
(`CLAUDE.md` §13).
"""

from __future__ import annotations

import argparse
import asyncio
import io
import os
import time
from datetime import date
from uuid import UUID

import polars as pl

from app.config import Settings
from app.db.models import DatasetVersionRow, RatingVersionRow
from app.db.session import Database
from app.platform import jobs as job_service
from app.platform.blobs import BlobStore
from app.platform.rating_algorithms import create_algorithm
from app.platform.rating_versions import compile_rating_version, record_bundle_blob
from app.worker.progress import JobProgress
from app.worker.scoring_handlers import _score_batch_handler
from model_schema import ActorKind, JobKind, JobResult, Principal, new_uuid7
from model_schema.refs import ArtifactRef

DEFAULT_DSN = os.environ.get(
    "GIP_DATABASE_URL",
    "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing",
)
BUCKET = os.environ.get("GIP_BLOB_BUCKET", "gip-bench-score-batch")

_SLUG = "bench-score-batch"
_REF = ArtifactRef.model_validate(f"rating_version:{_SLUG}@1")


def _algorithm_payload() -> dict:
    """`bench-compiled-for.py`'s own minimal shape, replicated (module docstring: no
    `model_call`, one `int` input) — see the module docstring for why this fixture, not a
    richer one, is the honest choice for a pipeline-throughput measurement."""
    return {
        "slug": _SLUG,
        "version": 1,
        "input_contract": [{"name": "premium_in", "type": "int", "nullable": False}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": "premium_in",
             "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_expr", "type": "expression", "label": "Apply",
             "expr": "premium_in * 2", "result_type": "money_minor",
             "consumes": ["premium_in"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor",
             "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


async def _setup(database: Database, blob_store: BlobStore) -> UUID:
    """One workspace, one compiled Rating Version reachable at `_REF`. Mirrors
    `bench-compiled-for.py`'s `_setup`."""
    workspace_id = new_uuid7()
    created_by = new_uuid7()

    await create_algorithm(database, workspace_id, created_by, _algorithm_payload())

    row = RatingVersionRow(
        workspace_id=workspace_id, slug=_SLUG, version=1, status="draft",
        dataset_version_id=new_uuid7(), model_ref="model:motor-ad-frequency@7",
        created_by=created_by, algorithm_ref=f"rating_algorithm:{_SLUG}@1",
        pins={"rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": []},
    )
    async with database.unit_of_work() as session:
        session.add(row)
        await session.flush()
        rating_version_id = row.id

    async with database.unit_of_work() as session:
        bundle = await compile_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_version_id,
            blob_store=blob_store,
        )
        payload = bundle.model_dump_json().encode()
        ref = await blob_store.put(session, payload, "application/json")
        await record_bundle_blob(
            session, workspace_id=workspace_id, rating_version_id=rating_version_id,
            blob_sha256=ref.sha256,
        )

    return workspace_id


def _scoring_frame(n: int) -> pl.DataFrame:
    """`03` §4.8's four reserved columns plus `_algorithm_payload`'s single input —
    `test_scoring_handlers.py`'s own `_scoring_frame` shape, vectorised for a large `n`
    (a Python-level loop over hundreds of thousands of rows would put fixture-construction
    time inside what looks like a throughput number if it were not built before timing
    starts — it is, but vectorising keeps total script wall time reasonable regardless)."""
    idx = pl.int_range(0, n, eager=True)
    return pl.DataFrame(
        {
            "quote_id": ("Q" + idx.cast(pl.Utf8).str.zfill(9)),
            "purpose": pl.repeat("new_business", n, eager=True),
            "effective_date": pl.repeat(date(2026, 9, 1).isoformat(), n, eager=True),
            "rating_version_ref": pl.repeat("rating_version:placeholder@0", n, eager=True),
            "premium_in": (idx % 1000) + 100,
        }
    )


async def _dataset_version(
    database: Database, blob_store: BlobStore, workspace_id: UUID, frame: pl.DataFrame
) -> UUID:
    buffer = io.BytesIO()
    frame.write_parquet(buffer, compression="zstd")
    async with database.unit_of_work() as session:
        blob_ref = await blob_store.put(session, buffer.getvalue(), "application/x-parquet")
        row = DatasetVersionRow(
            slug="bench-score-batch-fixture",
            workspace_id=workspace_id,
            dataset_id=new_uuid7(),
            version=1,
            status="draft",
            created_by=new_uuid7(),
            currency="GBP",
            tables=[{"name": "scoring_frame", "blob": {"sha256": blob_ref.sha256}}],
        )
        session.add(row)
        await session.flush()
        return row.id


async def _time_handler(
    database: Database, blob_store: BlobStore, workspace_id: UUID,
    dataset_version_id: UUID, *, chunk_rows: int,
) -> tuple[float, JobResult]:
    """One `score.batch` run, timed end to end — the handler's own wall clock, the same
    unit of work a Celery worker actually performs per Job. Job submission and
    `JobProgress` construction are excluded from the timed block (they are per-Job
    bookkeeping, not per-row scoring work); everything from the first row read onward is
    inside it."""
    principal = Principal(kind=ActorKind.SYSTEM, id=None, display="bench-score-batch")
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.SCORE_BATCH,
            {
                "workspace_id": str(workspace_id),
                "actor": principal.model_dump(mode="json"),
                "dataset_version_id": str(dataset_version_id),
                "rating_version_refs": [str(_REF)],
                "chunk_rows": chunk_rows,
            },
            principal,
            workspace_id=workspace_id,
        )
    loop = asyncio.get_running_loop()
    progress = JobProgress(job.id, database, loop, blob_store=blob_store)
    full_parameters = dict(job.parameters) | {"job_id": str(job.id)}

    t0 = time.perf_counter()
    result = await asyncio.to_thread(_score_batch_handler, full_parameters, progress)
    elapsed = time.perf_counter() - t0
    return elapsed, result


def _git_head() -> str:
    import subprocess

    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception as exc:  # pragma: no cover - diagnostic path only
        return f"(unavailable: {exc})"


def _loadavg() -> float:
    with open("/proc/loadavg") as handle:
        return float(handle.read().split()[0])


def _host_summary() -> str:
    import platform

    return f"{platform.processor() or platform.machine()}, {os.cpu_count()} cores"


async def main(n_rows: int, chunk_rows: int, warmup_rows: int) -> None:
    database = Database(Settings(database_url=DEFAULT_DSN))
    blob_store = BlobStore(Settings(database_url=DEFAULT_DSN, blob_bucket=BUCKET))
    await blob_store.ensure_bucket()

    workspace_id = await _setup(database, blob_store)

    print(f"tree: {_git_head()}")
    print(f"host: {_host_summary()}")
    print("pass count: 1 (one run of this script; warmup below is excluded from the figure)")
    print("row width: 1 input column (premium_in), no model_call -- see module docstring")
    print(f"chunk_rows: {chunk_rows}")
    print()

    if warmup_rows:
        warmup_dvid = await _dataset_version(
            database, blob_store, workspace_id, _scoring_frame(warmup_rows)
        )
        warmup_elapsed, _ = await _time_handler(
            database, blob_store, workspace_id, warmup_dvid, chunk_rows=chunk_rows
        )
        print(f"warmup: {warmup_rows} rows in {warmup_elapsed:.3f} s (excluded)")

    load_start = _loadavg()
    dataset_version_id = await _dataset_version(
        database, blob_store, workspace_id, _scoring_frame(n_rows)
    )
    elapsed, result = await _time_handler(
        database, blob_store, workspace_id, dataset_version_id, chunk_rows=chunk_rows
    )
    load_end = _loadavg()

    rows_per_hour = n_rows / elapsed * 3600
    print(f"load average (1-min): {load_start:.2f} -> {load_end:.2f}")
    print(f"measured: {n_rows} rows in {elapsed:.3f} s ({n_rows / elapsed:.1f} rows/s)")
    print(f"throughput: {rows_per_hour:,.0f} risks/hour/worker")
    print("budget (NFR-493): >= 1,000,000 risks/hour/worker")
    verdict = "PASS" if rows_per_hour >= 1_000_000 else "FAIL"
    print(f"verdict: {verdict}")
    print(
        "single worker only -- 'linear in workers' is NOT measured by this run "
        "(NFR-493's second clause; would need >= 2 concurrent workers)"
    )
    print(f"job result kind: {result.kind}")

    await database.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=300_000, help="rows in the measured run")
    parser.add_argument("--chunk-rows", type=int, default=50_000, help="score_batch chunk size")
    parser.add_argument(
        "--warmup-rows", type=int, default=5_000,
        help="rows in a discarded warmup run first (0 to skip)",
    )
    args = parser.parse_args()
    asyncio.run(main(args.rows, args.chunk_rows, args.warmup_rows))
