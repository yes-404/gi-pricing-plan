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

### …and then write the happy path, because the refusal alone can pass over a broken feature

The converse of the rule above, and it has cost real time here. The GBM slice's
interaction-constraint **refusal** passed the whole time every *valid* constraint was also
being rejected — XGBoost resolves constraints against the `DMatrix`'s `feature_names` and
refuses indices, LightGBM takes indices, and the refusal test could not tell "rejected
because it is invalid" from "rejected because nothing works". Writing the happy path
**after** the refusal is what found it.

So a refusal test is finished when a passing case sits beside it. Two assertions, and the
pair is the claim: *this* is rejected, *that* is accepted.

### A feature four sites agree on can still not work

`inverse` was declared in FR-MODEL-18, accepted by `GlmSpec`'s literal, implemented in
`predict._inverse_link`, and tested at the scorer. It could not be fitted: `glum` has no
such link name, and the string reached the library and raised a bare `ValueError`. The
translation between the spec's vocabulary and the library's was the fifth site, and nothing
tested it, because every existing test entered the path *after* it.

**Agreement among declarations is not evidence of a working path.** Where a value is a
string this repository chose and some library also has to understand, one test must run it
**end to end into the library** — fit the model, do not merely validate the spec that names
the family. One such test per enumerated value, and the cheapest form is a parametrised fit
over the whole literal.

### Parametrize over every backend that claims to do the same thing

Two libraries behind one interface will agree at the point you looked and disagree
somewhere else. XGBoost and LightGBM agree at fit time and diverge at prediction time,
which is why FR-MODEL-72 exists as a round-trip requirement rather than a fit-time one. A
test that exercises only the primary backend reports the pair healthy — and `libgomp1`
showed the same shape from the other side, where the secondary could not even import while
the suite stayed green.

### A registry that refuses unknown values needs a test over the *source*, not a scenario

`PlatformError` validates its `code` against an enumerated set and raises
`ValueError: unknown error code` for anything else — **from inside the error path**, so the
symptom is an unrelated 500 where a named refusal was meant to be. Eleven codes were
unregistered at once, and no scenario test would have found them: reaching each one needs
the specific failure that raises it.

The instrument is an **AST scan over the source** asserting every code a `raise
PlatformError(...)` mentions is in the registry — `tests/test_repository_invariants.py`.
Same class of blindness as W1's invisible enforcement: a check nothing exercises is
indistinguishable from a check that passes.

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

## Loosening a tolerance? Pin the other side of it in the same commit

A numerical check that was made *more permissive* to stop false positives has silently
become a weaker check, and nothing in the suite notices: every existing test still passes,
because they all feed it correct input. That is the shape of a check that stops checking.

The rule: when a tolerance, floor or noise term moves, add a test that feeds the check a
**deliberately wrong** value sized just above the new threshold, and assert it still fails.
Two tests, because they answer different questions:

```python
# 1. Broken input is caught at all — a 1 % error in a derivative is the shape of a
#    dropped constant, and it must reach `failed`, not `warn`.
_break(monkeypatch, T.GAMMA, "hess", lambda d: d * 1.01)

# 2. Broken input is caught *in the regime the loosening touched* — an absolute error of
#    1e-08, two hundred times the noise where this hessian is smallest.
_break(monkeypatch, T.GAMMA, "hess", lambda d: d + 1e-8)
```

Break it **upstream of compilation**, not in the object the check receives, so the whole
public path runs exactly as it does for real input:

```python
good = _TEMPLATES[template]
fn = getattr(good, which)
monkeypatch.setitem(
    _TEMPLATES, template, replace(good, **{which: lambda y, f, p: break_it(fn(y, f, p))})
)
```

`dataclasses.replace` on a frozen catalogue entry plus `monkeypatch.setitem` is the whole
mechanism, and it needs no seam in the production code.

