---
id: PL-804
family: plan
kind: leaf
title: W6b-12 — Dataset Lineage Graph Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-26
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-26-w6b-12-dataset-lineage.md
---

# W6b-12 — Dataset Lineage Graph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `GET /api/v1/dataset-versions/{id}/lineage` answer FR-75 in the shape
`01` §4.9 has defined for it since 2026-08-23 — replacing the untyped `dict[str, Any]`
handler and the three defects its typing note names — and render that answer as the lineage
graph `01` §5.3's Dataset detail Contents cell has obligated since 2026-08-15.

**Architecture:** The shape enters `model-schema` and is generated into the contract like
every other response (FR-451); the DATA service's `lineage_of` returns the typed data
arms it owns (`built_from`, `derived_versions`); a new modelling-service function supplies
the `models` arm; the router — where the modules meet (DEP-1) — assembles the §4.9 shape and
applies the direction filter's emptying semantics. The frontend's dead `getLineage()` gains
a typed response and a caller: a small ECharts graph with the mandated `ChartFigure` tabular
equivalent (NFR-463), in the Dataset detail view.

**Tech Stack:** Pydantic v2 in `model-schema` (frozen, `extra="forbid"`), FastAPI return
annotations, SQLAlchemy 2.x async, `scripts/generate-contracts.py` + `openapi-typescript`;
Vue 3 Composition API with `<script setup lang="ts">`, vue-echarts, Vitest +
`@testing-library/vue`.

