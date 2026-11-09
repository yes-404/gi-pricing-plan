---
id: FD-8419
family: finding
title: scripts/bench-deploy-path.py compiles an approved rating version, so its governed run 409s by construction, and S2's D5.12 "NO READING (409)" was this defect, not the product
status: active
created: 2026-11-09
owner: auditor
tree: 374a22bf33ad3c62a4d2c8b69ba83bd334d4b167   # the frozen tree the four lines were read at; origin/main 40ba57f4b320 holds the same four files (0 commits under scripts/, backend/, packages/ in 374a22bf..origin/main)
corrected_by: []
relates: [WK-690, LG-2003]
---

# FD-8419 — scripts/bench-deploy-path.py compiles an approved rating version, so its governed run 409s by construction, and S2's D5.12 "NO READING (409)" was this defect, not the product

## Finding

The committed measurement driver `scripts/bench-deploy-path.py` seeds an **approved** rating version and then POSTs `/compile` on it. The product refuses that: a compile is allowed only on a `draft`. The driver therefore stops at HTTP 409 on every governed run, before it reaches a reading. The product is not at fault; the driver orders its steps against a rule its own helper documents.

S2's row **"D5.12 NO READING (HTTP 409 at compile, body unprinted)"** (LG-2003, "Verdicts as ruled at S2's end") was this defect, not a reading of the deploy path and not a product failure. The 409 was recorded as "read in S3"; a second run of the same driver in S3 would have stopped at the same line.

**Severity LOW; owner P3-D (tools)**, per the maintainer's "2026-11-09 09:48:42 GMT" entry (`to-lead.md`). LOW because it costs a measurement aid, not a product behaviour; the exit reading it blocks is taken for S3 by a hash-pinned scratch driver under that entry's option (b).

## Evidence

Read at tree `374a22bf33ad` (the code freeze), by file and line:

1. `scripts/bench-deploy-path.py:142` — `ws = governed_workspace(approved=True)`; `:144` — `job = api("POST", f"/api/v1/rating-versions/{ws.rating_version_id}/compile", analyst)`.
2. `backend/src/app/platform/rating_versions.py:180` — `require_compilable`; it raises `RATING_VERSION_IMMUTABLE` (409) unless the status is `draft` (FR-239, RL-1379).
3. `backend/tests/test_deploy_switch_runtime.py:187-191` — the correct order (D5.11): `governed_workspace(approved=False)`, compile the draft, then approve the **same** version, with no second compile.
4. `backend/tests/deploy_stack_helpers.py:286` — `api()` is a bare `urllib.request.urlopen`, so an `HTTPError` reaches the caller with no body printed: the "driver prints the response body" condition of the 19:37:24 entry was never delivered. The same file's docstring at `governed_workspace` (`approved=False` "leaves the draft … `rating.compile` is refused with 409 `RATING_VERSION_IMMUTABLE` for any other status") states the rule.

The S2 traceback agrees: `scratch/nfr-bench-1/s2/Q1-d512-n1.log` (local, not in the repository) ends `bench-deploy-path.py", line 144, in _governed_run … urllib.error.HTTPError: HTTP Error 409: Conflict`.

Predicate for "no change since": `git log --oneline 374a22bf..origin/main -- scripts backend packages | wc -l` = 0 at `40ba57f4b320`, 2026-11-09.

## Disposition

Open, owner P3-D (tools). Not fixed before the freeze: a change under `scripts/` breaks the empty freeze diff and a measurement aid does not earn its own gate (the maintainer's 09:48:42 entry refuses option (a)). Remedy at P3: put `:142` in the D5.11 order (draft, compile, approve the same version), and make `api()` print the status and body of an `HTTPError`. Until then the S3 exit reading runs from a hash-pinned scratch driver; the n=1 proof reads that the 409 is gone and the reading shape is right, not a number of record.
