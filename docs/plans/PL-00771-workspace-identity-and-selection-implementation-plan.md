---
id: PL-771
family: plan
kind: leaf
title: Workspace Identity and Selection Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-7-workspace-identity-and-selection.md
---

# Workspace Identity and Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a Workspace a named row, let a principal with several memberships choose which one
it is acting in, and verify that choice against the memberships the platform already holds.

**Architecture:** Three requirements in one dependency chain, so one plan. FR-395 gives the
`workspaces` table its row and backfills one for every distinct `workspace_id` already stored
anywhere — the orphan case a foreign key must not discover after the fact. FR-396's four
obligations then have something to name: `GET /me` lists the caller's memberships with their names,
and `require_caller` reads FR-397's `Workspace-Id` header, checks it against
`AuthenticatedIdentity.workspaces` and refuses anything else. The header is declared once on the
dependency rather than on forty route signatures — FastAPI hoists a dependency's `Header(...)`
parameters into every operation's published parameters, so the generated client gets it and the
five-spec path-prefix edit FR-397 refused on cost stays refused. The switch audit closes it:
`06` FR-372 chains per workspace, so leaving one and entering another writes two events, one in
each chain.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x async, Alembic, PostgreSQL 16,
`pytest`, `uv`.

**Spec:** [`../specs/07-platform.md`](../specs/07-platform.md) §3.1 — FR-395, FR-396,
FR-397 (the last decides OQ-648). The audit obligation is
[`../specs/06-governance.md`](../specs/06-governance.md) FR-372; the identity endpoint is `06`
§5.1, built as `backend/src/app/api/me.py`.

**Proposed slice id:** `W32-7`. The WK-692 slice boundaries in
[`PL-00753-wk-664-and-wk-692-the-slice-map.md`](PL-00753-wk-664-and-wk-692-the-slice-map.md) are recorded as *pending* maintainer
acceptance and stop at `W32-6`; this number is a proposal, not an accepted allocation.

**Unblocks:** `W6b-11`, the workspace switcher in the app shell, which that slice map records as
blocked on this backend half.

## Global Constraints

- No new requirement ids. FR-395, FR-396 and FR-397 all exist in
  [`../specs/07-platform.md`](../specs/07-platform.md) §3.1 as of 2026-08-23.
- The header is spelled **`Workspace-Id`** — unprefixed, and deliberately not
  `x-dev-workspace-id`, which is the `local`/`dev` development header FR-393 confines. Do not
  reuse or rename either.
- **Refusing is the rule; the header only gives the caller a way to satisfy it.** A principal with
  several memberships and no header is refused, never defaulted into one — including "the first",
  "the oldest" or "the only one they used last time".
- `WORKSPACE_SCOPE_DENIED` and `WORKSPACE_SELECTION_REQUIRED` are already registered in
  `backend/src/app/errors.py:46-56`. Do not add codes; do delete the stale comment that says they
  are registered ahead of the code that raises them.
- Money is integer pence/cents or `Decimal`. Nothing here touches money.
- Every new test carries a `@pytest.mark.req(...)` marker. `--strict-markers` is on.
- `uv run alembic` needs the DSN from `GIP_DATABASE_URL`; `alembic.ini` carries no URL. See
  `.claude/skills/dev-commands`.
- Conventional Commits. Commit at the end of every task.

---

### Task 1: A Workspace is a row

**Files:**
- Modify: `backend/src/app/db/models.py` — add `WorkspaceRow` above `WorkspaceMemberRow:437`
- Modify: `backend/src/app/db/models.py:437-461` (`WorkspaceMemberRow`), `:465-491` (`WorkspaceSettingRow`) — add the foreign key
- Create: `backend/migrations/versions/<rev>_workspaces_table.py`
- Modify: `backend/tests/conftest_db.py:88-135` (`grant`) — create the row
- Test: `backend/tests/test_workspaces.py` (new)

**Interfaces:**
- Produces: `WorkspaceRow` with `id: UUID` (pk), `slug: str` (`String(64)`), `name: str`
  (`String(200)`), `created_at: datetime`, and
  `UniqueConstraint("slug", name="uq_workspaces_slug")`. A workspace is not itself
  workspace-scoped, so the slug is unique globally rather than per workspace — unlike every other
  slug in this schema. Say so in the class docstring.
- Produces: `ensure_workspace(session, *, workspace_id, slug=None, name=None) -> WorkspaceRow` in
  `backend/src/app/platform/workspaces.py` (new module), idempotent, modelled on
  `rbac.seed_builtin_roles` (`backend/src/app/platform/rbac.py:110-139`).

FR-395's backfill is the load-bearing half: *"a row for **every distinct `workspace_id`
already stored anywhere**, not only the ones with a membership."* A `SELECT DISTINCT workspace_id`
over `workspace_members` alone would leave an orphan for the foreign key to find at
`ALTER TABLE`-time, which is exactly the case the requirement names.

- [ ] **Step 1: Enumerate every table carrying a `workspace_id`**

```bash
grep -n "workspace_id: Mapped\[UUID\]" backend/src/app/db/models.py
```

Record the table name of each hit — this list *is* the backfill's `UNION`. Do not shorten it to
the tables that feel important: the requirement says "anywhere", and the list is the evidence that
"anywhere" was read rather than assumed. Write the list into the migration's docstring.

