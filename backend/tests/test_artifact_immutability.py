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
    """
    async with database.session() as session:
        for table in ("validation_reports", "profiles", "validation_acknowledgements"):
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
