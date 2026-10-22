---
id: LG-8201
family: ledger
title: WK-1178 slice SL-8200 — FD-8199, the switch slot-namespace test names a synthetic slot (slice ledger)
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-10-22
owner: executor
tree: 1fe82ee673cc8aef2bd3e70b81b8304059fccbc1
phase: P2
work: WK-1178
slice: SL-8200
plans: []
corrected_by: []
relates: [SL-8200, FD-8199, FD-1838]
---

# LG-8201 — WK-1178 slice SL-8200: the switch slot-namespace test names a synthetic slot

**GO:** the maintainer's entry "2026-10-22 23:42:23 BST" item 1 (`to-lead.md`), via the lead's brief `brief-exec-8200-2026-10-22.md`. Test only; product code untouched.
**MERGE-ACK:** (added at merge)

## Tasks

### Scope

FD 8199 (LOW-MEDIUM, owner WK-1178): `backend/tests/test_deployment_switch_slot_namespace.py` set `GIP_GATE_SLOT` to REAL slot names (`/tmp/slots/gate-1`, `/tmp/slots/gate-1b`). Redis pub/sub channels are server-wide, so a paired gate holding that slot adds a subscriber that the test counts in its PREPARE quorum: SL-1551's gate failed `test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum` with "1 of 2 subscribed processes acknowledged PREPARE". Product code (`switch_stack`) is unaffected. No requirement changes.

### Task list

1. Sweep (`git grep -n '/tmp/slots/gate-' -- backend packages tests frontend scripts`, tree only). In scope: `backend/tests/test_deployment_switch_slot_namespace.py:40,42,52`. Legitimate, not touched: `backend/tests/test_run_small_script.py:134` (proves run-small refusal 65; no Redis); `tests/test_root_conftest.py:211,217` (monkeypatched env, `_acquire_pytest_gate_slot` stubbed); `tests/test_root_conftest.py:312,316` (a regex over the dev-commands skill text).
2. RED: today's test with a subscriber injected on the real `gip:switch:local:local:gate-1:dev` channel, run in a no-gate gap.
3. Fix: a per-run synthetic slot `/tmp/slots/test-<8 hex>` at each hit; two different ones where the test compares two slots. The parametrized `other-slot` case is the permanent stand-in for a paired gate's subscriber, because a permanent test must not subscribe to a real gate channel.
4. GREEN by import closure (common brief item 29).
5. ruff and mypy on the changed file.

### Gate

Run on tree `fix-8199` @ `431c430a23b08e27d9dfd21c6c2072b2a99f5fd1` (tree `7bf0efb4befd96902995805107eb03f1841522ca`), in a no-gate gap opened by the lead (no gate running, all slots free), through `scripts/run-small.sh` of tools-main (read-only use). Per-worktree database `gipricing_fix-8199_a8d78b9c` made with `createdb -T` plus `alembic upgrade head` (rc 0). `GIP_REDIS_URL=redis://localhost:6379/11` (never db 0). Before: `PUBSUB CHANNELS 'gip:switch:*'` empty; `PUBSUB NUMSUB gip:switch:local:local:gate-1:dev` 0. Logs `scratch/fix-8199/431c430a23b08e27d9dfd21c6c2072b2a99f5fd1-*.log`, each named by its head. The injector (`scratch/fix-8199/inject.py`) subscribes to the REAL channel `gip:switch:local:local:gate-1:dev` for 300 s; NUMSUB showed 1 while it ran.

| Run | File | Injected subscriber | rc | Summary |
|---|---|---|---|---|
| RED (log `red-old-with-injected`) | `origin/main`'s test file, copied to an untracked `backend/tests/test_zz_red8199_old.py` and removed after | yes, on `gate-1:dev` | 1 | `1 failed, 2 passed in 4.05s`; `FAILED …::test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum`; `SwitchIncompleteError: 1 of 2 subscribed processes acknowledged PREPARE` |
| GREEN with (log `green-fixed-with-injected`) | `backend/tests/test_deployment_switch_slot_namespace.py` (fixed) | yes | 0 | `4 passed, 1 warning in 1.10s` |
| GREEN without (log `green-fixed-without-injected`) | same | no | 0 | `4 passed, 1 warning in 1.08s` |
| Closure (log `closure-a`) | `test_deployment_switch.py`, `test_deployment_switch_http.py`, `test_score.py` | no | 0 | `69 passed, 3 warnings in 69.90s (0:01:09)` |

**Closure derivation.** The slice changes one test file and no `src` module: `git diff --name-only origin/main...HEAD -- '*.py'` lists only `backend/tests/test_deployment_switch_slot_namespace.py`. Nothing imports a test file, so the closure is that file plus the other tests that import what it imports from `app.platform.deployment_switch`: `git grep -n -E "^(from|import) .*deployment_switch|^from app.platform import .*deployment_switch" -- backend/tests packages tests` lists `test_deployment_switch.py:16`, `test_deployment_switch_http.py:32`, `test_deployment_switch_slot_namespace.py:20` and `test_score.py:47`. The other four files that mention the name (`test_deployment_route_types.py`, `test_deployments.py`, `test_error_sinks.py`, plus three `src` modules) do not import it and do not import any changed file.

**Static checks.** `ruff check` and `ruff format --check` on the changed file: rc 0 and rc 0. `uv run mypy`: `Success: no issues found in 246 source files`.

**Cleanup.** `dropdb` rc 0; `select count(*) from pg_database where datname='gipricing_fix-8199_a8d78b9c'` 0. The runs left 18 ack keys in redis db 11 (switch acks of the `small-test` and `test-…` slots); `FLUSHDB` on db 11, then `redis-cli -n 11 dbsize` 0. `PUBSUB CHANNELS 'gip:switch:*'` empty and NUMSUB on `gate-1:dev` 0 after. Db 0 was not touched (dbsize 56 before and after the flush).

### Audit

(not yet)

### Build log

- 2026-10-22 — branch `fix/fd-8199-synthetic-gate-slot` from `origin/main` @ `1fe82ee6`; test edit, SL-8200 row and this ledger written; nothing run.
- 2026-10-22 — head `431c430a`: RED, GREEN and the closure set run in the lead's no-gate gap; lines in Gate above.

## PRs

(none yet)