Sizing the perturbation is where the thinking is: it must be **large against the noise the
check now subtracts** and **small in absolute terms**, or the test proves only that a
grossly wrong value fails, which was never in doubt. Check where the true quantity is
*smallest* over the sampled grid — that is where a noise term hides an error, and where the
test has to bite. If no sampled point reaches that regime, say so in the docstring rather
than asserting a status the grid happens to produce. (`certify_objective`'s derivative
check, `02` §4.7 — the gradient never gets near zero on a Gamma money grid, so only the
hessian can carry this test.)

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

### The skip guard checks that migrations exist, not that they are at head

`conftest_db.py` skips when `SELECT count(*) FROM alembic_version` fails — which is a test
for *any* migration having been applied. A branch that adds one gets no skip and no warning:
the database is a version behind, and every test touching the new table fails with

```
asyncpg.exceptions.UndefinedTableError: relation "peril_structures" does not exist
```

reported as an error in the code under test rather than as an out-of-date database. It bites
hardest in a **worktree**, where `uv sync --all-packages --dev` has to be run again anyway
and it is easy to assume the shared Postgres came with it. Run `alembic upgrade head` after
checking out any branch that adds a migration, before reading a single failure.

### The test database is never cleaned, and `TRUNCATE` will not clean it

`conftest_db.py`'s `database` fixture creates an engine per test and disposes it. **Nothing
rolls back and nothing truncates** — every row every test writes stays, and it is the same
database `scripts/demo.py` seeds into. Measured 2026-08-22: six days of runs left **766 MB**,
11 915 `models` rows across 737 throwaway workspaces and 448 k `audit_events`. Nothing breaks,
but a hand-written query against it answers for the debris of every branch anyone has tested
— which is how "find the stale `v9:` digests" returns 1045 rows that are all test fixtures.

**`TRUNCATE` is refused, by design.** `audit_events` carries two triggers,
`audit_events_no_modify` and `audit_events_no_truncate`, enforcing the append-only audit
chain in the database rather than only in the application:

```
ERROR: ... CONTEXT: PL/pgSQL function audit_events_append_only() line 3 at RAISE
```

One `DO` block truncating every table is a single transaction, so that refusal rolls the
whole statement back and **nothing at all is cleaned** — including the 40 tables that would
have truncated fine. **Do not disable the triggers to force it through.** A governance guard
switched off during a cleanup and not switched back on is precisely the defect the guard
exists to prevent, and it fails silently ever after.

Drop and recreate instead. It rebuilds the triggers from the migration that declares them,
so the guard cannot be left off by forgetting a step:

```bash
docker exec gi-pricing-postgres-1 psql -U gipricing -d postgres \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity
      WHERE datname='gipricing' AND pid <> pg_backend_pid();"
docker exec gi-pricing-postgres-1 psql -U gipricing -d postgres -v ON_ERROR_STOP=1 \
  -c "DROP DATABASE gipricing;" -c "CREATE DATABASE gipricing OWNER gipricing;"
export GIP_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
uv run alembic upgrade head
```

Then confirm the guard came back, because a rebuild is exactly where it could silently not:

```bash
docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing -tAc \
  "SELECT tgname FROM pg_trigger WHERE tgrelid='audit_events'::regclass AND NOT tgisinternal;"
# expects both: audit_events_no_modify, audit_events_no_truncate
```

`pg_dump | gzip` first if you would regret it — the 766 MB above compressed to 93 MB in under
a minute. Two traps on the way out: `psql ... 2>&1 | tail -3; echo $?` reports **tail's**
status, so a refused statement reads as a clean exit — read psql's own code or the `ERROR:`
line. And the demo seed goes with everything else; `uv run python scripts/demo.py` rebuilds it.

## A gate run is only valid if the tree held still for all of it

The gate is eight commands over several minutes, and every one of them reads the working
tree at the moment it runs — not a snapshot taken at the start. If anything moves the tree
in between, the run reports a state that never existed: `pytest` measured one revision,
`generate-contracts --check` another, and the summary says both passed.

