"""The demo's WF-698 postcondition check, exercised in pytest (finding F3).

`scripts/demo.py`'s `_verify_journey_postconditions` runs only inside the exit demo, over
the real seed, so nothing in pytest exercised the check until this file. The HTTP call is
stubbed here; the decision — refuse to open the browser when no approved model exists,
proceed when one does — is the logic that matters, and it is the same without the seed.
"""

from __future__ import annotations

import importlib.util
import pathlib
import urllib.request
from unittest import mock

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_demo():
    spec = importlib.util.spec_from_file_location(
        "gi_demo", ROOT / "scripts" / "demo.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


RECORD = {"analyst_id": "analyst-a", "workspace_id": "workspace-w"}


def test_the_postcondition_check_refuses_when_no_model_is_approved() -> None:
    demo = _load_demo()
    with (
        mock.patch.object(
            urllib.request, "urlopen", return_value=_FakeResponse(b'{"items": []}')
        ),
        pytest.raises(demo.DemoRefusedError),
    ):
        demo._verify_journey_postconditions(RECORD, {})


def test_the_postcondition_check_passes_when_a_model_is_approved() -> None:
    demo = _load_demo()
    with mock.patch.object(
        urllib.request,
        "urlopen",
        return_value=_FakeResponse(b'{"items": [{"id": "model:glm-1"}]}'),
    ):
        demo._verify_journey_postconditions(RECORD, {})  # must not raise
