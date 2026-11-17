"""Reconciling approved-state artifacts against the audit chain (`06` FR-2163).

The first half needs no database: each rule is shown red on a planted mismatch and green on
the reconciled set it was planted into. The DB-backed half (below the marker comment) plants
the same states through an owner connection and runs the real decision route; it is run in a
database window.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Database
from app.platform import reconcile as rc
from app.platform.reconcile import (
    ArtifactState,
    DecisionState,
    DeploymentState,
    EventState,
    RequestState,
    WorkspaceData,
    approved_or_later,
    approved_states,
    reconcile_data,
)
from model_schema import ArtifactRef, Principal

T0 = datetime(2026, 1, 1, tzinfo=UTC)
REF = "rating_version:motor@1"
SUBMITTER, APPROVER, OTHER = uuid4(), uuid4(), uuid4()
REQUEST_ID, DECISION_ID = uuid4(), uuid4()
DEPLOYMENT_ID = uuid4()


def _t(minutes: int) -> datetime:
    return T0 + timedelta(minutes=minutes)


def _reconciled() -> WorkspaceData:
    """One approved Rating Version through the decision path, as the platform writes it."""
    return WorkspaceData(
        artifacts=(ArtifactState("rating_versions", REF, "rating_version", "approved"),),
        requests=(
            RequestState(REQUEST_ID, REF, "rating_version", "approved", SUBMITTER, 1, _t(1)),
        ),
        decisions=(DecisionState(DECISION_ID, REQUEST_ID, APPROVER, "approve", _t(2)),),
        events=(
            EventState(1, _t(1), "approval_request.submitted", REF, SUBMITTER),
            EventState(
                2,
                _t(2),
                "approval_request.approve",
                REF,
                APPROVER,
                {"approval_request_id": str(REQUEST_ID), "decision_id": str(DECISION_ID)},
            ),
            EventState(3, _t(2), "rating_version.approved", REF, APPROVER),
        ),
    )


def _with_deployment(data: WorkspaceData, **kw: object) -> WorkspaceData:
    deployment = DeploymentState(DEPLOYMENT_ID, REF)
    deployment = replace(deployment, **kw)  # type: ignore[arg-type]
    created = EventState(
        4, _t(3), "deployment.created", "environment:uat", SUBMITTER, {"id": str(DEPLOYMENT_ID)}
    )
    return replace(data, deployments=(deployment,), events=(*data.events, created))


def _rules(mismatches: list[rc.Mismatch]) -> list[str]:
    return [m.rule for m in mismatches]


def test_a_reconciled_workspace_has_no_mismatch() -> None:
    assert reconcile_data(_reconciled()) == []
    assert reconcile_data(_with_deployment(_reconciled())) == []


# -- R1 ---------------------------------------------------------------------------------------


def test_r1_an_approved_artifact_without_an_approved_request() -> None:
    data = replace(_reconciled(), requests=(), decisions=(), events=())
    found = reconcile_data(data)
    assert _rules(found) == ["R1"], found
    assert found[0].ref == REF


def test_r1_a_request_that_is_not_approved_does_not_cover_the_artifact() -> None:
    data = _reconciled()
    data = replace(data, requests=(replace(data.requests[0], status="review"),))
    assert "R1" in _rules(reconcile_data(data))


def test_r1_covers_a_state_reachable_only_through_approval() -> None:
    superseded = WorkspaceData(
        artifacts=(ArtifactState("models", "model:m@1", "model", "superseded"),)
    )
    assert _rules(reconcile_data(superseded)) == ["R1"]
    archived = WorkspaceData(artifacts=(ArtifactState("models", "model:m@1", "model", "archived"),))
    assert reconcile_data(archived) == [], "archived is reachable from draft: not an approved state"


def test_r1_a_status_the_product_does_not_write_is_reported_whatever_requests_exist() -> None:
    data = _reconciled()
    live = ArtifactState("rating_versions", REF, "rating_version", "live")
    found = reconcile_data(replace(data, artifacts=(live,)))
    assert _rules(found) == ["R1"], found
    assert "does not write" in found[0].detail


def test_unwritten_states_are_derived_by_reachability() -> None:
    assert rc.unwritten_states("rating_version") == {"live", "retired"}
    assert rc.unwritten_states("model") == set()
    assert rc.unwritten_states("deployment") == set()


def test_approved_or_later_is_derived_from_the_lifecycle_graph() -> None:
    graph = {"a": {"b"}, "b": {"approved", "x"}, "approved": {"z"}, "z": set(), "x": set()}
    assert approved_or_later("a", graph) == {"approved", "z"}
    assert approved_states("model") == {"approved", "superseded"}
    assert approved_states("deployment") == {"approved", "executed"}


# -- R2 ---------------------------------------------------------------------------------------


def test_r2_an_approved_request_with_no_decisions() -> None:
    data = replace(
        _reconciled(), decisions=(), events=_reconciled().events[:1] + _reconciled().events[2:]
    )
    assert _rules(reconcile_data(data)) == ["R2"]


def test_r2_the_submitter_cannot_be_the_approver() -> None:
    data = _reconciled()
    data = replace(
        data,
        decisions=(replace(data.decisions[0], approver_id=SUBMITTER),),
        events=(data.events[0], replace(data.events[1], actor_id=SUBMITTER), data.events[2]),
    )
    found = reconcile_data(data)
    assert _rules(found) == ["R2"], found
    assert "submitter" in found[0].detail


def test_r2_fewer_distinct_approvers_than_required() -> None:
    data = _reconciled()
    data = replace(data, requests=(replace(data.requests[0], approvers_required=2),))
    assert _rules(reconcile_data(data)) == ["R2"]


# -- R3 ---------------------------------------------------------------------------------------


def test_r3_a_decision_row_without_its_event() -> None:
    data = _reconciled()
    data = replace(data, events=(data.events[0], data.events[2]))
    found = reconcile_data(data)
    assert "R3" in _rules(found), found


def test_r3_an_event_without_its_decision_row() -> None:
    data = _reconciled()
    unmatched = EventState(4, _t(3), "approval_request.approve", REF, OTHER, None)
    found = reconcile_data(replace(data, events=(*data.events, unmatched)))
    assert _rules(found) == ["R3"], found
    assert "no decision row" in found[0].detail


def test_r3_an_event_naming_another_request() -> None:
    data = _reconciled()
    wrong = replace(
        data.events[1], after={"approval_request_id": str(uuid4()), "decision_id": str(DECISION_ID)}
    )
    found = reconcile_data(replace(data, events=(data.events[0], wrong, data.events[2])))
    assert _rules(found) == ["R3"], found


def test_r3_an_earlier_event_matches_by_entity_actor_and_decision() -> None:
    data = _reconciled()
    legacy = replace(data.events[1], after={"status": "approved", "approvers_recorded": 1})
    found = reconcile_data(replace(data, events=(data.events[0], legacy, data.events[2])))
    assert [m.rule for m in found] == [], found


# -- R4 ---------------------------------------------------------------------------------------


def test_r4_a_decision_event_before_the_submitted_event() -> None:
    data = _reconciled()
    submitted = replace(data.events[0], sequence=5)
    found = reconcile_data(replace(data, events=(submitted, data.events[1], data.events[2])))
    assert _rules(found) == ["R4"], found
    assert "precedes every submitted" in found[0].detail


def test_r4_an_approval_event_before_the_last_decision_event() -> None:
    data = _reconciled()
    early = replace(data.events[2], sequence=1)
    submitted = replace(data.events[0], sequence=0)
    found = reconcile_data(replace(data, events=(submitted, early, data.events[1])))
    assert _rules(found) == ["R4"], found


def test_r4_the_approval_event_exists_exactly_once() -> None:
    data = _reconciled()
    twice = replace(data.events[2], sequence=4)
    assert _rules(reconcile_data(replace(data, events=(*data.events, twice)))) == ["R4"]
    assert _rules(reconcile_data(replace(data, events=data.events[:2]))) == ["R4"]


# -- R5 ---------------------------------------------------------------------------------------


def test_r5_a_deployment_of_a_version_that_does_not_reconcile_is_reported_first() -> None:
    data = _with_deployment(replace(_reconciled(), requests=(), decisions=()))
    found = reconcile_data(data)
    assert found[0].rule == "R5", found
    assert "does not reconcile" in found[0].detail


def test_r5_a_deployment_without_its_creation_event() -> None:
    data = _with_deployment(_reconciled())
    data = replace(data, events=data.events[:-1])
    found = reconcile_data(data)
    assert _rules(found) == ["R5"], found
    assert "deployment.created" in found[0].detail


def test_r5_a_deployment_of_a_version_that_is_not_stored() -> None:
    data = _with_deployment(_reconciled(), rating_version_ref="rating_version:ghost@9")
    assert _rules(reconcile_data(data)) == ["R5"]


def test_r5_a_deployment_request_must_be_executed() -> None:
    data = _with_deployment(_reconciled(), request_ref="deployment:d@1", request_status="approved")
    found = reconcile_data(data)
    assert _rules(found) == ["R5"], found
    assert "'executed'" in found[0].detail


# -- legacy marking (D2) ----------------------------------------------------------------------


def _legacy_pair(ref: str, event_sequence: int, event_at: datetime) -> WorkspaceData:
    """The reconciled workspace plus one approved artifact with no approved request, and the
    one chain event that names it, at the given sequence and claimed time."""
    base = _reconciled()
    artifact = ArtifactState("rating_versions", ref, "rating_version", "approved")
    event = EventState(event_sequence, event_at, "rating_version.created", ref, SUBMITTER)
    return replace(base, artifacts=(*base.artifacts, artifact), events=(*base.events, event))


def test_a_mismatch_before_the_first_id_event_in_the_chain_is_marked_legacy_but_reported() -> None:
    found = reconcile_data(_legacy_pair("rating_version:old@1", 0, _t(-100)))
    assert [(m.rule, m.ref, m.legacy) for m in found] == [("R1", "rating_version:old@1", True)]


def test_a_mismatch_after_the_first_id_event_in_the_chain_is_not_legacy() -> None:
    found = reconcile_data(_legacy_pair("rating_version:new@1", 10, _t(50)))
    assert [(m.rule, m.legacy) for m in found] == [("R1", False)]


def test_a_back_dated_event_placed_after_the_first_id_event_is_not_legacy() -> None:
    """The time is the writer's choice: an event claiming a time long before the first id event,
    but sitting after it in the chain, must not make its mismatch legacy."""
    found = reconcile_data(_legacy_pair("rating_version:late@1", 10, _t(-1000)))
    assert [(m.rule, m.legacy) for m in found] == [("R1", False)]


def test_a_mismatch_with_no_chain_evidence_is_not_legacy() -> None:
    base = _reconciled()
    bare = ArtifactState("rating_versions", "rating_version:bare@1", "rating_version", "approved")
    found = reconcile_data(replace(base, artifacts=(*base.artifacts, bare)))
    assert [(m.rule, m.legacy) for m in found] == [("R1", False)]


# -- census (DB-free half): the covered tables are the ones the guard migration installs -----


def test_census_covered_tables_equal_the_guard_migration_tables_plus_deployment_requests() -> None:
    import importlib.util
    from pathlib import Path

    path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "a9f3c6d21b87_approval_guard.py"
    )
    spec = importlib.util.spec_from_file_location("guard_migration", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    guarded = set(module.GUARDED_TABLES) - {"approval_requests"}
    assert set(rc.COVERED_TABLES) == guarded | {"deployment_requests"}
    assert {t for t, *_ in rc.COVERED_TABLES.values()} <= set(rc.STATE_GRAPHS)


def test_census_every_covered_type_has_a_derivable_approved_state() -> None:
    for table, (artifact_type, *_rest) in rc.COVERED_TABLES.items():
        assert "approved" in approved_states(artifact_type), table


# -- DB-backed: run in the slice's database window, not in the DB-free run above ---------------
#
# test_reconcile_db_census_covered_tables_equal_installed_approval_guard_triggers
# test_reconcile_db_the_decision_event_carries_both_ids
# test_reconcile_db_the_decision_route_reconciles_clean
# test_reconcile_db_a_planted_approved_request_without_decisions_is_reported
# test_reconcile_db_a_broken_chain_stops_the_rules


async def _decide_once(
    database: Database, workspace_id: UUID
) -> tuple[UUID, Principal, ArtifactRef]:
    """Submit and approve one model version through the approval service, as the platform
    does, and record the artifact's approval event the owning module writes after it."""
    from backend.tests.test_approvals import (
        _no_evidence_authors,
        _submit,
        _user,
        _with_role,
    )

    from app.platform import approvals, audit
    from model_schema import ArtifactRef, DecisionKind, JobSource

    ref = ArtifactRef.parse("model:motor-ad-frequency@7")
    submitter, approver = _user("s"), _user("a")
    await _with_role(database, workspace_id, approver, "approver")
    request_id = await _submit(database, workspace_id, submitter, ref=ref)
    async with database.unit_of_work() as session:
        await approvals.decide(
            session,
            evidence_authors=_no_evidence_authors,
            workspace_id=workspace_id,
            request_id=request_id,
            approver=approver,
            decision=DecisionKind.APPROVE,
            comment="clean",
        )
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=approver,
            source=JobSource.API,
            action="model.approved",
            entity_ref=str(ref),
        )
    return request_id, approver, ref


