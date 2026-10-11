"""The WF-699 journey over HTTP: approved Models to an approved, deployed Rating Version.

`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md` phases A to E and its
deploy step, walked as an `httpx` client of `/api/v1` and nothing else (RL-1521: no service
import, no row write, no SQL). `scripts/demo.py --journey wf-699` runs it against the live API;
`backend/tests/test_wf699_journey.py` runs the same module against the app in process.

Each step is one function that returns what the next step needs and raises `JourneyStepFailed`
carrying the step id (`"C1"`, `"D4"`, ...) and the RFC 9457 problem's `code`. A step the platform
does not yet do, or that a later phase owns, is a `Skip` in one table (`SKIPS`), each entry
naming its owner; a skip with no owner fails the journey (`check_skip_owners`).

**The demo's portfolio is a 20,000-policy sample** of the freMTPL2 book (PL-1577): the
dislocation and attribution (D6, D7) run over it, never over the full book. Full-book dislocation
cost is `PL-1574`'s and full-book attribution cost is `FD-1576`'s to measure; nothing printed here
is a full-book figure.

**D4 is a fixed declaration** (`D4_PROPERTY`), read from no fit: premium increasing in
`bonus_malus` over the NCD-ladder sub-graph. The ladder is the only thing the premium depends on
along that sweep, so the failure (a ladder band inverted wider than the grid spacing) and its fix
are deliberate and reproducible. The ladder's bands are demo values, not a priced NCD scale.
"""

from __future__ import annotations

import csv
import io
import re
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Any, Final
from uuid import UUID

import httpx

#: Starts a Job that the API has accepted. In the live demo a Celery worker consumes the outbox;
#: the in-process test passes a runner that executes the Job, because no worker runs there.
JobRunner = Callable[[str], None]


class JourneyStepFailed(RuntimeError):  # noqa: N818 - the plan's name (PL-1544 Task 1)
    """A step did not do what the journey asserts. The message is `<step>: <code>`: the step id,
    the problem's `code` and the HTTP status. It never carries the problem's `detail`, which may
    echo a submitted value; the detail is kept on the exception for the one reader that asks."""

    def __init__(
        self, step: str, code: str | None, status: int | None = None, detail: str = ""
    ) -> None:
        self.step = step
        self.code = code
        self.status = status
        self.detail = detail
        suffix = f" (HTTP {status})" if status is not None else ""
        super().__init__(f"{step}: {code or 'NO_CODE'}{suffix}")


# ---------------------------------------------------------------------------------------------
# What the journey does not do, each with its owner (PL-1544 Acceptance 2 and 13).
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Skip:
    step: str
    line: str


#: A skip or known gap is admitted only where it names an owned finding or a later-phase Work.
SKIPS: Final[tuple[Skip, ...]] = (
    Skip("D9", "SKIPPED D9: GIPP check; Phase 4; WK-685"),
    Skip("E5", "SKIPPED E5 inline review: Phase 3; WK-678"),
    Skip("E7", "SKIPPED E7 Commentary Block: Phase 3; WK-680"),
    Skip("A6", "KNOWN GAP A6: FD-1491"),
    Skip("B9", "KNOWN GAP B9: FD-1490"),
    Skip("B4", "SKIPPED B4 model_call: FD-1456; SL-1543"),
    Skip("C1′", "SKIPPED C1′: FD-1456; SL-1543"),  # noqa: RUF001
)

_OWNER: Final = re.compile(r"\b(?:FD|WK)-\d+\b")


def check_skip_owners(entries: Sequence[Skip]) -> None:
    """Fail the journey for the first entry that names no owned finding or later-phase Work."""
    for entry in entries:
        if _OWNER.search(entry.line) is None:
            raise JourneyStepFailed(entry.step, "SKIP_WITHOUT_OWNER")


# ---------------------------------------------------------------------------------------------
# D4: the fixed declaration (PL-1544 delta, DP-D4 (a)). Never derived from a fit.
# ---------------------------------------------------------------------------------------------

#: Premium increasing in `bonus_malus` on freMTPL2's own range 50..230. A worse bonus-malus
#: coefficient never lowers the premium. The sweep's uniform grid is 50, 95, 140, 185, 230: the
#: spacing is (230 - 50) / 4 = 45.
D4_PROPERTY: Final[dict[str, Any]] = {
    "name": "premium-increasing-in-bonus-malus",
    "check": {
        "kind": "monotone", "input": "bonus_malus", "direction": "increasing",
        "strict": False, "lower": "50", "upper": "230",
    },
}
D4_GRID_SPACING: Final = (230 - 50) // 4

#: The NCD ladder's demo bands (not a priced scale): factor by `bonus_malus` band. The defect
#: (D4) sets the middle band to 0.90, a band 50 wide, wider than the spacing of 45.
LADDER_SLUG: Final = "ncd-ladder"
LADDER_BANDS: Final = {"low": "1.00", "middle": "1.20", "high": "1.50"}
LADDER_DEFECT_MIDDLE: Final = "0.90"
LADDER_MIDDLE_EDGES: Final = (100, 150)


def ladder_body(middle: str, change_note: str) -> dict[str, Any]:
    """The `ncd-ladder` sub-graph body: bands 50-99, 100-149, 150-230 on `bonus_malus`."""
    low, high = LADDER_BANDS["low"], LADDER_BANDS["high"]
    first, second = LADDER_MIDDLE_EDGES
    expr = f"bonus_malus < {first} ? {low} : (bonus_malus < {second} ? {middle} : {high})"
    return {
        "inputs": [{"name": "bonus_malus", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "decimal", "required": True}],
        "steps": [{
            "step_id": "s_ladder", "type": "expression", "label": "NCD ladder", "expr": expr,
            "result_type": "decimal", "consumes": ["bonus_malus"], "produces": "ncd_factor",
        }],
        "change_note": change_note,
    }


