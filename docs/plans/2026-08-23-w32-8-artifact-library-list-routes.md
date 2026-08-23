# Artifact Library List Routes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Custom Objectives, Custom Metrics and Peril Structures the list routes they have
never had, each cursor-paginated, filterable by `status` and `slug`, and — for the first two —
carrying a `usage_count` computed as one aggregate per page.

**Architecture:** Three routes over one shared idea. Pagination, filtering and cursor encoding
already exist (`app/api/pagination.py`) and the exemplar is `GET /models`
(`backend/src/app/api/models.py:544-607`), so the list halves are near-mechanical. The load-bearing
half is `usage_count`: FR-MODEL-127 makes "one aggregate per page, never one per row" part of the
requirement, and the **two** existing usage handlers are per-artifact and unpaginated, so calling
one per row **is** the N+1 the requirement forbids. They are `get_metric_usage`
(`app/api/custom_metrics.py:260`) and `get_usage` (`app/api/custom_objectives.py:303`) — two, not
three, and not identically named: **peril structures have no usage function or route at all**,
which is Task 5's third recorded spec disagreement. The precedent to follow instead is the batched
aggregate on the dataset list, passed into the schema conversion as a keyword
(`backend/src/app/api/datasets.py:329-380`); note the keyword there is **`latest_version`** and it
carries a tuple, not a `latest_version_status` scalar — read the call site before copying its
shape. The objective side reads a top-level JSONB
scalar; the metric side needs a lateral expansion of a JSONB array.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x async, PostgreSQL 16 (JSONB),
`pytest`, `uv`.

**Spec:** [`../specs/02-modelling.md`](../specs/02-modelling.md) — FR-MODEL-127 (`:231`) and the
three §5.1 rows it added (`:1697`, `:1705`, `:1712`).

**Proposed slice id:** `W32-8`. The W32 slice boundaries in
[`2026-08-22-w6b-slice-map.md`](2026-08-22-w6b-slice-map.md) are recorded as *pending* maintainer
acceptance and stop at `W32-6`; this number is a proposal, not an accepted allocation.

## Global Constraints

- FR-MODEL-127 exists (appended 2026-08-23). No new requirement ids; no `Next free:` marker.
- **`usage_count` goes on objectives and metrics only.** §5.1's peril-structures row (`:1712`) asks
  for pagination and the two filters and no count, while the other two rows name `usage_count`
  explicitly. Task 5 records the discrepancy between that and FR-MODEL-127's unqualified prose;
  **do not resolve it by building a peril count**, which would be choosing a side silently
  (`CLAUDE.md` §0).
- **One aggregate per page.** Never call `get_metric_usage` or `get_usage` inside a row loop.
  Task 1 Step 9 proves the budget with a query counter rather than asserting it.
- The count must agree with the detail route's blast radius. `GET /{id}/usage` and the row's
  `usage_count` answering differently about the same artifact is worse than either being absent.
- Filters are `status` and `slug`. **`slug` is an exact match, not a prefix or substring** —
  FR-MODEL-127 says the filter is what resolves §5.3's `slug@version` addresses against UUID-only
  detail routes, which needs equality.
- List routes declare `responses=problems(400, 401, 403, 422)` — 400 in, **404 out**. An empty page
  is a 200 with no items; a filter matching nothing is not an error.
- Existing indexes cover the filters: every table carries
  `Index("ix_<table>_slug_status", "workspace_id", "slug", "status")`. **No migration in this
  slice.**
- Every new test carries `@pytest.mark.req("FR-MODEL-127")`. `--strict-markers` is on.
- Conventional Commits. Commit at the end of every task.

---

### Task 1: The batched usage aggregate

**Files:**
- Modify: `backend/src/app/platform/objectives.py` — add beside `usage` at `:618-670`
- Modify: `backend/src/app/platform/metrics.py` — add beside `usage` at `:543-596`
- Test: `backend/tests/test_artifact_usage_counts.py` (new)

**Interfaces:**
- Produces: `objectives.usage_counts(session, *, workspace_id: UUID, refs: Sequence[str]) -> dict[str, int]`
- Produces: `metrics.usage_counts(session, *, workspace_id: UUID, refs: Sequence[str]) -> dict[str, int]`

Both take the canonical `{type}:{slug}@{version}` refs of one page's rows and return a count per
ref. A ref with no models is **absent from the mapping**, not zero — the caller supplies the zero,
so a missing key and a genuine zero cannot be confused by a bug in either.

- [ ] **Step 1: Read what the per-artifact versions do**

