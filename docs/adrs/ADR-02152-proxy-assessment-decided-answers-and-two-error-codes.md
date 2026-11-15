---
id: ADR-2152
family: decision
title: Proxy assessment — the decided answers, and two error codes for its two kinds of invalid input
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: []   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2152 — Proxy assessment — the decided answers, and two error codes for its two kinds of invalid input

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer; the error-code ruling was decided on the maintainer's behalf by delegation.
- **Decision issue:** [#1501](https://github.com/yes-404/gi-pricing-plan/issues/1501) (WK-691, proxy assessment, `02` FR-91)
- **Decision:** [comment of 2026-11-14](https://github.com/yes-404/gi-pricing-plan/issues/1501#issuecomment-6882624466), opening: "**Decided by the maintainer, 2026-11-14.** Answers to the plan's open questions. The plan is accepted as written with these answers." Two further rulings follow, below.
- **Enacted by:** [#1861](https://github.com/yes-404/gi-pricing-plan/pull/1861), merge commit `06f379d22098be01046de84a61152a2044c84abc` (2026-11-15), slices 1 and 2 only. It does not close #1501.
- **Recorded after the fact.** Written on 2026-11-15, after the decision and its enactment.

## Context

FR-91 asks for proxy assessment: an insurer-supplied reference table, association measures (mutual
information, exposure-weighted AUC) and evidence attached to the approval request. It is evidence, never
a block (OQ-581). The plan left six questions to the maintainer.

## Decision

| Q | Question | Decided |
|---|---|---|
| Q1 | FR-302 | (a): this Work does not deliver FR-302; #1514 keeps it |
| Q2 | May a workspace policy require `proxy_assessment` evidence | (a): yes, existence only; the content never gates anything |
| Q3 | Reference table granularity | (b): area-level shares are accepted as well as per-row characteristics |
| Q4 | Units and outputs | as recommended: mutual information in bits, plus mutual information normalised by the characteristic's entropy; one-vs-rest AUC per class; no confidence interval in this Work; matched exposure and row count reported |
| Q5 | Is the reference data retained | (a): only the digest, source, as-at date and counts; rows are read once by the Job and never persisted |
| Q6 | Permission | (b): a new permission for the upload only; the result read stays under `model:read` |

**Q6's holder** (a plan amendment of 2026-11-14, decided on the maintainer's behalf by delegation):
`reference_population:upload` is granted to no built-in role, and a workspace Admin grants it. A test
must assert that no built-in role holds it. Under today's `grant_role` (FR-348) nobody can grant it yet;
that grant gap is a separate decision, #1843.

**The error-code ruling.** The maintainer's ruling of 2026-11-15, recorded in the project's channel
(not linkable publicly), decided on the maintainer's behalf by delegation, cited by #1861 as
"~01:29 GMT": the error-code census, option (A), two codes. `ProxyAssessmentError` takes a code first,
in the `GlmFitError` pattern. `PROXY_REFERENCE_INVALID` covers the reference table (a missing column,
a repeated key, null or out-of-range shares, shares not summing to 1) and `PROXY_INPUT_INVALID` covers
the call (classes, frame columns, exposure). Both are registered in `MODELLING_ERROR_CODES` and declared
in `02` §5.1. Conditions: `pricing-core` stays importable alone (the exception and its codes live in
`pricing-core`; the backend only registers them); a message names offending rows by their key in the
reference table and the column, never a share value and never a value from the caller's frame. The same
ruling keeps the `reference_population:upload` row "Specified and not yet built" in `06` until the
commit that adds the member and its check.

## Options not taken

From the plan:

- **Q1:** (b) deliver FR-302 now against a Dislocation Run's price change, with a `04` spec change; (c) keep it and wait for #1513.
- **Q2:** (b) no: the assessment is purely optional and never a policy kind.
- **Q3:** (a) a categorical characteristic per row of a declared key only.
- **Q5:** (b) keep the reference rows as a restricted artifact, for reproducibility.
- **Q6:** (a) `model:fit` to run and `model:read` to read, mirroring the transparency routes.
- **Error codes:** option (B), a single generic code, refused because it hides codes from the guard.
- **Q4:** no alternative is recorded; the plan notes a bootstrap confidence interval as a later option.

## Consequences

Accepted costs, from the plan: Q5 (a) means an assessment cannot be reproduced from the platform alone,
a departure from the reproducibility default that the plan names so it is not silent; the digest still
proves which data was used if the insurer supplies it again. Q3 (b) was chosen because individual-level
protected data is what UK insurers mostly do not hold. Costs of Q1, Q2, Q4, Q6 and the error codes are
not recorded. Slices 3 onward of #1501 are not decided here.
