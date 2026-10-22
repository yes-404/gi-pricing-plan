#!/usr/bin/env python3
"""WK-1178 / SL-1736 / PL-1735: the P2 NFR measurement sweep harness.

    uv run python scripts/measure-p2-nfr-sweep.py contention run --role A --out FILE
    uv run python scripts/measure-p2-nfr-sweep.py contention summarize FILE
    uv run python scripts/measure-p2-nfr-sweep.py --help

One committed instrument per NFR (PL-1735): `contention` (Task 0, the load factor of this box),
then `one-way` (NFR-468), `storage` (NFR-470), `cells-diff` (NFR-1443) and `profile`
(NFR-467). NFR-485's instrument is `bench-model.py --peak hwm`. Every reading is
DIAGNOSTIC on the shared VM and every latency figure is labelled LATENCY_LABEL (DP-2).

**The thresholds, bands and reading rules are module-level constants, committed before the
first run that uses them** (PL-1735 Global Constraints: pre-register before measuring). A
change is a new commit and a re-run, both recorded in the ledger. The decision logic is pure and
unit-tested by `tests/test_measure_p2_nfr_sweep.py`; the timed phases are run alone, in a held
gate slot, by a lead-granted window, never inside a gate.

Instrument rules (PL-1735): timers at request boundaries only; no profiler, no asyncio debug
mode, no sampler or poller thread during a timed phase; memory is the kernel's `VmHWM` read
after the phase, one phase per process.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

# =============================================================================================
# Pre-registered constants. P0 = the commit that first carries this block; the ledger cites it.
# =============================================================================================

#: DP-2: on every NFR-468 and NFR-1443 figure.
LATENCY_LABEL = "server-side, in-process, excludes network"

# --- Task 0: the contention factor (DP-1, "2026-10-14 12:25:22 BST", regime confirmed 12:31:22)
#: The fixed benchmark: `bench-model.py --only proposals` at its defaults (678 013 rows,
#: --levels 10000, --groups 20); only the line below is read. Its tree is the commit.
CONTENTION_ARGS = ("scripts/bench-model.py", "--only", "proposals")
CONTENTION_LABEL = "NFR-477 propose_grouping hierarchical_clustering"
#: ALONE run (A): load1 at start strictly below this.
ALONE_LOAD_BELOW = 1.0
#: Contended run (B): load1 at start in [lo, hi) ...
CONTENDED_LOAD_START = (1.0, 2.0)
#: ... and at end strictly below this. A run outside its regime is excluded and re-run.
CONTENDED_LOAD_END_BELOW = 2.0
MIN_PAIRS = 3
#: D4 (GO "2026-10-22 11:53:15 BST"): an ALONE start may settle this long, then STOP to the lead.
ALONE_SETTLE_MAX_S = 600
SETTLE_POLL_S = 15

# --- The sweep's thresholds and reading rules (DP-1, DP-3, the NFR sections of PL-1735)
#: Interim DP-1 band, accepted 12:25:22 (ii) as the conservative rounding of 1/2.3. Replaced by
#: `band_from_factor(max factor)` once Task 0's reading is in the ledger (commit P1).
NEAR_BOUND_FRACTION = 0.43
#: Budgets in ms (NFR-468: p95 < 300 ms; NFR-1443: page p95 <= 300 ms; NFR-467: 300 s).
THRESHOLDS_MS = {"NFR-468": 300.0, "NFR-1443": 300.0, "NFR-467": 300_000.0}
#: NFR-1443's p95(250 000) / p95(10 000) bands: <= 1.5 PASS, <= 2.0 NEAR-BOUND, above OVER.
RATIO_BANDS = (1.5, 2.0)
#: NFR-470 (DP-3 (b)): (payload + overhead) / payload <= 1.2, source upload excluded; dedup = 0
#: new parquet bytes for the identical table.
NFR_470_RULE = {"ratio_max": 1.2, "dedup_new_bytes": 0, "source_upload_excluded": True}
#: NFR-467 at 10 M (12:42:55 entry; r < 5.0 accepted 13:21:41 as DERIVED from "sub-linear").
NFR_467_RULE = {
    "sizes": [2_000_000, 10_000_000],
    "columns": 80,
    "time_budget_s": 300,
    "memory_ratio_below": 5.0,
    "mem_available_min_gb": 16,
    "disk_free_min_gb": 12,
}
#: NFR-485: peak VmHWM <= 32 GiB at 5 M x 60 (a projection is never read as a verdict).
NFR_485_CAP_BYTES = 32 * 2**30
#: NFR-468 / NFR-1443 request counts.
NFR_468_WARMUP, NFR_468_N = 20, 200
NFR_1443_N, NFR_1443_LIMIT, NFR_1443_SEEDED_JOBS = 100, 50, 10_000

# =============================================================================================
# Pure decision logic (unit-tested)
# =============================================================================================


def run_validity(role: str, load_start: float, load_end: float) -> tuple[bool, str]:
    """Is a contention run inside its regime? Returns (valid, reason); reason is "" if valid."""
    if role == "A":
        if load_start < ALONE_LOAD_BELOW:
            return True, ""
        return False, f"ALONE start load1 {load_start} >= {ALONE_LOAD_BELOW}"
    if role == "B":
        lo, hi = CONTENDED_LOAD_START
        if not lo <= load_start < hi:
            return False, f"contended start load1 {load_start} outside [{lo}, {hi})"
        if not load_end < CONTENDED_LOAD_END_BELOW:
            return False, f"contended end load1 {load_end} >= {CONTENDED_LOAD_END_BELOW}"
        return True, ""
    raise ValueError(f"role must be A or B, not {role!r}")


def band_from_factor(factor: float) -> float | None:
    """DP-1: the band is 1 / factor rounded DOWN to 2 decimals; a factor <= 1 gives none."""
    if factor <= 1.0:
        return None
    return math.floor(100 / factor) / 100


def contention_factor(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Pair interleaved A, B runs and return the factor (the MAX of the per-pair B/A wall ratios).

    An invalid run is excluded (never paired). Each valid A pairs with the next valid B; a valid
    A replaced by a later A before any B, and a valid B with no pending A, are reported as
    unpaired, never dropped silently.
    """
    excluded: list[dict[str, Any]] = []
    unpaired: list[dict[str, Any]] = []
    ratios: list[float] = []
    pending: dict[str, Any] | None = None
    for run in runs:
        ok, reason = run_validity(run["role"], run["load_start"], run["load_end"])
        if not ok:
            excluded.append({**run, "reason": reason})
            continue
        if run["role"] == "A":
            if pending is not None:
                unpaired.append(pending)
            pending = run
        else:
            if pending is None:
                unpaired.append(run)
                continue
            ratios.append(run["wall_s"] / pending["wall_s"])
            pending = None
    if pending is not None:
        unpaired.append(pending)
    result: dict[str, Any] = {
        "pairs": len(ratios),
        "ratios": ratios,
        "excluded": excluded,
        "unpaired": unpaired,
        "factor": None,
        "min": None,
        "spread": None,
        "band": None,
        "note": "",
    }
    if len(ratios) < MIN_PAIRS:
        result["note"] = f"fewer than {MIN_PAIRS} pairs: no factor"
        return result
    result["factor"] = max(ratios)
    result["min"] = min(ratios)
    result["spread"] = max(ratios) - min(ratios)
    result["band"] = band_from_factor(max(ratios))
    if result["band"] is None:
        result["note"] = "factor <= 1.0: band reported to the lead, not applied"
    return result


