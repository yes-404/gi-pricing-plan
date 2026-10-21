#!/usr/bin/env python3
"""The demo entrance: one command from a clean checkout to a browser (FR-408).

    uv run python scripts/demo.py

It starts the compose stack including the local provider behind the `auth` profile,
migrates, fetches and seeds freMTPL2 through the platform's own Job path, then runs the
API and the frontend — and prints the URL. The browser signs in through that provider
(`analyst` / `analyst`, FR-398), and the seeded membership answers the login.
`Ctrl-C` stops everything it started.

**One switch, and it is the refusal that already exists.** Every part of this hangs off
`dev_auth_enabled` (FR-387), which is `False` by default and *raises at startup* in a
deployed environment. This script sets it for the processes it starts and refuses to run
where `GIP_ENVIRONMENT` is not local or dev — a page that lists every route beside a
pre-authenticated session is a genuine hole if it ever ships, so there is no second flag to
leave on by mistake.

What it does not do is hide failure. Each step's exit code is checked and reported by name;
a demo that limps to a browser window showing an empty list has wasted the reader's time in
the most expensive way.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager, suppress
from pathlib import Path
from typing import Any, Final

#: Every print here is flushed. The subprocesses this starts write to the same descriptor
#: unbuffered, so a buffered step header appears *after* the output it introduces — and
#: when stdout is a file rather than a terminal, the final "open this URL" banner can sit
#: in the buffer indefinitely while the demo looks like it never finished starting.
ROOT: Final = Path(__file__).resolve().parents[1]
SEED_RECORD: Final = ROOT / "examples" / "fremtpl2" / "data" / "last-seed.json"
LOCAL_ENVIRONMENTS: Final = frozenset({"local", "dev", ""})

API_PORT: Final = 8000
FRONTEND_PORT: Final = 5173

#: The scripted journeys `--journey` can run after the seed (RL-1521: `scripts/demo.py`-style ONE
#: command). Off by default: a Phase 1 demo would otherwise pay for the whole journey.
JOURNEYS: Final = ("wf-699", "wf-701")
#: Where `--journey wf-701` runs: the API this command starts (`local`) or the Slice 4 stack's `lb`
#: that is already up (`compose`, PL-1710 T6), whose `api` replicas the A2/C4 limb is walked on.
TARGETS: Final = ("local", "compose")
COMPOSE_FILE: Final = "deploy/docker-compose.yml"
#: PL-1710 acceptance 4: WF-701's part of the run, alone on the box. A miss is recorded, not tuned.
WF701_TARGET_SECONDS: Final = 600
#: A2 and C4 show a COMMIT set of two: `docker compose --profile app up --scale api=2`.
API_REPLICAS: Final = 2


class DemoRefusedError(RuntimeError):
    """The demo will not run here."""


def check_environment(environ: dict[str, str] | None = None) -> None:
    """Refuse anywhere the platform would refuse development identity.

    Checked here as well as in the API so the refusal arrives before anything is started:
    a stack brought up and then rejected is a worse message than one never brought up.
    """
    environ = os.environ if environ is None else environ
    configured = environ.get("GIP_ENVIRONMENT", "").strip().lower()
    if configured not in LOCAL_ENVIRONMENTS:
        raise DemoRefusedError(
            f"GIP_ENVIRONMENT is {configured!r}. The demo entrance exists only where "
            "development identity does (FR-408), and development identity refuses to "
            "start outside local/dev."
        )


def run(command: list[str], *, step: str, env: dict[str, str] | None = None) -> None:
    """Run to completion, or stop the demo naming the step that failed."""
    print(f"\n── {step} " + "─" * max(0, 60 - len(step)), flush=True)
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    if completed.returncode != 0:
        raise DemoRefusedError(f"{step} failed ({' '.join(command)} → {completed.returncode}).")


def wait_for(url: str, *, step: str, timeout: float = 90.0) -> None:
    """Poll until the URL answers anything at all.

    *Anything*: a 401 from an endpoint requiring a credential proves the server is up as
    well as a 200 does, and waiting for 200 on an authenticated route would hang forever.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except urllib.error.HTTPError:
            return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(0.5)
    raise DemoRefusedError(f"{step} did not answer on {url} within {timeout:.0f}s.")


