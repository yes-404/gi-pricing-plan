---
id: FD-1953
family: finding
title: RL-1909's four obliged edits were never applied, so OQ-1901 reads open in both mirrors
status: active
created: 2026-10-26   # drafted 2026-10-26 under working id 8262
owner: auditor
tree: 1e0a8abbc90723ae9c887a901f700b72f6f94cc1
corrected_by: []
relates: [WK-675, CR-1952, RL-1909]
---

# FD-1953 — RL-1909's four obliged edits were never applied, so OQ-1901 reads open in both mirrors

## Finding

**MEDIUM (to-lead "2026-10-26 11:04:42 GMT"); owner WK-675, through the lane-C docs PR of Tue 27 Oct 2026.** A spec-record defect: no price moves. Authority: to-lead "2026-10-26 10:54:44 GMT" (the finding accepted). Filed under working id FD-1953, from CR-1952 §5a (CR-1907 E6).

RL-1909 decides OQ-1901 (`GET /api/v1/rating-versions` stays unpaginated, capped at 500 rating versions per workspace). Its "What it obliges" lists four edits: close OQ-1901, put the cap of 500 into `03` §5.1, strike the mirrors, and recount the gate row. None was applied.

## Evidence

At `origin/main` 1e0a8abbc90723ae9c887a901f700b72f6f94cc1:

- `git grep -c RL-1909 -- docs/specs/03-rating-engine.md` prints nothing and exits 1 (zero lines). RL-1909's own acceptance predicate, `grep -n "RL-1909" docs/specs/03-rating-engine.md`, needs 2.
- OQ-1901 reads **OPEN** at `docs/open-questions.md:165` and in `03` §10 at `docs/specs/03-rating-engine.md:1636`, and is unstruck at `docs/roadmap.md:3801`.
- RL-1909 minted in #1390 (`f7a1ccd9`), after S10 merged (`git merge-base --is-ancestor 85eac5b2 f7a1ccd9` rc 0); that PR touches `open-questions.md` by 2 lines and `03` by none.
- The mirror check cannot see it, because both mirrors agree.

## Severity

MEDIUM, by the register's usage: a decided question reads open and the spec states no cap, a wrong governance record, though no price moves.

## Remedy

Apply RL-1909's four edits in the lane-C docs PR of Tue 27 Oct 2026 (CR-1952 §5e owed row (1)). That PR discharges this finding, and closes it in place citing the PR.

## Disposition

Open, owner WK-675; **fix before close**, by Tue 27 Oct 2026. Filed under working id FD-1953.
