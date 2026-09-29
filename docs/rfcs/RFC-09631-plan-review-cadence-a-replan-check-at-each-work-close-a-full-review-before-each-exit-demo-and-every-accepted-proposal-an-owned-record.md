---
id: RFC-9631
family: proposal
kind: process
title: Plan-review cadence — a replan check at each Work close, a full review before each exit demo, and every accepted proposal an owned record
status: active
created: 2026-09-29
owner: maintainer
tree: 5638f69120e0f4d9c958dc1bf4a07f589b42f080
deliverable: the CLAUDE.md §14 trigger and output rule, restated at every site that states them, with a replan-check section in every Work close record and plan reviews filed as short indexes of owned records
lands_in: CLAUDE.md §14, .claude/skills/phase-review, .claude/skills/close-workstream, docs/process/checklists/work-item-close.md, docs/process/document-ids.md §1.6, .claude/roles/lead.md and planner.md
trigger: a Work close (the replan check), and each phase's exit demo (the full review)
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [CR-723, CR-722, CR-755, CR-788, CR-823, CR-824, CR-825, CR-830, CR-925, CR-926, CR-932, CR-1050, CR-1064, CR-1167, CR-1212, CR-1243]
---

# RFC-9631 — Plan-review cadence: a replan check at each Work close, a full review before each exit demo, and every accepted proposal an owned record

**Working id `9631`**; minted at this PR's merge turn with `python3 scripts/doc-id.py next
--ref origin/main`. **Drafted by the planner; owned by the maintainer** (`document-ids.md`
§1.6, RFC row). **`status: active`**: the maintainer decided both parts before this draft
(see *Acceptance*). The decision-maker records the process ruling on it as an `RL-`.

## Problem

`CLAUDE.md` §14 fires a full plan review **at each workstream close, and again before a
phase's exit demo**. The maintainer asked, on 2026-09-29: *"I find plan review to frequent,
and it is not so necessary. plz help me to evaluate it"*. The evidence below was re-derived
for this RFC from the fifteen review records on `main`, at `5638f691`.

**Frequency.** The records are every `docs/closures/CR-*.md` whose front matter reads
`kind: review` (`grep -l '^kind: review' docs/closures/CR-*.md`): 15, reviews 1 to 15, dated
by their `created:` field.

| Review | Record | Created | Lines (`wc -l`) | Trigger (its title) |
|---|---|---|---|---|
| 1 | `CR-723` | 2026-08-15 | 106 | WK-663's close |
| 2 | `CR-722` | 2026-08-15 | 152 | WK-667's close and before Phase 1a's exit demo |
| 3 | `CR-755` | 2026-08-22 | 115 | WK-661's close |
| 4 | `CR-788` | 2026-08-24 | 136 | WK-692's close |
| 5 | `CR-823` | 2026-08-27 | 171 | WK-664's close |
| 6 | `CR-824` | 2026-08-27 | 45 | WK-665's close, before the Phase 1b exit demo |
| 7 | `CR-825` | 2026-08-27 | 219 | WK-669's close |
| 8 | `CR-830` | 2026-08-28 | 305 | WK-670's close |
| 9 | `CR-925` | 2026-08-30 | 935 | WK-671's close |
| 10 | `CR-926` | 2026-08-30 | 341 | WK-671's second close |
| 11 | `CR-932` | 2026-08-31 | 347 | completing WK-671's close, before WK-672 |
| 12 | `CR-1050` | 2026-09-03 | 288 | the W37-6/W37-11 boundary, mid-window |
| 13 | `CR-1064` | 2026-09-18 | 637 | the W37-6 close, the W37-7…11 cut |
| 14 | `CR-1167` | 2026-09-27 | 207 | the WK-697 close |
| 15 | `CR-1212` | 2026-09-28 | 532 | P2's exit criteria |

- **Gaps.** Between consecutive reviews, in days by `created:`: 0, 7, 2, 3, 0, 0, 1, 2, 0, 1,
  3, 15, 9, 1 (14 gaps). **The median is 1.5 days**, the same as the maintainer's figure.
  - **The two counts differ, and both are stated here.** The maintainer's entries (16:05:14,
    and 18:43:03 above) read "12 of 14 gaps were under 7 days". This re-derivation gives
    **11 of 14 under 7 days** (the predicate `gap < 7`) and **12 of 14 at 7 days or under**
    (`gap <= 7`).
  - The difference is one gap: 7 days, between reviews 2 and 3.
  - The maintainer's research ran at `6ae8a99a` and its predicate is not recorded. This RFC
    does not choose between the two readings; the rule it adopts does not depend on either.
- **Length.** 4,536 lines over 15 reviews: **a mean of 302.4**. Every review from 9 to 15 is
  over 200 lines (207 to 935). Review 8 is 305.
- **Work closes with no review of their own.**
  - **The maintainer's figure is 4:** WK-660, 666, 668 and 694.
  - **This re-derivation finds 9 at `5638f691`.** The predicate is every `### WK-` section
    in `docs/roadmap.md` with `status: closed` whose close no review's title or trigger
    paragraph names.
    - The maintainer's 4 are confirmed.
    - **WK-693** (closed on `CR-933`) is missed by the 6ae8a99a count.
    - **WK-672** closed after `6ae8a99a` (`CR-1243`).
    - WK-657, 658 and 659 closed on 2026-08-14, the day before §14 existed (`RFC-711`,
      2026-08-15).
  - So it is **6 since §14 existed**. Under the old rule every one of them should have had a
    review; under option C each would have carried a replan check.
