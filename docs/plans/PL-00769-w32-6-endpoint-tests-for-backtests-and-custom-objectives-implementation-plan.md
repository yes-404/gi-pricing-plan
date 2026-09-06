---
id: PL-769
family: plan
kind: leaf
title: W32-6 — Endpoint tests for backtests and custom objectives Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-6-backtest-and-objective-endpoint-tests.md
---

# W32-6 — Endpoint tests for backtests and custom objectives Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the nine backtest and custom-objective HTTP routes real endpoint tests. Today
their entire evidence is two assertions that the paths appear in the OpenAPI document — a route
could return 500 on every call and both would stay green.

**Architecture:** Two new test files, one per surface, following
`backend/tests/test_custom_metrics_api.py`'s structure. No production code changes except one
correction to an existing test that proves less than it claims, and one enforcement gap closed.
The tests target the invariants the platform layer already enforces — workspace scoping, RBAC,
the 409 conflicts and the 422 refusals — because those are the ones a route can silently lose
while every unit test stays green.

**Tech Stack:** pytest (`asyncio_mode = "auto"`), FastAPI `TestClient`, async SQLAlchemy 2.x,
PostgreSQL 16.

**Spec:**
- [`../specs/02-modelling.md`](../specs/02-modelling.md) — FR-144 (backtest results),
  FR-94 (a backtest is readable only inside its workspace, the refusal *naming* it),
  FR-166 (the custom-objective routes), FR-150 (who may derive an objective).
- [`../specs/06-governance.md`](../specs/06-governance.md) — the RBAC model the read and write
  paths check.
- [`PL-00753-wk-664-and-wk-692-the-slice-map.md`](PL-00753-wk-664-and-wk-692-the-slice-map.md) — this slice's row.

---

## Global Constraints

Copied from [`../../CLAUDE.md`](../../CLAUDE.md). Every task's requirements implicitly
include this section.

- **Requirement IDs are permanent** (§5). **This slice allocates none.** Every marker names an
  existing requirement: FR-144, FR-94, FR-166, FR-150. FR-144 has no
  marker anywhere in the repository today, which is why it reads as unevidenced.
- **A `@pytest.mark.req` marker on each test, naming the requirement it satisfies** (§13).
  `--strict-markers` is set, so a typo fails rather than passing silently, and
  `scripts/req-coverage.py` fails on a marker naming a requirement that does not exist.
- **A negative test for every invariant** (§13). For a governed system the suite must prove the
  wrong thing *cannot* happen. Most of this slice is negative tests, on purpose.
- **A refusal test is finished only when a passing case sits beside it**
  (`.claude/skills/python-test/SKILL.md:42-49`). A 403 test whose request would have failed
  anyway proves nothing — Task 3 exists because exactly that happened here once.
- **Never nest `unit_of_work()`** — `.claude/skills/python-test/SKILL.md:526-560`. It hangs with
  no output at all, which reads as a slow test rather than a deadlock.
- **When code and spec disagree, resolve it — do not quietly change one to match the other**
  (§0). Task 4 carries six findings and their verdicts.
- **A fresh worktree has no `.venv`.** Run `uv sync --all-packages --dev` first.
- **The worktree guard refuses compound shell commands.** Run each plainly, not joined by `&&`.

### The gate

```bash
uv sync --all-packages --dev
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
```

`generate-contracts.py --check` must pass **without** a regenerate: this slice adds tests and
edits documents, and changes no shape. If it reports drift, something in Tasks 1–3 touched
`model-schema` and should not have.

**The frontend half is not needed.** Nothing here touches `docs/contracts/`, so
`.github/workflows/frontend.yml`'s `paths:` filter does not fire. Confirm before skipping it:

```bash
git diff --name-only main
```

If any path under `docs/contracts/` appears, run the frontend half too.