```bash
sed -n '618,670p' backend/src/app/platform/objectives.py
sed -n '543,596p' backend/src/app/platform/metrics.py
```

Two things to extract, because the new function must match them exactly or the row and the detail
route will disagree about the same artifact:

1. **The workspace filter** — how `usage` scopes models to the workspace.
2. **The status treatment** — whether `usage` counts every Model Spec or only some statuses
   (archived, draft). Whatever it does, `usage_counts` does the same.

Write both answers into the new functions' docstrings. If `usage` turns out to count something the
row plainly should not, stop and raise it rather than diverging: the requirement's `usage_count`
is "the count of Model Specs referencing that artifact", and the detail route is the existing
reading of that sentence.

- [ ] **Step 2: Write the failing test**

Create `backend/tests/test_artifact_usage_counts.py`:

```python
"""FR-MODEL-127: the per-page usage aggregate behind each library row's `usage_count`."""

from __future__ import annotations

import pytest

from app.platform import metrics, objectives


@pytest.mark.req("FR-MODEL-127")
async def test_objective_usage_counts_are_returned_per_ref(database, workspace_id, ...) -> None:
    """One call, several refs, a count each — the shape a page needs.

    Two objectives, one used by two models and one by none, plus a third ref belonging to
    another workspace's model so the scoping is exercised rather than assumed.
    """
    used, unused = await _two_objectives(...)
    await _model_using_objective(used)
    await _model_using_objective(used)

    counts = await objectives.usage_counts(
        session, workspace_id=workspace_id, refs=[used, unused]
    )
    assert counts[used] == 2
    assert unused not in counts, "an unused ref is absent, not zero — the caller supplies zero"


@pytest.mark.req("FR-MODEL-127")
async def test_metric_usage_counts_expand_the_eval_metrics_array(
    database, workspace_id, ...
) -> None:
    """`eval_metrics` is a JSONB **array**, so a model may reference several metrics.

    The objective side reads one scalar; this side must count a model once per metric it
    names, and must not miss a metric that is second in the array.
    """
    first, second = await _two_metrics(...)
    await _model_using_metrics([first, second])
    await _model_using_metrics([second])

    counts = await metrics.usage_counts(
        session, workspace_id=workspace_id, refs=[first, second]
    )
    assert counts == {first: 1, second: 2}


@pytest.mark.req("FR-MODEL-127")
async def test_a_count_matches_the_detail_route_blast_radius(database, workspace_id, ...) -> None:
    """The row and the detail route must not disagree about the same artifact.

    A row saying 3 beside a `/usage` page listing 5 is the kind of inconsistency an actuary
    reports as a data bug and an auditor reports as something worse.
    """
    ref = await _objective_used_by(3)
    counts = await objectives.usage_counts(session, workspace_id=workspace_id, refs=[ref])
    blast = await objectives.usage(session, workspace_id=workspace_id, ...)
    assert counts[ref] == len(blast.models)
```

The elided helpers build Model rows whose `spec` names the ref. Build them by copying an existing
fitted-model fixture rather than hand-writing a `ModelSpec` dict — `CLAUDE.md` §2 forbids
hand-writing a shape `model-schema` already defines, and a spec dict assembled by hand in a test is
exactly that. Find one with:

```bash
grep -rn "def _spec\|ModelSpec(" backend/tests/test_model_jobs.py | head
```

Check `usage`'s real return shape before writing the third test's last line — `blast.models` is a
guess from the §5.1 row's wording, not something this plan verified.

- [ ] **Step 3: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_artifact_usage_counts.py -v
```
Expected: FAIL with `AttributeError: module 'app.platform.objectives' has no attribute 'usage_counts'`.

- [ ] **Step 4: Write the objective aggregate**

In `backend/src/app/platform/objectives.py`:

```python
async def usage_counts(
    session: AsyncSession, *, workspace_id: UUID, refs: Sequence[str]
) -> dict[str, int]:
    """Count the Model Specs referencing each of `refs`, in **one** query (FR-MODEL-127).

    The library row's count, not the detail route's blast radius: same question, page-sized
    answer. `usage` above answers it for one artifact and is deliberately not reused here —
    calling it per row is the N+1 FR-MODEL-127 names as part of the requirement, and it would
    be indistinguishable from this until a workspace held a few hundred artifacts.

    A ref no model references is **absent** from the result rather than zero: the caller
    supplies the zero, so a bug that drops a ref cannot present as a genuine zero.

    `spec` is one JSONB column and `objective.ref` is a top-level scalar inside it, so this
    is an equality on an extracted text value. There is no index on `models.spec` today; at
    Phase 1b's scale the sequential scan is well inside budget, and the note is here so the
    next person reads a decision rather than an oversight.
    """
    if not refs:
        return {}
    ref_column = ModelRow.spec["objective"]["ref"].astext
    rows = await session.execute(
        select(ref_column, func.count())
        .where(ModelRow.workspace_id == workspace_id, ref_column.in_(list(refs)))
        .group_by(ref_column)
    )
    return {ref: count for ref, count in rows.all()}