- **Materiality** (the maintainer's classification: material 1, 2, 3, 6, 7, 13, 14 and 15;
  minor 4, 5, 8, 9, 10 and 11; review 12 "changed nothing" and was superseded). The
  predicate re-derived here: *material* means an accepted proposal changed a phase boundary,
  a Work's scope or membership, an exit criterion, or the ordering of Works. It agrees on
  every review but one.
  - **Review 9 is borderline.** Its row 4.4 corrected WK-672's recorded scope, which is
    material if a correction to recorded scope counts as a scope change.
  - Review 13's changes are at slice level, inside WK-697.
  - Review 12 accepted none of its proposals: `CR-1064` superseded its four rows before
    acceptance (`CR-1050:284-288`).

## Options

The options are as the maintainer recorded them in the entry `2026-09-29 18:43:03 BST · maintainer (acting on the maintainer's behalf) · the plan-review cadence OPTIONS A–D and the Part 2 options, recorded for RFC-9631`. They were presented
to the user in the maintainer's session on 2026-09-29 at about 16:02 BST, before the user
chose C (about 16:05).

**Part 1: cadence.** The table is quoted from that entry.

| | Rule | Effect, as presented |
|---|---|---|
| **A** | Keep as is: every Work close plus before each phase exit demo | The status quo: a review about every 1.5 days |
| **B** | Before each phase exit demo only | The fewest reviews. It misses the Work-close scope moves (reviews 1, 7, 13 and 14 were material at Work closes) |
| **C** (recommended; **chosen**) | A full review before each phase exit demo. At a Work close, a full review only if a replan trigger fires, and the auditor's CR carries a short replan check. A length cap of about 150 lines | It would have kept all 8 material reviews and dropped the 6 minor ones: about 40% fewer reviews, and much shorter ones |
| **D** | Time-based: every 2 weeks, plus before the phase exit demo | Predictable, but decoupled from when plans actually change |

**Part 2: the review's output.** The user asked: *"evaluate what if ask plan review generate
RFC rather than text in closure, as the closure report is not a file for requirement
analysis"*. Two options were presented, as the same entry records them:
- **Option 1, every accepted proposal becomes an RFC: not chosen.**
  - For it: the RFC lifecycle tracks landing.
  - Against it: it is heavy for minor proposals (6 of 15 reviews were convention or notes
    only); most proposals are not RFC-shaped (a replan is a new PL, a spec change is an RL, a
    gap is an FD); and it adds many ids.
