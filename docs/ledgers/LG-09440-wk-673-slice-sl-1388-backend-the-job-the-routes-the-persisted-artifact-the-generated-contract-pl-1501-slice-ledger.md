---
id: LG-9440
family: ledger
title: WK-673 slice SL-1388 — backend, the Job, the routes, the persisted artifact, the generated contract (PL-1501), slice ledger
status: active
created: 2026-10-09
owner: executor
tree: 5d6f71c7f3760abfd2b4f5630830e9ec5a9725ae
phase: P2
work: WK-673
slice: SL-1388
plans: [PL-1501]
corrected_by: []
relates: [PL-1501, RL-1504, RL-1445, RL-1263, FR-263, FR-265, FR-266, FR-1397, FR-1398, FR-1399, NFR-495, NFR-499, WK-673]
---

# LG-9440 — WK-673 slice SL-1388: backend, the Job, the routes, the persisted artifact, the generated contract

**GO:** not yet given. Authoring ahead of the GO at the user's order ("2026-10-09 13:17:43 BST — USER: 'plz ask the lead to work in parallel' …" item 1, in `to-lead.md`, a local file): code and tests are written on a branch from S3's head `5d6f71c7`; no test is run until S3's Task 7 ends; nothing merges before the GO and the gate.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `PL-1501` (minted `d85cf854`, #1244), slice `SL-1388`, WK-673 Slice 4: *"backend — the Job, the routes, the persisted artifact, the generated contract"*. Its scope is `PL-1501` §"Scope" (requirement coverage table) and §"Write set, and its contention", read at this branch's tree. Requirement ids covered: FR-263, FR-265, FR-266, FR-1397, FR-1398, FR-1399, NFR-495, `RL-1264` item 3, and the NFR-499 deny as `RL-1504` item 5 rules it. The decision points DP-S4-1, DP-S4-2, DP-S4-3 and DP-S4-5 are ruled by `RL-1504`; DP-S4-4 is the plan's, decided (a).

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1501`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1388`'s roadmap row at its head.

Write set: `PL-1501` §"Write set, and its contention" only. Any other path is a stop to the lead.

### Task list

Order and acceptance checks are `PL-1501` §"Tasks" and §"Acceptance Standard" (items 1 to 16). Each task below is added with its commit when it is pushed.

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no heavy run while S3's Task 7 holds gate-1; the gate runs after the lead's "gate slot granted" for the head) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-09, authoring phase.** Worktree `.claude/worktrees/sl-1388`, branch `sl-1388-wk673-s4-backend-job-routes`, from `5d6f71c7f3760abfd2b4f5630830e9ec5a9725ae` (#1243's head). Stamps are BST (`TZ=Europe/London date`).

- Commit 1: `PL-1501`'s `status:` line `draft` to `active` (the Q1 ruling, `L1 (a')`), and this file.
- **Red-first proof is OWED.** Every test is written before its code, as `PL-1501` §"Tasks" orders, but no test is run while S3's Task 7 holds gate-1. Each task entry below names the tests whose red (by cause, not status) has not yet been shown; the proof is made at the first test window after Task 7 by running the tests against the tree with the task's code absent (or the broken input of the plan's Step 4) and quoting the cause here.
- **Task 1 (PL-1501 Task 1), 2026-10-09.** `ATTRIBUTION_RECONCILIATION_FAILED` appended as the tail of `RATING_ERROR_CODES` (`backend/src/app/errors.py`; S4 appends first, the Q3 order); `03` §5.1's two dislocation rows replaced by RL-1504 T1's four rows and `03` §5.2's `select_movers` note by T2, dated 2026-10-09 and citing RL-1504, each find string counted once before the edit (`grep -cF`). Test `test_the_reconciliation_failure_code_is_registered` (FR-1397) written. Spec note: `03` already names the code in the owned-codes list (Slice 3's P1), so Task 1 adds no list entry. **Red-first proof OWED**: the test is expected to fail on the assert with the name absent from the set, to be shown by running it against `errors.py` at `5d6f71c7`. `ruff check` and `ruff format --check` clean on the two Python files; no pytest or audit-docs run (S3 Task 7 holds gate-1).
- **Task 2 (PL-1501 Task 2), 2026-10-09.** `DislocationRunRow` appended to `backend/src/app/db/models.py`; migration `b8d2f4a6c0e1_dislocation_runs.py` (`down_revision` `f3a7c1d9e2b4`, the single head at this tree by a parse of `revision`/`down_revision` over `backend/migrations/versions/`; the unique constraint is named `uq_dislocation_runs_job_id` as `NAMING_CONVENTION` would name the model's; `alembic upgrade head` not run, no DB work during Task 7); `backend/src/app/platform/dislocation_runs.py` with `persist_run`, `fetch_run` (raises 404 `NOT_FOUND`, the plan's text, where `regression_runs.fetch_run` returns `None`) and `movers_digest`. `blobs.py` untouched (RL-1504 item 5). Imports are from `model_schema.dislocation`: `model_schema/__init__.py` exports nothing from that module at this tree. Tests written: `test_the_scalar_movers_digest_equals_the_runs_movers_blob`, `test_fetch_is_scoped_to_the_workspace`, `test_a_run_without_a_movers_blob_or_a_job_id_is_not_persisted`, `test_the_generic_blob_route_refuses_a_movers_blob`, and a positive control `test_the_movers_digest_would_download_if_a_job_blob_result_named_it` (Step 4's broken input kept as a permanent test, not a scratch revert). **Red-first proof OWED** for all five: the first fails at import (`DislocationRunRow`/`app.platform.dislocation_runs` absent at `5d6f71c7`); the blob-route test is red by the positive control, not by absence. `largest_movers_blob` is written `blob:sha256:<hex>` (03 §4.6's example), parsed by `movers_digest`. ruff clean; imports smoke-tested only.

## PRs

None yet. The PR is not opened during the authoring phase.
