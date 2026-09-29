---
id: FD-1245
family: finding
title: WF-699 step E2 submits through POST /approval-requests, where FR-257's gate runs at /rating-versions/{id}/submit
status: active
created: 2026-09-29
owner: auditor
tree: 1c8762d9ed235f80e0f2fff80c44003694828e97
corrected_by: []
relates: [WK-672, WF-699]
---

# FD-1245 — WF-699 step E2 submits through POST /approval-requests, where FR-257's gate runs at /rating-versions/{id}/submit

## Finding

**Severity: low.** The auditor found it on 2026-09-29 by the `close-workstream` §5c reading at
the WK-672 Work close (`00` FR-1188). It is a disagreement between a journey step and the
requirement it cites. The code and its tests agree with the requirement. This record does not
decide which side moves: that is `CLAUDE.md` §0's question.

`WF-699` step E2 has the Pricing Actuary submit a Rating Version with
`POST /approval-requests` and says that evidence completeness is checked there. FR-257 and
FR-260's dated amendments put the check at `POST /api/v1/rating-versions/{id}/submit`, and the
generic approval route refuses a Rating Version that is still `draft`.

## Evidence

At `origin/main` `1c8762d9ed235f80e0f2fff80c44003694828e97`.

- The step, `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:96`:
  *"| E2 | Pricing Actuary | `POST /approval-requests`. Evidence completeness is checked at
  submission: structural diff, rate diffs, regression run, dislocation run, GIPP check where
  enabled, change summary. | `03` FR-257, `06` FR-352/363 |"*
- `03` FR-257 (`docs/specs/03-rating-engine.md:174`), clarified 2026-09-28: *"a submission whose
  suite has none, or whose algorithm has no suite, is refused with `EVIDENCE_INCOMPLETE`. It
  applies forward, at submit."*
- `03` FR-260 (`:177`), amended 2026-09-28: *"(1) The check runs at
  `POST /api/v1/rating-versions/{id}/submit`."* The §5.1 row for that route (`:754`) reads
  *"Submit for approval; evidence completeness checked (FR-257); golden quotes re-scored and the
  suite pinned (FR-260)."*
- The code: `backend/tests/test_rating_versions.py`,
  `test_golden_bypass_a_draft_cannot_be_put_to_approval_directly`, asserts that the generic
  route's resolver (`app.api.approvals._resolve_rating_version`) refuses a draft Rating Version
  with `APPROVAL_SUBJECT_NOT_IN_REVIEW` and leaves it `draft`. The FR-257 limb (1) refusals are
  asserted on `submit` (`test_no_regression_run_refuses_submission` and its siblings).
- The search that found the step is the one named in the WK-672 close record (20 hit lines,
  each read).

## Disposition

**Carry forward, unowned**, proposed by the auditor on 2026-09-29; the register row's
`decision:` is the lead's. The decision-maker decides whether E2 names
`POST /rating-versions/{id}/submit` (the route the requirement and the code use) or whether the
requirement moves (`CLAUDE.md` §0). Event: the decision-maker's ruling. If unowned at the next
`CLAUDE.md` §14 review, the row decays to that review.

**Lead's decision, 2026-09-29:** deferred with an owner — the decision-maker. Event: the decision-maker's ruling, no later than the gate before the P2 exit demo (plan review 16's Proposal 12). This matches the register row.
