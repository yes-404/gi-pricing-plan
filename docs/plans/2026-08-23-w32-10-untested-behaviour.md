# Untested W32 Behaviour Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test the three pieces of shipped W32 behaviour that no test exercises — a migration's
backfill, the EBM prediction route over HTTP, and the partial-dependence exposure share — so that
each has evidence rather than a plausible reading of the code.

**Architecture:** Three independent gaps, one per task, sharing only the reason they exist: each
was delivered with a test that passes whether or not the behaviour is right. The backfill has no
test at all, and **no test in this repository exercises a migration**, so Task 1 builds the first
one. The EBM predict route is proved at service level and asserted over HTTP only by a
contract-presence check and a 403. The exposure-share assertion is
`0.0 < share < 0.5`, which passes identically under the row-count definition the requirement
replaced — the test that was supposed to prove the fix cannot distinguish it from the bug.

**Tech Stack:** Python 3.12, `pytest`, Alembic, PostgreSQL 16, FastAPI `TestClient`, Polars,
XGBoost/LightGBM/interpret-EBM, `uv`.

**Spec:** [`../specs/01-data-management.md`](../specs/01-data-management.md) FR-DATA-51 (Task 1);
[`../specs/02-modelling.md`](../specs/02-modelling.md) FR-MODEL-124, FR-MODEL-37, FR-MODEL-62
(Task 2), FR-MODEL-118 and FR-MODEL-125 (Task 3).

**Proposed slice id:** `W32-10`. The W32 slice boundaries in
[`2026-08-22-w6b-slice-map.md`](2026-08-22-w6b-slice-map.md) are recorded as *pending* maintainer
acceptance and stop at `W32-6`; this is a proposal.

## Global Constraints

- **Tests only.** No production behaviour changes here. The one exception is Task 3 Step 4, which
  adds keyword forwarding to a **test helper** so the fixture the requirement needs can be built.
  If a task uncovers a real defect, stop and raise it — `CLAUDE.md` §0 — rather than adjusting the
  test until it passes.
- **Every test must fail against the behaviour it replaces.** Each task has an explicit step that
  breaks the implementation and confirms the new test catches it. `CLAUDE.md` §13: a check that has
  never printed a failure has not been tested. That step is not optional and its output goes in
  the ledger.
- Markers, exactly: Task 1 `FR-DATA-51`; Task 2 `FR-MODEL-124`, `FR-MODEL-37`, `FR-MODEL-62`
  stacked; Task 3 `FR-MODEL-118`, `FR-MODEL-125`. **Do not add `FR-MODEL-52`** to Task 3 — it is a
  different requirement about a different artifact and marking it here would report coverage the
  test does not give.
- All six ids exist. No `Next free:` marker.
- `pytest` runs `--strict-markers`, `asyncio_mode = "auto"`, `--import-mode=importlib`.
- Conventional Commits. Commit at the end of every task.

---

### Task 1: The dataset-owner backfill is exercised

**Files:**
- Create: `backend/tests/test_migration_dataset_owner.py`
- Read: `backend/migrations/versions/82edffbe1dce_dataset_owner.py:27-65`
- Test: the file above

**Interfaces:**
- Consumes: `_BACKFILL`, the module-level SQL constant in that migration.
- Produces: nothing importable — a test module only.

FR-DATA-51 gives a Dataset an owner. For a pre-existing Dataset the only record of who created it
is the audit chain, so the migration reads it back out with a `LIKE` over `entity_ref` and an
`ORDER BY sequence`. Four things in that query can be wrong in ways nothing would notice, and the
migration's own comment (`:27-36`) says two of them are load-bearing and pre-existing.

**Which shape of test.** Two are available and the choice matters:

1. **Shadow table.** `CREATE TEMP TABLE datasets (LIKE public.datasets INCLUDING ALL)`, drop the
   `NOT NULL` on `owner_id`, seed it, run `_BACKFILL` verbatim inside an uncommitted session.
   `pg_temp` precedes `public` on the search path, so `datasets` resolves to the shadow while
   `audit_events` still resolves to the real table. Fast, no scratch database, runs in the existing
   `database` fixture — but it cannot cover the `nullable=False` refusal, because that is
   `alter_column`, not `_BACKFILL`.
