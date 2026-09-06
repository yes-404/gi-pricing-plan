#!/usr/bin/env python3
"""Component-level delta: `_compiled_for` on a slot hit vs. the full blob-read path
(RL-921 §2's fix, measured per RL-922 §4 — WK-671 Slice 3, Task 3B).

**This is not an NFR-489 re-measurement, and no output of this script may be read as
one** (RL-922 §6). It does not run at 200 rps, it does not run on a dedicated host, and
a result here does not arm RL-921 §4's 15 ms trigger. What it measures is the ratio
RL-921 §2 predicted: on a slot hit, `_compiled_for` skips the blob primary-key lookup,
the object-store read and `Bundle.model_validate_json` entirely, because the content hash
`row.bundle` carries is checked against the slot before any of those three run. What it
does not skip, ever: the version-row `SELECT` — RL-921 §2 keeps that on the hot path on
purpose, so a recompile is visible on the very next request.

**`bundle_slot_capacity` is not raised** — it stays the shipped default of 1 (RL-921 §4
left it unset; raising it needs its own latency-harness evidence this script does not
produce). **Ref cardinality is 1** — one compiled Rating Version, scored against
repeatedly. RL-921 §4's own note: *"with capacity 1 and more than one ref in play the
slot thrashes and every request pays the full path"* — this script's numbers describe the
single-ref workload it runs, not a multi-tenant one.

Two conditions, same tree, same host, same run, same compiled bundle:

- **hit**: one `BundleSlot`, pre-warmed by a first call, then `n` repeat calls against the
  same ref. Every call after the first is a genuine slot hit on a freshly re-read hash.
- **full path**: a fresh `BundleSlot()` per call, forcing a cold miss every time — the path
  every request paid before RL-921 §2, and what a first-ever request to a worker still
  pays today.

No HTTP, no FastAPI — `_compiled_for` measured directly, the same reason `bench-rating.py`
measures `score_one` directly rather than through a route: a route's own overhead is not
this component's cost.

    docker compose -f deploy/docker-compose.yml up -d --wait
    GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing \\
        uv run alembic upgrade head
    uv run python scripts/bench-compiled-for.py [--calls N]

Not a CI gate, RL-872's governance carried over unchanged: a timing assertion on a shared
runner fails for reasons that have nothing to do with the code. This prints numbers for a
research note; a human reads them once against the ruling's own boundary, not a budget.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import statistics
import time
from uuid import UUID

from app.api.score import _compiled_for
from app.config import Settings
from app.db.models import RatingVersionRow
from app.db.session import Database
from app.platform.blobs import BlobStore
from app.platform.bundle_slot import BundleSlot
from app.platform.rating_algorithms import create_algorithm
from app.platform.rating_versions import (
    compile_rating_version,
    record_bundle_blob,
)
from model_schema import new_uuid7
from model_schema.refs import ArtifactRef

DEFAULT_DSN = os.environ.get(
    "GIP_DATABASE_URL",
    "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing",
)
BUCKET = os.environ.get("GIP_BLOB_BUCKET", "gip-bench-compiled-for")


def _algorithm_payload() -> dict:
    """Mirrors `backend/tests/test_rating_version_compile.py`'s `_minimal_algorithm` —
    no external artifact refs, so this script needs no rate table or model fixture."""
    return {
        "slug": "bench-compiled-for",
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


async def _setup(database: Database, blob_store: BlobStore) -> tuple[UUID, ArtifactRef]:
    """One workspace, one compiled Rating Version. Returns (workspace_id, ref)."""
    workspace_id = new_uuid7()
    created_by = new_uuid7()

    await create_algorithm(database, workspace_id, created_by, _algorithm_payload())

    row = RatingVersionRow(
        workspace_id=workspace_id, slug="bench-compiled-for", version=1, status="draft",
        dataset_version_id=new_uuid7(), model_ref="model:motor-ad-frequency@7",
        created_by=created_by, algorithm_ref="rating_algorithm:bench-compiled-for@1",
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

    return workspace_id, ArtifactRef.model_validate("rating_version:bench-compiled-for@1")


async def _time_calls(
    database: Database, blob_store: BlobStore, slot: BundleSlot, *,
    workspace_id: UUID, ref: ArtifactRef, n: int, fresh_slot_per_call: bool,
) -> list[float]:
    samples: list[float] = []
    for _ in range(n):
        call_slot = BundleSlot() if fresh_slot_per_call else slot
        t0 = time.perf_counter()
        await _compiled_for(database, blob_store, call_slot, workspace_id=workspace_id, ref=ref)
        samples.append((time.perf_counter() - t0) * 1000)
    return samples


def _git_head() -> str:
    import subprocess

    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception as exc:  # pragma: no cover - diagnostic path only
        return f"(unavailable: {exc})"


def _host_summary() -> str:
    import platform

    load = os.getloadavg() if hasattr(os, "getloadavg") else None
    return (
        f"{platform.processor() or platform.machine()}, {os.cpu_count()} cores, "
        f"1-min load {load[0] if load else 'unavailable'}"
    )


def _p99(samples: list[float]) -> float:
    return statistics.quantiles(samples, n=100, method="inclusive")[98]


def _report(label: str, samples: list[float]) -> None:
    print(
        f"{label:>10} | n={len(samples):3d} mean={statistics.mean(samples):8.3f} ms  "
        f"p50={statistics.median(samples):8.3f} ms  p99={_p99(samples):8.3f} ms  "
        f"max={max(samples):8.3f} ms"
    )


async def main(n: int) -> None:
    database = Database(Settings(database_url=DEFAULT_DSN))
    blob_store = BlobStore(Settings(database_url=DEFAULT_DSN, blob_bucket=BUCKET))
    await blob_store.ensure_bucket()

    workspace_id, ref = await _setup(database, blob_store)

    warm_slot = BundleSlot()
    # Prime it: the first call is always a miss regardless of condition, so it is excluded
    # from both reported distributions rather than silently pulled into the "hit" one.
    await _compiled_for(database, blob_store, warm_slot, workspace_id=workspace_id, ref=ref)

    hit_samples = await _time_calls(
        database, blob_store, warm_slot, workspace_id=workspace_id, ref=ref,
        n=n, fresh_slot_per_call=False,
    )
    full_path_samples = await _time_calls(
        database, blob_store, warm_slot, workspace_id=workspace_id, ref=ref,
        n=n, fresh_slot_per_call=True,
    )

    print(f"tree: {_git_head()}")
    print(f"host: {_host_summary()}")
    print(f"pass count: 1 (one run of this script; each condition below is {n} calls in it)")
    print("ref cardinality: 1 (one compiled Rating Version, bundle_slot_capacity=1, unraised)")
    print()
    _report("hit", hit_samples)
    _report("full path", full_path_samples)
    print()
    print(
        f"delta (mean): {statistics.mean(full_path_samples) - statistics.mean(hit_samples):.3f} ms"
    )
    print(
        "NOT an NFR-489 re-measurement (RL-922 §6) — component delta of RL-921 §2's "
        "own predicate only."
    )

    await database.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calls", type=int, default=200, help="calls per condition")
    args = parser.parse_args()
    asyncio.run(main(args.calls))
