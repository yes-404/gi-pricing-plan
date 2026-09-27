---
id: PL-763
family: plan
kind: leaf
title: W32-3 — The dataset list's derived fields, and dataset ownership Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-3-dataset-list-derived-fields.md
---

# W32-3 — The dataset list's derived fields, and dataset ownership Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver FR-55 and FR-82 — the dataset list's status badge, last-validated
date and the version each refers to, and a `Dataset`'s explicit owner — both of which have
been specified since 2026-08-19 and carry no evidence at all.

**Architecture:** The two derived fields are computed per request and stored nowhere, which is
FR-55's own instruction and the reason it gives: a status on `Dataset` would be a second
answer free to disagree with `DatasetVersion.status`. `last_validated_at` needs no new column
either — `dataset_versions`' `validated_names_its_report` CHECK guarantees a `validated`
version names a report, and `validation_reports.finished_at` is when that validation finished.
Ownership is the opposite kind of field: it is a fact about the container, not a projection of
its versions, so it is a column, set at ingestion, changed only through an audited route.

**Tech Stack:** Python 3.12, Pydantic v2, SQLAlchemy 2.x async, Alembic, PostgreSQL 16,
FastAPI, pytest.

**Spec:**
- [`../specs/01-data-management.md`](../specs/01-data-management.md) — FR-55 (line 117)
  defines both derived fields, their differing scopes and the "one further aggregate" budget;
  FR-82 (line 208) defines the owner and who may change it; §5.1 is the endpoint table;
  §5.3's Dataset list row is the view these fields feed.
- [`../specs/06-governance.md`](../specs/06-governance.md) — the audit obligation an owner
  change carries, and the Admin role the change path checks.
- [`PL-00753-wk-664-and-wk-692-the-slice-map.md`](PL-00753-wk-664-and-wk-692-the-slice-map.md) — this slice's row. W6b-3
  renders these fields; this slice makes them exist.

---

## Global Constraints

Copied from [`../../CLAUDE.md`](../../CLAUDE.md). Every task's requirements implicitly
include this section.

- **`model-schema` is the single source of truth** (§2, ADR-704). The three new fields are
  defined on `Dataset` there and nowhere else; the frontend's types are generated.
- **Requirement IDs are permanent** (§5). **This slice allocates none** — FR-55 and
  FR-82 already exist, were appended 2026-08-19, and say "Not delivered". This plan
  delivers them; it does not restate them.
- **Money is integer minor units** — not touched here, but `currency` travels on `Dataset` and
  must keep travelling unchanged.
- **Audit writes share the caller's transaction** (§0's retrofit list).
  `app.platform.audit.record` raises `RuntimeError` unless `session.in_transaction()`
  (`backend/src/app/platform/audit.py:71-76`), and its own docstring says why: an event that
  commits independently of the change it describes can disagree with it. Task 4's owner change
  writes both in one `unit_of_work()`.
- **There is no `ForeignKey` in `backend/src/app/db/models.py`** — deliberate, stated at
  `:1282-1285`. `owner_id` is a `PgUUID` column like every other actor column in the file
  (`:105`, `:453`, `:546`, `:592`, `:631`, `:988`, `:1058`, `:1125`).
- **When code and spec disagree, resolve it — do not quietly change one to match the other**
  (§0). Task 5 carries three resolutions.
- **A negative test for every invariant** (§13), and enforcement proven on deliberately broken
  input (§13 rule 4).
- **A fresh worktree has no `.venv`.** Run `uv sync --all-packages --dev` first.
- **The worktree guard refuses compound shell commands.** Run each plainly, not joined by `&&`.

### The gate

Read each command's **own** exit code; `cmd | tail -1` reports `tail`'s and has produced a
false clean here before.

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

**Both halves are required.** Tasks 1 and 4 change `Dataset` and add a route, so
`docs/contracts/openapi/generated.json` changes, and `.github/workflows/frontend.yml` triggers
on `docs/contracts/openapi/**`.

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build
```

The frontend half must pass, but **no `.vue` file is edited here.** `DatasetListView.vue`
renders five columns (`frontend/src/components/…/DatasetListView.vue:90-153`) and has no
spec file; adding the columns is W6b-3's slice. The generated client gaining three optional
fields and one route must not break `type-check` — if it does, that is a finding about the
generated client, not a licence to edit the view.

Database tests need the compose stack. Without it they **skip** rather than fail, and a
migration is exactly the change a skipped suite hides:

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
```

### Where this slice starts

```bash
uv run python scripts/scope-audit.py DATA
```

FR-55 and FR-82 are two of the five DATA requirements it reports with **no
evidence**. Neither carries a single `@pytest.mark.req`. At the end of Task 5 both must carry
markers and drop off that list; the other three are addressed in Task 5's verdicts, not in
code.

---

## File structure

| File | Change | Responsibility |
|---|---|---|
| `packages/model-schema/src/model_schema/datasets.py` | Modify `Dataset`, `:148-182` | Three derived fields and the validator that stops them disagreeing |
| `packages/model-schema/tests/test_dataset_derived_fields.py` | Create | The both-or-neither invariants, at the schema level |
| `backend/src/app/platform/datasets.py` | Modify `to_schema` `:277-299`, `create_dataset` `:140-190`; add `set_owner` | The single projection site, and ownership at ingestion and after |
| `backend/src/app/api/datasets.py` | Modify `list_datasets` `:285-324` and `_latest_versions` `:327-349`; add `PATCH /datasets/{dataset_id}` | One widened aggregate, one further aggregate, one route |
| `backend/src/app/db/models.py` | Modify `DatasetRow`, `:687-720` | `owner_id`, non-null |
| `backend/migrations/versions/<rev>_dataset_owner.py` | Create | The column, the backfill, the non-null promotion |
| `backend/tests/test_api_datasets.py` | Modify `:784-827`; append | The list's new fields, and the owner route's four outcomes |
| `docs/specs/01-data-management.md` | Modify FR-55, FR-82, §5.1 | Delivery recorded, the route published |
| `docs/roadmap.md` | Modify | The two requirements' status |

