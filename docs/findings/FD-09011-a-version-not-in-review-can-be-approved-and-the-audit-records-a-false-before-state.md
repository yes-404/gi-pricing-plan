---
id: FD-9011
family: finding
title: A version not in review can be approved, and the audit records a false before-state
status: active
created: 2026-09-28
owner: auditor
tree: 3a3df367990317c39ae41d3490ef85ae6054128e
corrected_by: []
relates: [WK-1178]
---

# FD-9011 — A version not in review can be approved, and the audit records a false before-state

**Severity: high.** It is on plan review 15's risk list until the fix merges. The auditor filed
this finding on 2026-09-28 in the register-and-records pass, on the lead's instruction and the
deputy's decision in his entry in the lead's local channel file `to-lead.md` stamped
2026-09-28 16:01:27 BST (line 8645), item 7.

## Finding

A Rating Version that is **not in `review`**, a `draft` for example, can be approved through the
generic `POST /api/v1/approval-requests` route without ever passing `…/submit`. Every gate that
submit enforces can therefore be skipped: FR-260's golden quotes and FR-364's evidence floor. The
approval's Audit Event also records `before: review` whatever the real prior state was, so the
audit trail misstates what happened. **It is a governance hole and an audit-integrity defect, and
it is live on `main`.**

## Evidence

At `3a3df367`, each citation re-read by the auditor:

- `backend/src/app/api/approvals.py:394` `_resolve_rating_version` looks the row up by workspace,
  slug and version, and ends at `:415` with `return row is not None`. It checks existence only,
  not status.
- `backend/src/app/platform/rating_versions.py:252` `apply_approval_decision` sets
  `row.status = RatingVersionStatus.APPROVED.value` at `:283` with no check of the current
  status. At `:293` it records `before={"status": RatingVersionStatus.REVIEW.value}`, a literal,
  not the row's prior state.
- **Observed end to end by auditor-a** in the WK-672 Slice 2 plan audit (its finding F1, recorded
  in auditor-a's local job directory, not in the repository). #861's
  `test_the_author_cannot_approve…[rating_version]` submits a draft Rating Version through the
  generic route and gets 201, and under auditor-a's M1 mutation the decision on it came back
  approved. That record also names `approvals.submit` (`platform/approvals.py:146–220`), which
  checks no artifact status, and `VALID_RATING_VERSION_TRANSITIONS` (`rating.py:46–58`), which
  lets `draft` go straight to `approved`.
- **The live window.** `git log -S'_resolve_rating_version' -- backend/src/app/api/approvals.py`
  and `git log -S'before={"status": RatingVersionStatus.REVIEW.value}' --
  backend/src/app/platform/rating_versions.py` both return the same first commit: `4493f804`
  (#268, 2026-08-27, "the demo comparison/approval and the Phase 1b rating version"). The hole has
  been open since then. There is no production deployment yet, so the blast radius is test and
  seed data. The fix PR answers that by a query against the Audit Events rather than assuming it.

## Disposition

**Fix in progress — owner the lead.** Event: executor-s1's WK-1178 PR after #861 (the number
follows). It outranks every other WK-1178 item (the deputy's decision (a)). The one PR, spec and
code in one commit, does the following:

- refuses an approval request for a version not in its type's review state, with a registered
  409 code naming the current state, across **all 7 approvable types**, enumerated by command;
- checks the current status again inside each `apply_approval_decision`;
- writes the audit `before=` from the row. Every hard-coded `before=` in the approval hooks is
  listed and fixed or justified; `metrics.py:537` and `modelling.py:1173` are named for reading;
- adds negative tests, red then green, per type;
- adds a dated `06` rule, or cites the existing one;
- answers the data question: a query for any version that reached `approved` without passing
  through `review`.

WK-672 Slice 2 does not merge its FR-260 hook until this fix is on `main`.
