---
id: RL-918
family: ruling
title: WK-671 reopen — the maintainer's direction, recorded (2026-08-30)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-w11-reopen-direction.md
---

# WK-671 reopen — the maintainer's direction, recorded (2026-08-30)

**What this is.** The maintainer's instruction to reopen the uncompleted part of WK-671, quoted
verbatim and dated. It exists because RL-919 clause 1 made it a precondition: until the
direction is in an artifact, the reopen rests on the lead's relay, and the WK-671 closure record
would be annotated on authority no later reader could find.

**Raised by the decision-maker, not by the lead.** The dispatch that requested Rulings 39–41
asserted the direction as established fact. The decision-maker checked the tree, found nothing
carrying it, and declined to build the ruling's shape on the relay — `CLAUDE.md` §12: *"Every
decision lands as a dated artifact — a ruling record, an audit record, a plan — never in
chat."* This record is the correction.

## 1. The direction

Received 2026-08-30, in the maintainer's own message opening this session, verbatim and
complete:

> *"read handover in /home/puzhenhao1989/gi-pricing-plan.local, spawn the team; landing
> NT0012, 13 and 14; reopen the uncompleted WK-671, follow the process to the end of WK-671"*

Nothing else in that message bears on WK-671's scope, and no later maintainer message in this
session has amended it.

## 2. What it does and does not authorise

**It reopens WK-671.** The reduced-scope close of 2026-08-30 (`docs/closures/CR-00927-work-item-record-wk-671-scoring.md`)
recorded three requirements as *not started*; *"reopen the uncompleted WK-671"* directs that they
be built. RL-919 fixes the scope at **FR-253, FR-254 and FR-259**, and with
FR-259 the NFR-500 that the closure record §6 tied to it.

**It does not authorise the lead to accept the re-close.** This is the point on which the
earlier delegation must not be stretched. The maintainer's 2026-08-30 delegation —
*"plz mind that I have already authorised you to decide WK-671 close"* — was given for the close
that then happened, and both `docs/plans/INDEX.md#2026-08-30-nt-0012-0013-0014-adoptionmd` §1.1 and the
closure record read it narrowly. A delegation to decide *one* close is not a standing licence
to decide the next one. **The re-close returns to `CLAUDE.md` §12's default: acceptance of a
Work close is the maintainer's, with a dated line.**

**It does not fold the adoption into WK-671.** *"landing NT0012, 13 and 14"* is a separate
instruction in the same message, and the adoption is a separate Work with its own filed record
and its own bounded delegation (RL-919 §1). Slices E, F and G continue under
`2026-08-30-nt-0012-0013-0014-adoption.md`.

## 3. One thing this record deliberately does not settle

**Whether NFR-489's remediation belongs inside the reopen.** NFR-489 was not
*uncompleted* at the close — it was measured, and it failed, and it was carried forward with a
named resolution. So the plain reading of *"the uncompleted WK-671"* does not reach it, and Ruling
39 scoped the reopen without it.

What has changed since is that **RL-921 makes the dominant term cheaply removable**: the
version-row read stays on the hot path while the blob lookup, the ~2 MB object read and the
full `model_validate_json` leave it, with **zero staleness window**. That was not known when
the close was written.

This is a scope question for the maintainer, not one the lead may settle by widening the work
it was given. It is **raised**, not assumed, and the point is recorded here so that a later
reader can tell a deliberate exclusion from an oversight. **Note that removing that term does
not make NFR-489 pass**: the 15 ms without-GBM limb already reads component p99 23.027 ms
with the fetch excluded, and RL-921 declines to amend the requirement or to call it
reachable.

---

## 4. Amendment, 2026-08-30 — the re-close is delegated to the lead, under two conditions

**This section supersedes exactly one sentence of §2**, which is left standing verbatim above
so a reader can see what was believed: *"It does not authorise the lead to accept the
re-close."* That was correct when written. The maintainer has since delegated the re-close,
and this section records the delegation and its limits. **It supersedes RL-919 §5** on the
same point.

### The instruction

Received 2026-08-30, later the same day, in reply to the lead's report that the re-close would
return to the maintainer:

> *"point 1: yes delagated to close WK-671 again but only approve after all the slices completed
> and the auditor happy with the WK-671 closure"*

### What it authorises, and the two conditions

The lead may accept WK-671's second close and write the dated acceptance line. **The delegation is
conditional, and both conditions are preconditions on the acceptance itself — not
considerations to weigh.** Neither may be waived by the lead, since a delegate cannot relax the
terms of its own delegation.

**Condition 1 — all the slices completed.** Read as the reopened scope: **WK-671 Slice 3 (tasks
3A, 3B, 3C, 3D) and WK-671 Slice 4 (tasks 4A, 4B, 4C, 4D)**, delivering FR-253, FR-254,
FR-259 and NFR-500 — the scope RL-919 §1 fixed and §9 of the closure record
restates. Two boundaries follow, and both are recorded rather than assumed:

- **Adoption slices E, F and G are not among them.** They are a separate Work under a separate
  delegation (RL-919 §1). WK-671's close does not wait on them and is not entitled to claim
  them.
- **If a further slice is ruled into the reopen it joins this condition automatically.** At the
  time of writing, the decision-maker holds an open ruling on whether NFR-489's remediation
  belongs inside the reopen. If it rules the remediation in, that work is part of "all the
  slices" and the condition is not met until it too is complete.

**Condition 2 — the auditor happy with the WK-671 closure.** The §13 closure audit must be clean
in the auditor's own judgement, and the lead may not accept over the auditor's dissatisfaction.

**This is stronger than `CLAUDE.md` §13's default and the difference is deliberate.** Under
§13 the auditor *proposes* verdicts and the lead adopts, amends or rejects them; the lead's
verdict authority is unchanged and is not transferred by this condition. What changes is the
**close**: an unresolved auditor objection is a bar to acceptance, not an input to it. **The
resolution when the lead and the auditor disagree is to escalate to the maintainer — never to
overrule the auditor and accept.** Recorded explicitly because the failure mode is silent: a
lead holding both the verdict pen and the acceptance pen can satisfy this condition by
amending the verdict that troubled the auditor, which would meet the words while defeating the
instruction.

### What it does not authorise

**It reaches WK-671's second close and nothing else.** Not the adoption's close, not WK-672, not
Phase 2, not any later close of WK-671 should it be reopened again. `CLAUDE.md` §12's default —
acceptance of a Work, Phase or Project close is the maintainer's — resumes the moment this one
is written. The lesson §2 records still stands: a delegation to decide one close is not a
standing licence for the next, and this record is dated so that the next reader must check
rather than infer.
