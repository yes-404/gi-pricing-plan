---
id: FD-9602
family: finding
title: WF-699 step D4 describes a band-edge monotone counterexample that 03 FR-261's grid cannot promise
status: active
created: 2026-09-29
owner: auditor
tree: 1c8762d9ed235f80e0f2fff80c44003694828e97
corrected_by: []
relates: [WK-672, WF-699, OQ-1224]
---

# FD-9602 — WF-699 step D4 describes a band-edge monotone counterexample that 03 FR-261's grid cannot promise

## Finding

**Severity: low. It bears on G2**, because plan review 15's G2 exit demo is `WF-699` end to end
(`CR-1212` Proposal 1). The auditor found it on 2026-09-29 by the `close-workstream` §5c reading
at the WK-672 Work close (`00` FR-1188). It is a disagreement between a journey step and the
requirement the step cites. It is not a verdict on the WK-672 close, and this record does not
say which side is wrong: that is `CLAUDE.md` §0's question.

`WF-699` step D4 cites `03` FR-261 and describes a `monotone` property that fails exactly at a
band edge, with a minimal counterexample at the two adjacent ages. FR-261, as clarified on
2026-09-28 (WK-672 Slice 3), says that the grid the property is checked on has no band edges and
may miss such an inversion, and that a counterexample is two adjacent **grid** values.

## Evidence

At `origin/main` `1c8762d9ed235f80e0f2fff80c44003694828e97`.

- The step, `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:84`:
  *"| D4 | Worker | A property assertion fails: `monotone_in_age` breaks between 63 and 64
  because two rate tables band age differently. Hypothesis shrinks it to a minimal
  counterexample. | `03` FR-261 |"*
- The requirement, `docs/specs/03-rating-engine.md:178` (FR-261), read to its end with every
  dated clarification. Three clauses disagree with the step:
  1. *"The grid is a uniform grid of five points, the declared bounds included …, plus five
     points sampled from a generator seeded by the suite's seed and the input's name"*, so
     *"the grid is one fixed set of at most ten points per property"*.
  2. *"A counterexample is the base context and the two adjacent grid values at which the
     order broke."* Ages 63 and 64 are the counterexample only if both are grid points.
  3. *"the compiled bundle pins no Banding, so no band edge is in the grid, and an inversion
     narrower than the spacing between the grid and sampled points may not be detected until
     `OQ-1224` lands."* A break confined to one band edge is that case.
- `OQ-1224` (`docs/open-questions.md:134`) is open, owner WK-1178: pinning Bandings would put
  band edges in the grid (`grid: banding-edges`).
- The search that found the step: `git grep -n -E '\b(FR-(248|251|257|258|260|261|262|273|353|364|368|1221)|NFR-(499|502))\b' 1c8762d9 -- 'docs/workflows/WF-*.md'`,
  20 hit lines, each opened and read; the WK-672 close record lists every row.

## Disposition

**Carry forward, unowned**, proposed by the auditor on 2026-09-29; the register row's
`decision:` is the lead's. Which side moves is the decision-maker's (`CLAUDE.md` §0): the step
could describe what the `uniform+sampled` grid does report, or keep its example and cite
`OQ-1224` as the condition under which it holds. Event: the decision-maker's ruling, or
`OQ-1224` landing, whichever comes first. If unowned at the next `CLAUDE.md` §14 review, the
row decays to that review.

**Lead's decision, 2026-09-29:** deferred with an owner — the decision-maker. Event: the decision-maker's ruling, or `OQ-1224` landing, whichever comes first, and no later than the gate before the P2 exit demo (plan review 16's Proposal 12 puts the two `WF-699` rulings on it). This matches the register row.
