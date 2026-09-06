---
id: RFC-839
family: proposal
kind: process
title: Pending proposals — for the §14 review at WK-671's close
status: closed                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-08-29
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this RFC itself corrects a frozen record
relates: []                     # ids only
was: docs/audit/plan-reviews.md
---

### Pending proposals — for the §14 review at WK-671's close (drafted 2026-08-29)

**This is not a plan review and binds nothing.** It has no review number, no five questions
and no maintainer acceptance line, because the §14 trigger — a workstream close — has not
fired. It exists because two rule proposals had no durable home: one lived only in the
comments of [`#370`](https://github.com/yes-404/gi-pricing-plan/pull/370), now merged and
closed, and the other was never written down at all.
[`../../CLAUDE.md`](../../CLAUDE.md) §12 requires a decision to land as a dated artifact
rather than in chat, and a comment on a closed pull request is nearer to chat than to a
record. The review at WK-671's close folds these in, numbers them, and takes them to the
maintainer.

**Deliberately unnumbered — and that is the first finding.** Both candidates below had been
referred to as "rule 6". Read at `97fcb16`,
`docs/findings/FD-00894-rfc-840-841-adoption-pilot.md`'s P7 disposition read *"the
writer's half … is drafted as rule 6 and deliberately **not landed**"*, and P13's read
*"Rides with rule 6 into the §14 review"* — while the only text actually drafted under that
number, in `#370`'s comments, was candidate B. **Candidate A was promised, not drafted**, so
the number attached to whichever proposal a reader had in mind. A rule number is an
identifier, and an identifier assigned before the thing exists is the same defect as a count
written before the list is closed. **Numbering happens at acceptance.**

> **Corrected upstream while this entry was open.** PR #390 (`e9f9fa5`) fixed both
> dispositions: P7 now records the writer's half as filed unnumbered here, and P13 is marked
> **fixed** because its clause is already in rule 5 on `main`. The quotations above are
> therefore historical, and are kept with the tree they were read at rather than deleted —
> the collision was real and is why both candidates are unnumbered. Reporting it rather than
> editing another role's tree was the disposition; the owning role made the correction.

#### Candidate A — do not move a branch someone is reading *(P7's writer's half; drafted here for the first time)*

> Rule 4's second half tells a **reader** to name the commit they read. The **writer's** half
> is cheaper and was missing: while a branch is under review or audit, do not push to it. A
> reviewer's finding is written against a tree, and moving that tree turns a correct finding
> into an apparently wrong one — the reviewer pays for a cost the author created, and pays it
> invisibly, because a stale finding reads exactly like a careless one. On 2026-08-29 the head
> of `#370` moved three times during an audit; the auditor filed a finding true of the tree
> they read and false by the time they wrote it. Freeze on request, name the frozen SHA where
> the reviewer will see it, and when a change genuinely cannot wait, say what moved and why
> rather than letting the reviewer discover it.

#### Candidate B — declare up front that a count is not load-bearing *(recovered verbatim from `#370`)*

> Rules 1–5 each guard a *claim* you wrote. This one guards a claim's *form*. A count of items
> in a plan — prerequisites, findings, divergences, sites — is the first thing to age, because
> the items are discovered incrementally while the total is written once, and every later
> discovery silently falsifies it. The retrospective fix works and is expensive:
> [`../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`](../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md) removed *"every
> bare count in this section … rather than corrected a third time, replaced by the enumerated
> list above"* — after the figure had already moved twice within an hour, in opposite
> directions, for unrelated reasons.
>
> The prospective form costs one clause and cannot go stale. The same plan's prerequisites
> heading reads *"named individually, because … a bare count of them is not load-bearing
> anywhere in this document"* — written before any count was wrong, and never corrected
> since. **Prefer the heading to the retraction.**
>
> Where a total is genuinely wanted, it carries the granularity it was counted at. Two readers
> who split the same list differently get different totals and each believes the other wrong —
> which is not hypothetical: one enumeration of the same divergences was filed as two, then
> four, then six, then none, and every one of those figures was correct at the granularity
> that produced it.

#### Also carried, and not a new rule

**P13 sharpens rule 5 rather than adding to it.** The sweep's unit is every obligation the
record imposes, not every heading matching a pattern — an addendum to an existing ruling
never gets a new numbered heading, so a heading-keyed index is blind to precisely the changes
that arrive late. That clause is already in rule 5 as merged (`#370`), and P13's disposition
now reads **fixed** for that reason (PR #390). Nothing rides with a rule-6 proposal.

**Why both candidates are proposals and not edits.** [`../../CLAUDE.md`](../../CLAUDE.md)
§14: a review's output is a proposal with a dated maintainer acceptance line, never a change.
Landing either rule now would decide the thing the review exists to test — and the planner
does not rule its own proposals.

---
