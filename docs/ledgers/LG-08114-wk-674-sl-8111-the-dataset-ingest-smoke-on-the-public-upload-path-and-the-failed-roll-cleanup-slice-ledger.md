---
id: LG-8114
family: ledger
title: WK-674 slice SL-8111 — the dataset-ingest smoke on the public upload path (E4.8) and the failed-roll cleanup (FD 8112) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-18
owner: executor
tree: ~
phase: P2
work: WK-674
slice: SL-8111
plans: [PL-8113]
corrected_by: []
relates: [PL-8113, SL-8111, SL-1258, SL-1722, FR-415, FR-406, FR-1776, NFR-531]
---

# LG-8114 — WK-674 slice SL-8111: E4.8 and the failed-roll cleanup

Working id (lead-reserved). Executed by `executor-8111`, branch `pl-8113-wk674-e48-2026-10-18`.
**Authority:** the maintainer, to-lead "2026-10-18 09:56:08 BST" (build SL 8111 now; its SOLO compose
gate at a free window) and PL 8113's GO at to-lead "2026-10-18 03:19:27 BST". The plan is PL 8113
(`docs/plans/PL-08113-…`); E4.8's text is PL 8061 (now `PL-1791`) §"Slice 4 — changes since
`PL-1714`", E4.8, `docs/plans/PL-01791-…:149-188`.

## Tasks

PHASE A — writing only (2026-10-18).

- **Base (Task 1).** Branch was `7886614a`; merged `origin/main` `eea416cab3c698a12bfc1f3620af0bc7906e4587`
  (`--no-ff`; only `docs/INDEX.md` conflicted, taken theirs, then regenerated in its own commit).
  `git merge-base --is-ancestor eea416ca HEAD` rc 0; `git merge-base --is-ancestor 39da0e1b HEAD`
  (SL-1722) rc 0.
- **Field names (Task 2).** Read at the base from `UploadUrlRequest`,
  `packages/model-schema/src/model_schema/uploads.py:23-29`: `media_type: str`, `parts: int`
  (1..10000, default 1), `extra="forbid"`. Response `UploadUrlResponse` (`:32-41`): `id`, `key`,
  `upload_id`, `urls`, `expires_in_s`. The single-part PUT sends `Content-Type: text/csv`
  (`backend/tests/test_api_blob_uploads.py`, SL-1722's `3a489dbf`).
- **Commit 1 — E4.8 rewrite, red first, not run:** `bd0edf1b8b8b48a90ec6adf72e904c664e8b6ff5`. The ingest test
  now runs upload-url → PUT → complete → POST versions, asserting both Jobs `succeeded` and their
  `result`. `_put_blob_inputs` stays (its caller is the score-batch test).
- **Commit 2 — FD 8112 failed-roll test, red first, not run:** `c708bfba3e7e69320d73097fcae7b67cce728bbf`. Committed
  before any trap; no change to `deploy/` yet.

**PHASE B owed:** Red A, Red B, FD 8112 red, the trap, the greens, NFR-531, shellcheck.

## PRs

None yet (PHASE A is pushed to the branch only; the PR is the lead's after PHASE B and the gate).
