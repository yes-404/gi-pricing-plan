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

PHASE B — the `GIP_DEPLOY_TESTS=1` runs (2026-10-18 12:19–12:40 BST; written by `executor-8111b`
under the lead's grant in `brief-executor-8111b-2026-10-18.md`). Every run: isolated project
`gip-s4-runtime` (own postgres/redis/minio on ephemeral ports, `lb` on 18000); gate-1 and
gate-1b free at each start; load1 at start 2.78–5.66 except NFR-531 (2.66, `small-test` free).

- **Red A, first run (a test defect, not the planned red).** Test at `51ad8a3a`, image
  `e2a2f79e0bba9f05b29ee585b52a9248899e4cf3`, `-k dataset_ingest`: rc 1, `socket.gaierror: [Errno -2]
  Name or service not known` at the PUT — the presigned URL names the compose-internal
  `minio:9000`, which the test process cannot resolve. Not `KeyError: 'id'`: the old image does
  return `urls`, so the failure came earlier than step 2's `upload['id']`.
- **Fix, test only** (`576c0294725366d36e16eca64f213f315e552b65`): connect to the published
  MinIO port (`_mapped('minio', 9000)`) and send the signed `Host: minio:9000` header unchanged.
- **Red A** (test with the fix, image `e2a2f79e`): rc 1, `E       KeyError: 'id'`, 55.86s.
- **Red B** (image and tree `51ad8a3a` + the same fix, `worker-io` left out of `_worker_services`
  by a scratch plugin not committed): rc 1, `AssertionError: job 01a14ec1-98a4-766f-b635-439dc909a9b7
  (blob.promote, queue io) is 'queued' after 90s: never consumed`.
- **Green, E4.8** (tree `576c0294`, every worker up): rc 0, `1 passed in 63.43s`;
  `job 01a14ec4-1cf7-7b6f-833d-56344c1bc29e kind=blob.promote queue=io -> succeeded in 1.0s (bound 90s)`;
  `job 01a14ec4-2159-77ac-bbd9-db2026c58a12 kind=dataset.ingest queue=io -> succeeded in 2.1s (bound 90s)`.
  The `ast` check of PL 8061 Acceptance 2 at `576c0294`: `[]`, rc 0; `git grep` shows both routes
  at `:663` and `:676`.
- **Red, FD 8112** (tree `576c0294`, untrapped `roll-api.sh`). First run: rc 1, `docker compose …
  up -d --wait --scale api=2 lb` returned non-zero in the test's setup, not reproduced by the same
  command by hand or on the re-run (cause unknown, recorded). Re-run: rc 1, `FAIL: 30a7a4712d2c not
  healthy within 30s`, then `AssertionError: a failed roll must leave exactly the pre-roll api
  containers ['54ade431c576', '9875870a0677'], found ['30a7a4712d2c', '54ade431c576', '8d65b5425209',
  '9875870a0677']` — the planned cause, four containers remain.
- **The trap + README sentence** (`f950840a3bfb8e956fa86d45d43456fef8d617f6`): `cleanup_new` on `EXIT`,
  armed before the scale-out, cleared before the first old stop.
- **Green, FD 8112** (tree `f950840a`): rc 0, `1 passed in 85.78s`; output
  `FAIL: 03ee49e152b3 not healthy within 30s`, `cleanup: removed new 03ee49e152b3`,
  `cleanup: removed new 07ec2a8ee4d1`, `cleanup: api containers now: 174ea5906811 5e748816f69c`.
- **NFR-531** (`-k previous_version_serves`, tree `f950840a`, load1 2.66 at start, `small-test` free):
  rc 0, `healthy api replicas across the roll: min=2 over 155 samples; failed requests=0`.
- **Script:** `bash -n deploy/roll-api.sh` rc 0; `shellcheck`: absent (`command not found`, rc 127).
  `ruff check .` rc 0; `mypy` rc 0; `ruff format --check backend/tests/test_deploy_stack_runtime.py`
  rc 1, and the file at `eea416ca` (before this slice) is also not format-clean (18 hunks at the
  head), so it is not reformatted here.
- **After:** no container of this project remains; keycloak bind
  `/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/tools-main/deploy/keycloak-local`; the four
  `gi-pricing-app:<sha>` tags built here were removed; `/` at 79% after, 74% before.

**Owed:** Acceptance 7, the SOLO compose-changer gate (the lead's).

## PRs

None yet (PHASE A is pushed to the branch only; the PR is the lead's after PHASE B and the gate).
