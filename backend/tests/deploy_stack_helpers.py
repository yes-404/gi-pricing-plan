"""Shared helpers for the compose-stack runtime tests (PL-1766 D5.14; DP-S5-Q8 (a)).

Moved out of `test_deploy_stack_runtime.py` (Slice 4's private helpers at `:118-246` there:
`_governed_workspace`, `_Workspace`, `_scoring_request`, with the stack plumbing they stand on)
so that Slice 5's runtime tests, in a new module, import them by public name rather than
reaching into another test file's privates. Nothing here runs at import: a function that touches
the stack is only called from a test that `GIP_DEPLOY_TESTS=1` enabled.
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import subprocess
import tempfile
import urllib.request
from collections.abc import Iterator
from typing import Any, NamedTuple
from uuid import UUID

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LB_PORT = os.environ.get("GIP_LB_PORT", "18000")
PROJECT = "gip-s4-runtime"


SHARED_POSTGRES_PORT = 5432


def own_postgres_owner_url(port: int) -> str:
    """The owner URL of THIS project's postgres, from its mapped host port.

    Refuses the shared stack's published port: the caller runs DDL against the URL (F2).
    """
    if port == SHARED_POSTGRES_PORT:
        raise ValueError(f"port {port} is the shared stack's postgres, not this project's own")
    return f"postgresql+asyncpg://gipricing:gipricing@127.0.0.1:{port}/gipricing"


#: Projects whose own postgres has been migrated and had the application login role provisioned.
_provisioned: set[str] = set()


def _provision_once(sha: str) -> None:
    """On a project's first `up`: its OWN postgres, `migrate`, then `provision-app-role.py`.

    The `api` and the beat relay connect as `gip_app_login`, which exists on a fresh volume with
    no password until `scripts/provision-app-role.py` runs (F2): without it `api` exits 3
    ("password authentication failed for user gip_app_login", seen at origin/main 1e17ec63).
    The owner URL is built from the project's mapped port and refused if it is the shared 5432,
    BEFORE any DDL. The same URL becomes `GIP_TEST_DATABASE_URL` for the seed's owner
    connection, reset by `down`.
    """
    _provisioned.add(PROJECT)
    compose(sha, "up", "-d", "--wait", "postgres")
    url = own_postgres_owner_url(int(mapped("postgres", 5432)))
    compose(sha, "run", "--rm", "migrate")
    subprocess.run(
        ["uv", "run", "--directory", str(ROOT), "python", "scripts/provision-app-role.py",
         "--allow-default-password"],
        cwd=ROOT, env={**os.environ, "GIP_MIGRATION_DATABASE_URL": url},
        check=True, capture_output=True,
    )
    os.environ["GIP_TEST_DATABASE_URL"] = url


def compose(sha: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    if args[:1] == ("up",) and PROJECT not in _provisioned:
        _provision_once(sha)
    if args[:1] == ("down",):
        _provisioned.discard(PROJECT)
        os.environ.pop("GIP_TEST_DATABASE_URL", None)
    env = {**os.environ, "GIP_BUILD": sha, "GIP_LB_PORT": LB_PORT}
    return subprocess.run(
        [
            "docker",
            "compose",
            "-p",
            PROJECT,
            "-f",
            str(ROOT / "deploy" / "docker-compose.yml"),
            "-f",
            str(ROOT / "deploy" / "docker-compose.isolated.yml"),
            "--profile",
            "app",
            *args,
        ],
        env=env,
        check=check,
        capture_output=True,
        text=True,
    )


def mapped(service: str, port: int) -> str:
    out = compose(os.environ["GIP_N_SHA"], "port", service, str(port)).stdout.strip()
    return out.rsplit(":", 1)[-1]


def compose_settings() -> Any:
    """Backend `Settings` pointed at the compose stack's published Postgres and MinIO ports."""
    from pydantic import SecretStr

    from app.config import Environment, Settings

    return Settings(
        environment=Environment.LOCAL,
        version="e43",
        database_url=SecretStr(
            "postgresql+asyncpg://gipricing:gipricing@127.0.0.1:"
            f"{mapped('postgres', 5432)}/gipricing"
        ),
        blob_bucket="gip-blobs",
        blob_endpoint_url=f"http://127.0.0.1:{mapped('minio', 9000)}",
    )


#: What the scoring key may do. `score:execute` and `score:batch` are granted by no builtin role
#: (FR-347), so the scoring credential is a Service Account, created through
#: `POST /api/v1/service-accounts` (FR-389: `ALLOWED_PERMISSIONS` is these two and nothing else).
#: Every other permission a test needs belongs to a USER principal, never to the key (below).
SCORING_PERMISSIONS = ["score:execute"]
BATCH_PERMISSIONS = ["score:execute", "score:batch"]


