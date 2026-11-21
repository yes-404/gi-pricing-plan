"""Reconciling approved-state artifacts against the audit chain (`06` FR-2163).

The first half needs no database: each rule is shown red on a planted mismatch and green on
the reconciled set it was planted into. The DB-backed half (below the marker comment) plants
the same states through an owner connection and runs the real decision route; it is run in a
database window.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
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


# -- R3: an id match compares the event to its decision row (S1) -----------------------------


def _event_with(**changes: object) -> WorkspaceData:
    data = _reconciled()
    return replace(
        data, events=(data.events[0], replace(data.events[1], **changes), data.events[2])
    )


def test_r3_an_event_with_the_decision_id_but_another_actor() -> None:
    found = reconcile_data(_event_with(actor_id=OTHER))
    assert "R3" in _rules(found), found
    assert "actor" in " ".join(m.detail for m in found)


def test_r3_an_event_with_the_decision_id_but_another_action() -> None:
    found = reconcile_data(_event_with(action="approval_request.reject"))
    assert "R3" in _rules(found), found
    assert "action" in " ".join(m.detail for m in found)


def test_r3_an_event_with_the_decision_id_but_another_entity_ref() -> None:
    found = reconcile_data(_event_with(entity_ref="rating_version:elsewhere@1"))
    assert "R3" in _rules(found), found
    assert "entity" in " ".join(m.detail for m in found)


# -- a malformed event does not end the run (S3) ----------------------------------------------


def _validation_error() -> Exception:
    try:
        Principal.model_validate({})
    except ValueError as exc:  # pydantic's ValidationError is a ValueError
        return exc
    raise AssertionError("an empty principal validated")


async def test_a_workspace_whose_chain_cannot_be_read_is_reported_unreadable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _raises(*_a: object, **_k: object) -> int:
        raise _validation_error()

    monkeypatch.setattr(rc.audit, "verify_chain", _raises)
    report = await rc.reconcile(None, uuid4())  # type: ignore[arg-type]
    assert report.chain == "unreadable"
    assert report.mismatches == ()
    assert report.chain_detail


async def test_a_workspace_with_a_malformed_event_body_is_reported_unreadable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _verified(*_a: object, **_k: object) -> int:
        return 3

    async def _load(*_a: object, **_k: object) -> WorkspaceData:
        data = _reconciled()
        bad = replace(data.events[1], after=["not", "an", "object"])  # type: ignore[arg-type]
        return replace(data, events=(data.events[0], bad, data.events[2]))

    monkeypatch.setattr(rc.audit, "verify_chain", _verified)
    monkeypatch.setattr(rc, "load_workspace_data", _load)
    report = await rc.reconcile(None, uuid4())  # type: ignore[arg-type]
    assert report.chain == "unreadable"
    assert report.mismatches == ()


@pytest.mark.parametrize("stage", ["verify_chain", "load_workspace_data"])
@pytest.mark.parametrize(
    "error",
    [ConnectionError("connection lost"), SQLAlchemyError("statement failed")],
    ids=["os-error", "sqlalchemy-error"],
)
async def test_a_database_error_aborts_the_run_and_is_not_read_as_an_unreadable_workspace(
    monkeypatch: pytest.MonkeyPatch, stage: str, error: Exception
) -> None:
    async def _raises(*_a: object, **_k: object) -> int:
        raise error

    async def _verified(*_a: object, **_k: object) -> int:
        return 3

    if stage == "verify_chain":
        monkeypatch.setattr(rc.audit, "verify_chain", _raises)
    else:
        monkeypatch.setattr(rc.audit, "verify_chain", _verified)
        monkeypatch.setattr(rc, "load_workspace_data", _raises)
    with pytest.raises(type(error)) as caught:
        await rc.reconcile(None, uuid4())  # type: ignore[arg-type]
    assert caught.value is error


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


@pytest.mark.parametrize("status", ["draft", "review"])
def test_r5_a_deployment_of_a_version_that_is_not_approved_is_reported(status: str) -> None:
    """FR-238: only an approved version deploys. A draft or review version has no R1 mismatch
    (R1 reads approved-or-later states only), so R5 must name it on its own."""
    version = ArtifactState("rating_versions", REF, "rating_version", status)
    data = _with_deployment(
        replace(_reconciled(), artifacts=(version,), requests=(), decisions=(), events=())
    )
    found = reconcile_data(data)
    assert [m.rule for m in found] == ["R5"], found
    assert status in found[0].detail
    assert "not approved" in found[0].detail


def test_r1_a_built_in_validation_rule_needs_no_request() -> None:
    """FR-68: the shipped catalogue is seeded `approved` with no request, by design."""
    rule = ArtifactState("validation_rules", "validation_rule:r@1", "validation_rule", "approved")
    assert [m.rule for m in reconcile_data(WorkspaceData(artifacts=(rule,)))] == ["R1"]
    shipped = replace(rule, builtin=True)
    assert reconcile_data(WorkspaceData(artifacts=(shipped,))) == []


def test_r1_a_validation_rule_set_needs_no_request() -> None:
    """PL-1303 Acceptance 7: a rule set is written `approved` with no request."""
    plain = ArtifactState(
        "validation_rule_sets", "validation_rule_set:s@1", "validation_rule_set", "approved"
    )
    assert reconcile_data(WorkspaceData(artifacts=(plain,))) == []


@pytest.mark.parametrize("action", ["deployment.created", "deployment.rolled_back"])
def test_r5_a_deployment_is_recorded_by_its_creation_or_its_rollback_event(action: str) -> None:
    data = _with_deployment(_reconciled())
    event = replace(data.events[-1], action=action)
    assert reconcile_data(replace(data, events=(*data.events[:-1], event))) == []


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


def test_a_workspace_with_no_id_carrying_event_marks_nothing_legacy() -> None:
    """Strict: with no decision event carrying its ids there is no cut-over to place anything
    before, so an invented approval with chain evidence is a plain mismatch, not a legacy one."""
    invented = WorkspaceData(
        artifacts=(ArtifactState("rating_versions", REF, "rating_version", "approved"),),
        requests=(
            RequestState(REQUEST_ID, REF, "rating_version", "approved", SUBMITTER, 1, _t(1)),
        ),
        events=(
            EventState(1, _t(1), "approval_request.submitted", REF, SUBMITTER),
            EventState(2, _t(2), "approval_request.approve", REF, APPROVER, None),
            EventState(3, _t(2), "rating_version.approved", REF, APPROVER),
        ),
    )
    found = reconcile_data(invented)
    assert found, "the invented approval must be reported"
    assert [m.legacy for m in found] == [False] * len(found), found


def test_an_r5_mismatch_is_never_legacy_even_with_chain_evidence_before_the_cut_over() -> None:
    """A deployment created before the cut-over. The shape of today's reference keeps R5 out of
    the chain's entity refs; this plants an event that does name it, so only the explicit skip
    in `_mark_legacy` keeps the mismatch from being marked."""
    version = ArtifactState("rating_versions", REF, "rating_version", "draft")
    data = _with_deployment(
        replace(_reconciled(), artifacts=(version,), requests=(), decisions=(), events=())
    )
    decision = EventState(
        9,
        _t(9),
        "approval_request.approve",
        "model:m@1",
        APPROVER,
        {"approval_request_id": str(uuid4()), "decision_id": str(uuid4())},
    )
    early = EventState(
        0,
        _t(-5),
        "deployment.created",
        f"deployment:{DEPLOYMENT_ID}",
        SUBMITTER,
        {"id": str(DEPLOYMENT_ID)},
    )
    found = [
        m
        for m in reconcile_data(replace(data, events=(early, *data.events, decision)))
        if m.rule == "R5"
    ]
    assert found, "the draft version's deployment must be reported"
    assert [m.legacy for m in found] == [False] * len(found), found


# -- census (DB-free half): the covered tables are the ones the guard migration installs -----


def _guard_migration_tables() -> set[str]:
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
    return set(module.GUARDED_TABLES) - {"approval_requests"} | {"deployment_requests"}


def _census_gap(covered: set[str], guarded: set[str]) -> set[str]:
    """The tables in one set and not the other: empty when the census holds."""
    return covered ^ guarded


def test_census_covered_tables_equal_the_guard_migration_tables_plus_deployment_requests() -> None:
    assert _census_gap(set(rc.COVERED_TABLES), _guard_migration_tables()) == set()
    assert {t for t, *_ in rc.COVERED_TABLES.values()} <= set(rc.STATE_GRAPHS)


def test_census_a_planted_governed_table_without_coverage_fails_it() -> None:
    """The census shown red: a new guarded table the reconcile run does not cover is named."""
    planted = _guard_migration_tables() | {"planted_governed_table"}
    assert _census_gap(set(rc.COVERED_TABLES), planted) == {"planted_governed_table"}
    dropped = set(rc.COVERED_TABLES) - {"models"}
    assert _census_gap(dropped, _guard_migration_tables()) == {"models"}


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
# test_reconcile_db_a_planted_live_rating_version_is_a_status_the_product_does_not_write (R1)
# test_reconcile_db_a_planted_stray_decision_event_is_reported (R3)
# test_reconcile_db_a_planted_second_approval_event_is_reported (R4)
# test_reconcile_db_a_planted_deployment_of_a_draft_version_is_reported (R5)
# (R2 is the planted request test above; each is planted, then run, red before and green on
# the route-written state of `the_decision_route_reconciles_clean`. Written for batch 2.)


async def _decide_to_approval(
    database: Database, workspace_id: UUID, ref_text: str = "model:motor-ad-frequency@7"
) -> tuple[UUID, Principal, ArtifactRef]:
    """Submit one artifact version (a model unless `ref_text` names another) and approve it
    through the approval service, as the platform does: as many APPROVE decisions as the
    stored request requires (`approvers_required`, fixed at submission; one for a model, two
    for a rating version under the default policy), each by a new approver distinct from the
    submitter and the creation author. Then the artifact's approval event the owning module
    writes after the last decision. Returns the request, the last approver and the ref."""
    from backend.tests.test_approvals import (
        _no_evidence_authors,
        _submit,
        _user,
        _with_role,
    )

    from app.db.models import ApprovalRequestRow
    from app.platform import approvals, audit
    from model_schema import ArtifactRef, DecisionKind, JobSource

    ref = ArtifactRef.parse(ref_text)
    request_id = await _submit(database, workspace_id, _user("s"), ref=ref)
    async with database.session() as session:
        required = (await session.get(ApprovalRequestRow, request_id)).approvers_required  # type: ignore[union-attr]
    approver = _user("a")
    for n in range(required):
        approver = _user(f"a{n}")
        await _with_role(database, workspace_id, approver, "approver")
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
    async with database.unit_of_work() as session:
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=approver,
            source=JobSource.API,
            action=f"{ref.type}.approved",
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

    request_id, _approver, _ref = await _decide_to_approval(database, workspace_id)
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
    await _decide_to_approval(database, workspace_id)
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

    await _decide_to_approval(database, workspace_id)

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


async def _rules_reported(database: Database, workspace_id: UUID) -> set[str]:
    async with database.session() as session:
        report = await rc.reconcile(session, workspace_id)
    assert report.chain == "intact"
    return {m.rule for m in report.mismatches}


def _draft_rating_version(workspace_id: UUID, status: str, slug: str | None = None) -> object:
    from app.db.models import RatingVersionRow

    return RatingVersionRow(
        workspace_id=workspace_id,
        slug=slug or f"rv-{uuid4().hex[:8]}",
        version=1,
        status=status,
        dataset_version_id=uuid4(),
        model_ref="model:motor-ad-frequency@7",
        created_by=uuid4(),
    )


async def test_reconcile_db_a_planted_live_rating_version_is_a_status_the_product_does_not_write(
    database: Database, workspace_id: UUID
) -> None:
    """R1 and the unwritten status: a `live` row, which no writer produces, planted through the
    application connection WITH an approved approval request for its ref (two approvers, as the
    default policy requires for a rating version). R1 reports a row in a status no lifecycle
    edge leads to whatever requests exist, so the approved request does not cover it. The
    request is also what lets the plant through wherever the database holds `live` like
    `approved` (an approved request for the ref is that guard's evidence): no guard is
    switched off. Only R1 reports: the request's trail is the product's own (R2 to R4)."""
    from app.db.models import ApprovalRequestRow

    slug = f"rv-{uuid4().hex[:8]}"
    request_id, _approver, _ref = await _decide_to_approval(
        database, workspace_id, f"rating_version:{slug}@1"
    )
    async with database.session() as session:
        request = await session.get(ApprovalRequestRow, request_id)
    assert request is not None
    assert request.status == "approved"  # the planted evidence, checked, not presumed
    async with database.unit_of_work() as session:
        session.add(_draft_rating_version(workspace_id, "live", slug))
    async with database.session() as session:
        report = await rc.reconcile(session, workspace_id)
    assert [m.rule for m in report.mismatches] == ["R1"]
    assert "does not write" in report.mismatches[0].detail


async def test_reconcile_db_a_planted_stray_decision_event_is_reported(
    database: Database, workspace_id: UUID
) -> None:
    """R3: after a clean decision, one more decision event with no decision row behind it."""
    from app.platform import audit
    from model_schema import JobSource

    _request_id, approver, ref = await _decide_to_approval(database, workspace_id)
    assert await _rules_reported(database, workspace_id) == set()
    async with database.unit_of_work() as session:
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=approver,
            source=JobSource.API,
            action="approval_request.approve",
            entity_ref=str(ref),
        )
    assert "R3" in await _rules_reported(database, workspace_id)


async def test_reconcile_db_a_planted_second_approval_event_is_reported(
    database: Database, workspace_id: UUID
) -> None:
    """R4: the artifact's approval event must exist exactly once; a second one is appended."""
    from app.platform import audit
    from model_schema import JobSource

    _request_id, approver, ref = await _decide_to_approval(database, workspace_id)
    assert await _rules_reported(database, workspace_id) == set()
    async with database.unit_of_work() as session:
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=approver,
            source=JobSource.API,
            action="model.approved",
            entity_ref=str(ref),
        )
    assert "R4" in await _rules_reported(database, workspace_id)


