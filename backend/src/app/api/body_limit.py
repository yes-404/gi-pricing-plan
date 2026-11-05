"""A request-body limit on the two upload routes (FR-450, FD-1802)."""

from __future__ import annotations

from starlette.types import ASGIApp, Receive, Scope, Send

__all__ = ["CAPPED_ROUTES", "BodyLimitMiddleware"]

CAPPED_ROUTES: tuple[str, ...] = ()


class BodyLimitMiddleware:
    """Placeholder: passes every request through. Replaced in the green commit."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.app(scope, receive, send)
