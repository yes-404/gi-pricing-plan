---
id: FD-1190
family: finding
title: The W37-6 migration mapped a superseded note to draft and dropped its status line
status: active
created: 2026-09-28
owner: auditor
tree: 37b2596e4318092178c9b0c9fedb83610ee9fd28
corrected_by: []
relates: [FD-1175, RFC-840, RFC-841]
---

# FD-1190 — The W37-6 migration mapped a superseded note to draft and dropped its status line

The auditor filed this finding on 2026-09-28 in the register-and-records pass, on the
maintainer's instruction as relayed in the deputy's entry in the lead's local channel file `to-lead.md` stamped 2026-09-28 12:51:59 BST (part B).

## Finding

`FD-1175` reports a symptom: adopted RFCs still read `status: draft`. This finding reports the
cause for two of them. The W37-6 migration (`71f5a220`, #782) turned each proposal note into an
`RFC-` record with an RFC-937 header. Its mapping sent a note's `landed` status to `closed` and
its `open` status to `draft`. It **also sent `superseded` to `draft`**, and the note's own
status row, which carried the dated reason, did not survive into the record.

## Evidence

- **Before the migration.** At `71f5a220^`, the proposal notes that became RFC-840 and RFC-841
  (their pre-migration locations are the two rows of `docs/REDIRECTS.csv` that map to these ids) had
  this status row at line 6: *"`superseded` 2026-08-29 — by the adopted specification,
  `docs/process/delivery-process.md`, which is authoritative from this date"*. RFC-841's note
  read the same, naming `.claude/roles/*.md` and `docs/process/agent-settings.md` as well.
- **After the migration.** At `71f5a220`, `git show 71f5a220:<path> | grep -m1 '^status:'`
  gives `status: draft` for RFC-840 and RFC-841, and `grep -c "superseded. 2026-08-29"` counts
  **0** in both files. By the same command, RFC-842, RFC-843 and RFC-895, whose notes read
  `landed`, became `closed`. RFC-896, RFC-897 and RFC-898, whose notes read `open`, became
  `draft`.
- **The adoption itself** is recorded in `CR-891:196–198`: *"On acceptance `RFC-840` and
  `RFC-841` received dated `superseded` status and `docs/process/delivery-process.md` became
  authoritative"*.

## Disposition

**Accepted as fixed by PR #855**, on the maintainer's instruction. Owner: the lead. PR #855 sets
RFC-840 and RFC-841 to `status: closed`. `superseded` is not used, because
`delivery-process.md` carries no governed id for `superseded_by:` to name, so `closed` means
"landed" (`document-ids.md:59`), as the deputy set the form. The migration tool has already run,
so no code fix is owed.