class Workspace(NamedTuple):
    """A workspace seeded through the governed path, and a key for it."""

    workspace_id: str
    headers: dict[str, str]  # the scoring Service Account's key (score:execute [+ score:batch])
    users: dict[str, dict[str, str]]  # demo user principals' development headers, by name
    rating_version_id: str
    rating_version_ref: str
    quote: dict[str, Any]  # a valid `POST /api/v1/score` body for the Rating Version


def governed_workspace(*, approved: bool, scoring: list[str] = SCORING_PERMISSIONS) -> Workspace:
    """Seed a Rating Version the way the platform would have accepted it, then a key.

    SL-1258, DP-S4-SEED (the maintainer's (by delegation) entry "2026-10-16 10:08:52 BST", (a)):
    no runtime test writes a Rating Version row. The principals are the demo seed's own
    (`grant_demo_principals`), the Model an approved GLM as WF-699's `_world` builds it, the
    Rate Tables and the algorithm come from `examples/fremtpl2/model.py`'s services, and
    `approved=True` runs `create_approved_rating_version` (create, executed regression
    evidence, submit, two approvers decide). `approved=False` stops after
    `create_rating_version` and leaves the `draft` the service created: `rating.compile` is
    refused with 409 `RATING_VERSION_IMMUTABLE` for any other status (`api/models.py`
    `compile_rating_version`, FR-239), so the compile test cannot take the approved version.
    No direct row is written for the credential (the maintainer's (by delegation) entry
    "2026-10-16 10:31:43 BST", (1a) and (1b)): the scoring key is created through
    `POST /api/v1/service-accounts` by the `admin` demo principal (`admin:manage_service_accounts`),
    with only the scoring permissions FR-389 allows. A test that needs any other permission calls
    with a demo USER principal (`users`, development identity), which really holds it through its
    built-in role.
    """
    from backend.tests.test_demo_rating_evidence import (
        _BASE_MINOR,
        _QUOTES,
        _approved_model,
        _bandings,
        _raw_inputs,
        demo_model,
    )
    from backend.tests.test_wf699_journey import _seed_module

    from app.api.deps import DEV_PRINCIPAL_HEADER
    from app.db.session import Database
    from app.platform import rating_versions as rating_service
    from app.platform.blobs import BlobStore
    from model_schema import Pins, new_uuid7

    settings = compose_settings()

    async def seed() -> tuple[UUID, dict[str, dict[str, str]], UUID, str, str]:
        database, blobs = Database(settings), BlobStore(settings)
        try:
            await blobs.ensure_bucket()
            workspace_id = new_uuid7()
            people = await _seed_module().grant_demo_principals(database, workspace_id)
            analyst, actuary = people["analyst"], people["actuary"]
            approver, second = people["approver"], people["second_approver"]
            model_id = await _approved_model(database, workspace_id)
            tables = await demo_model.seed_demo_rate_tables(
                database, settings, blobs, workspace_id, analyst, model_id
            )
            dataset_version_id = new_uuid7()
            if approved:
                rating_id = await demo_model.create_approved_rating_version(
                    database,
                    blobs,
                    workspace_id,
                    analyst,
                    actuary,
                    approver,
                    second,
                    dataset_version_id,
                    model_id,
                    tables,
                    _bandings(),
                    _BASE_MINOR,
                )
            else:
                model_ref, fit = await demo_model.load_approved_glm(
                    database, workspace_id, model_id
                )
                domains = {
                    factor: [r.level for r in fit.relativities[factor]]
                    for factor, _ in demo_model.CATEGORICAL_FACTORS
                }
                algorithm_ref = await demo_model.save_demo_algorithm(
                    database, workspace_id, analyst, tables, _bandings(), domains, _BASE_MINOR
                )
                async with database.unit_of_work() as session:
                    created = await rating_service.create_rating_version(
                        session,
                        workspace_id=workspace_id,
                        actor=analyst,
                        slug=demo_model.DEMO_RATING_SLUG,
                        dataset_version_id=dataset_version_id,
                        model_ref=model_ref,
                        algorithm_ref=algorithm_ref,
                        pins=Pins(rate_tables=list(tables.values()), models=[model_ref]),
                    )
                    rating_id = created.id
            async with database.session() as session:
                row = await rating_service.load_rating_version(
                    session, workspace_id=workspace_id, rating_version_id=rating_id
                )
                ref = f"rating_version:{row.slug}@{row.version}"
                status = row.status
            assert status == ("approved" if approved else "draft"), status

            users = {
                name: {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}
                for name, principal in people.items()
            }
            return workspace_id, users, rating_id, ref, status
        finally:
            await database.dispose()

    workspace_id, users, rating_id, ref, status = asyncio.run(seed())
    scorer = create_scorer(users["admin"], scoring)
    quote = {
        "quote_id": "E43-Q1",
        "purpose": "new_business",
        "quoted_at": "2026-09-28T09:00:00Z",
        "effective_date": "2026-10-01",
        "inputs": _raw_inputs(_QUOTES["base-levels"]),
        "options": {"rating_version_ref": ref},
    }
    print(f"  seeded workspace {workspace_id}: {ref} is {status} (governed path)")
    return Workspace(str(workspace_id), scorer, users, str(rating_id), ref, quote)


