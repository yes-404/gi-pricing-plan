"""The WF-701 deployment-steps journey over HTTP (PL-1710, SL-1711).

`docs/workflows/WF-00701-deploy-and-monitor.md` A1-A6, C1-C4, C6 and C7, walked as an `httpx`
client of `/api/v1` and nothing else (RL-1521: no service import, no row write, no SQL), on the
state `examples/fremtpl2/journey.py` leaves: `rv3` live in `dev`, `uat` and `prod`. The monitoring
steps (C5, D1-D4) and A3's notification are P4's (the maintainer's entry "2026-10-14 09:50:37
BST"). `scripts/demo.py --journey wf-701` runs it against the live API or, with `--target
compose`, against the Slice 4 stack's `lb`; `backend/tests/test_wf701_journey.py` runs it in
process.

**No faked step.** No step is a database write, a status write or a fixture. Every step asserts
its status and a server-side effect read back through a route other than the one that caused it.
`run_job` is the only in-process substitute; the compose run has none.

**Two candidates, both through the governed path** (DP-W4): K1 is the live algorithm with the
minimum premium raised 150 -> 180; K2 is K1 plus one constraint that declines. Each is a
Rating Version created, compiled, regression-run, dislocation-run, submitted and approved by two
distinct principals over HTTP. Their definitions are the two JSON files beside the shipped rating
artifacts; no shipped file is edited.

**Ruled lines.** Two lines are admitted by ruling, and the test asserts them: `COMPOSE_ONLY` (the
replica limb needs more than one process) and `C7_ERRORS` (RL-1712: a refused quote is not
traced). Every other step is `ok` or the journey fails.

**Not a measurement.** The deploy's < 30 s on C4 is a functional bound. NFR-494's and NFR-489's
verdicts are Slice 5's, on the dedicated host.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any, Final
from uuid import uuid4

import httpx

_HERE: Final = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import journey as _wf699  # noqa: E402  (the one definition of the client, the failure and the skip)

JourneyStepFailed = _wf699.JourneyStepFailed
Skip = _wf699.Skip
call = _wf699.call
run_wf699_journey = _wf699.run_wf699_journey
JobRunner = _wf699.JobRunner

RATING_DIR: Final = _HERE / "rating"
K1_FILE: Final = RATING_DIR / "fremtpl2-wf701.k1-min-premium.json"
K2_FILE: Final = RATING_DIR / "fremtpl2-wf701.k2-decline.json"

# -- the two ruled lines ------------------------------------------------------------------------

FIRST_LINE: Final = (
    "WF-701 demo: process environment dev with development identity (dev auth); "
    "deployments target the Environment resources uat and prod"
)
COMPOSE_ONLY: Final = "COMPOSE-ONLY A2/C4/C6 replica limb"
C7_ERRORS: Final = "C7-errors: refused, not traced (FR-259, RL-1712)"
RULED_LINES: Final = (COMPOSE_ONLY, C7_ERRORS)

#: The step order the journey records, once each (the test asserts it). It is the plan's order
#: (PL-1710, step table), not WF-701's: the refusals come before the first deploy they guard.
STEP_ORDER: Final = (
    "C3(iii)", "C2(prod)", "C2(route)", "FR-238",
    "A1", "A2", "A3", "A4", "A5", "A6",
    "C3(ii)", "C1", "C4", "C6",
    "C7(i)", "C7(ii)", "C7(iii)", "C7(iv)",
)  # fmt: skip

# -- the pre-registered volumes (PL-1710 DP-6, P8) ------------------------------------------------

COMPARE_POLICIES: Final = 200  # A5; grown only by `_pick_a6`'s rule, recorded
C6_QUOTES: Final = 50
C7_QUOTES: Final = 2000
C7_RATE: Final = Fraction(1, 100)  # `rating.trace_sample_rate`'s default
#: Pre-registered, not fitted. Binomial(2000, 0.01) has mean 20; `outside_band_probability` is
#: 8.030e-07 (P8), so a healthy run is outside it about once in 1.2 million.
C7_BAND: Final = (3, 45)
C7_DECLINES: Final = 20
STREAM_QUOTES: Final = 10  # the sequential old/new stream's size, before and after a deploy
FUNCTIONAL_BOUND_S: Final = 30.0
PAGE: Final = 100


# -- pure assertions (each unit-tested on its own broken input) ----------------------------------


def outside_band_probability(n: int, p: Fraction, band: tuple[int, int]) -> Fraction:
    """P(X < lo) + P(X > hi) for X ~ Binomial(n, p), in exact rational arithmetic."""
    low, high = band
    return sum(
        (
            Fraction(comb(n, k)) * p**k * (1 - p) ** (n - k)
            for k in range(n + 1)
            if not low <= k <= high
        ),
        Fraction(0),
    )


def check_trace_count(count: int, *, band: tuple[int, int] = C7_BAND) -> None:
    """C7 (i): the persisted quoted-trace count is inside the pre-registered band."""
    if not band[0] <= count <= band[1]:
        raise JourneyStepFailed(
            "C7", f"TRACE_COUNT_{count}_OUTSIDE_BAND_{band[0]}_{band[1]}", detail=f"band {band}"
        )


_SKIP_PREFIXES: Final = ("SKIPPED", "KNOWN GAP", "COMPOSE-ONLY", "C7-errors")


def check_lines(lines: Sequence[str], *, replica_limb: bool) -> None:
    """Fail for any skip, known-gap or ruled-form line that is not one of the two ruled lines, and
    for a ruled line printed the wrong number of times: `C7_ERRORS` once, `COMPOSE_ONLY` once when
    the replica limb could not be walked (`replica_limb` False) and never when it was."""
    for line in lines:
        text = line.strip()
        if text.startswith(_SKIP_PREFIXES) and text not in RULED_LINES:
            raise JourneyStepFailed("LINES", "UNRULED_SKIP", detail=text)
    wanted = {C7_ERRORS: 1, COMPOSE_ONLY: 0 if replica_limb else 1}
    for ruled, times in wanted.items():
        if sum(1 for line in lines if line.strip() == ruled) != times:
            raise JourneyStepFailed("LINES", "RULED_LINE_COUNT", detail=ruled)


def check_old_or_new(step: str, hashes: Sequence[str], old: str, new: str) -> None:
    """A2 (i) and C4 (i): every response during the switch carries the old or the new hash."""
    stray = sorted({h for h in hashes if h not in (old, new)})
    if stray:
        raise JourneyStepFailed(step, "BUNDLE_HASH_NEITHER_OLD_NOR_NEW", detail=", ".join(stray))


def check_none_old(step: str, hashes: Sequence[str], old: str) -> None:
    """A2 (ii) and C4 (ii): after the deploy returned, no response carries the old hash."""
    if old in hashes:
        raise JourneyStepFailed(step, "OLD_BUNDLE_SERVED_AFTER_THE_DEPLOY")


def committed_hosts(processes: Mapping[str, str]) -> frozenset[str]:
    """The host part of every process the switch records as `committed`. A process id is
    `<hostname>:<pid>:<start epoch>` (`platform/deployment_switch.py`)."""
    return frozenset(
        name.split(":", 1)[0] for name, state in processes.items() if state == "committed"
    )


def check_commit_set(step: str, processes: Mapping[str, str], expected: frozenset[str]) -> None:
    """A2 (iii) and C4 (iii): the COMMIT set equals the replicas the stack reports, and naming the
    one that is missing when it does not (R5)."""
    got = committed_hosts(processes)
    if got != expected:
        missing = ",".join(sorted(expected - got)) or "-"
        extra = ",".join(sorted(got - expected)) or "-"
        raise JourneyStepFailed(
            step, "COMMIT_SET_DIFFERS_FROM_THE_REPLICAS", detail=f"missing {missing}; extra {extra}"
        )


def binds_min_premium(result: Mapping[str, Any]) -> bool:
    """Whether a `/score` result's `constraints` rung records `MIN_PREMIUM_APPLIED`."""
    for rung in result.get("premium_ladder", []):
        operation = rung.get("operation") or {}
        if "MIN_PREMIUM_APPLIED" in (operation.get("applied") or []):
            return True
    return False