2. **Alembic against a scratch database.** Covers the refusal too, and is the only form that tests
   the migration rather than its SQL. Costs more: `env.py:66` calls `asyncio.run(...)` at import
   so `command.upgrade` must go through `asyncio.to_thread`; `versions/` has no `__init__.py` and
   the module names start with digits, so importing `_BACKFILL` needs
   `importlib.util.spec_from_file_location`.

**Do (1) for the resolution cases and (2) for the refusal**, in that order. The refusal is one test
and shape (1) carries the other six — five resolution cases in Step 3 plus the two mutation proofs
in Step 6, seven in total. Paying (2)'s setup for all seven is the wrong trade, and paying it for
none leaves the migration's most consequential branch — *refuse rather than invent an owner* —
unproven.

- [ ] **Step 1: Read the migration and copy nothing**

**Expect its comment to disagree with this plan, and trust the plan.** The comment at `:27-36`
cites three `platform/datasets.py` line numbers that have all since moved: `:191` → **`:205`**
(`dataset.created`, `dataset:{slug}@1`), `:868` → **`:951`** (`dataset.subject_purged`), `:271` →
**`:293`** (`dataset.dictionary_updated`). The behaviour it describes is unchanged and correct;
only the anchors rotted. Do not fix them in this slice — a tests-only slice that edits a merged
migration file, for any reason, is a diff a reviewer has to think about. Note the three in the
ledger instead.

```bash
sed -n '27,66p' backend/migrations/versions/82edffbe1dce_dataset_owner.py
```

Import `_BACKFILL` rather than pasting it. A test asserting against its own copy of the SQL proves
the copy works.

```python
import importlib.util
import pathlib

_MIGRATION = pathlib.Path("backend/migrations/versions/82edffbe1dce_dataset_owner.py")


def _backfill_sql() -> str:
    """Load `_BACKFILL` from the migration itself.

    `versions/` has no `__init__.py` and the module name starts with a digit, so it is not
    importable by name. Pasting the SQL into the test instead would test the paste.
    """
    spec = importlib.util.spec_from_file_location("_dataset_owner_migration", _MIGRATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module._BACKFILL)
```

Resolve `_MIGRATION` from `__file__` rather than the working directory.

- [ ] **Step 2: Write the shadow-table fixture**

```python
@pytest.fixture
async def shadow_datasets(database: Database) -> AsyncIterator[AsyncSession]:
    """A writable copy of `datasets` with `owner_id` nullable, in this transaction only.

    `pg_temp` precedes `public` on the search path, so `_BACKFILL`'s unqualified `datasets`
    resolves here while its `audit_events` still resolves to the real table — which is what
    lets the migration's SQL run **verbatim** against seeded audit rows. The transaction is
    never committed, so nothing outlives the test.
    """
    async with database.unit_of_work() as session:
        await session.execute(text(
            "CREATE TEMP TABLE datasets (LIKE public.datasets INCLUDING ALL) ON COMMIT DROP"
        ))
        await session.execute(text("ALTER TABLE pg_temp.datasets ALTER COLUMN owner_id DROP NOT NULL"))
        yield session
        await session.rollback()
```

Confirm `INCLUDING ALL` does not copy the foreign keys in a way that fights the temp table — if it
does, drop to `INCLUDING DEFAULTS` and add the columns the query needs. Verify the fixture works at
all before writing five tests on top of it.

- [ ] **Step 3: Write the failing tests**

