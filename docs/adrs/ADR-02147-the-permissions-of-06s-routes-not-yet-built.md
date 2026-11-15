---
id: ADR-2147
family: decision
title: The permission of each of 06's routes not yet built, with no new permission member
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-2145, ADR-2148]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2147 — The permission of each of 06's routes not yet built, with no new permission member

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer
- **Decision issue:** [#1547](https://github.com/yes-404/gi-pricing-plan/issues/1547) (migrated from open question OQ-2015)
- **Decision:** [comment of 2026-11-14](https://github.com/yes-404/gi-pricing-plan/issues/1547#issuecomment-6882599737), opening: "**Decided by the maintainer, 2026-11-14.** The recommendation's table: `GET /roles` under `settings:read`; dossier generate and read under the subject's read permission; dossier commentary under the subject's submit permission; dependencies under the subject's read permission; every other row as proposed; no new permission."
- **Enacted by:** in part, [#1858](https://github.com/yes-404/gi-pricing-plan/pull/1858), merge commit `6c005d5db353024e532c7be54329d2af2634afef` (2026-11-15), slice 1: it records `POST /audit/anchor` and `GET /artifacts/{ref}/history` under `audit:read` and marks OQ-2015 decided. The other rows land in the first commit of the Work that builds each route, as the decision says; they are not yet enacted by a merged PR named here.
- **Recorded after the fact.** Written on 2026-11-15, after the decision.

## Context

`06` §5.1 declares routes that are not yet built (roles, role assignments, break-glass, attestations,
the audit anchor, dossiers, regulatory exports, artifact history and dependencies). The permission
pin reads built routes only, so each route's permission was a proposal in a spec cell. The question
was which permission each needs, decided before the route is built.

## Decision

| Route | Permission |
|---|---|
| `GET /roles` | `settings:read` (changed: the Auditor must read roles, FR-346) |
| `POST /roles`, `POST /role-assignments` | `admin:manage_roles` |
| `POST /break-glass` | `admin:break_glass`, checked at the route (amend `06:296`) |
| `POST /attestations` | `approval:decide`, roles from `approver_roles` (option 5a) |
| `POST /audit/anchor` | `audit:read` |
| `POST /dossiers`, `GET /dossiers/{id}` | the subject's read permission (`model:read` / `rating:read`) (changed: the submitter must generate the pinned dossier) |
| `POST /dossiers/{id}/commentary` | the subject's submit permission (`model:submit` / `rating:submit`) (changed: FR-378, the submitter writes the mandatory blocks) |
| `POST /regulatory-exports` | `audit:read`; revisit with [ADR-2145](ADR-02145-audit-read-is-held-by-the-approver-deployer-auditor-and-admin-roles.md) |
| `GET /artifacts/{ref}/history` | `audit:read`; follows ADR-2145 |
| `GET /artifacts/{ref}/dependencies` | the subject's read permission (changed: matches the built lineage route) |

**No new permission enum member.** One permission per verb and resource family: reads use the family's
read verb, writes use its write or submit verb, administration reads with `settings:read` and writes
with `admin:manage_*`, sign-offs use `approval:decide`. Rows 7, 8, 9 and 12 of the table become
handler-checked cells, and each owning Work adds its `HANDLER_GUARDED` entry. The spec change for each
group lands in the first commit of the Work that builds the route.

## Options not taken

- **A new `attestation:record` member for attestations.** The issue's own recommendation, not taken
  (the decision comment notes the chosen cell "differs from the OQ's own recommendation"): attestation
  uses `approval:decide`.
- **A distinct export right for regulatory exports**, and **`authenticated` for `GET /roles`**: raised
  as alternatives in the issue's row groups. Not taken; the comment gives no further reason: not recorded.
- The issue's own cells for `GET /roles`, dossiers, commentary and dependencies were changed, as the table says.

## Consequences

The accepted cost is not recorded in the issue or the comment: not recorded. The comment says the
decision keeps one permission per verb and resource family. The issue noted that an attestation is a
periodic review and not a decision, and the comment chose `approval:decide` for it. The rows for
regulatory exports and history are to be revisited with ADR-2145.
