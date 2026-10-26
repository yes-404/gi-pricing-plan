---
id: FD-1920
family: finding
title: The tenant-binding test draws its Redis db from 1-15, ignoring GIP_REDIS_URL, so a paired gate can false-red
status: active
created: 2026-10-25   # drafted 2026-10-25 under working id 8233; created = mint date
owner: auditor
tree: 680f7e07e2d86a088c781d127a5e7d0a84dbd91f
corrected_by: []
relates: [WK-1178, SL-1921, LG-1922]
---

# FD-1920 — The tenant-binding test draws its Redis db from 1-15, ignoring GIP_REDIS_URL, so a paired gate can false-red

## Finding

**LOW; owner WK-1178. A test-isolation defect that pairing exposes; no product code is wrong and no price is affected.** Authority: the
maintainer's entry "2026-10-25 18:59:00 GMT — Maintainer: #1384 MERGED and VERIFIED …" (`to-lead.md`), item (1): "FD, LOW, owner WK-1178 — ACCEPTED
(an FD, not a backlog row: it lets a false gate result through under pairing and blocks work today)." Filed under working id 8233.

The test's `redis_url` fixture in `backend/tests/test_tenant_binding.py` returned `redis://localhost:6379/{1 + secrets.randbelow(15)}` (:43–45): a
random db 1–15 that ignores the gate's `GIP_REDIS_URL` isolation (gate-1 = db 1/3; gate-1b = db 2/4; run-small = 11; a seat's own run uses 11, 12 or 13).
`tenancy.py:80` SETNXes `gip:tenant` on every app start, so a draw landing on a paired gate's db finds that gate's tenant marker ("local").
**Cause: a test-isolation defect that pairing exposes; serial gates never collided.**

## Evidence

- **First observation:** SL-1552's gate @6975e2be (gate-1b, paired with SL-1569): pytest `14 failed, 6781 passed` — 13 = the 8-file docs-audit set, plus one real:
  `backend/tests/test_tenant_binding.py::test_the_database_is_checked_before_any_other_store_is_written` (:139, `assert 'local' is None`). Verified by the
  maintainer at `origin/main` (entry above).
- **Untouched since** aa14e90d (2026-09-30, #933); not in SL-1552's diff (entry above).
- **Earlier note:** the process backlog carried the same range on 2026-10-17 18:17:21 BST ("picks a random Redis db from 1 to 15 for its marker, which can
  land on a gate's per-slot db"), as a minor flake risk; the 18:59:00 entry raised it to a finding because it produced a false gate result.
- **Regression proof of the remedy:** `backend/tests/test_tenant_binding_redis_db.py` (SL-1921). Red: the pre-fix fixture a4531d80 restored over
  `test_tenant_binding.py`, run-small on that file, `8 failed, 2 warnings in 0.52s` rc 1; green at 680f7e07, `8 passed, 2 warnings in 0.36s` rc 0
  (LG-1922, the appended line of this slice).

## Severity

LOW, as ruled. Product impact is none; the cost is a false red on a gate under pairing, which blocks work and spends a gate slot.

## Remedy

The maintainer's remedy, "derive the test's db index from `GIP_REDIS_URL` when set (the gate's own pytest db), else draw from a range no gate or run-small
uses (5–10); one small fix slice with its own code gate". SL-1921 / LG-1922, branch `fix/fd-8233-tenant-binding-redis-db`: the fixture uses
`GIP_REDIS_URL`'s own db when set, else `5 + secrets.randbelow(6)` (5–10), disjoint from {1,2,3,4,11,12,13}. Its slice audit is RS-1923 (working id).

## Disposition

Open, owner WK-1178; **fix before close**: SL-1921 (LG-1922). Closed in place citing the PR when that slice merges. Filed under working id 8233.