async def test_reconcile_db_census_covered_tables_equal_installed_approval_guard_triggers(
    database: Database,
) -> None:
    from sqlalchemy import text

    async with database.session() as session:
        installed = {
            row[0]
            for row in await session.execute(
                text(
                    "SELECT c.relname FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid "
                    "WHERE t.tgname = 'approval_guard' AND NOT t.tgisinternal"
                )
            )
        }
    assert set(rc.COVERED_TABLES) | {"approval_requests"} == installed


async def test_reconcile_db_the_decision_event_carries_both_ids(
    database: Database, workspace_id: UUID
) -> None:
    from sqlalchemy import select

    from app.db.models import ApprovalDecisionRow, AuditEventRow

    request_id, _approver, _ref = await _decide_once(database, workspace_id)
    async with database.session() as session:
        decision = (
            await session.execute(
                select(ApprovalDecisionRow).where(ApprovalDecisionRow.request_id == request_id)
            )
        ).scalar_one()
        event = (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "approval_request.approve",
                )
            )
        ).scalar_one()
    assert (event.after or {}).get("approval_request_id") == str(request_id)
    assert (event.after or {}).get("decision_id") == str(decision.id)


async def test_reconcile_db_the_decision_route_reconciles_clean(
    database: Database, workspace_id: UUID
) -> None:
    await _decide_once(database, workspace_id)
    async with database.session() as session:
        report = await rc.reconcile(session, workspace_id)
    assert report.chain == "intact"
    assert report.requests_checked == 1
    assert report.mismatches == ()