**Ordering.** Task 1 → 2 → 3 → 4 → 5, strictly. Task 2 consumes Task 1's fields; Task 4
consumes Task 3's column. Tasks 1 and 3 both edit `platform/datasets.py` and must not run in
parallel — W32-1's ledger recorded that fan-out is bounded by file collisions.

---

### Task 1: The three derived fields

**Files:**
- Modify: `packages/model-schema/src/model_schema/datasets.py` — `Dataset`, `:148-182`
- Test: `packages/model-schema/tests/test_dataset_derived_fields.py` (create)

**Interfaces:**
- Consumes: `DatasetStatus` — the enum `DatasetVersion.status` uses, already in this module
  (`VALID_DATASET_TRANSITIONS` at `:57-93` is keyed by it).
- Produces, on `Dataset`:
  - `latest_version_status: DatasetStatus | None = None` — the status of the version
    `latest_version` names.
  - `last_validated_at: datetime | None = None` — when the most recently `validated` version
    finished validating.
  - `last_validated_version: int | None = None` — **which** version that was.

**Why three fields and not two.** FR-55 requires that "where the two refer to different
versions the list states which, so the pair cannot be read as one fact". A date with no version
beside it cannot satisfy that: a Dataset whose v12 is a fresh `draft` above a `validated` v11
would render a `draft` badge next to a date, and a reader has no way to tell whether the date
describes v12 or something older. The third field is the requirement's clause, not an extra.

**Why they are `None`-able and why that is not slack.** A Dataset with no versions has no
latest status; a Dataset never validated has no date. `None` is the honest value for both.
What must not happen is a *partial* answer — a date with no version, or a status with no
version — so two validators refuse exactly that.

- [ ] **Step 1: Write the failing test**

Create `packages/model-schema/tests/test_dataset_derived_fields.py`:

```python
"""FR-55's derived fields, and the pairs that must not come apart."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pydantic
import pytest

from model_schema import Dataset, DatasetStatus


def _dataset(**kwargs: object) -> Dataset:
    return Dataset(
        id=uuid4(),
        workspace_id=uuid4(),
        slug="motor-gb",
        created_at=datetime(2026, 8, 23, tzinfo=UTC),
        **kwargs,  # type: ignore[arg-type]
    )


@pytest.mark.req("FR-55")
def test_a_dataset_with_no_versions_carries_neither_field() -> None:
    dataset = _dataset()
    assert dataset.latest_version is None
    assert dataset.latest_version_status is None
    assert dataset.last_validated_at is None
    assert dataset.last_validated_version is None


@pytest.mark.req("FR-55")
def test_the_two_fields_may_name_different_versions() -> None:
    """The case the requirement was written for: a fresh draft above a validated version.

    A Dataset in this state must render a `draft` badge *and* a last-validated date, and
    must say the date belongs to v11 — otherwise the pair reads as one fact and the badge
    appears to contradict the date.
    """
    dataset = _dataset(
        latest_version=12,
        latest_version_status=DatasetStatus.DRAFT,
        last_validated_at=datetime(2026, 8, 20, tzinfo=UTC),
        last_validated_version=11,
    )
    assert dataset.latest_version != dataset.last_validated_version
    assert dataset.latest_version_status is DatasetStatus.DRAFT


@pytest.mark.req("FR-55")
def test_a_status_without_the_version_it_describes_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="latest_version"):
        _dataset(latest_version_status=DatasetStatus.VALIDATED)


@pytest.mark.req("FR-55")
def test_a_version_without_its_status_is_refused() -> None:
    """Both directions. A caller that batched the version numbers and forgot the statuses
    would otherwise render a blank badge for every row — which is exactly the defect
    `_latest_versions`' docstring records the list already had once."""
    with pytest.raises(pydantic.ValidationError, match="latest_version_status"):
        _dataset(latest_version=12)


@pytest.mark.req("FR-55")
def test_a_validation_date_without_its_version_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="last_validated_version"):
        _dataset(
            latest_version=11,
            latest_version_status=DatasetStatus.VALIDATED,
            last_validated_at=datetime(2026, 8, 20, tzinfo=UTC),
        )


@pytest.mark.req("FR-55")
def test_a_validated_version_without_its_date_is_refused() -> None:
    with pytest.raises(pydantic.ValidationError, match="last_validated_at"):
        _dataset(
            latest_version=11,
            latest_version_status=DatasetStatus.VALIDATED,
            last_validated_version=11,
        )
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest packages/model-schema/tests/test_dataset_derived_fields.py -q`
Expected: FAIL — `extra="forbid"` rejects `latest_version_status` as an unexpected field.

- [ ] **Step 3: Add the fields and the validators**

In `packages/model-schema/src/model_schema/datasets.py`, in `Dataset`, immediately after
`latest_version: int | None = None`:

```python
    #: The status of the version `latest_version` names (FR-55). Derived per request
    #: and stored on no row: a status column on `datasets` would be a second answer to
    #: "can I fit on this?", free to disagree with `DatasetVersion.status`, which §1.3
    #: makes the only one.
    latest_version_status: DatasetStatus | None = None

    #: When the most recently `validated` version finished validating — **not necessarily
    #: `latest_version`**. The badge answers *what state is the newest version in*; this
    #: answers *when was this Dataset last usable*, and FR-55 scopes them differently
    #: on purpose.
    last_validated_at: datetime | None = None

    #: Which version `last_validated_at` describes. FR-55: "where the two refer to
    #: different versions the list states which, so the pair cannot be read as one fact".
    last_validated_version: int | None = None
```