```

Apply whatever status filter Step 1 found on `usage`, in the same `where`.

- [ ] **Step 5: Write the metric aggregate**

In `backend/src/app/platform/metrics.py`:

```python
async def usage_counts(
    session: AsyncSession, *, workspace_id: UUID, refs: Sequence[str]
) -> dict[str, int]:
    """Count the Model Specs referencing each metric ref, in one query (FR-MODEL-127).

    `eval_metrics` is a JSONB **array**, not a scalar, so a model may name several metrics
    and must be counted once against each. The single-artifact query above uses containment
    (`spec["eval_metrics"] @> [{"ref": …}]`), which is right for one ref and cannot be
    grouped across a page — containment answers "does this model use it", and the page needs
    "which of these does each model use". Hence the lateral expansion.
    """
    if not refs:
        return {}
    element = func.jsonb_array_elements(ModelRow.spec["eval_metrics"]).table_valued("value").lateral()
    ref_column = element.c.value["ref"].astext
    rows = await session.execute(
        select(ref_column, func.count())
        .select_from(ModelRow)
        .join(element, true())
        .where(ModelRow.workspace_id == workspace_id, ref_column.in_(list(refs)))
        .group_by(ref_column)
    )
    return {ref: count for ref, count in rows.all()}
```

**The `coalesce` is required, and not for the reason it looks like.** `eval_metrics` is declared
on **`GbmSpec` only** — `packages/model-schema/src/model_schema/modelling.py:1345`, inside
`class GbmSpec(ModelSpecCommon)` at `:1303`. It is not on `ModelSpecCommon` (`:815`), so a
`GlmSpec` (`:1011`) or `EbmSpec` (`:1418`) row has **no `eval_metrics` key at all**, and every
workspace with a GLM in it has such rows. `jsonb_array_elements` errors on a missing key rather
than returning nothing, so the lateral must read:

```sql
jsonb_array_elements(coalesce(spec->'eval_metrics', '[]'::jsonb))
```

Its default on `GbmSpec` is `()`, which serialises to `[]` — so a GBM with no metrics is already
safe and would have hidden this. **Seed a GLM row in the test**, not a GBM with an empty array;
the empty array passes without the `coalesce` and proves nothing.

- [ ] **Step 6: Run the tests to verify they pass**

Run:
```bash
uv run pytest backend/tests/test_artifact_usage_counts.py -v
```
Expected: PASS.

- [ ] **Step 7: Prove the budget with a query counter**

FR-MODEL-127 makes the query count part of the requirement, so it gets a test, not a comment:

```python
@pytest.mark.req("FR-MODEL-127")
async def test_one_page_of_refs_costs_one_query(database, workspace_id, ...) -> None:
    """**The budget is the requirement.** One aggregate per page, never one per row.

    Asserted with a counter because an N+1 implementation returns identical results and
    would stay correct-looking until a workspace held a few hundred artifacts — the exact
    failure FR-MODEL-127 says it is stating the budget to prevent.
    """
    from sqlalchemy import event

    refs = await _n_objectives(25)
    statements: list[str] = []
    engine = database.engine.sync_engine

    def _record(conn, cursor, statement, parameters, context, executemany) -> None:
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", _record)
    try:
        await objectives.usage_counts(session, workspace_id=workspace_id, refs=refs)
    finally:
        event.remove(engine, "before_cursor_execute", _record)

    assert len(statements) == 1, f"{len(statements)} statements for 25 refs:\n" + "\n".join(statements)
