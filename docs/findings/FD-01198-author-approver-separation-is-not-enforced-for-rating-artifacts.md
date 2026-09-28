---
id: FD-1198
family: finding
title: Author-approver separation is not enforced for rating artifacts
status: closed
created: 2026-09-28
owner: auditor
tree: 81e061fbd6b38f307ae530f090badbd55fe759c4
corrected_by: []
relates: [WK-1178]
---

# FD-1198 — Author-approver separation is not enforced for rating artifacts

The auditor filed this finding on 2026-09-28 in the register-and-records pass, on the lead's
instruction. dm-e found it, the lead confirmed it at `origin/main` `81e061fb`, and the auditor
re-read each citation there.

## Finding

The approval path for rating artifacts refuses an approval **by the submitter** and by no one
else. The **author** of a Rating Version, a Rating Algorithm or a Rate Table Version is recorded
in `created_by`, but that field is never compared with the approver. An author who did not submit
can therefore approve their own work.

**The code matches the spec as written.** `06` FR-353 (`06-governance.md:94`) reads *"the
submitter cannot approve, and where two approvals are required they must be distinct Principals
(R1)"*. It names the submitter, not the author.

**The gap is against the deputy's condition on #856 (the permission catalogue ruling)'s DP-A.** That is his entry in the lead's
local channel file `to-lead.md`, stamped 2026-09-28 15:01:11 BST (line 8476). It says: *"coarse
write rights are acceptable only because the **approval step separates author from approver**.
… **If no such check exists in code, that is a new `FD-` and a WK-674 S2 or WK-1178 fix**"*. DP-A
keeps the coarse `rating:write`, which every actuary holds, so this separation is the only one
left between writing a rating artifact and approving it.

## Evidence

At `81e061fb`:

- `backend/src/app/platform/approvals.py:260` is the only separation check:
  `if row.submitted_by == approver.id:`, which raises `SUBMITTER_CANNOT_APPROVE`.
- `git show 81e061fb:backend/src/app/platform/approvals.py | grep -nE "created_by|authored_by"`
  finds nothing (exit 1).
- `backend/src/app/db/models.py` declares
  `created_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)` on
  `RatingVersionRow` (`:1899`), `RatingAlgorithmRow` (`:1938`) and `RateTableVersionRow`
  (`:2003`).
- **By contrast, Validation Rules enforce it.** `backend/src/app/platform/validation_rules.py:412`
  has `if row.authored_by == actor.id:`, which raises *"A rule cannot be approved by its
  author"*. The database backs it with the constraint quoted at `models.py:1150` on
  `ValidationRuleRow`: `… AND approved_by <> authored_by …`.

## Disposition

**Fix in progress — owner the lead.** Event: executor-s1's WK-1178 PR (the number follows). This
is the deputy's decision by the maintainer's delegation, in his entry in the lead's local
channel file `to-lead.md` stamped 2026-09-28 15:06:51 BST (line 8525). It supersedes the owner
line first written here ("until the deputy picks WK-674 Slice 2 or WK-1178"). The entry decides
option **(a)**: one WK-1178 PR, with spec, code and test in one commit, containing:

- **a dated amendment to FR-353.** The approver of an artifact version may be neither its
  submitter nor its **author**, and the author is defined as the `created_by` of the artifact
  version under approval;
- **the check in `approvals.py`,** applied to every approvable type (enumerated by command),
  with a named, registered error code;
- **a red-then-green test,** in which a creator who did not submit is refused. The existing
  submitter test stays.

It rides WK-1178 ahead of Dependabot and `FD-1195`. It must merge before any WK-674 or WK-673
slice adds an approvable type, and in any case before plan review 15's exit criteria are dated.

**Carried to WK-677, as a separate register row: component authors.** These are the
`created_by` of a rate table version or a model version that a Rating Version pins. The
amendment states that they are **not** covered. WK-677 is FR-353's owner (P3). The row sits
beside `03` FR-1186 (OQ-620's decision, merged by #830), under which Rate Table Versions have no approval lifecycle of
their own. That is the path by which a component author's work reaches approval unchecked.

**Resolved 2026-09-28 by #861**, merged as `3f7bddda`; re-read at `origin/main` `ffba6753`.
- `backend/src/app/platform/approvals.py` refuses the author with `AUTHOR_CANNOT_APPROVE` (`:302`),
  and refuses with `APPROVAL_AUTHOR_UNRESOLVED` (`:293`) when the author cannot be resolved.
- `06` FR-353 (`06-governance.md:94`) carries the dated amendment: neither the submitter nor the
  Author of an artifact version may decide on it.
- The tests are in `backend/tests/test_approvals.py` and `backend/tests/test_api_approvals.py`.

The component-author carry to WK-677 stays open in its own register row.
