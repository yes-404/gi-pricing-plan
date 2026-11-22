"""`01` FR-57's dated clause (2026-11-22): a rule set's reference version is checked.

At write (`PUT /datasets/{slug}/rule-set`): the reference Dataset Version must be in the caller's
workspace and the caller must hold `dataset:read` on the Dataset it belongs to; any other id is
one `404` with the same code, title and detail. At use (the validation worker): a reference that
no longer exists, or is in another workspace, is treated as absent, with one warning that
carries identifiers only; another Dataset's version in the same workspace is used.
`scripts/list-cross-dataset-references.py` lists, read-only, the stored rule sets whose reference
is another Dataset's version.
"""

from __future__ import annotations

import importlib.util
import io
import json
import logging
import pathlib
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from backend.tests.conftest_db import grant_roles_as_owner, seed_as_owner
from backend.tests.test_data_jobs import CLEAN, _ingest, _seed_dataset_and_rules
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DEV_PRINCIPAL_HEADER, Caller, job_identity
from app.db.models import (
    DatasetRow,
    RoleAssignmentRow,
    RoleRow,
    ValidationRuleSetRow,
)
from app.db.session import Database
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import profiles
from app.platform.blobs import BlobStore
from app.worker import data_handlers
from app.worker.data_handlers import register_data_handlers
from app.worker.tasks import execute_job
from model_schema import ActorKind, JobKind, JobStatus, Principal, Profile, ScopeType, new_uuid7

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "list-cross-dataset-references.py"


def _headers(principal_id: UUID, workspace_id: UUID) -> dict[str, str]:
    return {DEV_PRINCIPAL_HEADER: str(principal_id), "Workspace-Id": str(workspace_id)}


def _profile(version_id: UUID) -> Profile:
    return Profile(
        id=uuid4(),
        dataset_version_id=version_id,
        computed_at=datetime.now(UTC),
        row_count=4321,
        columns=(),
        one_ways=(),
    )


class World:
    """Datasets X and Y in the caller's workspace, Z in another; one version of each."""

    slug: dict[str, str]
    dataset_id: dict[str, UUID]
    version: dict[str, UUID]
    headers: dict[str, dict[str, str]]
    scoped_actor: Principal


@pytest_asyncio.fixture
async def world(database: Database, grant, membership, workspace_id, principal) -> World:
    w = World()
    w.slug, w.dataset_id, w.version, w.headers = {}, {}, {}, {}
    await grant("pricing_actuary")
    w.headers["workspace"] = _headers(principal.id, workspace_id)
    other_workspace = new_uuid7()
    await grant_roles_as_owner(
        other_workspace,
        principal.id,
        "pricing_actuary",
        workspace=True,
        membership=True,
        rules_author_id=principal.id,
    )
    for name, ws in (("x", workspace_id), ("y", workspace_id), ("z", other_workspace)):
        async with database.unit_of_work() as session:
            dataset = await dataset_service.create_dataset(
                session, workspace_id=ws, actor=principal, slug=f"ds-{name}-{new_uuid7().hex[-8:]}"
            )
            version = await dataset_service.new_version(
                session, workspace_id=ws, actor=principal, dataset_id=dataset.id
            )
        w.slug[name], w.dataset_id[name], w.version[name] = dataset.slug, dataset.id, version.id
        async with database.unit_of_work() as session:
            await profiles.store_profile(
                session, workspace_id=ws, actor=principal, profile=_profile(version.id)
            )

    # A caller whose only grant is on Dataset X.
    member = new_uuid7()
    w.scoped_actor = Principal(kind=ActorKind.USER, id=member, display="scoped")
    await membership(principal_id=member)

    async def seed(session: AsyncSession) -> None:
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == "pricing_actuary"
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=member,
                role_id=role.id,
                scope_type=ScopeType.DATASET.value,
                scope_id=w.dataset_id["x"],
            )
        )

    await seed_as_owner(seed)
    w.headers["scoped"] = _headers(member, workspace_id)
    return w


@pytest.fixture
def client(api_client: TestClient) -> TestClient:
    return api_client


def _put(client: TestClient, w: World, name: str, who: str, reference: UUID | None) -> Any:
    body: dict[str, Any] = {"rules": []}
    if reference is not None:
        body["reference_dataset_version_id"] = str(reference)
    return client.put(
        f"/api/v1/datasets/{w.slug[name]}/rule-set", json=body, headers=w.headers[who]
    )


