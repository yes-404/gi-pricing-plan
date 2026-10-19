---
id: LG-8126
family: ledger
title: WK-1178 slice SL-1770 — S-a, the artifact tables append-only at the database (PL-1769), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-19
owner: executor
tree: fbbadef54adcd247a2d59cc86861c19c376a495c
phase: P2
work: WK-1178
slice: SL-1770
plans: [PL-1769]
corrected_by: []
relates: [PL-1769, SL-1770, FD-1704, FD-1728]
---

# LG-8126 — WK-1178 slice SL-1770: S-a, the artifact tables append-only at the database

*(Working id 8126, reserved by the lead; not yet minted.)*

**GO:** to-lead.md "2026-10-18 22:50:32 BST — Maintainer: the duplicate-mint anomaly ruled; GO SL-1259, SL-1770, SL-1738, SL-1575 (with conditions)".
**MERGE-ACK:** not yet given.

## Tasks

Base: `origin/main` `84b0ff5765e55bc8edd139cd22bb57cd474de807`. Branch `sl-1770-wk1178-append-only-db`, worktree `.claude/worktrees/sl-1770`.

### Scope

`PL-1769` S-a (Tasks 1–6): the artifact tables append-only or guarded at the database, from the classification table of `PL-1769` ("Table classification (plan review R3)") plus its dated row 60.

### Task list

(entries follow; the order is the plan's)

### Gate

(to be filled at the slice PR's head)

### Audit

(written by the auditor)

### Build log

- **2026-10-19 — `blob_uploads` classed `mutable`, condition verified.** The maintainer (by delegation) confirmed `mutable` in to-lead.md "2026-10-18 23:27:47 BST" on one condition: no artifact row derives its identity from `blob_uploads` after promotion. Verified at `fbbadef5`:
  - `BlobUploadRow` (`backend/src/app/db/models.py:3030`, `__tablename__` `:3047`) is referenced by no foreign key: `grep -rn "blob_uploads" backend/src packages --include=*.py` finds the table name only at `models.py:3047` and in `backend/tests/test_api_blob_uploads.py`; the one migration naming it is `e7c3a9b15d82_blob_uploads.py`, which creates it. The only foreign key on the table points outward: `sha256 … ForeignKey("blobs.sha256")` (`models.py:3061`), beside `job_id` (`:3060`, no foreign key).
  - The promotion consumer reads the row once and returns the blob digest: `_promote` (`backend/src/app/worker/data_handlers.py:168-184`) takes `upload_id`, calls `promote_upload` (`backend/src/app/platform/blobs.py:337`) and returns `JobResult(kind="blob", ref=digest)`; `upload_id` is not stored anywhere after that.
  - `DatasetVersionRow` (`models.py:971`) carries no upload field: its blob references are inside `tables` (`models.py:985`, JSONB), written by `blob_store.put` in `backend/src/app/data/ingestion.py:308`, i.e. by sha256 / `BlobRow` (`models.py:347`).
  - `upload_id` elsewhere is the S3 multipart id of the presign response (`backend/src/app/platform/blobs.py:102`, `packages/model-schema/src/model_schema/uploads.py:39`), an API field, not an artifact.
  - Nothing keys on `upload_id` after promotion, so the condition holds and the table is not `guarded`. The `reason` in `models.py` and `PL-1769` row 60 (dated addition below the table) carry this text.
- **2026-10-19 — single alembic head at the branch head `fbbadef5`**, derived from `backend/migrations/versions/*.py` (revisions that no file names as a `down_revision`): `a4d1f08c3b97`, whose `down_revision` is `f2b6d90a4c17`, the head at base.

## PRs

(none yet)
