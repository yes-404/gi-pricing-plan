---
id: RL-9632
family: ruling
title: Plan-review cadence and routed outputs — option C, and every accepted proposal an owned record (process, on the maintainer's behalf)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-29
owner: maintainer               # a process ruling, authored on the maintainer's behalf (§1.6 RL row)
tree: 5638f69120e0f4d9c958dc1bf4a07f589b42f080
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RFC-9631]
---

# RL-9632 — Plan-review cadence and routed outputs: option C, and every accepted proposal an owned record

## Verified first, at 5638f69120e0f4d9c958dc1bf4a07f589b42f080

**What this record is.** It is a **process** ruling. `docs/process/document-ids.md` §1.6's RL
row (`:162`) says *"decision-maker; the maintainer may author one on scope or process"*. The
maintainer decided this question. The decision-maker records it on the maintainer's behalf, as
item (b) of the entry below orders: *"The decision-maker records the `RL-`: a process ruling
authored on the maintainer's behalf (§1.6 RL row: 'the maintainer may author one on …
process'), citing the RFC."* **This role decides nothing here.** Cadence and review output are
process questions, not technical decision points.

**RL-9632 is a working id.** It is minted at the merge turn, right after `RFC-9631`, with
`doc-id.py next --ref origin/main`. It was checked free on all 103 remote branches before use.

**The authority**, in the maintainer's channel, by full heading:
- `2026-09-29 16:05:14 BST · maintainer (acting on the maintainer's behalf) · PLAN-REVIEW
  CADENCE: option C adopted by the maintainer; RFC + RL + amendments in one PR`. It quotes the
  user: *"go with option C"*.
- `2026-09-29 16:12:57 BST · maintainer (acting on the maintainer's behalf) · PLAN-REVIEW RFC,
  Part 2 folded in: routed outputs (future-facing)`. It quotes the user: *"fold option 2 into
  the option C RFC; the decision is future facing and target to help track proposal, plz go
  ahead"*.
- `2026-09-29 18:43:03 BST · maintainer (acting on the maintainer's behalf) · the plan-review
  cadence OPTIONS A–D and the Part 2 options, recorded for RFC-9631`. It records the options as
  they were presented to the user, before the user chose.

**The proposal it rules on** is `RFC-9631` (working id), *"Plan-review cadence: a replan check
at each Work close, a full review before each exit demo, and every accepted proposal an owned
record"*. It was read on branch `wk1178-plan-review-cadence` at `a8bbbf2f`. Its *Proposal*
section carries Part 1 and Part 2, and they are quoted below exactly as the RFC states them. The
RFC holds the evidence, the options A to D, the Part 2 options, the baseline and the list of
sites. This record does not restate them.

## Ruled

**Adopted as the project's plan-review process, from this record's merge onward. It looks
forward only, and reviews 1–15 are not converted.**

### Part 1 — cadence (option C), as `RFC-9631` states it

1. **A full §14 plan review before each phase's exit demo**, unchanged.
2. **At a Work close:** the auditor's `CR- kind: work` carries a short **replan check**, the
   five `phase-review` questions each answered yes or no with one line.
   - **A full plan review runs only if one fires:** a phase boundary or Work scope moved; an
     exit criterion is at risk; a replan was decided; or a finding moves a slice or phase.
   - The lead gives its verdict on the check. "No trigger" is recorded, not assumed.
3. **Length cap:** a review is proposals-only, about 150 lines. Evidence lives in the cited
   records, not restated.
4. **Kept as they are:** the output is a proposal, never a change; the maintainer gives the
   dated acceptance line; nothing starts in the next phase while a current-phase finding
   lacks a resolution; every accepted proposal gets an owning row.

### Part 2 — routed outputs (future-facing), as `RFC-9631` states it

