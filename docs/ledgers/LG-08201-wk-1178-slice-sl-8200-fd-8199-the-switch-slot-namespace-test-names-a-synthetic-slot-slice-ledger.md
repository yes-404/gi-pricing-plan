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

(RED and GREEN lines are recorded here, verbatim, before the audit. Not run yet: the tests need the per-worktree database, so they wait for a no-gate gap.)

### Audit

(not yet)

### Build log

- 2026-10-22 — branch `fix/fd-8199-synthetic-gate-slot` from `origin/main` @ `1fe82ee6`; test edit, SL-8200 row and this ledger written; nothing run.

## PRs

(none yet)
