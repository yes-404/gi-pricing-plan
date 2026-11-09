---
id: FD-8421
family: finding
title: WF-701's lifecycle has two Job waits of about 500 s each, K2 compile to the dev precondition and C7(ii) to C7(iii); the 10-minute target is exceeded by the waits, not the work; cause unread
status: active
created: 2026-11-09
owner: auditor                  # DRAFT by the executor for the auditor's sign-off (document-ids §1.6)
tree: 374a22bf33ad
corrected_by: []
relates: [LG-8226, SL-1913]
---

# FD-8421 — WF-701's lifecycle has two Job waits of about 500 s each; cause unread

## Finding

`scripts/demo.py --journey wf-701 --no-compose` on the full seed (no `--rows`) reports "WF-701 part done in 1115s: OVER the pre-registered 10 min target (recorded, not tuned)" (first run) and 1127 s (re-run), against a 600 s target. Nearly all of that time sits in two Job waits of about 500 s each; every other step of the WF-701 part together takes about 25 s. The target is exceeded by the waits, not by the work. The cause is unread: a polling or scheduler interval is the first suspect, and that is a suspicion, not a reading. Raised by the maintainer's ruling to-lead "2026-11-09 21:10:32 GMT", item (c) (MEDIUM, owner P3-C).

## Evidence

Both runs: tree 374a22bf33ad, worktree reh-t10, copies of the template DB, load1 0.48 and 0.92 at start, so not a load reading. Times are the demo log's own request timestamps (`ts`), read as the first JSON line at or before each step line.

| Span | First run (log r6b/demo.log) | Re-run (log r6b2/demo.log) |
|---|---|---|
| K2 compiled → "PRECONDITION dev" line | 20:49:04 → 20:57:21 = 497 s | 21:35:25 → 21:43:52 = 507 s |
| C7(ii) → C7(iii) | 20:58:51 → 21:07:35 = 524 s | 21:45:24 → 21:54:08 = 524 s |
| A1 → C6 (all other WF-701 steps) | 20:57:22 → 20:57:46 = about 25 s | about 25 s |
| WF-701 part, as the demo prints it | 1115 s | 1127 s |

Request census over the first span (first run): `GET /api/v1/jobs/<id>` about 957 times, `POST /api/v1/dislocation-runs/estimate` 4. Over the second span: `GET /api/v1/jobs/<id>` about 995 times, `POST /api/v1/score` 20. Locators: `scripts/exec-sl1913` logs under `~/gi-pricing-plan.local/scratch/exec-sl1913/{r6b,r6b2}/demo.log`; the lines are the ones the table names. Dislocation run #1 of the WF-699 part took 539 s (row 5) and 488 / 487 s in the two row 6b runs, the same order of magnitude as the first wait.

## Disposition

Register decision: deferred with an owner, P3-C. The first reading to take is which Job each wait polls and what interval or queue delay it is waiting out. The Wednesday 11 November exit demo is WF-699 only (the maintainer's ruling above); WF-701 is not part of it, and the harness cap for WF-701 was raised to 3000 s by the same ruling.
