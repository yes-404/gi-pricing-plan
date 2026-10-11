"""WF-699 — approved Models to an approved Rating Version, walked over HTTP (PL-1544, SL-1527).

`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md` is the journey this
file proves: `examples/fremtpl2/journey.py` is an `httpx` client of `/api/v1` that walks its
phases A to E and its deploy step, and these tests run that module against the app in process.

The journey is a cheap-to-fake thing: a client that returns `ok` for every step proves nothing.
So each test below asserts a *code* the API returned, not only that a call succeeded, and the
skip lines are asserted by their exact text (PL-1544 Acceptance 2).

Marker form: `scripts/req-coverage.py` reads only `@pytest.mark.req("<FR or NFR id>")`, and a
workflow id is not one, so (as `test_wf01_journey.py` does for `WF-698`) the requirement ids the
journey exercises are the markers and `WF-699` is named here and in the test names.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import httpx
import pytest

_EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "fremtpl2"
sys.path.insert(0, str(_EXAMPLE))  # `journey.py` imports its sibling `algorithm`
_SPEC = importlib.util.spec_from_file_location("demo_journey", _EXAMPLE / "journey.py")
assert _SPEC is not None
assert _SPEC.loader is not None
journey = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = journey
_SPEC.loader.exec_module(journey)


@pytest.mark.req("FR-257")
def test_wf699_the_skip_and_known_gap_lines_are_exactly_the_ruled_ones() -> None:
    """PL-1544 Acceptance 2 (Amendment 1, DP-b2 (a)): each line names its phase and owner, and
    none names `FD-1456` as a `KNOWN GAP`."""
    assert [entry.line for entry in journey.SKIPS] == [
        "SKIPPED D9: GIPP check; Phase 4; WK-685",
        "SKIPPED E5 inline review: Phase 3; WK-678",
        "SKIPPED E7 Commentary Block: Phase 3; WK-680",
        "KNOWN GAP A6: FD-1491",
        "KNOWN GAP B9: FD-1490",
        "SKIPPED B4 model_call: FD-1456; SL-1543",
        "SKIPPED C1′: FD-1456; SL-1543",  # noqa: RUF001
    ]
    assert not [e for e in journey.SKIPS if e.line.startswith("KNOWN GAP") and "FD-1456" in e.line]
    # `SKIPPED B7: SL-1340` is moot: SL-1340 merged (PL-1544 activation need 18).
    assert not [e for e in journey.SKIPS if "B7" in e.line]


@pytest.mark.req("FR-257")
def test_an_unowned_skip_fails_the_journey() -> None:
    """PL-1544 Acceptance 13: a skip or known gap that names neither an owned finding nor a
    later-phase Work fails the journey for that step, and an owned one does not."""
    owned = journey.Skip(step="D9", line="SKIPPED D9: GIPP check; Phase 4; WK-685")
    unowned = journey.Skip(step="X1", line="SKIPPED X1: not built yet")
    journey.check_skip_owners([owned])
    with pytest.raises(journey.JourneyStepFailed) as failure:
        journey.check_skip_owners([owned, unowned])
    assert failure.value.step == "X1"
    assert str(failure.value).startswith("X1:")


@pytest.mark.req("FR-257")
def test_a_journey_failure_names_its_step() -> None:
    """PL-1544 Acceptance 6: an unexpected status raises `JourneyStepFailed` whose message starts
    with the step id and carries the problem's `code`, so the demo can print one line."""
    def refuse(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422, json={"code": "VALIDATION_FAILED", "detail": "pins: a rate table is missing"}
        )

    with httpx.Client(
        transport=httpx.MockTransport(refuse), base_url="http://journey.test/api/v1"
    ) as client, pytest.raises(journey.JourneyStepFailed) as failure:
        journey.call(client, "C1", "POST", "/rating-versions", json={}, expect=201)
    assert failure.value.step == "C1"
    assert failure.value.code == "VALIDATION_FAILED"
    assert str(failure.value).startswith("C1: VALIDATION_FAILED")


@pytest.mark.req("FR-257")
def test_a_refusal_that_was_expected_is_returned_with_its_code() -> None:
    """The deliberate failures (B6, C4, E3, E8) are asserted by code: a call that expects a
    refusal passes only when both the status and the problem's `code` match."""
    def refuse(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"code": "RATING_GRAPH_UNRESOLVED_REF", "detail": "x"})

    with httpx.Client(
        transport=httpx.MockTransport(refuse), base_url="http://journey.test/api/v1"
    ) as client:
        problem = journey.call(
            client, "B6", "POST", "/rating-algorithms", json={},
            expect=422, code="RATING_GRAPH_UNRESOLVED_REF",
        )
        assert problem["code"] == "RATING_GRAPH_UNRESOLVED_REF"
        with pytest.raises(journey.JourneyStepFailed) as failure:
            journey.call(
                client, "B6", "POST", "/rating-algorithms", json={},
                expect=422, code="RATING_GRAPH_CYCLIC",
            )
    assert failure.value.code == "RATING_GRAPH_UNRESOLVED_REF"