def read_seed_record(path: Path = SEED_RECORD) -> dict[str, str]:
    if not path.is_file():
        raise DemoRefusedError(
            f"No seed record at {path}. `uv run python examples/fremtpl2/seed.py` writes it."
        )
    record: dict[str, str] = json.loads(path.read_text(encoding="utf-8"))
    missing = [key for key in ("workspace_id", "analyst_id") if key not in record]
    if missing:
        raise DemoRefusedError(f"Seed record is missing {', '.join(missing)}.")
    return record


def require_free(port: int, *, step: str) -> None:
    """Refuse before starting anything if something already holds the port.

    This command promises to report only servers it started. `wait_for` returns on **any**
    answer, so with a stale server on 5173 it printed "Open http://localhost:5173/demo"
    while both its children were dead of `[Errno 98] address already in use` — sending the
    reader to a different server with a different identity.

    Checked up front rather than after the fact: polling the child after `wait_for` races
    the child's own death (`pnpm` outlives the `vite` it spawned by a moment, so
    `poll()` was still `None` when the stale server had already answered). A port that is
    free before the child starts and answering after it does is the child's.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(1.0)
        if probe.connect_ex(("127.0.0.1", port)) != 0:
            return
    raise DemoRefusedError(
        f"Port {port} is already in use, so {step} cannot start there and this command "
        f"would end up reporting a server it did not start. Stop the process holding it "
        f"(`ss -ltnp | grep {port}` names it), or use --no-frontend."
    )


def _still_running(process: subprocess.Popen[bytes], *, step: str) -> None:
    """Backstop for the case `require_free` cannot see: a child that dies of its own accord.

    A short settle first, because `pnpm` exits a moment after the `vite` it spawned.
    """
    with suppress(subprocess.TimeoutExpired):
        process.wait(timeout=2.0)
        raise DemoRefusedError(f"{step} exited with {process.returncode} instead of serving.")


@contextmanager
def background(
    command: list[str], *, step: str, env: dict[str, str]
) -> Iterator[subprocess.Popen[bytes]]:
    """Start a long-running child and stop it — **and its children** — on the way out.

    `start_new_session=True` plus `killpg`, not `Popen.send_signal`. The frontend is
    `pnpm` → `sh -c vite`, and signalling only the direct child left vite running after
    Ctrl-C: the command promises to stop everything it started, and a stray dev server
    holding port 5173 makes the next run fail for a reason that looks unrelated. Found by
    running it and then looking for what survived.
    """
    print(f"\n── {step} " + "─" * max(0, 60 - len(step)), flush=True)
    process = subprocess.Popen(command, cwd=ROOT, env=env, start_new_session=True)
    try:
        yield process
    finally:
        print(f"   stopping {step}…", flush=True)
        _stop_group(process)


def _stop_group(process: subprocess.Popen[bytes]) -> None:
    """SIGINT the child's whole process group, then SIGKILL what is left."""
    for send in (signal.SIGINT, signal.SIGKILL):
        if process.poll() is not None:
            return
        with suppress(ProcessLookupError, PermissionError):
            os.killpg(os.getpgid(process.pid), send)
        with suppress(subprocess.TimeoutExpired):
            process.wait(timeout=10 if send is signal.SIGINT else 5)