_BENCH_LINE = re.compile(re.escape(CONTENTION_LABEL) + r"\s+([\d.]+) s wall\s+([\d.]+) s cpu")


def parse_bench_line(output: str) -> tuple[float, float]:
    """(wall seconds, cpu seconds) of the named benchmark line in `bench-model.py`'s output."""
    found = _BENCH_LINE.search(output)
    if found is None:
        raise ValueError(f"no {CONTENTION_LABEL!r} line in the benchmark output")
    return float(found.group(1)), float(found.group(2))


def classify_latency(value: float, *, budget: float, fraction: float) -> str:
    """DP-1: <= fraction x budget PASS; above it and <= budget NEAR-BOUND; above budget OVER."""
    if value <= fraction * budget:
        return "DIAGNOSTIC-PASS"
    if value <= budget:
        return "NEAR-BOUND"
    return "DIAGNOSTIC-OVER"


def classify_ratio(ratio: float) -> str:
    """NFR-1443's 2x property: its own bands, since contention can move it either way."""
    lo, hi = RATIO_BANDS
    if ratio <= lo:
        return "DIAGNOSTIC-PASS"
    if ratio <= hi:
        return "NEAR-BOUND"
    return "DIAGNOSTIC-OVER"


def nearest_rank(values: list[float], percentile: float) -> float:
    """Nearest-rank percentile: the value at rank ceil(p/100 x n) of the sorted sample."""
    if not values:
        raise ValueError("nearest_rank of an empty sample")
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile / 100 * len(ordered)))
    return ordered[rank - 1]


def classify_storage(payload: int, overhead: int, dedup_new_bytes: int) -> str:
    """NFR-470 (DP-3 (b)): (payload + overhead) / payload <= 1.2 and dedup adds 0 new bytes."""
    if payload <= 0:
        raise ValueError("NFR-470 needs a positive parquet payload")
    ok = (payload + overhead) * 10 <= payload * 12 and (
        dedup_new_bytes == NFR_470_RULE["dedup_new_bytes"]
    )
    return "DIAGNOSTIC-PASS" if ok else "DIAGNOSTIC-OVER"


def memory_ratio(delta_large: float, delta_small: float) -> float:
    """NFR-467: r = delta-peak(10 M) / delta-peak(2 M)."""
    if delta_small <= 0:
        raise ValueError("the 2 M delta-peak must be positive")
    return delta_large / delta_small


