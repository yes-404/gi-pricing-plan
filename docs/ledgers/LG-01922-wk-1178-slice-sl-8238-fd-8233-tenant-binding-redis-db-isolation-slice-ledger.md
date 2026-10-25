---
id: LG-1922
family: ledger
title: WK-1178 slice SL-1921 — FD-1920, the tenant-binding tests' Redis db follows GIP_REDIS_URL and avoids the gate dbs (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-25   # drafted 2026-10-25 under working id 8239; created = mint date
owner: executor
tree: 102341aade6720dc7b71a1e696cc5b6d8017a2f1
phase: P2
work: WK-1178
slice: SL-1921
plans: []
corrected_by: []
relates: [SL-1921, FD-1920]
---

# LG-1922 — WK-1178 slice SL-1921: FD-1920, tenant-binding Redis db isolation

Working ids 8238 (SL) and 8239 (LG), unminted. Executed by `exec-fd8233`, base `origin/main` `102341aade6720dc7b71a1e696cc5b6d8017a2f1`, branch `fix/fd-8233-tenant-binding-redis-db`.

**GO:** the maintainer's entry "2026-10-25 21:06:06 GMT" (`to-lead.md`), item (4): "GO — FD-1920 fix slice on fix/fd-8233-tenant-binding-redis-db from 102341aa: red-first asserts (i) with GIP_REDIS_URL set the db equals the url's, (ii) unset → db ∉ {1,2,3,4,11,12,13}; DB-free red→green via run-heavy; gate in the next free slot". Remedy accepted at "2026-10-25 18:59:00 GMT": derive the db from `GIP_REDIS_URL` when set, else a range no gate or run-small uses (5–10).
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

2026-10-25 22:25 GMT — correction (RS-1923 B2): the GO quote above is a paraphrase; the verbatim (i) clause of to-lead 21:05:20 item (4) (the brief named the entry 21:06:06; item (4) is in the 21:05:20 GMT entry, to-lead.md:31030) is: "(i) with `GIP_REDIS_URL` set to each slot's url the chosen db equals that url's db". B1 commit 34f870e279f407d47cafeb7f3fdabaf1f1031ac9 parametrises (i) over {1,2,3,4,11,12,13}.
  - **GREEN** at `34f870e279f407d47cafeb7f3fdabaf1f1031ac9` (run-small, DB-free): `8 passed, 2 warnings in 0.43s`, rc=0.
  - **RED** at a4531d80 with only the new test file: NOT RUN — the throwaway worktree needed `uv sync --all-packages --frozen` under run-heavy, which refused rc=76 (gate-1 held, no grant); the step was stopped, not retried by another route. Owed to a gate gap or a grant.
  - `ruff check` on `backend/tests/test_tenant_binding_redis_db.py` at 34f870e2: `All checks passed!`, rc=0; `ruff format --check`: `1 file already formatted`, rc=0.

2026-10-25 22:40 GMT — red/green for B1, from the lead's from-lead entry "2026-10-25 22:36 GMT" (lead-run; supersedes by reference the "RED … NOT RUN" line above, which is not edited). RED, lead-run 22:24:38 UTC, in this worktree at head 680f7e07: `git restore --source=a4531d80 -- backend/tests/test_tenant_binding.py` (pre-fix fixture, uncommitted), run-small on `backend/tests/test_tenant_binding_redis_db.py` → "8 failed, 2 warnings in 0.52s" rc 1 on the a4531d80 fixture; FAILED: test_set_gip_redis_url_db_is_used[1], [2], [3], [4], [11], [12], [13] (the 7 (i) cases) and test_unset_gip_redis_url_draws_outside_reserved_dbs; then `git restore`, porcelain 0; log scratch/fix-8233/red-b1.log. GREEN, lead-run at 680f7e07: `run-small.sh <wt> backend/tests/test_tenant_binding_redis_db.py` → "8 passed, 2 warnings in 0.36s" rc 0.
