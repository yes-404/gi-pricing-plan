"""Artifacts cannot be rewritten, and the database is what says so (FR-43).

`01` FR-42 has said a Validation Report is immutable since the spec was written. Until
this was built, that was `frozen=True` on a Pydantic model — a rule about one process, which
an independent audit demonstrated by rewriting **190 stored reports** from `fail` to `pass`
in one statement. `01` §1.3's whole gate, undone by an `UPDATE`.

Every test here is a **prohibition**: the suite has to prove the wrong thing cannot happen,
not that the right thing can.
"""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from backend.tests.conftest_db import seed_as_owner
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.db.models import Base, DatasetVersionRow
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
from model_schema.datasets import VALID_DATASET_TRANSITIONS, DatasetStatus

ACTOR = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")



def _declared(kind: str) -> tuple[str, ...]:
    """The tables whose ORM declaration says `kind` (DP-8): derived, never restated.

    Every mapped table declares `immutability` in `__table_args__` (`app/db/models.py`); a table
    that declares nothing fails `test_every_mapped_table_declares_its_immutability`. The set of
    tables Layer 1 locks is therefore read from where the table is written, and a new artifact
    table cannot be forgotten silently (FD-1728). It replaces the list that was written out here,
    which had thirteen names and was why eleven artifact tables were missed.
    """
    return tuple(
        sorted(t.name for t in Base.metadata.sorted_tables if t.info.get("immutability") == kind)
    )


async def _grant(database: Database, workspace_id) -> None:
    """The actor needs `dataset:write` to create the artifacts these tests then protect."""
    from sqlalchemy import select

    from app.db.models import RoleAssignmentRow, RoleRow
    from app.platform import rbac
    from model_schema import ScopeType

    async def _seed(session):
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
    await seed_as_owner(_seed)


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


@pytest.mark.req("FR-43")
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


@pytest.mark.req("FR-43")
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


@pytest.mark.req("FR-43")
async def test_a_profile_cannot_be_rewritten(database: Database, workspace_id) -> None:
    """A profile is what the factor workbench reads and what drift is measured against.

    A rewritten profile makes two runs of the same comparison disagree with no artifact
    changing, which is the property FR-54 depends on.
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


@pytest.mark.req("FR-43")
async def test_an_acknowledgement_cannot_be_rewritten_or_removed(
    database: Database, workspace_id
) -> None:
    """An acknowledgement is a named person accepting a warning (FR-47).

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


@pytest.mark.req("FR-43")
async def test_a_blobs_content_cannot_change_while_its_lifecycle_can(
    owner_database: Database, workspace_id
) -> None:
    """`blobs` is deliberately **not** append-only, and the requirement was corrected to say so.

    `ref_count` changes on every reference and release, and reference-counted GC deletes
    unreferenced rows — so the trigger guards the content columns only. The digest is the
    content's own address: changed bytes are a different row, not an edited one.
    """
    digest = (new_uuid7().hex * 2)[:64]  # the column is the bare 64-char digest
    async with owner_database.unit_of_work() as session:
        await session.execute(
            text(
                "INSERT INTO blobs (sha256, bytes, media_type, ref_count, created_at) "
                "VALUES (:d, 10, 'application/octet-stream', 0, now())"
            ),
            {"d": digest},
        )

    # Lifecycle: permitted, because GC and referencing depend on it.
    async with owner_database.unit_of_work() as session:
        await session.execute(
            text("UPDATE blobs SET ref_count = ref_count + 1 WHERE sha256 = :d"), {"d": digest}
        )

    # Content: refused.
    with pytest.raises(DBAPIError) as refused:
        async with owner_database.unit_of_work() as session:
            await session.execute(
                text("UPDATE blobs SET bytes = 99 WHERE sha256 = :d"), {"d": digest}
            )
    assert "digest of its bytes" in str(refused.value)

    # And deletion stays possible: reference-counted GC is a requirement, not a leak.
    async with owner_database.unit_of_work() as session:
        await session.execute(
            text("UPDATE blobs SET ref_count = 0 WHERE sha256 = :d"), {"d": digest}
        )
        await session.execute(text("DELETE FROM blobs WHERE sha256 = :d"), {"d": digest})


@pytest.mark.req("FR-43")
async def test_the_application_role_holds_only_select_and_insert(
    database: Database,
) -> None:
    """Layer 1, as FR-370 does it: the application cannot even attempt the write.

    Asserted as an exact set — `UPDATE` granted back by a later migration would otherwise
    pass unnoticed, since the triggers would still refuse and every test above would stay
    green while the first layer was gone.

    The set is derived from the ORM declaration (DP-8), **not from these grants**, and that is
    the point: a table quietly regranted `UPDATE` stays in the declared set and is noticed here.
    The grants-derived trigger test this replaces dropped such a table out of its own set.
    """
    async with database.session() as session:
        for table in _declared("append_only"):
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


# -- Every artifact table, not the three anybody had counted (FR-44) ------------------


class _RollbackError(Exception):
    """Raised on purpose to end a probe's transaction by rolling it back."""


