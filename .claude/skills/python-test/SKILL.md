---
name: python-test
description: Testing discipline for this repo — requirement-traceability markers, the negative-test emphasis a governed system needs, pytest configuration, and how to run the suite in an environment without pip. Use when writing or running tests, adding a test marker, or checking which requirements the suite actually covers.
---

# Testing here

```bash
uv run pytest -q
uv run python scripts/req-coverage.py     # which requirements the suite claims
```

## Every test names the requirement it satisfies

```python
@pytest.mark.req("FR-OVR-7")
def test_money_minor_refuses_floats(): ...
```

`scripts/req-coverage.py` turns those marks into a traceability report and **fails when a
test claims a requirement that does not exist** — catching typos and any renumbering that
breaks the append-only rule (`CLAUDE.md` §5).

Coverage is currently *reported, not gated*. At 1.7 % a threshold would fail every build
and teach everyone to ignore it; it earns a floor once a phase's requirements are meant to
be complete.

## Write the negative test first

This is the habit that matters most here. For a governed system the suite has to prove the
wrong thing **cannot** happen, not merely that the right thing can:

- a float is **refused** in the money path, not coerced
- an artifact envelope **cannot** be mutated
- the generated JSON Schema **does not admit** a payload the spec forbids
- a submitter **cannot** approve their own request (`06` NFR-GOV-8)

A suite that only demonstrates the happy path will pass while the invariant it exists to
protect is quietly broken.

## Pin the case where a choice actually bites

Prefer an assertion that fails if the behaviour changes over one that merely documents it:

```python
# 24150 * 1.15 == 27772.5 exactly — a tie, so the rounding mode alone decides.
assert apply_factor(24150, Decimal("1.15"), "half_even") == 27772
assert apply_factor(24150, Decimal("1.15"), "half_up")   == 27773
```

That pair is worth more than either line alone: it shows the mode changes the answer, which
is *why* FR-RATE-12 makes rounding an explicit per-step declaration. (The half-even value
is also the one intuition gets wrong.)

## Configuration

- **`--import-mode=importlib`** — the mode pytest recommends for new projects, and required
  here because each package owns a `test_money.py`; the legacy `prepend` mode collides on
  the basename.
- **`--strict-markers`** — an unregistered marker is an error, so a typo'd `@pytest.mark.req`
  fails rather than silently doing nothing.
- Markers registered in the root `pyproject.toml`. Fixtures in `conftest.py`.

## Running the real toolchain in a sandbox without pip

`uv` itself installs from PyPI as a manylinux wheel, so the whole CI job runs locally even
with no `pip` and no `ensurepip`:

```bash
# one-off: fetch the uv wheel and unzip it (see library-spike for the recipe)
UV="$SP/libs/uv-*/data/scripts/uv"
export UV_CACHE_DIR="$SP/uvcache" UV_PYTHON_INSTALL_DIR="$SP/uvpy"
"$UV" sync --all-packages --dev
"$UV" run ruff check . && "$UV" run mypy && "$UV" run lint-imports && "$UV" run pytest -q
```

**Prefer this over hand-fetched wheels.** It resolves the versions CI resolves, so a pass
here means something. The `PYTHONPATH` approach in `library-spike` remains useful for a
throwaway spike on one library, but it is not a substitute for the gate.

## A green `pytest -q` with no database is a **partial** run

`backend/tests/conftest_db.py` **skips** rather than fails when nothing is listening on
5432, so a developer without the stack can still run the unit tests. The cost is that a run
which never touched Postgres reports the same cheerful summary as one that did — and every
migration, trigger, privilege and `FOR UPDATE` test is among the ones that did not run.