1. **Each accepted proposal becomes an owned record in the family §1.6 gives its kind**,
   created in its proposed or draft state by that family's owner:

   | Proposal kind | Record | Created by | Landing is tracked by |
   |---|---|---|---|
   | Process, scope, phase boundary or convention (skill, charter, CLAUDE.md, delivery-process) | **RFC** | the planner drafts; the maintainer owns | RFC `closed` when it ships |
   | Replan (re-cut, reorder) | **new PL** that supersedes the old one | the planner, on the lead's replan decision | the PL execution state (§1.7) |
   | Spec or requirement change | **RL + spec amendment** | the decision-maker | the RL sites checked at close |
   | Gap, defect or risk | **FD** with an owner | the auditor; the lead sets `decision:` | the FD `closed` citing the PR |
   | Open design question | **OQ** | the decision-maker | closed by an RL or ADR |
   | Owned Work or slice change | a **WK/SL row** edit | the lead or the planner | its own status |

2. **"Unowned" is not a permitted state for an accepted proposal.** At the acceptance line,
   every accepted proposal has a record id and an owner. Otherwise the lead names one, or the
   proposal is **withdrawn** with a dated reason.
3. **The review's `CR- kind: review` becomes a short index:** the evidence summary; a table
   of proposal → record id → owner → state; and the maintainer acceptance line. It has **no
   free-text proposals left without a record**. The ~150-line cap from Part 1 applies.
4. **Tracking:** the next review's first section lists the previous review's records with
   their current state, derived from the records and never recalled.

**Not ruled here.** The RFC's Part 1 also adds one evidence item that is not in the
maintainer's rule text: the replan check records `python3 scripts/register-owed.py review`'s
owed count at the close's tree. The RFC calls it *"evidence, not a new trigger"*. It stands or
falls with the RFC, and this record neither adds it nor removes it.

## What it obliges

- **This PR** restates Parts 1 and 2 at every site the RFC's *Sites* section lists: the
  `phase-review` and `close-workstream` skills, `docs/process/checklists/work-item-close.md`,
  `document-ids.md` §1.6, and the lead's and planner's charters. The lead's `CLAUDE.md` §14
  amendment, which the user sees as a diff before merge, cites `RFC-9631` and this record.
- **Every Work close from this merge on:** the auditor's `CR- kind: work` carries the replan
  check, and the lead gives its verdict on it.
- **Every plan review from this merge on:** it is filed as an index of owned records, and it
  opens by listing the previous review's records with their current state.
- **Not ordered:** no clean-up of the 48 not-landed and 12 partial proposals of reviews 1–15.
  The RFC records them as the baseline, and a later clean-up is a separate maintainer decision.

## Acceptance — the violation that must become detectable

The violation: **an accepted plan-review proposal with no owned record, or a Work-close `CR-`
with no replan check.** Neither is detected mechanically at this record's tree, and this record
does not claim otherwise:

- *Violation: a Work-close `CR- kind: work` filed without a Replan check section, or with the
  check but no lead verdict on it.* **Detected by review.** The auditor's close checklist
  (`docs/process/checklists/work-item-close.md`, the replan-check item this PR adds) requires
  the section, and the lead reviews the CR before the maintainer accepts the close. **No script
  checks it.** `audit-docs.py` check 37 requires only the sections its family template names,
  and `docs/_templates/CR.md` (headings at `:37-52`) has no Replan check heading.
- *Violation: an accepted proposal with no record id or no owner at the acceptance line.*
  **Detected by review, twice.** First by the maintainer when giving the acceptance line, which
  Part 2 rule 2 makes conditional on every row having an id and an owner. Then by the next
  review's opening section (Part 2 rule 4), which lists each earlier record with its state
  and so shows any row with no id. **No script checks it.** The index table's columns are not
  parsed by any check at this tree.

**Proposed for the lead, not done here:** two mechanical checks would each turn one of these
from review-detected into gate-detected.
- A `## Replan check` heading marked *kind: work only* in `docs/_templates/CR.md` would let
  check 37 fail a work CR that lacks it.
- A check could fail a `CR- kind: review` whose index table has an empty record-id or owner
  cell.

Either would be a `WK-1178` change of its own.
