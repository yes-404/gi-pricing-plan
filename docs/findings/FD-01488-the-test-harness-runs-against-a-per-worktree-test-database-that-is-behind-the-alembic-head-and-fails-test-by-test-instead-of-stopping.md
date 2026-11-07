---
id: FD-1488
family: finding
title: The test harness runs against a per-worktree test database that is behind the alembic head, and fails test by test instead of stopping
status: closed
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: 83ea509023d6d705d6f78fe74b7124fdf1375739
corrected_by: []
relates: [WK-1178, SL-1409, SL-2048, LG-2049, PL-2047]
---

# FD-1488 — the test harness runs on a database behind the alembic head and fails test by test

*Disclosure: drafted under working id 9645; minted as FD-1488 on 2026-10-08, in the T2 batch mint PR.*

Every locator below was read at `origin/main`
`83ea5090`, except the gate log, which is a run artefact (`~/.claude/jobs/6cad77f9/tmp/gatelogs/p.txt`, a local file, so cited by path).
Ordered by the maintainer's (by delegation) entry headed
"2026-10-05 14:09:21 BST — SL-1409 gate RED (124 failed): probable cause is the per-worktree TEST DB one migration behind the branch head; verify, upgrade, re-run (not a slice fix); unfreeze main now", item 4
(`to-lead.md`, a local channel file, so cited by its header).

## Finding

**Proposed severity: MEDIUM; owner WK-1178** (the maintainer sets severity). A test session whose
database is behind the alembic head is not refused. It runs, and each test that touches a
missing table or column fails alone. The run costs its full length and ends in a red that
looks like slice defects.

## Evidence

SL-1409's minted-head gate at `7b3ee551` (recorded in SL-1409's ledger, working id LG 9719,
minted as LG-1417; branch `sl-1409-validation-rule-approval-through-the-workflow`) ended:

```
33129:124 failed, 4815 passed, 4 skipped, 86 warnings in 2017.92s (0:33:37)
```

```
E   asyncpg.exceptions.UndefinedColumnError: column "bound_symbols" of relation "custom_objectives" does not exist
```
(the second line is `:263` of the same log; `bound_symbols` occurs on 514 lines of it.)

The maintainer's (by delegation) 14:10:08 BST entry grouped the 124: **121 are this fault**, 3 are real slice
defects. The per-worktree database `gipricing_sl-1409_8f3bb0b4` stood at `c4a81f6d2e95`;
the branch heads at `e5b7d9f1a3c6` (`backend/migrations/versions/e5b7d9f1a3c6_custom_objective_expression_storage.py`,
`down_revision "c4a81f6d2e95"`). The branch gained that migration when it merged main
`072c56e1`; nothing upgraded the worktree database.

## Cause

`backend/tests/conftest_db.py`, the `database` fixture (`:192-198` at `83ea5090`), skips only a
database with no migrations at all:

```python
    async with db.session() as session:
        applied = (
            await session.execute(text("SELECT count(*) FROM alembic_version"))
        ).scalar_one()
    if not applied:
        pytest.skip("database has no migrations applied; run `uv run alembic upgrade head`")
```

It counts rows in `alembic_version` and never compares the revision with the script heads.
The only other guard (`:125-136`) refuses a per-worktree database that does not exist yet,
and tells the operator to `alembic upgrade head` by hand once.

## Remedy (proposed; the decision-maker's)

At session start, compare `alembic current` with the script heads. Then either stop with one
named error that gives the upgrade command, or upgrade a per-worktree database
automatically (never the shared `gipricing` database, see `python-test`'s "mutually
destructive" section). Red first: a test database stamped one revision back must refuse the
session, not run it.

**Until then:** every gate checklist gets the line "alembic current == heads on the
worktree database" (`dev-commands` and the executor role file).

## Disposition

Owner **WK-1178**. **Proposed severity: MEDIUM** (the maintainer sets it). **Proposed
decision:** fix before close with an owner: WK-1178, by the remedy above; the lead gives
the verdict. Until the fix lands, the "alembic current == heads" gate-checklist line applies.

***Resolved 2026-11-06*** — closed in place 2026-11-06 by the auditor, as the closing act of the audit of SL-2048 (WK-1178, LG-2049, PL-2047; this PR; its number, squash commit and merge date are written at the merge's date-of-record), on the lead's brief under the GO "2026-11-05 10:31:31 GMT" (plans C and H accepted, DP-H1 to DP-H5 ruled; `to-lead.md`, a local channel file), on the order of "2026-11-05 09:58:58 GMT". Delivered remedy: DP-H1 (a), stop once and by name, never upgrade. `backend/tests/conftest_db.py` gains `migration_problem(current, heads, known)`, `_script_revisions()` (the script directory read once a session, `functools.cache`) and `_check_migrations_once(current)`; the `database` fixture runs the check once per session, after its `applied` check, and `pytest.exit`s with `the test database is at […], the scripts' heads are […]: run \`uv run alembic upgrade head\` against this database (FD-1488)`. It reads `alembic_version` and the script directory and writes nothing (G1), as the login role (G2). DP-H2 (a): a revision the checkout's scripts do not know is a database *ahead* of the branch and passes with a `UserWarning`. Red first, by cause, in LG-2049: `b96ea7da` (stub returning `None`) gave `2 failed, 2 passed` (`assert None is not None`), green `970d4b62`, `6 passed` in `test_conftest_db_migration.py`; the audit added two single-edit mutations (cache removed → the read-once test fails; `pytest.exit` removed → the stop test fails). Stamped proof in a granted DB window on a `createdb -T` copy (START 11:01:49, END 11:06:48 GMT, `test_workspaces.py`): one revision back → `Exit`, rc 1, in 25 s; restamped → `2 passed`; unknown revision → `UserWarning` and `2 passed`; both zeros at END. Not retired by this record: the "alembic current == heads" gate-checklist line in `dev-commands` and the executor role file (PL-2047 Hand-off: a separate record). Gate evidence: the gate: pytest `13 failed, 7224 passed, 27 skipped, 5 xfailed in 4949.99s` alone, the 13 being the item-31 docs-audit set, every other python and frontend stage rc 0, demo seeded rc 0 (LG-2049).

## Not this finding

SL-1409's three real failures (the registry test, the authorisation sweep's line pins,
`test_doc_id_migrate` in a worktree) are the slice's, per the 14:10:08 entry.

*(Dated line, 2026-11-05, docs batch 11, by the auditor, on to-lead "2026-11-05 09:51:53 GMT" (triage b28ba8e9454c accepted as the proposal of record), item (4): severity RULED MEDIUM, as proposed.)*
