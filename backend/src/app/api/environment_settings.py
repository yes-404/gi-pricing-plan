"""Environment settings routes (`07` §5.1, FR-431, FR-446; WK-674 Slice 3, `PL-1583`).

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/environments/{slug}/settings` | Effective values, every layer's candidate |
| `PUT` | `/api/v1/environments/{slug}/settings` | Update Environment settings (audited) |

A write validates each value against the key's declared type, constraints and scope, writes
the row and records one Audit Event naming the Environment, the key, and the old and new
values, in one transaction (`06` R2, FR-431). The body is `PUT /settings`' own.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep
from app.api.responses import problems
from app.api.settings import UpdateSettings
from app.platform import audit
from app.platform import settings as setting_service
from model_schema import JobSource, SettingResolution
from model_schema import Permission as Perm

__all__ = ["router"]

router = APIRouter(prefix="/environments", tags=["platform"])

ReadSettings = Annotated[Caller, Depends(requires(Perm.SETTINGS_READ))]
ManageSettings = Annotated[Caller, Depends(requires(Perm.ADMIN_MANAGE_SETTINGS))]


@router.get(
    "/{slug}/settings",
    summary="Effective settings for one environment with every layer's candidate",
    responses=problems(401, 403, 404),
)
async def get_environment_settings(
    slug: str, caller: ReadSettings, database: DatabaseDep, request: Request
) -> list[SettingResolution]:
    async with database.session() as session:
        await setting_service.require_environment(session, slug)
        return await setting_service.resolve_all(
            session, request.app.state.settings, caller.workspace_id, slug
        )


@router.put(
    "/{slug}/settings",
    summary="Update environment settings",
    status_code=status.HTTP_200_OK,
    responses=problems(401, 403, 404, 422),
)
async def update_environment_settings(
    slug: str,
    body: UpdateSettings,
    caller: ManageSettings,
    database: DatabaseDep,
    request: Request,
) -> list[SettingResolution]:
    """Validate, write and audit each change in one transaction (FR-431)."""
    settings = request.app.state.settings
    async with database.unit_of_work() as session:
        for key, value in body.values.items():
            definition, before = await setting_service.set_environment_setting(
                session, slug, key, value, caller.principal.id
            )
            await audit.record(
                session,
                workspace_id=caller.workspace_id,
                actor=caller.principal,
                source=JobSource.API,
                action="setting.updated",
                entity_ref=f"setting:{key.replace('.', '-')}@1",
                before={"environment": slug, "key": key, "value": before},
                after={"environment": slug, "key": key, "value": definition.coerce(value)},
            )
        return await setting_service.resolve_all(
            session, settings, caller.workspace_id, slug
        )
