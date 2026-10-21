"""Slice 4's load harness: drive `/score` through the compose `lb` at n replicas (PL-1237 Task 4).

    docker compose -f deploy/docker-compose.yml --profile app up -d --scale api=<n> --wait
    uv run python scripts/bench-deploy-path.py --replicas <n> --workers 1 --dsn <host DSN> \\
        --bucket <bucket> --rate 200 --seconds 30

Slice 5 reuses it (PL-1237 Task 4: "Slice 5 reuses it"). It adds no load generator of its own:
`scripts/bench-rating.py`'s `_drive` is the open-loop generator NFR-489 needs, and `_seed`
persists the bundle `POST /api/v1/score` reads. What this file adds is the *record* a run must
carry (PL-1537 R4.3, PL-9921 D4.2 and Acceptance 5), printed as one JSON object per run:

* the topology, the replica count (checked against what compose is actually running) and the
  worker count, stated rather than assumed;
* the **issued** and **offered** rate and the error count. OP-1455-M1 makes "issued = offered,
  0 errors" a condition of an NFR-489 reading, so a run that falls short of it is `void` and
  carries no reading;
* the load average at start and end, and the host.

It states the reading it ran under and chooses none: per-replica semantics is DP-3's.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
COMPOSE = ROOT / "deploy" / "docker-compose.yml"
TOPOLOGY = "nginx lb (deploy/lb.conf), round-robin over the api replicas via Docker DNS"


def _bench_rating() -> Any:
    """Load `bench-rating.py` (a hyphenated name cannot be imported by statement)."""
    path = ROOT / "scripts" / "bench-rating.py"
    spec = importlib.util.spec_from_file_location("bench_rating", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["bench_rating"] = module
    spec.loader.exec_module(module)
    return module


def running_api_replicas() -> int:
    """How many `api` containers compose is running — the count a record must not assume."""
    out = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE), "--profile", "app", "ps", "--status", "running",
         "--format", "{{.Service}}"],
        check=True, capture_output=True, text=True,
    ).stdout
    return sum(1 for line in out.splitlines() if line.strip() == "api")


def host() -> dict[str, str]:
    """Acceptance 5's host fields: nproc, free -g, and the machine type if one answers."""
    def run(*cmd: str) -> str:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

    machine_type = run(
        "curl", "-s", "-m", "2", "-H", "Metadata-Flavor: Google",
        "http://metadata.google.internal/computeMetadata/v1/instance/machine-type",
    )
    return {
        "nproc": run("nproc"),
        "free_g": run("free", "-g"),
        "machine_type": machine_type.rsplit("/", 1)[-1] or "not on a metadata server",
    }


def observed_workers(processes: dict[str, str]) -> dict[str, int]:
    """N per api container, as the deploy switch reported it (`PL-1766` D5.13): the number of
    named processes under each container. Observed, not assumed."""
    counts: dict[str, int] = {}
    for name in processes:
        container = name.split(":")[0]
        counts[container] = counts.get(container, 0) + 1
    return counts


def record(
    *,
    rung: Any,
    replicas: int,
    running: int,
    workers: int,
    tree: str,
    reading: str = "diagnostic",
    observed: dict[str, int] | None = None,
) -> dict[str, Any]:
    """One run's record. `void` is the D4.2 rule: issued short of offered, or any error.

    `reading` is `exit` (through `live`: no `rating_version_ref`, a version deployed by the
    governed route; DP-S5-Q1 (a)) or `diagnostic` (an explicit ref; never the NFR-489 exit
    reading). A run whose observed N differs from the declared `workers` is void (DP-S5-Q2 (a)).
    """
    issued_short = rung.achieved_rps < rung.offered_rps * 0.99
    reasons = []
    if issued_short:
        reasons.append(f"issued {rung.achieved_rps:.1f} rps short of offered {rung.offered_rps}")
    if rung.errors:
        reasons.append(f"{rung.errors} errors")
    if running != replicas:
        reasons.append(f"compose runs {running} api replicas, run claims {replicas}")
    if observed is not None and any(n != workers for n in observed.values()):
        reasons.append(f"observed workers per replica {observed}, run declares {workers}")
    return {
        "tree": tree,
        "topology": TOPOLOGY,
        "replicas": replicas,
        "replicas_running": running,
        "workers_per_replica": workers,
        "workers_observed": observed,
        "reading": reading,
        "offered_rps": rung.offered_rps,
        "issued_rps": round(rung.achieved_rps, 2),
        "errors": rung.errors,
        "load_start": rung.load_start,
        "load_end": rung.load_end,
        "host": host(),
        "void": bool(reasons),
        "void_reasons": reasons,
    }


