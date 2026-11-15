"""The uniform history of a governed artifact (`06` FR-383, §5.1).

One route, one shape for every artifact type: it reads the audit log by exact `entity_ref`,
so it needs nothing from the modules that own the types (`06` §7.1, DEP-1).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError

from app.api.authz import requires
from app.api.deps import Caller
from app.api.responses import problems
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit as audit_service
from model_schema import ArtifactHistory, ArtifactRef, Permission

__all__ = ["router"]

router = APIRouter(prefix="/artifacts", tags=["governance"])

ReadAudit = Annotated[Caller, Depends(requires(Permission.AUDIT_READ))]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


@router.get(
    "/{ref}/history",
    summary="The uniform history of one artifact version (FR-383)",
    responses=problems(401, 403, 404, 422),
)
async def artifact_history(
    ref: str, caller: ReadAudit, database: Annotated[Database, Depends(_database)]
) -> ArtifactHistory:
    """Events, oldest first, for exactly `{ref}` (`{type}:{slug}@{version}`).

    `422` when `{ref}` is not an artifact reference; `404` when the log holds no event for it
    in this workspace. Every artifact type's creation emits an event, so a real artifact
    always has a history.
    """
    try:
        parsed = ArtifactRef.model_validate(ref)
    except ValidationError as exc:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Not an artifact reference",
            422,
            "`{ref}` must have the form {type}:{slug}@{version}.",
        ) from exc
    async with database.session() as session:
        history = await audit_service.artifact_history(session, caller.workspace_id, parsed)
    if not history.events:
        raise PlatformError(
            "NOT_FOUND", "No recorded history", 404, f"No audit event is recorded for {parsed}."
        )
    return history
