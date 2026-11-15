---
id: ADR-2145
family: decision
title: The audit:read permission is held by the approver, deployer, auditor and admin roles
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-2146, ADR-2147, ADR-2148, ADR-2149]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2145 — The audit:read permission is held by the approver, deployer, auditor and admin roles

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer
- **Decision issue:** [#1548](https://github.com/yes-404/gi-pricing-plan/issues/1548) (migrated from open question OQ-1726)
- **Decision:** [comment of 2026-11-14](https://github.com/yes-404/gi-pricing-plan/issues/1548#issuecomment-6882618416), opening: "**Decided by the maintainer, 2026-11-14.** (b): record today's holders of `audit:read` (approver, deployer, auditor, admin) in `06` §4.1."
- **Enacted by:** [#1858](https://github.com/yes-404/gi-pricing-plan/pull/1858), merge commit `6c005d5db353024e532c7be54329d2af2634afef` (2026-11-15), slice 1.
- **Recorded after the fact.** This record was written on 2026-11-15, after the decision and its enactment. It records a decision already taken; it takes none.

## Context

`06` §5 defines `audit:read` as "Reading the audit log" and names no holders. FR-346 requires only that
the Auditor can read it. In the code, the four read-everything roles (approver, deployer, auditor,
admin) hold it; the analyst and the pricing actuary do not. All three audit routes (list, verify,
export) are gated on it. The audit event body carries the actor's name and free-text justifications,
comments and refusal reasons, so the choice of holders decides who sees personal data. The same
question gated the Outcome line of #1497 (the audit explorer).

## Decision

Option (b): the spec records today's four-role set. The holders of `audit:read` are `approver`,
`deployer`, `auditor` and `admin`, named in `06` §4.1. No code or test changes were needed. The
Outcome line of #1497 reads "an approver, deployer, auditor or admin".

The reasons given in the decision comment:

1. It is the behaviour that exists, that the run of 2026-10-14 confirmed, and that `audit.py` already states.
2. `audit:read` has no scope. A grant to authors would give them the whole workspace's trail across
   lines of business, which FR-345's scoping exists to prevent for every other right.
3. The need of an author to see the trail of their own artifact is real, but is better met by FR-383's
   per-artifact history route with a subject-scoped read. That is a later, separate decision, and the
   draft did not recommend it then.

Not a pricing-path decision: no rating, scoring or money path reads `audit:read`.

## Options not taken

From the issue:

- **(a) All workspace roles read the log.** Not taken: it widens who sees every principal's name and
  every free-text reason, and it is not today's behaviour.
- **(b-narrow) Admin plus a dedicated auditor role only.** Not taken: approver and deployer would lose a
  read they hold today and use in deciding and deploying; it was never asked for.
- **(c) Role-scoped reading, each role seeing the events of the artifacts it may read.** Not taken: it
  needs a per-event filter on three routes and splits verification from reading.
- **(d)** is named in the decision comment ("(a), (d)") as an option that would give the log to authors.
  The issue text does not set it out: not recorded.

## Consequences

Accepted cost: the issue and comment record no cost as such. They record that an author's need to see
the trail of their own artifact is real and is not met by this decision. The comment points to a later,
separate decision (moving the history row of
[ADR-2147](ADR-02147-the-permissions-of-06s-routes-not-yet-built.md) from `audit:read` to the
subject's read permission), which was not taken. The route pin
(`backend/tests/test_route_permission_pin.py`) and the RBAC tests catch a code change that drifts from
this set; #1858 added a pin test for the holder set.