Every test in this slice needs a database. **Without the compose stack they `SKIP` rather than
fail**, and a new test file that skips in full looks exactly like a passing one:

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
```

### Where this slice starts

```bash
uv run python scripts/req-coverage.py
uv run python scripts/scope-audit.py MODEL --endpoints
```

Record both numbers before starting; Task 4 quotes the movement. Coverage stands at **258 of
507 requirements marked (50.9%)**. For `--endpoints`, read the output rather than trusting a
zero: `scope-audit.py`'s `implemented_endpoints()` (`:270-271`) returns an **empty set
silently** when `docs/contracts/openapi/generated.json` is missing, so a run in a checkout that
has never generated contracts reports every endpoint unimplemented and looks like a
catastrophe. If the count is 0, regenerate first and re-run.

---

## File structure

| File | Change | Responsibility |
|---|---|---|
| `backend/tests/test_api_backtests.py` | Create | The two backtest routes: their permits, their refusals, their workspace boundary |
| `backend/tests/test_custom_objectives_api.py` | Create | The seven custom-objective routes, at the HTTP layer |
| `backend/tests/test_custom_objectives.py` | Modify `:608-619` | Correct a refusal test that observes the wrong refusal |
| *(the append-only test module)* | Modify | `backtests` is locked in the database and absent from the test's table list |
| `docs/specs/02-modelling.md` | Modify | Six findings resolved where the next stage will read them |
| `docs/roadmap.md` | Modify | The coverage movement, and what remains |

**Ordering.** Tasks 1 and 2 touch disjoint new files and may run in parallel. Task 3 modifies an
existing file neither of them touches. Task 4 is last and consumes all three. W32-1's ledger
recorded that fan-out here is bounded by file collisions, and this slice was cut so there are
none.

**Naming.** `backend/tests/test_backtests.py` and `test_custom_objectives.py` already exist and
test the *platform layer*. The new files carry the `_api` suffix that
`test_custom_metrics_api.py` established for the HTTP layer. Do not add HTTP tests to the
existing files: the two layers have different fixtures, and mixing them is how
`test_custom_objectives.py` ended up with two HTTP tests nobody could find.

### The house style, once, for both new files

Both files open the same way. `backend/tests/test_custom_metrics_api.py` (141 lines) is the
structural template — read it before writing either file.

- Use the **`api_client`** fixture (`backend/tests/conftest.py:56-60`), which is wired to
  `api_settings` (`:38-53`). **Do not use the plain `client` fixture** (`:30-35`) — it has no
  database, and every test here needs one.
- `_headers(role)` — `backend/tests/test_api_datasets.py:27-31`. The role fixtures are at
  `:34-43`; `_slug()` at `:46-47`.
- Tests are plain **sync `def`**. `asyncio_mode = "auto"` means an `async def` test runs, so
  this is a convention rather than an error — but the file's async helpers need
  `unit_of_work()`, and mixing the two styles is what makes the nesting deadlock easy to write.
- Every status assertion carries `, response.text`. A bare `assert r.status_code == 200` on a
  problem+json failure tells you the number and hides the reason.
- Assert problem+json failures on `["code"]`, never on the human-readable `detail`.
- To seed rows, follow the `_seed()` loop idiom at `backend/tests/test_api_models.py:61-96`.
  **`dispose()` is mandatory there** — an engine left open exhausts the pool across a file.

---

### Task 1: The backtest routes

**Files:**
- Create: `backend/tests/test_api_backtests.py`
- Modify: the append-only test module (located in Step 6)

**Interfaces:**
- Consumes:
  - `POST /api/v1/models/{model_id}/backtest` — `backend/src/app/api/models.py:879-928`.
    Requires `FitModels`. Returns **202** with a `Location` header, not the artifact.
  - `GET /api/v1/models/backtests/{backtest_id}` — `:931-957`. Requires `ReadModels`. Returns
    `Backtest` (`packages/model-schema/src/model_schema/backtests.py:98-118`).
  - `RunBacktest`, the request body, at `:869-876`.
  - `load_backtest` — `backend/src/app/platform/backtests.py:287-304`, which folds
    `workspace_id` into its predicate and raises with
    `f"No backtest {backtest_id} in this workspace."`
- Produces: no production interface. This task produces evidence.

**What is untested today.** `backend/tests/test_api_backtests.py` does not exist. The only route
evidence anywhere is `backend/tests/test_backtests.py:566-573`, marked FR-94, which
asserts the two paths appear in the OpenAPI document. That is a test of
`generate-contracts.py`, not of either route.

**The constraint that shapes every test in this file.** `BacktestRow`'s
`uq_backtests_model_version` (`backend/src/app/db/models.py:1359-1400`) has **no workspace
column**. So the same `(model_id, dataset_version_id)` pair cannot be backtested twice *even in
two different workspaces*. Tests here isolate by fresh `workspace_id` (this suite does not roll
back), which normally makes collisions impossible — this constraint is the one place that
guarantee does not hold. **Every test must seed its own model or its own dataset version**, and
a shared module-level fixture that seeds one pair will make the second test in the file fail
with an `IntegrityError` that reads like a bug in the route. That is a finding, recorded in
Task 4; it is not fixed here, because narrowing a uniqueness constraint is a migration and a
governance question about whether cross-workspace model ids can collide at all.

- [ ] **Step 1: Write the file, permits first**

Create `backend/tests/test_api_backtests.py`. Header, helpers, then the two passing cases:

```python
"""The backtest routes over HTTP (FR-144, FR-94).

`test_backtests.py` covers the platform layer. This file covers the two routes: who may
call them, what they return, and the workspace boundary — none of which the platform tests
can see, because they never build a request.
"""

