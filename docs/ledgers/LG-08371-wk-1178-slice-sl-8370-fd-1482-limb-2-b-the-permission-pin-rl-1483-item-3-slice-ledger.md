---
id: LG-8371
family: ledger
title: WK-1178 slice SL-8370 — FD-1482 limb 2 (b), RL-1483 item 3: the permission pin (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05            # filed under working id 8371
owner: executor
tree: 7400f0e5                    # sl-8370-permission-pin (base sl-8343 5748acc7bf0ea1ae83a1a63f81460f6b6d53f506 + sl-8361 921d9a3e5bed8d70f198dd118c97c65a81bf3a14 by sha)
slice: SL-8370
phase: P2
work: WK-1178
plans: []
corrected_by: []
relates: [FD-1482, RL-1483, FR-343]
---

# LG-8371 — WK-1178 slice SL-8370: the permission pin

**GO:** to-lead "2026-11-05 15:55:35 GMT" (2); rulings to-lead "2026-11-05 16:11:02 GMT". **MERGE-ACK:** none yet (unpushed).

## Tasks

### Scope

RL-1483 item 3: `backend/tests/test_route_permission_pin.py` compares, for every live route (included routers flattened), the `Permission` cell of its §5.1 row with what the route checks, failing in both directions. Rows are read through `model_schema.table_rows`; paths as `audit-docs.py`'s `_path_segments`. The declaration is never generated from `requires()` (RL-1483's rejected option (c)). DB-free.

**Route side, by what proves it** (ruled 16:11:02 GMT): the `PERMISSION_ATTRIBUTE` of `requires()` (dependency); a `require_permission(permission=)` call in the handler body (inline); the same in a function the handler calls that is defined in the same module, ONE level, by what the call reaches (one-level); the `HANDLER_GUARDED` code sites (site); and one NAMED entry, `PATCH /datasets/{dataset_id}` → `platform/datasets.py:set_owner` (FR-82), proved by AST: one `if` testing `is_owner` and `ADMIN_MANAGE_ROLES` whose body raises, with `is_owner` assigned. A test asserts the named list's exact contents.

**Counts** (predicate: `/tmp/sl8370_count.py`, not committed: each of the 168 operations of `_flattened_operations(create_app(...).routes)` classified, first match in the order open, named, site, one-level, inline, dependency, else authenticated; module = the spec file of the row read; at this tree):

| Module | dependency | inline | one-level | site | named | authenticated | open | routes |
|---|---|---|---|---|---|---|---|---|
| 01 | 38 | 0 | 0 | 1 | 1 | 0 | 0 | 40 |
| 02 | 44 | 1 | 0 | 0 | 0 | 0 | 0 | 45 |
| 03 | 35 | 2 | 3 | 5 | 0 | 0 | 0 | 45 |
| 06 | 6 | 0 | 0 | 1 | 0 | 6 | 0 | 13 |
| 07 | 19 | 0 | 0 | 0 | 0 | 1 | 5 | 25 |
| total | 142 | 3 | 3 | 7 | 1 | 7 | 5 | 168 |

Total checkable by the pin: 168 (every live operation has a row).

### Gate

`pytest -q backend/tests/test_route_permission_pin.py` at the build head: 20 passed, 1 failed, the live comparison, red on exactly two routes, both findings, no exemption (ruled):
- `POST /api/v1/models/{model_id}/archive`: spec 02:1920 `model:fit`; code `model:submit` (FD 8366, merges first; the pin takes its own gate slot after it).
- `GET /api/v1/dislocation-runs/{run_id}/movers`: spec 03:1128 cell `rating:read`; code checks `dataset:read` and `rating:read` (handler calls `_require_dataset_read`; its Purpose text and docstring say both). Found by the one-level walk; the cell is not changed here.

### Red first (planted on the live tree, each reverted)

- `ReadAudit` AUDIT_READ→JOB_READ: "GET /api/v1/audit: spec (06-governance.md:580) says '`audit:read`'; code checks job:read".
- Cell swapped, `GET /datasets` → `job:read`: "spec (01-data-management.md:858) says '`job:read`'; code checks dataset:read".
- Handler-guarded code swap (deployments.py DEPLOYMENT_PROMOTE→DATASET_READ) and the deploy row's cell → `rating:read`: both named the deployment routes.
- Handler's `_require_dataset_read` call removed from `start_dislocation_run`: "POST /api/v1/dislocation-runs: … code checks rating:compile".
- Helper's `require_permission` removed: dislocation-runs and /estimate both red.
- `set_owner` owner limb removed, then admin limb removed: each "PATCH /api/v1/datasets/{dataset_id}: … code checks dataset:read".
- Synthetic: swapped cell, swapped requires, missing row, authenticated/open mismatches, empty cell, two levels deep, another module, each named limb and the raise.

### Audit

Not yet. The auditor's.

### Build log

- 2026-11-05 — merge of sl-8361 @921d9a3e onto sl-8343 @5748acc7 (INDEX conflict only, regenerated); pin `d0a01354`; one-level walk and the named list in the next commit.

## PRs

None. Ends unpushed.
