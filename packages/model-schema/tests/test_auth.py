"""`OidcAuthConfig` — the shape `07` FR-394 publishes (`07` §5.1)."""

import pytest
from pydantic import ValidationError

from model_schema import OidcAuthConfig


@pytest.mark.req("FR-394")
def test_every_value_the_flow_needs_is_required() -> None:
    with pytest.raises(ValidationError):
        OidcAuthConfig.model_validate({"issuer": "https://idp.example/realms/gip"})


@pytest.mark.req("FR-394")
def test_a_full_config_round_trips() -> None:
    model = OidcAuthConfig.model_validate(
        {
            "issuer": "https://idp.example/realms/gip",
            "client_id": "gi-pricing-frontend",
            "dev_auth_enabled": True,
        }
    )
    assert model.model_dump() == {
        "issuer": "https://idp.example/realms/gip",
        "client_id": "gi-pricing-frontend",
        "dev_auth_enabled": True,
    }
