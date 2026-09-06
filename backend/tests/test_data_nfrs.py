"""The `01` non-functional requirements that are assertions rather than timings.

NFR-465/466/467 are throughput budgets and are *measured* rather than tested — a timing
assertion in CI fails on a busy runner and teaches everyone to re-run it, which is worse
than no check. Their measurements are recorded in the WK-660 closure evidence.
"""

from __future__ import annotations

import polars as pl
import pytest
from sqlalchemy import select

from app.data.ingestion import ingest_upload
from app.db.models import AuditEventRow, DatasetVersionRow, RoleAssignmentRow, RoleRow
from app.db.session import Database
from app.platform import datasets, rbac
from app.platform.blobs import BlobStore
from model_schema import ActorKind, DatasetStatus, Principal, ScopeType, new_uuid7

CSV = b"Policy ID,Exposure Years\nP1,1.0\nP2,0.5\n"


async def _analyst(database: Database, workspace_id) -> Principal:
    user = Principal(kind=ActorKind.USER, id=new_uuid7(), display="a@insurer.example")
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
                workspace_id=workspace_id, principal_kind="user", principal_id=user.id,
                role_id=role.id, scope_type=ScopeType.WORKSPACE.value,
            )
        )
    return user


@pytest.mark.req("NFR-469")
def test_validation_is_deterministic() -> None:
    """NFR-469: the same version and rule set version produce byte-identical report
    bodies apart from timestamps and ids.

    Determinism is what makes a report evidence. If two runs over identical data could
    disagree, a disputed failure would be settled by whoever re-ran it last.

    **Several rules, in a deliberate order.** The fixture used to hold one, so the single
    dimension a report body realistically drifts in — the order results come back in —
    could not vary, and randomising `run_validation`'s output left the whole suite green.
    """
    from uuid import uuid4

    from model_schema import (
        RuleSetEntry,
        Severity,
        ValidationLayer,
        ValidationRule,
        ValidationRuleSet,
    )
    from pricing_core.data.validate import run_validation

    frame = pl.DataFrame(
        {
            "policy_id": ["P1", "P2", "P3"],
            "exposure_years": [1.0, -0.5, 0.5],
            "driv_age": [40, 17, None],
        }
    )

    def rule(slug: str, layer: ValidationLayer, check: str, **params: object) -> ValidationRule:
        return ValidationRule(
            id=uuid4(), slug=slug, version=1, layer=layer, check=check,
            severity=Severity.FAIL if layer is ValidationLayer.STRUCTURAL else Severity.WARN,
            target={"table": "t", "column": params.pop("column", "exposure_years")},
            params={"key_columns": ["policy_id"], **params},
        )

    rules = (
        rule("exposure-positive", ValidationLayer.ACTUARIAL_SANITY, "range", min_exclusive=0),
        rule("driver-age-range", ValidationLayer.ACTUARIAL_SANITY, "range",
             column="driv_age", min_inclusive=18),
        rule("policy-id-present", ValidationLayer.STRUCTURAL, "not_null", column="policy_id"),
        rule("driver-age-present", ValidationLayer.STRUCTURAL, "not_null", column="driv_age"),
    )
    rule_set = ValidationRuleSet(
        id=uuid4(), slug="s", version=1,
        entries=tuple(RuleSetEntry(rule=r) for r in rules),
    )
    version_id = uuid4()

    def body(report) -> str:
        return report.model_dump_json(exclude={"id", "started_at", "finished_at"})

    first = run_validation({"t": frame}, rule_set, dataset_version_id=version_id)
    second = run_validation({"t": frame}, rule_set, dataset_version_id=version_id)
    assert body(first) == body(second)

    # The order itself, asserted rather than implied: results follow the rule set's own
    # order, so a reader comparing two reports side by side is comparing like with like.
    assert len(first.results) == len(rules)
    assert [r.rule_slug for r in first.results] == [r.slug for r in rules]
    assert [r.rule_slug for r in second.results] == [r.slug for r in rules]


