---
id: ADR-2146
family: decision
title: GET /audit/verify verifies the whole chain by default and takes an optional from/to range
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-2145, ADR-2149]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2146 — GET /audit/verify verifies the whole chain by default and takes an optional from/to range

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer
- **Decision issue:** [#1809](https://github.com/yes-404/gi-pricing-plan/issues/1809)
- **Decision:** [comment of 2026-11-14](https://github.com/yes-404/gi-pricing-plan/issues/1809#issuecomment-6881208148), opening: "**Decided by the maintainer, 2026-11-14: option C.**"
- **Enacted by:** [#1858](https://github.com/yes-404/gi-pricing-plan/pull/1858), merge commit `6c005d5db353024e532c7be54329d2af2634afef` (2026-11-15), slices 1 and 6.
- **Recorded after the fact.** Written on 2026-11-15, after the decision and its enactment.

## Context

The spec row in `06-governance.md` read `GET /api/v1/audit/verify?from=&to=`. The route took no
parameters and recomputed every hash for the workspace. Spec and code disagreed, and the repository
rule is to resolve such a disagreement and record which side was wrong, not to make one match the
other silently. FR-372 and NFR-521 ("verifiable over the whole retained range") depend on the answer.

## Decision

Option C. `GET /api/v1/audit/verify` verifies the whole chain by default and takes an optional
`from`/`to` range. Neither the spec row nor the code is kept as it stood: the code gains range
verification, and the spec gains one dated line saying that the whole-chain form is NFR-521's proof.

Reason from the comment: an audit explorer filtered to a period needs a status for that period, and
NFR-521 needs the whole retained range to be verifiable.

To enact it, #1497's spec slice amends the route row by a dated line and records which side was wrong
on which point; its range-verification slice carries a failing-first tamper test inside and outside the range.

## Options not taken

From the issue:

- **A. The spec is right: build range verification only**, from the checkpoint before `from`.
  Not taken alone: option C includes A's work and adds the whole-chain default.
- **B. The code is right: amend the spec to drop `from`/`to`.** Not taken: an explorer filtered to one
  month could not show a verification status for that month alone.

## Consequences

Accepted cost, from the issue: the work of A (new code in the chain verifier and a red-first tamper
test inside and outside the range), plus a spec line that says which form NFR-521's proof uses.

The meaning of a range was a later question of the plan (Q6 of #1497, see
[ADR-2149](ADR-02149-the-1497-plans-decided-items.md)): a range selects the contiguous sequence span.