def _governed_run(bench: Any, args: argparse.Namespace) -> tuple[Any, int, dict[str, int]]:
    """Seed through the services, deploy by `POST /environments/{dev,uat}/deployments`, and drive
    `/score` with no `rating_version_ref` so the request reads `live` (`PL-1766` D5.12).

    UNPROVEN: it needs the compose stack and a granted window; nothing here has run.
    """
    sys.path.insert(0, str(ROOT))
    from backend.tests.deploy_stack_helpers import api, governed_workspace

    ws = governed_workspace(approved=True)
    analyst, deployer = ws.users["analyst"], ws.users["deployer"]
    job = api("POST", f"/api/v1/rating-versions/{ws.rating_version_id}/compile", analyst)
    while api("GET", f"/api/v1/jobs/{job['id']}", analyst)["status"] not in {"succeeded", "failed"}:
        time.sleep(1)
    done: dict[str, Any] = {}
    for environment in ("dev", "uat"):
        done = api(
            "POST",
            f"/api/v1/environments/{environment}/deployments",
            deployer,
            {"rating_version_ref": ws.rating_version_ref, "reason": "bench"},
        )
    observed = observed_workers(done["switch"]["processes"])
    url = f"{args.base_url}/api/v1/score"
    body = {k: v for k, v in ws.quote.items() if k != "options"}
    asyncio.run(bench._await_ready(f"{args.base_url}/healthz"))
    asyncio.run(bench._drive(url, ws.headers, body, rate=25, seconds=4))  # warm-up, discarded
    running = running_api_replicas()
    rung = asyncio.run(bench._drive(url, ws.headers, body, rate=args.rate, seconds=args.seconds))
    return rung, running, observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--replicas", type=int, required=True)
    parser.add_argument("--workers", type=int, default=1, help="uvicorn workers per replica")
    parser.add_argument("--rate", type=int, default=200)
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--dsn", required=True, help="host-side DSN of the compose postgres")
    parser.add_argument("--bucket", default="gip-blobs")
    parser.add_argument(
        "--governed",
        action="store_true",
        help="the NFR-489 exit reading: seed through the services, deploy by the route, send "
        "quotes with no rating_version_ref (needs GIP_N_SHA and the stack up; PL-1766 D5.12)",
    )
    parser.add_argument("--dry-run", action="store_true", help="print the record shape; no load")
    args = parser.parse_args()

    tree = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()

    bench = _bench_rating()
    observed: dict[str, int] | None = None
    if args.governed and not args.dry_run:
        rung, running, observed = _governed_run(bench, args)
    elif args.dry_run:
        rung = bench.Rung(
            offered_rps=args.rate, achieved_rps=float(args.rate), samples=[], errors=0,
            load_start=bench.loadavg(), load_end=bench.loadavg(),
        )
        running = args.replicas
    else:
        bundle = asyncio.run(
            bench._serialisable(with_gbm=False, n_expr=bench.N_EXPR_STEPS, rounds=300, rows=5_000)
        )
        workspace_id, api_key = asyncio.run(bench._seed(bundle, dsn=args.dsn, bucket=args.bucket))
        asyncio.run(bench._await_ready(f"{args.base_url}/healthz"))
        headers = {"X-API-Key": api_key, "Workspace-Id": workspace_id}
        body = json.loads(bench._ctx().model_dump_json())
        url = f"{args.base_url}/api/v1/score"
        asyncio.run(bench._drive(url, headers, body, rate=25, seconds=4))  # warm-up, discarded
        running = running_api_replicas()
        rung = asyncio.run(bench._drive(url, headers, body, rate=args.rate, seconds=args.seconds))

    out = record(
        rung=rung,
        replicas=args.replicas,
        running=running,
        workers=args.workers,
        tree=tree,
        reading="exit" if args.governed else "diagnostic",
        observed=observed,
    )
    print(json.dumps(out, indent=2))
    return 1 if out["void"] else 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    raise SystemExit(main())
