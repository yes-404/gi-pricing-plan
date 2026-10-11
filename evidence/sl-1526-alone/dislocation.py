"""SL-1526 ALONE stage d: the dislocation + attribution run over the 20,000-policy sample (PL-1577 DP-2).

Usage: dislocation.py <slice worktree> <seed record json>     (env: GIP_DATABASE_URL = a THROWAWAY copy of the demo DB)
Ruled by the maintainer, to-lead "2026-10-11 16:37:21 BST" (option A), measurement scope "16:34:21 BST".

`scripts/demo.py` runs no dislocation, and the seed leaves ONE rating version with nothing to compare it to. This builds
the baseline the demo lacks, **a measurement fixture, not a seeded version**:
  baseline  = rating_version fremtpl2-demo@2: the same algorithm re-priced +1.95% (algorithm fremtpl2-rate@2, the stored
              @1 content with its `s_base` constant x 1.0195, half-even), the same pins and model, compiled by the
              `rating.compile` Job. It is a DRAFT: `dislocation.run` needs only a compiled bundle (`_compiled`), and
              the approval path (a regression suite with re-priced golden quotes, two approvers) adds nothing a
              dislocation measures. This deviates from "via the seed's approval path"; the report says so.
  candidate = the seeded fremtpl2-demo@1.
Then `dislocation.run` runs as a Job via `execute_job` IN-PROCESS (the pattern of model._run_job), over the portfolio
Dataset Version the seed wrote, attribution included (one job kind). The handler is the Celery worker's own; only the
process differs. Prints START/END per limb, the job wall as `JOBWALL_DISLOCATION <s>`, and STOP lines on any refusal.
"""
from __future__ import annotations

import asyncio
import copy
import json
import sys
import time
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path
from uuid import UUID

W = Path(sys.argv[1])
sys.path.insert(0, str(W / "examples" / "fremtpl2"))

from sqlalchemy import select  # noqa: E402

import model as demo_model  # noqa: E402
from app.config import load_settings  # noqa: E402
from app.db.models import JobRow, RatingAlgorithmRow, RatingVersionRow  # noqa: E402
from app.db.session import Database  # noqa: E402
from app.platform import jobs as job_service  # noqa: E402
from app.platform import rating_algorithms as algorithm_service  # noqa: E402
from app.platform import rating_versions as rv_service  # noqa: E402
from app.platform.blobs import BlobStore  # noqa: E402
from app.worker.dislocation_handlers import register_dislocation_handlers  # noqa: E402
from app.worker.rating_handlers import register_rating_handlers  # noqa: E402
from app.worker.tasks import execute_job  # noqa: E402
from model_schema import ArtifactRef, JobKind, JobStatus, Principal  # noqa: E402
from model_schema.dislocation import DislocationSpec  # noqa: E402

REPRICE = Decimal("1.0195")


def reprice(content: dict, next_version: int) -> tuple[dict, Decimal, Decimal]:
    """The stored algorithm content with its `s_base` constant x 1.0195 (half-even, whole minor units), as version
    `next_version`; returns (new content, old base, new base). Pure, so a proof can run it without a database."""
    out = copy.deepcopy(content)
    step = next(st for st in out["steps"] if st["step_id"] == "s_base")
    old = Decimal(step["expr"])
    new = (old * REPRICE).quantize(Decimal(1), rounding=ROUND_HALF_EVEN)
    step["expr"] = str(new)
    out["version"] = next_version
    return out, old, new


def now() -> str:
    return datetime.now(UTC).astimezone().isoformat(timespec="seconds")


def stop(msg: str) -> int:
    print(f"STOP: {msg}")
    return 4


async def poll(database: Database, job_id: UUID, seen: list[tuple[str, str]], quit_: asyncio.Event) -> None:
    """Best-effort limb stamps: every distinct progress stage the Job row shows (writes are throttled, so a
    short stage can be missed; the Job's own start and finish are printed regardless)."""
    last = None
    while not quit_.is_set():
        async with database.session() as s:
            row = await s.get(JobRow, job_id)
        stage = (row.progress or {}).get("stage") if row is not None else None
        if stage and stage != last:
            seen.append((stage, now()))
            print(f"LIMB {stage} first seen {now()} (progress {row.progress})", flush=True)
            last = stage
        await asyncio.sleep(2)