def classify_nfr467_memory(ratio: float) -> str:
    """r < 5.0 is sub-linear (the row's amendment); r >= 5.0 is OVER."""
    return "PASS" if ratio < NFR_467_RULE["memory_ratio_below"] else "OVER"


def classify_nfr485(vmhwm_bytes: int) -> str:
    return "PASS" if vmhwm_bytes <= NFR_485_CAP_BYTES else "OVER"


def parse_status_kb(text: str, key: str) -> int:
    """A `/proc/<pid>/status` field in bytes (the file reports kB)."""
    for line in text.splitlines():
        if line.startswith(key + ":"):
            return int(line.split()[1]) * 1024
    raise ValueError(f"{key} not in the status text")


# =============================================================================================
# Host readings
# =============================================================================================


def read_load1() -> float:
    with open("/proc/loadavg") as handle:
        return float(handle.read().split()[0])


def read_status_bytes(key: str) -> int:
    with open("/proc/self/status") as handle:
        return parse_status_kb(handle.read(), key)


def mem_available_gb() -> float:
    with open("/proc/meminfo") as handle:
        for line in handle:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 2**20
    raise ValueError("MemAvailable not in /proc/meminfo")


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()


def session_header() -> dict[str, Any]:
    """PL-1735 Task 0 Step 5: what every session records at its start and end."""

    def run(*cmd: str) -> str:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

    return {
        "head": git_head(),
        "tree": run("git", "-C", str(ROOT), "rev-parse", "HEAD^{tree}"),
        "nproc": os.cpu_count(),
        "loadavg": open("/proc/loadavg").read().strip(),
        "meminfo_available_gb": round(mem_available_gb(), 2),
        "pgrep": run("pgrep", "-af", "[p]ytest|[v]itest|[f]lock"),
        "at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }


# =============================================================================================
# Task 0: the contention subcommand
# =============================================================================================


def _contention_run(role: str, out: Path) -> int:
    if role == "A":
        waited = 0
        while read_load1() >= ALONE_LOAD_BELOW and waited < ALONE_SETTLE_MAX_S:
            time.sleep(SETTLE_POLL_S)
            waited += SETTLE_POLL_S
        if read_load1() >= ALONE_LOAD_BELOW:
            print(
                f"STOP: load1 {read_load1()} >= {ALONE_LOAD_BELOW} after {waited} s of settling "
                "(D4: record the reading and report to the lead; no run taken)"
            )
            return 3
    head = git_head()
    load_start = read_load1()
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    proc = subprocess.run(
        [sys.executable, *CONTENTION_ARGS], cwd=ROOT, capture_output=True, text=True
    )
    load_end = read_load1()
    if proc.returncode != 0:
        print(proc.stdout, proc.stderr, sep="\n")
        return proc.returncode
    wall, cpu = parse_bench_line(proc.stdout)
    valid, reason = run_validity(role, load_start, load_end)
    record = {
        "role": role,
        "tree": head,
        "started": started,
        "load_start": load_start,
        "load_end": load_end,
        "wall_s": wall,
        "cpu_s": cpu,
        "valid": valid,
        "reason": reason,
    }
    with open(out, "a") as handle:
        handle.write(json.dumps(record) + "\n")
    print(json.dumps(record))
    return 0


def _contention_summarize(path: Path) -> int:
    runs = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    trees = {r["tree"] for r in runs}
    if len(trees) > 1:
        print(f"ERROR: the factor runs span {len(trees)} trees: {sorted(trees)}")
        return 2
    result = contention_factor(runs)
    print(json.dumps(result, indent=2))
    if result["factor"] is None:
        print(f"no factor: {result['note']}")
        return 1
    print(
        f"factor (max of {result['pairs']} ratios) {result['factor']:.3f}; "
        f"min {result['min']:.3f}; spread {result['spread']:.3f}; band {result['band']}"
    )
    return 0


# =============================================================================================
# Shared scaffolding for the database-backed subcommands (NFR-468, NFR-470, NFR-1443)
#
# These phases are not unit-tested: they need the migrated development Postgres, MinIO and Redis
# and run only in a lead-granted window. What can be wrong in them is the wiring; what decides a
# reading is the pure logic above.
# =============================================================================================


def _bootstrap_paths() -> None:
    """The workspace packages and the backend are imported by path, as `seed.py` does, so the
    script runs the same under `uv run python` from the repository root."""
    for path in (
        ROOT,
        ROOT / "backend" / "src",
        ROOT / "packages" / "pricing-core" / "src",
        ROOT / "packages" / "model-schema" / "src",
        ROOT / "examples" / "fremtpl2",
    ):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def _import_seed() -> Any:
    _bootstrap_paths()
    import seed  # examples/fremtpl2/seed.py

    return seed


def _emit(kind: str, **fields: Any) -> None:
    """One JSON line per reading, with the host state beside it (load is part of the figure)."""
    print(json.dumps({"reading": kind, "label": fields.pop("label", None), **fields}, default=str))


def _latency_fields(samples_ns: list[int]) -> dict[str, float]:
    ms = [n / 1e6 for n in samples_ns]
    return {
        "n": len(ms),
        "p50_ms": nearest_rank(ms, 50),
        "p95_ms": nearest_rank(ms, 95),
        "p99_ms": nearest_rank(ms, 99),
        "max_ms": max(ms),
    }


class _Env:
    """The app, its database and blob store, and an in-process client. DP-2 (a)."""

    def __init__(self) -> None:
        _bootstrap_paths()
        from app.config import load_settings
        from app.db.session import Database
        from app.main import create_app
        from app.platform.blobs import BlobStore
        from app.worker.data_handlers import register_data_handlers
        from app.worker.rate_table_handlers import register_rate_table_handlers

        register_data_handlers()
        register_rate_table_handlers()
        self.settings = load_settings(dev_auth_enabled=True)
        self.database = Database(self.settings)
        self.blob_store = BlobStore(self.settings)
        self.app = create_app(self.settings)

    def headers(self, principal_id: Any, workspace_id: Any) -> dict[str, str]:
        from app.api.deps import DEV_PRINCIPAL_HEADER

        return {DEV_PRINCIPAL_HEADER: str(principal_id), "Workspace-Id": str(workspace_id)}

    def client(self) -> Any:
        import httpx

        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=self.app), base_url="http://measure"
        )


