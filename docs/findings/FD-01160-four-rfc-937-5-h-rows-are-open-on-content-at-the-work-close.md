---
id: FD-1160
family: finding
title: Four RFC-937 §5 H rows are still open on content at the Work close, and eighteen are closed only by the migration commit
status: active
created: 2026-09-27
owner: auditor
tree: 47065da50c34f0bf613f7dd972675c96d12f78ed
corrected_by: []
relates: [PL-939, PL-1144, CR-1065]
---

# FD-1160 — Four RFC-937 §5 H rows are still open on content at the Work close, and eighteen are closed only by the migration commit

Filed by the auditor at 2026-09-27 15:04:42 BST, under the lead's adoption of 2026-09-27 14:58:11 BST
(C13: the (i) walk's content-open rows → a finding). It is filed in one commit with FD-1154
to FD-1162, before the W37 closure record cites any of them.

## Finding

RFC-937 §7 (i) reads *"every H row in §5 closed by a named commit"*. `CR-1065` §2.4 sampled 56
rows and left *"the fuller walk"* to W37-11. W37-11 walked every H-bearing row: **59**. All 59
were last touched at or after the migration merge `71f5a22`. But a last-touching commit shows
that a file changed, not that the named hand edit is in it. Read to their content, four rows
are open:

1. **§5.7, `:416` and `:418`.** The RFC deletes the notes-tombstone test and the
   notes-move-citations test, and replaces them with `test_audit_docs_redirects.py`. At
   `47065da5`, `tests/test_notes_move_citations.py` **still exists**, and
   `tests/test_audit_docs_redirects.py` **does not exist**. `check_redirects` is exercised
   instead inside `tests/test_audit_docs_ids.py`. The tombstone test was deleted earlier, in
   W37-4 (`39ee30c0`).
2. **§5.2, `:330`.** The RFC turns `PL-853` into a research record of `kind: audit`, and turns
   its two unowned follow-ups into `FD-` rows. At `47065da5` the file is still
   `docs/plans/PL-00853-…`, with `family: plan` and `kind: leaf`.
3. **§5.4, `:364`, `writing-plans`.** The named edit is only partly present. `doc-id.py next`,
   the `PL-<nnnnn>-<slug>.md` form and `kind:` are there. There is **no** text for
   `_templates/PL.md`, the `Decision points` table, `phase:`, `work:` or `slice:`, freezing, or
   `SL-`.
4. **§5.4, `:377`, `testing-strategy`.** It was last touched by `e0b880e3`, before W37. The
   file is vendored, and it holds no `req(` marker, so the named marker edit has nothing to
   rewrite. Under `CLAUDE.md` §12's vendoring rule this is a no-op. It is recorded as open
   because no record says so.

**Eighteen rows are closed only by `71f5a220`**, the migration commit itself. It passes the
ancestry test because it *is* the migration merge. A scripted run's last touch is weak
evidence for a hand edit, and those rows' content was not checked.

## Evidence

A read-only walk of RFC-937 §5.1–§5.8 at `47065da5` (file lines 296–428). The predicate is the
last table cell (`Kind`) matching `/(^|[^A-Za-z])H([^A-Za-z]|$)/`. It found 16 `H`, 29
`H + M`, 10 `M + H`, and one each of `H / M`, `H (optional)`, `M + H (the two rows)` and
`M + H (§2 text, markers)`: **59**. §5.6 has no H row. Each path was tested with
`git log -1 --format='%h %aI %s' 47065da5 -- <path>` and
`git merge-base --is-ancestor 71f5a22 <commit>`. The auditor re-checked rows 1 and 2 directly
at `3749db65`:

- `ls tests/test_audit_docs_redirects.py` → *No such file*;
- `ls tests/test_notes_move_citations.py` → present;
- `PL-853`'s header reads `family: plan`, `kind: leaf`.

Of `CR-1065` §2.4's seven reassigned gaps, five were closed by their assigned slice. Two are
partial: `writing-plans` (above) and `subagent-driven-development`, whose `task-brief` was not
checked.

## Disposition

**Deferred with an owner — the lead** (the lead's adoption, 2026-09-27 14:58:11 BST). Event:
the create-read-retire audit's first slice. The eighteen migration-only rows are included in
that event's walk, to be read to their content.