async def main() -> int:
    rec = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    ws = UUID(rec["workspace_id"])
    portfolio = UUID(rec["portfolio_dataset_version_id"])
    settings = load_settings()
    database, blobs = Database(settings), BlobStore(settings)
    register_rating_handlers()
    register_dislocation_handlers()
    analyst = Principal(kind="user", id=UUID(rec["analyst_id"]), display="analyst@example.fr")

    print(f"LIMB baseline-fixture START {now()}", flush=True)
    async with database.session() as s:
        cand = (await s.execute(select(RatingVersionRow).where(
            RatingVersionRow.workspace_id == ws, RatingVersionRow.slug == demo_model.DEMO_RATING_SLUG,
            RatingVersionRow.version == 1))).scalar_one()
        cand_schema = rv_service.to_schema(cand)
        alg_ref = ArtifactRef.model_validate(cand.algorithm_ref)
        alg = (await s.execute(select(RatingAlgorithmRow).where(
            RatingAlgorithmRow.workspace_id == ws, RatingAlgorithmRow.slug == alg_ref.slug,
            RatingAlgorithmRow.version == alg_ref.version))).scalar_one()
        content = copy.deepcopy(alg.content)
    content, old, new = reprice(content, alg_ref.version + 1)
    print(f"fixture: base premium {old} -> {new} minor units (x{REPRICE}); "
          f"algorithm {alg_ref.slug}@{alg_ref.version} -> @{content['version']}; "
          "label: a measurement fixture, not a seeded version", flush=True)
    await algorithm_service.create_algorithm(database, ws, analyst.id, content)
    async with database.unit_of_work() as s:
        row = await rv_service.create_rating_version(
            s, workspace_id=ws, actor=analyst, slug=demo_model.DEMO_RATING_SLUG,
            dataset_version_id=cand_schema.dataset_version_id, model_ref=cand_schema.model_ref,
            algorithm_ref=ArtifactRef(type="rating_algorithm", slug=alg_ref.slug, version=content["version"]),
            pins=cand_schema.pins, model_reference_mode=cand_schema.model_reference_mode)
        baseline_id, baseline_version = row.id, row.version
    status = await demo_model._run_job(database, blobs, ws, analyst, JobKind.RATING_COMPILE,
                                       {"rating_version_id": str(baseline_id)})
    print(f"LIMB baseline-fixture END {now()} compile job {status}", flush=True)
    if status is not JobStatus.SUCCEEDED:
        return stop(f"the baseline fixture's compile Job ended {status}")

    spec = DislocationSpec(
        baseline_ref=ArtifactRef(type="rating_version", slug=demo_model.DEMO_RATING_SLUG, version=baseline_version),
        candidate_ref=ArtifactRef(type="rating_version", slug=demo_model.DEMO_RATING_SLUG, version=1),
        portfolio_dataset_version_id=portfolio, purpose="new_business", as_at=date(2026, 10, 1),
        band_edges_pct=["-10", "-5", "0", "5", "10"], mover_threshold_pct="10")
    async with database.unit_of_work() as s:
        job = await job_service.submit(
            s, JobKind.DISLOCATION_RUN,
            {"workspace_id": str(ws), "actor": analyst.model_dump(mode="json"), "spec": spec.model_dump(mode="json")},
            analyst, workspace_id=ws)
        job_id = job.id
    seen: list[tuple[str, str]] = []
    quit_ = asyncio.Event()
    poller = asyncio.create_task(poll(database, job_id, seen, quit_))
    print(f"LIMB dislocation.run (incl. attribution) START {now()} job {job_id} "
          f"baseline {spec.baseline_ref} candidate {spec.candidate_ref} portfolio {portfolio}", flush=True)
    t0 = time.monotonic()
    status = await execute_job(database, job_id, blobs)
    wall = time.monotonic() - t0
    quit_.set()
    await poller
    print(f"LIMB dislocation.run (incl. attribution) END {now()} status {status}", flush=True)
    async with database.session() as s:
        row = await s.get(JobRow, job_id)
    print(f"job row: status={row.status} started_at={row.started_at} finished_at={row.finished_at} "
          f"result={row.result} error={row.error}")
    print(f"limb stages seen: {seen or 'none (progress writes throttled)'}")
    print(f"JOBWALL_DISLOCATION {wall:.1f}")
    await database.dispose()
    if status is not JobStatus.SUCCEEDED:
        return stop(f"dislocation.run ended {status}: {row.error}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