def payable_minor(result: Mapping[str, Any]) -> int:
    rung = next(r for r in result["premium_ladder"] if r["rung"] == "payable_premium")
    return int(rung["value_minor"])


def contract_sample(
    input_contract: Sequence[Mapping[str, Any]], template: Mapping[str, Any], count: int
) -> list[dict[str, Any]]:
    """`count` distinct input sets spread over the contract's declared domains, deterministic:
    an enum cycles its domain, an int field steps through its `min..max` range, each at its own
    stride, so the sample is a spread and not a column. A field the contract declares without a
    domain (`current_premium_minor`) keeps the template's value. No random number is drawn."""
    rows: list[dict[str, Any]] = []
    strides = (1, 3, 7, 11, 13, 17, 19, 23)
    for i in range(count):
        row = dict(template)
        for j, field_ in enumerate(input_contract):
            name = str(field_["name"])
            stride = strides[j % len(strides)]
            if "domain" in field_:
                domain = list(field_["domain"])
                row[name] = domain[(i * stride) % len(domain)]
            elif "min" in field_ and "max" in field_:
                low, high = int(field_["min"]), int(field_["max"])
                row[name] = low + (i * stride * 37) % (high - low + 1)
        rows.append(row)
    return rows


# -- the result -----------------------------------------------------------------------------------


@dataclass
class Wf701Result:
    """What the journey leaves behind: one status per step, the printed ruled lines, and the
    figures the test and the rehearsal quote."""

    step_status: dict[str, str] = field(default_factory=dict)
    lines: list[str] = field(default_factory=list)
    k1_bundle_hash: str = ""
    k2_bundle_hash: str = ""
    a5_totals: dict[str, int] = field(default_factory=dict)
    c4_elapsed_s: float = 0.0
    c7_count: int = 0
    c7_declined: int = 0
    prod_golden_minor: int = 0


