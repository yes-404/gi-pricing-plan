<!--
TEMPLATE — Ruling (`RL-`).
Copy this file to `docs/rulings/RL-<nnnnn>-<slug>.md`, where `<nnnnn>` is the padded
result of `python3 scripts/doc-id.py next`. Fill in every placeholder, delete this
comment block, and remove any field this ruling does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `kind:` and `plans:` do not apply to
this family and must not appear here.
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
