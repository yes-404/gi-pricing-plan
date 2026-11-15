---
id: ADR-2154
family: decision
title: The audit trail is the seventh high-risk area
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: ab5f41269611a6f97147e101a638a1053668464e
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-2136]  # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2154 — The audit trail is the seventh high-risk area

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer; the detail of the rule was decided on the maintainer's behalf by delegation, 15 Nov 2026.
- **Amends:** the count of high-risk areas in ADR-2136 ("with six high-risk areas"). ADR-2136 is not edited and not superseded as a whole.

## Context

CONTRIBUTING.md names the areas where a change needs the other person's cross-review, and
`.github/CODEOWNERS` lists their paths so that GitHub requests that review by itself. The list
held six areas: the rating and scoring path, money handling, the shared data contracts,
authentication and roles, database migrations, and the project's own rules and CI.

The audit trail was not among them. Every governance record the platform keeps rests on it: an
approval, a deployment, a role grant and a data change are each recorded as an event in one
append-only chain, and each event's hash covers the one before it. A change to how an event is
recorded or chained gives no sign when it is wrong. Every later event is written as usual, and
the defect shows only when someone verifies the chain or relies on its evidence.

## Decision

The audit trail is the seventh high-risk area: how an audit event is recorded and chained, and
its routes. Its paths are listed in `.github/CODEOWNERS` under their own comment, with both
people on each line. They are the module that records and verifies the chain, the routes that
query, check and export it, the artifact-history route that reads it, and the tests that hold
the chain's rules. The hash function, the append-only triggers and their grant are already
covered by the contracts and migrations lines.

## Options not taken

- **The hand label alone.** The core lead would apply the `high-risk` label by hand to a pull
  request that touches the audit trail. Refused: a label that nobody is asked to apply is the
  gap #1878 closed for the other six areas. A path in CODEOWNERS requests the review whoever
  opens the pull request.

## Consequences

- A pull request that touches one of these paths requests the other person's review by
  itself, and it merges under CONTRIBUTING's tier 3.
- CONTRIBUTING.md lists seven high-risk areas.
- A file that only reads audit events, or a test that checks the chain once in passing, is not
  listed. A change there that alters what the chain records is labelled by hand.
