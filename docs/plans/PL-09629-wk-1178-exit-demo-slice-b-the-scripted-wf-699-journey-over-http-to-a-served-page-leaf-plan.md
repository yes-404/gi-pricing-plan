---
id: PL-9629
family: plan
kind: leaf
title: WK-1178 — exit-demo slice (b), the scripted WF-699 journey over HTTP from one command to a served page (G2): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: 809a3794af6d3a6ba688663b0d9b59f951190680
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1371, FD-1209, FD-1244, FD-1245, FD-1356, FD-1411, FD-1416, RL-1263, SL-1256, SL-1387, SL-1388, SL-1389, SL-1390, SL-1391, SL-1409, PL-1408, PL-1237]
---

# PL-9629 (working id) — WK-1178: exit-demo slice (b), the scripted `WF-699` journey over HTTP, leaf plan

Filed under working id 9629 (this plan) and slice working id 9625 (its `SL-` row under WK-1178,
`draft`), both reserved by the lead. It is the second of the two leaf plans `PL-1371` Task 3
orders: *"Task 3 (the planner, on the lead's order): cut the exit-demo SL rows under DP-1's Work,
`draft`, in `docs/roadmap.md`, and write their leaf plans in §5's preparation order"*
(`PL-1371` §Tasks). The lead's order is dated 2026-10-05 15:06 BST.

**This PR depends on #1161** (PL 9624, working id, exit-demo slice (a)). That PR carries both
`SL-` rows (SL 9626 for (a), SL 9625 for this slice) in `docs/roadmap.md`, and this plan
consumes slice (a)'s algorithm builder. (b) comes second because Appendix A of `PL-1371` gives
DEMO-b the dependency list `["673-S6", "674-S2", "DEMO-a", "1178-FD1356", "1178-FD9752"]`
(the `"DEMO-b"` line).