And, after the existing validators:

```python
    @model_validator(mode="after")
    def _the_latest_version_and_its_status_travel_together(self) -> Dataset:
        if (self.latest_version is None) != (self.latest_version_status is None):
            raise ValueError(
                "latest_version and latest_version_status are one fact: a version with no "
                "status renders a blank badge, and a status with no version describes "
                "nothing"
            )
        return self

    @model_validator(mode="after")
    def _the_validation_date_and_its_version_travel_together(self) -> Dataset:
        if (self.last_validated_at is None) != (self.last_validated_version is None):
            raise ValueError(
                "last_validated_at and last_validated_version are one fact (FR-55): a "
                "date with no version cannot be distinguished from the latest version's"
            )
        return self
```

Import `model_validator` from `pydantic` and `datetime` if the module does not already have
them; it has `datetime` for `created_at`.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest packages/model-schema/tests/test_dataset_derived_fields.py -q`
Expected: PASS, 6 tests.

- [ ] **Step 5: Regenerate the contract**

```bash
uv run python scripts/generate-contracts.py
git diff docs/contracts/
```

Expected: `docs/contracts/openapi/generated.json` gains the three optional fields on the
`Dataset` schema. **Read the diff**: a generated artifact matching its source proves neither is
correct (§13 rule 4), so confirm all three appear and that nothing else moved.

- [ ] **Step 6: Commit**

```bash
git add packages/model-schema/src/model_schema/datasets.py packages/model-schema/tests/test_dataset_derived_fields.py docs/contracts/
git commit -m "feat(w32-3): Dataset carries FR-55's three derived fields"
```

---

### Task 2: The list computes them

**Files:**
- Modify: `backend/src/app/api/datasets.py` — `_latest_versions` `:327-349`, `list_datasets`
  `:285-324`
- Modify: `backend/src/app/platform/datasets.py` — `to_schema` `:277-299`
- Test: `backend/tests/test_api_datasets.py` — extend `:784-827`, append two

**Interfaces:**
- Consumes: Task 1's three fields; `Page[T]` (`backend/src/app/api/pagination.py:48-61`,
  `DEFAULT_LIMIT` 50, `MAX_LIMIT` 200, `COUNT_CAP` 10 000).
- Produces:
  - `_latest_versions(session, dataset_ids) -> dict[UUID, tuple[int, str]]` — **widened**, was
    `dict[UUID, int]`. Same one query; it now selects the status alongside the version.
  - `_last_validated(session, dataset_ids) -> dict[UUID, tuple[int, datetime]]` — the one
    further aggregate FR-55 budgets for.
  - `to_schema(row, *, latest_version=None, latest_version_status=None, last_validated=None)`.

**Where `last_validated_at` comes from, and why no column is added.**
`dataset_versions` carries no `validated_at` and no `updated_at` — but its
`validated_names_its_report` CHECK (`backend/src/app/db/models.py:770-773`) guarantees that a
`validated` version names a `validation_report_id`, and `validation_reports.finished_at`
(`:954`) is non-null and is when that validation finished. So the timestamp already exists,
already cannot be null for a validated version, and needs neither a column nor a backfill. A
new `validated_at` column would have had to be backfilled, and the only honest backfill source
would have been the same report — a column duplicating a join.

Only *currently* `validated` versions count. FR-53 and FR-52 move a version that
re-validates to a failing report back to `draft` and clear its report reference, so a version
that is no longer validated correctly stops contributing a date — which is what "when was this
Dataset last usable" means.

**The aggregate budget.** `list_datasets` runs three statements per page today: the row query,
the capped count, and `_latest_versions`. FR-55 budgets "one further aggregate", so the
status must ride on the *existing* `_latest_versions` query rather than adding a fourth, and
`_last_validated` is the one addition. Four statements per page, independent of page size.

- [ ] **Step 1: Write the failing tests**

Extend `backend/tests/test_api_datasets.py`. The existing
`test_the_dataset_list_carries_each_dataset_s_latest_version` at `:784-827` is marked
`FR-27` and is the test to build on; leave its marker alone and add three beside it. Use
`_headers` (`:27-31`), the role fixtures (`:34-43`) and `_slug()` (`:46-47`); use the
`api_client` fixture (`backend/tests/conftest.py:56-60`), **not** the plain `client` fixture at
`:30-35`, which has no database.

```python
@pytest.mark.req("FR-55")
def test_the_list_carries_the_latest_version_s_status(api_client) -> None:
    """The badge. Blank before this slice: `to_schema` had nowhere to put a status."""
    slug = _slug()
    # create the dataset, ingest a version, leave it `draft`
    ...
    body = api_client.get("/api/v1/datasets", headers=_headers(READ_ROLE)).json()
    row = next(item for item in body["items"] if item["slug"] == slug)
    assert row["latest_version"] == 1
    assert row["latest_version_status"] == "draft"
    assert row["last_validated_at"] is None
    assert row["last_validated_version"] is None


@pytest.mark.req("FR-55")
def test_a_draft_above_a_validated_version_reports_both_and_says_which(api_client) -> None:
    """FR-55's worked example, and the only test that can catch the two fields being
    computed from the same version.

    Build v1, validate it, then create v2 and leave it `draft`. The badge must read
    `draft` for v2 while the date belongs to v1 — a list that computed both from
    `latest_version` would report no validation date at all and look entirely plausible.
    """
    ...
    assert row["latest_version"] == 2
    assert row["latest_version_status"] == "draft"
    assert row["last_validated_version"] == 1
    assert row["last_validated_at"] is not None