def _without_trace(response: Any) -> bytes:
    body = {k: v for k, v in response.json().items() if k != "trace_id"}
    return json.dumps(body, sort_keys=True).encode()


async def _rule_set_rows(database: Database, dataset_id: UUID) -> list[ValidationRuleSetRow]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(ValidationRuleSetRow).where(
                        ValidationRuleSetRow.dataset_id == dataset_id
                    )
                )
            ).scalars()
        )


@pytest.mark.req("FR-57")
@pytest.mark.asyncio
async def test_a_reference_the_caller_cannot_read_gets_one_404_whatever_the_cause(
    client: TestClient, database: Database, world: World
) -> None:
    other_workspace = _put(client, world, "x", "scoped", world.version["z"])
    unreadable_dataset = _put(client, world, "x", "scoped", world.version["y"])
    absent = _put(client, world, "x", "scoped", uuid4())
    for refused in (other_workspace, unreadable_dataset, absent):
        assert refused.status_code == 404, refused.text
        assert refused.json()["code"] == "NOT_FOUND"
    assert _without_trace(other_workspace) == _without_trace(unreadable_dataset)
    assert _without_trace(absent) == _without_trace(unreadable_dataset)
    assert other_workspace.headers["content-type"] == unreadable_dataset.headers["content-type"]
    assert await _rule_set_rows(database, world.dataset_id["x"]) == []


@pytest.mark.req("FR-57")
def test_a_readable_reference_is_accepted(client: TestClient, world: World) -> None:
    own = _put(client, world, "x", "scoped", world.version["x"])
    assert own.status_code == 200, own.text
    assert own.json()["reference_dataset_version_id"] == str(world.version["x"])
    # A workspace-wide reader may name another Dataset's version in the same workspace.
    wide = _put(client, world, "y", "workspace", world.version["x"])
    assert wide.status_code == 200, wide.text
    # And a rule set with no reference is unaffected.
    assert _put(client, world, "x", "scoped", None).status_code == 200


async def _worker_reference(database: Database, workspace_id: UUID, reference_id: UUID) -> Any:
    async with database.session() as session:
        return await data_handlers._reference_profile(
            session, workspace_id=workspace_id, reference_id=reference_id
        )


@pytest.mark.req("FR-57")
@pytest.mark.asyncio
async def test_the_worker_treats_a_reference_that_no_longer_exists_as_absent(
    database: Database, world: World, caplog: pytest.LogCaptureFixture, workspace_id: UUID
) -> None:
    gone = uuid4()
    with caplog.at_level(logging.WARNING, logger="app.worker.data"):
        assert await _worker_reference(database, workspace_id, gone) is None
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    text = warnings[0].getMessage()
    assert str(gone) in text
    assert str(workspace_id) in text
    assert "4321" not in text  # a profile's row count: no value is logged
    assert "row_count" not in text


@pytest.mark.req("FR-57")
@pytest.mark.asyncio
async def test_the_worker_treats_a_reference_in_another_workspace_as_absent(
    database: Database, world: World, caplog: pytest.LogCaptureFixture, workspace_id: UUID
) -> None:
    with caplog.at_level(logging.WARNING, logger="app.worker.data"):
        assert await _worker_reference(database, workspace_id, world.version["z"]) is None
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    text = warnings[0].getMessage()
    assert str(world.version["z"]) in text
    assert "4321" not in text
    assert "row_count" not in text


