---
id: LG-8173
family: ledger
title: WK-1178 slice SL-8172 — FD 8169, ensure_bucket treats losing the first-start create race as success (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
slice: SL-8172
plans: []
corrected_by: []
relates: [SL-8172, FD-8169]
---

# LG-8173 — WK-1178 slice SL-8172: FD 8169, ensure_bucket and the first-start create race

Working ids 8172 (SL) and 8173 (LG), unminted. Executed by `exec-8169`, base `origin/main` `f3462d8fc1336dc4583fe8a7af92fed399993a55`, branch `fix/fd-8169-ensure-bucket-race`.

**GO:** the maintainer's entry "2026-10-22 16:22:33 BST": FD 8169 MEDIUM, FIXED BEFORE THE EXIT DEMO, as a quick slice; "ensure_bucket treats BucketAlreadyOwnedByYou (and owned BucketAlreadyExists) as success; red-first with two concurrent ensure_bucket calls on a fresh bucket (or a stub raising the code); correct the 'Idempotent' docstring."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`backend/src/app/platform/blobs.py` `BlobStore.ensure_bucket` (FR-421, the lifecycle rule it also sets). FD 8169 itself is in the docs batch, not on this branch.

### Task list

Maintainer amendments of 2026-10-22 (relayed by lead 26, before the runs): `BucketAlreadyOwnedByYou` is success; `BucketAlreadyExists` means another owner in S3, so it is success only if `head_bucket` then succeeds, else the original error is re-raised; three tests, (iii) proven by a negative control.

1. RED `fdc29f08`: first stub tests (superseded in shape by task 3).
2. FIX `55d8a15e`: first fix (re-checked `head_bucket` for both codes).
3. DELTA (the commit after `7569d9d3`, named, not a silent amend): code matches the amendment exactly (`OwnedByYou` passes with no re-check; `Exists` re-heads and raises the original `exc` if that fails; other codes re-raise); docstring states it; tests are (i) OwnedByYou passes, (ii) Exists then head succeeds passes, (iii) Exists then head 403 / 404 raises `BucketAlreadyExists`.
   **Red-first for the final shape:** to be run with the final tests against `blobs.py` from `origin/main` (log `scratch/fix-8169/red.log`). (iii) raises on the old code too, so it is expected to PASS red; it is proven instead by the negative control (`scratch/fix-8169/negctl-iii.log`).

### Gate

(left empty for the lead's gate)

### Audit

(not yet)

### Build log

- 2026-10-22: RED commit `fdc29f08`, FIX commit `55d8a15e`. Static (ruff check rc 0 on both files; mypy on `blobs.py` rc 0; `ruff format --check` flags pre-existing hunks in both files, none in added lines).

## PRs

(none yet)