async def _probe(
    database: Database,
    probe: list[tuple[str, dict]],
    setup: list[tuple[str, dict]] | None = None,
) -> DBAPIError | None:
    """Run `setup`, then `probe`, in **one transaction that always rolls back**.

    Returns the database's refusal of a `probe` statement, or `None` when every statement was
    applied. A refusal of a `setup` statement is a defect in the arrangement and fails the test
    on the spot, so a red can never be a red for the wrong reason. Rolling back matters on the
    base tree, where a `TRUNCATE` that nothing refuses would otherwise empty a real table.
    """
    stage = failed_in = "setup"
    outcome: DBAPIError | None = None
    try:
        async with database.unit_of_work() as session:
            for sql, params in setup or []:
                await session.execute(text(sql), params)
            stage = "probe"
            for sql, params in probe:
                await session.execute(text(sql), params)
            raise _RollbackError
    except _RollbackError:
        pass
    except DBAPIError as refused:
        outcome = refused
        failed_in = stage
    if outcome is not None:
        assert failed_in == "probe", f"the arrangement itself was refused: {outcome}"
    return outcome


def _sqlstate(refused: DBAPIError) -> str | None:
    return getattr(refused.orig, "sqlstate", None) or getattr(
        getattr(refused.orig, "__cause__", None), "sqlstate", None
    )


def _assert_refused(refused: DBAPIError | None, what: str) -> str:
    """The trigger refused it: `insufficient_privilege`, not a constraint or a typo."""
    assert refused is not None, f"DID NOT RAISE: {what}"
    assert _sqlstate(refused) == "42501", f"{what}: refused for another reason: {refused}"
    return str(refused)


async def _referencing_closure(database: Database, table: str) -> str:
    """`table` plus every table that references it by foreign key, transitively, for a `TRUNCATE`.

    PostgreSQL refuses a `TRUNCATE` of a referenced table on the foreign key before any trigger
    runs. Naming the referencing tables gets the statement to the trigger. Read from
    `pg_constraint`, never written out per table, so a foreign key added later is followed.
    """
    async with database.session() as session:
        names = (
            await session.execute(
                text("""
                    WITH RECURSIVE r(oid) AS (
                        SELECT c.oid FROM pg_class c
                        WHERE c.relname = :t AND c.relnamespace = 'public'::regnamespace
                        UNION
                        SELECT con.conrelid FROM pg_constraint con
                        JOIN r ON con.confrelid = r.oid WHERE con.contype = 'f'
                    )
                    SELECT c.relname FROM r JOIN pg_class c ON c.oid = r.oid ORDER BY 1
                """),
                {"t": table},
            )
        ).scalars().all()
    assert table in names, table
    return ", ".join(names)