async def test_reconcile_db_a_planted_deployment_of_a_draft_version_is_reported(
    database: Database, workspace_id: UUID
) -> None:
    """R5 and FR-238: a deployment row on a `draft` version, with no creation event."""
    from sqlalchemy import select

    from app.db.models import DeploymentRow, EnvironmentRow
    from model_schema import new_uuid7

    version = _draft_rating_version(workspace_id, "draft")
    async with database.unit_of_work() as session:
        session.add(version)
        env_id = (
            await session.execute(select(EnvironmentRow.id).where(EnvironmentRow.slug == "uat"))
        ).scalar_one()
        session.add(
            DeploymentRow(
                workspace_id=workspace_id,
                environment_id=env_id,
                rating_version_ref=f"rating_version:{version.slug}@1",  # type: ignore[attr-defined]
                bundle_hash="sha256:" + "a" * 64,
                deployed_by=new_uuid7(),
                reason="planted",
            )
        )
    async with database.session() as session:
        report = await rc.reconcile(session, workspace_id)
    assert any("not approved or later" in m.detail for m in report.mismatches), report.mismatches


async def _skip_revalidation(session: AsyncSession, *, ref: ArtifactRef) -> None:
    """The stored-bundle guard is `test_stored_bundle_revalidation.py`'s; this test is about
    what the decision and deployment writers leave in the chain."""


