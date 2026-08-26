"""Derived versions, lineage, access and erasure (`01` §3.5 to §3.7)."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    AuditEventRow,
    ReferenceRowRow,
    ReferenceTableVersionRow,
    RoleAssignmentRow,
    RoleRow,
    SubjectPurgeRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets, rbac
from model_schema import (
    ActorKind,
    DatasetKind,
    DatasetStatus,
    Principal,
    ScopeType,
    new_uuid7,
)


async def _with_role(database: Database, workspace_id, role: str) -> Principal:
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display="u@insurer.example")
    async with database.unit_of_work() as session:
        await rbac.seed_builtin_roles(session, workspace_id)
        row = (
            await session.execute(
                select(RoleRow).where(
                    RoleRow.workspace_id == workspace_id, RoleRow.slug == role
                )
            )
        ).scalar_one()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id, principal_kind="user", principal_id=user.id,
                role_id=row.id, scope_type=ScopeType.WORKSPACE.value,
            )
        )
    return user


async def _version(database: Database, workspace_id, actor):
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor,
            slug=f"ds-{new_uuid7().hex[-8:]}",
        )
        version = await datasets.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset.id
        )
        return dataset.id, version.id


# -- FR-DATA-29: effective-dated intervals, enforced by the database -------------------------


@pytest.mark.req("FR-DATA-29")
async def test_overlapping_reference_intervals_are_rejected_by_the_database(
    database: Database, workspace_id
) -> None:
    """FR-DATA-29, enforced by an exclusion constraint rather than application code.

    Overlapping intervals mean an "as at" lookup has two answers, and which one a quote
    receives would depend on row order — a rating difference nobody could reproduce.
    """
    async with database.unit_of_work() as session:
        version = ReferenceTableVersionRow(
            workspace_id=workspace_id, reference_table_id=new_uuid7(), version=1,
            status="approved",
        )
        session.add(version)
        await session.flush()
        version_id = version.id
        session.add(
            ReferenceRowRow(
                reference_table_version_id=version_id, key="SW1A", payload={},
                effective_from=date(2026, 1, 1), effective_to=date(2026, 7, 1),
            )
        )

    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            session.add(
                ReferenceRowRow(
                    reference_table_version_id=version_id, key="SW1A", payload={},
                    effective_from=date(2026, 4, 1), effective_to=date(2026, 10, 1),
                )
            )


@pytest.mark.req("FR-DATA-29")
async def test_adjacent_intervals_are_permitted(
    database: Database, workspace_id
) -> None:
    """Negative of the above: if adjacency were rejected, consecutive effective periods
    would be impossible and the whole design unusable."""
    async with database.unit_of_work() as session:
        version = ReferenceTableVersionRow(
            workspace_id=workspace_id, reference_table_id=new_uuid7(), version=1,
        )
        session.add(version)
        await session.flush()
        session.add_all(
            [
                ReferenceRowRow(
                    reference_table_version_id=version.id, key="SW1A", payload={},
                    effective_from=date(2026, 1, 1), effective_to=date(2026, 7, 1),
                ),
                ReferenceRowRow(
                    reference_table_version_id=version.id, key="SW1A", payload={},
                    effective_from=date(2026, 7, 1), effective_to=None,
                ),
            ]
        )
        version_id = version.id

    async with database.session() as session:
        rows = (
            await session.execute(
                select(ReferenceRowRow).where(
                    ReferenceRowRow.reference_table_version_id == version_id
                )
            )
        ).scalars().all()
    assert len(rows) == 2


@pytest.mark.req("FR-DATA-30")
async def test_a_reference_version_number_is_unique_per_table(
    database: Database, workspace_id
) -> None:
    """FR-DATA-30: versions are immutable and pinned explicitly — never "latest"."""
    table_id = new_uuid7()
    async with database.unit_of_work() as session:
        session.add(
            ReferenceTableVersionRow(
                workspace_id=workspace_id, reference_table_id=table_id, version=1
            )
        )
    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            session.add(
                ReferenceTableVersionRow(
                    workspace_id=workspace_id, reference_table_id=table_id, version=1
                )
            )


# -- FR-DATA-33/34: derived versions ------------------------------------------------------------


@pytest.mark.req("FR-DATA-33")
async def test_a_derived_version_records_its_operation_and_parent(
    database: Database, workspace_id
) -> None:
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        child = await datasets.derive_version(
            session, workspace_id=workspace_id, actor=actor, parent_version_id=parent_id,
            operation="split", params={"method": "temporal", "cutoff": "2025-07-01",
                                       "part": "train", "seed": 20260814},
        )
    assert child.kind == DatasetKind.DERIVED
    assert child.derived_from["parent_version_id"] == str(parent_id)
    assert child.derived_from["operation"] == "split"


@pytest.mark.req("FR-DATA-33")
async def test_an_undeclared_derivation_is_refused(
    database: Database, workspace_id
) -> None:
    """Negative: a derivation the platform cannot describe is one it cannot reproduce, and
    a derived dataset nobody can rebuild is a dataset whose model cannot be defended."""
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.derive_version(
                session, workspace_id=workspace_id, actor=actor,
                parent_version_id=parent_id, operation="custom_python", params={},
            )
    assert exc.value.code == "VALIDATION_FAILED"


@pytest.mark.req("FR-OVR-8")
async def test_a_stochastic_derivation_without_a_seed_is_refused(
    database: Database, workspace_id
) -> None:
    """FR-OVR-8: identical inputs must give identical outputs. Without a recorded seed the
    version cannot be reproduced.

    Exercised on `split` because it is the only stochastic operation that gets as far as
    the seed check — `sample` is refused a line earlier as unmaterialised (FR-DATA-45).
    """
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as seed_exc:
            await datasets.derive_version(
                session, workspace_id=workspace_id, actor=actor,
                parent_version_id=parent_id, operation="split",
                params={"method": "random", "part": "train"},
            )
    assert seed_exc.value.title == "This derivation needs a seed"


@pytest.mark.req("FR-DATA-45")
@pytest.mark.parametrize("operation", ["sample", "filter", "join", "aggregate"])
async def test_a_derivation_that_cannot_produce_its_rows_is_refused(
    database: Database, workspace_id, operation: str
) -> None:
    """Negative, FR-DATA-45 (OQ-DATA-8, decided 2026-08-17): refusing beats succeeding.

    Each of these used to return a version that recorded the operation and pointed at the
    parent's blob, so a 1 % sample held 100 % of the rows and said nothing about it. A
    derivation nobody performed cannot be reproduced or defended (FR-DATA-33), and the
    failure is silent — the version validates, profiles and fits, and every number it
    produces is the parent's.
    """
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.derive_version(
                session, workspace_id=workspace_id, actor=actor,
                parent_version_id=parent_id, operation=operation,
                params={"seed": 1, "fraction": 0.01},
            )
    assert exc.value.code == "DERIVATION_NOT_MATERIALISED"
    assert exc.value.status_code == 501


@pytest.mark.req("FR-DATA-44")
async def test_split_is_the_one_derivation_that_is_not_refused(
    database: Database, workspace_id
) -> None:
    """The positive half, and the guard against the refusal widening to everything.

    `UNMATERIALISED_OPERATIONS` is `DERIVED_OPERATIONS` minus `split`; a refusal computed
    by subtraction is exactly the kind that quietly swallows the one case that works.
    """
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        child = await datasets.derive_version(
            session, workspace_id=workspace_id, actor=actor, parent_version_id=parent_id,
            operation="split", params={"part": "train", "seed": 1},
        )
    assert child.derived_from["operation"] == "split"


@pytest.mark.req("FR-DATA-34")
async def test_a_derived_version_starts_in_draft_and_must_be_validated_itself(
    database: Database, workspace_id
) -> None:
    """FR-DATA-34: it inherits schema and rule set, never validity.

    A stratified sample of a validated dataset can break rules the parent passed — an
    exposure band with two claims in the sample and two thousand in the parent fails a
    plausibility rule the parent never came near.
    """
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        await datasets.transition(
            session, workspace_id=workspace_id, actor=actor, version_id=parent_id,
            to_status=DatasetStatus.VALIDATING,
        )
    async with database.unit_of_work() as session:
        await datasets.promote_to_validated(
            session, workspace_id=workspace_id, actor=actor, version_id=parent_id,
            report_id=new_uuid7(), report_passed=True, unacknowledged_warnings=0,
        )
    async with database.unit_of_work() as session:
        child = await datasets.derive_version(
            session, workspace_id=workspace_id, actor=actor, parent_version_id=parent_id,
            operation="split", params={"part": "train", "seed": 7},
        )
        child_id = child.id

    async with database.session() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=child_id
            )
    assert exc.value.code == "DATASET_NOT_VALIDATED"


# -- FR-DATA-35/36: lineage -----------------------------------------------------------------------


@pytest.mark.req("FR-DATA-35")
async def test_lineage_answers_both_directions(
    database: Database, workspace_id
) -> None:
    """"What was this built from?" defends a model; "what depends on this?" is what someone
    asks before archiving, and getting it wrong means discovering the dependency when a
    rating version stops resolving."""
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        child = await datasets.derive_version(
            session, workspace_id=workspace_id, actor=actor, parent_version_id=parent_id,
            operation="split", params={"part": "train", "seed": 1},
        )
        child_id = child.id

    async with database.session() as session:
        upstream = await datasets.lineage_of(
            session, workspace_id=workspace_id, version_id=child_id
        )
        downstream = await datasets.lineage_of(
            session, workspace_id=workspace_id, version_id=parent_id
        )

    assert upstream.built_from is not None
    assert upstream.built_from.parent_version_id == parent_id
    assert upstream.built_from.operation == "split"
    assert upstream.built_from.parameters == {"part": "train", "seed": 1}
    assert upstream.depends_on_this.derived_versions == []
    assert [d.version_id for d in downstream.depends_on_this.derived_versions] == [child_id]
    assert [d.operation for d in downstream.depends_on_this.derived_versions] == ["split"]
    assert downstream.built_from is None


# -- FR-DATA-37/38/39: access, archival, erasure --------------------------------------


@pytest.mark.req("FR-DATA-37")
async def test_reading_a_dataset_requires_access(
    database: Database, workspace_id
) -> None:
    """FR-DATA-37: a user without read access cannot see it — not in lineage either."""
    stranger = Principal(kind=ActorKind.USER, id=new_uuid7(), display="x")
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.create_dataset(
                session, workspace_id=workspace_id, actor=stranger, slug="secret"
            )
    assert exc.value.code == "PERMISSION_DENIED"


@pytest.mark.req("FR-DATA-38")
async def test_an_archived_version_stays_readable_and_referenceable(
    database: Database, workspace_id
) -> None:
    """FR-DATA-38: archived versions remain readable and referenceable by existing Models.

    ID-5 is soft-delete only — nothing is removed from the database, because a Model fitted
    on a version must still be able to say what it was fitted on.
    """
    actor = await _with_role(database, workspace_id, "analyst")
    _, version_id = await _version(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        await datasets.archive_version(
            session, workspace_id=workspace_id, actor=actor, version_id=version_id,
            reason="superseded by the 2026H2 extract",
        )
    async with database.session() as session:
        from app.db.models import DatasetVersionRow

        row = await session.get(DatasetVersionRow, version_id)
    assert row is not None
    assert row.status == DatasetStatus.ARCHIVED


@pytest.mark.req("FR-DATA-38")
async def test_an_archived_version_cannot_be_fitted_on(
    database: Database, workspace_id
) -> None:
    """Negative: readable is not fittable."""
    actor = await _with_role(database, workspace_id, "analyst")
    _, version_id = await _version(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        await datasets.archive_version(
            session, workspace_id=workspace_id, actor=actor, version_id=version_id,
            reason="superseded",
        )
    async with database.session() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.fittable_or_refuse(
                session, workspace_id=workspace_id, version_id=version_id
            )
    assert exc.value.code == "DATASET_NOT_VALIDATED"


@pytest.mark.req("FR-DATA-39")
async def test_a_subject_purge_is_admin_only_and_recorded(
    database: Database, workspace_id
) -> None:
    """FR-DATA-39: the purge is recorded even though the data is gone — especially because
    it is. An erasure with no record is indistinguishable from data that was never there."""
    analyst = await _with_role(database, workspace_id, "analyst")
    dataset_id, _ = await _version(database, workspace_id, analyst)

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.purge_subject(
                session, workspace_id=workspace_id, actor=analyst, dataset_id=dataset_id,
                subject_token="a" * 32, reason="DSAR 2026-114",
            )
    assert exc.value.code == "PERMISSION_DENIED"

    admin = await _with_role(database, workspace_id, "admin")
    async with database.unit_of_work() as session:
        record = await datasets.purge_subject(
            session, workspace_id=workspace_id, actor=admin, dataset_id=dataset_id,
            subject_token="a" * 32, reason="DSAR 2026-114",
        )
        assert record.versions_affected >= 1

    async with database.session() as session:
        purges = (
            await session.execute(
                select(SubjectPurgeRow).where(SubjectPurgeRow.dataset_id == dataset_id)
            )
        ).scalars().all()
        actions = [
            e.action
            for e in (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace_id
                    )
                )
            ).scalars()
        ]
    assert len(purges) == 1
    assert purges[0].reason == "DSAR 2026-114"
    assert "dataset.subject_purged" in actions


@pytest.mark.req("FR-DATA-39")
async def test_a_purge_without_a_reason_is_refused(
    database: Database, workspace_id
) -> None:
    admin = await _with_role(database, workspace_id, "admin")
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.purge_subject(
                session, workspace_id=workspace_id, actor=admin, dataset_id=new_uuid7(),
                subject_token="a" * 32, reason="  ",
            )
    assert exc.value.title == "A purge requires a reason"


# -- FR-DATA-32: loaders, and the licence rule OQ-DATA-5 settled --------------------------------


@pytest.mark.req("FR-DATA-32")
def test_loaders_ship_for_every_reference_set_the_requirement_names() -> None:
    from app.data.reference_loaders import LOADERS

    assert {"ons-postcode-directory", "abi-vehicle-groups", "soc-occupation-codes",
            "uk-bank-holidays"} <= set(LOADERS)


@pytest.mark.req("FR-DATA-32")
def test_abi_vehicle_group_data_is_never_shippable() -> None:
    """OQ-DATA-5, decided 2026-08-14. The negative test that keeps the decision true.

    ABI group tables are not freely redistributable; bundling them would put a licence
    breach in every clone of this repository. The loader ships, the rows never do.
    """
    from app.data.reference_loaders import Licence, loader_for, shippable_loaders

    abi = loader_for("abi-vehicle-groups")
    assert abi.licence is Licence.PROPRIETARY
    assert abi.may_ship_data is False
    assert abi not in shippable_loaders()
    assert "NOT REDISTRIBUTABLE" in abi.fetch_note


@pytest.mark.req("FR-DATA-32")
def test_only_ogl_sources_may_ship_their_rows() -> None:
    from app.data.reference_loaders import Licence, shippable_loaders

    assert all(loader.licence is Licence.OGL for loader in shippable_loaders())


@pytest.mark.req("FR-DATA-32")
def test_no_reference_rows_are_bundled_in_the_repository() -> None:
    """The decision, checked against the tree rather than against intent.

    A loader is a parser plus a documented fetch step. If a data file ever appears here,
    somebody has shipped rows — and this is the test that says so before a licence holder
    does.

    Vendored skills under `.claude/skills/` are the one carve-out, and it is conditional
    rather than blanket. `ui-ux-pro-max` (2026-08-17) is the first vendored skill to ship
    data files — 18 CSVs of font, colour and UX guidance — and FR-DATA-32 is about UK
    *reference* sets whose rows are not ours to redistribute, not about a third-party
    payload committed under its own licence. So the exemption is bought by that licence:
    a skill may carry data only while its LICENSE travels with it in the same directory,
    which is precisely the exposure this test exists to prevent. Delete the licence and
    this fails, which is the point.
    """
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2]

    def licensed_vendored_skill(path: pathlib.Path) -> bool:
        """True when `path` sits under a skill directory that commits its upstream licence.

        Matched at any depth rather than against one fixed prefix: a worktree under
        `.claude/worktrees/` carries its own `.claude/skills/`, and a check anchored to
        the outer one would fail the whole suite in the main checkout whenever a worktree
        happened to exist.
        """
        parts = path.parts
        for i in range(len(parts) - 3):
            if parts[i] == ".claude" and parts[i + 1] == "skills":
                skill_dir = pathlib.Path(*parts[: i + 3])
                return any((skill_dir / n).is_file() for n in ("LICENSE", "LICENSE.txt"))
        return False

    data_files = [
        path
        for pattern in ("*.csv", "*.parquet", "*.xlsx")
        for path in root.rglob(pattern)
        if ".venv" not in path.parts
        and ".git" not in path.parts
        and not licensed_vendored_skill(path)
    ]
    assert data_files == [], f"unexpected bundled data: {data_files}"


# -- FR-DATA-36: splits recorded on the parent ----------------------------------------


@pytest.mark.req("FR-DATA-36")
async def test_a_split_is_recorded_on_the_parent_so_two_models_can_be_compared(
    database: Database, workspace_id
) -> None:
    """FR-DATA-36: "trained on the same split" becomes a single reference both models cite,
    rather than two derivations that were *believed* to match."""
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)

    async with database.unit_of_work() as session:
        train = await datasets.derive_version(
            session, workspace_id=workspace_id, actor=actor, parent_version_id=parent_id,
            operation="split", params={"part": "train", "seed": 20260814},
        )
        test = await datasets.derive_version(
            session, workspace_id=workspace_id, actor=actor, parent_version_id=parent_id,
            operation="split", params={"part": "test", "seed": 20260814},
        )
        split = await datasets.record_split(
            session, workspace_id=workspace_id, actor=actor,
            parent_version_id=parent_id, name="2026h1-temporal", method="temporal",
            seed=20260814, parts={"train": train.id, "test": test.id},
            params={"cutoff": "2025-07-01"},
        )
        assert split.parent_version_id == parent_id
        assert set(split.parts) == {"train", "test"}


@pytest.mark.req("FR-DATA-36")
async def test_a_one_part_split_is_refused(database: Database, workspace_id) -> None:
    """Negative: a one-part split is a filter, and recording it as a split would let a
    model claim a holdout it never had."""
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.record_split(
                session, workspace_id=workspace_id, actor=actor,
                parent_version_id=parent_id, name="broken", method="random", seed=1,
                parts={"train": new_uuid7()},
            )
    assert exc.value.title == "A split needs at least two parts"


@pytest.mark.req("FR-DATA-36")
async def test_a_split_name_cannot_be_reused_on_one_version(
    database: Database, workspace_id
) -> None:
    """Negative: reusing the name for different parts makes two models citing it
    incomparable, which is the exact claim the artifact exists to support."""
    actor = await _with_role(database, workspace_id, "analyst")
    _, parent_id = await _version(database, workspace_id, actor)
    parts = {"train": new_uuid7(), "test": new_uuid7()}
    async with database.unit_of_work() as session:
        await datasets.record_split(
            session, workspace_id=workspace_id, actor=actor, parent_version_id=parent_id,
            name="holdout", method="random", seed=1, parts=parts,
        )
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.record_split(
                session, workspace_id=workspace_id, actor=actor,
                parent_version_id=parent_id, name="holdout", method="random", seed=2,
                parts={"train": new_uuid7(), "test": new_uuid7()},
            )
    assert exc.value.status_code == 409