```python
@pytest.mark.req("FR-DATA-51")
async def test_the_backfill_resolves_an_owner_from_the_creation_event(shadow_datasets) -> None:
    """The happy path, and the only one the migration was shipped with any confidence in."""
    workspace, actor = new_uuid7(), new_uuid7()
    await _seed_dataset(shadow_datasets, workspace, slug="motor-ad")
    await _seed_event(shadow_datasets, workspace, "dataset.created", "dataset:motor-ad@1", actor)
    await shadow_datasets.execute(text(_backfill_sql()))
    assert await _owner_of(shadow_datasets, "motor-ad") == actor


@pytest.mark.req("FR-DATA-51")
async def test_the_earliest_creation_event_wins_by_sequence(shadow_datasets) -> None:
    """`ORDER BY sequence`, not `at`.

    The migration's comment says `at` has no defined order within a millisecond
    (`AuditEventRow:198-201`), so two events written in the same millisecond would resolve
    arbitrarily under an `at` ordering — and the test would pass most of the time, which is
    worse than failing.
    """
    # two `dataset.created` rows, later `sequence` carrying the *earlier* `at`,
    # and the assertion names the lower-sequence actor.


@pytest.mark.req("FR-DATA-51")
async def test_a_slug_that_prefixes_another_does_not_borrow_its_owner(shadow_datasets) -> None:
    """**Negative.** `LIKE 'dataset:' || slug || '@%'` and not `LIKE 'dataset:' || slug || '%'`.

    `motor` and `motor-ad` are ordinary neighbouring slugs. Without the `@` the first would
    resolve to the second's creator, silently and only for datasets whose names happen to
    nest — the kind of defect that survives review and appears as a governance question a
    year later.
    """
    # seed `motor` with no event of its own, seed `dataset:motor-ad@1` with an actor,
    # run the backfill, assert `motor`'s owner is still NULL.


@pytest.mark.req("FR-DATA-51")
async def test_any_version_in_the_ref_resolves(shadow_datasets) -> None:
    """`@%`, deliberately, and the migration's comment at :31-36 says why.

    `dataset.created` writes `@1` today, but `platform/datasets.py:951` writes a UUID where
    the rest write the slug and `:293` omits `@version` altogether. Those inconsistencies are
    what the migration must survive; narrowing to `@1` would stop resolving rows the day one
    of them is fixed. Asserting `@7` resolves is what stops a later tidy-up from narrowing it.
    """


@pytest.mark.req("FR-DATA-51")
async def test_the_inconsistent_refs_are_not_picked_up(shadow_datasets) -> None:
    """**Negative**, and the only way those two inconsistencies are reachable at all.

    `dataset.subject_purged` writes `dataset:<uuid>@1` (`datasets.py:951`) and
    `dataset.dictionary_updated` writes `dataset:<slug>` with no `@` (`:293`). Neither is a
    `dataset.created`, so the action filter should exclude them — and the `LIKE` should
    exclude them independently. Planting both and proving neither resolves tests both
    guards, so removing either one fails here.
    """
```

Write `_seed_dataset`, `_seed_event` and `_owner_of` as small `text()` inserts against the shadow
table and the real `audit_events`. `audit_events.actor` is JSONB holding a `Principal` — build it
from the `model-schema` type and dump it rather than hand-writing the JSON (`CLAUDE.md` §2).
`audit_events` may also require chain columns (`sequence`, a hash); read `AuditEventRow` around
`AuditEventRow` and supply **every** `nullable=False` column, which is more than the hash and
sequence pair: `workspace_id` (`:175`), `actor` (`:180`, JSONB), `source` (`:181`), `action`
(`:184`), `entity_ref` (`:185`), `event_hash` (`:196`) and `sequence` (`:201`). `id` (`:174`) has a
PK default and `at` (`:176`) a server default, so neither needs supplying. Reading only `:190-210`
finds two of the seven and the insert then fails on the first of the other five.

- [ ] **Step 4: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_migration_dataset_owner.py -v
```
Expected: FAIL — most likely on the fixture or the seed helpers first. Get them green one at a
time. A test that errors in setup is not evidence the query is wrong.

- [ ] **Step 5: Make them pass**

No production change should be needed: the backfill is believed correct and this task is proving
it. **If one of the five genuinely fails, that is a real defect in shipped behaviour** — stop,
record it, and raise it rather than weakening the test.

Run:
```bash
uv run pytest backend/tests/test_migration_dataset_owner.py -v
```
Expected: all five PASS.

- [ ] **Step 6: Prove each negative bites**

Two mutations of the SQL, run against the loaded copy rather than the file, so nothing on disk
changes:

```python
@pytest.mark.req("FR-DATA-51")
async def test_a_prefix_matching_backfill_would_be_caught(shadow_datasets) -> None:
    """The negative above, proven to bite: widen the LIKE and it must resolve wrongly."""
    widened = _backfill_sql().replace("|| '@%'", "|| '%'")
    # same seeding as the prefix test, run `widened`, assert `motor` DID borrow the owner —
    # which is what the real query must not do.
