---
id: FD-1022
family: finding
title: four counts stated as measurements that were never measured, in one day
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F85.md
---

# F85 — four counts stated as measurements that were never measured, in one day

**Raised** 2026-09-02 by the maintainer, on the lead's report. Phase 2. **Not assigned to a work
item**: this is a practice finding, and its remedy is a rule rather than a task.

## The instances, each with its paragraph and its figure

| # | Where | The figure | What it actually was |
|---|---|---|---|
| 1 | **RL-994**, in the paragraph routing the acceptance-item sweep to the lead | *"twelve ruling records now carry acceptance items"* | Asserted. The derived figure is **30**, of which **28 already existed** when RL-994 was written |
| 2 | **RL-1000**, revising RL-994 in the same routing paragraph | *"fourteen"* | Asserted, and a **revision of an asserted figure is not a derivation**. Filed at 13:27, it could have seen 29 of the 30 — an undercount of at least 15 |
| 3 | **The lead's dispatch** commissioning the close audit, as its stated reason for asking someone else to audit | *"seventeen merged PRs"* | Asserted. The real figures are **22 commits** `b648c22..09b7e9b` and **24 pull requests**, #591 to #614 |
| 4 | **The sweep's own class counts**, reported to the lead | `CONSTRUCTIBLE=52 … NONE_FOUND=35` | Asserted — a correction folded into a **running total** rather than recounted from the rows. Correct set is **54 / 35** |

**All four are the same act: a number produced without running anything, placed where a
measurement belongs, and read by everyone downstream as measured.** None was a lie and none was
careless in the ordinary sense — each author knew roughly the right magnitude and wrote it.

## Why the shape matters more than the individual errors

**A count in a governed document is load-bearing precisely because it looks checkable.** A reader
who would challenge *"most rulings carry acceptance items"* will not challenge *"twelve ruling
records carry acceptance items"* — the specificity is what buys the trust, and in all four cases
the specificity was the part that was invented.

**Instances 1 and 2 compound in a way single errors do not.** RL-1000 revised RL-994's figure,
which reads as a correction and therefore as a derivation — the second number carries *more*
apparent authority than the first while resting on the same absence. **A revised assertion is
still an assertion**, and it is harder to catch because revision is the shape verification takes.

## The adjacent class, named so the finding is not read too widely

**These four were never measured. A different failure is measuring the right thing over the wrong
population**, which reads identically downstream and is a separate defect:

- `d7c9b08`'s body says its guard *"names A1 and A2 as unaccounted"*; the guard names **three**.
  The body described the **fixture's** output, not the real file's.
- The superseded leaf plan's finding 11 against the map plan's *"1355 tracked files"* — a real
  count, of the wrong population.
- That plan's own *"710 renumbered"*, which included 41 `VR-` ids the same table guaranteed
  untouched. Corrected to **673**, then **675**.

**Keeping these separate matters for the remedy:** an unmeasured figure is fixed by measuring; a
figure measured over the wrong population is fixed by **stating the population**, and no amount of
re-running catches it.

## What the rule already required, and the one thing it did not

**`CLAUDE.md` §13 already forbids all four**: *"A reference carries its scope and its measurement.
A count carries the tree **and** the corpus it counted over."* Each instance carries neither. So
this finding is **not a gap in the standard** — it is four violations of a standing rule, in one
day, by four different authors including the lead and a ruling.

**One element §13 does not require, and today produced the case for it: the predicate.** `2446` and
`2519` were measured at the **same tree**, over the **same corpus**, and differ only by pattern —
`@pytest\.mark\.req(` against the bare string, which also matches prose mentions of the marker.
Both satisfy §13 completely. Three readers reproduced neither, and the lead published a false
claim about a third party's work on the strength of that failure.

**Proposed, for the maintainer to accept or strike** — an amendment to §13's existing sentence,
not a new rule:

> A count carries the tree, the corpus it counted over, **and the predicate it counted with** —
> the pattern, command or shipped constant, verbatim and runnable.

**A weaker argument against it, stated rather than hidden:** §13's own test — *"would it still
resolve for a reader holding none of your open context?"* — arguably implies the predicate already,
since a count nobody can re-run does not resolve. If the maintainer reads it that way the clause is
a clarification and may be struck. The lead's view is that the test is a principle and the list is
what people check against, so the list should name all three.

## Falsifiable

Discharged when §13 either carries the predicate clause or is recorded as having declined it with
a date. **Not discharged by the four figures being corrected** — they already are, each in a dated
correction naming what it supersedes. The defect this finding records is the practice, and a
practice is not fixed by fixing its instances.

---

## Discharged — 2026-09-02

**The maintainer accepted the predicate clause, amended in one place, and it is landed in
`CLAUDE.md` §13.** Ruled wording:

> A count carries the tree, the corpus it counted over, **and the predicate it counted with** —
> the pattern or command verbatim and runnable, or the shipped constant **by symbol at that tree**.

**The amendment is to the constant limb, and it is a real improvement on the proposal.** This
finding proposed *"the pattern, command or shipped constant, verbatim and runnable"* — which would
have licensed **pasting** a constant into a document. The maintainer's reason: *"a pasted constant
is RFC-756's stale copy with extra steps."* A constant reproduced in prose is a second copy that
nothing keeps in step with the first, so citing it **by symbol at a tree** is the only form that
stays true — which is the same rule this repository already applies to counts and status.

**The weaker argument this finding raised against the clause was not taken**, and the record notes
that: §13's *"would it still resolve"* test arguably implied the predicate already. The maintainer
added the clause anyway. That is consistent with the finding's own position — the test is a
principle and the list is what people check against.

**Discharge condition met as written**: §13 carries the clause, dated. The four instances remain
corrected in their own dated records; as this finding states, that was never the discharge.
