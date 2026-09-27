---
id: FD-1161
family: finding
title: A frozen plan's Roles table assigned a document family (CR, kind work) to a role whose charter does not name it, and nothing checks a Roles table against document-ids.md §1.6
status: active
created: 2026-09-27
owner: auditor
tree: 3749db65eb29fbe95dd46e6b787960fa8386af0b
corrected_by: []
relates: [PL-1144]
---

# FD-1161 — A frozen plan's Roles table assigned a document family (CR, kind work) to a role whose charter does not name it, and nothing checks a Roles table against document-ids.md §1.6

Filed by the auditor at 2026-09-27 15:04:42 BST, under the lead's adoption of 2026-09-27 14:58:11 BST, on
the deputy's ruling of 2026-09-27 14:23:04 BST. This is a `CLAUDE.md` §15 question against
`.claude/roles/planner.md`, and it is deferred. It is filed in one commit with FD-1154 to
FD-1162, before the W37 closure record cites any of them.

## Finding

`PL-1144`'s Roles table gives the executor *"Tasks 1–12"*. That range includes Task 10, whose
file line reads *"create `docs/closures/CR-<n>-<slug>.md`"*: the Work's closure record, of
`kind: work`. `document-ids.md` §1.6's `CR` row gives that family to *"auditor (`work`,
`phase`); lead (`review`)"*. `CLAUDE.md` §12 makes §1.6 the authority on which role writes which
family. The plan was frozen at activation, so the conflict could not be corrected in the plan.

The deputy ruled: *"A frozen plan's Roles table cannot widen a charter"*. The executor gathered
the evidence tables and the auditor writes the record. He recorded the conflict as a face, and
asked whether the planner's charter needs a line, *"check the Roles table against §1.6 before
activation"*, as a §15 question for the charter investigation.

## Evidence

At `3749db65`:

- `docs/plans/PL-01144-…md:363`, the Executor row, reads *"Tasks 1–12, one worktree, one branch per PR"*.
- `:365` (Auditor) names the register writes and the §13 proposal, but not authorship of the
  closure record.
- `docs/process/document-ids.md:159`, the CR row, reads *"auditor (`work`, `phase`); lead
  (`review`)"* in its writer column, and *"maintainer accepts a Work or Phase close"* in the next.
- The deputy's ruling of 2026-09-27 14:23:04 BST (in the lead's local channel file, not in the
  repository): *"the conflict itself is a face for the closure record: 'a frozen plan's Roles
  table assigned a document family (CR, `work`) to a role whose charter does not name it; §1.6
  governed, the plan was not edited (frozen at activation)'"*.

No check compares a plan's Roles table with §1.6. A mismatch surfaces only when a role reads
its own charter against the task.

## Disposition

**Deferred with an owner — the lead** (the deputy, 2026-09-27 14:23:04 BST, *"deferred with
you as owner"*). Event: the charter investigation's first slice (RFC-937 §8), beside
`FD-1151` and `FD-1153`. There is no charter edit in this Work.
