"""DP-4 (RL-1685): the app's own start-up calls `gc.freeze()`, after its last start-up step.

The ~200-300 ms stall RL-1685 attributes to a gen2 collection is not asserted by timing, which
a loaded machine would make flake. RL-1685's own form, `gc.get_freeze_count() > 0` once the app
has started, cannot fail here: `create_app(...)` alone leaves 375 objects in the permanent
generation before any lifespan runs (measured on this tree, with no `gc.freeze` call visible to
`sys.setprofile`), so a count proves nothing about the lifespan. This test therefore observes
the call itself: `gc.freeze` is replaced by a spy, and the spy records whether the lifespan's
last start-up step (the rate limiter, set just before `yield`) had run when it was called.
"""

from __future__ import annotations

import gc
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

pytestmark = pytest.mark.req("NFR-489")


def test_the_lifespan_freezes_the_heap_after_its_last_start_up_step(
    api_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = create_app(api_settings)
    calls: list[bool] = []

    def _spy_freeze() -> None:
        calls.append(hasattr(app.state, "rate_limiter"))

    monkeypatch.setattr(gc, "freeze", _spy_freeze)
    with TestClient(app):
        started: Any = list(calls)
    assert started == [True], (
        "gc.freeze() must be called exactly once during start-up, after the last start-up "
        f"step; the spy saw (rate_limiter present at each call) {started}"
    )
