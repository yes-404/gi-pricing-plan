---
id: RS-1871
family: research
kind: audit
title: SL-1869 (WK-1178) FD-1850 slice audit — ensure_bucket and the first-start create race
status: draft
created: 2026-10-23   # drafted 2026-10-22 under working id 8197; minted 2026-10-23 as RS-1871
owner: auditor
tree: b3dd2c18ae14b9246c85b8f59c99da7881fc3f89
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1869, LG-1870, FD-1850]
---

# RS-1871 — SL-1869 slice audit (FD-1850, `ensure_bucket`)

*(Minted 2026-10-23 as RS-1871 from working id 8197, in the slice PR (common brief item 34); statements below that call an id working or unminted describe the draft state at audit, not the tree at the mint. Written by `aud-8169` (auditor, sonnet, effort medium), 2026-10-22, from `brief-aud-8169-2026-10-22.md` (lead 26). Slice and ledger are cited by their working ids `SL-1869` and `LG-1870`.)*

## Question

Does `origin/main...fix/fd-8169-ensure-bucket-race` implement the maintainer's entries "2026-10-22 16:22:33 BST" and its correction, and is the evidence in `LG-1870` reachable and honest?

## Method

Range `origin/main...fix/fd-8169-ensure-bucket-race`; `origin/main` `71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5`; branch head `a32ac11762c6f5ae005d0ec72b736225348ef67e`, tree `b3dd2c18ae14b9246c85b8f59c99da7881fc3f89`; merge-base is `71e481fa` (the branch already carries the re-merge `83a72687`). Read with `git -C <root> show/diff` only; nothing was run (no tests, no DB). The five commits `fdc29f08`, `55d8a15e`, `e26b751c`, `6993fbf8` and `83a72687` were each checked with `git merge-base --is-ancestor <sha> origin/fix/fd-8169-ensure-bucket-race` (the first four: rc 0 each).

## Findings

### Verdict proposal: CLEAN with 3 non-blocking record items (R1-R3); the lead rules whether R1 is fixed before merge

No code or test defect. The blocking-class question is whether the gate's full suite is the decisive green (it is the plan; see 4).

### 1. Code (`backend/src/app/platform/blobs.py`, `ensure_bucket`)

| Clause | Evidence at head `a32ac117` | Result |
|---|---|---|
| `BucketAlreadyOwnedByYou` is success, no re-check | branch `pass` with the comment, no second `head_bucket` | met |
| `BucketAlreadyExists` re-runs `head_bucket`; success only if it succeeds | `try: head_bucket … except ClientError as head_exc: raise exc from head_exc` | met; the ORIGINAL create error is raised, chained to the head error |
| Any other code re-raises | `else: raise` | met |
| No broad except | only `except ClientError` (outer and inner) | met |
| Lifecycle step still runs after a race win | the `get/put_bucket_lifecycle_configuration` block sits after the `try/except ClientError`, at the outer `_ensure` level; tests (i)/(ii) assert `client.lifecycle is not None` | met |
| Docstring | "Safe to call on every start and from several services at once"; states OwnedByYou = success, Exists = success only if `head_bucket` then succeeds, else the original error chained; no "Idempotent" word | met |

### 2. Tests (`backend/tests/test_blobs.py`, +84 lines)

Stub `_RacingS3`. (i) OwnedByYou passes (asserts lifecycle set). (ii) Exists then head ok passes and asserts `client.heads == 2` (re-checked, not assumed). (iii) parametrised `403`/`404`: asserts the raised code is `BucketAlreadyExists`, `__cause__` is a `ClientError` whose code is the head code, and no lifecycle was written. A fourth test keeps "any other code re-raises" (AccessDenied). All carry `@pytest.mark.req("FR-421")`. Met.

### 3. Red-first and logs

- Commit order, reachable: test `fdc29f08` → fix `55d8a15e` → amendment `e26b751c` (code + tests together) → `6993fbf8` (chaining + `__cause__` asserts). The final test shape is not committed before its fix; the LG says so and proves red-first by overlaying `origin/main`'s `blobs.py` (disclosed, task 3). Acceptable for an amendment, not a silent amend.
- `red.log` first line `6993fbf873037cb8ffb9a18ad5c757472a056823`; its stat line `blobs.py | 4 ++--… 24 deletions` is the overlay; summary `4 failed, 1 passed, 24 deselected, 2 warnings in 0.43s`, rc=1, FAILED: (i), (ii), (iii)[403], (iii)[404]. Verbatim in LG. (iii) red only through the new `__cause__` assert: disclosed in the LG.
- `green.log` same first line: `5 passed, 24 deselected, 2 warnings in 0.11s`, rc=0. Verbatim in LG.
- `negctl-iii.log` same first line: stat `1 insertion(+), 4 deletions(-)` = the `try/except` replaced by `pass` (lines 166-169 of the final file, consistent with LG's "`blobs.py:166`"); summary `3 failed, 2 passed, 24 deselected, 2 warnings in 0.35s`, rc=1; FAILED are (ii), (iii)[403], (iii)[404]. LG's explanation of why (ii) also fails (the `heads == 2` assert) is right. Restored, never committed (LG: `git status --short` empty; not independently re-observable now).
- Every quoted summary line in LG-1870 exists verbatim in its log.

### 4. GREEN scope (item 29)

LG task 4 names the changed module, the importer command and its result, but lists only the first and last files, then says "pre-gate GREEN: `test_blobs.py` only (lead's ruling); the rest is covered by the full code gate". The closure is **derived but not listed**, and the one further importer level is not derived. Accepted only because the lead ruled it and the gate's full suite is decisive. The merge-ack must quote the gate's "Test Files/passed" line. Also: the green run was at `6993fbf8`, before the re-merge `83a72687`, which brought 9 files / 1036 insertions of main code under `packages/` (`git diff --stat 6993fbf8 83a72687 -- backend packages`); item 21 is therefore met only by the gate/PR CI, not by a pre-gate run.

### 5. Records

| Item | Evidence | Result |
|---|---|---|
| SL-1869 row | in `docs/roadmap.md`, `status: active`, `relates: [FD-1850, LG-1870, SL-1711]` | present |
| LG-1870 | five sections; Gate empty, Audit "not yet" (this record fills it); MERGE-ACK "not yet given"; does not claim FD-1850 closed; says FD-1850 is in the docs batch | met |
| FD-1850 essay | not on this branch (LG says docs batch, FD-1850 at mint) | not a defect |

Non-blocking record items:

- **R1 (should fix before merge, one line):** the SL-1869 row text in `docs/roadmap.md` says "`BucketAlreadyOwnedByYou` and `BucketAlreadyExists` from `create_bucket` are success only after a `head_bucket` proves the bucket is reachable". That is the first shape. The final code and the maintainer's amendment: OwnedByYou is success with NO re-check; only `BucketAlreadyExists` re-checks. The row records the superseded belief (CLAUDE.md §0: spec and code disagree).
- **R2:** LG task 3 says "the commit after `7569d9d3`, named, not a silent amend" but names no sha; the commits are `e26b751c` and `6993fbf8`.
- **R3:** LG task 4 says 42 importer files; the same command at head `a32ac117` (`git grep -lE … -- backend/tests`) counts 43 (main has moved; it is the same predicate at another tree). Cite the tree.

## Owed, not run by this seat

`mypy`/`ruff` on the head, the full code gate, and the post-merge test run; the gate is decisive.
