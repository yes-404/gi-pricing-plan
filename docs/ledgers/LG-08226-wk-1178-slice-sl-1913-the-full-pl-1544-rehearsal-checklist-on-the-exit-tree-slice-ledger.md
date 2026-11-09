---
id: LG-8226
family: ledger
title: WK-1178 slice SL-1913 — the full PL-1544 rehearsal checklist (rows 0–9 and PL-1912's row 6b) on the exit tree (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-09
owner: executor
tree: 26d782d42c996a90df04d144a27bb71e9804b218   # the tree of origin/main 40ba57f4b32087ec783383396ffada82601947c5, the activation base
slice: SL-1913
phase: P2
work: WK-1178
plans: [PL-1912]
corrected_by: []
relates: [PL-1912, PL-1544, SL-1913, LG-1841]
---

# LG-8226 — WK-1178 slice SL-1913: the full PL-1544 rehearsal checklist on the exit tree

*Disclosure: working id LG 8226, reserved by the lead; it stays unminted until the slice's close (the maintainer's ruling, to-lead "2026-10-25 21:07:44 GMT", (i): a slice's ledger is created in the slice's own PR at its activation, so LG 8226 stays an unminted working id; PL-1912 says the same). Born at activation with no results; Phase B fills it.*

**GO** (the maintainer's, to-lead "2026-11-09 19:35:31 GMT", quoted verbatim; the dispatch under CLAUDE.md §13 Lean P2 L1, ruling to-lead "2026-11-09 09:52:39 GMT", Phase A = (b)):

> 2026-11-09 19:35:31 GMT — Maintainer: GO — SL-1913 (the P2 exit-demo rehearsal, WK-1178) is DISPATCHED. Authority: CLAUDE.md §13 Lean P2 L1 (the maintainer's GO quoted verbatim in the slice's LG; no activation PR); the user's dates of record "move them: move the work forward" (to-lead 2026-11-09 14:58:57 GMT): rehearsal TUE 10 NOV 2026 on this box. Brief: handover/brief-exec-sl1913-2026-11-16.md sha256 4ce6e3bde274 (with today's dated amendments: the B3 tie rule, the docker-build form, never --rows on rows 5 and 6b, rows 6/6b headless via scratch/exec-rehprep2/ Playwright with the SL-1711 fallback, the six prep amendments, row 8 citing the S3 addendum); object: the frozen tree 374a22bf in worktree reh-t10, our stack (gi-pricing-*), the tools-main image cda1c385ad66, the digest-cached freMTPL2 seed; redis db 3 only, -n named, db 0 = 56 read before and after; one timed stage at a time, nothing else runs on this box during a timed row (the STOP is a branch); faults: a full-seed B3 tie = FD-2106's instance, CONTINUE; any other difference = RED, to me; the browser rows: headless first, fallback recorded. Start: TONIGHT Mon 9 Nov from 20:00 London, after the quiet bar (the evening before the Tue 10 date of record, within the user order to move the work forward; the record carries the actual times; no row needs daylight). Outputs: LG 8226 born on branch docs/sl1913-activation-2026-11-09 (eb254bca42e3) quoting this GO verbatim, the row's draft→active→closed lines, every row's result with its log path, the demo readings, the guards and zeros, the branch head; the lead's FINAL to me; ONE PR for the slice (row change + LG + results) on my grant. Prerequisite met: merge 107 (batch 32, the S3 addendum) on main at 2a66ce6388f4.

This file and the roadmap row's `draft → active` line are Phase A's work, kept unmerged on branch docs/sl1913-activation-2026-11-09 as the first commit of the rehearsal's own branch; no activation PR. **MERGE-ACK:** (added at merge.)

## Tasks

### Scope

`SL-1913` in `docs/roadmap.md` (heading "SL-1913 — WK-1178 rehearsal slice — the full PL-1544 rehearsal checklist (rows 0–9 and PL-1912's row 6b) on the exit tree"), under `PL-1912`: one full run of `PL-1544` §"Rehearsal checklist", rows 0 to 9 as written there (row 6, the browser path `SL-1711` waived, included), plus row 6b, the WF-701 browser check that PL-1912 adds; order 0–6, 6b, 7–9. This ledger records each row's command, output and tree; WF-701's timing lines are an observation with no budget (PL-1912 E1 item 3). No code, spec or plan file changes. The rehearsal date is Mon 16 Nov 2026 by the dated lines under the roadmap block.

### Task list

Rows 0–9 and 6b, one line per row (code tree = worktree reh-t10, detached at 374a22bf33ad3c62a4d2c8b69ba83bd334d4b167; logs under ~/gi-pricing-plan.local/scratch/exec-sl1913/; times from `date -u`/`TZ=Europe/London date`, London = GMT on 2026-11-09):