async def test_reconcile_db_a_planted_approved_request_without_decisions_is_reported(
    database: Database, workspace_id: UUID
) -> None:
    """The planted state: an approved request with no decision rows and no events, written the
    governed way: the decided-request fixture of `approved_rows` under `approval_decision()`,
    through the owner seam. No trigger is disabled and no superuser is assumed."""
    from backend.tests.approved_rows import decided_request
    from backend.tests.conftest_db import seed_as_owner

    async def _plant(session: AsyncSession) -> None:
        await decided_request(
            session, workspace_id=workspace_id, artifact_type="model", slug="planted", version=1
        )

    await seed_as_owner(_plant)
    async with database.session() as session:
        report = await rc.reconcile(session, workspace_id)
    assert report.chain == "intact"
    assert "R2" in {m.rule for m in report.mismatches}


async def test_reconcile_db_a_broken_chain_stops_the_rules(
    database: Database, workspace_id: UUID
) -> None:
    from backend.tests.conftest_db import seed_as_owner
    from sqlalchemy import text

    await _decide_once(database, workspace_id)

    async def _tamper(session: AsyncSession) -> None:
        # An UPDATE of an audit row is refused for the owner too, so the chain is broken by an
        # append the owner may make: one more event whose stored hash is not its content's.
        await session.execute(
            text(
                "INSERT INTO audit_events (id, workspace_id, at, actor, source, action, "
                "entity_ref, before, after, justification, trace_id, job_id, "
                "prev_event_hash, event_hash, sequence) "
                "SELECT gen_random_uuid(), workspace_id, at, actor, source, action, "
                "entity_ref, before, after, justification, trace_id, job_id, "
                "event_hash, 'sha256:' || repeat('0', 64), sequence + 1 "
                "FROM audit_events WHERE workspace_id = :w ORDER BY sequence DESC LIMIT 1"
            ),
            {"w": workspace_id},
        )

    await seed_as_owner(_tamper)
    async with database.session() as session:
        report = await rc.reconcile(session, workspace_id)
    assert report.chain == "broken"
    assert report.mismatches == ()


pytestmark = pytest.mark.req("FR-2163")
