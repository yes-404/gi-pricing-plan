---
name: dev-commands
description: The commands that build, gate, migrate, benchmark and demo this repository, each with the trap that makes the obvious form of it wrong — why `uv sync` without `--all-packages` produces a venv that looks fine and fails, why a "gate" covering only Python has been green while the frontend was red, why `cmd | tail -1 && echo ok` reports the wrong exit code, why a benchmark number taken on this shared machine can read as a 2.3x regression, and the alembic DSN that the bare command does not use. Use when running the gate, setting up a fresh checkout or worktree, migrating, benchmarking an NFR, or starting the demo.
---

# Development commands

`CLAUDE.md` §11 carries the bare invocations. This carries the commentary — which is the
part that was learned by something failing, and the part a bare command list cannot hold.

## Setup — `--all-packages` is not optional

```bash
uv sync --all-packages --dev
```

The root sets `package = false` and depends on no member, so a plain `uv sync` installs the
dev tools and **none of the workspace packages**. `mypy` and `pytest` then fail on
`No module named 'pydantic'` in a venv that looks fine. A fresh worktree with no `.venv`
reports ~690 phantom errors that read as real code defects.

## A borrowed venv silently tests the wrong tree

Pointing `uv run`/`pytest` at another worktree's (or the main checkout's) `.venv` to skip a
sync — via `cd`, `UV_PROJECT_ENVIRONMENT`, or `--no-sync` — does not test the tree you think
it does. This repo's packages are installed **editable**, and an editable install's `.pth`
shim (`_editable_impl_gi_backend.pth` for the backend) hardcodes the **absolute path** it
was synced from. Running from `/tmp/some-other-worktree` with that shim still imports
`app` from wherever it was originally synced — silently; no error names the mismatch.

Confirmed the hard way auditing PR #371 (2026-08-29): `backend/tests/test_rating_versions.py`
run from an isolated worktree, reusing the main checkout's `.venv`, gave 2 failed / 5 passed
(`POST /rating-versions` → 405, the pre-fix symptom) — the shim was resolving to the main
checkout's code, not the worktree's, and the main checkout happened to be on an unrelated
branch at the time. A real `uv sync --all-packages --dev` inside the worktree fixed it: 7/7
passed. **A test run against borrowed tooling is not evidence about the tree under audit —
sync fresh, every time, for any worktree whose code differs from wherever the venv was
built.** Check a `.pth` file's target path (`grep -r . <venv>/lib/*/site-packages/*.pth`)
before trusting a reused venv at all.

## The gate is two halves, and one of them is not Python

This repository is polyglot and CI runs two workflows. **A "gate" that covers only Python
has been green here while the frontend was red.** Run both.