```

Confirm the attribute path to the sync engine against `backend/src/app/db/session.py` before
running — `database.engine.sync_engine` is the usual shape for an `AsyncEngine` but check.

- [ ] **Step 8: Run it, then break the implementation to prove it bites**

```bash
uv run pytest backend/tests/test_artifact_usage_counts.py -k costs_one_query -v
```
Expected: PASS. Then replace the body of `objectives.usage_counts` with a loop calling `usage` per
ref, re-run, and confirm it FAILS reporting 25 statements. Restore with
`git checkout -- backend/src/app/platform/objectives.py` and verify with `git status --short`.
Record the failure message in the ledger.

- [ ] **Step 9: Commit**

```bash
git add backend/src/app/platform/objectives.py backend/src/app/platform/metrics.py
git add backend/tests/test_artifact_usage_counts.py
git commit -m "feat(w32-8): count artifact usage one page at a time"
```

---

### Task 2: `GET /api/v1/custom-objectives`

**Files:**
- Modify: `backend/src/app/api/custom_objectives.py` — a list route above the create at `:118`
- Modify: `backend/tests/test_custom_objectives_api.py:14-17`, `:366-368` — two stale comments
- Test: `backend/tests/test_custom_objectives_api.py`

**Interfaces:**
- Consumes: `objectives.usage_counts` from Task 1.
- Produces: `ObjectiveFilter` (query-parameter model) and
  `list_objectives(...) -> Page[CustomObjectiveSummary]`.
- Produces: `CustomObjectiveSummary` in `model-schema`, or a `usage_count` keyword on the existing
  summary conversion — Step 3 decides which against what is already there.

**A divergence this task must settle.** The list-route exemplars keep their query in the router
(`app/api/models.py:544-607`, `app/api/validation.py:200-255`), but all three artifact modules
import no SQLAlchemy at all — their queries live in `app/platform/{objectives,metrics,perils}.py`,
which also re-check RBAC. Follow the **module's own** convention, not the exemplar's: put
`list_objectives` in `app/platform/objectives.py` and keep the router thin. A router that reached
for SQLAlchemy here would be the only one in its module that does, and the next person would have
two patterns and no rule.

- [ ] **Step 1: Write the failing tests**

Add to `backend/tests/test_custom_objectives_api.py`. **Read `:56-178` before writing a line** —
four things about this harness are not what a list-route test usually assumes, and each one
produces a test that fails for the wrong reason:

| Assumption | What this module actually does |
|---|---|
| the client fixture is `api_client` | it is **`client`** (`:56-58`), an alias this module's tests use throughout |
| actor fixtures are principals, so wrap them in `_headers(...)` | `author`, `submitter`, `reader` and `stranger` **are already header dicts** (`:60-93`). Pass `headers=author`, never `headers=_headers(author)` |
| `_run(...)` unwraps a response | `_run[T](work: Callable[[Database], Awaitable[T]])` (`:96`) runs an **async callable on its own loop**. It has nothing to do with HTTP: `_run(client.get(...))` passes a `Response` where a coroutine function is expected |
| `_advance(client, obj, actor, to=...)` moves a lifecycle | it is `_advance(objective_id: UUID, *, status: ObjectiveStatus)` (`:130`) and does its own database work — no client, no actor, and `status` takes the enum, not a string |

Two more: there is **no `no_permission_actor` fixture**, and `stranger` is *authenticated into
this workspace holding nothing* (`:90-93`) — so `stranger` is the 403 case, not the
cross-workspace case. The cross-workspace idiom is `_copy_into(new_uuid7(), objective)` (`:147`),
which inserts the same declaration under another workspace directly, because `grant` is
workspace-scoped and no principal these tests can build holds `model:fit` in a second one.

```python
@pytest.mark.req("FR-MODEL-127")
def test_the_library_lists_the_workspace_objectives(
    client: TestClient, author: dict[str, str]
) -> None:
    """The screen `02` §5.3 specifies had no endpoint to draw from until this route."""
    first, second = _create(client, author), _create(client, author)
    response = client.get("/api/v1/custom-objectives", headers=author)
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["items"]}
    assert {first["id"], second["id"]} <= ids


@pytest.mark.req("FR-MODEL-127")
def test_the_slug_filter_is_an_exact_match(
    client: TestClient, author: dict[str, str]
) -> None:
    """**Exact**, not a prefix.

    FR-MODEL-127 makes this filter the thing that resolves §5.3's `slug@version` addresses
    against UUID-only detail routes. A prefix match would resolve `motor-ad` to `motor-ad`
    and `motor-ad-severity` alike, which is a wrong artifact rather than a wide result.
    """
    target = _create(client, author)
    _create(client, author, slug=f"{target['slug']}-extended")
    response = client.get(
        f"/api/v1/custom-objectives?slug={target['slug']}", headers=author
    )
    assert response.status_code == 200, response.text
    assert [row["id"] for row in response.json()["items"]] == [target["id"]]


@pytest.mark.req("FR-MODEL-127")
def test_the_status_filter_selects_one_lifecycle_state(
    client: TestClient, author: dict[str, str]
) -> None:
    draft = _create(client, author)
    moved = _create(client, author)
    _advance(UUID(moved["id"]), status=ObjectiveStatus.REVIEW)
    response = client.get("/api/v1/custom-objectives?status=review", headers=author)
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["items"]}
    assert moved["id"] in ids and draft["id"] not in ids


