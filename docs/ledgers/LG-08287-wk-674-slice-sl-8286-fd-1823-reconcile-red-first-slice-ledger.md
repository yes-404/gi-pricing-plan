---
id: LG-8287
family: ledger
title: WK-674 slice SL-8286 — FD-1823's reconcile: the deployment switch loads the latest committed Deployment periodically and on reconnect, and discovers Environments created after start (red first)
status: active                 # active → closed (§1.2a)
created: 2026-11-03
owner: executor
tree: 03d98c2170d7f7cbe283e1b91d91c9f2057f0480   # the branch head the runs below were made on (before this file)
phase: P2
work: WK-674
slice: SL-8286
plans: [PL-1688]
corrected_by: []
relates: [FD-1823, WK-674]
---

# LG-8287 — WK-674 SL 8286: FD-1823's reconcile

Working ids (SL 8286, LG 8287) are in space form in prose until the mint.

**GO:** to-lead "2026-11-03 15:50:00 GMT — Maintainer: MERGE-ACK #1413 (Dependabot frontend dev group, merge 44) + GO for SL 8286 (FD-1823's reconcile, PL-1688 row 3)", as relayed in the lead's brief: DP-R1 (b) a Settings field `deployment_reconcile_seconds` Field(ge=1, le=30) = 10 (`GIP_DEPLOYMENT_RECONCILE_SECONDS`), DP-R2 (a) restart-equivalent hydration, DP-R3 (a) no compose runtime run; condition: the 03 dated note names the field, its bounds and the NFR-494 derivation; reds in one single-tenant DB window; green + SOLO full gate Wed 4 Nov; hard stop Mon 9 Nov.
**MERGE-ACK:** (added at merge)

## Tasks

### Scope