### Python (`.github/workflows/python.yml`) and docs (`docs.yml`)

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
python3 scripts/audit-docs.py                # structural checks over docs/ and .claude/notes/
uv run python scripts/req-coverage.py        # requirement traceability
uv run python scripts/generate-contracts.py  # regenerate; --check fails CI on drift
```

Use `generate-contracts.py --check` rather than the plain regenerate when auditing: the
plain form *writes* the drift away instead of reporting it.

**`pytest -q` needs the compose stack up, and nothing in the command says so.** CI starts
Postgres and Redis as `services:` and **MinIO as an explicit step** (`python.yml:125-129` —
a `services:` entry cannot express it, because `minio/minio` needs `server /data`). Locally
that infrastructure is yours to start, from the *Local infrastructure* section far below:

```bash
docker compose -f deploy/docker-compose.yml up -d --wait   # BEFORE the gate, not just the demo
```

**Without it the suite does not error usefully — it comes back mostly green with a handful
of failures**, which is the dangerous shape. Seen 2026-08-30 on W11 Task 3A: 2,347 collected,
**5 failed**, and **255 `botocore.EndpointConnectionError`** entries that were only visible
because the run was piped through `tail`. Most infra-dependent tests skip when the stack is
absent; a few fail instead. **A test that fails rather than skips on missing infrastructure is
indistinguishable from a real regression**, and on that occasion the lead misdiagnosed it as
F45 contention and the executor agreed — while the refuting `botocore` line sat in the
executor's own report. F45 needs a database that exists and gets truncated; there was no
database at all.

So: **bring the stack up before the gate, and if the suite is red, check `docker ps` before
diagnosing anything.**

### `mypy`'s `files` list, and why it cannot be one flat list covering everything

Since 2026-08-30 the bare `uv run mypy` above also covers the repo-level `tests/` root, the
demo seed (`examples/fremtpl2`), and the two live operational skill scripts
(`.claude/skills/balance-watch/scripts`, `.claude/skills/reporter-cycle/scripts`) — before
that, nothing under `.claude/` and no test file anywhere was type-checked at all, and both
gaps had already concealed real defects (a wrong import path in a test, and three real bugs
in `balance_watch.py`).

**It still does not cover `packages/model-schema/tests`, `packages/pricing-core/tests` or
`backend/tests`, and cannot by adding them to `files`.** Every test directory lacks
`__init__.py` (deliberate — `python-test`'s own note explains why: it mirrors pytest's
`--import-mode=importlib`, which is what lets two packages each own a `conftest.py` and a
`test_money.py`). mypy has no equivalent of importlib mode: combining any two such
directories in **one invocation** is not a size problem, it is a hard failure —

```
error: Duplicate module named "conftest" (also at "packages/model-schema/tests/conftest.py")
```

— confirmed by actually trying it, not assumed. Each test directory needs its **own**
scoped invocation, one src tree combined with only its own tests — the same shape this
skill already uses for `bench-model.py --only curve`, one phase at a time.

Two settings make even the *current* `files` list work, and both are load-bearing:
`explicit_package_bases = true` is required the moment any `__init__.py`-less directory is
in `files` at all (without it, mypy's own fallback inference is what produces the
duplicate-module collision above, even for a single directory). And `mypy_path` must then
name every source root explicitly, `backend/src` included — leaving it out made `backend/src`
unable to resolve its own internal imports (`app.errors` etc.) once the flag was on, 536
bogus `import-untyped` errors that looked exactly like a real defect until `mypy_path` was
corrected and the count went to zero.

**Real per-directory debt, measured 2026-08-30** (`--strict --explicit-package-bases`, own
`mypy_path`, `--no-incremental` so concurrent runs don't race the cache) — not yet reduced,
reported so the next PR knows the shape rather than re-deriving it:

```bash
MYPYPATH="packages/model-schema/src" uv run mypy --strict --explicit-package-bases \
  packages/model-schema/src packages/model-schema/tests           # 144 errors / 14 files

MYPYPATH="packages/model-schema/src:packages/pricing-core/src" uv run mypy --strict \
  --explicit-package-bases packages/model-schema/src packages/pricing-core/src \
  packages/pricing-core/tests                                     # 107 errors / 23 files

MYPYPATH="packages/model-schema/src:packages/pricing-core/src:backend/src" uv run mypy \
  --strict --explicit-package-bases packages/model-schema/src packages/pricing-core/src \
  backend/src backend/tests                                       # 1243 errors / 82 files
```

`backend/tests`' 1243 is dominated by `no-untyped-def` (769 of them — mechanical, a missing
`-> None` or parameter type), but the remaining ~470 (`arg-type`, `union-attr`,
`no-untyped-call`, `index`…) are not. Large enough that fixing it is its own PR (or several),
not a config edit.

**A reused `async with ... as session:` name can make mypy misresolve an unrelated overload,
not just look untidy.** `examples/fremtpl2/seed.py`'s `run()` rebinds the name `session`
nine times across the function body and two nested closures — ordinary here, since each
`async with database.unit_of_work() as session:` / `database.session() as session:` block
scopes cleanly at runtime. Under `--strict` with the `explicit_package_bases`/`mypy_path`
pair this file now needs, one specific occurrence (`session.get(DatasetVersionRow, first)`,
guarding the "was the failed version left mid-run" check) resolved `AsyncSession.get()`'s
generic overload against `ValidationRuleRow` — the entity type an *earlier, unrelated*
`row = ValidationRuleRow(...)` binds `row` to, nothing to do with this call — and reported a
real-looking `arg-type` error (`type[DatasetVersionRow]` "incompatible" with what `.get()`
expected) for a line that was correct as written. A same-shaped fix already in this file
(renaming the *result* to `version_row`, adding `assert version_row is not None`) narrowed a
genuine `X | None` correctly but left this one standing, because it renamed the wrong
binding — the risk is `session`'s reuse, not `row`/`version_row`'s. Renaming *this*
occurrence's `session` to `verify_session`, nothing else, took the file from 4 errors to 0.
No other reused `session` binding in the file triggers it, so the fix is the one rename, not
a repo-wide rule against the pattern — but the shape (many `async with X as <name>:` blocks
sharing one name in a long function, one `.get()`/generic call among them) is worth
recognising before re-diagnosing it as a real type bug a second time.

### Frontend (`.github/workflows/frontend.yml`)

```bash
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api        # then type-check: the client is git-ignored,
                                        # so a diff against it can never fail
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

