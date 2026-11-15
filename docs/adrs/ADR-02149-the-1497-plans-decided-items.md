---
id: ADR-2149
family: decision
title: The decided items of the audit explorer plan, Work #1497
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-2145, ADR-2146, ADR-2147, ADR-2148]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2149 — The decided items of the audit explorer plan, Work #1497

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer, on the issue's own wording: "**Decided on the maintainer's behalf, by delegation of 2026-11-14**" for Q1 to Q7, Q9 to Q12; the maintainer accepted slices 1 to 9 of the plan.
- **Decision issue:** [#1497](https://github.com/yes-404/gi-pricing-plan/issues/1497) (WK-679, audit explorer, chain verification, export)
- **Decision:** [comment of 2026-11-14](https://github.com/yes-404/gi-pricing-plan/issues/1497#issuecomment-6882750335), opening: "**Status, 2026-11-14.** The maintainer accepted slices 1 to 9 of this plan. Slice 10 (the anchor and checkpoint) is held for decision issue Q8 (signing), which is the user's."
- **Enacted by:** [#1858](https://github.com/yes-404/gi-pricing-plan/pull/1858), merge commit `6c005d5db353024e532c7be54329d2af2634afef` (2026-11-15), slices 1 and 4 to 9. Slices 2 and 3 are not in that PR, and slice 10 (the signed anchor) is held. This record does not claim they are enacted.
- **Recorded after the fact.** Written on 2026-11-15, after the decision.

## Context

#1497 builds the audit explorer, chain verification, uniform artifact history and evidence export. Its
plan left twelve questions to the maintainer, each with a recommendation. Q8 (signing) is the user's and
is held; the others were answered on the maintainer's behalf.

## Decision

| Q | Question | Decided |
|---|---|---|
| Q1 | What "versions" means for a route keyed by one `{ref}` | (a): one exact ref, plus navigation between versions |
| Q2 | What a "diff" is | (a): the event's before and after |
| Q3 | Old return names in the explorer | (a2): forward only; the `<type>.returned` filter also matches legacy rows |
| Q4 | The unversioned artifact form and the old refs | the `@1` form; old uuid refs are not looked up |
| Q5 | The CSV | (b): it stays a readable report; JSON Lines is the evidence form |
| Q6 | What a `from`/`to` range selects | (a): the contiguous sequence span |
| Q7 | FR-372's "chain head is checkpointed" | (a): the anchor is the checkpoint |
| Q9 | A UI control for the anchor | none |
| Q10 | Who marks OQ-2015 decided in `06` §10 | #1497's slice 1; the four other Works append their own route rows and never re-mark it |
| Q11 | Where the trace-deletion event is emitted | at the service |
| Q12 | Whether the explorer links every `entity_ref` to history | yes |

Also settled by the same comment: #1497 owns the whole FR-383 mechanism (shape, route, permission,
view, read by exact `entity_ref`); slice 2 (`traces.py`) waits for #1504's slices 1 and 2; the pull
request carries the high-risk label and asks for a cross-review; the hand-written `AuditEventView`
is filed as its own finding, which slice 5 fixes.

## Options not taken

From the plan's question list:

- **Q1:** (b) also accept `{type}:{slug}` and return every version's events (needs a `text_pattern_ops` index, a migration); (c) as (a) plus a `versions` list from a prefix query.
- **Q2:** (b) the artifact content diff from each owning module (06 may not import 01 to 05); (c) (a) plus links to the owning module's diff view.
- **Q3:** (a1) forward only with a documented legacy spelling; (b) rewrite stored names (breaks FR-370 and the chain).
- **Q4:** the bare `type:slug` form; a lookup of old refs (would need governance to read dataset tables).
- **Q5:** (a) a recomputable CSV with the full actor JSON and JSON columns.
- **Q6:** (b) only events whose `at` is in the range (not a chain, so links cannot be checked).
- **Q7:** (b) a new `audit_checkpoints` table written on a schedule; (c) amend FR-372 to drop "checkpointed".
- **Q9, Q10, Q11, Q12:** the plan gives a recommendation; the options other than the one taken are, for Q12, (b) link only the artifact types (needs a hand-written copy of `ARTIFACT_TYPES` unless the contract exports it). For Q9 to Q11 no other option is recorded.

## Consequences

The accepted costs are those the plan names beside each recommendation: for Q1, "versions in one
place" becomes navigation, not one list; for Q4, history starts at the fix for the nine writers whose
`entity_ref` broke the form; for Q5, a spreadsheet of JSON cells was judged to help no reader. Cost for
Q2, Q3, Q6 and Q9 to Q12 is not recorded. Q8 (signing) is not decided by this record.