@pytest.mark.req("FR-55")
def test_the_page_costs_the_same_number_of_statements_at_any_size(api_client) -> None:
    """FR-55 budgets "one further aggregate"; `_latest_versions`' own docstring
    records the 51-round-trip defect this guards against.

    Counted with a SQLAlchemy `before_cursor_execute` listener rather than asserted in
    prose, because an N+1 reintroduced by a later refactor is invisible to every other
    test in this file.
    """
    ...
```

Fill the three elided bodies. For the third, attach an event listener to the engine, request a
page holding 3 datasets and then a page holding 10, and assert the statement count is equal and
is 4. The `_seed()` loop idiom at `backend/tests/test_api_models.py:61-96` shows how this file
seeds several rows — and note that `dispose()` is mandatory there. Never nest `unit_of_work()`:
`.claude/skills/python-test/SKILL.md:526-560` records that it hangs with no output at all.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest backend/tests/test_api_datasets.py -q -k "status or draft_above or statements"`

Expected: FAIL — the first on a missing key or a `null` status. **If it reports `SKIPPED`, the
compose stack is down**; start it and re-run.

- [ ] **Step 3: Widen `_latest_versions`**

Replace the query in `backend/src/app/api/datasets.py:327-349`. `func.max(version)` cannot
carry the status along, so use `DISTINCT ON`, which PostgreSQL gives directly:

```python
async def _latest_versions(
    session: AsyncSession, dataset_ids: list[UUID]
) -> dict[UUID, tuple[int, str]]:
    """The latest version of each dataset on a page, **and its status**, in one query.

    `DISTINCT ON` rather than `max(version)`: the status must be the status *of that
    version*, and an aggregate over `version` cannot carry a correlated column. Still one
    query — FR-55 budgets one *further* aggregate for the whole change, and the
    status rides on the query that was already here.
    """
    if not dataset_ids:
        return {}
    rows = (
        await session.execute(
            select(
                DatasetVersionRow.dataset_id,
                DatasetVersionRow.version,
                DatasetVersionRow.status,
            )
            .where(DatasetVersionRow.dataset_id.in_(dataset_ids))
            .distinct(DatasetVersionRow.dataset_id)
            .order_by(DatasetVersionRow.dataset_id, DatasetVersionRow.version.desc())
        )
    ).all()
    return {dataset_id: (version, status) for dataset_id, version, status in rows}
```

Keep the existing docstring's second and third paragraphs — they record the blank-column defect
and the 51-round-trip one, and both are still the reason this function exists.

- [ ] **Step 4: Add `_last_validated`**

Below it:

```python
async def _last_validated(
    session: AsyncSession, dataset_ids: list[UUID]
) -> dict[UUID, tuple[int, datetime]]:
    """The most recently validated version of each dataset, and when (FR-55).

    Not necessarily the latest version, which is the whole point of the field: a Dataset
    whose v12 is a fresh draft above a validated v11 was last usable at v11's validation,
    and a list computing this from `latest_version` would report it as never validated.

    The timestamp is the report's `finished_at` rather than a column on the version:
    `validated_names_its_report` guarantees a `validated` version has a report, so the
    join cannot drop a row, and a stored `validated_at` would duplicate it.

    Ordered by `finished_at` and not by `version`: "most recently validated" is a fact
    about time, and re-validating an older version after a newer one is a legitimate
    sequence.
    """
    if not dataset_ids:
        return {}
    rows = (
        await session.execute(
            select(
                DatasetVersionRow.dataset_id,
                DatasetVersionRow.version,
                ValidationReportRow.finished_at,
            )
            .join(
                ValidationReportRow,
                ValidationReportRow.id == DatasetVersionRow.validation_report_id,
            )
            .where(
                DatasetVersionRow.dataset_id.in_(dataset_ids),
                DatasetVersionRow.status == "validated",
            )
            .distinct(DatasetVersionRow.dataset_id)
            .order_by(DatasetVersionRow.dataset_id, ValidationReportRow.finished_at.desc())
        )
    ).all()
    return {
        dataset_id: (version, finished_at) for dataset_id, version, finished_at in rows
    }
```

Import `ValidationReportRow` and `datetime` at the top of the module.

- [ ] **Step 5: Widen `to_schema` and the two call sites**

In `backend/src/app/platform/datasets.py:277-299`:

```python
def to_schema(
    row: DatasetRow,
    *,
    latest_version: tuple[int, str] | None = None,
    last_validated: tuple[int, datetime] | None = None,
) -> Dataset:
    """The row as the `01` §4.1 artifact the API returns.

    `latest_version` is a `(version, status)` pair rather than two parameters so a caller
    cannot supply one without the other — the schema refuses that combination anyway
    (FR-55), and a pair turns a runtime `ValidationError` into a type error.
    """
```

and in the body:

```python
        latest_version=latest_version[0] if latest_version else None,
        latest_version_status=(
            DatasetStatus(latest_version[1]) if latest_version else None
        ),
        last_validated_version=last_validated[0] if last_validated else None,
        last_validated_at=last_validated[1] if last_validated else None,
```

Then update the two callers. In `list_datasets`, inside the second session block:

```python
    async with database.session() as session:
        page_ids = [row.id for row in page_rows]
        latest = await _latest_versions(session, page_ids)
        validated = await _last_validated(session, page_ids)

    return Page[Dataset](
        items=[
            service.to_schema(
                row,
                latest_version=latest.get(row.id),
                last_validated=validated.get(row.id),
            )
            for row in page_rows
        ],
        ...
    )
```

Run `grep -rn "to_schema(" backend/src/app | grep -i dataset` to find every other caller — the
detail route passes a bare `int` today and will not type-check until it passes a pair. Give the
detail route both fields too: it handles one dataset, so the two queries cost one row each, and
a detail page that showed nothing where the list showed a date would be its own defect.