- **Option 2, routed outputs: chosen.** Each accepted proposal becomes the §1.6 family that
  owns its kind. It is *Proposal*, Part 2.

## Proposal

### Part 1 — cadence (option C)

The rule, verbatim from the maintainer's entry of 2026-09-29 16:05:14 BST ("Option C, the
rule to adopt"):

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

**One addition, for the rows that wait on a review.** `python3 scripts/register-owed.py
review` lists the register rows naming the §14 review (`phase-review` skill, "The agenda
includes every register row that decayed to this review"). With fewer full reviews those
rows would wait longer unseen. So the replan check records that command's owed count at the
close's tree. It is evidence, not a new trigger: an owed row becomes a trigger only when it
moves a slice or phase, which rule 2 already names.

### Part 2 — routed outputs (future-facing)

Verbatim from the maintainer's entry of 2026-09-29 16:12:57 BST. **No retroactive
conversion** of reviews 1–15.

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

### The baseline (Part 2's evidence), not converted

Part 2 is future-facing: **no clean-up of reviews 1–15 is ordered**, and this baseline is
recorded as a count at a tree, not converted into records. Any later clean-up is a separate
decision for the maintainer. **Two counts are stated, because their predicates differ.**

- **The maintainer's landing check**, at `6ae8a99a`. Its predicate is not recorded; the
  figures come from the entries of 16:12:57 and 18:43:03:
  - 119 accepted proposals;
  - 57 landed, 12 partial, 48 not landed, 2 superseded;
  - not-landed items concentrated in unowned convention changes and unanswered questions,
    with reviews 9 and 10 holding 26 of them.
- **This RFC's re-derivation**, at `5638f691`:
  - **What counts as a proposal:** one row of a review's own consolidated proposals table,
    excluding "no change" rows. Reviews 1–4 have no such table, so there it is each item of
    the acceptance block. For review 14 it is its four "Proposals needing the maintainer's
    line". For review 15 it is P1, P2, P3–P12, P13 and P13b (14); its 91 finding resolutions
    and five G4 dispositions are not proposals.
  - **Accepted:** a dated acceptance line, the maintainer's or a delegate's, covers it.
  - **Landed:** the artifact exists on `main`.
  - **Result: 101 accepted proposals; 50 landed, 12 partial, 39 not landed, 0 superseded.**
    Per review, the accepted counts are:

    | Review | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
    |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
    | Accepted | 2 | 3 | 5 | 3 | 8 | 1 | 6 | 6 | 23 | 10 | 9 | 0 | 7 | 4 | 14 |

  - **Reviews 9 and 10 hold 25 of the 39 not landed** (19 and 6). Review 9's 19 are 11
    unowned conventions, 6 unanswered or maintainer-only questions, and 2 others. Review
    10's 6 are 4 unowned conventions and 2 unowned corrections.
- **Where they differ, and where they agree.**
  - The gap of 18 accepted proposals cannot be pinned down without the first check's
    predicate. The likely sources are review 12's rows (superseded, never accepted: counted
    as 0 here, while "2 superseded" there suggests some were counted), review 15's sub-items,
    and grouping choices in reviews 1 and 8.
  - **Both counts agree on what Part 2 rests on:** most not-landed proposals are unowned
    conventions and unanswered questions, concentrated in reviews 9 and 10. That is what
    "no unowned" and routing each proposal to an owned record address.
- **Review 4's owning-row rule was accepted and never written into a process document.**
  - `CR-788:77-78` proposed *"every accepted §14 proposal gets an owning row in the same
    edit that accepts it, or is explicitly marked unowned"*, and it was accepted at
    `:123-125`.
  - It was applied at reviews 4, 7 and 8, and restated only in frozen plans.
  - `git grep` at `5638f691` over `docs/process`, `.claude/skills`, `CLAUDE.md` and
    `docs/roadmap.md` finds no statement of it.
  - Its escape clause, "or is explicitly marked unowned", is what let proposals stay
    unowned. Part 2's rule 2 removes that escape and writes the rule into the sites below.