**RL 9623 (working id, #1160) mints before this plan.** RL 9623 records the maintainer's ruling,
by delegation, on what G2's *"in Phase 1b's form"* means. This plan cites it by that id, never by
the local channel entry the ruling came from, because a repository reader cannot resolve a local
entry (RFC-777). The plan's text quotes the ruling as RL 9623 quotes it (§"The decisions this
plan rests on").

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `fastapi-service` (the RFC 9457 problem shape every call can
> return), `dev-commands` (the two-half gate, the alembic DSN, `uv sync --all-packages`, the
> demo command) and `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions
> before the first step. The executor is spawned from `.claude/roles/executor.md`, model
> sonnet.

## Goal

**ONE command** (`uv run python scripts/demo.py --journey wf-699`, DP-b1) seeds the freMTPL2
demo, starts the API, and walks `WF-699` Phases A to E and its deploy step **over HTTP**: seed
the rate tables from the approved 7-factor GLM (A1–A2), edit and uplift them, build and save
the algorithm, compile with every pin, run the regression suite and the dislocation run with
attribution, submit, and get approval from principals who are neither submitter nor author. It
then deploys `dev → uat → prod` (FR-429) and scores one quote against `prod`'s live
deployment. **It ends with the frontend serving a 200 page**, with routes registered and the UI
available for hands-on driving but not driven. A journey test cites `WF-699` by id and runs
the same journey in the test suite.

This is the Exit demo row's journey. Its Scope cell reads: *"`WF-699` Phases A to E and its
deploy step as one scripted journey, and the journey test that cites `WF-699` by id; **the
script walks `WF-699` A1–A2 (seed-from-model) on the 7-factor freMTPL2 GLM**"*
(`docs/roadmap.md`, the `| **Exit demo** |` row, `:603`). It discharges `FD-1209`'s `WF-699`
half. Its register event reads *"the real freMTPL2 algorithm exists in the seed and `WF-699`
runs end to end on it"*; slice (a) discharges the algorithm half.

**Architecture:** one journey module, `examples/fremtpl2/journey.py`, is an `httpx` client of
`/api/v1` that walks the steps in `WF-699` §2's order. Each step is one function that returns
the ids the next step needs and raises a named error carrying the step id (`"C1"`, `"D6"`, …)
and the RFC 9457 problem when a call fails. `scripts/demo.py --journey wf-699` runs it against
the live API after `_verify_journey_postconditions` (`scripts/demo.py:274` at `cdaaa573`; `:266` at `809a3794`), then starts Vite
and checks the served page for a 200. The journey test runs the same module against the app in
process (`httpx.ASGITransport`) on a small seed. The algorithm is slice (a)'s
`build_fremtpl2_algorithm`, so the demo has one freMTPL2 algorithm.

**Tech Stack:** Python 3.12, `httpx` (already used by `scripts/demo.py`'s `wait_for`), FastAPI
(the API under test), pytest; Vite (the served page only).

**Spec, ruling and map plan:**
- [`../workflows/WF-00699-approved-models-to-approved-rating-version.md`](../workflows/WF-00699-approved-models-to-approved-rating-version.md)
  §2 (`:35-106`): the journey, step by step;
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md): FR-212, FR-221, FR-226,
  FR-229, FR-230, FR-231, FR-233, FR-234, FR-237, FR-239, FR-240, FR-242, FR-257, FR-260,
  FR-261, FR-263, FR-266, FR-267;
- [`../specs/06-governance.md`](../specs/06-governance.md): FR-353, FR-355, FR-356;
- [`../specs/07-platform.md`](../specs/07-platform.md): FR-399, FR-428, FR-429;
- `docs/roadmap.md` G2 (`:566`), the Exit demo row (`:603`), and the §10 gate row "Before the
  P2 exit demo" (`:1926`);
- RL 9623 (working id, #1160): the form of G2;
- `docs/plans/PL-01371-p2-scope-freeze-lane-loading-plan-every-remaining-slice-against-the-code-freeze-map-plan.md`,
  §3.8 row 7, §7 ("Exit demo (b)"), §9 DP-6.

## The decisions this plan rests on, quoted

**G2's form, RL 9623 (working id, #1160 @`295a483a`), §"Ruled"**, which quotes the maintainer's
entry verbatim, by delegation, headed *"2026-10-05 13:05:42 BST — RULING (the maintainer, by
delegation): G2's "in Phase 1b's form" = a scripted HTTP journey plus a served page; WK-675 is
OFF G2's critical path"*:

> Ruling: G2 is met by `scripts/demo.py`-style ONE command that runs WF-699 A–E and its deploy
> step over HTTP on the freMTPL2 seed and ends with the frontend SERVING (a 200 page, routes
> registered), the UI available for hands-on driving but not driven. No WK-675 view is a G2
> prerequisite. The Exit demo row's "where no view is needed" (:603) is read accordingly: no
> view is needed for G2.
> Consequences: WK-675 stays on its PL-1371 schedule, not the critical path; G1 still requires
> every P2 Work, WK-675 included, to be resolved, so its slices still need doing or a dated
> move. The exit-demo plan records this ruling by this entry's header when it is filed.

**The dependencies `PL-1371` §7 derived** (accepted 2026-10-03, `PL-1371` §9):

> "**Exit demo (b): the scripted `WF-699` journey**, A to E plus deploy, with A1–A2 on the
> 7-factor GLM, and the journey test citing `WF-699` by id. **Its real dependencies, re-derived
> as `RL-1263` item 5 requires:** WK-673 S6 (the run with attribution, and FR-364's floor at
> approval); WK-674 S2 only, because "deployment to `uat` and then `prod` (FR-429)" is FR-267,
> FR-428 and FR-429, all in `SL-1256` (`03:195`, `07:139-140`); WK-674 S3–S6 (isolation,
> deployment path, switchover, routing) are **bare sequencing**, and this plan lifts them. Also:
> the FD-1356 fix (the demo DB's end state, the maintainer's entry "2026-10-01 11:13:17 BST"),
> FD 9752 (the script reads approval responses), and the FD-1244 and FD-1245 rulings (the §10
> gate "Before the P2 exit demo"). FD-1356's Task 0 query is re-run before the demo. If (b)'s
> leaf plan finds a call to an S4–S6 route, it adds that slice as a dependency (DP-6)."

(`03:195` is a stale anchor: FR-267 is at `03-rating-engine.md:198` at `809a3794`.)

**The `/score` step's routing** (the maintainer, by delegation, entry "2026-10-05 09:59:49 BST
— A10 early ACCEPTED …; PL 9728 DP-6 RULED (b) with a binding condition"):

> "**PL 9728 DP-6 (#1113), RULED (b):** the remedy slice measures and fixes the default-live
> /score arm (Acceptance 2). The WF-699 scripted /score-on-G2 journey step goes to PL-1371
> §3.8 item 7 (the exit-demo leaf (b)), which already depends on WK-673 S6 and WK-674 S2/3/5/6.
> Pulling it in would stall the remedy behind four slices."

The earlier entry "2026-10-04 19:58:33 BST — PL 9728 (#1113 @7be9a887) filed, not merged
tonight; noted: no demo code calls /score today" adds: *"its script must call /score on the G2
path, and PL 9728's acceptance covers that path."* So this slice calls `/score` on the G2 path
(step S1 below). NFR-489 is measured by PL 9728 and `SL-1259`, not here. The "S2/3/5/6" in the
09:59:49 entry is DP-6's subject, below.

**DP-6, the dependencies, the two missing G2 needs and the Peril Structure question**, ruled by
the maintainer (by delegation), entry headed *"2026-10-05 15:28:26 BST — Wave results: D1 =
(c); D2 PL 9624 DPs; D3 PL 9629 DP-6 + plan the 2 missing G2 items; C1′ is FD 9995 (no new
finding); FD 9619 noted"*, item D3 and the entry's closing line, verbatim:

> D3 (leaf (b) PL 9629):
>  - DP-6: WK-674 S2 only, as the evidence supports. AGREED.
>  - The dependencies PL-1371 §7 omits (S7, WK-1250 S2/S3, the FD 9707 and FR-240 fixes) are named in PL 9629: right.
>  - YES, plan the two G2 needs with NO plan as the NEXT prep items: the FD-1416 fix (ApprovalRequest defined three ways; HOLD on reading its responses) and the FD-1244 and FD-1245 rulings (WF-699 D4 vs FR-261; E2 vs FR-257). One planner, one DM; docs only.
>  - C1′ (a Peril Structure cannot be pinned) is NOT new: it is FD 9995 (#980, "a peril structure has no approval path and the compile resolver has no peril branch", LOW, fail-closed). If PL 9629 confirms that G2's journey must pin a peril structure, FD 9995 is a G2 blocker: at its ACK it gets "deadline before the P2 exit demo" and MEDIUM (fail-closed, but it blocks an exit criterion). If the journey needs no peril pin, it stays LOW. PL 9629 states which.
>
> Also noted: PL-1371 §7's "FR-267 at 03:195" is :198 (frozen; the leaf is right); the §12 exit row's WF-701 A–D needs WK-674 S5/S6, put to the pre-exit-demo plan review (CLAUDE.md §14).

The entry is a local channel entry (RFC-777); it is quoted so the plan carries it. FR-267 at
`03-rating-engine.md:198` is the correction this plan already made (§"The dependencies
`PL-1371` §7 derived"). The `WF-701` A–D point is in Hand-off 3. **D3's C1′ line is now
decided.** The maintainer's Option A entry of 2026-10-05 16:43:31 BST makes FD 9995 HIGH and
puts the peril pin on G2's journey. It is quoted, with what it means for this slice, in §"Does
G2 pin a Peril Structure?".

## Status

`draft`. **DP-6 is ruled (a), WK-674 S2 only** (D3, above). **Four decision points are open**
(DP-b1 to DP-b4), and every activation need
except needs 8 (WK-674 S2) and 9 (`SL-1409`), both met, is unmet, most of them other slices. The plan moves to `active` only through a
separate activation PR, after every need below holds. That PR carries the `SL-` row's status
flip and this plan's.

### Activation needs, in order, each with its state at `cdaaa573` (2026-10-05 15:38 BST)

| # | Need | Why (the step it serves) | State now |
|---|---|---|---|
| 1 | RL 9623 minted | the form of G2 this plan builds | draft #1160 @`295a483a`, unminted |
| 2 | Exit-demo slice (a) merged (SL 9626, PL 9624, working ids) | A1–A2's tables, B's algorithm | draft #1161, plan `draft` (DP-a0 to DP-a3 ruled 2026-10-05 15:28:26 BST, item D2; its activation need 3 ruled at its ACK) |
| 3 | WK-673 S3 `SL-1387` merged (attribution) | D7, D8 | `draft`; leaf PL 9689 (working id), draft #1138 |
| 4 | WK-673 S4 `SL-1388` merged (`POST /dislocation-runs` and its Job) | D6, E4 | `draft`; no route and no `DISLOCATION_RUN` worker on `main` |
| 5 | WK-673 S5 `SL-1389` merged (change summary from diffs; the evidence gate) | E1, E3 | `draft` |
| 6 | WK-673 S6 `SL-1390` merged (the floor wiring at approval) | E3, E9 | `draft` |
| 7 | WK-673 S7 `SL-1391` merged (exposure weight per cell) | A3 | `draft`; leaf PL 9716 (working id), draft #1127 |
| 8 | WK-674 S2 `SL-1256` closed | deploy `dev → uat → prod` (FR-429) | **met**: `closed` |
| 9 | The FD-1356 fix `SL-1409` merged; its Task 0 query prints 0 | the demo DB's end state | merged: `closed`, `cdaaa573` (#1157); the Task 0 query is re-run at dispatch (Task 0 Step 3) |
| 10 | The FD 9708 fix (PL 9683, working id, #1140) merged | C1: `POST /rating-versions` with the algorithm and pins | plan draft; `RatingVersionCreate` is `slug`, `dataset_version_id`, `model_ref`, `extra="forbid"` (`backend/src/app/api/models.py:271-276`) |
| 11 | The FD 9707 fix (PL 9688, working id, #1145) merged | B3: `lookup` as at the effective date | plan draft; `runtime.py:27-33`: *"exact key match only"* |
| 12 | The FR-240 family fix (PL 9649, working id, #1152) merged | C3: compile validates everything at once | plan draft |
| 13 | `FD-1416` fixed (FD 9752; one ApprovalRequest shape; WK-1178, deadline before the P2 exit demo) | E5, E6, E8: the script reads approval responses | planned as **PL 9616** (working id, the leaf plan) and **SL 9615** (working id, its row), reserved 2026-10-05 15:29:48 BST for planner-1416 on D3's order; no PR at 15:35 BST |
| 14 | `FD-1244` and `FD-1245` ruled (§10 gate "Before the P2 exit demo", `docs/roadmap.md:1927` at `cdaaa573`, "2 (2 open)") | D4; E2 | both `active`; their ruling is **RL 9614** (working id), reserved 2026-10-05 15:29:48 BST for dm-1244 on D3's order; no PR at 15:35 BST |
| 15 | FD 9717 (working id, #1125) minted, and DP-b4 ruled | the seed record's pre-flight | draft #1125 @`51335e75` |
| 16 | DP-6 and DP-b1 to DP-b4 ruled | — | DP-6 **met** (D3); DP-b1 to DP-b4 open |
| 17 | The lead's go | — | — |

PL 9728 (working id, #1113, NFR-489's remedy) is **not** an activation need: the 09:59:49
ruling routes the `/score` journey step here and keeps NFR-489's measurement with PL 9728 and
`SL-1259`. The `/score` step needs only what is on `main`.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means the named test was run and failed **for the stated cause** before the code that turns it
green ([`README.md`](README.md) rule 2). Each red is recorded in the slice's ledger, with the
failure line as printed.

1. **The journey test cites `WF-699` by id and passes.** `backend/tests/test_wf699_journey.py`
   carries `pytestmark = pytest.mark.req("WF-699")` (or the house marker for a workflow id, as
   `python-test` defines it; Task 0 Step 5 records which) and a module docstring naming
   `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`. `uv run pytest -q
   backend/tests/test_wf699_journey.py` passes. Red first: on the base tree the module
   `examples.fremtpl2.journey` does not exist. `git grep -n -E 'WF-(00)?699' -- backend
   packages frontend/src tests examples scripts` then prints at least this file (it prints
   nothing at `809a3794`).
2. **Every in-scope step is walked over HTTP, in order** (§"The steps"). The test asserts each
   step's status code and its one named post-condition (the "Check" column). A step that is
   skipped under DP-b2 is asserted as skipped, with its reason string. It is never absent.
3. **The deliberate failures are shown, by their codes:** B6 `RATING_GRAPH_UNRESOLVED_REF`; C4
   `PIN_NOT_APPROVED`; D4's property failure, then a pass (as FD-1244's ruling shapes it); E3
   `EVIDENCE_INCOMPLETE`; E6's `changes_requested` returning the version to `draft` (FR-355);
   E8 `SUBMITTER_CANNOT_APPROVE` and `AUTHOR_CANNOT_APPROVE` before the valid approvals. Each
   assertion matches the problem's `code`, not only the status.
4. **Deploy and serve** (G2; FR-429). The approved version deploys to `dev`, then `uat`. A
   `prod` Deployment Request is approved, then the version deploys to `prod`. `POST /api/v1/score`
   with a `prod`-bound service-account key and no `rating_version_ref` returns 200, priced by
   the approved version (its bundle hash equals the compiled bundle's).
   `GET /environments/{env}/deployments` lists the version in each environment.
5. **One command to a served page** (RL 9623). `uv run python scripts/demo.py --journey wf-699
   --rows 20000` exits 0 on the slice head. Its output prints one line per journey step, then
   the `/demo` URL. The script itself fetches `http://localhost:5173/` and gets 200, and
   prints that. Run once by the executor, alone on the box with no gate slot held, with the
   elapsed time recorded. A test in `backend/tests/test_demo_command.py` asserts the
   `--journey` flag's wiring: after `_verify_journey_postconditions`, before the frontend
   starts, and the served-page check after it.
6. **Each journey failure names its step.** `test_a_journey_failure_names_its_step`: with the
   C1 call pointed at a body the API refuses, the journey raises `JourneyStepFailed` whose
   message starts `C1:` and carries the problem's `code`, and `scripts/demo.py` exits non-zero
   with that line. Proven on deliberately broken input (`CLAUDE.md` §13).
7. **The seed record's pre-flight** (FD 9717, under DP-b4 (a)). `scripts/demo.py`, on every
   path including `--skip-seed`, refuses to start the journey when `last-seed.json`'s workspace
   or analyst is absent from the database. It exits 1 with a message naming the workspace id
   and "re-run the seed without --skip-seed". Red first on a database whose workspace row was
   deleted (Task 5 Step 1).
8. **The rehearsal record.** The §"Rehearsal checklist" is run once in full on the slice head,
   and each line's command and output (or its tree and time) is recorded in the ledger.
9. **The gate.** Both halves green on the slice head, through the gate-runner holding a slot
   (`RL-1263`). `generate-contracts.py --check` rc 0. `audit-docs.py` red only on check 31
   before the mint and clean after. `req-coverage.py` lists the `WF-699` test.
10. **Scope held.** `git diff --stat origin/main...HEAD` touches only §"Write set"'s paths.

## Global Constraints

- **Over HTTP only** (RL 9623). The journey calls `/api/v1` routes and nothing else: no
  service import, no row write, no SQL. The seed before it is unchanged except for slice (a)'s
  work and DP-b4.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2). Request
  bodies are built from `model_schema` types and `.model_dump(mode="json")`. Responses are read
  through the `model_schema` types the routes declare. Until `FD-1416` is fixed, the approval
  routes' responses are untyped dicts, and `FD-1416`'s HOLD forbids a client that reads them
  (activation need 13).