- [ ] **Step 6: Run the tests**

Run: `uv run pytest backend/tests/test_api_datasets.py -q`
Expected: PASS. Then `uv run mypy` — the widened `to_schema` signature is what surfaces any
caller this step missed.

- [ ] **Step 7: Prove the statement count guard fails**

§13 rule 4. Temporarily move the `_last_validated` call inside the list comprehension so it
runs once per row, re-run
`uv run pytest backend/tests/test_api_datasets.py -q -k statements`, and confirm it fails with
a count that grows with the page. Restore the code and re-run.

- [ ] **Step 8: Commit**

```bash
git add backend/src/app/api/datasets.py backend/src/app/platform/datasets.py backend/tests/test_api_datasets.py
git commit -m "feat(w32-3): the dataset list derives its badge and last-validated date"
```

---

### Task 3: A Dataset has an owner

**Files:**
- Modify: `backend/src/app/db/models.py` — `DatasetRow`, `:687-720`
- Create: `backend/migrations/versions/<rev>_dataset_owner.py`
- Modify: `backend/src/app/platform/datasets.py` — `create_dataset` `:140-190`, `to_schema`
- Modify: `packages/model-schema/src/model_schema/datasets.py` — `Dataset`
- Test: `backend/tests/test_api_datasets.py` — append

**Interfaces:**
- Consumes: `Principal` (`packages/model-schema/src/model_schema/jobs.py:116-133`), whose
  `id: UUID | None` is null **only** for `ActorKind.SYSTEM`.
- Produces: `DatasetRow.owner_id: Mapped[UUID]`, non-null; `Dataset.owner_id: UUID`, non-null.

**The invariant this creates, and the one refusal it needs.** FR-82 makes `owner_id`
non-null and set at ingestion. `create_dataset` already takes `actor: Principal`, so the owner
is `actor.id` — except that a `system` principal has no id. A dataset created by the platform
itself would therefore have no owner, and a nullable column would be the easy way out and would
lose the requirement. Refuse instead: `system` cannot own a dataset, and a caller that reaches
`create_dataset` as `system` has a bug in the caller. That is a negative test.

**The backfill, and its known limit.** Existing rows have no owner, and the only record of who
created them is the audit chain: `action = 'dataset.created'` with
`entity_ref = 'dataset:' || slug || '@1'` (`backend/src/app/platform/datasets.py:186`). Two
other sites in that file write a UUID where every other site writes the slug, and
`dataset.dictionary_updated` omits `@version` — pre-existing defects that constrain what the
backfill can match. So the migration matches on `entity_ref LIKE 'dataset:' || slug || '@%'`
for the `dataset.created` action, and any row it cannot resolve is left null and blocks the
`nullable=False` promotion with PostgreSQL's own error naming the table. That is deliberate:
inventing an owner for a governed field is worse than a migration that stops and says so. On a
`demo.py`-seeded database every dataset resolves.

- [ ] **Step 1: Write the failing tests**

Append to `backend/tests/test_api_datasets.py`:

```python
@pytest.mark.req("FR-82")
def test_a_created_dataset_is_owned_by_its_creator(api_client) -> None:
    slug = _slug()
    created = api_client.post("/api/v1/datasets", json={"slug": slug}, headers=_headers(WRITE_ROLE))
    assert created.status_code == 201, created.text
    assert created.json()["owner_id"] == str(WRITE_ROLE_PRINCIPAL_ID)


@pytest.mark.req("FR-82")
def test_the_system_principal_cannot_own_a_dataset() -> None:
    """`Principal.id` is null only for `system`, and FR-82 makes `owner_id` non-null.

    Asserted at the service rather than over HTTP: no route authenticates as `system`, and
    a nullable column would have swallowed this silently.
    """
    ...
```

Fill the second body by calling `service.create_dataset` directly with
`Principal(kind=ActorKind.SYSTEM)` inside a `unit_of_work()`, asserting the refusal names the
reason. `WRITE_ROLE_PRINCIPAL_ID` is whatever the role fixtures at `:34-43` already expose —
read them rather than adding a constant.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest backend/tests/test_api_datasets.py -q -k owner`
Expected: FAIL — `owner_id` is not a key in the response.

- [ ] **Step 3: Add the column**

In `backend/src/app/db/models.py`, in `DatasetRow`:

```python
    #: FR-82. Non-null and set at ingestion: a Dataset with no owner has nobody to ask
    #: about it, and every review path that reaches for one would have to invent a
    #: fallback. Not a `ForeignKey` — `:1282-1285` states the rule and the reason.
    owner_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
