"""Dataset versions and the gate (`01` §1.3, §3.1, §4.2)."""

from __future__ import annotations

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.db.models import AuditEventRow, DatasetVersionRow, RoleAssignmentRow, RoleRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets, rbac
from model_schema import (
    ActorKind,
    DatasetKind,
    DatasetStatus,
    Principal,
    ScopeType,
    SourceKind,
    new_uuid7,
)


def _user() -> Principal:
    return Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")


async def _analyst(database: Database, workspace_id) -> Principal:
    user = _user()
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
                workspace_id=workspace_id,
                principal_kind="user",
                principal_id=user.id,
                role_id=role.id,
                scope_type=ScopeType.WORKSPACE.value,
            )
        )
    return user


async def _dataset(database: Database, workspace_id, actor: Principal, slug="motor-gb"):
    async with database.unit_of_work() as session:
        row = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=slug
        )
        return row.id


# -- version allocation (FR-DATA-2, ID-2) ------------------------------------------------


@pytest.mark.req("FR-DATA-2")
async def test_versions_start_at_one_and_increment(
    database: Database, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)

    versions = []
    for _ in range(3):
        async with database.unit_of_work() as session:
            row = await datasets.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
            )
            versions.append(row.version)
    assert versions == [1, 2, 3]


@pytest.mark.req("FR-DATA-2")
async def test_a_version_number_is_never_reused(
    database: Database, workspace_id
) -> None:
    """ID-2: never reused, including after a draft is archived.

    A reference to `@2` has to mean one body of data for ever — reusing the number after an
    archive would silently repoint every artifact that cited it.
    """
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        first = await datasets.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
        )
        second = await datasets.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
        )
        second_id = second.id
    async with database.unit_of_work() as session:
        await datasets.archive_version(
            session, workspace_id=workspace_id, actor=actor,
            version_id=second_id, reason="mis-ingested",
        )
    async with database.unit_of_work() as session:
        third = await datasets.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
        )
    assert (first.version, third.version) == (1, 3)


@pytest.mark.req("FR-DATA-2")
async def test_the_unique_constraint_backs_the_allocation(
    database: Database, workspace_id
) -> None:
    """Negative: the lock prevents contention, the constraint prevents corruption.

    Inserting a duplicate directly must fail, because the advisory lock only serialises
    callers who take it — anything else is one code path away from two `@1`s.
    """
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        await datasets.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
        )

    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            session.add(
                DatasetVersionRow(
                    workspace_id=workspace_id,
                    dataset_id=dataset_id,
                    version=1,
                    status=DatasetStatus.DRAFT.value,
                    kind=DatasetKind.INGESTED.value,
                )
            )


# -- the gate (`01` §1.3, FR-DATA-17) ------------------------------------------------------


@pytest.mark.req("FR-DATA-17")
async def test_validated_is_not_reachable_through_transition(
    database: Database, workspace_id
) -> None:
    """Negative, and the most important test in the module.

    A transition function that could set `validated` would be the override `01` §1.3 says
    does not exist.
    """
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        version = await datasets.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
        )
        version_id = version.id

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.transition(
                session, workspace_id=workspace_id, actor=actor,
                version_id=version_id, to_status=DatasetStatus.VALIDATED,
            )
    assert exc.value.code == "DATASET_VERSION_IMMUTABLE"


@pytest.mark.req("FR-DATA-17")
async def test_a_failing_report_cannot_validate_a_version(
    database: Database, workspace_id
) -> None:
    """`01` §1.3: no override, no force-fit, no admin bypass."""
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        version_id = (
            await datasets.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
            )
        ).id
        await datasets.transition(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, to_status=DatasetStatus.VALIDATING,
        )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.promote_to_validated(
                session, workspace_id=workspace_id, actor=actor, version_id=version_id,
                report_id=new_uuid7(), report_passed=False, unacknowledged_warnings=0,
            )
    assert exc.value.code == "VALIDATION_HAS_FAILURES"


@pytest.mark.req("FR-DATA-17")
async def test_unacknowledged_warnings_block_validation(
    database: Database, workspace_id
) -> None:
    """Negative: a warning nobody accepted is not an accepted warning."""
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        version_id = (
            await datasets.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
            )
        ).id
        await datasets.transition(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, to_status=DatasetStatus.VALIDATING,
        )

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.promote_to_validated(
                session, workspace_id=workspace_id, actor=actor, version_id=version_id,
                report_id=new_uuid7(), report_passed=True, unacknowledged_warnings=2,
            )
    assert exc.value.code == "WARN_NOT_ACKNOWLEDGED"


@pytest.mark.req("FR-DATA-17")
async def test_a_passing_acknowledged_report_validates_the_version(
    database: Database, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    report_id = new_uuid7()
    async with database.unit_of_work() as session:
        version_id = (
            await datasets.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
            )
        ).id
        await datasets.transition(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, to_status=DatasetStatus.VALIDATING,
        )
    async with database.unit_of_work() as session:
        row = await datasets.promote_to_validated(
            session, workspace_id=workspace_id, actor=actor, version_id=version_id,
            report_id=report_id, report_passed=True, unacknowledged_warnings=0,
        )
    assert row.status == DatasetStatus.VALIDATED
    assert row.validation_report_id == report_id


