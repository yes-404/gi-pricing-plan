---
id: LG-8171
family: ledger
title: WK-1178 slice SL-8170 — FD-1838, the deployment switch's channels carry the gate slot's name (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
slice: SL-8170
plans: []
corrected_by: []
relates: [SL-8170, FD-1838, SL-1711]
---

# LG-8171 — WK-1178 slice SL-8170: FD-1838, the deployment switch's channels carry the gate slot's name

Filed 2026-10-22 under working id 8171 (lead-reserved in eta.md); executed by `exec-1838`, base `origin/main` `f3462d8fc1336dc4583fe8a7af92fed399993a55`, branch `fix/fd-1838-switch-namespace`.

**GO:** the maintainer's (by delegation) entry "2026-10-22 15:43:10 BST — Maintainer: SPEED MEASURES …" item 2 (`to-lead.md`): FD-1838 prioritised, built red-first, the remedy as reserved at "2026-10-21 21:13:34 BST"; dispatched by lead 26 in the brief `brief-exec-1838-2026-10-22.md`.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`SL-8170` (a Work-plan delta row under WK-1178, Lean P2 L5), quoted: "one helper `switch_stack(environment, tenant_id)` that builds the stack prefix for both of its callers … and appends `basename($GIP_GATE_SLOT)` when the variable is set, through `RedisSwitch`'s existing `stack` argument; a process with no slot (production) is unchanged. Red first: a test with a foreign subscriber on the unsuffixed channel." Requirements covered: none new; FR-268 (the switch) keeps its behaviour. Remedy per FD-1838's "Remedy (not made here)".

### Task list

- [x] **Task 1, red first** (`a83531d0ada360cd92e87fd5a43d3a80668debf4`): `switch_stack` added behaviour-neutral, both callers moved onto it, and `backend/tests/test_deployment_switch_slot_namespace.py` (three tests).
- [x] **Task 2, the fix** (`b95c9d3d5ca070d396096c944e9544a55ba71dfe`): `switch_stack` appends `basename($GIP_GATE_SLOT)`; `.claude/skills/dev-commands/SKILL.md` gains a 3-line note beside the `GIP_GATE_SLOT` paragraph.
- [x] **Task 3, the gap run** (below).
- Where the switch is built: `backend/src/app/main.py` (`RedisSwitch(switch_client, switch_stack(...))`) and `backend/tests/test_deployment_switch_http.py` (`_Peer`). `scripts/run-small.sh` and the gate scripts already export `GIP_GATE_SLOT` (`scripts/run-small.sh:64`; `.claude/skills/dev-commands/SKILL.md` gate template), so none is changed.

**The gap run (2026-10-22, START 15:18:25 UTC, END 15:19:08 UTC; no gate, no other switch test).** Before each run `PUBSUB NUMSUB gip:switch:local:local:{dev,uat,prod}` = 0/0/0 and `PUBSUB CHANNELS 'gip:switch:*'` empty; after the green run, 0/0/0 and empty. Logs, first line `tree <sha>`: `~/gi-pricing-plan.local/scratch/fix-1838/red.log`, `~/gi-pricing-plan.local/scratch/fix-1838/green.log`.

- RED, `run-small.sh` on `backend/tests/test_deployment_switch_slot_namespace.py`, throwaway worktree at `a83531d0ada360cd92e87fd5a43d3a80668debf4`, rc=1:
  `FAILED backend/tests/test_deployment_switch_slot_namespace.py::test_two_gate_slots_get_two_stacks`
  `FAILED backend/tests/test_deployment_switch_slot_namespace.py::test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum`
  `E       app.platform.deployment_switch.SwitchIncompleteError: 1 of 2 subscribed processes acknowledged PREPARE; possibly stale (unacknowledged; a ghost of a crashed process may be among them): []`
  `2 failed, 1 passed, 2 warnings in 3.35s`
- GREEN, `run-small.sh` on `backend/tests/test_deployment_switch_slot_namespace.py` and `backend/tests/test_deployment_switch.py`, tree `b95c9d3d5ca070d396096c944e9544a55ba71dfe`, rc=0:
  `15 passed, 2 warnings in 0.26s` (0 failed, 0 skipped; the warnings are `GIP_TEST_DATABASE_URL is not set` and a Starlette deprecation).
- Throwaway worktree removed; `docker inspect` of the postgres, redis, minio and keycloak containers showed 0 mounts under it.
- Not run: `test_deploy_switch_runtime.py`, `test_deploy_stack_runtime.py` and the WF-701 journey (DB-backed); the slice gate's full suite is the decisive green.

**Static, at `b95c9d3d5ca070d396096c944e9544a55ba71dfe`:** `ruff check` on the 4 changed files rc 0; `ruff check .` rc 0; `ruff format --check` on the 4 changed files rc 0; `mypy` rc 0 (244 source files); `lint-imports` rc 0.

**Deviation (recorded, lead 26, 2026-10-22):** the full-repo `ruff check .`, `mypy` and `lint-imports` ran beside a running code gate, where the brief said changed files only.

### Gate

| Command | rc | Tree |
|---|---|---|
| | | |

### Audit

Not yet written.

### Build log

- 2026-10-22 `a83531d0` red commit; `b95c9d3d` fix commit; pushed to `fix/fd-1838-switch-namespace`.
- 2026-10-22 16:19 BST the gap run above (lead 26's "GAP OPEN 1838").

## PRs

Not yet opened. The PR title names `SL-8170`.
