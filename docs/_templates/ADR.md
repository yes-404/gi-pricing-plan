<!--
TEMPLATE — Decision (`ADR-`), an architecture decision record.
Copy this file to `docs/adrs/ADR-<nnnnn>-<slug>.md` (the migration renames `docs/adr/`
to `docs/adrs/` — see docs/process/document-ids.md §1.4), where `<nnnnn>` is the padded
result of `python3 scripts/doc-id.py next`. Write it with the `adr-write` skill, which
covers numbering and the status lifecycle in full; this template only fixes the header
to the closed field set. Fill in every placeholder, delete this comment block, and
remove any field this record does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `kind:`, `phase:`, `work:`, `slice:`
and `plans:` do not apply to this family and must not appear here.
-->

---
id: ADR-NNNNN
family: decision
title: <one line — the decision, phrased as a stance not a question>
status: draft                 # draft → active → superseded | retired (§1.2a)
created: YYYY-MM-DD
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: <commit-sha this was written against>
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                    # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-NNNNN — <Title>

- **Status:** draft
- **Deciders:** maintainer

## Context

<The forces in tension — what would happen by default, and why that is a problem worth
a standing decision rather than a one-off choice.>

## Decision

<The decision, stated so a reader can check compliance against it — what it commits to,
and what it explicitly rules out.>

## Consequences

<What this makes easier, what it makes harder, and what it forecloses.>
