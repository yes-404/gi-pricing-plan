"""FR-PLAT-66 — the unauthenticated values the browser login needs to start.

The channel exists because the flow cannot start with an auth gate: the issuer and the
client_id are what a *public* client publishes, and nothing here is a credential.
"""

import pytest
from fastapi.testclient import TestClient

from app.config import Environment, Settings
from app.main import create_app


@pytest.mark.req("FR-PLAT-66")
def test_the_auth_config_publishes_the_flow_s_bootstrap_values() -> None:
    app = create_app(
        Settings(
            environment=Environment.LOCAL,
            version="test",
            oidc_issuer="https://idp.example/realms/gip",
            oidc_client_id="gi-pricing-frontend",
            dev_auth_enabled=True,
        )
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        body = client.get("/api/v1/auth/config").json()
    assert body == {
        "issuer": "https://idp.example/realms/gip",
        "client_id": "gi-pricing-frontend",
        "dev_auth_enabled": True,
    }


@pytest.mark.req("FR-PLAT-66")
def test_the_auth_config_answers_with_no_credential_at_all(client: TestClient) -> None:
    """The flow cannot start with an auth gate — no dependency, so no 401, no dev header."""
    body = client.get("/api/v1/auth/config").json()
    assert body == {"issuer": "", "client_id": "", "dev_auth_enabled": False}


@pytest.mark.req("FR-PLAT-66")
def test_the_auth_config_is_published_in_the_contract(api_client: TestClient) -> None:
    """The generated client is the reason a route must be declared rather than assumed."""
    document = api_client.get("/openapi.json").json()
    schema = document["paths"]["/api/v1/auth/config"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert schema["$ref"] == "#/components/schemas/OidcAuthConfig"
