<!--
TEMPLATE — Ruling (`RL-`).
Copy this file to `docs/rulings/RL-<nnnnn>-<slug>.md`, where `<nnnnn>` is the padded
result of `python3 scripts/doc-id.py next`. Fill in every placeholder, delete this
comment block, and remove any field this ruling does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `kind:` and `plans:` do not apply to
this family and must not appear here.

The "## Acceptance" heading below is load-bearing: copy its text exactly, including
"the violation that must become detectable" — `scripts/ruling-acceptance-item-census.py`
matches on that phrase (any heading depth, case-sensitive) to recognise a ruling as
carrying a genuine acceptance item. Ruling-form flag-day, 2026-09-02 (maintainer ruling,
`#623`'s merge, `aab6327`): every ruling filed after the flag-day uses this form. If the
question this ruling answers has no testable check to attach — a scope decision, a
disclosure for someone else to weigh — say so in the section rather than deleting it or
forcing a check that cannot fail; do not leave it blank.
-->

---
id: RL-NNNNN
family: ruling
title: <one line — the question this rules on>
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: YYYY-MM-DD
owner: decision-maker           # the maintainer may also author one on scope or process
tree: <commit-sha this was written against>
phase: P<n>
work: WK-NNNNN
slice: SL-NNNNN                 # only where this ruling is slice-scoped
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
---

# RL-NNNNN — <Title>

## Question

<The decision point or conflict as it was put, quoting the options if it came from a
plan's `Decision points` table.>

## Ruling

<The decision, stated so "planner and executor apply it at every site" (§1.6) without
re-deriving it — what changes, and where.>

## Rationale

<Why this option over the others that were on the table.>

## Acceptance — the violation that must become detectable

<One sentence naming the violation this ruling makes checkable: "The violation: ...".
Then one item per check, each stating the specific broken input it must red on —
`*Violation: <the condition>*` — not a description of what the check does. A check
that has never printed a failure has not been tested (`CLAUDE.md` §13); show it red on
deliberately broken input before this ruling is filed, where a check is possible.

If this ruling answers a scope question, a disclosure, or anything else with no
testable check to attach, say that plainly here instead — do not delete this section
and do not force a check that cannot fail.>