async def _timed_get(
    client: Any, url: str, headers: dict[str, str], **params: Any
) -> tuple[int, Any]:
    """One awaited request, timed at its boundaries only: (nanoseconds, response)."""
    start = time.perf_counter_ns()
    response = await client.get(url, params=params, headers=headers)
    return time.perf_counter_ns() - start, response


async def _ingest(
    env: _Env,
    *,
    workspace_id: Any,
    actor: Any,
    dataset_id: Any,
    payload: bytes,
    media_type: str,
    filename: str,
    recipe: list[dict[str, Any]] | None = None,
) -> Any:
    """Upload -> blob -> `dataset.ingest` Job -> execute_job, the path a worker takes
    (`examples/fremtpl2/seed.py::run`'s `ingest`). Returns the new version's id."""
    from sqlalchemy import select

    from app.db.models import DatasetVersionRow
    from app.platform import jobs as job_service
    from app.worker.tasks import execute_job
    from model_schema import JobKind, JobStatus

    async with env.database.unit_of_work() as session:
        ref = await env.blob_store.put(session, payload, media_type)
        job = await job_service.submit(
            session,
            JobKind.DATASET_INGEST,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "dataset_id": str(dataset_id),
                "blob": ref.sha256,
                "filename": filename,
                "recipe": recipe or [],
            },
            actor,
            workspace_id=workspace_id,
        )
    status = await execute_job(env.database, job.id, env.blob_store)
    if status is not JobStatus.SUCCEEDED:
        raise SystemExit(f"ingestion job {job.id} ended {status.value}, not succeeded")
    async with env.database.session() as session:
        return (
            await session.execute(
                select(DatasetVersionRow.id)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc())
                .limit(1)
            )
        ).scalar_one()


async def _fremtpl2(env: _Env, rows: int | None, reuse: bool) -> tuple[Any, Any, Any, Any]:
    """Seed freMTPL2 through `seed.py` (or reuse the last seed): returns
    (workspace_id, analyst Principal, dataset_id, [version ids by version number])."""
    from uuid import UUID

    from sqlalchemy import select

    from app.db.models import DatasetRow, DatasetVersionRow

    seed = _import_seed()
    if not reuse:
        await seed.run(rows)
    info = json.loads((seed.DATA_DIR / "last-seed.json").read_text())
    workspace_id = UUID(info["workspace_id"])
    principals = await seed.grant_demo_principals(env.database, workspace_id)
    async with env.database.session() as session:
        dataset_id = (
            await session.execute(
                select(DatasetRow.id)
                .where(DatasetRow.workspace_id == workspace_id)
                .order_by(DatasetRow.created_at.desc())
                .limit(1)
            )
        ).scalar_one()
        versions = (
            await session.execute(
                select(DatasetVersionRow.id, DatasetVersionRow.status)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version)
            )
        ).all()
    return workspace_id, principals["analyst"], dataset_id, versions


# --- NFR-468: the one-way read -----------------------------------------------------------------


