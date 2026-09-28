---
id: FD-9009
family: finding
title: Author-approver separation is not enforced for rating artifacts
status: active
created: 2026-09-28
owner: auditor
tree: 81e061fbd6b38f307ae530f090badbd55fe759c4
corrected_by: []
relates: [WK-1178]
---

# FD-9009 — Author-approver separation is not enforced for rating artifacts

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

**The gap is against the deputy's condition on RL-9204's DP-A.** That is his entry in the lead's
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

**Deferred with an owner — the lead**, until the deputy picks the fix's home: WK-674 Slice 2
or WK-1178, as his DP-A condition names them. Event: the deputy's pick. FR-353's own owner is WK-677. Whether FR-353 is amended to name the
author is a spec change first (`CLAUDE.md` §0), and it is the owner's to raise.
