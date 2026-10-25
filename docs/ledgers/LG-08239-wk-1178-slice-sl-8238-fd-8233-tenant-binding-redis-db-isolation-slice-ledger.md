---
id: LG-8239
family: ledger
title: WK-1178 slice SL-8238 — FD-8233, the tenant-binding tests' Redis db follows GIP_REDIS_URL and avoids the gate dbs (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-25
owner: executor
tree: 102341aade6720dc7b71a1e696cc5b6d8017a2f1
phase: P2
work: WK-1178
slice: SL-8238
plans: []
corrected_by: []
relates: [SL-8238, FD-8233]
---

# LG-8239 — WK-1178 slice SL-8238: FD-8233, tenant-binding Redis db isolation

Working ids 8238 (SL) and 8239 (LG), unminted. Executed by `exec-fd8233`, base `origin/main` `102341aade6720dc7b71a1e696cc5b6d8017a2f1`, branch `fix/fd-8233-tenant-binding-redis-db`.

**GO:** the maintainer's entry "2026-10-25 21:06:06 GMT" (`to-lead.md`), item (4): "GO — FD 8233 fix slice on fix/fd-8233-tenant-binding-redis-db from 102341aa: red-first asserts (i) with GIP_REDIS_URL set the db equals the url's, (ii) unset → db ∉ {1,2,3,4,11,12,13}; DB-free red→green via run-heavy; gate in the next free slot". Remedy accepted at "2026-10-25 18:59:00 GMT": derive the db from `GIP_REDIS_URL` when set, else a range no gate or run-small uses (5–10).
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`backend/tests/test_tenant_binding.py`'s `redis_url` fixture drew `1 + randbelow(15)`, i.e. dbs 1–15, which collides with the gates' dbs (1–4) and the seats' (11–13). It now returns `GIP_REDIS_URL` when set, else a db in 5–10. Requirement touched: FR-436 (tests only; no application code).

### Task list

1. Red: `backend/tests/test_tenant_binding_redis_db.py` (new, DB-free): (i) `GIP_REDIS_URL=redis://localhost:6379/7` → db 7; (ii) unset, 300 draws → none in {1,2,3,4,11,12,13}, all in 5–10.
2. Fix: `redis_url` in `test_tenant_binding.py`.
3. Green: same run.

### Gate

(left empty for the lead's gate; owed: prelaunch-check, full code gate, audit-docs, the 13)

### Audit

(not yet)

### Build log

- 2026-10-25, DB-free, via `run-heavy.sh -- scripts/run-small.sh <wt> backend/tests/test_tenant_binding_redis_db.py`; the 2 warnings are the Starlette `httpx` deprecation and the per-worktree test-database teardown notice (no database used).
  - **RED** at `a4531d805cde986d18aa64ebb732c79262a869c5`: `FAILED backend/tests/test_tenant_binding_redis_db.py::test_set_gip_redis_url_db_is_used`, `FAILED backend/tests/test_tenant_binding_redis_db.py::test_unset_gip_redis_url_draws_outside_reserved_dbs`, `2 failed, 2 warnings in 0.56s`, rc=1.
  - **GREEN** at `1a8762d41bd93c00771a5e91d6d4342434efeaf2`: `2 passed, 2 warnings in 0.35s`, rc=0.
  - `ruff check` on both files at `1a8762d4`: `All checks passed!`, rc=0. `ruff format --check`: the new file is clean; `test_tenant_binding.py` reports reformatting on lines this slice did not touch (:82, :163, :204), left as they are.

## PRs

(none yet)
