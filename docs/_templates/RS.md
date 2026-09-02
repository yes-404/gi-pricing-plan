<!--
TEMPLATE — Research (`RS-`), one spike, measurement or audit.
Copy this file to `docs/research/RS-<nnnnn>-<slug>.md`, where `<nnnnn>` is the padded
result of `python3 scripts/doc-id.py next`. Fill in every placeholder, delete this
comment block, and remove any field this record does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `slice:`, `plans:`, `supersedes:` and
`superseded_by:` do not apply to this family and must not appear here.
-->

---
id: RS-NNNNN
family: research
kind: spike                    # spike | measurement | audit — no other value (§1.2)
title: <one line — the question this spike, measurement or audit answers>
status: draft                  # draft → active → closed | retired (§1.2a)
created: YYYY-MM-DD
owner: executor                 # `library-spike` / measurements; auditor for `kind: audit`
tree: <commit-sha this was written against>
phase: P<n>
work: WK-NNNNN
corrected_by: []
relates: []                     # ids only — the FR-/ADR-/RFC- target a spike's `closed` cites
---

# RS-NNNNN — <Title>

## Question

<What was uncertain, and why a spec assumption could not be settled by reading alone.>

## Method

<How it was verified in this environment — the `library-spike` shape for `kind: spike`;
the measurement's setup and instrumentation for `kind: measurement`; scope, evidence and
verdicts for `kind: audit`.>

## Findings

<The result. For `kind: audit`, every finding filed as its own `FD-`, listed here by id.>

<!-- `status: active` is set on filing; `closed` only by citing the FR-/ADR-/RFC- the
     decision-maker created from this finding — never by the spike itself deciding. -->
