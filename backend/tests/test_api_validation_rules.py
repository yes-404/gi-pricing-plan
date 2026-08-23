"""The built-in rule catalogue, seeded and served.

`01` §4.4 names 38 rules and calls their ids stable; until FR-DATA-53 the platform held
none of them. These tests are the outside view of that: the rules are rows in a workspace,
they are approved without an in-workspace approver or a fabricated dry run, and there is a
route that lists them.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import Settings
from app.db.models import ValidationRuleRow
from app.db.session import Database
from model_schema import BUILTIN_RULES, new_uuid7


@pytest_asyncio.fixture
async def analyst(workspace_id, principal, grant) -> dict[str, str]:
    """`analyst` holds `dataset:read`, and granting it is what seeds the workspace.

    The `grant` fixture is the only workspace-creation path this repository has — there is
    no workspace service, a workspace is a bare `UUID` column — so seeding hangs off it for
    the same reason the built-in roles do.
    """
    await grant("analyst")
    return _headers(principal.id, workspace_id)


@pytest.fixture
def unprivileged(workspace_id, principal) -> dict[str, str]:
    """A caller in the workspace holding no role at all.

    Development identity grants no permissions (`app/api/authz.py`), so this is the refusal
    of the route's own permission check rather than the absence of a workspace.
    """
    return _headers(principal.id, workspace_id)


def _on_the_database(work: Callable[[Database], Any]) -> Any:
    """Run one async unit of work on a loop of our own.

    `TestClient` is blocking, so an async fixture cannot be requested from the synchronous
    tests below — `test_api_models._seed` reaches for the same construction and records
    why. `dispose()` is mandatory: a leaked pool outlives the loop it was created on.
    """
    from backend.tests.conftest_db import test_database_url

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            return loop.run_until_complete(work(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()


def _rule_rows(workspace_id: UUID) -> list[ValidationRuleRow]:
    async def _read(database: Database) -> list[ValidationRuleRow]:
        async with database.unit_of_work() as session:
            rows = list(
                (
                    await session.execute(
                        select(ValidationRuleRow).where(
                            ValidationRuleRow.workspace_id == workspace_id
                        )
                    )
                ).scalars()
            )
            for row in rows:
                session.expunge(row)
            return rows

    return _on_the_database(_read)


def _seed_again(workspace_id: UUID, authored_by: UUID) -> int:
    async def _seed(database: Database) -> int:
        from app.platform.validation_rules import seed_builtin_rules

        async with database.unit_of_work() as session:
            created = await seed_builtin_rules(
                session, workspace_id, authored_by=authored_by
            )
            return len(created)

    return _on_the_database(_seed)


def _all_rules(client: TestClient, headers: dict[str, str], **params: Any) -> list[dict]:
    items: list[dict] = []
    cursor: str | None = None
    for _ in range(20):
        query: dict[str, Any] = {"limit": 200, **params}
        if cursor is not None:
            query["cursor"] = cursor
        response = client.get("/api/v1/validation-rules", params=query, headers=headers)
        assert response.status_code == 200, response.text
        body = response.json()
        items.extend(body["items"])
        cursor = body["next_cursor"]
        if cursor is None:
            break
    else:  # pragma: no cover - only reached if the cursor never terminates
        raise AssertionError("the cursor did not terminate")
    return items


@pytest.mark.req("FR-DATA-53")
def test_seeding_puts_every_catalogue_rule_in_the_workspace(
    api_client: TestClient, analyst: dict[str, str]
) -> None:
    ids = {item["catalogue_id"] for item in _all_rules(api_client, analyst)}
    assert set(BUILTIN_RULES) <= ids, sorted(set(BUILTIN_RULES) - ids)


@pytest.mark.req("FR-DATA-53")
def test_seeding_twice_creates_no_duplicates(
    api_client: TestClient, analyst: dict[str, str], workspace_id: UUID, principal
) -> None:
    """Idempotent like `seed_builtin_roles`, and for the same reason: it runs on a path
    that may be retried, and `uq_validation_rule_version` turns a second run into an
    IntegrityError that surfaces far from its cause."""
    created = _seed_again(workspace_id, principal.id)
    assert created == 0

    ids = [item["catalogue_id"] for item in _all_rules(api_client, analyst)]
    assert len(ids) == len(set(ids))
    assert sorted(i for i in ids if i is not None) == sorted(BUILTIN_RULES)


@pytest.mark.req("FR-DATA-53")
def test_a_seeded_rule_is_approved_without_a_fabricated_dry_run(
    api_client: TestClient, analyst: dict[str, str], workspace_id: UUID
) -> None:
    """The constraint's new arm, asserted from the outside.

    Before this slice the only way to seed an approved rule was to invent a
    `dry_run_report_id` pointing at no report — which is what `examples/fremtpl2/seed.py`
    did, and what this slice removes. An unapproved rule cannot go in a rule set, so a
    built-in rule that is not `approved` is a built-in rule nobody can use.
    """
    rows = [row for row in _rule_rows(workspace_id) if row.builtin]
    assert len(rows) == len(BUILTIN_RULES)
    for row in rows:
        assert row.status == "approved", row.slug
        assert row.dry_run_report_id is None, row.slug
        assert row.approved_by is None, row.slug
        assert row.catalogue_id in BUILTIN_RULES, row.slug


@pytest.mark.req("FR-DATA-53")
def test_the_collection_is_paginated_and_filterable_by_builtin(
    api_client: TestClient, analyst: dict[str, str]
) -> None:
    page = api_client.get(
        "/api/v1/validation-rules", params={"builtin": True, "limit": 10}, headers=analyst
    )
    assert page.status_code == 200, page.text
    body = page.json()
    assert len(body["items"]) == 10
    assert all(item["catalogue_id"] is not None for item in body["items"])
    assert body["next_cursor"]

    second = api_client.get(
        "/api/v1/validation-rules",
        params={"builtin": True, "limit": 10, "cursor": body["next_cursor"]},
        headers=analyst,
    )
    assert second.status_code == 200, second.text
    first_ids = {item["id"] for item in body["items"]}
    assert not (first_ids & {item["id"] for item in second.json()["items"]})


@pytest.mark.req("FR-DATA-53")
def test_reading_rules_without_the_permission_is_refused(
    api_client: TestClient, unprivileged: dict[str, str]
) -> None:
    """**Negative.** A caller with no role, so the refusal is the route's own check and not
    the fixture's absence of a workspace."""
    response = api_client.get("/api/v1/validation-rules", headers=unprivileged)
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-DATA-53")
def test_rules_seeded_in_another_workspace_are_not_visible(
    api_client: TestClient, analyst: dict[str, str], workspace_id: UUID
) -> None:
    """**Negative**, and the highest-value test here. Isolation is a folded `workspace_id`
    predicate, so a dropped `.where` clause leaks every workspace's rules and no other test
    would see it.

    Shaped after `test_api_models.test_the_model_list_is_scoped_to_the_callers_workspace`,
    which seeds under a stranger rather than merely asking as one.
    """
    stranger = new_uuid7()
    _seed_again(stranger, new_uuid7())
    stranger_ids = {row.id for row in _rule_rows(stranger)}
    assert len(stranger_ids) == len(BUILTIN_RULES)

    seen = {UUID(item["id"]) for item in _all_rules(api_client, analyst)}
    assert not (seen & stranger_ids)
    assert seen == {row.id for row in _rule_rows(workspace_id)}