# ---------------------------------------------------------------------------------------------
# The client
# ---------------------------------------------------------------------------------------------


def call(
    client: httpx.Client,
    step: str,
    method: str,
    path: str,
    *,
    expect: int | tuple[int, ...],
    code: str | None = None,
    headers: Mapping[str, str] | None = None,
    **kwargs: Any,
) -> Any:
    """One HTTP call. An unexpected status raises `JourneyStepFailed(step, <problem code>)`; so
    does an expected refusal whose problem `code` is not `code`. Returns the JSON body (text for a
    non-JSON body, `None` for an empty one)."""
    response = client.request(method, path, headers=dict(headers or {}), **kwargs)
    wanted = (expect,) if isinstance(expect, int) else expect
    body: Any
    try:
        body = response.json() if response.content else None
    except ValueError:
        body = response.text
    problem_code = body.get("code") if isinstance(body, dict) else None
    if response.status_code not in wanted:
        raise JourneyStepFailed(
            step, problem_code or f"HTTP_{response.status_code}", response.status_code,
            str(body.get("detail", "")) if isinstance(body, dict) else "",
        )
    if code is not None and problem_code != code:
        raise JourneyStepFailed(step, problem_code or "NO_CODE", response.status_code)
    return body


@dataclass
class JourneyResult:
    """What the journey leaves behind: one status per step, the final Rating Version and the
    deployed bundle's premium."""

    step_status: dict[str, str] = field(default_factory=dict)
    rating_version_id: UUID | None = None
    bundle_hash: str = ""
    prod_premium_minor: int = 0


class _Journey:
    def __init__(
        self,
        client: httpx.Client,
        record: Mapping[str, str],
        log: Callable[[str], None],
        run_job: JobRunner | None,
        job_timeout: float,
    ) -> None:
        self.client = client
        self.record = record
        self.log = log
        self.run_job = run_job
        self.job_timeout = job_timeout
        self.result = JourneyResult()

    # -- plumbing ------------------------------------------------------------------------
    def who(self, name: str) -> dict[str, str]:
        return {
            "x-dev-principal-id": self.record[f"{name}_id"],
            "Workspace-Id": self.record["workspace_id"],
        }

    def req(self, step: str, who: str, method: str, path: str, **kwargs: Any) -> Any:
        return call(self.client, step, method, path, headers=self.who(who), **kwargs)

    def done(self, step: str, note: str = "") -> None:
        self.result.step_status[step] = "ok"
        self.log(f"  {step:<4} ok{('  ' + note) if note else ''}")

    def skip(self, step: str) -> None:
        entry = next(e for e in SKIPS if e.step == step)
        self.result.step_status[step] = f"SKIPPED: {entry.line}"
        self.log(f"  {step:<4} {entry.line}")

    def job(self, step: str, who: str, accepted: Mapping[str, Any]) -> dict[str, Any]:
        """Wait for an accepted Job to end and return it. A failed Job is returned too, for the
        steps that assert a failure; the caller checks `status` and `error`."""
        job_id = str(accepted["id"])
        if self.run_job is not None:
            self.run_job(job_id)
        deadline = time.monotonic() + self.job_timeout
        while True:
            job: dict[str, Any] = self.req(step, who, "GET", f"/jobs/{job_id}", expect=200)
            if job["status"] in ("succeeded", "failed", "cancelled"):
                return job
            if time.monotonic() > deadline:
                raise JourneyStepFailed(step, "JOB_TIMEOUT")
            time.sleep(0.5)

    def job_ok(self, step: str, who: str, accepted: Mapping[str, Any]) -> dict[str, Any]:
        job = self.job(step, who, accepted)
        if job["status"] != "succeeded":
            raise JourneyStepFailed(step, (job.get("error") or {}).get("code") or "JOB_FAILED")
        return job

    # -- the journey ---------------------------------------------------------------------
    def run(self) -> JourneyResult:
        check_skip_owners(SKIPS)
        models = self.discover()
        tables = self.phase_a(models)
        algorithm = self.phase_b_c(models, tables)
        self.phase_d(algorithm)
        self.phase_e()
        self.deploy_and_score()
        return self.result

    # Everything below is added phase by phase, red first (PL-1544 Tasks 2-5).
    def discover(self) -> dict[str, Any]:
        raise NotImplementedError

    def phase_a(self, models: dict[str, Any]) -> dict[str, str]:
        raise NotImplementedError

    def phase_b_c(self, models: dict[str, Any], tables: dict[str, str]) -> Any:
        raise NotImplementedError

    def phase_d(self, algorithm: Any) -> None:
        raise NotImplementedError

    def phase_e(self) -> None:
        raise NotImplementedError

    def deploy_and_score(self) -> None:
        raise NotImplementedError


def run_wf699_journey(
    client: httpx.Client,
    record: Mapping[str, str],
    *,
    log: Callable[[str], None] = print,
    run_job: JobRunner | None = None,
    job_timeout: float = 1800.0,
) -> JourneyResult:
    """Walk WF-699 A to E and the deploy step. `record` is the seed's `last-seed.json`: the
    workspace id, every principal's id and the portfolio Dataset Version. `client` has the API's
    `/api/v1` as its base URL."""
    return _Journey(client, record, log, run_job, job_timeout).run()


def _minor(value: Decimal) -> int:
    return int(value.quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


def _csv_cells(text: str) -> tuple[list[str], list[list[str]]]:
    rows = list(csv.reader(io.StringIO(text)))
    return rows[0], rows[1:]
