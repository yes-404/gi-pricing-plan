<!--
TEMPLATE — Work (`WK-`), a row family: one work item, living under its milestone in
docs/roadmap.md. Unlike a document family, a WK- is not its own file — it is a heading
in docs/roadmap.md carrying this fenced header block underneath it (§1.5). Copy the
block below under the phase section it belongs to, replace `NNNNN` with the padded
result of `python3 scripts/doc-id.py next`, fill in every placeholder, and delete this
comment.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `kind:`, `slice:`, `plans:`,
`supersedes:` and `superseded_by:` do not apply to this family and must not appear here
— a Work is never superseded, only withdrawn (`retired`).
-->

### WK-NNNNN — <Title>

```yaml
id: WK-NNNNN
family: work
title: <one line>
status: draft                  # draft → active → closed | retired (§1.2a)
created: YYYY-MM-DD
owner: maintainer                # opens (draft); planner writes the map plan; maintainer
                                  # sets active; maintainer accepts the close
tree: <commit-sha this was written against>
phase: P<n>
corrected_by: []
relates: []                      # ids only
```

<One paragraph: what this Work delivers, and which slices it is expected to cut into
(the map plan, once written, is the authority on the actual cut).>