**This is not hypothetical, and the mover need not be a person.** Two Claude sessions
sharing one working directory produced it twice in an hour — a `git checkout main` that
reverted an edit between two tool calls with nothing in either output mentioning it, and an
amended commit that moved the tree under a gate run already in progress. The second was
sound only by luck: the delta was two markdown files carrying test counts, and nothing under
test changed.

So bracket the run and check, rather than assuming:

```bash
before=$(git rev-parse HEAD); git status --short | grep -v '^??' > /tmp/gate-dirty.before
# … the gate …
[ "$before" = "$(git rev-parse HEAD)" ] || echo "TREE MOVED — the run proves nothing"
```

If it moved, re-run — and if the delta is genuinely documentation only, say so explicitly
with the command that shows it (`git diff --stat $before HEAD`) rather than calling the
result byte-identical. A closure record's numbers are worth exactly what the tree they were
measured on is.

Before starting a gate you intend to quote, check for company: `git worktree list` shows the
sibling checkouts, but a second session in *this* directory shows up nowhere — ask.

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

### A GBM fixture must be asserted **converged** before its calibration is read

A boosted model with too few rounds is not a weaker model — it is a model that has barely
left its base rate, and every calibration figure you read off it is shrinkage wearing the
costume of a finding.

Concretely, W5's backtest slice: 30 rounds at `eta=0.1` gave the booster a **train A/E of
0.53** on its own training frame. Scored against a book carrying 30 % more claims, it read
0.65 — so a test written to assert "deterioration shows up as A/E > 1" failed, and the
tempting fix is to widen the bound until it passes. That bound would then have been
calibrated against an unconverged fit and would have accepted almost any arithmetic.

The rule: **assert the fit reconciles on its own training data first**, in the same test.

```python
on_train = backtest_model(fit.result, spec, factors, train, ...)
assert on_train.partition.ae_overall == pytest.approx(1.0, abs=0.01)   # it is a model
assert 1.1 < later.partition.ae_overall < 1.35                          # now read the finding
```

300 rounds got train A/E to 1.000 here. The number is fixture-specific; the ordering of the
two assertions is not. A GLM needs no equivalent — its fit solves rather than approaches, so
the Poisson identity holds at the first iteration.

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

### A *legacy* fitted model is built on a reserved draft, never by editing a fitted one

A fixture for "a model fitted before field X existed" cannot strip X from a fitted row — the
immutability trigger refuses, correctly. Reserve a second draft in the same workspace and
write the older-shaped `fit_result` onto **it**, which is the transition the worker makes:

```python
spare, _ = await model_service.reserve_model(session, workspace_id=..., actor=..., spec=...)
stored = dict(real.fit_result); stored.pop("covariance_blob")     # the older shape
await session.execute(ModelRow.__table__.update().where(ModelRow.id == spare.id).values(
    fit_result=stored, status="fitted", diagnostics_id=real.diagnostics_id,
))
```

`ck_models_fitted_model_has_diagnostics` applies to the spare too, so it needs a
`diagnostics_id`; sharing the real model's is right when nothing under test reads it, and
worth a comment saying so — a reader's next assumption is that it was forged.

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

## Never open a `unit_of_work` inside another one — it hangs, it does not fail

Each `database.unit_of_work()` takes its **own connection** from the pool. Opening a second
one while the first is still held does not raise, does not time out, and prints nothing: the
inner one waits for a connection the outer one is holding, and **pytest hangs with no output
at all**. There is no traceback to read, because nothing has failed yet.

The shape that causes it is innocent — a fixture that builds one thing inside the transaction
that builds another:

```python
# WRONG — the helper opens its own unit_of_work while this one is still open
async with database.unit_of_work() as session:
    row, _ = await model_service.reserve_model(session, ...)
    central = _Central(..., objective_ref=await _approved_objective(database, ...))
```

