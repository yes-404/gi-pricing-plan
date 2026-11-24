---
id: ADR-2180
family: decision
title: A code-owned pull request, in a period with no cross-review, is merged on an independent audit, the maintainer's read and the workflows green on its landing tree
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-24
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 3a02515f6f64807a9728e078ce33373738f8651f
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-2136, ADR-2154]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2180 — A code-owned pull request, in a period with no cross-review, is merged on an independent audit, the maintainer's read and the workflows green on its landing tree

- **Status:** Accepted (front matter `active`).
- **Date:** 2026-11-24
- **Deciders:** the maintainer, on 2026-11-24.
- **Related:** ADR-2136 (the project frame and `CONTRIBUTING.md`); ADR-2154 (the audit trail is the seventh high-risk area); `CONTRIBUTING.md` "Review", which carries a dated amendment that points here.
- **Enacted by:** the pull request that adds this record and that amendment.

## Context

`CONTRIBUTING.md` "Review" says a pull request in a high-risk area, one that `.github/CODEOWNERS` requests a reviewer for, is cross-reviewed by the other person, and that the maintainer may proceed if that does not happen within three working days.

From 1 December 2026, no cross-review is available in this period. The period ends when the maintainer ends it with a dated line in the same place; it is expected to end in mid January 2027.

The present rule has no answer for a period of that length. The three-working-day fallback lets the maintainer proceed, but it names nothing that stands in the place of the second reader.

Options considered:

- **Three checks in place of the cross-review, accepted.** The work continues, and each high-risk pull request still gets a reader who is not its author, the maintainer's own read, and a run of its workflows on the tree it lands as.
- **Pause the merge of code-owned pull requests for the period.** Not taken: the high-risk areas hold the rating path, money, the contracts, authentication, the audit trail, migrations and the project's own rules, so a pause of several weeks would stop most of the product's work.
- **Merge on the maintainer's read alone.** Not taken: it removes the independent reader, and the independent audit is the check that starts from the range and the specification and not from the author's conclusions.

## Decision

- **Period.** From 1 December 2026 until the maintainer ends it with a dated line in `CONTRIBUTING.md` "Review". No cross-review is available in this period.
- **What replaces the cross-review.** A code-owned (high-risk) pull request merges in the period only when **all three** hold:
  1. **An independent audit** by a reader who did not write the change and who starts from the range and the specification, not from the author's conclusions. Its findings, and what was decided about each, are stated in the pull request description.
  2. **The maintainer's own read of the diff** and check of the evidence.
  3. **The workflows its paths fire are green on the exact tree it lands as.**
- **What does not change.** Nobody merges their own pull request: the core lead merges, one at a time, on the maintainer's MERGE-ACK naming the head. Every other rule of "Review" stands. Findings and private reports are handled as now (`SECURITY.md`).
- **The record.** A pull request merged under this rule says so in one line of its description and carries the label `no-cross-review`. When the period ends, the collaborator is asked to read those pull requests. That read is a request and gates nothing already merged. A finding from it is a finding like any other.
- **The collaborator's own Works** are not taken over by the core team in the period.
- **In force** only once this record is on `main` and 1 December 2026 is reached. Until both are true, the present rule of "Review" applies.

## Consequences

- **Positive:** high-risk work continues in the period, with a reader who is not the author, a second read by the maintainer, and evidence from the landing tree. A pull request merged this way is labelled and listed in its own description, so the later read has a closed set to start from.
- **Negative:** the three checks are not a second domain reader. The independent audit and the maintainer's read are by readers the team already has, and a defect that both miss is found later than a cross-review would have found it. Every high-risk pull request in the period also waits on the maintainer's read, which is a single point of delay.
- **Neutral:** the read when the period ends gates nothing already merged. Its findings are handled as any finding is. The tiers other than the high-risk tier are not changed.
