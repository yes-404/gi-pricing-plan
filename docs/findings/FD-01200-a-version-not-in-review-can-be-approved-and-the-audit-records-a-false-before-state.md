---
id: FD-1200
family: finding
title: A version not in review can be approved, and the audit records a false before-state
status: closed
created: 2026-09-28
owner: auditor
tree: 3a3df367990317c39ae41d3490ef85ae6054128e
corrected_by: []
relates: [WK-1178]
---

# FD-1200 — A version not in review can be approved, and the audit records a false before-state

**Severity: critical.** The deputy raised it from high on 2026-09-28, in his entry in the lead's
local channel file `to-lead.md` stamped 16:59:19 BST, when the second defect below was confirmed.
It is on plan review 15's risk list until the fix merges. The auditor filed
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

## The second defect: any decision approves

Found by executor-s1's red tests and confirmed by the deputy at `ffba6753` (the 16:59:19 BST
entry). `backend/src/app/platform/rating_versions.py` `apply_approval_decision` (from `:252`)
**never reads the request's status**. It sets `row.status = APPROVED` and records
`rating_version.approved` after **every** decision, so a rejection, a changes-requested, or the
first of two required approvals all approve a Rating Version. The auditor re-read the function
at `ffba6753`: in `:252–300`, `grep -c "request.status"` is 0, and the only fields of `request`
read are `artifact_type` and `artifact_ref`.

The reds, as executor-s1 quoted them against `main`:

- the first of two approvals gives `assert 'approved' == 'review'`;
- a rejection gives `assert 'approved' == 'draft'`;
- a draft approved through the service gives `DID NOT RAISE`.

`test_create_submit_approve_a_rating_version` passed only because of this defect. It is a test
that proved nothing. The defect has been live since the same `4493f804` (#268, 2026-08-27).
Together with the status bypass above, the only thing between a draft pricing change and
"approved" was that nobody had tried.

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

**The same PR fixes the second defect** (the deputy accepted folding it in, 16:59:19 BST), on four
conditions:

1. a table-driven test across all 7 approvable types and every decision outcome, asserting
   FR-355's mapping and a true audit `action`, `before` and `after`, with the reds quoted
   against `main`;
2. `test_create_submit_approve_a_rating_version` is corrected, not deleted: two distinct
   approvers, `review` after the first and `approved` after the second, and the PR states why it
   passed before;
3. the data query also reports every Rating Version whose `approved` status lacks the required
   number of distinct approving decisions, or that follows a reject or changes-requested;
4. the priority is unchanged, and WK-672 Slice 2's FR-260 hook and WK-674 Slice 2's floor wiring
   wait for it.

**Resolved 2026-09-28 by #864**, merged as `e6a9ca71` (17:00:47Z). `git merge-base --is-ancestor
e6a9ca71 origin/main` exits 0. Both defects were re-read at `e6a9ca71`:

- **The status bypass is closed at the route and in the hook.** `platform/approvals.py:84`
  `require_in_review` refuses an approval subject not in its type's reviewable state, with
  `APPROVAL_SUBJECT_NOT_IN_REVIEW` (`errors.py:260`). It is called for every resolver in
  `api/approvals.py` (`:338`, `:356`, `:393`, `:420`) and in the platform modules: `perils.py:465`,
  `datasets.py:824` (reviewable state `validated`), `validation_rules.py:340`, and
  `rating_versions.py:299`, where it runs inside the hook on the row that transaction holds
  locked.
- **Any decision no longer approves.** `rating_versions.apply_approval_decision` now reads the
  request's status (`:288`, `target = _target_status(ApprovalStatus(request.status))`). The
  mapping at `:319` sends APPROVED to `approved`, and CHANGES_REQUESTED, REJECTED and WITHDRAWN to
  `draft`. A first approval of two maps to nothing and moves nothing.
- **The audit `before` is the row's own prior state** (`:313`, `before={"status": before}`), with
  the comment *"never a literal: this line once recorded `review` whatever the version had been"*.
- `06` FR-351 carries the dated clause (`06-governance.md:92`): only a version in its type's
  reviewable state can be put to a decision.
- The tests are in `backend/tests/test_api_approvals.py` and `backend/tests/test_rating_versions.py`
  (+265 and +235 lines in #864).

The deputy recorded #864's audit as *"41/41 cases, and **the hole is closed**"*, with exact
mutation reds (M1 → 6, M2 → 1), in his 17:44:58 BST entry quoted in `FD-9012`. The related
FR-357 withdrawal disagreement stays open as `FD-9012`, and #864 does not decide it.