@pytest.mark.req("FR-DATA-17")
async def test_a_validated_version_cannot_exist_without_a_report(
    database: Database, workspace_id
) -> None:
    """Negative, at the database: the check constraint is what survives a stray UPDATE."""
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        version_id = (
            await datasets.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
            )
        ).id

    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            await session.execute(
                text(
                    "UPDATE dataset_versions SET status = 'validated' WHERE id = :id"
                ).bindparams(id=version_id)
            )


@pytest.mark.req("FR-DATA-23")
async def test_a_validated_version_can_be_revalidated_and_fail(
    database: Database, workspace_id
) -> None:
    """FR-DATA-23: a dataset that was good under an older rule set is not good now, and
    models fitted on it are the reason anyone would want to know."""
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        version_id = (
            await datasets.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
            )
        ).id
        await datasets.transition(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, to_status=DatasetStatus.VALIDATING,
        )
    async with database.unit_of_work() as session:
        await datasets.promote_to_validated(
            session, workspace_id=workspace_id, actor=actor, version_id=version_id,
            report_id=new_uuid7(), report_passed=True, unacknowledged_warnings=0,
        )
    async with database.unit_of_work() as session:
        await datasets.transition(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, to_status=DatasetStatus.VALIDATING,
        )
    async with database.unit_of_work() as session:
        row = await datasets.transition(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, to_status=DatasetStatus.FAILED,
        )
    assert row.status == DatasetStatus.FAILED


@pytest.mark.req("FR-DATA-15")
async def test_fitting_on_an_unvalidated_version_is_refused(
    database: Database, workspace_id
) -> None:
    """The check `02` will call. One place answers "may I fit on this?"."""
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        version_id = (
            await datasets.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
            )
        ).id

    async with database.session() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=version_id
            )
    assert exc.value.code == "DATASET_NOT_VALIDATED"
    assert "no override" in (exc.value.detail or "")


@pytest.mark.req("FR-DATA-2")
async def test_an_archived_version_cannot_transition(
    database: Database, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        version_id = (
            await datasets.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
            )
        ).id
    async with database.unit_of_work() as session:
        await datasets.archive_version(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, reason="superseded",
        )
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError, match="cannot move"):
            await datasets.transition(
                session, workspace_id=workspace_id, actor=actor,
                version_id=version_id, to_status=DatasetStatus.VALIDATING,
            )


# -- sources (FR-DATA-1) --------------------------------------------------------------------


@pytest.mark.req("FR-DATA-1")
async def test_credentials_must_be_a_secret_reference(
    database: Database, workspace_id
) -> None:
    """Negative: `07` R3 — a credential value here would be stored, returned and logged."""
    actor = await _analyst(database, workspace_id)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.create_source(
                session, workspace_id=workspace_id, actor=actor, slug="warehouse",
                kind=SourceKind.SQL, credentials_secret_ref="postgres://user:hunter2@db",
            )
    assert exc.value.code == "VALIDATION_FAILED"


@pytest.mark.req("FR-DATA-1")
async def test_the_database_also_refuses_a_credential_value(
    database: Database, workspace_id
) -> None:
    """The service check is a convention; the constraint is what a hurried change hits."""
    from app.db.models import SourceRow

    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            session.add(
                SourceRow(
                    workspace_id=workspace_id,
                    slug="sneaky",
                    kind="sql",
                    credentials_secret_ref="postgres://user:hunter2@db",
                )
            )


@pytest.mark.req("FR-DATA-1")
async def test_a_source_with_a_reference_is_accepted(
    database: Database, workspace_id
) -> None:
    actor = await _analyst(database, workspace_id)
    async with database.unit_of_work() as session:
        row = await datasets.create_source(
            session, workspace_id=workspace_id, actor=actor, slug="warehouse",
            kind=SourceKind.SQL, credentials_secret_ref="secret:warehouse-dsn",
        )
    assert row.credentials_secret_ref == "secret:warehouse-dsn"


# -- permissions and auditing ---------------------------------------------------------------


@pytest.mark.req("FR-GOV-2")
async def test_creating_a_dataset_requires_the_permission(
    database: Database, workspace_id
) -> None:
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.create_dataset(
                session, workspace_id=workspace_id, actor=_user(), slug="unauthorised"
            )
    assert exc.value.code == "PERMISSION_DENIED"


@pytest.mark.req("FR-GOV-20")
async def test_every_lifecycle_step_is_audited_and_chained(
    database: Database, workspace_id
) -> None:
    from app.platform import audit as audit_service

    actor = await _analyst(database, workspace_id)
    dataset_id = await _dataset(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        version_id = (
            await datasets.new_version(
                session, workspace_id=workspace_id, actor=actor, dataset_id=dataset_id
            )
        ).id
        await datasets.transition(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, to_status=DatasetStatus.VALIDATING,
        )
    async with database.unit_of_work() as session:
        await datasets.promote_to_validated(
            session, workspace_id=workspace_id, actor=actor, version_id=version_id,
            report_id=new_uuid7(), report_passed=True, unacknowledged_warnings=0,
        )

    async with database.session() as session:
        actions = [
            e.action
            for e in (
                await session.execute(
                    select(AuditEventRow)
                    .where(AuditEventRow.workspace_id == workspace_id)
                    .order_by(AuditEventRow.sequence)
                )
            ).scalars()
        ]
        checked = await audit_service.verify_chain(session, workspace_id)

    assert actions == [
        "dataset.created",
        "dataset_version.created",
        "dataset_version.validating",
        "dataset_version.validated",
    ]
    assert checked == len(actions)