async def _one_way(args: argparse.Namespace) -> int:
    from sqlalchemy import text

    import pricing_core.data.profile as profile_module
    from app.platform import datasets as dataset_service
    from app.platform import profiles as profile_service
    from model_schema import RecordGrain, new_uuid7

    env = _Env()
    _bootstrap_paths()
    header = session_header()
    async with env.app.router.lifespan_context(env.app), env.client() as client:
        corpora: list[tuple[str, Any, Any, Any]] = []  # (name, workspace, actor, version id)
        # (i) the freMTPL2 prepared version: the validated version with the most profiled rows
        workspace_id, actor, _dataset_id, versions = await _fremtpl2(
            env, args.fremtpl2_rows, args.reuse_last_seed
        )
        best, best_rows = None, -1
        async with env.database.session() as session:
            for version_id, status in versions:
                if status != "validated":
                    continue
                profile = await profile_service.latest_profile(
                    session, workspace_id=workspace_id, version_id=version_id
                )
                if profile.row_count > best_rows:
                    best, best_rows = version_id, profile.row_count
        if best is None:
            raise SystemExit("no validated freMTPL2 version with a profile")
        corpora.append((f"freMTPL2 prepared version ({best_rows} rows)", workspace_id, actor, best))

        # (ii) the wide synthetic version: 80 columns x 1 000 000 rows, ingested as parquet
        seed = _import_seed()
        wide_ws = new_uuid7()
        wide_actor = (await seed.grant_demo_principals(env.database, wide_ws))["analyst"]
        async with env.database.unit_of_work() as session:
            dataset = await dataset_service.create_dataset(
                session,
                workspace_id=wide_ws,
                actor=wide_actor,
                slug=f"wide-{new_uuid7().hex[-6:]}",
                name="NFR-468 wide synthetic",
                line_of_business="motor",
                territory="FR",
                currency="EUR",
                default_record_grain=RecordGrain.POLICY_EXPOSURE,
            )
            wide_dataset = dataset.id
        bench_data = _load_module("bench_data", ROOT / "scripts" / "bench-data.py")
        import io

        buffer = io.BytesIO()
        bench_data.synthesise(args.wide_rows).write_parquet(buffer)
        wide_version = await _ingest(
            env,
            workspace_id=wide_ws,
            actor=wide_actor,
            dataset_id=wide_dataset,
            payload=buffer.getvalue(),
            media_type="application/vnd.apache.parquet",
            filename="wide.parquet",
        )
        wide_name = f"wide synthetic 80 columns x {args.wide_rows} rows"
        corpora.append((wide_name, wide_ws, wide_actor, wide_version))

        for name, ws, who, version_id in corpora:
            async with env.database.session() as session:
                profile = await profile_service.latest_profile(
                    session, workspace_id=ws, version_id=version_id
                )
                columns = [summary.column for summary in profile.one_ways]
                body_bytes = (
                    await session.execute(
                        text(
                            "select pg_column_size(body) from profiles "
                            "where dataset_version_id = :v order by created_at desc limit 1"
                        ),
                        {"v": version_id},
                    )
                ).scalar_one()
            if not columns:
                raise SystemExit(f"{name}: the stored profile has no one-way to read")
            url = f"/api/v1/dataset-versions/{version_id}/one-ways"
            headers = env.headers(who.id, ws)

            async def call(
                column: str,
                url: str = url,
                headers: dict[str, str] = headers,
                name: str = name,
            ) -> int:
                ns, response = await _timed_get(client, url, headers, column=column)
                if response.status_code != 200:
                    raise SystemExit(
                        f"{name}: {column} answered {response.status_code}: {response.text}"
                    )
                return ns

            for i in range(NFR_468_WARMUP):
                await call(columns[i % len(columns)])
            # "Never computed on request": any of the three raises for the timed phase only.
            originals = {}
            for fn in ("profile_frame", "profile_parquet", "one_way"):
                originals[fn] = getattr(profile_module, fn)

                def _raiser(*_a: Any, _fn: str = fn, **_k: Any) -> Any:
                    raise AssertionError(f"NFR-468: {_fn} called on request")

                setattr(profile_module, fn, _raiser)
            load_before, cpu_before = read_load1(), time.process_time()
            try:
                samples = [await call(columns[i % len(columns)]) for i in range(NFR_468_N)]
            finally:
                for fn, original in originals.items():
                    setattr(profile_module, fn, original)
            fields = _latency_fields(samples)
            _emit(
                "NFR-468",
                label=LATENCY_LABEL,
                corpus=name,
                one_way_columns=len(columns),
                profile_body_bytes=body_bytes,
                load_before=load_before,
                load_after=read_load1(),
                cpu_s=round(time.process_time() - cpu_before, 3),
                band=classify_latency(
                    fields["p95_ms"], budget=THRESHOLDS_MS["NFR-468"], fraction=NEAR_BOUND_FRACTION
                ),
                near_bound_fraction=NEAR_BOUND_FRACTION,
                session=header,
                **fields,
            )
    return 0


# --- NFR-470: storage overhead and deduplication -----------------------------------------------


