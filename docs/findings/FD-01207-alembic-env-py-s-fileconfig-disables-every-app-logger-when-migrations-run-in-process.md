---
id: FD-1207
family: finding
title: Alembic env.py's fileConfig disables every app logger when migrations run in-process
status: closed
created: 2026-09-28
owner: auditor
tree: 109cd065987c399b9cdbecc2fcb6628843dfb79a
corrected_by: []
relates: [LG-1204, WK-1178]
---

# FD-1207 — Alembic env.py's fileConfig disables every app logger when migrations run in-process

**Severity: low.** The auditor filed this finding on 2026-09-28, on the lead's instruction and
the deputy's MERGE-ACK of #867, which asks for *"the env.py logger fix as a WK-1178 item with an
owner"*. executor-s2 found and measured the defect during WK-672 Slice 2, and `LG-1204` records
it.

## Finding

`backend/migrations/env.py:25` calls `fileConfig(config.config_file_name)`. `fileConfig`'s
`disable_existing_loggers` argument defaults to true. When alembic runs **in-process**, as it
does in the test suite, every `app.*` logger that already exists is disabled for the rest of the
session. A disabled logger drops its records before any handler sees them. So later tests that
assert on log output, or on its absence, pass vacuously. NFR-499's "quote inputs never logged in
full" check is one of them.

## Evidence

At `origin/main` `109cd065`:

- `backend/migrations/env.py:25` reads `fileConfig(config.config_file_name)`, with no
  `disable_existing_loggers` argument.
- **Measured by executor-s2**, recorded in `LG-1204` (lines 121–128):
  - a script that imports the app's modules and then calls `fileConfig('alembic.ini')` printed
    *"0 of the `app.*` loggers disabled before and 22 of 22 after"*;
  - the order-dependent failure reproduces with `uv run pytest -p no:randomly
    backend/tests/test_migration_dataset_owner.py backend/tests/test_regression_suites.py`.
- **The test-side guard** is commit `6cc5078c`, in #867, squashed into `109cd065`.
  `backend/tests/test_regression_suites.py:163`–`169` re-enables disabled loggers for that test
  and requires a sentinel to be captured. It guards one test. It does not fix `env.py`.
- **Production is unaffected.** At `109cd065`, the command
  `git grep -n 'command\.upgrade\|alembic\.config\|alembic import\|fileConfig\|from alembic\|import alembic' origin/main -- backend/src`
  prints nothing (exit 1). `fileConfig` appears only in `backend/migrations/env.py` and
  `backend/tests/test_regression_suites.py`. Every other migration run is its own `alembic` CLI
  process (`LG-1204`'s list: `.github/workflows/python.yml`, `scripts/demo.py`).

## Disposition

**Deferred with an owner — the lead**, under WK-1178. Event: a small WK-1178 PR that passes
`fileConfig(config.config_file_name, disable_existing_loggers=False)` in
`backend/migrations/env.py`. That fixes the cause for every in-process caller, not only the one
guarded test.

## Resolution

**Resolved 2026-09-28 by #873, merge commit `91d08d8a`** (`fix(migrations): env.py's fileConfig no longer
disables the app's loggers (WK-1178, #869) (#873)`, merged 2026-09-28 22:20:19 BST). Read at `91d08d8a`:

- `backend/migrations/env.py:28` is `fileConfig(config.config_file_name, disable_existing_loggers=False)`,
  under a comment saying alembic can run in-process and the default would disable every existing logger.
- `backend/tests/test_migration_env_logging.py` (one test, marked `NFR-499`) runs `command.current` in a
  thread against the test database and asserts that the probe logger `app.env_logging_probe` is still
  enabled, and that no logger under `app` is disabled. A fixture restores every logger's `disabled` flag, so
  a red run cannot poison other tests. This record read the test's assertions, and did not run it.
- The change removes #867's test-side guard from `backend/tests/test_regression_suites.py`, the guard this
  record described as covering one test and not the cause.

Production was never affected: this record's own evidence found no in-process alembic in `backend/src`.

