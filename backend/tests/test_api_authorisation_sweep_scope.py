"""The sweep's `RESOURCE_BACKED` exemption is the Environment-scoped writes' alone (RL-1848).

Kept apart from `test_api_authorisation_sweep.py` because it needs no app and no database:
it reads the mapping and nothing else.
"""

from __future__ import annotations

from typing import Any

import pytest
from backend.tests.test_api_authorisation_sweep import RESOURCE_BACKED

#: The one prefix `RESOURCE_BACKED` may hold (`RL-1848`: Environment-scoped writes keep
#: load-first, so the 404 for an unknown slug is accepted *only* for those routes).
ENVIRONMENT_PREFIX = "/api/v1/environments/{env}/"


def _outside_the_environment_scope(
    backed: dict[tuple[str, str], tuple[dict[str, str], dict[str, Any]]],
) -> list[tuple[str, str]]:
    """The entries of a `RESOURCE_BACKED`-shaped mapping not under `ENVIRONMENT_PREFIX`."""
    return sorted(key for key in backed if not key[1].startswith(ENVIRONMENT_PREFIX))


@pytest.mark.req("FR-343")
def test_resource_backed_holds_only_environment_scoped_paths() -> None:
    """RL-1848: the load-first exemption is the Environment-scoped writes' alone.

    A non-Environment route added here would have its anonymous/role-less 403 replaced by a
    resource 404 unnoticed — the sweep would stop proving it enforces its permission first.
    """
    assert RESOURCE_BACKED, "the guard would pass on an empty mapping"
    assert _outside_the_environment_scope(RESOURCE_BACKED) == []


@pytest.mark.req("FR-343")
def test_the_resource_backed_guard_rejects_an_injected_non_environment_path() -> None:
    """Broken-input proof: the guard returns the violation instead of passing everything."""
    injected = {
        **RESOURCE_BACKED,
        ("POST", "/api/v1/datasets/{dataset_id}/versions"): ({"dataset_id": "x"}, {}),
        ("POST", "/api/v1/environments-extra/{env}/deployments"): ({"env": "dev"}, {}),
    }
    assert _outside_the_environment_scope(injected) == [
        ("POST", "/api/v1/datasets/{dataset_id}/versions"),
        ("POST", "/api/v1/environments-extra/{env}/deployments"),
    ]
