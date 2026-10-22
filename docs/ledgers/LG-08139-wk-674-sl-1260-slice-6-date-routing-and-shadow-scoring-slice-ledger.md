---
id: LG-8139
family: ledger
title: WK-674 slice SL-1260 — Slice 6, date-based routing and shadow scoring (PL-1537 R6.1 to R6.3) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-21
owner: executor
tree: 44c18e11
phase: P2
work: WK-674
slice: SL-1260
plans: [PL-1537]
corrected_by: []
relates: [PL-1537, PL-1237, PL-1620, SL-1260, SL-1259, RL-1311, RL-1232]
---

# LG-8139 — WK-674 slice SL-1260: Slice 6

Filed 2026-10-21 under working id 8139 (lead-reserved in eta.md 15:04:27). Executor seat `exec-1260`, base `origin/main` 44c18e11, branch `sl-1260-wk674-s6`.

**GO:** the maintainer's (by delegation) entry "2026-10-21 15:03:33 BST — Maintainer: GOs on the 15:02:44 work queue", item 5. **MERGE-ACK:** not yet given.

## Scope

No leaf plan (`PL-1620` :26): the scope is `PL-1237` Task 6 as changed by `PL-1537` R6.1 to R6.3 (the SL-1260 row of `PL-1537`; write-set its S6 row). Cut-ladder rung 5, lowest priority: it takes a gate only when no row-2 slice waits.

## Needs census (on main 44c18e11)

- `SL-1259`: roadmap row `status: closed`.

## Tasks

Task rows are appended here as each task starts. The order follows `RL-1834`'s "What it obliges"
and its Acceptance list. Resume under `RL-1834` by exec-1260c, 2026-10-22 (the maintainer's
(by delegation) entry "2026-10-22 11:44:34 BST", SL-1260 RESUME GO).

| Task | What | State |
|---|---|---|
| T2 | `03` FR-270 clarification, §4.13, §5.1 routing row | done, `5f406245` |
| T3 | `model-schema` routing and shadow shapes, generated schemas | done, `2720bcce` |
| T4 | `routing_rules`, `shadow_configs`, `shadow_results`: models, migration `9b3e7c15d4a2`, immutability seed rows, `DEPLOY_DATE_RANGE_OVERLAP`, the two Environment-only flags | written unrun in `c53d75f0`; reviewed 2026-10-22 (below) |
| T5 | routing write: `platform/routing.py`, `PUT .../routing`, tests first | tests `1f119659`; code next commit; unrun (no DB window) |
| T6 | selection in `/score` (flag, pin check, byte-identical flag-off), `test_routing.py` | owed |
| T7 | `PUT .../shadow` route, `deployment.shadow_configured`, tests | owed |
| T8 | shadow scoring after the response, `shadow_results` writes, tests | owed |
| T9 | settings tests (R6.1), regenerate contracts and INDEX, gate | owed |

**WIP review of `c53d75f0`, 2026-10-22.** Right: the three tables, columns, `ck_`/`fk_` names
(they match the model's naming convention), the indexes, the `artifact_append_only()` trigger
pair and the `SELECT, INSERT`-only grants follow `c4a81f6d2e95`'s `deployments` exactly; the
revision chains onto `a4d1f08c3b97`, the one head; the two flags are Environment-scoped with
`SAFE_DEFAULT` False (RL-1834 D2 item 1); `DEPLOY_DATE_RANGE_OVERLAP` is registered once; the
immutability seed rows satisfy each table's one foreign key. Missing or unverified, none run:
the migration has not been applied; `ruff format` has not been run on the new files;
`test_migration_deployments.py`'s pattern (grants, triggers, downgrade) has no counterpart for
the three tables; `test_settings.py` has no test of the two flags (R6.1, RL-1311:275).

## PRs

None yet. The slice stops at PR-READY; the lead opens the PR.