- [ ] **Step 2: Write the failing test**

Create `backend/tests/test_workspaces.py`:

```python
"""FR-395: a Workspace is a named, addressable entity rather than a bare column."""

from __future__ import annotations

import pytest
from sqlalchemy import inspect, select

from app.db.models import WorkspaceMemberRow, WorkspaceRow
from app.db.session import Database
from model_schema import new_uuid7


@pytest.mark.req("FR-395")
async def test_a_workspace_row_carries_a_name_and_a_slug(database: Database) -> None:
    """Every surface that would show a workspace shows a UUID until this row exists."""
    workspace_id = new_uuid7()
    slug = f"ws-{workspace_id.hex[-10:]}"
    async with database.unit_of_work() as session:
        session.add(WorkspaceRow(id=workspace_id, slug=slug, name="Motor Pricing"))

    async with database.session() as session:
        row = await session.get(WorkspaceRow, workspace_id)
    assert row is not None
    assert row.name == "Motor Pricing"
    assert row.slug == slug
    assert row.created_at is not None


@pytest.mark.req("FR-395")
async def test_a_membership_cannot_name_a_workspace_that_does_not_exist(
    database: Database,
) -> None:
    """**Negative**, and the reason the backfill covers every table rather than this one.

    The foreign key is what makes a workspace addressable rather than conventionally
    referenced. Without it a membership row can name an id nothing describes, which is the
    state the whole schema was in before this slice.
    """
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            session.add(
                WorkspaceMemberRow(user_id=new_uuid7(), workspace_id=new_uuid7())
            )
```

- [ ] **Step 3: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_workspaces.py -v
```
Expected: collection FAILS with `ImportError: cannot import name 'WorkspaceRow'`.

If it reports `SKIPPED — PostgreSQL not reachable`, start the stack first (`.claude/skills/dev-commands`
has the compose command). A skipped test is not a failing test and proves nothing.

- [ ] **Step 4: Add the model and the two foreign keys**

In `backend/src/app/db/models.py`, immediately above `WorkspaceMemberRow`:

```python
class WorkspaceRow(Base):
    """A Workspace: a named, addressable entity (FR-395).

    It existed as a `workspace_id` column and nothing else, so a workspace had no name and
    every surface that would show one showed a UUID — which is why `W6b-11`'s switcher had
    nothing to render and was specified against an entity that did not exist.

    The slug is unique **globally**, not per workspace, unlike every other slug in this
    schema: a workspace is the scope others are unique within, so there is no outer scope for
    it to be unique inside.
    """

    __tablename__ = "workspaces"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=new_uuid7)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (UniqueConstraint("slug", name="uq_workspaces_slug"),)
```

Then give both existing rows the reference FR-395 asks for. In `WorkspaceMemberRow` and
`WorkspaceSettingRow`, change the `workspace_id` column to:

```python
    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
