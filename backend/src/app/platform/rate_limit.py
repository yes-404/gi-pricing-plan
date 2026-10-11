"""The scoring rate limit (`07` FR-452, FR-430; `RL-1347`; WK-674 Slice 3).

One counter per (route class, Environment, Principal) per fixed one-second window, held in
the tenant's Redis so that every replica counts into the same number — an in-process limiter
"is not a limit" (register F48). The module is route-class aware (`route`), so that Slice 4 can
reuse it for the management API under a separate key and limit (`PL-1537` R4.1); this slice
passes only `"score"`.

**Fail open.** Any `RedisError` admits the request, logs one warning that carries the error
type and the Environment only, and counts on `gip_rate_limit_unenforced_total`. A rate limit
is a capacity control, not the security boundary: authentication and the Environment check
still run on every request. A request is never refused because the counter is down.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Final
from uuid import UUID

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import Settings
from app.db.session import Database
from app.errors import PlatformError
from app.observability import metrics
from app.observability.logging import get_logger
from app.platform import settings as settings_service
from model_schema import Principal

__all__ = ["RateLimiter", "build_redis_client", "enforce", "refusal"]

_log = get_logger("app.platform.rate_limit")

#: The 2-second expiry only removes old windows; the window itself is in the key, so a crash
#: between `INCR` and `EXPIRE` cannot lock a client out (RL-1347 rule 3).
_KEY_TTL_SECONDS: Final = 2

#: RL-1347 rule 5: a hung Redis costs a request at most about 100 ms, and only while it is down.
_SOCKET_TIMEOUT_SECONDS: Final = 0.05


def build_redis_client(url: str) -> Redis:
    """The process-wide client, built once in the lifespan (never per request)."""
    client: Redis = Redis.from_url(
        url,
        socket_connect_timeout=_SOCKET_TIMEOUT_SECONDS,
        socket_timeout=_SOCKET_TIMEOUT_SECONDS,
    )
    return client


def refusal(limit: int) -> PlatformError:
    """The 429 `RATE_LIMITED` problem. Names the limit and the window, nothing of the request."""
    return PlatformError(
        "RATE_LIMITED",
        "Rate limit exceeded",
        429,
        f"More than {limit} requests in one second.",
        headers={"Retry-After": "1"},
    )


class RateLimiter:
    """A fixed one-second window counter in Redis, failing open."""

    def __init__(
        self, client: Redis, *, clock: Callable[[], float] = time.time
    ) -> None:
        self._client = client
        #: Read once per request. A test sets it to fix the window, so a run cannot straddle a
        #: second boundary and flake.
        self.clock = clock

    @staticmethod
    def key(
        route: str, environment: str | None, principal_kind: str, principal_id: UUID | None,
        window: int,
    ) -> str:
        return (
            f"gip:ratelimit:{route}:{environment or ''}:{principal_kind}:{principal_id}:{window}"
        )

    async def admit(
        self, route: str, environment: str | None, principal: Principal, limit: int
    ) -> bool:
        """Count this request; `True` if it is within `limit` (or the counter is down).

        A refused request is counted too: it arrived in that second.
        """
        key = self.key(
            route, environment, principal.kind.value, principal.id, int(self.clock())
        )
        try:
            async with self._client.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.expire(key, _KEY_TTL_SECONDS)
                count, _ = await pipe.execute()
        except RedisError as exc:
            metrics.rate_limit_unenforced.labels(environment=environment or "").inc()
            _log.warning(
                "rate limit not enforced: %s",
                type(exc).__name__,
                extra={"environment": environment or ""},
            )
            return True
        return bool(count <= limit)


async def enforce(
    limiter: RateLimiter,
    database: Database,
    settings: Settings,
    *,
    route: str,
    default_setting: str,
    workspace_id: UUID,
    environment: str | None,
    principal: Principal,
    account_limit: int | None,
) -> None:
    """Refuse with 429 when the caller is over its limit; otherwise return.

    The limit is the account's own `rate_limit_rps` when set, else the Setting
    `default_setting` resolved for the caller's Environment, else none — and with none the
    request is admitted without a counter call (RL-1347 rule 2).
    """
    limit = account_limit
    if limit is None:
        async with database.session() as session:
            resolved = await settings_service.resolve(
                session, settings, workspace_id, default_setting, environment
            )
        limit = resolved.effective_value
    if limit is None:
        return
    if not await limiter.admit(route, environment, principal, limit):
        raise refusal(limit)