`--frozen-lockfile` from a **clean** `node_modules` is what CI does, and a populated one
hides a missing dependency.

**pnpm is not on this image** and `corepack enable pnpm` fails on it. The way in is:

```bash
npm config set prefix ~/.npm-global && npm i -g pnpm    # then put that bin on PATH
```

### Read each command's own exit code

`cmd | tail -1 && echo ok` reports **tail's** exit code, and has produced a false "clean"
here more than once. The same trap in other clothes: a `✓` echoed on `head`'s status rather
than the command's, and a `\echo` in `psql` that printed unconditionally and read as success
while the `ERROR` line above it proved the opposite.

### `gh --jq` always exits 0, whatever the predicate says

`gh`'s built-in `--jq` filters the output but **does not adopt jq's exit code**, so a
boolean predicate prints `false` and still succeeds. Verified 2026-08-30 against a merged
PR #438:

```bash
gh pr view 438 --json state --jq '.state == "OPEN"'   # prints: false   exit: 0
gh pr view 438 --json state | jq -e '.state == "OPEN"' # prints: false   exit: 1
```

**This silently breaks every loop and `&&` built on it.** `until gh pr view N --json … --jq
'<done?>'; do sleep 60; done` exits on the first iteration regardless of the answer, because
the condition is always true. A CI watcher written that way reports "terminal" the moment it
starts. Pipe through real `jq -e` when the exit code is load-bearing; `--jq` is fine for
formatting output a human or a later command will read.

Same family as the two above, and as `pgrep -af 'pytest'` matching its own wrapper
(`python-test`): **a check whose exit code is decoupled from the thing it checks.** The
question to ask of any guard is not "is it the right command" but "can this ever come back
negative" — run it once against a case you know is false, and see.

### vitest exits 1 while printing every test as passed

The worst form of the trap above, because here the command's **own** exit code is the honest
one and its **own** printed summary is the misleading one. An unhandled error thrown outside
a test — from a timer, an animation frame, a promise nothing awaits — is counted separately
from assertions:

```
 Test Files  39 passed (39)
      Tests  231 passed (231)
     Errors  80 errors          <- the only line that says anything is wrong
```

Exit code 1. Every test genuinely passed. A gate read by eye calls this green, and W6b-1b
shipped two commits that were red this way before anyone noticed.

**The cause here is ECharts.** `vue-echarts` paints to a canvas jsdom does not provide, so
every render leaks `TypeError: Cannot read properties of null (reading 'clearRect')` out of
zrender's animation loop — asynchronously, after the test that mounted the chart has already
passed. Any component test that mounts a real chart does this.

**The fix is to stub the renderer**, not to shim a canvas. Each chart asserts the `option`
object it computes, which is the thing worth asserting anyway:

```ts
vi.mock("vue-echarts", () => ({
  default: { name: "VChart", props: ["option"], template: "<div data-testid='chart' />" },
}));
```

`HistogramChart.test.ts` is the precedent. A **view** test that mounts charts incidentally
needs the same stub even though it asserts nothing about them.

**To detect it:** `echo "exit=$?"` on its own line after the run — never `&&`, never piped —
and treat a non-zero exit as failure even when the summary says otherwise. Grep the output
for `Errors ` as well as `Tests `; the two are different counters and only one of them is
in the line most readers stop at.

### The full suite outlives a foreground turn, and backgrounding it strands a subagent

`uv run pytest -q` collects **2,347 tests** and routinely runs past the **10-minute
foreground limit**, so the tool backgrounds it. That is fine for the main thread, which is
re-invoked when the command exits. **It is a trap for a subagent**: a backgrounded command
does not notify an agent that has already ended its turn, so the agent stops "waiting for
the completion notification" and waits forever. Seen 2026-08-30, W11 Task 3A — the executor
had a green gate and a finished commit and sat idle on a run that was healthy the whole time.

**So a subagent running the full suite polls in the foreground**, keeping its turn open:

```bash
until ! pgrep -f 'bin/pytest -q' >/dev/null; do sleep 20; done
```

Two ways that loop lies, both of which have happened here:

- **It never exits** if the pattern also matches the wrapper shell running the loop —
  `pgrep -f 'pytest'` matches its own command line. Match `bin/pytest`, and verify with one
  `pgrep -af` before trusting it. Same family as the `--jq` exit-code trap above: *can this
  check ever come back negative?*
- **It exits instantly** when the run has already finished — which is indistinguishable from
  never having started. Confirm against the output before concluding anything.

The dispatching lead's half: **say this in the dispatch**, and if a subagent reports it is
waiting on a background run, resume it and tell it to poll — do not re-dispatch the task,
which throws away a completed implementation.