PL-1688 row 3 ("A new row 3: SL 8286 — FD-1823's reconcile …") at `origin/draft/pl-fd1823` 67900242, items R0–R3, G, A1–A10, DP-R1..R3. Requirements: `03` FR-268 (dated note at :213), FR-269 (a rollback writes a new `DeploymentRow`, so the same read converges a missed rollback COMMIT); NFR-494 is the bound for B, not re-measured. Register FD-1823 closes at merge (the auditor's, A9).

**Not applicable, moot (A10):** "no window beside nfr-bench-1" — nfr-bench-1 is a dedicated VM and reserves no shared-box slot (the maintainer's entry after 15:58:45 GMT, relayed by the lead).

### Task list

- **T0** the row's sites re-read at the base 67900242 (+ origin/main 5a9e47c5 merged clean as 2addaa6b): `main.py:141` ("it names no such process … FD-1823"), `score.py:234`, `deployments.py:688`, `deployment_switch.py:19` (the FD-1823 cites), `deployment_switch.py:128` (`load_latest`), `:442`/`:446` (transports fixed at construction), `main.py:142-149` (slug read), `test_deployment_switch_http.py:63` `_DeafToCommit`, `:156`, `config.py:184` `job_stall_seconds`, `03` :213 / :1042 / :1584. No site had moved.
- **T1 reds** (commit f83dffd3, tests only): R1.a, R3.a, R3.b (unit, `test_deployment_switch.py`); R1.b, R1.c, R2, R3.c (HTTP, `test_deployment_switch_http.py`). A test-only repair followed in 03d98c21 (see Build log).
- **T2 fix** (706a7f0c) and **spec notes** (139899bd), within the row's write set.

**The design, by site.** `LiveRefs.reconcile(read)` (one pass; never backwards), `LatestState` / `read_latest(session)` (the DB read), `SwitchReconciler` (the loop: every B seconds or when `wake` is set; a failing pass is logged and the loop goes on), `SwitchSubscription.ensure(environments)` (subscribe and join new Environments; restart a dead listener and re-subscribe/re-join all), `Settings.deployment_reconcile_seconds`, wired in `main.py`'s lifespan.

**The hook for R1.c (A3):** `SwitchSubscription` registers its bound method `_on_connect` with `register_connect_callback` on the pub/sub connection (redis-py holds callbacks weakly, as bound methods); it sets the `reconnected` asyncio.Event, which is the `wake` of `SwitchReconciler`, so a reconnect runs a pass at once.

**Two deviations from the row, accepted by the lead (message to exec-sl8286, after 139899bd):**
1. **R3.a "never backwards" by a per-key write counter**, not by comparing `(deployed_at, id)`: `LiveRefs.reconcile` snapshots the per-key write counts before the read and keeps any entry a COMMIT wrote while the read was in flight. Evidence the row's comparison was not implementable: `LiveEntry` is `(deployment_id, rating_version_ref, bundle_hash)` and `SwitchMessage` carries `switch_id, phase, workspace_id, environment, deployment_id, rating_version_ref, bundle_hash`; neither holds `deployed_at` (`backend/src/app/platform/deployment_switch.py`, `class LiveEntry`, `class SwitchMessage`). The test that a COMMIT written during a pass's in-flight read is kept: `test_r3a_a_commit_landing_during_a_pass_read_is_not_overwritten_by_the_older_read`.
2. **R1.c is deterministic**: the app's member is deaf to COMMIT (so deploy 2 commits in the DB and the app misses it), B = 30 (the ceiling, so no tick can converge it inside the 5 s margin), then `pubsub.connection.disconnect()` in-process on the app's loop (never `CLIENT KILL`); only the reconnect hook can converge it. No racing publish in the gap.

**Other test-design notes.** The HTTP tests set B through `settings.model_copy(update={"deployment_reconcile_seconds": n})`, which at the base (no such field) is silently ignored, so the base runs on the absence of any reconcile, not on a settings error. R1.b/R1.c substitute the app's `SwitchMember` with `_DeafWhenSet` (the file's `_DeafToCommit` made switchable) by monkeypatching `app.main.SwitchMember`; the subscription is captured by monkeypatching `app.main.SwitchSubscription`.

### Gate

**Window** (grant: to-lead "2026-11-03 17:19:47 GMT" for the DB-free runs; the DB window by the lead's message "gate-1 END", 18:20:41 UTC): START 18:21:05 UTC (load1 1.55, mem avail 25 GiB; datnames `gipricing postgres template0 template1`; redis db 11 dbsize 0); own DB `gipricing_sl-8286_5f177197` by `createdb -T gipricing`, `alembic upgrade head` rc=0 against that copy only; `GIP_REDIS_URL=redis://localhost:6379/11`. END 18:27:15 UTC: redis db 11 `flushdb` then `dbsize` = 0 (db 12, 13 = 0); `dropdb` rc=0; datnames back to `gipricing postgres template0 template1`; `select count(*) from pg_database where datname='gipricing_sl-8286_5f177197'` = 0.

**DB-free runs under the 17:19:47 grant** (`test_deployment_switch.py` only, via `run-heavy.sh --grant`, under gate-2; `GIP_TEST_DATABASE_URL` and `GIP_TEST_APP_DATABASE_URL` set to a dead port, because `conftest_db.py:1632` `_empty_the_database_after_the_session` is session-autouse and truncates the owner DB at teardown; teardown warned ConnectionRefused, nothing reached Postgres or Redis). The first two runs started at load1 3.07 and 4.02, above the grant's < 3 (recorded; both ended in under a second).

| Run | head= / src | Result | rc |
|---|---|---|---|
| unit RED (structural) | f83dffd3, `backend/src` == f83dffd3 (`git diff --quiet` rc=0) | 3 failed, 12 passed; the three `ImportError: cannot import name 'LatestState'` (R1.a, R3.a, R3.b). **Structural rereds**: they prove the symbol is absent, not behaviour. | 1 |
| unit GREEN | 139899bd | 15 passed | 0 |

**HTTP reds at the base source** (head=03d98c21 tests, `backend/src` == f83dffd3, `git diff --quiet f83dffd3 -- backend/src` rc=0; restored after, `git diff --quiet HEAD` rc=0). `-k "r1b or r1c or r2 or r3c"`, `--tb=short`. Result line `4 failed, 5 deselected, 1 warning in 48.17s`, rc=1. Each by its cause, on behaviour:

- R1.b `AssertionError: live still names 01a1a2a8-1485-… , not 01a1a2a8-1558-…` — the previous Deployment is still served (assertion line `assert await _until(converged, 1 + 5), (f"live still names …`).
- R1.c `AssertionError: live still names 01a1a2a8-57ac-… after the reconnect` — the reconnect converges nothing.
- R2 `AssertionError: the app's process never joined the new roster`.
- R3.c `AssertionError: the listener task is still dead`.

At the first red attempt (head 139899bd tests) R1.c was reported only as the lifespan-shutdown `redis.exceptions.ConnectionError: Connection closed by server` (the base listener dies on the dropped connection and `SwitchSubscription.stop` re-raises it), which masked the body failure; 03d98c21 makes `_app` report a failing body as itself.

**Greens at head=03d98c2170d7f7cbe283e1b91d91c9f2057f0480** (each file singly, DB window above, `-rs`):

| File | Result | rc |
|---|---|---|
| `backend/tests/test_deployment_switch_http.py` (R1.b, R1.c, R2, R3.c and the 5 existing tests, `test_a_partial_commit_names_the_unacknowledged_process_possibly_stale` unchanged) | 9 passed, 1 warning in 51.10s | 0 |
| `backend/tests/test_config.py` (incl. the new bounds test) | 43 passed | 0 |
| `backend/tests/test_deployment_switch.py` | 15 passed | 0 |

**Static / docs at 03d98c21 (plus uncommitted nothing):** `ruff check` (backend/src and the four test files) rc=0; `ruff format --check` on the changed files rc=0; `mypy` rc=0 (251 source files) at 706a7f0c, and src is unchanged since; `python3 scripts/audit-docs.py` rc=0 ("All checks passed.", before this file was added); `req-coverage.py` rc=0.

**A6:** `git diff origin/main...HEAD -- backend/tests/test_deployment_switch_http.py | grep -c '^-[^-]'` = 0 removed lines. **A7:** `git grep -n -i "not built here\|until it restarts" -- backend/src` prints nothing (rc=1); every `FD-1823` line under `backend` states the reconcile. The "full gate" (G), the GREEN import-closure set (seat brief item 29) and its skipped count are the separate SOLO gate seat's (Wed 4 Nov); not run here.

### Audit

(the auditor's)

### Build log

- 2026-11-03 f83dffd3 — reds only (T1).
- 2026-11-03 706a7f0c — the fix (T2), `Settings.deployment_reconcile_seconds`, `test_config` bounds test.
- 2026-11-03 139899bd — `03` dated note after :213 and the :1042 parenthetical.
- 2026-11-03 03d98c21 — test-only repair found in the window: the shared helper asserted the app was still stale after deploy 2, which is false for R1.b at B = 1 once the reconcile exists (it converges during the 10 s COMMIT wait); the assertion moved to R1.c (B = 30). `_app` now reports a failing body as itself. The base reds were re-run on this head (above). No test was removed or weakened (A6).

## PRs

(none yet; the lead opens the PR after the SOLO gate)
