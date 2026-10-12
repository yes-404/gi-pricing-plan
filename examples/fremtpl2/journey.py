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

import copy
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
        "kind": "monotone",
        "input": "bonus_malus",
        "direction": "increasing",
        "strict": False,
        "lower": "50",
        "upper": "230",
    },
}
D4_GRID_SPACING: Final = (230 - 50) // 4


def declared_d4_property() -> dict[str, Any]:
    """D4's property, a copy of the constant. It takes no fit (and no table, and no database):
    a property chosen from the fit it is checked against can never fail (the maintainer's
    18:59:23 rule), so there is nothing here to hand a fit to."""
    return copy.deepcopy(D4_PROPERTY)


#: The NCD ladder's demo bands (not a priced scale): factor by `bonus_malus` band. The defect
#: (D4) sets the middle band to 0.90, a band 50 wide, wider than the spacing of 45.
LADDER_SLUG: Final = "ncd-ladder"
LADDER_BANDS: Final = {"low": "1.00", "middle": "1.20", "high": "1.50"}
LADDER_DEFECT_MIDDLE: Final = "0.90"
LADDER_MIDDLE_EDGES: Final = (100, 150)

#: B3's reference rows are in force from this date; a quote dated before it finds no row.
EFFECTIVE_FROM: Final = "2020-01-01"
BEFORE_EFFECTIVE_FROM: Final = "2019-06-01"
#: One region's loading rises to 1.05 on this date, after every golden and demo quote date; a
#: quote on a later date in that region is the earlier premium x 1.05 (the multiply is observable).
LOADING_RISES_ON: Final = "2027-01-01"
LOADING_AFTER: Final = "1.05"
AFTER_LOADING_RISES: Final = "2027-06-01"


