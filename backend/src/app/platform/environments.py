"""The Environment record (`07` §4.2, FR-428; WK-674 Slice 2, `PL-1392` Task 4).

An **Environment** is a named place a Rating Version is deployed to. It is deployment-wide,
not per workspace (ADR-710), so its row has no `workspace_id`; the Audit Event of a write is
written in the caller's workspace, the only chain a caller has.

**The slug is the Environment's identity** (`RL-1301` A.6). It is immutable and unique across
every row, retired ones included, so a slug is never reissued and a stored
`deployment:<slug>@n` reference can never come to name another Environment. Only `name` and
`description` change. A retirement keeps the row.

**"Existing" means non-retired** (auditor-plans N3). `require_existing` is the one check that
`set_policy` and the Service Account credential routes both call, so the three cannot
disagree about what an Environment is.

**`live_deployments` is derived**, never stored (`07` §4.2): the latest Deployment of the
caller's workspace in that Environment (`03` §4.12: "The live Deployment of an Environment is
derived from these rows"). It reads `DeploymentRow`; this module never writes one.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.pagination import COUNT_CAP, Page, decode_cursor, encode_cursor
from app.db.models import (
    ApiKeyRow,
    ApprovalPolicyRow,
    DeploymentRow,
    EnvironmentRow,
    WorkspaceRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit
from model_schema import (
    DEFAULT_POLICY,
    ArtifactRef,
    Environment,
    EnvironmentCreate,
    EnvironmentUpdate,
    JobSource,
    LiveDeployment,
    Principal,
)

__all__ = [
    "create_environment",
    "list_environments",
    "live_rating_version_ref",
    "require_existing",
    "retire_environment",
    "update_environment",
]


def _not_found(slug: str) -> PlatformError:
    return PlatformError(
        "NOT_FOUND", "Environment not found", 404, f"No environment with slug {slug!r}."
    )


async def _live_by_environment(
    session: AsyncSession, workspace_id: UUID, environment_ids: list[UUID]
) -> dict[UUID, DeploymentRow]:
    """The latest Deployment of each Environment, in one workspace."""
    if not environment_ids:
        return {}
    rows = (
        await session.scalars(
            select(DeploymentRow)
            .where(
                DeploymentRow.workspace_id == workspace_id,
                DeploymentRow.environment_id.in_(environment_ids),
            )
            .order_by(DeploymentRow.deployed_at.desc(), DeploymentRow.id.desc())
        )
    ).all()
    latest: dict[UUID, DeploymentRow] = {}
    for row in rows:
        latest.setdefault(row.environment_id, row)
    return latest


async def live_rating_version_ref(
    session: AsyncSession, *, workspace_id: UUID, environment_slug: str
) -> str | None:
    """The Rating Version ref live in one Environment, or `None` (nothing deployed there, or
    no such Environment).

    FR-257 limb (2)'s baseline reader (`03` FR-257's 2026-10-10 clarification, RL-1504 T3):
    the one public resolution of "live", beside `_live_by_environment`, which stays private.
    """
    environment_id = await session.scalar(
        select(EnvironmentRow.id).where(EnvironmentRow.slug == environment_slug)
    )
    if environment_id is None:
        return None
    live = (await _live_by_environment(session, workspace_id, [environment_id])).get(
        environment_id
    )
    return None if live is None else live.rating_version_ref


def _to_model(row: EnvironmentRow, live: DeploymentRow | None) -> Environment:
    return Environment(
        slug=row.slug,
        name=row.name,
        description=row.description,
        promotion_order=row.promotion_order,
        requires_prior_environment=row.requires_prior_environment,
        retired_at=row.retired_at,
        live_deployments=()
        if live is None
        else (
            LiveDeployment(
                rating_version_ref=ArtifactRef.parse(live.rating_version_ref),
                deployed_at=live.deployed_at,
                bundle_hash=live.bundle_hash,
            ),
        ),
    )


def _state(row: EnvironmentRow) -> dict[str, Any]:
    """What an Audit Event records of an Environment: its record fields, not its derived ones."""
    return {
        "slug": row.slug,
        "name": row.name,
        "description": row.description,
        "promotion_order": row.promotion_order,
        "requires_prior_environment": row.requires_prior_environment,
        "retired_at": row.retired_at.isoformat() if row.retired_at else None,
    }


async def _load(session: AsyncSession, slug: str, *, lock: bool = False) -> EnvironmentRow:
    query = select(EnvironmentRow).where(EnvironmentRow.slug == slug)
    if lock:
        query = query.with_for_update()
    row = (await session.execute(query)).scalar_one_or_none()
    if row is None:
        raise _not_found(slug)
    return row


async def require_existing(session: AsyncSession, slug: str, *, subject: str) -> EnvironmentRow:
    """The Environment named `slug`, or a 422 `VALIDATION_FAILED` naming it.

    A retired Environment is refused as an unknown one: it exists as a record and not as a
    target (N3). `subject` says what named it, so the refusal reads as that caller's.
    """
    row = (
        await session.execute(select(EnvironmentRow).where(EnvironmentRow.slug == slug))
    ).scalar_one_or_none()
    if row is None or row.retired_at is not None:
        reason = "is retired" if row is not None else "is not an Environment"
        raise PlatformError(
            "VALIDATION_FAILED",
            "Unknown environment",
            422,
            f"{subject} names {slug!r}, which {reason}. An Environment must exist and not be "
            "retired (`07` FR-428, `RL-1301` A.6); a name no Environment has would "
            "ungate or strand the target it was meant to name.",
        )
    return row


async def list_environments(
    database: Database, workspace_id: UUID, cursor: str | None, limit: int
) -> Page[Environment]:
    """Every Environment, retired ones included, in promotion order then id order."""
    after = decode_cursor(cursor)
    async with database.session() as session:
        ordered = select(EnvironmentRow).order_by(
            EnvironmentRow.promotion_order, EnvironmentRow.id
        )
        total = len(
            (await session.scalars(select(EnvironmentRow.id).limit(COUNT_CAP))).all()
        )
        everything = list((await session.scalars(ordered)).all())
        if after is not None:
            position = next((i for i, r in enumerate(everything) if r.id == after), None)
            if position is None:
                raise PlatformError(
                    "VALIDATION_FAILED",
                    "Malformed cursor",
                    400,
                    "The cursor is not one this API issued. Omit it to start from the beginning.",
                )
            everything = everything[position + 1 :]
        page = everything[:limit]
        live = await _live_by_environment(session, workspace_id, [r.id for r in page])
    return Page[Environment](
        items=[_to_model(r, live.get(r.id)) for r in page],
        next_cursor=encode_cursor(page[-1].id) if len(everything) > limit else None,
        total_estimate=total,
    )


async def create_environment(
    database: Database, workspace_id: UUID, actor: Principal, body: EnvironmentCreate
) -> Environment:
    async with database.unit_of_work() as session:
        existing = (
            await session.execute(select(EnvironmentRow).where(EnvironmentRow.slug == body.slug))
        ).scalar_one_or_none()
        if existing is not None:
            how = "was retired and its slug is never reissued" if existing.retired_at else "exists"
            raise PlatformError(
                "VALIDATION_FAILED",
                "Environment already exists",
                409,
                f"Environment {body.slug!r} {how} (`RL-1301` A.6: otherwise an old "
                f"`deployment:{body.slug}@n` reference would name a different Environment).",
            )
        if body.requires_prior_environment is not None:
            await require_existing(
                session,
                body.requires_prior_environment,
                subject="`requires_prior_environment`",
            )
        row = EnvironmentRow(
            slug=body.slug,
            name=body.name,
            description=body.description,
            promotion_order=body.promotion_order,
            requires_prior_environment=body.requires_prior_environment,
        )
        session.add(row)
        await session.flush()
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=actor,
            source=JobSource.API,
            action="environment.created",
            entity_ref=f"environment:{row.slug}",
            after=_state(row),
        )
        return _to_model(row, None)


async def update_environment(
    database: Database,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    body: EnvironmentUpdate,
) -> Environment:
    """Rename: `name` and `description` only. The slug is not in the body's shape."""
    async with database.unit_of_work() as session:
        row = await _load(session, slug, lock=True)
        _require_not_retired(row, "renamed")
        before = _state(row)
        if body.name is not None:
            row.name = body.name
        if body.description is not None:
            row.description = body.description
        await session.flush()
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=actor,
            source=JobSource.API,
            action="environment.updated",
            entity_ref=f"environment:{row.slug}",
            before=before,
            after=_state(row),
        )
        live = await _live_by_environment(session, workspace_id, [row.id])
        return _to_model(row, live.get(row.id))