```

Add `Dataset.owner_id: UUID` in `packages/model-schema/src/model_schema/datasets.py` — non-null
and with no default, so a projection that forgets it fails loudly rather than reporting a
plausible null.

- [ ] **Step 4: Write the migration**

```bash
uv run alembic revision -m "dataset owner"
```

Three operations, in this order — the shape `backend/migrations/versions/55b2bea92837_*.py`
established:

1. `op.add_column("datasets", sa.Column("owner_id", pg.UUID(as_uuid=True), nullable=True))`
2. A backfill, the second data backfill in this tree (`d4e5f6a7b8c9:63-81` is the first, and
   is the shape to copy):
   ```sql
   UPDATE datasets d SET owner_id = (
       SELECT a.actor_id FROM audit_events a
       WHERE a.workspace_id = d.workspace_id
         AND a.action = 'dataset.created'
         AND a.entity_ref LIKE 'dataset:' || d.slug || '@%'
       ORDER BY a.sequence ASC LIMIT 1
   )
   ```
   Read `AuditEventRow` before writing this — the actor column's real name and the ordering
   column must come from the model, not from this plan.
3. `op.alter_column("datasets", "owner_id", nullable=False)`

`downgrade()` drops the column. Confirm `down_revision` is `9e4c7b21fa08`, the current head.

Add a comment above the backfill recording that it matches `@%` rather than `@1` because two
sites in `platform/datasets.py` write a UUID in place of the slug and one omits the version —
otherwise the next reader will "tidy" it to `@1` and silently narrow it.

- [ ] **Step 5: Apply it, and prove the downgrade**

```bash
GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing uv run alembic upgrade head
GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing uv run alembic downgrade -1
GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing uv run alembic upgrade head
```

The bare `alembic upgrade head` does **not** work against the compose stack:
`backend/src/app/config.py`'s `database_url` defaults to `gip:gip@localhost:5432/gip` while
compose provisions `gipricing:gipricing@…/gipricing`, so it dies with `InvalidPasswordError`.

No migration in this tree has a test. The round trip above is the only check this one gets, and
if step 3's `alter_column` fails, read the error: it names the rows the backfill could not
resolve, and that is a finding to record rather than a nullable column to settle for.

- [ ] **Step 6: Set the owner at ingestion**

In `create_dataset` (`backend/src/app/platform/datasets.py:140-190`), before building the row:

```python
    if actor.id is None:
        raise PlatformError(
            "VALIDATION_FAILED",
            "A dataset needs an owner",
            422,
            "FR-82 makes owner_id non-null and set at ingestion; the system principal "
            "has no id and cannot own one. Create it as the user or service account "
            "responsible for it.",
        )
```

Add `owner_id=actor.id` to the `DatasetRow(...)` call, and `owner_id=row.owner_id` to
`to_schema`. Add `"owner_id": str(row.owner_id)` to the existing `audit.record` call's `after`
payload — ownership is part of what creating a dataset established, and the audit's `after`
should say so.

- [ ] **Step 7: Run the tests**

Run: `uv run pytest backend/tests/test_api_datasets.py -q`

Expected: PASS. Every test in the file that creates a dataset now needs a resolvable actor;
any that fails is a fixture using a system principal, which is a legitimate breakage to fix in
the test.

- [ ] **Step 8: Regenerate and re-seed**

```bash
uv run python scripts/generate-contracts.py
uv run python scripts/demo.py --rows 60000
```

Expected: the contract gains `owner_id` as required on `Dataset`, and the demo seed completes.
The seed is the only exercise the production creation path gets.

- [ ] **Step 9: Commit**

```bash
git add backend/src/app/db/models.py backend/migrations/versions backend/src/app/platform/datasets.py packages/model-schema/src/model_schema/datasets.py backend/tests/test_api_datasets.py docs/contracts/
git commit -m "feat(w32-3): a Dataset carries a non-null owner, set at ingestion"
```

---

### Task 4: Transferring ownership

**Files:**
- Modify: `backend/src/app/api/datasets.py` — add `PATCH /datasets/{dataset_id}`
- Modify: `backend/src/app/platform/datasets.py` — add `set_owner`
- Modify: `docs/specs/01-data-management.md` — §5.1's endpoint table
- Test: `backend/tests/test_api_datasets.py` — append

**Interfaces:**
- Consumes: Task 3's `owner_id`; `rbac.require_permission`; `audit.record`; the
  `Database.unit_of_work()` context manager.
- Produces:
  - `set_owner(session, *, workspace_id, actor, dataset_id, owner_id) -> DatasetRow`
  - `PATCH /api/v1/datasets/{dataset_id}` taking `{"owner_id": "<uuid>"}` and returning the
    updated `Dataset`.

**Why a route is needed at all.** FR-82 says the owner is "changeable only by Admin or
current owner, audited as a metadata change". `backend/src/app/api/datasets.py` has no dataset
update route — only `PUT …/dictionary` (`:374`) and `PATCH …/schema` (`:590`), both scoped to a
version. So the requirement's change clause has nowhere to live, and a requirement whose only
implementable half is delivered is half-delivered.

**Two-condition authorisation, which is unlike everything else in this file.** Every other
route here asks a single question of RBAC. This one is `Admin **or** the current owner`, and
the owner is not a role. Put both conditions in `set_owner`, in the service layer, so the rule
is written once and the route cannot forget half of it — and so the refusal can say *which*
condition failed, which a caller who is neither cannot otherwise work out.

- [ ] **Step 1: Write the failing tests**

Append to `backend/tests/test_api_datasets.py`. Four outcomes, because a governed field's
change path needs its permit, its two refusals and its record:

```python
@pytest.mark.req("FR-82")
def test_the_owner_can_hand_the_dataset_on(api_client) -> None:
    ...
    assert response.status_code == 200, response.text
    assert response.json()["owner_id"] == str(OTHER_PRINCIPAL_ID)


@pytest.mark.req("FR-82")
def test_an_admin_can_reassign_a_dataset_they_do_not_own(api_client) -> None:
    """The second arm. Without this test the rule collapses to "the owner may", and an
    Admin unable to reassign an ownerless-in-practice dataset is exactly the situation the
    Admin arm exists for."""
    ...


@pytest.mark.req("FR-82")
def test_a_third_party_with_dataset_write_is_refused(api_client) -> None:
    """The load-bearing refusal. `DATASET_WRITE` is not enough — a writer who is neither
    Admin nor owner may edit the dictionary and may not reassign the dataset, and a route
    that checked only the permission would look correct in every other test here."""
    response = ...
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "FORBIDDEN"


