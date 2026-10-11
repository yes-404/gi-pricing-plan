"""SL-1455 Task 0 driver (PL-1454 Task 0 Steps 3, 3b, 4) — SCRATCH, never committed.

Reuses `scripts/bench-rating.py`'s own seed, bundle, quote body and open-loop driver, so the
load is the load FD-1411 measured; only the server is started as `t0_app:create_app`
(the instruments) instead of `app.main:create_app`.

Arms (one bundle and one seeded workspace per arm):
  bench-gbm / bench-nogbm   explicit `rating_version_ref`, no Deployment (the bench path)
  live-gbm  / live-nogbm    no ref in the body, a `uat` Deployment seeded (Step 3b: the exit
                            demo's default-live path; `_serving_ref` finds the Deployment)

Per pass: a fresh server (cold slot), the bench's discarded 4 s warm-up rung at 25 rps, then
one measured rung. Output: <out>/<arm>/r<rate>-run<k>/{requests,events}.jsonl, server.log,
client.json (and profile.txt for a py-spy pass).
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ARMS = {
    "bench-gbm": (True, False),
    "bench-nogbm": (False, False),
    "live-gbm": (True, True),
    "live-nogbm": (False, True),
}


def london_now() -> str:
    """Europe/London to the second (the maintainer's 15:12:46 BST rule: per timed invocation)."""
    return subprocess.run(["date", "+%F %T %Z"], capture_output=True, text=True,
                          env={**os.environ, "TZ": "Europe/London"}).stdout.strip()


def cpu_steal() -> tuple[int, int]:
    """(steal, total) jiffies from the aggregate `cpu` line of /proc/stat (steal = 8th field)."""
    fields = [int(x) for x in Path("/proc/stat").read_text().splitlines()[0].split()[1:]]
    return fields[7], sum(fields[:8])


def load_bench(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("bench_rating", root / "scripts" / "bench-rating.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["bench_rating"] = module
    spec.loader.exec_module(module)
    return module


async def seed_deployment(bench: Any, bundle: Any, *, dsn: str, workspace_id: str) -> None:
    """Step 3b: the bench workspace's bundle as a `uat` Deployment (scratch DB only)."""
    bench._backend_on_path()
    from uuid import UUID, uuid4

    from app.config import Environment, Settings
    from app.db.models import DeploymentRow, EnvironmentRow
    from app.db.session import Database
    from pydantic import SecretStr
    from sqlalchemy import select

    database = Database(
        Settings(environment=Environment.LOCAL, version="bench", database_url=SecretStr(dsn))
    )
    async with database.unit_of_work() as session:
        env_id = (
            await session.execute(select(EnvironmentRow.id).where(EnvironmentRow.slug == "uat"))
        ).scalar_one()
        session.add(
            DeploymentRow(
                workspace_id=UUID(workspace_id),
                environment_id=env_id,
                rating_version_ref=str(bench._RATING_VERSION_REF),
                bundle_hash=bundle.content_hash,
                deployed_by=uuid4(),
                reason="SL-1455 Task 0 default-live arm (scratch)",
            )
        )
    await database.dispose()


def server_cmd(root: Path, port: int) -> list[str]:
    return [
        str(root / ".venv" / "bin" / "python"), "-m", "uvicorn", "t0_app:create_app",
        "--factory", "--host", "127.0.0.1", "--port", str(port),
        "--log-level", "warning", "--no-access-log",
    ]


def start_server(root: Path, cmd: list[str], env: dict[str, str], log: Path, *, spy: Path | None) -> Any:
    full = cmd
    if spy is not None:
        # SAMPLING only: --nonblocking so py-spy never pauses the process to read it (pre-registered).
        full = ["uvx", "py-spy", "record", "--nonblocking", "--format", "raw", "--rate", "100",
                "-o", str(spy), "--"] + cmd
    return subprocess.Popen(full, cwd=str(root), env=env, stdout=log.open("wb"),
                            stderr=subprocess.STDOUT)


def stop_server(proc: Any, *, spy: bool) -> None:
    """SIGINT by pid. Under py-spy the uvicorn process is py-spy's child: signal that."""
    targets = [proc.pid]
    if spy:
        out = subprocess.run(["pgrep", "-P", str(proc.pid)], capture_output=True, text=True).stdout
        targets = [int(p) for p in out.split()] or [proc.pid]
    for pid in targets:
        try:
            os.kill(pid, signal.SIGINT)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=60)
    except Exception:
        proc.kill()


def one_pass(bench: Any, root: Path, *, arm: str, rate: int, run: int, ctx: dict[str, Any],
             headers: dict[str, str], body: dict[str, Any], dsn: str, bucket: str, port: int,
             out: Path, seconds: int, spy: bool) -> None:
    pass_dir = out / arm / (f"r{rate}-run{run}" if not spy else f"r{rate}-profile")
    pass_dir.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "GIP_ENVIRONMENT": "local", "GIP_VERSION": "bench",
        "GIP_DATABASE_URL": dsn, "GIP_BLOB_BUCKET": bucket,
        "PYTHONPATH": str(HERE) + os.pathsep + os.environ.get("PYTHONPATH", ""),
        "T0_OUT": str(pass_dir),
    }
    if os.environ.get("T0_ASYNCIO_DEBUG", "1") == "1":
        env["PYTHONASYNCIODEBUG"] = "1"
    else:  # the rerun: no asyncio debug hooks of any kind, nor from the inherited environment
        env.pop("PYTHONASYNCIODEBUG", None)
    start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    london_start = london_now()
    steal0, total0 = cpu_steal()
    print(f"  START {arm} {rate} rps run{run}{' (py-spy)' if spy else ''}: {london_start}", flush=True)
    load_start = bench.loadavg()
    proc = start_server(root, server_cmd(root, port), env, pass_dir / "server.log",
                        spy=(pass_dir / "profile.txt") if spy else None)
    base = f"http://127.0.0.1:{port}"
    try:
        asyncio.run(bench._await_ready(f"{base}/healthz", seconds=120.0))
        asyncio.run(bench._drive(f"{base}/api/v1/score", headers, body, rate=25, seconds=4))
        measure_from = time.time()
        rung = asyncio.run(
            bench._drive(f"{base}/api/v1/score", headers, body, rate=rate, seconds=seconds)
        )
    finally:
        stop_server(proc, spy=spy)
    london_end = london_now()
    steal1, total1 = cpu_steal()
    steal_pct = 100.0 * (steal1 - steal0) / max(total1 - total0, 1)
    print(f"  END   {arm} {rate} rps run{run}: {london_end}; steal {steal1 - steal0} of "
          f"{total1 - total0} jiffies ({steal_pct:.2f}%)", flush=True)
    (pass_dir / "client.json").write_text(json.dumps({
        "start_london": london_start, "end_london": london_end,
        "steal_jiffies": steal1 - steal0, "total_jiffies": total1 - total0,
        "steal_pct": steal_pct,
        "arm": arm, "rate": rate, "run": run, "profile": spy,
        "start_utc": start, "end_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "load_start": load_start, "load_end": bench.loadavg(),
        "measure_from": measure_from, "offered_rps": rung.offered_rps,
        "achieved_rps": rung.achieved_rps, "errors": rung.errors, "samples_ms": rung.samples,
    }))
    p99 = bench._percentile(rung.samples, 0.99) if rung.samples else float("nan")
    print(f"  {arm} {rate} rps run{run}{' (py-spy)' if spy else ''}: n={len(rung.samples)} "
          f"errors={rung.errors} client p99={p99:.1f} ms", flush=True)


def probe_live(bench: Any, root: Path, *, arm: str, headers: dict[str, str], body: dict[str, Any],
               dsn: str, bucket: str, port: int, out: Path) -> None:
    """One default-live request with `main`'s handler unchanged (`T0_FILL_REF=0`): what does
    `main` answer when the body carries no ref? Recorded, not timed."""
    import httpx

    pass_dir = out / arm / "probe-main-handler"
    pass_dir.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ, "GIP_ENVIRONMENT": "local", "GIP_VERSION": "bench",
        "GIP_DATABASE_URL": dsn, "GIP_BLOB_BUCKET": bucket,
        "PYTHONPATH": str(HERE) + os.pathsep + os.environ.get("PYTHONPATH", ""),
        "T0_OUT": str(pass_dir), "T0_FILL_REF": "0",
    }
    proc = start_server(root, server_cmd(root, port), env, pass_dir / "server.log", spy=None)
    try:
        asyncio.run(bench._await_ready(f"http://127.0.0.1:{port}/healthz", seconds=120.0))
        response = httpx.post(f"http://127.0.0.1:{port}/api/v1/score", json=body, headers=headers,
                              timeout=60.0)
        record = {"status": response.status_code, "body": response.text[:600]}
    finally:
        stop_server(proc, spy=False)
    (pass_dir / "probe.json").write_text(json.dumps(record))
    print(f"  PROBE {arm}, main's handler, no ref in body: HTTP {record['status']} "
          f"{record['body'][:200]}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path, help="the worktree")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--bucket", default=os.environ.get("GIP_TEST_BUCKET", "gip-test-blobs"))
    parser.add_argument("--arms", default=",".join(ARMS))
    parser.add_argument("--rates", default="25,50")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--seconds", type=int, default=20)
    parser.add_argument("--port", type=int, default=8155)
    parser.add_argument("--profile", action="store_true", help="one 25 rps py-spy pass per arm")
    args = parser.parse_args()

    bench = load_bench(args.root)
    for name in args.arms.split(","):
        with_gbm, live = ARMS[name]
        print(f"\n=== arm {name} (gbm={with_gbm}, default-live={live}) ===", flush=True)
        bundle = asyncio.run(bench._serialisable(with_gbm=with_gbm, n_expr=bench.N_EXPR_STEPS,
                                                 rounds=300, rows=5_000))
        workspace_id, api_key = asyncio.run(bench._seed(bundle, dsn=args.dsn, bucket=args.bucket))
        if live:
            asyncio.run(seed_deployment(bench, bundle, dsn=args.dsn, workspace_id=workspace_id))
        headers = {"X-API-Key": api_key, "Workspace-Id": workspace_id}
        body = json.loads(bench._ctx().model_dump_json())
        if live:
            body.pop("options", None)
        common: dict[str, Any] = dict(
            ctx={}, headers=headers, body=body, dsn=args.dsn, bucket=args.bucket,
            port=args.port, out=args.out, seconds=args.seconds,
        )
        if live:
            probe_live(bench, args.root, arm=name, headers=headers, body=body, dsn=args.dsn,
                       bucket=args.bucket, port=args.port, out=args.out)
        for rate in (int(r) for r in args.rates.split(",")):
            for run in range(1, args.runs + 1):
                one_pass(bench, args.root, arm=name, rate=rate, run=run, spy=False, **common)
        if args.profile:
            one_pass(bench, args.root, arm=name, rate=25, run=0, spy=True, **common)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