Bring the stack up first, and pass the DSN:

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
export GIP_TEST_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
uv run pytest -q            # ~740 tests; without the DSN it is ~90 fewer, silently
```

**The DSN is not optional and not the default.** The compose credentials are
`gipricing:gipricing` (`deploy/docker-compose.yml`), while the application's default
settings use `gip` — so `alembic` and the suite both fail with
`InvalidPasswordError: password authentication failed for user "gip"` until
`GIP_DATABASE_URL` / `GIP_TEST_DATABASE_URL` is set. The error names the *user*, which is
the fastest way to recognise it.

```bash
export GIP_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
uv run alembic upgrade head
uv run alembic downgrade -1 && uv run alembic upgrade head   # prove the downgrade too
```

## Assert on a metric that responds to what the fixture changed

Two fits of the same factor differing only in regularisation **tie on Gini**, and a test that
expected the unpenalised one to win fails for a reason that looks like a bug and is not: Gini
is computed from the *ordering* of predicted rates, and shrinkage moves every level toward the
grand mean without ever swapping two of them. Rank-based metrics — Gini, lift, anything built
on `_bin_index` — cannot see a change that preserves order.

Pick the metric by what the fixture perturbed:

| The fixture changed | Assert on |
|---|---|
| which factors are in the model | Gini, normalised Gini, lift |
| the *magnitude* of a prediction (regularisation, an offset, a base level) | deviance, A/E, calibration |
| the ordering of two models against each other | double lift |

And prefer a fixture whose answer you can state before the run. "The model fitted on the
factor that drives the risk must beat the one fitted on noise" is a known answer; "the leader
is not null" passes against a leader chosen by dictionary order.

## Getting a *different* weighting scheme into a fixture

`_weighting` reads the spec: an exposure offset means `exposure`, a weight column means
`claim_count`, neither means `count`. Building a second scheme is not as simple as dropping the
offset, because `GlmSpec` refuses a Poisson model without one (FR-MODEL-19) — the only route
the contract allows is a genuine severity model:

```python
GlmSpec(..., response_column="avg_cost", family="gamma",
        offset=OffsetSpec(kind="none"),
        weight=WeightSpec(kind="column", column="claim_count"))
```

Two consequences for the fixture: the response column must be **strictly positive** (Gamma
refuses zeros outright, and a book's `claim_count` has plenty), and it should be fitted on
claim-bearing rows only — otherwise `glum` divides by a zero weight and the run is noisy for a
reason that has nothing to do with the test.

## Constructing a **fitted** model row: the write order is forced

Three guards on `models` interact, and only one order satisfies all three. A fixture that
needs a fitted model — a second version for a supersession test, say — has to do this:

```python
row = ModelRow(..., status="draft")   # no fit_result, no diagnostics_id
session.add(row); await session.flush()          # 1. the model exists, so it can be named
session.add(DiagnosticsRow(model_id=row.id, payload=...))
await session.flush()                            # 2. the evidence exists
row.fit_result, row.diagnostics_id, row.status = fit, diagnostics.id, "fitted"
await session.flush()                            # 3. all three together
```

Every shortcut fails, each for a different reason:

* **Insert straight at `fitted`** → `ck_models_fitted_model_has_diagnostics`. The row needs a
  `diagnostics_id`, and `diagnostics` needs the model's id to point at — the cycle is real,
  and `draft` is how you break it.
* **Write `fit_result` first, the pointer second** → the immutability trigger. It fires when
  `OLD.fit_result IS NOT NULL`, so by the second statement the row is already protected.
* **Un-fit an existing model** (`row.fit_result = None`) → the same trigger,
  `a fitted Model is immutable (02 R2): UPDATE rejected`. To test a `draft` model, insert one.

`app/platform/modelling.record_fit` does exactly this, and it is the reference.

## Query `pg_constraint` by suffix, not by the name you wrote

The metadata naming convention prefixes check constraints: `model_status_is_in_the_lifecycle`
is stored as `ck_models_model_status_is_in_the_lifecycle`. A test asserting a constraint's
*definition* (rather than catching its error) must use
`conname LIKE '%%model_status_is_in_the_lifecycle'` — the doubled `%%` because SQLAlchemy's
`text()` treats a single one as a bind marker. Querying the bare name returns no rows, and
`scalar_one()` then raises `NoResultFound`, which reads like a missing constraint.

The error path needs no such care: `pytest.raises(..., match="...")` sees the full prefixed
name in the exception message.

## An HTTP test that needs real data builds it on its own event loop

Every HTTP test in this suite is **synchronous** — `TestClient` is a blocking client — so the
async `database` and `blob_store` fixtures cannot be requested from one. Building the data
with `asyncio.new_event_loop()` inside the test is the honest route:

```python
loop = asyncio.new_event_loop()
try:
    database = Database(Settings(database_url=test_database_url()))
    try:
        actor, model_id = loop.run_until_complete(_fit(database, store, workspace_id))
    finally:
        loop.run_until_complete(database.dispose())