@pytest.mark.req("FR-MODEL-127")
def test_each_row_carries_its_usage_count(
    client: TestClient, author: dict[str, str]
) -> None:
    """§5.1:1697 puts the count on the row; an unreferenced objective reads zero, not null."""
    used, unused = _create(client, author), _create(client, author)
    _seed_model_referencing(UUID(used["id"]), used["slug"])
    response = client.get("/api/v1/custom-objectives", headers=author)
    assert response.status_code == 200, response.text
    rows = {row["id"]: row for row in response.json()["items"]}
    assert rows[used["id"]]["usage_count"] == 1
    assert rows[unused["id"]]["usage_count"] == 0


@pytest.mark.req("FR-MODEL-127")
def test_the_library_stops_at_the_workspace_boundary(
    client: TestClient, author: dict[str, str]
) -> None:
    """**Negative.** A list route is the easiest place to leak a whole workspace at once."""
    mine = _create(client, author)
    elsewhere = _copy_into(new_uuid7(), mine)
    response = client.get("/api/v1/custom-objectives", headers=author)
    assert response.status_code == 200, response.text
    ids = {row["id"] for row in response.json()["items"]}
    assert mine["id"] in ids
    assert str(elsewhere) not in ids


@pytest.mark.req("FR-MODEL-127")
def test_listing_without_model_read_is_refused(
    client: TestClient, author: dict[str, str], stranger: dict[str, str]
) -> None:
    """**Negative.** The refusal idiom at `:394-404`, on the list route.

    `stranger` is authenticated into this workspace and holds nothing, so the 403 is the
    permission answering rather than an empty page that happens to look the same.
    """
    _create(client, author)
    response = client.get("/api/v1/custom-objectives", headers=stranger)
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "PERMISSION_DENIED"


@pytest.mark.req("FR-MODEL-127")
def test_the_page_is_cursor_paginated(
    client: TestClient, author: dict[str, str]
) -> None:
    """Two pages, no overlap, and the cursor is opaque — the `GET /models` contract."""
    for _ in range(3):
        _create(client, author)
    first = client.get("/api/v1/custom-objectives?limit=2", headers=author)
    assert first.status_code == 200, first.text
    page_one = first.json()
    assert len(page_one["items"]) == 2 and page_one["next_cursor"]
    second = client.get(
        f"/api/v1/custom-objectives?limit=2&cursor={page_one['next_cursor']}",
        headers=author,
    )
    assert second.status_code == 200, second.text
    assert not (
        {row["id"] for row in page_one["items"]}
        & {row["id"] for row in second.json()["items"]}
    )
```

`_seed_model_referencing(objective_id, slug)` is the helper **Task 1 Step 2 writes** — a `_run`-
based insert of one `ModelRow` whose `spec` names the objective, mirroring `_copy_into`'s shape.
It is not a placeholder: if Task 1 has not landed it, write it here and move it in Task 1's commit.
`ObjectiveStatus`, `UUID` and `new_uuid7` are already imported by this module; `_seed_model_referencing`
is the only new name.

Match the fixture and helper signatures to what `:55-178` actually declares — `_create`'s keyword
for the slug, whether `_headers` takes an actor or an id, and the fixture name for the
no-permission actor at `:394-404`. This plan names them from a read of the file, not from having
run them.

- [ ] **Step 2: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_custom_objectives_api.py -k "library or slug_filter or status_filter or usage_count or boundary or cursor" -v
```
Expected: every one FAILS with 404 or 405 — there is no route.

- [ ] **Step 3: Decide where `usage_count` lives on the wire**

```bash
grep -rn "class CustomObjective\b\|class CustomObjectiveSummary" packages/model-schema/src/model_schema/
sed -n '148,192p' packages/model-schema/src/model_schema/datasets.py
```

The second is the precedent, and its shape is not the one the Architecture note guessed. The
dataset list computes **two** aggregates and passes **two** keywords —
`latest_version=latest.get(row.id)` and `last_validated=validated.get(row.id)`, not a single
`latest_version_status` scalar (`backend/src/app/api/datasets.py:329-343`), and `latest_version`
carries a tuple. What transfers is the pattern, not the name: aggregate once over the page's ids,
then pass the per-row lookup into `to_schema` as a keyword.

