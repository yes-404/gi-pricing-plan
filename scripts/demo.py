#!/usr/bin/env python3
"""The demo entrance: one command from a clean checkout to a browser (FR-PLAT-53).

    uv run python scripts/demo.py

It starts the compose stack including the local provider behind the `auth` profile,
migrates, fetches and seeds freMTPL2 through the platform's own Job path, then runs the
API and the frontend — and prints the URL. The browser signs in through that provider
(`analyst` / `analyst`, FR-PLAT-58), and the seeded membership answers the login.
`Ctrl-C` stops everything it started.

**One switch, and it is the refusal that already exists.** Every part of this hangs off
`dev_auth_enabled` (FR-PLAT-1), which is `False` by default and *raises at startup* in a
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
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Final

#: Every print here is flushed. The subprocesses this starts write to the same descriptor
#: unbuffered, so a buffered step header appears *after* the output it introduces — and
#: when stdout is a file rather than a terminal, the final "open this URL" banner can sit
#: in the buffer indefinitely while the demo looks like it never finished starting.
ROOT: Final = Path(__file__).resolve().parents[1]
SEED_RECORD: Final = ROOT / "examples" / "fremtpl2" / "data" / "last-seed.json"
LOCAL_ENVIRONMENTS: Final = frozenset({"local", "dev", ""})

API_PORT: Final = 8000
FRONTEND_PORT: Final = 5173


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
            "development identity does (FR-PLAT-53), and development identity refuses to "
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

    The local provider (FR-PLAT-58) is started behind the `auth` profile, and the API must
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


def demo(*, rows: int | None, skip_seed: bool, frontend: bool) -> int:
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

    # The record the seed wrote is the membership the login resolves to (FR-PLAT-58).
    # Read it here — after the seed, and in `--skip-seed` runs as the proof the
    # workspace this run reuses was seeded at all.
    record = read_seed_record()
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
    with background(api, step=f"API on :{API_PORT}", env=env) as api_process:
        _still_running(api_process, step="the API")
        wait_for(f"http://localhost:{API_PORT}/api/v1/demo/guide", step="API")
        _verify_journey_postconditions(record, env)
        if not frontend:
            print(f"\n   API ready: http://localhost:{API_PORT}/docs", flush=True)
            print("   Ctrl-C to stop.\n", flush=True)
            _wait_for_interrupt()
            return 0
        require_free(FRONTEND_PORT, step="the frontend")
        with background(
            frontend_command, step=f"frontend on :{FRONTEND_PORT}", env=env
        ) as frontend_process:
            _still_running(frontend_process, step="the frontend")
            wait_for(f"http://localhost:{FRONTEND_PORT}/", step="frontend")
            elapsed = time.monotonic() - started
            print(
                f"\n{'═' * 62}\n"
                f"  Open  http://localhost:{FRONTEND_PORT}/demo\n"
                f"{'═' * 62}\n"
                f"  Seeded to a usable state in {elapsed:.0f}s"
                f"  (NFR-PLAT-4: < 5 min on a developer laptop).\n\n"
                "  That page is derived from this checkout — the specs' view tables\n"
                "  against the router, the published contract, and the roadmap. It says\n"
                "  what is worth clicking and, more usefully, what is not built yet.\n\n"
                f"  The seeded membership that answers the login (FR-PLAT-58) is analyst\n"
                f"  {record['analyst_id']} in workspace {record['workspace_id']}.\n\n"
                "  Ctrl-C to stop everything this command started.\n",
                flush=True,
            )
            _wait_for_interrupt()
    return 0


def _verify_journey_postconditions(record: dict[str, str], env: dict[str, str]) -> None:
    """wf-01 §4's demo subset, over HTTP: an approved model exists (W7-5 T1).

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
    with urllib.request.urlopen(request, timeout=10) as response:
        body = json.loads(response.read())
    approved = body.get("items", [])
    if not approved:
        raise DemoRefusedError(
            "wf-01's demo subset: no approved model after the seed — see the seed output"
        )
    print(f"  wf-01 demo subset: {len(approved)} approved model(s)", flush=True)


def _wait_for_interrupt() -> None:
    """Block until Ctrl-C, and treat it as the documented way to stop rather than a crash.

    Also caught in `main`, because a signal that arrives while a child is being started
    lands outside this function and would otherwise print a traceback at a moment when
    nothing has gone wrong.
    """
    with suppress(KeyboardInterrupt):
        while True:
            time.sleep(3600)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, help="Seed a sample rather than all 678 013")
    parser.add_argument(
        "--skip-seed", action="store_true", help="Reuse the workspace from the last run"
    )
    parser.add_argument("--no-frontend", action="store_true", help="API only")
    args = parser.parse_args()
    try:
        return demo(rows=args.rows, skip_seed=args.skip_seed, frontend=not args.no_frontend)
    except DemoRefusedError as exc:
        print(f"\n  {exc}\n", file=sys.stderr, flush=True)
        return 1
    except KeyboardInterrupt:
        # Ctrl-C is how this command is meant to end. A traceback would suggest otherwise.
        print("\n  stopped.\n", flush=True)
        return 0


if __name__ == "__main__":
    sys.exit(main())
