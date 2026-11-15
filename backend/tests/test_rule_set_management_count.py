"""`01` FR-452 (#1837's audit clause C6): `PUT /api/v1/datasets/{slug}/rule-set` is counted against
the management limit exactly once on a pass and exactly once when the dataset load is a 404.

A sibling of `test_management_rate_limit.py`, whose fixtures and spy helpers are imported, not
copied. DB-backed (the `database` fixture, as that file is).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_management_rate_limit import (  # noqa: F401  (client, set_limit: fixtures)
    _spy_management_count,
    _user_headers,
    client,
    set_limit,
)
from fastapi.testclient import TestClient

from model_schema import new_uuid7


@pytest.mark.req("FR-452")
async def test_the_rule_set_replace_is_counted_exactly_once_on_a_pass_and_on_a_load_404(
    client: TestClient,  # noqa: F811
    workspace_id: UUID,
    grant: Any,
    set_limit: Any,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FR-452 (#1837's audit clause C6): `PUT /api/v1/datasets/{slug}/rule-set` moves the management
    counter by exactly one on a replace that passes and by exactly one when the dataset load is a
    404 (the count is after the permission check, never doubled by a second scoped check). Red: a
    second `await count()` after the scoped check makes either delta 2."""
    await set_limit(1000)
    headers = await _user_headers(grant, workspace_id, "analyst")
    slug = f"ds-{new_uuid7().hex[-8:]}"
    assert client.post(
        "/api/v1/datasets", json={"slug": slug, "name": "Counted rule set"}, headers=headers
    ).status_code == 201
    calls = _spy_management_count(client, monkeypatch)

    before = len(calls)
    passed = client.put(f"/api/v1/datasets/{slug}/rule-set", json={"rules": []}, headers=headers)
    after_pass = len(calls)
    missing = client.put(
        "/api/v1/datasets/no-such-dataset/rule-set", json={"rules": []}, headers=headers
    )
    after_missing = len(calls)

    assert passed.status_code == 200, passed.text
    assert missing.status_code == 404, missing.text
    assert after_pass - before == 1
    assert after_missing - after_pass == 1
