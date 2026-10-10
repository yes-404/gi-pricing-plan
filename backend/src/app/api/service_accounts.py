"""Service Account management (`07` §5.1, FR-389, FR-392).

| Method | Path |
|---|---|
| `POST` | `/api/v1/service-accounts` — create, one key per granted Environment, shown **once** |
| `POST` | `/api/v1/service-accounts/{id}/rotate` — a new key for one named Environment |
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
from app.auth.api_keys import GeneratedKey, generate_key
from app.db.models import ApiKeyRow, ServiceAccountRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import audit, environments
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


class IssuedKey(BaseModel):
    """One key's secret, for the Environment it was issued for (FR-430)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: str
    prefix: str
    key: str = Field(
        description="The full key. Shown once and never recoverable — nothing stores it."
    )


class RotateKey(BaseModel):
    """FR-430: rotation acts on the key of one named Environment (DP-S3E-2 (a))."""

    model_config = ConfigDict(extra="forbid")

    environment: str


class CreatedServiceAccount(BaseModel):
    """The one response that carries key values (FR-389).

    `keys` always lists what was issued, one per Environment. `key` is the secret when
    exactly one key was issued and `None` otherwise (DP-S3E-1 (b)): a caller granted
    several Environments has no "first" secret to take.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    account: ServiceAccountView
    keys: list[IssuedKey]
    key: str | None = Field(
        description="The secret of the one key issued, when exactly one was; otherwise null."
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


async def _check_environments(session: AsyncSession, requested: list[str]) -> None:
    """Every granted environment must be an existing, non-retired Environment slug.

    `RL-1301` A.6: a key minted from a name no Environment has (`prd` for `prod`) would be a
    credential for a target that does not exist, and the check is made at creation and at
    rotation, the two places a key is minted from `environments[0]`.
    """
    for slug in requested:
        await environments.require_existing(
            session, slug, subject="A Service Account's `environments`"
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
    """Create the account and one key per granted Environment (FR-430).

    The keys are in this response and nowhere else.
    """
    _check_permissions(body.permissions)

    async with database.unit_of_work() as session:
        await _check_environments(session, body.environments)
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

        generated_keys = [generate_key(slug) for slug in dict.fromkeys(body.environments)]
        rows = [
            ApiKeyRow(
                service_account_id=account.id,
                prefix=g.prefix,
                secret_hash=g.secret_hash,
                environment=g.environment,
                expires_at=datetime.now(UTC) + timedelta(days=body.expires_in_days),
            )
            for g in generated_keys
        ]
        session.add_all(rows)
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
                "key_prefixes": {g.environment: g.prefix for g in generated_keys},
            },
        )
        view = _view(account, rows)

    return _created(view, generated_keys)


@router.post(
    "/{account_id}/rotate",
    summary="Rotate the key with an overlap window",
    responses=problems(401, 403, 404, 422),
)
async def rotate_key(
    account_id: UUID,
    body: RotateKey,
    caller: ManageAccounts,
    database: DatabaseDep,
    overlap_days: Annotated[int, Field(ge=0, le=90)] = DEFAULT_ROTATION_OVERLAP_DAYS,
) -> CreatedServiceAccount:
    """Issue a new key for one Environment and give that Environment's old one a deadline.

    The old key keeps working for the overlap window rather than dying immediately. A
    rotation that breaks production the instant it is requested is a rotation nobody
    performs, and an unrotated key is the failure this exists to prevent.
    """
    async with database.unit_of_work() as session:
        account = await _load_scoped(session, account_id, caller)
        if body.environment not in account.environments:
            raise PlatformError(
                "VALIDATION_FAILED",
                "Environment not granted",
                422,
                f"The account is not granted {body.environment!r}; granted: "
                f"{sorted(account.environments)}.",
            )
        await _check_environments(session, [body.environment])

        current = (
            await session.execute(
                select(ApiKeyRow).where(
                    ApiKeyRow.service_account_id == account.id,
                    ApiKeyRow.environment == body.environment,
                    ApiKeyRow.revoked_at.is_(None),
                )
            )
        ).scalars().all()

        overlap_until = datetime.now(UTC) + timedelta(days=overlap_days)
        for key in current:
            if key.expires_at > overlap_until:
                key.expires_at = overlap_until

        generated = generate_key(body.environment)
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
            before={"environment": body.environment, "key_prefixes": [k.prefix for k in current]},
            after={
                "environment": body.environment,
                "successor_prefix": generated.prefix,
                "overlap_until": overlap_until.isoformat(),
            },
        )
        view = _view(account, [*current, successor])

    return _created(view, [generated])


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


def _created(view: ServiceAccountView, generated: list[GeneratedKey]) -> CreatedServiceAccount:
    keys = [
        IssuedKey(environment=g.environment, prefix=g.prefix, key=g.value) for g in generated
    ]
    return CreatedServiceAccount(
        account=view, keys=keys, key=keys[0].key if len(keys) == 1 else None
    )


async def _load_scoped(
    session: AsyncSession, account_id: UUID, caller: Caller
) -> ServiceAccountRow:
    account: ServiceAccountRow | None = await session.get(ServiceAccountRow, account_id)
    if account is None or account.workspace_id != caller.workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Service account not found", 404, f"No account with id {account_id}."
        )
    return account
