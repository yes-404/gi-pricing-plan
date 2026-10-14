"""WF-701 deployment-steps journey — STUB for red-first (SL 8015 prep); replaced at the GO.

No logic. It exists so `backend/tests/test_wf701_journey.py` collects and fails at its own
asserts (R6, R7, R8 red by cause), not at collection. The interface names are the ones the tests
use; the GO replaces every body.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from journey import JourneyStepFailed, Skip  # type: ignore[import-not-found]  # noqa: F401

RULED_LINES: tuple[Skip, ...] = ()


@dataclass
class Wf701Result:
    step_status: dict[str, str] = field(default_factory=dict)
    refusals: dict[str, str] = field(default_factory=dict)
    preconditions: list[str] = field(default_factory=list)
    k1_approvers: list[str] = field(default_factory=list)
    k1_ref: str = ""
    k2_ref: str = ""
    trace_count: int = 0
    refused_quote_id: str = ""


def check_ruled_lines(entries: list[Skip]) -> None:
    return None


def run_wf701_journey(
    client: Any,
    record: dict[str, str],
    *,
    log: Callable[[str], None],
    run_job: Callable[[str], None],
) -> Wf701Result:
    return Wf701Result()