- 2026-11-09 20:00 GMT, row 0 — head=374a22bf33ad3c62a4d2c8b69ba83bd334d4b167: `git status --short` printed nothing; HEAD 374a22bf…, origin/main 2a66ce63…; code tree equal (`git diff --name-only 374a22bf origin/main -- . ':!docs' ':!.claude'` empty, rc=0). The exit tree is 374a22bf (the freeze tree the GO names). Log rows/r0149.log. rc=0.
- 2026-11-09 20:00 GMT, row 1 — head=374a22bf…: no demo.py or vitest process (the `[p]ytest|[v]itest|[f]lock` pgrep matched only the executor's own shell line); gate-1, gate-1b, gate-2 free by `flock -n`. Log rows/r0149.log. rc=0.
- 2026-11-09 20:00 GMT, row 2 — head=374a22bf…: on the copy gipricing_sl1913_r23 (`createdb -T gipricing`), `alembic_version` = b7e4c2a91d36 = `alembic heads` "b7e4c2a91d36 (head)". Template guard at START "alembic_version=1 environments=3 tenant_marker=1", redis `-n 0 dbsize` 56. Log rows/r23.log. rc=0.
- 2026-11-09 20:00 GMT, row 3 — head=374a22bf…: PL-1408 Task 0 script verbatim (sed -n 623,643p of the plan; sha256 prefix 5932de806be2): "databases=2 with_tables=2 without_table_or_error=0" / "TOTAL route_approved=0 self_approved=0 user_approved_no_approved_request=0"; the copy dropped afterwards (0 rows), db0 56. Log rows/r23.log. rc=0.
- 2026-11-09 20:00 GMT, row 4 — head=374a22bf…: both ancestors of HEAD: cdaaa573 "SL-1409: … the FD-1356 fix … (#1157)"; e3a98c97 "fix(approvals): SL-1529 … (FD-1416 …) (#1276)". Log rows/r0149.log. rc=0.
- 2026-11-09 20:00:26–20:24:32 GMT, row 5 — head=374a22bf…: `demo.py --journey wf-699 --no-compose` on copy gipricing_sl1913_r5 (both URLs on the copy; GIP_REDIS_URL redis://localhost:6379/3 read from the demo's environ), full seed, no --rows, quiet window load1 1.21 at start (waited 0 s). Designed stop: both lines seen. "journey done in 1332s", "Seeded to a usable state in 1444s", script 1446 s; dislocation #1 = 539 s (552 / 558 earlier; 555 / 592 / 623 / 697 today). B3 ok (no tie). Non-ok lines only A6 KNOWN GAP FD-1491, B9 KNOWN GAP FD-1490, D9 / E5 / E7 SKIPPED. Teardown: infra diff rc=0, restore from tools-main rc=0, keycloak bind under tools-main, dropdb 0 rows, bucket removed, redis db 3 = 0, db 0 = 56, template guard unchanged. Log r5/demo.log, r5.out, r5/start.log, r5/stop.log. rc=0.
- 2026-11-09 20:25 GMT, row 6 — head=374a22bf…: headless Playwright 1.55.0 chromium (scratch/exec-rehprep2/rows-6-6b.v2.mjs, a copy of the prep's draft): /demo HTTP 200; Keycloak login; /rating-versions/01a1c1e8-5255-789f-997b-554292da9746 (fremtpl2-wf699@3) h1 "fremtpl2-wf699 @3", Status reads "approved", no alert. First draft failed (a full page reload after login dropped the in-memory token and landed on /data); the v2 navigates inside the SPA. Console pageerror "Development identity is enabled; supply x-dev-principal-id." seen on each load. Screenshots row6/, log row6.log. rc=0.
- 2026-11-09 20:26:12–21:07:37 GMT, row 6b — head=374a22bf…: `demo.py --journey wf-701 --no-compose` on copy gipricing_sl1913_r6b, full seed, load1 0.48 at start. CAP STOP at 2400 s (21:06:15, load1 1.38; the cap covered the whole process) — by Q4 not a pass; the maintainer's ruling to-lead "2026-11-09 21:07:10 GMT" let it run on: it FINISHED, "WF-701 part done in 1115s: OVER the pre-registered 10 min target (recorded, not tuned)", "journey done in 2384s", "Seeded to a usable state in 2485s". WF-699 part 1269 s (dislocation #1 488 s); WF-701 part 1115 s, of which ~497 s from K2 compiled (20:49:04) to the dev-deploy precondition (20:57:21, a Job polled ~957 times) and ~524 s from C7(ii) (20:58:51) to C7(iii) (21:07:35, ~995 Job polls, 20 POST /score); A1–C6 ≈ 25 s. K1 / K2 compiled; C1 ok "K1 is prod's newest deployment"; C4 "0.7 s (< 30 s functional bound, not the NFR-494 verdict)"; C7(i) 22 traces of N = 2000 quotes at p = 0.01, band [3, 45]; non-ok lines only A6 FD-1491, B9 FD-1490, D9 / E5 / E7. Browser 6b headless: K1 and K2 pages read "approved" (h1 k1 @1 / k2 @1), /demo chips for both read approved, RESULT PASS; a pushState navigation from K1's page to K2's did not re-render the h1 (K2 reached by the /demo chip) — observation, undiagnosed. Teardown as row 5, all guards equal (db 0 = 56, db 3 = 0, template guard unchanged). Logs r6b/demo.log, r6b.out, row6b.log. Verdict: cap stop, not a pass; the route is the maintainer's. rc=0 (demo finished; script cap rc recorded as capped).

### Gate

Phase A is docs-only (common brief item 30); no PR is opened for it. Recorded at the branch head by the executor in the build log.

### Audit

(Written by the auditor at the slice's close.)

### Build log

- 2026-11-09 (executor, exec-sl1913a): Phase A commit on branch docs/sl1913-activation-2026-11-09 (unmerged, no PR) from origin/main 40ba57f4b32087ec783383396ffada82601947c5: SL-1913 `draft → active` by a dated line under the roadmap block; this ledger created from `docs/_templates/LG.md`.

## PRs

(Added when the rehearsal's one PR opens.)