```python
# RIGHT — sequence the transactions, and carry only plain data across the boundary
objective_ref = await _approved_objective(database, ...)

async with database.unit_of_work() as session:
    row, _ = await model_service.reserve_model(session, ...)
    identity = (row.id, row.model_family_slug, row.version)   # not the ORM row

return _Central(id=identity[0], ..., objective_ref=objective_ref)
```

Two habits that keep it away:

* **A helper taking `database` opens a transaction; a helper taking `session` joins one.**
  Never call the first from inside the second.
* **Do not carry an ORM row out of its `async with`.** Read the fields you need into a tuple
  or a frozen dataclass inside the block — the row is detached afterwards, and touching a
  lazy attribute re-enters the session machinery.

**Diagnosing it:** a run with zero output for minutes is this until proven otherwise. Do not
wait it out — `pgrep -af "bin/pytest"` confirms the process is alive, then kill it and read
the fixture for a nested `unit_of_work`.

## Verified

2026-08-22 — W5, resetting the shared test database after the GBM weighting slice. `TRUNCATE`
over every table was refused by `audit_events`' append-only triggers and rolled back whole;
the drop-and-recreate path above was run end to end, `alembic upgrade head` returned to the
same head, both triggers were confirmed restored, and 62 DB-backed tests passed against the
rebuilt schema (766 MB to 9.9 MB).

2026-08-19 — W5, the GLM approximation as a Model. The `git checkout --` rule above cost a
whole task's rewrite: reverting a deliberately-broken file with `git checkout -- <file>` to
prove an enforcement path fails on bad input restored **HEAD**, discarding every uncommitted
edit written earlier in the same task rather than only the injected defect. The implementer
re-spliced the rewrite from scratch; every later task in the plan was told to `cp file
/tmp/file.bak` first instead. The rule was already written here (added in #72) — this is a
second, costlier confirmation that it is not optional even when the file being restored is
not the one the rule's own example names.

2026-08-19 — W5, paired quantile models. The nesting rule above cost six minutes and a killed
run: a fixture called an objective-building helper from inside the transaction that reserved
a model, and the suite hung with no output. Three further fixture defects were the platform
catching the test rather than the reverse — a `custom_objectives` CHECK refusing a status
stamped past `draft` with no certificate, a factor naming a column the dataset lacks, and
FR-MODEL-44 requiring a spec with a custom objective to declare its `response`. Suite at 1339,
zero skipped.

2026-08-18 — W5, custom objectives. The tolerance rule above came from raising a certification grid's floor from 600 to 1 000 points: three of twelve templates then warned on derivatives that were exactly correct, the fix loosened the agreement check, and nothing in the suite would have noticed that it had stopped catching a wrong one. Suite at 1213.

2026-08-18 — W5, prediction. The two rules above came from this slice: the `inverse` link
was declared in four places and fitted in none, and a legacy-model fixture was refused by the
immutability trigger until it was built on a reserved draft. Suite at 1093.

2026-08-18 — W5, backtests. The GBM-convergence rule above was found by a test that failed for a reason that looked like a broken scoring path and was an unconverged fixture: train A/E 0.53 at 30 rounds, 1.000 at 300. Suite at 1073.

2026-08-18 — the three rules above (happy path after the refusal, parametrise over
backends, AST-scan a registry) were carried out of a local handover note that was being
deleted. Each was learned in W5 and each had been recorded only in an untracked file, so
none of them would have survived it — which is the argument for `.claude/skills/` over a
scratch file, made concrete.

2026-08-18 — W5, peril structures. The migration-skip rule above was found in a worktree:
eleven DB-backed tests failed with `UndefinedTableError` and no skip, because the guard
only asks whether *any* migration has run. Suite at 1026 with the stack up.

2026-08-17 — Two sessions, one working directory. The bracket above was written after a
gate run began at one revision and ended at another, and after a `checkout` in the same
directory silently discarded an edit made between two commands. Both were found by
comparing SHAs, not by any command reporting an error.

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
