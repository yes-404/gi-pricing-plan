---
id: RL-992
family: ruling
title: a work's several rows merge into one `WK-` row; every row's prose survives in its body
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-roadmap-transform-rulings.md
---

## RL-992 — a work's several rows merge into one `WK-` row; every row's prose survives in its body

### 1. Verified first, at `f4cbbb7`

**56 leading rows over 41 ids**, nine ids with more than one. A work heads a row in up to three
tables: a phase *plan* table, a phase *status* table, and the original-scope table.

**The rows agree on status and differ in prose.** This is the fact the question turns on and it
was not in the brief. `WK-657`'s three rows (207, 218, 331) and `WK-661`'s three (232, 283, 335), Status
cells only:

```
WK-657  207  **Closed 2026-08-14** — see the status table below
WK-657  218  ✔ **closed 2026-08-14**
WK-657  331  **Closed 2026-08-14** — see the status table below

WK-661  232  ✔ **closed 2026-08-22** — see docs/closures/INDEX.md#closure-recordsmd
WK-661  283  **Closed 2026-08-22** — 110 built · 10 declared-and-refused-by-name · 16 unevidenced …
WK-661  335  **Closed 2026-08-22** — 136 in scope at close, of which 110 built. All ~~124~~ MODEL …
```

**Same word, same date, three different amounts of detail.** So the merge does not have to
arbitrate a status conflict — it has to avoid losing prose.

### 2. Ruled

**One `WK-` row per work id, under the milestone of the phase the work was executed in. The
several source rows merge; they do not become several rows and none is chosen over the others.**

§1.2 fixes it: the unit is *"one work item"* and the row lives *"under its milestone"* — singular
on both counts. Three rows for `WK-657` would be three ids for one work, which is the thing
[`RFC-937`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) is titled after.

### 3. What happens to what it does not choose — the lead's condition, answered

**Three obligations, because "merge" without them leaves the executor to invent the hard part.**

1. **`status:` is taken from the Status cells, which must agree.** Verified agreeing for `WK-657` and
   `WK-661`. **Where they disagree, `migrate` refuses and names the work and its rows** — it does not
   pick the first, the last, or the richest. A status conflict across a work's own rows is a
   data defect in the roadmap, and resolving it is a human's.
2. **Every source row's Notes prose is preserved in the merged row's body, each labelled with
   the table it came from.** `WK-661`'s three cells carry three different measurements — a pointer
   to the closure record, a delivery breakdown, and a scope-at-close figure. **Dropping two
   thirds of that is a content loss the standard nowhere authorises**, and the richest cell is
   not a superset of the others.
3. **The tables the rows came from are not silently deleted.** They are prose a reader uses
   today. Whether the restructure keeps them, folds them, or replaces them is the executor's —
   **but the migration diff must show what happened to each**, and a table that vanishes with no
   hunk accounting for it is a violation, not a tidy-up.

### 4. Acceptance — the violation that must become detectable

**The violation: a work's content is reduced by the merge without the diff saying so.**

- **41 ids in, 41 `WK-` rows out, and no `WK-` id appears twice.** *Violation: a work with two
  rows, or a work with none.*
- **For each of the nine multi-row works, the merged body contains a fragment from every source
  row.** *Violation: a merge that keeps one cell and drops the rest.* `WK-661` is the positive
  control: three cells, three distinct figures, all three must be findable after the merge.
- **A fixture in which one work's two rows carry different status words must make `migrate`
  refuse**, naming the work. *Violation: a status conflict resolved by precedence rather than by
  refusal* — the check that proves obligation 1 is real rather than aspirational.

---