async def _storage(args: argparse.Namespace) -> int:
    from sqlalchemy import text

    seed = _import_seed()
    env = _Env()
    workspace_id, actor, dataset_id, _versions = await _fremtpl2(
        env, args.fremtpl2_rows, args.reuse_last_seed
    )
    # The identical source again, as a later version: same bytes and recipe as the cleaned v2.
    async with env.app.router.lifespan_context(env.app):
        third = await _ingest(
            env,
            workspace_id=workspace_id,
            actor=actor,
            dataset_id=dataset_id,
            payload=seed.build_csv(args.fremtpl2_rows),
            media_type="text/csv",
            filename="fremtpl2.csv",
            recipe=seed.recipe(drop_implausible_exposure=True),
        )
    parquet = "application/vnd.apache.parquet"
    async with env.database.session() as session:
        rows = (
            await session.execute(
                text(
                    "select id, version, tables from dataset_versions "
                    "where dataset_id = :d order by version"
                ),
                {"d": dataset_id},
            )
        ).all()
        seen: set[str] = set()
        for version_id, number, tables in rows:
            digests = [t["blob"]["sha256"] for t in tables]
            sizes = {
                d: (b, m)
                for d, b, m in (
                    await session.execute(
                        text("select sha256, bytes, media_type from blobs where sha256 = any(:d)"),
                        {"d": digests},
                    )
                ).all()
            }
            payload = sum(b for b, m in sizes.values() if m == parquet)
            other_blobs = sum(b for b, m in sizes.values() if m != parquet)
            new_bytes = sum(b for d, (b, m) in sizes.items() if m == parquet and d not in seen)
            seen.update(sizes)

            async def scalar(query: str, version_id: Any = version_id) -> int:
                return int((await session.execute(text(query), {"v": version_id})).scalar_one())

            own = {
                "dataset_versions_row": await scalar(
                    "select pg_column_size(t.*) from dataset_versions t where id = :v"
                ),
                "validation_reports": await scalar(
                    "select coalesce(sum(pg_column_size(t.*)), 0) from validation_reports t "
                    "where dataset_version_id = :v"
                ),
                "profiles": await scalar(
                    "select coalesce(sum(pg_column_size(t.*)), 0) from profiles t "
                    "where dataset_version_id = :v"
                ),
                "non_parquet_blobs": other_blobs,
            }
            overhead = int(sum(own.values()))
            excluded = {
                "ingestion_runs_rows": await scalar(
                    "select coalesce(sum(pg_column_size(t.*)), 0) from ingestion_runs t "
                    "where dataset_version_id = :v"
                ),
                "ingestion_runs_source_bytes_read": await scalar(
                    "select coalesce(sum(bytes_read), 0) from ingestion_runs "
                    "where dataset_version_id = :v"
                ),
                "audit_events_rows": await scalar(
                    "select coalesce(sum(pg_column_size(t.*)), 0) from audit_events t "
                    "where entity_ref like '%' || cast(:v as text) || '%'"
                ),
            }
            ratio = (payload + overhead) / payload if payload else None
            _emit(
                "NFR-470",
                version=number,
                version_id=version_id,
                is_third_identical=(version_id == third),
                payload_bytes=payload,
                counted_overhead_bytes=overhead,
                counted=own,
                excluded=excluded,
                ratio=ratio,
                new_parquet_bytes_vs_earlier=new_bytes,
                band=classify_storage(payload, overhead, new_bytes if version_id == third else 0)
                if payload
                else "NO-PAYLOAD",
                rule=NFR_470_RULE,
                session=session_header(),
            )
    return 0


# --- NFR-1443: the cells-diff page -------------------------------------------------------------

#: (name, storage expected, cells, cell_threshold). The plan says "six"; it lists these five
#: (GO "2026-10-22 11:53:15 BST" D3: the sweep runs five).
CELLS_DIFF_RUNS = (
    ("rows-10000", "rows", 10_000, 250_000),
    ("rows-250000", "rows", 250_000, 250_000),
    ("parquet-10000", "parquet", 10_000, 5_000),
    ("parquet-250000", "parquet", 250_000, 5_000),
    ("parquet-1000000", "parquet", 1_000_000, 250_000),
)