async def _decided_rating_version(database: Database, workspace_id: UUID, slug: str) -> str:
    """A compiled Rating Version in `review`, then approved as the platform does: the request
    through `approvals.submit`, each decision through `approvals.decide`, the version moved by
    `rating_versions.apply_approval_decision`. The artifact row is present throughout and no
    approval event is written by hand."""
    from backend.tests.test_approvals import _no_evidence_authors, _submit, _user, _with_role
    from backend.tests.test_deployments import _compiled_metadata

    from app.db.models import ApprovalRequestRow, RatingVersionRow
    from app.platform import approvals
    from app.platform import rating_versions as rating_versions_service
    from model_schema import DecisionKind

    async with database.unit_of_work() as session:
        session.add(
            RatingVersionRow(
                workspace_id=workspace_id,
                slug=slug,
                version=1,
                status="review",
                dataset_version_id=uuid4(),
                model_ref="model:motor-ad-frequency@7",
                created_by=uuid4(),
                bundle=await _compiled_metadata(session),
            )
        )
    ref = ArtifactRef.parse(f"rating_version:{slug}@1")
    request_id = await _submit(database, workspace_id, _user("s"), ref=ref)
    async with database.session() as session:
        required = (await session.get(ApprovalRequestRow, request_id)).approvers_required  # type: ignore[union-attr]
    for n in range(required):
        approver = _user(f"{slug}-a{n}")
        await _with_role(database, workspace_id, approver, "approver")
        async with database.unit_of_work() as session:
            decided = await approvals.decide(
                session,
                evidence_authors=_no_evidence_authors,
                workspace_id=workspace_id,
                request_id=request_id,
                approver=approver,
                decision=DecisionKind.APPROVE,
                comment="clean",
            )
            async with approvals.approval_decision(session):
                await rating_versions_service.apply_approval_decision(
                    session, workspace_id=workspace_id, actor=approver, request=decided
                )
    return str(ref)


