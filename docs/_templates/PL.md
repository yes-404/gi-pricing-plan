<!--
TEMPLATE — Plan (`PL-`), a map plan or a leaf slice plan.
Copy this file to `docs/plans/PL-<nnnnn>-<slug>.md`, where `<nnnnn>` is the padded
result of `python3 scripts/doc-id.py next`. Write it with the `writing-plans` skill,
which covers task breakdown and review checkpoints in full; this template only fixes
the header to the closed field set and carries the `Decision points` table shape §1.7
requires. Fill in every placeholder, delete this comment block, and remove any field
this plan does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6, §1.7. `plans:` does not apply to this
family (it is the ledger's own field) and must not appear here. `slice:` applies only to
a `kind: leaf` plan — a `map` plan cuts multiple slices and does not carry one.

**Freeze is mechanical (§1.7):** `status: active` is permitted only when every blocking
row in the Decision points table below has a resolver id in its `Resolved by` cell, and
every non-blocking row names the step that resolves it. A plan with an open blocking row
stays `draft`.
-->

---
id: PL-NNNNN
family: plan
kind: leaf                     # map | leaf | review | handover — no other value (§1.2)
title: <one line — what this plan delivers>
status: draft                  # draft → active → superseded | retired (§1.2a)
created: YYYY-MM-DD
owner: planner
tree: <commit-sha this was written against>
phase: P<n>
work: WK-NNNNN
slice: SL-NNNNN                 # `kind: leaf` only
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
---

# PL-NNNNN — <Title>

## Goal

<What "done" means for this plan, in one paragraph.>

## Decision points

Kind, blocking status and resolver per RFC-937 §1.7. A blocking row must carry a
resolver id before the slice it blocks may start; a non-blocking row names the step that
resolves it and the default applied until then.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | <question> | <options> | <recommendation> | decision point \| fact \| scope \| design unknown | yes/no | <resolver id, once ruled> |

## Tasks

<Bite-sized steps, per `writing-plans`.>

## Acceptance Standard

<Every item a fresh reviewer can check by running a command or reading a named artifact.
Required on every plan filed on or after 2026-08-31 (check 28).>
