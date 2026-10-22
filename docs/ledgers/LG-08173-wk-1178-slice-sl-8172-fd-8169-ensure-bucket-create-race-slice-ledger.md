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

1. RED `fdc29f08`: `backend/tests/test_blobs.py` stub-client tests (no MinIO, no DB): both codes are success and the lifecycle rule is still set; `BucketAlreadyExists` for a bucket `head_bucket` cannot reach re-raises; any other create code re-raises.
2. FIX `55d8a15e`: `_CREATE_RACE_CODES`; on those codes `create_bucket` is followed by `head_bucket`, which raises if the bucket is not ours. Docstring: safe on every start and from several services at once.
   **Choice on owned `BucketAlreadyExists`:** the code alone cannot tell "ours" from "another account's" (S3 answers `BucketAlreadyOwnedByYou` only outside us-east-1; MinIO may answer either). So both are success only when the follow-up `head_bucket` succeeds; a foreign bucket still fails there, at start, with a clear cause.

### Gate

(left empty for the lead's gate)

### Audit

(not yet)

### Build log

- 2026-10-22: RED commit `fdc29f08`, FIX commit `55d8a15e`. Static (ruff check rc 0 on both files; mypy on `blobs.py` rc 0; `ruff format --check` flags pre-existing hunks in both files, none in added lines).

## PRs

(none yet)
