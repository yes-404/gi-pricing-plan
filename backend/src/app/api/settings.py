"""Settings API (`07` §5.1, FR-PLAT-43..46).

| Method | Path |
|---|---|
| `GET` | `/api/v1/settings` — effective values with their resolution source |
| `PUT` | `/api/v1/settings` — update workspace settings (audited) |

Reads show the whole resolution, not the winning value: FR-PLAT-43 requires the source to
be inspectable, and an Admin asked "why is the PSI threshold 0.25 here?" needs to see which
layer said so.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.authz import requires
from app.api.deps import Caller
from app.api.responses import problems
from app.db.session import Database
from app.platform import audit
from app.platform import settings as setting_service
from model_schema import JobSource, SettingResolution
from model_schema import Permission as Perm

__all__ = ["router"]

router = APIRouter(prefix="/settings", tags=["platform"])

ReadSettings = Annotated[Caller, Depends(requires(Perm.SETTINGS_READ))]
ManageSettings = Annotated[Caller, Depends(requires(Perm.ADMIN_MANAGE_SETTINGS))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


def _settings(request: Request) -> Any:
    return request.app.state.settings


DatabaseDep = Annotated[Database, Depends(_database)]


class UpdateSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    values: dict[str, Any] = Field(
        description="Setting key to value. Only declared keys are accepted; an unknown key "
        "is a 404 rather than a silently stored value nothing will ever read."
    )


@router.get(
    "",
    summary="Effective settings with their resolution source",
    responses=problems(401, 403),
)
async def get_settings(
    caller: ReadSettings, database: DatabaseDep, request: Request
) -> list[SettingResolution]:
    async with database.session() as session:
        return await setting_service.resolve_all(
            session, _settings(request), caller.workspace_id
        )


@router.put(
    "",
    summary="Update workspace settings",
    status_code=status.HTTP_200_OK,
    responses=problems(401, 403, 404, 422),
)
async def update_settings(
    body: UpdateSettings, caller: ManageSettings, database: DatabaseDep, request: Request
) -> list[SettingResolution]:
    """Validate, write and audit each change in one transaction (`06` R2, FR-PLAT-31)."""
    async with database.unit_of_work() as session:
        for key, value in body.values.items():
            before = await setting_service.resolve(
                session, _settings(request), caller.workspace_id, key
            )
            await setting_service.set_workspace_setting(
                session, caller.workspace_id, key, value
            )
            await audit.record(
                session,
                workspace_id=caller.workspace_id,
                actor=caller.principal,
                source=JobSource.API,
                action="setting.updated",
                entity_ref=f"setting:{key.replace('.', '-')}@1",
                before={"effective_value": before.effective_value,
                        "resolved_from": before.resolved_from.value},
                after={"workspace_value": value},
            )
        return await setting_service.resolve_all(
            session, _settings(request), caller.workspace_id
        )
