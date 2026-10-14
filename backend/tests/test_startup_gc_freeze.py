"""DP-4 (RL-1685): a started server process has a frozen generation (`gc.freeze()`).

The ~200-300 ms stall RL-1685 attributes to a gen2 collection is not asserted by timing, which
a loaded machine would make flake. The timing-free fact is that start-up moved the objects it
built into the permanent generation, so `gc.get_freeze_count()` is non-zero once the app is up.
"""

from __future__ import annotations

import gc

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

pytestmark = pytest.mark.req("NFR-489")


def test_a_started_app_has_a_frozen_generation(api_settings: Settings) -> None:
    gc.unfreeze()  # a freeze left by an earlier app in this process must not satisfy the test
    try:
        assert gc.get_freeze_count() == 0
        with TestClient(create_app(api_settings)):
            assert gc.get_freeze_count() > 0
    finally:
        gc.unfreeze()