```

Add `ForeignKey` to the `sqlalchemy` import if it is not already there. **Only these two tables**
— FR-395 names `workspace_members` and `workspace_settings` and no others, and putting the key
on every workspace-scoped table is a larger change than the requirement asks for.

- [ ] **Step 5: Write the migration**

```bash
uv run alembic revision -m "workspaces table"
```

Confirm the generated file's `down_revision` is `"82edffbe1dce"` — the current head. If it is not,
someone else has landed a migration; rebase and regenerate rather than editing the revision id by
hand.

Fill it in, following `backend/migrations/versions/82edffbe1dce_dataset_owner.py` as the template:

```python
"""workspaces table

A Workspace becomes a named row (`07` FR-395), and `workspace_members` and
`workspace_settings` reference it.

The backfill covers **every table carrying a `workspace_id`**, not only the two that gain the
foreign key: an id stored anywhere and described nowhere is exactly the orphan the `ALTER TABLE`
must not discover. The union below was enumerated from `app.db.models` rather than recalled —
`grep -n "workspace_id: Mapped\\[UUID\\]"` — and every table it found is listed.

Revision ID: <rev>
Revises: 82edffbe1dce
Create Date: <generated>
"""
```

The body — replace the `UNION` list with Step 1's actual enumeration, one `SELECT` per table:

```python
#: One row per distinct workspace id, named after the id itself. A generated name is honest
#: about what is known: nobody recorded a name for these, and inventing "Workspace 1" would
#: read like a name someone chose.
_BACKFILL = """
INSERT INTO workspaces (id, slug, name, created_at)
SELECT ids.workspace_id,
       'ws-' || replace(ids.workspace_id::text, '-', ''),
       'Workspace ' || left(replace(ids.workspace_id::text, '-', ''), 8),
       now()
  FROM (
        SELECT DISTINCT workspace_id FROM workspace_members
        UNION SELECT DISTINCT workspace_id FROM workspace_settings
        UNION SELECT DISTINCT workspace_id FROM audit_events
        -- ... one line per table from Step 1 ...
       ) AS ids
 WHERE ids.workspace_id IS NOT NULL
ON CONFLICT (id) DO NOTHING
"""


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("slug", name="uq_workspaces_slug"),
    )
    op.execute(_BACKFILL)
    # After the backfill, never before: the key is what proves the backfill was complete, and
    # PostgreSQL's own error names the offending table if it was not.
    op.create_foreign_key(
        "fk_workspace_members_workspace", "workspace_members", "workspaces",
        ["workspace_id"], ["id"],
    )
    op.create_foreign_key(
        "fk_workspace_settings_workspace", "workspace_settings", "workspaces",
        ["workspace_id"], ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_workspace_settings_workspace", "workspace_settings", type_="foreignkey")
    op.drop_constraint("fk_workspace_members_workspace", "workspace_members", type_="foreignkey")
    op.drop_table("workspaces")
```

The slug is derived from the id rather than generated randomly so that re-running the backfill on
a restored dump produces the same slugs — `ON CONFLICT DO NOTHING` then means what it says.

- [ ] **Step 6: Apply the migration and re-run the tests**

```bash
uv run alembic upgrade head
uv run pytest backend/tests/test_workspaces.py -v
```
Expected: `upgrade` exits 0 and both tests PASS.

- [ ] **Step 7: Give the test suite a workspace row**

Every existing test mints a bare `new_uuid7()` as its workspace (`conftest_db.py:136-140`), and
the foreign key now refuses their membership and settings writes. `grant` is the suite's only
workspace-creation path — its own comment at `conftest_db.py:108-117` says so, and says *"a
workspace is a bare `UUID` column, not a row"*, which this task falsifies.

In `backend/tests/conftest_db.py`, inside `_grant`'s `unit_of_work` block and **before**
`seed_builtin_roles`:

```python
        async with database.unit_of_work() as session:
            # The workspace row arrives first: `workspace_members` and `workspace_settings`
            # now carry a foreign key to it (FR-395), so seeding either without it is an
            # integrity error rather than a missing name.
            await workspaces.ensure_workspace(session, workspace_id=workspace_id)
            await rbac.seed_builtin_roles(session, workspace_id)
```

Add `workspaces` to the `from app.platform import ...` line, and correct the stale comment at
`:108-117` — it now reads that the catalogue and the roles hang off `grant` because it is the
suite's workspace-creation path, without the "not a row" clause.

- [ ] **Step 8: Write `ensure_workspace`**

Create `backend/src/app/platform/workspaces.py`:

```python
"""Workspace rows (`07` FR-395).

A Workspace is created by provisioning, which `06` owns and which does not exist yet. What
exists here is the idempotent ensure the seeds and the test suite need, modelled on
`rbac.seed_builtin_roles` for the same reason: the row must arrive with the workspace, and
there is no other moment that owns doing it.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WorkspaceRow

__all__ = ["ensure_workspace"]


async def ensure_workspace(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    slug: str | None = None,
    name: str | None = None,
) -> WorkspaceRow:
    """Create the workspace's row if it is absent, and return it either way.

    Idempotent, like `seed_builtin_roles`: called on a path that may run twice, and a second
    call must not raise. The derived slug and name match the migration's backfill so that a
    workspace created here and one backfilled there are indistinguishable.
    """
    existing = await session.get(WorkspaceRow, workspace_id)
    if existing is not None:
        return existing
    bare = workspace_id.hex
    row = WorkspaceRow(
        id=workspace_id,
        slug=slug or f"ws-{bare}",
        name=name or f"Workspace {bare[:8]}",
    )
    session.add(row)
    await session.flush()
    return row
```

- [ ] **Step 9: Run the backend suite**

```bash
uv run pytest backend/tests -q
uv run pytest tests/test_repository_invariants.py -q
```
Expected: both pass. The second is the single-head check at `tests/test_repository_invariants.py:281-313`
— note it lives in the **repo-root** `tests/`, not `backend/tests/`. If the backend suite reports
integrity errors, a test creates a workspace without going through `grant`; find it with the
failure's table name and give it `ensure_workspace`.

- [ ] **Step 10: Prove the migration's backfill covers the orphan case**

The requirement's whole point is the workspace with no membership. Prove it on a real orphan:

```bash
uv run alembic downgrade -1
```
Then, against the test database, insert an `audit_events` row (or any table from Step 1 that is
*not* `workspace_members`) carrying a fresh `workspace_id`, and run:
```bash
uv run alembic upgrade head
```
Expected: the upgrade succeeds and `SELECT * FROM workspaces WHERE id = '<that id>'` returns a row.
Then narrow `_BACKFILL` to `workspace_members` alone, downgrade, re-upgrade, and confirm the
`create_foreign_key` **fails** with a violation naming that table. Restore the full union.

Record both outcomes in the ledger. `CLAUDE.md` §13: enforcement is proven on deliberately broken
input, and a backfill that has never been run against an orphan has not been tested against one.

- [ ] **Step 11: Commit**

```bash
git add backend/src/app/db/models.py backend/src/app/platform/workspaces.py
git add backend/migrations/versions backend/tests/conftest_db.py backend/tests/test_workspaces.py
git commit -m "feat(w32-7): a Workspace is a named row with a backfilled id"
```

---

### Task 2: `GET /me` lists the caller's memberships by name

**Files:**
- Modify: `backend/src/app/api/me.py:50-66` (`Me`), `:69-113` (`get_me`)
- Test: `backend/tests/test_api_me.py` (or the existing `/me` test module — find it with
  `grep -rln '"/api/v1/me"' backend/tests/`)

**Interfaces:**
- Consumes: `WorkspaceRow` from Task 1.
- Produces: `WorkspaceMembership(workspace_id: str, slug: str, name: str)` and
  `Me.workspaces: tuple[WorkspaceMembership, ...]`.

FR-396 opens with it: *"The memberships are readable from the identity endpoint `06` §5.1
declares, each carrying FR-395's name."* Without this the switcher can enforce a choice it
cannot offer.

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.req("FR-396")
async def test_me_lists_every_membership_with_its_name(
    api_client: TestClient, database: Database, workspace_id, principal, grant
) -> None:
    """A switcher cannot offer a choice the identity endpoint does not describe.

    Two memberships, and the response must name both — not only the one the caller is acting
    in, which is what `workspace_id` already says.
    """
    other = new_uuid7()
    async with database.unit_of_work() as session:
        # Named *before* `grant`, deliberately. `grant` calls `ensure_workspace` with no
        # name (Task 1 Step 7), and `ensure_workspace` returns an existing row untouched —
        # so naming afterwards would silently do nothing and this assertion would read
        # "Workspace xxxxxxxx". Creating both named up front also exercises that
        # idempotency: `grant`'s later call must find these rows and leave them alone.
        await workspaces.ensure_workspace(session, workspace_id=workspace_id, name="Motor")
        await workspaces.ensure_workspace(session, workspace_id=other, name="Household")
        session.add(WorkspaceMemberRow(user_id=principal.id, workspace_id=other))

    await grant("analyst")  # supplies the membership in `workspace_id`

    response = api_client.get("/api/v1/me", headers=_headers(principal.id, workspace_id))
    assert response.status_code == 200, response.text
    named = {w["workspace_id"]: w["name"] for w in response.json()["workspaces"]}
    assert named == {str(workspace_id): "Motor", str(other): "Household"}
```

`_headers` comes from `backend/tests/test_api_datasets.py:30-35`. Check the existing `/me` test
module's fixture names before pasting — if it aliases `api_client` to `client`, follow that.

- [ ] **Step 2: Run the test to verify it fails**

Run:
```bash
uv run pytest backend/tests/test_api_me.py -k lists_every_membership -v
```
Expected: FAIL with `KeyError: 'workspaces'`.

- [ ] **Step 3: Add the shape and fill it**

In `backend/src/app/api/me.py`, beside `RoleAssignmentView`:

```python
class WorkspaceMembership(BaseModel):
    """One workspace this principal may act in, named (FR-395, FR-396)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workspace_id: str
    slug: str
    name: str
```

on `Me`:

```python
    workspaces: tuple[WorkspaceMembership, ...] = Field(
        default=(),
        description="Every workspace this principal is a member of, each named. A principal "
        "with more than one names its choice in the `Workspace-Id` header (FR-397); this "
        "is the list that choice is made from.",
    )
```

and in `get_me`, inside the existing `database.session()` block:

```python
        memberships = (
            await session.execute(
                select(WorkspaceRow)
                .join(
                    WorkspaceMemberRow,
                    WorkspaceMemberRow.workspace_id == WorkspaceRow.id,
                )
                .where(WorkspaceMemberRow.user_id == caller.principal.id)
                .order_by(WorkspaceRow.name)
            )
        ).scalars().all()
```

then in the `Me(...)` construction:

```python
        workspaces=tuple(
            WorkspaceMembership(workspace_id=str(w.id), slug=w.slug, name=w.name)
            for w in memberships
        ),
```

Import `WorkspaceMemberRow` and `WorkspaceRow` from `app.db.models`.

A Service Account has no `workspace_members` row — its workspace comes from the account itself —
so this list is empty for one. That is correct and not a bug: FR-397 says a Service Account
never sends the header. Say so in a comment beside the query.

- [ ] **Step 4: Run the test to verify it passes**

Run:
```bash
uv run pytest backend/tests/test_api_me.py -q
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/api/me.py backend/tests/test_api_me.py
git commit -m "feat(w32-7): /me names every workspace the caller may act in"
```

---

### Task 3: The verified `Workspace-Id` header

**Files:**
- Modify: `backend/src/app/api/deps.py:71-91` (`require_caller`), `:94-127` (`_single_workspace`), module docstring `:12-23`
- Modify: `backend/src/app/errors.py:46-52` — the stale comment
- Modify: `backend/tests/test_auth_users.py:121-140`
- Test: `backend/tests/test_auth_users.py`, `backend/tests/test_workspace_selection.py` (new)

**Interfaces:**
- Consumes: nothing from Tasks 1 and 2 at runtime — this task reads
  `AuthenticatedIdentity.workspaces`, which already exists.
- Produces: `require_caller(request, settings, workspace_id: Annotated[str | None,
  Header(alias="Workspace-Id", description=WORKSPACE_ID_DESCRIPTION)] = None) -> Caller`, and
  `_select_workspace(identity, selected: UUID | None) -> Caller` replacing `_single_workspace`.
- Produces: `WORKSPACE_ID_DESCRIPTION`, a module constant, exported in `__all__`.

**Where the header is declared, and why it is not on the routes.** FR-397 says *"declared on
the route, optional in the published contract and required in the handler, which is the shape
`If-Match` already uses."* `If-Match` is declared per route because only some routes take it.
`Workspace-Id` applies to every authenticated route, and FastAPI hoists a dependency's `Header(...)`
parameters into every operation that depends on it — so declaring it on `require_caller` puts it in
all ~40 operations' published parameters and therefore in the generated client, which is the
outcome the requirement is asking for, at one site instead of forty. Step 6 asserts that hoisting
actually happened rather than trusting it. If the assertion fails, fall back to declaring it per
route and say so in the ledger — the requirement's outcome is what binds, not the mechanism.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_workspace_selection.py`. Four tests, one per FR-396 obligation:

```python
"""FR-396 and FR-397: choosing a workspace, and the platform verifying the choice."""

from __future__ import annotations

import pytest

from app.api.deps import _select_workspace
from app.errors import PlatformError
from model_schema import new_uuid7

from backend.tests.test_auth_users import StubVerifier, _claims


@pytest.mark.req("FR-397")
async def test_a_selection_among_memberships_is_honoured(database, ...) -> None:
    """A choice among facts the platform already holds is not a claim (FR-397)."""
    identity, first, second = await _two_memberships(database)
    caller = _select_workspace(identity, second)
    assert caller.workspace_id == second


@pytest.mark.req("FR-397")
async def test_a_selection_outside_the_memberships_is_denied(database, ...) -> None:
    """**Negative.** The header is checked, never trusted — this is the whole requirement.

    A caller who is a genuine member of two workspaces names a third. If this passed, the
    header would be a claim rather than a choice, which is the invariant `deps.py` has
    carried since WK-658 and which FR-397 answers rather than overrides.
    """
    identity, _, _ = await _two_memberships(database)
    with pytest.raises(PlatformError) as exc:
        _select_workspace(identity, new_uuid7())
    assert exc.value.code == "WORKSPACE_SCOPE_DENIED"
    assert exc.value.status_code == 403


@pytest.mark.req("FR-396")
async def test_several_memberships_and_no_selection_is_refused(database, ...) -> None:
    """Refusing is the permanent rule; the header only gives a way to satisfy it."""
    identity, _, _ = await _two_memberships(database)
    with pytest.raises(PlatformError) as exc:
        _select_workspace(identity, None)
    assert exc.value.code == "WORKSPACE_SELECTION_REQUIRED"
    assert exc.value.status_code == 403


@pytest.mark.req("FR-396")
async def test_a_single_membership_needs_no_selection(database, ...) -> None:
    """A Service Account has exactly one by construction and never sends the header."""
    identity, only = await _one_membership(database)
    assert _select_workspace(identity, None).workspace_id == only
```

Write `_two_memberships` and `_one_membership` in this module, following
`test_auth_users.py:100-140`: authenticate with `StubVerifier(_claims(subject))`, add
`WorkspaceMemberRow`s, re-authenticate so `identity.workspaces` is populated. Both return the
identity and the ids. Do not import the private helpers if `test_auth_users` does not export them
— copy the six-line body rather than reaching across modules for it.

Then add the HTTP half, in the same file:

```python
@pytest.mark.req("FR-397")
def test_the_header_is_published_on_an_operation(api_client) -> None:
    """Declared on the dependency, and therefore on every operation that depends on it.

    Asserted rather than assumed: the whole reason for declaring it instead of reading the
    raw request is that a generated client should carry it, and nothing else in the suite
    would notice if FastAPI stopped hoisting it.
    """
    document = api_client.get("/openapi.json").json()
    names = [
        p["name"]
        for p in document["paths"]["/api/v1/me"]["get"].get("parameters", [])
    ]
    assert "Workspace-Id" in names
```

The path is `/openapi.json`, not `/api/v1/openapi.json` — `main.py:84` sets `openapi_url`, and
`test_api_me.py:64` and `test_api_authorisation_sweep.py:25` both use it. Cross-check against
`backend/src/app/main.py` before running.

- [ ] **Step 2: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_workspace_selection.py -v
```
Expected: FAIL with `ImportError: cannot import name '_select_workspace'`.

- [ ] **Step 3: Replace `_single_workspace` with `_select_workspace`**

In `backend/src/app/api/deps.py`:

```python
#: Reused as the header's OpenAPI description on every operation, so the published contract
#: says the same thing in each place. A generated client is written against this text.
WORKSPACE_ID_DESCRIPTION = (
    "The workspace to act in, as a UUID. Required when the principal is a member of more "
    "than one (`07` FR-397); a principal with exactly one, and a Service Account, send "
    "nothing. Checked against the principal's own memberships: a workspace it does not "
    "belong to yields `403 WORKSPACE_SCOPE_DENIED`, and an absent selection with several "
    "memberships yields `403 WORKSPACE_SELECTION_REQUIRED`."
)


def _select_workspace(identity: AuthenticatedIdentity, selected: UUID | None) -> Caller:
    """Collapse an authenticated identity to the one workspace it is acting in.

    Takes the header's **value**, not the `Request`. `require_caller` declares `Workspace-Id`
    as a parameter so that it appears in the published contract a client generates from, and
    a helper that then went behind the dependency's back to read the raw request would leave
    that declared parameter unused — which is how a documented header stops being the one the
    server actually reads.

    The selection is **checked, never trusted** (FR-396, FR-397). The invariant this
    module has carried since WK-658 — that a header-supplied workspace would make the scope a
    claim rather than a fact — refuses *trusting* the caller. A choice among memberships the
    platform already holds is not a claim; defaulting would be, which is why an absent
    selection is refused rather than resolved.
    """
    if not identity.workspaces:
        raise PlatformError(
            "UNAUTHENTICATED",
            "No workspace access",
            403,
            "This principal is authenticated but is a member of no workspace. Access is "
            "granted explicitly (FR-390); it is never the default.",
        )
    if selected is not None:
        if selected not in identity.workspaces:
            raise PlatformError(
                "WORKSPACE_SCOPE_DENIED",
                "Workspace scope denied",
                403,
                "The Workspace-Id header names a workspace this principal is not a member "
                "of. The selection is checked against the memberships the platform holds "
                "(07 FR-397); it is never taken on trust.",
            )
        chosen = selected
    elif len(identity.workspaces) > 1:
        raise PlatformError(
            "WORKSPACE_SELECTION_REQUIRED",
            "Workspace selection required",
            403,
            "This principal belongs to more than one workspace. Name one in the "
            "Workspace-Id header (07 FR-397); the platform will not choose for you.",
        )
    else:
        chosen = next(iter(identity.workspaces))

    return Caller(
        principal=identity.principal,
        workspace_id=chosen,
        environments=identity.environments,
        permissions=identity.permissions,
    )
```

Note what changed and what did not: the no-membership branch keeps `UNAUTHENTICATED` — FR-390
owns it and FR-396 does not touch it. Only the multi-membership branch gains a code of its own.

Delete the `from app.auth.service import AuthenticatedIdentity` / `assert isinstance(...)` pair at
the top of the old body: the import is already at module scope (`deps.py:39`), and a runtime
`assert` for a type the annotation states is dead weight `mypy --strict` already covers.

Add `WORKSPACE_ID_DESCRIPTION` to `__all__`.

- [ ] **Step 4: Declare the header on `require_caller`**

```python
async def require_caller(
    request: Request,
    settings: SettingsDep,
    workspace_id: Annotated[
        str | None, Header(alias="Workspace-Id", description=WORKSPACE_ID_DESCRIPTION)
    ] = None,
) -> Caller:
    """Resolve the caller, or refuse."""
    selected: UUID | None = None
    if workspace_id is not None:
        try:
            selected = UUID(workspace_id)
        except ValueError as exc:
            raise PlatformError(
                "WORKSPACE_SCOPE_DENIED",
                "Workspace scope denied",
                403,
                "The Workspace-Id header must be a UUID.",
            ) from exc

    authorization = request.headers.get("authorization", "")
```

and change both `_single_workspace(identity)` call sites to `_select_workspace(identity, selected)`.

`_development_caller` is untouched: it reads `x-dev-workspace-id`, which is a different header for
a different purpose, and FR-397 says so in as many words. Add a one-line comment at its call
site saying the selection does not apply there, so the omission reads as a decision.

Taking the header as `str | None` and parsing it here rather than annotating `UUID | None` is
deliberate: FastAPI would answer a malformed UUID with a `422` outside the platform error
catalogue, and FR-397 requires the refusal to be a typed platform error. Say so in a comment.

Add `Header` to the `fastapi` import.

- [ ] **Step 5: Update the module docstring and the stale comment**

`deps.py:12-23` currently says the capability is unbuilt: *"Until WK-692 builds that check, the multi-
membership caller below is refused rather than defaulted."* Rewrite that paragraph to describe what
the code now does — the check exists, the header carries the choice, and refusing an unverified
scope is still the rule.

`backend/src/app/errors.py:46-52` says the two codes are *"Registered ahead of the code that raises
them — WK-692 builds the header check; `_single_workspace` still refuses a multi-membership caller as
`UNAUTHENTICATED` until it does."* That is now false in three ways. Replace with:

```python
        # FR-396's workspace selection, and FR-397 (OQ-648, 2026-08-23) the
        # verified `Workspace-Id` header that carries it. Raised by `api.deps._select_workspace`.
```

- [ ] **Step 6: Update the test that asserted the old refusal**

`backend/tests/test_auth_users.py:121-140`,
`test_membership_of_several_workspaces_requires_a_choice`, calls `_single_workspace(identity)` and
asserts a bare 403. It must become a `_select_workspace(identity, None)` call asserting
`WORKSPACE_SELECTION_REQUIRED` — the behaviour is the same and the code is not, and a test that
only checks the status would go on passing if the code regressed to `UNAUTHENTICATED`.

Its two siblings at `:80-97` and `:100-117` also call `_single_workspace`; give both the second
argument `None`. Their assertions are unchanged.

- [ ] **Step 7: Run the tests to verify they pass**

```bash
uv run pytest backend/tests/test_workspace_selection.py backend/tests/test_auth_users.py -v
uv run pytest backend/tests -q
uv run mypy
```
Expected: all pass. A broad failure here usually means the header parameter changed
`require_caller`'s signature in a way a test that calls it directly did not expect — those call
sites need `workspace_id=None`.

- [ ] **Step 8: Commit**

```bash
git add backend/src/app/api/deps.py backend/src/app/errors.py
git add backend/tests/test_workspace_selection.py backend/tests/test_auth_users.py
git commit -m "feat(w32-7): a verified Workspace-Id header carries the caller's choice"
```

- [ ] **Step 9: Prove the check refuses on deliberately broken input**

The scope-denied branch is the requirement. Break it and watch the test catch it:

```bash
sed -i 's|if selected not in identity.workspaces:|if False:|' backend/src/app/api/deps.py
uv run pytest backend/tests/test_workspace_selection.py -q
git checkout -- backend/src/app/api/deps.py
git status --short backend/src/app/api/deps.py
```
Expected: `test_a_selection_outside_the_memberships_is_denied` FAILS, and `git status` prints
nothing after the restore. Record the message in the ledger.

---

### Task 4: A switch is audited into both chains

**Files:**
- Create: `backend/src/app/platform/workspace_switch.py`
- Modify: `backend/src/app/api/deps.py` — call it from `require_caller`
- Test: `backend/tests/test_workspace_selection.py`

**Interfaces:**
- Consumes: `audit.record(session, *, workspace_id, actor, source, action, entity_ref, before,
  after, justification, job_id)` from `backend/src/app/platform/audit.py:52-76`. It requires an
  **open transaction** and raises `RuntimeError` without one, so the call goes inside
  `database.unit_of_work()`.
- Produces: `record_switch(session, *, principal, left: UUID | None, entered: UUID) -> None`.

FR-396's fourth obligation: *"a switch is audited into both chains — `06` FR-372 chains
audit events per workspace, so recording only the workspace entered leaves the workspace left with
no record that the principal stopped acting there… The first selection after login has no chain to
leave and writes one event."*

`audit.record` takes a `pg_advisory_xact_lock` per workspace, so two events in two workspaces take
two locks in one transaction. Order them by `workspace_id` to keep the lock order total, or two
principals switching in opposite directions can deadlock. This is the one non-obvious hazard in the
task; the code below does it.

**Design question this task must raise, not answer.** `entity_ref` is a plain `str` on both
`audit.record` and `AuditEvent` (`model_schema/audit.py:58`) and nothing parses it, so
`workspace:<slug>@1` is writable today with no change to `ARTIFACT_TYPES`. But `workspace` is not
in that frozenset (`model_schema/refs.py:19-28`) and `ArtifactRef.parse` would reject the string,
so the event would carry a ref that does not round-trip. Options and a recommendation go in
[`../open-questions.md`](../open-questions.md) per `CLAUDE.md` §10 — do not add `workspace` to
`ARTIFACT_TYPES` inside this slice, because `refs.py:19-20` says extending it is a spec change
(`docs/contracts/schemas/common/artifact-ref.schema.json` carries the same list). Build against
whichever spelling the maintainer accepts; until then use `workspace:<slug>@1` and say in the
ledger that it does not parse.

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.req("FR-396")
async def test_a_switch_is_recorded_in_both_chains(database, ...) -> None:
    """`06` FR-372 chains per workspace, so one event answers only half the question.

    An auditor reconstructing "who was acting where, and when did they stop" reads the chain
    of the workspace they are auditing. A single event in the workspace entered is invisible
    from the workspace left — which is the one the auditor is usually looking at.
    """
    identity, first, second = await _two_memberships(database)
    async with database.unit_of_work() as session:
        await workspace_switch.record_switch(
            session, principal=identity.principal, left=first, entered=second
        )

    async with database.session() as session:
        recorded: dict[UUID, str] = {}
        for workspace in (first, second):
            events = (
                await session.execute(
                    select(AuditEventRow).where(
                        AuditEventRow.workspace_id == workspace,
                        AuditEventRow.action.like("workspace.%"),
                    )
                )
            ).scalars().all()
            assert len(events) == 1, f"{workspace} has {len(events)} switch events"
            recorded[workspace] = events[0].action
    assert recorded == {first: "workspace.left", second: "workspace.entered"}, (
        "each chain records its own side of the move, not a copy of the same event"
    )


@pytest.mark.req("FR-396")
async def test_the_first_selection_after_login_writes_one_event(database, ...) -> None:
    """No chain to leave. The requirement says one event, not a synthetic departure."""
    identity, first, second = await _two_memberships(database)
    async with database.unit_of_work() as session:
        await workspace_switch.record_switch(
            session, principal=identity.principal, left=None, entered=second
        )
    # assert exactly one event, in `second`, and none in `first`.
```

Fill in the elided assertions when writing — the plan states what they check; the executor writes
the four lines. Import `AuditEventRow` from `app.db.models`.

- [ ] **Step 2: Run the tests to verify they fail**

```bash
uv run pytest backend/tests/test_workspace_selection.py -k switch -v
```
Expected: FAIL with `ModuleNotFoundError: app.platform.workspace_switch`.

- [ ] **Step 3: Write `record_switch`**

```python
"""Auditing a workspace switch into both chains (`07` FR-396)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WorkspaceRow
from app.platform import audit
from model_schema import JobSource, Principal

__all__ = ["record_switch"]


async def record_switch(
    session: AsyncSession, *, principal: Principal, left: UUID | None, entered: UUID
) -> None:
    """Record the departure and the arrival, one event in each workspace's chain.

    `06` FR-372 chains audit events **per workspace**, so an event written only in the
    workspace entered is invisible from the workspace left — and "when did this principal
    stop acting here" is asked of the chain of the place they left. `left is None` is the
    first selection after login: there is no chain to leave, and one event is the whole
    record rather than half of one.

    The two events are written **in id order**. Each `audit.record` takes a per-workspace
    advisory lock inside this transaction, and two principals switching in opposite
    directions between the same pair would otherwise take the same two locks in opposite
    orders, which is a deadlock rather than a slow request.
    """
    entries: list[tuple[UUID, str]] = [(entered, "workspace.entered")]
    if left is not None and left != entered:
        entries.append((left, "workspace.left"))

    for workspace_id, action in sorted(entries):
        row = await session.get(WorkspaceRow, workspace_id)
        assert row is not None, f"no workspace row for {workspace_id}"
        await audit.record(
            session,
            workspace_id=workspace_id,
            actor=principal,
            source=JobSource.API,
            action=action,
            entity_ref=f"workspace:{row.slug}@1",
        )
```

Check `JobSource`'s members before pasting — use whatever the interactive-API source is called
(`grep -n "class JobSource" -A 8 packages/model-schema/src/model_schema/*.py`).

`sorted(entries)` sorts on the UUID first, which is the total order the docstring promises. Do not
"simplify" it to a fixed entered-then-left order.

- [ ] **Step 4: Run the tests to verify they pass**

```bash
uv run pytest backend/tests/test_workspace_selection.py -k switch -v
```
Expected: PASS.

- [ ] **Step 5: Call it from the request path**

A switch happens when the selected workspace differs from the one the principal was last acting
in. `require_caller` has no memory of the previous request, so the previous workspace has to come
from somewhere. **Two honest options, and this task must not pick silently:**

1. **Audit every selection, with `left=None`.** Correct and lossless per request, but writes an
   audit event on every authenticated request a multi-membership principal makes, which is a write
   and an advisory lock on the read path. Almost certainly unacceptable.
2. **Audit only at the point the selection changes**, which needs the previous selection stored —
   a session row, or a `last_workspace_id` on the user. That is state the platform does not have
   and is a design decision, not an implementation detail.

Record both in [`../open-questions.md`](../open-questions.md) with a recommendation for (2) and the
row it implies, and **leave the request-path call unbuilt in this slice**. `record_switch` and its
tests still land: they are the obligation's mechanism, and the trigger is what is open. Say so
explicitly in the ledger, and give FR-396's fourth obligation the §13 verdict *deferred with an
owner* rather than letting a passing test suite imply it is delivered.

- [ ] **Step 6: Commit**

```bash
git add backend/src/app/platform/workspace_switch.py backend/tests/test_workspace_selection.py
git commit -m "feat(w32-7): a workspace switch is recorded in both chains"
```

---

### Task 5: Run the gate and record what this slice found

**Files:**
- Modify: [`../roadmap.md`](../roadmap.md) — a slice record, appended
- Modify: [`../open-questions.md`](../open-questions.md) — two questions
- Create: `PL-00770-w32-7-workspace-identity-and-selection-execution-ledger.md`

**Interfaces:**
- Consumes: Tasks 1-4 complete and committed.

- [ ] **Step 1: Write the two open questions**

Follow the shape of the existing entries in [`../open-questions.md`](../open-questions.md) —
options, trade-offs, a recommendation, an owner, and the mirrored row in the module spec's §10 that
`.claude/skills/spec-change` requires:

1. **`workspace` as an artifact ref type.** Should `ARTIFACT_TYPES` and
   `artifact-ref.schema.json` gain `workspace`, so a switch event's `entity_ref` parses like every
   other? Options: add it (a spec change touching two files); keep the unparseable string; drop the
   ref shape for these events and use a bare id. Recommend adding it — an audit chain whose refs do
   not all parse is a chain a reader must special-case.
2. **What triggers a switch audit.** Task 4 Step 5's two options. Recommend storing the previous
   selection.

- [ ] **Step 2: Run the Python half of the gate**

```bash
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
```
Expected: every command exits 0. Check exit codes, not output text.

- [ ] **Step 3: Run the frontend half**

Task 2 and Task 3 both change the OpenAPI document — a new `Me.workspaces` field and a new header
parameter on every operation — so the client regenerates and must still type-check.

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build
```
Expected: every command exits 0. Inspect the regenerated client for the `Workspace-Id` parameter
and paste the relevant lines into the ledger — that artifact is the evidence FR-397's
"declared… in the published contract" clause is satisfied.

- [ ] **Step 4: Write the ledger and the slice record**

Create `docs/plans/PL-00770-w32-7-workspace-identity-and-selection-execution-ledger.md` with the real gate
output, the two deliberate-breakage proofs (Task 1 Step 10, Task 3 Step 9) and their failure
messages, and every place this plan was wrong.

Give each of FR-396's four obligations an explicit §13 verdict. Three should be *delivered and
tested*; the fourth — the switch trigger — is *deferred with an owner*, and the ledger says so
rather than letting `record_switch`'s green tests imply otherwise.

Then append the slice record to [`../roadmap.md`](../roadmap.md), following the W32-6 record's
shape, and note that `W6b-11` is unblocked.

- [ ] **Step 5: Commit**

```bash
git add docs/plans docs/roadmap.md docs/open-questions.md docs/specs/07-platform.md
git commit -m "docs(w32-7): record the workspace identity slice and its two open questions"
```