Do the same — add `usage_count: int = 0` to whichever schema the list row uses, with a docstring
saying it is a per-page aggregate and not stored. **Write the answer into this plan's Step 5
before writing Step 5's code**: the route below is drafted against `CustomObjectiveSummary`, which
is one of the two candidates this step is choosing between. If the grep finds no such class and
the right answer is `usage_count` on the existing `CustomObjective`, substitute it in the
`response_model`, the return annotation and Task 4's mirror — three sites, and a stale one type-checks
cleanly while returning the wrong shape.

**Do not hand-write a row shape in the router.** `CLAUDE.md` §2: nobody hand-writes a shape that
already exists in `model-schema`. If the detail route's schema is too heavy for a row, add a
summary model to `model-schema` rather than assembling dicts.

- [ ] **Step 4: Write the query**

In `backend/src/app/platform/objectives.py`, following the shape of `models.list_models`
(`backend/src/app/api/models.py:544-607`) — `order_by(Row.id.desc())`, `where(Row.id < after)` for
the cursor, `COUNT_CAP` for the total:

```python
async def list_objectives(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    status: ObjectiveStatus | None = None,
    slug: str | None = None,
    limit: int = DEFAULT_LIMIT,
    after: UUID | None = None,
) -> tuple[Sequence[CustomObjectiveRow], int | None]:
    """One page of the workspace's objectives (FR-MODEL-127).

    `ix_custom_objectives_slug_status` covers `(workspace_id, slug, status)`, so both filters
    are index-served and no migration accompanies this route.
    """
```

Return the rows and the capped total; let the router build the `Page`. Re-check RBAC here if the
module's other functions do — Step 3's grep of the neighbours will show it.

- [ ] **Step 5: Write the route**

Above the create at `custom_objectives.py:118`.

**Give the decorator the full path.** `custom_objectives.py:57` declares
`router = APIRouter(tags=["modelling"])` — **no `prefix`** — and every route in the module spells
its path out in full. `@router.get("")` would mount at `""`, not at the collection. The same holds
for the other two modules (`validation.py:56`, `models.py:102`), so Tasks 4 and 5 inherit it:

```python
@router.get(
    "/api/v1/custom-objectives",
    response_model=Page[CustomObjectiveSummary],
    responses=problems(400, 401, 403, 422),
    summary="List the workspace's custom objectives",
)
async def list_custom_objectives(
    caller: ReadModels,
    database: DatabaseDep,
    filters: Annotated[ObjectiveFilter, Query()],
) -> Page[CustomObjectiveSummary]:
    """The library `02` §5.3 renders (FR-MODEL-127).

    `usage_count` is one grouped aggregate over the page's refs, never one query per row —
    the budget is part of the requirement, not an optimisation.
    """
```

Body: decode the cursor, call `list_objectives`, build the page's refs as
`f"custom_objective:{row.slug}@{row.version}"`, call `objectives.usage_counts` once, then convert
each row with `usage_count=counts.get(ref, 0)`.

Declare `ObjectiveFilter` beside it, modelled on `ModelFilter` (`app/api/models.py:167-192`) and
`RuleFilter` (`app/api/validation.py:175-194`) — `status`, `slug`, `limit` with `MAX_LIMIT`,
`cursor`.

- [ ] **Step 6: Run the tests to verify they pass**

Run:
```bash
uv run pytest backend/tests/test_custom_objectives_api.py -v
```
Expected: PASS, **including the two pre-existing tests around `:366-368`**, which may assert the
count of registered routes.

- [ ] **Step 7: Correct the two comments this route falsifies**

`test_custom_objectives_api.py:14-17` is the module docstring: *"**There is no list route.** Seven
routes, and none of them lists."* And `:366-368` says the same in a test comment. Both were true
when written and are the observation FR-MODEL-127 was raised from.

Rewrite both to say what is now true and keep the history: eight routes, the eighth added by
FR-MODEL-127 on 2026-08-23, and the library screen `02` §5.3 specifies now has an endpoint. Do not
delete the sentences — the record of what was missing and for how long is the reason the
requirement exists.

**A third comment, and two more in Tasks 4 and 5.** Each of the three router modules opens with a
docstring listing its routes; adding one to a module without updating its own header leaves the
file disagreeing with itself on line 1. Run

```bash
head -40 backend/src/app/api/custom_objectives.py
head -40 backend/src/app/api/custom_metrics.py
head -40 backend/src/app/api/perils.py
```

and correct whichever of the three carries a route table or a count. This step covers
`custom_objectives.py`; Tasks 4 and 5 each repeat it for their own module.

- [ ] **Step 8: Commit**

```bash
git add backend/src/app/api/custom_objectives.py backend/src/app/platform/objectives.py
git add backend/tests/test_custom_objectives_api.py packages/model-schema/src
git commit -m "feat(w32-8): the custom objective library is listable"
```

