---
id: FD-2105
family: finding
title: scripts/bench-deploy-path.py compiles an approved rating version, so its governed run 409s by construction, and S2's D5.12 "NO READING (409)" was this defect, not the product
status: active
created: 2026-11-09
owner: auditor
tree: 374a22bf33ad3c62a4d2c8b69ba83bd334d4b167   # the frozen tree the four lines were read at; origin/main 40ba57f4b320 holds the same four files (0 commits under scripts/, backend/, packages/ in 374a22bf..origin/main)
corrected_by: []
relates: [WK-690, LG-2003]
---

# FD-2105 — scripts/bench-deploy-path.py compiles an approved rating version, so its governed run 409s by construction, and S2's D5.12 "NO READING (409)" was this defect, not the product

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

5. **Second limb (a second defect of the same script, added on the lead's word of 2026-11-09; the ruling names four lines and they stay as they are).** `scripts/bench-deploy-path.py:52-59`, `running_api_replicas`, runs `docker compose -f <COMPOSE> --profile app ps --status running --format {{.Service}}` with **no `-p`**, so it counts the `api` containers of the default compose project, not the isolated project the helper brings up (`backend/tests/deploy_stack_helpers.py` passes `-p PROJECT` at `:83`). It is called at `:160` and `:207`, after the compile, so a governed run that reached it would record the wrong replica count. S2's run through the committed script stopped at the 409 at `:144` before this code was reached; this limb has never been exercised and is read from source only.

The S2 traceback agrees: `scratch/nfr-bench-1/s2/Q1-d512-n1.log` (local, not in the repository) ends `bench-deploy-path.py", line 144, in _governed_run … urllib.error.HTTPError: HTTP Error 409: Conflict`.

Predicate for "no change since": `git log --oneline 374a22bf..origin/main -- scripts backend packages | wc -l` = 0 at `40ba57f4b320`, 2026-11-09.

6. **Third limb (added 2026-11-09 by the lead, on the maintainer's "2026-11-09 12:03:43 GMT" ruling, D5.12 v4).** The committed `record()` (`scripts/bench-deploy-path.py:88-130`, read at origin/main `2ecdd7a3`) has **no latency field**: its returned dict carries `offered_rps`, `issued_rps`, `errors`, `load_start`, `load_end`, `workers_per_replica`, `workers_observed`, `void` and `void_reasons`, and no `p50`, `p99` or sample count, and the run's `samples` stay inside the `Rung` and are never printed. Predicate: `grep -n -E "p99|p95|percentile|samples" scripts/bench-deploy-path.py` matches only the dry-run `samples=[]` at `:193` and none in `record()`. A run that completes therefore reads offered rate, issued rate and errors, and not the p99 that NFR-489 is about. The remedy is the v4 line the ruling orders: one printed line per run through `scripts/bench-rating.py`'s `_report_rung` (`:1047`) or `_percentile` (`:500`), with N observed taken from the record's `workers_observed`. The record's `void` field is not the verdict: the verdict line is built from the printed p99 line and the offered rate. Same owner and disposition as the limbs above; severity is unchanged.

7. **Fourth limb (added 2026-11-09 by the lead, on the maintainer's "2026-11-09 10:52:33 GMT" entry, limb (b); the ruling's four lines and the earlier limbs stay as they are).** The load generator is single-threaded, and that bounds the rate it can offer: at the first D5.12 proof the client hung at about 97% CPU with the api idle (0.17%) and 1041 CLOSE-WAIT sockets, so 200 rps is client-bound. The entry's rule: if 25 rps is clean and 200 is client-bound, S3's D5.12 runs at the highest rate the client is proven to offer on nfr-bench-1 (8 vCPU), "with the limitation written as a limb of FD 8419 and as an input to P3-A (the spec-host measurement needs a multi-process generator)". This limb is that input: a single-threaded generator has a client ceiling at 200 rps, and P3-A's spec-host measurement needs a multi-process generator. Owner unchanged (P3-D, tools); the input is P3-A's. [FD 8419 is the working id the entry names; this record is its minted form, FD-2105.]

## Disposition

Open, owner P3-D (tools). Not fixed before the freeze: a change under `scripts/` breaks the empty freeze diff and a measurement aid does not earn its own gate (the maintainer's 09:48:42 entry refuses option (a)). Remedy at P3: put `:142` in the D5.11 order (draft, compile, approve the same version), make `api()` print the status and body of an `HTTPError`, and pass `-p` in `running_api_replicas`. Until then the S3 exit reading runs from a hash-pinned scratch driver; the n=1 proof reads that the 409 is gone and the reading shape is right, not a number of record.

*(Dated line, 2026-11-09, docs batch 32, by the planner (plan-s3fill), on the maintainer's (by delegation) entry "2026-11-09 18:35:07 GMT" (2), (3): this finding gains two limbs, not new findings, both of the hash-pinned scratch driver `bench-d512-governed-v4.py` (sha256 `70de8caead01`), in S3's logs under `scratch/nfr-bench-1/s3/`. (a) The run label is hard-coded: `rate=200 exit` is printed at every `--rate`, so a 100 rps run carries it (`D512-n1-N4-r100.log:119`, `:143`, against `ISSUED … offered 100 rps` at `:144`); the rate is read from ISSUED. (b) The driver brings compose up after the quiet bar, so load_start read 3.1 to 4.4 at the timed n = 1 runs (4.02, 3.32, 4.42, 3.12; `D512-n1-N4.log:74`, `:227`; `D512-n1-N4-r100.log:75`, `:133`) against quiet bars of 0.69 and 0.49. Owner as this row: P3-D.)*
