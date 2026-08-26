"""The unauthenticated OIDC bootstrap values the browser login needs (FR-PLAT-66).

One route, built the way `/version` is (`health.version_route`, `main.py:124-131`): a
closure bound to the loaded settings, mounted in `main.py`. Deliberately **no** auth
dependency — the channel exists because the flow cannot start with an auth gate, and
nothing here is a credential.
"""

from __future__ import annotations

from collections.abc import Callable

from app.config import Settings
from model_schema import OidcAuthConfig

__all__ = ["auth_config_route"]


def auth_config_route(settings: Settings) -> Callable[[], OidcAuthConfig]:
    """Build the `/api/v1/auth/config` handler bound to the loaded settings."""

    def auth_config() -> OidcAuthConfig:
        return OidcAuthConfig(
            issuer=settings.oidc_issuer,
            client_id=settings.oidc_client_id,
            dev_auth_enabled=settings.dev_auth_enabled,
        )

    return auth_config
