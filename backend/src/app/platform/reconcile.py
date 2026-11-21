"""Reconciling approved-state artifacts against the verified audit chain (`06` FR-2163).

> **FR-2163** — Every artifact in an approved state, and every deployment, has the approval
> request, the decisions and the audit events the decision path writes, in order, in a chain
> that verifies. A run reports each artifact that does not, per workspace.

The check is **detective**: it reports after the fact and prevents no write. It is read-only.

The rule logic (`reconcile_data`) is a pure function over in-memory rows, so every rule is
testable without a database. `load_workspace_data` reads the rows and `reconcile` adds the
precondition: the chain must verify first, otherwise the workspace is reported as broken and
no rule runs for it — reconciling against a broken chain proves nothing, the reason an
anchor refuses one (FR-373 (4)).

Rules (rule ids are this module's vocabulary, not requirement ids):

* **R1** — every artifact in an approved state, or in a state reachable only through
  `approved`, has an approved approval request; a row in a status no lifecycle edge leads to
  (today a rating version that is `live` or `retired`) is reported whatever requests exist.
  Two kinds of row are outside R1: a built-in validation rule (FR-68, `builtin IS TRUE`: seeded
  `approved` with no request, by design) and a validation rule set (the PL-1303 Acceptance 7
  allowance: its writer records no request). The rule-set table stays in `COVERED_TABLES`: the
  census needs it.
  A model archived after it was superseded is not claimed by R1: `archived` is reachable from
  `draft`, so R2 to R4 cover its approval through the chain.
* **R2** — every approved request has enough approving decisions, from distinct approvers,
  none of them its submitter (FR-353). The reconciliation compares a request with its own
  events: a request's stored `approvers_required` equals the `approvers_required` recorded in
  its submitted event.
* **R3** — every decision row has exactly one matching chain event (its actor, action and
  entity reference those of the row), and every such event has its decision row. Events
  written since the decision event carries its ids match by id; earlier events match by
  `(entity_ref, actor, decision)` in order.
* **R4** — the chain order is the process order: submitted, then the decisions, then the
  artifact's approval event, once. A request whose status is `approved` has a final decision
  event recording status `approved`: one approved with only decision events recording another
  status is a mismatch.
* **R5** — every deployment rests on an approved-or-later version that passes R1 to R4 and has
  its creation or rollback event (`deployment.created`, `deployment.rolled_back`; FR-269,
  FR-238: a draft or review version does not deploy); where it names a
  deployment request, that request is `executed` and passes R1 to R4.

A mismatch whose chain evidence all lies before the workspace's first id-carrying decision
event (by sequence, never by timestamp) is marked `legacy`; it is reported and counted like any
other (nothing is silenced). An R5 mismatch is never legacy: a deployment is not an event a
cut-over can place it before. A workspace with no id-carrying decision event has no cut-over:
nothing in it is legacy. Rule 6 of the issue (anchors, FR-373) is deferred to #1919.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Collection, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Final
from uuid import UUID

from sqlalchemy import false, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalDecisionRow,
    ApprovalRequestRow,
    AuditEventRow,
    CustomMetricRow,
    CustomObjectiveRow,
    DeploymentRequestRow,
    DeploymentRow,
    ModelRow,
    PerilStructureRow,
    RatingVersionRow,
    ValidationRuleRow,
    ValidationRuleSetRow,
    WorkspaceRow,
)
from app.platform import audit
from app.platform.safe_exception import safe_job_error_text
from model_schema import (
    VALID_METRIC_TRANSITIONS,
    VALID_MODEL_TRANSITIONS,
    VALID_OBJECTIVE_TRANSITIONS,
    VALID_PERIL_STRUCTURE_TRANSITIONS,
    ApprovalStatus,
    DecisionKind,
)
from model_schema.rating import VALID_RATING_VERSION_TRANSITIONS

__all__ = [
    "COVERED_TABLES",
    "ArtifactState",
    "DecisionState",
    "DeploymentState",
    "EventState",
    "Mismatch",
    "RequestState",
    "WorkspaceData",
    "WorkspaceReport",
    "approved_or_later",
    "approved_states",
    "load_workspace_data",
    "reconcile",
    "reconcile_data",
    "unwritten_states",
    "workspace_ids",
]

APPROVED: Final = "approved"
DECISION_ACTIONS: Final[Mapping[str, str]] = {
    kind.value: f"approval_request.{kind.value}" for kind in DecisionKind
}
#: What a malformed stored row raises while it is read or its rules run.
_UNREADABLE: Final = (ValueError, TypeError, AttributeError, KeyError)
SUBMITTED_ACTION: Final = "approval_request.submitted"
#: The events that record a deployment: a deploy writes `deployment.created`, a rollback
#: (FR-269) `deployment.rolled_back`; the new deployment's id is `after["id"]` in both.
DEPLOYMENT_ACTIONS: Final = frozenset({"deployment.created", "deployment.rolled_back"})
#: A validation rule set is written `approved` under the PL-1303 Acceptance 7 allowance with no
#: approval request (`validation_rules.replace_rule_set`); R1 has nothing to require for it.
_NO_REQUEST_TABLE: Final = "validation_rule_sets"

#: The action of the event that records an artifact's approval, per approval-request artifact
#: type; `<type>.approved` unless named here. A validation rule set carries no approval event
#: of its own (its writers record `validation_rule_set.replaced`), so R4 has no event to
#: require for it. A deployment request records `deployment_request.approved`.
_APPROVAL_EVENT_OVERRIDES: Final[Mapping[str, str | None]] = {
    "deployment": "deployment_request.approved",
    "validation_rule_set": None,
}


def _graph(transitions: Mapping[Any, Collection[Any]]) -> dict[str, frozenset[str]]:
    return {
        str(getattr(s, "value", s)): frozenset(str(getattr(t, "value", t)) for t in targets)
        for s, targets in transitions.items()
    }


#: Per approval-request artifact type: the initial status and the lifecycle as data. The
#: first five are the `model-schema` tables, read, never copied. A validation rule, a validation
#: rule set and a deployment request have no transition table: their graphs are written here from
#: their only writers (`platform/validation_rules.py`, `platform/deployments.py`), and a graph
#: that reached a later status without `approved` would be a change to those writers.
STATE_GRAPHS: Final[Mapping[str, tuple[str, dict[str, frozenset[str]]]]] = {
    "model": ("draft", _graph(VALID_MODEL_TRANSITIONS)),
    "peril_structure": ("draft", _graph(VALID_PERIL_STRUCTURE_TRANSITIONS)),
    "custom_objective": ("draft", _graph(VALID_OBJECTIVE_TRANSITIONS)),
    "custom_metric": ("draft", _graph(VALID_METRIC_TRANSITIONS)),
    "rating_version": ("draft", _graph(VALID_RATING_VERSION_TRANSITIONS)),
    "validation_rule": (
        "draft",
        {
            "draft": frozenset({"review"}),
            "review": frozenset({"approved", "draft"}),
            "approved": frozenset(),
        },
    ),
    "validation_rule_set": (
        "draft",
        {
            "draft": frozenset({"review"}),
            "review": frozenset({"approved", "draft"}),
            "approved": frozenset(),
        },
    ),
    "deployment": (
        "draft",
        {
            "draft": frozenset({"review"}),
            "review": frozenset({"approved", "rejected", "withdrawn"}),
            "approved": frozenset({"executed"}),
            "rejected": frozenset(),
            "withdrawn": frozenset(),
            "executed": frozenset(),
        },
    ),
}

#: governed table -> (approval-request artifact type, row class, the slug attribute). A literal
#: dict: the census test checks its key set against the installed `approval_guard` triggers, and
#: nothing else about it.
COVERED_TABLES: Final[Mapping[str, tuple[str, Any, str]]] = {
    "models": ("model", ModelRow, "model_family_slug"),
    "custom_metrics": ("custom_metric", CustomMetricRow, "slug"),
    "custom_objectives": ("custom_objective", CustomObjectiveRow, "slug"),
    "peril_structures": ("peril_structure", PerilStructureRow, "slug"),
    "rating_versions": ("rating_version", RatingVersionRow, "slug"),
    "validation_rules": ("validation_rule", ValidationRuleRow, "slug"),
    "validation_rule_sets": ("validation_rule_set", ValidationRuleSetRow, "slug"),
    "deployment_requests": ("deployment", DeploymentRequestRow, "slug"),
}


def approved_or_later(initial: str, graph: Mapping[str, Collection[str]]) -> frozenset[str]:
    """The statuses that are `approved` or reachable only through it, derived from the graph.

    Every status that cannot be reached from `initial` along edges that avoid `approved`.
    Computed from the graph it is given: a status added to that graph changes the answer.
    """
    free = {initial}
    stack = [initial]
    while stack:
        for target in graph.get(stack.pop(), ()):
            if target != APPROVED and target not in free:
                free.add(target)
                stack.append(target)
    return frozenset(set(graph) - free)


def approved_states(artifact_type: str) -> frozenset[str]:
    initial, graph = STATE_GRAPHS[artifact_type]
    return approved_or_later(initial, graph)


def unwritten_states(artifact_type: str) -> frozenset[str]:
    """The statuses no lifecycle edge leads to: the product never writes a row in one.

    Every status unreachable from the initial status, `approved` included as a way through.
    A rating version's `live` and `retired` are such statuses today.
    """
    initial, graph = STATE_GRAPHS[artifact_type]
    reached = {initial}
    stack = [initial]
    while stack:
        for target in graph.get(stack.pop(), ()):
            if target not in reached:
                reached.add(target)
                stack.append(target)
    return frozenset(set(graph) - reached)


@dataclass(frozen=True)
class ArtifactState:
    table: str
    ref: str  # `<type>:<slug>@<version>`
    type: str
    status: str
    #: A shipped catalogue row (FR-68), seeded `approved` with no request. Only validation rules.
    builtin: bool = False


@dataclass(frozen=True)
class RequestState:
    id: UUID
    ref: str
    type: str
    status: str
    submitted_by: UUID
    approvers_required: int
    submitted_at: datetime


@dataclass(frozen=True)
class DecisionState:
    id: UUID
    request_id: UUID
    approver_id: UUID
    decision: str
    at: datetime


@dataclass(frozen=True)
class EventState:
    sequence: int
    at: datetime
    action: str
    entity_ref: str
    actor_id: UUID | None
    after: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class DeploymentState:
    id: UUID
    rating_version_ref: str
    #: The approval ref of its deployment request (`deployment:<slug>@<version>`) and that
    #: request's own status, when `deployment_request_id` is set.
    request_ref: str | None = None
    request_status: str | None = None


@dataclass(frozen=True)
class WorkspaceData:
    artifacts: tuple[ArtifactState, ...] = ()
    requests: tuple[RequestState, ...] = ()
    decisions: tuple[DecisionState, ...] = ()
    events: tuple[EventState, ...] = ()
    deployments: tuple[DeploymentState, ...] = ()


@dataclass(frozen=True)
class Mismatch:
    rule: str
    ref: str
    detail: str
    #: Older than the workspace's first decision event that carries its ids (D2).
    legacy: bool = False


@dataclass(frozen=True)
class WorkspaceReport:
    workspace_id: UUID
    chain: str  # "intact" | "broken" | "unreadable"
    events_verified: int = 0
    artifacts_checked: int = 0
    requests_checked: int = 0
    mismatches: tuple[Mismatch, ...] = ()
    chain_detail: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


# -- the rules ------------------------------------------------------------------------------


def _r1(data: WorkspaceData) -> list[Mismatch]:
    approved_refs = {r.ref for r in data.requests if r.status == APPROVED}
    found: list[Mismatch] = []
    for a in data.artifacts:
        if a.builtin or a.table == _NO_REQUEST_TABLE:
            continue
        if a.status in unwritten_states(a.type):
            # Whatever requests exist: no writer of this product produces a row in this status.
            found.append(
                Mismatch(
                    "R1",
                    a.ref,
                    f"{a.table} row is {a.status!r}, a status the product does not write",
                )
            )
        elif a.status in approved_states(a.type) and a.ref not in approved_refs:
            found.append(
                Mismatch(
                    "R1",
                    a.ref,
                    f"{a.table} row is {a.status!r} and no approved approval request names {a.ref}",
                )
            )
    return found


def _recorded_approvers(data: WorkspaceData) -> dict[UUID, int]:
    """Per request, the `approvers_required` its submitted event records.

    A request is paired with the submitted event of the same position among the requests and
    the submitted events that name its reference, in order; a ref with a different number of
    each cannot be paired and is left out (a missing or surplus submitted event is not this
    check's to name).
    """
    requests: dict[str, list[RequestState]] = defaultdict(list)
    for request in sorted(data.requests, key=lambda r: (r.submitted_at, str(r.id))):
        requests[request.ref].append(request)
    submitted: dict[str, list[EventState]] = defaultdict(list)
    for event in sorted(data.events, key=lambda e: e.sequence):
        if event.action == SUBMITTED_ACTION:
            submitted[event.entity_ref].append(event)
    recorded: dict[UUID, int] = {}
    for ref, its_requests in requests.items():
        events = submitted.get(ref, [])
        if len(events) != len(its_requests):
            continue
        for request, event in zip(its_requests, events, strict=True):
            value = (event.after or {}).get("approvers_required")
            if value is not None:
                recorded[request.id] = int(value)
    return recorded


def _r2(data: WorkspaceData) -> list[Mismatch]:
    found: list[Mismatch] = []
    recorded = _recorded_approvers(data)
    for request in data.requests:
        if recorded.get(request.id, request.approvers_required) != request.approvers_required:
            found.append(
                Mismatch(
                    "R2",
                    request.ref,
                    f"stores approvers_required {request.approvers_required}; its submitted "
                    f"event records {recorded[request.id]}",
                )
            )
        if request.status != APPROVED:
            continue
        approves = [
            d for d in data.decisions if d.request_id == request.id and d.decision == "approve"
        ]
        approvers = {d.approver_id for d in approves}
        if len(approvers) < request.approvers_required:
            found.append(
                Mismatch(
                    "R2",
                    request.ref,
                    f"approved with {len(approvers)} distinct approving decision(s); "
                    f"{request.approvers_required} required",
                )
            )
        if len(approves) != len(approvers):
            found.append(Mismatch("R2", request.ref, "one approver is counted twice"))
        if request.submitted_by in approvers:
            found.append(Mismatch("R2", request.ref, "its submitter is among its approvers"))
    return found


def _match_decisions(
    data: WorkspaceData,
) -> tuple[list[Mismatch], dict[UUID, EventState]]:
    """R3's matching: each decision row to its one event, and the leftovers either way."""
    found: list[Mismatch] = []
    matched: dict[UUID, EventState] = {}
    requests = {r.id: r for r in data.requests}
    decision_events = [e for e in data.events if e.action in DECISION_ACTIONS.values()]
    by_id: dict[str, list[EventState]] = defaultdict(list)
    legacy_pool: dict[tuple[str, UUID | None, str], list[EventState]] = defaultdict(list)
    for event in sorted(decision_events, key=lambda e: e.sequence):
        decision_id = (event.after or {}).get("decision_id")
        if decision_id is not None:
            by_id[str(decision_id)].append(event)
        else:
            legacy_pool[(event.entity_ref, event.actor_id, event.action)].append(event)

    consumed: set[int] = set()
    for decision in sorted(data.decisions, key=lambda d: (d.at, str(d.id))):
        request = requests.get(decision.request_id)
        if request is None:
            found.append(
                Mismatch("R3", str(decision.id), "decision row names a request that is not there")
            )
            continue
        events = by_id.get(str(decision.id), [])
        if not events:
            pool = legacy_pool.get(
                (request.ref, decision.approver_id, DECISION_ACTIONS[decision.decision]), []
            )
            events = [pool.pop(0)] if pool else []
        if not events:
            found.append(
                Mismatch(
                    "R3",
                    request.ref,
                    f"decision {decision.id} ({decision.decision}) has no chain event",
                )
            )
            continue
        if len(events) > 1:
            found.append(
                Mismatch(
                    "R3", request.ref, f"decision {decision.id} has {len(events)} chain events"
                )
            )
        event = events[0]
        for what, got, expected in (
            ("actor", event.actor_id, decision.approver_id),
            ("action", event.action, DECISION_ACTIONS[decision.decision]),
            ("entity_ref", event.entity_ref, request.ref),
        ):
            if got != expected:
                found.append(
                    Mismatch(
                        "R3",
                        request.ref,
                        f"event {event.sequence} has {what} {got}, its decision row {expected}",
                    )
                )
        named = (event.after or {}).get("approval_request_id")
        if named is not None and str(named) != str(decision.request_id):
            found.append(
                Mismatch(
                    "R3",
                    request.ref,
                    f"event {event.sequence} names request {named}, not {decision.request_id}",
                )
            )
        consumed.update(e.sequence for e in events)
        matched[decision.id] = event

    for event in decision_events:
        if event.sequence not in consumed:
            found.append(
                Mismatch(
                    "R3",
                    event.entity_ref,
                    f"event {event.sequence} ({event.action}) has no decision row",
                )
            )
    return found, matched


def _r4(data: WorkspaceData, matched: Mapping[UUID, EventState]) -> list[Mismatch]:
    found: list[Mismatch] = []
    submitted: dict[str, list[int]] = defaultdict(list)
    for event in data.events:
        if event.action == SUBMITTED_ACTION:
            submitted[event.entity_ref].append(event.sequence)
    for request in data.requests:
        events = [
            (d, matched[d.id])
            for d in data.decisions
            if d.request_id == request.id
            if d.id in matched
        ]
        for _, event in events:
            if not any(s < event.sequence for s in submitted.get(request.ref, [])):
                found.append(
                    Mismatch(
                        "R4",
                        request.ref,
                        f"decision event {event.sequence} precedes every submitted event",
                    )
                )
        if request.status != APPROVED:
            continue
        with_status = [
            (event.sequence, status)
            for _, event in events
            if (status := (event.after or {}).get("status")) is not None
        ]
        if with_status:
            # The FINAL decision event that records a status; one with none is not read as
            # another status. A stored value outside ApprovalStatus is never printed.
            final = max(with_status)[1]
            if final != APPROVED:
                shown = (
                    repr(final)
                    if isinstance(final, str) and final in {s.value for s in ApprovalStatus}
                    else "a status that is not an approval status"
                )
                found.append(
                    Mismatch(
                        "R4",
                        request.ref,
                        f"approved, but its final decision event records {shown}",
                    )
                )
        action = _APPROVAL_EVENT_OVERRIDES.get(request.type, f"{request.type}.approved")
        if action is None:
            continue
        approvals = [e for e in data.events if e.action == action and e.entity_ref == request.ref]
        if len(approvals) != 1:
            found.append(
                Mismatch(
                    "R4",
                    request.ref,
                    f"{len(approvals)} {action} event(s); exactly one is required",
                )
            )
            continue
        last_approval = max(
            (e.sequence for d, e in events if d.decision == "approve"), default=None
        )
        if last_approval is not None and approvals[0].sequence < last_approval:
            found.append(
                Mismatch(
                    "R4",
                    request.ref,
                    f"{action} (sequence {approvals[0].sequence}) precedes the last approving "
                    f"decision event (sequence {last_approval})",
                )
            )
    return found


def _r5(data: WorkspaceData, upstream: Collection[Mismatch]) -> list[Mismatch]:
    found: list[Mismatch] = []
    unreconciled = {m.ref for m in upstream}
    versions = {a.ref: a.status for a in data.artifacts if a.type == "rating_version"}
    deployable = approved_states("rating_version")
    created = {
        str((e.after or {}).get("id")) for e in data.events if e.action in DEPLOYMENT_ACTIONS
    }
    for deployment in data.deployments:
        ref = deployment.rating_version_ref
        subject = f"deployment:{deployment.id}"
        if ref not in versions:
            found.append(Mismatch("R5", subject, f"its version {ref} is not a stored version"))
        elif versions[ref] not in deployable:
            found.append(
                Mismatch(
                    "R5",
                    subject,
                    f"its version {ref} is {versions[ref]!r}, not approved or later (FR-238)",
                )
            )
        elif ref in unreconciled:
            found.append(Mismatch("R5", subject, f"its version {ref} does not reconcile"))
        if str(deployment.id) not in created:
            found.append(
                Mismatch(
                    "R5", subject, "no deployment.created or deployment.rolled_back event names it"
                )
            )
        if deployment.request_ref is not None:
            if deployment.request_status != "executed":
                found.append(
                    Mismatch(
                        "R5",
                        subject,
                        f"its deployment request {deployment.request_ref} is "
                        f"{deployment.request_status!r}, not 'executed'",
                    )
                )
            if deployment.request_ref in unreconciled:
                found.append(
                    Mismatch(
                        "R5",
                        subject,
                        f"its deployment request {deployment.request_ref} does not reconcile",
                    )
                )
    return found


def _mark_legacy(data: WorkspaceData, mismatches: list[Mismatch]) -> list[Mismatch]:
    """Mark a mismatch `legacy` by chain sequence, never by a timestamp.

    `at` is chosen by whoever writes the event, so it cannot say what is old. A mismatch is
    legacy only when it has chain evidence and all of it, every event naming its reference, lies
    at a sequence before the workspace's first decision event that carries its ids. A mismatch
    with no event naming its reference has nothing to place and is not legacy, and a workspace
    with no id-carrying decision event has no cut-over to place anything before: nothing in it
    is legacy. An R5 mismatch is never legacy: its subject is a deployment, which no cut-over of
    decision events places it before, and its reference is not what the chain's events name.
    """
    first_new = min(
        (
            e.sequence
            for e in data.events
            if e.action in DECISION_ACTIONS.values() and (e.after or {}).get("decision_id")
        ),
        default=None,
    )
    latest: dict[str, int] = {}
    for event in data.events:
        latest[event.entity_ref] = max(event.sequence, latest.get(event.entity_ref, event.sequence))
    out: list[Mismatch] = []
    for m in mismatches:
        last = latest.get(m.ref)
        legacy = m.rule != "R5" and first_new is not None and last is not None and last < first_new
        out.append(Mismatch(m.rule, m.ref, m.detail, legacy))
    return out


def reconcile_data(data: WorkspaceData) -> list[Mismatch]:
    """Every mismatch of R1 to R5 in one workspace's rows; R5's first."""
    r3, matched = _match_decisions(data)
    upstream = [*_r1(data), *_r2(data), *r3, *_r4(data, matched)]
    return _mark_legacy(data, [*_r5(data, upstream), *upstream])


# -- the database edge ------------------------------------------------------------------------


async def load_workspace_data(session: AsyncSession, workspace_id: UUID) -> WorkspaceData:
    """Read one workspace's rows. Read-only; the caller owns the transaction."""
    artifacts: list[ArtifactState] = []
    for table, (artifact_type, row_class, slug_attr) in COVERED_TABLES.items():
        builtin = row_class.builtin if row_class is ValidationRuleRow else false()
        rows = (
            await session.execute(
                select(
                    getattr(row_class, slug_attr), row_class.version, row_class.status, builtin
                ).where(row_class.workspace_id == workspace_id)
            )
        ).all()
        artifacts.extend(
            ArtifactState(
                table, f"{artifact_type}:{slug}@{version}", artifact_type, status, bool(is_builtin)
            )
            for slug, version, status, is_builtin in rows
        )
    requests = tuple(
        RequestState(
            r.id,
            r.artifact_ref,
            r.artifact_type,
            r.status,
            r.submitted_by,
            r.approvers_required,
            r.submitted_at,
        )
        for r in (
            await session.execute(
                select(ApprovalRequestRow).where(ApprovalRequestRow.workspace_id == workspace_id)
            )
        ).scalars()
    )
    request_ids = [r.id for r in requests]
    decisions = tuple(
        DecisionState(d.id, d.request_id, d.approver_id, d.decision, d.at)
        for d in (
            await session.execute(
                select(ApprovalDecisionRow).where(ApprovalDecisionRow.request_id.in_(request_ids))
            )
        ).scalars()
    )
    events = tuple(
        EventState(
            e.sequence,
            e.at,
            e.action,
            e.entity_ref,
            UUID(e.actor["id"]) if e.actor and e.actor.get("id") else None,
            e.after,
        )
        for e in (
            await session.execute(
                select(AuditEventRow)
                .where(AuditEventRow.workspace_id == workspace_id)
                .order_by(AuditEventRow.sequence)
            )
        ).scalars()
    )
    deployment_requests = {
        row.id: row
        for row in (
            await session.execute(
                select(DeploymentRequestRow).where(
                    DeploymentRequestRow.workspace_id == workspace_id
                )
            )
        ).scalars()
    }
    deployments = []
    for d in (
        await session.execute(
            select(DeploymentRow).where(DeploymentRow.workspace_id == workspace_id)
        )
    ).scalars():
        request = (
            deployment_requests.get(d.deployment_request_id) if d.deployment_request_id else None
        )
        deployments.append(
            DeploymentState(
                d.id,
                d.rating_version_ref,
                None if request is None else f"deployment:{request.slug}@{request.version}",
                None if request is None else request.status,
            )
        )
    return WorkspaceData(tuple(artifacts), requests, decisions, events, tuple(deployments))


async def workspace_ids(session: AsyncSession) -> tuple[list[UUID], frozenset[UUID]]:
    """Every workspace id the run covers, and which of them have no `workspaces` row.

    The union of `workspaces`, `audit_events.workspace_id` and the `workspace_id` of every
    `COVERED_TABLES` row class. No foreign key holds a governed row or an event to a
    `workspaces` row (only `workspace_members` and `workspace_settings` carry one), so an id can
    be in the chain or on a governed row with no workspace row: one that never had a row, or one
    whose row was deleted after its events were written. Such an id is reconciled like any
    other and returned in the second value, so the run reports it (FR-2163).
    """
    listed = set((await session.execute(select(WorkspaceRow.id))).scalars())
    seen = set(listed)
    for column in (
        AuditEventRow.workspace_id,
        *(row_class.workspace_id for _type, row_class, _slug in COVERED_TABLES.values()),
    ):
        seen.update((await session.execute(select(column).distinct())).scalars())
    return sorted(seen, key=str), frozenset(seen - listed)


async def reconcile(session: AsyncSession, workspace_id: UUID) -> WorkspaceReport:
    """One workspace: the chain first, then the rules. A broken chain stops the rules."""
    try:
        verified = await audit.verify_chain(session, workspace_id)
        data = await load_workspace_data(session, workspace_id)
        mismatches = tuple(reconcile_data(data))
    except audit.ChainBrokenError as exc:
        # The verifier's own authored reason and the sequence number, never `str(exc)`.
        return WorkspaceReport(
            workspace_id,
            "broken",
            chain_detail=f"audit chain broken at sequence {int(exc.sequence)}: {exc.reason}",
        )
    except _UNREADABLE as exc:
        # A row whose stored shape the models refuse: this workspace cannot be read, the run
        # carries on with the others (a pydantic `ValidationError` is a `ValueError`).
        # The allow-list's text, which for these types is the class name only: what the models
        # raise can carry the stored row (NFR-499).
        return WorkspaceReport(workspace_id, "unreadable", chain_detail=safe_job_error_text(exc))
    return WorkspaceReport(
        workspace_id,
        "intact",
        events_verified=verified,
        artifacts_checked=len(data.artifacts),
        requests_checked=len(data.requests),
        mismatches=mismatches,
    )