async def _cells_diff(args: argparse.Namespace) -> int:
    from uuid import UUID, uuid4

    from backend.tests.test_rate_tables_service import _seed_approved_model, _set_threshold
    from sqlalchemy import select, update

    from app.db.models import JobRow, RateTableRow, RateTableVersionRow
    from app.platform import jobs as job_service
    from app.platform import rate_tables as svc
    from app.worker.tasks import execute_job
    from model_schema import JobKind, JobStatus, new_uuid7
    from model_schema.refs import ArtifactRef

    seed = _import_seed()
    env = _Env()
    workspace_id = new_uuid7()
    actor = (await seed.grant_demo_principals(env.database, workspace_id))["actuary"]
    headers = env.headers(actor.id, workspace_id)
    selected = [r for r in CELLS_DIFF_RUNS if args.only in (None, r[0])]
    p95: dict[str, float] = {}
    async with env.app.router.lifespan_context(env.app), env.client() as client:
        # 10 000 completed diff_cells Jobs of other keys, seeded first (LG-1444 Hold B).
        for start in range(0, args.seeded_jobs, 500):
            async with env.database.unit_of_work() as session:
                for i in range(start, min(start + 500, args.seeded_jobs)):
                    await job_service.submit(
                        session,
                        JobKind.RATE_TABLE_DIFF_CELLS,
                        {
                            "workspace_id": str(workspace_id),
                            "slug": f"other-{i}",
                            "version": 2,
                            "against": "previous",
                            "portfolio": None,
                        },
                        actor,
                        workspace_id=workspace_id,
                    )
        async with env.database.unit_of_work() as session:
            await session.execute(
                update(JobRow)
                .where(
                    JobRow.workspace_id == workspace_id,
                    JobRow.kind == JobKind.RATE_TABLE_DIFF_CELLS,
                )
                .values(status=JobStatus.SUCCEEDED)
            )
        for name, storage, cells, threshold in selected:
            await _set_threshold(env.database, workspace_id, threshold)
            levels = [f"L{i:07d}" for i in range(cells)]
            family, slug = f"mf-{uuid4().hex[:8]}", f"tbl-{uuid4().hex[:8]}"
            await _seed_approved_model(
                env.database,
                workspace_id,
                family,
                {"driver_age_band": [(lv, 1.0) for lv in levels]},
            )
            await svc.seed_from_model(
                env.database,
                workspace_id,
                actor,
                env.settings,
                env.blob_store,
                slug=slug,
                model_ref=ArtifactRef(type="model", slug=family, version=1),
                factor="driver_age_band",
                change_note="NFR-1443 measurement",
            )
            v2 = "driver_age_band,relativity\n" + "".join(f"{lv},1.1\n" for lv in levels)
            await svc.import_confirmed(
                env.database,
                workspace_id,
                actor,
                env.settings,
                env.blob_store,
                slug=slug,
                version=1,
                filename="v2.csv",
                content=v2.encode(),
            )
            async with env.database.session() as session:
                table_id = (
                    await session.execute(
                        select(RateTableRow.id).where(
                            RateTableRow.workspace_id == workspace_id, RateTableRow.slug == slug
                        )
                    )
                ).scalar_one()
                stored = set(
                    (
                        await session.execute(
                            select(RateTableVersionRow.storage).where(
                                RateTableVersionRow.rate_table_id == table_id
                            )
                        )
                    ).scalars()
                )
            if stored != {storage}:
                raise SystemExit(f"{name}: both versions must be storage={storage}, got {stored}")
            url = f"/api/v1/rate-tables/{slug}@2/diff/cells"
            first = await client.get(
                url, params={"against": "previous", "limit": NFR_1443_LIMIT}, headers=headers
            )
            if first.status_code != 202:
                raise SystemExit(f"{name}: the first request answered {first.status_code}, not 202")
            job_id = UUID(first.json()["id"])
            status = await execute_job(env.database, job_id, env.blob_store)
            async with env.database.session() as session:
                job = await session.get(JobRow, job_id)
            artifact = (job.result or {}).get("ref") if job is not None else None
            if status is not JobStatus.SUCCEEDED or not artifact:
                raise SystemExit(f"{name}: the Job did not succeed with its artifact: {status}")
            samples, cursor = [], None
            load_before, cpu_before = read_load1(), time.process_time()
            for _ in range(NFR_1443_N):
                params = {"against": "previous", "limit": NFR_1443_LIMIT}
                if cursor:
                    params["cursor"] = cursor
                ns, response = await _timed_get(client, url, headers, **params)
                if response.status_code != 200:
                    raise SystemExit(f"{name}: a later page answered {response.status_code}")
                samples.append(ns)
                cursor = response.json()["next_cursor"]
            fields = _latency_fields(samples)
            p95[name] = fields["p95_ms"]
            _emit(
                "NFR-1443",
                label=LATENCY_LABEL,
                run=name,
                storage=storage,
                cells=cells,
                limit=NFR_1443_LIMIT,
                seeded_jobs=args.seeded_jobs,
                load_before=load_before,
                load_after=read_load1(),
                cpu_s=round(time.process_time() - cpu_before, 3),
                band=classify_latency(
                    fields["p95_ms"], budget=THRESHOLDS_MS["NFR-1443"], fraction=NEAR_BOUND_FRACTION
                ),
                near_bound_fraction=NEAR_BOUND_FRACTION,
                session=session_header(),
                **fields,
            )
    for path, small, large in (
        ("rows", "rows-10000", "rows-250000"),
        ("parquet", "parquet-10000", "parquet-250000"),
    ):
        if small in p95 and large in p95:
            ratio = p95[large] / p95[small]
            _emit(
                "NFR-1443-ratio",
                label=LATENCY_LABEL,
                path=path,
                ratio=ratio,
                band=classify_ratio(ratio),
            )
    return 0


# --- NFR-467: profiling a 10 M-row version -----------------------------------------------------


