---
id: LG-1855
family: ledger
title: WK-1178 slice SL-1854 — FD-1838, the deployment switch's channels carry the gate slot's name (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
slice: SL-1854
plans: []
corrected_by: []
relates: [SL-1854, FD-1838, SL-1711]
---

# LG-1855 — WK-1178 slice SL-1854: FD-1838, the deployment switch's channels carry the gate slot's name

Filed 2026-10-22 under working id 8171 (lead-reserved in eta.md); minted 2026-10-22 as LG-1855 (history lines below that quote "LG 8171" or "SL 8170" name this ledger and its slice by their working ids); executed by `exec-1838`, base `origin/main` `f3462d8fc1336dc4583fe8a7af92fed399993a55`, branch `fix/fd-1838-switch-namespace`.

**GO:** the maintainer's (by delegation) entry "2026-10-22 15:43:10 BST — Maintainer: SPEED MEASURES …" item 2 (`to-lead.md`): FD-1838 prioritised, built red-first, the remedy as reserved at "2026-10-21 21:13:34 BST"; dispatched by lead 26 in the brief `brief-exec-1838-2026-10-22.md`.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`SL-1854` (a Work-plan delta row under WK-1178, Lean P2 L5), quoted: "one helper `switch_stack(environment, tenant_id)` that builds the stack prefix for both of its callers … and appends `basename($GIP_GATE_SLOT)` when the variable is set, through `RedisSwitch`'s existing `stack` argument; a process with no slot (production) is unchanged. Red first: a test with a foreign subscriber on the unsuffixed channel." Requirements covered: none new; FR-268 (the switch) keeps its behaviour. Remedy per FD-1838's "Remedy (not made here)".

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

The gate ran 2026-10-22 from 16:09:23Z to 17:32:38Z on slot `gate-1b`, head `34c427ea3a65dfc38858890e0923f17437f95373` (tree `69a895dce4aca6c3281fce51f27eb19ed1994c0c`), script `~/gi-pricing-plan.local/scratch/fd1838-gate.sh` (a substitution-only copy of `sl1711-gate.sh` plus one `GIP_GATE_SLOT` preflight row); logs `~/gi-pricing-plan.local/scratch/fd1838-gate/`. The gate log, verbatim:

```
START head: 34c427ea3a65dfc38858890e0923f17437f95373 tree: 69a895dce4aca6c3281fce51f27eb19ed1994c0c branch: fix/fd-1838-switch-namespace load(date l1 l5 l15): 2026-10-22T16:09:23+00:00 2.09 2.68 2.78
| redis isolation | pytest db 2, demo db 4 (GIP_REDIS_URL) |
| bucket gip-test-blobs-gate-1b reset (start) | rc=0 |
| bucket gip-blobs-demo-gate-1b reset (start) | rc=0 |
| test bucket | GIP_TEST_BUCKET=gip-test-blobs-gate-1b |
| isolation (gate env) | gate effective broker: redis://localhost:6379/2 blob_bucket: gip-blobs blob_endpoint: http://localhost:9000 |
locks held: gate-1b held, gate-2 NOT-HELD, small-test held
## preflight
| head guard | ok |
| GIP_GATE_SLOT | /tmp/slots/gate-1b (exported) |
| branch | ok |
| clean tree | ok |
| createdb gipricing_fd-1838_gate | rc=0 |
| alembic upgrade | rc=0 |
| alembic heads | 1 head(s) |
| container gi-pricing-keycloak-1 | healthy |
| container gi-pricing-minio-1 | healthy |
| container gi-pricing-postgres-1 | healthy |
| container gi-pricing-redis-1 | healthy |
| pg_isready | rc=0 |
| redis db 2 FLUSHDB (start) | rc=0 |
| redis db 4 FLUSHDB (start) | rc=0 |
| redis dbsize after start flush | RT db 2=0 RD db 4=0 |
## python half
| ruff | rc=0 |
| mypy | rc=0 |
| import_linter | rc=0 |
| audit_docs | rc=1 |
| req_coverage | rc=0 |
| contracts | rc=0 |
| pytest | rc=1 |
pytest summary: 13 failed, 6646 passed, 19 skipped, 135 warnings in 3090.46s (0:51:30)
## frontend half
| pnpm install --frozen-lockfile | rc=0 |
| pnpm generate:api | rc=0 |
| pnpm lint | rc=0 |
| pnpm type-check | rc=0 |
| pnpm test --maxWorkers=2 | rc=0 |
| pnpm build | rc=0 |
tree after gate: 0 changed path(s)
## demo (wf-699, with the frontend)
| demo lock wait start | 2026-10-22T17:04:13+00:00 |
| demo lock acquired | 2026-10-22T17:04:13+00:00 |
| quiet window | load1 < 2.0 after 300 s |
NOTICE:  database "gipricing_fd-1838_demo" does not exist, skipping
| createdb demo | rc=0 |
| compose + bind mounts | = origin/main |
| demo redis db 4 purge (start) | rc=0 |
| isolation (demo worker env) | demo effective broker: redis://localhost:6379/4 blob_bucket: gip-blobs-demo-gate-1b blob_endpoint: http://localhost:9000 |
| demo alembic | rc=0 |
| demo start load1 | 1.97 at 2026-10-22T17:09:15+00:00 |
| demo | designed stop at 2026-10-22T17:31:52+00:00 (both lines seen) |
| demo.py --journey wf-699 | rc=0 |
| demo seconds | 1363 |
| dislocation #1 | 451 s |
| demo end load1 | 3.62 at 2026-10-22T17:31:58+00:00 |
| D7 | ok  19985 policies in the sample; rate table edits: +485990825; NCD ladder and expense loading: +3851186; sum +489842011 minor units (full-book attribution cost: FD-1576) |
| demo redis db 4 purge (stop) | rc=0 |
| keycloak restore from tools-main (up -d --no-deps --wait keycloak) | rc=0 |
| keycloak bind source | /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy/keycloak-local  (under tools-main) |
| demo lock released | 2026-10-22T17:32:36+00:00 |
| bucket gip-test-blobs-gate-1b removed (end) | rc=0 |
| bucket gip-blobs-demo-gate-1b removed (end) | rc=0 |
| dropdb gipricing_fd-1838_gate (end) | rc=0 |
| dropdb gipricing_fd-1838_demo (end) | rc=0 |
| redis db 2 FLUSHDB (end) | rc=0 |
| redis db 4 FLUSHDB (end) | rc=0 |
| zeros | own-DB count=0 redis RT db 2 dbsize=0 redis RD db 4 dbsize=0 |
END 2026-10-22T17:32:38+00:00 4.15 4.24 4.40 (date l1 l5 l15)
```

Pytest: `13 failed, 6646 passed, 19 skipped`; vitest `Test Files  129 passed (129)`, `Tests  817 passed (817)`. The 13 FAILED lines, by file (a nodeid listed twice in `pytest.log` is counted once):

- `tests/test_audit_docs_finding_citations.py`: `test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`
- `tests/test_audit_docs_ids.py`: `test_the_real_tree_passes_all_ten_checks`, `test_doc_id_check_exits_0_on_the_real_tree`
- `tests/test_audit_docs_process_core_digest.py`: `test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`, `test_the_committed_digest_currently_matches_the_committed_spec`
- `tests/test_audit_docs_w37_11_ceiling.py`: `test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`
- `tests/test_doc_index.py`: `test_an_index_skipping_a_reserved_block_breaks_contiguity`
- `tests/test_register_lint.py`: `test_check_29_is_wired_into_the_docs_gate`, `test_check_29_note_carries_the_residue_line`, `test_phase1b_residue_count_matches_check_29s_own_count`
- `tests/test_register_owed.py`: `test_check_29_wiring_is_undisturbed`
- `tests/test_repository_invariants.py`: `test_money_discipline_is_enforced_by_the_docs_audit`, `test_journey_citations_are_audited_in_ci`

**Reading (lead 26, relaying the maintainer's standing 1(f) of "2026-10-22 18:02:34 BST"):** the frontend and the demo are green and the python failures are exactly the docs-audit set, the gate stands. These tests read `scripts/audit-docs.py` on the real tree, which exits 1 at this head on the unminted working ids (check 31: a gap in the allocation below the then-unminted ids); the 13 re-run on the minted head. The overlap: SL-1260's DB window ran beside this gate by the maintainer's deliberate exception (`to-lead.md` 17:10:35); its TestClients subscribe on the unsuffixed switch channels and this gate's are `gate-1b`-suffixed, and no switch-touching test failed here.

**The 13 re-run on the minted head** `89eea73d6e20fdd5dbf861c3809d9f70854cb489` (2026-10-22, `run-small.sh`, DB-free, three calls of at most 3 files; `audit-docs` at that head: rc 0, "All checks passed."):

- `tests/test_audit_docs_finding_citations.py`, `tests/test_audit_docs_ids.py`, `tests/test_audit_docs_process_core_digest.py`: rc=0, `124 passed in 202.81s (0:03:22)`.
- `tests/test_audit_docs_w37_11_ceiling.py`, `tests/test_doc_index.py`, `tests/test_register_lint.py`: rc=0, `110 passed in 94.71s (0:01:34)`.
- `tests/test_register_owed.py`, `tests/test_repository_invariants.py`: rc=0, `23 passed in 72.76s (0:01:12)`.

All 13 previously failing tests pass; the gate's pytest count is 13 failed, 6646 passed at `34c427ea`, and the full suite is not re-run for a docs-only delta (mint, merges of main).

### Audit

Not yet written.

### Build log

- 2026-10-22 `a83531d0` red commit; `b95c9d3d` fix commit; pushed to `fix/fd-1838-switch-namespace`.
- 2026-10-22 16:19 BST the gap run above (lead 26's "GAP OPEN 1838").

## PRs

- #1363 — `fix(backend): SL-1854 — FD-1838, the switch channels carry the gate slot's name`, opened 2026-10-22; merge commit: not yet merged.