from __future__ import annotations

import pytest


@pytest.mark.req("FR-144")
def test_requesting_a_backtest_returns_202_and_points_at_the_result(api_client) -> None:
    """202 and a `Location`, not the artifact.

    The route enqueues a job; a caller that expected a `Backtest` body would read `{}` and
    conclude the backtest was empty rather than pending.
    """
    model_id, version_id = _seed_model_and_version()
    response = api_client.post(
        f"/api/v1/models/{model_id}/backtest",
        json={"dataset_version_id": str(version_id)},
        headers=_headers(FIT_ROLE),
    )
    assert response.status_code == 202, response.text
    assert response.headers["Location"]


@pytest.mark.req("FR-144")
def test_a_completed_backtest_reads_back_with_its_summary(api_client) -> None:
    ...
```

Write `_seed_model_and_version()` as a module-level helper that creates a fresh workspace, a
model and a dataset version and returns their ids — following `test_api_models.py:61-96`,
including the mandatory `dispose()`. It must mint a **new pair on every call**, for the
uniqueness reason above.

For the second test, seed a `BacktestRow` directly rather than running the worker: the job path
is `test_backtests.py`'s subject, and a route test that ran a fit would be measuring the fit.
Assert the response's `id`, that `summary` is present, and one field inside it — enough that a
route returning a differently-shaped artifact fails here.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest backend/tests/test_api_backtests.py -q`

Expected: FAIL. **If it reports `SKIPPED`, the compose stack is down** — start it and re-run,
because a skipped new file is indistinguishable from a passing one.

- [ ] **Step 3: Make them pass**

These routes exist. A failure here is a defect in the test's seeding or in the route, and the
difference matters: read the failure before changing anything. If a route is genuinely wrong,
that is a §0 resolution for Task 4, not a test to soften.

- [ ] **Step 4: Add the refusals**

Append four negative tests. These are the reason the slice exists.

```python
@pytest.mark.req("FR-94")
def test_a_backtest_in_another_workspace_is_not_found(api_client) -> None:
    """The highest-value test in this task.

    `load_backtest` folds `workspace_id` into its predicate, so a stranger gets 404 rather
    than 403 — the id must not be confirmed to exist. Nothing proves this today, and a
    refactor that moved the workspace check into a separate `if` would leak existence
    through a 403 while every platform test stayed green.

    Shaped after `test_api_models.py:254-272`: seed the backtest under one workspace and
    request it as a fully-authorised principal of another. A test that requested it with no
    role would observe the RBAC refusal instead and prove nothing about scoping.
    """
    backtest_id = _seed_backtest_in_a_stranger_workspace()
    response = api_client.get(
        f"/api/v1/models/backtests/{backtest_id}", headers=_headers(READ_ROLE)
    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-94")
def test_the_refusal_names_the_backtest_that_was_asked_for(api_client) -> None:
    """FR-94's "naming it" clause, which `load_backtest:287-304` implements as
    `f"No backtest {backtest_id} in this workspace."` — an operator holding an id from
    another environment needs to see *which* id was refused."""
    ...


@pytest.mark.req("FR-94")
def test_reading_a_backtest_without_read_models_is_refused(api_client) -> None:
    response = api_client.get(
        f"/api/v1/models/backtests/{backtest_id}", headers=_headers(NO_ROLE)
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "FORBIDDEN"


@pytest.mark.req("FR-144")
def test_requesting_a_backtest_without_fit_models_is_refused(api_client) -> None:
    """`ReadModels` is not enough to *start* one. The permit above uses `FIT_ROLE`, so this
    pair distinguishes the two permissions rather than testing that some header works."""
    ...
```

