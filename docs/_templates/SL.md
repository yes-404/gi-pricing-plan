<!--
TEMPLATE — Slice (`SL-`), a row family: one unit of execution, living under its Work in
docs/roadmap.md. Like `WK-`, a slice is not its own file — it is a heading carrying
this fenced header block underneath it (§1.5). Copy the block below under the Work it
belongs to, replace `NNNNN` with the padded result of `python3 scripts/doc-id.py next`,
fill in every placeholder, and delete this comment.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `kind:`, `plans:`, `supersedes:` and
`superseded_by:` do not apply to this family and must not appear here — a slice is
never superseded; a re-cut retires it and the planner cuts a new one.

An `SL-` may not move `draft → active` while any row of its plan's `Decision points`
table is open (§1.7) — **not** an executor-writable condition on this block itself, but
what the lead checks before dispatching it.
**Lean P2, L1 (amended 2026-10-08 by the maintainer (dated line by delegation), on
RFC-9479 P6).** For every slice whose GO is given after the maintainer's entry
"2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items 1, 3 and 5 APPROVED; IN PRACTICE NOW;
the files are amended through RFC 9479 P6 (the maintainer's amendment, by delegation)", this
row is the slice's ONE record. There is no per-slice `PL-`, no `LG-`, no dispatch `RL-` and no
activation PR. The slice is one PR carrying the code, the tests, any spec change it needs and
this record, with the five labelled paragraphs below filled in that PR (labels, not headings, so the roadmap's row parser and anchors are untouched). The status change rides the
same PR; in-flight status lives in `eta.md`. A slice dispatched before that entry keeps its
`LG-` and its leaf plan.
-->

### SL-NNNNN — <Title>

```yaml
id: SL-NNNNN
family: slice
title: <one line>
status: draft                  # draft → active → closed | retired (§1.2a)
created: YYYY-MM-DD
owner: planner                   # cut in the map plan (draft); lead dispatches (active)
tree: <commit-sha this was written against>
phase: P<n>
work: WK-NNNNN
corrected_by: []
relates: []                      # ids only — its Work's plan (L5); a leaf plan only for a slice dispatched before 2026-10-08
```

<One paragraph: what this slice delivers, and its dependency on any sibling slice.>

**Scope.** <The slice's row in its Work's plan, quoted verbatim with the plan's id and the row's
heading (L5: one plan per Work, slices as rows). The requirements it covers, each id listed.>

**Decisions.** <The maintainer's GO and MERGE-ACK headers from `to-lead.md`, each quoted verbatim, with any
condition the GO set. A dispatch record that `delivery-process.md` §8 requires (a same-Work
pair) is written here.>

**Tasks.** <The task list the executor works from, each task with its acceptance check.>

**Gate.** <The full local gate's rc table at the slice PR's head: each command, its exit code, the tree
it ran on, and the failing excerpt if any.>

**Audit and ledger.** <The slice audit (`CLAUDE.md` §13: scope from the spec, four verdicts, NFRs measured,
broken-input proofs), then the ledger: appended per task and per push, never rewritten, each
entry dated and naming its commit.>