def demo_env() -> dict[str, str]:
    """The environment the demo's processes run with.

    The local provider (FR-398) is started behind the `auth` profile, and the API must
    verify against it: `deploy/README.md` pins these OIDC values, and the browser signs in
    through this issuer — so the one-command demo sets them here, not on the operator.
    Exposed as a function so `test_demo_command.py` can assert the browser path is wired
    without running the orchestration.
    """
    return {
        **os.environ,
        "GIP_DEV_AUTH_ENABLED": "true",
        "GIP_DATABASE_URL": os.environ.get(
            "GIP_DATABASE_URL",
            "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing",
        ),
        "GIP_OIDC_ISSUER": "http://localhost:8080/realms/gi-pricing",
        "GIP_OIDC_CLIENT_ID": "gi-pricing-frontend",
        "GIP_OIDC_AUDIENCE": "gi-pricing-api",
        "GIP_OIDC_JWKS_URL": (
            "http://localhost:8080/realms/gi-pricing/protocol/openid-connect/certs"
        ),
    }


def demo_queues() -> list[str]:
    """Every queue the platform routes a Job to, plus the relay's: read from the routing table,
    never listed here, so a new pool is consumed by the demo without an edit (PL-1714 E4.5).
    Imported inside the function: the demo script is not otherwise coupled to the backend."""
    from app.platform.jobs import DEFAULT_QUEUE_FOR_KIND
    from app.worker.celery_app import RELAY_QUEUE

    return sorted({q.value for q in DEFAULT_QUEUE_FOR_KIND.values()} | {RELAY_QUEUE.value})


def worker_command() -> list[str]:
    """The Celery worker the journey needs. The API only writes an outbox row for a Job
    (`07` FR-406); with no worker the first 202 never completes and the journey would wait for
    ever. One process consumes every pool: this is the local demo, not the deployed topology,
    whose per-pool sizing (FR-405) is `deploy/docker-compose.yml`'s."""
    return [
        "uv",
        "run",
        "celery",
        "-A",
        "app.worker.entrypoint",
        "worker",
        "--queues",
        ",".join(demo_queues()),
        "--concurrency",
        "2",
    ]


def beat_command() -> list[str]:
    """The outbox relay: without `beat`, committed Jobs stay `queued` and nothing says why
    (`.claude/skills/dev-commands`). Its schedule file is kept under the gitignored data dir."""
    schedule = ROOT / "examples" / "fremtpl2" / "data" / "celerybeat-schedule"
    return [
        "uv",
        "run",
        "celery",
        "-A",
        "app.worker.entrypoint",
        "beat",
        "--schedule",
        str(schedule),
    ]


def journey_failure_line(failure: Any, journey: str = "wf-699") -> str:
    """The one line a failed journey prints: the step and the problem's code, built from the
    failure's fields and never from its text."""
    status = f" (HTTP {failure.status})" if failure.status is not None else ""
    return f"the {journey.upper()} journey failed at {failure.step}: {failure.code}{status}"


def compose_command(*args: str) -> list[str]:
    """`docker compose` on the stack's file and `app` profile; `GIP_COMPOSE_PROJECT` names the
    project when the stack was not started under the default one."""
    project = os.environ.get("GIP_COMPOSE_PROJECT")
    return [
        "docker", "compose", *(["-p", project] if project else []),
        "-f", COMPOSE_FILE, "--profile", "app", *args,
    ]


def compose_services() -> set[str]:
    """The services the stack must be running: the datastores, `lb`, `api`, and one `worker-<pool>`
    per queue the routing table names (derived, so a new pool is required without an edit)."""
    from app.platform.jobs import DEFAULT_QUEUE_FOR_KIND

    pools = {f"worker-{queue.value}" for queue in DEFAULT_QUEUE_FOR_KIND.values()}
    return {"postgres", "redis", "minio", "lb", "api", *pools}


