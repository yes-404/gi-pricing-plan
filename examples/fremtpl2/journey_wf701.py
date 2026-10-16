"""WF-701 deployment-steps journey (PL-1710, SL-1711).

T1 is real: the two ruled lines and the check that refuses any other skip. The step bodies
(`run_wf701_journey`, T2 to T6) are still the stub of the red-first commit: no logic, so
`backend/tests/test_wf701_journey.py` collects and fails at its own asserts. The interface names
are the ones the tests use.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from journey import JourneyStepFailed, Skip  # type: ignore[import-not-found]  # noqa: F401

#: PL-1710 T1 and acceptance 2: the only two lines a WF-701 run may print as a ruled limb. The
#: second is the walked limb of RL-1712 (FR-259), not a skip, so no `KNOWN GAP` line exists.
RULED_LINES: tuple[Skip, ...] = (
    Skip("A2/C4/C6", "COMPOSE-ONLY A2/C4/C6 replica limb"),
    Skip("C7iv", "C7-errors: refused, not traced (FR-259, RL-1712)"),
)


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
    """Fail the journey for the first entry whose line is not one of `RULED_LINES`."""
    ruled = {entry.line for entry in RULED_LINES}
    for entry in entries:
        if entry.line not in ruled:
            raise JourneyStepFailed(entry.step, "UNRULED_SKIP")


def run_wf701_journey(
    client: Any,
    record: dict[str, str],
    *,
    log: Callable[[str], None],
    run_job: Callable[[str], None],
) -> Wf701Result:
    return Wf701Result()
