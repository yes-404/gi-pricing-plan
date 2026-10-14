"""DP-4 (RL-1685): start-up freezes the heap, proven by its call and by its effect.

The stall RL-1685 attributes to a gen2 collection is not asserted by timing, which a loaded
machine would make flake. RL-1685's own form, `gc.get_freeze_count() > 0` once the app has
started, was said to be unable to fail because a non-zero count already stood before any
lifespan ran. That figure (375 in one earlier run) has an UNKNOWN source and was not
reproduced: the final file read 0 before the lifespan. This file does not rely on it;
the difference form below holds whatever the baseline is. The ruling of the maintainer
(by delegation), to-lead "2026-10-14 10:54:56 BST", replaces it with two asserts, each red on
the base tree.

1. **Call.** `gc.freeze` is wrapped by a spy that still calls the real one. Start-up calls it
   exactly once, after the lifespan's last step (the rate limiter is on `app.state`).
2. **Effect.** With the real `gc.freeze`, the permanent generation is larger at `yield` than
   just before the lifespan started. It is a difference, not a level: a level would pass with
   no freeze at all if anything had frozen the heap earlier in the process.
"""

from __future__ import annotations

import gc

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

pytestmark = pytest.mark.req("NFR-489")


def test_the_lifespan_calls_gc_freeze_once_after_its_last_start_up_step(
    api_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = create_app(api_settings)
    real_freeze = gc.freeze
    rate_limiter_present_at_each_call: list[bool] = []

    def _spy() -> None:
        rate_limiter_present_at_each_call.append(hasattr(app.state, "rate_limiter"))
        real_freeze()

    monkeypatch.setattr(gc, "freeze", _spy)
    with TestClient(app):
        seen = list(rate_limiter_present_at_each_call)
    assert seen == [True], (
        "gc.freeze() must be called exactly once during start-up, after the last start-up "
        f"step; the spy saw (rate_limiter present at each call) {seen}"
    )


def test_the_lifespan_moves_objects_into_the_permanent_generation(
    api_settings: Settings,
) -> None:
    app = create_app(api_settings)
    before = gc.get_freeze_count()
    with TestClient(app):
        at_yield = gc.get_freeze_count()
    assert at_yield > before, (
        "start-up froze nothing: the permanent generation held "
        f"{before} objects before the lifespan and {at_yield} at yield"
    )