#: One insertable row per table `e1f2a3b4c5d6` repaired, then the eleven of FD-1704/FD-1728.
#: A value is one statement, or a tuple of statements that run in order (a table whose row needs
#: its parent first). Bare `INSERT`s: the artifact's real production path is exercised by its own
#: module's tests, and what is under test here is the table, not the writer.
_APPEND_ONLY_ROWS: dict[str, str | tuple[str, ...]] = {
    #: **Added 2026-08-23 (W32-6).** `backtests` was in the append-only set above — so the
    #: grants and the both-triggers checks covered it — and absent from this list, which is
    #: the only one that makes a trigger *fire*. Every other locked table had its refusal
    #: observed and this one did not.
    "backtests": (
        "INSERT INTO backtests (id, workspace_id, model_id, dataset_version_id, payload) "
        "VALUES (:id, :ws, gen_random_uuid(), gen_random_uuid(), :body)"
    ),
    "bandings": (
        "INSERT INTO bandings (id, workspace_id, dataset_id, slug, version, column_name, "
        "body) VALUES (:id, :ws, gen_random_uuid(), :slug, 1, 'vehicle_age', :body)"
    ),
    #: **Added 2026-10-03 (WK-674 Slice 2, PL-1392 Task 3).** A Deployment is a record, never
    #: updated or deleted (`00` FR-4). The one foreign key is satisfied by the seeded `dev`.
    "deployments": (
        "INSERT INTO deployments (id, workspace_id, environment_id, rating_version_ref, "
        "bundle_hash, deployed_by, reason) VALUES (:id, :ws, "
        "(SELECT id FROM environments WHERE slug = 'dev'), 'rating_version:motor@1', "
        "'sha256:' || repeat('a', 64), gen_random_uuid(), :body)"
    ),
    #: **Added 2026-10-21 (WK-674 Slice 6, RL-1834).** The date-routing rule, the shadow
    #: configuration and the shadow results are appended, never rewritten. The one foreign key
    #: of each is satisfied by the seeded `dev`.
    "routing_rules": (
        "INSERT INTO routing_rules (id, workspace_id, environment_id, ranges, written_by) "
        "VALUES (:id, :ws, (SELECT id FROM environments WHERE slug = 'dev'), :body, "
        "gen_random_uuid())"
    ),
    "shadow_configs": (
        "INSERT INTO shadow_configs (id, workspace_id, environment_id, "
        "candidate_rating_version_ref, candidate_bundle_hash, fraction, written_by) "
        "VALUES (:id, :ws, (SELECT id FROM environments WHERE slug = 'dev'), "
        "'rating_version:motor@1', 'sha256:' || repeat('a', 64), 0.5, gen_random_uuid())"
    ),
    "shadow_results": (
        "INSERT INTO shadow_results (id, workspace_id, environment_id, live_result, "
        "candidate_result) VALUES (:id, :ws, (SELECT id FROM environments WHERE slug = 'dev'), "
        ":body, :body)"
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
    #: **Added 2026-10-18 (WK-1178, SL-1770, FD-1704, FD-1728).** The nine below are
    #: `append_only` after SL-1770; `rate_tables` and `reference_table_versions` are `guarded`
    #: and have their own rows in `_GUARDED_ROWS`. A Model pins its Factors by row id, so an
    #: edited `factors` row re-prices every pinned fitted Model with the pin unchanged.
    "factors": (
        "INSERT INTO factors (id, workspace_id, dataset_id, slug, version, body) "
        "VALUES (:id, :ws, gen_random_uuid(), :slug, 1, :body)"
    ),
    "rate_table_cells": (
        "INSERT INTO rate_table_cells (id, version_id, key, value) "
        "VALUES (:id, gen_random_uuid(), CAST('[\"a\"]' AS jsonb), CAST('\"1.0\"' AS jsonb))"
    ),
    "rate_table_versions": (
        "INSERT INTO rate_table_versions (id, workspace_id, rate_table_id, version_number, "
        "storage, definition, change_note, created_by) "
        "VALUES (:id, :ws, gen_random_uuid(), 1, 'rows', :body, 'n', gen_random_uuid())"
    ),
    "rating_algorithms": (
        "INSERT INTO rating_algorithms (id, workspace_id, slug, version, content, created_by) "
        "VALUES (:id, :ws, :slug, 1, :body, gen_random_uuid())"
    ),
    "reference_rows": (
        "INSERT INTO reference_rows (id, reference_table_version_id, key, payload, "
        "effective_from) VALUES (:id, gen_random_uuid(), 'k', :body, DATE '2026-01-01')"
    ),
    "reference_tables": (
        "INSERT INTO reference_tables (id, workspace_id, slug, key_columns, payload_columns) "
        "VALUES (:id, :ws, :slug, CAST('[]' AS jsonb), CAST('[]' AS jsonb))"
    ),
    #: `regression_suite_versions.suite_id` is the one foreign key among the eleven (E4).
    "regression_suites": (
        "INSERT INTO regression_suites (id, workspace_id, slug, algorithm_slug, created_by) "
        "VALUES (:id, :ws, :slug, 'alg-' || CAST(:slug AS varchar), gen_random_uuid())"
    ),
    "regression_suite_versions": (
        "INSERT INTO regression_suites (id, workspace_id, slug, algorithm_slug, created_by) "
        "VALUES (:id, :ws, :slug, 'alg-' || CAST(:slug AS varchar), gen_random_uuid())",
        "INSERT INTO regression_suite_versions (id, suite_id, version, content, content_hash, "
        "change_note, created_by) VALUES (:id, :id, 1, :body, 'sha256:' || repeat('a', 64), "
        "'n', gen_random_uuid())",
    ),
    "sub_graph_versions": (
        "INSERT INTO sub_graph_versions (id, workspace_id, slug, version, content, change_note, "
        "created_by) VALUES (:id, :ws, :slug, 1, :body, 'n', gen_random_uuid())"
    ),
}


def _row_params(workspace_id, row_id) -> dict:
    return {
        "id": row_id,
        "ws": workspace_id,
        "slug": f"s-{row_id.hex[-8:]}",
        "body": '{"stored": true}',
    }


def _statements(entry: str | tuple[str, ...]) -> list[str]:
    return [entry] if isinstance(entry, str) else list(entry)


#: The statements a table refuses once it is `append_only`.
_APPEND_ONLY_STATEMENTS = ("UPDATE", "DELETE", "TRUNCATE")

_CASES = [
    pytest.param(table, statement, id=f"{table}-{statement}")
    for table in sorted(_APPEND_ONLY_ROWS)
    for statement in _APPEND_ONLY_STATEMENTS
]


@pytest.mark.req("FR-44")
@pytest.mark.parametrize(("table", "statement"), _CASES)
async def test_an_artifact_cannot_be_rewritten_from_the_owner_connection(
    owner_database: Database, workspace_id, table: str, statement: str
) -> None:
    """Each artifact table refuses each of `UPDATE`, `DELETE` and `TRUNCATE`, one case apiece.

    Every session here connects as the **owner**, which is the case layer 1 cannot reach:
    `REVOKE UPDATE` from a table's owner does nothing, because ownership carries implicit
    privileges. One case per (table, statement), not a loop inside a test (plan review R10,
    PL-1769): a loop ends at its first `DID NOT RAISE` and hides the rest, and the red of this
    slice is exactly 27 of them at once.
    """
    row_id = new_uuid7()
    params = _row_params(workspace_id, row_id)
    async with owner_database.unit_of_work() as session:
        for insert in _statements(_APPEND_ONLY_ROWS[table]):
            await session.execute(text(insert), params)

    sql = {
        "UPDATE": f"UPDATE {table} SET id = id WHERE id = :id",
        "DELETE": f"DELETE FROM {table} WHERE id = :id",
        # a row trigger does not fire on this, which is why two exist
        "TRUNCATE": f"TRUNCATE {await _referencing_closure(owner_database, table)}",
    }[statement]
    refused = await _probe(owner_database, [(sql, {"id": row_id})])
    assert "append-only" in _assert_refused(refused, f"{table}: {sql}")

    async with owner_database.session() as session:
        survived = (
            await session.execute(
                text(f"SELECT count(*) FROM {table} WHERE id = :id"), {"id": row_id}
            )
        ).scalar_one()
    assert survived == 1


#: **Added 2026-10-18 (SL-1770, DP-9, DP-11).** The two `guarded` tables of the eleven. Each
#: entry is the arrangement; `case` below says what is then attempted.
_GUARDED_ROWS: dict[str, str] = {
    "rate_tables": (
        "INSERT INTO rate_tables (id, workspace_id, slug, current_version, created_by) "
        "VALUES (:id, :ws, :slug, 3, gen_random_uuid())"
    ),
    "reference_table_versions": (
        "INSERT INTO reference_table_versions (id, workspace_id, reference_table_id, "
        "version, status) VALUES (:id, :ws, gen_random_uuid(), 1, :status)"
    ),
}

#: (table, case id, row status, statement, refused?). `rate_tables` moves forward on
#: `current_version` and nothing else (DP-9); `reference_table_versions` goes `draft` to
#: `published` and nothing else (DP-11, FR-70). The allowed cases are controls: green on the base
#: because nothing guards, and they must stay green after SL-1770.
_GUARDED_CASES = [
    (
        "rate_tables", "edit-slug", None,
        "UPDATE rate_tables SET slug = slug || 'x' WHERE id = :id", True,
    ),
    ("rate_tables", "delete", None, "DELETE FROM rate_tables WHERE id = :id", True),
    ("rate_tables", "truncate", None, "TRUNCATE rate_tables", True),
    (
        "rate_tables", "version-forward", None,
        "UPDATE rate_tables SET current_version = current_version + 1 WHERE id = :id", False,
    ),
    (
        "rate_tables", "version-backward", None,
        "UPDATE rate_tables SET current_version = current_version - 1 WHERE id = :id", True,
    ),
    (
        "reference_table_versions", "edit-note", "draft",
        "UPDATE reference_table_versions SET source_note = 'x' WHERE id = :id", True,
    ),
    (
        "reference_table_versions", "delete", "draft",
        "DELETE FROM reference_table_versions WHERE id = :id", True,
    ),
    ("reference_table_versions", "truncate", "draft", "TRUNCATE reference_table_versions", True),
    (
        "reference_table_versions", "publish", "draft",
        "UPDATE reference_table_versions SET status = 'published' WHERE id = :id", False,
    ),
    (
        "reference_table_versions", "unpublish", "published",
        "UPDATE reference_table_versions SET status = 'draft' WHERE id = :id", True,
    ),
]


@pytest.mark.req("FR-44")
@pytest.mark.parametrize(
    ("table", "status", "statement", "refused"),
    [pytest.param(t, s, sql, r, id=f"{t}-{c}") for t, c, s, sql, r in _GUARDED_CASES],
)
async def test_a_guarded_artifact_moves_only_forward_from_the_owner_connection(
    database: Database, workspace_id, table: str, status: str | None, statement: str,
    refused: bool,
) -> None:
    """`rate_tables` and `reference_table_versions` keep their one legitimate in-place write.

    `current_version` is also the version allocator and `publish_version` is FR-70's
    independent approval, so neither table can be plainly append-only (E4, W1 and W3). Each is
    `guarded`: one named column moves one named way, and every other `UPDATE`, every `DELETE`
    and `TRUNCATE` is refused. As the owner, so layer 1 cannot be what refuses.
    """
    row_id = new_uuid7()
    params = {**_row_params(workspace_id, row_id), "status": status}
    insert = _GUARDED_ROWS[table]
    arrange = [(insert, {k: v for k, v in params.items() if f":{k}" in insert})]
    probe = [(statement, {"id": row_id} if ":id" in statement else {})]
    outcome = await _probe(database, probe, arrange)
    if refused:
        _assert_refused(outcome, f"{table}: {statement}")
    else:
        assert outcome is None, f"{table}: {statement} was refused: {outcome}"


@pytest.mark.req("FR-44")
async def test_a_gip_app_update_on_factors_is_refused_by_the_trigger_not_only_the_grant(
    owner_database: Database, workspace_id
) -> None:
    """FD-1704 and the maintainer's ADD (PL-1769 DP-1 (a)): the planted UPDATE is refused.

    Two observations, told apart by message and not by SQLSTATE (both are 42501): the grant
    refuses `gip_app` first, and the trigger refuses it again when a later migration grants
    `UPDATE` back. That second case is the one a grants-derived set could not see.
    """
    row_id = new_uuid7()
    row = _row_params(workspace_id, row_id)
    async with owner_database.unit_of_work() as session:
        await session.execute(text(str(_APPEND_ONLY_ROWS["factors"])), row)
    planted = text("UPDATE factors SET body = '{\"rewritten\": true}' WHERE id = :id")

    async def as_gip_app(*, reopen_layer_1: bool) -> None:
        # `owner_database.session()` never commits: neither the role switch nor the GRANT survives.
        async with owner_database.session() as session:
            if reopen_layer_1:
                await session.execute(text("GRANT UPDATE ON factors TO gip_app"))
            await session.execute(text("SET LOCAL ROLE gip_app"))
            await session.execute(planted, {"id": row_id})

    # Layer 1: the grant.
    with pytest.raises(DBAPIError) as by_grant:
        await as_gip_app(reopen_layer_1=False)
    assert "permission denied for table factors" in str(by_grant.value)

    # Layer 2: the trigger, with layer 1 reopened inside this transaction only.
    with pytest.raises(DBAPIError) as by_trigger:
        await as_gip_app(reopen_layer_1=True)
    assert "factors is append-only: UPDATE rejected (01 FR-42, FR-43)" in str(by_trigger.value)

    async with owner_database.session() as session:
        leaked = (
            await session.execute(
                text("SELECT has_table_privilege('gip_app', 'factors', 'UPDATE')")
            )
        ).scalar_one()
        body = (
            await session.execute(text("SELECT body FROM factors WHERE id = :id"), {"id": row_id})
        ).scalar_one()
    assert leaked is False
    assert body == {"stored": True}


#: The six tables that carry a row guard and no `TRUNCATE` trigger today (plan review R2).
_ROW_GUARDED_ONLY = (
    "approval_requests",
    "blobs",
    "deployment_requests",
    "rating_versions",
    "validation_rule_sets",
    "validation_rules",
)


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("table", _ROW_GUARDED_ONLY)
async def test_a_row_guarded_table_refuses_truncate_from_the_owner_connection(
    owner_database: Database, table: str
) -> None:
    """A row guard does not fire on `TRUNCATE`: six tables had one and could still be emptied.

    The table is truncated together with every table that references it, read from
    `pg_constraint`, in a transaction that rolls back. Where a referencing table's own `TRUNCATE`
    trigger already refuses, that message is the one printed here (plan review R2); the catalog
    test `<table>_no_truncate` is the table-specific proof.
    """
    sql = f"TRUNCATE {await _referencing_closure(owner_database, table)}"
    refused = await _probe(owner_database, [(sql, {})])
    message = _assert_refused(refused, sql)
    assert "append-only" in message, message
    print(f"{table}: {message.splitlines()[0] if message else message}")


@pytest.mark.req("FR-44")
def test_every_mapped_table_declares_its_immutability() -> None:
    """A table that declares nothing fails here on the day it is added (FD-1728)."""
    failures = []
    for table in Base.metadata.sorted_tables:
        kind = table.info.get("immutability")
        if kind not in {"append_only", "guarded", "mutable"}:
            failures.append(f"{table.name}: immutability={kind!r}")
        elif kind != "append_only" and not table.info.get("reason"):
            failures.append(f"{table.name}: {kind} without a reason")
        elif kind == "guarded" and not table.info.get("guards"):
            failures.append(f"{table.name}: guarded without its named guard triggers")
    assert failures == []


@pytest.mark.req("FR-44")
async def test_the_declarations_cover_every_table_in_the_database(database: Database) -> None:
    """Closed both ways against `pg_class`: nothing is undeclared, nothing declared is absent."""
    async with database.session() as session:
        public = {
            row[0]
            for row in (
                await session.execute(
                    text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
                )
            ).all()
        }
    assert public - {"alembic_version"} == {t.name for t in Base.metadata.sorted_tables}


async def _triggers(database: Database, tables: tuple[str, ...]) -> dict[str, dict[str, set[str]]]:
    """`{table: {"row": {names}, "statement": {names}}}` for the non-internal triggers."""
    found: dict[str, dict[str, set[str]]] = {t: {"row": set(), "statement": set()} for t in tables}
    async with database.session() as session:
        rows = (
            await session.execute(
                text("""
                    SELECT c.relname, t.tgname, (t.tgtype & 1 = 1) AS is_row
                    FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid
                    WHERE c.relnamespace = 'public'::regnamespace AND NOT t.tgisinternal
                      AND c.relname = ANY(:tables)
                """),
                {"tables": list(tables)},
            )
        ).all()
    for table, name, is_row in rows:
        found[table]["row" if is_row else "statement"].add(name)
    return found


@pytest.mark.req("FR-44")
async def test_every_declared_append_only_table_carries_both_triggers(
    database: Database,
) -> None:
    """The check that catches the *next* table, rather than the six this slice found.

    The set is the ORM declaration's (DP-8), not the grants': a table whose grants were widened
    by a later migration is still in it. Each carries `<table>_no_modify` (a row trigger) and
    `<table>_no_truncate` (a statement trigger): a row trigger does not fire on `TRUNCATE`.
    """
    declared = _declared("append_only")
    # Guard against the derivation going quiet: an empty set passes every assertion below.
    assert len(declared) >= 22, declared
    found = await _triggers(database, declared)
    missing = [
        t
        for t in declared
        if f"{t}_no_modify" not in found[t]["row"]
        or f"{t}_no_truncate" not in found[t]["statement"]
    ]
    assert missing == [], f"append-only tables missing a trigger: {missing}"


@pytest.mark.req("FR-44")
async def test_every_guarded_table_carries_its_named_guards_and_the_truncate_trigger(
    database: Database,
) -> None:
    """Each `guarded` table: every guard its declaration names is a row trigger, plus
    `<table>_no_truncate` (plan review R2: red on the base for the six row-guarded tables)."""
    guarded = _declared("guarded")
    assert len(guarded) >= 13, guarded
    found = await _triggers(database, guarded)
    missing = []
    for table in guarded:
        info = next(t.info for t in Base.metadata.sorted_tables if t.name == table)
        for guard in info["guards"]:
            if guard not in found[table]["row"]:
                missing.append(f"{table}: row trigger {guard}")
        if f"{table}_no_truncate" not in found[table]["statement"]:
            missing.append(f"{table}: {table}_no_truncate")
    assert missing == []


@pytest.mark.req("FR-44")
async def test_the_two_guarded_artifacts_grant_the_application_one_column_update(
    database: Database,
) -> None:
    """Layer 1 for `rate_tables` and `reference_table_versions` (DP-12): the one column that moves.

    Table-level `UPDATE` is not granted (the exact-grant test would see it); the column
    privilege is what the guarded transition needs, and it is pinned here exactly.
    """
    async with database.session() as session:
        rows = (
            await session.execute(
                text("""
                    SELECT table_name, array_agg(column_name::text ORDER BY column_name)
                    FROM information_schema.column_privileges
                    WHERE grantee = 'gip_app' AND privilege_type = 'UPDATE'
                      AND table_name IN ('rate_tables', 'reference_table_versions')
                    GROUP BY table_name
                """)
            )
        ).all()
    assert dict(rows) == {
        "rate_tables": ["current_version", "updated_at"],
        "reference_table_versions": ["status"],
    }
    async with database.session() as session:
        table_level = {
            row[0]
            for row in (
                await session.execute(
                    text("""
                        SELECT DISTINCT privilege_type FROM information_schema.table_privileges
                        WHERE grantee = 'gip_app'
                          AND table_name IN ('rate_tables', 'reference_table_versions')
                    """)
                )
            ).all()
        }
    assert table_level == {"SELECT", "INSERT"}


# -- `dataset_versions`: the immutable snapshot, guarded (DP-21; FD-1728) ---------------
#
# Added 2026-10-18 (WK-1178, SL-1770). `dataset_versions` is "the immutable snapshot" of
# `CLAUDE.md` §7 and `00` §2, yet the application updates eleven columns in place. The
# maintainer (by delegation) ruled it `guarded`: the DATA frozen from the first
# `draft -> validating`, for ever (`to-lead.md` "2026-10-14 13:27:39 BST"); `status` follows
# `VALID_DATASET_TRANSITIONS` (corrected by "2026-10-16 09:40:20 BST" Q1: derived, not counted);
# the report id moves only out of `validating`; `profile_id` only `NULL -> value` after the
# freeze. Every case runs as the owner, in a transaction that rolls back, and is arranged
# through *allowed* transitions only, so no arrangement depends on the guard's own column.

_DS_INSERT = (
    "INSERT INTO dataset_versions (id, slug, workspace_id, dataset_id, version, status, kind, "
    "tables, library_versions, labels, schema_version, currency, created_by) "
    "VALUES (:id, :slug, :ws, gen_random_uuid(), 1, 'draft', 'ingested', "
    "CAST('[]' AS jsonb), CAST('{}' AS jsonb), CAST('{}' AS jsonb), 1, 'GBP', "
    "gen_random_uuid())"
)

#: How to reach a status through allowed transitions only. `validated` needs its report id
#: (`validated_names_its_report`); it is set on the way out of `validating`, which is when the
#: ruling lets the report id move. `archived` takes its `archived_at` in the same `UPDATE`.
_TO_VALIDATING = "UPDATE dataset_versions SET status = 'validating' WHERE id = :id"
_TO_VALIDATED = (
    "UPDATE dataset_versions SET status = 'validated', "
    "validation_report_id = gen_random_uuid() WHERE id = :id"
)
_TO_FAILED = "UPDATE dataset_versions SET status = 'failed' WHERE id = :id"
_BACK_TO_DRAFT = (
    "UPDATE dataset_versions SET status = 'draft', validation_report_id = NULL WHERE id = :id"
)
_TO_ARCHIVED = (
    "UPDATE dataset_versions SET status = 'archived', archived_at = now() WHERE id = :id"
)

_PATH_TO: dict[str, tuple[str, ...]] = {
    "draft": (),
    "validating": (_TO_VALIDATING,),
    "validated": (_TO_VALIDATING, _TO_VALIDATED),
    "failed": (_TO_VALIDATING, _TO_FAILED),
    "archived": (_TO_ARCHIVED,),
    #: FR-53: `validated -> validating -> draft`. The data stays frozen.
    "returned-to-draft": (_TO_VALIDATING, _BACK_TO_DRAFT),
}

#: One new value per data column the ruling freezes (`tables`, `source_fingerprint`, `totals`,
#: `derived_from`, `library_versions`, `ingestion_run_id`).
_FROZEN_DATA_WRITES: dict[str, str] = {
    "tables": "tables = CAST('[{\"name\": \"x\"}]' AS jsonb)",
    "source_fingerprint": "source_fingerprint = CAST('{\"sha\": \"x\"}' AS jsonb)",
    "totals": "totals = CAST('{\"rows\": 1}' AS jsonb)",
    "derived_from": "derived_from = CAST('{\"parent\": \"x\"}' AS jsonb)",
    "library_versions": "library_versions = CAST('{\"polars\": \"1\"}' AS jsonb)",
    "ingestion_run_id": "ingestion_run_id = gen_random_uuid()",
}


def _ds_params(workspace_id) -> dict:
    row_id = new_uuid7()
    return {"id": row_id, "ws": workspace_id, "slug": f"s-{row_id.hex[-8:]}"}


async def _ds_probe(
    database: Database, workspace_id, reach: str, *statements: str
) -> DBAPIError | None:
    """Arrange a `dataset_versions` row in `reach`, then attempt `statements`, rolled back."""
    params = _ds_params(workspace_id)
    arrange = [(_DS_INSERT, params)] + [(sql, params) for sql in _PATH_TO[reach]]
    return await _probe(database, [(sql, params) for sql in statements], arrange)


def _status_set(target: str) -> str:
    """The `UPDATE` that sets `status` to `target`, valid on every constraint but the guard.

    `validated` carries a report id (`validated_names_its_report`), so a refusal of the
    transition is the guard's, never the check constraint's.
    """
    extra = (
        ", validation_report_id = COALESCE(validation_report_id, gen_random_uuid())"
        if target == "validated"
        else ", archived_at = now()" if target == "archived" else ""
    )
    return f"UPDATE dataset_versions SET status = '{target}'{extra} WHERE id = :id"


_STATUSES = [status.value for status in DatasetStatus]
_PAIRS = [
    pytest.param(source, target, id=f"{source}->{target}")
    for source in _STATUSES
    for target in _STATUSES
    if source != target
]


@pytest.mark.req("FR-44")
@pytest.mark.parametrize(("source", "target"), _PAIRS)
async def test_a_dataset_version_status_follows_the_transition_table_exactly(
    database: Database, workspace_id, source: str, target: str
) -> None:
    """Refused iff the pair is not in `VALID_DATASET_TRANSITIONS`; applied iff it is.

    Parametrised from the imported table itself (the maintainer (by delegation), "2026-10-16
    09:40:20 BST" Q1: *by derivation, not by count*): every `(from, to)` pair of `DatasetStatus`
    with `from != to`. Eleven of the twenty are refused at main `0877e6e7`; the nine allowed
    ones are controls that pass on the base and must stay green.
    """
    allowed = DatasetStatus(target) in VALID_DATASET_TRANSITIONS[DatasetStatus(source)]
    outcome = await _ds_probe(database, workspace_id, source, _status_set(target))
    if allowed:
        assert outcome is None, f"{source} -> {target} is in the table but was refused: {outcome}"
    else:
        _assert_refused(outcome, f"{source} -> {target}")


@pytest.mark.req("FR-44")
async def test_an_archived_dataset_version_takes_no_update_at_all(
    database: Database, workspace_id
) -> None:
    """`archived` is terminal: even `updated_at` alone is refused (09:40:20 Q1)."""
    outcome = await _ds_probe(
        database, workspace_id, "archived",
        "UPDATE dataset_versions SET updated_at = now() WHERE id = :id",
    )
    _assert_refused(outcome, "UPDATE of an archived dataset version")


@pytest.mark.req("FR-44")
async def test_an_unchanged_status_is_not_a_transition_and_is_not_refused_as_one(
    database: Database, workspace_id
) -> None:
    """The control of the "unchanged" limb (09:44:25 item 2): the other rules still decide.

    `validated -> validated` setting `profile_id` `NULL -> value` on a data-frozen row is
    permitted. Green on the base (nothing guards) and green after SL-1770; its pair below is
    the one that is refused, so rule 3 cannot be read as a bypass of the freeze.
    """
    outcome = await _ds_probe(
        database, workspace_id, "validated",
        "UPDATE dataset_versions SET status = 'validated', profile_id = gen_random_uuid() "
        "WHERE id = :id",
    )
    assert outcome is None, f"a same-status profile_id NULL -> value was refused: {outcome}"


@pytest.mark.req("FR-44")
async def test_an_unchanged_status_does_not_unfreeze_the_data(
    database: Database, workspace_id
) -> None:
    """The refused half of the pair: `validated -> validated` setting `tables` is the freeze's."""
    outcome = await _ds_probe(
        database, workspace_id, "validated",
        "UPDATE dataset_versions SET status = 'validated', "
        "tables = CAST('[{\"name\": \"x\"}]' AS jsonb) WHERE id = :id",
    )
    _assert_refused(outcome, "validated -> validated setting tables on a frozen row")


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("column", sorted(_FROZEN_DATA_WRITES))
async def test_a_version_returned_to_draft_by_fr_53_keeps_its_data_frozen(
    database: Database, workspace_id, column: str
) -> None:
    """The ruling's own red: the data freezes at the first validation and stays frozen.

    FR-53 sends a version back to `draft` and flags the Models fitted on it; it does not let
    the data change under them. `draft` is not "never validated".
    """
    outcome = await _ds_probe(
        database, workspace_id, "returned-to-draft",
        f"UPDATE dataset_versions SET {_FROZEN_DATA_WRITES[column]} WHERE id = :id",
    )
    _assert_refused(outcome, f"{column} on a version returned to draft")


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("state", ["validating", "validated", "failed"])
async def test_the_data_of_a_dataset_version_is_frozen_in_every_later_state(
    database: Database, workspace_id, state: str
) -> None:
    outcome = await _ds_probe(
        database, workspace_id, state,
        f"UPDATE dataset_versions SET {_FROZEN_DATA_WRITES['tables']} WHERE id = :id",
    )
    _assert_refused(outcome, f"tables on a {state} version")


@pytest.mark.req("FR-44")
async def test_the_data_of_a_never_validated_draft_may_still_change(
    database: Database, workspace_id
) -> None:
    """Ingestion, `correct_schema`, derivation and the split write `tables` pre-validation."""
    outcome = await _ds_probe(
        database, workspace_id, "draft",
        f"UPDATE dataset_versions SET {_FROZEN_DATA_WRITES['tables']} WHERE id = :id",
        f"UPDATE dataset_versions SET {_FROZEN_DATA_WRITES['totals']} WHERE id = :id",
    )
    assert outcome is None, f"a pre-validation data write was refused: {outcome}"


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("state", ["draft", "validated"])
async def test_the_report_id_moves_only_out_of_validating(
    database: Database, workspace_id, state: str
) -> None:
    """`draft -> draft` and `validated -> validated` may not change `validation_report_id`."""
    outcome = await _ds_probe(
        database, workspace_id, state,
        "UPDATE dataset_versions SET validation_report_id = gen_random_uuid() WHERE id = :id",
    )
    _assert_refused(outcome, f"validation_report_id on a {state} version")


@pytest.mark.req("FR-44")
async def test_a_frozen_dataset_version_is_never_re_profiled_at_the_database(
    database: Database, workspace_id
) -> None:
    """`profile_id` is `NULL -> value` once after the freeze; a re-point is refused (15:14:52)."""
    params = _ds_params(workspace_id)
    arrange = [(_DS_INSERT, params)] + [(sql, params) for sql in _PATH_TO["validated"]]
    arrange.append(
        ("UPDATE dataset_versions SET profile_id = gen_random_uuid() WHERE id = :id", params)
    )
    outcome = await _probe(
        database,
        [("UPDATE dataset_versions SET profile_id = gen_random_uuid() WHERE id = :id", params)],
        arrange,
    )
    _assert_refused(outcome, "a profile re-point on a data-frozen version")


@pytest.mark.req("FR-44")
async def test_a_dataset_version_keeps_its_identity(database: Database, workspace_id) -> None:
    outcome = await _ds_probe(
        database, workspace_id, "draft",
        "UPDATE dataset_versions SET slug = slug || 'x' WHERE id = :id",
    )
    _assert_refused(outcome, "an identity column of a draft dataset version")


@pytest.mark.req("FR-44")
@pytest.mark.parametrize("statement", ["DELETE", "TRUNCATE"])
async def test_a_dataset_version_is_never_deleted_or_truncated(
    database: Database, workspace_id, statement: str
) -> None:
    sql = {
        "DELETE": "DELETE FROM dataset_versions WHERE id = :id",
        "TRUNCATE": f"TRUNCATE {await _referencing_closure(database, 'dataset_versions')}",
    }[statement]
    outcome = await _ds_probe(database, workspace_id, "draft", sql)
    _assert_refused(outcome, sql)


@pytest.mark.req("FR-44")
async def test_fr_53_may_revalidate_a_validated_version_and_move_the_report_id(
    database: Database, workspace_id
) -> None:
    """Allowed, green before and after: `validated -> validating -> validated` (new report) and
    `validating -> draft` (report cleared). The report id moves only out of `validating`.
    """
    new_report = (
        "UPDATE dataset_versions SET status = 'validated', "
        "validation_report_id = gen_random_uuid() WHERE id = :id"
    )
    revalidate = await _ds_probe(
        database, workspace_id, "validated", _TO_VALIDATING, new_report
    )
    assert revalidate is None, f"FR-53 re-validation was refused: {revalidate}"
    back = await _ds_probe(database, workspace_id, "validated", _TO_VALIDATING, _BACK_TO_DRAFT)
    assert back is None, f"FR-53's return to draft was refused: {back}"


@pytest.mark.req("FR-43")
def test_the_snapshot_guard_names_only_columns_that_exist() -> None:
    """The guard compares `to_jsonb(NEW) - <columns>` and names the frozen data by column. A
    name that no longer matches a `DatasetVersionRow` column removes nothing from either side,
    so the comparison passes where it should refuse: the migration's lists are held to the
    model (the postgres-pro review of `a4d1f08c3b97`, PL-1769 Step 6.1)."""
    path = next(Path(__file__).resolve().parents[1].glob("migrations/versions/a4d1f08c3b97_*.py"))
    spec = importlib.util.spec_from_file_location("a4d1f08c3b97_pin", path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    columns = {column.name for column in DatasetVersionRow.__table__.columns}
    assert set(migration.MOVING_COLUMNS) <= columns
    assert set(migration.FROZEN_DATA_COLUMNS) <= set(migration.MOVING_COLUMNS)
