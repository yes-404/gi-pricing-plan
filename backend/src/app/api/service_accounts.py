"""Service Account management (`07` §5.1, FR-389, FR-392).

| Method | Path |
|---|---|
| `POST` | `/api/v1/service-accounts` — create, key shown **once** |
| `POST` | `/api/v1/service-accounts/{id}/rotate` — new key, old one valid for an overlap |
| `DELETE` | `/api/v1/service-accounts/{id}/keys/{prefix}` — revoke |

The key value appears in exactly one response body in the platform's whole lifetime. Every
other representation carries the prefix only. That is not a UI decision — nothing stores
the secret, so there is nothing to show later even if the API wanted to.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authz import requires
from app.api.deps import Caller
from app.api.responses import problems
from app.auth.api_keys import generate_key
from app.db.models import ApiKeyRow, ServiceAccountRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit
from model_schema import JobSource
from model_schema import Permission as Perm

__all__ = ["router"]

router = APIRouter(prefix="/service-accounts", tags=["platform"])

ManageAccounts = Annotated[Caller, Depends(requires(Perm.ADMIN_MANAGE_SERVICE_ACCOUNTS))]

#: FR-389 scopes service accounts to scoring. A key that could fit a model or approve a
#: rating version would be a standing credential with an actuary's authority.
ALLOWED_PERMISSIONS = frozenset({"score:execute", "score:batch"})

DEFAULT_KEY_LIFETIME_DAYS = 365
DEFAULT_ROTATION_OVERLAP_DAYS = 7


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


class CreateServiceAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")
    description: str | None = None
    environments: list[str] = Field(min_length=1)
    permissions: list[str] = Field(min_length=1)
    rate_limit_rps: int | None = Field(default=None, gt=0)
    expires_in_days: int = Field(default=DEFAULT_KEY_LIFETIME_DAYS, gt=0, le=3650)


class KeyView(BaseModel):
    """A key as it can safely be shown: prefix and dates, never the secret."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    prefix: str
    environment: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    last_used_at: datetime | None = None


