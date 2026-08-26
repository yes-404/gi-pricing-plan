"""The values the browser OIDC login needs before it can start (`07` FR-PLAT-66).

Public by design: the issuer and the client_id are what a *public* client publishes
(FR-PLAT-55, OQ-PLAT-6), and nothing here is a credential.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

__all__ = ["OidcAuthConfig"]


class OidcAuthConfig(BaseModel):
    """The unauthenticated `/api/v1/auth/config` payload — `07` §5.1."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    issuer: str
    client_id: str
    dev_auth_enabled: bool