@pytest.mark.req("NFR-470")
async def test_identical_tables_across_versions_are_stored_once(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """NFR-470: identical tables across versions are deduplicated by content hash.

    Two versions of a dataset usually share most of their tables — a re-ingest that only
    corrects the claims file should not double the storage of the exposure file. Content
    addressing (ID-4) gives this for free, and this is the test that says it still does.
    """
    actor = await _analyst(database, workspace_id)
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        dataset_id = dataset.id

    refs = []
    for _ in range(2):
        async with database.unit_of_work() as session:
            outcome = await ingest_upload(
                session, blob_store, workspace_id=workspace_id, actor=actor,
                dataset_id=dataset_id, data=CSV, filename="exposure.csv",
            )
            refs.append(outcome.version.tables[0]["blob"]["sha256"])

    assert refs[0] == refs[1], "identical content produced two blobs"

    from app.db.models import BlobRow

    async with database.session() as session:
        rows = (
            await session.execute(select(BlobRow).where(BlobRow.sha256 == refs[0]))
        ).scalars().all()
    assert len(rows) == 1


@pytest.mark.req("NFR-472")
async def test_every_dataset_transition_emits_an_audit_event_with_before_and_after(
    database: Database, workspace_id
) -> None:
    """NFR-472: transitions, acknowledgements, dictionary edits, rule-set changes and
    purges each emit an Audit Event with before and after state."""
    actor = await _analyst(database, workspace_id)
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        version = await datasets.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset.id
        )
        version_id = version.id
    async with database.unit_of_work() as session:
        await datasets.transition(
            session, workspace_id=workspace_id, actor=actor, version_id=version_id,
            to_status=DatasetStatus.VALIDATING,
        )

    async with database.session() as session:
        events = (
            await session.execute(
                select(AuditEventRow)
                .where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "dataset_version.validating",
                )
            )
        ).scalars().all()
    assert len(events) == 1
    assert events[0].before == {"status": "draft"}
    assert events[0].after["status"] == "validating"


@pytest.mark.req("NFR-474")
async def test_a_failed_ingestion_leaves_no_partially_visible_version(
    database: Database, blob_store: BlobStore, workspace_id
) -> None:
    """NFR-474: version rows become visible only on successful commit.

    A half-written version is worse than none: it looks like a dataset, and the first thing
    anyone does with a dataset is fit on it. The unit of work is what makes this true —
    the version, its tables and its ingestion run commit together or not at all.
    """
    actor = await _analyst(database, workspace_id)
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        dataset_id = dataset.id

    # PT012: the failure has to happen after the ingestion, inside the transaction.
    with pytest.raises(RuntimeError, match="deliberate"):  # noqa: PT012
        async with database.unit_of_work() as session:
            await ingest_upload(
                session, blob_store, workspace_id=workspace_id, actor=actor,
                dataset_id=dataset_id, data=CSV, filename="exposure.csv",
            )
            raise RuntimeError("deliberate failure after the version was built")

    async with database.session() as session:
        versions = (
            await session.execute(
                select(DatasetVersionRow).where(
                    DatasetVersionRow.dataset_id == dataset_id
                )
            )
        ).scalars().all()
    assert versions == []


@pytest.mark.req("NFR-468")
def test_a_one_way_is_read_from_the_profile_not_recomputed() -> None:
    """NFR-468: a one-way read from a stored Profile is never computed on request.

    Asserted structurally — the summaries are a field on the artifact, so reading one is a
    lookup rather than a scan. A property that recomputed would meet the latency budget
    today on a small dataset and miss it on a real one, which is the failure this rules out.
    """
    from uuid import uuid4

    from pricing_core.data.profile import profile_frame

    frame = pl.DataFrame(
        {"vehicle_group": ["G1", "G2"] * 50, "exposure_years": [1.0] * 100,
         "claim_count": [1, 0] * 50, "claim_amount_minor": [100_000, 0] * 50}
    )
    profile = profile_frame(
        frame, dataset_version_id=uuid4(), one_way_columns=["vehicle_group"]
    )
    stored = profile.model_dump_json()

    from model_schema import Profile

    reloaded = Profile.model_validate_json(stored)
    assert reloaded.one_ways[0].column == "vehicle_group"
    assert len(reloaded.one_ways[0].rows) == 2
    assert reloaded.one_ways[0].rows[0].frequency is not None