def _load_module(name: str, path: Path) -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _profile_child(parquet: Path) -> int:
    """One fresh process that never held the data: baseline VmRSS after imports, the call as
    `bench-data.py:196-198` makes it, VmHWM after. One phase per process."""
    _bootstrap_paths()
    from uuid import uuid4

    from pricing_core.data.profile import profile_parquet

    baseline = read_status_bytes("VmRSS")
    load_start = read_load1()
    start = time.perf_counter()
    profile_parquet(
        [str(parquet)],
        dataset_version_id=uuid4(),
        one_way_columns=["vehicle_group", "postcode_area", "driver_age"],
    )
    wall = time.perf_counter() - start
    hwm = read_status_bytes("VmHWM")
    print(
        json.dumps(
            {
                "wall_s": wall,
                "vmhwm_bytes": hwm,
                "baseline_bytes": baseline,
                "delta_peak_bytes": hwm - baseline,
                "payload_bytes": parquet.stat().st_size,
                "load_start": load_start,
                "load_end": read_load1(),
            }
        )
    )
    return 0


def _profile(args: argparse.Namespace) -> int:
    import shutil

    tmpdir = args.tmpdir
    if str(tmpdir.resolve()).startswith("/tmp"):
        raise SystemExit("--tmpdir must be the job's directory, never /tmp")
    tmpdir.mkdir(parents=True, exist_ok=True)
    rule = NFR_467_RULE
    readings: dict[int, dict[str, Any]] = {}
    for rows in rule["sizes"]:
        free_gb = shutil.disk_usage(tmpdir).free / 2**30
        guards = {
            "mem_available_gb": round(mem_available_gb(), 2),
            "disk_free_gb": round(free_gb, 2),
        }
        print(json.dumps({"guards": guards, "rows": rows}))
        if (
            guards["mem_available_gb"] < rule["mem_available_min_gb"]
            or free_gb < rule["disk_free_min_gb"]
        ):
            raise SystemExit(
                f"guard failed at {rows} rows: {guards}; "
                "name this run an nfr-bench-1 session 2 extra reading"
            )
        path = tmpdir / f"nfr467-{rows}.parquet"
        try:
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "bench-data.py"),
                    "--rows",
                    str(rows),
                    "--generate-to",
                    str(path),
                ],
                check=True,
            )
            child = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "profile-child",
                    "--parquet",
                    str(path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        finally:
            path.unlink(missing_ok=True)
        readings[rows] = json.loads(child.stdout.strip().splitlines()[-1])
        _emit(
            "NFR-467-run",
            rows=rows,
            columns=rule["columns"],
            guards=guards,
            session=session_header(),
            **readings[rows],
        )
    small, large = (readings[r] for r in rule["sizes"])
    ratio = memory_ratio(large["delta_peak_bytes"], small["delta_peak_bytes"])
    wall = large["wall_s"]
    _emit(
        "NFR-467",
        label="DIAGNOSTIC (time); a reading (memory)",
        time_s=wall,
        time_band=classify_latency(
            wall, budget=rule["time_budget_s"], fraction=NEAR_BOUND_FRACTION
        ),
        memory_ratio=ratio,
        memory_verdict=classify_nfr467_memory(ratio),
        memory_rule="derived from 'sub-linear', ruled 2026-10-14 13:21:41",
        rule=rule,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    cont = sub.add_parser("contention", help="Task 0: re-measure the contention factor")
    cont_sub = cont.add_subparsers(dest="action", required=True)
    run = cont_sub.add_parser("run", help="one A or B run of the fixed benchmark")
    run.add_argument("--role", choices=("A", "B"), required=True)
    run.add_argument("--out", type=Path, required=True, help="JSON-lines file, appended")
    summ = cont_sub.add_parser("summarize", help="pair the runs and print the factor and band")
    summ.add_argument("file", type=Path)

    one = sub.add_parser("one-way", help="NFR-468: the one-way read (server-side, in-process)")
    for p in (one, sub.add_parser("storage", help="NFR-470: storage overhead and dedup")):
        p.add_argument("--fremtpl2-rows", type=int, default=None, help="default: all 678 013")
        p.add_argument(
            "--reuse-last-seed",
            action="store_true",
            help="use examples/fremtpl2/data/last-seed.json instead of seeding",
        )
        if p is one:
            p.add_argument("--wide-rows", type=int, default=1_000_000)
    cells = sub.add_parser("cells-diff", help="NFR-1443: the cells-diff page")
    cells.add_argument("--only", choices=[r[0] for r in CELLS_DIFF_RUNS], default=None)
    cells.add_argument("--seeded-jobs", type=int, default=NFR_1443_SEEDED_JOBS)
    prof = sub.add_parser("profile", help="NFR-467: profiling at 2 M and 10 M rows x 80 columns")
    prof.add_argument("--tmpdir", type=Path, required=True, help="the job's directory, not /tmp")
    child = sub.add_parser("profile-child", help="(internal) one fresh profiling process")
    child.add_argument("--parquet", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "contention":
        if args.action == "run":
            return _contention_run(args.role, args.out)
        return _contention_summarize(args.file)
    if args.command == "profile":
        return _profile(args)
    if args.command == "profile-child":
        return _profile_child(args.parquet)
    import asyncio

    handler = {"one-way": _one_way, "storage": _storage, "cells-diff": _cells_diff}[args.command]
    return asyncio.run(handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
