<!--
TEMPLATE — Proposal (`RFC-`).
Copy this file to `docs/rfcs/RFC-<nnnnn>-<slug>.md`, where `<nnnnn>` is the padded result
of `python3 scripts/doc-id.py next`. Fill in every placeholder, delete this comment
block, and remove any field this proposal does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `phase:`, `work:`, `slice:` and
`plans:` do not apply to this family and must not appear here. `deliverable`,
`lands_in` and `trigger` below are this family's declared extras (§1.5's closing
paragraph) — no other family may use them, and this family may use no other extra.
-->

---
id: RFC-NNNNN
family: proposal
kind: enhancement              # enhancement | process | incident — no other value (§1.2)
title: <one line — the topic, not the answer>
status: draft                  # draft → active → closed | retired | superseded (§1.2a)
created: YYYY-MM-DD
owner: maintainer               # mints and owns; any role drafts on instruction (§1.6)
tree: <commit-sha this was written against>
deliverable: <what shipping this produces — what `close-workstream` checks for before
  setting this `closed`>
lands_in: <the module, component or document this deliverable lands in>
trigger: <the condition that starts this RFC's procedure, for a `process` or `incident`
  kind; omit for `enhancement`>
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this RFC itself corrects a frozen record
relates: []                     # ids only
---

# RFC-NNNNN — <Title>

## Problem

<What is missing, wrong or costly today, evidenced rather than asserted.>

## Proposal

<The change. For a `process` RFC, the procedure it establishes; for an `incident` RFC,
the post-mortem and the fix; for `enhancement`, the design.>

## Deliverable

<Restates the `deliverable:`/`lands_in:` fields in prose — what "done" looks like, and
which Work will cut it (planner "cuts an active RFC into a Work", §1.6).>