def ladder_body(middle: str, change_note: str) -> dict[str, Any]:
    """The `ncd-ladder` sub-graph body: bands 50-99, 100-149, 150-230 on `bonus_malus`."""
    low, high = LADDER_BANDS["low"], LADDER_BANDS["high"]
    first, second = LADDER_MIDDLE_EDGES
    expr = f"bonus_malus < {first} ? {low} : (bonus_malus < {second} ? {middle} : {high})"
    return {
        "inputs": [{"name": "bonus_malus", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "decimal", "required": True}],
        "steps": [
            {
                "step_id": "s_ladder",
                "type": "expression",
                "label": "NCD ladder",
                "expr": expr,
                "result_type": "decimal",
                "consumes": ["bonus_malus"],
                "produces": "ncd_factor",
            }
        ],
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
            step,
            problem_code or f"HTTP_{response.status_code}",
            response.status_code,
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
        self.loading_ref: str | None = None
        self.loading_region = ""

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
        self.discover()
        self.phase_a()
        self.phase_b()
        self.phase_c()
        self.phase_d()
        self.phase_e()
        self.deploy_and_score()
        return self.result

    # -- setup: the approved models, found over HTTP -----------------------------------
    def discover(self) -> None:
        approved = self.req(
            "A0",
            "analyst",
            "GET",
            "/models",
            params={"status": "approved", "limit": 100},
            expect=200,
        )["items"]
        glm = next(
            (m for m in approved if (m.get("fit_result") or {}).get("model_type") == "glm"), None
        )
        if glm is None:
            raise JourneyStepFailed("A0", "NO_APPROVED_GLM")
        self.glm = glm
        self.glm_ref = f"model:{glm['model_family_slug']}@{glm['version']}"
        self.factors: list[str] = list(glm["fit_result"]["relativities"])
        drafts = self.req(
            "A0",
            "analyst",
            "GET",
            "/models",
            params={"status": "fitted", "limit": 100},
            expect=200,
        )["items"]
        gbm = next((m for m in drafts if m.get("fit_result") is not None), None)
        if gbm is None:
            raise JourneyStepFailed("A0", "NO_UNAPPROVED_GBM")
        self.gbm = gbm
        self.gbm_ref = f"model:{gbm['model_family_slug']}@{gbm['version']}"

    # -- Phase A: from the technical estimate to rate tables ---------------------------
    def phase_a(self) -> None:
        slugs = {f: "wf699-" + f.replace("_", "-") for f in self.factors}
        self.table_refs: dict[str, str] = {}
        seed_notes: list[str] = []
        for factor, slug in slugs.items():
            seeded = self.req(
                "A1",
                "analyst",
                "POST",
                f"/rate-tables/{slug}/seed-from-model",
                expect=201,
                json={
                    "model_ref": self.glm_ref,
                    "factor": factor,
                    "change_note": f"seeded from {self.glm_ref}: the technical rate, explicitly",
                },
            )
            if (
                not seeded.get("seeded_from")
                or len(seeded["keys"]) != 1
                or not seeded["keys"][0].get("factor_ref")
            ):
                raise JourneyStepFailed("A1", "SEED_NOT_RECORDED")
            self.table_refs[factor] = f"rate_table:{slug}@{seeded['version']}"
            seed_notes.append(seeded.get("change_note", ""))
        self.done("A1", f"{len(slugs)} tables, one per rateable Factor of the approved GLM")
        self.done("A2")

        edited = "region" if "region" in slugs else self.factors[-1]
        edit_slug = slugs[edited]
        exported = self.req(
            "A3", "analyst", "GET", f"/rate-tables/{edit_slug}@1/export/csv", expect=200
        )
        header, rows = _csv_cells(exported)
        middle = len(rows) // 2
        before = Decimal(rows[middle][-1])
        rows[middle][-1] = format(before * Decimal("0.98"), "f")  # commercial judgement: -2 %
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
        imported = self.req(
            "A3",
            "analyst",
            "POST",
            f"/rate-tables/{edit_slug}@1/import",
            expect=201,
            files={"file": (f"{edit_slug}.csv", buffer.getvalue(), "text/csv")},
            data={"confirm": "true"},
        )
        self.table_refs[edited] = f"rate_table:{edit_slug}@{imported['version']}"
        portfolio = self.record["portfolio_dataset_version_id"]
        for against in ("previous", "seed"):
            diff = self.diff(edit_slug, imported["version"], against, portfolio)
            if not diff["changed_cells"]:
                raise JourneyStepFailed("A3", "DIFF_EMPTY")
        cells = self.req(
            "A3",
            "analyst",
            "GET",
            f"/rate-tables/{edit_slug}@{imported['version']}/diff/cells",
            params={"against": "previous", "portfolio": portfolio},
            expect=200,
        )
        if not any(cell.get("weight") is not None for cell in cells["items"]):
            raise JourneyStepFailed("A3", "NO_EXPOSURE_WEIGHT")
        self.done("A3", f"{edit_slug}: both diffs non-empty, a weight per changed cell")

        bulk_slug = slugs["area"] if "area" in slugs else slugs[self.factors[0]]
        bulk = self.req(
            "A4",
            "analyst",
            "POST",
            f"/rate-tables/{bulk_slug}@1/bulk-operation",
            expect=201,
            json={"kind": "uplift_table", "parameters": {"percentage": "2"}},
        )
        bulk_factor = next(f for f, s in slugs.items() if s == bulk_slug)
        self.table_refs[bulk_factor] = f"rate_table:{bulk_slug}@{bulk['version']}"
        self.done("A4", f"{bulk_slug}: +2 % as a recorded operation")

        duplicate = [header, *rows, rows[0]]
        buffer = io.StringIO()
        csv.writer(buffer, lineterminator="\n").writerows(duplicate)
        self.req(
            "A5",
            "analyst",
            "POST",
            f"/rate-tables/{edit_slug}@{imported['version']}/import",
            expect=422,
            code="RATE_TABLE_KEY_DUPLICATE",
            files={"file": (f"{edit_slug}-dup.csv", buffer.getvalue(), "text/csv")},
            data={"confirm": "true"},
        )
        self.done("A5", "a duplicate key is refused")

        # A6: every save is a new version with a change note. The notes are read from the create
        # responses (the definition read carries none). Seed and import notes are present; the bulk
        # version's is the service-built one (FD-1491), which is today's behaviour, printed as a
        # known gap and never as ok.
        if not all(str(note).strip() for note in seed_notes):
            raise JourneyStepFailed("A6", "CHANGE_NOTE_MISSING")
        if not str(imported.get("change_note", "")).strip():
            raise JourneyStepFailed("A6", "CHANGE_NOTE_MISSING")
        if not str(bulk.get("change_note", "")).strip():
            raise JourneyStepFailed("A6", "BULK_CHANGE_NOTE_ABSENT_NOT_THE_FD_1491_BEHAVIOUR")
        self.skip("A6")

    def diff(self, slug: str, version: int, against: str, portfolio: str) -> dict[str, Any]:
        path = f"/rate-tables/{slug}@{version}/diff"
        params = {"against": against, "portfolio": portfolio}
        response = self.client.get(path, params=params, headers=self.who("analyst"))
        if response.status_code == 202:
            self.job_ok("A3", "analyst", response.json())
            response = self.client.get(path, params=params, headers=self.who("analyst"))
        if response.status_code != 200:
            raise JourneyStepFailed("A3", "DIFF_FAILED", response.status_code)
        body: dict[str, Any] = response.json()
        return body

    # -- Phase B: the rating algorithm -----------------------------------------------------
    def phase_b(self) -> None:
        self.seeded = self.req(
            "B1", "analyst", "GET", "/rating-algorithms/fremtpl2-rate@1", expect=200
        )
        self.ladder_version = 0
        self.algorithm_version = 1
        broken = self.fork(version=99, ladder_ref=None)
        broken["steps"] = [s for s in broken["steps"] if s["step_id"] != "s_in_area"]
        self.req(
            "B6",
            "analyst",
            "POST",
            "/rating-algorithms",
            expect=422,
            code="RATING_GRAPH_UNRESOLVED_REF",
            json=broken,
        )
        self.done("B6", "a dangling input cannot be saved")
        floaty = self.fork(version=99, ladder_ref=None)
        floaty["outputs"][0]["type"] = "float"
        self.req(
            "B9",
            "analyst",
            "POST",
            "/rating-algorithms",
            expect=422,
            code="VALIDATION_FAILED",
            json=floaty,
        )
        self.skip("B9")
        self.skip("B4")
        self.done("B8", "output rounding half_even, 0 dp")
        self.reference_table()

    def fork(self, *, version: int, ladder_ref: str | None) -> dict[str, Any]:
        """The seeded algorithm forked to `version` over the A-phase tables (WF-699 B1) and, with
        a `ladder_ref`, with the NCD ladder mounted and its factor in the premium (B7)."""
        payload: dict[str, Any] = {
            key: value
            for key, value in self.seeded.items()
            if key in ("slug", "input_contract", "outputs", "steps", "sub_graphs")
        }
        payload = {**payload, "version": version}
        payload["steps"] = [dict(step) for step in payload["steps"]]
        payload["outputs"] = [dict(out) for out in payload["outputs"]]
        for step in payload["steps"]:
            if step["type"] == "table":
                factor = step["step_id"].removeprefix("s_t_")
                step["rate_table_ref"] = self.table_refs[factor]
        if ladder_ref is not None:
            payload["sub_graphs"] = [
                {
                    "ref": ladder_ref,
                    "mount_point": "m_ncd",
                    "inputs": {"bonus_malus": "bonus_malus"},
                    "outputs": {"ncd_factor": "ncd_factor"},
                }
            ]
            for step in payload["steps"]:
                if step["step_id"] == "s_premium":
                    step["expr"] = f"{step['expr']} * ncd_factor"
                    step["consumes"] = [*step["consumes"], "ncd_factor"]
            if self.loading_ref is not None:
                # B3: the loading in force on the quote's effective date, from the pinned
                # reference table (FR-221). `on_miss: error`, so a quote dated before the row's
                # `effective_from` does not use it and is refused instead of priced without it.
                lookup = {
                    "step_id": "s_loading",
                    "type": "lookup",
                    "label": "Expense loading as at the effective date",
                    "reference_table_ref": self.loading_ref,
                    "key_expr": ["region"],
                    "as_at": "effective_date",
                    "on_miss": "error",
                    "consumes": ["region"],
                    "produces": "expense_loading",
                }
                steps = payload["steps"]
                at = next(i for i, step in enumerate(steps) if step["step_id"] == "s_premium")
                payload["steps"] = [*steps[:at], lookup, *steps[at:]]
                for step in payload["steps"]:
                    if step["step_id"] == "s_premium":
                        step["expr"] = f"{step['expr']} * number(expense_loading)"
                        step["consumes"] = [*step["consumes"], "expense_loading"]
        return payload

    def reference_table(self) -> None:
        """B3: a reference table created over HTTP by the seeded admin through the existing
        `/reference-tables` routes, loaded with one row per region (loading 1.00, so the premium
        is unchanged) effective from 2020-01-01, and published so that it can be pinned."""
        slug = "wf699-region-loading"
        self.req(
            "B3",
            "admin",
            "POST",
            "/reference-tables",
            expect=201,
            json={
                "slug": slug,
                "key_columns": ["region"],
                "payload_columns": ["expense_loading"],
                "description": "WF-699 B3: the expense loading in force by region, as at a date",
            },
        )
        relativities = self.glm["fit_result"]["relativities"]["region"]
        levels = [r["level"] for r in relativities]
        # The golden quotes sit on each Factor's base level, so the region with a second row is the
        # base region: the same region on two dates then hits two rows. The 1.05 row starts after
        # every golden and demo quote date, so no golden moves.
        self.loading_region = next(r["level"] for r in relativities if r["is_base"])
        rows: list[dict[str, Any]] = []
        for level in levels:
            if level == self.loading_region:
                rows.append(
                    {
                        "key": level,
                        "payload": {"expense_loading": "1.00"},
                        "effective_from": EFFECTIVE_FROM,
                        "effective_to": LOADING_RISES_ON,
                    }
                )
                rows.append(
                    {
                        "key": level,
                        "payload": {"expense_loading": LOADING_AFTER},
                        "effective_from": LOADING_RISES_ON,
                    }
                )
            else:
                rows.append(
                    {
                        "key": level,
                        "payload": {"expense_loading": "1.00"},
                        "effective_from": EFFECTIVE_FROM,
                    }
                )
        loaded = self.req(
            "B3",
            "admin",
            "POST",
            f"/reference-tables/{slug}/versions",
            expect=201,
            json={
                "source_note": f"demo loading: 1.00, and {LOADING_AFTER} in {self.loading_region} "
                f"from {LOADING_RISES_ON}",
                "rows": rows,
            },
        )
        self.req(
            "B3",
            "admin",
            "POST",
            f"/reference-tables/{slug}/versions/{loaded['version']}/publish",
            expect=(200, 201),
        )
        self.loading_ref = f"reference_table:{slug}@{loaded['version']}"
        self.done("B3", f"{self.loading_ref}: a pinned lookup as at the effective date")

    def build_version(self, label: str, middle: str, change_note: str) -> dict[str, Any]:
        """B7 and C1: save the next ladder, the algorithm mounting it by exact pin, and a Rating
        Version pinning everything. The versions are read from the create responses."""
        body = ladder_body(middle, change_note)
        if self.ladder_version == 0:
            ladder = self.req(
                "B7",
                "analyst",
                "POST",
                "/sub-graphs",
                expect=201,
                json={"slug": LADDER_SLUG, **body},
            )
        else:
            ladder = self.req(
                "B7",
                "analyst",
                "POST",
                f"/sub-graphs/{LADDER_SLUG}/versions",
                expect=201,
                json=body,
            )
        self.ladder_version = int(ladder["version"])
        ladder_ref = f"sub_graph:{LADDER_SLUG}@{self.ladder_version}"
        self.algorithm_version += 1
        saved = self.req(
            "B1",
            "analyst",
            "POST",
            "/rating-algorithms",
            expect=201,
            json=self.fork(version=self.algorithm_version, ladder_ref=ladder_ref),
        )
        version = self.req(
            "C1",
            "analyst",
            "POST",
            "/rating-versions",
            expect=201,
            json={
                "slug": "fremtpl2-wf699",
                "dataset_version_id": self.glm["dataset_version_id"],
                "model_ref": self.glm_ref,
                "algorithm_ref": f"rating_algorithm:{saved['slug']}@{saved['version']}",
                "pins": {
                    "rate_tables": list(self.table_refs.values()),
                    "models": [self.glm_ref, self.gbm_ref],
                    "reference_tables": [self.loading_ref] if self.loading_ref else [],
                    "sub_graphs": [ladder_ref],
                },
            },
        )
        self.log(
            f"  {label}: rating version {version['slug']}@{version['version']} pins {ladder_ref}"
        )
        return dict(version)

    def compile(
        self, step: str, version: Mapping[str, Any], *, expect_failure: str | None = None
    ) -> dict[str, Any]:
        accepted = self.req(
            step, "analyst", "POST", f"/rating-versions/{version['id']}/compile", expect=202
        )
        job = self.job(step, "analyst", accepted)
        if expect_failure is None:
            if job["status"] != "succeeded":
                raise JourneyStepFailed(step, (job.get("error") or {}).get("code") or "JOB_FAILED")
        elif (job.get("error") or {}).get("code") != expect_failure:
            raise JourneyStepFailed(step, (job.get("error") or {}).get("code") or job["status"])
        return job

    # -- Phase C: compile and pin ------------------------------------------------------------
    def phase_c(self) -> None:
        self.rv1 = self.build_version("RV1", LADDER_BANDS["middle"], "the NCD ladder, demo bands")
        self.done("B7", f"{LADDER_SLUG}@{self.ladder_version} mounted by exact pin")
        self.skip("C1′")  # noqa: RUF001
        self.done("C1", "the version pins the algorithm, every table, both models and the ladder")
        self.compile("C2", self.rv1, expect_failure="PIN_NOT_APPROVED")
        self.done("C4", "PIN_NOT_APPROVED: the GBM is not approved")
        self.approve_gbm()
        self.compile("C5", self.rv1)
        read = self.req("C6", "analyst", "GET", f"/rating-versions/{self.rv1['id']}", expect=200)
        self.done("C2")
        self.done("C3")
        self.done("C5", "approved through the workflow, recompiled")
        self.done("C6", read["bundle"]["content_hash"])

    def approve_gbm(self) -> None:
        slug, number = self.gbm["model_family_slug"], self.gbm["version"]
        fetched = self.client.get(
            f"/models/{slug}", params={"version": number}, headers=self.who("actuary")
        )
        if fetched.status_code != 200:
            raise JourneyStepFailed("C5", "MODEL_READ_FAILED", fetched.status_code)
        call(
            self.client,
            "C5",
            "POST",
            f"/models/{self.gbm['id']}/submit",
            expect=200,
            headers={**self.who("actuary"), "If-Match": fetched.headers["etag"]},
            json={"change_summary": "the GBM as a challenger for the rating version"},
        )
        # The submit route answers with the Model, not the request: find its Approval Request.
        requests = self.req(
            "C5",
            "approver",
            "GET",
            "/approval-requests",
            params={"artifact_type": "model", "limit": 100},
            expect=200,
        )["items"]
        pending = [r for r in requests if r["artifact_ref"] == self.gbm_ref]
        if not pending:
            raise JourneyStepFailed("C5", "NO_APPROVAL_REQUEST_FOR_THE_MODEL")
        self.decide_until_approved("C5", str(pending[0]["id"]))

    def decide_until_approved(self, step: str, request_id: str) -> None:
        for who in ("approver", "second_approver", "prod_approver"):
            decided = self.req(
                step,
                who,
                "POST",
                f"/approval-requests/{request_id}/decide",
                expect=200,
                json={"decision": "approve", "comment": "approved in the WF-699 journey"},
            )
            if decided["status"] == "approved":
                return
        raise JourneyStepFailed(step, "NOT_APPROVED")

    # -- Phase D: evidence --------------------------------------------------------------------
    def regression(
        self, step: str, version: Mapping[str, Any], *, expect_failure: bool
    ) -> dict[str, Any]:
        """Run the suite. A failed Job still records the run, whose id is only in the Job's
        message (no route lists runs), so it is read from there."""
        accepted = self.req(
            step, "analyst", "POST", f"/rating-versions/{version['id']}/regression-runs", expect=202
        )
        job = self.job(step, "analyst", accepted)
        if job["status"] == "succeeded":
            if expect_failure:
                raise JourneyStepFailed(step, "RUN_PASSED_BUT_A_FAILURE_WAS_EXPECTED")
            run_id = str(job["result"]["ref"]).split(":", 1)[1]
        else:
            if not expect_failure:
                raise JourneyStepFailed(step, (job.get("error") or {}).get("code") or "JOB_FAILED")
            found = re.search(
                r"regression run ([0-9a-f-]{36})", (job.get("error") or {}).get("message", "")
            )
            if found is None:
                raise JourneyStepFailed(step, "RUN_ID_NOT_IN_JOB_MESSAGE")
            run_id = found.group(1)
        run: dict[str, Any] = self.req(
            step,
            "analyst",
            "GET",
            f"/rating-versions/{version['id']}/regression-runs/{run_id}",
            expect=200,
        )
        return run

    def suite_version(
        self,
        change_note: str,
        golden: Sequence[Mapping[str, Any]],
        properties: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        return dict(
            self.req(
                "D3",
                "analyst",
                "POST",
                f"/regression-suites/{self.suite['slug']}/versions",
                expect=201,
                json={
                    "algorithm_slug": self.suite["algorithm_slug"],
                    "golden_quotes": list(golden),
                    "properties": list(properties),
                    "generation": self.suite["generation"],
                    "change_note": change_note,
                },
            )
        )

    def phase_d(self) -> None:
        self.suite = self.req(
            "D1", "analyst", "GET", "/regression-suites/fremtpl2-rate-suite@1", expect=200
        )
        properties = [*self.suite["properties"], declared_d4_property()]
        self.suite_version(
            "adds the declared D4 property: premium increasing in bonus_malus (WF-699 D4)",
            self.suite["golden_quotes"],
            properties,
        )
        run = self.regression("D1", self.rv1, expect_failure=True)
        moved = [g for g in run["golden_results"] if g["status"] == "fail"]
        if not moved:
            raise JourneyStepFailed("D2", "NO_GOLDEN_MOVED")
        d4 = next(p for p in run["property_results"] if p["name"] == D4_PROPERTY["name"])
        if d4["status"] != "pass":
            # The declared property failed before the defect was written: STOP, never re-choose.
            raise JourneyStepFailed("D4", "D4_PROPERTY_FAILED_BEFORE_THE_DEFECT")
        self.done("D1", "the suite, with the D4 property, ran against the first version")
        self.done("D2", f"{len(moved)} of {len(run['golden_results'])} golden quotes moved")

        by_name = {g["name"]: g for g in moved}
        updated = []
        for quote in self.suite["golden_quotes"]:
            if quote["name"] in by_name:
                quote = {
                    **quote,
                    "expected": {
                        **quote["expected"],
                        "payable_premium_minor": by_name[quote["name"]]["actual_minor"],
                    },
                    "note": "updated deliberately: the A-phase table edits and the NCD ladder band "
                    "(1.20 at bonus_malus 100) moved this premium (WF-699 D3)",
                }
            updated.append(quote)
        self.suite = self.suite_version(
            "golden quotes updated deliberately after the A-phase edits and the NCD ladder",
            updated,
            properties,
        )
        self.golden = updated
        passed = self.regression("D3", self.rv1, expect_failure=False)
        if passed["overall"] != "pass":
            raise JourneyStepFailed("D3", "RUN_DID_NOT_PASS")
        self.done("D3", "new suite version; the run passes")

        self.rv2 = self.build_version(
            "RV2", LADDER_DEFECT_MIDDLE, "D4's deliberate defect: the middle band is inverted"
        )
        self.compile("D4", self.rv2)
        failing = self.regression("D4", self.rv2, expect_failure=True)
        d4 = next(p for p in failing["property_results"] if p["name"] == D4_PROPERTY["name"])
        points = d4.get("counterexample_points") or []
        if d4["status"] != "fail" or d4.get("grid") != "uniform+sampled" or len(points) != 2:
            raise JourneyStepFailed("D4", "NO_MONOTONE_FAILURE")
        low, high = LADDER_MIDDLE_EDGES
        if not (
            int(points[0]) < high and int(points[1]) >= low and int(points[0]) < int(points[1])
        ):
            raise JourneyStepFailed("D4", "COUNTEREXAMPLE_NOT_AT_THE_DEFECT")
        self.done(
            "D4",
            f"{D4_PROPERTY['name']} failed between {points[0]} and {points[1]} "
            f"(spacing {D4_GRID_SPACING})",
        )

        self.rv3 = self.build_version("RV3", LADDER_BANDS["middle"], "D5: the middle band restored")
        self.compile("D5", self.rv3)
        fixed = self.regression("D5", self.rv3, expect_failure=False)
        d4 = next(p for p in fixed["property_results"] if p["name"] == D4_PROPERTY["name"])
        if fixed["overall"] != "pass" or d4["status"] != "pass":
            raise JourneyStepFailed("D5", "D4_PROPERTY_FAILED_AFTER_THE_FIX")
        self.done("D5", "the same property passes")

    # -- Phase E: approval ------------------------------------------------------------------
    def submit(self, step: str, text: str, *, expect: int, code: str | None = None) -> Any:
        return self.req(
            step,
            "actuary",
            "POST",
            f"/rating-versions/{self.rv3['id']}/submit",
            expect=expect,
            code=code,
            json={"change_summary": text},
        )

    def phase_e(self) -> None:
        draft = self.req(
            "E1",
            "analyst",
            "GET",
            f"/rating-versions/{self.rv3['id']}/change-summary-draft",
            expect=200,
        )
        text = f"{draft['text']}\nWhy: the NCD ladder and the A-phase edits (WF-699 journey)."
        self.done("E1", "drafted from the structural and rate diffs, then edited")
        self.submit("E2", text, expect=422, code="EVIDENCE_INCOMPLETE")
        self.done("E3", "EVIDENCE_INCOMPLETE: no Dislocation Run for this version yet")
        self.dislocation()
        first = self.submit("E4", text, expect=200)
        self.done("E4", "dislocation run, resubmitted")
        self.decide("E5", "approver", first["approval_request_id"], "approve")
        self.skip("E5")
        changes = self.decide(
            "E6", "second_approver", first["approval_request_id"], "request_changes"
        )
        read = self.req("E6", "analyst", "GET", f"/rating-versions/{self.rv3['id']}", expect=200)
        if changes["status"] != "changes_requested" or read["status"] != "draft":
            raise JourneyStepFailed("E6", "VERSION_NOT_RETURNED_TO_DRAFT")
        self.done("E6", "changes requested; the version is back in draft (FR-355)")
        second = self.submit("E7", text, expect=200)
        self.skip("E7")
        request = second["approval_request_id"]
        self.req(
            "E8",
            "actuary",
            "POST",
            f"/approval-requests/{request}/decide",
            expect=403,
            code="SUBMITTER_CANNOT_APPROVE",
            json={"decision": "approve", "comment": "no"},
        )
        self.req(
            "E8",
            "analyst",
            "POST",
            f"/approval-requests/{request}/decide",
            expect=403,
            code="AUTHOR_CANNOT_APPROVE",
            json={"decision": "approve", "comment": "no"},
        )
        self.decide_until_approved("E8", request)
        self.done("E8", "the submitter and the author are refused; two approvers approve")
        final = self.req("E9", "analyst", "GET", f"/rating-versions/{self.rv3['id']}", expect=200)
        if final["status"] != "approved" or not final.get("evidence"):
            raise JourneyStepFailed("E9", "NOT_APPROVED")
        self.result.rating_version_id = UUID(final["id"])
        self.result.bundle_hash = final["bundle"]["content_hash"]
        self.done("E9", "approved, evidence pinned")

    def decide(self, step: str, who: str, request_id: str, decision: str) -> dict[str, Any]:
        decided: dict[str, Any] = self.req(
            step,
            who,
            "POST",
            f"/approval-requests/{request_id}/decide",
            expect=200,
            json={"decision": decision, "comment": f"{decision} in the WF-699 journey"},
        )
        return decided

    def dislocation(self) -> None:
        spec = {
            "baseline_ref": "rating_version:fremtpl2-demo@1",
            "candidate_ref": f"rating_version:{self.rv3['slug']}@{self.rv3['version']}",
            "portfolio_dataset_version_id": self.record["portfolio_dataset_version_id"],
            "purpose": "new_business",
            "as_at": "2026-10-01",
            "segments": ["area"],
            "band_edges_pct": ["-10", "-5", "0", "5", "10"],
            "mover_threshold_pct": "10",
        }
        accepted = self.req("D6", "analyst", "POST", "/dislocation-runs", expect=202, json=spec)
        self.done("D6", "a 20,000-policy sample of the freMTPL2 book (full-book cost: PL-1574)")
        job = self.job_ok("D6", "analyst", accepted)
        run_id = str(job["result"]["ref"]).split(":", 1)[1]
        run = self.req("D7", "analyst", "GET", f"/dislocation-runs/{run_id}", expect=200)
        if not run.get("attribution"):
            raise JourneyStepFailed("D7", "NO_ATTRIBUTION")
        self.req("D7", "analyst", "GET", f"/dislocation-runs/{run_id}/movers", expect=200)
        self.done(
            "D7",
            f"{run['policy_count']} policies in the sample; attribution persisted "
            "(full-book attribution cost: FD-1576)",
        )
        self.done("D8", f"dislocation run {run_id}")
        self.skip("D9")

    # -- Deploy and the served quote -------------------------------------------------------
    def deploy_and_score(self) -> None:
        ref = f"rating_version:{self.rv3['slug']}@{self.rv3['version']}"
        for env in ("dev", "uat"):
            self.req(
                "DEP",
                "deployer",
                "POST",
                f"/environments/{env}/deployments",
                expect=201,
                json={"rating_version_ref": ref, "reason": f"WF-699 journey: {env}"},
            )
        asked = self.req(
            "DEP",
            "deployer",
            "POST",
            "/environments/prod/deployment-requests",
            expect=201,
            json={"rating_version_ref": ref, "change_summary": "WF-699 journey: prod"},
        )
        self.decide("DEP", "prod_approver", str(asked["approval_request_id"]), "approve")
        self.req(
            "DEP",
            "deployer",
            "POST",
            "/environments/prod/deployments",
            expect=201,
            json={
                "rating_version_ref": ref,
                "reason": "WF-699 journey: prod",
                "deployment_request_ref": asked["ref"],
            },
        )
        for env in ("dev", "uat", "prod"):
            listed = self.req(
                "DEP", "deployer", "GET", f"/environments/{env}/deployments", expect=200
            )
            if not any(d["rating_version_ref"] == ref for d in listed["items"]):
                raise JourneyStepFailed("DEP", "NOT_LISTED")
        self.done("DEP", "dev, uat, then prod through a decided Deployment Request (FR-429)")

        account = self.req(
            "S1",
            "admin",
            "POST",
            "/service-accounts",
            expect=201,
            json={"slug": "wf699-prod", "environments": ["prod"], "permissions": ["score:execute"]},
        )
        context = {
            key: value
            for key, value in self.golden[0]["context"].items()
            if key in ("purpose", "quoted_at", "effective_date", "inputs")
        }
        scored = call(
            self.client,
            "S1",
            "POST",
            "/score",
            expect=200,
            headers={"X-API-Key": account["key"]},
            json=context,
        )
        if scored["bundle_hash"] != self.result.bundle_hash or scored["outcome"] != "quoted":
            raise JourneyStepFailed("S1", "SERVED_BUNDLE_DIFFERS")
        rung = next(r for r in scored["premium_ladder"] if r["rung"] == "payable_premium")
        self.result.prod_premium_minor = int(rung["value_minor"])
        if self.result.prod_premium_minor != self.golden[0]["expected"]["payable_premium_minor"]:
            raise JourneyStepFailed("S1", "PREMIUM_DIFFERS_FROM_THE_GOLDEN_QUOTE")
        # B3, the multiply made observable: the same region on a later date hits the 1.05 row, and
        # its premium is exactly the earlier premium x 1.05 in Decimal, half-even to whole minor
        # units (the declared rounding). A wiring that consulted the lookup and dropped the
        # multiply would pass the refusal below and fail here.
        if context["inputs"]["region"] != self.loading_region:
            raise JourneyStepFailed("B3", "GOLDEN_NOT_IN_THE_LOADED_REGION")
        later = call(
            self.client,
            "B3",
            "POST",
            "/score",
            expect=200,
            headers={"X-API-Key": account["key"]},
            json={**context, "effective_date": AFTER_LOADING_RISES},
        )
        later_rung = next(r for r in later["premium_ladder"] if r["rung"] == "payable_premium")
        expected = _minor(Decimal(self.result.prod_premium_minor) * Decimal(LOADING_AFTER))
        if int(later_rung["value_minor"]) != expected:
            raise JourneyStepFailed("B3", "LOADING_NOT_MULTIPLIED_INTO_THE_PREMIUM")
        # B3's other half: a quote dated before the reference row's `effective_from` does not use
        # it. The lookup has no row in force, so the quote is refused, not priced without it.
        call(
            self.client,
            "B3",
            "POST",
            "/score",
            expect=422,
            code="REFERENCE_LOOKUP_MISS",
            headers={"X-API-Key": account["key"]},
            json={**context, "effective_date": BEFORE_EFFECTIVE_FROM},
        )
        self.done(
            "S1", f"prod scored {self.result.prod_premium_minor} minor units from the live version"
        )


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
