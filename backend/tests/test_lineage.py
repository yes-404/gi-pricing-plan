"""Derived versions, lineage, access and erasure (`01` §3.5 to §3.7)."""

from __future__ import annotations

import asyncio
import csv
import pathlib
import re
import subprocess
from datetime import date

import pytest
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    AuditEventRow,
    ModelRow,
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


async def _derive_child(database: Database, workspace_id, actor, parent_id):
    async with database.unit_of_work() as session:
        child = await datasets.derive_version(
            session, workspace_id=workspace_id, actor=actor,
            parent_version_id=parent_id, operation="split",
            params={"part": "train", "seed": 1},
        )
        return child.id


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    return _headers(principal.id, workspace_id)


# -- FR-69: effective-dated intervals, enforced by the database -------------------------


@pytest.mark.req("FR-69")
async def test_overlapping_reference_intervals_are_rejected_by_the_database(
    database: Database, workspace_id
) -> None:
    """FR-69, enforced by an exclusion constraint rather than application code.

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


@pytest.mark.req("FR-69")
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


@pytest.mark.req("FR-70")
async def test_a_reference_version_number_is_unique_per_table(
    database: Database, workspace_id
) -> None:
    """FR-70: versions are immutable and pinned explicitly — never "latest"."""
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


# -- FR-73/74: derived versions ------------------------------------------------------------


@pytest.mark.req("FR-73")
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


@pytest.mark.req("FR-73")
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


@pytest.mark.req("FR-11")
async def test_a_stochastic_derivation_without_a_seed_is_refused(
    database: Database, workspace_id
) -> None:
    """FR-11: identical inputs must give identical outputs. Without a recorded seed the
    version cannot be reproduced.

    Exercised on `split` because it is the only stochastic operation that gets as far as
    the seed check — `sample` is refused a line earlier as unmaterialised (FR-78).
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


@pytest.mark.req("FR-78")
@pytest.mark.parametrize("operation", ["sample", "filter", "join", "aggregate"])
async def test_a_derivation_that_cannot_produce_its_rows_is_refused(
    database: Database, workspace_id, operation: str
) -> None:
    """Negative, FR-78 (OQ-563, decided 2026-08-17): refusing beats succeeding.

    Each of these used to return a version that recorded the operation and pointed at the
    parent's blob, so a 1 % sample held 100 % of the rows and said nothing about it. A
    derivation nobody performed cannot be reproduced or defended (FR-73), and the
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


@pytest.mark.req("FR-77")
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


@pytest.mark.req("FR-74")
async def test_a_derived_version_starts_in_draft_and_must_be_validated_itself(
    database: Database, workspace_id
) -> None:
    """FR-74: it inherits schema and rule set, never validity.

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


# -- FR-75/76: lineage -----------------------------------------------------------------------


@pytest.mark.req("FR-75")
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


@pytest.mark.req("FR-75")
async def test_the_models_arm_lists_every_model_on_the_version(
    database: Database, workspace_id
) -> None:
    """`01` §4.9's `models` arm: every Model whose `dataset_version_id` is this
    version, any status, deterministic order. The blast radius FR-53 computes
    does not stop at approval."""
    actor = await _with_role(database, workspace_id, "analyst")
    _, version_id = await _version(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        session.add(
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug="motor-freq-2026",
                status="approved",
                dataset_version_id=version_id,
                spec={"family": "glm", "response": "claim_count"},
                spec_hash=f"v1:sha256:{'0' * 64}",
                fit_result={"fitted": True},
                diagnostics_id=new_uuid7(),
            )
        )
        session.add(
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug="motor-freq-2026",
                status="draft",
                version=2,
                dataset_version_id=version_id,
                spec={"family": "glm", "response": "claim_count"},
                spec_hash=f"v1:sha256:{'1' * 64}",
            )
        )

    async with database.session() as session:
        from app.platform import modelling as modelling_service

        arm = await modelling_service.models_referencing_version(
            session, workspace_id=workspace_id, dataset_version_id=version_id
        )

    assert [(m.slug, m.status) for m in arm] == [
        ("motor-freq-2026", "approved"),
        ("motor-freq-2026", "draft"),
    ]