```

Do the same for the action filter (`AND a.action = 'dataset.created'` removed). Both prove the
guard is load-bearing rather than incidental.

- [ ] **Step 7: Prove the refusal, through alembic**

The `alter_column(nullable=False)` at `:61` is the migration's most consequential line — *inventing
an owner for a governed field is worse than a migration that refuses*. It is unreachable from the
shadow table, so this one test runs the real thing.

```python
@pytest.mark.req("FR-DATA-51")
async def test_an_unresolvable_dataset_stops_the_migration(scratch_database) -> None:
    """**Deliberately broken input.** A dataset with no creation event has no owner.

    The migration must refuse and name the table, not invent one. This is the branch the
    requirement's governance argument rests on, and it is the one the shadow-table tests
    cannot reach.
    """
```

The fixture creates a scratch database, upgrades to the revision **before** `82edffbe1dce`
(`down_revision` is `7c1a9e40b3d2`), inserts a dataset with no `dataset.created` event, then
upgrades one more and asserts it raises. Two mechanics to get right:

- `backend/migrations/env.py:66` calls `asyncio.run(...)` at import, so calling
  `alembic.command.upgrade` from an async test deadlocks. Wrap it: `await asyncio.to_thread(command.upgrade, cfg, "82edffbe1dce")`.
- The config needs the DSN. `alembic.ini` carries none — set it from the same environment variable
  the app uses (`.claude/skills/dev-commands` has the form).

Skip this test cleanly when no database is reachable, matching `conftest_db.py:42-72`'s idiom.

If the scratch-database fixture turns out to cost more than a task's worth of work, **stop and say
so** rather than dropping the coverage silently: record the refusal branch as *delivered but
untested* with an owner (`CLAUDE.md` §13), and land the seven shadow-table tests that do work.

- [ ] **Step 8: Commit**

```bash
git add backend/tests/test_migration_dataset_owner.py
git commit -m "test(w32-10): the dataset owner backfill resolves, and refuses"
```

---

### Task 2: The EBM prediction route over HTTP

**Files:**
- Modify: `backend/tests/test_prediction.py` — add under the `# -- Over HTTP` banner at `:686`
- Test: the file above

**Interfaces:**
- Consumes: `_fitted_ebm(database, blob_store, workspace_id) -> tuple[Principal, UUID]` at
  `test_prediction.py:139` — a **helper coroutine, not a fixture**; `ROWS` at `:76`; `_headers`,
  imported at `:35` from `test_api_datasets`.
- Produces: nothing importable.

FR-MODEL-124 makes ad-hoc scoring a route. The EBM arm is proved at service level
(`test_an_ebm_is_scored_and_states_that_its_type_has_no_interval`, `:536-567`) and over HTTP only
by a contract-presence check and a no-permission 403 (`:689-715`) — so the route returning the
right number for an EBM is currently inferred from the service test plus the fact that the route
calls the service.

**What the service test already establishes**, and what this task must not re-litigate: an EBM
scores, `model_type == "ebm"`, `uncertainty.kind is UncertaintyKind.UNAVAILABLE` with
`reason is UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL`, every row's `lower`/`upper` is `None`,
and `ROWS[0]` and `ROWS[1]` score differently. The HTTP test's job is to prove the **route** says
all of that too, not to re-derive it.

**Two mechanics to expect, and the second is a blocker unless it is fixed first.**

`_fitted_ebm`'s actor comes from `test_model_jobs._actuary` (`:144-165`) and already holds
`analyst` + `pricing_actuary`, so `_headers(actor.id, workspace_id)` needs no `grant` call. The
`database` side is fine too: `api_settings` (`backend/tests/conftest.py:38-53`) reuses
`conftest_db.test_database_url()`, so the model row the fixture writes is the row the app reads.

**The blob store is not fine.** The two halves point at different buckets:

| Side | Bucket | Where |
|---|---|---|
| `blob_store` fixture | `$GIP_TEST_BUCKET`, default **`gip-test-blobs`** | `backend/tests/conftest_db.py:81` |
| the app under `api_client` | **`gip-blobs`** — `Settings.blob_bucket`'s default, because `api_settings` never sets it | `backend/src/app/config.py:115` |

So the fit writes the EBM artifact to one bucket and the route looks for it in another. Written as
drafted, this test asserts against a 500.

There is **no dependency-override mechanism to fall back on** — `grep -rn "dependency_overrides"
backend/` returns nothing; `api_settings` shares the database purely by reusing the DSN, and the
same trick is the fix here. Before Step 1, add `blob_bucket` to `api_settings` so both sides read
one value:

```python
    return Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=os.environ.get("GIP_TEST_BUCKET", "gip-test-blobs"),
    )
```

That is a change to a shared fixture, so run the whole `backend/tests` suite after it, not just
this file. It is also the only edit in this plan outside a test body and a test helper; name it in
the ledger.

One thing the plan did get right: there is precedent for `async def test(api_client: TestClient,
…)` (`test_custom_objectives.py:636, 662`), but neither of those uses `blob_store`, so this is
still the first test in the suite to combine the two.

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.req("FR-MODEL-124")
@pytest.mark.req("FR-MODEL-37")
@pytest.mark.req("FR-MODEL-62")
async def test_an_ebm_scores_over_http(
    api_client: TestClient, database, blob_store, workspace_id
) -> None:
    """FR-MODEL-124 for the EBM arm at the edge, which nothing asserts today.

    The route's own tests prove it is published (`:690`) and that it refuses without the
    permission (`:703`). Neither would notice if the EBM branch returned the GLM's numbers,
    the intercept for every row, or a 500 — the whole of scoring over HTTP is inferred from
    a service test plus the fact that the router calls the service.

    Asserted against the **service's own** output rather than a literal: a hard-coded number
    would pin this to one interpret/EBM version and would say nothing about whether the
    route and the service agree, which is the only thing HTTP adds here.
    """
    actor, model_id = await _fitted_ebm(database, blob_store, workspace_id)

    async with database.session() as session:
        expected = await service.predict_rows(
            session,
            workspace_id=workspace_id,
            actor=actor,
            model_id=model_id,
            rows=ROWS,
            blob_store=blob_store,
        )

    response = api_client.post(
        f"/api/v1/models/{model_id}/predict",
        json={"rows": ROWS},
        headers=_headers(actor.id, workspace_id),
    )
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["model_type"] == "ebm"
    assert len(body["rows"]) == len(ROWS)
    assert [row["expected"] for row in body["rows"]] == [
        pytest.approx(row.expected, rel=1e-9) for row in expected.rows
    ]
```

`ROWS` is a list of plain dicts at `:76`, so it serialises as the request body unchanged; confirm
that with `sed -n '76,90p' backend/tests/test_prediction.py` before relying on it. If it holds
non-JSON values, dump it through the request model rather than hand-writing a JSON copy
(`CLAUDE.md` §2 — nobody hand-writes a shape `model-schema` already defines).

- [ ] **Step 2: Write the interval-refusal test**

`02` §5.3's Prediction view promises the interval where the model type offers one and **the refusal
by name** where it does not. The service names it; the route must carry the name, not three nulls.

```python
@pytest.mark.req("FR-MODEL-124")
@pytest.mark.req("FR-MODEL-62")
async def test_the_ebm_refusal_reaches_the_client_by_name(
    api_client: TestClient, database, blob_store, workspace_id
) -> None:
    """Three nulls and a named refusal are indistinguishable to a client that only sees
    `lower`/`upper`, and they mean different things: one is "no interval for this model
    type", the other could be a fit that failed to produce one. The service distinguishes
    them (`:562-565`); this proves the wire does too.
    """
    actor, model_id = await _fitted_ebm(database, blob_store, workspace_id)

    response = api_client.post(
        f"/api/v1/models/{model_id}/predict",
        json={"rows": ROWS},
        headers=_headers(actor.id, workspace_id),
    )
    assert response.status_code == 200, response.text
    uncertainty = response.json()["uncertainty"]

    assert uncertainty["kind"] == UncertaintyKind.UNAVAILABLE.value
    assert uncertainty["reason"] == UnavailableReason.MODEL_TYPE_HAS_NO_INTERVAL.value
    assert uncertainty["level"] is None
    assert all(
        row["lower"] is None and row["upper"] is None for row in response.json()["rows"]
    )
