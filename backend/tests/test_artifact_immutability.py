"""Artifacts cannot be rewritten, and the database is what says so (FR-DATA-42).

`01` FR-DATA-15 has said a Validation Report is immutable since the spec was written. Until
this was built, that was `frozen=True` on a Pydantic model — a rule about one process, which
an independent audit demonstrated by rewriting **190 stored reports** from `fail` to `pass`
in one statement. `01` §1.3's whole gate, undone by an `UPDATE`.

Every test here is a **prohibition**: the suite has to prove the wrong thing cannot happen,
not that the right thing can.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.db.session import Database
from app.platform import datasets, profiles, validation
from model_schema import (
    ActorKind,
    Principal,
    Profile,
    RuleOutcome,
    RuleResult,
    Severity,
    ValidationLayer,
    ValidationReport,
    new_uuid7,
)

ACTOR = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")

#: Layer 1 holds these and nothing else. Ordered as the database reports them.
APPEND_ONLY_TABLES = (
    "audit_events",
    "backtests",
    "bandings",
    "diagnostics",
    "groupings",
    "model_comparisons",
    "objective_certificates",
    "profiles",
    "transparency_artifacts",
    "validation_acknowledgements",
    "validation_reports",
)


async def _grant(database: Database, workspace_id) -> None:
    """The actor needs `dataset:write` to create the artifacts these tests then protect."""
    from sqlalchemy import select

    from app.db.models import RoleAssignmentRow, RoleRow
    from app.platform import rbac
    from model_schema import ScopeType

    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        role = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == "analyst"
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id, principal_kind="user", principal_id=ACTOR.id,
                role_id=role.id, scope_type=ScopeType.WORKSPACE.value,
            )
        )


async def _version(database: Database, workspace_id):
    await _grant(database, workspace_id)
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=ACTOR, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        version = await datasets.new_version(
            session, workspace_id=workspace_id, actor=ACTOR, dataset_id=dataset.id
        )
        return version.id


async def _report(database: Database, workspace_id, version_id):
    started = datetime.now(UTC)
    report = ValidationReport(
        id=uuid4(),
        dataset_version_id=version_id,
        rule_set_id=uuid4(),
        rule_set_version=1,
        started_at=started,
        finished_at=started + timedelta(seconds=1),
        results=(
            RuleResult(
                rule_id=uuid4(), rule_slug="exposure-plausible", rule_version=1,
                layer=ValidationLayer.ACTUARIAL_SANITY, severity=Severity.FAIL,
                outcome=RuleOutcome.FAIL, detail="55 rows outside the declared range",
            ),
        ),
    )
    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=ACTOR, report=report
        )
    return report.id


@pytest.mark.req("FR-DATA-42")
async def test_a_stored_report_cannot_be_rewritten(database: Database, workspace_id) -> None:
    """The exact statement an audit used to turn 190 failures into passes."""
    report_id = await _report(database, workspace_id, await _version(database, workspace_id))

    with pytest.raises(DBAPIError) as refused:
        async with database.unit_of_work() as session:
            await session.execute(
                text("UPDATE validation_reports SET overall = 'pass' WHERE id = :id"),
                {"id": report_id},
            )
    assert "append-only" in str(refused.value)

    # ...and it is still a failure.
    async with database.session() as session:
        overall = (
            await session.execute(
                text("SELECT overall FROM validation_reports WHERE id = :id"), {"id": report_id}
            )
        ).scalar_one()
    assert overall == "fail"


@pytest.mark.req("FR-DATA-42")
async def test_a_stored_report_cannot_be_deleted_or_truncated(
    database: Database, workspace_id
) -> None:
    """`DELETE` removes the evidence; `TRUNCATE` removes all of it.

    Both are covered because a **row** trigger does not fire on `TRUNCATE` — the same
    lesson `audit_events` learned, and the reason there are two triggers per table.
    """
    report_id = await _report(database, workspace_id, await _version(database, workspace_id))

    with pytest.raises(DBAPIError) as deleted:
        async with database.unit_of_work() as session:
            await session.execute(
                text("DELETE FROM validation_reports WHERE id = :id"), {"id": report_id}
            )
    assert "append-only" in str(deleted.value)

    with pytest.raises(DBAPIError) as truncated:
        async with database.unit_of_work() as session:
            await session.execute(text("TRUNCATE validation_reports"))
    assert "append-only" in str(truncated.value)


@pytest.mark.req("FR-DATA-42")
async def test_a_profile_cannot_be_rewritten(database: Database, workspace_id) -> None:
    """A profile is what the factor workbench reads and what drift is measured against.

    A rewritten profile makes two runs of the same comparison disagree with no artifact
    changing, which is the property FR-DATA-24 depends on.
    """
    version_id = await _version(database, workspace_id)
    profile = Profile(
        id=uuid4(), dataset_version_id=version_id, computed_at=datetime.now(UTC),
        row_count=10, columns=(), one_ways=(),
    )
    async with database.unit_of_work() as session:
        await profiles.store_profile(
            session, workspace_id=workspace_id, actor=ACTOR, profile=profile
        )

    with pytest.raises(DBAPIError) as refused:
        async with database.unit_of_work() as session:
            await session.execute(
                text("UPDATE profiles SET body = '{}'::jsonb WHERE id = :id"), {"id": profile.id}
            )
    assert "append-only" in str(refused.value)


@pytest.mark.req("FR-DATA-42")
async def test_an_acknowledgement_cannot_be_rewritten_or_removed(
    database: Database, workspace_id
) -> None:
    """An acknowledgement is a named person accepting a warning (FR-DATA-18).

    Editing its justification, or deleting it, would leave a version `validated` on the
    strength of a decision nobody made.
    """
    version_id = await _version(database, workspace_id)
    report_id = await _report(database, workspace_id, version_id)

    async with database.unit_of_work() as session:
        await session.execute(
            text(
                "INSERT INTO validation_acknowledgements (id, workspace_id, "
                "dataset_version_id, report_id, rule_id, user_id, justification, "
                "acknowledged_at) VALUES (:id, :ws, :ver, :report, :rule, :user, :why, now())"
            ),
            {"id": new_uuid7(), "ws": workspace_id, "ver": version_id, "report": report_id,
             "rule": uuid4(), "user": ACTOR.id, "why": "Reviewed with the reserving team."},
        )

    with pytest.raises(DBAPIError) as edited:
        async with database.unit_of_work() as session:
            await session.execute(
                text("UPDATE validation_acknowledgements SET justification = 'ok'")
            )
    assert "append-only" in str(edited.value)

    with pytest.raises(DBAPIError) as removed:
        async with database.unit_of_work() as session:
            await session.execute(text("DELETE FROM validation_acknowledgements"))
    assert "append-only" in str(removed.value)


@pytest.mark.req("FR-DATA-42")
async def test_a_blobs_content_cannot_change_while_its_lifecycle_can(
    database: Database, workspace_id
) -> None:
    """`blobs` is deliberately **not** append-only, and the requirement was corrected to say so.

    `ref_count` changes on every reference and release, and reference-counted GC deletes
    unreferenced rows — so the trigger guards the content columns only. The digest is the
    content's own address: changed bytes are a different row, not an edited one.
    """
    digest = (new_uuid7().hex * 2)[:64]  # the column is the bare 64-char digest
    async with database.unit_of_work() as session:
        await session.execute(
            text(
                "INSERT INTO blobs (sha256, bytes, media_type, ref_count, created_at) "
                "VALUES (:d, 10, 'application/octet-stream', 0, now())"
            ),
            {"d": digest},
        )

    # Lifecycle: permitted, because GC and referencing depend on it.
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE blobs SET ref_count = ref_count + 1 WHERE sha256 = :d"), {"d": digest}
        )

    # Content: refused.
    with pytest.raises(DBAPIError) as refused:
        async with database.unit_of_work() as session:
            await session.execute(
                text("UPDATE blobs SET bytes = 99 WHERE sha256 = :d"), {"d": digest}
            )
    assert "digest of its bytes" in str(refused.value)

    # And deletion stays possible: reference-counted GC is a requirement, not a leak.
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE blobs SET ref_count = 0 WHERE sha256 = :d"), {"d": digest}
        )
        await session.execute(text("DELETE FROM blobs WHERE sha256 = :d"), {"d": digest})


@pytest.mark.req("FR-DATA-42")
async def test_the_application_role_holds_only_select_and_insert(
    database: Database,
) -> None:
    """Layer 1, as FR-GOV-22 does it: the application cannot even attempt the write.

    Asserted as an exact set — `UPDATE` granted back by a later migration would otherwise
    pass unnoticed, since the triggers would still refuse and every test above would stay
    green while the first layer was gone.

    The list is written out rather than derived, and that is the point: the trigger test
    below *derives* its table list from these grants, so a table quietly regranted `UPDATE`
    would drop out of its set and be checked by nobody. This test is what notices.
    """
    async with database.session() as session:
        for table in APPEND_ONLY_TABLES:
            granted = {
                row[0]
                for row in (
                    await session.execute(
                        text(
                            "SELECT privilege_type FROM information_schema.table_privileges "
                            "WHERE grantee = 'gip_app' AND table_name = :t"
                        ),
                        {"t": table},
                    )
                ).all()
            }
            assert granted == {"SELECT", "INSERT"}, f"{table}: {sorted(granted)}"


# -- Every artifact table, not the three anybody had counted (FR-DATA-47) ------------------

#: One insertable row per table `e1f2a3b4c5d6` repaired. None of these tables carries a
#: foreign key, so a bare `INSERT` is enough to give the row trigger something to refuse —
#: the artifact's real production path is exercised by its own module's tests, and what is
#: under test here is the table, not the writer.
_APPEND_ONLY_ROWS: dict[str, str] = {
    "bandings": (
        "INSERT INTO bandings (id, workspace_id, dataset_id, slug, version, column_name, "
        "body) VALUES (:id, :ws, gen_random_uuid(), :slug, 1, 'vehicle_age', :body)"
    ),
    "diagnostics": (
        "INSERT INTO diagnostics (id, workspace_id, model_id, payload) "
        "VALUES (:id, :ws, gen_random_uuid(), :body)"
    ),
    "groupings": (
        "INSERT INTO groupings (id, workspace_id, dataset_id, slug, version, column_name, "
        "body) VALUES (:id, :ws, gen_random_uuid(), :slug, 1, 'area', :body)"
    ),
    "model_comparisons": (
        "INSERT INTO model_comparisons (id, workspace_id, payload) VALUES (:id, :ws, :body)"
    ),
    "objective_certificates": (
        "INSERT INTO objective_certificates (id, workspace_id, custom_objective_id, "
        "objective_version, payload) VALUES (:id, :ws, gen_random_uuid(), 1, :body)"
    ),
    "transparency_artifacts": (
        "INSERT INTO transparency_artifacts (id, workspace_id, model_id, payload) "
        "VALUES (:id, :ws, gen_random_uuid(), :body)"
    ),
}


@pytest.mark.req("FR-DATA-47")
@pytest.mark.parametrize("table", sorted(_APPEND_ONLY_ROWS))
async def test_an_artifact_cannot_be_rewritten_from_the_owner_connection(
    database: Database, workspace_id, table: str
) -> None:
    """The six tables that had the grants and not the trigger, each refusing all three.

    Every session here connects as the **owner**, which is the case layer 1 cannot reach:
    `REVOKE UPDATE` from a table's owner does nothing, because ownership carries implicit
    privileges. Before `e1f2a3b4c5d6` these six `UPDATE`s all succeeded — three of them
    against evidence something is approved against (`02` §4.8 makes diagnostics the
    condition of `fitted`; `06` §3.3 makes a comparison required evidence for a Model
    approval), and `TRUNCATE` succeeded against three of them as well.
    """
    row_id = new_uuid7()
    async with database.unit_of_work() as session:
        await session.execute(
            text(_APPEND_ONLY_ROWS[table]),
            {
                "id": row_id,
                "ws": workspace_id,
                "slug": f"s-{row_id.hex[-8:]}",
                "body": '{"stored": true}',
            },
        )

    for statement in (
        f"UPDATE {table} SET workspace_id = workspace_id WHERE id = :id",
        f"DELETE FROM {table} WHERE id = :id",
        f"TRUNCATE {table}",  # a row trigger does not fire on this, which is why two exist
    ):
        with pytest.raises(DBAPIError) as refused:
            async with database.unit_of_work() as session:
                await session.execute(text(statement), {"id": row_id})
        assert "append-only" in str(refused.value), statement

    async with database.session() as session:
        survived = (
            await session.execute(
                text(f"SELECT count(*) FROM {table} WHERE id = :id"), {"id": row_id}
            )
        ).scalar_one()
    assert survived == 1


@pytest.mark.req("FR-DATA-47")
async def test_every_table_the_grants_call_append_only_carries_both_triggers(
    database: Database,
) -> None:
    """The check that catches the *next* table, rather than the six this slice found.

    FR-DATA-47 was raised naming three tables, measured by hand. Measuring the invariant
    instead of re-reading the list found three more — `bandings`, `groupings` and
    `objective_certificates` each had the `TRUNCATE` half and not the row half, and
    `c3d4e5f6a7b8` claimed in a comment that a direct `UPDATE` was refused while it was not.
    Nothing could fail while that was untrue.

    So the table list is **derived**: a table whose grants say `SELECT, INSERT` and nothing
    else is a table the schema has declared append-only, and it must carry both triggers.
    `blobs` and `custom_objectives` are correctly outside the set — both hold `UPDATE` for a
    stated reason, and both have their own narrower trigger.
    """
    async with database.session() as session:
        rows = (
            await session.execute(
                text("""
                    SELECT g.table_name,
                           count(*) FILTER (WHERE t.tgtype & 1 = 1) AS row_triggers,
                           count(*) FILTER (WHERE t.tgtype & 1 = 0) AS statement_triggers
                    FROM (
                        SELECT table_name
                        FROM information_schema.role_table_grants
                        WHERE grantee = 'gip_app'
                        GROUP BY table_name
                        HAVING string_agg(DISTINCT privilege_type, ',' ORDER BY privilege_type)
                               = 'INSERT,SELECT'
                    ) g
                    JOIN pg_class c
                      ON c.relname = g.table_name AND c.relnamespace = 'public'::regnamespace
                    LEFT JOIN pg_trigger t ON t.tgrelid = c.oid AND NOT t.tgisinternal
                    GROUP BY g.table_name
                    ORDER BY g.table_name
                """)
            )
        ).all()

    # Guard against the query itself going quiet: an empty or shrunken result would pass
    # every assertion below while proving nothing.
    assert {row[0] for row in rows} == set(APPEND_ONLY_TABLES)

    missing = [
        (table, row_triggers, statement_triggers)
        for table, row_triggers, statement_triggers in rows
        if row_triggers < 1 or statement_triggers < 1
    ]
    assert missing == [], f"append-only tables missing a trigger: {missing}"