class ServiceAccountView(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: str
    description: str | None
    environments: list[str]
    permissions: list[str]
    rate_limit_rps: int | None
    keys: list[KeyView]


class CreatedServiceAccount(BaseModel):
    """The one response that carries a key value (FR-389)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    account: ServiceAccountView
    key: str = Field(
        description="The full key. Shown once and never recoverable — nothing stores it."
    )
    warning: str = "Store this now. It cannot be retrieved again."


def _view(account: ServiceAccountRow, keys: list[ApiKeyRow]) -> ServiceAccountView:
    return ServiceAccountView(
        id=account.id,
        slug=account.slug,
        description=account.description,
        environments=list(account.environments),
        permissions=list(account.permissions),
        rate_limit_rps=account.rate_limit_rps,
        keys=[
            KeyView(
                prefix=k.prefix,
                environment=k.environment,
                created_at=k.created_at,
                expires_at=k.expires_at,
                revoked_at=k.revoked_at,
                last_used_at=k.last_used_at,
            )
            for k in keys
        ],
    )


def _check_permissions(requested: list[str]) -> None:
    unknown = set(requested) - ALLOWED_PERMISSIONS
    if unknown:
        raise PlatformError(
            "VALIDATION_FAILED",
            "Unsupported permission for a service account",
            422,
            f"{sorted(unknown)} is not in {sorted(ALLOWED_PERMISSIONS)}. FR-389 scopes "
            "service accounts to the scoring permission set.",
        )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a service account",
    responses=problems(401, 403, 409, 422),
)
async def create_service_account(
    body: CreateServiceAccount, caller: ManageAccounts, database: DatabaseDep
) -> CreatedServiceAccount:
    """Create the account and its first key. The key is in this response and nowhere else."""
    _check_permissions(body.permissions)

    async with database.unit_of_work() as session:
        existing = (
            await session.execute(
                select(ServiceAccountRow).where(
                    ServiceAccountRow.workspace_id == caller.workspace_id,
                    ServiceAccountRow.slug == body.slug,
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Service account already exists",
                409,
                f"A service account with slug {body.slug!r} already exists.",
            )

        account = ServiceAccountRow(
            workspace_id=caller.workspace_id,
            slug=body.slug,
            description=body.description,
            environments=body.environments,
            permissions=body.permissions,
            rate_limit_rps=body.rate_limit_rps,
        )
        session.add(account)
        await session.flush()

        generated = generate_key(body.environments[0])
        key = ApiKeyRow(
            service_account_id=account.id,
            prefix=generated.prefix,
            secret_hash=generated.secret_hash,
            environment=generated.environment,
            expires_at=datetime.now(UTC) + timedelta(days=body.expires_in_days),
        )
        session.add(key)
        await session.flush()

        # FR-392 / FR-427: the *prefix* is audited, never the secret. An audit log
        # that recorded the value would be a credential store with a retention policy.
        await audit.record(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            source=JobSource.API,
            action="service_account.created",
            entity_ref=f"service_account:{account.slug}@1",
            after={
                "slug": account.slug,
                "environments": list(account.environments),
                "permissions": list(account.permissions),
                "key_prefix": generated.prefix,
            },
        )
        view = _view(account, [key])

    return CreatedServiceAccount(account=view, key=generated.value)


@router.post(
    "/{account_id}/rotate",
    summary="Rotate the key with an overlap window",
    responses=problems(401, 403, 404, 422),
)
async def rotate_key(
    account_id: UUID,
    caller: ManageAccounts,
    database: DatabaseDep,
    overlap_days: Annotated[int, Field(ge=0, le=90)] = DEFAULT_ROTATION_OVERLAP_DAYS,
) -> CreatedServiceAccount:
    """Issue a new key and give the old one a deadline (FR-389).

    The old key keeps working for the overlap window rather than dying immediately. A
    rotation that breaks production the instant it is requested is a rotation nobody
    performs, and an unrotated key is the failure this exists to prevent.
    """
    async with database.unit_of_work() as session:
        account = await _load_scoped(session, account_id, caller)

        current = (
            await session.execute(
                select(ApiKeyRow).where(
                    ApiKeyRow.service_account_id == account.id,
                    ApiKeyRow.revoked_at.is_(None),
                )
            )
        ).scalars().all()

        overlap_until = datetime.now(UTC) + timedelta(days=overlap_days)
        for key in current:
            if key.expires_at > overlap_until:
                key.expires_at = overlap_until

        generated = generate_key(account.environments[0])
        successor = ApiKeyRow(
            service_account_id=account.id,
            prefix=generated.prefix,
            secret_hash=generated.secret_hash,
            environment=generated.environment,
            expires_at=datetime.now(UTC) + timedelta(days=DEFAULT_KEY_LIFETIME_DAYS),
        )
        session.add(successor)
        await session.flush()

        await audit.record(
            session,
            workspace_id=caller.workspace_id,
            actor=caller.principal,
            source=JobSource.API,
            action="service_account.key_rotated",
            entity_ref=f"service_account:{account.slug}@1",
            before={"key_prefixes": [k.prefix for k in current]},
            after={
                "successor_prefix": generated.prefix,
                "overlap_until": overlap_until.isoformat(),
            },
        )
        view = _view(account, [*current, successor])

    return CreatedServiceAccount(account=view, key=generated.value)


@router.delete(
    "/{account_id}/keys/{prefix}",
    status_code=status.HTTP_200_OK,
    summary="Revoke a key immediately",
    responses=problems(401, 403, 404, 422),
)
async def revoke_key(
    account_id: UUID, prefix: str, caller: ManageAccounts, database: DatabaseDep
) -> ServiceAccountView:
    async with database.unit_of_work() as session:
        account = await _load_scoped(session, account_id, caller)
        key = (
            await session.execute(
                select(ApiKeyRow).where(
                    ApiKeyRow.service_account_id == account.id, ApiKeyRow.prefix == prefix
                )
            )
        ).scalar_one_or_none()
        if key is None:
            raise PlatformError(
                "NOT_FOUND", "Key not found", 404, f"No key with prefix {prefix!r}."
            )

        if key.revoked_at is None:
            key.revoked_at = datetime.now(UTC)
            await session.flush()
            await audit.record(
                session,
                workspace_id=caller.workspace_id,
                actor=caller.principal,
                source=JobSource.API,
                action="service_account.key_revoked",
                entity_ref=f"service_account:{account.slug}@1",
                after={"key_prefix": prefix},
            )

        keys = (
            await session.execute(
                select(ApiKeyRow).where(ApiKeyRow.service_account_id == account.id)
            )
        ).scalars().all()
        return _view(account, list(keys))


async def _load_scoped(
    session: AsyncSession, account_id: UUID, caller: Caller
) -> ServiceAccountRow:
    account: ServiceAccountRow | None = await session.get(ServiceAccountRow, account_id)
    if account is None or account.workspace_id != caller.workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Service account not found", 404, f"No account with id {account_id}."
        )
    return account