```

Both enums are already imported in this module (the service test at `:562-564` uses them). Check
the serialised spelling — if the enum values are not the strings the API emits, assert the emitted
strings and say in a comment where they come from.

- [ ] **Step 3: Run the tests to verify they fail**

Run:
```bash
uv run pytest backend/tests/test_prediction.py -k "over_http or refusal_reaches" -v
```
Expected: FAIL. If the failure is a fixture, blob-store or visibility error rather than an
assertion, fix that first — see the mechanics above. A test that errors in setup is not evidence
about the route.

- [ ] **Step 4: Make them pass**

No production change is expected: the route is believed correct and this task is proving it. **If
either genuinely fails on its assertion, that is a defect in shipped behaviour** — stop, record it,
and raise it under `CLAUDE.md` §0 rather than adjusting the test.

Run:
```bash
uv run pytest backend/tests/test_prediction.py -v
```
Expected: PASS.

- [ ] **Step 5: Prove the tests would catch a wrong arm**

The gap is that the route could score an EBM as something else and nothing would notice. Prove it
is closed:

```bash
grep -rn "ebm" backend/src/app/platform/prediction.py | head
```

Find where the arm is dispatched, force it to the GLM branch with a one-line `sed`, run both new
tests, and confirm **both** FAIL — the first on the numbers, the second on `model_type`/`reason`.
Restore with `git checkout --` and verify with `git status --short`. Record both failure messages
in the ledger.

If the dispatch turns out to live in `pricing-core` rather than the service, break it there
instead. The point is that a wrong prediction now fails wherever the wrongness would come from.

- [ ] **Step 6: Commit**

```bash
git add backend/tests/test_prediction.py
git commit -m "test(w32-10): an EBM scores over HTTP, not only at the service boundary"
```

---

### Task 3: The partial-dependence share is exposure, not rows

**Files:**
- Modify: `packages/pricing-core/tests/test_gbm.py:599-627` (`_diagnose` — keyword forwarding)
- Modify: `packages/pricing-core/tests/test_gbm.py:1827-1851` — add beside the existing assertion
- Test: the file above

**Interfaces:**
- Consumes: `_diagnose(backend, factors=None, *, data=None, …) -> (fit, diagnostics)` at `:599`;
  `_curve_for(diagnostics, factor_slug)` at `:630`; `_factor(slug, column, **over) -> Factor` at
  `:64`; `BACKENDS = ["xgboost", "lightgbm"]` at `:59`.
- Produces: `_capped_book()` — the discriminating fixture.

W32-5 changed `OmittedLevels.exposure_share` from a row-count share to an exposure share. The test
that was supposed to prove it asserts `0.0 < wide.omitted.exposure_share < 0.5` (`:1847`), **which
passes under both definitions**. The requirement's whole content is untested.

**Why a new fixture is needed.** `_diagnose_wide` (`:1813-1824`) forwards `**over` to
`compute_gbm_diagnostics` but hard-codes `_wide_book()` and its two factors; `_diagnose`
(`:599-627`) takes a `data` frame but forwards no keywords. The test needs both — a frame whose
exposure and row counts disagree, and `max_partial_dependence_levels` low enough to force an
omission on it. Step 3 adds `**over` to `_diagnose`, which is the smaller change and the one that
leaves the helper more useful.

**The fixture, and why these numbers.** Three levels, `max_partial_dependence_levels=2`:

| level | rows | exposure each | total exposure |
|---|---|---|---|
| `heavy_a` | 2 | 100.0 | 200.0 |
| `heavy_b` | 2 | 100.0 | 200.0 |
| `common_light` | 400 | 0.01 | 4.0 |

Total exposure 404.0, total rows 404.

- Ranking by **exposure** keeps both heavies and drops `common_light`: share `4.0/404.0 ≈ 0.00990`.
- Ranking by **rows** keeps `common_light` and one heavy, dropping the other: share `2/404 ≈ 0.00495`.

`omitted.levels == 1` either way, so the level count cannot be the assertion — the share is the only
observable that separates them, which is exactly the property the current test lacks.

- [ ] **Step 1: Write the fixture**

```python
def _capped_book() -> pl.DataFrame:
    """Three levels whose exposure ranking and row-count ranking disagree.

    Built so that `exposure_share` reports a different number under each definition of
    "share": exposure keeps the two heavy levels and drops the 400 light rows (4.0/404.0),
    while row counts keep the light level and drop one heavy (2/404). One omitted level
    either way, so the count cannot tell them apart and the share is the whole test.
    """
