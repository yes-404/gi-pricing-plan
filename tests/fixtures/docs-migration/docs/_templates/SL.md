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
relates: []                      # ids only — its leaf plan, once written
```

<One paragraph: what this slice delivers, and its dependency on any sibling slice.>