class _Wf701:
    def __init__(
        self,
        client: httpx.Client,
        record: Mapping[str, str],
        wf699: Any,
        log: Callable[[str], None],
        run_job: JobRunner | None,
        job_timeout: float,
        replica_hosts: Callable[[], frozenset[str]] | None,
        stream_client: Callable[[], httpx.Client] | None,
        before_step: Callable[[str], None] | None,
    ) -> None:
        self.client = client
        self.record = record
        self.log = log
        self.run_job = run_job
        self.job_timeout = job_timeout
        self.replica_hosts = replica_hosts
        self.stream_client = stream_client
        self.before_step = before_step
        self.result = Wf701Result()
        self.wf699 = wf699
        self.printed: list[str] = []
        self.saved: dict[str, dict[str, Any]] = {}

    # -- plumbing ----------------------------------------------------------------------------
    def say(self, line: str) -> None:
        self.result.lines.append(line)
        self.log(line)

    def who(self, name: str) -> dict[str, str]:
        return {
            "x-dev-principal-id": self.record[f"{name}_id"],
            "Workspace-Id": self.record["workspace_id"],
        }

    def req(self, step: str, who: str, method: str, path: str, **kwargs: Any) -> Any:
        return call(self.client, step, method, path, headers=self.who(who), **kwargs)

    def done(self, step: str, note: str = "") -> None:
        self.result.step_status[step] = "ok"
        self.say(f"  {step:<8} ok{('  ' + note) if note else ''}")

    def start(self, step: str) -> None:
        if self.before_step is not None:
            self.before_step(step)

    def job(self, step: str, who: str, accepted: Mapping[str, Any]) -> dict[str, Any]:
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
            error = job.get("error") or {}
            raise JourneyStepFailed(
                step, error.get("code") or "JOB_FAILED", detail=str(error.get("message", ""))
            )
        return job

    def pages(self, step: str, who: str, path: str, **params: Any) -> list[dict[str, Any]]:
        """Every item of a cursor-paginated list."""
        items: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            query = {**params, "limit": PAGE, **({"cursor": cursor} if cursor else {})}
            page = self.req(step, who, "GET", path, expect=200, params=query)
            items.extend(page["items"])
            cursor = page.get("next_cursor")
            if not cursor:
                return items

    # -- the state WF-699 left -------------------------------------------------------------------
    def discover(self) -> None:
        wf = self.wf699
        self.rv3 = self.req(
            "A0", "analyst", "GET", f"/rating-versions/{wf.rating_version_id}", expect=200
        )
        self.rv3_ref = f"rating_version:{self.rv3['slug']}@{self.rv3['version']}"
        self.rv3_hash = str(self.rv3["bundle"]["content_hash"])
        if self.rv3_hash != wf.bundle_hash:
            raise JourneyStepFailed("A0", "WF699_BUNDLE_DIFFERS")
        algorithm_ref = str(self.rv3["algorithm_ref"]).split(":", 1)[1]
        self.algorithm = self.req(
            "A0", "analyst", "GET", f"/rating-algorithms/{algorithm_ref}", expect=200
        )
        self.algorithm_slug = str(self.algorithm["slug"])
        self.next_algorithm_version = int(self.algorithm["version"]) + 1
        # The golden quotes the journey left in the algorithm's one Regression Suite: the newest
        # version (`GET /regression-suites/{slug}@{n}` is the only read; n counts up to the 404).
        suite, number = None, 1
        while True:
            response = self.client.get(
                f"/regression-suites/fremtpl2-rate-suite@{number}", headers=self.who("analyst")
            )
            if response.status_code == 404:
                break
            if response.status_code != 200:
                raise JourneyStepFailed("A0", "SUITE_READ_FAILED", response.status_code)
            suite, number = response.json(), number + 1
        if suite is None or not suite["golden_quotes"]:
            raise JourneyStepFailed("A0", "NO_GOLDEN_QUOTE")
        self.suite = suite
        self.golden = suite["golden_quotes"][0]
        self.context = {
            key: value
            for key, value in self.golden["context"].items()
            if key in ("purpose", "quoted_at", "effective_date", "inputs")
        }
        self.result.prod_golden_minor = int(self.golden["expected"]["payable_premium_minor"])

    # -- a candidate: created, compiled, evidenced, submitted --------------------------------
    def build(
        self, label: str, patch: Mapping[str, Any], *, base: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        """Fork `base` (default: the live algorithm) with one step added after `patch["after"]`,
        save it as the next version, and create and compile a Rating Version pinning what `rv3`
        pins. K1 adds the minimum-premium clamp; K2 forks K1 and adds the decline."""
        source = base if base is not None else self.algorithm
        body = {
            key: value
            for key, value in source.items()
            if key in ("slug", "input_contract", "outputs", "steps", "sub_graphs")
        }
        steps = [dict(step) for step in body["steps"]]
        at = next(i for i, s in enumerate(steps) if s["step_id"] == patch["after"]) + 1
        steps = [*steps[:at], dict(patch["add_step"]), *steps[at:]]
        version = self.next_algorithm_version
        self.next_algorithm_version += 1
        saved = self.req(
            label,
            "analyst",
            "POST",
            "/rating-algorithms",
            expect=201,
            json={**body, "steps": steps, "version": version},
        )
        created = self.req(
            label,
            "analyst",
            "POST",
            "/rating-versions",
            expect=201,
            json={
                "slug": f"fremtpl2-wf701-{label.lower()}",
                "dataset_version_id": self.rv3["dataset_version_id"],
                "model_ref": self.rv3["model_ref"],
                "algorithm_ref": f"rating_algorithm:{saved['slug']}@{saved['version']}",
                "pins": self.rv3["pins"],
            },
        )
        accepted = self.req(
            label, "analyst", "POST", f"/rating-versions/{created['id']}/compile", expect=202
        )
        self.job_ok(label, "analyst", accepted)
        compiled: dict[str, Any] = self.req(
            label, "analyst", "GET", f"/rating-versions/{created['id']}", expect=200
        )
        if not compiled.get("bundle"):
            raise JourneyStepFailed(label, "COMPILED_BUT_NO_BUNDLE")
        self.say(f"  {label}: rating version {compiled['slug']}@{compiled['version']} compiled")
        self.saved[label] = self.req(
            label,
            "analyst",
            "GET",
            f"/rating-algorithms/{saved['slug']}@{saved['version']}",
            expect=200,
        )
        return compiled

    def regression(self, label: str, version: Mapping[str, Any]) -> dict[str, Any]:
        accepted = self.req(
            label,
            "analyst",
            "POST",
            f"/rating-versions/{version['id']}/regression-runs",
            expect=202,
        )
        job = self.job(label, "analyst", accepted)
        if job["status"] == "succeeded":
            run_id = str(job["result"]["ref"]).split(":", 1)[1]
        else:
            import re

            found = re.search(
                r"regression run ([0-9a-f-]{36})", (job.get("error") or {}).get("message", "")
            )
            if found is None:
                raise JourneyStepFailed(label, (job.get("error") or {}).get("code") or "JOB_FAILED")
            run_id = found.group(1)
        run: dict[str, Any] = self.req(
            label,
            "analyst",
            "GET",
            f"/rating-versions/{version['id']}/regression-runs/{run_id}",
            expect=200,
        )
        return run

    def pass_regression(
        self, label: str, version: Mapping[str, Any], *, floor_minor: int | None
    ) -> None:
        """Run the suite; a golden that moved is updated deliberately ONLY where the new value is
        exactly `floor_minor` (K1's minimum premium binding), the form of WF-699's D2/D3."""
        run = self.regression(label, version)
        if run["overall"] == "pass":
            return
        moved = [g for g in run["golden_results"] if g["status"] == "fail"]
        if floor_minor is None or any(int(g["actual_minor"]) != floor_minor for g in moved):
            raise JourneyStepFailed(label, "GOLDEN_MOVED_FOR_A_REASON_THE_CHANGE_DOES_NOT_GIVE")
        by_name = {g["name"]: g for g in moved}
        updated = [
            {
                **quote,
                "expected": {**quote["expected"], "payable_premium_minor": floor_minor},
                "note": "updated deliberately: the minimum premium rose 150 -> 180 (WF-701 K1)",
            }
            if quote["name"] in by_name
            else quote
            for quote in self.suite["golden_quotes"]
        ]
        self.suite = self.req(
            label,
            "analyst",
            "POST",
            f"/regression-suites/{self.suite['slug']}/versions",
            expect=201,
            json={
                "algorithm_slug": self.suite["algorithm_slug"],
                "golden_quotes": updated,
                "properties": self.suite["properties"],
                "generation": self.suite["generation"],
                "change_note": "WF-701 K1: golden quotes moved by the minimum premium",
            },
        )
        if self.regression(label, version)["overall"] != "pass":
            raise JourneyStepFailed(label, "RUN_DID_NOT_PASS")

    def live_prod_ref(self) -> str:
        listed = self.req("DEP", "deployer", "GET", "/environments/prod/deployments", expect=200)
        return str(listed["items"][0]["rating_version_ref"])

    def dislocation(self, label: str, version: Mapping[str, Any]) -> None:
        spec = {
            "baseline_ref": self.live_prod_ref(),
            "candidate_ref": f"rating_version:{version['slug']}@{version['version']}",
            "portfolio_dataset_version_id": self.record["portfolio_dataset_version_id"],
            "purpose": "new_business",
            "as_at": "2026-10-01",
            "segments": ["area"],
            "band_edges_pct": ["-10", "-5", "0", "5", "10"],
            "mover_threshold_pct": "10",
        }
        accepted = self.req(label, "analyst", "POST", "/dislocation-runs", expect=202, json=spec)
        self.job_ok(label, "analyst", accepted)

    def submit(self, label: str, version: Mapping[str, Any], text: str) -> str:
        first = self.req(
            label,
            "actuary",
            "POST",
            f"/rating-versions/{version['id']}/submit",
            expect=200,
            json={"change_summary": text},
        )
        return str(first["approval_request_id"])

    def decide(self, label: str, who: str, request_id: str) -> dict[str, Any]:
        decided: dict[str, Any] = self.req(
            label,
            who,
            "POST",
            f"/approval-requests/{request_id}/decide",
            expect=200,
            json={"decision": "approve", "comment": f"approved in the WF-701 journey ({label})"},
        )
        return decided

    def evidence(self, label: str, version: Mapping[str, Any], *, floor_minor: int | None) -> str:
        self.pass_regression(label, version, floor_minor=floor_minor)
        self.dislocation(label, version)
        return self.submit(
            label, version, f"WF-701 {label}: see the structural diff and the dislocation run."
        )

    def read(self, version: Mapping[str, Any]) -> dict[str, Any]:
        read: dict[str, Any] = self.req(
            "DEP", "analyst", "GET", f"/rating-versions/{version['id']}", expect=200
        )
        return read

    # -- scoring ---------------------------------------------------------------------------------
    def key(self, slug: str, environment: str) -> str:
        account = self.req(
            "S1",
            "admin",
            "POST",
            "/service-accounts",
            expect=201,
            json={"slug": slug, "environments": [environment], "permissions": ["score:execute"]},
        )
        return str(account["key"])

    def score(
        self,
        step: str,
        key: str,
        context: Mapping[str, Any],
        *,
        client: httpx.Client | None = None,
        expect: int | tuple[int, ...] = 200,
        code: str | None = None,
    ) -> Any:
        return call(
            client or self.client,
            step,
            "POST",
            "/score",
            expect=expect,
            code=code,
            headers={"X-API-Key": key},
            json=dict(context),
        )

    def stream_across(
        self, step: str, key: str, deploy: Callable[[], Any], old: str, new: str
    ) -> Any:
        """Run `deploy` with a `/score` stream across it: every response old or new (i), and none
        old once the deploy returned (ii). With a `stream_client` the stream is a thread running
        beside the deploy; without one, a sequential stream before and after it (in process, where
        one client cannot be shared across threads)."""
        hashes: list[str] = []
        lock = threading.Lock()
        stop = threading.Event()
        errors: list[str] = []

        def pump(client: httpx.Client) -> None:
            while not stop.is_set():
                response = client.post("/score", headers={"X-API-Key": key}, json=self.context)
                if response.status_code != 200:
                    errors.append(f"HTTP_{response.status_code}")
                    return
                with lock:
                    hashes.append(response.json()["bundle_hash"])

        thread: threading.Thread | None = None
        side: httpx.Client | None = None
        if self.stream_client is not None:
            side = self.stream_client()
            thread = threading.Thread(target=pump, args=(side,), daemon=True)
            thread.start()
        else:
            for _ in range(STREAM_QUOTES):
                hashes.append(self.score(step, key, self.context)["bundle_hash"])
        try:
            outcome = deploy()
        finally:
            stop.set()
            if thread is not None:
                thread.join(timeout=60)
            if side is not None:
                side.close()
        if errors:
            raise JourneyStepFailed(step, errors[0])
        after = [self.score(step, key, self.context)["bundle_hash"] for _ in range(STREAM_QUOTES)]
        check_old_or_new(step, hashes, old, new)
        check_none_old(step, after, old)
        self.stream_total = len(hashes) + len(after)
        return outcome

    def commit_set(self, step: str, environment: str, deployed: Mapping[str, Any]) -> str:
        """(iii): the COMMIT set the audit log records for this deploy, read through `GET /audit`
        (not the deploy response), equal to the replicas the stack reports."""
        events = self.req(
            step,
            "admin",
            "GET",
            "/audit",
            expect=200,
            params={
                "entity": f"environment:{environment}",
                "action": "deployment.switched",
                "limit": 1,
            },
        )["items"]
        if self.replica_hosts is None:
            return COMPOSE_ONLY
        if not events or str(events[0]["after"]["deployment_ref"]) != str(deployed["id"]):
            raise JourneyStepFailed(step, "NO_SWITCH_EVENT_FOR_THIS_DEPLOY")
        processes = events[0]["after"]["processes"]
        if processes != deployed["switch"]["processes"]:
            raise JourneyStepFailed(step, "AUDIT_AND_RESPONSE_DISAGREE")
        check_commit_set(step, processes, self.replica_hosts())
        return f"{len(committed_hosts(processes))} replicas committed"

    # -- the journey ---------------------------------------------------------------------------
    def run(self) -> Wf701Result:
        self.say(FIRST_LINE)
        self.discover()
        self.candidates()
        self.refusals()
        self.uat_and_a()
        self.prod_and_c()
        self.c7()
        if COMPOSE_ONLY in self.printed:
            self.say(COMPOSE_ONLY)
        check_lines(self.result.lines, replica_limb=self.replica_hosts is not None)
        return self.result

    def candidates(self) -> None:
        self.start("C3(iii)")
        k1 = self.build("K1", json.loads(K1_FILE.read_text(encoding="utf-8")))
        k2 = self.build(
            "K2", json.loads(K2_FILE.read_text(encoding="utf-8")), base=self.saved["K1"]
        )
        request = self.evidence("K1", k1, floor_minor=18000)
        # C3 (iii), FR-354: after ONE of the two approvers the request is `review`, the version is
        # not approved, and nothing can deploy it; the second, distinct approver completes it.
        one = self.decide("C3(iii)", "approver", request)
        if one["status"] == "approved" or self.read(k1)["status"] == "approved":
            raise JourneyStepFailed("C3(iii)", "APPROVED_AFTER_ONE_OF_TWO")
        two = self.decide("C3(iii)", "second_approver", request)
        self.k1 = self.read(k1)
        if two["status"] != "approved" or self.k1["status"] != "approved":
            raise JourneyStepFailed("C3(iii)", "NOT_APPROVED_AFTER_TWO")
        self.k2 = k2
        self.k1_ref = f"rating_version:{self.k1['slug']}@{self.k1['version']}"
        self.k2_ref = f"rating_version:{k2['slug']}@{k2['version']}"
        self.result.k1_bundle_hash = str(self.k1["bundle"]["content_hash"])
        self.result.k2_bundle_hash = str(k2["bundle"]["content_hash"])
        self.done(
            "C3(iii)",
            "one of two approvals leaves the request in review; the second approves (FR-354)",
        )

    def listed(self, step: str, environment: str) -> list[dict[str, Any]]:
        listed: dict[str, Any] = self.req(
            step, "deployer", "GET", f"/environments/{environment}/deployments", expect=200
        )
        return list(listed["items"])

    def refusals(self) -> None:
        self.start("C2(prod)")
        before = [d["id"] for d in self.listed("C2(prod)", "prod")]
        self.req(
            "C2(prod)",
            "deployer",
            "POST",
            "/environments/prod/deployment-requests",
            expect=422,
            code="EVIDENCE_INCOMPLETE",
            json={
                "rating_version_ref": self.k1_ref,
                "change_summary": "WF-701 C2: prod before uat",
            },
        )
        after = self.listed("C2(prod)", "prod")
        if [d["id"] for d in after] != before or after[0]["rating_version_ref"] != self.rv3_ref:
            raise JourneyStepFailed("C2(prod)", "PROD_LIST_CHANGED")
        self.done(
            "C2(prod)",
            "422 EVIDENCE_INCOMPLETE: prod needs a successful uat deployment first (FR-429)",
        )

        self.start("C2(route)")
        uat_before = [d["id"] for d in self.listed("C2(route)", "uat")]
        self.req(
            "C2(route)",
            "deployer",
            "POST",
            "/environments/uat/deployments",
            expect=409,
            code="PROMOTION_ORDER_VIOLATION",
            json={"rating_version_ref": self.k1_ref, "reason": "WF-701 C2: uat before dev"},
        )
        if [d["id"] for d in self.listed("C2(route)", "uat")] != uat_before:
            raise JourneyStepFailed("C2(route)", "UAT_LIST_CHANGED")
        self.done(
            "C2(route)",
            "409 PROMOTION_ORDER_VIOLATION: uat needs a successful dev deployment first",
        )

        self.req(
            "PRECONDITION",
            "deployer",
            "POST",
            "/environments/dev/deployments",
            expect=201,
            json={
                "rating_version_ref": self.k1_ref,
                "reason": "WF-701 precondition: dev before uat",
            },
        )
        if self.listed("PRECONDITION", "dev")[0]["rating_version_ref"] != self.k1_ref:
            raise JourneyStepFailed("PRECONDITION", "NOT_LISTED")
        self.say("PRECONDITION dev: K1 deployed to dev (a setup step, not an A-step)")

        self.start("FR-238")
        uat_before = [d["id"] for d in self.listed("FR-238", "uat")]
        self.req(
            "FR-238",
            "deployer",
            "POST",
            "/environments/uat/deployments",
            expect=409,
            code="VALIDATION_FAILED",
            json={
                "rating_version_ref": self.k2_ref,
                "reason": "WF-701 FR-238: compiled, not approved",
            },
        )
        if [d["id"] for d in self.listed("FR-238", "uat")] != uat_before:
            raise JourneyStepFailed("FR-238", "UAT_LIST_CHANGED")
        self.done("FR-238", "409 VALIDATION_FAILED: only an approved Rating Version deploys")

    def uat_and_a(self) -> None:
        self.uat_key = self.key("wf701-uat", "uat")
        self.start("A1")
        deployed = self.stream_across(
            "A2",
            self.uat_key,
            lambda: self.req(
                "A1",
                "deployer",
                "POST",
                "/environments/uat/deployments",
                expect=201,
                json={"rating_version_ref": self.k1_ref, "reason": "WF-701 A1: K1 to uat"},
            ),
            self.rv3_hash,
            self.result.k1_bundle_hash,
        )
        head = self.listed("A1", "uat")[0]
        if (
            head["rating_version_ref"] != self.k1_ref
            or head["bundle_hash"] != self.result.k1_bundle_hash
        ):
            raise JourneyStepFailed("A1", "NOT_LISTED_FIRST")
        self.done("A1", f"K1 {self.result.k1_bundle_hash[:19]} is uat's newest deployment")
        self.start("A2")
        note = self.commit_set("A2", "uat", deployed)
        if note == COMPOSE_ONLY:
            self.printed.append(COMPOSE_ONLY)
        self.done(
            "A2", f"old or new, none old after the deploy ({self.stream_total} responses); {note}"
        )

        self.start("A3")
        event = self.req(
            "A3",
            "admin",
            "GET",
            "/audit",
            expect=200,
            params={"entity": "environment:uat", "action": "deployment.created", "limit": 1},
        )["items"][0]
        if (
            event["after"]["rating_version_ref"] != self.k1_ref
            or event["justification"] != "WF-701 A1: K1 to uat"
            or event["actor"].get("id") != self.record["deployer_id"]
            or event["before"] is None
        ):
            raise JourneyStepFailed("A3", "AUDIT_EVENT_DIFFERS")
        self.done("A3", "deployment.created: before and after state, the reason, the deployer")

        self.start("A4")
        scored = self.score("A4", self.uat_key, self.context)
        if (
            scored["outcome"] != "quoted"
            or scored["bundle_hash"] != self.result.k1_bundle_hash
            or not scored["premium_ladder"]
        ):
            raise JourneyStepFailed("A4", "SERVED_BUNDLE_DIFFERS")
        self.done("A4", f"uat served K1: {payable_minor(scored)} minor units")
        self.a5_a6()

    def compare(self, context: Mapping[str, Any]) -> dict[str, Any]:
        compared: dict[str, Any] = self.req(
            "A5",
            "analyst",
            "POST",
            "/score/compare",
            expect=200,
            json={"context": dict(context), "base": self.rv3_ref, "comparison": self.k1_ref},
        )
        return compared

    def a5_a6(self) -> None:
        self.start("A5")
        template = self.context["inputs"]
        base = {k: v for k, v in self.context.items() if k != "inputs"}
        count = COMPARE_POLICIES
        best: tuple[float, dict[str, Any], dict[str, Any]] | None = None
        changed = total = 0
        while best is None and count <= 10 * COMPARE_POLICIES:
            # A6 needs a quote where K1 binds the minimum premium and rv3 does not (Task 0.5):
            # the sample grows and the final K is recorded; a quote is never made up.
            policies = contract_sample(self.algorithm["input_contract"], template, count)
            changed = total = 0
            for inputs in policies:
                context = {**base, "inputs": inputs}
                both = self.compare(context)
                total += 1
                before, after = payable_minor(both["base"]), payable_minor(both["comparison"])
                if before != after:
                    changed += 1
                    move = abs(after - before) / before if before else 0.0
                    if (
                        binds_min_premium(both["comparison"])
                        and not binds_min_premium(both["base"])
                        and (best is None or move > best[0])
                    ):
                        best = (move, context, both)
            if best is None:
                count *= 2
        if changed == 0:
            raise JourneyStepFailed("A5", "NO_PREMIUM_DIFFERS")
        self.result.a5_totals = {"compared": total, "changed": changed}
        self.done(
            "A5",
            f"{total} contract-domain policies compared, {changed} premiums differ (K = {count})",
        )
        if best is None:
            raise JourneyStepFailed("A6", "NO_QUOTE_BINDS_THE_NEW_MINIMUM")
        self.start("A6")
        move, context, _ = best
        traced = self.score(
            "A6",
            self.uat_key,
            {**context, "options": {"trace": True}},
        )
        steps = {s["step_id"]: s for s in (traced.get("trace") or {}).get("steps", [])}
        if (
            "s_floor" not in steps
            or not steps["s_floor"].get("violation")
            or not binds_min_premium(traced)
        ):
            raise JourneyStepFailed("A6", "K1_TRACE_SHOWS_NO_MIN_PREMIUM")
        base_traced = self.req(
            "A6",
            "analyst",
            "POST",
            "/score/compare",
            expect=200,
            json={"context": context, "base": self.rv3_ref, "comparison": self.k1_ref},
        )["base"]
        if binds_min_premium(base_traced):
            raise JourneyStepFailed("A6", "RV3_ALSO_APPLIES_THE_MINIMUM")
        self.done(
            "A6", f"s_floor applied MIN_PREMIUM_APPLIED in K1 only; the move is {move * 100:.1f} %"
        )

    def prod_and_c(self) -> None:
        self.start("C3(ii)")
        before = [d["id"] for d in self.listed("C3(ii)", "prod")]
        self.req(
            "C3(ii)",
            "deployer",
            "POST",
            "/environments/prod/deployments",
            expect=409,
            code="DEPLOY_REQUIRES_APPROVAL",
            json={"rating_version_ref": self.k1_ref, "reason": "WF-701 C3: no request named"},
        )
        if [d["id"] for d in self.listed("C3(ii)", "prod")] != before:
            raise JourneyStepFailed("C3(ii)", "PROD_LIST_CHANGED")
        self.done("C3(ii)", "409 DEPLOY_REQUIRES_APPROVAL: a prod deploy needs an approved request")

        self.prod_key = self.key("wf701-prod", "prod")
        self.start("C1")
        asked = self.req(
            "C1",
            "deployer",
            "POST",
            "/environments/prod/deployment-requests",
            expect=201,
            json={"rating_version_ref": self.k1_ref, "change_summary": "WF-701 C1: K1 to prod"},
        )
        self.decide("C1", "prod_approver", str(asked["approval_request_id"]))
        started = time.monotonic()
        deployed = self.stream_across(
            "C4",
            self.prod_key,
            lambda: self.req(
                "C1",
                "deployer",
                "POST",
                "/environments/prod/deployments",
                expect=201,
                json={
                    "rating_version_ref": self.k1_ref,
                    "reason": "WF-701 C1: K1 to prod",
                    "deployment_request_ref": asked["ref"],
                },
            ),
            self.rv3_hash,
            self.result.k1_bundle_hash,
        )
        self.result.c4_elapsed_s = time.monotonic() - started
        if self.listed("C1", "prod")[0]["rating_version_ref"] != self.k1_ref:
            raise JourneyStepFailed("C1", "NOT_LISTED_FIRST")
        self.done(
            "C1", "a decided Deployment Request, then the deploy; K1 is prod's newest deployment"
        )

        self.start("C4")
        note = self.commit_set("C4", "prod", deployed)
        if note == COMPOSE_ONLY:
            self.printed.append(COMPOSE_ONLY)
        if self.result.c4_elapsed_s >= FUNCTIONAL_BOUND_S:
            raise JourneyStepFailed("C4", "DEPLOY_OVER_THE_FUNCTIONAL_BOUND")
        self.done(
            "C4",
            f"old or new, none old after the deploy; {note}; {self.result.c4_elapsed_s:.1f} s "
            f"(< {FUNCTIONAL_BOUND_S:.0f} s functional bound, not the NFR-494 verdict)",
        )

        self.start("C6")
        for _ in range(C6_QUOTES):
            scored = self.score("C6", self.prod_key, self.context)
            if scored["bundle_hash"] != self.result.k1_bundle_hash or scored["outcome"] != "quoted":
                raise JourneyStepFailed("C6", "SERVED_BUNDLE_DIFFERS")
        golden = payable_minor(self.score("C6", self.prod_key, self.context))
        if golden not in (self.result.prod_golden_minor, 18000):
            raise JourneyStepFailed("C6", "PREMIUM_DIFFERS_FROM_THE_GOLDEN_QUOTE")
        self.done(
            "C6", f"{C6_QUOTES} prod quotes on K1's hash; the golden quote is {golden} minor units"
        )

    # -- C7: sampling ---------------------------------------------------------------------------
    def drain_traces(self, step: str) -> None:
        """In process, nothing consumes the queue: run each queued `score.trace_produce` Job."""
        if self.run_job is None:
            return
        while True:
            queued = self.req(
                step,
                "analyst",
                "GET",
                "/jobs",
                expect=200,
                params={"kind": "score.trace_produce", "status": "queued", "limit": PAGE},
            )["items"]
            if not queued:
                return
            for job in queued:
                self.run_job(str(job["id"]))

    def trace_list(self, step: str, rating_version: str | None = None) -> list[dict[str, Any]]:
        params = {"rating_version": rating_version} if rating_version else {}
        return self.pages(step, "analyst", "/traces", **params)

    def stable_traces(self, step: str, rating_version: str) -> list[dict[str, Any]]:
        """Poll until two reads, a second apart, count the same; the worker is asynchronous."""
        deadline = time.monotonic() + self.job_timeout
        last = -1
        while True:
            self.drain_traces(step)
            traces = self.trace_list(step, rating_version)
            if len(traces) == last:
                return traces
            last = len(traces)
            if time.monotonic() > deadline:
                raise JourneyStepFailed(step, "TRACES_NEVER_SETTLED")
            time.sleep(1.0)

    def c7(self) -> None:
        self.start("C7(i)")
        for _ in range(C7_QUOTES):
            if self.score("C7(i)", self.prod_key, self.context)["outcome"] != "quoted":
                raise JourneyStepFailed("C7(i)", "NOT_QUOTED")
        traces = self.stable_traces("C7(i)", self.k1_ref)
        self.result.c7_count = len(traces)
        outside = float(outside_band_probability(C7_QUOTES, C7_RATE, C7_BAND))
        check_trace_count(len(traces))
        self.done(
            "C7(i)",
            f"{len(traces)} traces of N = {C7_QUOTES} quotes at p = {float(C7_RATE)}; "
            f"band [{C7_BAND[0]}, {C7_BAND[1]}] (outside it: {outside:.3e})",
        )
        self.start("C7(ii)")
        if any(t["bundle_hash"] != self.result.k1_bundle_hash for t in traces):
            raise JourneyStepFailed("C7(ii)", "TRACE_ON_ANOTHER_BUNDLE")
        self.done("C7(ii)", "every persisted trace carries K1's bundle hash")

        self.start("C7(iii)")
        self.deploy_k2()
        low, high = json.loads(K2_FILE.read_text(encoding="utf-8"))["declined_bonus_malus"]
        for i in range(C7_DECLINES):
            inputs = {**self.context["inputs"], "bonus_malus": low + i % (high - low + 1)}
            scored = self.score("C7(iii)", self.prod_key, {**self.context, "inputs": inputs})
            if scored["outcome"] != "declined":
                raise JourneyStepFailed("C7(iii)", "NOT_DECLINED")
        declined = [
            t for t in self.stable_traces("C7(iii)", self.k2_ref) if t["sample_reason"] == "decline"
        ]
        self.result.c7_declined = len(declined)
        if len(declined) != C7_DECLINES:
            raise JourneyStepFailed("C7(iii)", f"DECLINED_TRACES_{len(declined)}_OF_{C7_DECLINES}")
        self.done(
            "C7(iii)",
            f"exactly {C7_DECLINES} of {C7_DECLINES} declined quotes are traced (the 100 % floor)",
        )

        self.start("C7(iv)")
        quote_id = f"wf701-c7-errors-{uuid4()}"
        incomplete = {k: v for k, v in self.context["inputs"].items() if k != "area"}
        self.score(
            "C7(iv)",
            self.prod_key,
            {**self.context, "inputs": incomplete, "quote_id": quote_id},
            expect=422,
            code="INPUT_CONTRACT_VIOLATION",
        )
        self.drain_traces("C7(iv)")
        if any(t.get("quote_id") == quote_id for t in self.trace_list("C7(iv)")):
            raise JourneyStepFailed("C7(iv)", "A_REFUSED_QUOTE_WAS_TRACED")
        self.say(C7_ERRORS)
        self.done("C7(iv)", "422 INPUT_CONTRACT_VIOLATION; no listed trace carries the quote_id")

    def deploy_k2(self) -> None:
        """K2 reaches prod by the governed path only: evidence, two approvals, dev, uat, then a
        decided Deployment Request for prod. No row is written, no status is set."""
        request = self.evidence("K2", self.k2, floor_minor=None)
        self.decide("K2", "approver", request)
        self.decide("K2", "second_approver", request)
        if self.read(self.k2)["status"] != "approved":
            raise JourneyStepFailed("K2", "NOT_APPROVED")
        for environment in ("dev", "uat"):
            self.req(
                "K2",
                "deployer",
                "POST",
                f"/environments/{environment}/deployments",
                expect=201,
                json={
                    "rating_version_ref": self.k2_ref,
                    "reason": f"WF-701 C7: K2 to {environment}",
                },
            )
        asked = self.req(
            "K2",
            "deployer",
            "POST",
            "/environments/prod/deployment-requests",
            expect=201,
            json={"rating_version_ref": self.k2_ref, "change_summary": "WF-701 C7: K2 to prod"},
        )
        self.decide("K2", "prod_approver", str(asked["approval_request_id"]))
        self.req(
            "K2",
            "deployer",
            "POST",
            "/environments/prod/deployments",
            expect=201,
            json={
                "rating_version_ref": self.k2_ref,
                "reason": "WF-701 C7: K2 to prod",
                "deployment_request_ref": asked["ref"],
            },
        )
        if self.listed("K2", "prod")[0]["rating_version_ref"] != self.k2_ref:
            raise JourneyStepFailed("K2", "NOT_LISTED_FIRST")


def run_wf701_after(
    client: httpx.Client,
    record: Mapping[str, str],
    wf699: Any,
    *,
    log: Callable[[str], None] = print,
    run_job: JobRunner | None = None,
    job_timeout: float = 1800.0,
    replica_hosts: Callable[[], frozenset[str]] | None = None,
    stream_client: Callable[[], httpx.Client] | None = None,
    before_step: Callable[[str], None] | None = None,
) -> Wf701Result:
    """Walk WF-701's deployment steps on the state `wf699` (WF-699's `JourneyResult`) left.

    `replica_hosts` names the hosts the stack runs `api` on (compose only): given, A2 and C4 assert
    the audit log's COMMIT set equals it; absent, the one `COMPOSE_ONLY` line is printed instead.
    `stream_client` makes the A2/C4 `/score` stream a thread beside the deploy (compose only).
    `before_step(step)` runs before a step, so a test can break the setting that step reads."""
    return _Wf701(
        client, record, wf699, log, run_job, job_timeout, replica_hosts, stream_client, before_step
    ).run()


def run_wf701_journey(
    client: httpx.Client,
    record: Mapping[str, str],
    *,
    log: Callable[[str], None] = print,
    run_job: JobRunner | None = None,
    job_timeout: float = 1800.0,
    **kwargs: Any,
) -> Wf701Result:
    """WF-699's journey, then WF-701's (`run_wf701_after`)."""
    wf699 = run_wf699_journey(client, record, log=log, run_job=run_job, job_timeout=job_timeout)
    return run_wf701_after(
        client, record, wf699, log=log, run_job=run_job, job_timeout=job_timeout, **kwargs
    )