async def test_reconcile_db_the_real_paths_with_artifact_rows_reconcile_clean(
    database: Database, workspace_id: UUID, grant: Any
) -> None:
    """The clean case through every real writer, artifact rows present: the seeded built-in
    rules (FR-68), a rule set written by `replace_rule_set`, two Rating Versions approved through
    `approvals.decide`, a deploy and a rollback. Nothing is written by hand."""
    from backend.tests.test_approvals import _user, _with_role
    from sqlalchemy import select

    from app.db.models import ValidationRuleRow
    from app.platform import datasets, deployments
    from app.platform import validation_rules as rule_service
    from model_schema import DeploymentCreate, RollbackCreate

    await grant("analyst")  # seeds the built-in catalogue, as every workspace has it (FR-68)
    actor = _user("analyst")
    await _with_role(database, workspace_id, actor, "analyst")
    async with database.unit_of_work() as session:
        dataset = await datasets.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug="reconcile-clean"
        )
        rule_id = (
            (
                await session.execute(
                    select(ValidationRuleRow.id).where(
                        ValidationRuleRow.workspace_id == workspace_id,
                        ValidationRuleRow.builtin.is_(True),
                    )
                )
            )
            .scalars()
            .first()
        )
        assert rule_id is not None, "the built-in rules are seeded"
        await rule_service.replace_rule_set(
            session,
            workspace_id=workspace_id,
            actor=actor,
            dataset_id=dataset.id,
            slug="reconcile-clean",
            members=[rule_service.RuleSetMember(rule_id=rule_id)],
        )

    first = await _decided_rating_version(database, workspace_id, "rv-first")
    second = await _decided_rating_version(database, workspace_id, "rv-second")
    deployer = _user("deployer")
    await _with_role(database, workspace_id, deployer, "deployer")
    for ref in (first, second):
        async with database.unit_of_work() as session:
            await deployments.deploy(
                session,
                workspace_id=workspace_id,
                actor=deployer,
                environment="dev",
                body=DeploymentCreate(rating_version_ref=ArtifactRef.parse(ref), reason="release"),
                revalidate=_skip_revalidation,
                switch=None,
            )
    async with database.unit_of_work() as session:
        await deployments.rollback(
            session,
            workspace_id=workspace_id,
            actor=deployer,
            environment="dev",
            body=RollbackCreate(rating_version_ref=ArtifactRef.parse(first), reason="back"),
            revalidate=_skip_revalidation,
            switch=None,
        )

    async with database.session() as session:
        report = await rc.reconcile(session, workspace_id)
    assert report.chain == "intact"
    assert report.artifacts_checked > 38, "built-in rules, the rule set and both versions are rows"
    assert report.mismatches == (), report.mismatches


pytestmark = pytest.mark.req("FR-2163")