- **Money is integer minor units, or Decimal in the rating path, never float** (`CLAUDE.md` §7).
  The script compares premiums as integers.
- **No pandas** (`CLAUDE.md` §3).
- **No view is built** (RL 9623: "No WK-675 view is a G2 prerequisite"). The served page is
  the existing frontend.
- **Run nothing heavy beside a held gate slot.** Check `pgrep -af 'pytest|vitest|flock'` and both
  slots (`flock -n /tmp/slots/gate-1 true`, the same for `gate-2`) before the demo run and the
  gate. `alembic current` equals `alembic heads` before any pytest.
- **Shared files** (`RL-1263` option (c)): two concurrent build slices may not both change the
  same existing function, class, spec section or policy table. `docs/INDEX.md` is a registry:
  regenerate, never hand-merge.
- **No spec text is written by this slice** unless a ruling carries it verbatim.

## Scope

### The steps, against `main` at `809a3794`

Routes are under `/api/v1`. "Needs" is the activation need (by number) that makes the step
work over HTTP. A blank Needs cell means the step works on `main` today. The evidence for each
`main` verdict is the draft exit-demo script's table (local, 2026-10-05), whose cites were
re-checked at `809a3794` by a read-only sweep. Every cite held, except `model_schema/approvals.py:282`,
which opens `DEFAULT_POLICY`; the Rating Version entry is at `:335-338` (`:292` and `:345-348`
at `cdaaa573`).