def compose_running() -> dict[str, int]:
    """Each running service and how many containers run it, from `docker compose ps`."""
    done = subprocess.run(
        compose_command("ps", "--status", "running", "--format", "{{.Service}}"),
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    counts: dict[str, int] = {}
    for name in done.stdout.split():
        counts[name] = counts.get(name, 0) + 1
    return counts


def check_compose_up(running: dict[str, int]) -> None:
    """Refuse, naming what is missing, before anything is seeded (R9). `api` must run twice."""
    missing = sorted(compose_services() - running.keys() - {"api"})
    if running.get("api", 0) < API_REPLICAS:
        missing.append(f"api (x{API_REPLICAS}; {running.get('api', 0)} running)")
    if missing:
        up = f"up -d --wait --scale api={API_REPLICAS}"
        raise DemoRefusedError(
            f"The compose stack is not up. Missing: {', '.join(missing)}. "
            f"Start it from tools-main: `docker compose -f {COMPOSE_FILE} --profile app {up}`."
        )


def api_hosts() -> frozenset[str]:
    """The hostname of every `api` container (Docker's default is the short container id)."""
    done = subprocess.run(
        compose_command("ps", "-q", "api"), cwd=ROOT, capture_output=True, text=True, check=False
    )
    return frozenset(line.strip()[:12] for line in done.stdout.splitlines() if line.strip())


def _load_journey(module: str) -> Any:
    example = ROOT / "examples" / "fremtpl2"
    sys.path.insert(0, str(example))
    spec = importlib.util.spec_from_file_location(f"fremtpl2_{module}", example / f"{module}.py")
    assert spec is not None
    assert spec.loader is not None
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def run_journey(
    record: dict[str, str], journey_name: str = "wf-699", *, target: str = "local"
) -> None:
    """Walk WF-699 (and for `wf-701`, then WF-701's deployment steps) over HTTP against the API
    this command started, or against the compose stack's `lb` (`examples/fremtpl2/journey.py`,
    `journey_wf701.py`).

    The 20,000-policy sample is the journey's dislocation portfolio, and its output says so.
    """
    import httpx

    walker = _load_journey("journey_wf701" if journey_name == "wf-701" else "journey")
    port = int(os.environ.get("GIP_LB_PORT", "8000")) if target == "compose" else API_PORT
    base_url = f"http://localhost:{port}/api/v1"
    print(f"\n── the {journey_name.upper()} journey over HTTP " + "─" * 30, flush=True)
    started = time.monotonic()

    def log(line: str) -> None:
        print(line, flush=True)

    with httpx.Client(base_url=base_url, timeout=120.0) as client:
        try:
            first = walker.run_wf699_journey(client, record, log=log)
            if journey_name == "wf-701":
                split = time.monotonic()
                print(f"   WF-699 part done in {split - started:.0f}s", flush=True)
                compose = target == "compose"
                walker.run_wf701_after(
                    client, record, first, log=log,
                    replica_hosts=api_hosts if compose else None,
                    stream_client=(lambda: httpx.Client(base_url=base_url, timeout=60.0))
                    if compose else None,
                )
                elapsed = time.monotonic() - split
                verdict = "within" if elapsed <= WF701_TARGET_SECONDS else "OVER"
                print(
                    f"   WF-701 part done in {elapsed:.0f}s: {verdict} the pre-registered "
                    f"{WF701_TARGET_SECONDS // 60} min target (recorded, not tuned)",
                    flush=True,
                )
        except walker.JourneyStepFailed as failure:
            raise DemoRefusedError(journey_failure_line(failure, journey_name)) from failure
    print(f"   journey done in {time.monotonic() - started:.0f}s", flush=True)


def check_served_page(url: str) -> None:
    """G2 ends with the frontend serving a 200 page (RL-1521); anything else is a refusal."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            status = response.status
    except urllib.error.HTTPError as failure:
        raise DemoRefusedError(f"the frontend answered {failure.code} at {url}, not 200.") from None
    if status != 200:
        raise DemoRefusedError(f"the frontend answered {status} at {url}, not 200.")
    print(f"   served page: {url} answered 200", flush=True)


def prepare_world(*, rows: int | None, skip_seed: bool, env: dict[str, str]) -> dict[str, str]:
    """Seed (unless `skip_seed`), read the seed record, and run the two pre-flights. Shared by the
    local demo and the compose run: both need the same seeded workspace before a journey."""
    if not skip_seed:
        arff = ROOT / "examples" / "fremtpl2" / "data" / "freMTPL2freq.arff"
        if not arff.is_file():
            run(
                ["uv", "run", "python", "examples/fremtpl2/fetch.py"],
                step="fetch freMTPL2 (36 MB, once)",
                env=env,
            )
        seed = ["uv", "run", "python", "examples/fremtpl2/seed.py"]
        if rows is not None:
            seed += ["--rows", str(rows)]
        run(seed, step="seed freMTPL2 through the real Job path", env=env)

    # The record the seed wrote is the membership the login resolves to (FR-398).
    # Read it here — after the seed, and in `--skip-seed` runs as the proof the
    # workspace this run reuses was seeded at all.
    record = read_seed_record()
    # FD-1494 limb 1: the record is a file, the database may have been reset since. Checked on
    # every path and BEFORE the rule-set pre-flight, which for an absent workspace takes its zero
    # branch and prints "the seed did not finish", the wrong message for this cause.
    run(
        [
            "uv", "run", "python", "scripts/check-seed-record.py",
            record["workspace_id"], record["analyst_id"],
        ],
        step="pre-flight: the seed record's workspace and analyst are in the database",
        env=env,
    )
    # The seed, or a `--skip-seed` run's earlier seed, must have left rule sets every
    # member of which is approved: a workspace reset by the FD-1356 data reset has none that
    # run (RL-1407 condition 2). Read-only, and it needs the migrated database.
    run(
        ["uv", "run", "python", "scripts/check-rule-sets-runnable.py", record["workspace_id"]],
        step="pre-flight: the demo workspace's rule sets are runnable",
        env=env,
    )
    return record


def demo(
    *,
    rows: int | None,
    skip_seed: bool,
    frontend: bool,
    journey: str | None = None,
    target: str = "local",
) -> int:
    if target == "compose":
        if journey != "wf-701":
            raise DemoRefusedError("--target compose runs only `--journey wf-701` (PL-1710 T6).")
        return demo_compose(rows=rows, skip_seed=skip_seed)
    if journey is not None and not frontend:
        # G2 is a journey that ENDS with the frontend serving a 200 page (RL-1521). Without the
        # frontend it would run, wait for Ctrl-C and exit 0 with no such check.
        raise DemoRefusedError(
            "--journey needs the frontend: the command ends with it serving a 200 page "
            "(RL-1521). Drop --no-frontend."
        )
    if journey is not None and shutil.which("pnpm") is None:
        # Refused up front, not after a seed: the fallback below would run the API only.
        raise DemoRefusedError(
            "--journey needs pnpm to serve the frontend (RL-1521), and pnpm is not on PATH. "
            "`npm config set prefix ~/.npm-global && npm i -g pnpm` installs it."
        )
    check_environment()
    started = time.monotonic()

    env = demo_env()

    run(
        [
            "docker", "compose", "-f", "deploy/docker-compose.yml",
            "--profile", "auth", "up", "-d", "--wait",
        ],
        step="infrastructure (postgres, redis, minio, keycloak)",
        env=env,
    )
    run(["uv", "run", "alembic", "upgrade", "head"], step="migrations", env=env)

    record = prepare_world(rows=rows, skip_seed=skip_seed, env=env)
    api = [
        "uv", "run", "uvicorn", "app.main:create_app", "--factory",
        "--app-dir", "backend/src", "--port", str(API_PORT),
    ]
    frontend_command = [
        # `--strictPort`: without it Vite quietly moves to the next free port when 5173 is
        # taken, and this command then prints a URL for a server it did not start — a
        # stale dev server with a different identity, answering happily. Observed exactly
        # once, which was enough.
        "pnpm", "--dir", "frontend", "dev", "--port", str(FRONTEND_PORT), "--strictPort",
        # `--host 127.0.0.1` binds **both** loopback families; the default binds `[::1]`
        # only, and nothing else changes — the external interface still refuses either way.
        # It matters when the demo runs on a remote machine: `ssh -L 5173:localhost:5173`
        # resolves `localhost` on the *server*, usually to 127.0.0.1 first, and the tunnel
        # then fails with "connect failed: Connection refused" against a dev server that is
        # running perfectly.
        "--host", "127.0.0.1",
    ]
    if frontend and shutil.which("pnpm") is None:
        print(
            "\n   pnpm is not on PATH — starting the API only. "
            "`npm config set prefix ~/.npm-global && npm i -g pnpm` installs it.",
            flush=True,
        )
        frontend = False

    require_free(API_PORT, step="the API")
    # One stack for everything this command starts: they stop together, in reverse, on the way out.
    with ExitStack() as started_here:
        api_process = started_here.enter_context(
            background(api, step=f"API on :{API_PORT}", env=env)
        )
        _still_running(api_process, step="the API")
        wait_for(f"http://localhost:{API_PORT}/api/v1/demo/guide", step="API")
        _verify_journey_postconditions(record, env)
        if journey is not None:
            # The API only writes an outbox row for a Job; the worker and the relay consume it.
            worker_env = {**env, "PYTHONPATH": str(ROOT / "backend" / "src")}
            worker_process = started_here.enter_context(
                background(
                    worker_command(),
                    step=f"Celery worker ({', '.join(demo_queues())})",
                    env=worker_env,
                )
            )
            beat_process = started_here.enter_context(
                background(beat_command(), step="Celery beat (the outbox relay)", env=worker_env)
            )
            _still_running(worker_process, step="the Celery worker")
            _still_running(beat_process, step="Celery beat")
            run_journey(record, journey)
        if not frontend:
            print(f"\n   API ready: http://localhost:{API_PORT}/docs", flush=True)
            print("   Ctrl-C to stop.\n", flush=True)
            _wait_for_interrupt()
            return 0
        require_free(FRONTEND_PORT, step="the frontend")
        frontend_process = started_here.enter_context(
            background(frontend_command, step=f"frontend on :{FRONTEND_PORT}", env=env)
        )
        _still_running(frontend_process, step="the frontend")
        wait_for(f"http://localhost:{FRONTEND_PORT}/", step="frontend")
        if journey is not None:
            check_served_page(f"http://localhost:{FRONTEND_PORT}/")
        elapsed = time.monotonic() - started
        print(
            f"\n{'═' * 62}\n"
            f"  Open  http://localhost:{FRONTEND_PORT}/demo\n"
            f"{'═' * 62}\n"
            f"  Seeded to a usable state in {elapsed:.0f}s from the start of this command"
            f"  (NFR-529's budget is < 5 min; this run is not a timing measurement).\n\n"
            "  That page is derived from this checkout — the specs' view tables\n"
            "  against the router, the published contract, and the roadmap. It says\n"
            "  what is worth clicking and, more usefully, what is not built yet.\n\n"
            f"  The seeded membership that answers the login (FR-398) is analyst\n"
            f"  {record['analyst_id']} in workspace {record['workspace_id']}.\n\n"
            "  Ctrl-C to stop everything this command started.\n",
            flush=True,
        )
        _wait_for_interrupt()
    return 0


def demo_compose(*, rows: int | None, skip_seed: bool) -> int:
    """WF-701 against the Slice 4 stack: refuse first, naming what is down (R9), then seed through
    the stack's own ports, start the one process the stack lacks (the outbox relay, `beat`), walk
    the journey over `lb`, and stop the relay. The frontend is not part of this run."""
    check_environment()
    check_compose_up(compose_running())
    started = time.monotonic()
    env = demo_env()
    record = prepare_world(rows=rows, skip_seed=skip_seed, env=env)
    print("\n── the outbox relay (beat) from the stack's image " + "─" * 12, flush=True)
    relay = subprocess.run(
        [*compose_command("run", "--rm", "-d", "worker-default"), "celery", "-A",
         "app.worker.entrypoint", "beat", "--schedule", "/tmp/celerybeat-schedule"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=False,
    )
    if relay.returncode != 0 or not relay.stdout.strip():
        raise DemoRefusedError(
            f"the outbox relay did not start ({relay.returncode}): {relay.stderr[-300:]}"
        )
    container = relay.stdout.strip().splitlines()[-1]
    try:
        run_journey(record, "wf-701", target="compose")
    finally:
        subprocess.run(["docker", "rm", "-f", container], check=False, capture_output=True)
    print(f"\n   compose run done in {time.monotonic() - started:.0f}s", flush=True)
    return 0


def _verify_journey_postconditions(record: dict[str, str], env: dict[str, str]) -> None:
    """WF-698 §4's demo subset, over HTTP: an approved model exists (W7-5 T1).

    The full §4 list includes bandings, a peril structure and a reconciliation the demo
    does not seed; the demo's subset is the validated dataset, the split, one approved
    model and the rating version. The approved-model check is the one the API can answer
    without extra ids, and it fails the demo loudly if the seed produced nothing approved
    — a demo that reaches a browser with no model to show has wasted the reader's time.
    """
    import urllib.request

    url = f"http://localhost:{API_PORT}/api/v1/models?status=approved&limit=5"
    request = urllib.request.Request(
        url,
        headers={
            "x-dev-principal-id": record["analyst_id"],
            "Workspace-Id": record["workspace_id"],
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = json.loads(response.read())
    except urllib.error.HTTPError as refused:
        # FD-1494 limb 2: an HTTP refusal is a refusal, not a traceback. The usual cause is a
        # record naming a workspace or analyst the database no longer holds.
        raise DemoRefusedError(
            f"The API answered {refused.code} to the approved-model check for workspace "
            f"{record['workspace_id']}. The seed record ({SEED_RECORD.relative_to(ROOT)}) may "
            "name a workspace or analyst the database no longer holds: re-run the seed "
            "without --skip-seed."
        ) from None
    approved = body.get("items", [])
    if not approved:
        raise DemoRefusedError(
            "WF-698's demo subset: no approved model after the seed — see the seed output"
        )
    print(f"  WF-698 demo subset: {len(approved)} approved model(s)", flush=True)


def _wait_for_interrupt() -> None:
    """Block until Ctrl-C, and treat it as the documented way to stop rather than a crash.

    Also caught in `main`, because a signal that arrives while a child is being started
    lands outside this function and would otherwise print a traceback at a moment when
    nothing has gone wrong.
    """
    with suppress(KeyboardInterrupt):
        while True:
            time.sleep(3600)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, help="Seed a sample rather than all 678 013")
    parser.add_argument(
        "--skip-seed", action="store_true", help="Reuse the workspace from the last run"
    )
    parser.add_argument("--no-frontend", action="store_true", help="API only")
    parser.add_argument(
        "--journey",
        choices=JOURNEYS,
        help="After the seed, start a worker and walk this scripted journey over HTTP, "
        "then serve the frontend (G2: WF-699 A to E and its deploy step; wf-701 adds WF-701's "
        "deployment steps A1-A6, C1-C4, C6, C7)",
    )
    parser.add_argument(
        "--target",
        choices=TARGETS,
        default="local",
        help="`compose` walks `--journey wf-701` against the Slice 4 stack already up "
        "(`--scale api=2`) instead of starting an API here",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return demo(
            rows=args.rows,
            skip_seed=args.skip_seed,
            frontend=not args.no_frontend,
            journey=args.journey,
            target=args.target,
        )
    except DemoRefusedError as exc:
        print(f"\n  {exc}\n", file=sys.stderr, flush=True)
        return 1
    except KeyboardInterrupt:
        # Ctrl-C is how this command is meant to end. A traceback would suggest otherwise.
        print("\n  stopped.\n", flush=True)
        return 0


if __name__ == "__main__":
    sys.exit(main())