@pytest.mark.req("FR-82")
def test_the_reassignment_is_audited_with_both_owners(api_client) -> None:
    """`06` R2 and FR-82's "audited as a metadata change". `before` must carry the
    outgoing owner: an audit event saying only who owns it now cannot answer who lost it."""
    ...
    event = ...
    assert event["action"] == "dataset.owner_changed"
    assert event["before"]["owner_id"] == str(WRITE_ROLE_PRINCIPAL_ID)
    assert event["after"]["owner_id"] == str(OTHER_PRINCIPAL_ID)
```

Fill the four bodies. Read the role fixtures at `:34-43` for the principals available, and the
cross-workspace 404 test at `:228-238` for how this file reads back an audit chain. Assert
problem+json failures on `["code"]`, and put `, response.text` on every status assertion — both
are this file's idiom.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest backend/tests/test_api_datasets.py -q -k "hand_the_dataset or admin_can_reassign or third_party or audited_with_both"`
Expected: all four FAIL with 405 or 404 — there is no PATCH on that path.

- [ ] **Step 3: Write `set_owner`**

In `backend/src/app/platform/datasets.py`:

```python
async def set_owner(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    dataset_id: UUID,
    owner_id: UUID,
) -> DatasetRow:
    """Hand a Dataset to a new owner (FR-82).

    Two conditions, not one: **Admin, or the current owner**. Both live here rather than in
    the route so the rule is written once, and so the refusal can name which condition
    failed — a caller who holds `DATASET_WRITE` and is refused would otherwise have no way
    to tell this from a missing permission.
    """
    row = await load_dataset(session, workspace_id=workspace_id, dataset_id=dataset_id)
    is_owner = actor.id is not None and actor.id == row.owner_id
    if not is_owner:
        await rbac.require_permission(
            session,
            workspace_id=workspace_id,
            principal=actor,
            permission=Permission.WORKSPACE_ADMIN,
        )
    before = {"owner_id": str(row.owner_id)}
    row.owner_id = owner_id
    await session.flush()
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="dataset.owner_changed",
        entity_ref=f"dataset:{row.slug}",
        before=before,
        after={"owner_id": str(owner_id)},
    )
    return row
```

`Permission.WORKSPACE_ADMIN` is a placeholder for whatever the real Admin permission is called
— read `packages/model-schema/src/model_schema/permissions.py`'s `Permission` enum and
`BUILTIN_ROLES` (`:123-160`) and use the one the `admin` role actually holds. Do not add a new
permission.

`load_dataset` already folds `workspace_id` into its predicate, which is what makes a
cross-workspace request a 404 rather than a 403.

- [ ] **Step 4: Add the route**

In `backend/src/app/api/datasets.py`, following the module's route idiom for the request body
model, the dependency injection and `problems(...)`:

```python
@router.patch(
    "/datasets/{dataset_id}",
    summary="Change a dataset's owner",
    responses=problems(400, 401, 403, 404, 422),
)
async def patch_dataset_owner(...) -> Dataset:
    """FR-82's change path: Admin or the current owner, audited.

    A PATCH with one settable field rather than a bespoke `/owner` sub-resource, so the
    next metadata field FR-82's sibling requirements add has somewhere to go.
    """
```

Wrap the service call in `database.unit_of_work()` — `audit.record` raises `RuntimeError`
outside a transaction, and this route writes both the change and its record.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest backend/tests/test_api_datasets.py -q`
Expected: PASS.

- [ ] **Step 6: Publish the endpoint in `01` §5.1**

Add the row to §5.1's endpoint table, matching its neighbours' columns. Then:

```bash
uv run python scripts/generate-contracts.py
uv run python scripts/scope-audit.py DATA --endpoints
```

Expected: the contract gains the path, and `--endpoints` counts it implemented. Run this
**after** step 4, never before — a §5.1 row with no route published makes the count worse.

- [ ] **Step 7: Commit**

```bash
git add backend/src/app/api/datasets.py backend/src/app/platform/datasets.py backend/tests/test_api_datasets.py docs/specs/01-data-management.md docs/contracts/
git commit -m "feat(w32-3): an audited owner-transfer path for datasets"
```

---

### Task 5: Resolve the spec and the roadmap

**Files:**
- Modify: `docs/specs/01-data-management.md` — FR-55, FR-82
- Modify: `docs/roadmap.md`

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: no code. §0's resolution step and §13 rule 6's statement of what was not delivered.

**Three findings, three verdicts.**

1. **FR-55 said "Not delivered. Phase 1b, owner WK-664"** and predicted the shape of the work
   — "one further aggregate plus the two columns in the view". The prediction was right about
   the aggregate and **wrong about the field count**: two derived fields cannot satisfy the
   clause "where the two refer to different versions the list states which", so there are
   three. The requirement gains a dated delivery note saying so. The two *columns in the view*
   are still not delivered and are still W6b-3's — that half of the sentence stands.
2. **FR-82 said the same**, and is delivered including the change path it implies. Its
   note records the one thing the requirement did not anticipate: a `system` principal has no
   id, so `create_dataset` refuses it rather than accepting a null owner.
3. **FR-67 is unevidenced *by design*.** `scope-audit.py DATA` lists it beside the two
   this slice delivers, which invites a reader to treat all three as gaps. It is a decided
   deferral with an explicitly unowned trigger — "assigning it to a workstream would schedule
   work no consumer has asked for" — so its verdict is **deferred, deliberately, trigger
   unchanged**, and the roadmap says that rather than leaving it to be re-discovered. Likewise
   NFR-465 and NFR-466 are budgets needing a measurement, not a marker; §13 rule 5 makes
   that a `bench-data.py` run, and it is **not this slice's**.

- [ ] **Step 1: Append delivery notes to both requirements**

To FR-55's row in `docs/specs/01-data-management.md`, append — as part of the same single
line, since §3's rows are one line each:

> **Delivered 2026-08-23 (W32-3), as three fields rather than two.** `last_validated_at` cannot
> satisfy "the list states which" on its own — a date beside a `draft` badge is unreadable
> without the version it belongs to — so `last_validated_version` accompanies it, and a
> validator refuses either without the other. Neither field is stored:
> `latest_version_status` rides on the existing `_latest_versions` query via `DISTINCT ON`, and
> `last_validated_at` is the `finished_at` of the report that `validated_names_its_report`
> already guarantees a `validated` version has — so the "one further aggregate" budget is met
> exactly, at four statements per page independent of page size, and no `validated_at` column
> was added. **The view columns remain W6b-3's**: this slice delivers the fields, not their
> rendering.

To FR-82's row:

> **Delivered 2026-08-23 (W32-3).** `owner_id` is non-null on `datasets`, set from the creating
> principal, and changed only through `PATCH /api/v1/datasets/{dataset_id}` by an Admin or the
> current owner, audited as `dataset.owner_changed` with both owners in `before`/`after`. One
> case the requirement did not anticipate: `Principal.id` is null for `system`, so
> `create_dataset` refuses a system principal rather than accepting an ownerless dataset. The
> backfill matched the audit chain's `dataset.created` events on
> `entity_ref LIKE 'dataset:<slug>@%'` rather than `@1`, because two sites in
> `platform/datasets.py` write a UUID where the rest write the slug and one omits the version —
> a pre-existing inconsistency, recorded here rather than silently worked around.

- [ ] **Step 2: Update the roadmap**

Record both as delivered, and add the third verdict:

```
FR-55 and FR-82 delivered 2026-08-23 (W32-3). FR-55 landed as three fields
rather than two — the requirement's "states which" clause needs the version beside the date.