def test_the_direction_filter_empties_the_excluded_arm(
    api_client: TestClient, workspace_id, principal, actuary, database
) -> None:
    """`01` §4.9: a direction filter empties the arm it excludes rather than omitting
    it — `up` returns `depends_on_this` with four empty arms, `down` returns
    `built_from: null`."""
    loop = asyncio.get_event_loop()
    actor = loop.run_until_complete(_with_role(database, workspace_id, "analyst"))
    _, parent_id = loop.run_until_complete(_version(database, workspace_id, actor))
    child_id = loop.run_until_complete(
        _derive_child(database, workspace_id, actor, parent_id)
    )

    up = api_client.get(
        f"/api/v1/dataset-versions/{child_id}/lineage?direction=up", headers=actuary
    ).json()
    assert up["built_from"]["parent_version_id"] == str(parent_id)
    assert up["depends_on_this"] == {
        "derived_versions": [],
        "models": [],
        "rating_versions": [],
        "monitoring_baselines": [],
    }

    down = api_client.get(
        f"/api/v1/dataset-versions/{child_id}/lineage?direction=down", headers=actuary
    ).json()
    assert down["built_from"] is None
    assert down["depends_on_this"]["derived_versions"] == []

    both = api_client.get(
        f"/api/v1/dataset-versions/{child_id}/lineage", headers=actuary
    ).json()
    assert both["built_from"]["parent_version_id"] == str(parent_id)
    assert [d["version_id"] for d in both["depends_on_this"]["derived_versions"]] == []
    assert both["depends_on_this"]["models"] == []


# -- FR-79/80/81: access, archival, erasure --------------------------------------


@pytest.mark.req("FR-79")
async def test_reading_a_dataset_requires_access(
    database: Database, workspace_id
) -> None:
    """FR-79: a user without read access cannot see it — not in lineage either."""
    stranger = Principal(kind=ActorKind.USER, id=new_uuid7(), display="x")
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await datasets.create_dataset(
                session, workspace_id=workspace_id, actor=stranger, slug="secret"
            )
    assert exc.value.code == "PERMISSION_DENIED"


@pytest.mark.req("FR-80")
async def test_an_archived_version_stays_readable_and_referenceable(
    database: Database, workspace_id
) -> None:
    """FR-80: archived versions remain readable and referenceable by existing Models.

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


@pytest.mark.req("FR-80")
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


@pytest.mark.req("FR-81")
async def test_a_subject_purge_is_admin_only_and_recorded(
    database: Database, workspace_id
) -> None:
    """FR-81: the purge is recorded even though the data is gone — especially because
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


@pytest.mark.req("FR-81")
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


# -- FR-72: loaders, and the licence rule OQ-561 settled --------------------------------

# RL-949 (`docs/rulings/RL-00949-rfc-897-slice-2-s-census-csv-and-fr-72-the-test-is-overbroad-the.md`) §3: a second,
# conditional carve-out for a generated repository self-census, alongside
# `licensed_vendored_skill` below. It is a closed, explicit registry of
# (generator script, filename pattern the generator owns) — a filename match makes a file a
# *candidate* only; it never itself grants the exemption (§3 point 1 and point 4). Everything
# unregistered still goes through the unmodified whole-tree sweep.
GENERATED_CORPUS_REGISTRY: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "scripts/file-census.py",
        re.compile(r"^docs/audit/file-census-(?P<sha>[0-9a-f]{7,40})\.csv$"),
    ),
)

# The header `scripts/file-census.py` writes (plan §7 Interfaces). Checked verbatim, not
# inferred, so a header drift is itself caught rather than silently tolerated.
CENSUS_CSV_HEADER = "path,area,name_pattern,size_bytes,mutability,referenced_by"


def resolve_commit(root: pathlib.Path, sha: str) -> str | None:
    """Resolve `sha` to a commit reachable from `root`'s git history.

    RL-949 §3 point 2: tries local resolution first, then a shallow
    `git fetch --depth 1 origin <sha>` and retries against `FETCH_HEAD` — the shape
    `.github/workflows/python.yml`'s undeclared (so depth-1) `actions/checkout@v4` needs.
    Returns `None`, never raises, when both attempts fail; the caller decides what that
    means (§3 point 2's last bullet: never a silent exemption).
    """

    def _verify(ref: str) -> str | None:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--quiet", "--verify", f"{ref}^{{commit}}"],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode != 0:
            return None
        resolved = proc.stdout.strip()
        return resolved or None

    resolved = _verify(sha)
    if resolved is not None:
        return resolved

    fetch = subprocess.run(
        ["git", "-C", str(root), "fetch", "--depth", "1", "origin", sha],
        capture_output=True, text=True, check=False,
    )
    if fetch.returncode != 0:
        return None
    return _verify("FETCH_HEAD")