```

Give it the response and offset columns `_spec`/`fit_gbm` need — copy the column set from
`_wide_book` (**`:1766-1787`** — not `:1790-1810`, which is `_crossable_book`, a different fixture
with no `vehicle_group` column at all) and change only the factor column and the exposure.

**Put the exposure in the column the weighting actually reads.** `_weights`
(`packages/pricing-core/src/pricing_core/modelling/diagnostics.py:128-134`) checks the **offset**
column first and only falls back to the weight column:

```python
    if spec.offset.kind in {"log_column", "column"} and str(spec.offset.column) in data.columns:
        return data[str(spec.offset.column)].cast(pl.Float64).to_numpy()
    if spec.weight.kind == "column" and str(spec.weight.column) in data.columns:
        return data[str(spec.weight.column)].cast(pl.Float64).to_numpy()
    return np.ones(data.height, dtype=np.float64)
```

So the 100.0/0.01 values must land in whichever column `_spec` declares as its offset. Populate
the weight column instead and `_weights` returns the offset — or, if neither is declared, a vector
of ones, at which point exposure ranking *is* row ranking and the fixture stops discriminating
while still looking correct. Read `_spec` before writing the frame, and assert the arithmetic:
`assert _weights(spec, book).sum() == pytest.approx(404.0)` is one line and it catches all three
failure modes.

Determinism matters too: the test asserts an exact share, so use fixed values rather than a draw, exactly as
`_diagnose`'s docstring (`:607-613`) says a caller checking arithmetic must.

- [ ] **Step 2: Write the failing test**

```python
@pytest.mark.req("FR-MODEL-118")
@pytest.mark.req("FR-MODEL-125")
@pytest.mark.parametrize("backend", BACKENDS)
def test_the_omitted_share_is_exposure_and_not_row_count(backend: str) -> None:
    """FR-MODEL-125: the share is **exposure**, which the existing assertion cannot check.

    `0.0 < share < 0.5` at :1847 passes under both definitions, so W32-5's change is
    untested — the fixture there has no disagreement between the two rankings for it to
    detect. This one does: exposure drops the 400 light rows (4.0/404.0 ≈ 0.0099) while row
    counts would drop one heavy level (2/404 ≈ 0.0050). One level omitted either way, so the
    share is the only thing that separates them.

    An exposure share is what the sentence under the chart means. A curve omitting levels
    holding 1% of the book is a footnote; one omitting levels holding 40% is a warning, and
    row counts answer neither question in a book where exposure is the unit of risk.
    """
    frame = _capped_book()
    _, diagnostics = _diagnose(
        backend,
        [_factor("vehicle_group", "vehicle_group")],
        data=frame,
        max_partial_dependence_levels=2,
    )
    assert diagnostics.gbm is not None
    curve = _curve_for(diagnostics, "vehicle_group")  # the helper at :630, not a dict rebuild
    assert curve.omitted is not None
    assert curve.omitted.levels == 1, "one level omitted under either definition — see docstring"
    assert curve.omitted.exposure_share == pytest.approx(4.0 / 404.0, rel=1e-6)
    assert curve.omitted.exposure_share != pytest.approx(2 / 404, rel=1e-6)
