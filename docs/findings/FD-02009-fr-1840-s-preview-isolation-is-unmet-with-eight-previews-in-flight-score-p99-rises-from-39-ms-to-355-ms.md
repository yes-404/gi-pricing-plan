---
id: FD-2009
family: finding
title: FR-1840's preview isolation is unmet: with eight previews in flight /score p99 rises from a median 39.193 ms to 355.461 ms at 25 rps
status: active
created: 2026-11-05   # drafted 2026-11-05 under working id 8352
owner: auditor
tree: 2f108b1eda22a4835279cee9b4c9e305babe3662   # origin/main when read
corrected_by: []
relates: [WK-690, SL-1275, PL-1665, LG-1839, FD-2007]
---

# FD-2009 — FR-1840's preview isolation is unmet: with eight previews in flight /score p99 rises from a median 39.193 ms to 355.461 ms at 25 rps

## Finding

**MEDIUM, owner WK-690, working id 8352.** Ruled MEDIUM by the maintainer, `to-lead.md` "2026-11-05 10:20:03 GMT" (S1 item B accepted as read), after the rule of "2026-11-04 09:51:05 GMT" that an unmet 3c reading becomes an FD owned by WK-690. FR-1840's Isolation clause (`docs/specs/02-modelling.md:270`, sub-item 3c) reads: "Preview work can never queue ahead of `/score`. A test or a measurement shows `/score`'s p99 at a moderate rate is unaffected while previews saturate their executor."

S1 item B, driver B (`bench-b-pl1665-57.py`, sha256 `c68de47cb777b79c6ee3be7265cdd0674ca9aa5b554284ca518ab3b524eb6cd1`), main `dae9637e`, DB `nfrs1_b`, window 2026-11-05 10:15:20 to 10:18:52Z, rc 0, 3 runs each arm. At 25 rps, `/score` p99 (ms, runs 1/2/3):

| arm | p99 per run | median |
|---|---|---|
| ALONE (n = 750 each, errors 0) | 84.691 / 39.193 / 35.188 | 39.193 (range 49.503) |
| 8 previews in flight (about 1115 previews per run, all 200, preview p50 about 240 ms) | 355.461 / 483.061 / 304.985 | 355.461 |

The 3c verdict takes the DP-A2 stop-rule form (the maintainer's "2026-11-04 09:04:20 GMT" Q4): median(saturated) minus median(alone) is 316.268 ms, which exceeds the alone runs' own range of 49.503 ms: **AFFECTED = UNMET**. The stricter reading (the alone baseline) is noisy: one alone run read 84.691 ms, so the alone range is wide, and the delta of 316 ms is still more than six times it. Sub-item 3d reads PASS: the preview's own p95 31.6 ms (n = 100) against its provisional 2000 ms budget. Record: `LG-1839` Item B.

## Evidence

`LG-1839` Item B (nfr-bench-1 addendum, 2026-11-05) holds the tables and the log name `itemB-run.log`. The host is the dedicated VM `nfr-bench-1` (GCE e2-standard-8, 8 vCPU). Not re-run by the auditor.

## Severity

**MEDIUM** (the maintainer, 10:20:03). It misses a requirement's measurement clause on a diagnostic path; the preview route is flag-gated and nothing prices through it.

## Disposition

Open, owner WK-690, in CR 8314 with FD-2007. The remedy is a design question for the section 14 round, not a pre-freeze code item unless the planner sizes a cap at 2 h or less: **options** (1) a preview concurrency cap (a bounded semaphore on the preview route, defaulting below the executor's width); (2) a separate worker pool or process for previews, as FR-1840's intent states ("its own executor, shared with nothing else"; the measured result suggests the executor is not isolated from the event loop or the shared CPU); (3) accept the measured effect as a documented bound and amend the clause. **Recommendation: (1) first, because it is the smallest change and testable by driver B itself, with (2) if the cap alone does not bring the delta under the alone range.** This is a recommendation for the planner and the decision-maker, not a decision. Filed as working id 8352; minted FD-2009 in docs batch 11.

*(Dated line, 2026-11-07, docs batch 15, by the executor, on to-lead "2026-11-07 18:49:24 GMT" (S2 item G): the S2 GBM process ran 4063 s, of which 3875.41 s was post-fit diagnostics after a 154.83 s fit (994 s CPU) on 3.75 M rows; the GBM arm's cost is its diagnostics, not its fit. AMD EPYC 7B12; not like-for-like with S1; 8 vCPU; a lower bound on a non-spec host. Cites LG-2003 @7f078775 and LG-1839 @184d9602.)*

*(Dated line, 2026-11-07, docs batch 15, by the executor, on to-lead "2026-11-07 20:28:26 GMT" (3), the maintainer's ruling by delegation: NAMED CARRY, not a fix before Thu 12. Carried into the P2 closure record by name, owner WK-690, read on AMD EPYC 7B12, 8 vCPU, S2 2026-11-07; §14 proposes the P3 Work that measures on the spec host first and fixes second.)*
