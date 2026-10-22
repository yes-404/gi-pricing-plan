---
id: LG-8173
family: ledger
title: WK-1178 slice SL-8172 — FD-1850, ensure_bucket treats losing the first-start create race as success (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-22
owner: executor
tree: f3462d8fc1336dc4583fe8a7af92fed399993a55
phase: P2
work: WK-1178
slice: SL-8172
plans: []
corrected_by: []
relates: [SL-8172, FD-1850]
---

# LG-8173 — WK-1178 slice SL-8172: FD-1850, ensure_bucket and the first-start create race

Working ids 8172 (SL) and 8173 (LG), unminted. Executed by `exec-8169`, base `origin/main` `f3462d8fc1336dc4583fe8a7af92fed399993a55`, branch `fix/fd-8169-ensure-bucket-race`.

**GO:** the maintainer's entry "2026-10-22 16:22:33 BST": FD-1850 MEDIUM, FIXED BEFORE THE EXIT DEMO, as a quick slice; "ensure_bucket treats BucketAlreadyOwnedByYou (and owned BucketAlreadyExists) as success; red-first with two concurrent ensure_bucket calls on a fresh bucket (or a stub raising the code); correct the 'Idempotent' docstring."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`backend/src/app/platform/blobs.py` `BlobStore.ensure_bucket` (FR-421, the lifecycle rule it also sets). FD-1850 itself is in the docs batch, not on this branch.

### Task list

Maintainer amendments of 2026-10-22 (relayed by lead 26, before the runs): `BucketAlreadyOwnedByYou` is success; `BucketAlreadyExists` means another owner in S3, so it is success only if `head_bucket` then succeeds, else the original error is re-raised; three tests, (iii) proven by a negative control.

1. RED `fdc29f08`: first stub tests (superseded in shape by task 3).
2. FIX `55d8a15e`: first fix (re-checked `head_bucket` for both codes).
3. DELTA (the commit after `7569d9d3`, named, not a silent amend): code matches the amendment exactly (`OwnedByYou` passes with no re-check; `Exists` re-heads and, if that fails, raises the original create error chained to the head error (`raise exc from head_exc`); other codes re-raise); docstring states it; tests are (i) OwnedByYou passes, (ii) Exists then head succeeds passes, (iii) Exists then head 403 / 404 raises `BucketAlreadyExists`, `__cause__` being the head error.
   **Red-first for the final shape:** to be run with the final tests against `blobs.py` from `origin/main` (log `scratch/fix-8169/red.log`). (iii) raises on the old code too, so it is expected to PASS red; it is proven instead by the negative control (`scratch/fix-8169/negctl-iii.log`).

4. **GREEN scope (import closure, item 29).** Changed module: `backend/src/app/platform/blobs.py` (`git diff --name-only origin/main...HEAD -- backend/src`). Direct test importers, command `git -C <wt> grep -lE "(from app\.platform import .*\bblobs\b|from app\.platform\.blobs import|import app\.platform\.blobs)" -- backend/tests`: 42 files (`conftest_db.py`, `deploy_stack_helpers.py` and 40 `test_*.py`, beginning `test_api_blob_uploads.py`, `test_blobs.py`, `test_tenant_binding.py`, ending `test_wf01_journey.py`, `test_worker_rate_tables.py`); the source importers (`api/*`, `worker/*`, `platform/*`) widen it to most of the backend suite. **Pre-gate GREEN: `test_blobs.py` only (lead's ruling); the rest is covered by the full code gate.**
5. **Static, per-file run, pre-existing lines:** `mypy backend/src/app/platform/blobs.py` rc 0; a per-file `mypy` of `test_blobs.py` reports 7 errors at lines 168-418, none in added lines, and `ruff format --check` flags hunks in untouched code; `ruff format --diff` shows nothing in the added lines. The gate's `uv run mypy` decides.

### Gate

(left empty for the lead's gate)

### Audit

RS 8197 CLEAN (aud-8169, 2026-10-22, at `f7075e73`); the lead's verdict: ADOPTED. Findings R1 to R3 are fixed in the 2026-10-22 build-log lines below.

### Build log

- 2026-10-22: RED commit `fdc29f08`, FIX commit `55d8a15e`. Static (ruff check rc 0 on both files; mypy on `blobs.py` rc 0; `ruff format --check` flags pre-existing hunks in both files, none in added lines).
- 2026-10-22 (W2 END 16:57:07 BST), runs on tree `6993fbf873037cb8ffb9a18ad5c757472a056823`, `pytest backend/tests/test_blobs.py -k "owned_by_you or bucket_already_exists or reraises_any_other" -q`, via the small-test flock, load1 2.21-3.35, logs in `~/gi-pricing-plan.local/scratch/fix-8169/`:
  - RED (`red.log`, final tests with `blobs.py` overlaid from `origin/main`, restored afterwards, empty `git status --short`): `4 failed, 1 passed, 24 deselected, 2 warnings in 0.43s`, rc=1. (i), (ii) and both (iii) cases fail; the one pass is the unchanged "any other code re-raises". (iii) fails on the old code only on the new `__cause__` assertion (old code already raised `BucketAlreadyExists`, unchained); that is the truthful reading.
  - GREEN (`green.log`): `5 passed, 24 deselected, 2 warnings in 0.11s`, rc=0.
  - NEGATIVE CONTROL for (iii) (`negctl-iii.log`): mutation at `backend/src/app/platform/blobs.py:166` replaced the re-check `try/except` with `pass` (`BucketAlreadyExists` always succeeds): `3 failed, 2 passed, 24 deselected, 2 warnings in 0.35s`, rc=1; (iii) [403] and [404] red, as is (ii). Restored with `git checkout -- <file>`, `git status --short` empty. The mutation was never committed.
  - Why (ii) also went red under the mutation: (ii) asserts `client.heads == 2` (the bucket was re-checked, not assumed). The mutation removes the re-check, so `heads` stays 1 and the assert fails; that is a call-count assertion, not a behavioural difference in the result.
  - The 2 warnings are the per-worktree test-database teardown notice from `conftest_db.py`; no database was used.
- 2026-10-22: merged `origin/main` `71e481fa` (merge-tree rc 0), `docs/INDEX.md` regenerated, `doc-index.py --check` rc 0. `audit-docs.py` rc 1 with exactly: check 31 `gap in the full allocation between 1840 and 8172` (working ids, expected) and check 32 `LG-08173…md:14: FD-1850 does not resolve in docs/INDEX.md` (FD-1850 is in the docs batch, not on this branch).
- 2026-10-22 18:5x BST (exec-8169g, tree `a32ac117` + this line): re-merge of `origin/main` `71e481fa` is a no-op (it is already an ancestor of the branch; no new merge commit). `uv sync --all-packages --frozen` rc 0, `pnpm install --frozen-lockfile` rc 0 (both niced). Docs checks under gate-2: `doc-index.py --check` rc 0, `register-lint.py` rc 0, `audit-docs.py` rc 1 with 4 FAILED rows, all on this slice's own working ids: check 31 (allocation gap 1840..8172), check 32 FD-1850 does not resolve (two rows, the front matter and the build-log line above), and check 32 padded id in the build-log line above (it writes the ledger file name with its zero-padded id; the line is append-only, so it stands until the mint step re-points it). `generate-contracts --check` not run: the diff touches no contracts. Gate script `scratch/fix8169-gate.sh` prepared by substitution from `fd1838-gate.sh`, not launched. Audit still owed.
- 2026-10-22 (audit fixes R1 to R3, RS 8197): R1, the SL-8172 roadmap row text now states the amended shape (`OwnedByYou` is success with no re-check; `Exists` re-checks with `head_bucket`, else re-raises the original). R2, the commits: `e26b751c` made `OwnedByYou` success directly and `Exists` success only after the `head_bucket` re-check; `6993fbf8` added `raise exc from head_exc` and the `__cause__` assert. R3, the import-closure count in task 4 is 43 files, not 42, at `052aa5e6`, by the same grep verbatim: `git -C <wt> grep -lE "(from app\.platform import .*\bblobs\b|from app\.platform\.blobs import|import app\.platform\.blobs)" -- backend/tests`. The FD-1850 rows of audit-docs check 32 are re-pointed to the batch's real id at the gate turn, after the batch merges.

## PRs

(none yet)