def create_scorer(admin: dict[str, str], permissions: list[str]) -> dict[str, str]:
    """The scoring key, through the product's own route: `POST /api/v1/service-accounts`, called
    by a principal holding `admin:manage_service_accounts` (the demo `admin`). Returns the key's
    request headers."""
    created = api(
        "POST",
        "/api/v1/service-accounts",
        admin,
        {"slug": "e43-scorer", "environments": ["uat"], "permissions": permissions},
    )
    return {"X-API-Key": created["keys"][0]["key"], "Workspace-Id": admin["Workspace-Id"]}


def scoring_request() -> tuple[str, dict[str, str], dict[str, Any]]:
    ws = governed_workspace(approved=True)
    return f"http://127.0.0.1:{LB_PORT}/api/v1/score", ws.headers, ws.quote


def api(method: str, path: str, headers: dict[str, str], body: Any = None) -> Any:
    request = urllib.request.Request(
        f"http://127.0.0.1:{LB_PORT}{path}",
        data=None if body is None else json.dumps(body).encode(),
        headers={**headers, "Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read())


# Moved verbatim from `test_deploy_stack_runtime.py` (SL-1259 D5.11 fix A, to-lead 03:40:19 BST):
# the switch test needs the same test-supplied beat. `_compose` is the name the moved text uses.
_compose = compose


def _build_from_commit(sha: str) -> None:
    """Build `gi-pricing-app:<sha>` from `git archive <sha>`, so the image is that commit's."""
    with tempfile.TemporaryDirectory() as tmp:
        archive = subprocess.run(
            ["git", "-C", str(ROOT), "archive", sha], check=True, capture_output=True
        ).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=archive, check=True)
        subprocess.run(
            ["docker", "build", "-f", "deploy/Dockerfile", "--build-arg", f"GIP_BUILD={sha}",
             "-t", f"gi-pricing-app:{sha}", "."],
            cwd=tmp, check=True,
        )


@pytest.fixture
def built_n() -> str:
    """Only image N: the delivery proof does not need N-1."""
    n = os.environ["GIP_N_SHA"]
    _build_from_commit(n)
    return n


def one_beat_problems(ps: list[dict[str, str]]) -> list[str]:
    """FR-413: exactly one beat runs. `ps` is `docker compose ps --format json` rows.

    A beat is any running container whose command runs `celery ... beat`, whatever its service:
    that catches a second `scheduler` and a one-off `run` of another service alike (two beats
    relay the outbox twice).
    """
    beats = [
        row for row in ps
        if row.get("State") == "running" and " beat" in f" {row.get('Command', '')}"
    ]
    if len(beats) != 1:
        return [f"{len(beats)} beat containers running, not exactly 1"]
    if beats[0].get("Service") != "scheduler":
        return [f"the one beat is service {beats[0].get('Service')!r}, not scheduler"]
    return []


@pytest.fixture
def beat_fixture(built_n: str) -> Iterator[None]:
    """Starts the compose `scheduler` service (SL-1689; FR-432) and proves it is the only beat.

    The outbox relay is a beat schedule entry (`app.worker.entrypoint`), so without a beat
    process no Job ever leaves the outbox. The fixture starts no beat of its own: it brings up
    the stack's own `scheduler` and asserts, from `compose ps -a`, that exactly one beat
    container runs (`one_beat_problems`). It is stopped in teardown.
    """
    _compose(built_n, "up", "-d", "--wait", "scheduler")
    listing = _compose(built_n, "ps", "-a", "--no-trunc", "--format", "json").stdout
    rows = [json.loads(line) for line in listing.splitlines() if line.strip()]
    assert one_beat_problems(rows) == [], rows
    try:
        yield
    finally:
        _compose(built_n, "stop", "scheduler", check=False)
