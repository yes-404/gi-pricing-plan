---
family: reference
title: docs/closures — how each close was audited
status: active                  # active → retired (§1.2a)
created: 2026-09-06
owner: lead
corrected_by: []
relates: []                      # ids only
---

# docs/closures — how each close was audited

One `CR-` record per close, `kind:` naming which layer it closed: `work` for a work item,
`phase` for a phase, `review` for a §14 plan review. Each says what was audited, against
what scope, and what the verdict was — the record of what was believed and decided at that
date. Nothing here changes status afterwards.

This directory is one of the four — [`../process/`](../process/),
[`../findings/`](../findings/README.md), [`../research/`](../research/) and this one — that
the old `docs/audit/` dissolved into. The forward-looking plan is
[`../roadmap.md`](../roadmap.md); these are the archive.

The checklists a close writes against are in
[`../process/checklists/`](../process/checklists/), and the findings a close carries forward
are rows in [`../findings/register.md`](../findings/register.md).

## Conventions

- **A close is named by an existing id** — a `WK-` work item, a phase, a PR number. No new id
  family is minted here; the id comes from `docs/process/document-ids.md` §1.2.
- **Checklist versioning.** A checklist is versioned; a record names the checklist version it
  was written against.
- **Evidence is write-once**, and a correction after the fact is dated and says so.
- **A tag at phase close.** The phase record is tagged at the phase's close.
- **ISO dates**, and no secrets, credentials or dataset contents.