def _require_not_retired(row: EnvironmentRow, verb: str) -> None:
    if row.retired_at is not None:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Environment is retired",
            409,
            f"Environment {row.slug!r} was retired at {row.retired_at.isoformat()} and "
            f"cannot be {verb}.",
        )


async def _blockers(session: AsyncSession, row: EnvironmentRow) -> list[str]:
    """Everything that still names the Environment, as sentences for a refusal."""
    blockers: list[str] = []

    latest = await _live_by_environment_any_workspace(session, row.id)
    if latest:
        refs = ", ".join(sorted({d.rating_version_ref for d in latest}))
        blockers.append(f"a Deployment is live in it ({refs})")

    named = False
    stored = (await session.scalars(select(ApprovalPolicyRow))).all()
    for policy in stored:
        for entry in policy.policy.get("policies", []):
            if entry.get("artifact_type") == "deployment" and entry.get("environment") == row.slug:
                named = True
    if not named:
        # A workspace holding no policy row is under `DEFAULT_POLICY`, which names `prod`.
        lacking = await session.scalar(
            select(WorkspaceRow.id)
            .where(WorkspaceRow.id.not_in(select(ApprovalPolicyRow.workspace_id)))
            .limit(1)
        )
        if lacking is not None:
            named = any(
                p.artifact_type == "deployment" and p.environment == row.slug
                for p in DEFAULT_POLICY.policies
            )
    if named:
        blockers.append(
            f"a `deployment` approval policy entry names it (remove the entry for "
            f"{row.slug!r} first)"
        )

    prefixes = (
        await session.scalars(
            select(ApiKeyRow.prefix).where(
                ApiKeyRow.environment == row.slug, ApiKeyRow.revoked_at.is_(None)
            )
        )
    ).all()
    if prefixes:
        blockers.append(
            f"unrevoked Service Account keys name it ({', '.join(sorted(prefixes))}); "
            "revoke them first"
        )
    return blockers


