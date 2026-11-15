---
id: ADR-2148
family: decision
title: Work #1497 owns the permission of GET /artifacts/{ref}/history
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-2147, ADR-2145]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2148 — Work #1497 owns the permission of GET /artifacts/{ref}/history

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer
- **Decision issue:** [#1811](https://github.com/yes-404/gi-pricing-plan/issues/1811)
- **Decision:** [comment of 2026-11-14](https://github.com/yes-404/gi-pricing-plan/issues/1811#issuecomment-6881208710), opening: "**Decided by the maintainer, 2026-11-14: option A.**"
- **Enacted by:** [#1858](https://github.com/yes-404/gi-pricing-plan/pull/1858), merge commit `6c005d5db353024e532c7be54329d2af2634afef` (2026-11-15), slice 1 (the history route's permission is recorded as `audit:read`) and slice 7 (the route).
- **Recorded after the fact.** Written on 2026-11-15, after the decision and its enactment.

## Context

The owner cell of #1547 (OQ-2015, [ADR-2147](ADR-02147-the-permissions-of-06s-routes-not-yet-built.md))
named the Works that build each unbuilt `06` route, but omitted #1497 (WK-679), which builds
`GET /api/v1/artifacts/{ref}/history`. The question: is #1497 the owner of that route's permission?

## Decision

Option A. #1497 (WK-679) is the owner of the permission for `GET /api/v1/artifacts/{ref}/history`
within #1547. #1497's specification slice records the permission once #1547 is decided.

## Options not taken

- **B. No: the permission is decided by another Work named in the owner cell before #1497 builds the
  route.** Not taken. Cost named in the issue: #1497's history slice would wait on a Work that does not
  build the route.

## Consequences

Accepted cost, from the issue: none beyond the record. The permission itself was decided in #1547
(`audit:read`, following [ADR-2145](ADR-02145-audit-read-is-held-by-the-approver-deployer-auditor-and-admin-roles.md)).