**Still open, and deliberately so:** FR-67 is a decided deferral with no owner, by its own
terms — the trigger is a named reader asking for an exposure-ordered view, and assigning it to a
workstream would schedule work nobody has asked for. It appears in `scope-audit.py DATA`'s
unevidenced list and should not be read as a gap.

**Still open, and owned elsewhere:** NFR-465 and NFR-466 are budgets. §13 rule 5 makes
them a `bench-data.py` measurement rather than a marker; not this slice's.

**Not delivered here:** `01` §5.3's Dataset list columns. The fields exist and the endpoint
returns them; rendering them is W6b-3.
```

- [ ] **Step 3: Run the documentation checks**

```bash
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/scope-audit.py DATA
```

Expected: the first two PASS; `scope-audit.py DATA` no longer lists FR-55 or FR-82
as unevidenced, and still lists FR-67, NFR-465 and NFR-466 — which is correct and is
what Step 2 explains.

- [ ] **Step 4: Run the full gate**

Every command in both gate blocks, each on its own line, reading each one's own exit code.

- [ ] **Step 5: Commit**

```bash
git add docs/specs/01-data-management.md docs/roadmap.md
git commit -m "docs(w32-3): FR-55 and FR-82 delivered, with what changed"
```

---

## Closing the slice

- [ ] Every task's steps are checked.
- [ ] `scope-audit.py DATA` no longer reports FR-55 or FR-82 without evidence.
- [ ] `scope-audit.py DATA --endpoints` counts the new PATCH route.
- [ ] The statement-count guard was shown to fail on a deliberately re-introduced N+1.
- [ ] The migration was downgraded and re-upgraded against the compose stack.
- [ ] `demo.py` runs end to end, which is the only exercise the creation path gets.
- [ ] Backend tests ran against a live database — no `SKIPPED` in the DB suite.
- [ ] The frontend gate passes with no `.vue` file edited.
- [ ] FR-67's deliberate deferral is written down, so it is not re-audited as a gap.
- [ ] The branch is pushed and a PR is open. Do not force-push, do not merge, do not push to
      `main`.

## Self-Review

**1. Spec coverage.** FR-55's five clauses each map to a task: the two derived fields
(Task 1), their differing scopes and the "need not be the latest one" case (Task 2's second
test), "states which" (the third field, Task 1), "one further aggregate" (Task 2's statement
count test), and "neither is stored, neither writable" (fields on `Dataset` with no column, and
no route that sets them). FR-82's three clauses map to Task 3 (non-null, set at ingestion)
and Task 4 (Admin-or-owner, audited). §5.1 gains the PATCH row in Task 4 Step 6. §5.3's view
columns are explicitly out of scope with W6b-3 named as owner, in both the gate section and
Task 5.

**2. Placeholder scan.** Nine test bodies are elided with `...`, each naming the exact file and
line range of the idiom to copy (`test_api_models.py:61-96` for seeding,
`test_api_datasets.py:228-238` for reading the audit chain, `:34-43` for the role fixtures)
rather than saying "similar to the above". Two identifiers are deliberately marked as
placeholders to be resolved by reading, not guessed: `Permission.WORKSPACE_ADMIN` in Task 4
Step 3, which says to read the enum and use the one the `admin` role holds, and the audit
actor/ordering column names in Task 3 Step 4. Both would be wrong to invent, and both are
one `grep` away.

**3. Type consistency.** `_latest_versions` returns `dict[UUID, tuple[int, str]]` in Task 2's
Interfaces block, in its implementation, and at its one call site; `_last_validated` returns
`dict[UUID, tuple[int, datetime]]` in all three. `to_schema`'s widened signature takes those
two pair types by the same names in Task 2 Step 5 and is called with them in the same step.
`owner_id` is `UUID` on the row (Task 3 Step 3), on the schema (same step), in `set_owner`'s
signature (Task 4 Step 3) and as a `str` only in JSON assertions and audit payloads, where it
is explicitly `str(...)`-wrapped.
