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
  A model archived after it was superseded is not claimed by R1: `archived` is reachable from
  `draft`, so R2 to R4 cover its approval through the chain.
* **R2** — every approved request has enough approving decisions, from distinct approvers,
  none of them its submitter (FR-353).
* **R3** — every decision row has exactly one matching chain event, and every such event has
  its decision row. Events written since the decision event carries its ids match by id;
  earlier events match by `(entity_ref, actor, decision)` in order.
* **R4** — the chain order is the process order: submitted, then the decisions, then the
  artifact's approval event, once.
* **R5** — every deployment rests on a version that passes R1 to R4 and has its creation
  event; where it names a deployment request, that request is `executed` and passes R1 to R4.

A mismatch whose chain evidence all lies before the workspace's first id-carrying decision
event (by sequence, never by timestamp) is marked `legacy`; it is reported and counted like any
other (nothing is silenced).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Collection, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Final
from uuid import UUID

from sqlalchemy import select
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
)
from app.platform import audit
from model_schema import (
    VALID_METRIC_TRANSITIONS,
    VALID_MODEL_TRANSITIONS,
    VALID_OBJECTIVE_TRANSITIONS,
    VALID_PERIL_STRUCTURE_TRANSITIONS,
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
]

APPROVED: Final = "approved"
DECISION_ACTIONS: Final[Mapping[str, str]] = {
    kind.value: f"approval_request.{kind.value}" for kind in DecisionKind
}
SUBMITTED_ACTION: Final = "approval_request.submitted"
DEPLOYMENT_CREATED_ACTION: Final = "deployment.created"

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
#: first five are the `model-schema` tables, read, never copied. A deployment request and a
#: validation rule have no transition table: their graphs are written here from their only
#: writers (`platform/deployments.py`, `platform/validation_rules.py`), and a graph that
#: reached a later status without `approved` would be a change to those writers.
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

#: governed table -> (approval-request artifact type, row class, the slug attribute). The
#: census test derives this key set from the installed `approval_guard` triggers.
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
    Derived, never listed: a status added to a lifecycle changes the answer by itself.
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
    chain: str  # "intact" | "broken"
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


def _r2(data: WorkspaceData) -> list[Mismatch]:
    found: list[Mismatch] = []
    for request in data.requests:
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
    versions = {a.ref for a in data.artifacts if a.type == "rating_version"}
    created = {
        str((e.after or {}).get("id")) for e in data.events if e.action == DEPLOYMENT_CREATED_ACTION
    }
    for deployment in data.deployments:
        ref = deployment.rating_version_ref
        subject = f"deployment:{deployment.id}"
        if ref not in versions:
            found.append(Mismatch("R5", subject, f"its version {ref} is not a stored version"))
        elif ref in unreconciled:
            found.append(Mismatch("R5", subject, f"its version {ref} does not reconcile"))
        if str(deployment.id) not in created:
            found.append(Mismatch("R5", subject, "no deployment.created event names it"))
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
    with no event naming its reference has nothing to place and is not legacy.
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
        legacy = last is not None and (first_new is None or last < first_new)
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
        rows = (
            await session.execute(
                select(getattr(row_class, slug_attr), row_class.version, row_class.status).where(
                    row_class.workspace_id == workspace_id
                )
            )
        ).all()
        artifacts.extend(
            ArtifactState(table, f"{artifact_type}:{slug}@{version}", artifact_type, status)
            for slug, version, status in rows
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


async def reconcile(session: AsyncSession, workspace_id: UUID) -> WorkspaceReport:
    """One workspace: the chain first, then the rules. A broken chain stops the rules."""
    try:
        verified = await audit.verify_chain(session, workspace_id)
    except audit.ChainBrokenError as exc:
        return WorkspaceReport(workspace_id, "broken", chain_detail=str(exc))
    data = await load_workspace_data(session, workspace_id)
    return WorkspaceReport(
        workspace_id,
        "intact",
        events_verified=verified,
        artifacts_checked=len(data.artifacts),
        requests_checked=len(data.requests),
        mismatches=tuple(reconcile_data(data)),
    )