### A pytest total is only honest against `--collect-only`

A pass count from a run that silently collected fewer tests than exist reads as clean —
the summary reports what ran, not what should have. A `conftest.py` import error, a
misnamed `test_*.py` file, or a path excluded from `testpaths` all shrink what gets
collected without failing the run itself.

```bash
uv run pytest --collect-only -q | tail -1   # 'N tests collected'
uv run pytest -q                            # reconcile N against what actually ran
```

Reconcile the two before citing a pass count in a closure record or an audit — a smaller
collected total than expected is itself the finding, not something a green run rules out.

### `req-coverage.py`'s percentage has three silent failure modes — two inflate it, one deflates it

The script counts a requirement as **specified** only where its id appears in bold
(`**FR-XXX-N**`) somewhere in `docs/specs/`, and **claimed** wherever any test carries
`@pytest.mark.req("FR-XXX-N")` — both are per-id presence checks, with no notion of degree
or cross-linkage between related ids (`scripts/req-coverage.py`, read in full to confirm
this before writing it here).

- **Bold-coupling** (inflates): a requirement defined without bold markup — a typo, or a
  citation outside the standard `| **FR-XXX-N** | ... |` table row — never enters the
  `specified` set. The denominator shrinks; the percentage rises for a requirement suite
  that did not actually get smaller.
- **Clause-conflation** (inflates): one `@pytest.mark.req(...)` marker marks an id **fully
  claimed**, regardless of how many distinct clauses that requirement actually bundles. A
  compound requirement with five behaviours and one test covering one of them reports as
  100% claimed for that id.
- **Shared-clause-attribution** (deflates): a clause shared across several requirement ids
  gets tagged against only one of them in practice. The untagged siblings show zero
  coverage even though the same test exercises their shared behaviour too.

None of these are bugs — the script counts exactly what it says it counts. Read `N%
claimed` as a floor on attention, not a measure of test quality.

## Closure audit — expected scope first, then evidence

```bash
uv run python scripts/scope-audit.py PLAT --sections 3.1,3.2,3.3,3.7,3.8
uv run python scripts/scope-audit.py DATA --endpoints    # §5.1 table vs the contract
uv run python scripts/scope-audit.py DATA --catalogue VR # a spec's named-item catalogue
```

The three axes answer different questions and none substitutes for another —
[`close-workstream`](../close-workstream/SKILL.md) has the method and the incident behind each.

## NFR measurement — and the contention factor that reads like a regression

`bench-data.py` knows `01`'s budgets; `bench-model.py` knows `02`'s. Run phases in separate
processes: glibc does not return freed arenas, so a peak-RSS reading taken after an earlier
phase is **that phase's**.

```bash
uv run python scripts/bench-model.py --only curve   # one phase at a time
```

**This machine is shared between concurrent agent sessions.** The same grouping proposal
measured **8.58 s at load 1.6 and 20.01 s at load 8.4** — a **2.3x contention factor that
reads exactly like a regression**. Both harnesses report `/proc/loadavg` and CPU seconds
beside wall-clock for that reason.

**Quote the load with every number, and re-take a headline figure in a quiet window before
recording it in a spec.**

## The demo entrance (FR-PLAT-53)

```bash
uv run python scripts/demo.py                # then open http://localhost:5173/demo
uv run python scripts/demo.py --rows 60000   # a sample; the full seed is 678 013 rows
```

One command from a clean checkout to a browser: compose, migrations, freMTPL2 seeded
through the **real Job path**, the API and the frontend, with a development identity for the
seeded workspace. Ctrl-C stops everything it started.

It **refuses outside local/dev before starting anything** — the whole path hangs off
`dev_auth_enabled`, `False` by default and fatal at startup in a deployed environment.

The demo *guide* (FR-PLAT-54) is derived, not written, so there is nothing to update — but
check that it still derives: `uv run pytest backend/tests/test_demo_guide.py`, which also
runs in the gate.

## Local infrastructure

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
docker compose -f deploy/docker-compose.yml down
```

`deploy/README.md` has the credentials and ports. Compose brings up **postgres/redis/minio
only** — there is no app container, because a Dockerfile for it is deployment (W14) rather
than a dev loop.

## Migrations — the bare command does not work against the compose stack

```bash
GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing \
    uv run alembic upgrade head
