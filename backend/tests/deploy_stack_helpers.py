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
import urllib.request
from typing import Any, NamedTuple
from uuid import UUID

ROOT = pathlib.Path(__file__).resolve().parents[2]
LB_PORT = os.environ.get("GIP_LB_PORT", "18000")
PROJECT = "gip-s4-runtime"


def compose(sha: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
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


def approve_draft(ws: Workspace) -> None:
    """Approve the draft `governed_workspace(approved=False)` left, the SAME Rating Version.

    PL-1766 D5.11 (the maintainer's entry "2026-10-19 03:23:43 BST", fix A): the evidence step
    `create_approved_rating_version` runs is `author_demo_rating_evidence` (it compiles the
    draft through the `rating.compile` Job, then runs the regression), then
    `submit_and_approve_demo` (submit through the gate, two approvers decide). Both are the
    example's own functions, called on the existing version rather than a second one.
    """
    from backend.tests.test_demo_rating_evidence import _BASE_MINOR, _bandings, demo_model
    from backend.tests.test_wf699_journey import _seed_module
    from sqlalchemy import select

    from app.db.models import ModelRow
    from app.db.session import Database
    from app.platform.blobs import BlobStore

    settings = compose_settings()
    workspace_id, rating_id = UUID(ws.workspace_id), UUID(ws.rating_version_id)

    async def approve() -> None:
        database, blobs = Database(settings), BlobStore(settings)
        try:
            await blobs.ensure_bucket()
            people = await _seed_module().grant_demo_principals(database, workspace_id)
            async with database.session() as session:
                model_id = (
                    await session.execute(
                        select(ModelRow.id).where(ModelRow.workspace_id == workspace_id)
                    )
                ).scalar_one()
            _, fit = await demo_model.load_approved_glm(database, workspace_id, model_id)
            await demo_model.author_demo_rating_evidence(
                database, blobs, workspace_id, people["analyst"], rating_id,
                demo_model.demo_golden_cases(fit, _bandings(), _BASE_MINOR),
            )  # fmt: skip
            await demo_model.submit_and_approve_demo(
                database, blobs, workspace_id, people["actuary"], people["approver"],
                people["second_approver"], rating_id,
            )  # fmt: skip
        finally:
            await database.dispose()

    asyncio.run(approve())


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
