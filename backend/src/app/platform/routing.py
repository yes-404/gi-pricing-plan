"""The Environment's date-routing rule (`03` §4.13, FR-270, FR-272; WK-674 Slice 6, `RL-1834` D1).

The rule is written whole and appended: the latest `routing_rules` row of an Environment is its
current rule, and an empty list of ranges clears it. A range may name only a Rating Version that
has a Deployment row in this Environment, so a version never promoted here cannot be routed to;
the range pins the id of that version's latest Deployment at write time. The Audit Event shares
the row's transaction (FR-272, NFR-498).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import date
from itertools import combinations
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DeploymentRow, EnvironmentRow, RoutingRuleRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit
from app.platform.deployments import _authorised_environment, _require_rating_version
from model_schema import (
    ArtifactRef,
    JobSource,
    Principal,
    RoutedRange,
    RoutingRange,
    RoutingRule,
    RoutingRuleUpdate,
    new_uuid7,
)

__all__ = ["select", "write_rule"]

_ACTION = "deployment.routing_changed"
_log = get_logger(__name__)


def _overlaps(a: RoutingRange, b: RoutingRange) -> bool:
    """Half-open ranges `[from, to)` share a date; `None` is an open end."""
    return (b.effective_to is None or a.effective_from < b.effective_to) and (
        a.effective_to is None or b.effective_from < a.effective_to
    )


def _span(r: RoutingRange) -> str:
    end = "open" if r.effective_to is None else r.effective_to.isoformat()
    return f"{r.rating_version_ref} [{r.effective_from.isoformat()}, {end})"


def _to_rule(row: RoutingRuleRow, slug: str) -> RoutingRule:
    return RoutingRule(
        environment=slug,
        ranges=[RoutedRange.model_validate(r) for r in row.ranges],
        written_by=row.written_by,
        written_at=row.written_at,
    )


async def write_rule(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    environment: str,
    body: RoutingRuleUpdate,
    count_management: Callable[[], Awaitable[None]] | None = None,
) -> RoutingRule:
    """Write the Environment's rule. Refusals, in `RL-1834` D1 item 3's order, each writing
    nothing: unknown Environment 404, retired 409 (both in `_authorised_environment`, after
    `deployment:promote`), a reference that is not a Rating Version 422, a range that does not
    end after it starts 422, a Rating Version never deployed here 409, overlap 409
    `DEPLOY_DATE_RANGE_OVERLAP`."""
    env = await _authorised_environment(
        session,
        workspace_id=workspace_id,
        actor=actor,
        slug=environment,
        count_management=count_management,
    )
    for r in body.ranges:
        _require_rating_version(r.rating_version_ref, what="A routing range")
    for r in body.ranges:
        if r.effective_to is not None and r.effective_to <= r.effective_from:
            raise PlatformError(
                "VALIDATION_FAILED",
                "A routing range must end after it starts",
                422,
                f"{_span(r)} ends on or before {r.effective_from.isoformat()}. A range is "
                "half-open, so its end date must be later than its start date.",
            )
    pins = await _latest_deployments(session, workspace_id, env, body)
    for a, b in combinations(sorted(body.ranges, key=_sort_key), 2):
        if _overlaps(a, b):
            raise PlatformError(
                "DEPLOY_DATE_RANGE_OVERLAP",
                "Routing ranges overlap",
                409,
                f"{_span(a)} and {_span(b)} share a date. A quote's effective date must select "
                "at most one Rating Version.",
            )
    previous = (
        await session.execute(
            select(RoutingRuleRow)
            .where(
                RoutingRuleRow.workspace_id == workspace_id,
                RoutingRuleRow.environment_id == env.id,
            )
            .order_by(RoutingRuleRow.written_at.desc(), RoutingRuleRow.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    routed = [
        RoutedRange(**r.model_dump(), deployment_id=pins[str(r.rating_version_ref)])
        for r in body.ranges
    ]
    row = RoutingRuleRow(
        id=new_uuid7(),
        workspace_id=workspace_id,
        environment_id=env.id,
        ranges=[r.model_dump(mode="json") for r in routed],
        written_by=actor.id,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)
    rule = _to_rule(row, env.slug)
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=_ACTION,
        entity_ref=f"environment:{env.slug}",
        before=None if previous is None else _to_rule(previous, env.slug).model_dump(mode="json"),
        after=rule.model_dump(mode="json"),
    )
    return rule


def _sort_key(r: RoutingRange) -> tuple[date, str]:
    return (r.effective_from, str(r.rating_version_ref))


async def _latest_deployments(
    session: AsyncSession, workspace_id: UUID, env: EnvironmentRow, body: RoutingRuleUpdate
) -> dict[str, UUID]:
    """Each named Rating Version's latest Deployment id in `env`; 409 for one with none."""
    pins: dict[str, UUID] = {}
    for r in body.ranges:
        ref = str(r.rating_version_ref)
        if ref in pins:
            continue
        found = (
            await session.execute(
                select(DeploymentRow.id)
                .where(
                    DeploymentRow.workspace_id == workspace_id,
                    DeploymentRow.environment_id == env.id,
                    DeploymentRow.rating_version_ref == ref,
                )
                .order_by(DeploymentRow.deployed_at.desc(), DeploymentRow.id.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if found is None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Not deployed to this Environment",
                409,
                f"{ref} was never deployed to {env.slug!r}. A routing range names a Rating "
                "Version this Environment has been deployed with.",
            )
        pins[ref] = found
    return pins


async def select(
    session: AsyncSession, *, workspace_id: UUID, environment: str, effective_date: date
) -> tuple[ArtifactRef, UUID] | None:
    """The Rating Version and Deployment the Environment's current rule selects for a quote with
    this effective date, or `None` (`RL-1834` D1 item 5).

    One read of the current rule and one of the Deployments it pins, through the caller's
    session, with no cache: a rule write takes effect at the next request. A range is a candidate
    only if its pinned Deployment is a row of **this** Environment whose Rating Version is the
    range's own; any other range is ignored and logged, so a version never promoted here is never
    selected, whatever the stored rule says. Ranges of a written rule do not overlap, so the first
    candidate holding the date is the only one.
    """
    rule = (
        await session.execute(
            select(RoutingRuleRow)
            .join(EnvironmentRow, EnvironmentRow.id == RoutingRuleRow.environment_id)
            .where(RoutingRuleRow.workspace_id == workspace_id, EnvironmentRow.slug == environment)
            .order_by(RoutingRuleRow.written_at.desc(), RoutingRuleRow.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if rule is None:
        return None
    for stored in rule.ranges:
        r = RoutedRange.model_validate(stored)
        if r.effective_from > effective_date or (
            r.effective_to is not None and effective_date >= r.effective_to
        ):
            continue
        pinned = (
            await session.execute(
                select(DeploymentRow.id)
                .join(EnvironmentRow, EnvironmentRow.id == DeploymentRow.environment_id)
                .where(
                    DeploymentRow.id == r.deployment_id,
                    DeploymentRow.workspace_id == workspace_id,
                    EnvironmentRow.slug == environment,
                    DeploymentRow.rating_version_ref == str(r.rating_version_ref),
                )
            )
        ).scalar_one_or_none()
        if pinned is None:
            _log.error(
                "routing range ignored: its pinned Deployment is not a Deployment of this "
                "Environment for that Rating Version",
                extra={
                    "rating_version_ref": str(r.rating_version_ref),
                    "deployment_id": str(r.deployment_id),
                    "workspace_id": str(workspace_id),
                    "environment": environment,
                },
            )
            continue
        return r.rating_version_ref, pinned
    return None