```

`CLAUDE.md` §11 claimed the bare `alembic upgrade head` worked until 2026-08-22. It does
not: `backend/src/app/config.py`'s `database_url` defaults to `gip:gip@localhost:5432/gip`
while `deploy/docker-compose.yml` provisions `gipricing:gipricing@…/gipricing`, and Alembic
reads `Settings`, so it dies with
`InvalidPasswordError: password authentication failed for user "gip"`.

**Why it survived every green suite:** `backend/tests/conftest_db.py`'s `DEFAULT_TEST_DSN`
carries the compose credentials itself, so the tests never touch the default.
[`fastapi-service`](../fastapi-service/SKILL.md) carries the full post-mortem and the other
paths that route around it.

## Serving the API and the frontend by hand

```bash
GIP_DEV_AUTH_ENABLED=true uv run uvicorn app.main:create_app \
    --factory --reload --app-dir backend/src --port 8000
pnpm --dir frontend dev                      # proxies /api to localhost:8000
```

Without `GIP_DEV_AUTH_ENABLED`, a browser gets 401 on everything — see
[`vue-frontend`](../vue-frontend/SKILL.md).

## Worker and outbox relay

```bash
celery -A app.worker.entrypoint worker --queues compute,default,io,scoring
celery -A app.worker.entrypoint beat
```

The relay is what moves a committed job to the broker. **Without `beat` running, jobs stay
`queued` and nothing explains why.**

## Verified

2026-08-30 (third entry, the reused-`session` note immediately above) — `225c0dd`'s own
message claimed the extension's 8 surfaced errors fixed, `examples/fremtpl2/seed.py`
included. Re-running `uv run mypy` fresh against that commit found 4 of the 8 still
present, all in `seed.py`, all at the `session.get(DatasetVersionRow, first)` call the
commit's diff had touched — its fix (renaming the *result* to `version_row`, adding
`assert version_row is not None`) narrowed a real `X | None` correctly but never renamed
`session` itself, so the actual cause (above) survived it. The claim was not re-verified
against a clean run before being written; this entry is that verification, done the second
time. Confirmed both ways, directly: `uv run mypy` against `225c0dd`'s own committed
`seed.py` reproduces exactly those 4; the one-line rename on top, nothing else, gives
`Success: no issues found in 163 source files`.

2026-08-30 (second entry, the mypy-coverage section immediately above) — extended `files`
to `tests/`, `examples/fremtpl2` and the two skill script dirs; documented why
`packages/*/tests` and `backend/tests` cannot join the same invocation. The
"structural blocker" a first dry-run reported for `backend/src` under
`--explicit-package-bases` (536 errors, even checking it completely alone) was re-run with
`mypy_path` naming `backend/src` itself and went to zero — not a defect in `backend/src`,
a missing one-line config the flag requires. The duplicate-module collision, by contrast,
was re-verified as genuine: combining any two test directories in one invocation fails the
same way every time, with or without `mypy_path` set correctly.

2026-08-30 — the `gh --jq` section added, found by a CI watcher on PR #438 whose polling
loop terminated immediately. Reproduced directly against that PR once merged, so the
predicate had a known-false answer: `--jq '.state == "OPEN"'` printed `false` and exited 0,
while the same predicate through `jq -e` exited 1. Filed here rather than in `python-test`
because it is a property of `gh`, not of the suite — and beside the exit-code pitfall
because it is the same defect, a check whose exit code cannot report what it checked.

2026-08-29 — the borrowed-venv section above added, found auditing PR #371's task-brief
regression fix. A false 2-failed/5-passed test result was traced, before being reported as
a finding, to `_editable_impl_gi_backend.pth` hardcoding the main checkout's absolute path;
re-run with a real `uv sync --all-packages --dev` inside the PR's own worktree gave the
genuine 7/7 the PR itself claimed.

2026-08-29 — the `--collect-only` reconciliation note and `req-coverage.py`'s three
failure modes added (task #30, item 3), found by the auditor checking `close-workstream`,
`dev-commands`, `python-test` and the script's own source and finding none of the four
stated either. Each failure mode re-derived and confirmed directly against
`scripts/req-coverage.py`'s actual logic before writing it here, not taken as given: the
bold-only regex, the per-id binary presence check with no clause-level granularity, and
the absence of any cross-id linkage that would catch a shared clause tagged against only
one sibling.

2026-08-24 — the vitest exit-code trap was found during W6b-1b, by running `echo "exit=$?"`
after a suite whose summary read `231 passed`; the same run at the preceding commit
reproduced it, which is what showed the redness predated the change rather than being caused
by it.

2026-08-23 — extracted from `CLAUDE.md` §11 verbatim when that section was cut to bare
invocations. Every trap here was recorded in `CLAUDE.md` at the date its own line states;
the alembic mismatch was found 2026-08-22 during W5 audit remediation, and the contention
factor during a W5 grouping measurement.