For the second test, assert the id appears in the response body — read the problem+json shape
in `test_api_datasets.py:228-238` for where the human-readable text lands, and assert on that
field, not on `["code"]`.

- [ ] **Step 5: Run the file**

Run: `uv run pytest backend/tests/test_api_backtests.py -q`
Expected: PASS, 6 tests, none skipped.

- [ ] **Step 6: Close the append-only gap**

`backtests` is in `APPEND_ONLY_TABLES` — the database refuses updates to it — but it is absent
from the test module's `_APPEND_ONLY_ROWS` (`:302-326`), so that enforcement is proven for every
other locked table and not for this one. Locate the module and the two lists:

```bash
grep -rn "_APPEND_ONLY_ROWS" backend/tests
grep -rn "APPEND_ONLY_TABLES" backend/src
```

Add a `backtests` entry to `_APPEND_ONLY_ROWS` matching its neighbours' shape, then run that
module. §13 rule 4 wants the enforcement shown to work, not assumed: the new entry must make
the parametrised test attempt an update and observe the database's refusal. If it passes
without the trigger firing, the entry is wrong.

- [ ] **Step 7: Commit**

```bash
git add backend/tests/test_api_backtests.py backend/tests
git commit -m "test(w32-6): endpoint tests for the backtest routes, and the append-only gap"
```

---

### Task 2: The custom-objective routes

**Files:**
- Create: `backend/tests/test_custom_objectives_api.py`

**Interfaces:**
- Consumes, all in `backend/src/app/api/custom_objectives.py` — seven routes at `:118`, `:165`,
  `:180` (derive), `:204`, `:251` (certify), `:270`, `:298`; request bodies at `:72-115`;
  the shared handler guards at `:137-149`.
- Also consumes:
  - `_get_or_404` — `backend/src/app/platform/objectives.py:703-714`, the workspace-folded
    lookup.
  - The certify conflict at `objectives.py:376-388`, the submit conflict at `:505-516`.
  - `_require_evidence`, which raises 422 `EVIDENCE_INCOMPLETE`.
  - `refuse_expression_kind` — `:243-283`, typed `-> NoReturn`, raising 409.
  - `default_sampling(...)`, whose contract `model_handlers.py:1528-1531` documents.
- Produces: no production interface.

**What is untested today.** Two HTTP tests exist, both marooned in
`backend/tests/test_custom_objectives.py` (`:608-619` and `:622-658`) — a platform-layer file —
plus one OpenAPI-presence assertion at `:591-605` marked FR-166. Seven routes, one of
which is a governance gate, and the evidence is that their paths are spelled correctly.

**What to test, and what not to.** Immutability is already the best-covered invariant in the
custom-objective code, and `CustomObjectiveRow`'s six CHECK constraints
(`backend/src/app/db/models.py:1530-1610`) are enforced by the database and exercised by the
platform tests. **There is no PATCH or PUT route**, so there is no update path to test. The gap
is the HTTP layer: authorisation, workspace scoping, and the three conflicts that a route can
report as a 500 without any platform test noticing.

- [ ] **Step 1: Write the permits**

Create `backend/tests/test_custom_objectives_api.py`. Follow
`backend/tests/test_custom_metrics_api.py` closely — it is the nearest neighbour in both
subject and shape.

Cover the read paths first: list, get, and one create. Assert the artifact's shape on the way
back out, not merely the status:

```python
@pytest.mark.req("FR-166")
def test_an_objective_reads_back_with_its_declared_kind(api_client) -> None:
    ...
    assert body["expression_kind"] == "..."
```

Read `:72-115` for the exact request bodies. Do not invent field names — `extra="forbid"` means
a wrong one produces a 422 that looks like a validation test passing.

- [ ] **Step 2: Run them to verify they fail, then make them pass**

Run: `uv run pytest backend/tests/test_custom_objectives_api.py -q`

New tests against existing routes fail on seeding, not on the route. Read each failure.

- [ ] **Step 3: The workspace boundary**

```python
@pytest.mark.req("FR-166")
def test_an_objective_in_another_workspace_is_not_found(api_client) -> None:
    """`_get_or_404` (`objectives.py:703-714`) folds the workspace into its predicate, so a
    stranger sees 404 and not 403. Untested today, and the failure mode is silent: a route
    that lost the fold would return other workspaces' objectives to any authorised reader,
    and every existing test would stay green because they all use one workspace."""
    ...
```