finally:
    loop.close()
```

`dispose()` matters: an asyncpg pool bound to a closed loop surfaces later as
`got Future attached to a different loop` in an unrelated test. The alternative — hand-built
rows — makes the route test prove the routes work on a shape the real path never produces.

## A negative DB test that *fails* rolls back, so it leaks nothing

`with pytest.raises(...)` inside `async with database.unit_of_work()` raises pytest's
`Failed` out of the block when the expected exception does not arrive, and the unit of work
rolls back on any exception. So a not-yet-implemented constraint leaves no bad row behind for
the migration that adds it to trip over. Worth knowing before going looking for one.

## Never `git checkout --` a file you are working on

`git checkout -- path` restores the file to **HEAD**, not to the state before your last
edit. Used to revert a deliberately-injected defect it silently discards the whole feature
in that file — the injection *and* everything written this session. Copy the file aside
first (`cp file /tmp/file.bak`) and restore from the copy.

## A journey test pins the steps it cannot drive, inverted

An end-to-end journey (FR-OVR-17(ii)) will always reach steps the platform cannot execute yet.
Skipping them, or naming them in a comment, leaves nothing that notices when they arrive —
`wf-01`'s D7 and E4/E5 would have stayed absent from the journey long after the slices landed.

Write each as an assertion that **passes while the capability is absent and fails the day it
lands**:

```python
with pytest.raises(FactorResolutionError) as unbuilt:      # D7 — interaction factors
    resolve_factors(frame, [interaction])
assert "interaction" in str(unbuilt.value).lower()

assert not hasattr(model_schema, "PerilStructure"), (      # E4/E5 — no contract at all
    "E4/E5 are buildable now — extend the journey test above rather than deleting this"
)
```

The failure message is the handover: it tells the slice that broke it what to do. This is what
makes "FR-OVR-17(ii) partial" a claim with an expiry rather than a permanent excuse.

**And a journey test earns its cost by producing states no fixture does.** `wf-01`'s B8/B9 —
a warning, acknowledged, then promoted — was the first thing in the suite to ask for that
sequence, and it found a deadlock that had made *every* dataset version with one warning
unpromotable since the spec was amended three days earlier. Fixtures produced all-pass or a
hard fail; nothing in between.

## Verified

2026-08-17 — W5's `wf-01` journey slice, compose stack up: **961 Python tests** and the
frontend's 105. The inverted-assertion procedure above came from the three steps `wf-01`
cannot drive; the paragraph after it from the defect the journey found on its first run.

2026-08-17 — W5's comparison slice, compose stack up: **855 Python tests** and the frontend's
105, plus both alembic directions. Two new checks proved by injection (the shared-split refusal
and the runner's `job_id` injection), each failing exactly the tests that name it. The two
procedures added above both came from a test that failed for the *right* reason and the wrong
one: a Gini assertion that could never hold, and a weighting fixture the `GlmSpec` contract
refuses.

2026-08-17 — W5's model-lifecycle slice, compose stack up: **823 Python tests** and the
frontend's 105. Two new checks proved by injection — skipping `require_if_match` and skipping
supersession each failed exactly the tests that name them, and nothing else. Four procedures
added above, all of them found by a test failing for the *right* reason and the wrong one:
a status-CHECK test that passed against a table with no such constraint (the other CHECKs
refused the row first), a `pg_constraint` lookup that found nothing, an attempt to un-fit a
model, and an insert straight to `fitted`.

2026-08-15 — W5's banding and grouping slice, run with the compose stack up: 740 Python
tests and both alembic directions. **Corrects this skill's previous claim that
`docker compose` is unavailable** — it runs here, and the DB-backed tests it enables are
the ones that catch migrations and privileges. Four defects surfaced by running rather than
assuming, three of them by injection: a `banding` factor that silently resolved to its raw
column broke no test, `GLM_SEPARATION_DETECTED` was raised and registered nowhere,
`POST /factors` turned an invariant into a 500, and `git checkout --` ate a file mid-task.

2026-08-14 — W1's 21 tests, run without a database. Two defects surfaced by *running*
rather than assuming: the `test_money.py` basename collision (fixed by `importlib` mode),
and an expected value of mine that was simply wrong — 24150 × 1.15 is exactly 27772.5, so
half-even gives 27772 and my intuition had defaulted to half-up.