async def _live_by_environment_any_workspace(
    session: AsyncSession, environment_id: UUID
) -> list[DeploymentRow]:
    """The latest Deployment of the Environment in each workspace that has one."""
    rows = (
        await session.scalars(
            select(DeploymentRow)
            .where(DeploymentRow.environment_id == environment_id)
            .order_by(DeploymentRow.deployed_at.desc(), DeploymentRow.id.desc())
        )
    ).all()
    latest: dict[UUID, DeploymentRow] = {}
    for row in rows:
        latest.setdefault(row.workspace_id, row)
    return list(latest.values())


async def retire_environment(
    database: Database, workspace_id: UUID, actor: Principal, slug: str
) -> Environment:
    """Retire: refused while a Deployment is live in it, a policy entry names it, or an
    unrevoked key names it. The row and its slug are kept."""
    async with database.unit_of_work() as session:
        row = await _load(session, slug, lock=True)
        _require_not_retired(row, "retired again")
        blockers = await _blockers(session, row)
        if blockers:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Environment still in use",
                409,
                f"Environment {slug!r} cannot be retired: " + "; ".join(blockers) + ".",
            )
        before = _state(row)
        row.retired_at = datetime.now(UTC)
        await session.flush()
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=actor,
            source=JobSource.API,
            action="environment.retired",
            entity_ref=f"environment:{row.slug}",
            before=before,
            after=_state(row),
        )
        return _to_model(row, None)