def _a_rule(workspace_id: UUID, **overrides: Any) -> ValidationRuleRow:
    fields: dict[str, Any] = {
        "workspace_id": workspace_id,
        "slug": f"r-{new_uuid7().hex[-8:]}",
        "version": 1,
        "layer": "structural",
        "check": "not_null",
        "severity": "fail",
        "body": {"target": {}, "params": {}, "scope": {}, "tolerance": {}},
        "status": "draft",
        "authored_by": new_uuid7(),
    }
    return ValidationRuleRow(**{**fields, **overrides})


@pytest.mark.req("FR-DATA-53")
async def test_a_builtin_row_must_name_a_catalogue_entry(database, workspace_id) -> None:
    """**Negative**, at the layer a direct `UPDATE` cannot walk past.

    `builtin IS TRUE` is an exemption from `approved_rule_dry_run_and_separate_approver`,
    so a `builtin` row that names no catalogue entry is a row claiming that exemption with
    nothing to trace it back to.

    The converse is *allowed*, and asserted here so the asymmetry is deliberate rather than
    an oversight: a workspace configuring a shipped rule against its own tables authors the
    next version of it (`01` §4.5 step 4), which is workspace data — its own approver, its
    own dry run — that still records the entry it derives from.
    """
    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            session.add(_a_rule(workspace_id, builtin=True, catalogue_id=None))

    async with database.unit_of_work() as session:
        session.add(_a_rule(workspace_id, builtin=False, catalogue_id="VR-STR-1"))


@pytest.mark.req("FR-DATA-53")
async def test_the_approval_exemption_reaches_builtin_rows_only(
    database, workspace_id
) -> None:
    """**Negative.** Widening a constraint is where an exemption quietly becomes the rule.

    A workspace's own rule still cannot reach `approved` without a separate approver and a
    dry run (`01` §4.5 steps 2 and 3); only a row that came from the shipped catalogue is
    excused, and it is excused because it was reviewed in the specification instead.
    """
    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            session.add(_a_rule(workspace_id, status="approved"))

    async with database.unit_of_work() as session:
        session.add(
            _a_rule(workspace_id, status="approved", builtin=True, catalogue_id="VR-STR-1")
        )