Use the seed-under-a-stranger shape from `test_api_models.py:254-272` — a fully-authorised
principal of a *different* workspace. Add the same test for the list route: a list that leaks is
worse than a get that leaks, and it fails differently (an extra item, not a wrong status).

- [ ] **Step 4: The three conflicts**

Each of these is a specific status the routes are documented to return and that nothing
currently proves they do.

```python
@pytest.mark.req("FR-166")
def test_certifying_an_already_certified_objective_conflicts(api_client) -> None:
    """`objectives.py:376-388`. 409 rather than a silent re-certification: certification is
    a governance event, and repeating one would write a second audit record claiming a
    review that did not happen."""
    ...
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "..."


@pytest.mark.req("FR-166")
def test_submitting_an_objective_twice_conflicts(api_client) -> None:
    """`objectives.py:505-516`."""
    ...


@pytest.mark.req("FR-166")
def test_certifying_without_the_required_evidence_is_refused(api_client) -> None:
    """`_require_evidence` → 422 `EVIDENCE_INCOMPLETE`. The distinction from the 409 above
    matters to a caller: one means "already done", the other "not yet allowed"."""
    ...
    assert response.json()["code"] == "EVIDENCE_INCOMPLETE"
```

Read the real error codes from the raising sites; do not guess them. `grep -n "code=" ` in
`backend/src/app/platform/objectives.py` gives all three.

- [ ] **Step 5: The expression-kind refusal, with its permit beside it**

`refuse_expression_kind` (`:243-283`) is typed `-> NoReturn` and raises 409. Write the refusal
**and a passing case using an accepted kind** —
`.claude/skills/python-test/SKILL.md:42-49` is explicit that a refusal test alone cannot
distinguish "refused for the right reason" from "refused for any reason", and Task 3 is the
worked example of that failure in this very subject area.

- [ ] **Step 6: Certify's sampling default**

`model_handlers.py:1528-1531` documents that `_certify` fills `parameters["sampling"]` from
`default_sampling(...)`. That means the endpoint can be tested **without running the job**:
call certify, read the stored objective back through the get route, and assert
`parameters["sampling"] == default_sampling(...)` with the same arguments the handler uses.
Import `default_sampling` rather than hard-coding its result — a test asserting a literal would
pass after the default changed and the endpoint stopped applying it.

- [ ] **Step 7: Run the file**

Run: `uv run pytest backend/tests/test_custom_objectives_api.py -q`
Expected: PASS, none skipped.

- [ ] **Step 8: Commit**

```bash
git add backend/tests/test_custom_objectives_api.py
git commit -m "test(w32-6): endpoint tests for the custom-objective routes"
```

---

### Task 3: Correct the refusal test that observes the wrong refusal

**Files:**
- Modify: `backend/tests/test_custom_objectives.py:608-619`

**Interfaces:**
- Consumes: the derive route (`custom_objectives.py:180-201`) and its `FitModels` requirement.
- Produces: no interface. It replaces a test whose claim exceeds what it observes.

**The defect.** `test_the_derive_route_refuses…` at `:608-619` grants the caller **nothing**,
and asserts `response.status_code in (403, 409)`. `FitModels` is checked first, so the request
can only ever produce the 403 — the 409 arm is unreachable. The test is marked as evidence for
FR-150, which is about *who may derive an objective under what conditions*, and it proves
only that an unauthorised caller is refused. The conditional assertion is what hid it: a test
that accepts either of two statuses cannot fail when the wrong one arrives.

This is §0 territory. The route is right; the test's claim is wrong. Split it.

- [ ] **Step 1: Read the current test and the route it targets**

```bash
sed -n '600,625p' backend/tests/test_custom_objectives.py
sed -n '180,205p' backend/src/app/api/custom_objectives.py
```

Confirm the order of the guards before rewriting — if RBAC is *not* first, the finding changes
and Task 4's verdict must change with it.

- [ ] **Step 2: Replace it with two tests**

One keeps the 403 and says so plainly; the other grants `FitModels` and drives the route to the
actual 409 condition. Neither uses a disjunctive assertion:

```python
@pytest.mark.req("FR-150")
def test_deriving_without_fit_models_is_refused(...) -> None:
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "FORBIDDEN"


@pytest.mark.req("FR-150")
def test_deriving_from_an_objective_in_the_wrong_state_conflicts(...) -> None:
    """The arm the old test could never reach: RBAC is checked first, so a caller granted
    nothing is refused before the state is looked at. Granting `FitModels` is what makes
    this a test of FR-150 rather than of RBAC."""
    assert response.status_code == 409, response.text
```

- [ ] **Step 3: Run them**

Run: `uv run pytest backend/tests/test_custom_objectives.py -q -k derive`
Expected: PASS, both.

- [ ] **Step 4: Prove the second one can fail**

§13 rule 4. Temporarily remove the state that causes the conflict and confirm the second test
fails with a 2xx rather than passing on a coincidence. Restore it and re-run.

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_custom_objectives.py
git commit -m "test(w32-6): split the derive refusal so each test observes one refusal"
```

---

### Task 4: Resolve the findings

**Files:**
- Modify: `docs/specs/02-modelling.md`
- Modify: `docs/roadmap.md`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: no code. §0's resolution and §13 rule 6's statement of what was not delivered.

**Six findings. Four are resolved here; two are recorded with owners.**

1. **The derive refusal proved a different thing than it claimed** (Task 3). Resolved: split
   into two tests, each observing one refusal, with the 409 arm actually reached.
2. **`backtests` was locked in the database and absent from the append-only test's table list**
   (Task 1 Step 6). Resolved: the entry added, and the trigger shown to fire.
3. **FR-144 had no marker anywhere.** Resolved: Task 1's four tests carry it.
4. **A stale docstring** at `backend/src/app/platform/backtests.py:18` says `n_points=300`;
   `COUNT_GRID` at `:76-78` uses `n_points=1_000`. Resolved: correct the docstring. It is one
   line, it is in this slice's subject area, and a docstring stating a wrong default is read by
   the next person as the contract.
5. **`uq_backtests_model_version` carries no workspace column** (`db/models.py:1359-1400`), so
   the same `(model_id, dataset_version_id)` pair cannot be backtested in two workspaces.
   **Recorded, not fixed.** Narrowing it is a migration plus a governance question — whether
   model ids are workspace-unique at all — and this slice is a test slice. It gets a spec note
   with an owner, because the next person to write a backtest test will hit it and needs to know
   it is known.
6. **The read routes are single-layer RBAC**, and the `derive` route publishes a 200
   `CustomObjective` response it can never return (it enqueues). **Recorded, not fixed.** The
   second is a contract inaccuracy that would mislead a generated client; it is small, but it is
   a `model-schema` change and this slice must not touch shapes — Task 4's whole point is that
   the gate's `--check` passes without a regenerate.

- [ ] **Step 1: Fix the stale docstring**

```bash
sed -n '14,22p' backend/src/app/platform/backtests.py
sed -n '74,80p' backend/src/app/platform/backtests.py
```

Correct `300` to `1_000`, or better, have the docstring name `COUNT_GRID` rather than restate
its value — a restated constant goes stale again the next time it changes.

- [ ] **Step 2: Append the resolution notes to `02-modelling.md`**

To FR-144's row, as part of the same single line:

> **Evidenced 2026-08-23 (W32-6).** Previously carried no `@pytest.mark.req` marker anywhere;
> `backend/tests/test_api_backtests.py` now covers the 202-and-`Location` contract, the read-back
> shape, and both permission refusals.

To FR-94's row:

> **Evidenced 2026-08-23 (W32-6).** The prior marker sat on an OpenAPI-presence assertion
> (`test_backtests.py:566-573`) which would have stayed green against a route returning 500 on
> every call. The cross-workspace 404 and the "naming it" clause are now tested over HTTP.

To FR-166's row, the same shape.

To FR-150's row:

> **Evidenced 2026-08-23 (W32-6), and the prior evidence corrected.** The test claiming this
> requirement asserted `status_code in (403, 409)` while granting the caller nothing; RBAC is
> checked before state, so only the 403 was ever reachable and the requirement's actual subject
> was untested. Split into two tests, each observing one refusal.

Then append a note in §4's backtest data-contract subsection, at the end of the existing prose:

> **`uq_backtests_model_version` is not workspace-scoped** (recorded 2026-08-23, W32-6). The
> same `(model_id, dataset_version_id)` pair therefore cannot be backtested twice even in two
> different workspaces, which is the one place this suite's fresh-workspace isolation does not
> hold. Whether that is correct depends on whether model ids may collide across workspaces at
> all — a governance question, not a test-fixture problem. **Owner: unassigned; raise before the
> next backtest slice.**

- [ ] **Step 3: Update the roadmap**

```
W32-6 closed 2026-08-23. Nine routes that had two OpenAPI-presence assertions between them
now have endpoint tests. FR-144, FR-94, FR-166 and FR-150 evidenced;
FR-150's prior evidence was wrong and is corrected rather than added to.