@pytest.mark.req("FR-57")
@pytest.mark.asyncio
@pytest.mark.parametrize("actor_kind", [ActorKind.SERVICE_ACCOUNT, ActorKind.USER])
async def test_a_validation_job_uses_another_datasets_version_whoever_submitted_it(
    database: Database,
    blob_store: BlobStore,
    world: World,
    principal: Principal,
    workspace_id: UUID,
    monkeypatch: pytest.MonkeyPatch,
    actor_kind: ActorKind,
) -> None:
    """The reference was accepted at the write; a run of any actor uses it (`01` FR-57).

    The Job's parameters are built with `job_identity`, as the route builds them. The
    Service Account holds no grant on the Dataset the reference belongs to."""
    register_data_handlers()
    dataset_id = await _seed_dataset_and_rules(database, blob_store, workspace_id, principal)
    version_id = await _ingest(database, blob_store, workspace_id, principal, dataset_id, CLEAN)

    async def set_reference(session: AsyncSession) -> None:
        await session.execute(
            update(ValidationRuleSetRow)
            .where(ValidationRuleSetRow.dataset_id == dataset_id)
            .values(reference_dataset_version_id=world.version["y"])
        )

    # The application role holds no UPDATE on `validation_rule_sets`: set-up goes through the owner.
    await seed_as_owner(set_reference)

    seen: list[Profile | None] = []
    real_run_validation = data_handlers.run_validation

    def spy(*args: Any, **kwargs: Any) -> Any:
        seen.append(kwargs["reference_profile"])
        return real_run_validation(*args, **kwargs)

    monkeypatch.setattr(data_handlers, "run_validation", spy)
    submitter = (
        principal
        if actor_kind is ActorKind.USER
        else Principal(kind=actor_kind, id=new_uuid7(), display="sa-run")
    )
    async with database.unit_of_work() as session:
        job = await job_service.submit(
            session,
            JobKind.DATASET_VALIDATE,
            {
                **job_identity(Caller(principal=submitter, workspace_id=workspace_id)),
                "dataset_version_id": str(version_id),
            },
            submitter,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    assert len(seen) == 1
    assert seen[0] is not None, "the stored reference was treated as absent"
    assert seen[0].dataset_version_id == world.version["y"]
    assert seen[0].row_count == 4321


def _load_script() -> Any:
    spec = importlib.util.spec_from_file_location("gi_list_cross_refs", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def _snapshot(database: Database, workspace_id: UUID) -> list[tuple[Any, ...]]:
    async with database.session() as session:
        sets = (
            await session.execute(
                select(ValidationRuleSetRow)
                .where(ValidationRuleSetRow.workspace_id == workspace_id)
                .order_by(ValidationRuleSetRow.id)
            )
        ).scalars()
        rows: list[tuple[Any, ...]] = [
            (r.id, r.dataset_id, r.version, r.status, r.reference_dataset_version_id, r.body)
            for r in sets
        ]
        datasets = (
            await session.execute(
                select(DatasetRow)
                .where(DatasetRow.workspace_id == workspace_id)
                .order_by(DatasetRow.id)
            )
        ).scalars()
        rows += [(d.id, d.validation_rule_set_id) for d in datasets]
        return rows


@pytest.mark.req("FR-57")
@pytest.mark.asyncio
async def test_the_listing_names_exactly_the_cross_dataset_references_and_changes_nothing(
    client: TestClient, database: Database, world: World, workspace_id: UUID
) -> None:
    # Dataset X: one rule set naming its own version (not listed).
    assert _put(client, world, "x", "workspace", world.version["x"]).status_code == 200
    # Dataset Y: four versions of its rule set, each one shape.
    assert (
        _put(client, world, "y", "workspace", world.version["x"]).status_code == 200
    )  # v1: another Dataset
    assert _put(client, world, "y", "workspace", None).status_code == 200  # v2: no reference
    assert (
        _put(client, world, "y", "workspace", None).status_code == 200
    )  # v3: set to another workspace
    assert (
        _put(client, world, "y", "workspace", None).status_code == 200
    )  # v4: set to a missing version
    rows = {r.version: r for r in await _rule_set_rows(database, world.dataset_id["y"])}
    assert sorted(rows) == [1, 2, 3, 4]

    async def set_references(session: AsyncSession) -> None:
        for version, reference in ((3, world.version["z"]), (4, new_uuid7())):
            await session.execute(
                update(ValidationRuleSetRow)
                .where(ValidationRuleSetRow.id == rows[version].id)
                .values(reference_dataset_version_id=reference)
            )

    # The application role holds no UPDATE on `validation_rule_sets`: set-up goes through the owner.
    await seed_as_owner(set_references)

    before = await _snapshot(database, workspace_id)
    out, err = io.StringIO(), io.StringIO()
    rc = await _load_script().list_references(database, workspace_id, out=out, err=err)
    after = await _snapshot(database, workspace_id)

    assert rc == 0, err.getvalue()
    assert before == after
    listed = out.getvalue().splitlines()
    # Listed: another Dataset's version in the workspace (v1) and in another workspace (v3).
    # Not listed: an own-Dataset reference, no reference (v2), a reference to no version (v4).
    assert str(rows[1].id) in listed[0]
    assert str(world.version["x"]) in listed[0]
    assert str(rows[3].id) in listed[1]
    assert str(world.version["z"]) in listed[1]
    assert listed[-1] == "cross-dataset references: 2"
    assert len(listed) == 3