```

The last line is redundant arithmetic and deliberately kept: it states in the test what the
docstring argues, so a future reader changing the fixture sees immediately that the two numbers
must stay apart.

`_diagnose` sets `train = holdout = data` when `data` is given (`:620-622`), which is what makes an
exact-share assertion possible at all — `_diagnose_wide` takes two independent draws, so the share
it produces is not a number a test can pin down. That is the second reason this task cannot reuse
it.

- [ ] **Step 3: Run the test to verify it fails**

Run:
```bash
uv run pytest packages/pricing-core/tests/test_gbm.py -k omitted_share -v
```
Expected: FAIL with `TypeError: _diagnose() got an unexpected keyword argument
'max_partial_dependence_levels'`.

- [ ] **Step 4: Forward keywords from `_diagnose`**

At `:599-606`, add `**over: object` to the signature, and at `:622-627` pass `**over` into
`compute_gbm_diagnostics` — the same shape `_diagnose_wide` already uses at `:1823`, including its
`# type: ignore[arg-type]` if `mypy` asks for it.

Extend the docstring with one sentence: keywords pass through to `compute_gbm_diagnostics`, which
is what lets a caller supply both its own frame and a diagnostics option — the combination neither
helper offered.

- [ ] **Step 5: Run the test to verify it passes**

Run:
```bash
uv run pytest packages/pricing-core/tests/test_gbm.py -k omitted_share -v
```
Expected: PASS for both backends.

If it fails on the share value, check the fixture arithmetic before touching the implementation —
the exposure column name and the weight the sweep actually uses are the two likely culprits, and
`compute_gbm_diagnostics` reading a different weight column than the fixture sets would produce a
plausible wrong number.

- [ ] **Step 6: Prove it fails against the definition it replaced**

This is the point of the whole task. Revert the behaviour and watch the test catch it:

```bash
grep -n "exposure_share" packages/pricing-core/src/pricing_core/modelling/*.py
```

Find the omitted-levels share computation, replace the exposure sum with a row count, run:

```bash
uv run pytest packages/pricing-core/tests/test_gbm.py -k "omitted_share or categorical_grid" -v
```
Expected: the new test FAILS with `0.00495 != 0.00990`, and the **existing** test at `:1847` still
PASSES — which is the finding, demonstrated rather than argued. Restore with `git checkout --`,
verify with `git status --short`, and put both outcomes in the ledger.

- [ ] **Step 7: Commit**

```bash
git add packages/pricing-core/tests/test_gbm.py
git commit -m "test(w32-10): the omitted-level share is exposure, proven against row counts"
```

---

### Task 4: Run the gate and record the verdicts

**Files:**
- Modify: [`../roadmap.md`](../roadmap.md) — a slice record, appended
- Create: `2026-08-23-w32-10-untested-behaviour-ledger.md`

**Interfaces:**
- Consumes: Tasks 1-3 complete and committed.

- [ ] **Step 1: Run the Python half of the gate**

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

**Only FR-MODEL-125 gains its first evidence.** The other two are already marked: FR-DATA-51 six
times in `backend/tests/test_api_datasets.py` (`:1053, 1063, 1094, 1107, 1133, 1164`) and
FR-MODEL-124 at `backend/tests/test_prediction.py:537` and
`backend/tests/test_paired_quantile_models.py:782`. Their coverage line will not move, and that is
expected rather than a sign a marker was missed — this slice deepens their evidence, it does not
create it. If the FR-MODEL-125 line does **not** move from zero, a marker is wrong; check that one
specifically.

`req-coverage.py` should now report evidence against FR-DATA-51, FR-MODEL-124 and FR-MODEL-125 that
it did not before. Paste those rows into the ledger — they are the point of the slice.

The frontend half is **not** required: this slice is tests only and touches no contract. Say so in
the ledger rather than silently skipping it.

- [ ] **Step 2: Write the ledger**

Create `docs/plans/2026-08-23-w32-10-untested-behaviour-ledger.md` with the gate output, the three
deliberate-breakage proofs and their exact failure messages, and — if Task 1 Step 7's scratch
database proved too costly — the explicit `CLAUDE.md` §13 verdict recorded against the refusal
branch, with an owner.

Record anything a task uncovered that it did not fix, each as its own verdict rather than as a note.

- [ ] **Step 3: Append the slice record**

Add it to [`../roadmap.md`](../roadmap.md) following the W32-6 record's shape, naming which
requirements gained evidence and which remain *delivered but untested*.

- [ ] **Step 4: Commit**

```bash
git add docs/
git commit -m "docs(w32-10): record the test-hardening slice and its verdicts"
```