Requirement coverage moved from 258/507 (50.9%) to <N>/507.

**Recorded, not fixed:** `uq_backtests_model_version` is not workspace-scoped (a migration and
a governance question, owner unassigned); the `derive` route publishes a 200 `CustomObjective`
it can never return (a `model-schema` change, owner unassigned); the read routes are
single-layer RBAC, which is consistent with the rest of the API and is noted rather than
proposed as a change.
```

Fill `<N>` from the actual run — do not predict it.

- [ ] **Step 4: Run the documentation checks**

```bash
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/scope-audit.py MODEL --endpoints
```

Expected: the first passes; the second reports a higher marked count and lists FR-144 as
covered. `--endpoints` should be **unchanged** — this slice publishes no new endpoint, and a
movement there means something in Tasks 1–3 edited a route.

- [ ] **Step 5: Run the full gate**

Every command in the gate block, each on its own line, reading each one's own exit code.
`generate-contracts.py --check` must pass without a regenerate.

- [ ] **Step 6: Commit**

```bash
git add docs/specs/02-modelling.md docs/roadmap.md backend/src/app/platform/backtests.py
git commit -m "docs(w32-6): resolve the six findings the endpoint tests surfaced"
```

---

## Closing the slice

- [ ] Every task's steps are checked.
- [ ] `uv run pytest backend/tests/test_api_backtests.py backend/tests/test_custom_objectives_api.py -q`
      reports passes and **no skips** — a skipped file is the failure mode this slice is
      designed to avoid.
- [ ] `req-coverage.py` shows FR-144 covered, and the total moved.
- [ ] The append-only entry was shown to fire the database trigger, not merely added.
- [ ] The derive 409 test was shown to fail when the conflicting state is removed.
- [ ] `generate-contracts.py --check` passed with no regenerate.
- [ ] The two unfixed findings have spec notes with owners; neither was quietly dropped.
- [ ] The branch is pushed and a PR is open. Do not force-push, do not merge, do not push to
      `main`.

## Self-Review

**1. Spec coverage.** All four requirements this slice claims get tests that exercise the
behaviour rather than the document: FR-144 (Task 1's 202/`Location`, read-back, and two
permission refusals), FR-94 (the cross-workspace 404 and the "naming it" clause, both in
Task 1 Step 4), FR-166 (Task 2's seven-route coverage: reads, the boundary, the three
conflicts, the expression-kind refusal with its permit, and certify's sampling default),
FR-150 (Task 3's split). The three findings this slice does **not** fix — the uniqueness
constraint, the `derive` response shape, single-layer RBAC on reads — are each stated with a
reason and an owner in Task 4, rather than being left for the next reader to rediscover.

**2. Placeholder scan.** Test bodies are elided with `...` in eleven places. Each names the exact
source to read for the missing part — `test_api_models.py:254-272` for the stranger-workspace
shape, `test_api_models.py:61-96` for seeding, `test_custom_metrics_api.py` for file structure,
`custom_objectives.py:72-115` for request bodies, `objectives.py` for the three error codes —
rather than saying "similar to the above". Three values are deliberately not written into this
plan because writing them would be guessing: the three conflict error codes (Task 2 Step 4 says
to `grep -n "code="` for them), the append-only test module's path (Task 1 Step 6 greps for it),
and the new coverage total (Task 4 Step 3 says to fill it from the run). Each has the exact
command beside it.

**3. Type consistency.** `_seed_model_and_version()` is introduced in Task 1 Step 1 and used
under that name in every later step of the task; `_seed_backtest_in_a_stranger_workspace()`
likewise in Step 4. `_headers(role)` and `_slug()` are used with the signatures they have at
`test_api_datasets.py:27-31` and `:46-47`. `default_sampling(...)` is imported and called in
Task 2 Step 6 rather than having its result inlined, which is the only place a type mismatch
could hide. No task defines a production symbol, so there is no cross-task signature to
diverge — this slice adds tests, and that is by design.