---

### Task 3: `GET /api/v1/custom-metrics`

**Files:**
- Modify: `backend/src/app/api/custom_metrics.py` — a list route above the create
- Modify: `backend/src/app/platform/metrics.py` — `list_metrics`
- Test: `backend/tests/test_custom_metrics_api.py`

**Interfaces:**
- Consumes: `metrics.usage_counts` from Task 1; the `ObjectiveFilter` shape from Task 2 as the
  model to copy.
- Produces: `MetricFilter`, `list_metrics`, `list_custom_metrics`.

Same seven tests, same route shape, one real difference: the ref prefix is `custom_metric:` and the
aggregate is the lateral one. §5.1:1705 asks for `usage_count` here too.

- [ ] **Step 1: Write the failing tests**

Copy Task 2 Step 1's seven tests into `backend/tests/test_custom_metrics_api.py`, adapting the
path, the fixtures and the helper names to that module's own (check them —
`sed -n '1,120p' backend/tests/test_custom_metrics_api.py`). Add one test the objective side does
not need:

```python
@pytest.mark.req("FR-MODEL-127")
def test_a_model_naming_several_metrics_counts_against_each(api_client, author, database) -> None:
    """`eval_metrics` is an array, unlike `GbmSpec.objective`, which is a single ref.

    Named precisely: only `GbmSpec.objective` (`modelling.py:1321`) is a `GbmFunctionRef`.
    `EbmSpec.objective` (`:1427`) is `Literal["rmse", "mae"]` — a closed builtin set that
    can never name a custom artifact, so it contributes nothing to any usage count.

    One model naming three metrics is one use of each — not one use of the first, and not
    three uses of one. This is the case the lateral expansion exists for.
    """
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_custom_metrics_api.py -k "library or filter or usage_count or boundary or cursor or several_metrics" -v
```
Expected: all FAIL with 404 or 405.

- [ ] **Step 3: Write `list_metrics`**

In `backend/src/app/platform/metrics.py`, the same body as `list_objectives` against
`CustomMetricRow` and its status enum. Do not factor the two into a shared generic: they are
fifteen lines each over different tables with different status types, and the abstraction that
unified them would be harder to read than both.

- [ ] **Step 4: Write the route**

In `backend/src/app/api/custom_metrics.py`, mirroring Task 2 Step 5, with refs built as
`f"custom_metric:{row.slug}@{row.version}"` and `metrics.usage_counts`.

- [ ] **Step 5: Run the tests to verify they pass**

Run:
```bash
uv run pytest backend/tests/test_custom_metrics_api.py -v
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/src/app/api/custom_metrics.py backend/src/app/platform/metrics.py
git add backend/tests/test_custom_metrics_api.py packages/model-schema/src
git commit -m "feat(w32-8): the custom metric library is listable"
```

---

### Task 4: `GET /api/v1/peril-structures`

**Files:**
- Modify: `backend/src/app/api/peril_structures.py` — a list route above the create
- Modify: `backend/src/app/platform/perils.py` — `list_peril_structures`
- Test: `backend/tests/test_peril_structures_api.py`

**Interfaces:**
- Consumes: the filter and route shape from Tasks 2 and 3.
- Produces: `PerilStructureFilter`; `perils.list_peril_structures(...)` in `app/platform/perils.py`
  (the query); and the route function `list_peril_structures_route` in
  `app/api/peril_structures.py`. **Two different things must not share one name** — the router
  imports the platform function, and a route function shadowing it in the same module is an import
  the reader has to disambiguate. Tasks 2 and 3 avoid this by naming their routes
  `list_custom_objectives` and `list_custom_metrics` over `list_objectives` / `list_metrics`;
  follow that, not a literal copy.

**No `usage_count` here.** §5.1:1712 asks for pagination and the two filters and stops, while
:1697 and :1705 name the count. Build what the endpoint table says and let Task 5 raise the
discrepancy with FR-MODEL-127's unqualified prose. Add a comment on the route saying the omission
is deliberate and pointing at the open question, so the next reader finds a decision rather than a
gap.

- [ ] **Step 1: Write the failing tests**

Six tests — Task 2 Step 1's seven minus `test_each_row_carries_its_usage_count`. Add:

```python
@pytest.mark.req("FR-MODEL-127")
def test_the_row_carries_no_usage_count(api_client, author) -> None:
    """§5.1:1712 asks for pagination and two filters and no count, unlike its two siblings.

    Asserted rather than left implicit: the difference between the three rows is the open
    question Task 5 raises, and a row that silently grew a count would answer it by accident.
    """
    created = _create_peril_structure(client, author)
    response = client.get("/api/v1/peril-structures", headers=author)
    assert response.status_code == 200, response.text
    rows = {row["id"]: row for row in response.json()["items"]}
    assert "usage_count" not in rows[created["id"]]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_peril_structures_api.py -k "library or filter or boundary or cursor or usage_count" -v
```
Expected: FAIL with 404 or 405.

- [ ] **Step 3: Write the query and the route**

As Tasks 2 and 3, against `PerilStructureRow`, with no aggregate call.

- [ ] **Step 4: Run the tests to verify they pass**

Run:
```bash
uv run pytest backend/tests/test_peril_structures_api.py -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/api/peril_structures.py backend/src/app/platform/perils.py
git add backend/tests/test_peril_structures_api.py packages/model-schema/src
git commit -m "feat(w32-8): the peril structure library is listable"
```

---

### Task 5: Run the gate, record the two spec disagreements

**Files:**
- Modify: [`../specs/02-modelling.md`](../specs/02-modelling.md) §10 — two open questions mirrored
- Modify: [`../open-questions.md`](../open-questions.md) — the same two
- Modify: [`../roadmap.md`](../roadmap.md) — a slice record, appended
- Create: `2026-08-23-w32-8-artifact-library-list-routes-ledger.md`

**Interfaces:**
- Consumes: Tasks 1-4 complete and committed.

- [ ] **Step 1: Record the §5.3 disagreement**

FR-MODEL-127 opens *"The three artifact libraries **§5.3 renders** are listable."* §5.3
(`02-modelling.md:2545-2558`) contains **one** library view — `Custom objective library`
`/objectives` — plus a `Peril structure` **detail** view at `/peril-structures/{id}` and no
custom-metric view at all.

This is a spec-versus-spec disagreement, and `CLAUDE.md` §0 says resolve it rather than quietly
make either side match the other. Do not edit §5.3 to invent two views on this slice's authority.
Write the question with options: add the two missing §5.3 rows (making FR-MODEL-127's sentence
true and giving `W6b` two more screens to build); or amend FR-MODEL-127's wording to say the three
libraries §5.1 exposes, of which §5.3 renders one. Recommend the first — three list endpoints whose
data only one screen consumes is the same asymmetry in the other direction — and name the owner.

- [ ] **Step 2: Record the `usage_count` asymmetry**

FR-MODEL-127's prose says *"`usage_count` is on the row, as §5.3 asks"* without qualifying which
rows, and §5.3's one library view does ask for a usage count. But §5.1 puts the field on objectives
(`:1697`) and metrics (`:1705`) and not on peril structures (`:1712`).

Both readings are defensible: a Peril Structure is referenced by Model Specs differently from an
objective, so the omission may be deliberate. Record the question, note that Task 4 built the
endpoint table's reading and asserted the absence, and recommend whichever the reference direction
supports after checking how a `ModelSpec` names a peril structure — state that check as part of
the question rather than performing it as a decision here.

- [ ] **Step 3: Run the Python half of the gate**

```bash
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
```
Expected: every command exits 0. `generate-contracts.py --check` **will** report drift here rather
than might: three new operations and a new schema field both land in
`docs/contracts/openapi/generated.json`, and the `usage_count` field also lands in the generated
schema beside it. Run without `--check`, commit everything under `docs/contracts/`, then re-run
with it. Do not hand-edit either file (`CLAUDE.md` §2).

Two audit traps: an open question must be mirrored in both `open-questions.md` and the module
spec's §10 or check 7 fails; and a bolded audit anchor phrase inside a table row breaks check 10,
so write "the §5.1 endpoint rows" rather than the bolded form.

- [ ] **Step 4: Run the frontend half**

Three new operations change the OpenAPI document, so the client regenerates.

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build
```
Expected: every command exits 0.

- [ ] **Step 5: Write the ledger and the slice record**

Create `docs/plans/2026-08-23-w32-8-artifact-library-list-routes-ledger.md`: the real gate output,
the Task 1 Step 8 N+1 proof and its failure message, the answers Task 1 Step 1 found about the
existing `usage` functions, and every place this plan named a fixture or attribute that turned out
to be called something else.

Give FR-MODEL-127 a §13 verdict: *delivered and tested* if all three routes and the budget test
landed, with the two open questions listed as the parts it left unresolved.

Append the slice record to [`../roadmap.md`](../roadmap.md), following the W32-6 record's shape.

- [ ] **Step 6: Commit**

```bash
git add docs/
git commit -m "docs(w32-8): record the artifact library slice and its two spec disagreements"
```