## Sites: every grep hit, with its verdict

**Tree:** `5638f691` (this branch's base, `git grep … HEAD`, before any edit). **Two greps,
verbatim:**

- **Grep 1** (trigger and output wording), over the whole tree **excluding the frozen record
  families** `docs/closures`, `docs/rulings`, `docs/findings`, `docs/plans`, `docs/rfcs`,
  `docs/research` and `docs/ledgers`:

  ```text
  git grep -nIiE 'each workstream close|every workstream close|at each (work|workstream)[ -]close|at every work close|each work close|every work close|workstream close, and again|plan review.*(trigger|at each)|§14 (plan )?review|phase-review' HEAD -- ':!docs/closures' ':!docs/rulings' ':!docs/findings' ':!docs/plans' ':!docs/rfcs' ':!docs/research' ':!docs/ledgers'
  ```

  It prints 60 lines.
- **Grep 2** (any mention of the review), over the process, charter and skill files that
  state procedure:

  ```text
  git grep -nIiE 'plan review|plan-review|phase review|§14' HEAD -- docs/process .claude/roles .claude/skills/close-workstream .claude/skills/phase-review .claude/skills/README.md .claude/agents/README.md docs/process/delivery-process.core.json
  ```

  It prints 63 lines.

Together they give **116 distinct `file:line` sites**:
- 17 **amended**;
- 2 **the lead's** (`CLAUDE.md` §14);
- 12 **historical**: not amended, because each is a dated record of the rule then;
- 85 **unaffected**.

The *Grep* column says which grep found each site. **No live copy of the old trigger
survives:** every site stating "at each workstream close" as the rule now is amended, or is
the lead's §14 edit. The ones left are dated records.

**Amended, but on no grep line** (Part 2's named sites, and new text):
- `docs/process/document-ids.md:165`, the CR row: review-as-index, the replan check on
  `work` records, and no unowned;
- the `close-workstream` closure-record template's new **Replan check** field;
- `phase-review`'s new *Length* section, its replan-check questions, the fifth rule, and a
  *Verified* entry;
- `close-workstream`'s *Verified* entry.

| Site | Grep | Verdict | Why |
|---|---|---|---|
| `.claude/agents/README.md:43` | 2 | unaffected | the delegable-agent rules; the output is still a proposal with an acceptance line |
| `.claude/agents/README.md:74` | 2 | unaffected | the delegable-agent rules; the output is still a proposal with an acceptance line |
| `.claude/agents/README.md:86` | 1+2 | unaffected | the delegable-agent rules; the output is still a proposal with an acceptance line |
| `.claude/agents/README.md:111` | 1 | unaffected | the delegable-agent rules; the output is still a proposal with an acceptance line |
| `.claude/agents/README.md:127` | 2 | unaffected | the delegable-agent rules; the output is still a proposal with an acceptance line |
| `.claude/agents/README.md:156` | 1 | unaffected | the delegable-agent rules; the output is still a proposal with an acceptance line |
| `.claude/roles/auditor.md:13` | 2 | unaffected | the effort rule names "a plan review" as a raise case |
| `.claude/roles/decision-maker.md:13` | 2 | unaffected | the effort rule names "a plan review" as a raise case |
| `.claude/roles/lead.md:25` | 1+2 | unaffected | the verdict on §14 recommendations and the `review` family: unchanged |
| `.claude/roles/lead.md:26` | 2 | unaffected | the verdict on §14 recommendations and the `review` family: unchanged |
| `.claude/roles/lead.md:33` | 1+2 | unaffected | the verdict on §14 recommendations and the `review` family: unchanged |
| `.claude/roles/lead.md:82` | 2 | **amended** | "answerable for §14 firing on its fixed trigger": restated, plus "no unowned" |
| `.claude/roles/lead.md:83` | 1 | **amended** | "answerable for §14 firing on its fixed trigger": restated, plus "no unowned" |
| `.claude/roles/planner.md:13` | 2 | unaffected | effort line, mandatory skill, or the CR filing the charter already names |
| `.claude/roles/planner.md:15` | 1 | unaffected | effort line, mandatory skill, or the CR filing the charter already names |
| `.claude/roles/planner.md:16` | 2 | unaffected | effort line, mandatory skill, or the CR filing the charter already names |
| `.claude/roles/planner.md:28` | 2 | historical | a citation of review 8 Q4 |
| `.claude/roles/planner.md:36` | 1+2 | **amended** | the trigger and the filing form |
| `.claude/roles/planner.md:40` | 2 | **amended** | the trigger and the filing form |
| `.claude/roles/planner.md:42` | 2 | unaffected | effort line, mandatory skill, or the CR filing the charter already names |
| `.claude/roles/planner.md:59` | 2 | unaffected | effort line, mandatory skill, or the CR filing the charter already names |
| `.claude/roles/planner.md:64` | 2 | unaffected | effort line, mandatory skill, or the CR filing the charter already names |
| `.claude/skills/README.md:86` | 1 | unaffected | an index or history line naming the skill or §14 |
| `.claude/skills/README.md:121` | 1+2 | **amended** | the `phase-review` index row |
| `.claude/skills/README.md:521` | 2 | unaffected | an index or history line naming the skill or §14 |
| `.claude/skills/README.md:651` | 2 | unaffected | an index or history line naming the skill or §14 |
| `.claude/skills/close-workstream/SKILL.md:11` | 2 | **amended** | the §14 paragraph: the replan check replaces "at each workstream close" |
| `.claude/skills/close-workstream/SKILL.md:12` | 1 | **amended** | the §14 paragraph: the replan check replaces "at each workstream close" |
| `.claude/skills/close-workstream/SKILL.md:13` | 2 | **amended** | the §14 paragraph: the replan check replaces "at each workstream close" |
| `.claude/skills/close-workstream/SKILL.md:14` | 1 | **amended** | the §14 paragraph: the replan check replaces "at each workstream close" |
| `.claude/skills/close-workstream/SKILL.md:351` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:507` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:509` | 1+2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:511` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:516` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:521` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:525` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:695` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:741` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:742` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:746` | 2 | unaffected | binding plan-review conditions (§5a) and their instances: still due for every accepted review |
| `.claude/skills/close-workstream/SKILL.md:781` | 2 | historical | a *Verified* or instance note: a dated record |
| `.claude/skills/close-workstream/SKILL.md:796` | 2 | historical | a *Verified* or instance note: a dated record |
| `.claude/skills/phase-review/SKILL.md:2` | 1 | unaffected | the skill name, a heading, or §14 cited as the standard |
| `.claude/skills/phase-review/SKILL.md:3` | 1+2 | **amended** | description: the trigger |
| `.claude/skills/phase-review/SKILL.md:6` | 2 | unaffected | the skill name, a heading, or §14 cited as the standard |
| `.claude/skills/phase-review/SKILL.md:8` | 2 | unaffected | the skill name, a heading, or §14 cited as the standard |
| `.claude/skills/phase-review/SKILL.md:16` | 1 | **amended** | *When*: the trigger |
| `.claude/skills/phase-review/SKILL.md:77` | 2 | unaffected | the skill name, a heading, or §14 cited as the standard |
| `.claude/skills/phase-review/SKILL.md:124` | 2 | **amended** | *Output*: the index form (it also named a pre-migration location) |
| `.claude/skills/phase-review/SKILL.md:143` | 2 | historical | a *Verified* entry: a dated record of the rule then |
| `.claude/skills/phase-review/SKILL.md:145` | 2 | historical | a *Verified* entry: a dated record of the rule then |
| `.claude/skills/phase-review/SKILL.md:150` | 2 | historical | a *Verified* entry: a dated record of the rule then |
| `.claude/skills/repo-architecture/SKILL.md:209` | 1 | unaffected | cites the skill's worked example |
| `CLAUDE.md:254` | 1 | unaffected | the acceptance-line owner (:254) and the record destination (:273) |
| `CLAUDE.md:309` | 1 | **the lead's** | §14 heading and trigger sentence: the lead drafts the edit, and the user sees the diff before merge |
| `CLAUDE.md:315` | 1 | **the lead's** | §14 heading and trigger sentence: the lead drafts the edit, and the user sees the diff before merge |
| `backend/tests/test_contracts.py:99` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `docs/INDEX.md:848` | 1 | unaffected | generated titles of closed or historical records |
| `docs/INDEX.md:976` | 1 | unaffected | generated titles of closed or historical records |
| `docs/INDEX.md:1304` | 1 | unaffected | generated titles of closed or historical records |
| `docs/INDEX.md:1328` | 1 | unaffected | generated titles of closed or historical records |
| `docs/process/agent-settings.md:57` | 2 | unaffected | the effort rule names "a plan review" as a raise case |
| `docs/process/agent-settings.md:61` | 2 | unaffected | the effort rule names "a plan review" as a raise case |
| `docs/process/checklists/phase-close.md:14` | 1 | unaffected | the pre-demo review: unchanged |
| `docs/process/checklists/work-item-close.md:27` | 2 | **amended** | the §14 paragraph: the replan check |
| `docs/process/checklists/work-item-close.md:28` | 1 | **amended** | the §14 paragraph: the replan check |
| `docs/process/checklists/work-item-close.md:30` | 2 | **amended** | the §14 paragraph: the replan check |
| `docs/process/checklists/work-item-close.md:31` | 1 | **amended** | the §14 paragraph: the replan check |
| `docs/process/delivery-process.md:281` | 1 | unaffected | §12 is a pointer to the skills, and :349/:374 are dated history; the trigger is not stated here, so no second copy is added (RFC-756) |
| `docs/process/delivery-process.md:349` | 2 | unaffected | §12 is a pointer to the skills, and :349/:374 are dated history; the trigger is not stated here, so no second copy is added (RFC-756) |
| `docs/process/delivery-process.md:374` | 2 | unaffected | §12 is a pointer to the skills, and :349/:374 are dated history; the trigger is not stated here, so no second copy is added (RFC-756) |
| `docs/process/document-ids.md:152` | 1 | **amended** | Phase row: "lead runs `phase-review`" aligned to the planner (flagged for the maintainer) |
| `docs/process/document-ids.md:155` | 2 | unaffected | a row naming the review as an actor or event, not the trigger |
| `docs/process/document-ids.md:166` | 2 | unaffected | a row naming the review as an actor or event, not the trigger |
| `docs/process/document-ids.md:251` | 2 | unaffected | a row naming the review as an actor or event, not the trigger |
| `docs/process/residue-ceiling-record.md:59` | 2 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:61` | 2 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:109` | 2 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:110` | 2 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:173` | 2 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:174` | 2 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:215` | 1 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:328` | 1 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:399` | 2 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:480` | 2 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:481` | 2 | unaffected | a residue row naming the skill file |
| `docs/process/residue-ceiling-record.md:482` | 2 | unaffected | a residue row naming the skill file |
| `docs/roadmap.md:361` | 1 | historical | not amended: a dated record of the rule then (the Phase 1a plan-review row; the RFC-895…898 reconciliation clause) |
| `docs/roadmap.md:372` | 1 | historical | not amended: a dated record of the rule then (the Phase 1a plan-review row; the RFC-895…898 reconciliation clause) |
| `docs/roadmap.md:375` | 1 | historical | not amended: a dated record of the rule then (the Phase 1a plan-review row; the RFC-895…898 reconciliation clause) |
| `docs/roadmap.md:412` | 1 | unaffected | a row naming "the next §14 review" as an event, not the trigger |
| `docs/roadmap.md:742` | 1 | unaffected | a row naming "the next §14 review" as an event, not the trigger |
| `docs/roadmap.md:757` | 1 | unaffected | a row naming "the next §14 review" as an event, not the trigger |
| `docs/roadmap.md:859` | 1 | historical | not amended: a dated record of the rule then (the Phase 1a plan-review row; the RFC-895…898 reconciliation clause) |
| `docs/roadmap.md:860` | 1 | historical | not amended: a dated record of the rule then (the Phase 1a plan-review row; the RFC-895…898 reconciliation clause) |
| `docs/roadmap.md:863` | 1 | historical | not amended: a dated record of the rule then (the Phase 1a plan-review row; the RFC-895…898 reconciliation clause) |
| `docs/roadmap.md:894` | 1 | unaffected | a row naming "the next §14 review" as an event, not the trigger |
| `docs/roadmap.md:1202` | 1 | unaffected | a row naming "the next §14 review" as an event, not the trigger |
| `docs/specs/00-overview.md:230` | 1 | unaffected | FR-1188 is `close-workstream` §5c, a close check, not the plan review |
| `scripts/doc-id.py:7907` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `scripts/doc-id.py:7925` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `scripts/register-lint.py:408` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `scripts/register-owed.py:45` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `scripts/register-owed.py:172` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_doc_id_migrate.py:2573` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_doc_id_migrate.py:2628` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_doc_id_migrate.py:2648` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_doc_id_migrate.py:2652` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_doc_id_migrate.py:2679` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_register_lint.py:184` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_register_lint.py:218` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_register_lint.py:248` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_register_lint.py:279` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_register_lint.py:318` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |
| `tests/test_register_lint.py:472` | 1 | unaffected | code, or a test fixture string; `register-owed.py review` and the decay rule name "the next plan review", which still exists |

## Deliverable

The trigger and output rule above, stated at every site that states them, as listed. A
Work close record carries a **Replan check** section, and a plan review is a short index of
owned records. It lands in this one PR, together with the decision-maker's process `RL-` and
the lead's `CLAUDE.md` §14 edit, which the user sees as a diff before merge. **It is `closed`
when that PR merges and the first Work close after it carries a replan check.**

## Acceptance

**Maintainer acceptance, verbatim:**
- The maintainer's words, 2026-09-29 (~16:05 BST), as quoted in the entry `2026-09-29
  16:05:14 BST · maintainer (acting on the maintainer's behalf) · PLAN-REVIEW CADENCE: option C
  adopted by the maintainer; RFC + RL + amendments in one PR`: *"go with option C"*.
- The maintainer's words, 2026-09-29, as quoted in the entry `2026-09-29 16:12:57 BST ·
  maintainer (acting on the maintainer's behalf) · PLAN-REVIEW RFC, Part 2 folded in: routed
  outputs (future-facing)`: *"fold option 2 into the option C RFC; the decision is future
  facing and target to help track proposal, plz go ahead"*.
- **The user's confirmations**, given in the lead's session and relayed by the lead with
  these times:
  - *"i confirm option C of the RFC"*: 2026-09-29 15:23:09Z (16:23:09 BST).
  - *"Plan-review RFC. I confirm BOTH parts: Part 1, option C cadence; and Part 2, routed
    outputs (every accepted proposal becomes an owned record, no 'unowned', the review is a
    short index). This includes any change Part 2 needs to CLAUDE.md §14's own wording. Show
    me the final §14 diff before merge, as you planned."*: **between 16:25:49 BST and
    16:28:03 BST**. It is a bound, not a point time: the lead's transcript copy was
    compacted. The message cites the maintainer's 16:25:49 BST entry, and the lead's commit
    `5f27c02f` (15:28:03Z) already quotes its trailer instruction.