def generated_from_tracked_corpus(path: pathlib.Path, root: pathlib.Path) -> bool:
    """RL-949 §3's `generated_from_tracked_corpus` carve-out predicate.

    Returns `False` — not exempted, falls through to the unmodified whole-tree sweep — when
    `path` does not match a registered pattern, when its header does not match
    `CENSUS_CSV_HEADER` exactly, or when its sorted `path` column does not exactly equal the
    named commit's `git ls-tree -r --name-only` output, sorted (full-list equality, not a
    set — §3 point 2's second-to-last bullet: a set would hide a duplicated or dropped row).

    Raises `AssertionError`, naming the file and the unresolved SHA, when a candidate names a
    commit that cannot be resolved even after the fetch attempt in `resolve_commit`. A
    carve-out satisfied by "cannot verify, so allow it" is exactly the failure class this
    repository keeps re-finding (§3 point 2's last bullet) — this refuses that fallback by
    raising rather than by discipline.
    """
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return False

    sha: str | None = None
    for _generator, pattern in GENERATED_CORPUS_REGISTRY:
        match = pattern.match(rel)
        if match is not None:
            sha = match.group("sha")
            break
    if sha is None:
        return False  # not a registered candidate — §3 point 1

    commit = resolve_commit(root, sha)
    if commit is None:
        raise AssertionError(
            f"{rel}: names commit {sha!r} as the tree it documents, but that commit could "
            "not be resolved (local resolution and `git fetch --depth 1 origin <sha>` both "
            "failed) — refusing to exempt a file whose provenance cannot be verified "
            "(RL-949 §3 point 2)"
        )

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    lines = text.splitlines()
    if not lines or lines[0] != CENSUS_CSV_HEADER:
        return False  # header mismatch — not exempted (§3 point 3)

    csv_paths = sorted(row[0] for row in csv.reader(lines[1:]) if row)

    tree = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-r", "--name-only", commit],
        capture_output=True, text=True, check=True,
    )
    tree_paths = sorted(line for line in tree.stdout.splitlines() if line)

    return csv_paths == tree_paths


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


@pytest.mark.req("FR-72")
def test_loaders_ship_for_every_reference_set_the_requirement_names() -> None:
    from app.data.reference_loaders import LOADERS

    assert {"ons-postcode-directory", "abi-vehicle-groups", "soc-occupation-codes",
            "uk-bank-holidays"} <= set(LOADERS)


@pytest.mark.req("FR-72")
def test_abi_vehicle_group_data_is_never_shippable() -> None:
    """OQ-561, decided 2026-08-14. The negative test that keeps the decision true.

    ABI group tables are not freely redistributable; bundling them would put a licence
    breach in every clone of this repository. The loader ships, the rows never do.
    """
    from app.data.reference_loaders import Licence, loader_for, shippable_loaders

    abi = loader_for("abi-vehicle-groups")
    assert abi.licence is Licence.PROPRIETARY
    assert abi.may_ship_data is False
    assert abi not in shippable_loaders()
    assert "NOT REDISTRIBUTABLE" in abi.fetch_note


@pytest.mark.req("FR-72")
def test_only_ogl_sources_may_ship_their_rows() -> None:
    from app.data.reference_loaders import Licence, shippable_loaders

    assert all(loader.licence is Licence.OGL for loader in shippable_loaders())


@pytest.mark.req("FR-72")
def test_no_reference_rows_are_bundled_in_the_repository() -> None:
    """The decision, checked against the tree rather than against intent.

    A loader is a parser plus a documented fetch step. If a data file ever appears here,
    somebody has shipped rows — and this is the test that says so before a licence holder
    does.

    Two carve-outs, both conditional rather than blanket. Vendored skills under
    `.claude/skills/` are the first: `ui-ux-pro-max` (2026-08-17) is the first vendored
    skill to ship data files — 18 CSVs of font, colour and UX guidance — and FR-72 is
    about UK *reference* sets whose rows are not ours to redistribute, not about a
    third-party payload committed under its own licence. So the exemption is bought by that
    licence: a skill may carry data only while its LICENSE travels with it in the same
    directory, which is precisely the exposure this test exists to prevent. Delete the
    licence and this fails, which is the point.

    The second is `generated_from_tracked_corpus` (RL-949,
    `docs/rulings/RL-00949-rfc-897-slice-2-s-census-csv-and-fr-72-the-test-is-overbroad-the.md`) — a closed registry of
    generated repository self-census artifacts, bought by provable reproducibility against
    the tree their own filename names, never by location or filename alone. Delete a row
    from the census, or point it at a tree it does not match, and this fails too.
    """
    root = pathlib.Path(__file__).resolve().parents[2]

    data_files = [
        path
        for pattern in ("*.csv", "*.parquet", "*.xlsx")
        for path in root.rglob(pattern)
        if ".venv" not in path.parts
        and ".git" not in path.parts
        and not licensed_vendored_skill(path)
        and not generated_from_tracked_corpus(path, root)
    ]
    assert data_files == [], f"unexpected bundled data: {data_files}"


# -- FR-76: splits recorded on the parent ----------------------------------------


@pytest.mark.req("FR-76")
async def test_a_split_is_recorded_on_the_parent_so_two_models_can_be_compared(
    database: Database, workspace_id
) -> None:
    """FR-76: "trained on the same split" becomes a single reference both models cite,
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


@pytest.mark.req("FR-76")
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


@pytest.mark.req("FR-76")
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