| Step | Route (and what the journey does) | Check | Needs |
|---|---|---|---|
| A1–A2 | `POST /rate-tables/{slug}/seed-from-model`, one per rateable Factor of the approved GLM (7 under DP-a1 (a); 4 otherwise) | 201 each; `seeded_from` set; one key with `factor_ref` | 2 |
| A3 | export, edit one cell, `POST /rate-tables/{slug}/import`; `GET /rate-tables/{slug}@{v}/diff?against=previous` and `?against=seed` with the portfolio's exposure weights | both diffs non-empty; a weight per changed cell | 7 |
| A4 | `POST /rate-tables/{slug}@{v}/bulk-operation` (+2 %) | 201; the version records the operation | |
| A5 | an import with a duplicate key | 422 `RATE_TABLE_KEY_DUPLICATE` | |
| A6 | every save is a new version with a change note | seed and import notes present; bulk has none (unowned gap U1, DP-b2) | DP-b2 |
| B1–B2 | `POST /rating-algorithms` with slice (a)'s algorithm built over the A-phase table versions | 201 | 2 |
| B3 | the algorithm's `lookup` on a reference table (`/reference-tables`, `api/reference_tables.py:48`) as at `effective_date` | the row in force on the quote's date is used | 11 |
| B4–B5 | the algorithm's `table`, `expression` and `output` steps (slice (a)) | saved | 2 |
| B6 | one save with a dangling input | 422 `RATING_GRAPH_UNRESOLVED_REF` | |
| B7 | mount `sub_graph:ncd-ladder@4` | inlined at compile | DP-b3 |
| B8 | `output` rounding `half_even`, 0 dp | (in the saved algorithm) | |
| B9 | money × float refused | `MONETARY_FLOAT_REFUSED` is registered (`errors.py:314` at `cdaaa573`) and raised nowhere (unowned gap U2, DP-b2) | DP-b2 |
| C1 | `POST /rating-versions` declaring the algorithm and every pin | 201; `pins` echo the request | 10 |
| C1′ | a Peril Structure pin | **on G2's journey under Option A, built by SL 9594 (A-4), not this slice** (§"Does G2 pin a Peril Structure?"). This slice's algorithm has no `model_call`. The gap is FD 9995 (working id, #980; HIGH, a G2 blocker; U3, DP-b2). The script prints `SKIPPED C1′` naming FD 9995 and SL 9594, and SL 9594 removes that line | DP-b2 |
| C2 | `POST /rating-versions/{id}/compile` → 202 + `rating.compile` Job | Job `succeeded` | |
| C3 | compile validates the whole structure | — | 12 |
| C4 | the version also pins the seed's GBM, which the journey submits but has not approved | Job `failed`, `PIN_NOT_APPROVED` | |
| C5 | approve the GBM (`WF-698` E, two approvers via `/approval-requests/{id}/decide`), recompile | Job `succeeded` | 13 |
| C6 | the bundle is content-hashed | bundle hash recorded | |
| D1–D2 | `POST /rating-versions/{id}/regression-runs` | 202; run passes on slice (a)'s golden quotes | |
| D3 | a new suite version updating one expected value, its reason in the change note | 201 | |
| D4 | a `monotone_in_*` property that fails, shrunk; then the banding fixed (A-phase) and passing | as FD-1244's ruling words it | 14 |
| D5 | the fix | (A-phase routes) | |
| D6 | `POST /dislocation-runs` | 202; run persisted | 4 |
| D7–D8 | the run's segments, movers and attribution | attribution persisted and cited by id | 3, 4 |
| D9 | the GIPP check "where enabled" | **skipped**: `04` FR-294 is WK-685, Phase 4; the demo runs with GIPP not enabled and says so | DP-b2 |
| E1 | change summary drafted from the structural and rate diffs | non-blank; drafted | 5 |
| E2 | submit | as FD-1245's ruling names the route (`POST /rating-versions/{id}/submit` works on `main`; `POST /approval-requests` does not for a Rating Version) | 14 |
| E3 | the first submission is refused: the dislocation run is stale | 422 `EVIDENCE_INCOMPLETE` | 5, 6 |
| E4 | re-run dislocation, resubmit | 202, then accepted | 4 |
| E5 | Approver #1 approves | decision recorded; inline review **skipped** (WK-678, Phase 3) | 13, DP-b2 |
| E6 | Approver #2 requests changes | the version returns to `draft` (FR-355) | 13 |
| E7 | resubmit (a new request, a fresh quorum of 2) | Commentary Block **skipped** (WK-680, Phase 3) | DP-b2 |
| E8 | the submitter, then the author, try to approve; then two valid approvals | 403 `SUBMITTER_CANNOT_APPROVE`, 403 `AUTHOR_CANNOT_APPROVE`; then `approved` | 13 |
| E9 | `approved`, evidence pinned, audit events | status `approved`; the evidence ids on the decision | 6 |
| Deploy | `POST /environments/{env}/deployments` for `dev`, then `uat`; `POST /environments/prod/deployment-requests`, decided; then `prod` | 201s; `GET …/deployments` lists the version in each | 8 (met), 13 |
| S1 | `POST /service-accounts` bound to `prod`; `POST /score` with its key and no ref | 200; bundle hash = C6's | |
| Serve | Vite starts; `GET http://localhost:5173/` | 200 | |

**Count:** 38 rows (counted from the table's Needs column). **12** need nothing beyond
`main` (A4, A5, B6, B8, C2, C4, C6, D1–D2, D3, D5, S1, Serve). **21** need another slice, fix
or ruling (activation needs 2–7 and 10–14; the Deploy row needs only `FD-1416`'s response
shape). **5** wait on a DP alone: D9 (skipped, Phase 4), A6, B9 and C1′ (the unowned gaps
U1–U3, DP-b2) and B7 (DP-b3). E5 and E7 also have Phase 3 halves, skipped under DP-b2.

### Does G2 pin a Peril Structure? **Yes, under Option A**, built by a follow-on slice, not this one

The maintainer has decided this question. Entry headed *"2026-10-05 16:43:31 BST — THE MAINTAINER'S DECISION (asked live): G2 takes OPTION A, WF-699's literal Peril Structure path is BUILT IN P2; and the FD 9605 approval, now on the record"* (`channel/to-lead.md`),
quoted verbatim from its opening paragraph to its item 6. The FD 9605 approval paragraph
after item 6 is left out because it is not this plan's subject:

> THE MAINTAINER, asked live with the sizing memo's two options (handover/sizing-g2-peril-path-2026-10-05.md, read at cdaaa573): "A: build it in P2". So G2 (CR-1212 :62-69, "WF-699 end to end") stands as written, no amendment, and the exit demo walks WF-699's trigger (:19), precondition (:28), B4 (:59, a model_call referencing the Peril Structure) and C1 (:70, pinning it).
> CONSEQUENCES, binding:
> 1. Four serial build slices under WK-1178, as sized: A-1 FD 9995 in full (the peril approval carry plus the _Resolver peril branch; it flips PL 9683's Acceptance 7); A-2 GLM via model_call (FD 9605); A-3 Peril Structure scoring (compile resolves and maturity-checks the component models; the runtime calls assemble_risk_premium, fixing the bare KeyError on payload["fit_result"] at runtime.py:540); A-4 the demo scope on PL 9624/PL 9629 (a severity GLM, the peril structure, reconcile, approve, the B4 model_call, the C1 pin). About 5 executor-days likely (3.5–8), a chain after PL 9683 and PL 9649.
> 2. SEVERITY: FD 9995 → HIGH, deadline before the P2 exit demo (now a G2 blocker). FD 9605 (#1172, the GLM model_call refusal) → HIGH, the same. Both take lanes under my 13:12:56 priority rule.
> 3. Planning starts now: leaf plans for A-1..A-4, red first, with contention against the in-flight plans.
> 4. The DOUBLE-COUNT design point (A1 seeds tables from the AD frequency model while B4's model_call scores a Peril Structure containing it, so the factor effects may count twice; WF-699 does not say how they combine) needs a DM's options and a recommendation, ruled BEFORE A-4's plan activates.
> 5. RISK, recorded: the sizing fits before the 4 Nov code freeze only on "3 lanes every day" (about 2 days spare at best). The maintainer has said the VM may be shut down from when the weekly allowance runs out until the reset (10 Oct 01:59 UTC); lost days come out of that slack. The Friday 9 Oct checkpoint re-checks the fit with measured progress.
> 6. G2 needs no governed amendment (Option B was not taken); RL 9623's G2-form ruling is unaffected.

The entry is a local channel entry (RFC-777). It is quoted here so the plan carries it. It
**supersedes** this section's earlier statement (*"the journey needs no Peril Structure pin,
so FD 9995 stays LOW"*) and that statement's FR-237 reasoning. What it means for this slice:

1. **FD 9995 (working id, #980) is HIGH, a G2 blocker, deadline before the P2 exit demo**
   (item 2). Its fix is A-1 (SL 9600 / PL 9599, working ids, reserved).
2. **G2 now walks `WF-699`'s literal path**: the trigger (`:19`), the precondition (`:28`),
   B4's `model_call` *"referencing the Peril Structure"* (`:59`) and C1's peril-structure pin
   (`:70`), all in `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md` at
   `137bc817`.
3. **This slice's scope does not change.** A-4, the demo scope that walks B4 and C1′ (a
   severity GLM, the Peril Structure, its reconciliation and approval, B4's `model_call`, the
   C1 pin, the golden quotes and dislocation baseline regenerated, and the `SKIPPED` lines for
   B4 and C1′ removed), is **its own slice**: SL 9594 / PL 9593 (working ids, reserved
   conditionally for this choice). It is not an edit to this plan. A-4 needs A-1, A-2 and A-3
   merged and the double-count ruling (item 4). Folded in here, those needs would block this
   slice behind the whole chain. As a separate slice, this plan keeps no plan dependency on
   the A chain, so it can run beside it, and the 3-lane fit (item 5) needs that.
4. **So this slice still prints C1′ and B4's `model_call` clause as `SKIPPED`**, under DP-b2.
   The reason string now names SL 9594 and FD 9995. **G2 is met only when SL 9594 merges**
   (Hand-off 6). This slice alone is not G2.
5. **A-4 waits on the double-count ruling.** Item 4: A1 seeds tables from the AD frequency
   model, while B4's `model_call` scores a Peril Structure that contains that same model.
   This needs a decision-maker's options and the maintainer's (by delegation) ruling *"BEFORE
   A-4's plan activates"*. That ruling does not touch this slice: A1–A2 seeds the tables as
   slice (a) builds them.

### Requirement coverage, each id individually

The journey test exercises these requirements end to end. Each already has its own unit or API
tests in the slice that built it. The journey test carries the `WF-699` marker, not a marker per
FR, because it proves the journey and not each requirement (`python-test`).

| Spec | Ids walked |
|---|---|
| `03` | FR-212, FR-221 (need 11), FR-226, FR-229, FR-230, FR-231 (need 7), FR-233, FR-234, FR-237 (need 10), FR-239, FR-240 (need 12), FR-242 (need 5), FR-257, FR-260, FR-261, FR-263 (need 4), FR-266 (need 3), FR-267 |
| `06` | FR-353, FR-355, FR-356 |
| `07` | FR-399, FR-428, FR-429 |

### Write set, and its contention (`RL-1263`)

| Path | Change | Other slices touching it | Consequence |
|---|---|---|---|
| `examples/fremtpl2/journey.py` | added (new module): `run_wf699_journey(client: httpx.Client, record: Mapping[str, str], *, log: Callable[[str], None]) -> JourneyResult`, one function per phase, `JourneyStepFailed` | none | none |
| `backend/tests/test_wf699_journey.py` | added | none | none |
| `scripts/demo.py` | edited: `main` (`:346-355` at `cdaaa573`, the `--journey` flag), `demo` (`:203-`, the journey call after `_verify_journey_postconditions` at `:274`, and the served-page check after the frontend starts); added: the seed-record pre-flight *(DP-b4 a)* | **SL-1409** added a checked step after `read_seed_record()` (`PL-1408` Acceptance, condition 2), merged as `cdaaa573` (#1157); **PL 9728** (working id, #1113) edits it | **serial**: SL-1409 first (activation need 9, merged); with PL 9728, whichever merges second re-reads `demo` |
| `backend/tests/test_demo_command.py` | edited: the `--journey` wiring assertion, and the pre-flight test *(DP-b4 a)* | **SL-1409** and **PL 9728** edit it | serial, as above |
| `examples/fremtpl2/README.md` | edited: the one command and what it shows | slice (a) edits another paragraph | different paragraphs |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | registry |

**Not written:** `backend/src/` (any route the journey needs is another slice's), `packages/`,
`frontend/`, `docs/specs/`, `examples/fremtpl2/model.py`, `seed.py` and `algorithm.py` (slice
(a)'s).

**Open PRs read at `809a3794`** (`gh pr list --state open`, 2026-10-05 15:2x BST). These rule
on, or touch, this slice's subject: #1160 (RL 9623), #1161 (slice (a)), #1140 (PL 9683), #1145
(PL 9688), #1152 (PL 9649), #1155 (RL 9633), #1133 (RL 9695), #1148 (RL 9642), #1138 (PL 9689),
#1127 (PL 9716), #1113 (PL 9728), #1125 (FD 9717), #1130 (FD 9708), #1132 (FD 9707), #980
(FD 9995). None is merged.

### Size

Medium: about one and a half executor days, once every activation need holds. Six tasks
after the preconditions. The journey test runs a small seed in process. The one-command run is
the full seed (`--rows 20000` in rehearsal; the full 678,013 rows on demo day). One full
two-half gate (a gate slot under `RL-1263`). No NFR is measured here; NFR-489 is PL 9728's and
`SL-1259`'s.

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-6** (`PL-1371` §9) | Does the journey call any WK-674 S3–S6 route? | (a) **no: S2 only.** Every deploy-step route is on `main` (`environments.py:list_environments` :45, `create_environment` :62; `deployments.py:submit_deployment_request` :49, `create_deployment` :74, `list_deployments` :96; `service_accounts.py:create_service_account` :159; `score.py:score` :351, live by `_serving_ref` :169). S3, S4 and S5 add no route (`PL-1237` Tasks 3–5), and S6 adds only the shadow PUT and a routing route (`PL-1237` Task 6, `:977-979`), which the journey does not call. FR-429 (`07:140`) requires order and evidence, not switchover. (b) **S2 + S5**: the demo also shows the atomic switchover and rollback (FR-268, FR-269), which `WF-701` A2 and C4 describe. (c) **S2, S3, S5, S6**, as `PL-1371` §3.8 row 7 lists ("WK-674 S2, 3, 5, 6") and the 09:59:49 entry repeats ("WK-674 S2/3/5/6") | **(a)** for G2. §3.8 row 7 and §7 disagree inside `PL-1371`; §7 is the later derivation and lifts S3–S6 as bare sequencing, and the route evidence agrees. **Separately, for the lead:** the §12 Phase 2 exit row (`docs/roadmap.md:2209` at `cdaaa573`) binds "`WF-699` end to end, plus `WF-701` phases A–D, meeting NFR-489". `WF-701` A2 and C4 need S5's switchover, and B1 needs S6's shadow PUT (Phase B is optional: `WF-701`'s Phase B heading, line 48 of its file). That is an exit obligation beside G2, not this slice's: a proposal for the pre-exit-demo plan review | planner (`PL-1371` DP-6: "planner, at (b)'s leaf"); confirmed by the lead | activation need 16 |
| **DP-b1** | Where does the ONE command live? | (a) `scripts/demo.py --journey wf-699`, which adds the journey to the existing demo path between the API start and the frontend. (b) a new `scripts/exit-demo.py` that calls `demo.py`'s pieces. (c) `--journey` on by default | **(a).** RL 9623 says "`scripts/demo.py`-style ONE command". One entry point keeps the Phase 1a/1b demo and G2 on one path, and `demo.py` already owns the environment check, compose, migrations, seed, API and Vite. (c) would slow every Phase 1 demo by the whole journey | the lead | Task 5 |
| **DP-b2** | How does the script treat a step that `main` cannot do and no P2 slice owns: the later-phase halves (D9 → P4; E5's inline review → WK-678, P3; E7's Commentary Block → WK-680, P3) and the **unowned gaps** U1 (A6: bulk takes no change note; FR-229 says mandatory), U2 (B9: `MONETARY_FLOAT_REFUSED` raised nowhere), U3 (C1′: no Peril Structure pin; FD 9995, working id, #980)? | (a) the script runs the step's P2 half and prints `SKIPPED <step>: <reason>` for the rest; the journey test asserts the skip; the `CR- kind: phase` lists each skip. (b) G2 is not met until each is built. (c) as (a) for the later-phase halves; U1–U3 each go to the auditor for a finding with an owner before the demo | **(c).** G2 says "end to end" with no exception list. A later phase's capability is a spec matter, not P2 code (`CLAUDE.md` §0), so the skips are honest. U1–U3 are P2 behaviour the spec states and the code lacks, so they need an owner, not a skip. That is the auditor's to file and the lead's to route; this plan does not file them | the maintainer (by delegation): what "end to end" admits is G2's reading | Tasks 2–4, activation need 16 |
| **DP-b3** | B7, the sub-graph mount, needs `compile_bundle` to read `sub_graphs` (`pricing_core/rating/score.py:401-403`), which WK-1250 S2/S3 (`SL-1340`, `SL-1341`, `draft`) build. `PL-1371` §7's dependency list does not name WK-1250 | (a) **add WK-1250 S2/S3 as activation needs**, so the journey mounts `ncd-ladder`. (b) skip B7 with its reason, as DP-b2 (a). (c) mount without inlining (the sub-graph is stored but not compiled) | **(a).** B7 is a `WF-699` step and FR-217 is P2 scope. `PL-1371` §5 places WK-1250 S2/S3 in the week of 24 Oct, before the code freeze, so it lengthens (b)'s chain without breaking it. **This is a dependency `PL-1371` §7 did not derive.** If the lead takes (a), `PL-1371`'s G2 list needs it at the next re-baseline (§8.1) | the lead (sequencing), with the maintainer (by delegation) if it moves the exit date | activation need 16 |
| **DP-b4** | FD 9717's gap (the seed record is trusted without checking the database) sits on this slice's path. Who fixes it? | (a) **this slice**: `scripts/demo.py` checks the record's workspace and analyst exist before the journey (Acceptance 7). (b) a separate WK-1178 fix slice. (c) the rehearsal checklist's manual check only | **(a).** It is a few lines on the one command this slice owns, and FD 9717 is already WK-1178's. (c) is the check-by-hand the finding says is missing. The owner and slice are settled at FD 9717's ACK, as severity and owner always are | the maintainer (by delegation), at FD 9717's ACK | Task 5 |

**Ruled:** **DP-6 (a), WK-674 S2 only** (the maintainer (by delegation), 2026-10-05 15:28:26
BST, D3: *"DP-6: WK-674 S2 only, as the evidence supports. AGREED."*). DP-b2's U3 is not a new
gap for the auditor: it is FD 9995 (working id, #980), per D3's C1′ line. DP-b1 to DP-b4 stay
open. The table above is kept as written.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** `pwd` is the slice worktree; `git branch --show-current` is the slice
  branch; `uv sync --all-packages`; `alembic current` equals `alembic heads` before any pytest.
- [ ] **Step 2:** Re-derive every activation need's state at the dispatch tree and record it
  in the ledger, with the command. Quote each DP's ruling verbatim, and FD-1244's and
  FD-1245's rulings (they decide D4 and E2; RL 9614, working id, until it mints), and
  activation need 13's fix (PL 9616 and SL 9615, working ids, until they mint).
- [ ] **Step 3:** Re-run `PL-1408` Task 0's script verbatim (FD-1356 containment, `PL-1371`
  §7: "FD-1356's Task 0 query is re-run before the demo"). Its last line must read
  `TOTAL route_approved=0`. Anything else is a STOP to the lead.
- [ ] **Step 4:** For every row of §"The steps" whose Needs cell is blank, re-verify its
  route and post-condition at the dispatch tree (`git grep -n` on the route and its test). A
  route that has moved is a STOP, not a silent adjustment.
- [ ] **Step 5:** Record how a test cites a workflow id under `python-test`'s marker rules,
  and use that form in Acceptance 1.

### Task 1: The journey test, red first (Acceptance 1, 2, 6)

**Files:** create `backend/tests/test_wf699_journey.py`.

**Interfaces (consumes):** `examples.fremtpl2.journey.run_wf699_journey`, `JourneyResult`
(fields `step_status: dict[str, str]`, where each value is `"ok"` or `"SKIPPED: <reason>"`,
`rating_version_id: UUID`, `bundle_hash: str`, `prod_premium_minor: int`) and
`JourneyStepFailed(step: str, code: str | None)`.

- [ ] **Step 1: Write the failing tests.** `test_wf699_journey_runs_end_to_end`: seed a small
  workspace with the seed's own functions (the existing `test_demo_rating_evidence.py`
  fixtures, as slice (a) extends them), build an `httpx.Client` over `ASGITransport(app)`
  authenticated as the seed's principals, run `run_wf699_journey`, and assert each step's
  status in §"The steps" order, the codes of Acceptance 3, and Acceptance 4's premium and
  hash. `test_a_journey_failure_names_its_step` (Acceptance 6).
- [ ] **Step 2: Run them, and see each fail by its cause** (`ModuleNotFoundError:
  examples.fremtpl2.journey`). Record the line.
- [ ] **Step 3: Commit** `test(examples): the WF-699 journey test, red (exit-demo (b), WK-1178)`.

### Task 2: Phases A and B over HTTP (Acceptance 2, 3)

**Files:** create `examples/fremtpl2/journey.py`.

- [ ] **Step 1:** `JourneyStepFailed`, `JourneyResult` and a `_call(client, step, method,
  path, *, json=None, expect)` helper. On an unexpected status it raises
  `JourneyStepFailed(step, problem.get("code"))` with the RFC 9457 body's `code` and `detail`.
- [ ] **Step 2:** `_phase_a`: A1–A5 as §"The steps" states, with A6's status per DP-b2's
  ruling. The table slugs and the Factor list come from the approved GLM over HTTP, not from
  constants.
- [ ] **Step 3:** `_phase_b`: build the algorithm with
  `examples.fremtpl2.algorithm.build_fremtpl2_algorithm` over the A-phase table versions, add
  B3's `lookup` and (DP-b3 (a)) B7's sub-graph mount, show B6's refusal with a copy that drops
  one input step, then save. B9 per DP-b2's ruling.
- [ ] **Step 4:** Run the Task 1 test. A and B pass; C onwards still fail at `C1:` with the
  base tree's `VALIDATION_FAILED`, until activation need 10 holds. Commit
  `feat(examples): WF-699 journey phases A and B over HTTP`.

### Task 3: Phases C and D (Acceptance 2, 3)

- [ ] **Step 1:** `_phase_c`: C1 with the algorithm and every pin (PL 9683's typed body),
  including the seed's GBM, submitted but unapproved, so that C4 fails with
  `PIN_NOT_APPROVED`; C5 approves it over HTTP and recompiles; C6 records the bundle hash. C1′
  per DP-b2's ruling.
- [ ] **Step 2:** `_phase_d`: D1–D2 regression; D3 a suite version; D4–D5 as FD-1244's ruling
  shapes it; D6–D8 the dislocation run with attribution; D9 `SKIPPED` with its reason.
- [ ] **Step 3:** Run the Task 1 test to the end of D, then commit
  `feat(examples): WF-699 journey phases C and D over HTTP`.

### Task 4: Phase E, the deploy step and the served quote (Acceptance 2–4)

- [ ] **Step 1:** `_phase_e`: E1–E9 as §"The steps" states, using the submit route FD-1245's
  ruling names, and reading approval responses only through the shape `FD-1416`'s fix
  publishes (activation need 13).
- [ ] **Step 2:** `_deploy`: `dev`, `uat`, the `prod` Deployment Request decided by an
  approver, then `prod`; then S1, the `prod`-bound key and `POST /score`. Assert the bundle
  hash and the integer premium.
- [ ] **Step 3:** Run the Task 1 test green end to end, then commit
  `feat(examples): WF-699 journey phase E, deploy and the served quote`.

### Task 5: The one command, the pre-flight and the served page (Acceptance 5, 7; DP-b1, DP-b4)

**Files:** modify `scripts/demo.py`, `backend/tests/test_demo_command.py`.

- [ ] **Step 1 (DP-b4 (a)): Write the failing pre-flight test.** On a database where the
  record's workspace row is absent, `scripts/demo.py --skip-seed` exits 1 with the message of
  Acceptance 7. Run it red. On the base tree the script starts the API and fails later, inside
  `_verify_journey_postconditions`, which is FD 9717's own reading.
- [ ] **Step 2:** Add the pre-flight after `read_seed_record()`, after SL-1409's checked step
  (activation need 9), so that the two run in that order.
- [ ] **Step 3:** Add `--journey {wf-699}` to `main`. In `demo`, after
  `_verify_journey_postconditions(record, env)`, run the journey against
  `http://localhost:{API_PORT}`, print one line per step, and exit non-zero on
  `JourneyStepFailed` with its `step: code` line. After the frontend starts, `GET` the frontend
  root and require 200, then print the `/demo` URL as today.
- [ ] **Step 4:** The wiring test (Acceptance 5's `test_demo_command.py` assertion). Run green,
  then commit `feat(scripts): one command runs WF-699 to a served page (G2)`.

### Task 6: Rehearsal, the gate and the ledger (Acceptance 5, 8–10)

- [ ] **Step 1:** Check `pgrep -af 'pytest|vitest|flock'` and both gate slots. With none held,
  run the §"Rehearsal checklist" once in full. Record each line.
- [ ] **Step 2:** The full two-half gate through the gate-runner, which holds a gate slot
  under `RL-1263` (Acceptance 9). Record each rc and the tree.
- [ ] **Step 3:** In the slice's `LG-` ledger: every red with its printed line; the DP rulings
  quoted; Task 0's need states and containment output; the rehearsal record;
  `git diff --stat origin/main...HEAD` against §"Write set" (Acceptance 10).

## Rehearsal checklist

Every command runs in the repository root, on `main` at the exit tree, never from a
subdirectory. The tree is recorded before step 1. Each line's output goes into the ledger and
then into the `CR- kind: phase`, by command and tree, never pasted from memory.

| # | Command | Check |
|---|---|---|
| 0 | `git status --short && git rev-parse HEAD origin/main` | clean; HEAD is the exit tree |
| 1 | `pgrep -af 'pytest\|vitest\|flock'`; `flock -n /tmp/slots/gate-1 true`; the same for `gate-2` | nothing heavy running; both slots free |
| 2 | `docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing -Atc "select version_num from alembic_version"` | equals `uv run alembic heads` on the exit tree |
| 3 | `PL-1408` Task 0's script, verbatim | last line `TOTAL route_approved=0` |
| 4 | `FD-1356`'s containment and `FD-1416`'s fix both merged: `git log --oneline origin/main` for each slice's squash | both present |
| 5 | `uv run python scripts/demo.py --journey wf-699` (full seed) | every step `ok` or a ruled `SKIPPED`; the served page 200; the `/demo` URL printed. Elapsed time recorded against NFR-529 (< 5 min to the seeded demo, before the journey) |
| 6 | In the browser: `/demo`, then `/rating-versions/<id>` from step 5's output | both load; the version shows `approved` |
| 7 | `uv run pytest -q backend/tests/test_wf699_journey.py` | passes on the exit tree |
| 8 | NFR-489's verdict on the exit tree: read `SL-1259`'s ledger and PL 9728's result (not re-run here) | recorded with its tree |
| 9 | Ctrl-C the demo; `pgrep -af 'uvicorn\|vite'` | nothing left running |

## Hand-off

1. The lead mints PL 9629 after RL 9623 has minted, and after #1161 (SL 9625, SL 9626, PL 9624)
   has merged or minted in the same batch. It dispatches only after §"Activation needs" hold,
   in a separate activation PR.
2. **Post-mint working-id sweep** (`brief-mint-draft-2026-10-05.md` item 7a): every working id
   this plan cites is re-pointed to its minted id where one exists at the mint tree: RL 9623,
   SL 9625, SL 9626, PL 9624, PL 9683, PL 9688, PL 9689, PL 9649, PL 9716, PL 9728, PL 9776,
   FD 9717, FD 9995, PL 9616, SL 9615, RL 9614, SL 9600, PL 9599, SL 9594, PL 9593. Ids not yet minted are listed as such in the
   mint PR body.
3. **For the lead, from DP-6:** the §12 exit row's `WF-701` A–D (switchover S5, shadow S6) is
   an exit obligation that no slice yet walks as a journey. **The maintainer (by delegation)
   put it to the pre-exit-demo plan review** (`CLAUDE.md` §14), entry 2026-10-05 15:28:26 BST,
   closing line: *"the §12 exit row's WF-701 A–D needs WK-674 S5/S6, put to the pre-exit-demo
   plan review (CLAUDE.md §14)"*. It is not this slice's scope.
4. **For the lead, from DP-b2 (c) and DP-b3:** U1 and U2 to the auditor for findings with
   owners. U3 needs none: it is FD 9995 (working id, #980), per D3. WK-1250 S2/S3 go into `PL-1371`'s G2 list at the next re-baseline if DP-b3 (a) is
   taken.
5. When this slice merges, `FD-1209`'s `WF-699` half is discharged, and with slice (a) the
   whole finding. The auditor closes it.
6. **G2 is not met by this slice alone** (Option A, the maintainer's entry of 2026-10-05
   16:43:31 BST, quoted in §"Does G2 pin a Peril Structure?"). It is met when SL 9594 (A-4,
   working id) merges on top of this slice. SL 9594 walks B4's `model_call` and C1's
   peril-structure pin, and it removes this slice's two `SKIPPED` lines for them. The chain is
   PL 9683 and PL 9649, then A-1, A-2, A-3, then A-4. A-4 also waits on the double-count
   ruling (item 4 of that entry).

## Self-review

1. **Coverage of `PL-1371` §7's (b) paragraph, clause by clause.** "A to E plus deploy":
   §"The steps", Tasks 2–4. "A1–A2 on the 7-factor GLM": A1–A2 row, with the count under
   DP-a1. "the journey test citing `WF-699` by id": Acceptance 1. "WK-673 S6": need 6, with S3,
   S4, S5 and S7 re-derived as needs 3, 4, 5 and 7 (S6 cannot merge before them, and each
   serves a step). "WK-674 S2 only": need 8 and DP-6. "the FD-1356 fix … re-run before the
   demo": need 9, Task 0 Step 3, rehearsal 3. "FD 9752": need 13. "FD-1244 and FD-1245
   rulings": need 14. "DP-6": its row.
2. **The brief's named items:** FD 9708's route (PL 9683): need 10, C1. The FD 9707 fix
   (PL 9688): need 11, B3. The FR-240 fix (PL 9649): need 12, C3. FD 9717 (#1125): need 15,
   DP-b4, Acceptance 7. SL-1409: need 9. The WK-673 slices: needs 3–7. RL 9623: quoted, need 1.
   The PL 9728 DP-6 routing: quoted, step S1.
3. **Dependencies this plan found that `PL-1371` §7 did not list:** WK-673 S7 (A3's weights),
   WK-1250 S2/S3 (B7, DP-b3), and the FD 9707 and FR-240 fixes (findings filed after
   `PL-1371`). Each is named, not folded in silently. `PL-1371` is frozen and is not edited.
4. **Every design choice left open is a DP with an owner** (DP-6, DP-b1 to DP-b4), each with
   options and a recommendation. None is picked silently.
5. **What was not executed.** No code or test was run (docs-only preparation wave). The route
   verdicts rest on the read-only sweep at `809a3794`, re-run at dispatch by Task 0 Step 4.
6. **Type consistency.** `run_wf699_journey`, `JourneyResult` and `JourneyStepFailed` are
   defined in Task 2 Step 1 and consumed with those names in Task 1 and Task 5.

## Pre-mint note, 2026-10-05

*Dated 2026-10-05 (`TZ=Europe/London date`: 2026-10-05 15:35:05 BST), before the mint of PL
9629 (working id).* Edited in place on the unmerged draft #1164, on the lead's order (prep
wave, section S), to record the maintainer's (by delegation) ruling of 2026-10-05 15:28:26 BST,
item D3 and its closing line, and nothing else. What changed: the ruling quoted verbatim;
§"Status"; activation needs 2, 13, 14 and 16; the C1′ row; §"Does G2 pin a Peril Structure?"
(new: the statement D3 asks for, no pin, with the other reading and a recommendation for FD
9995's ACK); a **Ruled** line after the decision-point table; Task 0 Step 2; Hand-off 2, 3 and
4. The new working ids (PL 9616, SL 9615, RL 9614) are in the space form until they mint. No
scope, task cut, write set or other decision point changed. Verified at `origin/main`
`809a3794`; then, after merging `origin/main` `cdaaa573` (#1157, `SL-1409`), re-verified there
at 15:38:18 BST: need 9 is met, and the `demo.py`, `approvals.py`, `errors.py` and
`roadmap.md` line cites that moved are re-anchored beside their `809a3794` values. Needs 13
and 14 still had no PR at 15:38:18 BST.

## Pre-mint note 2, 2026-10-05

*Dated 2026-10-05 (`TZ=Europe/London date`: 2026-10-05 16:50:24 BST), before the mint of PL
9629 (working id).* Edited in place on the unmerged draft #1164, on the lead's order (prep
wave, section AM), to record the maintainer's Option A decision, entry 2026-10-05 16:43:31
BST, and nothing else. What changed: §"Does G2 pin a Peril Structure?" was replaced. Its
answer was "No, FD 9995 stays LOW". It is now "Yes, under Option A", with the entry quoted
verbatim from its opening paragraph to item 6. FD 9995 is HIGH, and A-4 is its own slice (SL
9594 / PL 9593, working ids), not an edit to this plan. Also changed: the C1′ row's reason
(`SKIPPED`, naming FD 9995 and SL 9594); a pointer after the D3 quote; Hand-off 2 (the four
new working ids added to the sweep); and Hand-off 6 (new: G2 is met only when SL 9594 merges).
No task, acceptance item, write set, activation need, owner or other decision point changed,
and the decision-point table is kept as written. `origin/main` `137bc817` merged in. Between
`cdaaa573` and `137bc817`, main changed only `docs/INDEX.md`, `RL-1361` and the new `RL-1418`,
so no line cite moved. The `WF-699` cites `:19`, `:28`, `:59` and `:70` were re-read at
`137bc817` and hold.
