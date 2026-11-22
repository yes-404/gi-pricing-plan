"""`01` FR-57's dated clause (2026-11-22): a rule set's reference version is checked.

At write (`PUT /datasets/{slug}/rule-set`): the reference Dataset Version must be in the caller's
workspace and the caller must hold `dataset:read` on the Dataset it belongs to; any other id is
one `404` with the same code, title and detail. At use (the validation worker): a reference that
fails the same check is treated as absent, with one warning that carries identifiers only.
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
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.models import (
    DatasetRow,
    RoleAssignmentRow,
    RoleRow,
    ValidationRuleSetRow,
)
from app.db.session import Database
from app.platform import datasets as dataset_service
from app.platform import profiles
from app.worker import data_handlers
from model_schema import ActorKind, Principal, Profile, ScopeType, new_uuid7

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


@pytest.mark.req("FR-57")
@pytest.mark.asyncio
async def test_the_worker_treats_a_failing_reference_as_absent_with_one_warning(
    database: Database, world: World, caplog: pytest.LogCaptureFixture, workspace_id: UUID
) -> None:
    actor = world.scoped_actor
    with caplog.at_level(logging.WARNING, logger="app.worker.data"):
        async with database.session() as session:
            failing = await data_handlers._reference_profile(
                session, workspace_id=workspace_id, actor=actor, reference_id=world.version["y"]
            )
    assert failing is None
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    text = warnings[0].getMessage()
    assert str(world.version["y"]) in text
    assert "4321" not in text  # the profile's row count: no value is logged
    assert "row_count" not in text

    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="app.worker.data"):
        async with database.session() as session:
            readable = await data_handlers._reference_profile(
                session, workspace_id=workspace_id, actor=actor, reference_id=world.version["x"]
            )
        assert readable is not None
        assert readable.row_count == 4321
    assert [r for r in caplog.records if r.levelno == logging.WARNING] == []


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
    assert _put(client, world, "x", "workspace", world.version["x"]).status_code == 200  # own
    assert _put(client, world, "y", "workspace", world.version["x"]).status_code == 200  # foreign
    assert _put(client, world, "y", "workspace", None).status_code == 200  # none
    foreign_rows = [
        r
        for r in await _rule_set_rows(database, world.dataset_id["y"])
        if r.reference_dataset_version_id is not None
    ]
    assert len(foreign_rows) == 1

    before = await _snapshot(database, workspace_id)
    out, err = io.StringIO(), io.StringIO()
    rc = await _load_script().list_references(database, workspace_id, out=out, err=err)
    after = await _snapshot(database, workspace_id)

    assert rc == 0, err.getvalue()
    assert before == after
    listed = out.getvalue().splitlines()
    assert str(foreign_rows[0].id) in listed[0]
    assert str(world.version["x"]) in listed[0]
    assert listed[-1] == "cross-dataset references: 1"
    assert len(listed) == 2
