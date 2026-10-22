"""The Environment's shadow configuration (`03` §4.13, FR-271, FR-272; WK-674 Slice 6,
`RL-1834` D2).

The configuration is written whole and appended: the latest `shadow_configs` row of an
Environment is current. It is written only here, under `admin:manage_settings` with the
Environment as the resource, so the candidate is always checked against the database (this
workspace, not `draft`, compiled) and the history is kept. The candidate need not be deployed:
shadow scoring is the pre-deployment net. It never prices a quote, so this permission does not
breach the rule that nothing guarded by `admin:manage_settings` changes a live price.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EnvironmentRow, RatingVersionRow, ShadowConfigRow, ShadowResultRow
from app.errors import PlatformError
from app.platform import audit, environments, rbac
from app.platform.deployments import _require_rating_version
from model_schema import (
    ArtifactRef,
    ScoringResult,
    JobSource,
    Permission,
    Principal,
    ScopeType,
    ShadowConfig,
    ShadowConfigUpdate,
    new_uuid7,
)

__all__ = ["current", "record_result", "write_config"]

_ACTION = "deployment.shadow_configured"


def _to_config(row: ShadowConfigRow, slug: str) -> ShadowConfig:
    return ShadowConfig(
        environment=slug,
        candidate_rating_version_ref=ArtifactRef.parse(row.candidate_rating_version_ref),
        candidate_bundle_hash=row.candidate_bundle_hash,
        fraction=row.fraction,
        written_by=row.written_by,
        written_at=row.written_at,
    )


async def write_config(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    environment: str,
    body: ShadowConfigUpdate,
    count_management: Callable[[], Awaitable[None]] | None = None,
) -> ShadowConfig:
    """Write the Environment's shadow configuration. Refusals, each writing nothing and no
    Audit Event: unknown Environment 404; no `admin:manage_settings` on it 403; retired 409
    `VALIDATION_FAILED`; a reference that is not a Rating Version, names none of this workspace,
    or names a `draft` one 422 `VALIDATION_FAILED`; no compiled bundle 409
    `BUNDLE_COMPILE_FAILED`. A fraction outside `(0, 1]` is refused by the body's own shape."""
    env = await environments._load(session, environment)
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.ADMIN_MANAGE_SETTINGS,
        resource=rbac.ResourceRef(scope_type=ScopeType.ENVIRONMENT, scope_id=env.id),
    )
    if count_management is not None:
        await count_management()
    environments._require_not_retired(env, "configured for shadow scoring")
    ref = body.candidate_rating_version_ref
    _require_rating_version(ref, what="A shadow candidate")
    candidate = (
        await session.execute(
            select(RatingVersionRow).where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == ref.slug,
                RatingVersionRow.version == ref.version,
            )
        )
    ).scalar_one_or_none()
    if candidate is None or candidate.status == "draft":
        why = "names no Rating Version of this workspace" if candidate is None else "is a draft"
        raise PlatformError(
            "VALIDATION_FAILED",
            "Not a usable shadow candidate",
            422,
            f"{ref} {why}. A shadow candidate is a compiled Rating Version that has left "
            "`draft`, so its results attach to one fixed bundle.",
        )
    content_hash = (candidate.bundle or {}).get("content_hash")
    if not content_hash:
        raise PlatformError(
            "BUNDLE_COMPILE_FAILED",
            "The Rating Version has no compiled Bundle",
            409,
            f"{ref} has no `content_hash`, so there is no Bundle to shadow-score against.",
        )
    previous = (
        await session.execute(
            select(ShadowConfigRow)
            .where(
                ShadowConfigRow.workspace_id == workspace_id,
                ShadowConfigRow.environment_id == env.id,
            )
            .order_by(ShadowConfigRow.written_at.desc(), ShadowConfigRow.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    row = ShadowConfigRow(
        id=new_uuid7(),
        workspace_id=workspace_id,
        environment_id=env.id,
        candidate_rating_version_ref=str(ref),
        candidate_bundle_hash=str(content_hash),
        fraction=body.fraction,
        written_by=actor.id,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)
    config = _to_config(row, env.slug)
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=_ACTION,
        entity_ref=f"environment:{env.slug}",
        before=None if previous is None else _to_config(previous, env.slug).model_dump(mode="json"),
        after=config.model_dump(mode="json"),
    )
    return config


#: Not content: the trace is a debugging aid and `timing_ms` is the wall clock, so two calls
#: never agree on it. A shadow result holds the premiums exactly as `ScoringResult` does.
_NOT_CONTENT = {"trace", "timing_ms"}


async def current(
    session: AsyncSession, *, workspace_id: UUID, environment: str
) -> tuple[ArtifactRef, float] | None:
    """The Environment's current candidate and sampling fraction, or `None` if none was written.
    One read through the caller's session (`RL-1834` D2 item 4)."""
    row = (
        await session.execute(
            select(ShadowConfigRow)
            .join(EnvironmentRow, EnvironmentRow.id == ShadowConfigRow.environment_id)
            .where(ShadowConfigRow.workspace_id == workspace_id, EnvironmentRow.slug == environment)
            .order_by(ShadowConfigRow.written_at.desc(), ShadowConfigRow.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if row is None:
        return None
    return ArtifactRef.parse(row.candidate_rating_version_ref), row.fraction


async def record_result(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    environment: str,
    live_deployment_id: UUID | None,
    live: ScoringResult,
    candidate: ScoringResult,
) -> None:
    """Append one `shadow_results` row (`RL-1834` D2 item 5). It holds the two results and no
    Quote Context, so it is not a quote-input store (NFR-499)."""
    env_id = (
        await session.execute(select(EnvironmentRow.id).where(EnvironmentRow.slug == environment))
    ).scalar_one()
    session.add(
        ShadowResultRow(
            id=new_uuid7(),
            workspace_id=workspace_id,
            environment_id=env_id,
            live_deployment_id=live_deployment_id,
            live_result=live.model_dump(mode="json", exclude=_NOT_CONTENT),
            candidate_result=candidate.model_dump(mode="json", exclude=_NOT_CONTENT),
        )
    )
    await session.flush()