**Spec:** [`../specs/01-data-management.md`](../specs/01-data-management.md) — §4.9
`DatasetLineage` (`:771-807`, its definition and invariants), FR-75 (`:186`),
FR-76 (`:187`), FR-53 (`:115`), the §5.1 lineage row (`:846`, whose P3 amendment
record is the slice's scope statement), and §5.3's Dataset detail row (`:982`).

**Slice source:** [`PL-00786-wk-664-the-revised-slice-map.md`](PL-00786-wk-664-the-revised-slice-map.md)
§3, line 161 — *"Lineage graph — plus the typed handler and the three defects moved here
from `W6b-13`"*, under proposal **P3**, decided 2026-08-25 in `8d778ed` (PR #231): the
`01:846` clause is kept verbatim, the reassignment is the dated note appended to it,
`DatasetLineage` is spec-only (§4.9 is its definition, no wire shape exists to hand-write),
and **typing the handler is `W6b-12`'s primary work, not a fourth defect**.

**Highest ids in use, verified at `845f298` by scanning
[`../specs/01-data-management.md`](../specs/01-data-management.md) and
[`../open-questions.md`](../open-questions.md):** FR-58, NFR-474, OQ-570.
Next free: `FR-59`, `NFR-DATA-11`, `OQ-DATA-16`.
**This plan mints none of them** — it cites FR-75, which already states the rule, and
delivers a §5.3 Contents item, which is an obligation because the row exists, not because a
requirement names it. The line is published because the revised slice map's equivalent
(*"Next free: `FR-57`"*, `beba1ae` #166) is now two ids stale, and a stale allocation
aid is what mints a colliding id.

## Global Constraints

- **Nobody hand-writes a shape that already exists in `model-schema`**
  ([`../../CLAUDE.md`](../../CLAUDE.md) §2 and §3). `DatasetLineage` is spec-only today —
  `packages/model-schema/` and `docs/contracts/` hold no trace of it, verified by sweep at
  `845f298` — so this slice's first task is to define it there, from §4.9's example and
  invariants, before any backend or frontend code types against it.
- **`01` §4.9's invariants are the contract.** Every field is present in every response;
  a direction filter **empties the arm it excludes rather than omitting it** (`direction=up`
  returns `depends_on_this` with four empty arms, `direction=down` returns
  `built_from: null`); `rating_versions` and `monitoring_baselines` are declared and always
  empty (WK-669's and WK-687's); the response is assembled where the modules meet, not inside the
  DATA service.
- **DEP-1 (ADR-703) forbids a module importing from its right.** `app.platform.datasets`
  must not import `app.platform.modelling` — and cannot, without a circular import, because
  `backend/src/app/platform/modelling.py:36` already imports `app.platform.datasets`. The
  models arm reaches the response through the router.
- **Never hand-write an API type in the frontend.** Shapes come from
  `frontend/src/api/generated`, which is VCS-ignored and therefore **cannot be cited as
  evidence** — cite `docs/contracts/openapi/generated.json`, which is committed, instead.
- **Vue 3 Composition API with `<script setup lang="ts">` only.** No Options API, no JSX.
- **A chart is a canvas plus a table** (NFR-463, `00-overview.md:520`): every chart the
  slice adds renders through `ChartFigure`, whose table is always in the DOM.
- **Both halves of the gate must pass locally before pushing**
  ([`../../CLAUDE.md`](../../CLAUDE.md) §11). A Python-only run is not a gate run for a
  slice that touches the frontend.

---

## Findings the plan is built on

Each was verified against shipped source at `845f298`. They are recorded here rather than
only in the PR body because three of them are the three defects `01:846` already names, and
the plan must be checkable against them one by one.

### Finding 1 — the `direction` filter tests for keys nothing has ever produced (defect 1)

`backend/src/app/api/dataset_versions.py:384-387`:

```python
    if direction == "up":
        return {key: value for key, value in graph.items() if key != "descendants"}
    if direction == "down":
        return {key: value for key, value in graph.items() if key != "ancestors"}
```

`lineage_of` emits `version_id`, `built_from` and `depends_on_this` — never `descendants` or
`ancestors` — so both filters are identities and `direction` is dead on arrival. The §4.9
semantics the filter was reaching for are different and are stated in its invariants: the
excluded arm is **emptied, not removed**. Task 4 replaces the filter with the invariant.

### Finding 2 — `depends_on_this` is a flat list, and becomes §4.9's named object (defect 2)

`backend/src/app/platform/datasets.py:882-884`:

```python
        "depends_on_this": [
            {"version_id": str(c.id), "version": c.version,
             "operation": (c.derived_from or {}).get("operation")}
            for c in children
        ],
```

The wire today is a list; §4.9 defines an object with four arms (`derived_versions`,
`models`, `rating_versions`, `monitoring_baselines`). This is a breaking wire change, and
`01:846` records that it is safe because `getLineage` is exported and called by no view —
re-verified at `845f298`: `frontend/src/api/datasets.ts:63-65` is the only definition, and a
repo-wide sweep finds zero call sites. Tasks 2 and 4 make the change; Task 5 creates the
first caller.

### Finding 3 — the only FR-75 evidence marker reads the old shape (defect 3)

`backend/tests/test_lineage.py:305-328` is the only `@pytest.mark.req("FR-75")` marker
in the repository (verified by sweep: `scripts/req-coverage.py:51` reads
`@pytest.mark.req(...)` markers by regex over every test path; the hit is unique). Its
assertions are dict-shaped:

```python
    assert upstream["built_from"]["parent_version_id"] == str(parent_id)
    assert [d["version_id"] for d in downstream["depends_on_this"]] == [str(child_id)]
    assert downstream["built_from"]["parent_version_id"] is None
```

`01:846` requires the test to be **rewritten in the same commit** as the typing — it is the
only evidence the coverage script sees, so a commit that breaks it without rewriting it
deletes FR-75's evidence. Task 2 rewrites it in the same commit as the service change
that breaks it.

### Finding 4 — the current `built_from` serves two fields §4.9 does not define, and omits one it does

`lineage_of`'s `built_from` (`platform/datasets.py:876-880`) carries `parent_version_id`,
`operation`, `ingestion_run_id` and `source_id`. §4.9's example defines exactly
`parent_version_id`, `operation` and `parameters` — and the third is available in the data:
`derive_version` writes `derived_from={"parent_version_id": ..., "operation": ...,
"params": params}` at `platform/datasets.py:820-823`, and no read path ever returns `params`
back out. The typed wire follows §4.9 — that is the point of the slice — so `ingestion_run_id`
and `source_id` leave the response and `parameters` enters it, read from
`derived_from["params"]` with a `{}` default. Nothing reads either departing field: the
response has no callers (Finding 2), and the raw `derived_from` column stays available to
anyone who needs the run id (`api/datasets.py:694` returns it unchanged).

### Finding 5 — the models arm is scoped by nothing in the spec; every status counts

FR-75 (`01:186`) says "what depends on this?" spans Models, Rating Versions and
Monitoring baselines, "used to compute the blast radius of FR-53" (`01:115` — a
re-validation that flags *every* Model fitted on the version). Neither FR-53 nor §4.9's
invariants scope model statuses; §4.9's example shows `"status": "approved"` and that is a
sample value, not a filter. The arm therefore lists **every** Model whose
`dataset_version_id` is the queried version, any status — a draft model still references
the version it was fitted on. The query §4.9 needs already has its index:
`db/models.py:1385` `ix_models_dataset_version ("workspace_id", "dataset_version_id")`.

### Finding 6 — where the modules meet has a live precedent

`backend/src/app/api/approvals.py:43` and `:45` import `app.platform.datasets` and
`app.platform.modelling` side by side, and the decide flow calls both. The API layer sits
above both modules, so assembling the §4.9 response there violates no layer rule —
`.importlinter`'s `layering` contract (`app / pricing_core / model_schema`) forbids only
upward imports, and `app.api → app.platform.modelling` is already live at
`api/models.py:68`. Task 4's handler is the assembly point.

### Finding 7 — the two roadmap rows that record the lineage gap are stale in the count but not in the item

`docs/roadmap.md:1774`'s *"Six §5.3 Contents items"* row still says *"four remain"* — a
count that predates the W6b-13 threshold delivery announced in the same row, and W6b-3's
delivery of the status/validated/owner columns (`#200`, `cdb9f9d`). `:3295`'s *"the other
two remain"* has the same second side. After this slice the row reads: **all six delivered,
the lineage graph last**. Task 6 corrects both rows with dated notes — a note appended,
never the clause rewritten, per the rule that governs an owner clause. The executor verifies
the row text at execution time before amending.

### Finding 8 — the view renders for the newest version, not per version

`01` §5.3's Dataset detail Contents cell (`:982`) names the lineage graph as one item of the
Dataset detail view; it does not specify which version's graph. The view already loads the
version timeline newest first (`frontend/src/views/DatasetDetailView.vue:35-49`), so the
graph renders for the first row of the first page — the newest version — and the section
hides when the dataset has no versions. Per-version lineage navigation (a link on each
timeline row) is deliberately out of scope: it multiplies the UI surface without adding an
obligation the Contents cell states. Recorded here so the executor does not pick it up
silently.

---

## Out of scope

**The model-detail lineage strip.** `02` §5.3's Model detail row names a "lineage strip" —
FR-203's `parent_model_id` refit lineage. That is a different lineage, on a different
endpoint, and is not this slice's. This slice touches only `01` §4.9's dataset-version
lineage.

**The `rating_versions` and `monitoring_baselines` arms.** Declared and always empty by
§4.9; WK-669 and WK-687 own them. This slice types them `list[Any]` and never populates them.

**FR-79's access scoping.** The handler already refuses callers without read access
(`_scoped`); the slice keeps that and extends nothing.

**The raw `derived_from` exposure** at `api/datasets.py:694` — the stored column, not the
§4.9 wire. Untouched.

**`semantic_type` read-only and the unrendered `unit`/`reference_table`** — recorded in the
same roadmap row (`:1704`) as separate gaps; unrelated to lineage.

**Per-version lineage navigation** — Finding 8.

## File Structure

| File | Change | Responsible for |
|---|---|---|
| `packages/model-schema/src/model_schema/datasets.py` | Modify (after `DatasetVersion`; `__all__`) | The five §4.9 classes |
| `packages/model-schema/tests/test_dataset_lineage.py` | Create | The shape, from §4.9's example |
| `scripts/generate-contracts.py` | Modify (`GENERATED_SHAPES`) | `dataset-lineage` schema file |
| `docs/contracts/` | Regenerate | Committed contract, drift-checked in CI |
| `backend/src/app/platform/datasets.py` | Modify `:851-886` | `lineage_of` returns the typed data arms |
| `backend/src/app/platform/modelling.py` | Modify (near `load_model` `:841`; `model_schema` import `:37`) | `models_referencing_version` |
| `backend/src/app/api/dataset_versions.py` | Modify `:369-388`, imports `:40-51` | The typed handler; assembly; direction semantics |
| `backend/tests/test_lineage.py` | Modify `:305-328`, add tests | The FR-75 rewrite; models arm; direction semantics |
| `frontend/src/api/datasets.ts` | Modify `:63-65` | Typed `getLineage`, `DatasetLineage` alias |
| `frontend/src/components/LineageGraph.vue` | Create | The graph and its `ChartFigure` table |
| `frontend/src/components/__tests__/LineageGraph.test.ts` | Create | The table, chart mocked |
| `frontend/src/views/DatasetDetailView.vue` | Modify | The Lineage section |
| `frontend/src/views/__tests__/DatasetDetailView.test.ts` | Modify | The section, in the fetch stub |
| `docs/roadmap.md` | Modify `:1704`, `:1774`, `:3295` | Dated delivery notes; corrected counts |

### Task 1: The `DatasetLineage` shape, in `model-schema`

**Files:**
- Modify: `packages/model-schema/src/model_schema/datasets.py`
- Modify: `scripts/generate-contracts.py:38` (`GENERATED_SHAPES`)
- Test: `packages/model-schema/tests/test_dataset_lineage.py` (create)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces — the wire vocabulary every later task types against (names fixed here, used
  verbatim in Tasks 2-5): `DatasetLineage` with fields `version_id: UUID`,
  `built_from: LineageBuiltFrom | None`, `depends_on_this: LineageDependsOn`;
  `LineageBuiltFrom(parent_version_id: UUID, operation: str, parameters: dict[str, Any])`;
  `LineageDerivedVersion(version_id: UUID, version: int, operation: str)`;
  `LineageModel(model_id: UUID, slug: str, status: str)`; `LineageDependsOn(derived_versions,
  models, rating_versions, monitoring_baselines)` — the last two `list[Any]`, declared and
  always empty (§4.9: WK-669's and WK-687's).

- [ ] **Step 1: Write the failing test**

Create `packages/model-schema/tests/test_dataset_lineage.py`:

```python
"""`01` §4.9's DatasetLineage — the wire form of FR-75, defined here first."""

import pytest
from pydantic import ValidationError

from model_schema.datasets import (
    DatasetLineage,
    LineageBuiltFrom,
    LineageDependsOn,
    LineageDerivedVersion,
    LineageModel,
)

# The example JSON from `01` §4.9 (`:777-782`), verbatim apart from concrete ids.
EXAMPLE = {
    "version_id": "11111111-1111-4111-8111-111111111111",
    "built_from": {
        "parent_version_id": "22222222-2222-4222-8222-222222222222",
        "operation": "sample",
        "parameters": {},
    },
    "depends_on_this": {
        "derived_versions": [
            {"version_id": "33333333-3333-4333-8333-333333333333", "version": 3,
             "operation": "split"},
        ],
        "models": [
            {"model_id": "44444444-4444-4444-8444-444444444444",
             "slug": "motor-freq-2026", "status": "approved"},
        ],
        "rating_versions": [],
        "monitoring_baselines": [],
    },
}


def test_the_spec_example_round_trips() -> None:
    """§4.9's example is a claim about the wire: parse it, emit it, get it back."""
    parsed = DatasetLineage.model_validate(EXAMPLE)
    assert parsed.model_dump(mode="json") == EXAMPLE
    assert parsed.built_from == LineageBuiltFrom(
        parent_version_id="22222222-2222-4222-8222-222222222222",
        operation="sample",
        parameters={},
    )
    assert parsed.depends_on_this.derived_versions == [
        LineageDerivedVersion(
            version_id="33333333-3333-4333-8333-333333333333", version=3, operation="split"
        )
    ]
    assert parsed.depends_on_this.models == [
        LineageModel(
            model_id="44444444-4444-4444-8444-444444444444",
            slug="motor-freq-2026",
            status="approved",
        )
    ]


def test_built_from_is_nullable_for_a_root_version() -> None:
    """§4.9: `direction=down` returns `built_from: null` — and a version with no
    parent has no `built_from` in any direction."""
    root = {**EXAMPLE, "built_from": None}
    assert DatasetLineage.model_validate(root).built_from is None


def test_the_declared_empty_arms_are_present_and_empty() -> None:
    """§4.9: a key that appears and disappears is a second shape. Both arms are
    always on the wire, so a blast radius cannot silently read as one of one."""
    parsed = DatasetLineage.model_validate({**EXAMPLE, "depends_on_this": {
        "derived_versions": [],
        "models": [],
        "rating_versions": [],
        "monitoring_baselines": [],
    }})
    dumped = parsed.model_dump(mode="json")
    assert dumped["depends_on_this"]["rating_versions"] == []
    assert dumped["depends_on_this"]["monitoring_baselines"] == []


def test_the_shape_is_closed_and_frozen() -> None:
    """A shape defined twice diverges (CLAUDE.md §2): the wire refuses both a stray
    key and a missing one, and no caller can mutate a parsed response."""
    with pytest.raises(ValidationError):
        DatasetLineage.model_validate({**EXAMPLE, "surprise": 1})
    with pytest.raises(ValidationError):
        DatasetLineage.model_validate({**EXAMPLE, "built_from": {
            "parent_version_id": "22222222-2222-4222-8222-222222222222"}})
    parsed = DatasetLineage.model_validate(EXAMPLE)
    with pytest.raises(TypeError):
        parsed.version_id = "55555555-5555-4555-8555-555555555555"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest packages/model-schema/tests/test_dataset_lineage.py -v`
Expected: FAIL at collection — `ImportError: cannot import name 'DatasetLineage'` from
`model_schema.datasets`. That is the discriminator: a failure naming the missing names is
the shape being absent; a failure with a different cause is a defect in the test or the
import path, and must be resolved before proceeding.

- [ ] **Step 3: Define the five classes**

Append to `packages/model-schema/src/model_schema/datasets.py`, after the `DatasetVersion`
class (near `:272`):

```python
class LineageBuiltFrom(BaseModel):
    """The version this one was built from, and the operation that built it (`01` §4.9).

    `None` on the wire when the version has no parent — a version an Ingestion Run
    created from a Source, and any `direction=down` response (§4.9's invariants).
    `parameters` is the derivation's parameters, read back from the parent's
    `derived_from["params"]`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    parent_version_id: UUID
    operation: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class LineageDerivedVersion(BaseModel):
    """A version derived from this one (`01` §4.9's `derived_versions` arm)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version_id: UUID
    version: int
    operation: str


class LineageModel(BaseModel):
    """A Model fitted on this version (`01` §4.9's `models` arm).

    Any status: a draft Model still references the version it was fitted on, and the
    blast radius FR-75 exists to compute (FR-53) does not stop at approval.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: UUID
    slug: str
    status: str


class LineageDependsOn(BaseModel):
    """What depends on this version (`01` §4.9).

    `rating_versions` and `monitoring_baselines` are declared and always empty — WK-669's
    and WK-687's arms, kept on the wire so a blast radius that silently omits two of the
    three downstream kinds cannot read as a blast radius of one (FR-75).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    derived_versions: list[LineageDerivedVersion] = Field(default_factory=list)
    models: list[LineageModel] = Field(default_factory=list)
    rating_versions: list[Any] = Field(default_factory=list)
    monitoring_baselines: list[Any] = Field(default_factory=list)


class DatasetLineage(BaseModel):
    """The lineage graph for one Dataset Version (`01` §4.9, FR-75)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version_id: UUID
    built_from: LineageBuiltFrom | None
    depends_on_this: LineageDependsOn
```

Add the five names to `__all__` in the same file. Check the file's existing class
definitions first: if `model_config` is spelled as a class attribute exactly as above in
the neighbouring classes, mirror that; if the file uses a shared base or a different
ConfigDict pattern, follow the file's own convention — the point is the frozen-closed wire,
not the spelling.

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest packages/model-schema/tests/test_dataset_lineage.py -v`
Expected: PASS (4 passed). A passing run here means the shape parses §4.9's example
byte-for-byte — the definition the plan's later tasks assume.

- [ ] **Step 5: Publish the generated schema**

In `scripts/generate-contracts.py:38` (`GENERATED_SHAPES`), add an entry with the same
comment style as its neighbours:

```python
    # Added 2026-08-26 (W6b-12). **No hand-authored Phase-0 counterpart** — `01` §4.9 is
    # the shape's first written form, defined in the spec before any code, and the
    # generated file is the only place a consumer can see the wire form.
    "dataset-lineage": "DatasetLineage",
```

Then regenerate and inspect the drift:

Run: `uv run python scripts/generate-contracts.py`
Run: `git diff --stat docs/contracts/`
Expected: `docs/contracts/schemas/generated/dataset-lineage.schema.json` is created;
`docs/contracts/openapi/generated.json` is unchanged (the endpoint still returns an untyped
dict until Task 4). If `generated.json` changed, stop: the handler is not the only thing
the shape touches — find what else changed before committing.

- [ ] **Step 6: Run the docs audit**

Run: `python3 scripts/audit-docs.py`
Expected: PASS (check 2 reads `docs/plans/`; check 4 reads every `ADR-NNNN` cited; the new
schema file must not trip a check).

- [ ] **Step 7: Commit**

```bash
git add packages/model-schema/src/model_schema/datasets.py \
  packages/model-schema/tests/test_dataset_lineage.py \
  scripts/generate-contracts.py docs/contracts/
git commit -m "feat(w6b-12): the DatasetLineage shape, from 01 §4.9's definition"
```

### Task 2: `lineage_of` returns the typed data arms

**Files:**
- Modify: `backend/src/app/platform/datasets.py:851-886`
- Modify: `backend/tests/test_lineage.py:305-328` (the FR-75 rewrite, same commit)

**Interfaces:**
- Consumes: `DatasetLineage`, `LineageBuiltFrom`, `LineageDerivedVersion`,
  `LineageDependsOn` (Task 1).
- Produces: `lineage_of(session, *, workspace_id, version_id) -> DatasetLineage` — the
  data arms populated (`built_from` null when the version has no parent, `derived_versions`
  listing every workspace child), `models`/`rating_versions`/`monitoring_baselines` empty.
  The router (Task 4) fills `models`; the last two are never filled by anyone (WK-669, WK-687).

- [ ] **Step 1: Rewrite the FR-75 test to the typed shape — before the service changes**

In `backend/tests/test_lineage.py`, replace the body of
`test_lineage_answers_both_directions` (from the `async with database.session()` block at
`:313` down to the final assertion) with:

```python
    async with database.session() as session:
        upstream = await datasets.lineage_of(
            session, workspace_id=workspace_id, version_id=child_id
        )
        downstream = await datasets.lineage_of(
            session, workspace_id=workspace_id, version_id=parent_id
        )

    assert upstream.built_from is not None
    assert upstream.built_from.parent_version_id == parent_id
    assert upstream.built_from.operation == "split"
    assert upstream.built_from.parameters == {"part": "train", "seed": 1}
    assert upstream.depends_on_this.derived_versions == []
    assert [d.version_id for d in downstream.depends_on_this.derived_versions] == [child_id]
    assert [d.operation for d in downstream.depends_on_this.derived_versions] == ["split"]
    assert downstream.built_from is None
```

The test's setup derives the child with `params={"part": "train", "seed": 1}` and
`operation="split"` (verified at `845f298`) — the assertions above are the §4.9 wire read
back from exactly that. `parent_id` and `child_id` are already UUIDs; the dict-shaped
`str(...)` comparisons go away with the dict. Keep `@pytest.mark.req("FR-75")` and the
test's docstring.

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest backend/tests/test_lineage.py::test_lineage_answers_both_directions -v`
Expected: FAIL — `AttributeError: 'dict' object has no attribute 'built_from'` (the service
still returns a dict). The cause is named in the error; a different error is a defect in
the rewrite.

- [ ] **Step 3: Type `lineage_of`**

Replace the body of `lineage_of` (`platform/datasets.py:851-886`) with:

```python
async def lineage_of(
    session: AsyncSession, *, workspace_id: UUID, version_id: UUID
) -> DatasetLineage:
    """What this was built from, and what was built from it (FR-75).

    Both directions, because they answer different questions. "What was this built from?"
    defends a model; "what depends on this?" is what someone asks before archiving a
    version, and getting it wrong means discovering the dependency when a rating version
    stops resolving.

    Returns the `01` §4.9 shape with the arms this service owns populated — `built_from`
    and `derived_versions`. The `models` arm is the modelling module's and is filled by
    the router, where the modules meet (DEP-1); `rating_versions` and
    `monitoring_baselines` are WK-669's and WK-687's and stay empty. A version with no parent
    has `built_from: null` in every direction (§4.9's invariants).
    """
    row = await load_version(session, workspace_id=workspace_id, version_id=version_id)

    children = (
        await session.execute(
            select(DatasetVersionRow).where(
                DatasetVersionRow.workspace_id == workspace_id,
                DatasetVersionRow.derived_from["parent_version_id"].astext
                == str(version_id),
            )
        )
    ).scalars().all()

    built_from: LineageBuiltFrom | None = None
    parent_id = (row.derived_from or {}).get("parent_version_id")
    if parent_id is not None:
        built_from = LineageBuiltFrom(
            parent_version_id=parent_id,
            operation=(row.derived_from or {}).get("operation"),
            parameters=(row.derived_from or {}).get("params") or {},
        )
    return DatasetLineage(
        version_id=version_id,
        built_from=built_from,
        depends_on_this=LineageDependsOn(
            derived_versions=[
                LineageDerivedVersion(
                    version_id=c.id,
                    version=c.version,
                    operation=(c.derived_from or {}).get("operation"),
                )
                for c in children
            ]
        ),
    )
```

The children query above is the one already in the function — keep the existing
`select`/`.astext` form the function uses today rather than inventing a second spelling.
Add `DatasetLineage`, `LineageBuiltFrom`, `LineageDerivedVersion`, `LineageDependsOn` to
the file's `model_schema` import block. The two fields the old dict served that §4.9 does
not define — `ingestion_run_id` and `source_id` — leave the wire here (Finding 4); the raw
`derived_from` column still carries them.

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest backend/tests/test_lineage.py -q`
Expected: PASS. The rewritten marker still carries `@pytest.mark.req("FR-75")`, so
the coverage script's single FR-75 evidence marker survives the commit that breaks
its old shape — defect 3 closed.

- [ ] **Step 5: Commit — the test and the service change in one commit**

```bash
git add backend/src/app/platform/datasets.py backend/tests/test_lineage.py
git commit -m "feat(w6b-12): lineage_of returns 01 §4.9's typed shape, parameters included"
```

### Task 3: The models arm

**Files:**
- Modify: `backend/src/app/platform/modelling.py` (new function beside `load_model` `:841`;
  `LineageModel` into the `model_schema` import at `:37`)
- Modify: `backend/tests/test_lineage.py` (`ModelRow` into the `app.db.models` import;
  the arm test)

**Interfaces:**
- Consumes: `LineageModel` (Task 1); `ModelRow` (`db/models.py:1319-1390`, fields `id`
  `:1326`, `workspace_id` `:1327`, `model_family_slug` `:1328`, `version` `:1329`, `status`
  `:1330`, `dataset_version_id` `:1331`; the arm's index `ix_models_dataset_version`
  `:1385`).
- Produces: `models_referencing_version(session, *, workspace_id, dataset_version_id) ->
  list[LineageModel]` — every Model fitted on the version, any status, ordered by
  `(model_family_slug, version)` so the wire is deterministic. The router calls it
  (Task 4); the DATA service must not (Finding 6, DEP-1).

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_lineage.py`, after the rewritten
`test_lineage_answers_both_directions`:

```python
@pytest.mark.req("FR-75")
async def test_the_models_arm_lists_every_model_on_the_version(
    database: Database, workspace_id
) -> None:
    """`01` §4.9's `models` arm: every Model whose `dataset_version_id` is this
    version, any status, deterministic order. The blast radius FR-53 computes
    does not stop at approval."""
    actor = await _with_role(database, workspace_id, "analyst")
    _, version_id = await _version(database, workspace_id, actor)
    async with database.unit_of_work() as session:
        session.add(
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug="motor-freq-2026",
                status="approved",
                dataset_version_id=version_id,
                spec={"family": "glm", "response": "claim_count"},
                spec_hash=f"v1:sha256:{'0' * 64}",
            )
        )
        session.add(
            ModelRow(
                workspace_id=workspace_id,
                model_family_slug="motor-freq-2026",
                status="draft",
                version=2,
                dataset_version_id=version_id,
                spec={"family": "glm", "response": "claim_count"},
                spec_hash=f"v1:sha256:{'1' * 64}",
            )
        )

    async with database.session() as session:
        from app.platform import modelling as modelling_service

        arm = await modelling_service.models_referencing_version(
            session, workspace_id=workspace_id, dataset_version_id=version_id
        )

    assert [(m.slug, m.status) for m in arm] == [
        ("motor-freq-2026", "approved"),
        ("motor-freq-2026", "draft"),
    ]
```

Add `ModelRow` to the file's existing `from app.db.models import (...)` block — check
whether `ModelRow` is already imported there before adding a duplicate. The in-test
`from app.platform import modelling as modelling_service` import keeps this task's first
commit self-contained; if the file already imports `modelling` at the top, use that
instead.

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest backend/tests/test_lineage.py::test_the_models_arm_lists_every_model_on_the_version -v`
Expected: FAIL with `AttributeError: module 'app.platform.modelling' has no attribute
'models_referencing_version'` — the missing name is the discriminator; any other failure
is a defect in the fixture or the insert.

- [ ] **Step 3: Implement the function**

In `backend/src/app/platform/modelling.py`, beside `load_model` (`:841`), add:

```python
async def models_referencing_version(
    session: AsyncSession, *, workspace_id: UUID, dataset_version_id: UUID
) -> list[LineageModel]:
    """Every Model fitted on this Dataset Version (`01` §4.9's `models` arm).

    Any status — a draft Model still references the version it was fitted on, and the
    blast radius FR-75 exists to compute (FR-53) does not stop at approval.
    The `ix_models_dataset_version` index serves the query. Owned by this module, not
    the DATA service's: DEP-1 forbids DATA importing MODEL, so the router assembles
    this arm into the lineage response where the modules meet.
    """
    rows = (
        await session.execute(
            select(ModelRow)
            .where(
                ModelRow.workspace_id == workspace_id,
                ModelRow.dataset_version_id == dataset_version_id,
            )
            .order_by(ModelRow.model_family_slug, ModelRow.version)
        )
    ).scalars().all()
    return [
        LineageModel(model_id=row.id, slug=row.model_family_slug, status=row.status)
        for row in rows
    ]
```

Add `LineageModel` to the file's `from model_schema import (...)` block (`:37`).
`select` is already imported at `:24`.

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest backend/tests/test_lineage.py -q`
Expected: PASS (the new test and the rewritten FR-75 test). The ordering assertion
is the point: `approved` before `draft` is `(slug, version)` order, not insertion order.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/platform/modelling.py backend/tests/test_lineage.py
git commit -m "feat(w6b-12): the models arm — every model on the version, any status"
```

### Task 4: The typed handler — assembly and the direction semantics

**Files:**
- Modify: `backend/src/app/api/dataset_versions.py:369-388` and the imports at `:40-51`
- Modify: `backend/tests/test_lineage.py` (the API-level direction tests)
- Regenerate: `docs/contracts/` (the OpenAPI response becomes `DatasetLineage`)

**Interfaces:**
- Consumes: `DatasetLineage`, `LineageDependsOn` (Task 1); `lineage_of` (Task 2);
  `models_referencing_version` (Task 3).
- Produces: the `GET /dataset-versions/{id}/lineage` response — `DatasetLineage` on the
  wire, direction semantics per §4.9's invariants. This is the commit that closes
  defects 1 and 2 at the API boundary.

- [ ] **Step 1: Write the failing API-level test**

Append to `backend/tests/test_lineage.py`:

```python
def test_the_direction_filter_empties_the_excluded_arm(
    api_client: TestClient, workspace_id, principal, actuary, database
) -> None:
    """`01` §4.9: a direction filter empties the arm it excludes rather than omitting
    it — `up` returns `depends_on_this` with four empty arms, `down` returns
    `built_from: null`."""
    loop = asyncio.get_event_loop()
    actor = loop.run_until_complete(_with_role(database, workspace_id, "analyst"))
    _, parent_id = loop.run_until_complete(_version(database, workspace_id, actor))
    child_id = loop.run_until_complete(
        _derive_child(database, workspace_id, actor, parent_id)
    )

    up = api_client.get(
        f"/api/v1/dataset-versions/{child_id}/lineage?direction=up", headers=actuary
    ).json()
    assert up["built_from"]["parent_version_id"] == str(parent_id)
    assert up["depends_on_this"] == {
        "derived_versions": [],
        "models": [],
        "rating_versions": [],
        "monitoring_baselines": [],
    }

    down = api_client.get(
        f"/api/v1/dataset-versions/{child_id}/lineage?direction=down", headers=actuary
    ).json()
    assert down["built_from"] is None
    assert down["depends_on_this"]["derived_versions"] == []

    both = api_client.get(
        f"/api/v1/dataset-versions/{child_id}/lineage", headers=actuary
    ).json()
    assert both["built_from"]["parent_version_id"] == str(parent_id)
    assert [d["version_id"] for d in both["depends_on_this"]["derived_versions"]] == []
    assert both["depends_on_this"]["models"] == []
```

with the helper, placed beside `_version`:

```python
async def _derive_child(database: Database, workspace_id, actor, parent_id):
    async with database.unit_of_work() as session:
        child = await datasets.derive_version(
            session, workspace_id=workspace_id, actor=actor,
            parent_version_id=parent_id, operation="split",
            params={"part": "train", "seed": 1},
        )
        return child.id
```

The file is currently service-level async; the fixtures this test needs are shared: the
`actuary` fixture pattern and its `_headers` import (`from backend.tests.test_api_datasets
import _headers`) come from `backend/tests/test_api_acknowledge.py:70-77`; `principal` and
`grant` are re-exported from `backend/tests/conftest.py:79-86`; `api_client` is the
DB-backed TestClient at `conftest.py:57`. Add `asyncio` and `from fastapi.testclient import
TestClient` to the file's imports.

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest backend/tests/test_lineage.py::test_the_direction_filter_empties_the_excluded_arm -v`
Expected: FAIL — the 200 body's `depends_on_this` is still the flat list, so
`up["depends_on_this"]["models"]` raises `TypeError: list indices must be integers`. A
failure naming that shape is the old wire; any other failure is a defect in the test.

- [ ] **Step 3: Implement the typed handler**

Replace the handler (`dataset_versions.py:369-388`) with:

```python
@router.get(
    "/{version_id}/lineage", summary="Lineage graph", responses=problems(401, 403, 404, 422)
)
async def lineage(
    version_id: UUID,
    caller: ReadDatasets,
    database: DatabaseDep,
    direction: Annotated[str, Query(pattern="^(up|down|both)$")] = "both",
) -> DatasetLineage:
    """FR-75, shaped by `01` §4.9.

    A direction filter empties the arm it excludes rather than omitting it: `up`
    returns `depends_on_this` with four empty arms, `down` returns `built_from: null`
    (`01` §4.9). The response is assembled here, where the modules meet (DEP-1): the
    DATA service supplies `built_from` and `derived_versions`; the models arm comes
    from the modelling module, which owns the table.
    """
    async with database.session() as session:
        await _scoped(session, version_id, caller)
        graph = await dataset_service.lineage_of(
            session, workspace_id=caller.workspace_id, version_id=version_id
        )
        if direction == "up":
            return graph.model_copy(update={"depends_on_this": LineageDependsOn()})
        models = await modelling_service.models_referencing_version(
            session, workspace_id=caller.workspace_id, dataset_version_id=version_id
        )
        depends = graph.depends_on_this
        return graph.model_copy(
            update={
                "depends_on_this": LineageDependsOn(
                    derived_versions=depends.derived_versions,
                    models=models,
                    rating_versions=depends.rating_versions,
                    monitoring_baselines=depends.monitoring_baselines,
                ),
                "built_from": None if direction == "down" else graph.built_from,
            }
        )
```

Add `DatasetLineage` and `LineageDependsOn` to the `model_schema` import block (`:40-51`),
and `from app.platform import modelling as modelling_service` beside the existing
`dataset_service` import. `direction=up` never runs the models query — the arm it would
fill is the one the filter empties. Keep `dict[str, Any]` in the file only where the other
handlers still need it — if the import becomes unused, drop it (ruff will say).

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest backend/tests/test_lineage.py -q`
Expected: PASS. The `up` body asserting all four arms empty is the §4.9 invariant on the
wire, and the `down` body asserting `built_from is null` for a version that has a parent
is the emptying semantics — a filter that dropped the key instead would fail here.

- [ ] **Step 5: Regenerate the contract and verify the wire shape**

Run: `uv run python scripts/generate-contracts.py`
Run: `python3 -c "import json; d=json.load(open('docs/contracts/openapi/generated.json')); print(json.dumps(d['paths']['/api/v1/dataset-versions/{version_id}/lineage']['get']['responses']['200'], indent=1))"`
Expected: the 200 response schema now reads `{"$ref": "#/components/schemas/DatasetLineage"}`
— a named schema, not the untyped `additionalProperties: true` object the endpoint
published before this slice. If the response still shows an inline object, the handler's
return annotation is not the one FastAPI sees — stop and find out why before committing.

- [ ] **Step 6: Run the docs audit and commit**

Run: `python3 scripts/audit-docs.py`
Expected: PASS.

```bash
git add backend/src/app/api/dataset_versions.py backend/tests/test_lineage.py docs/contracts/
git commit -m "feat(w6b-12): the typed lineage handler — assembly at the router, direction empties the excluded arm"
```

### Task 5: The lineage graph in the Dataset detail view

**Files:**
- Modify: `frontend/src/api/datasets.ts:63-65`
- Create: `frontend/src/components/LineageGraph.vue`
- Create: `frontend/src/components/__tests__/LineageGraph.test.ts`
- Modify: `frontend/src/views/DatasetDetailView.vue`
- Modify: `frontend/src/views/__tests__/DatasetDetailView.test.ts`

**Interfaces:**
- Consumes: the regenerated client (`DatasetLineage` from `components["schemas"]`);
  `getLineage(versionId: string)` — already exported, now typed (Task 4's contract);
  `ChartFigure` (props `title`, `caption?`, `columns`, `rows` —
  `frontend/src/components/ChartFigure.vue:31-39`); `listVersions` first-page rows
  (each carries `id`, `version`, `status` — the view's timeline table already renders
  them at `DatasetDetailView.vue:158-228`).
- Produces: `LineageGraph.vue` — props `{ lineage: DatasetLineage; version: number }`;
  renders a single-node-or-chain ECharts `graph` series plus a `ChartFigure` table; and a
  Lineage section in `DatasetDetailView.vue` that calls `getLineage` for the newest
  version (Finding 8).

- [ ] **Step 1: Regenerate the client and type `getLineage`**

Run: `pnpm --dir frontend generate:api`
Expected: `frontend/src/api/generated/schema.d.ts` now defines
`components["schemas"]["DatasetLineage"]` (with the five nested classes flattened into
schemas). `git status` must show no tracked change — the client is VCS-ignored; the
visible proof of the new shape is `docs/contracts/openapi/generated.json` from Task 4,
which CI's `frontend.yml:78-86` regenerates from before type-checking.

In `frontend/src/api/datasets.ts`, replace `:63-65` with:

```ts
export type DatasetLineage = components["schemas"]["DatasetLineage"];

export function getLineage(versionId: string): Promise<DatasetLineage> {
  return request<DatasetLineage>(`/dataset-versions/${versionId}/lineage`);
}
```

- [ ] **Step 2: Write the failing component test**

Create `frontend/src/components/__tests__/LineageGraph.test.ts`, following the
`vi.mock("vue-echarts")` convention (`BacktestView.test.ts:11`) and asserting on the
table — the accessible equivalent is the DOM the test can read:

```ts
import { render, screen } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import LineageGraph from "../LineageGraph.vue";

vi.mock("vue-echarts", () => ({
  default: { template: "<div data-testid=\"chart\" />", props: ["option"] },
}));

const LINEAGE = {
  version_id: "11111111-1111-4111-8111-111111111111",
  built_from: {
    parent_version_id: "22222222-2222-4222-8222-222222222222",
    operation: "sample",
    parameters: {},
  },
  depends_on_this: {
    derived_versions: [
      { version_id: "33333333-3333-4333-8333-333333333333", version: 3, operation: "split" },
    ],
    models: [
      { model_id: "44444444-4444-4444-8444-444444444444", slug: "motor-freq-2026", status: "approved" },
    ],
    rating_versions: [],
    monitoring_baselines: [],
  },
};

describe("the lineage graph", () => {
  it("renders a chart and a table that says what the chart says", () => {
    render(LineageGraph, { props: { lineage: LINEAGE, version: 2 } });
    expect(screen.getByTestId("chart")).toBeTruthy();
    const table = screen.getByRole("table", { name: "Lineage" });
    expect(table).toHaveTextContent("v2");
    expect(table).toHaveTextContent("v3");
    expect(table).toHaveTextContent("motor-freq-2026");
    expect(table).toHaveTextContent("approved");
    expect(table).toHaveTextContent("sample");
  });

  it("renders a single node when nothing depends on the version", () => {
    render(LineageGraph, {
      props: {
        lineage: {
          version_id: "11111111-1111-4111-8111-111111111111",
          built_from: null,
          depends_on_this: {
            derived_versions: [],
            models: [],
            rating_versions: [],
            monitoring_baselines: [],
          },
        },
        version: 1,
      },
    });
    const table = screen.getByRole("table", { name: "Lineage" });
    expect(table).toHaveTextContent("v1");
    expect(table).not.toHaveTextContent("v3");
  });
});
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `pnpm --dir frontend test -- --run src/components/__tests__/LineageGraph.test.ts`
Expected: FAIL — the module cannot be resolved (`Cannot find module '../LineageGraph.vue'`).
That is the discriminator: a failure to find the component, not an assertion inside it.

- [ ] **Step 4: Create `LineageGraph.vue`**

Mirror `OneWayChart.vue`'s structure (`use([...])` at `:18-19`, computed `option`, `<VChart
class="h-80 w-full" :option="option" autoresize />` at `:189-193`) — with one difference:
this repo has no ECharts `graph`-series component yet (verified: zero `type: "graph"`
hits in `frontend/src`), so the registration list is this component's own:

```vue
<script setup lang="ts">
import { computed } from "vue";
import { use } from "echarts/core";
import { GraphChart } from "echarts/charts";
import { TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import VChart from "vue-echarts";

import type { DatasetLineage } from "@/api/datasets";
import ChartFigure from "./ChartFigure.vue";

use([GraphChart, TooltipComponent, CanvasRenderer]);

const props = defineProps<{
  lineage: DatasetLineage;
  /** The queried version's number — the payload carries ids, not numbers. */
  version: number;
}>();

type GraphNode = { id: string; name: string; category: number; x: number; y: number };

const versionNode = computed<GraphNode>(() => ({
  id: props.lineage.version_id,
  name: `v${props.version}`,
  category: 0,
  x: 50,
  y: 60,
}));

const parentNode = computed<GraphNode | null>(() => {
  const builtFrom = props.lineage.built_from;
  if (builtFrom === null) return null;
  return {
    id: builtFrom.parent_version_id,
    name: builtFrom.parent_version_id.slice(0, 8),
    category: 0,
    x: 50,
    y: 0,
  };
});

const childNodes = computed<GraphNode[]>(() =>
  props.lineage.depends_on_this.derived_versions.map((child, i) => ({
    id: child.version_id,
    name: `v${child.version}`,
    category: 0,
    x: 50 + (i - (props.lineage.depends_on_this.derived_versions.length - 1) / 2) * 90,
    y: 120,
  })),
);

const modelNodes = computed<GraphNode[]>(() =>
  props.lineage.depends_on_this.models.map((model, i) => ({
    id: model.model_id,
    name: model.slug,
    category: 1,
    x: 50 + (i - (props.lineage.depends_on_this.models.length - 1) / 2) * 120,
    y: 180,
  })),
);

const nodes = computed<GraphNode[]>(() => {
  const list: GraphNode[] = [versionNode.value];
  if (parentNode.value) list.push(parentNode.value);
  list.push(...childNodes.value, ...modelNodes.value);
  return list;
});

const links = computed(() => {
  const list: { source: string; target: string; symbol: string[] }[] = [];
  if (parentNode.value) {
    list.push({ source: parentNode.value.id, target: versionNode.value.id, symbol: ["none", "arrow"] });
  }
  for (const child of childNodes.value) {
    list.push({ source: versionNode.value.id, target: child.id, symbol: ["none", "arrow"] });
  }
  for (const model of modelNodes.value) {
    list.push({ source: versionNode.value.id, target: model.id, symbol: ["none", "arrow"] });
  }
  return list;
});

const option = computed(() => ({
  tooltip: { trigger: "item" as const },
  series: [
    {
      type: "graph" as const,
      layout: "none",
      data: nodes.value,
      links: links.value,
      categories: [{ name: "version" }, { name: "model" }],
      roam: false,
      label: { show: true, position: "bottom" as const },
      lineStyle: { color: "#94a3b8" },
      itemStyle: { color: "#0284c7" },
      emphasis: { focus: "adjacency" as const },
    },
  ],
}));

const columns = ["Kind", "Name", "Operation", "Status"] as const;

const rows = computed<readonly (readonly (string | number | null)[])[]>(() => {
  const list: (string | number | null)[][] = [];
  if (parentNode.value) {
    list.push(["Built from", parentNode.value.name, props.lineage.built_from?.operation ?? null, null]);
  }
  list.push(["This version", versionNode.value.name, null, null]);
  for (const child of props.lineage.depends_on_this.derived_versions) {
    list.push(["Derived version", `v${child.version}`, child.operation, null]);
  }
  for (const model of props.lineage.depends_on_this.models) {
    list.push(["Model", model.slug, null, model.status]);
  }
  return list;
});
</script>

<template>
  <ChartFigure title="Lineage" :columns="columns" :rows="rows">
    <VChart class="h-80 w-full" :option="option" autoresize />
  </ChartFigure>
</template>
```

The table is `ChartFigure`'s always-in-DOM tabular equivalent (NFR-463); the chart
shows the same four kinds as nodes. The chart's single-node case (a root version nothing
depends on) renders `v{n}` alone — the table's "This version" row says the same thing.
If the repo's other chart components pass `aria-label` or a caption to `ChartFigure`,
mirror that call here — the prop set is the one `ChartFigure.vue:31-39` declares.

- [ ] **Step 5: Run the component test to verify it passes**

Run: `pnpm --dir frontend test -- --run src/components/__tests__/LineageGraph.test.ts`
Expected: PASS. If the table's row-arity guard in `ChartFigure` throws, the `columns` and
`rows` shapes disagree — that is a defect in this task's table, not a guard misfire.

- [ ] **Step 6: Add the section to the Dataset detail view**

In `frontend/src/views/DatasetDetailView.vue`:

Script — add `getLineage`, `type DatasetLineage` to the `@/api/datasets` import, and after
the `versions` ref:

```ts
const lineage = ref<DatasetLineage | null>(null);
```

and inside `load()`, after `nextCursor.value = page.next_cursor ?? null;`:

```ts
    if (!cursor && page.items.length > 0) {
      try {
        lineage.value = await getLineage(page.items[0].id);
      } catch {
        lineage.value = null;
      }
    }
```

Template — after the Versions section's closing `</section>` (following `:228`), add:

```html
      <section v-if="lineage" class="mt-8">
        <LineageGraph :lineage="lineage" :version="versions[0].version" />
      </section>
```

and import `LineageGraph` beside the other component imports. A failed lineage read hides
the section (the graph is a secondary read; the view's problem alert stays reserved for
the loads the page cannot render without). `versions[0]` is the newest version: the first
page is newest-first, and `lineage` is only set when the first page had rows.

- [ ] **Step 7: Extend the view test**

In `frontend/src/views/__tests__/DatasetDetailView.test.ts`, extend the `stub()` fetch
dispatch (after the `VERSIONS` branch) so a lineage URL returns a payload:

```ts
      if (url.includes("/lineage")) {
        return new Response(JSON.stringify({
          version_id: "a",
          built_from: null,
          depends_on_this: {
            derived_versions: [], models: [],
            rating_versions: [], monitoring_baselines: [],
          },
        }), { status: 200, headers: { "Content-Type": "application/json" } });
      }
```

and add, inside the existing `describe` block:

```ts
  it("shows the lineage graph for the newest version", async () => {
    render(DatasetDetailView, { props, ...mounted });
    expect(
      await screen.findByRole("table", { name: "Lineage" }),
    ).toHaveTextContent("v2");
  });

  it("hides the lineage section when the dataset has no versions", async () => {
    vi.stubGlobal("fetch", vi.fn(async () =>
      new Response(JSON.stringify({ items: [], next_cursor: null }), {
        status: 200, headers: { "Content-Type": "application/json" },
      }),
    ));
    render(DatasetDetailView, { props, ...mounted });
    await screen.findByRole("table", { name: "Versions" });
    expect(screen.queryByRole("table", { name: "Lineage" })).toBeNull();
  });
```

The second test's stub overrides the first `vi.stubGlobal` call — both are unset by the
file's `afterEach(() => vi.unstubAllGlobals())`. The fetch stub's `url.includes("/versions")`
branch already fires before the lineage branch, so a lineage URL never hits the dataset
branch.

- [ ] **Step 8: Run the view test to verify it passes**

Run: `pnpm --dir frontend test -- --run src/views/__tests__/DatasetDetailView.test.ts`
Expected: PASS (the six existing its and the two new ones). The newest-version assertion
pins the contract of the section: `v2` is `VERSIONS.items[0].version`, and the graph's
table row is built from the lineage payload's `version_id: "a"`.

- [ ] **Step 9: Commit**

```bash
git add frontend/src/api/datasets.ts frontend/src/components/LineageGraph.vue \
  frontend/src/components/__tests__/LineageGraph.test.ts \
  frontend/src/views/DatasetDetailView.vue \
  frontend/src/views/__tests__/DatasetDetailView.test.ts
git commit -m "feat(w6b-12): the lineage graph on the dataset detail view, getLineage's first caller"
```

### Task 6: The roadmap record, and the gate

**Files:**
- Modify: `docs/roadmap.md` — the Dataset detail row (`:1704`), the Six-Contents-items
  row (`:1774`), and the other-four row (`:3295`)

**Interfaces:**
- Consumes: the delivered slice; the W6b-3 and W6b-13 deliveries already on main
  (`#200` `cdb9f9d`, `#232` `5faa776`).
- Produces: the delivery record the close will audit against (CLAUDE.md §13: scope is
  derived from the spec first, then evidenced).

- [ ] **Step 1: Amend the Dataset detail row**

At `docs/roadmap.md:1704`, the Not-built cell reads:

> `**lineage graph** — getLineage() exists, is typed, and is called by nothing while GET
> …/lineage serves it. semantic_type is read-only; unit and reference_table are not rendered`

Move the lineage graph item into the Built cell with a dated note — append, never rewrite:

> `**lineage graph — delivered 2026-08-26 (W6b-12)**: `getLineage()` is typed by `01` §4.9's
> `DatasetLineage` and called by the detail view; the handler serves the four-arm object,
> the direction filter empties the excluded arm, and the graph renders for the newest
> version.`

Leave `semantic_type`, `unit` and `reference_table` in the Not-built cell — they are a
separate gap (Finding 7).

- [ ] **Step 2: Correct the two stale counts**

`:1774`'s *"four remain"* and `:3295`'s *"the other two remain"* both predate the W6b-3
delivery (`#200`) and the W6b-13 delivery (`#232`). After this slice the record closes:
all six Contents items are delivered, the lineage graph last. Append a dated note to each
row stating that — and state the arithmetic in the note, because a bare count has been
the stale thing twice already: the six are status badge, last validated, owner (W6b-3),
histograms (WK-661), PSI selector (WK-661), lineage graph (W6b-12), plus threshold editing
(W6b-13). Do not rewrite either row's earlier clauses.

- [ ] **Step 3: Run the docs gate**

Run: `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
Expected: PASS, and FR-75 reported with evidence (the rewritten marker still carries
`@pytest.mark.req("FR-75")` — verified in Task 2).

- [ ] **Step 4: Run the full gate — both halves**

Run the Python half: `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
Run the frontend half: `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && pnpm --dir frontend lint && pnpm --dir frontend type-check && pnpm --dir frontend test && pnpm --dir frontend build`
Expected: all green. The drift check `uv run python scripts/generate-contracts.py --check`
runs inside CI (`python.yml:153-154`) and must pass here too — run it explicitly; a
regenerated contract that was not committed fails CI even though every test passes.

- [ ] **Step 5: Commit**

```bash
git add docs/roadmap.md
git commit -m "docs(w6b-12): the lineage graph delivered — the last of the six §5.3 Contents items"
```

---

## Self-review

**1. Spec coverage.** §4.9's example and invariants → Task 1 (the shape) and Task 4 (every
field present; direction empties, tested on the wire). `built_from` null for a root /
`direction=down` → Tasks 2 and 4. `rating_versions`/`monitoring_baselines` declared and
always empty → Task 1 (typed `list[Any]`, documented WK-669/WK-687) and Task 2 (never populated).
The response assembled where the modules meet → Task 4 (router), with the DEP-1 refusal
and the circular-import reason in Global Constraints and Finding 6. The shape in
`model-schema`, generated into the contract → Task 1 (schema file) and Task 4 (OpenAPI
response). FR-75's two directions → Tasks 2-4 and their tests; FR-76's
derivation recording → the `derived_versions` arm reading `derived_from` (Task 2).
FR-53's blast radius → Task 3's any-status models arm. §5.3's Dataset detail
Contents item → Task 5, with Finding 8 recording the newest-version reading. The three
defects `01:846` names → defect 1 closed in Task 4, defect 2 closed in Tasks 2+4, defect 3
closed in Task 2's same-commit rewrite.

**2. Placeholder scan.** No TBD/TODO; every step carries its code and its predicted
failure cause. The two convention guards (the file's own ConfigDict spelling in Task 1,
the existing children query form in Task 2) are instructions to follow the file's idiom,
not placeholders for missing facts.

**3. Type consistency.** `DatasetLineage`, `LineageBuiltFrom`, `LineageDerivedVersion`,
`LineageModel`, `LineageDependsOn` are defined once in Task 1 and used under the same
names in Tasks 2-5. `lineage_of`'s return, `models_referencing_version`'s return, the
handler's return annotation and the frontend alias all resolve to the same class names.
The handler's `model_copy(update=...)` uses `LineageDependsOn`'s exact field names; the
component test's payload mirrors the wire field names (`derived_versions`, `models`,
`built_from`, `version_id`).

**Gaps found in review, fixed inline:** the models-arm test originally inserted one model;
Finding 5's any-status claim needs two statuses and a deterministic order, so the test
inserts two and asserts `(slug, version)` order. The view's no-versions case was an
untested branch; Task 5 Step 7 covers it.
