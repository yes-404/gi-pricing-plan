"""Spike F1: one measured run. N uvicorn workers, open-loop load at R rps, and a deploy A→B at T s.

usage: run.py <workers> [--rps 200] [--duration 40] [--deploy-at 10] [--tag x]

Every response is asserted on its own: status 200; the engine-stamped hash is in {A,B} and
equals the held object's hash; and the result signature equals that hash's reference
signature (the mix detector). The run writes results/<tag>.json (summary) and
results/<tag>.jsonl (every response).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import statistics
import subprocess
import sys
import time
from pathlib import Path

import httpx
import redis

HERE = Path(__file__).resolve().parent
SCRATCH = HERE.parents[1]
PY = str(SCRATCH / ".venv" / "bin" / "python")
REFS = json.loads((HERE / "refs.json").read_text())
A, B = REFS["A"]["hash"], REFS["B"]["hash"]
SIG = {REFS[k]["hash"]: REFS[k]["sig"] for k in ("A", "B")}
PORT = 8611


def pct(xs: list[float], p: float) -> float | None:
    if not xs:
        return None
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(p / 100 * len(xs)))] * 1000, 2)


def start_workers(n: int) -> list[subprocess.Popen]:
    """N independent uvicorn processes, one port each (a pod per worker behind an L7 balancer).

    Replaces `uvicorn --workers N` after run m-n4-r1: kernel accept-sharing pinned
    keep-alive connections unevenly (one worker took ~50% of requests), overloading it.
    """
    r = redis.Redis(port=6390)
    r.set("env:dev:current", A)
    r.delete("ready")
    env = dict(os.environ, PYTHONPATH=str(SCRATCH), OMP_NUM_THREADS="1")
    procs = [subprocess.Popen(
        [PY, "-m", "uvicorn", "spike.f1.app:app", "--port", str(PORT + k),
         "--log-level", "warning", "--no-access-log"],
        cwd=str(SCRATCH), env=env, start_new_session=True) for k in range(n)]
    deadline = time.time() + 180
    while r.llen("ready") < n:
        if time.time() > deadline or any(p.poll() is not None for p in procs):
            stop_workers(procs)
            raise SystemExit(f"workers not ready: {r.llen('ready')}/{n}")
        time.sleep(0.2)
    return procs


def stop_workers(procs: list[subprocess.Popen]) -> None:
    # S-9: by PID, after readlink names it as ours.
    for proc in procs:
        if proc.poll() is None:
            cwd = os.readlink(f"/proc/{proc.pid}/cwd")
            assert cwd == str(SCRATCH), f"pid {proc.pid} cwd {cwd} is not the spike scratch"
            os.kill(proc.pid, signal.SIGINT)  # SIGTERM is guarded (sigguard.py)
    for proc in procs:
        proc.wait(timeout=60)


async def load(rps: int, duration: float, deploy_at: float, n: int) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    deploy: dict = {}
    limits = httpx.Limits(max_connections=1000, max_keepalive_connections=1000)
    clients = [httpx.AsyncClient(base_url=f"http://127.0.0.1:{PORT + k}", limits=limits,
                                 timeout=10.0) for k in range(n)]
    if True:

        async def one(i: int) -> None:
            t_send = time.time()
            row: dict = {"i": i, "t_send": t_send}
            try:
                resp = await clients[i % n].post("/score")  # round-robin
                row["status"] = resp.status_code
                if resp.status_code == 200:
                    row.update(resp.json())
            except Exception as exc:  # a drop
                row["error"] = f"{type(exc).__name__}: {exc}"[:200]
            row["t_recv"] = time.time()
            rows.append(row)

        async def do_deploy() -> None:
            await asyncio.sleep(deploy_at)
            p = await asyncio.create_subprocess_exec(
                PY, str(HERE / "deploy.py"), B, str(n), "30", stdout=asyncio.subprocess.PIPE)
            out, _ = await p.communicate()
            deploy.update(json.loads(out))

        t0 = time.perf_counter()
        dep = asyncio.create_task(do_deploy())
        tasks = []
        for i in range(int(rps * duration)):  # open loop: send on schedule, never wait
            delay = t0 + i / rps - time.perf_counter()
            if delay > 0:
                await asyncio.sleep(delay)
            tasks.append(asyncio.create_task(one(i)))
        await asyncio.gather(*tasks)
        await dep
        for c in clients:
            await c.aclose()
    return rows, deploy


def analyse(rows: list[dict], dep: dict, n: int, rps: int) -> dict:
    ok = [r for r in rows if r.get("status") == 200]
    drops = [r for r in rows if r.get("status") != 200]
    mixed = [r for r in ok if r["h"] not in SIG or r["h"] != r["held"] or r["sig"] != SIG[r["h"]]]
    a = [r for r in ok if r["h"] == A]
    b = [r for r in ok if r["h"] == B]
    commit_by_pid = {c["pid"]: c["t"] for c in dep.get("commits", [])}
    # Per worker: an A response that STARTED after its own worker committed (must be 0).
    stale_own = [r for r in a if r["pid"] in commit_by_pid and r["ts"] > commit_by_pid[r["pid"]]]
    # Across workers: an A response that STARTED after some B response had COMPLETED.
    first_b_done = min((r["te"] for r in b), default=None)
    stale_cross = [r for r in a if first_b_done is not None and r["ts"] > first_b_done]
    last_a_start = max((r["ts"] for r in a), default=None)
    first_b_start = min((r["ts"] for r in b), default=None)
    lat = lambda rs: [r["t_recv"] - r["t_send"] for r in rs]  # noqa: E731
    t_cmd, t_prep = dep.get("t_cmd", 0), dep.get("t_prepared", 0)
    t_done = dep.get("t_all_committed", 0)
    pre = [r for r in ok if r["t_send"] < t_cmd]
    warm = [r for r in ok if t_cmd <= r["t_send"] < t_prep]
    post = [r for r in ok if r["t_send"] >= t_done]
    commits = sorted(commit_by_pid.values())
    return {
        "workers": n, "rps": rps, "sent": len(rows), "ok": len(ok), "drops": len(drops),
        "drop_samples": [d.get("error") or d.get("status") for d in drops[:3]],
        "mixed": len(mixed), "a": len(a), "b": len(b),
        "pids_seen": len({r["pid"] for r in ok}),
        "stale_own_worker": len(stale_own), "stale_cross_worker": len(stale_cross),
        "overlap_window_ms": (round((last_a_start - first_b_start) * 1000, 2)
                              if a and b else None),
        "deploy_abort": dep.get("abort"),
        "switch_s": round(dep["switch_s"], 3) if "switch_s" in dep else None,
        "prepare_s": round(t_prep - t_cmd, 3) if t_prep else None,
        "warm_s": sorted(round(p["warm_s"], 3) for p in dep.get("prepares", [])),
        "commit_spread_ms": round((commits[-1] - commits[0]) * 1000, 2) if commits else None,
        "lat_ms": {k: {"n": len(v), "p50": pct(lat(v), 50), "p99": pct(lat(v), 99),
                       "max": pct(lat(v), 100)} for k, v in
                   (("pre", pre), ("warm", warm), ("post", post))},
        "server_ms": {"p50": pct([r["te"] - r["ts"] for r in ok], 50),
                      "p99": pct([r["te"] - r["ts"] for r in ok], 99)},
        "send_lag_p99_ms": pct([r["t_send"] - (min(x["t_send"] for x in rows) + r["i"] / rps) for r in rows], 99),
        "load1": os.getloadavg()[0],
    }


def main() -> None:
    sys.path.insert(0, str(HERE))
    import sigguard

    sigguard.install("run.py")
    ap = argparse.ArgumentParser()
    ap.add_argument("workers", type=int)
    ap.add_argument("--rps", type=int, default=200)
    ap.add_argument("--duration", type=float, default=40)
    ap.add_argument("--deploy-at", type=float, default=10)
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or f"n{args.workers}-{int(time.time())}"
    load_before = os.getloadavg()[0]
    procs = start_workers(args.workers)
    try:
        rows, dep = asyncio.run(load(args.rps, args.duration, args.deploy_at, args.workers))
    finally:
        stop_workers(procs)
    summary = analyse(rows, dep, args.workers, args.rps)
    summary["load1_before"] = load_before
    summary["tag"] = tag
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / f"{tag}.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    (HERE / "results" / f"{tag}.json").write_text(json.dumps({"summary": summary, "deploy": dep}, indent=1))
    print(json.dumps(summary))


if __name__ == "__main__":
    sys.exit(main())
